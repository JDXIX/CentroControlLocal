"""Pruebas de funcionalidad y límites arquitectónicos del componente local."""
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from dominio.entidades import Residente
from dominio.objetos_valor import LecturaBiometrica, UmbralCritico
from dominio.evaluador_riesgo import EvaluadorRiesgo
from dominio.eventos import CaidaDetectada, RitmoCardiacoCriticoDetectado
from aplicacion.casos_uso import ProcesarLectura
from adaptadores.adaptador_lecturas import AdaptadorLecturas
from adaptadores.centro_control_local import CentroControlLocal
from adaptadores.alarma_consola import AlarmaConsola
from adaptadores.repositorios_memoria import RepositorioResidentesMemoria, RepositorioPendientesMemoria
from adaptadores.cliente_alertas_prueba import ClienteAlertasPrueba
from infraestructura.generador_lecturas import GeneradorLecturas


class ReceptorQueFalla(ClienteAlertasPrueba):
    def recibir_alerta(self, alerta):
        raise ConnectionError('No hay internet')


class PruebasCentroControlLocal(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.alarma = AlarmaConsola(str(Path(self.temporal.name) / 'alertas.log'), mostrar=False)
        self.central = ClienteAlertasPrueba(mostrar=False)
        self.pendientes = RepositorioPendientesMemoria()
        self.residente = Residente('RES-001', 'Residente de prueba',
                                  UmbralCritico(55, 100, Decimal('38.0')))
        self.procesador = ProcesarLectura(
            RepositorioResidentesMemoria([self.residente]), self.alarma,
            self.central, self.pendientes, EvaluadorRiesgo())
        self.centro = CentroControlLocal('RESIDENCIA-01', self.procesador, AdaptadorLecturas())
        self.generador = GeneradorLecturas()

    def lectura(self, pulso=80, temperatura='36.5', impacto=False, residente='RES-001'):
        return self.generador.generar(residente, pulso, temperatura, impacto)

    def test_lectura_normal_no_genera_alarma(self):
        self.assertEqual(self.centro.recibir_lectura(self.lectura()), [])
        self.assertEqual(len(self.alarma.activadas), 0)

    def test_pulso_critico_genera_evento_y_alarma(self):
        alertas = self.centro.recibir_lectura(self.lectura(pulso=125))
        self.assertEqual(len(alertas), 1)
        self.assertEqual(alertas[0].tipo, 'PULSO_CRITICO')
        self.assertIsInstance(self.procesador.ultimos_eventos[0], RitmoCardiacoCriticoDetectado)
        self.assertEqual(len(self.alarma.activadas), 1)
        self.assertEqual(len(self.central.recibidas), 1)
        self.assertTrue(Path(self.alarma.archivo).exists())

    def test_caida_genera_evento_y_alarma(self):
        alertas = self.centro.recibir_lectura(self.lectura(impacto=True))
        self.assertEqual(alertas[0].tipo, 'CAIDA')
        self.assertIsInstance(self.procesador.ultimos_eventos[0], CaidaDetectada)

    def test_temperatura_fuera_umbral_genera_alerta(self):
        alertas = self.centro.recibir_lectura(self.lectura(temperatura='39.0'))
        self.assertEqual([a.tipo for a in alertas], ['TEMPERATURA_ALTA'])

    def test_duplicado_se_suprime_y_recuperacion_reactiva(self):
        self.assertEqual(len(self.centro.recibir_lectura(self.lectura(pulso=120))), 1)
        self.assertEqual(len(self.centro.recibir_lectura(self.lectura(pulso=130))), 0)
        self.assertEqual(len(self.centro.recibir_lectura(self.lectura())), 0)
        self.assertEqual(len(self.centro.recibir_lectura(self.lectura(pulso=125))), 1)
        self.assertEqual(len(self.alarma.activadas), 2)

    def test_sin_internet_alarma_local_y_pendiente(self):
        self.central.disponible = False
        self.centro.recibir_lectura(self.lectura(impacto=True))
        self.assertEqual(len(self.alarma.activadas), 1)
        self.assertEqual(len(self.central.recibidas), 0)
        self.assertEqual(len(self.pendientes.listar()), 1)

    def test_reconexion_reenvia_y_elimina_pendientes(self):
        self.central.disponible = False
        alertas = self.centro.recibir_lectura(self.lectura(impacto=True))
        self.central.disponible = True
        self.assertEqual(self.procesador.reintentar_pendientes(), (1, 0))
        self.assertIn(alertas[0].id, self.central.recibidas)
        self.assertEqual(self.procesador.reintentar_pendientes(), (0, 0))

    def test_excepcion_remota_no_impide_alarma(self):
        self.procesador.receptor = ReceptorQueFalla(mostrar=False)
        self.centro.recibir_lectura(self.lectura(pulso=130))
        self.assertEqual(len(self.alarma.activadas), 1)
        self.assertEqual(len(self.pendientes.listar()), 1)

    def test_identificador_desconocido_es_rechazado(self):
        with self.assertRaisesRegex(ValueError, 'no registrado'):
            self.centro.recibir_lectura(self.lectura(residente='RES-999'))

    def test_datos_incompletos_y_extra_son_rechazados(self):
        datos = self.lectura()
        del datos['residente_id']
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(datos)
        datos = self.lectura()
        datos['campo_extra'] = 'no esperado'
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(datos)

    def test_pulso_bool_y_valores_imposibles_se_rechazan(self):
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(self.lectura(pulso=True))
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(self.lectura(pulso=500))
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(self.lectura(temperatura='NaN'))

    def test_fecha_sin_zona_y_bandera_invalida_se_rechazan(self):
        datos = self.lectura()
        datos['fecha_hora'] = '2026-11-06T12:00:00'
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(datos)
        datos = self.lectura()
        datos['impacto_detectado'] = 'verdadero'
        with self.assertRaises(ValueError):
            self.centro.recibir_lectura(datos)

    def test_objetos_valor_son_inmutables(self):
        lectura = LecturaBiometrica('RES-001', 80, Decimal('36.5'), False,
                                   datetime.now(timezone.utc))
        with self.assertRaises(FrozenInstanceError):
            lectura.pulso = 100

    def test_central_idempotente_no_repite_recepcion(self):
        alerta = self.centro.recibir_lectura(self.lectura(pulso=120))[0]
        self.assertTrue(self.central.recibir_alerta(alerta))
        self.assertEqual(len(self.central.recibidas), 1)


if __name__ == '__main__':
    unittest.main()

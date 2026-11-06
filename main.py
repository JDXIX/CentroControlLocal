"""Punto de composición: conecta los adaptadores con los puertos de aplicación."""
from decimal import Decimal
from time import perf_counter

from dominio.entidades import Residente
from dominio.objetos_valor import UmbralCritico
from dominio.evaluador_riesgo import EvaluadorRiesgo
from aplicacion.casos_uso import ProcesarLectura
from adaptadores.adaptador_lecturas import AdaptadorLecturas
from adaptadores.centro_control_local import CentroControlLocal
from adaptadores.repositorios_memoria import RepositorioResidentesMemoria, RepositorioPendientesMemoria
from adaptadores.alarma_consola import AlarmaConsola
from adaptadores.cliente_alertas_prueba import ClienteAlertasPrueba
from infraestructura.generador_lecturas import GeneradorLecturas


def crear_prototipo():
    # 30 residentes ficticios = una residencia tipo de la Entrega 1.
    # Estos límites son únicamente DE PRUEBA, no recomendaciones médicas.
    residentes = [
        Residente(f'RES-{numero:03}', f'Residente de prueba {numero}',
                  UmbralCritico(55, 100, Decimal('38.0')))
        for numero in range(1, 31)
    ]
    central = ClienteAlertasPrueba()
    pendientes = RepositorioPendientesMemoria()
    procesador = ProcesarLectura(
        RepositorioResidentesMemoria(residentes), AlarmaConsola(), central,
        pendientes, EvaluadorRiesgo())
    centro = CentroControlLocal('RESIDENCIA-01', procesador, AdaptadorLecturas())
    return centro, procesador, central, pendientes


def main():
    centro, procesador, central, pendientes = crear_prototipo()
    generador = GeneradorLecturas()
    print('CENTRO DE CONTROL LOCAL | RESIDENCIA-01 | 30 residentes de prueba')
    print('Límites de prueba: pulso 55-100; temperatura máxima 38.0 (NO clínicos)')
    casos = [
        ('1. Lectura normal', 'RES-001', 80, '36.5', False, True),
        ('2. Pulso crítico', 'RES-001', 125, '36.5', False, True),
        ('3. Pulso crítico repetido (no se duplica)', 'RES-001', 127, '36.5', False, True),
        ('4. Pulso normal (restablece)', 'RES-001', 79, '36.5', False, True),
        ('5. Caída con internet desconectado', 'RES-002', 80, '36.5', True, False),
        ('6. Misma caída (no se duplica)', 'RES-002', 80, '36.5', True, False),
        ('7. Temperatura elevada con central desconectada', 'RES-003', 80, '39.0', False, False),
    ]
    for titulo, residente, pulso, temperatura, impacto, disponible in casos:
        print(f'\n{titulo}')
        central.disponible = disponible
        inicio = perf_counter()
        alertas = centro.recibir_lectura(generador.generar(residente, pulso, temperatura, impacto))
        print(f'Alertas nuevas: {len(alertas)} | Eventos de dominio: '
              f'{[type(e).__name__ for e in procesador.ultimos_eventos]} '
              f'| tiempo local del prototipo: {(perf_counter()-inicio)*1000:.3f} ms')
    print(f'\nPendientes de envío (conexión caída): {len(pendientes.listar())}')
    print('8. Conectividad restablecida: reenvío de pendientes')
    central.disponible = True
    enviadas, restantes = procesador.reintentar_pendientes()
    print(f'Reenviadas: {enviadas} | Pendientes: {restantes} '
          f'| Central recibió: {len(central.recibidas)} alertas únicas')
    print('Bitácora local: alertas.log')
    print('Nota: estos tiempos miden solo la ejecución local de este programa, no latencia BLE/HTTP.')


if __name__ == '__main__':
    main()

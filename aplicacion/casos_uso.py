"""Caso de uso principal: orquestar entradas, dominio, alarmas y envío remoto."""
from uuid import uuid4

from aplicacion.puertos import (IProcesarLectura, IRepositorioResidentes,
                               IAlarmaLocal, IRecepcionAlertas, IRepositorioPendientes)
from dominio.entidades import AlertaMedica
from dominio.eventos import (CaidaDetectada, RitmoCardiacoCriticoDetectado,
                             TemperaturaCriticaDetectada)
from dominio.evaluador_riesgo import EvaluadorRiesgo
from dominio.objetos_valor import LecturaBiometrica


class ProcesarLectura(IProcesarLectura):
    def __init__(self, residentes: IRepositorioResidentes,
                 alarma: IAlarmaLocal, receptor: IRecepcionAlertas,
                 pendientes: IRepositorioPendientes,
                 evaluador: EvaluadorRiesgo):
        self.residentes = residentes
        self.alarma = alarma
        self.receptor = receptor
        self.pendientes = pendientes
        self.evaluador = evaluador
        self.ultimos_eventos = []  # Evidencia de Domain Events en la demostración.

    def ejecutar(self, lectura: LecturaBiometrica) -> list[AlertaMedica]:
        residente = self.residentes.obtener_por_id(lectura.residente_id)
        if residente is None:
            raise ValueError('Residente no registrado en esta residencia')
        riesgos = self.evaluador.evaluar(lectura, residente.obtener_umbral())
        nuevos = residente.registrar_riesgos(riesgos)
        alertas = []
        self.ultimos_eventos = []
        for tipo in sorted(nuevos):
            evento = self._crear_evento(tipo, lectura)
            self.ultimos_eventos.append(evento)
            alerta = AlertaMedica(
                id=uuid4().hex, residente_id=lectura.residente_id,
                tipo=tipo, severidad='CRITICA', fecha_hora=lectura.fecha_hora)
            alertas.append(alerta)
            # Orden deliberado: la alarma local NO espera a internet.
            self.alarma.activar_alarma(alerta)
            # Primero se retiene el aviso; se quita cuando el receptor confirma.
            self.pendientes.guardar(alerta)
            self._intentar_envio(alerta)
        return alertas

    @staticmethod
    def _crear_evento(tipo: str, lectura: LecturaBiometrica):
        if tipo == 'CAIDA':
            return CaidaDetectada(lectura.residente_id, lectura.fecha_hora)
        if tipo == 'PULSO_CRITICO':
            return RitmoCardiacoCriticoDetectado(
                lectura.residente_id, lectura.fecha_hora, lectura.pulso)
        return TemperaturaCriticaDetectada(
            lectura.residente_id, lectura.fecha_hora, str(lectura.temperatura))

    def _intentar_envio(self, alerta: AlertaMedica) -> bool:
        try:
            recibido = self.receptor.recibir_alerta(alerta)
        except Exception:  # El fallo remoto se aísla del camino de alarma local.
            recibido = False
        if recibido:
            self.pendientes.eliminar(alerta.id)
        return recibido

    def reintentar_pendientes(self) -> tuple[int, int]:
        enviadas = 0
        for alerta in self.pendientes.listar():
            if self._intentar_envio(alerta):
                enviadas += 1
        return enviadas, len(self.pendientes.listar())

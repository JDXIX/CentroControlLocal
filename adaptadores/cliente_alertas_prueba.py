"""Contrato IRecepcionAlertas, sin servidor real ni conexiones a internet."""
from aplicacion.puertos import IRecepcionAlertas
from dominio.entidades import AlertaMedica


class ClienteAlertasPrueba(IRecepcionAlertas):
    def __init__(self, disponible: bool = True, mostrar: bool = True):
        self.disponible = disponible
        self.mostrar = mostrar
        self.recibidas = {}  # Clave id: recepción idempotente de alertas.

    def recibir_alerta(self, alerta: AlertaMedica) -> bool:
        if not self.disponible:
            if self.mostrar:
                print('CENTRAL NO DISPONIBLE | alerta pendiente, alarma local ya activada')
            return False
        if alerta.id not in self.recibidas:
            self.recibidas[alerta.id] = alerta
            if self.mostrar:
                print(f'CENTRAL (PRUEBA) | alerta {alerta.id[:8]} recibida')
        return True

"""Implementación local de IAlarmaLocal: consola y bitácora mínima."""
from datetime import timezone
from pathlib import Path
from aplicacion.puertos import IAlarmaLocal
from dominio.entidades import AlertaMedica


class AlarmaConsola(IAlarmaLocal):
    def __init__(self, archivo: str = 'alertas.log', mostrar: bool = True):
        self.archivo = Path(archivo)
        self.mostrar = mostrar
        self.activadas = []

    def activar_alarma(self, alerta: AlertaMedica) -> None:
        mensaje = (f'ALARMA LOCAL | id={alerta.id} | residente={alerta.residente_id} '
                   f'| tipo={alerta.tipo} | fecha={alerta.fecha_hora.astimezone(timezone.utc).isoformat()}')
        self.activadas.append(alerta)
        if self.mostrar:
            print(mensaje)
        # Se registra solo el identificador pseudónimo y lo imprescindible del evento.
        with self.archivo.open('a', encoding='utf-8') as registro:
            registro.write(mensaje + '\n')

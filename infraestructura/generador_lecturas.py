"""Datos reproducibles: NO requiere sensores físicos ni BLE."""
from datetime import datetime, timezone


class GeneradorLecturas:
    def generar(self, residente_id: str, pulso: int = 80, temperatura: str = '36.5',
                impacto_detectado: bool = False) -> dict:
        return {
            'residente_id': residente_id,
            'pulso': pulso,
            'temperatura': temperatura,
            'impacto_detectado': impacto_detectado,
            'fecha_hora': datetime.now(timezone.utc).isoformat(),
        }

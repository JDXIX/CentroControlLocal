"""Objetos de valor del dominio (sin dependencias externas)."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class UmbralCritico:
    pulso_minimo: int
    pulso_maximo: int
    temperatura_maxima: Decimal

    def __post_init__(self):
        if (isinstance(self.pulso_minimo, bool) or isinstance(self.pulso_maximo, bool)
                or not isinstance(self.pulso_minimo, int)
                or not isinstance(self.pulso_maximo, int)
                or not 20 <= self.pulso_minimo < self.pulso_maximo <= 250):
            raise ValueError("Umbrales de pulso inválidos")
        if not isinstance(self.temperatura_maxima, Decimal) or not self.temperatura_maxima.is_finite():
            raise ValueError("Umbral de temperatura inválido")
        if not Decimal('25') <= self.temperatura_maxima <= Decimal('45'):
            raise ValueError("Umbral de temperatura fuera de rango técnico")


@dataclass(frozen=True)
class LecturaBiometrica:
    residente_id: str
    pulso: int
    temperatura: Decimal
    impacto_detectado: bool
    fecha_hora: datetime

    def __post_init__(self):
        if not isinstance(self.residente_id, str) or not 1 <= len(self.residente_id) <= 40:
            raise ValueError("Identificador de residente inválido")
        if isinstance(self.pulso, bool) or not isinstance(self.pulso, int) or not 20 <= self.pulso <= 250:
            raise ValueError("Pulso fuera del rango técnico permitido (20-250)")
        if not isinstance(self.temperatura, Decimal) or not self.temperatura.is_finite():
            raise ValueError("Temperatura inválida")
        if not Decimal('25') <= self.temperatura <= Decimal('45'):
            raise ValueError("Temperatura fuera del rango técnico permitido (25-45)")
        if not isinstance(self.impacto_detectado, bool):
            raise ValueError("Indicador de caída inválido")
        if not isinstance(self.fecha_hora, datetime) or self.fecha_hora.tzinfo is None:
            raise ValueError("Fecha de lectura debe incluir zona horaria")

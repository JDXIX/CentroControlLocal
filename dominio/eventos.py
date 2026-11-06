"""Domain Events: describen hechos del dominio; no mensajes de red."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CaidaDetectada:
    residente_id: str
    fecha_hora: datetime


@dataclass(frozen=True)
class RitmoCardiacoCriticoDetectado:
    residente_id: str
    fecha_hora: datetime
    pulso: int


@dataclass(frozen=True)
class TemperaturaCriticaDetectada:
    residente_id: str
    fecha_hora: datetime
    temperatura: str

"""Entidades y Aggregate Roots: Residente y AlertaMedica."""
from dataclasses import dataclass, field
from datetime import datetime
from dominio.objetos_valor import UmbralCritico


@dataclass(eq=False)
class Residente:
    id: str
    nombre: str
    umbral: UmbralCritico
    _riesgos_activos: set[str] = field(default_factory=set, repr=False)

    def obtener_umbral(self) -> UmbralCritico:
        return self.umbral

    def registrar_riesgos(self, detectados: set[str]) -> set[str]:
        """Solo devuelve riesgos nuevos; se restablece tras lectura normal."""
        nuevos = detectados - self._riesgos_activos
        self._riesgos_activos = set(detectados)
        return nuevos


@dataclass(eq=False)
class AlertaMedica:
    id: str
    residente_id: str
    tipo: str
    severidad: str
    fecha_hora: datetime

    def obtener_detalle(self) -> str:
        return f'{self.tipo} | residente={self.residente_id} | severidad={self.severidad}'

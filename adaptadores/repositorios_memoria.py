"""Adaptadores de salida sin motor de base de datos."""
from aplicacion.puertos import IRepositorioResidentes, IRepositorioPendientes
from dominio.entidades import Residente, AlertaMedica


class RepositorioResidentesMemoria(IRepositorioResidentes):
    def __init__(self, residentes: list[Residente]):
        self._residentes = {residente.id: residente for residente in residentes}

    def obtener_por_id(self, residente_id: str) -> Residente | None:
        return self._residentes.get(residente_id)


class RepositorioPendientesMemoria(IRepositorioPendientes):
    def __init__(self):
        self._alertas = {}

    def guardar(self, alerta: AlertaMedica) -> None:
        self._alertas[alerta.id] = alerta

    def listar(self) -> list[AlertaMedica]:
        return list(self._alertas.values())

    def eliminar(self, alerta_id: str) -> None:
        self._alertas.pop(alerta_id, None)

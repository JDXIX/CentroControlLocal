"""Contratos internos. Los adaptadores implementan los puertos de salida."""
from abc import ABC, abstractmethod
from dominio.entidades import AlertaMedica, Residente
from dominio.objetos_valor import LecturaBiometrica


class IProcesarLectura(ABC):
    @abstractmethod
    def ejecutar(self, lectura: LecturaBiometrica) -> list[AlertaMedica]: ...


class IRepositorioResidentes(ABC):
    @abstractmethod
    def obtener_por_id(self, residente_id: str) -> Residente | None: ...


class IAlarmaLocal(ABC):
    @abstractmethod
    def activar_alarma(self, alerta: AlertaMedica) -> None: ...


class IRecepcionAlertas(ABC):
    @abstractmethod
    def recibir_alerta(self, alerta: AlertaMedica) -> bool: ...


class IRepositorioPendientes(ABC):
    @abstractmethod
    def guardar(self, alerta: AlertaMedica) -> None: ...

    @abstractmethod
    def listar(self) -> list[AlertaMedica]: ...

    @abstractmethod
    def eliminar(self, alerta_id: str) -> None: ...

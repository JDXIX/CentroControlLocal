"""Adaptador de entrada del componente elegido en la Entrega 1."""
from aplicacion.puertos import IProcesarLectura
from adaptadores.adaptador_lecturas import AdaptadorLecturas


class CentroControlLocal:
    def __init__(self, residencia_id: str, procesador: IProcesarLectura,
                 adaptador: AdaptadorLecturas):
        self.residencia_id = residencia_id
        self.procesador = procesador
        self.adaptador = adaptador

    def recibir_lectura(self, datos: dict):
        lectura = self.adaptador.convertir(datos)
        return self.procesador.ejecutar(lectura)

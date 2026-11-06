"""Adaptador de entrada: traduce diccionarios a Value Objects válidos."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from dominio.objetos_valor import LecturaBiometrica


class AdaptadorLecturas:
    def convertir(self, datos: dict) -> LecturaBiometrica:
        if not isinstance(datos, dict):
            raise ValueError('Formato de lectura inválido')
        obligatorios = {'residente_id', 'pulso', 'temperatura', 'impacto_detectado', 'fecha_hora'}
        if set(datos) != obligatorios:
            raise ValueError('Campos de lectura incompletos o no permitidos')
        try:
            if isinstance(datos['pulso'], bool) or not isinstance(datos['pulso'], int):
                raise ValueError('El pulso debe ser entero')
            if isinstance(datos['temperatura'], bool):
                raise ValueError('La temperatura debe ser numérica')
            temperatura = Decimal(str(datos['temperatura']))
            fecha = datetime.fromisoformat(datos['fecha_hora'])
            return LecturaBiometrica(
                residente_id=datos['residente_id'], pulso=datos['pulso'],
                temperatura=temperatura,
                impacto_detectado=datos['impacto_detectado'], fecha_hora=fecha)
        except (KeyError, TypeError, InvalidOperation, ValueError) as error:
            raise ValueError(f'Lectura rechazada: {error}') from error

"""Servicio de dominio: evalúa políticas académicas de riesgo."""
from dominio.objetos_valor import LecturaBiometrica, UmbralCritico


class EvaluadorRiesgo:
    def evaluar(self, lectura: LecturaBiometrica, umbral: UmbralCritico) -> set[str]:
        riesgos = set()
        if lectura.pulso < umbral.pulso_minimo or lectura.pulso > umbral.pulso_maximo:
            riesgos.add('PULSO_CRITICO')
        if lectura.temperatura > umbral.temperatura_maxima:
            riesgos.add('TEMPERATURA_ALTA')
        # En esta prueba, el dato provisto representa un indicador de caída
        # confirmado por el dispositivo de prueba; no es un detector clínico.
        if lectura.impacto_detectado:
            riesgos.add('CAIDA')
        return riesgos

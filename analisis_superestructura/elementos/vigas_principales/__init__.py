"""Análisis y diseño parametrizado de vigas I compuestas simplemente apoyadas."""

from .configuracion import validar_configuracion
from .orquestador import analizar, analizar_distribucion_parrilla, buscar_secciones, verificar

__all__ = [
    "analizar",
    "analizar_distribucion_parrilla",
    "buscar_secciones",
    "validar_configuracion",
    "verificar",
]

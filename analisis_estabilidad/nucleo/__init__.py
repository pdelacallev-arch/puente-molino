"""Configuración, contratos y orquestación comunes."""

from .configuracion import cargar_configuracion
from .contratos import EntradaElemento, ResultadoElemento

__all__ = ["EntradaElemento", "ResultadoElemento", "cargar_configuracion"]


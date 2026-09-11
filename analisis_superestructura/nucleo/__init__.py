"""Infraestructura común para configurar y orquestar elementos."""

from .motores import OBJETIVOS, VALIDADORES
from .orquestador import (
    consolidar,
    ejecutar_en_carpeta,
    ejecutar_objetivo,
    ejecutar_todos,
    obtener_ejecucion,
    ultima_ejecucion,
    validar_caso,
)

__all__ = [
    "OBJETIVOS",
    "VALIDADORES",
    "consolidar",
    "ejecutar_en_carpeta",
    "ejecutar_objetivo",
    "ejecutar_todos",
    "obtener_ejecucion",
    "ultima_ejecucion",
    "validar_caso",
]

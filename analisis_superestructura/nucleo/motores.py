"""Registro central de cálculos disponibles por elemento.

Cada objetivo declara cómo calcular, cómo serializar su resultado canónico, qué
artefactos (CSV y figuras) genera y cómo redactar su reporte Markdown. El núcleo
sólo despacha; la lógica técnica permanece en ``elementos/``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..elementos.vigas_principales.configuracion import validar_configuracion
from ..elementos.vigas_principales.orquestador import (
    analizar,
    analizar_distribucion_parrilla,
    buscar_secciones,
    verificar,
)
from ..elementos.vigas_principales.reportes.exportar import (
    analisis_a_dict,
    artefactos_analisis,
    artefactos_busqueda,
    artefactos_diseno,
    busqueda_a_dict,
    diseno_a_dict,
    reporte_analisis,
    reporte_busqueda,
    reporte_diseno,
    reporte_parrilla,
)


@dataclass(frozen=True)
class Motor:
    elemento: str
    calculo: str
    calcular: Callable[[Any], Any]
    serializar: Callable[[Any], dict]
    artefactos: Callable[[Any, Path], list[Path]]
    reporte: Callable[[Any], str]
    aplicable: Callable[[Any], bool] = lambda _config: True


def _sin_artefactos(_resultado: Any, _carpeta: Path) -> list[Path]:
    return []


def _busqueda_habilitada(config: Any) -> bool:
    return bool(config.busqueda.habilitada)


OBJETIVOS: dict[str, Motor] = {
    "vigas_principales.analisis": Motor(
        "vigas_principales",
        "analisis",
        analizar,
        analisis_a_dict,
        artefactos_analisis,
        reporte_analisis,
    ),
    "vigas_principales.parrilla": Motor(
        "vigas_principales",
        "parrilla",
        analizar_distribucion_parrilla,
        lambda resultado: resultado.resumen(),
        _sin_artefactos,
        reporte_parrilla,
    ),
    "vigas_principales.diseno": Motor(
        "vigas_principales",
        "diseno",
        verificar,
        diseno_a_dict,
        artefactos_diseno,
        reporte_diseno,
    ),
    "vigas_principales.busqueda": Motor(
        "vigas_principales",
        "busqueda",
        buscar_secciones,
        busqueda_a_dict,
        artefactos_busqueda,
        reporte_busqueda,
        _busqueda_habilitada,
    ),
}

VALIDADORES: dict[str, Callable[[str | Path], Any]] = {
    "vigas_principales": validar_configuracion,
}

"""Carga, mezcla y validación de la configuración maestra."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Seccion(BaseModel):
    model_config = ConfigDict(extra="allow")


class Proyecto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    nombre: str
    revision: str
    responsable: str | None = None


class DatosComunes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materiales: dict[str, Any]
    cargas_superestructura: dict[str, Any]
    sismo: dict[str, Any]


class Elementos(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estribo: dict[str, Any]
    pantalla: dict[str, Any]
    contrafuertes: dict[str, Any]
    zapata: dict[str, Any]
    dentellon: dict[str, Any]
    cajuela: dict[str, Any]


class TrazabilidadConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fuentes: dict[str, str] = Field(default_factory=dict)
    estado_datos: dict[str, str] = Field(default_factory=dict)


class ConfiguracionCaso(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proyecto: Proyecto
    normativa: dict[str, str]
    unidades: Literal["MKS"] = "MKS"
    datos_comunes: DatosComunes
    elementos: Elementos
    trazabilidad: TrazabilidadConfig = Field(default_factory=TrazabilidadConfig)


class ErrorConfiguracion(ValueError):
    pass


def validar_coherencia_geometrica(config: ConfiguracionCaso) -> None:
    """Impide alturas incompatibles entre el estribo y sus submodelos.

    La cota de coronación se mide desde la base de la zapata estructural y es
    ``hz + hp``. En este modelo debe coincidir con ``H``; de ello dependen la
    altura de empujes y el nivel automático de frenado (BR = H + 0.90 m).
    """
    elementos = config.elementos
    g = elementos.estribo["geometria"]
    h_total = float(g["H"])
    h_corona = float(g["hz"]) + float(g["hp"])
    tolerancia_m = 1e-6

    def exigir(nombre: str, valor: float, esperado: float) -> None:
        if abs(float(valor) - esperado) > tolerancia_m:
            raise ErrorConfiguracion(
                f"{nombre}={float(valor):.3f} m es incompatible con "
                f"{esperado:.3f} m derivado de la geometría del estribo"
            )

    exigir("elementos.estribo.geometria.H", h_total, h_corona)

    cajuela = elementos.cajuela["verificacion_voladizo"]
    exigir(
        "elementos.cajuela.verificacion_voladizo.altura_m",
        cajuela["altura_m"],
        float(g["c_cajuela"]) + float(g["d_cajuela"]),
    )
    exigir(
        "elementos.cajuela.verificacion_voladizo.altura_global_empuje_m",
        cajuela["altura_global_empuje_m"],
        h_total,
    )

    h_efectiva = float(g["hp"]) - float(g["c_cajuela"]) - float(g["d_cajuela"])
    shell = elementos.pantalla["analisis_shell_3d"]
    exigir("elementos.pantalla.analisis_shell_3d.altura_total_m", shell["altura_total_m"], float(g["hp"]))
    exigir("elementos.pantalla.analisis_shell_3d.altura_modelada_m", shell["altura_modelada_m"], h_efectiva)

    diseno_pantalla = elementos.pantalla["diseno_e060_mtc"]
    exigir("elementos.pantalla.diseno_e060_mtc.altura_total_m", diseno_pantalla["altura_total_m"], float(g["hp"]))
    exigir("elementos.pantalla.diseno_e060_mtc.altura_efectiva_m", diseno_pantalla["altura_efectiva_m"], h_efectiva)

    for calculo in ("analisis_2d", "diseno_stm"):
        exigir(
            f"elementos.contrafuertes.{calculo}.altura_m",
            elementos.contrafuertes[calculo]["altura_m"],
            h_efectiva,
        )


def cargar_configuracion(ruta: str | Path) -> tuple[ConfiguracionCaso, str]:
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8")
        datos = yaml.safe_load(texto)
        if not isinstance(datos, dict):
            raise TypeError("la raíz debe ser un objeto")
        config = ConfiguracionCaso.model_validate(datos)
        validar_coherencia_geometrica(config)
    except Exception as exc:
        raise ErrorConfiguracion(f"Configuración inválida en {ruta}: {exc}") from exc
    return config, hashlib.sha256(texto.encode("utf-8")).hexdigest()


def mezclar(base: dict[str, Any], cambios: dict[str, Any]) -> dict[str, Any]:
    """Mezcla profunda sin modificar los objetos originales."""
    salida = copy.deepcopy(base)
    for clave, valor in cambios.items():
        if isinstance(valor, dict) and isinstance(salida.get(clave), dict):
            salida[clave] = mezclar(salida[clave], valor)
        else:
            salida[clave] = copy.deepcopy(valor)
    return salida

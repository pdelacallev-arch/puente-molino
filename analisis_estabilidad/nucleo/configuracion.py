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


def cargar_configuracion(ruta: str | Path) -> tuple[ConfiguracionCaso, str]:
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8")
        datos = yaml.safe_load(texto)
        if not isinstance(datos, dict):
            raise TypeError("la raíz debe ser un objeto")
        config = ConfiguracionCaso.model_validate(datos)
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


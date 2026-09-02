"""Lectura, normalizacion, validacion y huella de configuraciones YAML."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from .modelos import Configuracion
from .unidades import normalizar_a_si


class ErrorConfiguracion(ValueError):
    """Error legible para datos de entrada invalidos."""


def cargar_yaml(ruta: str | Path) -> tuple[dict, str]:
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8")
        datos = yaml.safe_load(texto)
    except (OSError, yaml.YAMLError) as exc:
        raise ErrorConfiguracion(f"no se pudo leer {ruta}: {exc}") from exc
    if not isinstance(datos, dict):
        raise ErrorConfiguracion("la raiz del YAML debe ser un objeto")
    huella = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return datos, huella


def validar_configuracion(ruta: str | Path) -> Configuracion:
    datos, _ = cargar_yaml(ruta)
    try:
        return Configuracion.model_validate(normalizar_a_si(datos))
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        raise ErrorConfiguracion(str(exc)) from exc


def huella_configuracion(configuracion: Configuracion) -> str:
    contenido = json.dumps(
        configuracion.model_dump(mode="json"), sort_keys=True, ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(contenido).hexdigest()

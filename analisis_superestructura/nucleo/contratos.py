"""Contratos JSON comunes entre elementos de la superestructura.

Replican el criterio de ``analisis_estabilidad.nucleo.contratos``: cada cálculo
registra su entrada resuelta, su resultado y la trazabilidad de configuración.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


VERSION_ESQUEMA = "1.0"
EstadoResultado = Literal["OK", "ADVERTENCIA", "NO_CUMPLE", "ERROR", "OBSOLETO"]


class ModeloContrato(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TrazabilidadEntrada(ModeloContrato):
    configuracion_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    fuentes_por_parametro: dict[str, str] = Field(default_factory=dict)
    estados_datos: dict[str, str] = Field(default_factory=dict)


class EntradaElemento(ModeloContrato):
    version_esquema: str = VERSION_ESQUEMA
    ejecucion_id: str
    elemento: str
    calculo: str
    unidades: Literal["SI", "MKS"] = "SI"
    parametros: dict[str, Any]
    trazabilidad: TrazabilidadEntrada

    @model_validator(mode="after")
    def validar_version(self) -> "EntradaElemento":
        if self.version_esquema != VERSION_ESQUEMA:
            raise ValueError(f"Versión de entrada no soportada: {self.version_esquema}")
        return self


class ResultadoElemento(ModeloContrato):
    version_esquema: str = VERSION_ESQUEMA
    ejecucion_id: str
    elemento: str
    calculo: str
    entrada_sha256: str
    estado: EstadoResultado
    resultados: dict[str, Any]
    advertencias: list[str] = Field(default_factory=list)
    archivos_generados: list[str] = Field(default_factory=list)
    generado_en: str = Field(default_factory=lambda: datetime.now().astimezone().isoformat())


def json_canonico(datos: Any) -> str:
    if isinstance(datos, BaseModel):
        datos = datos.model_dump(mode="json")
    return json.dumps(datos, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_datos(datos: Any) -> str:
    return hashlib.sha256(json_canonico(datos).encode("utf-8")).hexdigest()


def sha256_archivo(ruta: str | Path) -> str:
    h = hashlib.sha256()
    with Path(ruta).open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def leer_entrada(ruta: str | Path) -> EntradaElemento:
    return EntradaElemento.model_validate_json(Path(ruta).read_text(encoding="utf-8"))


def leer_resultado(ruta: str | Path) -> ResultadoElemento:
    return ResultadoElemento.model_validate_json(Path(ruta).read_text(encoding="utf-8"))


def escribir_json_atomico(ruta: str | Path, datos: BaseModel | dict[str, Any]) -> Path:
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix + ".tmp")
    contenido = datos.model_dump(mode="json") if isinstance(datos, BaseModel) else datos
    temporal.write_text(
        json.dumps(contenido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporal.replace(destino)
    return destino

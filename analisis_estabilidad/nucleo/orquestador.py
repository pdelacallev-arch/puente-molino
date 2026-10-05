"""Preparación, resolución de dependencias y ejecución reproducible."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .configuracion import (
    ConfiguracionCaso,
    cargar_configuracion,
    mezclar,
    validar_coherencia_geometrica,
)
from .contratos import (
    DependenciaEntrada,
    EntradaElemento,
    TrazabilidadEntrada,
    escribir_json_atomico,
    leer_resultado,
    sha256_archivo,
    sha256_datos,
)
from .motores import MOTORES, ejecutar_entrada
from .rutas import RAIZ_ESTABILIDAD, asegurar_interna, carpeta_caso


DEPENDENCIAS: dict[str, tuple[str, ...]] = {
    "estribo.estabilidad_global": (),
    "pantalla.analisis_shell_3d": ("estribo.estabilidad_global",),
    "pantalla.reacciones_contrafuertes": ("pantalla.analisis_shell_3d",),
    "pantalla.diseno_e060_mtc": ("estribo.estabilidad_global",),
    "contrafuertes.analisis_2d": ("pantalla.reacciones_contrafuertes",),
    "contrafuertes.diseno_stm": ("contrafuertes.analisis_2d",),
    "zapata.diseno_longitudinal_e060": ("estribo.estabilidad_global",),
    "zapata.diseno_transversal_e060_mtc": ("estribo.estabilidad_global",),
    "dentellon.diseno_e060": ("estribo.estabilidad_global",),
    "cajuela.verificacion_voladizo": ("estribo.estabilidad_global",),
    "pantalla.diseno_voladizo": ("estribo.estabilidad_global",),
}


def _huella_codigo() -> str:
    h = hashlib.sha256()
    for ruta in sorted(RAIZ_ESTABILIDAD.rglob("*.py")):
        if "__pycache__" in ruta.parts:
            continue
        h.update(str(ruta.relative_to(RAIZ_ESTABILIDAD)).encode("utf-8"))
        h.update(ruta.read_bytes())
    return h.hexdigest()


def _huella_overrides(carpeta: Path) -> str:
    """Identifica el conjunto completo de ajustes particulares del caso."""
    h = hashlib.sha256()
    entradas = carpeta / "entradas"
    if entradas.exists():
        for ruta in sorted(entradas.rglob("*.override.json")):
            h.update(str(ruta.relative_to(carpeta)).encode("utf-8"))
            h.update(ruta.read_bytes())
    return h.hexdigest()


def _id_ejecucion() -> str:
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def _config_path(caso: str, revision: str) -> Path:
    return carpeta_caso(caso, revision) / "entrada.yaml"


def _indice(carpeta: Path) -> dict[str, Any]:
    ruta = carpeta / "ejecuciones" / "indice.json"
    if not ruta.exists():
        return {"version": 1, "ejecuciones": {}}
    return json.loads(ruta.read_text(encoding="utf-8"))


def obtener_ejecucion(
    caso: str, revision: str, nueva: bool = False
) -> tuple[ConfiguracionCaso, str, Path, str]:
    carpeta = carpeta_caso(caso, revision)
    config, huella_config = cargar_configuracion(_config_path(caso, revision))
    huella_codigo = _huella_codigo()
    huella_overrides = _huella_overrides(carpeta)
    huella = hashlib.sha256(
        f"{huella_config}:{huella_codigo}:{huella_overrides}".encode()
    ).hexdigest()
    indice = _indice(carpeta)
    existente = indice["ejecuciones"].get(huella)
    if existente and not nueva:
        ejecucion = asegurar_interna(carpeta / "ejecuciones" / existente)
        if ejecucion.exists():
            return config, huella_config, ejecucion, huella_codigo
    ejecuciones = carpeta / "ejecuciones"
    ejecuciones.mkdir(parents=True, exist_ok=True)
    identificador = _id_ejecucion()
    ejecucion = asegurar_interna(ejecuciones / identificador)
    contador = 1
    while ejecucion.exists():
        ejecucion = asegurar_interna(ejecuciones / f"{identificador}-{contador:02d}")
        contador += 1
    ejecucion.mkdir(parents=True)
    (ejecucion / "configuracion_resuelta.yaml").write_text(
        yaml.safe_dump(config.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    indice["ejecuciones"][huella] = ejecucion.name
    escribir_json_atomico(ejecuciones / "indice.json", indice)
    escribir_json_atomico(ejecucion / "manifiesto.json", {
        "version": 1,
        "ejecucion_id": ejecucion.name,
        "caso": caso,
        "revision": revision.upper(),
        "configuracion_sha256": huella_config,
        "overrides_sha256": huella_overrides,
        "codigo_sha256": huella_codigo,
        "modulos": {},
    })
    return config, huella_config, ejecucion, huella_codigo


def _seccion_objetivo(config: ConfiguracionCaso, objetivo: str) -> dict[str, Any]:
    elemento, calculo = objetivo.split(".", 1)
    elementos = config.elementos.model_dump(mode="python")
    if objetivo == "estribo.estabilidad_global":
        return {
            "geometria": elementos["estribo"]["geometria"],
            "falsa_zapata": elementos["estribo"]["falsa_zapata"],
            **config.datos_comunes.model_dump(mode="python"),
        }
    if objetivo == "pantalla.reacciones_contrafuertes":
        parametros = dict(elementos["pantalla"]["analisis_shell_3d"])
        parametros["altura_modelada_m"] = elementos["contrafuertes"]["analisis_2d"][
            "altura_m"
        ]
        return {"elemento": parametros}
    try:
        return {"elemento": elementos[elemento][calculo]}
    except KeyError as exc:
        raise ValueError(f"No existe configuración para {objetivo}") from exc


def _aplicar_override(caso_dir: Path, objetivo: str, parametros: dict[str, Any]) -> tuple[dict, str | None]:
    elemento, calculo = objetivo.split(".", 1)
    ruta = caso_dir / "entradas" / elemento / f"{calculo}.override.json"
    if not ruta.exists():
        return parametros, None
    cambios = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(cambios, dict):
        raise ValueError(f"El override debe ser un objeto JSON: {ruta}")
    if objetivo == "estribo.estabilidad_global":
        return mezclar(parametros, cambios), sha256_archivo(ruta)
    base = parametros["elemento"]
    return {"elemento": mezclar(base, cambios)}, sha256_archivo(ruta)


def preparar(
    objetivo: str,
    config: ConfiguracionCaso,
    huella_config: str,
    ejecucion: Path,
    dependencias: list[Path],
) -> tuple[EntradaElemento, Path]:
    if objetivo not in MOTORES:
        raise ValueError(f"Objetivo desconocido: {objetivo}")
    parametros = _seccion_objetivo(config, objetivo)
    parametros, huella_override = _aplicar_override(
        _config_path(config.proyecto.id, config.proyecto.revision).parent,
        objetivo,
        parametros,
    )
    if huella_override is not None:
        # Un override puede modificar una cota que también participa en otro
        # módulo. Se recompone el caso completo para verificar las mismas
        # relaciones geométricas que se revisan en el YAML maestro.
        datos_resueltos = config.model_dump(mode="python")
        elemento_override, calculo_override = objetivo.split(".", 1)
        if objetivo == "estribo.estabilidad_global":
            datos_resueltos["elementos"][elemento_override] = parametros
        else:
            datos_resueltos["elementos"][elemento_override][calculo_override] = (
                parametros["elemento"]
            )
        validar_coherencia_geometrica(
            ConfiguracionCaso.model_validate(datos_resueltos)
        )
    elemento, calculo = objetivo.split(".", 1)
    carpeta = asegurar_interna(ejecucion / "elementos" / elemento / calculo)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_entrada = carpeta / "entrada.json"
    contratos_dep = []
    for ruta in dependencias:
        resultado = leer_resultado(ruta)
        contratos_dep.append(DependenciaEntrada(
            elemento=resultado.elemento,
            calculo=resultado.calculo,
            resultado=os.path.relpath(ruta, ruta_entrada.parent).replace("\\", "/"),
            sha256=sha256_archivo(ruta),
        ))
    entrada = EntradaElemento(
        ejecucion_id=ejecucion.name,
        elemento=elemento,
        calculo=calculo,
        parametros=parametros,
        dependencias=contratos_dep,
        trazabilidad=TrazabilidadEntrada(
            configuracion_sha256=huella_config,
            fuentes_por_parametro=config.trazabilidad.fuentes,
            override_sha256=huella_override,
        ),
    )
    escribir_json_atomico(ruta_entrada, entrada)
    return entrada, ruta_entrada


def ejecutar_objetivo(
    objetivo: str,
    config: ConfiguracionCaso,
    huella_config: str,
    ejecucion: Path,
    cache: dict[str, Path] | None = None,
) -> Path:
    cache = {} if cache is None else cache
    if objetivo in cache:
        return cache[objetivo]
    rutas_dependencias = [
        ejecutar_objetivo(dep, config, huella_config, ejecucion, cache)
        for dep in DEPENDENCIAS[objetivo]
    ]
    entrada, ruta_entrada = preparar(
        objetivo, config, huella_config, ejecucion, rutas_dependencias
    )
    carpeta = ruta_entrada.parent
    ruta_resultado = carpeta / "resultado.json"
    if ruta_resultado.exists():
        anterior = leer_resultado(ruta_resultado)
        if anterior.entrada_sha256 == sha256_datos(entrada) and anterior.estado not in (
            "ERROR", "OBSOLETO"
        ):
            cache[objetivo] = ruta_resultado
            return ruta_resultado
    resultado = ejecutar_entrada(objetivo, ruta_entrada, carpeta)
    manifiesto_ruta = ejecucion / "manifiesto.json"
    manifiesto = json.loads(manifiesto_ruta.read_text(encoding="utf-8"))
    manifiesto["modulos"][objetivo] = {
        "estado": resultado.estado,
        "entrada": str(ruta_entrada.relative_to(ejecucion)).replace("\\", "/"),
        "resultado": str(ruta_resultado.relative_to(ejecucion)).replace("\\", "/"),
        "reporte": str((carpeta / "reporte.md").relative_to(ejecucion)).replace("\\", "/"),
        "resultado_sha256": sha256_archivo(ruta_resultado),
    }
    escribir_json_atomico(manifiesto_ruta, manifiesto)
    cache[objetivo] = ruta_resultado
    return ruta_resultado


def ejecutar(
    objetivo: str, caso: str, revision: str, nueva: bool = False
) -> tuple[Path, list[Path]]:
    config, huella, ejecucion, _ = obtener_ejecucion(caso, revision, nueva)
    objetivos = list(DEPENDENCIAS) if objetivo == "todo" else [objetivo]
    cache: dict[str, Path] = {}
    resultados = [
        ejecutar_objetivo(x, config, huella, ejecucion, cache) for x in objetivos
    ]
    return ejecucion, resultados


def consolidar(ejecucion: Path) -> Path:
    manifiesto = json.loads((ejecucion / "manifiesto.json").read_text(encoding="utf-8"))
    modulos = []
    for objetivo, registro in manifiesto["modulos"].items():
        resultado = leer_resultado(ejecucion / registro["resultado"])
        modulos.append({
            "objetivo": objetivo,
            "estado": resultado.estado,
            "advertencias": resultado.advertencias,
            "resultado": registro["resultado"],
            "reporte": registro.get("reporte"),
        })
    ruta = ejecucion / "consolidado.json"
    escribir_json_atomico(ruta, {
        "ejecucion_id": ejecucion.name,
        "configuracion_sha256": manifiesto["configuracion_sha256"],
        "modulos": modulos,
    })
    return ruta

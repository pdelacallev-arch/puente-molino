"""Despacho, ejecución reproducible y consolidación por caso.

Replica el criterio de ``analisis_estabilidad.nucleo.orquestador``: los
resultados viven junto a la entrada del caso, dentro de una carpeta de ejecución
identificada por la huella de configuración y de código.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .contratos import (
    EntradaElemento,
    ResultadoElemento,
    TrazabilidadEntrada,
    escribir_json_atomico,
    leer_resultado,
    sha256_archivo,
    sha256_datos,
)
from .motores import OBJETIVOS, VALIDADORES
from .rutas import RAIZ_SUPERESTRUCTURA, asegurar_interna, carpeta_caso, entrada_caso


def _huella_codigo() -> str:
    h = hashlib.sha256()
    for ruta in sorted(RAIZ_SUPERESTRUCTURA.rglob("*.py")):
        if "__pycache__" in ruta.parts or ".tmp" in ruta.parts:
            continue
        h.update(str(ruta.relative_to(RAIZ_SUPERESTRUCTURA)).encode("utf-8"))
        h.update(ruta.read_bytes())
    return h.hexdigest()


def _id_ejecucion() -> str:
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def _indice(carpeta: Path) -> dict[str, Any]:
    ruta = carpeta / "ejecuciones" / "indice.json"
    if not ruta.exists():
        return {"version": 1, "ejecuciones": {}}
    return json.loads(ruta.read_text(encoding="utf-8"))


def validar_caso(elemento: str, caso: str, revision: str) -> Any:
    try:
        validador = VALIDADORES[elemento]
    except KeyError as exc:
        raise ValueError(f"Elemento desconocido: {elemento}") from exc
    return validador(entrada_caso(caso, revision))


def ultima_ejecucion(caso: str, revision: str) -> Path:
    """Devuelve la ejecución existente más reciente del caso."""
    ejecuciones = carpeta_caso(caso, revision) / "ejecuciones"
    carpetas = (
        sorted((p for p in ejecuciones.iterdir() if p.is_dir()), key=lambda p: p.name)
        if ejecuciones.exists()
        else []
    )
    if not carpetas:
        raise FileNotFoundError(
            f"No hay ejecuciones para el caso {caso} / {revision}; ejecute primero"
        )
    return carpetas[-1]


def obtener_ejecucion(
    caso: str,
    revision: str,
    elemento: str = "vigas_principales",
    nueva: bool = False,
) -> tuple[Any, str, Path, str]:
    """Resuelve o crea la carpeta de ejecución compatible con el caso."""
    carpeta = carpeta_caso(caso, revision)
    ruta_config = entrada_caso(caso, revision)
    config = validar_caso(elemento, caso, revision)
    huella_config = sha256_archivo(ruta_config)
    huella_codigo = _huella_codigo()
    huella = hashlib.sha256(f"{huella_config}:{huella_codigo}".encode()).hexdigest()
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
        "revision": revision,
        "configuracion_sha256": huella_config,
        "codigo_sha256": huella_codigo,
        "modulos": {},
    })
    return config, huella_config, ejecucion, huella_codigo


def preparar(
    objetivo: str,
    config: Any,
    huella_config: str,
    ejecucion: Path,
) -> tuple[EntradaElemento, Path]:
    motor = OBJETIVOS[objetivo]
    carpeta = asegurar_interna(ejecucion / "elementos" / motor.elemento / motor.calculo)
    carpeta.mkdir(parents=True, exist_ok=True)
    entrada = EntradaElemento(
        ejecucion_id=ejecucion.name,
        elemento=motor.elemento,
        calculo=motor.calculo,
        unidades=config.proyecto.sistema_unidades,
        parametros=config.model_dump(mode="json"),
        trazabilidad=TrazabilidadEntrada(
            configuracion_sha256=huella_config,
            fuentes_por_parametro=dict(config.fuentes),
            estados_datos=dict(config.estados_datos),
        ),
    )
    ruta_entrada = carpeta / "entrada.json"
    escribir_json_atomico(ruta_entrada, entrada)
    return entrada, ruta_entrada


def _estado(resultado: dict[str, Any], calculo: str) -> str:
    if calculo == "busqueda":
        return "OK" if resultado.get("factibles") else "NO_CUMPLE"
    estado = str(resultado.get("estado", "")).upper()
    if "NO_CUMPLE" in estado or "NO CUMPLE" in estado:
        return "NO_CUMPLE"
    if "CONDICIONAL" in estado:
        return "ADVERTENCIA"
    advertencias = resultado.get("advertencias", [])
    return "ADVERTENCIA" if advertencias else "OK"


def ejecutar_en_carpeta(
    objetivo: str,
    config: Any,
    huella_config: str,
    ejecucion: Path,
) -> tuple[ResultadoElemento, Path]:
    """Ejecuta un cálculo y escribe entrada, resultado, reporte y artefactos."""
    motor = OBJETIVOS[objetivo]
    entrada, ruta_entrada = preparar(objetivo, config, huella_config, ejecucion)
    carpeta = ruta_entrada.parent
    resultado_obj = motor.calcular(config)
    resultado_dict = motor.serializar(resultado_obj)
    archivos = motor.artefactos(resultado_obj, carpeta)
    contrato = ResultadoElemento(
        ejecucion_id=ejecucion.name,
        elemento=motor.elemento,
        calculo=motor.calculo,
        entrada_sha256=sha256_datos(entrada),
        estado=_estado(resultado_dict, motor.calculo),
        resultados=resultado_dict,
        advertencias=[str(x) for x in resultado_dict.get("advertencias", [])],
        archivos_generados=[
            str(x.relative_to(carpeta)).replace("\\", "/") for x in archivos
        ],
    )
    ruta_resultado = escribir_json_atomico(carpeta / "resultado.json", contrato)
    (carpeta / "reporte.md").write_text(motor.reporte(resultado_obj), encoding="utf-8")
    return contrato, ruta_resultado


def _registrar_modulo(
    ejecucion: Path, objetivo: str, contrato: ResultadoElemento, ruta_resultado: Path
) -> None:
    manifiesto_ruta = ejecucion / "manifiesto.json"
    manifiesto = json.loads(manifiesto_ruta.read_text(encoding="utf-8"))
    carpeta = ruta_resultado.parent
    manifiesto["modulos"][objetivo] = {
        "estado": contrato.estado,
        "entrada": str((carpeta / "entrada.json").relative_to(ejecucion)).replace("\\", "/"),
        "resultado": str(ruta_resultado.relative_to(ejecucion)).replace("\\", "/"),
        "reporte": str((carpeta / "reporte.md").relative_to(ejecucion)).replace("\\", "/"),
        "resultado_sha256": sha256_archivo(ruta_resultado),
    }
    escribir_json_atomico(manifiesto_ruta, manifiesto)


def ejecutar_objetivo(
    objetivo: str,
    caso: str,
    revision: str,
    nueva: bool = False,
) -> tuple[ResultadoElemento, Path]:
    if objetivo not in OBJETIVOS:
        raise ValueError(f"Objetivo desconocido: {objetivo}")
    motor = OBJETIVOS[objetivo]
    config, huella_config, ejecucion, _ = obtener_ejecucion(
        caso, revision, motor.elemento, nueva
    )
    contrato, ruta_resultado = ejecutar_en_carpeta(
        objetivo, config, huella_config, ejecucion
    )
    _registrar_modulo(ejecucion, objetivo, contrato, ruta_resultado)
    return contrato, ejecucion


def ejecutar_todos(caso: str, revision: str, nueva: bool = False) -> Path:
    config, huella_config, ejecucion, _ = obtener_ejecucion(
        caso, revision, "vigas_principales", nueva
    )
    for objetivo, motor in OBJETIVOS.items():
        if not motor.aplicable(config):
            continue
        contrato, ruta_resultado = ejecutar_en_carpeta(
            objetivo, config, huella_config, ejecucion
        )
        _registrar_modulo(ejecucion, objetivo, contrato, ruta_resultado)
    return ejecucion


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

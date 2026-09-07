"""Interfaz general del sistema de estabilidad."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .nucleo.configuracion import ErrorConfiguracion, cargar_configuracion
from .nucleo.orquestador import (
    DEPENDENCIAS,
    consolidar,
    ejecutar,
    ejecutar_objetivo,
    obtener_ejecucion,
    preparar,
)
from .nucleo.rutas import carpeta_caso


ALIAS = {
    "estribo.estabilidad": "estribo.estabilidad_global",
    "pantalla.shell": "pantalla.analisis_shell_3d",
    "pantalla.reacciones": "pantalla.reacciones_contrafuertes",
    "pantalla.diseno": "pantalla.diseno_e060_mtc",
    "contrafuertes.analisis": "contrafuertes.analisis_2d",
    "contrafuertes.diseno": "contrafuertes.diseno_stm",
    "zapata.longitudinal": "zapata.diseno_longitudinal_e060",
    "zapata.transversal": "zapata.diseno_transversal_e060_mtc",
    "dentellon.diseno": "dentellon.diseno_e060",
    "cajuela.verificacion": "cajuela.verificacion_voladizo",
}


def _objetivo(valor: str) -> str:
    objetivo = ALIAS.get(valor, valor)
    if objetivo != "todo" and objetivo not in DEPENDENCIAS:
        raise argparse.ArgumentTypeError(f"objetivo desconocido: {valor}")
    return objetivo


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Análisis de estabilidad por elementos")
    sub = parser.add_subparsers(dest="comando", required=True)
    for nombre in ("validar", "estado", "consolidar"):
        p = sub.add_parser(nombre)
        p.add_argument("--caso", required=True)
        p.add_argument("--revision", required=True)
    for nombre in ("preparar", "ejecutar"):
        p = sub.add_parser(nombre)
        p.add_argument("objetivo", type=_objetivo)
        p.add_argument("--caso", required=True)
        p.add_argument("--revision", required=True)
        p.add_argument("--nueva-ejecucion", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = crear_parser().parse_args(argv)
    try:
        if args.comando == "validar":
            config, huella = cargar_configuracion(
                carpeta_caso(args.caso, args.revision) / "entrada.yaml"
            )
            print(json.dumps({
                "estado": "VALIDA",
                "proyecto": config.proyecto.id,
                "revision": config.proyecto.revision,
                "sha256": huella,
            }, ensure_ascii=False, indent=2))
            return 0
        config, huella, ejecucion, _ = obtener_ejecucion(
            args.caso, args.revision, getattr(args, "nueva_ejecucion", False)
        )
        if args.comando == "preparar":
            rutas = [
                ejecutar_objetivo(dep, config, huella, ejecucion)
                for dep in DEPENDENCIAS[args.objetivo]
            ]
            _, ruta = preparar(args.objetivo, config, huella, ejecucion, rutas)
            print(json.dumps({"estado": "PREPARADA", "entrada": str(ruta)}, indent=2))
            return 0
        if args.comando == "ejecutar":
            ejecucion, resultados = ejecutar(
                args.objetivo, args.caso, args.revision, args.nueva_ejecucion
            )
            print(json.dumps({
                "estado": "EJECUTADO",
                "ejecucion": str(ejecucion),
                "resultados": [str(x) for x in resultados],
            }, ensure_ascii=False, indent=2))
            return 0
        if args.comando == "consolidar":
            ruta = consolidar(ejecucion)
            print(json.dumps({"estado": "CONSOLIDADO", "resultado": str(ruta)}, indent=2))
            return 0
        manifiesto = ejecucion / "manifiesto.json"
        print(manifiesto.read_text(encoding="utf-8"))
        return 0
    except Exception as exc:
        print(json.dumps({"estado": "ERROR", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Interfaz general del sistema modular de superestructura."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .nucleo.motores import OBJETIVOS, VALIDADORES
from .nucleo.orquestador import (
    consolidar,
    ejecutar_objetivo,
    ejecutar_todos,
    ultima_ejecucion,
    validar_caso,
)


def _objetivo(valor: str) -> str:
    if valor != "todo" and valor not in OBJETIVOS:
        raise argparse.ArgumentTypeError(f"objetivo desconocido: {valor}")
    return valor


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Análisis de superestructura por elementos")
    sub = parser.add_subparsers(dest="comando", required=True)

    validar = sub.add_parser("validar")
    validar.add_argument("--elemento", choices=sorted(VALIDADORES), required=True)
    validar.add_argument("--caso", required=True)
    validar.add_argument("--revision", required=True)

    ejecutar = sub.add_parser("ejecutar")
    ejecutar.add_argument("objetivo", type=_objetivo)
    ejecutar.add_argument("--caso", required=True)
    ejecutar.add_argument("--revision", required=True)
    ejecutar.add_argument("--nueva-ejecucion", action="store_true")

    for nombre in ("consolidar", "estado"):
        p = sub.add_parser(nombre)
        p.add_argument("--caso", required=True)
        p.add_argument("--revision", required=True)

    sub.add_parser("objetivos")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = crear_parser().parse_args(argv)
    try:
        if args.comando == "objetivos":
            print(json.dumps({"objetivos": sorted(OBJETIVOS)}, indent=2))
            return 0
        if args.comando == "validar":
            config = validar_caso(args.elemento, args.caso, args.revision)
            print(json.dumps({
                "estado": "VALIDA",
                "elemento": args.elemento,
                "proyecto": config.proyecto.id,
                "revision": config.proyecto.revision,
            }, ensure_ascii=False, indent=2))
            return 0
        if args.comando == "ejecutar":
            if args.objetivo == "todo":
                ejecucion = ejecutar_todos(args.caso, args.revision, args.nueva_ejecucion)
                print(json.dumps({
                    "estado": "EJECUTADO",
                    "ejecucion": str(ejecucion),
                }, ensure_ascii=False, indent=2))
                return 0
            contrato, ejecucion = ejecutar_objetivo(
                args.objetivo, args.caso, args.revision, args.nueva_ejecucion
            )
            print(json.dumps({
                "estado": contrato.estado,
                "objetivo": args.objetivo,
                "ejecucion": str(ejecucion),
            }, ensure_ascii=False, indent=2))
            return 1 if contrato.estado == "NO_CUMPLE" else 0
        if args.comando == "consolidar":
            ejecucion = ultima_ejecucion(args.caso, args.revision)
            ruta = consolidar(ejecucion)
            print(json.dumps({"estado": "CONSOLIDADO", "resultado": str(ruta)}, indent=2))
            return 0
        ejecucion = ultima_ejecucion(args.caso, args.revision)
        manifiesto = ejecucion / "manifiesto.json"
        print(manifiesto.read_text(encoding="utf-8"))
        return 0
    except Exception as exc:
        print(json.dumps({"estado": "ERROR", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

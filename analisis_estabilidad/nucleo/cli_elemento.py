"""CLI de bajo nivel para ejecutar un elemento con contratos explícitos."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .motores import ejecutar_entrada


def main_elemento(elemento: str, calculos: tuple[str, ...]) -> int:
    parser = argparse.ArgumentParser(
        description=f"Ejecución independiente del elemento {elemento}"
    )
    parser.add_argument("calculo", choices=calculos)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    objetivo = f"{elemento}.{args.calculo}"
    try:
        resultado = ejecutar_entrada(objetivo, args.entrada, args.salida)
    except Exception as exc:
        print(json.dumps({"estado": "ERROR", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({
        "estado": resultado.estado,
        "resultado": str((args.salida / "resultado.json").resolve()),
    }, ensure_ascii=False, indent=2))
    return 1 if resultado.estado == "NO_CUMPLE" else 0


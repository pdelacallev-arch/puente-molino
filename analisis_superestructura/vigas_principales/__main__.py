"""Interfaz de línea de comandos."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .configuracion import ErrorConfiguracion, huella_configuracion, validar_configuracion
from .orquestador import analizar, buscar_secciones, verificar
from .reportes.exportar import exportar_analisis, exportar_busqueda, exportar_diseno


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vigas principales compuestas - MTC 2018")
    sub = parser.add_subparsers(dest="comando", required=True)
    for comando in ("validate", "analyze", "design"):
        p = sub.add_parser(comando)
        p.add_argument("configuracion", type=Path)
        if comando != "validate":
            p.add_argument("--output", type=Path, default=Path("outputs/vigas_principales"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = crear_parser().parse_args(argv)
    try:
        config = validar_configuracion(args.configuracion)
    except ErrorConfiguracion as exc:
        print(f"CONFIGURACION INVALIDA\n{exc}")
        return 2
    if args.comando == "validate":
        print(json.dumps({"estado": "VALIDA", "sha256": huella_configuracion(config)}, indent=2))
        return 0
    if args.comando == "analyze":
        resultado = analizar(config)
        salida = exportar_analisis(resultado, args.output)
        print(json.dumps({"estado": "ANALIZADO", "salida": str(salida), "equilibrio": resultado.equilibrio_relativo}, indent=2))
        return 0
    diseno = verificar(config)
    salida = exportar_diseno(diseno, args.output)
    respuesta = {"estado": diseno.estado, "salida": str(salida), "dcr_gobernante": diseno.estado_gobernante.dcr}
    estado_salida = diseno.estado
    if config.busqueda.habilitada:
        busqueda = buscar_secciones(config)
        exportar_busqueda(busqueda, salida)
        respuesta["busqueda"] = {"evaluados": busqueda.evaluados, "factibles": len(busqueda.factibles), "truncado": busqueda.truncado}
        if busqueda.factibles:
            optima = busqueda.factibles[0]
            estado_salida = optima.estado
            respuesta["estado_optimo"] = optima.estado
            respuesta["dcr_optimo"] = optima.maximo_dcr
            respuesta["masa_optima_kg"] = optima.masa_kg
        else:
            estado_salida = "NO_CUMPLE"
            respuesta["estado_optimo"] = "SIN_ALTERNATIVA_FACTIBLE"
    print(json.dumps(respuesta, indent=2, ensure_ascii=False))
    return 1 if estado_salida == "NO_CUMPLE" else 0


if __name__ == "__main__":
    raise SystemExit(main())

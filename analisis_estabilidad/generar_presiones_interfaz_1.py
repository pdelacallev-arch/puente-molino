#!/usr/bin/env python3
"""Genera los diagramas de presión de todos los estados de la interfaz 1.

La interfaz 1 corresponde al contacto entre la zapata estructural y la falsa
zapata. El cálculo y la auditoría de equilibrio se toman del modelo central;
este archivo es un ejecutable dedicado que produce los cuatro PNG de una vez.

Uso::

    python analisis_estabilidad/generar_presiones_interfaz_1.py
    python analisis_estabilidad/generar_presiones_interfaz_1.py --dpi 200
"""

from __future__ import annotations

import argparse
from pathlib import Path

if __package__ in (None, ""):
    from dibujar_presiones_interfaces import draw_interface
else:
    from .dibujar_presiones_interfaces import draw_interface


CASOS = (
    "servicio-i",
    "resistencia-ia",
    "resistencia-ib",
    "evento-extremo-i",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Genera los cuatro diagramas de presión de la interfaz 1 "
            "(zapata estructural/falsa zapata)."
        )
    )
    parser.add_argument(
        "--directorio-salida",
        type=Path,
        default=Path("imagenes"),
        help="Carpeta de los PNG (predeterminado: imagenes).",
    )
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    args.directorio_salida.mkdir(parents=True, exist_ok=True)
    for caso in CASOS:
        args.caso = caso
        args.salida = str(
            args.directorio_salida / f"presiones_interfaz_1_{caso}.png"
        )
        draw_interface(args, interface_number=1)

    print(
        f"Generación terminada: {len(CASOS)} estados límite de la interfaz 1."
    )


if __name__ == "__main__":
    main()

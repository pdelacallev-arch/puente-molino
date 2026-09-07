#!/usr/bin/env python3
"""
Dibujo del estribo - Figura 3.44
================================

Genera una figura limpia del estribo en voladizo usando directamente los
parametros de `agente_subestructura.py`.

La orientacion del dibujo replica la Figura 3.44 de la referencia:
    - B1 queda a la izquierda.
    - B2 queda a la derecha.

El agente de estabilidad usa el eje horizontal desde la punta hacia el talon.
Por eso, para calculo de brazos, esta figura es el espejo horizontal del eje
interno de `agente_subestructura.py`.

Uso:
    python dibujar_estribo.py
    python dibujar_estribo.py --salida imagenes/figura_3.44_estribo.png
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import Polygon
import numpy as np

from .estabilidad_global import (
    GEOM,
    LOADS,
    SubstructureAnalysis,
    MAT,
    SEISMIC,
    cajuela_area_and_centroid,
    fill_trapezoid_area_and_centroid,
)


CONCRETE_FILL = "#d9e2ec"
CONCRETE_EDGE = "#1f2933"
SOIL_FILL = "#f3dfb6"
SOIL_EDGE = "#b08945"
SOIL_DOT = "#8a6f3d"
DIM_COLOR = "#111827"
SECONDARY_DIM = "#374151"
RED = "#991b1b"
GREEN = "#166534"
BLUE = "#1e3a8a"


def m(value: float) -> str:
    """Formato compacto en metros."""
    return f"{value:.2f}".rstrip("0").rstrip(".")


def close_poly(points: Iterable[tuple[float, float]]) -> np.ndarray:
    pts = np.array(list(points), dtype=float)
    return np.vstack([pts, pts[0]])


def polygon_area(points: Iterable[tuple[float, float]]) -> float:
    pts = np.array(list(points), dtype=float)
    x = pts[:, 0]
    y = pts[:, 1]
    return abs(0.5 * np.dot(x, np.roll(y, -1)) - 0.5 * np.dot(y, np.roll(x, -1)))


def dimension_h(
    ax,
    x1: float,
    x2: float,
    y: float,
    label: str,
    *,
    color: str = DIM_COLOR,
    text_dy: float = -0.16,
    ext_to: float | None = None,
    fontsize: int = 8,
    weight: str = "normal",
    above: bool = False,
) -> None:
    """Cota horizontal con flechas y lineas auxiliares."""
    dy = abs(text_dy)
    text_y = y + dy if above else y - dy
    va = "bottom" if above else "top"
    ax.annotate(
        "",
        xy=(x1, y),
        xytext=(x2, y),
        arrowprops=dict(arrowstyle="<->", color=color, lw=0.9, shrinkA=0, shrinkB=0),
        zorder=5,
    )
    if ext_to is not None:
        for x in (x1, x2):
            ax.plot([x, x], [ext_to, y], color=color, lw=0.55, ls=":", zorder=1)
    ax.text(
        (x1 + x2) / 2,
        text_y,
        label,
        ha="center",
        va=va,
        fontsize=fontsize,
        color=color,
        fontweight=weight,
        bbox=dict(facecolor="white", edgecolor="none", pad=0.8, alpha=0.92),
        zorder=6,
    )


def dimension_v(
    ax,
    x: float,
    y1: float,
    y2: float,
    label: str,
    *,
    color: str = DIM_COLOR,
    text_dx: float = 0.16,
    ext_to: float | None = None,
    fontsize: int = 8,
    weight: str = "normal",
    side: str = "right",
) -> None:
    """Cota vertical con flechas y lineas auxiliares."""
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y2),
        arrowprops=dict(arrowstyle="<->", color=color, lw=0.9, shrinkA=0, shrinkB=0),
        zorder=5,
    )
    if ext_to is not None:
        for y in (y1, y2):
            ax.plot([ext_to, x], [y, y], color=color, lw=0.55, ls=":", zorder=1)
    sign = 1 if side == "right" else -1
    ha = "left" if side == "right" else "right"
    ax.text(
        x + sign * abs(text_dx),
        (y1 + y2) / 2,
        label,
        ha=ha,
        va="center",
        fontsize=fontsize,
        color=color,
        fontweight=weight,
        rotation=90,
        bbox=dict(facecolor="white", edgecolor="none", pad=0.8, alpha=0.92),
        zorder=6,
    )


def add_part_label(ax, x: float, y: float, text: str, fontsize: int = 8) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#334e68",
        fontweight="bold",
        fontstyle="italic",
        bbox=dict(facecolor=CONCRETE_FILL, edgecolor="none", pad=1.0, alpha=0.75),
        zorder=7,
    )


def add_soil_label(ax, x: float, y: float, text: str, fontsize: int = 8) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#6b4e16",
        fontweight="bold",
        fontstyle="italic",
        bbox=dict(facecolor=SOIL_FILL, edgecolor="none", pad=1.2, alpha=0.70),
        zorder=2,
    )


def draw_soil_texture(ax, points: Iterable[tuple[float, float]]) -> None:
    """Dibuja puntos de suelo dentro del poligono de relleno."""
    pts = np.array(list(points), dtype=float)
    path = MplPath(pts)
    xmin, ymin = pts.min(axis=0)
    xmax, ymax = pts.max(axis=0)
    xs = np.arange(xmin + 0.22, xmax, 0.42)
    ys = np.arange(ymin + 0.22, ymax, 0.42)
    grid = np.array([(x, y) for y in ys for x in xs])
    if grid.size == 0:
        return
    inside = grid[path.contains_points(grid)]
    ax.scatter(
        inside[:, 0],
        inside[:, 1],
        s=3.0,
        color=SOIL_DOT,
        alpha=0.35,
        linewidths=0,
        zorder=1.6,
    )


def build_geometry(g=GEOM) -> dict:
    """Coordenadas con orientacion igual a la Figura 3.44."""
    y_footing_top = g.hz
    y_stem_top = g.hz + max(g.hp - (g.c_cajuela + g.d_cajuela), 0.0)
    y_cajuela_base_top = y_stem_top + g.d_cajuela
    y_top = g.hz + g.hp

    x_stem_back_bottom = g.B1
    x_stem_front_bottom = g.B1 + g.tp2
    x_stem_back_top = g.B1
    x_stem_front_top = g.B1 + g.tp1

    x_cajuela_base_left = x_stem_back_top - g.e_cajuela
    x_cajuela_base_right = x_stem_front_top + g.f_cajuela
    x_wall_left = x_cajuela_base_left
    x_wall_right = x_wall_left + g.b_cajuela

    zapata = [
        (0.0, 0.0),
        (g.B, 0.0),
        (g.B, y_footing_top),
        (0.0, y_footing_top),
    ]
    tronco = [
        (x_stem_back_bottom, y_footing_top),
        (x_stem_front_bottom, y_footing_top),
        (x_stem_front_top, y_stem_top),
        (x_stem_back_top, y_stem_top),
    ]
    cajuela_base = [
        (x_cajuela_base_left, y_stem_top),
        (x_cajuela_base_right, y_stem_top),
        (x_cajuela_base_right, y_cajuela_base_top),
        (x_cajuela_base_left, y_cajuela_base_top),
    ]
    cajuela_pared = [
        (x_wall_left, y_cajuela_base_top),
        (x_wall_right, y_cajuela_base_top),
        (x_wall_right, y_top),
        (x_wall_left, y_top),
    ]
    x_relleno_top = max(g.B1 - g.back_face_slope * g.hp, 0.0)
    relleno_ev = [
        (0.0, y_footing_top),
        (x_stem_back_bottom, y_footing_top),
        (x_relleno_top, y_top),
        (0.0, y_top),
    ]
    x_relleno_visible_top = min(x_cajuela_base_left, x_relleno_top)
    relleno_visible = [
        (0.0, y_footing_top),
        (x_stem_back_bottom, y_footing_top),
        (x_stem_back_top, y_stem_top),
        (x_cajuela_base_left, y_stem_top),
        (x_relleno_visible_top, y_top),
        (0.0, y_top),
    ]

    return {
        "y_footing_top": y_footing_top,
        "y_stem_top": y_stem_top,
        "y_cajuela_base_top": y_cajuela_base_top,
        "y_top": y_top,
        "x_stem_back_bottom": x_stem_back_bottom,
        "x_stem_front_bottom": x_stem_front_bottom,
        "x_stem_back_top": x_stem_back_top,
        "x_stem_front_top": x_stem_front_top,
        "x_cajuela_base_left": x_cajuela_base_left,
        "x_cajuela_base_right": x_cajuela_base_right,
        "x_wall_left": x_wall_left,
        "x_wall_right": x_wall_right,
        "x_relleno_top": x_relleno_top,
        "x_relleno_visible_top": x_relleno_visible_top,
        "zapata": zapata,
        "tronco": tronco,
        "cajuela_base": cajuela_base,
        "cajuela_pared": cajuela_pared,
        "relleno_ev": relleno_ev,
        "relleno_visible": relleno_visible,
    }


def draw_estribo(ax, g=GEOM) -> None:
    geo = build_geometry(g)

    ax.set_aspect("equal")
    ax.set_xlim(-1.15, g.B + 1.35)
    ax.set_ylim(-1.05, geo["y_top"] + 0.95)
    ax.axis("off")

    # Relleno sobre el talon B1. La muesca evita invadir visualmente la
    # cajuela; la envolvente EV analitica se verifica aparte.
    ax.add_patch(
        Polygon(
            geo["relleno_visible"],
            closed=True,
            facecolor=SOIL_FILL,
            edgecolor=SOIL_EDGE,
            linewidth=0.8,
            alpha=0.82,
            zorder=1,
            )
    )
    draw_soil_texture(ax, geo["relleno_visible"])
    relleno_centroid_x = geo["x_cajuela_base_left"] * 0.48
    add_soil_label(
        ax,
        relleno_centroid_x,
        geo["y_footing_top"] + g.hp * 0.52,
        "RELLENO\nSOBRE TALON",
        fontsize=8,
    )

    # Concreto.
    for key in ("zapata", "tronco", "cajuela_base", "cajuela_pared"):
        points = geo[key]
        ax.add_patch(
            Polygon(
                points,
                closed=True,
                facecolor=CONCRETE_FILL,
                edgecolor=CONCRETE_EDGE,
                linewidth=1.4,
                zorder=3,
            )
        )

    # Linea exterior mas marcada.
    for key in ("zapata", "tronco", "cajuela_base", "cajuela_pared"):
        pts = close_poly(geo[key])
        ax.plot(pts[:, 0], pts[:, 1], color=CONCRETE_EDGE, lw=1.0, zorder=4)

    # Rayado suave de concreto, recortado visualmente por poligonos simples.
    for key in ("zapata", "tronco", "cajuela_base", "cajuela_pared"):
        pts = np.array(geo[key])
        xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
        ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
        for x in np.arange(xmin + 0.16, xmax, 0.36):
            ax.plot(
                [x, min(x + 0.22, xmax)],
                [ymin + 0.05, min(ymin + 0.24, ymax - 0.04)],
                color="#9fb3c8",
                lw=0.35,
                alpha=0.65,
                zorder=4,
            )

    # Etiquetas internas.
    add_part_label(ax, g.B / 2, g.hz / 2, "ZAPATA")
    add_part_label(
        ax,
        (geo["x_stem_back_bottom"] + geo["x_stem_front_bottom"]) / 2 + 0.10,
        (g.hz + geo["y_stem_top"]) / 2,
        "PANTALLA",
    )
    add_part_label(
        ax,
        (geo["x_cajuela_base_left"] + geo["x_cajuela_base_right"]) / 2,
        geo["y_stem_top"] + g.d_cajuela / 2,
        "CAJUELA",
    )

    # Cotas horizontales en zapata.
    y_base_dim = -0.35
    dimension_h(
        ax,
        0,
        geo["x_stem_back_bottom"],
        y_base_dim,
        f"B1 = {m(g.B1)} m",
        color=GREEN,
        ext_to=0,
        fontsize=8,
    )
    dimension_h(
        ax,
        geo["x_stem_back_bottom"],
        geo["x_stem_front_bottom"],
        y_base_dim - 0.38,
        f"tp2 = {m(g.tp2)} m",
        color=GREEN,
        ext_to=0,
        fontsize=7,
    )
    dimension_h(
        ax,
        geo["x_stem_front_bottom"],
        g.B,
        y_base_dim,
        f"B2 = {m(g.B2)} m",
        color=GREEN,
        ext_to=0,
        fontsize=8,
    )
    dimension_h(
        ax,
        0,
        g.B,
        y_base_dim - 0.78,
        f"B = {m(g.B)} m",
        color=BLUE,
        ext_to=0,
        fontsize=9,
        weight="bold",
    )

    # Cotas verticales principales.
    x_dim_right = g.B + 0.45
    dimension_v(
        ax,
        x_dim_right,
        0,
        geo["y_top"],
        f"H = {m(g.H)} m",
        color=BLUE,
        ext_to=g.B,
        fontsize=9,
        weight="bold",
    )
    dimension_v(
        ax,
        x_dim_right - 0.45,
        geo["y_footing_top"],
        geo["y_top"],
        f"hp = {m(g.hp)} m",
        color=GREEN,
        ext_to=g.B,
        fontsize=8,
    )
    dimension_v(
        ax,
        x_dim_right - 0.90,
        0,
        geo["y_footing_top"],
        f"hz = {m(g.hz)} m",
        color=GREEN,
        ext_to=g.B,
        fontsize=8,
    )

    # Cotas de cajuela.
    y_top_1 = geo["y_top"] + 0.18
    y_top_2 = geo["y_top"] + 0.46
    y_top_3 = geo["y_top"] + 0.74
    dimension_h(
        ax,
        geo["x_wall_left"],
        geo["x_wall_right"],
        y_top_1,
        f"b = {m(g.b_cajuela)} m",
        color=RED,
        ext_to=geo["y_top"],
        fontsize=7,
        above=True,
    )
    dimension_h(
        ax,
        geo["x_wall_right"],
        geo["x_wall_right"] + g.a_cajuela,
        y_top_2,
        f"a = {m(g.a_cajuela)} m",
        color=RED,
        ext_to=geo["y_top"],
        fontsize=7,
        above=True,
    )
    dimension_h(
        ax,
        geo["x_stem_back_top"],
        geo["x_stem_front_top"],
        y_top_1,
        f"tp1 = {m(g.tp1)} m",
        color=RED,
        ext_to=geo["y_stem_top"],
        fontsize=7,
    )
    dimension_h(
        ax,
        geo["x_cajuela_base_left"],
        geo["x_stem_back_top"],
        geo["y_stem_top"] - 0.18,
        f"e = {m(g.e_cajuela)} m",
        color=RED,
        ext_to=geo["y_stem_top"],
        fontsize=7,
    )
    dimension_h(
        ax,
        geo["x_stem_front_top"],
        geo["x_cajuela_base_right"],
        geo["y_stem_top"] - 0.18,
        f"f = {m(g.f_cajuela)} m",
        color=RED,
        ext_to=geo["y_stem_top"],
        fontsize=7,
    )
    dimension_h(
        ax,
        geo["x_wall_right"],
        geo["x_wall_right"] + g.g_cajuela,
        geo["y_cajuela_base_top"] + g.c_cajuela * 0.58,
        f"g = {m(g.g_cajuela)} m",
        color=RED,
        fontsize=7,
        above=True,
    )
    dimension_v(
        ax,
        geo["x_wall_left"] - 0.28,
        geo["y_cajuela_base_top"],
        geo["y_top"],
        f"c = {m(g.c_cajuela)} m",
        color=RED,
        ext_to=geo["x_wall_left"],
        fontsize=7,
        side="left",
    )
    dimension_v(
        ax,
        geo["x_wall_left"] - 0.28,
        geo["y_stem_top"],
        geo["y_cajuela_base_top"],
        f"d = {m(g.d_cajuela)} m",
        color=RED,
        ext_to=geo["x_wall_left"],
        fontsize=7,
        side="left",
    )

    # Indicacion discreta del punto de volteo del agente.
    ax.plot([g.B], [0], marker="o", ms=4, color="#dc2626", zorder=8)
    ax.text(
        g.B + 0.05,
        -0.08,
        "O (punta en el eje de calculo)",
        ha="left",
        va="top",
        fontsize=6.5,
        color="#dc2626",
    )

    # Titulo y nota.
    ax.text(
        g.B / 2,
        geo["y_top"] + 0.88,
        "Figura 3.44: Dimensionamiento del estribo",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
        color="#111827",
    )
    ax.text(
        0,
        geo["y_top"] + 0.70,
        "Parametros importados desde agente_subestructura.GEOM",
        ha="left",
        va="bottom",
        fontsize=7,
        color="#4b5563",
    )


def verification_lines(g=GEOM) -> list[str]:
    """Resumen de consistencia entre dibujo y agente."""
    geo = build_geometry(g)
    a_zapata = polygon_area(geo["zapata"])
    a_tronco = polygon_area(geo["tronco"])
    a_cajuela_base = polygon_area(geo["cajuela_base"])
    a_cajuela_pared = polygon_area(geo["cajuela_pared"])
    a_relleno_envolvente = polygon_area(geo["relleno_ev"])
    a_relleno_visible = polygon_area(geo["relleno_visible"])
    a_dc_dibujo = a_zapata + a_tronco + a_cajuela_base + a_cajuela_pared

    a_cajuela, brazo_cajuela, y_cajuela = cajuela_area_and_centroid(g, LOADS.brazo_super)
    a_relleno, brazo_relleno, w_top = fill_trapezoid_area_and_centroid(
        g.B1,
        g.hp,
        g.back_face_slope,
        g.B2,
        g.tp2,
        cajuela_recess=g.e_cajuela,
        cajuela_height=g.c_cajuela + g.d_cajuela,
    )
    analysis = SubstructureAnalysis(g, MAT, LOADS, SEISMIC)
    weights = analysis.compute_weights_and_moments()
    a_dc_agente = sum(item["peso"] for item in weights["detail"] if item["tipo"] == "DC") / MAT.gamma_c
    a_ls = 0.61 * w_top

    checks = [
        ("H = hp + hz", g.H, g.hp + g.hz),
        ("B = B1 + tp2 + B2", g.B, g.B1 + g.tp2 + g.B2),
        ("A cajuela dibujo = funcion agente", a_cajuela_base + a_cajuela_pared, a_cajuela),
        ("A DC dibujo = A DC agente", a_dc_dibujo, a_dc_agente),
        ("A EV visible = funcion agente", a_relleno_visible, a_relleno),
    ]

    lines = ["Verificacion de parametros usados en la figura:"]
    for label, expected, actual in checks:
        ok = math.isclose(expected, actual, rel_tol=1e-9, abs_tol=5e-3)
        status = "OK" if ok else "REVISAR"
        lines.append(f"  [{status}] {label}: {expected:.4f} vs {actual:.4f}")

    lines.extend(
        [
            "Areas derivadas con GEOM actual:",
            f"  A_zapata = {a_zapata:.4f} m2",
            f"  A_tronco pantalla = {a_tronco:.4f} m2",
            f"  A_cajuela = {a_cajuela:.4f} m2; centroide agente x={brazo_cajuela:.4f} m, y={y_cajuela:.4f} m",
            f"  A_DC total dibujo/agente = {a_dc_dibujo:.4f} m2",
            f"  A_relleno visible en figura = {a_relleno_visible:.4f} m2",
            f"  A_EV envolvente sin recorte = {a_relleno_envolvente:.4f} m2",
            f"  A_EV relleno agente = {a_relleno:.4f} m2; brazo={brazo_relleno:.4f} m; ancho superior={w_top:.4f} m",
            f"  A_LS sobrecarga agente = {a_ls:.4f} m2",
            "Nota: el Cuadro 39 de la referencia reporta A_EV=35.64 m2, A_LS=1.91 m2 y A_DC=14.09 m2.",
            "      Con los parametros actuales del agente se obtiene otra particion de areas; la figura ya usa GEOM correctamente.",
        ]
    )
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dibuja el perfil del estribo segun la Figura 3.44.")
    parser.add_argument(
        "--salida",
        "-s",
        default=Path(__file__).resolve().parents[2] / ".tmp" / "legacy" / "estribo" / "figura_3.44_estribo.png",
        help="Ruta del archivo de salida.",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Resolucion de salida.")
    parser.add_argument(
        "--mostrar",
        action="store_true",
        help="Muestra la figura en pantalla despues de generarla.",
    )
    parser.add_argument(
        "--sin-verificacion",
        action="store_true",
        help="No imprime la verificacion de parametros.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fig, ax = plt.subplots(figsize=(8.4, 12.0))
    draw_estribo(ax, GEOM)
    fig.tight_layout(pad=0.3)

    if args.salida:
        salida = Path(args.salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(salida, dpi=args.dpi, bbox_inches="tight", facecolor="white")
        print(f"Figura guardada: {salida.resolve()}")

    if not args.sin_verificacion:
        print()
        print("\n".join(verification_lines(GEOM)))

    if args.mostrar:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()

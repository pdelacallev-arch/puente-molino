#!/usr/bin/env python3
"""Dibuja el modelo STM por cortes usado en los contrafuertes centrales.

El script lee el JSON de diseño de la misma carpeta. La figura diferencia:

1. la geometría y las trayectorias resistentes idealizadas;
2. los brazos internos de cada corte;
3. los polígonos vectoriales que verifican T + C = V.

No inventa un reticulado global: las bielas ``C`` son las resultantes
comprimidas de cierre obtenidas en cada corte del modelo implementado.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle


CARPETA = Path(__file__).resolve().parent
ENTRADA = CARPETA / "diseno_contrafuertes_centrales_stm.json"
SALIDA = CARPETA / "modelo_stm_contrafuertes.png"

COLOR_T = "#ba1f33"
COLOR_C = "#176b8a"
COLOR_V = "#31343a"
COLOR_NODO = "#f0a202"
COLOR_CORTE = "#6b7280"


def cargar(ruta: Path) -> dict:
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el diseño STM: {ruta}")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if datos.get("identificacion") != "Diseño STM del armado común de contrafuertes centrales":
        raise ValueError("El JSON no corresponde al diseño STM de contrafuertes")
    if len(datos.get("zonas", [])) != 3:
        raise ValueError("Se esperaban exactamente tres zonas STM")
    return datos


def _flecha(ax, inicio, fin, color, lw=2.6, mutation=16, zorder=6):
    ax.add_patch(FancyArrowPatch(
        inicio, fin, arrowstyle="-|>", mutation_scale=mutation,
        linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=zorder,
    ))


def _longitud(z: float, p: dict) -> float:
    return p["longitud_base_m"] + (
        p["longitud_corona_m"]-p["longitud_base_m"]
    )*z/p["altura_m"]


def dibujar_geometria(ax, datos: dict) -> None:
    p = datos["parametros"]
    zonas = datos["zonas"]
    h = p["altura_m"]
    lb = p["longitud_base_m"]
    lc = p["longitud_corona_m"]

    ax.add_patch(Polygon(
        [(0, 0), (lb, 0), (lc, h), (0, h)], closed=True,
        facecolor="#f5f1e8", edgecolor="#20262e", linewidth=2.4, zorder=1,
    ))
    ax.add_patch(Rectangle(
        (-0.42, -0.78), lb+1.05, 0.78,
        facecolor="#dedede", edgecolor="#20262e", linewidth=1.8, zorder=0,
    ))
    ax.plot([0, 0], [0, h], color="#20262e", lw=5.0, alpha=0.22, zorder=2)

    # Eje comprimido y tirante con el centroide real de cada zona.
    x_comp = zonas[0]["stm"]["x_compresion_m"]
    ax.plot([x_comp, x_comp], [0, h], color=COLOR_C, lw=7,
            solid_capstyle="round", label="Eje comprimido", zorder=4)
    for zona in zonas:
        za, zb = zona["z_inferior_m"], zona["z_superior_m"]
        retiro = zona["stm"]["retiro_normal_lomo_m"]
        factor = math.sqrt(1+(
            (lc-lb)/h
        )**2)
        retiro_horizontal = retiro*factor
        ax.plot(
            [_longitud(za, p)-retiro_horizontal,
             _longitud(zb, p)-retiro_horizontal],
            [za, zb], color=COLOR_T, lw=7, solid_capstyle="round", zorder=5,
        )

    # Nodos, cortes, brazos y resultantes direccionales de compresión.
    for zona in zonas:
        i = zona["zona"]
        z = zona["z_inferior_m"]
        stm = zona["stm"]
        dem = zona["demanda"]
        xc, xt = stm["x_compresion_m"], stm["x_tirante_m"]
        ax.plot([0, _longitud(z, p)], [z, z], color=COLOR_CORTE,
                lw=1.35, ls=(0, (5, 4)), zorder=3)
        ax.plot([xc, xt], [z, z], color="#805d27", lw=2.2,
                ls=(0, (2, 3)), zorder=5)
        ax.scatter([xc, xt], [z, z], s=72, color=COLOR_NODO,
                   edgecolor="#6b4300", linewidth=1.1, zorder=8)
        ax.text((xc+xt)/2, z+0.16, f"$j_{i}$ = {stm['brazo_perpendicular_m']:.3f} m",
                ha="center", va="bottom", fontsize=9.5, color="#604316")
        ax.text(-0.16, z, f"C{i}", ha="right", va="center",
                fontsize=10, weight="bold", color=COLOR_CORTE)

        # La flecha azul da sólo la dirección de la resultante C en el corte.
        ang = math.radians(stm["angulo_biela_desde_horizontal_grados"])
        largo = min(1.10, 0.75+0.00025*stm["fuerza_biela_kN"])
        _flecha(ax, (xc+0.06, z+0.05),
                (xc+0.06+largo*math.cos(ang), z+0.05+largo*math.sin(ang)),
                COLOR_C, lw=2.8, mutation=15)
        ax.text(xc+0.12+largo*math.cos(ang), z+0.10+largo*math.sin(ang),
                f"$C_u$={stm['fuerza_biela_kN']:.0f} kN",
                fontsize=9, color=COLOR_C, weight="bold")

        # Cortante de la sección, orientado hacia la pantalla.
        longitud_v = 0.68+0.00030*dem["V_u_kN"]
        _flecha(ax, (xc+longitud_v, z-0.25), (xc+0.04, z-0.25),
                COLOR_V, lw=2.2, mutation=13)
        ax.text(xc+longitud_v/2+0.20, z-0.42,
                f"$V_u$={dem['V_u_kN']:.0f} kN",
                ha="center", va="top", fontsize=8.8, color=COLOR_V,
                zorder=9, bbox=dict(fc="white", ec="none", alpha=0.78, pad=0.4))

    # Etiquetas de trayectorias.
    ax.text(0.28, 8.75, "Trayectoria comprimida\njunto a pantalla",
            color=COLOR_C, fontsize=10, weight="bold", ha="left")
    ax.text(3.55, 7.70, "Tirante inclinado del lomo\n(barras principales)",
            color=COLOR_T, fontsize=10, weight="bold", rotation=-63,
            ha="center", va="center")

    # Cotas globales.
    ax.annotate("", xy=(-0.52, 0), xytext=(-0.52, h),
                arrowprops=dict(arrowstyle="<->", color="#3f4650", lw=1.2))
    ax.text(-0.68, h/2, f"H = {h:.2f} m", rotation=90,
            ha="center", va="center", fontsize=9.5)
    ax.annotate("", xy=(0, -1.05), xytext=(lb, -1.05),
                arrowprops=dict(arrowstyle="<->", color="#3f4650", lw=1.2))
    ax.text(lb/2, -1.22, f"L base = {lb:.2f} m",
            ha="center", va="top", fontsize=9.5)
    ax.annotate("", xy=(0, h+0.35), xytext=(lc, h+0.35),
                arrowprops=dict(arrowstyle="<->", color="#3f4650", lw=1.2))
    ax.text(lc/2, h+0.48, f"L corona = {lc:.2f} m",
            ha="center", va="bottom", fontsize=9.5)

    ax.set_xlim(-0.95, 7.05)
    ax.set_ylim(-1.48, 10.75)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("A. Geometría, ejes resistentes y cortes",
                 loc="left", fontsize=13, weight="bold", pad=10)


def dibujar_poligono_fuerzas(ax, zona: dict) -> None:
    stm = zona["stm"]
    tx, tz = stm["tirante_vector_kN"]
    cx, cz = stm["biela_vector_kN"]
    vu = zona["demanda"]["V_u_kN"]
    escala = max(vu, stm["fuerza_tirante_kN"], stm["fuerza_biela_kN"])
    t = (tx/escala, tz/escala)
    c = (cx/escala, cz/escala)
    v = (vu/escala, 0.0)

    origen = (0.0, 0.0)
    p_t = t
    p_tc = (t[0]+c[0], t[1]+c[1])

    _flecha(ax, origen, p_t, COLOR_T, lw=3.2, mutation=17)
    _flecha(ax, p_t, p_tc, COLOR_C, lw=3.2, mutation=17)
    _flecha(ax, origen, v, COLOR_V, lw=2.5, mutation=15)
    ax.scatter([origen[0], p_t[0], p_tc[0]],
               [origen[1], p_t[1], p_tc[1]],
               s=35, color=COLOR_NODO, edgecolor="#6b4300", zorder=8)

    ax.text(t[0]*0.50-0.03, t[1]*0.50+0.06,
            f"$T_u$ = {stm['fuerza_tirante_kN']:.1f} kN",
            color=COLOR_T, fontsize=9.5, weight="bold", rotation=63)
    ax.text(p_t[0]+c[0]*0.48+0.03, p_t[1]+c[1]*0.48,
            f"$C_u$ = {stm['fuerza_biela_kN']:.1f} kN",
            color=COLOR_C, fontsize=9.5, weight="bold", rotation=-50)
    ax.text(v[0]*0.50, -0.12, f"$V_u$ = {vu:.1f} kN",
            ha="center", va="top", color=COLOR_V, fontsize=9.5, weight="bold")

    ax.axhline(0, color="#c9ced5", lw=0.8, zorder=0)
    ax.axvline(0, color="#c9ced5", lw=0.8, zorder=0)
    ax.set_xlim(-0.12, 1.20)
    ax.set_ylim(-0.15, 1.03)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#b8bec7")
    ax.set_title(
        f"Corte C{zona['zona']} · z={zona['z_inferior_m']:.3f} m · "
        f"error={stm['error_relativo_equilibrio']:.1e}",
        fontsize=10.5, weight="bold", loc="left", pad=6,
    )
    ax.text(1.17, 0.94, r"$\vec T+\vec C=\vec V$", ha="right", va="top",
            fontsize=10.5, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#ccd1d8"))
    ax.text(1.17, 0.10, f"$M_u$ = {zona['demanda']['M_u_kN_m']:.1f} kN·m",
            ha="right", va="bottom", fontsize=9.2, color="#5b4a2d")


def generar(datos: dict, salida: Path, dpi: int = 180) -> Path:
    fig = plt.figure(figsize=(16, 10), constrained_layout=False)
    gs = fig.add_gridspec(3, 2, width_ratios=(1.16, 1.0),
                          left=0.035, right=0.98, top=0.88, bottom=0.11,
                          hspace=0.28, wspace=0.10)
    ax_geo = fig.add_subplot(gs[:, 0])
    dibujar_geometria(ax_geo, datos)
    for i, zona in enumerate(datos["zonas"]):
        dibujar_poligono_fuerzas(fig.add_subplot(gs[i, 1]), zona)

    fig.suptitle(
        "MODELO DE BIELAS Y TIRANTES (STM) — CONTRAFUERTES CF-C1 / CF-C2 / CF-C3",
        fontsize=17, weight="bold", y=0.965,
    )
    fig.text(
        0.5, 0.925,
        "Modelo por equilibrio de cortes · envolvente Resistencia I / Evento Extremo I · "
        "geometría 6.10–1.17–9.80 m",
        ha="center", fontsize=10.5, color="#4a5059",
    )
    leyenda = [
        Line2D([0], [0], color=COLOR_T, lw=6, label="Tirante T: tracción en acero del lomo"),
        Line2D([0], [0], color=COLOR_C, lw=6, label="Biela/resultante C: compresión en concreto"),
        Line2D([0], [0], color=COLOR_V, lw=2.5, label="Resultante externa V del corte"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_NODO,
               markeredgecolor="#6b4300", markersize=8, label="Nodo/eje resistente"),
    ]
    fig.legend(handles=leyenda, loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 0.048), fontsize=9.5)
    fig.text(
        0.5, 0.018,
        "Nota: las flechas C de la vista geométrica indican la dirección de la resultante comprimida "
        "en cada corte; los polígonos de la derecha son la representación exacta usada en el cálculo.",
        ha="center", fontsize=9, color="#555b64",
    )
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=dpi, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return salida


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=ENTRADA)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    parser.add_argument("--dpi", type=int, default=180)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dpi < 100:
        raise ValueError("Use dpi >= 100 para conservar legibilidad")
    ruta = generar(cargar(args.entrada), args.salida, args.dpi)
    print(ruta)


if __name__ == "__main__":
    main()

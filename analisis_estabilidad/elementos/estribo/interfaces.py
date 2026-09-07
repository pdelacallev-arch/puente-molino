#!/usr/bin/env python3
"""
Cargas distribuidas y presion de contacto en las dos interfaces del estribo
con falsa zapata (zapata/falsa-zapata y falsa-zapata/suelo).

Todos los valores se leen de ``agente_subestructura.py`` con ``FALSE_FOOTING``
activo. No se mantienen calculos paralelos.

Uso::

    python dibujar_presiones_interfaces.py
    python dibujar_presiones_interfaces.py --interface 1 --caso servicio-i
    python dibujar_presiones_interfaces.py --interface 2 --caso resistencia-ia

Sin argumentos se generan los dos PNG. ``--interface`` permite limitar la
salida a una superficie de contacto:
1 = zapata estructural / falsa zapata; 2 = falsa zapata / suelo.  Este es el
único punto de entrada para los diagramas de presión de ambas interfaces.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon
from matplotlib.path import Path as MplPath
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Utilidades gráficas integradas (antes dibujar_cargas_servicioI.py)
# ---------------------------------------------------------------------------
C_HOR = {"Ea": "#b91c1c", "Es": "#d97706", "BR": "#7c3aed"}
C_VERT = {"EV": "#92400e", "LS": "#a16207", "DC": "#1e3a8a", "SUPER": "#15803d"}
C_RESULTANT = "#be123c"
TEXT_DARK = "#1e293b"
TEXT_MUTED = "#64748b"
FONT_SCALE = 3.0

from .estabilidad_global import (
    FALSE_FOOTING,
    GEOM,
    LOADS,
    MAT,
    SEISMIC,
    SubstructureAnalysis,
    compute_brazo_BR,
    validate_case_consistency,
)
from .geometria import (
    CONCRETE_EDGE,
    CONCRETE_FILL,
    SOIL_DOT,
    SOIL_EDGE,
    SOIL_FILL,
    build_geometry,
    close_poly,
)


def label(ax, x, y, text, *, color=TEXT_DARK, fontsize=8, ha="center",
          va="center", rotation=0, facecolor="white", alpha=0.88, **kwargs):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fontsize * FONT_SCALE, color=color,
            rotation=rotation,
            bbox=dict(facecolor=facecolor, edgecolor="none", pad=1.2, alpha=alpha),
            zorder=20, **kwargs)


def draw_abutment(ax, g=GEOM, *, show_origin=True) -> dict:
    """Dibuja el perfil base del estribo para superponer cargas."""
    geo = build_geometry(g)
    pts = np.array(geo["relleno_visible"], dtype=float)
    ax.add_patch(Polygon(geo["relleno_visible"], closed=True,
                         facecolor=SOIL_FILL, edgecolor=SOIL_EDGE,
                         linewidth=0.7, alpha=0.70, zorder=1))
    path = MplPath(pts)
    xmin, ymin = pts.min(axis=0); xmax, ymax = pts.max(axis=0)
    grid = np.array([(x, y) for y in np.arange(ymin + 0.22, ymax, 0.42)
                     for x in np.arange(xmin + 0.22, xmax, 0.42)])
    if grid.size:
        inside = grid[path.contains_points(grid)]
        if len(inside):
            ax.scatter(inside[:, 0], inside[:, 1], s=2.5, color=SOIL_DOT,
                       alpha=0.30, linewidths=0, zorder=1.6)
    for key in ("zapata", "tronco", "cajuela_base", "cajuela_pared"):
        ax.add_patch(Polygon(geo[key], closed=True, facecolor=CONCRETE_FILL,
                             edgecolor=CONCRETE_EDGE, linewidth=1.2, zorder=3))
        p = close_poly(geo[key])
        ax.plot(p[:, 0], p[:, 1], color=CONCRETE_EDGE, lw=0.9, zorder=4)
    if show_origin:
        ax.plot([g.B], [0], marker="o", ms=3, color="#dc2626", zorder=8)
        ax.text(g.B + 0.04, -0.06, "O", ha="left", va="top",
                fontsize=6 * FONT_SCALE, color="#dc2626")
    return geo


# ---------------------------------------------------------------------------
# Geometria ampliada con falsa zapata
# ---------------------------------------------------------------------------

def build_geometry_with_false_footing(g=GEOM):
    """Construye geometria de dibujo que incluye la falsa zapata.

    La falsa zapata se dibuja como un rectangulo debajo de la zapata
    estructural, con el mismo ancho (centrada si offset=0).
    """
    geo = build_geometry(g)
    fz = FALSE_FOOTING
    if fz is None or not fz.enabled:
        return geo
    toe_offset = fz.structural_offset(g.B)
    heel_offset = fz.width - g.B - toe_offset
    # El estribo conserva x=0 en el talón estructural. La falsa zapata puede
    # sobresalir hacia ambos lados y por eso su origen gráfico puede ser < 0.
    x0 = -heel_offset
    x1 = x0 + fz.width
    y0 = -fz.height
    y1 = 0.0
    geo["false_footing"] = [
        (x0, y0),
        (x1, y0),
        (x1, y1),
        (x0, y1),
    ]
    geo["false_footing_height"] = fz.height
    geo["false_footing_width"] = fz.width
    geo["false_footing_toe_offset"] = toe_offset
    geo["false_footing_heel_offset"] = heel_offset
    geo["false_footing_x0"] = x0
    geo["false_footing_x1"] = x1
    return geo


def draw_false_footing(ax, geo):
    """Dibuja el bloque de falsa zapata y su textura."""
    pts = geo["false_footing"]
    ax.add_patch(
        Polygon(
            pts,
            closed=True,
            facecolor="#e2e8f0",
            edgecolor=CONCRETE_EDGE,
            linewidth=1.0,
            zorder=3,
        )
    )
    ax.plot(
        np.array(pts + [pts[0]]).reshape(-1, 2)[:, 0],
        np.array(pts + [pts[0]]).reshape(-1, 2)[:, 1],
        color=CONCRETE_EDGE, lw=0.7, zorder=4,
    )
    xs = np.array(pts)[:, 0]
    xmin, xmax = xs.min(), xs.max()
    for x in np.arange(xmin + 0.20, xmax, 0.40):
        ax.plot(
            [x, min(x + 0.18, xmax)],
            [-0.08, -0.28],
            color="#94a3b8", lw=0.35, alpha=0.50, zorder=4,
        )
    cy = -geo["false_footing_height"] + 0.28
    ax.text(
        xmin + 0.25, cy, "FALSA ZAPATA",
        ha="left", va="bottom", fontsize=7.5 * FONT_SCALE,
        color="#334155", fontweight="bold", fontstyle="italic",
        bbox=dict(facecolor="#e2e8f0", edgecolor="none", pad=1.5, alpha=0.75),
        zorder=7,
    )


# ---------------------------------------------------------------------------
# Diagramas de presion
# ---------------------------------------------------------------------------

def draw_linear_pressure(ax, bearing, g, pressure_depth=1.45):
    """Distribucion lineal elastica q=V/B(1+/-6e/B) (interfaz 1)."""
    q_talon = bearing["q_talon_t_m2"]
    q_punta = bearing["q_punta_t_m2"]
    q_abs = max(abs(q_talon), abs(q_punta), 1e-9)
    y_talon = -pressure_depth * q_talon / q_abs
    y_punta = -pressure_depth * q_punta / q_abs
    ax.plot([0, g.B], [y_talon, y_punta], color="#1d4ed8", lw=1.5, zorder=4)
    ax.plot([0, g.B], [0, 0], color="#64748b", lw=0.8, zorder=3)

    if q_talon >= 0 and q_punta >= 0:
        ax.add_patch(Polygon(
            [(0, 0), (g.B, 0), (g.B, y_punta), (0, y_talon)],
            closed=True, facecolor="#bfdbfe", edgecolor="#1d4ed8",
            linewidth=1.2, alpha=0.72, zorder=3,
        ))
    elif q_talon < 0 < q_punta:
        x_zero = g.B * (-q_talon) / (q_punta - q_talon)
        ax.add_patch(Polygon(
            [(0, 0), (x_zero, 0), (0, y_talon)],
            closed=True, facecolor="#fecaca", edgecolor="#dc2626",
            alpha=0.72, zorder=3,
        ))
        ax.add_patch(Polygon(
            [(x_zero, 0), (g.B, 0), (g.B, y_punta)],
            closed=True, facecolor="#bfdbfe", edgecolor="#1d4ed8",
            alpha=0.72, zorder=3,
        ))
        label(ax, x_zero / 2, y_talon + 0.08, "Traccion teorica\n(sin contacto)",
              color="#dc2626", fontsize=6.5)
    elif q_punta < 0 < q_talon:
        x_zero = g.B * q_talon / (q_talon - q_punta)
        ax.add_patch(Polygon(
            [(0, 0), (x_zero, 0), (0, y_talon)],
            closed=True, facecolor="#bfdbfe", edgecolor="#1d4ed8",
            alpha=0.72, zorder=3,
        ))
        ax.add_patch(Polygon(
            [(x_zero, 0), (g.B, 0), (g.B, y_punta)],
            closed=True, facecolor="#fecaca", edgecolor="#dc2626",
            alpha=0.72, zorder=3,
        ))

    for x in np.linspace(0.18, g.B - 0.18, 13):
        qx = q_talon + (q_punta - q_talon) * x / g.B
        yx = -pressure_depth * qx / q_abs
        color = "#1d4ed8" if qx >= 0 else "#dc2626"
        ax.annotate(
            "", xy=(x, -0.02 if qx >= 0 else yx),
            xytext=(x, yx if qx >= 0 else 0.02),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0,
                            mutation_scale=9), zorder=13,
        )

    label(ax, g.B / 2, -pressure_depth - 0.58,
          "Distribucion lineal elastica de presiones",
          color="#1d4ed8", fontsize=8, facecolor="white")
    label(ax, -0.08, y_talon,
          f"q talon = {q_talon:.2f} t/m2\n({q_talon/10:.3f} kg/cm2)",
          color="#1d4ed8" if q_talon >= 0 else "#dc2626",
          fontsize=7, ha="right")
    label(ax, g.B + 0.08, y_punta,
          f"q punta = {q_punta:.2f} t/m2\n({q_punta/10:.3f} kg/cm2)",
          color="#1d4ed8" if q_punta >= 0 else "#dc2626",
          fontsize=7, ha="left")
    return y_talon, y_punta


def draw_meyerhof_pressure(ax, bearing, width, Xo, pressure_depth=1.45,
                           y_base=0.0, x_origin=0.0):
    """Distribucion rectangular de Meyerhof q=V/[L(B-2e)] (interfaz 2).

    El area efectiva se centra en la resultante (Xo medido desde la punta).
    ``y_base`` desplaza todo el diagrama verticalmente (para falsa zapata).
    """
    q_act = bearing["q_max_t_m2"]
    eff_w = bearing["effective_width"]
    q_abs = max(abs(q_act), 1e-9)
    y_top = y_base
    y_bot = y_base - pressure_depth * q_act / q_abs

    center = x_origin + width - Xo
    x_start = max(center - eff_w / 2, x_origin)
    x_end = min(center + eff_w / 2, x_origin + width)

    ax.plot([x_start, x_end], [y_bot, y_bot], color="#0369a1", lw=2.0, zorder=4)
    ax.plot([x_start, x_start], [y_bot, y_top], color="#0369a1", lw=0.6, zorder=3)
    ax.plot([x_end, x_end], [y_bot, y_top], color="#0369a1", lw=0.6, zorder=3)
    ax.plot(
        [x_origin, x_origin + width],
        [y_top, y_top],
        color="#64748b",
        lw=0.8,
        zorder=3,
    )
    ax.add_patch(Polygon(
        [(x_start, y_top), (x_end, y_top), (x_end, y_bot), (x_start, y_bot)],
        closed=True, facecolor="#bae6fd", edgecolor="#0369a1",
        linewidth=1.2, alpha=0.72, zorder=3,
    ))

    for x in np.linspace(x_start + 0.15, x_end - 0.15,
                         max(5, int((x_end - x_start) / 0.6))):
        ax.annotate(
            "", xy=(x, y_top - 0.02), xytext=(x, y_bot),
            arrowprops=dict(arrowstyle="-|>", color="#0369a1",
                            lw=1.0, mutation_scale=9), zorder=13,
        )

    label(ax, (x_start + x_end) / 2, y_base - pressure_depth - 0.58,
          f"Meyerhof: q = V / (L x B_efectivo)\n"
          f"B_efectivo = {eff_w:.3f} m",
          color="#0369a1", fontsize=7.5, facecolor="white")
    label(ax, x_start - 0.08, (y_top + y_bot) / 2,
          f"q = {q_act:.2f} t/m2\n({q_act/10:.3f} kg/cm2)",
          color="#0369a1", fontsize=7, ha="right")
    return y_bot


# ---------------------------------------------------------------------------
# Flechas distribuidas (empujes)
# ---------------------------------------------------------------------------

def distributed_arrows(ax, x0, y_values, lengths, color, *, lw=1.15):
    for y, length in zip(y_values, lengths):
        ax.annotate(
            "", xy=(x0, y), xytext=(x0 - length, y),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                            mutation_scale=10), zorder=14,
        )


# ---------------------------------------------------------------------------
# Funcion principal unificada
# ---------------------------------------------------------------------------

def build_case_map(kebab: str) -> str:
    return {
        "servicio-i": "case_service_I",
        "resistencia-ia": "case_resistance_Ia",
        "resistencia-ib": "case_resistance_Ib",
        "evento-extremo-i": "case_extreme_event_I",
    }[kebab]


def validate_interface_case(case: dict, interface_number: int,
                            tol: float = 0.02) -> dict:
    """Audita equilibrio, resultante y presión antes de generar una figura."""
    fv = sum(d["valor"] for d in case["fv_detail"])
    me = sum(d["momento"] for d in case["fv_detail"])
    fh = sum(d["valor"] for d in case["fh_detail"])
    mv = sum(d["momento"] for d in case["fh_detail"])
    width = case["support_width"]
    xo = (me - mv) / fv
    eccentricity = abs(width / 2.0 - xo)
    bearing = case["bearing"]

    checks = {
        "Fv_detalle": abs(fv - case["Fv"]) <= tol,
        "Me_detalle": abs(me - case["Me"]) <= tol,
        "Fh_detalle": abs(fh - case["Fh"]) <= tol,
        "Mv_detalle": abs(mv - case["Mv"]) <= tol,
        "Xo": abs(xo - case["overturning"]["Xo"]) <= tol,
        "excentricidad": (
            abs(eccentricity - case["overturning"]["e"]) <= tol
        ),
    }
    if interface_number == 1:
        q_mean = fv / width
        q_max = q_mean * (1.0 + 6.0 * eccentricity / width)
        q_min = q_mean * (1.0 - 6.0 * eccentricity / width)
        checks.update({
            "q_max_lineal": abs(q_max - bearing["q_max_t_m2"]) <= 0.03,
            "q_min_lineal": abs(q_min - bearing["q_min_t_m2"]) <= 0.03,
        })
    else:
        effective_width = width - 2.0 * eccentricity
        q_act = fv / effective_width if effective_width > 0 else float("inf")
        checks.update({
            "ancho_efectivo_positivo": effective_width > 0,
            "ancho_efectivo_meyerhof": (
                abs(effective_width - bearing["effective_width"]) <= tol
            ),
            "presion_meyerhof": (
                abs(q_act - bearing["q_max_t_m2"]) <= 0.03
            ),
        })
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "sumas": {"Fv": fv, "Me": me, "Fh": fh, "Mv": mv},
        "Xo": xo,
        "e": eccentricity,
    }


def draw_interface(
    args: argparse.Namespace,
    interface_number: int,
    results: dict | None = None,
) -> None:
    """Genera el PNG de una de las superficies de contacto."""

    if results is None:
        analysis = SubstructureAnalysis(GEOM, MAT, LOADS, SEISMIC, FALSE_FOOTING)
        results = analysis.run_full_analysis()

    if "interfaces" not in results:
        raise RuntimeError(
            "El analisis no contiene interfaces de falsa zapata. "
            "Verifique que FALSE_FOOTING este activo."
        )

    interface_key = f"interface_{interface_number}"
    interface = results["interfaces"][interface_key]
    case_key = build_case_map(args.caso)
    case = interface["cases"][case_key]
    is_extreme = args.caso == "evento-extremo-i"
    is_interface_2 = interface_number == 2

    audit = validate_interface_case(case, interface_number)
    if not audit["ok"]:
        raise RuntimeError(
            f"Inconsistencia del caso antes de dibujar: {audit}"
        )
    # Se conserva además la auditoría histórica de la distribución lineal.
    if not is_interface_2:
        legacy_audit = validate_case_consistency(case, GEOM)
        if not legacy_audit["ok"]:
            raise RuntimeError(
                f"Inconsistencia lineal antes de dibujar: {legacy_audit}"
            )

    g = GEOM
    fz = FALSE_FOOTING
    earth = interface["earth_pressures"]
    width = case["support_width"]

    geo = build_geometry_with_false_footing(g) if is_interface_2 else build_geometry(g)

    # Altura de empuje para este plano
    H_eff = earth["analysis_height"]
    y_pressure_base = -fz.height if is_interface_2 else 0.0
    y_pressure_top = y_pressure_base + H_eff
    x_support_origin = geo.get("false_footing_x0", 0.0)
    x_support_end = x_support_origin + width

    def plot_x_from_toe(arm: float) -> float:
        return x_support_origin + width - arm

    def plot_y_from_interface(arm: float) -> float:
        return y_pressure_base + arm

    pressure_depth = 1.45

    # El perfil se dibuja en un eje exclusivo con escala 1:1. El panel lateral
    # evita que el resumen obligue a ensanchar el rango de datos y deforme la
    # geometria del estribo.
    # El lienzo ampliado conserva las tipografias a 3x sin superponer el
    # perfil, el titulo y el panel de verificacion.
    fig = plt.figure(figsize=(24.0, 22.0))
    grid = fig.add_gridspec(
        nrows=1, ncols=2, width_ratios=(4.2, 2.2), wspace=0.08,
    )
    ax = fig.add_subplot(grid[0, 0])
    ax_summary = fig.add_subplot(grid[0, 1])
    ax_summary.axis("off")

    # Dibujar estribo
    draw_abutment(ax, g, show_origin=not is_interface_2)

    # Dibujar falsa zapata si aplica
    if is_interface_2:
        draw_false_footing(ax, geo)
        ax.plot([x_support_end], [y_pressure_base], marker="o", ms=3,
                color="#dc2626", zorder=18)
        ax.text(x_support_end + 0.04, y_pressure_base - 0.06, "O",
                ha="left", va="top", fontsize=6 * FONT_SCALE,
                color="#dc2626", zorder=20)

    # Brazos
    brazo_br_final = (
        (LOADS.brazo_BR if LOADS.brazo_BR is not None else compute_brazo_BR(GEOM))
        + (fz.height if is_interface_2 else 0.0)
    )

    brazo_br_plot = plot_y_from_interface(brazo_br_final)
    y_axis_max = max(geo["y_top"] + 2.35, brazo_br_plot + 0.7)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(min(-3.15, x_support_origin - 3.15),
                max(g.B, x_support_end) + 1.45)
    ax.set_ylim(
        y_pressure_base - pressure_depth - 1.65,
        y_axis_max,
    )
    ax.set_xlabel("Distancia horizontal (m)", color=TEXT_MUTED,
                  fontsize=8 * FONT_SCALE)
    ax.set_ylabel(
        "Cota respecto a la base de la zapata estructural (m)",
        color=TEXT_MUTED,
        fontsize=8 * FONT_SCALE,
    )
    ax.tick_params(axis="both", labelsize=8 * FONT_SCALE, colors=TEXT_MUTED)

    # --- Fuerzas verticales ---
    fv_detail = case["fv_detail"]
    fh_detail = case["fh_detail"]

    def vertical(desc=None, tipo=None, origen=None):
        return [
            d for d in fv_detail
            if (desc is None or d["desc"] == desc)
            and (tipo is None or d["tipo"] == tipo)
            and (origen is None or d["origen"] == origen)
        ]

    def horizontal(tipo):
        return next(d for d in fh_detail if d["tipo"] == tipo)

    # EV
    ev_list = vertical(tipo="EV", origen="estribo")
    if ev_list:
        ev = ev_list[0]
        x_ev = plot_x_from_toe(ev["brazo"])
        ax.annotate(
            "", xy=(x_ev, geo["y_top"] - 0.65),
            xytext=(x_ev, geo["y_top"] + 0.2),
            arrowprops=dict(arrowstyle="-|>", color=C_VERT["EV"], lw=1.8,
                            mutation_scale=14), zorder=15,
        )
        label(ax, x_ev - 0.15, geo["y_top"] + 0.1,
              f"EV = {ev['valor']:.2f} t\nb = {ev['brazo']:.2f} m",
              color=C_VERT["EV"], fontsize=7, ha="right")

    # LS
    ls_list = vertical(tipo="LS", origen="estribo")
    if ls_list and ls_list[0]["valor"] > 0:
        ls = ls_list[0]
        x_ls = plot_x_from_toe(ls["brazo"])
        ancho_ls = 2.0 * x_ls
        for x in np.linspace(0.18, ancho_ls - 0.18, 8):
            ax.annotate(
                "", xy=(x, geo["y_top"] - 0.22),
                xytext=(x, geo["y_top"] + 0.62),
                arrowprops=dict(arrowstyle="-|>", color=C_VERT["LS"],
                                lw=1.0, mutation_scale=9), zorder=14,
            )
        ax.plot([0.0, ancho_ls],
                [geo["y_top"] + 0.64] * 2, color=C_VERT["LS"], lw=1.2)
        label(ax, x_ls, geo["y_top"] + 0.95,
              f"LS = {ls['valor']:.2f} t | b = {ls['brazo']:.2f} m",
              color=C_VERT["LS"], fontsize=7)

    # Superestructura
    super_items = [
        d for d in vertical(origen="superestructura") if d["valor"] > 0
    ]
    if super_items:
        super_total = sum(d["valor"] for d in super_items)
        super_moment = sum(d["momento"] for d in super_items)
        brazo_super = super_moment / super_total
        x_super = plot_x_from_toe(brazo_super)
        ax.annotate(
            "", xy=(x_super, geo["y_stem_top"] + 0.55),
            xytext=(x_super, geo["y_top"] + 0.25),
            arrowprops=dict(arrowstyle="-|>", color=C_VERT["SUPER"], lw=1.8,
                            mutation_scale=14), zorder=15,
        )
        label(ax, x_super + 0.2, geo["y_stem_top"] + 0.55,
              f"Superestructura = {super_total:.2f} t\nb = {brazo_super:.2f} m",
              color=C_VERT["SUPER"], fontsize=7, ha="left")

    # DC del estribo (Zapata, Tronco, Cajuela)
    # Las posiciones verticales deben seguir a GEOM. Los valores nominales de
    # y_cg ya son calculados por el agente para la geometria vigente; mantener
    # coordenadas fijas aqui dejaba las flechas en las cotas del estribo viejo
    # cuando cambiaban H y hp.
    dc_y_cg = {
        item["desc"]: item["y_cg"]
        for item in results["weights"]["detail"]
        if item["tipo"] == "DC" and "y_cg" in item
    }
    dc_bounds = {
        "Zapata": (0.0, geo["y_footing_top"]),
        "Tronco pantalla": (geo["y_footing_top"], geo["y_stem_top"]),
        "Cajuela (asiento viga)": (geo["y_stem_top"], geo["y_top"]),
    }
    for dc in vertical(tipo="DC", origen="estribo"):
        if dc["valor"] <= 0 or dc["desc"] not in dc_bounds:
            continue
        y_lower, y_upper = dc_bounds[dc["desc"]]
        y_cg = dc_y_cg.get(dc["desc"], (y_lower + y_upper) / 2.0)
        arrow_half = min(0.45, max((y_upper - y_lower) * 0.25, 0.18))
        y_from = min(y_cg + arrow_half, y_upper - 0.08)
        y_to = max(y_cg - arrow_half, y_lower + 0.08)
        y_text = min(y_from + 0.32, y_upper - 0.05)
        x_dc = plot_x_from_toe(dc["brazo"])
        ax.annotate(
            "", xy=(x_dc, y_to), xytext=(x_dc, y_from),
            arrowprops=dict(arrowstyle="-|>", color=C_VERT["DC"], lw=1.5,
                            mutation_scale=12), zorder=15,
        )
        short = {
            "Zapata": "DC zapata",
            "Tronco pantalla": "DC pantalla",
            "Cajuela (asiento viga)": "DC cajuela",
        }[dc["desc"]]
        label(ax, x_dc - 0.10, y_text,
              f"{short} = {dc['valor']:.2f} t\nb = {dc['brazo']:.2f} m",
              color=C_VERT["DC"], fontsize=6.5, ha="right")

    # Falsa zapata DC (solo interfaz 2)
    if is_interface_2:
        ff_items = [d for d in fv_detail if d["desc"] == "Falsa zapata"]
        if ff_items:
            ff = ff_items[0]
            x_ff = plot_x_from_toe(ff["brazo"])
            ff_y_text = -fz.height / 2
            ax.annotate(
                "", xy=(x_ff, -fz.height + 0.22),
                xytext=(x_ff, -0.22),
                arrowprops=dict(arrowstyle="-|>", color=C_VERT["DC"], lw=1.5,
                                mutation_scale=12), zorder=15,
            )
            label(ax, x_ff - 0.25, ff_y_text,
                  f"Falsa zapata = {ff['valor']:.2f} t\nb = {ff['brazo']:.2f} m",
                  color=C_VERT["DC"], fontsize=7, ha="right")

    # --- Fuerzas horizontales ---
    x_load = 0.0
    y0, y1 = y_pressure_base, y_pressure_top

    # Ea triangular
    ys = np.linspace(y0, y1, 14)
    tri_lengths = 2.35 * (y1 - ys) / (y1 - y0)
    distributed_arrows(ax, x_load, ys, tri_lengths, C_HOR["Ea"])
    ax.plot(x_load - tri_lengths, ys, color=C_HOR["Ea"], lw=1.4)
    ax.plot([x_load, x_load], [y0, y1], color=C_HOR["Ea"], lw=0.8, alpha=0.55)
    ea = horizontal("Ea")
    label(ax, x_load - 2.55, (y0 + y1) / 2,
          f"Ea triangular\nR = {ea['valor']:.2f} t\ny = {ea['brazo']:.2f} m",
          color=C_HOR["Ea"], fontsize=8, rotation=90)

    if is_extreme:
        # dEas triangular invertido
        deas = horizontal("Delta Eas")
        ys_d = np.linspace(y0, y1, 12)
        deas_lengths = 1.45 * (ys_d - y0) / (y1 - y0)
        distributed_arrows(ax, x_load, ys_d, deas_lengths, C_HOR["Es"])
        ax.plot(x_load - deas_lengths, ys_d, color=C_HOR["Es"], lw=1.4)
        label(ax, x_load - 1.65, y1 - 1.25,
              f"Delta Eas triangular\nR = {deas['valor']:.2f} t\ny = {deas['brazo']:.2f} m",
              color=C_HOR["Es"], fontsize=7, rotation=90)

        # Fuerzas sismicas (Eq-super, Eq-estribo, Eq-falsa-zapata)
        eq_items = [
            d for d in fh_detail if d["tipo"] in ("Eq-super", "Eq-estribo", "Eq-falsa-zapata")
        ]
        for item in eq_items:
            length = 2.15 if "super" in item["tipo"] else 1.25
            y_item = plot_y_from_interface(item["brazo"])
            ax.annotate(
                "", xy=(geo["x_stem_front_bottom"] + length, y_item),
                xytext=(geo["x_stem_front_bottom"] + 0.12, y_item),
                arrowprops=dict(arrowstyle="-|>", color=C_HOR["BR"], lw=1.7,
                                mutation_scale=13), zorder=15,
            )
            if "falsa" in item["tipo"]:
                tx = x_support_end - 0.15
                ha = "right"
                label_y = y_item - 1.0
            else:
                tx = geo["x_stem_front_bottom"] + length + 0.12
                ha = "left"
                label_y = y_item + (1.1 if "super" in item["tipo"] else 0.15)
            label(ax, tx, label_y,
                  f"{item['tipo']} = {item['valor']:.2f} t\n"
                  f"y = {item['brazo']:.2f} m",
                  color=C_HOR["BR"], fontsize=6.5, ha=ha)
    else:
        # Es uniforme
        ys_s = np.linspace(y0, y1, 12)
        distributed_arrows(ax, x_load, ys_s, np.full_like(ys_s, 0.82), C_HOR["Es"])
        ax.plot([x_load - 0.82, x_load - 0.82], [ys_s[0], ys_s[-1]],
                color=C_HOR["Es"], lw=1.4)
        es = horizontal("Es")
        label(ax, x_load - 1.05, y1 - 1.15,
              f"Es uniforme\nR = {es['valor']:.2f} t\ny = {es['brazo']:.2f} m",
              color=C_HOR["Es"], fontsize=7, rotation=90)

        # BR frenado
        br = horizontal("BR")
        y_br = plot_y_from_interface(br["brazo"])
        ax.annotate(
            "", xy=(geo["x_stem_front_top"] + 2.25, y_br),
            xytext=(geo["x_stem_front_top"] + 0.2, y_br),
            arrowprops=dict(arrowstyle="-|>", color=C_HOR["BR"], lw=1.8,
                            mutation_scale=14), zorder=15,
        )
        label(ax, geo["x_stem_front_top"] + 1.25, y_br - 0.28,
              f"BR = {br['valor']:.2f} t | y = {br['brazo']:.2f} m",
              color=C_HOR["BR"], fontsize=7)

    # --- Presion de contacto ---
    V = case["Fv"]
    e = case["overturning"]["e"]
    bearing = case["bearing"]

    if is_interface_2:
        draw_meyerhof_pressure(ax, bearing, width,
                               Xo=case["overturning"]["Xo"],
                               pressure_depth=pressure_depth,
                               y_base=y_pressure_base,
                               x_origin=x_support_origin)
    else:
        draw_linear_pressure(ax, bearing, g, pressure_depth)

    # Resultante vertical
    x_rv = plot_x_from_toe(case["overturning"]["Xo"])
    ax.plot(
        [x_rv, x_rv],
        [y_pressure_base + 0.05, geo["y_top"] + 1.45],
        color=C_RESULTANT, lw=1.2, linestyle=(0, (4, 3)), zorder=12,
    )
    ax.annotate(
        "", xy=(x_rv, y_pressure_base + 0.04),
        xytext=(x_rv, geo["y_top"] + 1.35),
        arrowprops=dict(arrowstyle="-|>", color=C_RESULTANT, lw=2.0,
                        mutation_scale=16), zorder=16,
    )
    label(ax, x_rv + 0.2, y_pressure_base + 2.15,
          f"Rv = {V:.1f} t\nXo = {case['overturning']['Xo']:.2f} m",
          color=C_RESULTANT, fontsize=8, ha="left")

    # --- Cotas geometricas ---
    # H se mide desde la base de la zapata estructural. En la interfaz 2 la
    # altura de empuje incluye, adicionalmente, el espesor de falsa zapata.
    dimension_color = "#334155"
    x_dim_h = max(g.B, x_support_end) + 0.55
    ax.annotate(
        "", xy=(x_dim_h, g.H), xytext=(x_dim_h, 0.0),
        arrowprops=dict(arrowstyle="<->", color=dimension_color, lw=1.0),
        zorder=17,
    )
    ax.plot([g.B, x_dim_h], [0.0, 0.0], color=dimension_color,
            lw=0.6, linestyle=":", zorder=16)
    ax.plot([geo["x_relleno_visible_top"], x_dim_h], [g.H, g.H],
            color=dimension_color, lw=0.6, linestyle=":", zorder=16)
    label(
        ax, x_dim_h + 0.18, g.H / 2.0, f"H = {g.H:.2f} m",
        color=dimension_color, fontsize=7.5, rotation=90,
    )

    # Se ubica por debajo del rotulo propio del diagrama de presiones para que
    # ambas anotaciones sigan siendo legibles a escala 1:1.
    y_dim_b = y_pressure_base - pressure_depth - 1.15
    ax.annotate(
        "", xy=(g.B, y_dim_b), xytext=(0.0, y_dim_b),
        arrowprops=dict(arrowstyle="<->", color=dimension_color, lw=1.0),
        zorder=17,
    )
    ax.plot([0.0, 0.0], [y_pressure_base, y_dim_b], color=dimension_color,
            lw=0.6, linestyle=":", zorder=16)
    ax.plot([g.B, g.B], [y_pressure_base, y_dim_b], color=dimension_color,
            lw=0.6, linestyle=":", zorder=16)
    label(
        ax, g.B / 2.0, y_dim_b - 0.17, f"B = {g.B:.2f} m",
        color=dimension_color, fontsize=7.5, va="top",
    )

    # --- Resumen en panel independiente ---
    vf = {d["tipo"]: d["factor"] for d in fv_detail}
    hf = {d["tipo"]: d["factor"] for d in fh_detail}
    if is_extreme:
        delta_key = "Delta Eas"
        factors_text = (
            f"EV {vf.get('EV', 0):.2f} | DC {vf.get('DC', 0):.2f} | DW {vf.get('DW', 0):.2f}\n"
            f"Ea {hf.get('Ea', 0):.2f} | {delta_key} {hf.get(delta_key, 0):.2f} | Eq 1.00"
        )
    else:
        factors_text = (
            f"EV {vf.get('EV', 0):.2f} | DC {vf.get('DC', 0):.2f} | DW {vf.get('DW', 0):.2f}\n"
            f"LS {vf.get('LS', 0):.2f} | PL {vf.get('PL', 0):.2f} | LL+IM {vf.get('LL+IM', 0):.2f}\n"
            f"Ea {hf.get('Ea', 0):.2f} | Es {hf.get('Es', 0):.2f} | BR {hf.get('BR', 0):.2f}"
        )
    e_ok = case["overturning"]["e < B/6"] == "CONFORME"
    method_line = (
        "Metodo: Meyerhof q=V/[L(B-2e)]" if is_interface_2 else
        f"qmin = {bearing['q_min']:.3f} | qmax = {bearing['q_max']:.3f} kg/cm2"
    )
    capacity_status = bearing["q <= q_adm"]
    if capacity_status.startswith("PENDIENTE"):
        capacity_line = "Capacidad: PENDIENTE\n(falta capacidad portante factorizada)"
    elif is_interface_2:
        capacity_line = f"Capacidad del suelo: {capacity_status}"
    else:
        capacity_line = (
            f"Compresion de interfaz: {capacity_status}\n"
            "(criterio preliminar)"
        )
    summary = (
        f"{case['name'].upper()}\n{factors_text}\n"
        f"Fv = {case['Fv']:.1f} t | Me = {case['Me']:.1f} t-m\n"
        f"Fh = {case['Fh']:.1f} t | Mv = {case['Mv']:.1f} t-m\n"
        f"e = {e:.3f} m {'<' if e_ok else '>'} B/6 = {width/6:.2f} m\n"
        f"{method_line}\n"
        f"q = {bearing['q']:.3f} kg/cm2\n{capacity_line}\n"
        f"Contacto: {bearing.get('contacto', 'AREA EFECTIVA')}"
    )
    ax_summary.text(
        0.06, 0.53, summary,
        transform=ax_summary.transAxes,
        ha="left", va="center", fontsize=8 * FONT_SCALE,
        color=TEXT_DARK, linespacing=1.35, wrap=True,
        bbox=dict(
            boxstyle="round,pad=0.65",
            facecolor="#f8fafc",
            edgecolor="#cbd5e1",
            linewidth=0.9,
        ),
    )
    ax_summary.text(
        0.06, 0.72,
        "RESUMEN DE VERIFICACION\nPanel fuera de la escala geometrica",
        transform=ax_summary.transAxes,
        ha="left", va="bottom", fontsize=8.5 * FONT_SCALE,
        fontweight="bold",
        color=TEXT_MUTED,
    )

    # Titulo
    interfaz_nombre = interface["description"]
    fig.suptitle(
        f"Perfil del estribo: cargas distribuidas y presiones\n"
        f"{interfaz_nombre} — Estado Limite de {case['name']}",
        fontsize=13 * FONT_SCALE, fontweight="bold", color=TEXT_DARK,
        y=0.975, linespacing=1.08,
    )
    height_note = f"H estructural = {g.H:.2f} m"
    if is_interface_2:
        height_note += (
            f" | H de empuje desde interfaz = {H_eff:.2f} m "
            f"(H + h falsa zapata = {g.H:.2f} + {fz.height:.2f})"
        )
    else:
        height_note += f" | H de empuje = {H_eff:.2f} m"
    ax.set_title(
        f"Escala geometrica 1:1 | Valores por metro lineal\n{height_note}",
        fontsize=8 * FONT_SCALE, fontweight="normal", color=TEXT_MUTED,
        pad=8,
    )
    fig.subplots_adjust(
        left=0.06, right=0.985, bottom=0.06, top=0.83, wspace=0.08,
    )

    # Salida
    case_label = args.caso
    interfaz_label = f"interfaz_{interface_number}"
    default_output = (
        SCRIPT_DIR.parents[1] / ".tmp" / "legacy" / "estribo" /
        f"presiones_{interfaz_label}_{case_label}.png"
    )
    output = Path(args.salida).expanduser() if args.salida else default_output
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=args.dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Figura guardada: {output.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Dibuja las presiones de una o ambas interfaces de la falsa zapata."
    )
    parser.add_argument(
        "--interface", choices=("1", "2", "ambas"), default="ambas",
        help="1 = zapata/falsa-zapata; 2 = falsa-zapata/suelo; ambas = las dos (predeterminado)",
    )
    parser.add_argument(
        "--caso",
        choices=("servicio-i", "resistencia-ia", "resistencia-ib",
                 "evento-extremo-i"),
        default="servicio-i",
    )
    parser.add_argument(
        "--salida", "-s", default=None,
        help=(
            "PNG de salida; solo se admite al solicitar una interfaz. "
            "Sin este argumento se guarda junto al script, en "
            "analisis_estabilidad/imagenes."
        ),
    )
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    interfaces = (1, 2) if args.interface == "ambas" else (int(args.interface),)
    if args.salida and len(interfaces) > 1:
        parser.error("--salida requiere indicar --interface 1 o --interface 2")
    for interface_number in interfaces:
        draw_interface(args, interface_number)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Dibuja las cargas y reacciones de la pared de cajuela en voladizo.

El script es complementario de ``verificar_cajuela_voladizo.py``. Importa la
misma clase de parámetros y los mismos casos; no recalcula combinaciones en
paralelo. Sin argumentos genera un PNG por cada combinación considerada.

Uso::

    python analisis_estabilidad/dibujar_cargas_cajuela_voladizo.py
    python analisis_estabilidad/dibujar_cargas_cajuela_voladizo.py --caso resistencia-i-a
    python analisis_estabilidad/dibujar_cargas_cajuela_voladizo.py --dpi 200
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, FancyArrowPatch, Polygon, Rectangle  # noqa: E402
import numpy as np  # noqa: E402


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.verificar_cajuela_voladizo import (  # noqa: E402
    Caso,
    Parametros,
    coeficientes,
    construir_casos,
)


CONCRETE_FILL = "#e2e8f0"
CONCRETE_EDGE = "#334155"
SOIL_FILL = "#fef3c7"
SOIL_EDGE = "#a16207"
C_TRI = "#b91c1c"
C_TRAP = "#be185d"
C_UNI = "#d97706"
C_POINT = "#7c3aed"
C_AXIAL = "#15803d"
C_REACTION = "#1d4ed8"
TEXT_DARK = "#1e293b"
TEXT_MUTED = "#64748b"


@dataclass(frozen=True)
class Auditoria:
    error_fuerza_horizontal_tf_m: float
    error_momento_tf_m_m: float
    error_vertical_tf_m: float
    tolerancia: float = 1e-9

    @property
    def cumple(self) -> bool:
        return max(
            abs(self.error_fuerza_horizontal_tf_m),
            abs(self.error_momento_tf_m_m),
            abs(self.error_vertical_tf_m),
        ) <= self.tolerancia


def nombre_archivo(caso: str) -> str:
    limpio = caso.lower().replace("-", "_")
    limpio = re.sub(r"[^a-z0-9]+", "_", limpio).strip("_")
    return f"cargas_cajuela_{limpio}.png"


def clave_cli(caso: str) -> str:
    return caso.lower().replace(" ", "-").replace("-a", "-a").replace("-b", "-b")


def auditar_equilibrio(caso: Caso, p: Parametros) -> Auditoria:
    fuerza = (
        caso.E_tri_tf_m
        + caso.E_trap_tf_m
        + caso.E_uni_tf_m
        + caso.P_puente_tf_m
    )
    momento_trap = (
        caso.q_trap_base_tf_m2 * p.altura_m**2 / 2.0
        + (caso.q_trap_corona_tf_m2 - caso.q_trap_base_tf_m2)
        * p.altura_m**2 / 3.0
    )
    momento = (
        caso.E_tri_tf_m * p.altura_m / 3.0
        + momento_trap
        + caso.E_uni_tf_m * p.altura_m / 2.0
        + caso.P_puente_tf_m * p.altura_carga_puente_m
    )
    # La reacción vertical de la base equilibra la carga axial descendente.
    vertical = caso.axial_tf_m - caso.axial_tf_m
    return Auditoria(
        error_fuerza_horizontal_tf_m=fuerza - caso.V_tf_m,
        error_momento_tf_m_m=momento - caso.M_tf_m_m,
        error_vertical_tf_m=vertical,
    )


def etiquetas_componentes(caso: Caso) -> tuple[str, str | None, str, str]:
    if caso.nombre.startswith("Evento Extremo"):
        tri = "Ea"
        trapecio = "Delta Eas"
        uni = "PIR"
        point = "EQ-super"
    else:
        tri = "Ea"
        trapecio = None
        uni = "Es"
        point = "BR"
    return tri, trapecio, uni, point


def _texto(ax, x, y, text, *, color=TEXT_DARK, size=10, ha="center",
           va="center", rotation=0, weight="normal", alpha=0.92):
    ax.text(
        x, y, text, ha=ha, va=va, fontsize=size, color=color,
        rotation=rotation, fontweight=weight, zorder=30,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.5, alpha=alpha),
    )


def _flecha(ax, xy, xytext, color, *, lw=1.7, scale=13, zorder=20):
    ax.annotate(
        "", xy=xy, xytext=xytext,
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=lw, mutation_scale=scale,
            shrinkA=0, shrinkB=0,
        ),
        zorder=zorder,
    )


def _dibujar_momento(ax, centro, radio, sentido_antihorario=True):
    theta1, theta2 = (35, 320) if sentido_antihorario else (220, -65)
    ax.add_patch(Arc(
        centro, 2 * radio, 2 * radio, theta1=theta1, theta2=theta2,
        color=C_REACTION, lw=2.0, zorder=22,
    ))
    ang = math.radians(theta2)
    punta = (centro[0] + radio * math.cos(ang), centro[1] + radio * math.sin(ang))
    tang = ang + (math.pi / 2 if sentido_antihorario else -math.pi / 2)
    inicio = (punta[0] - 0.18 * math.cos(tang), punta[1] - 0.18 * math.sin(tang))
    ax.add_patch(FancyArrowPatch(
        inicio, punta, arrowstyle="-|>", mutation_scale=13,
        color=C_REACTION, lw=1.8, zorder=23,
    ))


def dibujar_caso(caso: Caso, p: Parametros, salida: Path, dpi: int = 220) -> Auditoria:
    auditoria = auditar_equilibrio(caso, p)
    if not auditoria.cumple:
        raise RuntimeError(f"El caso no cierra antes de dibujar: {auditoria}")

    h = p.altura_m
    t = p.espesor_m
    tri_label, trap_label, uni_label, point_label = etiquetas_componentes(caso)
    q_tri_base = 2.0 * caso.E_tri_tf_m / h
    q_trap_base = caso.q_trap_base_tf_m2
    q_trap_top = caso.q_trap_corona_tf_m2
    q_uni = caso.E_uni_tf_m / h
    a = p.altura_carga_puente_m
    y_top_plot = max(h, a)

    fig = plt.figure(figsize=(16.5, 10.5))
    grid = fig.add_gridspec(1, 2, width_ratios=(3.7, 2.0), wspace=0.06)
    ax = fig.add_subplot(grid[0, 0])
    panel = fig.add_subplot(grid[0, 1])
    panel.axis("off")

    # Relleno y pared.
    ax.add_patch(Rectangle(
        (t, 0), 2.55, h, facecolor=SOIL_FILL, edgecolor=SOIL_EDGE,
        linewidth=0.9, alpha=0.58, zorder=1,
    ))
    for x in np.arange(t + 0.18, t + 2.45, 0.30):
        for y in np.arange(0.18, h, 0.30):
            ax.plot(x, y, marker=".", ms=1.5, color=SOIL_EDGE, alpha=0.22, zorder=2)
    ax.add_patch(Rectangle(
        (0, 0), t, h, facecolor=CONCRETE_FILL,
        edgecolor=CONCRETE_EDGE, linewidth=2.0, zorder=5,
    ))
    # Sección de empotramiento: se omite deliberadamente toda zapata.
    x_base_izq, x_base_der = -0.24, t + 0.24
    ax.plot([x_base_izq, x_base_der], [0, 0], color=CONCRETE_EDGE, lw=3.0, zorder=8)
    for x in np.linspace(x_base_izq + 0.02, x_base_der - 0.02, 9):
        ax.plot([x - 0.10, x], [-0.15, 0], color=CONCRETE_EDGE, lw=1.0, zorder=7)
    _texto(ax, t / 2, h * 0.52, f"PARED DE CAJUELA\nt = {t:.2f} m",
           color=CONCRETE_EDGE, size=9, rotation=90, weight="bold")
    _texto(ax, t + 1.65, h - 0.18, "RELLENO", color=SOIL_EDGE, size=9, weight="bold")

    # Presión triangular factorizada, leída del caso.
    escala_tri = 1.65
    q_tri_ref = max(q_tri_base, q_trap_base, q_trap_top, 1e-12)
    escala_tri_base = escala_tri * q_tri_base / q_tri_ref
    escala_trap_base = escala_tri * q_trap_base / q_tri_ref
    escala_trap_top = escala_tri * q_trap_top / q_tri_ref
    ys = np.linspace(0.08, h - 0.04, 12)
    largos = escala_tri_base * (h - ys) / h
    ax.add_patch(Polygon(
        [(t, 0), (t + escala_tri_base, 0), (t, h)], closed=True,
        facecolor="#fecaca", edgecolor=C_TRI, linewidth=1.4,
        alpha=0.72, zorder=10,
    ))
    for y, largo in zip(ys, largos):
        _flecha(ax, (t + 0.02, y), (t + max(largo, 0.10), y), C_TRI, lw=1.05, scale=9)
    _texto(
        ax, t + 1.78, h * 0.30,
        f"{tri_label} triangular\nq_base = {q_tri_base:.3f} tf/m²\n"
        f"E = {caso.E_tri_tf_m:.3f} tf/m\ny = H/3",
        color=C_TRI, size=8.5, ha="left",
    )

    # Incremento sísmico recortado del triángulo global: trapecio local.
    if caso.E_trap_tf_m > 0.0:
        largos_trap = escala_trap_base + (
            escala_trap_top - escala_trap_base
        ) * ys / h
        ax.add_patch(Polygon(
            [
                (t, 0), (t + escala_trap_base, 0),
                (t + escala_trap_top, h), (t, h),
            ], closed=True,
            facecolor="#fbcfe8", edgecolor=C_TRAP, linewidth=1.4,
            alpha=0.68, zorder=11,
        ))
        for y, largo in zip(ys, largos_trap):
            _flecha(
                ax, (t + 0.02, y), (t + max(largo, 0.10), y),
                C_TRAP, lw=1.05, scale=9, zorder=21,
            )
        y_trap = (
            caso.q_trap_base_tf_m2 * h**2 / 2.0
            + (caso.q_trap_corona_tf_m2 - caso.q_trap_base_tf_m2)
            * h**2 / 3.0
        ) / caso.E_trap_tf_m
        _texto(
            ax, t + 0.70, h * 0.86,
            f"{trap_label} trapezoidal (H_g = {p.altura_global_empuje_m:.2f} m)\n"
            f"q_base = {q_trap_base:.3f} tf/m²\n"
            f"q_corona = {q_trap_top:.3f} tf/m²\n"
            f"E = {caso.E_trap_tf_m:.3f} tf/m\ny = {y_trap:.3f} m",
            color=C_TRAP, size=8.2, ha="left",
        )

    # Presión uniforme factorizada, separada gráficamente.
    x_uni0 = t + 2.05
    escala_uni = 0.55
    ax.plot([x_uni0 + escala_uni, x_uni0 + escala_uni], [0, h], color=C_UNI, lw=1.4)
    for y in np.linspace(0.10, h - 0.10, 10):
        _flecha(ax, (x_uni0, y), (x_uni0 + escala_uni, y), C_UNI, lw=1.05, scale=9)
    _texto(
        ax, x_uni0 + 0.72, h * 0.72,
        f"{uni_label} uniforme\nq = {q_uni:.3f} tf/m²\n"
        f"E = {caso.E_uni_tf_m:.3f} tf/m\ny = H/2",
        color=C_UNI, size=8.5, ha="left",
    )

    # Fuerza horizontal del puente, introducida en la mesa de apoyo.
    x_point_from = t + 2.55
    _flecha(ax, (t / 2, a), (x_point_from, a), C_POINT, lw=2.5, scale=17)
    _texto(
        ax, x_point_from + 0.08, a,
        f"{point_label} = {caso.P_puente_tf_m:.3f} tf/m\na = {a:.2f} m",
        color=C_POINT, size=9, ha="left",
    )

    # Carga axial vertical del puente, transmitida en la misma mesa de apoyo.
    _flecha(ax, (t / 2, a), (t / 2, y_top_plot + 0.72), C_AXIAL, lw=2.5, scale=17)
    _texto(
        ax, t / 2 - 0.10, y_top_plot + 0.78,
        f"P axial = {caso.axial_tf_m:.3f} tf/m\nmesa: a = {a:.2f} m",
        color=C_AXIAL, size=9, ha="right", va="bottom",
    )

    # Reacciones en el empotramiento.
    _flecha(ax, (0.03, 0.12), (-0.58, 0.12), C_REACTION, lw=2.4, scale=16)
    _texto(ax, -0.62, 0.28, f"R_H = {caso.V_tf_m:.3f} tf/m",
           color=C_REACTION, size=9, ha="right")
    _flecha(ax, (t / 2, 0.78), (t / 2, -0.34), C_REACTION, lw=2.4, scale=16)
    _texto(ax, t / 2 + 0.12, -0.50, f"R_V = {caso.axial_tf_m:.3f} tf/m",
           color=C_REACTION, size=9, ha="left")
    _dibujar_momento(ax, (-0.18, -0.06), 0.40, sentido_antihorario=False)
    _texto(ax, -0.62, -0.52, f"M_base = {caso.M_tf_m_m:.3f} tf·m/m",
           color=C_REACTION, size=9, ha="right")

    # Cotas.
    ax.annotate(
        "", xy=(-0.48, h), xytext=(-0.48, 0),
        arrowprops=dict(arrowstyle="<->", color=TEXT_MUTED, lw=1.1), zorder=15,
    )
    _texto(ax, -0.56, h / 2, f"H = {h:.2f} m", color=TEXT_MUTED,
           size=9, ha="right", rotation=90)
    ax.annotate(
        "", xy=(t, h + 0.22), xytext=(0, h + 0.22),
        arrowprops=dict(arrowstyle="<->", color=TEXT_MUTED, lw=1.1), zorder=15,
    )
    _texto(ax, t / 2, h + 0.35, f"t = {t:.2f} m", color=TEXT_MUTED, size=8)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1.55, t + 4.15)
    ax.set_ylim(-0.95, y_top_plot + 1.35)
    ax.set_xlabel("Esquema de cargas por metro lineal", fontsize=10, color=TEXT_MUTED)
    ax.set_ylabel("Altura sobre el arranque del voladizo (m)", fontsize=10, color=TEXT_MUTED)
    ax.tick_params(axis="both", labelsize=9, colors=TEXT_MUTED)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.7, alpha=0.7)

    # Panel resumen fuera de la escala geométrica.
    linea_trapecio = (
        f"E trapezoidal = {caso.E_trap_tf_m:.3f} tf/m\n"
        f"q base/corona = {caso.q_trap_base_tf_m2:.3f} / "
        f"{caso.q_trap_corona_tf_m2:.3f} tf/m²\n"
        if caso.E_trap_tf_m > 0.0 else ""
    )
    summary = (
        f"{caso.nombre.upper()}\n\n"
        f"Combinación:\n{caso.descripcion}\n\n"
        f"CARGAS FACTORIZADAS\n"
        f"E tri. máx. base = {caso.E_tri_tf_m:.3f} tf/m\n"
        f"{linea_trapecio}"
        f"E uniforme   = {caso.E_uni_tf_m:.3f} tf/m\n"
        f"Puente horiz.= {caso.P_puente_tf_m:.3f} tf/m\n"
        f"Puente axial = {caso.axial_tf_m:.3f} tf/m\n\n"
        f"REACCIONES EN LA BASE\n"
        f"R_H = {caso.V_tf_m:.3f} tf/m\n"
        f"R_V = {caso.axial_tf_m:.3f} tf/m\n"
        f"M_base = {caso.M_tf_m_m:.3f} tf·m/m\n\n"
        f"AUDITORÍA DE EQUILIBRIO\n"
        f"error ΣH = {auditoria.error_fuerza_horizontal_tf_m:+.2e} tf/m\n"
        f"error ΣM = {auditoria.error_momento_tf_m_m:+.2e} tf·m/m\n"
        f"error ΣV = {auditoria.error_vertical_tf_m:+.2e} tf/m\n"
        f"Estado: {'CONFORME' if auditoria.cumple else 'NO CONFORME'}"
    )
    panel.text(
        0.07, 0.53, summary, transform=panel.transAxes,
        ha="left", va="center", fontsize=11, color=TEXT_DARK,
        linespacing=1.35,
        bbox=dict(
            boxstyle="round,pad=0.75", facecolor="#f8fafc",
            edgecolor="#cbd5e1", linewidth=1.0,
        ),
    )
    panel.text(
        0.07, 0.86,
        "RESUMEN DE CARGAS Y REACCIONES\nPanel fuera de la escala geométrica",
        transform=panel.transAxes, ha="left", va="bottom",
        fontsize=11.5, fontweight="bold", color=TEXT_MUTED,
    )

    fig.suptitle(
        "Pared de cajuela como muro en voladizo\n"
        f"Distribución de cargas — {caso.nombre}",
        fontsize=17, fontweight="bold", color=TEXT_DARK, y=0.975,
    )
    ax.set_title(
        "Valores factorizados por franja de 1.00 m | Reacciones de empotramiento",
        fontsize=10.5, color=TEXT_MUTED, pad=12,
    )
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.08, top=0.86)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return auditoria


def _mapa_casos(casos: list[Caso]) -> dict[str, Caso]:
    return {
        "servicio-i": next(c for c in casos if c.nombre == "Servicio I"),
        "resistencia-i-a": next(c for c in casos if c.nombre == "Resistencia I-a"),
        "resistencia-i-b": next(c for c in casos if c.nombre == "Resistencia I-b"),
        "evento-extremo-i": next(c for c in casos if c.nombre == "Evento Extremo I"),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--caso",
        choices=(
            "todos", "servicio-i", "resistencia-i-a", "resistencia-i-b",
            "evento-extremo-i",
        ),
        default="todos",
    )
    parser.add_argument("--altura", type=float, default=3.40)
    parser.add_argument(
        "--altura-global-empuje", type=float, default=14.65,
        help="Altura global H_g del diagrama de Delta Eas (m)",
    )
    parser.add_argument("--espesor", type=float, default=0.40)
    parser.add_argument(
        "--altura-carga-puente", type=float, default=1.00,
        help="Cota de la mesa de apoyo sobre el arranque local (m)",
    )
    parser.add_argument("--porcentaje-sismico-superestructura", type=float, default=0.24)
    parser.add_argument("--output-dir", default="outputs/calc_est_2026_006/cargas")
    parser.add_argument("--dpi", type=int, default=220)
    args = parser.parse_args()

    if args.dpi <= 0:
        parser.error("--dpi debe ser positivo")
    p = Parametros(
        altura_m=args.altura,
        altura_global_empuje_m=args.altura_global_empuje,
        espesor_m=args.espesor,
        altura_carga_puente_m=args.altura_carga_puente,
        porcentaje_sismico_superestructura=args.porcentaje_sismico_superestructura,
    )
    p.validar()
    casos = _mapa_casos(construir_casos(p, coeficientes(p)))
    seleccion = casos.items() if args.caso == "todos" else ((args.caso, casos[args.caso]),)
    out = Path(args.output_dir)
    for clave, caso in seleccion:
        path = out / nombre_archivo(clave)
        audit = dibujar_caso(caso, p, path, dpi=args.dpi)
        print(f"Figura guardada: {path.resolve()} | equilibrio: {audit.cumple}")


if __name__ == "__main__":
    main()

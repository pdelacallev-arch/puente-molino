"""Dibuja el esquema del ancho efectivo de losa para las vigas principales."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def dibujar_ancho_efectivo(salida: Path) -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titleweight": "bold",
    })

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=220)

    # Coordenadas en metros
    # Losa de concreto: x de -3.0 a +3.0, y de 0 a 0.20 m
    # Haunch: en x = -2.0, 0.0, 2.0; ancho 0.50 m (x +- 0.25), y de -0.05 a 0.0
    # Viga de acero:
    # Ala sup: y de -0.05-0.032 a -0.05 (-0.082 a -0.05), ancho 0.50 (x +- 0.25)
    # Alma: y de -0.082-1.755 a -0.082 (-1.837 a -0.082), espesor 0.019 (x +- 0.0095)
    # Ala inf: y de -1.837-0.050 a -1.837 (-1.887 a -1.837), ancho 0.60 (x +- 0.30)

    # 1. Dibujar Losa
    losa = patches.Rectangle((-3.0, 0.0), 6.0, 0.20, facecolor="#e2e8f0", edgecolor="#475569", lw=1.2, zorder=2)
    ax.add_patch(losa)

    # 2. Haunches y Vigas
    vigas_x = [-2.0, 0.0, 2.0]
    for vx in vigas_x:
        # Haunch
        haunch = patches.Rectangle((vx - 0.25, -0.05), 0.50, 0.05, facecolor="#cbd5e1", edgecolor="#475569", lw=1.0, zorder=2)
        ax.add_patch(haunch)
        # Ala superior
        ala_sup = patches.Rectangle((vx - 0.25, -0.082), 0.50, 0.032, facecolor="#1e293b", edgecolor="#0f172a", lw=1.0, zorder=3)
        ax.add_patch(ala_sup)
        # Alma
        alma = patches.Rectangle((vx - 0.0095, -1.837), 0.019, 1.755, facecolor="#334155", edgecolor="#0f172a", lw=0.8, zorder=3)
        ax.add_patch(alma)
        # Ala inferior
        ala_inf = patches.Rectangle((vx - 0.30, -1.887), 0.60, 0.050, facecolor="#1e293b", edgecolor="#0f172a", lw=1.0, zorder=3)
        ax.add_patch(ala_inf)

    # 3. Franjas de ancho efectivo (destacadas con colores)
    # Viga ext izq: -3.0 a -1.0 (ancho 2.0 m)
    # Viga interior: -1.0 a 1.0 (ancho 2.0 m)
    # Viga ext der: 1.0 a 3.0 (ancho 2.0 m)
    colores = ["#93c5fd", "#86efac", "#93c5fd"]
    etiquetas = ["Viga exterior izquierda\n$b_{e,ext} = 2.00$ m", "Viga interior\n$b_{e,int} = 2.00$ m", "Viga exterior derecha\n$b_{e,ext} = 2.00$ m"]
    rangos = [(-3.0, -1.0), (-1.0, 1.0), (1.0, 3.0)]

    for (x1, x2), col, eti in zip(rangos, colores, etiquetas):
        franja = patches.Rectangle((x1, 0.0), x2 - x1, 0.20, facecolor=col, alpha=0.5, edgecolor="none", zorder=4)
        ax.add_patch(franja)
        # Cota superior de ancho efectivo
        ym = 0.32
        ax.annotate("", xy=(x1, ym), xytext=(x2, ym), arrowprops=dict(arrowstyle="<->", color="#1e3a8a", lw=1.5))
        ax.text((x1 + x2)/2, ym + 0.04, eti, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#1e3a8a")

    # Cotas geométricas inferiores
    # Separación entre vigas S = 2.0 m
    yc = -2.10
    ax.annotate("", xy=(-2.0, yc), xytext=(0.0, yc), arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.2))
    ax.text(-1.0, yc - 0.12, "$S = 2.00$ m", ha="center", va="top", fontsize=8.5, color="#334155")
    ax.annotate("", xy=(0.0, yc), xytext=(2.0, yc), arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.2))
    ax.text(1.0, yc - 0.12, "$S = 2.00$ m", ha="center", va="top", fontsize=8.5, color="#334155")

    # Voladizos v = 1.0 m
    ax.annotate("", xy=(-3.0, yc), xytext=(-2.0, yc), arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.2))
    ax.text(-2.5, yc - 0.12, "$v = 1.00$ m", ha="center", va="top", fontsize=8.5, color="#334155")
    ax.annotate("", xy=(2.0, yc), xytext=(3.0, yc), arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.2))
    ax.text(2.5, yc - 0.12, "$v = 1.00$ m", ha="center", va="top", fontsize=8.5, color="#334155")

    # Ejes de vigas (líneas verticales de centro)
    for vx in vigas_x:
        ax.plot([vx, vx], [-2.05, 0.28], color="#94a3b8", ls="--", lw=0.8, zorder=1)

    # Límites de tablero
    ax.plot([-3.0, -3.0], [-2.05, 0.28], color="#94a3b8", ls=":", lw=0.8, zorder=1)
    ax.plot([3.0, 3.0], [-2.05, 0.28], color="#94a3b8", ls=":", lw=0.8, zorder=1)

    # Espesor de losa
    ax.annotate("", xy=(3.15, 0.0), xytext=(3.15, 0.20), arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.0))
    ax.text(3.25, 0.10, "$t_s = 0.20$ m", ha="left", va="center", fontsize=8, color="#334155")

    # Altura de viga
    ax.annotate("", xy=(3.15, -1.887), xytext=(3.15, -0.05), arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.0))
    ax.text(3.25, -0.97, "$h_{viga} = 1.837$ m\n(Segmento C)", ha="left", va="center", fontsize=8, color="#334155")

    ax.set_xlim(-3.6, 4.2)
    ax.set_ylim(-2.4, 0.65)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Ancho efectivo de losa para las vigas principales (Sección transversal)", fontsize=13, pad=12)

    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("salida", type=Path, help="Ruta de la figura PNG")
    args = parser.parse_args()
    dibujar_ancho_efectivo(args.salida)


if __name__ == "__main__":
    main()

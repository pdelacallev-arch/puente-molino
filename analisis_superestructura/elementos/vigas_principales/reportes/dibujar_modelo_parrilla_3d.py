"""Dibuja la idealizacion tridimensional del modelo de parrilla.

La geometria se lee del resultado del analisis para conservar exactamente la
malla longitudinal, los ejes transversales y la posicion de las vigas usadas
en el calculo.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def _buscar_parrilla(objeto: Any) -> dict[str, Any] | None:
    """Localiza el bloque que contiene la geometria de la parrilla."""
    if isinstance(objeto, dict):
        claves = {"x_nodos_mm", "y_nodos_mm", "y_vigas_mm"}
        if claves.issubset(objeto):
            return objeto
        for valor in objeto.values():
            hallado = _buscar_parrilla(valor)
            if hallado is not None:
                return hallado
    elif isinstance(objeto, list):
        for valor in objeto:
            hallado = _buscar_parrilla(valor)
            if hallado is not None:
                return hallado
    return None


def dibujar_modelo(resultado: Path, salida: Path) -> None:
    datos = json.loads(resultado.read_text(encoding="utf-8"))
    parrilla = _buscar_parrilla(datos)
    if parrilla is None:
        raise ValueError("No se encontro la geometria de la parrilla en el resultado.")

    x = np.asarray(parrilla["x_nodos_mm"], dtype=float) / 1000.0
    y = np.asarray(parrilla["y_nodos_mm"], dtype=float) / 1000.0
    y_vigas = np.asarray(parrilla["y_vigas_mm"], dtype=float) / 1000.0
    z = np.zeros_like(x)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titleweight": "bold",
        }
    )
    fig = plt.figure(figsize=(13.5, 7.2), dpi=180)
    ax = fig.add_subplot(111, projection="3d")

    # Superficie tenue del tablero; los elementos de la parrilla permanecen visibles.
    xx, yy = np.meshgrid([x.min(), x.max()], [y.min(), y.max()])
    ax.plot_surface(
        xx,
        yy,
        np.full_like(xx, -0.035),
        color="#d9eaf2",
        alpha=0.28,
        shade=False,
        edgecolor="none",
    )

    # Franjas transversales de losa en cada estacion de la malla.
    for xi in x:
        ax.plot(
            np.full_like(y, xi),
            y,
            np.zeros_like(y),
            color="#d97706",
            linewidth=0.95,
            alpha=0.82,
            zorder=3,
        )

    # Vigas longitudinales compuestas.
    colores_viga = ["#164e63", "#0f766e", "#164e63"]
    for indice, yv in enumerate(y_vigas):
        ax.plot(
            x,
            np.full_like(x, yv),
            z,
            color=colores_viga[indice % len(colores_viga)],
            linewidth=3.0,
            solid_capstyle="round",
            zorder=5,
        )

    # Nodos analiticos: cinco ejes transversales por estacion longitudinal.
    xn, yn = np.meshgrid(x, y, indexing="ij")
    ax.scatter(
        xn.ravel(),
        yn.ravel(),
        np.zeros(xn.size),
        s=7,
        color="#172554",
        depthshade=False,
        zorder=6,
    )

    # Restricciones w=0 en ambos extremos de cada viga; los giros permanecen libres.
    z_apoyo = -0.42
    for xi in (x.min(), x.max()):
        for yv in y_vigas:
            ax.plot([xi, xi], [yv, yv], [0.0, z_apoyo + 0.07], color="#334155", lw=0.8)
            ax.scatter(
                [xi],
                [yv],
                [z_apoyo],
                marker="^",
                s=75,
                facecolor="#f8fafc",
                edgecolor="#111827",
                linewidth=0.9,
                depthshade=False,
                zorder=7,
            )

    ax.set_title("Modelo estructural de parrilla elástica lineal", pad=14, fontsize=14)
    ax.set_xlabel("Eje longitudinal, X (m)", labelpad=10)
    ax.set_ylabel("Eje transversal, Y (m)", labelpad=9)
    ax.set_xlim(-1.0, 52.5)
    ax.set_ylim(-4.1, 4.1)
    ax.set_zlim(-0.65, 0.65)
    ax.set_xticks(np.arange(0.0, 50.1, 10.0))
    ax.set_yticks([-3.0, -2.0, 0.0, 2.0, 3.0])
    ax.set_zticks([])
    ax.set_box_aspect((5.2, 1.75, 0.78))
    ax.view_init(elev=27, azim=-61)

    ax.xaxis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.pane.set_facecolor((0.96, 0.97, 0.98, 0.65))
    ax.grid(True, color="#cbd5e1", linewidth=0.45, alpha=0.7)

    leyenda = [
        Line2D([0], [0], color="#164e63", lw=3.0, label="Vigas longitudinales"),
        Line2D([0], [0], color="#d97706", lw=1.2, label="Franjas transversales de losa"),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#172554",
            markeredgecolor="#172554",
            markersize=4,
            label="Nodos (3 GDL: w, θx, θy)",
        ),
        Line2D(
            [0],
            [0],
            marker="^",
            color="none",
            markerfacecolor="#f8fafc",
            markeredgecolor="#111827",
            markersize=7,
            label="Apoyo: desplazamiento vertical restringido",
        ),
    ]
    ax.legend(
        handles=leyenda,
        loc="upper left",
        bbox_to_anchor=(0.015, 0.95),
        frameon=True,
        framealpha=0.95,
        edgecolor="#cbd5e1",
        fontsize=8.5,
    )

    fig.text(
        0.985,
        0.82,
        "L = 50.00 m  |  B = 6.00 m  |  3 vigas  |  S = 2.00 m",
        ha="right",
        color="#0f766e",
        fontsize=9,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.02,
        f"Malla analítica: {len(x)} estaciones longitudinales, {len(y)} ejes transversales, "
        f"{len(x) * len(y)} nodos y {3 * len(x) * len(y)} grados de libertad.",
        ha="center",
        color="#334155",
        fontsize=9,
    )
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.08, top=0.91)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resultado", type=Path, help="Archivo resultado.json del analisis")
    parser.add_argument("salida", type=Path, help="Ruta de la figura PNG")
    args = parser.parse_args()
    dibujar_modelo(args.resultado, args.salida)


if __name__ == "__main__":
    main()

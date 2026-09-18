"""Dibuja las lineas de influencia y las posiciones criticas del camion HL-93."""

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


def _buscar_casos_criticos(objeto: Any) -> dict[str, Any] | None:
    """Localiza el bloque de casos criticos de la parrilla en el resultado."""
    if isinstance(objeto, dict):
        casos = objeto.get("casos_criticos")
        if isinstance(casos, dict) and {"momento", "corte"}.issubset(casos):
            return casos
        for valor in objeto.values():
            hallado = _buscar_casos_criticos(valor)
            if hallado is not None:
                return hallado
    elif isinstance(objeto, list):
        for valor in objeto:
            hallado = _buscar_casos_criticos(valor)
            if hallado is not None:
                return hallado
    return None


def _buscar_analisis(objeto: Any) -> dict[str, Any] | None:
    """Localiza las envolventes longitudinales y sus estaciones."""
    if isinstance(objeto, dict):
        if {"x_mm", "tipos_viga", "factores_distribucion"}.issubset(objeto):
            return objeto
        for valor in objeto.values():
            hallado = _buscar_analisis(valor)
            if hallado is not None:
                return hallado
    elif isinstance(objeto, list):
        for valor in objeto:
            hallado = _buscar_analisis(valor)
            if hallado is not None:
                return hallado
    return None


def _influencia_momento(x: np.ndarray, luz: float, seccion: float) -> np.ndarray:
    return np.where(
        x <= seccion,
        x * (luz - seccion) / luz,
        seccion * (luz - x) / luz,
    )


def _influencia_reaccion_izquierda(x: np.ndarray, luz: float) -> np.ndarray:
    return (luz - x) / luz


def _dibujar_carga_carril(
    ax: plt.Axes,
    luz: float,
    nivel: float,
    texto_y: float,
) -> None:
    color = "#15803d"
    ax.plot([0.0, luz], [nivel, nivel], color=color, lw=1.8, solid_capstyle="round")
    for xi in np.linspace(1.0, luz - 1.0, 22):
        ax.annotate(
            "",
            xy=(xi, nivel - 0.10),
            xytext=(xi, nivel),
            arrowprops={"arrowstyle": "-|>", "color": color, "lw": 0.7},
        )
    ax.text(
        luz,
        texto_y,
        r"Carga de carril $q=9.30$ kN/m sobre la zona favorable",
        ha="right",
        va="bottom",
        color=color,
        fontsize=8.5,
        fontweight="bold",
    )


def _dibujar_camion(
    ax: plt.Axes,
    caso: dict[str, Any],
    ordenadas: np.ndarray,
    posiciones: np.ndarray,
    nivel_superior: float,
    escala_flecha: float,
    niveles_texto: tuple[float, ...] | None = None,
    alineaciones: tuple[str, ...] | None = None,
) -> None:
    color = "#b91c1c"
    cargas_kn = np.asarray(caso["cargas_eje_n"], dtype=float) / 1000.0
    for indice, (xi, yi, carga) in enumerate(zip(posiciones, ordenadas, cargas_kn), start=1):
        ax.annotate(
            "",
            xy=(xi, yi),
            xytext=(xi, nivel_superior),
            arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.8, "mutation_scale": 11},
            zorder=8,
        )
        alineacion = (
            alineaciones[indice - 1]
            if alineaciones is not None
            else ("left" if xi < 1.0 else "center")
        )
        y_texto = (
            niveles_texto[indice - 1]
            if niveles_texto is not None
            else nivel_superior + escala_flecha
        )
        ax.text(
            xi,
            y_texto,
            f"P{indice}={carga:.1f} kN\nx={xi:.2f} m",
            ha=alineacion,
            va="bottom",
            color=color,
            fontsize=8.1,
            fontweight="bold",
        )


def dibujar(resultado: Path, salida: Path, luz: float = 50.0) -> None:
    datos = json.loads(resultado.read_text(encoding="utf-8"))
    casos = _buscar_casos_criticos(datos)
    analisis = _buscar_analisis(datos)
    if casos is None or analisis is None:
        raise ValueError("No se encontraron las envolventes o los casos criticos.")

    caso_m = casos["momento"]
    caso_v = casos["corte"]
    x_analisis = np.asarray(analisis["x_mm"], dtype=float)
    interior = analisis["tipos_viga"]["interior"]
    envolvente_m = np.asarray(interior["momentos_nmm"]["LL_IM"], dtype=float)
    indice_maximo = int(np.argmax(envolvente_m))
    seccion_m = x_analisis[indice_maximo] / 1000.0
    factor_momento = float(interior["factor_momento"])
    momento_knm = envolvente_m[indice_maximo] / factor_momento / 1.0e6

    offsets_m = np.asarray(caso_m["offsets_mm"], dtype=float) / 1000.0
    cargas_m_kn = np.asarray(caso_m["cargas_eje_n"], dtype=float) / 1000.0
    q_kn_m = float(caso_m["carga_carril_n_mm"])
    mejor: tuple[float, np.ndarray] | None = None
    for offset_eje in offsets_m:
        posiciones = seccion_m - offset_eje + offsets_m
        mascara = (posiciones >= 0.0) & (posiciones <= luz)
        ordenadas = _influencia_momento(posiciones[mascara], luz, seccion_m)
        respuesta = float(np.dot(cargas_m_kn[mascara], ordenadas))
        respuesta += q_kn_m * seccion_m * (luz - seccion_m) / 2.0
        if mejor is None or respuesta > mejor[0]:
            mejor = (respuesta, posiciones)
    if mejor is None:
        raise RuntimeError("No se pudo ubicar el camion critico de momento.")
    posiciones_m = mejor[1]
    posiciones_v = (
        float(caso_v["posicion_frente_mm"])
        + np.asarray(caso_v["offsets_mm"], dtype=float)
    ) / 1000.0

    x = np.linspace(0.0, luz, 1001)
    eta_m = _influencia_momento(x, luz, seccion_m)
    eta_v = _influencia_reaccion_izquierda(x, luz)
    eta_m_ejes = _influencia_momento(posiciones_m, luz, seccion_m)
    eta_v_ejes = _influencia_reaccion_izquierda(posiciones_v, luz)

    reaccion_kn = float(caso_v["respuesta_referencia"]) / 1000.0

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titleweight": "bold",
            "axes.edgecolor": "#64748b",
        }
    )
    fig, ejes = plt.subplots(2, 1, figsize=(13.2, 8.4), dpi=180, sharex=True)
    azul = "#1d4ed8"
    relleno = "#bfdbfe"

    ax = ejes[0]
    ax.plot(x, eta_m, color=azul, lw=2.2, zorder=3)
    ax.fill_between(x, 0.0, eta_m, color=relleno, alpha=0.62, zorder=1)
    ax.axhline(0.0, color="#334155", lw=0.9)
    _dibujar_carga_carril(ax, luz, 14.45, 14.62)
    _dibujar_camion(ax, caso_m, eta_m_ejes, posiciones_m, 13.55, 0.17)
    ax.axvline(seccion_m, color="#64748b", lw=0.9, ls="--", zorder=2)
    ax.text(
        seccion_m,
        0.32,
        f"Sección crítica\nx = {seccion_m:.2f} m",
        ha="center",
        color="#475569",
    )
    ax.text(
        0.985,
        0.48,
        f"Efecto máximo por carril\n$M_{{LL+IM}}={momento_knm:,.2f}$ kN·m",
        transform=ax.transAxes,
        ha="right",
        va="center",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#93c5fd"},
        fontsize=9,
    )
    ax.set_ylim(-0.25, 15.5)
    ax.set_ylabel(r"Ordenada $\eta_M$ (m)")
    ax.set_title("a) Momento positivo máximo")

    ax = ejes[1]
    ax.plot(x, eta_v, color=azul, lw=2.2, zorder=3)
    ax.fill_between(x, 0.0, eta_v, color=relleno, alpha=0.62, zorder=1)
    ax.axhline(0.0, color="#334155", lw=0.9)
    _dibujar_carga_carril(ax, luz, 1.22, 1.245)
    _dibujar_camion(
        ax,
        caso_v,
        eta_v_ejes,
        posiciones_v,
        1.12,
        0.025,
        niveles_texto=(1.145, 1.31, 1.145),
        alineaciones=("left", "left", "left"),
    )
    ax.scatter([0.0], [1.0], s=28, color=azul, zorder=5)
    ax.text(
        0.985,
        0.44,
        f"Efecto máximo por carril\n$V_{{LL+IM}}={reaccion_kn:,.2f}$ kN",
        transform=ax.transAxes,
        ha="right",
        va="center",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#93c5fd"},
        fontsize=9,
    )
    ax.set_ylim(-0.03, 1.37)
    ax.set_ylabel(r"Ordenada $\eta_V$ (—)")
    ax.set_xlabel("Posición longitudinal de la carga, z (m)")
    ax.set_title("b) Reacción — cortante positivo en el apoyo izquierdo")

    for ax in ejes:
        ax.set_xlim(-1.2, luz + 1.0)
        ax.set_xticks(np.arange(0.0, luz + 0.1, 5.0))
        ax.grid(True, which="major", color="#cbd5e1", linewidth=0.55, alpha=0.75)
        ax.spines[["top", "right"]].set_visible(False)

    leyenda = [
        Line2D([0], [0], color=azul, lw=2.2, label="Línea de influencia"),
        Line2D([0], [0], color="#b91c1c", lw=1.8, marker="v", label="Ejes del camión con IM = 33 %"),
        Line2D([0], [0], color="#15803d", lw=1.8, label="Carga de carril"),
    ]
    fig.legend(
        handles=leyenda,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.944),
        ncol=3,
        frameon=True,
        framealpha=0.96,
        edgecolor="#cbd5e1",
    )
    fig.suptitle("Líneas de influencia y posiciones críticas del camión HL-93", fontsize=15, y=0.99)
    fig.text(
        0.5,
        0.014,
        "Las cargas de eje mostradas incluyen el incremento dinámico; la carga de carril no lo incluye.",
        ha="center",
        color="#475569",
        fontsize=8.8,
    )
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.09, top=0.88, hspace=0.32)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resultado", type=Path, help="Archivo resultado.json del análisis")
    parser.add_argument("salida", type=Path, help="Ruta de la figura PNG")
    parser.add_argument("--luz", type=float, default=50.0, help="Luz del puente, en m")
    args = parser.parse_args()
    dibujar(args.resultado, args.salida, args.luz)


if __name__ == "__main__":
    main()

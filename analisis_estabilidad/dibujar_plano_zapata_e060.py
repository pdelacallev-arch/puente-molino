#!/usr/bin/env python3
"""Genera el plano técnico de armaduras de la zapata diseñada con E.060.

El script no repite cálculos estructurales: consume exclusivamente la salida
de ``disenar_zapata_e060.disenar()`` y genera únicamente la sección A-A
punta-pantalla-talón con armaduras, desarrollos, ganchos y cotas.

Salida predeterminada: PNG y SVG en ``outputs/``.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.disenar_zapata_e060 import disenar  # noqa: E402


COLOR_CONCRETO = "#e5e7eb"
COLOR_BORDE = "#111827"
COLOR_SUPERIOR = "#1d4ed8"
COLOR_INFERIOR = "#dc2626"
COLOR_TRANSVERSAL = "#059669"
COLOR_COTA = "#374151"
COLOR_TEXTO = "#111827"


def _mapa_armaduras(resultado: dict) -> dict[tuple[str, str], dict]:
    return {
        (r["zona"], r["cara"]): r
        for r in resultado["refuerzo_envolvente"]
    }


def _mapa_anclajes(resultado: dict) -> dict[tuple[str, str, str], dict]:
    return {
        (r["direccion"], r["zona"], r["cara"]): r
        for r in resultado["desarrollo_y_anclajes"]
    }


def _cota_horizontal(ax, x1: float, x2: float, y: float, texto: str,
                     extension_y: float | None = None) -> None:
    ax.annotate(
        "", xy=(x1, y), xytext=(x2, y),
        arrowprops=dict(arrowstyle="<->", color=COLOR_COTA, lw=0.8),
        zorder=20,
    )
    if extension_y is not None:
        ax.plot([x1, x1], [extension_y, y], color=COLOR_COTA, lw=0.5)
        ax.plot([x2, x2], [extension_y, y], color=COLOR_COTA, lw=0.5)
    ax.text((x1 + x2) / 2, y + 0.08, texto, ha="center", va="bottom",
            fontsize=7, color=COLOR_TEXTO,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.4))


def _cota_vertical(ax, x: float, y1: float, y2: float, texto: str,
                   extension_x: float | None = None) -> None:
    ax.annotate(
        "", xy=(x, y1), xytext=(x, y2),
        arrowprops=dict(arrowstyle="<->", color=COLOR_COTA, lw=0.8),
        zorder=20,
    )
    if extension_x is not None:
        ax.plot([extension_x, x], [y1, y1], color=COLOR_COTA, lw=0.5)
        ax.plot([extension_x, x], [y2, y2], color=COLOR_COTA, lw=0.5)
    ax.text(x + 0.08, (y1 + y2) / 2, texto, ha="left", va="center",
            fontsize=7, rotation=90, color=COLOR_TEXTO,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.4))


def _dibujar_barra_seccion(ax, x_inicio: float, x_fin: float, y: float,
                           gancho_x: float, gancho_hacia_arriba: bool,
                           color: str, etiqueta: str, texto_x: float,
                           texto_y: float) -> None:
    ax.plot([x_inicio, x_fin], [y, y], color=color, lw=2.0,
            solid_capstyle="round", zorder=10)
    altura = 0.38 if gancho_hacia_arriba else -0.38
    ax.plot([gancho_x, gancho_x], [y, y + altura], color=color, lw=2.0,
            solid_capstyle="round", zorder=10)
    ax.annotate(
        etiqueta, xy=((x_inicio + x_fin) / 2, y), xytext=(texto_x, texto_y),
        fontsize=7, fontweight="bold", color=color,
        arrowprops=dict(arrowstyle="->", color=color, lw=0.7),
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                  edgecolor=color, linewidth=0.6), zorder=25,
    )


def _dibujar_seccion(ax, resultado: dict) -> None:
    g = resultado["geometria_m"]
    p = resultado["parametros"]
    acero = _mapa_armaduras(resultado)
    anc = _mapa_anclajes(resultado)
    B, B2, tp2, B1, h = (
        g["B"], g["B2_punta"], g["tp2"], g["B1_talon"], g["h"],
    )
    rec = p["recubrimiento_mm"] / 1000.0
    x_frente = B2
    x_posterior = B2 + tp2

    ax.add_patch(Rectangle((0, 0), B, h, facecolor=COLOR_CONCRETO,
                           edgecolor=COLOR_BORDE, linewidth=1.1, zorder=2))
    ax.add_patch(Rectangle((x_frente, h), tp2, 2.15,
                           facecolor=COLOR_CONCRETO, edgecolor=COLOR_BORDE,
                           linewidth=1.1, zorder=2))
    ax.plot([x_frente, x_posterior], [h + 1.88, h + 2.02],
            color="white", lw=5, zorder=3)
    ax.plot([x_frente, x_posterior], [h + 1.88, h + 2.02],
            color=COLOR_BORDE, lw=0.7, linestyle="--", zorder=4)

    marcas = {
        ("punta", "superior"): "L1",
        ("punta", "inferior"): "L2",
        ("talon", "superior"): "L3",
        ("talon", "inferior"): "L4",
    }
    for zona, cara in marcas:
        item = acero[(zona, cara)]
        anclaje = anc[("longitudinal", zona, cara)]
        ld = anclaje["ld_adoptada_mm"] / 1000.0
        db = item["diametro_mm"] / 1000.0
        y = h - rec - db / 2 if cara == "superior" else rec + db / 2
        color = COLOR_SUPERIOR if cara == "superior" else COLOR_INFERIOR
        if zona == "punta":
            x1, x2, gancho_x = rec, min(x_frente + ld, B - rec), rec
            tx = 0.35 * B2
        else:
            x1, x2, gancho_x = max(x_posterior - ld, rec), B - rec, B - rec
            tx = x_posterior + 0.60 * B1
        texto = (
            f"{marcas[(zona, cara)]}  Ø{item['barra']} @ "
            f"{item['espaciamiento_adoptado_mm']:.0f} mm\n"
            f"ld={anclaje['ld_adoptada_mm']:.0f} mm"
        )
        _dibujar_barra_seccion(
            ax, x1, x2, y, gancho_x, cara == "inferior", color,
            texto, tx, 0.34 if cara == "inferior" else h - 0.34,
        )

    # Barras transversales vistas en corte.
    trans = {r["cara"]: r for r in resultado["refuerzo_transversal"]}
    for cara, y in (("superior", h - rec - 0.025), ("inferior", rec + 0.025)):
        for x in [0.55, B2 * 0.55, x_frente + tp2 / 2,
                  x_posterior + B1 * 0.45, B - 0.55]:
            ax.add_patch(Circle((x, y), 0.035, facecolor="white",
                                edgecolor=COLOR_TRANSVERSAL, linewidth=1.3,
                                zorder=12))
            ax.plot([x - 0.024, x + 0.024], [y - 0.024, y + 0.024],
                    color=COLOR_TRANSVERSAL, lw=0.8, zorder=13)
        tid = "T1" if cara == "superior" else "T2"
        ax.text(
            B + 0.18, y,
            f"{tid} Ø{trans[cara]['barra']} @ "
            f"{trans[cara]['espaciamiento_adoptado_mm']:.0f}",
            fontsize=7, va="center", color=COLOR_TRANSVERSAL,
        )

    y_cota = -0.50
    _cota_horizontal(ax, 0, B2, y_cota, f"PUNTA B2 = {B2:.2f} m", 0)
    _cota_horizontal(ax, B2, x_posterior, y_cota, f"tp2 = {tp2:.2f} m", 0)
    _cota_horizontal(ax, x_posterior, B, y_cota, f"TALÓN B1 = {B1:.2f} m", 0)
    _cota_horizontal(ax, 0, B, -0.93, f"B = {B:.2f} m", 0)
    _cota_vertical(ax, B + 1.22, 0, h, f"h = {h:.2f} m", B)
    _cota_vertical(ax, -0.52, rec, h - rec,
                   f"rec. = {p['recubrimiento_mm']:.0f} mm", 0)

    ax.text(B2 / 2, h + 0.14, "PUNTA", ha="center", va="bottom",
            fontsize=8, fontweight="bold")
    ax.text(x_posterior + B1 / 2, h + 0.14, "TALÓN", ha="center",
            va="bottom", fontsize=8, fontweight="bold")
    ax.text((x_frente + x_posterior) / 2, h + 1.1, "PANTALLA",
            rotation=90, ha="center", va="center", fontsize=8,
            fontweight="bold")
    ax.set_xlim(-0.85, B + 1.65)
    ax.set_ylim(-1.13, h + 2.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("SECCIÓN A–A  ·  ARMADURA LONGITUDINAL Y ANCLAJES",
                 fontsize=10, fontweight="bold", loc="left")


def _posiciones(longitud: float, rec: float, espaciamiento_mm: float,
                max_lineas: int = 90) -> list[float]:
    s = espaciamiento_mm / 1000.0
    cantidad = max(2, int(math.floor((longitud - 2 * rec) / s)) + 1)
    if cantidad > max_lineas:
        salto = math.ceil(cantidad / max_lineas)
    else:
        salto = 1
    return [rec + i * s for i in range(0, cantidad, salto)]


def _dibujar_planta(ax, resultado: dict, cara: str) -> None:
    g = resultado["geometria_m"]
    p = resultado["parametros"]
    acero = _mapa_armaduras(resultado)
    anc = _mapa_anclajes(resultado)
    B, B2, tp2 = g["B"], g["B2_punta"], g["tp2"]
    L = p["longitud_estribo_m"]
    rec = p["recubrimiento_mm"] / 1000.0
    x_posterior = B2 + tp2
    color = COLOR_SUPERIOR if cara == "superior" else COLOR_INFERIOR

    ax.add_patch(Rectangle((0, 0), B, L, facecolor="#f9fafb",
                           edgecolor=COLOR_BORDE, linewidth=1.0))
    ax.add_patch(Rectangle((B2, 0), tp2, L, facecolor="#d1d5db",
                           edgecolor=COLOR_BORDE, linewidth=0.8))

    for zona in ("punta", "talon"):
        item = acero[(zona, cara)]
        ld = anc[("longitudinal", zona, cara)]["ld_adoptada_mm"] / 1000.0
        if zona == "punta":
            x1, x2 = rec, min(B2 + ld, B - rec)
        else:
            x1, x2 = max(x_posterior - ld, rec), B - rec
        for y in _posiciones(L, rec, item["espaciamiento_adoptado_mm"], 55):
            ax.plot([x1, x2], [y, y], color=color, lw=0.65, alpha=0.82)
        ax.text(
            (x1 + x2) / 2, L + 0.18,
            f"{'L1' if (zona, cara)==('punta','superior') else 'L2' if zona=='punta' else 'L3' if cara=='superior' else 'L4'}\n"
            f"Ø{item['barra']} @ {item['espaciamiento_adoptado_mm']:.0f}",
            ha="center", va="bottom", fontsize=6.5, color=color,
        )

    trans = next(r for r in resultado["refuerzo_transversal"] if r["cara"] == cara)
    for x in _posiciones(B, rec, trans["espaciamiento_adoptado_mm"], 90):
        ax.plot([x, x], [rec, L - rec], color=COLOR_TRANSVERSAL,
                lw=0.45, alpha=0.42)
    ax.text(B - 0.08, -0.18,
            f"{'T1' if cara == 'superior' else 'T2'} Ø{trans['barra']} @ "
            f"{trans['espaciamiento_adoptado_mm']:.0f}",
            ha="right", va="top", fontsize=6.5, color=COLOR_TRANSVERSAL)

    _cota_horizontal(ax, 0, B, -0.55, f"B = {B:.2f} m", 0)
    _cota_vertical(ax, B + 0.55, 0, L, f"L = {L:.2f} m", B)
    ax.set_xlim(-0.42, B + 0.85)
    ax.set_ylim(-0.72, L + 0.72)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"PLANTA · ACERO {cara.upper()}", fontsize=9, fontweight="bold", loc="left"
    )


def _filas_cuadro(resultado: dict) -> list[list[str]]:
    acero = _mapa_armaduras(resultado)
    anc = _mapa_anclajes(resultado)
    filas: list[list[str]] = []
    ids = {
        ("punta", "superior"): "L1",
        ("punta", "inferior"): "L2",
        ("talon", "superior"): "L3",
        ("talon", "inferior"): "L4",
    }
    for clave, ident in ids.items():
        r = acero[clave]
        a = anc[("longitudinal", clave[0], clave[1])]
        filas.append([
            ident, f"{clave[0]} {r['signo']}", clave[1], f"Ø{r['barra']}",
            f"{r['espaciamiento_adoptado_mm']:.0f}",
            f"{r['As_diseno_cm2_m']:.2f}", f"{r['As_provisto_cm2_m']:.2f}",
            f"{a['ld_adoptada_mm']:.0f}", f"{a['ldg_adoptada_mm']:.0f}",
        ])
    for i, r in enumerate(resultado["refuerzo_transversal"], start=1):
        a = anc[("transversal", "ancho_total_del_estribo", r["cara"])]
        filas.append([
            f"T{i}", "transversal", r["cara"], f"Ø{r['barra']}",
            f"{r['espaciamiento_adoptado_mm']:.0f}",
            f"{r['As_requerido_cm2_m']:.2f}", f"{r['As_provisto_cm2_m']:.2f}",
            f"{a['ld_adoptada_mm']:.0f}", f"{a['ldg_adoptada_mm']:.0f}",
        ])
    return filas


def _dibujar_cuadro(ax, resultado: dict) -> None:
    ax.axis("off")
    ax.set_title("CUADRO DE ARMADURAS", fontsize=10, fontweight="bold", loc="left")
    columnas = ["ID", "Zona", "Cara", "Barra", "s\nmm", "As req.\ncm²/m",
                "As prov.\ncm²/m", "ld\nmm", "ldg\nmm"]
    tabla = ax.table(cellText=_filas_cuadro(resultado), colLabels=columnas,
                     loc="upper left", cellLoc="center", colLoc="center",
                     bbox=[0.0, 0.46, 1.0, 0.48],
                     colWidths=[0.06, 0.16, 0.11, 0.09, 0.08, 0.12, 0.12, 0.08, 0.08])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(6.2)
    for (fila, _), celda in tabla.get_celld().items():
        celda.set_edgecolor("#6b7280")
        celda.set_linewidth(0.45)
        if fila == 0:
            celda.set_facecolor("#dbeafe")
            celda.set_text_props(weight="bold")

    p = resultado["parametros"]
    g = resultado["geometria_m"]
    notas = [
        "NOTAS GENERALES",
        "1. Dimensiones en metros; refuerzo, separaciones y anclajes en milímetros.",
        f"2. f'c={resultado['materiales']['fc_kg_cm2']:.0f} kgf/cm²; "
        f"fy={resultado['materiales']['fy_kg_cm2']:.0f} kgf/cm²; "
        f"recubrimiento={p['recubrimiento_mm']:.0f} mm.",
        "3. Barras corrugadas sin epóxico. La barra de 7/8\" está excluida.",
        "4. Los ganchos indicados son estándar de 90°; verificar interferencias en obra.",
        "5. Las barras longitudinales deben superar la cara crítica en la ld indicada.",
        "6. Plano de diseño preliminar: coordinar con geometría 3D, juntas y contrafuertes.",
        f"7. Zapata: B={g['B']:.2f} m, h={g['h']:.2f} m; longitud={p['longitud_estribo_m']:.2f} m.",
    ]
    ax.text(0.01, 0.41, "\n".join(notas), transform=ax.transAxes,
            ha="left", va="top", fontsize=6.6, color=COLOR_TEXTO,
            linespacing=1.45)

    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 0.16, transform=ax.transAxes,
                           facecolor="white", edgecolor=COLOR_BORDE, lw=0.8))
    ax.text(0.02, 0.13, "PUENTE MOLINOHUAYCCO", transform=ax.transAxes,
            fontsize=8.5, fontweight="bold", va="top")
    ax.text(0.02, 0.075, "PLANO DE ARMADURAS — ZAPATA DE ESTRIBO",
            transform=ax.transAxes, fontsize=7.3, va="top")
    ax.text(0.68, 0.13, "NORMA: NTE E.060", transform=ax.transAxes,
            fontsize=6.8, va="top")
    ax.text(0.62, 0.075, "ESCALA: ESQUEMÁTICA", transform=ax.transAxes,
            fontsize=6.8, va="top")
    ax.text(0.93, 0.075, "LÁMINA\nZE-01", transform=ax.transAxes,
            fontsize=7.5, fontweight="bold", ha="center", va="top")


def crear_figura(resultado: dict):
    fig, ax_sec = plt.subplots(figsize=(15.5, 5.8), facecolor="white")
    _dibujar_seccion(ax_sec, resultado)
    fig.subplots_adjust(left=0.035, right=0.975, top=0.91, bottom=0.08)
    return fig


def generar_plano(salida: Path, dpi: int = 300) -> list[Path]:
    if dpi <= 0:
        raise ValueError("El DPI debe ser positivo")
    resultado = disenar()
    fig = crear_figura(resultado)
    salida = salida.resolve()
    salida.parent.mkdir(parents=True, exist_ok=True)
    base = salida.with_suffix("")
    png = base.with_suffix(".png")
    svg = base.with_suffix(".svg")
    fig.savefig(png, dpi=dpi, facecolor="white")
    fig.savefig(svg, facecolor="white")
    plt.close(fig)
    return [png, svg]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--salida", "-s", type=Path,
        default=Path("outputs/plano_zapata_e060.png"),
        help="Ruta base; se generan archivos PNG y SVG",
    )
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archivos = generar_plano(args.salida, args.dpi)
    for archivo in archivos:
        print(f"Plano guardado: {archivo}")


if __name__ == "__main__":
    main()

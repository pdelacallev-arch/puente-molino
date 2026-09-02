#!/usr/bin/env python3
"""Dibuja las presiones sobre el dentellón enlazadas al agente de subestructura.

El script consume ``disenar_dentellon_e060.disenar()``; por tanto, geometría,
casos, fuerzas horizontales y resistencia al deslizamiento proceden de
``agente_subestructura.py``. No mantiene un juego paralelo de solicitaciones.

Se muestran la presión pasiva nominal y la presión estructural del caso elegido.
La escala horizontal del diagrama es gráfica; las cotas y valores son numéricos.
Salida predeterminada: PNG y SVG en ``outputs/``.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.disenar_dentellon_e060 import (  # noqa: E402
    ENTRADAS,
    ParametrosDentellon,
    disenar,
)


CASOS_CLI = {
    "servicio-i": "case_service_I",
    "resistencia-ia": "case_resistance_Ia",
    "resistencia-ib": "case_resistance_Ib",
    "evento-extremo-i": "case_extreme_event_I",
}

COLOR_CONCRETO = "#e5e7eb"
COLOR_BORDE = "#111827"
COLOR_NOMINAL = "#2563eb"
COLOR_FACTORIZADO = "#dc2626"
COLOR_RESULTANTE = "#991b1b"
COLOR_COTA = "#4b5563"
COLOR_SUELO = "#fef3c7"
COLOR_TEXTO = "#111827"


def _buscar_caso(resultado: dict, caso_clave: str) -> dict:
    casos = {
        x["caso_clave"]: x for x in resultado["resultados_por_caso"]
    }
    if caso_clave not in casos:
        raise ValueError(f"El diseño no contiene el caso {caso_clave}")
    return casos[caso_clave]


def validar_diagrama(resultado: dict, caso_clave: str,
                     tolerancia: float = 2e-3) -> dict:
    """Audita la ley global dibujada y el tramo que diseña el dentellón."""
    caso = _buscar_caso(resultado, caso_clave)
    h = resultado["geometria"]["profundidad_vertical_m"]
    hz = resultado["geometria"]["espesor_zapata_para_anclaje_m"]
    pasivo = resultado["pasivo_nominal"]
    ep_nom = pasivo["Ep_total_tf_m"]
    if ep_nom <= 0:
        raise ValueError("El empuje pasivo nominal debe ser positivo")
    escala_u = caso["Vu_dentellon_tf_m"] / ep_nom
    p_tri_base_nom = pasivo["incremento_presion_dentellon_tf_m2"]
    ep_uni_nom = pasivo["componente_uniforme_tf_m"]
    p_uni_nom = ep_uni_nom / h
    p_tri_base_u = escala_u * p_tri_base_nom
    p_uni_u = escala_u * p_uni_nom

    # Ley completa desde la coronación de la zapata hasta el fondo del
    # dentellón. El tramo inferior, entre y=0 y y=-h, es el trapecio que se
    # integra para obtener Vu y Mu del diseño estructural.
    profundidad_base = pasivo["profundidad_base_pasivo_adoptada_m"]
    altura_total = hz + h
    profundidad_coronacion_zapata = profundidad_base - altura_total
    kp = pasivo["Kp_Rankine"]
    gamma = resultado["materiales"]["gamma_medio_tf_m3"]
    sobrecarga = resultado["parametros"]["sobrecarga_tf_m2"]
    p_global_top_nom = kp * (
        gamma * profundidad_coronacion_zapata + sobrecarga)
    p_global_junta_nom = kp * (
        gamma * (profundidad_coronacion_zapata + hz) + sobrecarga)
    p_global_base_nom = kp * (gamma * profundidad_base + sobrecarga)
    p_global_top_u = escala_u * p_global_top_nom
    p_global_junta_u = escala_u * p_global_junta_nom
    p_global_base_u = escala_u * p_global_base_nom
    fuerza_global_nom = (
        0.5 * (p_global_top_nom + p_global_base_nom) * altura_total)

    fuerza_integrada = 0.5 * p_tri_base_u * h + p_uni_u * h
    momento_integrado = (
        0.5 * p_tri_base_u * h * (2.0 * h / 3.0)
        + p_uni_u * h * (h / 2.0)
    )
    checks = {
        "fuerza": math.isclose(
            fuerza_integrada, caso["Vu_dentellon_tf_m"],
            rel_tol=tolerancia, abs_tol=tolerancia,
        ),
        "momento": math.isclose(
            momento_integrado, caso["Mu_dentellon_tf_m_m"],
            rel_tol=tolerancia, abs_tol=tolerancia,
        ),
        "agente": caso["Fh_agente_tf_m"] >= caso["Vu_dentellon_tf_m"] - tolerancia,
        "continuidad_junta": math.isclose(
            p_global_junta_nom, p_uni_nom,
            rel_tol=tolerancia, abs_tol=tolerancia,
        ),
        "continuidad_base": math.isclose(
            p_global_base_nom, p_uni_nom + p_tri_base_nom,
            rel_tol=tolerancia, abs_tol=tolerancia,
        ),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "escala_estructural": escala_u,
        "incremento_presion_nominal_tf_m2": p_tri_base_nom,
        "p_uniforme_nominal_tf_m2": p_uni_nom,
        "p_tri_base_u_tf_m2": p_tri_base_u,
        "p_uniforme_u_tf_m2": p_uni_u,
        "altura_total_pasiva_m": altura_total,
        "profundidad_coronacion_zapata_m": profundidad_coronacion_zapata,
        "p_global_top_nominal_tf_m2": p_global_top_nom,
        "p_global_junta_nominal_tf_m2": p_global_junta_nom,
        "p_global_base_nominal_tf_m2": p_global_base_nom,
        "p_global_top_u_tf_m2": p_global_top_u,
        "p_global_junta_u_tf_m2": p_global_junta_u,
        "p_global_base_u_tf_m2": p_global_base_u,
        "fuerza_global_nominal_tf_m": fuerza_global_nom,
        "fuerza_integrada_tf_m": fuerza_integrada,
        "momento_integrado_tf_m_m": momento_integrado,
    }


def _cota_horizontal(ax, x1: float, x2: float, y: float, texto: str,
                     extension_y: float) -> None:
    ax.annotate("", xy=(x1, y), xytext=(x2, y),
                arrowprops=dict(arrowstyle="<->", color=COLOR_COTA, lw=0.9))
    ax.plot([x1, x1], [extension_y, y], color=COLOR_COTA, lw=0.55)
    ax.plot([x2, x2], [extension_y, y], color=COLOR_COTA, lw=0.55)
    ax.text((x1 + x2) / 2, y + 0.06, texto, ha="center", va="bottom",
            fontsize=8, color=COLOR_TEXTO,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.7))


def _cota_vertical(ax, x: float, y1: float, y2: float, texto: str,
                   extension_x: float) -> None:
    ax.annotate("", xy=(x, y1), xytext=(x, y2),
                arrowprops=dict(arrowstyle="<->", color=COLOR_COTA, lw=0.9))
    ax.plot([extension_x, x], [y1, y1], color=COLOR_COTA, lw=0.55)
    ax.plot([extension_x, x], [y2, y2], color=COLOR_COTA, lw=0.55)
    ax.text(x + 0.06, (y1 + y2) / 2, texto, rotation=90,
            ha="left", va="center", fontsize=8, color=COLOR_TEXTO,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.7))


def _dibujar_seccion(ax, resultado: dict, caso: dict, auditoria: dict) -> None:
    g = resultado["geometria"]
    p = resultado["parametros"]
    t = g["espesor_horizontal_m"]
    h = g["profundidad_vertical_m"]
    hz = g["espesor_zapata_para_anclaje_m"]
    rec = p["recubrimiento_mm"] / 1000.0

    # Zapata esquemática y dentellón en su extremo de talón.
    ax.add_patch(Rectangle((-0.75 * t, 0), 1.75 * t, hz,
                           facecolor=COLOR_CONCRETO, edgecolor=COLOR_BORDE,
                           lw=1.2, zorder=4))
    ax.add_patch(Rectangle((0, -h), t, h,
                           facecolor=COLOR_CONCRETO, edgecolor=COLOR_BORDE,
                           lw=1.3, zorder=5))
    ax.add_patch(Rectangle((t, -h), 2.05 * t, hz + h,
                           facecolor=COLOR_SUELO, edgecolor="none",
                           alpha=0.60, zorder=0))
    ax.text(0.50 * t, 0.50 * hz, "ZAPATA", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#374151")
    ax.text(0.50 * t, -0.50 * h, "DENTELLÓN", ha="center", va="center",
            fontsize=9, fontweight="bold", rotation=90, color="#374151")
    ax.text(2.05 * t, 0.84 * hz, "MEDIO GRANULAR PASIVO",
            ha="center", va="top", fontsize=8, color="#92400e")
    ax.plot([t, 3.05 * t], [-h, -h], color="#a16207", lw=0.8, zorder=1)

    # Barras principales esquemáticas que cruzan la junta.
    # Para la presión dibujada de derecha a izquierda, la cara derecha del
    # voladizo es la cara traccionada.
    x_barra = t - rec
    ax.plot([x_barra, x_barra], [-h + rec, hz - rec],
            color="#b91c1c", lw=2.2, zorder=8)
    ax.plot([x_barra, x_barra - 0.20 * t], [-h + rec, -h + rec],
            color="#b91c1c", lw=2.2, zorder=8)
    ax.annotate(
        f"Acero principal\nØ{resultado['flexion']['barra']} @ "
        f"{resultado['flexion']['espaciamiento_adoptado_mm']:.0f} mm",
        xy=(x_barra, -0.18 * h), xytext=(-0.30 * t, 0.42 * hz),
        fontsize=7.5, ha="left", color="#991b1b",
        arrowprops=dict(arrowstyle="->", color="#991b1b", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                  edgecolor="#fecaca"),
        zorder=15,
    )

    # Ley pasiva completa sobre la altura hz + h. En la zapata es el tramo
    # superior y sobre el dentellón es un trapecio continuo.
    p_nom_top = auditoria["p_global_top_nominal_tf_m2"]
    p_nom_joint = auditoria["p_global_junta_nominal_tf_m2"]
    p_nom_bottom = auditoria["p_global_base_nominal_tf_m2"]
    p_u_top = auditoria["p_global_top_u_tf_m2"]
    p_u_joint = auditoria["p_global_junta_u_tf_m2"]
    p_u_bottom = auditoria["p_global_base_u_tf_m2"]
    p_max = max(p_nom_bottom, p_u_bottom, 1e-9)
    ancho_max = 1.18 * t

    def x_presion(valor: float) -> float:
        return t + ancho_max * valor / p_max

    nominal_pts = [(t, hz), (x_presion(p_nom_top), hz),
                   (x_presion(p_nom_bottom), -h), (t, -h)]
    ax.add_patch(Polygon(nominal_pts, closed=True, facecolor="#bfdbfe",
                         edgecolor=COLOR_NOMINAL, lw=1.2, alpha=0.62, zorder=2))
    ax.plot([x_presion(p_u_top), x_presion(p_u_bottom)], [hz, -h],
            color=COLOR_FACTORIZADO, lw=2.0, ls="--", zorder=10,
            label="Presión estructural del caso")

    # Flechas de la presión estructural hacia toda la cara zapata-dentellón.
    altura_total = hz + h
    for i in range(1, 13):
        fraccion = i / 13.0
        y = hz - altura_total * fraccion
        pres = p_u_top + (p_u_bottom - p_u_top) * fraccion
        x0 = x_presion(pres)
        ax.annotate("", xy=(t + 0.015 * t, y), xytext=(x0, y),
                    arrowprops=dict(arrowstyle="-|>", color=COLOR_FACTORIZADO,
                                    lw=1.0, mutation_scale=10), zorder=9)

    # Resultante estructural: el caso ya contiene el brazo desde la raíz.
    y_r = -caso["brazo_desde_raiz_m"]
    x_r = t + ancho_max + 0.55 * t
    ax.annotate("", xy=(t + 0.03 * t, y_r), xytext=(x_r, y_r),
                arrowprops=dict(arrowstyle="-|>", color=COLOR_RESULTANTE,
                                lw=2.1, mutation_scale=15), zorder=12)
    ax.text(x_r, y_r + 0.08 * h,
            f"Vu = {caso['Vu_dentellon_tf_m']:.3f} tf/m\n"
            f"y = {caso['brazo_desde_raiz_m']:.3f} m\n"
            f"Mu = {caso['Mu_dentellon_tf_m_m']:.3f} tf·m/m",
            ha="right", va="bottom", fontsize=8, fontweight="bold",
            color=COLOR_RESULTANTE,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="#fca5a5"), zorder=15)

    ax.annotate(
        f"σp,nom = {p_nom_bottom:.3f} tf/m²",
        xy=(x_presion(p_nom_bottom), -h), xytext=(1.75 * t, -1.11 * h),
        ha="center", va="top", fontsize=7.5, color=COLOR_NOMINAL,
        arrowprops=dict(arrowstyle="->", color=COLOR_NOMINAL, lw=0.65),
        bbox=dict(facecolor="white", edgecolor="#bfdbfe", pad=1.0),
    )
    ax.annotate(
        f"σp,u = {p_u_bottom:.3f} tf/m²",
        xy=(x_presion(p_u_bottom), -h), xytext=(2.50 * t, -0.91 * h),
        ha="center", va="bottom", fontsize=7.5, color=COLOR_FACTORIZADO,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=COLOR_FACTORIZADO, lw=0.65),
        bbox=dict(facecolor="white", edgecolor="#fecaca", pad=1.0),
    )

    ax.text(x_presion(max(p_nom_joint, p_u_joint)) + 0.05 * t,
            0.08 * hz,
            f"σp en fondo de zapata\n"
            f"nom. = {p_nom_joint:.3f} tf/m²\n"
            f"u = {p_u_joint:.3f} tf/m²",
            ha="left", va="bottom", fontsize=7.2, color=COLOR_TEXTO,
            bbox=dict(facecolor="white", edgecolor="#d1d5db", pad=1.2),
            zorder=14)
    ax.text(1.68 * t, 0.52 * hz, "PRESIÓN SOBRE\nLA ZAPATA",
            ha="center", va="center", fontsize=7.5, color=COLOR_NOMINAL,
            fontweight="bold")
    ax.text(1.48 * t, -0.25 * h, "PRESIÓN SOBRE\nEL DENTELLÓN\n(TRAPECIO)",
            ha="center", va="center", fontsize=7.5, color=COLOR_NOMINAL,
            fontweight="bold",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.82,
                      pad=1.0))

    _cota_horizontal(ax, 0, t, -h - 0.26 * h,
                     f"espesor = {t:.2f} m", -h)
    _cota_vertical(ax, -0.18 * t, -h, 0,
                   f"profundidad = {h:.2f} m", 0)
    _cota_vertical(ax, -0.88 * t, -h, hz,
                   f"H pasiva = {hz + h:.2f} m", 0)

    ax.axhline(0, color="#6b7280", lw=0.55, ls=":", zorder=1)
    ax.text(-0.05 * t, 0.03 * h, "RAÍZ / EMPOTRAMIENTO",
            ha="left", va="bottom", fontsize=7.5, color="#374151")
    ax.set_xlim(-1.05 * t, 3.35 * t)
    ax.set_ylim(-h - 0.42 * h, hz + 0.23 * h)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.set_title("SECCIÓN Y DIAGRAMA DE PRESIONES", loc="left",
                 fontsize=11, fontweight="bold", pad=12)


def _dibujar_resumen(ax, resultado: dict, caso: dict, auditoria: dict) -> None:
    ax.axis("off")
    ax.set_title("TRAZABILIDAD Y EQUILIBRIO", loc="left",
                 fontsize=11, fontweight="bold", pad=12)
    p_nom_top = auditoria["p_uniforme_nominal_tf_m2"]
    p_nom_base = p_nom_top + auditoria["incremento_presion_nominal_tf_m2"]
    p_u_top = auditoria["p_uniforme_u_tf_m2"]
    p_u_base = p_u_top + auditoria["p_tri_base_u_tf_m2"]
    datos = [
        ["Caso", caso["caso"]],
        ["Fuente", resultado["fuente_solicitaciones"]],
        ["Fh del agente", f"{caso['Fh_agente_tf_m']:.3f} tf/m"],
        ["QR sin dentellón", f"{caso['QR_sin_dentellon_tf_m']:.3f} tf/m"],
        ["Déficit de deslizamiento", f"{caso['deficit_deslizamiento_tf_m']:.3f} tf/m"],
        ["Kp Rankine", f"{resultado['pasivo_nominal']['Kp_Rankine']:.4f}"],
        ["Ep nominal", f"{resultado['pasivo_nominal']['Ep_total_tf_m']:.3f} tf/m"],
        ["σp coronación (nom. / u)", f"{p_nom_top:.3f} / {p_u_top:.3f} tf/m²"],
        ["σp base (nom. / u)", f"{p_nom_base:.3f} / {p_u_base:.3f} tf/m²"],
        ["Factor estructural efectivo", f"{auditoria['escala_estructural']:.3f}"],
        ["Vu integrado", f"{auditoria['fuerza_integrada_tf_m']:.3f} tf/m"],
        ["Mu integrado", f"{auditoria['momento_integrado_tf_m_m']:.3f} tf·m/m"],
    ]
    tabla = ax.table(cellText=datos, cellLoc="left", colLoc="left",
                     bbox=[0.0, 0.44, 1.0, 0.50], colWidths=[0.52, 0.48])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(7.0)
    for (fila, col), celda in tabla.get_celld().items():
        celda.set_edgecolor("#9ca3af")
        celda.set_linewidth(0.5)
        if col == 0:
            celda.set_facecolor("#f3f4f6")
            celda.set_text_props(weight="bold")

    checks = auditoria["checks"]
    notas = [
        "CONTROL DEL DIAGRAMA",
        f"✓ Área = Vu: {'CONFORME' if checks['fuerza'] else 'NO CONFORME'}",
        f"✓ Primer momento = Mu: {'CONFORME' if checks['momento'] else 'NO CONFORME'}",
        f"✓ Vu ≤ Fh del agente: {'CONFORME' if checks['agente'] else 'NO CONFORME'}",
        "",
        "CONVENCIONES",
        "Azul: presión pasiva nominal.",
        "Rojo discontinuo: presión estructural del caso.",
        "Ley: σp(z) = Kp(γz + q).",
        "El dentellón toma el tramo inferior de la distribución triangular",
        "del agente; localmente resulta un trapecio de presiones.",
        "La componente rectangular actúa a h/2 y la triangular a 2h/3.",
        "",
        "ALCANCE",
        "Esquema por metro lineal del estribo; escala gráfica no contractual.",
        "Válido para medio granular drenado; no representa una llave embebida",
        "en concreto ni acredita anclajes postinstalados.",
    ]
    ax.text(0.01, 0.39, "\n".join(notas), transform=ax.transAxes,
            ha="left", va="top", fontsize=6.8, color=COLOR_TEXTO,
            linespacing=1.20)
    ax.add_patch(Rectangle((0, 0), 1, 0.11, transform=ax.transAxes,
                           facecolor="white", edgecolor=COLOR_BORDE, lw=0.8))
    ax.text(0.02, 0.086, "PUENTE MOLINOHUAYCCO", transform=ax.transAxes,
            fontsize=8, fontweight="bold", va="top")
    ax.text(0.02, 0.040, "PRESIONES SOBRE DENTELLÓN",
            transform=ax.transAxes, fontsize=7, va="top")
    ax.text(0.70, 0.086, "NTE E.060 / CARGAS DEL AGENTE",
            transform=ax.transAxes, fontsize=6.4, va="top")


def crear_figura(resultado: dict, caso_clave: str):
    caso = _buscar_caso(resultado, caso_clave)
    auditoria = validar_diagrama(resultado, caso_clave)
    if not auditoria["ok"]:
        raise RuntimeError(f"El diagrama no supera la auditoría: {auditoria}")
    fig, ax_sec = plt.subplots(figsize=(10.5, 7.2), facecolor="white")
    _dibujar_seccion(ax_sec, resultado, caso, auditoria)
    fig.suptitle(
        f"PRESIONES SOBRE EL DENTELLÓN — {caso['caso'].upper()}",
        fontsize=13, fontweight="bold", y=0.975,
    )
    fig.subplots_adjust(left=0.055, right=0.965, top=0.90, bottom=0.08)
    return fig


def generar_dibujo(salida: Path, caso_clave: str = "case_resistance_Ia",
                   parametros: ParametrosDentellon | None = None,
                   dpi: int = 300) -> list[Path]:
    if dpi <= 0:
        raise ValueError("El DPI debe ser positivo")
    resultado = disenar(parametros)
    fig = crear_figura(resultado, caso_clave)
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
    # El dibujo representa el mismo dentellón que el cálculo; no mantiene
    # valores geométricos ni materiales paralelos.
    base = ENTRADAS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caso", choices=tuple(CASOS_CLI),
                        default="resistencia-ia")
    parser.add_argument("--interfaz", choices=("interface_1", "interface_2"),
                        default=base.interfaz)
    parser.add_argument("--espesor-m", type=float, default=base.espesor_m)
    parser.add_argument("--profundidad-m", type=float,
                        default=base.profundidad_m)
    parser.add_argument("--longitud-m", type=float, default=base.longitud_m)
    parser.add_argument("--gamma-medio", type=float, default=None)
    parser.add_argument("--phi-medio", type=float, default=None)
    parser.add_argument("--sobrecarga", type=float,
                        default=base.sobrecarga_tf_m2)
    parser.add_argument("--salida", "-s", type=Path,
                        default=Path("outputs/presiones_dentellon.png"))
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    a = parse_args()
    p = replace(
        ENTRADAS,
        interfaz=a.interfaz,
        espesor_m=a.espesor_m,
        profundidad_m=a.profundidad_m,
        longitud_m=a.longitud_m,
        gamma_medio_tf_m3=(
            ENTRADAS.gamma_medio_tf_m3
            if a.gamma_medio is None else a.gamma_medio),
        phi_medio_grados=(
            ENTRADAS.phi_medio_grados
            if a.phi_medio is None else a.phi_medio),
        sobrecarga_tf_m2=a.sobrecarga,
    )
    archivos = generar_dibujo(
        a.salida, caso_clave=CASOS_CLI[a.caso], parametros=p, dpi=a.dpi)
    for archivo in archivos:
        print(f"Dibujo guardado: {archivo}")


if __name__ == "__main__":
    main()

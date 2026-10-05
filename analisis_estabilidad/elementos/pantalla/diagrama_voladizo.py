#!/usr/bin/env python3
"""Generación de diagramas y figuras didácticas para la pantalla de estribo en voladizo.

Genera:
1. Diagrama de cuerpo libre con geometría, cargas actuantes (LS, EH, EQterr, PIR, PEQi, BR),
   brazos de palanca y reacciones de empotramiento en la base.
2. Diagramas de distribución de fuerza cortante V(y) y momento flector M(y) a lo largo
   de la altura de la pantalla, comparando Resistencia I, Evento Extremo I y Servicio I,
   junto con el esquema de armado adoptado en la sección crítica.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
import numpy as np


CONCRETE_FILL = "#e2e8f0"
CONCRETE_EDGE = "#1e293b"
SOIL_FILL = "#fef3c7"
SOIL_EDGE = "#b45309"
FOOTING_FILL = "#cbd5e1"
FOOTING_EDGE = "#475569"

C_EH = "#b91c1c"
C_LS = "#d97706"
C_EQ = "#be185d"
C_PIR = "#7c3aed"
C_PEQ = "#2563eb"
C_BR = "#059669"
C_REAC = "#0f172a"


def generar_diagrama_cargas(
    resultado: dict[str, Any],
    ruta_salida: str | Path,
    dpi: int = 220,
) -> Path:
    """Dibuja el diagrama de cuerpo libre con geometría de pantalla y cargas actuantes."""
    p = resultado["parametros"]
    geom = resultado["geometria_y_peso"]
    cargas = resultado["cargas"]
    comb = resultado["combinaciones"]

    hp = p["altura_total_hp_m"]
    hef = p["altura_efectiva_m"]
    t_sup1 = p["espesor_sup1_m"]
    t_sup2 = p["espesor_sup2_m"]
    t_inf = p["espesor_inf_m"]

    fig, ax = plt.subplots(figsize=(10.5, 9.5))

    # Coordenadas de la pantalla (cara libre vertical en x=0, cara terreno hacia x > 0)
    # y=0: base (empotramiento) [0,0] a [t_inf, 0]
    # y=hef: garganta [0, hef] a [t_sup2, hef]
    # y=hp: corona [0, hp] a [t_sup1, hp]
    pts_pantalla = np.array([
        [0.0, 0.0],
        [t_inf, 0.0],
        [t_sup2, hef],
        [t_sup1, hp],
        [0.0, hp],
    ])
    patch_pantalla = Polygon(pts_pantalla, closed=True, facecolor=CONCRETE_FILL, edgecolor=CONCRETE_EDGE, lw=2.2, zorder=3)
    ax.add_patch(patch_pantalla)

    # Zapata esquemática en la base
    hz = 1.50
    bz_izq = 1.50
    bz_der = 2.50
    patch_zapata = Rectangle((-bz_izq, -hz), bz_izq + bz_der, hz, facecolor=FOOTING_FILL, edgecolor=FOOTING_EDGE, lw=1.5, hatch="//", zorder=2)
    ax.add_patch(patch_zapata)
    ax.text(-0.5 * bz_izq, -0.5 * hz, "ZAPATA DE CIMENTACIÓN", ha="center", va="center", fontsize=9, fontweight="bold", color="#334155")

    # Relleno de suelo detrás de la pantalla
    pts_suelo = np.array([
        [t_inf, 0.0],
        [bz_der, 0.0],
        [bz_der, hp],
        [t_sup1, hp],
        [t_sup2, hef],
    ])
    patch_suelo = Polygon(pts_suelo, closed=True, facecolor=SOIL_FILL, edgecolor=SOIL_EDGE, lw=1.0, ls="--", alpha=0.6, zorder=1)
    ax.add_patch(patch_suelo)
    ax.text(t_inf + 0.8, hp * 0.45, "RELLENO\nGRANULAR", ha="center", va="center", fontsize=10, fontweight="bold", color="#92400e")

    # Línea de nivel freático o rasante
    ax.plot([t_sup1, bz_der + 1.0], [hp, hp], color="#78350f", lw=2, zorder=2)
    ax.text(bz_der + 0.5, hp + 0.15, "Nivel Rasante", fontsize=9, color="#78350f", fontweight="bold")

    # Dibujar Cargas con flechas estilizadas
    # 1. EH (triangular, empuje activo hacia la izquierda)
    c_eh = cargas["EH"]
    y_eh = c_eh["brazo_yp_m"]
    ax.annotate(
        "", xy=(0.0, y_eh), xytext=(2.6, y_eh),
        arrowprops=dict(arrowstyle="->", lw=2.5, color=C_EH, mutation_scale=18),
    )
    ax.text(2.7, y_eh, f"EH = {c_eh['fuerza_tf_m']:.2f} tf/m\n(Y = {y_eh:.2f} m)", color=C_EH, va="center", fontsize=9, fontweight="bold")

    # 2. LS (uniforme, sobrecarga)
    c_ls = cargas["LS"]
    y_ls = c_ls["brazo_yp_m"]
    ax.annotate(
        "", xy=(0.0, y_ls), xytext=(2.6, y_ls),
        arrowprops=dict(arrowstyle="->", lw=2.2, color=C_LS, mutation_scale=16),
    )
    ax.text(2.7, y_ls, f"LS = {c_ls['fuerza_tf_m']:.2f} tf/m\n(Y = {y_ls:.2f} m)", color=C_LS, va="center", fontsize=9, fontweight="bold")

    # 3. EQterr (sismo de suelo)
    c_eq = cargas["EQterr"]
    y_eq = c_eq["brazo_yp_m"]
    ax.annotate(
        "", xy=(0.0, y_eq), xytext=(2.6, y_eq),
        arrowprops=dict(arrowstyle="->", lw=2.0, color=C_EQ, mutation_scale=15),
    )
    ax.text(2.7, y_eq - 0.45, f"EQterr = {c_eq['fuerza_tf_m']:.2f} tf/m\n(Y = {y_eq:.2f} m)", color=C_EQ, va="center", fontsize=8.5, fontweight="bold")

    # 4. 0.5 PIR (inercia propia — misma dirección que empujes del terreno)
    c_pir = cargas["PIR_half"]
    y_pir = c_pir["brazo_yp_m"]
    ax.annotate(
        "", xy=(-0.3, y_pir), xytext=(2.3, y_pir),
        arrowprops=dict(arrowstyle="->", lw=2.0, color=C_PIR, mutation_scale=15),
    )
    ax.text(2.4, y_pir, f"0.5 PIR = {c_pir['fuerza_tf_m']:.2f} tf/m\n(Y = {y_pir:.2f} m)", color=C_PIR, va="center", fontsize=8.5, fontweight="bold")

    # 5. PEQi (inercia superestructura — actúa hacia la cara libre, izquierda)
    c_peq = cargas["PEQi"]
    y_peq = c_peq["brazo_yp_m"]
    ax.annotate(
        "", xy=(-2.2, y_peq), xytext=(-0.3, y_peq),
        arrowprops=dict(arrowstyle="->", lw=2.5, color=C_PEQ, mutation_scale=18),
    )
    ax.text(-2.3, y_peq, f"PEQi = {c_peq['fuerza_tf_m']:.2f} tf/m\n(Y = {y_peq:.2f} m)", color=C_PEQ, ha="right", va="center", fontsize=9, fontweight="bold")

    # 6. BR (frenado en cima — actúa hacia la cara libre, izquierda)
    c_br = cargas["BR"]
    y_br = c_br["brazo_yp_m"]
    ax.annotate(
        "", xy=(-2.2, hp), xytext=(-0.3, hp),
        arrowprops=dict(arrowstyle="->", lw=2.2, color=C_BR, mutation_scale=16),
    )
    ax.text(-2.3, hp, f"BR = {c_br['fuerza_tf_m']:.2f} tf/m\n(elev = {y_br:.2f} m)", color=C_BR, ha="right", va="center", fontsize=9, fontweight="bold")

    # Reacciones de empotramiento en la base (Punto P) — Cortante hacia la derecha para equilibrar
    ext = comb["Evento_Extremo_I"]
    res = comb["Resistencia_I"]
    ax.annotate(
        "", xy=(t_inf / 2.0 + 1.8, -0.4), xytext=(t_inf / 2.0, -0.4),
        arrowprops=dict(arrowstyle="->", lw=3.0, color=C_REAC, mutation_scale=20),
    )
    ax.text(t_inf / 2.0 + 1.9, -0.4, f"Vu (Ext I) = {ext['V_u_tf_m']:.2f} tf/m\nVu (Res I) = {res['V_u_tf_m']:.2f} tf/m", color=C_REAC, va="center", fontsize=9, fontweight="bold")

    # Flecha curva de momento flector en la base
    ax.text(
        -1.3, -0.4,
        f"Mu (Ext I) = {ext['M_u_tf_m_m']:.2f} tf-m/m\nMu (Res I) = {res['M_u_tf_m_m']:.2f} tf-m/m",
        color=C_REAC, ha="right", va="center", fontsize=9.5, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f1f5f9", edgecolor="#64748b")
    )

    # Cotas dimensionales
    ax.plot([-0.2, -0.2], [0.0, hp], color="#64748b", lw=1.2, ls=":")
    ax.text(-0.35, hp / 2.0, f"hp = {hp:.2f} m", rotation=90, ha="center", va="center", fontsize=10, fontweight="bold", color="#334155")
    ax.text(t_inf / 2.0, 0.15, f"t_inf = {t_inf:.2f} m", ha="center", fontsize=8.5, fontweight="bold", color="#1e293b")
    ax.text(t_sup1 / 2.0, hp + 0.15, f"t_sup1 = {t_sup1:.2f} m", ha="center", fontsize=8.5, fontweight="bold", color="#1e293b")

    ax.set_title("DIAGRAMA DE CUERPO LIBRE Y CARGAS ACTUANTES EN LA PANTALLA EN VOLADIZO", fontsize=12, fontweight="bold", pad=15)
    ax.set_xlim(-4.2, 5.0)
    ax.set_ylim(-2.0, hp + 1.2)
    ax.set_aspect("equal", "box")
    ax.axis("off")

    fig.tight_layout()
    salida = Path(ruta_salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return salida


def generar_diagramas_esfuerzos_y_armado(
    resultado: dict[str, Any],
    ruta_salida: str | Path,
    dpi: int = 220,
) -> Path:
    """Genera panel doble: diagramas V(y) y M(y) a lo largo de la altura y croquis de armado."""
    p = resultado["parametros"]
    cargas = resultado["cargas"]
    comb = resultado["combinaciones"]
    flex = resultado["diseno_flexion"]["adoptado"]
    temp = resultado["acero_temperatura"]["adoptado"]

    hp = p["altura_total_hp_m"]
    hef = p["altura_efectiva_m"]
    t_inf = p["espesor_inf_m"]
    t_sup1 = p["espesor_sup1_m"]
    t_sup2 = p["espesor_sup2_m"]

    # Cálculo analítico de V(y) y M(y) a lo largo de la altura y desde y=0 hasta y=hp
    n_pts = 100
    y_vals = np.linspace(0, hp, n_pts)

    k_act = resultado["coeficientes_empuje"]["Ka_calculo"]
    k_seis = resultado["coeficientes_empuje"]["Kae_calculo"]
    gamma_r = p["gamma_relleno_tf_m3"]
    gamma_c = p["gamma_concreto_tf_m3"]
    kh = p["kh"]
    h_eq = p["h_sobrecarga_m"]

    br = cargas["BR"]["fuerza_tf_m"]
    peqi = cargas["PEQi"]["fuerza_tf_m"]
    y_peq = cargas["PEQi"]["brazo_yp_m"]
    y_br = cargas["BR"]["brazo_yp_m"]

    # Curvas de momentos y cortantes para Resistencia I, Evento Extremo I y Servicio I
    M_res_y = np.zeros(n_pts)
    M_ext_y = np.zeros(n_pts)
    M_serv_y = np.zeros(n_pts)
    V_res_y = np.zeros(n_pts)
    V_ext_y = np.zeros(n_pts)

    for i, y in enumerate(y_vals):
        hy = hp - y  # Altura de voladizo por encima del corte y
        if hy <= 0:
            continue

        # Cargas sobre la porción superior [y, hp]
        # LS
        p_ls = k_act * gamma_r * h_eq
        v_ls = p_ls * hy
        m_ls = v_ls * (hy / 2.0)

        # EH (trapecio o triángulo en corte superior)
        # intensidad en y: p1 = k_act * gamma_r * (hp - hy) = k_act * gamma_r * y
        # intensidad en base del corte: p2 = k_act * gamma_r * hp
        p_tope = k_act * gamma_r * (hp - hy)
        p_base = k_act * gamma_r * hp
        v_eh = 0.5 * (p_tope + p_base) * hy
        # Brazo desde el corte y:
        m_eh = (p_tope * (hy**2) / 2.0) + ((p_base - p_tope) * (hy**2) / 3.0)

        # EQterr
        p_eq = 0.5 * max(k_seis - k_act, 0.0) * hp * gamma_r
        v_eq = p_eq * hy
        m_eq = v_eq * (hy / 2.0)

        # PIR porción superior
        # Simplificación: masa aproximada de la porción superior
        t_y = t_inf - (t_inf - t_sup2) * (y / hef) if y <= hef else t_sup1
        t_prom_y = 0.5 * (t_y + t_sup1)
        w_y = gamma_c * t_prom_y * hy
        v_pir = 0.5 * kh * w_y
        m_pir = v_pir * (hy / 2.0)

        # PEQi (solo actúa si el corte está por debajo de y_peq)
        v_peq = peqi if y <= y_peq else 0.0
        m_peq = peqi * (y_peq - y) if y <= y_peq else 0.0

        # BR (siempre está por encima)
        v_br = br
        m_br = br * (y_br - y)

        # Combinaciones en corte y
        M_res_y[i] = 1.75 * m_ls + 1.50 * m_eh + 1.75 * m_br
        V_res_y[i] = 1.75 * v_ls + 1.50 * v_eh + 1.75 * v_br

        M_ext_y[i] = 0.50 * m_ls + 1.00 * m_eh + 1.00 * (m_eq + m_pir + m_peq) + 0.50 * m_br
        V_ext_y[i] = 0.50 * v_ls + 1.00 * v_eh + 1.00 * (v_eq + v_pir + v_peq) + 0.50 * v_br

        M_serv_y[i] = 1.00 * m_ls + 1.00 * m_eh + 1.00 * m_br

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.0, 7.5), gridspec_kw={"width_ratios": [1.1, 1.1, 1.2]})

    # Panel 1: Diagramas de Momento Flector M(y)
    ax1.plot(M_ext_y, y_vals, label="Evento Extremo I (Sismo)", color=C_EQ, lw=2.4)
    ax1.plot(M_res_y, y_vals, label="Resistencia I", color=C_EH, lw=2.0, ls="--")
    ax1.plot(M_serv_y, y_vals, label="Servicio I (Fisuración)", color=C_LS, lw=1.8, ls=":")
    ax1.axhline(hef, color="#64748b", ls="-.", lw=1.0, label="Nivel Garganta (hef)")
    ax1.set_xlabel("Momento Flector $M$ (tf·m/m)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Elevación sobre zapata $y$ (m)", fontsize=10, fontweight="bold")
    ax1.set_title("Diagrama de Momento $M(y)$", fontsize=11, fontweight="bold")
    ax1.grid(True, ls=":", alpha=0.6)
    ax1.legend(fontsize=8.5, loc="upper right")
    ax1.set_ylim(0, hp)

    # Panel 2: Diagramas de Fuerza Cortante V(y)
    ax2.plot(V_ext_y, y_vals, label="Evento Extremo I", color=C_EQ, lw=2.4)
    ax2.plot(V_res_y, y_vals, label="Resistencia I", color=C_EH, lw=2.0, ls="--")
    ax2.axvline(resultado["cortante"]["Vr_tf_m"], color="#15803d", lw=2.0, ls="-", label=f"Vr = {resultado['cortante']['Vr_tf_m']:.2f} tf/m")
    ax2.axhline(hef, color="#64748b", ls="-.", lw=1.0)
    ax2.set_xlabel("Fuerza Cortante $V$ (tf/m)", fontsize=10, fontweight="bold")
    ax2.set_title("Diagrama de Cortante $V(y)$", fontsize=11, fontweight="bold")
    ax2.grid(True, ls=":", alpha=0.6)
    ax2.legend(fontsize=8.5, loc="upper right")
    ax2.set_ylim(0, hp)

    # Panel 3: Esquema de Sección y Disposición de Armadura en la base
    ax3.set_title("Disposición de Refuerzo en Sección Base", fontsize=11, fontweight="bold")
    b_vis = 1.00  # 1.0 m de ancho
    h_vis = t_inf  # espesor base

    patch_sec = Rectangle((0, 0), b_vis, h_vis, facecolor=CONCRETE_FILL, edgecolor=CONCRETE_EDGE, lw=2.0)
    ax3.add_patch(patch_sec)

    # Acero principal vertical en cara terreno (y cercano a h_vis)
    r_terr = p["recubrimiento_terreno_mm"] / 1000.0
    r_libre = p["recubrimiento_libre_mm"] / 1000.0

    s_vert_m = flex["s_adoptado_cm"] / 100.0
    n_barras = int(b_vis / s_vert_m) + 1
    x_barras = np.linspace(0.08, b_vis - 0.08, n_barras)

    y_acero_ppal = h_vis - r_terr - (flex["db_mm"] / 2000.0)
    for xb in x_barras:
        ax3.plot(xb, y_acero_ppal, marker="o", markersize=9, color="#b91c1c", zorder=5)

    # Acero de temperatura en cara libre (y cercano a 0)
    s_temp_m = temp["s_adoptado_cm"] / 100.0
    n_temp = int(b_vis / s_temp_m) + 1
    x_temp = np.linspace(0.08, b_vis - 0.08, n_temp)
    y_acero_temp = r_libre + (temp["db_mm"] / 2000.0)
    for xt in x_temp:
        ax3.plot(xt, y_acero_temp, marker="o", markersize=6, color="#2563eb", zorder=5)

    # Indicaciones de texto
    ax3.text(
        b_vis / 2.0, h_vis + 0.08,
        f"CARA DEL TERRENO (Tracción)\nAcero Principal: {flex['barra']} @ {flex['s_adoptado_cm']:.0f} cm\n(As prov = {flex['As_provisto_cm2_m']:.2f} cm²/m)",
        ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#b91c1c",
    )
    ax3.text(
        b_vis / 2.0, -0.08,
        f"CARA LIBRE (Compresión)\nAcero Temperatura: {temp['barra']} @ {temp['s_adoptado_cm']:.0f} cm\n(As temp = {temp['As_provisto_cm2_m']:.2f} cm²/m)",
        ha="center", va="top", fontsize=8.5, fontweight="bold", color="#2563eb",
    )

    ax3.set_xlim(-0.25, b_vis + 0.25)
    ax3.set_ylim(-0.35, h_vis + 0.35)
    ax3.set_aspect("equal")
    ax3.axis("off")

    fig.tight_layout()
    salida = Path(ruta_salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return salida

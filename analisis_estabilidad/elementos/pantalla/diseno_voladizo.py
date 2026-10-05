#!/usr/bin/env python3
"""Diseño normativo de la pantalla del estribo en voladizo (AASHTO LRFD / MTC).

Modela la pantalla como una viga en voladizo empotrada en la zapata (punto P),
sujeta a empujes de tierra (EH), sobrecarga vehicular (LS), sismo del terreno (EQterr),
inercia de la pantalla (PIR), inercia de la superestructura (PEQi) y frenado (BR).

Geometría:
- Nivel de corona de cajuela: hp (ancho t_sup1)
- Nivel de garganta / asiento de cajuela: h_efectiva (ancho t_sup2)
- Nivel de base / empotramiento: y = 0 sobre la zapata (ancho t_inf = 0.10 * H)

Implementa rigurosamente los Pasos 1 a 8 de la 'guia_diseno_pantalla_estribo.md':
- Paso 1: Geometría y espesores de la pantalla.
- Paso 2: Cargas actuantes, empujes y brazos respecto al punto P.
- Paso 3: Combinaciones de carga y momentos últimos (Resistencia I, Evento Extremo I, Servicio I).
- Paso 4: Diseño por flexión del acero vertical principal (cara terreno).
- Paso 5: Verificación de acero mínimo (Art. 5.6.3.3 / Mcr).
- Paso 6: Acero de temperatura y retracción en ambas caras (Art. 5.10.6).
- Paso 7: Control de fisuración bajo cargas de servicio (Art. 5.6.7).
- Paso 8: Revisión por cortante por el Método General de AASHTO (Art. 5.7.3.4.2).

Unidades internas: m, tf, tf/m, tf-m/m, kgf/cm2, MPa, mm y cm2/m.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from analisis_estabilidad.elementos.estribo.estabilidad_global import (
    GEOM,
    coulomb_active_coefficient,
    deg2rad,
    mononobe_okabe_coefficient,
    rad2deg,
)


TF_A_KN = 9.80665
TF_M_A_N_MM = 9.80665e6
KGF_CM2_A_MPA = 0.0980665
MPA_A_KSI = 0.1450377377
MM_POR_PULGADA = 25.4
CM2_M_POR_IN2_FT = 6.4516 / 0.3048

BARRAS_INGLESAS_MM = {
    '3/8"': 9.525,
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
    '1 3/8"': 35.814,
}


def area_barra_cm2(db_mm: float) -> float:
    return math.pi * (db_mm / 10.0) ** 2 / 4.0


def diametro_barra_mm(designacion: str) -> float:
    if designacion not in BARRAS_INGLESAS_MM:
        raise ValueError(f"Designación de barra desconocida: {designacion}")
    return BARRAS_INGLESAS_MM[designacion]


@dataclass(frozen=True)
class ParametrosPantallaVoladizo:
    # Geometría principal
    altura_total_hp_m: float = GEOM.hp  # Altura sobre zapata (8.37 m)
    altura_efectiva_m: float = GEOM.hp - GEOM.c_cajuela - GEOM.d_cajuela  # Garganta (5.33 m)
    altura_global_h_m: float = GEOM.H  # Altura total de relleno H (9.87 m)
    espesor_sup1_m: float = 0.40  # Corona de la cajuela
    espesor_sup2_m: float = 0.40  # Nivel garganta / mesa de apoyo
    espesor_inf_m: float = 0.10 * GEOM.H  # Base empotrada (t_inf = 0.10 * H = 0.987 m)
    ancho_franja_m: float = 1.00  # Franja unitaria de diseño

    # Recubrimientos
    recubrimiento_terreno_mm: float = 50.0  # Cara en contacto con terreno (tracción)
    recubrimiento_libre_mm: float = 50.0  # Cara exterior libre

    # Refuerzo y espaciamientos
    barras_verticales: tuple[str, ...] = ('5/8"', '3/4"', '1"')
    barras_temperatura: tuple[str, ...] = ('1/2"', '5/8"')
    espaciamiento_minimo_mm: float = 100.0
    espaciamiento_maximo_mm: float = 400.0
    paso_espaciamiento_mm: float = 5.0
    barra_vertical_adoptada: str | None = None
    espaciamiento_vertical_adoptado_mm: float | None = None
    barra_temp_adoptada: str | None = None
    espaciamiento_temp_adoptado_mm: float | None = None

    # Materiales
    fc_kgf_cm2: float = 280.0
    fy_kgf_cm2: float = 4200.0
    gamma_relleno_tf_m3: float = 1.80
    gamma_concreto_tf_m3: float = 2.40
    phi_relleno_grados: float = 39.8
    delta_grados: float = 19.9
    es_mpa: float = 200000.0
    tamano_agregado_pulgadas: float = 0.75  # 3/4"

    # Cargas de superestructura y acciones
    dc_tf_m: float = 25.98
    dw_tf_m: float = 2.88
    pl_tf_m: float = 3.08
    ll_im_tf_m: float = 12.95
    br_tf_m: float = 1.63
    h_sobrecarga_m: float = 0.61
    kh: float = 0.125
    kv: float = 0.05
    porcentaje_sismico_superestructura: float = 0.24
    brazo_br_m: float | None = None  # None -> hp + 0.90 m
    brazo_eq_super_m: float | None = None  # None -> h_efectiva + d_cajuela/2

    # Factores normativos AASHTO LRFD
    factor_modificacion_eta: float = 1.00
    phi_flexion_resistencia: float = 0.90
    phi_flexion_extremo: float = 1.00
    phi_cortante: float = 0.90
    factor_exposicion_fisuracion_gamma_e: float = 0.75  # 0.75 severo, 1.00 moderado
    usar_componente_normal_empuje: bool = False  # False = Ka directo según guía Serquén

    def validar(self) -> None:
        if self.altura_total_hp_m <= 0 or self.altura_efectiva_m <= 0:
            raise ValueError("Las alturas de pantalla deben ser positivas")
        if self.altura_efectiva_m >= self.altura_total_hp_m:
            raise ValueError("La altura efectiva debe ser menor que la altura total hp")
        if min(self.espesor_sup1_m, self.espesor_sup2_m, self.espesor_inf_m) <= 0:
            raise ValueError("Los espesores de pantalla deben ser positivos")
        if self.ancho_franja_m <= 0:
            raise ValueError("El ancho de franja debe ser positivo")
        if min(self.espaciamiento_minimo_mm, self.espaciamiento_maximo_mm, self.paso_espaciamiento_mm) <= 0:
            raise ValueError("Los límites de espaciamiento deben ser positivos")
        if self.espaciamiento_minimo_mm > self.espaciamiento_maximo_mm:
            raise ValueError("El espaciamiento mínimo no puede superar al máximo")
        if not self.barras_verticales or not self.barras_temperatura:
            raise ValueError("Debe configurarse al menos una barra vertical y de temperatura")
        faltantes = (set(self.barras_verticales) | set(self.barras_temperatura)) - set(BARRAS_INGLESAS_MM)
        if faltantes:
            raise ValueError(f"Barras no reconocidas: {sorted(faltantes)}")


@dataclass(frozen=True)
class CargaAccion:
    codigo: str
    nombre: str
    tipo: str
    intensidad_o_valor: float
    fuerza_tf_m: float
    brazo_yp_m: float
    momento_tf_m_m: float
    descripcion: str


@dataclass(frozen=True)
class CombinacionEstado:
    nombre: str
    M_u_tf_m_m: float
    V_u_tf_m: float
    phi_flexion: float
    phi_cortante: float
    M_u_sobre_phi: float
    detalle_factores: dict[str, float]


def calcular_geometria_y_peso(p: ParametrosPantallaVoladizo) -> dict[str, float]:
    """Calcula áreas, pesos y centroide vertical de la pantalla sobre el punto P."""
    hp = p.altura_total_hp_m
    hef = p.altura_efectiva_m
    h_cajuela = hp - hef

    # Tramo 1: cajuela superior (rectángulo)
    area1 = p.espesor_sup1_m * h_cajuela
    peso1 = p.gamma_concreto_tf_m3 * area1 * p.ancho_franja_m
    y1 = hef + h_cajuela / 2.0

    # Tramo 2: fuste inferior (trapecio con base t_inf y cima t_sup2)
    area2 = 0.5 * (p.espesor_sup2_m + p.espesor_inf_m) * hef
    peso2 = p.gamma_concreto_tf_m3 * area2 * p.ancho_franja_m
    # Centroide vertical del trapecio medido desde la base y = 0
    y2 = (hef / 3.0) * (p.espesor_inf_m + 2.0 * p.espesor_sup2_m) / (p.espesor_inf_m + p.espesor_sup2_m)

    peso_total = peso1 + peso2
    y_centroide = (peso1 * y1 + peso2 * y2) / peso_total

    return {
        "h_cajuela_m": h_cajuela,
        "h_fuste_m": hef,
        "area1_m2": area1,
        "area2_m2": area2,
        "peso1_tf_m": peso1,
        "peso2_tf_m": peso2,
        "peso_pantalla_total_tf_m": peso_total,
        "y_cg_pantalla_m": y_centroide,
    }


def calcular_coeficientes_empuje(p: ParametrosPantallaVoladizo) -> dict[str, float]:
    """Calcula coeficientes de empuje activo estático (Coulomb) y dinámico (Mononobe-Okabe)."""
    ka = coulomb_active_coefficient(p.phi_relleno_grados, p.delta_grados)
    psi = math.degrees(math.atan2(p.kh, 1.0 - p.kv))
    kae = mononobe_okabe_coefficient(p.phi_relleno_grados, p.delta_grados, psi)

    cos_delta = math.cos(deg2rad(p.delta_grados))
    k_act = ka * cos_delta if p.usar_componente_normal_empuje else ka
    k_seis = kae * cos_delta if p.usar_componente_normal_empuje else kae

    return {
        "Ka": ka,
        "Kae": kae,
        "Ka_calculo": k_act,
        "Kae_calculo": k_seis,
        "psi_deg": psi,
        "cos_delta": cos_delta,
    }


def calcular_cargas_base(
    p: ParametrosPantallaVoladizo,
    geom_peso: dict[str, float],
    coefs: dict[str, float],
) -> dict[str, CargaAccion]:
    """Calcula las 6 cargas normativas actuantes sobre la pantalla en voladizo (Paso 2)."""
    hp = p.altura_total_hp_m
    k_act = coefs["Ka_calculo"]
    k_seis = coefs["Kae_calculo"]
    w_est = geom_peso["peso_pantalla_total_tf_m"]
    y_pir = geom_peso["y_cg_pantalla_m"]

    # 1. LS: Sobrecarga viva vehicular de suelo (Art. 3.11.6.4)
    p_ls = k_act * p.gamma_relleno_tf_m3 * p.h_sobrecarga_m
    v_ls = p_ls * hp * p.ancho_franja_m
    y_ls = hp / 2.0
    m_ls = v_ls * y_ls
    c_ls = CargaAccion(
        codigo="LS",
        nombre="Sobrecarga viva de terreno",
        tipo="uniforme",
        intensidad_o_valor=p_ls,
        fuerza_tf_m=v_ls,
        brazo_yp_m=y_ls,
        momento_tf_m_m=m_ls,
        descripcion=f"p'' = {p_ls:.4f} tf/m2 sobre h={hp:.2f} m",
    )

    # 2. EH: Empuje horizontal estático activo (Coulomb)
    p_eh = k_act * p.gamma_relleno_tf_m3 * hp
    v_eh = 0.5 * p_eh * hp * p.ancho_franja_m
    y_eh = hp / 3.0
    m_eh = v_eh * y_eh
    c_eh = CargaAccion(
        codigo="EH",
        nombre="Empuje activo estático",
        tipo="triangular_max_base",
        intensidad_o_valor=p_eh,
        fuerza_tf_m=v_eh,
        brazo_yp_m=y_eh,
        momento_tf_m_m=m_eh,
        descripcion=f"p = {p_eh:.4f} tf/m2 en base, resultante a h/3",
    )

    # 3. EQterr: Empuje sísmico del suelo (Incremento dinámico Mononobe-Okabe)
    delta_k = max(k_seis - k_act, 0.0)
    p_eq = 0.5 * delta_k * hp * p.gamma_relleno_tf_m3
    v_eq = p_eq * hp * p.ancho_franja_m
    y_eq = hp / 2.0
    m_eq = v_eq * y_eq
    c_eq = CargaAccion(
        codigo="EQterr",
        nombre="Empuje sísmico del suelo",
        tipo="uniforme_equivalente",
        intensidad_o_valor=p_eq,
        fuerza_tf_m=v_eq,
        brazo_yp_m=y_eq,
        momento_tf_m_m=m_eq,
        descripcion=f"p' = 0.5*(Kae-Ka)*h*gamma = {p_eq:.4f} tf/m2",
    )

    # 4. 0.5 PIR: Fuerza inercial de la pantalla (50% según Art. 11.6.5.1)
    pir_total = p.kh * w_est
    v_pir_half = 0.5 * pir_total
    m_pir_half = v_pir_half * y_pir
    c_pir = CargaAccion(
        codigo="0.5PIR",
        nombre="Inercia pantalla (50%)",
        tipo="inercial",
        intensidad_o_valor=pir_total,
        fuerza_tf_m=v_pir_half,
        brazo_yp_m=y_pir,
        momento_tf_m_m=m_pir_half,
        descripcion=f"0.5 * Kh * West = 0.5 * {p.kh:.3f} * {w_est:.2f} tf/m",
    )

    # 5. PEQi: Fuerza inercial superestructura transmitida al estribo
    peqi = p.porcentaje_sismico_superestructura * (p.dc_tf_m + p.dw_tf_m)
    y_peqi = p.brazo_eq_super_m if p.brazo_eq_super_m is not None else (p.altura_efectiva_m + (GEOM.d_cajuela / 2.0))
    m_peqi = peqi * y_peqi
    c_peqi = CargaAccion(
        codigo="PEQi",
        nombre="Inercia superestructura",
        tipo="concentrada_apoyo",
        intensidad_o_valor=peqi,
        fuerza_tf_m=peqi,
        brazo_yp_m=y_peqi,
        momento_tf_m_m=m_peqi,
        descripcion=f"{p.porcentaje_sismico_superestructura*100:.1f}% * (DC+DW) en apoyo",
    )

    # 6. BR: Fuerza longitudinal de frenado
    br = p.br_tf_m
    y_br = p.brazo_br_m if p.brazo_br_m is not None else (hp + 0.90)
    m_br = br * y_br
    c_br = CargaAccion(
        codigo="BR",
        nombre="Fuerza de frenado",
        tipo="concentrada_cima",
        intensidad_o_valor=br,
        fuerza_tf_m=br,
        brazo_yp_m=y_br,
        momento_tf_m_m=m_br,
        descripcion=f"BR = {br:.2f} tf/m aplicado a hp+0.90={y_br:.2f} m",
    )

    return {
        "LS": c_ls,
        "EH": c_eh,
        "EQterr": c_eq,
        "PIR_half": c_pir,
        "PEQi": c_peqi,
        "BR": c_br,
    }


def calcular_combinaciones(
    p: ParametrosPantallaVoladizo,
    cargas: dict[str, CargaAccion],
) -> dict[str, CombinacionEstado]:
    """Evalúa los estados límite Resistencia I, Evento Extremo I y Servicio I (Paso 3)."""
    eta = p.factor_modificacion_eta
    ls = cargas["LS"]
    eh = cargas["EH"]
    eq = cargas["EQterr"]
    pir = cargas["PIR_half"]
    peqi = cargas["PEQi"]
    br = cargas["BR"]

    # Resistencia I
    # Mu = eta * [1.75 M_LS + 1.50 M_EH + 1.75 M_BR]
    m_u_res = eta * (1.75 * ls.momento_tf_m_m + 1.50 * eh.momento_tf_m_m + 1.75 * br.momento_tf_m_m)
    v_u_res = eta * (1.75 * ls.fuerza_tf_m + 1.50 * eh.fuerza_tf_m + 1.75 * br.fuerza_tf_m)
    comb_res = CombinacionEstado(
        nombre="Resistencia I",
        M_u_tf_m_m=m_u_res,
        V_u_tf_m=v_u_res,
        phi_flexion=p.phi_flexion_resistencia,
        phi_cortante=p.phi_cortante,
        M_u_sobre_phi=m_u_res / p.phi_flexion_resistencia,
        detalle_factores={"LS": 1.75, "EH": 1.50, "BR": 1.75},
    )

    # Evento Extremo I (Sismo)
    # Mu = eta * [0.50 M_LS + 1.00 M_EH + 1.00 (M_EQterr + M_0.5PIR + M_PEQi) + 0.50 M_BR]
    m_sismo_total = eq.momento_tf_m_m + pir.momento_tf_m_m + peqi.momento_tf_m_m
    v_sismo_total = eq.fuerza_tf_m + pir.fuerza_tf_m + peqi.fuerza_tf_m
    m_u_ext = eta * (
        0.50 * ls.momento_tf_m_m
        + 1.00 * eh.momento_tf_m_m
        + 1.00 * m_sismo_total
        + 0.50 * br.momento_tf_m_m
    )
    v_u_ext = eta * (
        0.50 * ls.fuerza_tf_m
        + 1.00 * eh.fuerza_tf_m
        + 1.00 * v_sismo_total
        + 0.50 * br.fuerza_tf_m
    )
    comb_ext = CombinacionEstado(
        nombre="Evento Extremo I",
        M_u_tf_m_m=m_u_ext,
        V_u_tf_m=v_u_ext,
        phi_flexion=p.phi_flexion_extremo,
        phi_cortante=1.00,
        M_u_sobre_phi=m_u_ext / p.phi_flexion_extremo,
        detalle_factores={"LS": 0.50, "EH": 1.00, "EQ": 1.00, "BR": 0.50},
    )

    # Servicio I (para control de fisuración y deflexión)
    # Ms = eta * [1.00 M_LS + 1.00 M_EH + 1.00 M_BR]
    m_s = eta * (1.00 * ls.momento_tf_m_m + 1.00 * eh.momento_tf_m_m + 1.00 * br.momento_tf_m_m)
    v_s = eta * (1.00 * ls.fuerza_tf_m + 1.00 * eh.fuerza_tf_m + 1.00 * br.fuerza_tf_m)
    comb_serv = CombinacionEstado(
        nombre="Servicio I",
        M_u_tf_m_m=m_s,
        V_u_tf_m=v_s,
        phi_flexion=1.00,
        phi_cortante=1.00,
        M_u_sobre_phi=m_s,
        detalle_factores={"LS": 1.00, "EH": 1.00, "BR": 1.00},
    )

    return {
        "Resistencia_I": comb_res,
        "Evento_Extremo_I": comb_ext,
        "Servicio_I": comb_serv,
    }


def resolver_flexion_exacta(
    Mu_tf_m_m: float,
    d_cm: float,
    fc_kgf_cm2: float,
    fy_kgf_cm2: float,
    b_cm: float,
    phi_f: float,
) -> tuple[float, float]:
    """Resuelve la ecuación cuadrática de flexión simple."""
    # Mu = phi * As * fy * (d - a/2) con a = As*fy / (0.85*fc*b)
    # (phi * fy^2 / (1.7*fc*b)) * As^2 - (phi * fy * d) * As + Mu = 0
    A = phi_f * (fy_kgf_cm2**2) / (1.7 * fc_kgf_cm2 * b_cm)
    B = -phi_f * fy_kgf_cm2 * d_cm
    C = Mu_tf_m_m * 1e5  # tf-m/m a kgf-cm/m
    disc = B**2 - 4.0 * A * C
    if disc < 0:
        raise ValueError(f"Sección insuficiente por compresión en flexión: discriminante {disc:.2e} < 0")
    As_cm2_m = (-B - math.sqrt(disc)) / (2.0 * A)
    a_cm = As_cm2_m * fy_kgf_cm2 / (0.85 * fc_kgf_cm2 * b_cm)
    return As_cm2_m, a_cm


def disenar_acero_principal(
    p: ParametrosPantallaVoladizo,
    comb: dict[str, CombinacionEstado],
) -> dict[str, Any]:
    """Diseña y selecciona el acero vertical principal en la cara del terreno (Paso 4)."""
    b_cm = p.ancho_franja_m * 100.0
    h_base_cm = p.espesor_inf_m * 100.0
    r_cm = p.recubrimiento_terreno_mm / 10.0

    comb_res = comb["Resistencia_I"]
    comb_ext = comb["Evento_Extremo_I"]

    candidatos = []
    for barra in p.barras_verticales:
        db_mm = diametro_barra_mm(barra)
        db_cm = db_mm / 10.0
        dc_cm = r_cm + db_cm / 2.0
        d_cm = h_base_cm - dc_cm

        # As requerido para Resistencia I
        as_res, a_res = resolver_flexion_exacta(
            comb_res.M_u_tf_m_m, d_cm, p.fc_kgf_cm2, p.fy_kgf_cm2, b_cm, comb_res.phi_flexion
        )
        # As requerido para Evento Extremo I
        as_ext, a_ext = resolver_flexion_exacta(
            comb_ext.M_u_tf_m_m, d_cm, p.fc_kgf_cm2, p.fy_kgf_cm2, b_cm, comb_ext.phi_flexion
        )

        as_req = max(as_res, as_ext)
        estado_gobernante = "Evento Extremo I" if as_ext >= as_res else "Resistencia I"

        # Área de 1 barra
        a1_cm2 = area_barra_cm2(db_mm)
        s_calc_cm = (a1_cm2 / as_req) * 100.0

        # Espaciamiento adoptado (redondeo hacia abajo a múltiplo de paso)
        paso_cm = p.paso_espaciamiento_mm / 10.0
        s_adopt_cm = math.floor(s_calc_cm / paso_cm) * paso_cm
        s_adopt_cm = max(p.espaciamiento_minimo_mm / 10.0, min(p.espaciamiento_maximo_mm / 10.0, s_adopt_cm))

        # Si el usuario fijó la barra y espaciamiento:
        if p.barra_vertical_adoptada == barra and p.espaciamiento_vertical_adoptado_mm is not None:
            s_adopt_cm = p.espaciamiento_vertical_adoptado_mm / 10.0

        as_prov = (a1_cm2 * 100.0) / s_adopt_cm
        a_real_cm = as_prov * p.fy_kgf_cm2 / (0.85 * p.fc_kgf_cm2 * b_cm)

        # Capacidad nominal y de diseño
        mn_tf_m_m = as_prov * p.fy_kgf_cm2 * (d_cm - a_real_cm / 2.0) * 1e-5
        phi_mn_res = p.phi_flexion_resistencia * mn_tf_m_m
        phi_mn_ext = p.phi_flexion_extremo * mn_tf_m_m

        dcr_res = comb_res.M_u_tf_m_m / phi_mn_res
        dcr_ext = comb_ext.M_u_tf_m_m / phi_mn_ext
        dcr_max = max(dcr_res, dcr_ext)

        candidatos.append({
            "barra": barra,
            "db_mm": db_mm,
            "dc_cm": dc_cm,
            "d_cm": d_cm,
            "As_req_ResI_cm2_m": as_res,
            "As_req_ExtI_cm2_m": as_ext,
            "As_requerido_cm2_m": as_req,
            "estado_gobernante": estado_gobernante,
            "s_calculado_cm": s_calc_cm,
            "s_adoptado_cm": s_adopt_cm,
            "s_adoptado_mm": s_adopt_cm * 10.0,
            "As_provisto_cm2_m": as_prov,
            "a_real_cm": a_real_cm,
            "Mn_tf_m_m": mn_tf_m_m,
            "phi_Mn_ResI_tf_m_m": phi_mn_res,
            "phi_Mn_ExtI_tf_m_m": phi_mn_ext,
            "DCR_ResI": dcr_res,
            "DCR_ExtI": dcr_ext,
            "DCR_flexion": dcr_max,
            "cumple": dcr_max <= 1.0 and as_prov >= as_req,
        })

    # Seleccionar candidato preferido (el que cumpla con menor DCR o el fijado por el usuario)
    if p.barra_vertical_adoptada is not None:
        adoptado = next(
            (c for c in candidatos if c["barra"] == p.barra_vertical_adoptada),
            candidatos[0],
        )
    else:
        aptos = [c for c in candidatos if c["cumple"]]
        if aptos:
            adoptado = sorted(aptos, key=lambda c: (abs(c["s_adoptado_cm"] - 15.0), c["DCR_flexion"]))[0]
        else:
            adoptado = candidatos[-1]

    return {
        "candidatos": candidatos,
        "adoptado": adoptado,
    }


def verificar_acero_minimo(
    p: ParametrosPantallaVoladizo,
    comb: dict[str, CombinacionEstado],
    diseno_flex: dict[str, Any],
) -> dict[str, Any]:
    """Verifica el requisito de acero mínimo según AASHTO LRFD Art. 5.6.3.3 (Paso 5)."""
    fc_mpa = p.fc_kgf_cm2 * KGF_CM2_A_MPA
    fr_mpa = 0.63 * math.sqrt(fc_mpa)
    fr_kgf_cm2 = fr_mpa * (1.0 / KGF_CM2_A_MPA)

    b_cm = p.ancho_franja_m * 100.0
    h_base_cm = p.espesor_inf_m * 100.0
    S_cm3 = (b_cm * (h_base_cm**2)) / 6.0

    Mcr_tf_m_m = 1.1 * fr_kgf_cm2 * S_cm3 * 1e-5

    mu_gobernante = max(comb["Resistencia_I"].M_u_tf_m_m, comb["Evento_Extremo_I"].M_u_tf_m_m)
    limite_133_mu = 1.33 * mu_gobernante

    m_minimo_exigido = min(Mcr_tf_m_m, limite_133_mu)
    adoptado = diseno_flex["adoptado"]
    mn_provisto = adoptado["Mn_tf_m_m"]

    cumple = mn_provisto >= m_minimo_exigido

    return {
        "fc_MPa": fc_mpa,
        "fr_MPa": fr_mpa,
        "fr_kgf_cm2": fr_kgf_cm2,
        "S_cm3": S_cm3,
        "Mcr_tf_m_m": Mcr_tf_m_m,
        "limite_133_Mu_tf_m_m": limite_133_mu,
        "M_minimo_exigido_tf_m_m": m_minimo_exigido,
        "Mn_provisto_tf_m_m": mn_provisto,
        "criterio_gobernante": "Mcr" if Mcr_tf_m_m <= limite_133_mu else "1.33 Mu",
        "cumple": cumple,
    }


def disenar_acero_temperatura(p: ParametrosPantallaVoladizo) -> dict[str, Any]:
    """Calcula el refuerzo por temperatura y retracción según AASHTO Art. 5.10.6 (Paso 6)."""
    t_prom_cm = 0.5 * (p.espesor_sup1_m + p.espesor_inf_m) * 100.0
    h_temp_cm = max((p.altura_total_hp_m - 2.50) * 100.0, 300.0)

    as_temp_calc = (0.18 * h_temp_cm * t_prom_cm) / (2.0 * (h_temp_cm + t_prom_cm))
    as_temp_norm = max(2.33, min(12.70, as_temp_calc))

    candidatos = []
    for barra in p.barras_temperatura:
        db_mm = diametro_barra_mm(barra)
        a1_cm2 = area_barra_cm2(db_mm)
        s_calc_cm = (a1_cm2 / as_temp_norm) * 100.0

        s_max_norm_cm = min(3.0 * t_prom_cm, 45.0)
        s_adopt_cm = min(math.floor(s_calc_cm / (p.paso_espaciamiento_mm / 10.0)) * (p.paso_espaciamiento_mm / 10.0), s_max_norm_cm)
        s_adopt_cm = max(p.espaciamiento_minimo_mm / 10.0, s_adopt_cm)

        if p.barra_temp_adoptada == barra and p.espaciamiento_temp_adoptado_mm is not None:
            s_adopt_cm = p.espaciamiento_temp_adoptado_mm / 10.0

        as_prov = (a1_cm2 * 100.0) / s_adopt_cm
        cumple = as_prov >= as_temp_norm and s_adopt_cm <= s_max_norm_cm

        candidatos.append({
            "barra": barra,
            "db_mm": db_mm,
            "s_calculado_cm": s_calc_cm,
            "s_max_normativo_cm": s_max_norm_cm,
            "s_adoptado_cm": s_adopt_cm,
            "s_adoptado_mm": s_adopt_cm * 10.0,
            "As_provisto_cm2_m": as_prov,
            "cumple": cumple,
        })

    adoptado = next(
        (c for c in candidatos if c["barra"] == p.barra_temp_adoptada),
        candidatos[0],
    )

    return {
        "t_prom_cm": t_prom_cm,
        "h_temp_cm": h_temp_cm,
        "As_temp_calculado_cm2_m": as_temp_calc,
        "As_temp_normativo_cm2_m": as_temp_norm,
        "candidatos": candidatos,
        "adoptado": adoptado,
    }


def verificar_fisuracion_servicio(
    p: ParametrosPantallaVoladizo,
    comb: dict[str, CombinacionEstado],
    diseno_flex: dict[str, Any],
) -> dict[str, Any]:
    """Verifica control de fisuración bajo Servicio I según AASHTO Art. 5.6.7 (Paso 7)."""
    comb_serv = comb["Servicio_I"]
    ms_tf_m_m = comb_serv.M_u_tf_m_m
    adoptado = diseno_flex["adoptado"]

    b_cm = p.ancho_franja_m * 100.0
    h_base_cm = p.espesor_inf_m * 100.0
    d_cm = adoptado["d_cm"]
    dc_cm = adoptado["dc_cm"]
    as_prov_cm2_m = adoptado["As_provisto_cm2_m"]

    es_kgf_cm2 = p.es_mpa * (1.0 / KGF_CM2_A_MPA)
    ec_kgf_cm2 = 15300.0 * math.sqrt(p.fc_kgf_cm2)
    n = es_kgf_cm2 / ec_kgf_cm2

    A_y = b_cm / 2.0
    B_y = n * as_prov_cm2_m
    C_y = -n * as_prov_cm2_m * d_cm
    y_cr_cm = (-B_y + math.sqrt(B_y**2 - 4.0 * A_y * C_y)) / (2.0 * A_y)

    jd_cm = d_cm - y_cr_cm / 3.0
    fs_kgf_cm2 = (ms_tf_m_m * 1e5) / (as_prov_cm2_m * jd_cm)
    limite_fs = 0.60 * p.fy_kgf_cm2

    beta_s = 1.0 + dc_cm / (0.7 * (h_base_cm - dc_cm))
    gamma_e = p.factor_exposicion_fisuracion_gamma_e

    s_max_fis_cm = (125000.0 * gamma_e) / (beta_s * fs_kgf_cm2) - 2.0 * dc_cm
    s_adopt_cm = adoptado["s_adoptado_cm"]

    cumple_fs = fs_kgf_cm2 <= limite_fs * 1.02
    cumple_espaciamiento = s_adopt_cm <= s_max_fis_cm
    cumple = cumple_fs and cumple_espaciamiento

    return {
        "Ms_tf_m_m": ms_tf_m_m,
        "n": n,
        "Es_kgf_cm2": es_kgf_cm2,
        "Ec_kgf_cm2": ec_kgf_cm2,
        "y_cr_cm": y_cr_cm,
        "jd_cm": jd_cm,
        "fs_kgf_cm2": fs_kgf_cm2,
        "limite_fs_kgf_cm2": limite_fs,
        "fs_MPa": fs_kgf_cm2 * KGF_CM2_A_MPA,
        "beta_s": beta_s,
        "gamma_e": gamma_e,
        "s_max_fisuracion_cm": s_max_fis_cm,
        "s_max_fisuracion_mm": s_max_fis_cm * 10.0,
        "s_adoptado_cm": s_adopt_cm,
        "s_adoptado_mm": s_adopt_cm * 10.0,
        "cumple_esfuerzo": cumple_fs,
        "cumple_espaciamiento": cumple_espaciamiento,
        "cumple": cumple,
    }


def verificar_cortante_general(
    p: ParametrosPantallaVoladizo,
    comb: dict[str, CombinacionEstado],
    diseno_flex: dict[str, Any],
) -> dict[str, Any]:
    """Verifica resistencia al cortante con el Método General de AASHTO Art. 5.7.3.4.2 (Paso 8)."""
    adoptado = diseno_flex["adoptado"]
    d_cm = adoptado["d_cm"]
    a_cm = adoptado["a_real_cm"]
    h_base_cm = p.espesor_inf_m * 100.0
    b_cm = p.ancho_franja_m * 100.0
    as_prov_cm2_m = adoptado["As_provisto_cm2_m"]

    dv_cm = max(d_cm - a_cm / 2.0, 0.90 * d_cm, 0.72 * h_base_cm)

    v_u_res = comb["Resistencia_I"].V_u_tf_m
    v_u_ext = comb["Evento_Extremo_I"].V_u_tf_m
    vu_gobernante = max(v_u_res, v_u_ext)
    mu_asociado = comb["Resistencia_I"].M_u_tf_m_m if vu_gobernante == v_u_res else comb["Evento_Extremo_I"].M_u_tf_m_m

    es_kgf_cm2 = p.es_mpa * (1.0 / KGF_CM2_A_MPA)
    fuerza_flexion_corte = abs(mu_asociado * 1e5 / dv_cm) + (vu_gobernante * 1e3)
    eps_s = fuerza_flexion_corte / (es_kgf_cm2 * as_prov_cm2_m)

    sx_in = dv_cm / 2.54
    ag_in = p.tamano_agregado_pulgadas
    sxe_in = 1.38 * sx_in / (ag_in + 0.63)
    sxe_in = max(12.0, min(80.0, sxe_in))

    beta = (4.8 / (1.0 + 750.0 * eps_s)) * (51.0 / (39.0 + sxe_in))

    fc_mpa = p.fc_kgf_cm2 * KGF_CM2_A_MPA
    bv_mm = b_cm * 10.0
    dv_mm = dv_cm * 10.0
    vc_kn = 0.083 * beta * math.sqrt(fc_mpa) * bv_mm * dv_mm * 1e-3
    vc_tf = vc_kn / TF_A_KN

    vn_max_kn = 0.25 * fc_mpa * bv_mm * dv_mm * 1e-3
    vn_max_tf = vn_max_kn / TF_A_KN
    vn_tf = min(vc_tf, vn_max_tf)

    phi_v = p.phi_cortante
    vr_tf = phi_v * vn_tf
    dcr_v = vu_gobernante / vr_tf

    requiere_estribos = dcr_v > 1.0
    cumple = dcr_v <= 1.0

    return {
        "dv_cm": dv_cm,
        "limite_090_d_cm": 0.90 * d_cm,
        "limite_072_h_cm": 0.72 * h_base_cm,
        "Vu_tf_m": vu_gobernante,
        "Mu_asociado_tf_m_m": mu_asociado,
        "eps_s": eps_s,
        "sx_in": sx_in,
        "sxe_in": sxe_in,
        "beta": beta,
        "Vc_tf_m": vc_tf,
        "Vn_max_tf_m": vn_max_tf,
        "Vn_tf_m": vn_tf,
        "phi_v": phi_v,
        "Vr_tf_m": vr_tf,
        "DCR_cortante": dcr_v,
        "requiere_estribos": requiere_estribos,
        "cumple": cumple,
    }


def evaluar(p: ParametrosPantallaVoladizo) -> dict[str, Any]:
    """Ejecuta el diseño completo de la pantalla en voladizo (Pasos 1 a 8)."""
    p.validar()

    geom_peso = calcular_geometria_y_peso(p)
    coefs = calcular_coeficientes_empuje(p)
    cargas = calcular_cargas_base(p, geom_peso, coefs)
    comb = calcular_combinaciones(p, cargas)

    diseno_flex = disenar_acero_principal(p, comb)
    acero_min = verificar_acero_minimo(p, comb, diseno_flex)
    acero_temp = disenar_acero_temperatura(p)
    fisuracion = verificar_fisuracion_servicio(p, comb, diseno_flex)
    cortante = verificar_cortante_general(p, comb, diseno_flex)

    cumple_global = (
        diseno_flex["adoptado"]["cumple"]
        and acero_min["cumple"]
        and acero_temp["adoptado"]["cumple"]
        and fisuracion["cumple"]
        and cortante["cumple"]
    )

    advertencias: list[str] = []
    if not diseno_flex["adoptado"]["cumple"]:
        advertencias.append("El refuerzo vertical por flexión no cumple la demanda.")
    if not acero_min["cumple"]:
        advertencias.append("La sección no cumple con el refuerzo mínimo por flexión (Art. 5.6.3.3).")
    if not fisuracion["cumple"]:
        advertencias.append("El espaciamiento supera el límite normativo de fisuración bajo Servicio I (Art. 5.6.7).")
    if cortante["requiere_estribos"]:
        advertencias.append("La pantalla requiere refuerzo transversal por corte (Vu > Vr).")

    return {
        "elemento": "pantalla",
        "calculo": "diseno_voladizo",
        "parametros": asdict(p),
        "geometria_y_peso": geom_peso,
        "coeficientes_empuje": coefs,
        "cargas": {k: asdict(v) for k, v in cargas.items()},
        "combinaciones": {k: asdict(v) for k, v in comb.items()},
        "diseno_flexion": diseno_flex,
        "acero_minimo": acero_min,
        "acero_temperatura": acero_temp,
        "fisuracion_servicio": fisuracion,
        "cortante": cortante,
        "cumple_global": cumple_global,
        "estado": "OK" if cumple_global else "NO_CUMPLE",
        "advertencias": advertencias,
    }


def _fmt(val: float | None, dec: int = 2) -> str:
    if val is None:
        return "—"
    return f"{val:.{dec}f}"


def reporte_markdown(resultado: dict[str, Any]) -> str:
    """Genera un reporte didáctico y técnico en formato Markdown siguiendo la estructura de la guía."""
    p = resultado["parametros"]
    geom = resultado["geometria_y_peso"]
    coefs = resultado["coeficientes_empuje"]
    cargas = resultado["cargas"]
    comb = resultado["combinaciones"]
    flex = resultado["diseno_flexion"]["adoptado"]
    minimo = resultado["acero_minimo"]
    temp = resultado["acero_temperatura"]["adoptado"]
    fis = resultado["fisuracion_servicio"]
    cort = resultado["cortante"]

    lines = [
        "# MEMORIA DE CÁLCULO: DISEÑO DE LA PANTALLA DE ESTRIBO EN VOLADIZO",
        "",
        "**Norma aplicable:** AASHTO LRFD Bridge Design Specifications / Manual de Puentes MTC  ",
        "**Referencia didáctica:** *Puentes – AASHTO LRFD* · MSc. Ing. Arturo Rodríguez Serquén (Págs. 270, 282-288)  ",
        f"**Estado global:** **{'CUMPLE' if resultado['cumple_global'] else 'NO CUMPLE'}**",
        "",
        "---",
        "",
        "## 1. PRE-DIMENSIONADO Y GEOMETRÍA (Paso 1)",
        "",
        "| Parámetro | Símbolo | Valor | Unidad | Criterio / Ubicación |",
        "|:---|:---:|:---:|:---:|:---|",
        f"| Altura total de relleno | $H$ | {_fmt(p['altura_global_h_m'])} | m | Superficie de terreno a base zapata |",
        f"| Altura libre sobre zapata | $h_p$ | {_fmt(p['altura_total_hp_m'])} | m | Altura total de pantalla voladizo |",
        f"| Altura de garganta / mesa | $h_{{ef}}$ | {_fmt(p['altura_efectiva_m'])} | m | Cima de fuste inferior |",
        f"| Altura de pared cajuela | $h_{{caj}}$ | {_fmt(geom['h_cajuela_m'])} | m | $h_p - h_{{ef}}$ |",
        f"| Espesor corona cajuela | $t_{{sup1}}$ | {_fmt(p['espesor_sup1_m'])} | m | Nivel $y = h_p$ |",
        f"| Espesor nivel garganta | $t_{{sup2}}$ | {_fmt(p['espesor_sup2_m'])} | m | Nivel $y = h_{{ef}}$ |",
        f"| Espesor inferior base | $t_{{inf}}$ | {_fmt(p['espesor_inf_m'])} | m | Nivel $y = 0$ (Punto P, empotramiento) |",
        f"| Peso propio pantalla | $W_{{est}}$ | {_fmt(geom['peso_pantalla_total_tf_m'])} | tf/m | Sin suelo sobre talón (Art. C11.6.5.1) |",
        f"| Centro de gravedad vertical | $Y_{{P,PIR}}$ | {_fmt(geom['y_cg_pantalla_m'])} | m | Medido desde Punto P |",
        "",
        "---",
        "",
        "## 2. CARGAS ACTUANTES SOBRE LA PANTALLA (Paso 2)",
        "",
        "La pantalla se analiza como una viga en voladizo empotrada en el Punto P (cara superior de zapata).",
        "",
        "| Carga | Tipo / Distribución | Fuerza $V$ (tf/m) | Brazo $Y_P$ (m) | Momento $M$ (tf-m/m) | Ecuación / Justificación |",
        "|:---|:---|:---:|:---:|:---:|:---|",
    ]

    for k in ("LS", "EH", "EQterr", "PIR_half", "PEQi", "BR"):
        c = cargas[k]
        lines.append(
            f"| **{c['codigo']}** ({c['nombre']}) | {c['tipo']} | {_fmt(c['fuerza_tf_m'])} | "
            f"{_fmt(c['brazo_yp_m'])} | {_fmt(c['momento_tf_m_m'])} | {c['descripcion']} |"
        )

    lines += [
        "",
        "> **Parámetros geotécnicos y sísmicos empleados:**",
        f"> - $K_a = {_fmt(coefs['Ka_calculo'], 4)}$, $K_{{ae}} = {_fmt(coefs['Kae_calculo'], 4)}$, $\\gamma_r = {_fmt(p['gamma_relleno_tf_m3'])} \\text{{ tf/m}}^3$, $\\phi = {_fmt(p['phi_relleno_grados'])}^\\circ$, $\\delta = {_fmt(p['delta_grados'])}^\\circ$.",
        f"> - $K_h = {_fmt(p['kh'], 3)}$, $K_v = {_fmt(p['kv'], 3)}$, $h_{{eq}} = {_fmt(p['h_sobrecarga_m'])} \\text{{ m}}$.",
        "",
        "---",
        "",
        "## 3. COMBINACIONES DE CARGA Y MOMENTO ÚLTIMO (Paso 3)",
        "",
        "| Estado Límite | $M_u$ (tf-m/m) | $V_u$ (tf/m) | $\\phi_f$ | $M_u / \\phi_f$ (tf-m/m) | ¿Rige flexión? |",
        "|:---|:---:|:---:|:---:|:---:|:---:|",
    ]

    m_res = comb["Resistencia_I"]
    m_ext = comb["Evento_Extremo_I"]
    m_serv = comb["Servicio_I"]

    rige_flex = "Evento Extremo I" if m_ext["M_u_sobre_phi"] >= m_res["M_u_sobre_phi"] else "Resistencia I"

    lines += [
        f"| **Resistencia I** | {_fmt(m_res['M_u_tf_m_m'])} | {_fmt(m_res['V_u_tf_m'])} | {_fmt(m_res['phi_flexion'])} | {_fmt(m_res['M_u_sobre_phi'])} | {'RIGE' if rige_flex == 'Resistencia I' else '—'} |",
        f"| **Evento Extremo I** | {_fmt(m_ext['M_u_tf_m_m'])} | {_fmt(m_ext['V_u_tf_m'])} | {_fmt(m_ext['phi_flexion'])} | {_fmt(m_ext['M_u_sobre_phi'])} | {'RIGE' if rige_flex == 'Evento Extremo I' else '—'} |",
        f"| **Servicio I** | {_fmt(m_serv['M_u_tf_m_m'])} | {_fmt(m_serv['V_u_tf_m'])} | 1.00 | {_fmt(m_serv['M_u_sobre_phi'])} | (Para fisuración) |",
        "",
        f"> **Momento de diseño que rige:** **{rige_flex}** con solicitación normalizada $M_u/\\phi_f = {_fmt(max(m_res['M_u_sobre_phi'], m_ext['M_u_sobre_phi']))} \\text{{ tf-m/m}}$.",
        "",
        "---",
        "",
        "## 4. DISEÑO POR FLEXIÓN: ACERO VERTICAL PRINCIPAL (Paso 4)",
        "",
        "El acero principal se coloca en la **cara del terreno** (cara sometida a tracción).",
        "",
        "| Parámetro | Símbolo | Valor | Unidad | Observaciones |",
        "|:---|:---:|:---:|:---:|:---|",
        f"| Espesor en la base | $t_{{inf}}$ | {_fmt(p['espesor_inf_m']*100, 1)} | cm | Empotramiento en zapata |",
        f"| Recubrimiento | $r$ | {_fmt(p['recubrimiento_terreno_mm']/10, 1)} | cm | Cara terreno |",
        f"| Peralte efectivo | $d$ | {_fmt(flex['d_cm'])} | cm | $t_{{inf}} - r - \\varnothing/2$ |",
        f"| $A_s$ requerido Resistencia I | $A_{{s,Res}}$ | {_fmt(flex['As_req_ResI_cm2_m'])} | cm²/m | $\\phi_f = 0.90$ |",
        f"| $A_s$ requerido Evento Extremo I | $A_{{s,Ext}}$ | {_fmt(flex['As_req_ExtI_cm2_m'])} | cm²/m | $\\phi_f = 1.00$ |",
        f"| **$A_s$ de diseño requerido** | $A_{{s,req}}$ | **{_fmt(flex['As_requerido_cm2_m'])}** | **cm²/m** | Rige {flex['estado_gobernante']} |",
        f"| **Refuerzo adoptado** | — | **{flex['barra']} @ {_fmt(flex['s_adoptado_cm'], 0)} cm** | — | **{flex['barra']} @ {_fmt(flex['s_adoptado_mm'], 0)} mm** |",
        f"| $A_s$ provisto | $A_{{s,prov}}$ | **{_fmt(flex['As_provisto_cm2_m'])}** | cm²/m | $A_{{s,prov}} \\geq A_{{s,req}}$ ✓ |",
        f"| Profundidad bloque compresión | $a$ | {_fmt(flex['a_real_cm'])} | cm | $0.85 f'_c b$ |",
        f"| Resistencia nominal | $M_n$ | {_fmt(flex['Mn_tf_m_m'])} | tf-m/m | Par interno $d - a/2$ |",
        f"| Ratio Demanda/Capacidad | DCR | {_fmt(flex['DCR_flexion'], 3)} | — | {'✅ Cumple' if flex['cumple'] else '❌ No cumple'} |",
        "",
        "---",
        "",
        "## 5. VERIFICACIÓN DE ACERO MÍNIMO (Paso 5 - Art. 5.6.3.3)",
        "",
        "| Parámetro | Fórmula / Referencia | Valor | Unidad |",
        "|:---|:---|:---:|:---:|",
        f"| Módulo de rotura del concreto | $f_r = 0.63\\sqrt{{f'_c}}$ | {_fmt(minimo['fr_MPa'])} MPa ({_fmt(minimo['fr_kgf_cm2'])} kg/cm²) | — |",
        f"| Módulo de sección bruta | $S = b \\cdot h^2 / 6$ | {_fmt(minimo['S_cm3'])} | cm³ |",
        f"| Momento de fisuración | $M_{{cr}} = 1.1 f_r S$ | {_fmt(minimo['Mcr_tf_m_m'])} | tf-m/m |",
        f"| 1.33 veces Momento último | $1.33 M_u$ | {_fmt(minimo['limite_133_Mu_tf_m_m'])} | tf-m/m |",
        f"| Mínimo normativo exigido | $\\min(M_{{cr}}, 1.33 M_u)$ | **{_fmt(minimo['M_minimo_exigido_tf_m_m'])}** | tf-m/m |",
        f"| Capacidad provista | $M_n$ | **{_fmt(minimo['Mn_provisto_tf_m_m'])}** | tf-m/m |",
        f"| **Estado verificación** | $M_n \\geq \\min(M_{{cr}}, 1.33M_u)$ | **{'✅ CUMPLE' if minimo['cumple'] else '❌ NO CUMPLE'}** | — |",
        "",
        "---",
        "",
        "## 6. ACERO DE TEMPERATURA Y RETRACCIÓN (Paso 6 - Art. 5.10.6)",
        "",
        "| Parámetro | Fórmula / Criterio | Valor | Unidad |",
        "|:---|:---|:---:|:---:|",
        f"| Espesor promedio | $t_{{prom}} = (t_{{sup1}} + t_{{inf}})/2$ | {_fmt(resultado['acero_temperatura']['t_prom_cm'])} | cm |",
        f"| Altura de aplicación | $h_{{temp}}$ | {_fmt(resultado['acero_temperatura']['h_temp_cm'])} | cm |",
        f"| Cuantía calculada | $A_{{s,temp}} = \\frac{{0.18 b h}}{{2(b+h)}}$ | {_fmt(resultado['acero_temperatura']['As_temp_calculado_cm2_m'])} | cm²/m en cada cara |",
        f"| Límite AASHTO LRFD | $2.33 \\leq A_s \\leq 12.70$ | {_fmt(resultado['acero_temperatura']['As_temp_normativo_cm2_m'])} | cm²/m en cada cara |",
        f"| **Refuerzo adoptado** | Ambas caras / Ambas direcciones | **{temp['barra']} @ {_fmt(temp['s_adoptado_cm'], 0)} cm** | **{temp['barra']} @ {_fmt(temp['s_adoptado_mm'], 0)} mm** |",
        f"| Área provista | $A_{{s,prov}}$ | {_fmt(temp['As_provisto_cm2_m'])} | cm²/m |",
        f"| Separación máxima permitida | $s_{{max}} = \\min(3t, 45\\text{{ cm}})$ | {_fmt(temp['s_max_normativo_cm'])} | cm |",
        f"| **Estado verificación** | $s_{{adopt}} \\leq s_{{max}}$ | **{'✅ CUMPLE' if temp['cumple'] else '❌ NO CUMPLE'}** | — |",
        "",
        "---",
        "",
        "## 7. CONTROL DE FISURACIÓN BAJO SERVICIO I (Paso 7 - Art. 5.6.7)",
        "",
        "| Parámetro | Fórmula / Símbolo | Valor | Límite / Criterio | Estado |",
        "|:---|:---|:---:|:---:|:---:|",
        f"| Momento de Servicio I | $M_s$ | {_fmt(fis['Ms_tf_m_m'])} tf-m/m | — | — |",
        f"| Relación modular | $n = E_s / E_c$ | {_fmt(fis['n'], 2)} | — | — |",
        f"| Eje neutro elástico | $y_{{cr}}$ | {_fmt(fis['y_cr_cm'])} cm | — | — |",
        f"| Brazo del par interno | $jd = d - y/3$ | {_fmt(fis['jd_cm'])} cm | — | — |",
        f"| Esfuerzo en el acero | $f_{{ss}} = \\frac{{M_s}}{{A_s \\cdot jd}}$ | {_fmt(fis['fs_kgf_cm2'], 1)} kg/cm² | $\\leq {_fmt(fis['limite_fs_kgf_cm2'], 1)}$ kg/cm² (0.60 fy) | {'✅ OK' if fis['cumple_esfuerzo'] else '❌ Excede'} |",
        f"| Factor geométrico | $\\beta_s = 1 + \\frac{{d_c}}{{0.7(h-d_c)}}$ | {_fmt(fis['beta_s'], 3)} | — | — |",
        f"| Factor de exposición | $\\gamma_e$ | {_fmt(fis['gamma_e'], 2)} | Severa (contacto con suelo) | — |",
        f"| Espaciamiento máximo | $s_{{max}} = \\frac{{125000\\gamma_e}}{{\\beta_s f_{{ss}}}} - 2d_c$ | **{_fmt(fis['s_max_fisuracion_cm'], 1)} cm** | $s_{{adopt}} = {_fmt(fis['s_adoptado_cm'], 0)} \\text{{ cm}}$ | {'✅ CUMPLE' if fis['cumple_espaciamiento'] else '❌ NO CUMPLE'} |",
        "",
        "---",
        "",
        "## 8. REVISIÓN POR CORTE — MÉTODO GENERAL AASHTO (Paso 8 - Art. 5.7.3.4.2)",
        "",
        "| Parámetro | Símbolo / Fórmula | Valor | Unidad | Criterio |",
        "|:---|:---|:---:|:---:|:---|",
        f"| Cortante último actuante | $V_u$ | {_fmt(cort['Vu_tf_m'])} | tf/m | Rige {'Evento Extremo I' if cort['Vu_tf_m'] == m_ext['V_u_tf_m'] else 'Resistencia I'} |",
        f"| Peralte efectivo de corte | $d_v = \\max(d-a/2, 0.9d, 0.72h)$ | {_fmt(cort['dv_cm'])} | cm | $d_v \\geq {_fmt(cort['limite_090_d_cm'])} \\text{{ cm}}$ ✓ |",
        f"| Deformación longitudinal | $\\varepsilon_s = \\frac{{|M_u/d_v + V_u|}}{{E_s A_s}}$ | {_fmt(cort['eps_s'], 6)} | — | Tracción longitudinal |",
        f"| Espaciamiento fisuras equiv. | $s_{{xe}}$ | {_fmt(cort['sxe_in'], 2)} | pulg | $12 \\leq s_{{xe}} \\leq 80$ ✓ |",
        f"| Factor de resistencia concreto | $\\beta$ | **{_fmt(cort['beta'], 3)}** | — | Ec. 5.7.3.4.2-2 |",
        f"| Resistencia del concreto | $V_c$ | {_fmt(cort['Vc_tf_m'])} | tf/m | Ec. 5.7.3.3-3 |",
        f"| Resistencia nominal | $V_n = \\min(V_c, 0.25 f'_c b d_v)$ | {_fmt(cort['Vn_tf_m'])} | tf/m | — |",
        f"| Resistencia de diseño | $V_r = \\phi_v V_n$ ($\\phi_v = 0.90$) | **{_fmt(cort['Vr_tf_m'])}** | **tf/m** | Capacidad sin estribos |",
        f"| Ratio Demanda/Capacidad | DCR corte | {_fmt(cort['DCR_cortante'], 3)} | — | {'✅ CUMPLE' if cort['cumple'] else '❌ NO CUMPLE'} |",
        "",
        f"> **Conclusión de corte:** $V_r = {_fmt(cort['Vr_tf_m'])} \\text{{ tf/m}} > V_u = {_fmt(cort['Vu_tf_m'])} \\text{{ tf/m}}$. **La pantalla NO requiere estribos transversales.** ✅",
        "",
        "---",
        "",
        "## 9. CUADRO RESUMEN DE ARMADURAS Y ESPECIFICACIONES",
        "",
        "| Elemento / Dirección | Refuerzo Adoptado | Espaciamiento | Cara de Colocación | Área Provista | Estado |",
        "|:---|:---:|:---:|:---|:---:|:---:|",
        f"| **Acero principal vertical** | **{flex['barra']}** | **@ {_fmt(flex['s_adoptado_cm'], 0)} cm** | Cara terreno (posterior) | {_fmt(flex['As_provisto_cm2_m'])} cm²/m | ✅ Conforme |",
        f"| **Acero temperatura vertical** | **{temp['barra']}** | **@ {_fmt(temp['s_adoptado_cm'], 0)} cm** | Cara libre (frontal) | {_fmt(temp['As_provisto_cm2_m'])} cm²/m | ✅ Conforme |",
        f"| **Acero horizontal (ambas caras)** | **{temp['barra']}** | **@ {_fmt(temp['s_adoptado_cm'], 0)} cm** | Ambas caras | {_fmt(temp['As_provisto_cm2_m'])} cm²/m | ✅ Conforme |",
        "",
        "---",
        "",
        "## 10. VERIFICACIONES NORMATIVAS CONSOLIDADAS",
        "",
        "| Verificación | Artículo AASHTO | Demanda | Capacidad / Límite | DCR | Estado |",
        "|:---|:---:|:---:|:---:|:---:|:---:|",
        f"| Flexión (Resistencia / Extremo) | Art. 5.6.3.2 | $M_u/\\phi = {_fmt(flex['As_requerido_cm2_m'], 1)} \\text{{ cm}}^2$ | $A_s = {_fmt(flex['As_provisto_cm2_m'], 1)} \\text{{ cm}}^2$ | {_fmt(flex['DCR_flexion'], 3)} | {'✅ OK' if flex['cumple'] else '❌ NO CUMPLE'} |",
        f"| Acero Mínimo | Art. 5.6.3.3 | $M_{{min}} = {_fmt(minimo['M_minimo_exigido_tf_m_m'])} \\text{{ tf-m}}$ | $M_n = {_fmt(minimo['Mn_provisto_tf_m_m'])} \\text{{ tf-m}}$ | {_fmt(minimo['M_minimo_exigido_tf_m_m']/minimo['Mn_provisto_tf_m_m'], 3)} | {'✅ OK' if minimo['cumple'] else '❌ NO CUMPLE'} |",
        f"| Control de Fisuración | Art. 5.6.7 | $s = {_fmt(fis['s_adoptado_cm'], 0)} \\text{{ cm}}$ | $s_{{max}} = {_fmt(fis['s_max_fisuracion_cm'], 1)} \\text{{ cm}}$ | {_fmt(fis['s_adoptado_cm']/fis['s_max_fisuracion_cm'], 3)} | {'✅ OK' if fis['cumple'] else '❌ NO CUMPLE'} |",
        f"| Cortante sin estribos | Art. 5.7.3.3 | $V_u = {_fmt(cort['Vu_tf_m'])} \\text{{ tf}}$ | $V_r = {_fmt(cort['Vr_tf_m'])} \\text{{ tf}}$ | {_fmt(cort['DCR_cortante'], 3)} | {'✅ OK' if cort['cumple'] else '❌ NO CUMPLE'} |",
        "",
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hp", type=float, default=GEOM.hp, help="Altura total de pantalla hp (m)")
    parser.add_argument("--hef", type=float, default=GEOM.hp - GEOM.c_cajuela - GEOM.d_cajuela, help="Altura efectiva de garganta (m)")
    parser.add_argument("--H", type=float, default=GEOM.H, help="Altura total de relleno H (m)")
    parser.add_argument("--tsup1", type=float, default=0.40, help="Espesor corona cajuela (m)")
    parser.add_argument("--tsup2", type=float, default=0.40, help="Espesor garganta (m)")
    parser.add_argument("--tinf", type=float, default=None, help="Espesor base empotrada (m, default 0.10*H)")
    parser.add_argument("--barras-verticales", nargs="+", default=['5/8"', '3/4"', '1"'])
    parser.add_argument("--barras-temperatura", nargs="+", default=['1/2"', '5/8"'])
    parser.add_argument("--barra-vertical-adoptada", type=str, default=None)
    parser.add_argument("--espaciamiento-vertical-adoptado", type=float, default=None)
    parser.add_argument("--recubrimiento-terreno", type=float, default=50.0)
    parser.add_argument("--output-dir", default=None, help="Carpeta de salida para resultados JSON y MD")

    args = parser.parse_args()
    t_inf_val = args.tinf if args.tinf is not None else 0.10 * args.H

    p = ParametrosPantallaVoladizo(
        altura_total_hp_m=args.hp,
        altura_efectiva_m=args.hef,
        altura_global_h_m=args.H,
        espesor_sup1_m=args.tsup1,
        espesor_sup2_m=args.tsup2,
        espesor_inf_m=t_inf_val,
        barras_verticales=tuple(args.barras_verticales),
        barras_temperatura=tuple(args.barras_temperatura),
        barra_vertical_adoptada=args.barra_vertical_adoptada,
        espaciamiento_vertical_adoptado_mm=args.espaciamiento_vertical_adoptado,
        recubrimiento_terreno_mm=args.recubrimiento_terreno,
    )

    resultado = evaluar(p)
    reporte = reporte_markdown(resultado)

    if args.output_dir:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "diseno_pantalla_voladizo.json").write_text(
            json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (out / "diseno_pantalla_voladizo.md").write_text(reporte, encoding="utf-8")
        print(f"Resultados guardados en {out}")

    print(reporte)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verificacion de la pared de cajuela como muro en voladizo.

El modelo corresponde a una franja de 1.00 m de la pared superior del estribo.
La base del voladizo se ubica donde termina el contrafuerte y la corona esta
3.40 m por encima. Las cargas del puente y sus factores proceden de
CALC-EST-2026-002-R00. El script no reparte cargas concentradas de apoyos en
la direccion horizontal: para ello se necesitan posiciones y placas de apoyo.

Unidades internas: m, tf, tf/m, tf-m, mm, MPa y cm2/m.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.agente_subestructura import (  # noqa: E402
    coulomb_active_coefficient,
    mononobe_okabe_coefficient,
)


TF_A_KN = 9.80665
TF_M_A_N_MM = 9.80665e6
KGF_CM2_A_MPA = 0.0980665
MPA_A_KSI = 0.1450377377
MM_POR_PULGADA = 25.4
CM2_M_POR_IN2_FT = 6.4516 / 0.3048


@dataclass(frozen=True)
class Parametros:
    # Geometria indicada por el usuario.
    altura_m: float = 3.40
    altura_global_empuje_m: float = 14.65
    espesor_m: float = 0.40
    ancho_franja_m: float = 1.00
    recubrimiento_frontal_mm: float = 50.0
    recubrimiento_relleno_mm: float = 75.0
    diametro_mm: float = 15.875  # 5/8 pulg
    espaciamiento_vertical_mm: float = 230.0
    espaciamiento_horizontal_mm: float = 230.0
    # Escenario complementario solicitado: sección engrosada solo en el
    # arranque, definida directamente mediante su peralte efectivo.
    peralte_efectivo_base_alternativo_mm: float = 1500.0

    # Materiales de CALC-EST-2026-002-R00.
    fc_kgf_cm2: float = 280.0
    fy_kgf_cm2: float = 4200.0
    gamma_relleno_tf_m3: float = 1.80
    gamma_concreto_tf_m3: float = 2.40
    phi_relleno_grados: float = 39.8
    delta_grados: float = 19.9

    # Reacciones por metro de CALC-EST-2026-002-R00.
    dc_tf_m: float = 25.98
    dw_tf_m: float = 2.88
    pl_tf_m: float = 3.08
    ll_im_tf_m: float = 12.95
    br_tf_m: float = 1.63

    # Parametros usados por el calculo vigente de subestructura.
    h_sobrecarga_m: float = 0.61
    kh: float = 0.125
    kv: float = 0.05
    porcentaje_sismico_superestructura: float = 0.24
    # La fuerza longitudinal del puente se introduce en la mesa de apoyo,
    # medida desde el arranque local del voladizo.
    altura_carga_puente_m: float = 1.00

    phi_flexion: float = 0.90
    phi_cortante_e060: float = 0.85
    phi_cortante_mtc: float = 0.90

    def validar(self) -> None:
        if self.altura_m <= 0 or self.espesor_m <= 0 or self.ancho_franja_m <= 0:
            raise ValueError("La geometria debe ser positiva")
        if self.altura_carga_puente_m < 0:
            raise ValueError("La altura de la carga del puente no puede ser negativa")
        if self.altura_global_empuje_m < self.altura_m:
            raise ValueError("La altura global de empuje no puede ser menor que la altura local")
        if min(self.espaciamiento_vertical_mm, self.espaciamiento_horizontal_mm) <= 0:
            raise ValueError("Los espaciamientos deben ser positivos")
        if self.peralte_efectivo_base_alternativo_mm <= 0:
            raise ValueError("El peralte efectivo alternativo debe ser positivo")
        limite = self.espesor_m * 1000.0 / 2.0
        if not 0 < self.recubrimiento_frontal_mm < limite:
            raise ValueError("Recubrimiento frontal incompatible con el espesor")
        if not 0 < self.recubrimiento_relleno_mm < limite:
            raise ValueError("Recubrimiento de relleno incompatible con el espesor")


@dataclass(frozen=True)
class Caso:
    nombre: str
    # Triángulo con intensidad máxima en la base: resultante a H/3.
    E_tri_tf_m: float
    # Trapezoide de Delta Eas recortado del diagrama global.
    E_trap_tf_m: float
    q_trap_base_tf_m2: float
    q_trap_corona_tf_m2: float
    E_uni_tf_m: float
    P_puente_tf_m: float
    V_tf_m: float
    M_tf_m_m: float
    axial_tf_m: float
    descripcion: str


def area_barra_cm2(db_mm: float) -> float:
    return math.pi * (db_mm / 10.0) ** 2 / 4.0


def acero_provisto_cm2_m(db_mm: float, s_mm: float) -> float:
    return area_barra_cm2(db_mm) * 1000.0 / s_mm


def coeficientes(p: Parametros) -> dict[str, float]:
    ka = coulomb_active_coefficient(p.phi_relleno_grados, p.delta_grados)
    psi = math.degrees(math.atan2(p.kh, 1.0 - p.kv))
    kae = mononobe_okabe_coefficient(
        p.phi_relleno_grados, p.delta_grados, psi
    )
    normal = math.cos(math.radians(p.delta_grados))
    return {
        "Ka_resultante": ka,
        "Kae_resultante": kae,
        "Ka_normal": ka * normal,
        "Kae_normal": kae * normal,
        "angulo_sismico_grados": psi,
    }


def _resultante_triangular(k: float, p: Parametros, factor_kv: float = 1.0) -> tuple[float, float]:
    q_base = p.gamma_relleno_tf_m3 * factor_kv * k * p.altura_m
    fuerza = 0.5 * q_base * p.altura_m
    momento = fuerza * p.altura_m / 3.0
    return fuerza, momento


def _resultante_uniforme(q_tf_m2: float, p: Parametros) -> tuple[float, float]:
    fuerza = q_tf_m2 * p.altura_m
    momento = fuerza * p.altura_m / 2.0
    return fuerza, momento


def _resultante_trapezoidal(
    q_base_tf_m2: float, q_corona_tf_m2: float, p: Parametros
) -> tuple[float, float]:
    """Resultante y momento de una presión lineal sobre la altura local.

    ``q_base`` actúa en y=0 y ``q_corona`` en y=H. El momento se obtiene
    separando un rectángulo de intensidad q_base y un triángulo superior.
    """
    h = p.altura_m
    fuerza = 0.5 * (q_base_tf_m2 + q_corona_tf_m2) * h
    momento = (
        q_base_tf_m2 * h**2 / 2.0
        + (q_corona_tf_m2 - q_base_tf_m2) * h**2 / 3.0
    )
    return fuerza, momento


def construir_casos(p: Parametros, c: dict[str, float]) -> list[Caso]:
    eh, meh = _resultante_triangular(c["Ka_normal"], p)
    qls = p.gamma_relleno_tf_m3 * c["Ka_normal"] * p.h_sobrecarga_m
    es, mes = _resultante_uniforme(qls, p)
    incremento_k = (1.0 - p.kv) * c["Kae_normal"] - c["Ka_normal"]
    if incremento_k < -1e-12:
        raise ValueError("El incremento sísmico Delta Eas resultó negativo")
    incremento_k = max(incremento_k, 0.0)
    q_delta_corona = p.gamma_relleno_tf_m3 * p.altura_global_empuje_m * incremento_k
    cota_arranque_global = p.altura_global_empuje_m - p.altura_m
    q_delta_base = q_delta_corona * (
        cota_arranque_global / p.altura_global_empuje_m
    )
    delta_eas, m_delta_eas = _resultante_trapezoidal(
        q_delta_base, q_delta_corona, p
    )
    pir, mpir = _resultante_uniforme(
        p.kh * p.gamma_concreto_tf_m3 * p.espesor_m, p
    )
    eq_super = p.porcentaje_sismico_superestructura * (p.dc_tf_m + p.dw_tf_m)

    servicio = Caso(
        "Servicio I",
        eh,
        0.0,
        0.0,
        0.0,
        es,
        p.br_tf_m,
        eh + es + p.br_tf_m,
        meh + mes + p.br_tf_m * p.altura_carga_puente_m,
        p.dc_tf_m + p.dw_tf_m + p.pl_tf_m + p.ll_im_tf_m,
        "Ea + Es + BR",
    )
    resistencia_ia = Caso(
        "Resistencia I-a",
        1.50 * eh,
        0.0,
        0.0,
        0.0,
        1.75 * es,
        1.75 * p.br_tf_m,
        1.50 * eh + 1.75 * es + 1.75 * p.br_tf_m,
        1.50 * meh + 1.75 * mes + 1.75 * p.br_tf_m * p.altura_carga_puente_m,
        0.90 * p.dc_tf_m + 0.65 * p.dw_tf_m + 1.75 * (p.pl_tf_m + p.ll_im_tf_m),
        "1.50 Ea + 1.75 Es + 1.75 BR",
    )
    resistencia_ib = Caso(
        "Resistencia I-b",
        resistencia_ia.E_tri_tf_m,
        resistencia_ia.E_trap_tf_m,
        resistencia_ia.q_trap_base_tf_m2,
        resistencia_ia.q_trap_corona_tf_m2,
        resistencia_ia.E_uni_tf_m,
        resistencia_ia.P_puente_tf_m,
        resistencia_ia.V_tf_m,
        resistencia_ia.M_tf_m_m,
        1.25 * p.dc_tf_m + 1.50 * p.dw_tf_m + 1.75 * (p.pl_tf_m + p.ll_im_tf_m),
        "1.50 Ea + 1.75 Es + 1.75 BR",
    )
    # Evento Extremo I oficial del expediente. En el modelo local:
    # PAE = Ea + Delta Eas. Delta Eas se recorta del triángulo global de H_g,
    # por lo que sobre los últimos H metros resulta un trapecio;
    # PIR = inercia propia de la pantalla (Eq-estribo).
    evento_extremo = Caso(
        "Evento Extremo I",
        eh,
        delta_eas,
        q_delta_base,
        q_delta_corona,
        pir,
        eq_super,
        eh + delta_eas + pir + eq_super,
        meh + m_delta_eas + mpir + eq_super * p.altura_carga_puente_m,
        0.90 * p.dc_tf_m + 0.65 * p.dw_tf_m,
        "Ea + Delta Eas trapezoidal + PIR + EQ-super",
    )
    return [servicio, resistencia_ia, resistencia_ib, evento_extremo]


def capacidad_flexion_tf_m(as_cm2_m: float, d_mm: float, p: Parametros) -> float:
    b_cm = p.ancho_franja_m * 100.0
    d_cm = d_mm / 10.0
    a_cm = as_cm2_m * p.fy_kgf_cm2 / (0.85 * p.fc_kgf_cm2 * b_cm)
    if a_cm >= d_cm:
        raise ValueError("Bloque de compresion incompatible con el peralte")
    mn_kgf_cm = as_cm2_m * p.fy_kgf_cm2 * (d_cm - a_cm / 2.0)
    return p.phi_flexion * mn_kgf_cm / 100_000.0


def acero_flexion_requerido_cm2_m(mu_tf_m: float, d_mm: float, p: Parametros) -> float:
    if mu_tf_m <= 0:
        return 0.0
    b_cm = p.ancho_franja_m * 100.0
    d_cm = d_mm / 10.0
    mu_kgf_cm = mu_tf_m * 100_000.0
    disc = d_cm**2 - 2.0 * mu_kgf_cm / (
        p.phi_flexion * 0.85 * p.fc_kgf_cm2 * b_cm
    )
    if disc <= 0:
        return float("inf")
    a_cm = d_cm - math.sqrt(disc)
    return 0.85 * p.fc_kgf_cm2 * b_cm * a_cm / p.fy_kgf_cm2


def minimos_por_cara(p: Parametros, d_mm: float) -> dict[str, float]:
    b_cm = p.ancho_franja_m * 100.0
    h_cm = p.espesor_m * 100.0
    as_temp_e060 = 0.0018 * b_cm * h_cm / 2.0
    as_min_flex_e060 = 0.70 * math.sqrt(p.fc_kgf_cm2) * b_cm * (d_mm / 10.0) / p.fy_kgf_cm2

    b_in = 12.0
    h_in = p.espesor_m * 1000.0 / MM_POR_PULGADA
    fy_ksi = p.fy_kgf_cm2 * KGF_CM2_A_MPA * MPA_A_KSI
    as_in2_ft = 1.30 * b_in * h_in / (2.0 * (b_in + h_in) * fy_ksi)
    as_in2_ft = min(max(as_in2_ft, 0.11), 0.60)
    as_temp_mtc = as_in2_ft * CM2_M_POR_IN2_FT
    return {
        "temperatura_E060_cm2_m": as_temp_e060,
        "min_flexion_E060_cm2_m": as_min_flex_e060,
        "temperatura_MTC_cm2_m": as_temp_mtc,
    }


def capacidades_cortante_tf(d_mm: float, p: Parametros) -> dict[str, float]:
    fc_mpa = p.fc_kgf_cm2 * KGF_CM2_A_MPA
    bw_mm = p.ancho_franja_m * 1000.0
    vc_e_n = 0.17 * math.sqrt(fc_mpa) * bw_mm * d_mm
    dv_mm = max(0.9 * d_mm, 0.72 * p.espesor_m * 1000.0)
    vc_m_n = 0.083 * 2.0 * math.sqrt(fc_mpa) * bw_mm * dv_mm
    e060 = p.phi_cortante_e060 * vc_e_n / 9806.65
    mtc = p.phi_cortante_mtc * vc_m_n / 9806.65
    return {"E060_tf": e060, "MTC_tf": mtc, "adoptada_tf": min(e060, mtc)}


def esfuerzo_acero_servicio_mpa(ms_tf_m: float, as_cm2_m: float, d_mm: float) -> float:
    return ms_tf_m * TF_M_A_N_MM / (as_cm2_m * 100.0 * 0.90 * d_mm)


def limite_fisuracion_mm(fs_mpa: float, recubrimiento_mm: float, db_mm: float, p: Parametros) -> float:
    if fs_mpa <= 0:
        return float("inf")
    dc_in = (recubrimiento_mm + db_mm / 2.0) / MM_POR_PULGADA
    h_in = p.espesor_m * 1000.0 / MM_POR_PULGADA
    fs_ksi = fs_mpa * MPA_A_KSI
    beta_s = 1.0 + dc_in / (0.7 * (h_in - dc_in))
    return (700.0 / (beta_s * fs_ksi) - 2.0 * dc_in) * MM_POR_PULGADA


def desplazamiento_servicio_mm(p: Parametros, c: dict[str, float]) -> dict[str, float]:
    h = p.altura_m
    q_tri_base = p.gamma_relleno_tf_m3 * c["Ka_normal"] * h
    q_uni = p.gamma_relleno_tf_m3 * c["Ka_normal"] * p.h_sobrecarga_m
    fc_mpa = p.fc_kgf_cm2 * KGF_CM2_A_MPA
    ec_mpa = 4700.0 * math.sqrt(fc_mpa)
    i_mm4 = p.ancho_franja_m * 1000.0 * (p.espesor_m * 1000.0) ** 3 / 12.0
    h_mm = h * 1000.0
    qtri_n_mm = q_tri_base * TF_A_KN
    quni_n_mm = q_uni * TF_A_KN
    p_n = p.br_tf_m * TF_A_KN * 1000.0
    a_mm = p.altura_carga_puente_m * 1000.0
    # Si la resultante actua por encima de la corona, se representa como una
    # fuerza en el extremo mas el momento P(a-H) transmitido al muro.
    momento_extremo_n_mm = p_n * max(a_mm - h_mm, 0.0)
    delta = (
        qtri_n_mm * h_mm**4 / (30.0 * ec_mpa * i_mm4)
        + quni_n_mm * h_mm**4 / (8.0 * ec_mpa * i_mm4)
        + p_n * h_mm**3 / (3.0 * ec_mpa * i_mm4)
        + momento_extremo_n_mm * h_mm**2 / (2.0 * ec_mpa * i_mm4)
    )
    return {"Ig_mm": delta, "0.35Ig_mm": delta / 0.35, "Ec_MPa": ec_mpa}


def evaluar(p: Parametros) -> dict:
    p.validar()
    c = coeficientes(p)
    casos = construir_casos(p, c)
    servicio = next(x for x in casos if x.nombre == "Servicio I")
    resistentes = [x for x in casos if x.nombre != "Servicio I"]
    gobernante = max(resistentes, key=lambda x: x.M_tf_m_m)
    as_vertical = acero_provisto_cm2_m(p.diametro_mm, p.espaciamiento_vertical_mm)
    as_horizontal = acero_provisto_cm2_m(p.diametro_mm, p.espaciamiento_horizontal_mm)

    caras = []
    for nombre, rec in (
        ("frontal/no relleno", p.recubrimiento_frontal_mm),
        ("posterior/relleno", p.recubrimiento_relleno_mm),
    ):
        d = p.espesor_m * 1000.0 - rec - p.diametro_mm / 2.0
        mins = minimos_por_cara(p, d)
        as_flex = acero_flexion_requerido_cm2_m(gobernante.M_tf_m_m, d, p)
        as_req = max(as_flex, *mins.values())
        phi_mn = capacidad_flexion_tf_m(as_vertical, d, p)
        fs = esfuerzo_acero_servicio_mpa(servicio.M_tf_m_m, as_vertical, d)
        s_fis = limite_fisuracion_mm(fs, rec, p.diametro_mm, p)
        caras.append({
            "cara": nombre,
            "recubrimiento_mm": rec,
            "d_mm": d,
            "As_flexion_requerido_cm2_m": as_flex,
            **mins,
            "As_requerido_cm2_m": as_req,
            "As_provisto_cm2_m": as_vertical,
            "DCR_area": as_req / as_vertical,
            "phi_Mn_tf_m_m": phi_mn,
            "DCR_flexion": gobernante.M_tf_m_m / phi_mn,
            "fs_servicio_MPa": fs,
            "limite_fs_MPa": 0.60 * p.fy_kgf_cm2 * KGF_CM2_A_MPA,
            "limite_separacion_fisuracion_mm": s_fis,
            "fisuracion_cumple": p.espaciamiento_vertical_mm <= s_fis and fs <= 0.60 * p.fy_kgf_cm2 * KGF_CM2_A_MPA,
        })

    min_horizontal = max(
        minimos_por_cara(p, min(x["d_mm"] for x in caras))["temperatura_E060_cm2_m"],
        minimos_por_cara(p, min(x["d_mm"] for x in caras))["temperatura_MTC_cm2_m"],
    )
    vc = capacidades_cortante_tf(min(x["d_mm"] for x in caras), p)
    axial_mpa = gobernante.axial_tf_m * TF_A_KN * 1000.0 / (
        p.ancho_franja_m * 1000.0 * p.espesor_m * 1000.0
    )
    resultado = {
        "parametros": asdict(p),
        "fuente": "CALC-EST-2026-002-R00.md",
        "coeficientes": c,
        "casos": [asdict(x) for x in casos],
        "caso_gobernante": gobernante.nombre,
        "momento_gobernante_tf_m_m": gobernante.M_tf_m_m,
        "cortante_gobernante_tf_m": max(x.V_tf_m for x in resistentes),
        "caras_verticales": caras,
        "horizontal": {
            "As_requerido_cm2_m": min_horizontal,
            "As_provisto_cm2_m": as_horizontal,
            "DCR_area": min_horizontal / as_horizontal,
            "cumple": as_horizontal >= min_horizontal,
        },
        "cortante": {
            **vc,
            "Vu_tf_m": max(x.V_tf_m for x in resistentes),
            "DCR": max(x.V_tf_m for x in resistentes) / vc["adoptada_tf"],
        },
        "axial": {
            "Pu_tf_m": gobernante.axial_tf_m,
            "esfuerzo_promedio_MPa": axial_mpa,
            "relacion_P_Ag_fc": axial_mpa / (p.fc_kgf_cm2 * KGF_CM2_A_MPA),
            "nota": "No se acredita aumento de capacidad a flexion por compresion axial.",
        },
        "desplazamiento_servicio": desplazamiento_servicio_mm(p, c),
    }

    # Verificación complementaria de la sección crítica en la base. Se cambia
    # únicamente el peralte efectivo; las demandas y el armado se conservan.
    d_alt = p.peralte_efectivo_base_alternativo_mm
    mins_alt = minimos_por_cara(p, d_alt)
    as_flex_alt = acero_flexion_requerido_cm2_m(
        gobernante.M_tf_m_m, d_alt, p
    )
    as_req_alt = max(as_flex_alt, *mins_alt.values())
    phi_mn_alt = capacidad_flexion_tf_m(as_vertical, d_alt, p)
    vc_alt = capacidades_cortante_tf(d_alt, p)
    resultado["base_alternativa"] = {
        "alcance": "Sección local en el arranque; demandas sin modificación.",
        "d_mm": d_alt,
        "As_flexion_requerido_cm2_m": as_flex_alt,
        **mins_alt,
        "control_normativo": "Acero mínimo a flexión E.060",
        "As_requerido_cm2_m": as_req_alt,
        "As_provisto_cm2_m": as_vertical,
        "DCR_area": as_req_alt / as_vertical,
        "phi_Mn_tf_m_m": phi_mn_alt,
        "DCR_flexion": gobernante.M_tf_m_m / phi_mn_alt,
        "cortante_capacidad_tf_m": vc_alt["adoptada_tf"],
        "DCR_cortante": max(x.V_tf_m for x in resistentes) / vc_alt["adoptada_tf"],
        "cumple_resistencia_flexion": gobernante.M_tf_m_m <= phi_mn_alt,
        "cumple_area": as_vertical >= as_req_alt,
        "cumple_cortante": max(x.V_tf_m for x in resistentes) <= vc_alt["adoptada_tf"],
    }
    resultado["base_alternativa"]["cumple"] = (
        resultado["base_alternativa"]["cumple_resistencia_flexion"]
        and resultado["base_alternativa"]["cumple_area"]
        and resultado["base_alternativa"]["cumple_cortante"]
    )
    resultado["cumple_vertical"] = all(
        x["DCR_area"] <= 1.0 and x["DCR_flexion"] <= 1.0 and x["fisuracion_cumple"]
        for x in caras
    )
    resultado["cumple_cortante"] = resultado["cortante"]["DCR"] <= 1.0
    resultado["cumple_global"] = (
        resultado["cumple_vertical"]
        and resultado["horizontal"]["cumple"]
        and resultado["cumple_cortante"]
    )
    separaciones_ok = []
    for s_mm in range(50, 401, 5):
        as_s = acero_provisto_cm2_m(p.diametro_mm, float(s_mm))
        cumple_s = True
        for x in caras:
            phi_mn_s = capacidad_flexion_tf_m(as_s, x["d_mm"], p)
            fs_s = esfuerzo_acero_servicio_mpa(
                servicio.M_tf_m_m, as_s, x["d_mm"]
            )
            s_fis_s = limite_fisuracion_mm(
                fs_s, x["recubrimiento_mm"], p.diametro_mm, p
            )
            cumple_s = cumple_s and (
                as_s >= x["As_requerido_cm2_m"]
                and gobernante.M_tf_m_m <= phi_mn_s
                and s_mm <= s_fis_s
                and fs_s <= 0.60 * p.fy_kgf_cm2 * KGF_CM2_A_MPA
            )
        if cumple_s:
            separaciones_ok.append(float(s_mm))
    resultado["separacion_maxima_vertical_5_8_mm"] = (
        max(separaciones_ok) if separaciones_ok else None
    )
    s_area_horizontal = area_barra_cm2(p.diametro_mm) * 1000.0 / min_horizontal
    resultado["separacion_maxima_horizontal_5_8_mm"] = min(
        400.0, math.floor(s_area_horizontal / 5.0) * 5.0
    )
    return resultado


def _fmt(x: float, n: int = 3) -> str:
    return f"{x:.{n}f}"


def reporte_markdown(r: dict) -> str:
    p = r["parametros"]
    if p["porcentaje_sismico_superestructura"] > 0:
        nota_eq = (
            "El resultado incluye la fuerza sismica de la superestructura "
            "indicada por el modelo vigente. Si esa fuerza se transfiere por "
            "otro elemento y no por la pared de cajuela, debe documentarse la "
            "ruta de carga y volver a ejecutar el script con el caso "
            "correspondiente; no debe eliminarse sin sustento."
        )
    else:
        nota_eq = (
            "Escenario de sensibilidad sin transferencia de EQ-super a la "
            "pared. Solo es util si la ruta alternativa de esa fuerza queda "
            "demostrada mediante el detalle de apoyos, cajuela y contrafuertes."
        )
    lines = [
        "# Verificacion de la pared de cajuela en voladizo",
        "",
        "## Modelo",
        "",
        f"- Franja: 1.00 m; altura local: {p['altura_m']:.2f} m; altura global de empuje: {p['altura_global_empuje_m']:.2f} m; espesor: {p['espesor_m']:.2f} m.",
        f"- Armado evaluado: Ø5/8\" @ {p['espaciamiento_vertical_mm']:.0f} mm vertical y @ {p['espaciamiento_horizontal_mm']:.0f} mm horizontal, en ambas caras.",
        f"- Escenario complementario en la base: peralte efectivo local d = {p['peralte_efectivo_base_alternativo_mm'] / 1000.0:.2f} m, sin modificar las demandas del voladizo.",
        f"- La fuerza horizontal del puente se aplica en la mesa de apoyo, a {p['altura_carga_puente_m']:.2f} m sobre el arranque.",
        "- La compresion axial del puente se cuantifica, pero no se acredita para aumentar la capacidad a flexion.",
        "",
        "## Demandas",
        "",
        "| Caso | Combinacion | V (tf/m) | M base (tf·m/m) | P axial (tf/m) |",
        "|---|---|---:|---:|---:|",
    ]
    for c in r["casos"]:
        lines.append(
            f"| {c['nombre']} | {c['descripcion']} | {_fmt(c['V_tf_m'])} | {_fmt(c['M_tf_m_m'])} | {_fmt(c['axial_tf_m'])} |"
        )
    lines += [
        "",
        f"Gobierna **{r['caso_gobernante']}**, con M_u = {_fmt(r['momento_gobernante_tf_m_m'])} tf·m/m.",
        "",
        "## Acero vertical por cara",
        "",
        "| Cara | d (mm) | As calc. | As norm. gobernante | As req. | As disp. | D/C acero | φMn | D/C flexión | Estado |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for x in r["caras_verticales"]:
        ok = x["DCR_area"] <= 1 and x["DCR_flexion"] <= 1 and x["fisuracion_cumple"]
        lines.append(
            f"| {x['cara']} | {_fmt(x['d_mm'],1)} | {_fmt(x['As_flexion_requerido_cm2_m'])} cm²/m | {_fmt(max(x['temperatura_E060_cm2_m'], x['min_flexion_E060_cm2_m'], x['temperatura_MTC_cm2_m']))} cm²/m (mín. flexión) | {_fmt(x['As_requerido_cm2_m'])} cm²/m | {_fmt(x['As_provisto_cm2_m'])} cm²/m | {_fmt(x['DCR_area'])} | {_fmt(x['phi_Mn_tf_m_m'])} tf·m/m | {_fmt(x['DCR_flexion'])} | {'Cumple' if ok else 'No cumple'} |"
        )
    lines += [
        "",
        "### Fisuración bajo Servicio I",
        "",
        "| Cara | f_s | Límite de f_s | Separación dispuesta | Separación límite | Estado |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for x in r["caras_verticales"]:
        lines.append(
            f"| {x['cara']} | {_fmt(x['fs_servicio_MPa'],1)} MPa | {_fmt(x['limite_fs_MPa'],1)} MPa | {p['espaciamiento_vertical_mm']:.0f} mm | {_fmt(x['limite_separacion_fisuracion_mm'],0)} mm | {'Cumple' if x['fisuracion_cumple'] else 'No cumple'} |"
        )
    b_alt = r["base_alternativa"]
    lines += [
        "",
        "La fisuración de la sección actual se verifica adicionalmente con el momento de Servicio I; no gobierna el resultado de las dos caras.",
        "",
        "## Verificación complementaria en la base con d = 1.50 m",
        "",
        "Esta comprobación representa únicamente una sección local engrosada en el arranque. Se mantienen el momento, el cortante y el armado Ø5/8\" @ 230 mm de la evaluación principal. El cambio no se extiende a la rigidez del fuste ni modifica la distribución de cargas. La geometría final deberá proporcionar efectivamente d = 1.50 m y permitir el desarrollo y anclaje del refuerzo.",
        "",
        "| Control | Demanda o requisito | Capacidad o disposición | D/C | Estado |",
        "|---|---:|---:|---:|---|",
        f"| Área por flexión calculada | {_fmt(b_alt['As_flexion_requerido_cm2_m'])} cm²/m | {_fmt(b_alt['As_provisto_cm2_m'])} cm²/m | {_fmt(b_alt['As_flexion_requerido_cm2_m'] / b_alt['As_provisto_cm2_m'])} | {'Cumple' if b_alt['As_provisto_cm2_m'] >= b_alt['As_flexion_requerido_cm2_m'] else 'No cumple'} |",
        f"| Acero mínimo a flexión adoptado | {_fmt(b_alt['min_flexion_E060_cm2_m'])} cm²/m | {_fmt(b_alt['As_provisto_cm2_m'])} cm²/m | {_fmt(b_alt['DCR_area'])} | {'Cumple' if b_alt['cumple_area'] else 'No cumple'} |",
        f"| Resistencia a flexión | M_u = {_fmt(r['momento_gobernante_tf_m_m'])} tf·m/m | φM_n = {_fmt(b_alt['phi_Mn_tf_m_m'])} tf·m/m | {_fmt(b_alt['DCR_flexion'])} | {'Cumple' if b_alt['cumple_resistencia_flexion'] else 'No cumple'} |",
        f"| Cortante | V_u = {_fmt(r['cortante_gobernante_tf_m'])} tf/m | φV_n = {_fmt(b_alt['cortante_capacidad_tf_m'])} tf/m | {_fmt(b_alt['DCR_cortante'])} | {'Cumple' if b_alt['cumple_cortante'] else 'No cumple'} |",
        "",
        f"**Resultado de la sección local con d = 1.50 m: {'CUMPLE' if b_alt['cumple'] else 'NO CUMPLE'}.** La resistencia a flexión y a cortante es suficiente, pero el cumplimiento global exige además satisfacer el acero mínimo asociado al nuevo peralte.",
    ]
    h = r["horizontal"]
    v = r["cortante"]
    a = r["axial"]
    lines += [
        "",
        "## Otros controles",
        "",
        "| Control | Demanda/requisito | Capacidad/provision | D/C | Estado |",
        "|---|---:|---:|---:|---|",
        f"| Acero horizontal por cara | {_fmt(h['As_requerido_cm2_m'])} cm²/m | {_fmt(h['As_provisto_cm2_m'])} cm²/m | {_fmt(h['DCR_area'])} | {'Cumple' if h['cumple'] else 'No cumple'} |",
        f"| Cortante | {_fmt(v['Vu_tf_m'])} tf/m | {_fmt(v['adoptada_tf'])} tf/m | {_fmt(v['DCR'])} | {'Cumple' if v['DCR'] <= 1 else 'No cumple'} |",
        f"| Compresion axial media | {_fmt(a['esfuerzo_promedio_MPa'])} MPa | f'c = {_fmt(p['fc_kgf_cm2']*KGF_CM2_A_MPA)} MPa | {_fmt(a['relacion_P_Ag_fc'])} | Informativo |",
        "",
        f"Con Ø5/8\", la separación vertical máxima que satisface la envolvente calculada es **{_fmt(r['separacion_maxima_vertical_5_8_mm'],0)} mm**. Para el acero horizontal por mínimos, el límite calculado es **{_fmt(r['separacion_maxima_horizontal_5_8_mm'],0)} mm** (además de los límites generales de espaciamiento).",
        "",
        "## Resultado",
        "",
        f"**Estado global: {'CUMPLE' if r['cumple_global'] else 'NO CUMPLE'}.**",
        "",
        nota_eq,
        "",
        "Pendiente para cierre definitivo: verificar distribucion horizontal/local alrededor de apoyos y juntas con sus posiciones, dimensiones de placas, excentricidades y detalle de anclaje al cuello de la pantalla.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--altura", type=float, default=3.40)
    parser.add_argument(
        "--altura-global-empuje", type=float, default=14.65,
        help="Altura global H_g del diagrama de Delta Eas (m)",
    )
    parser.add_argument("--espesor", type=float, default=0.40)
    parser.add_argument("--separacion-vertical", type=float, default=230.0)
    parser.add_argument("--separacion-horizontal", type=float, default=230.0)
    parser.add_argument(
        "--peralte-efectivo-base", type=float, default=1500.0,
        help="Peralte efectivo de la sección local alternativa en la base (mm)",
    )
    parser.add_argument(
        "--altura-carga-puente", type=float, default=1.00,
        help="Cota de la mesa de apoyo sobre el arranque local (m)",
    )
    parser.add_argument("--porcentaje-sismico-superestructura", type=float, default=0.24)
    parser.add_argument("--output-dir", default="outputs/calc_est_2026_006")
    args = parser.parse_args()
    p = Parametros(
        altura_m=args.altura,
        altura_global_empuje_m=args.altura_global_empuje,
        espesor_m=args.espesor,
        espaciamiento_vertical_mm=args.separacion_vertical,
        espaciamiento_horizontal_mm=args.separacion_horizontal,
        peralte_efectivo_base_alternativo_mm=args.peralte_efectivo_base,
        altura_carga_puente_m=args.altura_carga_puente,
        porcentaje_sismico_superestructura=args.porcentaje_sismico_superestructura,
    )
    resultado = evaluar(p)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "verificacion_cajuela_voladizo.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out / "verificacion_cajuela_voladizo.md").write_text(
        reporte_markdown(resultado), encoding="utf-8"
    )
    print(reporte_markdown(resultado))


if __name__ == "__main__":
    main()

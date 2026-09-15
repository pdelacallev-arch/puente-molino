#!/usr/bin/env python3
"""Diseño normativo de la pared de cajuela como muro en voladizo.

El modelo corresponde a una franja de 1.00 m de la pared superior del estribo.
La seccion de analisis se ubica en la base, inmediatamente debajo de la mesa
de apoyo, y la corona esta a la altura local por encima. Las cargas del puente y sus factores proceden de
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

from analisis_estabilidad.elementos.estribo.estabilidad_global import (  # noqa: E402
    GEOM,
    coulomb_active_coefficient,
    mononobe_okabe_coefficient,
)


TF_A_KN = 9.80665
TF_M_A_N_MM = 9.80665e6
KGF_CM2_A_MPA = 0.0980665
MPA_A_KSI = 0.1450377377
MM_POR_PULGADA = 25.4
CM2_M_POR_IN2_FT = 6.4516 / 0.3048
BARRAS_INGLESAS_MM = {
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
}


@dataclass(frozen=True)
class Parametros:
    # Geometría derivada del estribo (GEOM): altura local = cajuela (c + d) y
    # altura global de empuje = altura total del estribo (H).
    altura_m: float = GEOM.c_cajuela + GEOM.d_cajuela
    altura_global_empuje_m: float = GEOM.H
    espesor_m: float = 0.40
    ancho_franja_m: float = 1.00
    recubrimiento_frontal_mm: float = 50.0
    recubrimiento_relleno_mm: float = 75.0
    barras_verticales: tuple[str, ...] = ('5/8"', '3/4"', '1"')
    barras_horizontales: tuple[str, ...] = ('1/2"',)
    espaciamiento_horizontal_adoptado_mm: float | None = 300.0
    espaciamiento_minimo_mm: float = 100.0
    espaciamiento_maximo_mm: float = 400.0
    paso_espaciamiento_mm: float = 5.0

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
    # Brazos independientes medidos desde el arranque local del voladizo.
    # BR conserva la cota previamente adoptada; EQ-super se ubica en la cara
    # superior de la mesa de apoyo de 0.70 m.
    brazo_br_m: float = 1.00
    brazo_eq_super_m: float = 0.70

    phi_flexion: float = 0.90
    phi_cortante_e060: float = 0.85
    phi_cortante_mtc: float = 0.90

    def validar(self) -> None:
        if self.altura_m <= 0 or self.espesor_m <= 0 or self.ancho_franja_m <= 0:
            raise ValueError("La geometria debe ser positiva")
        if min(self.brazo_br_m, self.brazo_eq_super_m) < 0:
            raise ValueError("Los brazos de BR y EQ-super no pueden ser negativos")
        if self.altura_global_empuje_m < self.altura_m:
            raise ValueError("La altura global de empuje no puede ser menor que la altura local")
        if min(
            self.espaciamiento_minimo_mm,
            self.espaciamiento_maximo_mm,
            self.paso_espaciamiento_mm,
        ) <= 0:
            raise ValueError("Los límites y el paso de espaciamiento deben ser positivos")
        if self.espaciamiento_minimo_mm > self.espaciamiento_maximo_mm:
            raise ValueError("El espaciamiento mínimo supera al máximo")
        if not self.barras_verticales or not self.barras_horizontales:
            raise ValueError("Debe existir al menos una barra vertical y una horizontal")
        faltantes = (
            set(self.barras_verticales) | set(self.barras_horizontales)
        ) - set(BARRAS_INGLESAS_MM)
        if faltantes:
            raise ValueError(f"Barras desconocidas: {sorted(faltantes)}")
        if self.espaciamiento_horizontal_adoptado_mm is not None:
            s_h = self.espaciamiento_horizontal_adoptado_mm
            if not self.espaciamiento_minimo_mm <= s_h <= self.espaciamiento_maximo_mm:
                raise ValueError("El espaciamiento horizontal adoptado está fuera de límites")
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


@dataclass(frozen=True)
class CasoInverso:
    """Respuesta con la inercia sísmica invertida (hacia el relleno).

    La presión del terreno permanece hacia el vacío; la inercia propia (PIR)
    y la de la superestructura (EQ-super) actúan en sentido contrario. Los
    factores PAE/PIR corresponden a las concurrencias del MTC 2018,
    Art. 2.8.1.1.14.1.
    """

    nombre: str
    componente_terreno: str
    factor_pae: float
    factor_pir: float
    M_Ea_tf_m_m: float
    M_Delta_Eas_tf_m_m: float
    M_PIR_tf_m_m: float
    M_EQsuper_tf_m_m: float
    M_inverso_tf_m_m: float
    V_inverso_tf_m: float
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
        meh + mes + p.br_tf_m * p.brazo_br_m,
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
        1.50 * meh + 1.75 * mes + 1.75 * p.br_tf_m * p.brazo_br_m,
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
    # Evento Extremo I, MTC 2018 Art. 2.8.1.1.14.1:
    #   I-A = 100% PAE + 50% PIR
    #   I-B = max(50% PAE, PA) + 100% PIR
    # PAE = Ea + Delta Eas. En el tramo local de la cajuela, Delta Eas es el
    # recorte trapezoidal del diagrama global de altura H_g. EQ-super se
    # mantiene al 100% en ambas concurrencias mientras su ruta de carga pase
    # por la pared de cajuela.
    evento_extremo_ia = Caso(
        "Evento Extremo I-A",
        eh,
        delta_eas,
        q_delta_base,
        q_delta_corona,
        0.50 * pir,
        eq_super,
        eh + delta_eas + 0.50 * pir + eq_super,
        meh + m_delta_eas + 0.50 * mpir + eq_super * p.brazo_eq_super_m,
        0.90 * p.dc_tf_m + 0.65 * p.dw_tf_m,
        "100% PAE + 50% PIR + 100% EQ-super",
    )

    # La comparación MTC se efectúa entre fuerzas. Si 50% PAE es menor que
    # PA se recupera el diagrama estático completo; en caso contrario se
    # escala el diagrama PAE completo.
    usa_pa_en_ib = 0.50 * (eh + delta_eas) < eh
    if usa_pa_en_ib:
        ib_eh, ib_meh = eh, meh
        ib_delta, ib_mdelta = 0.0, 0.0
        ib_qbase, ib_qcorona = 0.0, 0.0
        seleccion_ib = "PA"
    else:
        ib_eh, ib_meh = 0.50 * eh, 0.50 * meh
        ib_delta, ib_mdelta = 0.50 * delta_eas, 0.50 * m_delta_eas
        ib_qbase = 0.50 * q_delta_base
        ib_qcorona = 0.50 * q_delta_corona
        seleccion_ib = "50% PAE"
    evento_extremo_ib = Caso(
        "Evento Extremo I-B",
        ib_eh,
        ib_delta,
        ib_qbase,
        ib_qcorona,
        pir,
        eq_super,
        ib_eh + ib_delta + pir + eq_super,
        ib_meh + ib_mdelta + mpir + eq_super * p.brazo_eq_super_m,
        0.90 * p.dc_tf_m + 0.65 * p.dw_tf_m,
        f"max(50% PAE, PA) + 100% PIR + 100% EQ-super [{seleccion_ib}]",
    )
    return [
        servicio, resistencia_ia, resistencia_ib,
        evento_extremo_ia, evento_extremo_ib,
    ]


def construir_casos_inversos(
    p: Parametros, casos: list[Caso], axial_tf_m: float
) -> list[CasoInverso]:
    """Evalúa ambas concurrencias MTC con la inercia en sentido inverso."""
    e_eqs = p.porcentaje_sismico_superestructura * (p.dc_tf_m + p.dw_tf_m)
    m_eqs = e_eqs * p.brazo_eq_super_m
    salida: list[CasoInverso] = []
    for nombre, factor_pir in (
        ("Evento Extremo I-A inverso", 0.50),
        ("Evento Extremo I-B inverso", 1.00),
    ):
        directo = next(c for c in casos if c.nombre == nombre.removesuffix(" inverso"))
        e_terreno = directo.E_tri_tf_m + directo.E_trap_tf_m
        m_ea = directo.E_tri_tf_m * p.altura_m / 3.0
        m_delta = (
            directo.q_trap_base_tf_m2 * p.altura_m**2 / 2.0
            + (directo.q_trap_corona_tf_m2 - directo.q_trap_base_tf_m2)
            * p.altura_m**2 / 3.0
        )
        e_pir = directo.E_uni_tf_m
        m_pir = e_pir * p.altura_m / 2.0
        salida.append(CasoInverso(
            nombre=nombre,
            componente_terreno=(
                "100% PAE" if nombre.startswith("Evento Extremo I-A")
                else directo.descripcion.split(" + 100% PIR", 1)[0]
            ),
            factor_pae=1.00 if nombre.startswith("Evento Extremo I-A") else 0.50,
            factor_pir=factor_pir,
            M_Ea_tf_m_m=m_ea,
            M_Delta_Eas_tf_m_m=m_delta,
            M_PIR_tf_m_m=m_pir,
            M_EQsuper_tf_m_m=m_eqs,
            M_inverso_tf_m_m=(m_pir + m_eqs) - (m_ea + m_delta),
            V_inverso_tf_m=(e_pir + e_eqs) - e_terreno,
            axial_tf_m=axial_tf_m,
            descripcion=(
                "PIR + EQ-super hacia el relleno; componente MTC de terreno "
                "hacia el vacio"
            ),
        ))
    return salida


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


def limite_espaciamiento_general_mm(p: Parametros) -> float:
    e060 = min(3.0 * p.espesor_m * 1000.0, 400.0)
    mtc = min(1.5 * p.espesor_m * 1000.0, 450.0)
    return min(e060, mtc, p.espaciamiento_maximo_mm)


def _redondear_abajo(valor: float, paso: float) -> float:
    return math.floor((valor + 1e-9) / paso) * paso


def _minimo_normativo(minimos: dict[str, float]) -> tuple[float, str]:
    etiquetas = {
        "temperatura_E060_cm2_m": "retracción y temperatura E.060",
        "min_flexion_E060_cm2_m": "mínimo de flexión E.060",
        "temperatura_MTC_cm2_m": "retracción y temperatura MTC",
    }
    clave = max(minimos, key=minimos.get)
    return minimos[clave], etiquetas[clave]


def seleccionar_refuerzo_vertical(
    mu_tf_m: float,
    ms_tf_m: float,
    recubrimiento_mm: float,
    p: Parametros,
) -> dict:
    limite_general = limite_espaciamiento_general_mm(p)
    limite_fs = 0.60 * p.fy_kgf_cm2 * KGF_CM2_A_MPA
    for barra in p.barras_verticales:
        db = BARRAS_INGLESAS_MM[barra]
        d = p.espesor_m * 1000.0 - recubrimiento_mm - db / 2.0
        minimos = minimos_por_cara(p, d)
        as_norm, control_norm = _minimo_normativo(minimos)
        as_calc = acero_flexion_requerido_cm2_m(mu_tf_m, d, p)
        as_req = max(as_calc, as_norm)
        area_barra = area_barra_cm2(db)
        s_teorico = area_barra * 1000.0 / as_req
        s = _redondear_abajo(
            min(s_teorico, limite_general), p.paso_espaciamiento_mm
        )
        while s >= p.espaciamiento_minimo_mm - 1e-9:
            as_disp = acero_provisto_cm2_m(db, s)
            phi_mn = capacidad_flexion_tf_m(as_disp, d, p)
            fs = esfuerzo_acero_servicio_mpa(ms_tf_m, as_disp, d)
            s_fis = limite_fisuracion_mm(fs, recubrimiento_mm, db, p)
            cumple = (
                as_disp + 1e-9 >= as_req
                and phi_mn + 1e-9 >= mu_tf_m
                and fs <= limite_fs + 1e-9
                and s <= s_fis + 1e-9
            )
            if cumple:
                return {
                    "barra": barra,
                    "diametro_mm": db,
                    "espaciamiento_teorico_mm": s_teorico,
                    "espaciamiento_adoptado_mm": s,
                    "d_mm": d,
                    "As_flexion_requerido_cm2_m": as_calc,
                    **minimos,
                    "As_normativo_cm2_m": as_norm,
                    "control_normativo": control_norm,
                    "As_requerido_cm2_m": as_req,
                    "As_provisto_cm2_m": as_disp,
                    "DCR_area": as_req / as_disp,
                    "phi_Mn_tf_m_m": phi_mn,
                    "DCR_flexion": mu_tf_m / phi_mn,
                    "fs_servicio_MPa": fs,
                    "limite_fs_MPa": limite_fs,
                    "limite_separacion_fisuracion_mm": s_fis,
                    "fisuracion_cumple": True,
                    "cumple": True,
                }
            s -= p.paso_espaciamiento_mm
    raise ValueError(
        "Ninguna barra disponible satisface acero, flexión y fisuración vertical"
    )


def seleccionar_refuerzo_horizontal(as_req: float, p: Parametros) -> dict:
    limite_general = limite_espaciamiento_general_mm(p)
    for barra in p.barras_horizontales:
        db = BARRAS_INGLESAS_MM[barra]
        area_barra = area_barra_cm2(db)
        s_teorico = area_barra * 1000.0 / as_req
        if p.espaciamiento_horizontal_adoptado_mm is None:
            s = _redondear_abajo(
                min(s_teorico, limite_general), p.paso_espaciamiento_mm
            )
        else:
            s = p.espaciamiento_horizontal_adoptado_mm
        if s < p.espaciamiento_minimo_mm - 1e-9:
            continue
        as_disp = acero_provisto_cm2_m(db, s)
        cumple = (
            s <= limite_general + 1e-9
            and as_disp + 1e-9 >= as_req
        )
        if not cumple:
            continue
        return {
            "barra": barra,
            "diametro_mm": db,
            "espaciamiento_teorico_mm": s_teorico,
            "espaciamiento_adoptado_mm": s,
            "As_requerido_cm2_m": as_req,
            "As_provisto_cm2_m": as_disp,
            "DCR_area": as_req / as_disp,
            "cumple": True,
        }
    raise ValueError("Ninguna barra disponible satisface el acero horizontal")


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
    a_mm = p.brazo_br_m * 1000.0
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

    # Sentido sísmico inverso: se revisan las dos concurrencias MTC, no una
    # suma ad hoc con 100% PAE y 100% PIR simultáneos.
    axial_inverso = 0.90 * p.dc_tf_m + 0.65 * p.dw_tf_m
    inversos = construir_casos_inversos(p, casos, axial_inverso)
    inverso = max(inversos, key=lambda x: x.M_inverso_tf_m_m)

    # Demanda de tracción por cara:
    #   directo  (hacia el vacío)   -> cara posterior/relleno
    #   inverso  (hacia el relleno) -> cara frontal/no relleno
    demanda_por_cara = {
        "frontal/no relleno": max(inverso.M_inverso_tf_m_m, 0.0),
        "posterior/relleno": gobernante.M_tf_m_m,
    }
    direccion_por_cara = {
        "frontal/no relleno": "inverso (hacia el relleno)",
        "posterior/relleno": "directo (hacia el vacio)",
    }
    momento_envolvente = max(demanda_por_cara.values())
    V_gobernante = max(
        max(abs(x.V_tf_m) for x in resistentes),
        max(abs(x.V_inverso_tf_m) for x in inversos),
    )

    caras = []
    for nombre, rec in (
        ("frontal/no relleno", p.recubrimiento_frontal_mm),
        ("posterior/relleno", p.recubrimiento_relleno_mm),
    ):
        mu_cara = demanda_por_cara[nombre]
        diseno = seleccionar_refuerzo_vertical(
            mu_cara, servicio.M_tf_m_m, rec, p
        )
        caras.append({
            "cara": nombre,
            "recubrimiento_mm": rec,
            "momento_demanda_tf_m_m": mu_cara,
            "direccion_demanda": direccion_por_cara[nombre],
            **diseno,
        })

    min_horizontal = max(
        minimos_por_cara(p, min(x["d_mm"] for x in caras))["temperatura_E060_cm2_m"],
        minimos_por_cara(p, min(x["d_mm"] for x in caras))["temperatura_MTC_cm2_m"],
    )
    horizontal = seleccionar_refuerzo_horizontal(min_horizontal, p)
    vc = capacidades_cortante_tf(min(x["d_mm"] for x in caras), p)
    axial_mpa = gobernante.axial_tf_m * TF_A_KN * 1000.0 / (
        p.ancho_franja_m * 1000.0 * p.espesor_m * 1000.0
    )
    resultado = {
        "parametros": asdict(p),
        "fuente": "CALC-EST-2026-002-R00.md",
        "coeficientes": c,
        "casos": [asdict(x) for x in casos],
        "criterio_evento_extremo": {
            "norma": "Manual de Puentes MTC 2018",
            "articulo": "2.8.1.1.14.1",
            "concurrencia_I_A": "100% PAE + 50% PIR",
            "concurrencia_I_B": "max(50% PAE, PA) + 100% PIR",
            "criterio": "Se adopta la envolvente mas desfavorable",
            "eq_super": (
                "100% en ambas concurrencias; aplicada en la mesa de apoyo, "
                "a 0.70 m sobre la seccion de base"
            ),
        },
        "casos_inversos": [asdict(x) for x in inversos],
        "caso_inverso": asdict(inverso),
        "caso_gobernante": gobernante.nombre,
        "momento_gobernante_tf_m_m": gobernante.M_tf_m_m,
        "momento_diseno_envolvente_tf_m_m": momento_envolvente,
        "cortante_gobernante_tf_m": V_gobernante,
        "caras_verticales": caras,
        "horizontal": horizontal,
        "cortante": {
            **vc,
            "Vu_tf_m": V_gobernante,
            "DCR": V_gobernante / vc["adoptada_tf"],
        },
        "axial": {
            "Pu_tf_m": gobernante.axial_tf_m,
            "esfuerzo_promedio_MPa": axial_mpa,
            "relacion_P_Ag_fc": axial_mpa / (p.fc_kgf_cm2 * KGF_CM2_A_MPA),
            "nota": "No se acredita aumento de capacidad a flexion por compresion axial.",
        },
        "desplazamiento_servicio": desplazamiento_servicio_mm(p, c),
    }
    resultado["cumple_vertical"] = all(x["cumple"] for x in caras)
    resultado["cumple_cortante"] = resultado["cortante"]["DCR"] <= 1.0
    resultado["cumple_global"] = (
        resultado["cumple_vertical"]
        and resultado["horizontal"]["cumple"]
        and resultado["cumple_cortante"]
    )
    resultado["estado"] = "CUMPLE" if resultado["cumple_global"] else "NO_CUMPLE"
    return resultado


def _fmt(x: float, n: int = 3) -> str:
    return f"{x:.{n}f}"


def reporte_markdown(r: dict) -> str:
    p = r["parametros"]
    if p["espaciamiento_horizontal_adoptado_mm"] is None:
        criterio_horizontal = (
            f"El acero horizontal se selecciona entre {', '.join(p['barras_horizontales'])}."
        )
    else:
        criterio_horizontal = (
            f"Para el acero horizontal se adopta {', '.join(p['barras_horizontales'])} "
            f"@ {p['espaciamiento_horizontal_adoptado_mm']:.0f} mm."
        )
    if p["porcentaje_sismico_superestructura"] > 0:
        nota_eq = (
            "El resultado incluye la fuerza sismica de la superestructura al "
            "100% en ambas concurrencias, aplicada en la mesa de apoyo a "
            f"{p['brazo_eq_super_m']:.2f} m sobre la seccion de base analizada."
        )
    else:
        nota_eq = (
            "Escenario de sensibilidad sin transferencia de EQ-super a la "
            "pared. Solo es util si la ruta alternativa de esa fuerza queda "
            "demostrada mediante el detalle de apoyos, cajuela y contrafuertes."
        )
    lines = [
        "# Diseño normativo de la pared de cajuela en voladizo",
        "",
        "## Modelo",
        "",
        f"- Franja: 1.00 m; altura local: {p['altura_m']:.2f} m; altura global de empuje: {p['altura_global_empuje_m']:.2f} m; espesor: {p['espesor_m']:.2f} m.",
        f"- El acero vertical se selecciona entre {', '.join(p['barras_verticales'])}. {criterio_horizontal}",
        f"- La sección de análisis está en la base, inmediatamente debajo de la mesa de apoyo. BR se aplica con brazo de {p['brazo_br_m']:.2f} m y EQ-super con brazo de {p['brazo_eq_super_m']:.2f} m, medidos desde dicha sección.",
        "- La compresion axial del puente se cuantifica, pero no se acredita para aumentar la capacidad a flexion.",
        "- Evento Extremo I aplica las dos concurrencias del MTC 2018, Art. 2.8.1.1.14.1; I-A e I-B son etiquetas internas del calculo.",
        "- EQ-super se conserva al 100% en ambas concurrencias mientras no se demuestre una ruta de carga alternativa.",
        "",
        "## Criterios de diseño",
        "",
        "El acero requerido por cara se obtiene como la envolvente entre el acero calculado por flexión, el mínimo de flexión E.060 y los mínimos de retracción y temperatura E.060 y MTC:",
        "",
        "$$A_{s,req}=\\max(A_{s,calc},A_{s,min,E.060},A_{s,rt,E.060},A_{s,rt,MTC})$$",
        "",
        "Para cada barra disponible se determina el espaciamiento por área, se redondea hacia abajo al paso constructivo y se comprueban $A_{s,disp}\\ge A_{s,req}$, $M_u\\le\\phi M_n$, esfuerzo del acero y separación por fisuración. Se adopta además el menor límite general de espaciamiento aplicable.",
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
        f"Gobierna **{r['caso_gobernante']}**, con M_u = {_fmt(r['momento_gobernante_tf_m_m'])} tf·m/m (cara posterior/relleno).",
        "",
        "### Casos sísmicos inversos (inercia hacia el relleno)",
        "",
        "Para la cara frontal/no relleno también se evalúan I-A e I-B. La componente de terreno permanece hacia el vacío y las inercias PIR + EQ-super actúan hacia el relleno; un momento inverso positivo tracciona la cara frontal.",
        "",
        "| Caso | Terreno opuesto | M terreno | M(PIR) | M(EQ-super) | M inverso | V inverso |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for inv in r["casos_inversos"]:
        m_terreno = inv["M_Ea_tf_m_m"] + inv["M_Delta_Eas_tf_m_m"]
        lines.append(
            f"| {inv['nombre']} | {inv['componente_terreno']} | "
            f"{_fmt(m_terreno)} | {_fmt(inv['M_PIR_tf_m_m'])} | "
            f"{_fmt(inv['M_EQsuper_tf_m_m'])} | {_fmt(inv['M_inverso_tf_m_m'])} | "
            f"{_fmt(inv['V_inverso_tf_m'])} |"
        )
    lines += [
        "",
        "## Diseño del acero vertical por cara",
        "",
        "Cada cara se dimensiona para su demanda de tracción gobernante: la posterior/relleno con el caso directo y la frontal/no relleno con el caso inverso.",
        "",
        "| Cara | Caso/dirección | M_u | A_s,calc | A_s,norm | Control normativo | A_s,req | Refuerzo dispuesto | A_s,disp | D/C acero | φM_n | D/C flexión | Estado |",
        "|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for x in r["caras_verticales"]:
        lines.append(
            f"| {x['cara']} | {x['direccion_demanda']} | {_fmt(x['momento_demanda_tf_m_m'])} tf·m/m | {_fmt(x['As_flexion_requerido_cm2_m'])} cm²/m | {_fmt(x['As_normativo_cm2_m'])} cm²/m | {x['control_normativo']} | {_fmt(x['As_requerido_cm2_m'])} cm²/m | {x['barra']} @ {_fmt(x['espaciamiento_adoptado_mm'],0)} mm | {_fmt(x['As_provisto_cm2_m'])} cm²/m | {_fmt(x['DCR_area'])} | {_fmt(x['phi_Mn_tf_m_m'])} tf·m/m | {_fmt(x['DCR_flexion'])} | {'Cumple' if x['cumple'] else 'No cumple'} |"
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
            f"| {x['cara']} | {_fmt(x['fs_servicio_MPa'],1)} MPa | {_fmt(x['limite_fs_MPa'],1)} MPa | {_fmt(x['espaciamiento_adoptado_mm'],0)} mm | {_fmt(x['limite_separacion_fisuracion_mm'],0)} mm | {'Cumple' if x['fisuracion_cumple'] else 'No cumple'} |"
        )
    lines += [
        "",
        "La fisuración se verifica con Servicio I para el refuerzo finalmente dispuesto.",
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
        f"| Acero horizontal por cara | {_fmt(h['As_requerido_cm2_m'])} cm²/m | {h['barra']} @ {_fmt(h['espaciamiento_adoptado_mm'],0)} mm = {_fmt(h['As_provisto_cm2_m'])} cm²/m | {_fmt(h['DCR_area'])} | {'Cumple' if h['cumple'] else 'No cumple'} |",
        f"| Cortante | {_fmt(v['Vu_tf_m'])} tf/m | {_fmt(v['adoptada_tf'])} tf/m | {_fmt(v['DCR'])} | {'Cumple' if v['DCR'] <= 1 else 'No cumple'} |",
        f"| Compresion axial media | {_fmt(a['esfuerzo_promedio_MPa'])} MPa | f'c = {_fmt(p['fc_kgf_cm2']*KGF_CM2_A_MPA)} MPa | {_fmt(a['relacion_P_Ag_fc'])} | Informativo |",
        "",
        "## Armado normativo adoptado",
        "",
        *[
            f"- Acero vertical, cara {x['cara']}: {x['barra']} @ {_fmt(x['espaciamiento_adoptado_mm'],0)} mm."
            for x in r["caras_verticales"]
        ],
        f"- Acero horizontal, ambas caras: {h['barra']} @ {_fmt(h['espaciamiento_adoptado_mm'],0)} mm.",
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
    parser.add_argument("--altura", type=float, default=GEOM.c_cajuela + GEOM.d_cajuela)
    parser.add_argument(
        "--altura-global-empuje", type=float, default=GEOM.H,
        help="Altura global H_g del diagrama de Delta Eas (m)",
    )
    parser.add_argument("--espesor", type=float, default=0.40)
    parser.add_argument("--barras-verticales", nargs="+", default=['5/8"', '3/4"', '1"'])
    parser.add_argument("--barras-horizontales", nargs="+", default=['1/2"'])
    parser.add_argument("--espaciamiento-horizontal", type=float, default=300.0)
    parser.add_argument("--espaciamiento-minimo", type=float, default=100.0)
    parser.add_argument("--espaciamiento-maximo", type=float, default=400.0)
    parser.add_argument("--paso-espaciamiento", type=float, default=5.0)
    parser.add_argument("--brazo-br", type=float, default=None)
    parser.add_argument("--brazo-eq-super", type=float, default=None)
    parser.add_argument(
        "--altura-carga-puente", type=float, default=None,
        help="Opcion heredada: aplica el mismo brazo a BR y EQ-super",
    )
    parser.add_argument("--porcentaje-sismico-superestructura", type=float, default=0.24)
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).resolve().parents[2] / ".tmp" / "legacy" / "cajuela",
    )
    args = parser.parse_args()
    p = Parametros(
        altura_m=args.altura,
        altura_global_empuje_m=args.altura_global_empuje,
        espesor_m=args.espesor,
        barras_verticales=tuple(args.barras_verticales),
        barras_horizontales=tuple(args.barras_horizontales),
        espaciamiento_horizontal_adoptado_mm=args.espaciamiento_horizontal,
        espaciamiento_minimo_mm=args.espaciamiento_minimo,
        espaciamiento_maximo_mm=args.espaciamiento_maximo,
        paso_espaciamiento_mm=args.paso_espaciamiento,
        brazo_br_m=(
            args.brazo_br if args.brazo_br is not None
            else args.altura_carga_puente if args.altura_carga_puente is not None
            else 1.00
        ),
        brazo_eq_super_m=(
            args.brazo_eq_super if args.brazo_eq_super is not None
            else args.altura_carga_puente if args.altura_carga_puente is not None
            else 0.70
        ),
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

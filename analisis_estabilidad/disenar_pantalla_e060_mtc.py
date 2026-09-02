#!/usr/bin/env python3
"""Análisis matricial y diseño de la pantalla inferior del estribo.

La pantalla se idealiza como una viga continua desplegada en planta, apoyada
en los ejes de los contrafuertes. Se analizan tres franjas horizontales de
1.00 m de altura. Las acciones y combinaciones proceden del Manual de Puentes
MTC 2018/AASHTO LRFD y de ``agente_subestructura.py``; el diseño de concreto
armado se comprueba con la NTE E.060 y, complementariamente, con MTC/AASHTO.

Alcance deliberadamente excluido: cajuela, contrafuertes, alas como ménsulas
verticales, zapata, torsión espacial en los quiebres y cargas concentradas de
los apoyos de la superestructura.

Unidades internas: m, tf, tf/m, tf-m, kgf/cm2, MPa, mm y cm2/m.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Iterable


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.agente_subestructura import (  # noqa: E402
    GEOM as GEOM_BASE,
    MAT,
    SEISMIC,
    coulomb_active_coefficient,
    get_surcharge_height,
    mononobe_okabe_coefficient,
)


# =============================================================================
# DATOS EDITABLES
# =============================================================================

VANOS_M = (3.00, 3.00, 4.77, 2.80, 2.80, 4.77, 3.00, 3.00)
APOYOS_FRANJA = (
    "CF-I1", "CF-I2", "CF-I3", "CF-C1", "CF-C2",
    "CF-C3", "CF-D1", "CF-D2", "CF-D3",
)
ALTURA_TOTAL_PANTALLA_M = 13.15
ALTURA_EFECTIVA_M = 9.80
ESPESOR_PANTALLA_M = 0.40
ANCHO_FRANJA_M = 1.00
RECUBRIMIENTO_EXTERIOR_MM = 100.0
RECUBRIMIENTO_INTERIOR_MM = 75.0

BARRAS_INGLESAS_MM = {
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
}
BARRAS_DISPONIBLES = ('5/8"', '5/8"', '3/4"', '1"')
ESPACIAMIENTO_MINIMO_MM = 100.0
PASO_ESPACIAMIENTO_MM = 5.0

# La corrección cierra B1 + tp2 + B2 = 11.95 m sin alterar otros datos.
GEOM = replace(GEOM_BASE, B2=5.45)


TF_M_A_N_MM = 9.80665e6
KGF_CM2_A_MPA = 0.0980665
MPA_A_KSI = 0.1450377377
MM_POR_PULGADA = 25.4
CM2_M_POR_IN2_FT = 6.4516 / 0.3048


@dataclass(frozen=True)
class ParametrosPantalla:
    vanos_m: tuple[float, ...] = VANOS_M
    altura_total_m: float = ALTURA_TOTAL_PANTALLA_M
    altura_efectiva_m: float = ALTURA_EFECTIVA_M
    espesor_m: float = ESPESOR_PANTALLA_M
    ancho_franja_m: float = ANCHO_FRANJA_M
    recubrimiento_exterior_mm: float = RECUBRIMIENTO_EXTERIOR_MM
    recubrimiento_interior_mm: float = RECUBRIMIENTO_INTERIOR_MM
    barras_disponibles: tuple[str, ...] = BARRAS_DISPONIBLES
    espaciamiento_minimo_mm: float = ESPACIAMIENTO_MINIMO_MM
    paso_espaciamiento_mm: float = PASO_ESPACIAMIENTO_MM
    phi_flexion_e060: float = 0.90
    phi_cortante_e060: float = 0.85
    phi_flexion_mtc: float = 0.90
    phi_cortante_mtc: float = 0.90
    factor_exposicion_fisuracion: float = 1.00

    def validate(self) -> None:
        if len(self.vanos_m) < 1 or any(L <= 0 for L in self.vanos_m):
            raise ValueError("Todos los vanos deben ser positivos")
        if self.altura_total_m <= 0 or self.altura_efectiva_m <= 0:
            raise ValueError("Las alturas deben ser positivas")
        if self.altura_efectiva_m >= self.altura_total_m:
            raise ValueError("La pantalla efectiva debe excluir una zona superior")
        if self.espesor_m <= 0 or self.ancho_franja_m <= 0:
            raise ValueError("El espesor y el ancho de franja deben ser positivos")
        for nombre, recubrimiento in (
            ("exterior", self.recubrimiento_exterior_mm),
            ("interior", self.recubrimiento_interior_mm),
        ):
            if not 0 < recubrimiento < self.espesor_m * 1000 / 2:
                raise ValueError(
                    f"Recubrimiento {nombre} incompatible con el espesor"
                )
        if self.espaciamiento_minimo_mm <= 0 or self.paso_espaciamiento_mm <= 0:
            raise ValueError("Los espaciamientos deben ser positivos")
        faltantes = set(self.barras_disponibles) - set(BARRAS_INGLESAS_MM)
        if faltantes:
            raise ValueError(f"Barras desconocidas: {sorted(faltantes)}")


@dataclass
class ResultadoVano:
    indice: int
    longitud_m: float
    momento_izq_tf_m: float
    momento_der_tf_m: float
    cortante_izq_tf: float
    cortante_der_tf: float
    momento_max_tf_m: float
    x_momento_max_m: float
    momento_min_tf_m: float
    x_momento_min_m: float


@dataclass
class ResultadoViga:
    carga_tf_m: float
    nodos_m: list[float]
    giros_rad: list[float]
    reacciones_tf: list[float]
    vanos: list[ResultadoVano]
    carga_total_tf: float
    suma_reacciones_tf: float
    error_fuerza_tf: float
    error_momento_tf_m: float


@dataclass
class ResultadoFranjaCaso:
    franja: str
    altura_sobre_zapata_m: float
    profundidad_m: float
    caso: str
    escenario: str
    presion_eh_tf_m2: float
    presion_ls_tf_m2: float
    presion_ae_tf_m2: float
    presion_ir_tf_m2: float
    presion_diseno_tf_m2: float
    viga: ResultadoViga


@dataclass
class RefuerzoCara:
    franja: str
    cara: str
    signo: str
    recubrimiento_mm: float
    peralte_efectivo_mm: float
    caso_gobernante: str
    Mu_tf_m: float
    Ms_servicio_tf_m: float
    As_flexion_e060_cm2_m: float
    As_min_flexion_e060_cm2_m: float
    As_temp_e060_cara_cm2_m: float
    As_min_mtc_cm2_m: float
    As_temp_mtc_cara_cm2_m: float
    As_requerido_cm2_m: float
    norma_gobernante_acero: str
    barra: str
    diametro_mm: float
    espaciamiento_mm: float
    As_provisto_cm2_m: float
    phi_Mn_tf_m: float
    DCR_flexion: float
    fs_servicio_mpa: float
    limite_fs_servicio_mpa: float
    separacion_fisuracion_mtc_mm: float
    fisuracion_cumple: bool
    ld_e060_mm: float
    ld_mtc_mm: float
    ld_adoptado_mm: float
    norma_gobernante_desarrollo: str
    traslape_clase_b_mm: float


@dataclass
class DisenoFranja:
    franja: str
    altura_sobre_zapata_m: float
    profundidad_m: float
    refuerzo: list[RefuerzoCara]
    Vu_tf: float
    caso_cortante: str
    phi_Vc_e060_tf: float
    phi_Vc_mtc_tf: float
    phi_Vc_diseno_tf: float
    norma_gobernante_cortante: str
    DCR_cortante: float
    cortante_cumple: bool


def _resolver_sistema(A: list[list[float]], b: list[float]) -> list[float]:
    """Eliminación gaussiana con pivoteo parcial, sin dependencias externas."""
    n = len(b)
    if len(A) != n or any(len(fila) != n for fila in A):
        raise ValueError("El sistema lineal debe ser cuadrado")
    aug = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    for k in range(n):
        piv = max(range(k, n), key=lambda i: abs(aug[i][k]))
        if abs(aug[piv][k]) < 1e-14:
            raise ValueError("Matriz singular: revise apoyos, vanos y rigideces")
        aug[k], aug[piv] = aug[piv], aug[k]
        for i in range(k + 1, n):
            factor = aug[i][k] / aug[k][k]
            if factor == 0:
                continue
            for j in range(k, n + 1):
                aug[i][j] -= factor * aug[k][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (aug[i][n] - sum(aug[i][j] * x[j] for j in range(i + 1, n))) / aug[i][i]
    return x


def _matriz_elemento(EI: float, L: float) -> list[list[float]]:
    f = EI / L**3
    return [
        [12*f, 6*L*f, -12*f, 6*L*f],
        [6*L*f, 4*L**2*f, -6*L*f, 2*L**2*f],
        [-12*f, -6*L*f, 12*f, -6*L*f],
        [6*L*f, 2*L**2*f, -6*L*f, 4*L**2*f],
    ]


def _carga_elemento_uniforme(w: float, L: float) -> list[float]:
    """Carga nodal consistente; desplazamiento positivo hacia arriba."""
    return [-w*L/2, -w*L**2/12, -w*L/2, w*L**2/12]


def _mat_vec(A: list[list[float]], x: list[float]) -> list[float]:
    return [sum(aij*xj for aij, xj in zip(fila, x)) for fila in A]


def analizar_viga_continua(vanos_m: Iterable[float], carga_tf_m: float,
                           EI_tf_m2: float = 1.0) -> ResultadoViga:
    """Resuelve una viga continua con apoyos verticales en todos sus nodos."""
    vanos = tuple(float(x) for x in vanos_m)
    if not vanos or any(L <= 0 for L in vanos):
        raise ValueError("Se requiere al menos un vano positivo")
    if carga_tf_m < 0 or EI_tf_m2 <= 0:
        raise ValueError("La carga debe ser no negativa y EI positivo")

    n_nodos = len(vanos) + 1
    ndof = 2*n_nodos
    K = [[0.0]*ndof for _ in range(ndof)]
    F = [0.0]*ndof
    elementos: list[tuple[list[int], list[list[float]], list[float]]] = []
    for i, L in enumerate(vanos):
        dofs = [2*i, 2*i+1, 2*(i+1), 2*(i+1)+1]
        ke = _matriz_elemento(EI_tf_m2, L)
        fe = _carga_elemento_uniforme(carga_tf_m, L)
        elementos.append((dofs, ke, fe))
        for a, ga in enumerate(dofs):
            F[ga] += fe[a]
            for b, gb in enumerate(dofs):
                K[ga][gb] += ke[a][b]

    # Todos los desplazamientos verticales son nulos; los giros son libres.
    libres = [2*i+1 for i in range(n_nodos)]
    Kff = [[K[i][j] for j in libres] for i in libres]
    Ff = [F[i] for i in libres]
    theta = _resolver_sistema(Kff, Ff)
    d = [0.0]*ndof
    for dof, valor in zip(libres, theta):
        d[dof] = valor

    residuo = [sum(K[i][j]*d[j] for j in range(ndof)) - F[i] for i in range(ndof)]
    reacciones = [residuo[2*i] for i in range(n_nodos)]

    resultados_vanos: list[ResultadoVano] = []
    for i, (L, (dofs, ke, fe)) in enumerate(zip(vanos, elementos), 1):
        de = [d[j] for j in dofs]
        q = [a-b for a, b in zip(_mat_vec(ke, de), fe)]
        m_izq = -q[1]
        m_der = q[3]
        v_izq = q[0]
        v_der = -q[2]
        candidatos = [(0.0, m_izq), (L, m_der)]
        if carga_tf_m > 1e-14:
            xcrit = v_izq/carga_tf_m
            if 0 < xcrit < L:
                mcrit = m_izq + v_izq*xcrit - carga_tf_m*xcrit**2/2
                candidatos.append((xcrit, mcrit))
        x_max, m_max = max(candidatos, key=lambda par: par[1])
        x_min, m_min = min(candidatos, key=lambda par: par[1])
        resultados_vanos.append(ResultadoVano(
            indice=i,
            longitud_m=L,
            momento_izq_tf_m=m_izq,
            momento_der_tf_m=m_der,
            cortante_izq_tf=v_izq,
            cortante_der_tf=v_der,
            momento_max_tf_m=m_max,
            x_momento_max_m=x_max,
            momento_min_tf_m=m_min,
            x_momento_min_m=x_min,
        ))

    nodos = [0.0]
    for L in vanos:
        nodos.append(nodos[-1] + L)
    carga_total = carga_tf_m*sum(vanos)
    suma_reacciones = sum(reacciones)
    momento_cargas = carga_tf_m*sum(L*(x0+L/2) for x0, L in zip(nodos[:-1], vanos))
    momento_reacciones = sum(R*x for R, x in zip(reacciones, nodos))
    return ResultadoViga(
        carga_tf_m=carga_tf_m,
        nodos_m=nodos,
        giros_rad=theta,
        reacciones_tf=reacciones,
        vanos=resultados_vanos,
        carga_total_tf=carga_total,
        suma_reacciones_tf=suma_reacciones,
        error_fuerza_tf=suma_reacciones-carga_total,
        error_momento_tf_m=momento_reacciones-momento_cargas,
    )


def _modulo_elasticidad_e060_tf_m2() -> float:
    # E.060: Ec = 15000 sqrt(f'c), con f'c y Ec en kgf/cm2.
    return 15000.0*math.sqrt(MAT.f_c)*10.0


def _rigidez_franja(p: ParametrosPantalla) -> float:
    inercia = p.ancho_franja_m*p.espesor_m**3/12.0
    return _modulo_elasticidad_e060_tf_m2()*inercia


def niveles_franjas(p: ParametrosPantalla) -> list[tuple[str, float, float]]:
    alturas = (0.0, p.altura_efectiva_m/3.0, 2*p.altura_efectiva_m/3.0)
    nombres = ("Inferior", "Intermedia", "Superior")
    return [(nombre, y, p.altura_total_m-y) for nombre, y in zip(nombres, alturas)]


def coeficientes_presion(p: ParametrosPantalla) -> dict:
    ka = coulomb_active_coefficient(MAT.phi_relleno, MAT.delta)
    psi = math.degrees(math.atan2(SEISMIC.Kh, 1-SEISMIC.Kv))
    kae = mononobe_okabe_coefficient(
        MAT.phi_relleno, MAT.delta, psi,
    )
    # Las funciones del agente entregan la resultante de Coulomb. Para la
    # franja se usa su componente normal a una pared vertical.
    componente_normal = math.cos(math.radians(MAT.delta))
    return {
        "Ka_resultante": ka,
        "Kae_resultante": kae,
        "factor_normal": componente_normal,
        "Ka_normal": ka*componente_normal,
        "Kae_normal": kae*componente_normal,
        "angulo_sismico_grados": psi,
        "h_sobrecarga_m": get_surcharge_height(p.altura_total_m),
    }


def presiones_en_profundidad(profundidad_m: float,
                             p: ParametrosPantalla,
                             coef: dict | None = None) -> dict:
    if not 0 <= profundidad_m <= p.altura_total_m:
        raise ValueError("Profundidad fuera de la pantalla total")
    c = coef or coeficientes_presion(p)
    p_eh = MAT.gamma_r*c["Ka_normal"]*profundidad_m
    p_ls = MAT.gamma_r*c["Ka_normal"]*c["h_sobrecarga_m"]
    p_ae = MAT.gamma_r*(1-SEISMIC.Kv)*c["Kae_normal"]*profundidad_m
    p_ir = SEISMIC.Kh*MAT.gamma_c*p.espesor_m
    evento_a = p_ae + 0.5*p_ir
    evento_b = max(0.5*p_ae, p_eh) + p_ir
    return {
        "EH": p_eh,
        "LS": p_ls,
        "AE": p_ae,
        "IR": p_ir,
        "Servicio I": {"presion": p_eh+p_ls, "escenario": "EH + LS"},
        "Resistencia I-a": {
            "presion": 1.50*p_eh+1.75*p_ls,
            "escenario": "1.50 EH + 1.75 LS",
        },
        "Resistencia I-b": {
            "presion": 1.50*p_eh+1.75*p_ls,
            "escenario": "1.50 EH + 1.75 LS",
        },
        "Evento Extremo I-A": {
            "presion": evento_a,
            "escenario": "100% PAE + 50% PIR",
        },
        "Evento Extremo I-B": {
            "presion": evento_b,
            "escenario": "max(50% PAE, PA) + 100% PIR",
        },
        "Evento Extremo I": {
            "presion": max(evento_a, evento_b),
            "escenario": "A" if evento_a >= evento_b else "B",
        },
    }


def ejecutar_casos(p: ParametrosPantalla) -> tuple[dict, list[ResultadoFranjaCaso]]:
    coef = coeficientes_presion(p)
    EI = _rigidez_franja(p)
    resultados: list[ResultadoFranjaCaso] = []
    casos = ("Servicio I", "Resistencia I-a", "Resistencia I-b", "Evento Extremo I")
    for nombre, altura, profundidad in niveles_franjas(p):
        pres = presiones_en_profundidad(profundidad, p, coef)
        for caso in casos:
            carga = pres[caso]["presion"]*p.ancho_franja_m
            resultados.append(ResultadoFranjaCaso(
                franja=nombre,
                altura_sobre_zapata_m=altura,
                profundidad_m=profundidad,
                caso=caso,
                escenario=pres[caso]["escenario"],
                presion_eh_tf_m2=pres["EH"],
                presion_ls_tf_m2=pres["LS"],
                presion_ae_tf_m2=pres["AE"],
                presion_ir_tf_m2=pres["IR"],
                presion_diseno_tf_m2=pres[caso]["presion"],
                viga=analizar_viga_continua(p.vanos_m, carga, EI),
            ))
    return coef, resultados


def _as_flexion(Mu_tf_m: float, d_mm: float, phi: float) -> float:
    if Mu_tf_m <= 1e-12:
        return 0.0
    b_cm = 100.0
    d_cm = d_mm/10.0
    Mu_kg_cm = Mu_tf_m*100_000.0
    disc = d_cm**2 - 2*Mu_kg_cm/(phi*0.85*MAT.f_c*b_cm)
    if disc <= 0:
        raise ValueError("La sección de 0.40 m excede la flexión simple")
    a_cm = d_cm-math.sqrt(disc)
    return 0.85*MAT.f_c*b_cm*a_cm/MAT.fy


def _as_min_flexion_e060(d_mm: float) -> float:
    # E.060 10.5: expresión en kgf/cm2 y cm.
    return 0.70*math.sqrt(MAT.f_c)*100.0*(d_mm/10.0)/MAT.fy


def _as_temp_e060_cara(p: ParametrosPantalla) -> float:
    as_total = 0.0018*100.0*(p.espesor_m*100.0)
    return as_total/2.0


def _as_temp_mtc_cara(p: ParametrosPantalla) -> float:
    # MTC 2.9.1.4.5.8 / AASHTO 5.10.8, por cara y dirección.
    b_in = 12.0
    h_in = p.espesor_m*1000.0/MM_POR_PULGADA
    fy_ksi = MAT.fy*KGF_CM2_A_MPA*MPA_A_KSI
    as_in2_ft = 1.30*b_in*h_in/(2*(b_in+h_in)*fy_ksi)
    as_in2_ft = min(max(as_in2_ft, 0.11), 0.60)
    return as_in2_ft*CM2_M_POR_IN2_FT


def _momento_fisuracion_mtc(p: ParametrosPantalla) -> float:
    fc_mpa = MAT.f_c*KGF_CM2_A_MPA
    fr_mpa = 0.63*math.sqrt(fc_mpa)
    S_mm3 = (p.ancho_franja_m*1000.0)*(p.espesor_m*1000.0)**2/6.0
    return fr_mpa*S_mm3/TF_M_A_N_MM


def _as_min_mtc(Mu_tf_m: float, d_mm: float,
                p: ParametrosPantalla) -> tuple[float, float]:
    # MTC 2.9.1.4.4.2: sección monolítica no pretensada, A615 Grado 60.
    mcr = _momento_fisuracion_mtc(p)
    minimo_momento = min(1.33*Mu_tf_m, 0.67*1.60*mcr)
    objetivo = max(Mu_tf_m, minimo_momento)
    return _as_flexion(objetivo, d_mm, p.phi_flexion_mtc), objetivo


def _capacidad_flexion(As_cm2_m: float, d_mm: float, phi: float) -> float:
    b_cm = 100.0
    d_cm = d_mm/10.0
    a_cm = As_cm2_m*MAT.fy/(0.85*MAT.f_c*b_cm)
    Mn_kg_cm = As_cm2_m*MAT.fy*(d_cm-a_cm/2)
    return phi*Mn_kg_cm/100_000.0


def _capacidades_cortante(d_mm: float, p: ParametrosPantalla) -> tuple[float, float]:
    fc_mpa = MAT.f_c*KGF_CM2_A_MPA
    bw_mm = p.ancho_franja_m*1000.0
    vc_e060_n = 0.17*math.sqrt(fc_mpa)*bw_mm*d_mm
    # MTC/AASHTO, procedimiento simplificado para elemento no pretensado:
    # beta=2.0 y dv=max(0.9de, 0.72h).
    dv_mm = max(0.9*d_mm, 0.72*p.espesor_m*1000.0)
    vc_mtc_n = 0.083*2.0*math.sqrt(fc_mpa)*bw_mm*dv_mm
    return (
        p.phi_cortante_e060*vc_e060_n/9806.65,
        p.phi_cortante_mtc*vc_mtc_n/9806.65,
    )


def _esfuerzo_servicio(Ms_tf_m: float, As_cm2_m: float, d_mm: float) -> float:
    if Ms_tf_m <= 1e-12:
        return 0.0
    As_mm2 = As_cm2_m*100.0
    return Ms_tf_m*TF_M_A_N_MM/(As_mm2*0.90*d_mm)


def _limite_separacion_fisuracion(fs_mpa: float, db_mm: float,
                                  recubrimiento_mm: float,
                                  p: ParametrosPantalla) -> float:
    if fs_mpa <= 1e-12:
        return float("inf")
    # MTC 2.9.1.4.4.3 / AASHTO 5.7.3.4: la forma con coeficiente
    # 700 usa fss en ksi y dc, h, s en pulgadas. Se convierte el resultado
    # final a milímetros para evitar mezclar esa forma con unidades SI.
    dc_in = (recubrimiento_mm+db_mm/2)/MM_POR_PULGADA
    h_in = p.espesor_m*1000.0/MM_POR_PULGADA
    fs_ksi = fs_mpa*MPA_A_KSI
    beta_s = 1.0+dc_in/(0.7*(h_in-dc_in))
    s_in = 700.0*p.factor_exposicion_fisuracion/(beta_s*fs_ksi)-2.0*dc_in
    return s_in*MM_POR_PULGADA


def _limite_espaciamiento_general(p: ParametrosPantalla) -> float:
    e060 = min(3*p.espesor_m*1000.0, 400.0)
    mtc = min(1.5*p.espesor_m*1000.0, 450.0)
    return min(e060, mtc)


def _seleccionar_refuerzo(As_req: float, Ms_tf_m: float, d_mm: float,
                          recubrimiento_mm: float, p: ParametrosPantalla) -> dict:
    s_general = _limite_espaciamiento_general(p)
    for barra in p.barras_disponibles:
        db = BARRAS_INGLESAS_MM[barra]
        area_cm2 = math.pi*(db/10.0)**2/4.0
        s_por_area = area_cm2*1000.0/As_req
        s = math.floor(min(s_por_area, s_general)/p.paso_espaciamiento_mm)*p.paso_espaciamiento_mm
        while s >= p.espaciamiento_minimo_mm-1e-9:
            As_prov = area_cm2*1000.0/s
            fs = _esfuerzo_servicio(Ms_tf_m, As_prov, d_mm)
            s_fis = _limite_separacion_fisuracion(fs, db, recubrimiento_mm, p)
            if s <= s_fis+1e-9 and fs <= 0.60*MAT.fy*KGF_CM2_A_MPA+1e-9:
                return {
                    "barra": barra,
                    "diametro_mm": db,
                    "espaciamiento_mm": s,
                    "As_provisto_cm2_m": As_prov,
                    "fs_servicio_mpa": fs,
                    "separacion_fisuracion_mm": s_fis,
                }
            s -= p.paso_espaciamiento_mm
    raise ValueError("No hay barra/espaciamiento que satisfaga resistencia y fisuración")


def _ld_e060(db_mm: float) -> float:
    fc_mpa = MAT.f_c*KGF_CM2_A_MPA
    fy_mpa = MAT.fy*KGF_CM2_A_MPA
    denom = 2.6 if db_mm <= 19.05+1e-9 else 2.1
    # Factor superior 1.3 conservador para barras horizontales del muro.
    return max(fy_mpa*1.3/(denom*min(math.sqrt(fc_mpa), 8.3))*db_mm, 300.0)


def _ld_mtc(db_mm: float) -> float:
    # MTC 2.6.5.6.2.1.1 / AASHTO 5.11.2.1.1, sin reducciones.
    fy_ksi = MAT.fy*KGF_CM2_A_MPA*MPA_A_KSI
    fc_ksi = MAT.f_c*KGF_CM2_A_MPA*MPA_A_KSI
    db_in = db_mm/MM_POR_PULGADA
    ldb_in = 2.4*db_in*fy_ksi/math.sqrt(fc_ksi)
    return max(1.3*ldb_in*MM_POR_PULGADA, 12.0*MM_POR_PULGADA)


def _redondear_50(valor_mm: float) -> float:
    return math.ceil(valor_mm/50.0)*50.0


def _extremos_viga(viga: ResultadoViga) -> tuple[float, float, float]:
    max_pos = max(0.0, *(v.momento_max_tf_m for v in viga.vanos))
    min_neg = min(0.0, *(v.momento_min_tf_m for v in viga.vanos))
    max_v = max(abs(v.cortante_izq_tf) for v in viga.vanos)
    max_v = max(max_v, *(abs(v.cortante_der_tf) for v in viga.vanos))
    return max_pos, abs(min_neg), max_v


def generar_diagramas_momento(resultados: list[ResultadoFranjaCaso],
                               p: ParametrosPantalla,
                               subdivisiones_vano: int = 60) -> list[dict]:
    """Genera envolventes de momento de diseño a lo largo de la pantalla.

    El momento positivo tracciona la cara exterior/no relleno y el negativo
    tracciona la cara interior/relleno. Se incluyen los puntos críticos exactos
    de cada caso además de una discretización uniforme para dibujar las curvas.
    """
    if subdivisiones_vano < 2:
        raise ValueError("Se requieren al menos dos subdivisiones por vano")
    salida: list[dict] = []
    for nombre, altura, profundidad in niveles_franjas(p):
        grupo = [r for r in resultados
                 if r.franja == nombre and r.caso != "Servicio I"]
        puntos: list[dict] = []
        s0 = 0.0
        for iv, L in enumerate(p.vanos_m):
            x_locales = {L*k/subdivisiones_vano
                         for k in range(subdivisiones_vano+1)}
            for r in grupo:
                v = r.viga.vanos[iv]
                x_locales.add(v.x_momento_max_m)
                x_locales.add(v.x_momento_min_m)
            for x in sorted(x_locales):
                if iv > 0 and abs(x) < 1e-12:
                    continue
                candidatos: list[tuple[float, ResultadoFranjaCaso]] = []
                for r in grupo:
                    v = r.viga.vanos[iv]
                    momento = (
                        v.momento_izq_tf_m+v.cortante_izq_tf*x
                        -r.viga.carga_tf_m*x**2/2.0
                    )
                    candidatos.append((momento, r))
                m_pos, caso_pos = max(candidatos, key=lambda par: par[0])
                m_neg, caso_neg = min(candidatos, key=lambda par: par[0])
                puntos.append({
                    "s_m": s0+x,
                    "vano": iv+1,
                    "x_local_m": x,
                    "Mu_exterior_tf_m": max(0.0, m_pos),
                    "Mu_exterior_kN_m": max(0.0, m_pos)*9.80665,
                    "caso_exterior": caso_pos.caso,
                    "Mu_interior_tf_m": min(0.0, m_neg),
                    "Mu_interior_kN_m": min(0.0, m_neg)*9.80665,
                    "caso_interior": caso_neg.caso,
                })
            s0 += L
        max_pos = max(puntos, key=lambda x: x["Mu_exterior_tf_m"])
        min_neg = min(puntos, key=lambda x: x["Mu_interior_tf_m"])
        salida.append({
            "franja": nombre,
            "altura_sobre_zapata_m": altura,
            "profundidad_m": profundidad,
            "convencion": (
                "Momento positivo: cara exterior/no relleno; momento negativo: "
                "cara interior/relleno"
            ),
            "maximo_exterior": {
                "Mu_tf_m": max_pos["Mu_exterior_tf_m"],
                "Mu_kN_m": max_pos["Mu_exterior_kN_m"],
                "s_m": max_pos["s_m"],
                "caso": max_pos["caso_exterior"],
            },
            "maximo_interior": {
                "Mu_abs_tf_m": abs(min_neg["Mu_interior_tf_m"]),
                "Mu_abs_kN_m": abs(min_neg["Mu_interior_kN_m"]),
                "s_m": min_neg["s_m"],
                "caso": min_neg["caso_interior"],
            },
            "puntos": puntos,
        })
    return salida


def _disenar_cara(franja: str, cara: str, signo: str,
                  Mu: float, Ms: float, caso: str,
                  d_mm: float, recubrimiento_mm: float,
                  p: ParametrosPantalla) -> RefuerzoCara:
    as_e060 = _as_flexion(Mu, d_mm, p.phi_flexion_e060)
    as_min_e060 = _as_min_flexion_e060(d_mm)
    as_temp_e060 = _as_temp_e060_cara(p)
    as_mtc, _ = _as_min_mtc(Mu, d_mm, p)
    as_temp_mtc = _as_temp_mtc_cara(p)
    requisitos = {
        "flexión requerida E.060": as_e060,
        "mínimo de flexión E.060": as_min_e060,
        "temperatura E.060": as_temp_e060,
        "mínimo de flexión MTC/AASHTO": as_mtc,
        "temperatura MTC/AASHTO": as_temp_mtc,
    }
    norma_as, as_req = max(requisitos.items(), key=lambda item: item[1])
    sel = _seleccionar_refuerzo(as_req, Ms, d_mm, recubrimiento_mm, p)
    phi_mn_e060 = _capacidad_flexion(sel["As_provisto_cm2_m"], d_mm, p.phi_flexion_e060)
    phi_mn_mtc = _capacidad_flexion(sel["As_provisto_cm2_m"], d_mm, p.phi_flexion_mtc)
    phi_mn = min(phi_mn_e060, phi_mn_mtc)
    ld_e = _ld_e060(sel["diametro_mm"])
    ld_m = _ld_mtc(sel["diametro_mm"])
    ld = _redondear_50(max(ld_e, ld_m))
    return RefuerzoCara(
        franja=franja,
        cara=cara,
        signo=signo,
        recubrimiento_mm=recubrimiento_mm,
        peralte_efectivo_mm=d_mm,
        caso_gobernante=caso,
        Mu_tf_m=Mu,
        Ms_servicio_tf_m=Ms,
        As_flexion_e060_cm2_m=as_e060,
        As_min_flexion_e060_cm2_m=as_min_e060,
        As_temp_e060_cara_cm2_m=as_temp_e060,
        As_min_mtc_cm2_m=as_mtc,
        As_temp_mtc_cara_cm2_m=as_temp_mtc,
        As_requerido_cm2_m=as_req,
        norma_gobernante_acero=norma_as,
        barra=sel["barra"],
        diametro_mm=sel["diametro_mm"],
        espaciamiento_mm=sel["espaciamiento_mm"],
        As_provisto_cm2_m=sel["As_provisto_cm2_m"],
        phi_Mn_tf_m=phi_mn,
        DCR_flexion=Mu/phi_mn if phi_mn else float("inf"),
        fs_servicio_mpa=sel["fs_servicio_mpa"],
        limite_fs_servicio_mpa=0.60*MAT.fy*KGF_CM2_A_MPA,
        separacion_fisuracion_mtc_mm=sel["separacion_fisuracion_mm"],
        fisuracion_cumple=(
            sel["espaciamiento_mm"] <= sel["separacion_fisuracion_mm"]+1e-9
            and sel["fs_servicio_mpa"] <= 0.60*MAT.fy*KGF_CM2_A_MPA+1e-9
        ),
        ld_e060_mm=ld_e,
        ld_mtc_mm=ld_m,
        ld_adoptado_mm=ld,
        norma_gobernante_desarrollo=(
            "E.060" if ld_e >= ld_m else "MTC/AASHTO"
        ),
        traslape_clase_b_mm=_redondear_50(1.3*ld),
    )


def disenar_franjas(resultados: list[ResultadoFranjaCaso],
                     p: ParametrosPantalla) -> list[DisenoFranja]:
    db_control = max(BARRAS_INGLESAS_MM[b] for b in p.barras_disponibles)
    d_exterior_mm = p.espesor_m*1000.0-p.recubrimiento_exterior_mm-db_control/2
    d_interior_mm = p.espesor_m*1000.0-p.recubrimiento_interior_mm-db_control/2
    if min(d_exterior_mm, d_interior_mm) <= 0:
        raise ValueError("No existe peralte efectivo positivo")
    disenos: list[DisenoFranja] = []
    for nombre, altura, profundidad in niveles_franjas(p):
        grupo = [r for r in resultados if r.franja == nombre]
        servicio = next(r for r in grupo if r.caso == "Servicio I")
        ms_pos, ms_neg, _ = _extremos_viga(servicio.viga)
        resistencia = [r for r in grupo if r.caso != "Servicio I"]
        demandas = [(r, *_extremos_viga(r.viga)) for r in resistencia]
        gob_pos = max(demandas, key=lambda x: x[1])
        gob_neg = max(demandas, key=lambda x: x[2])
        gob_v = max(demandas, key=lambda x: x[3])
        ref_pos = _disenar_cara(
            nombre, "cara exterior/no relleno", "momento positivo",
            gob_pos[1], ms_pos, gob_pos[0].caso, d_exterior_mm,
            p.recubrimiento_exterior_mm, p,
        )
        ref_neg = _disenar_cara(
            nombre, "cara interior/relleno", "momento negativo",
            gob_neg[2], ms_neg, gob_neg[0].caso, d_interior_mm,
            p.recubrimiento_interior_mm, p,
        )
        # Se adopta el menor peralte efectivo para corte, independientemente
        # de la cara que quede traccionada en la sección crítica.
        vc_e, vc_m = _capacidades_cortante(min(d_exterior_mm, d_interior_mm), p)
        vc = min(vc_e, vc_m)
        disenos.append(DisenoFranja(
            franja=nombre,
            altura_sobre_zapata_m=altura,
            profundidad_m=profundidad,
            refuerzo=[ref_pos, ref_neg],
            Vu_tf=gob_v[3],
            caso_cortante=gob_v[0].caso,
            phi_Vc_e060_tf=vc_e,
            phi_Vc_mtc_tf=vc_m,
            phi_Vc_diseno_tf=vc,
            norma_gobernante_cortante=(
                "E.060" if vc_e <= vc_m else "MTC/AASHTO"
            ),
            DCR_cortante=gob_v[3]/vc,
            cortante_cumple=gob_v[3] <= vc,
        ))
    return disenos


def _refuerzo_vertical(p: ParametrosPantalla) -> dict:
    requerido_e060 = _as_temp_e060_cara(p)
    requerido_mtc = _as_temp_mtc_cara(p)
    requerido = max(requerido_e060, requerido_mtc)
    db_control = max(BARRAS_INGLESAS_MM[b] for b in p.barras_disponibles)
    d_mm = p.espesor_m*1000-p.recubrimiento_interior_mm-db_control/2
    sel = _seleccionar_refuerzo(
        requerido, 0.0, d_mm, p.recubrimiento_interior_mm, p
    )
    if math.isinf(sel["separacion_fisuracion_mm"]):
        sel["separacion_fisuracion_mm"] = None
    return {
        "direccion": "vertical, por cara",
        "As_E060_cm2_m": requerido_e060,
        "As_MTC_cm2_m": requerido_mtc,
        "As_requerido_cm2_m": requerido,
        **sel,
        "norma_gobernante": "E.060" if requerido_e060 >= requerido_mtc else "MTC/AASHTO",
    }


def _validaciones(p: ParametrosPantalla, resultados: list[ResultadoFranjaCaso],
                  disenos: list[DisenoFranja]) -> dict:
    profundidades = [x[2] for x in niveles_franjas(p)]
    ia = [r for r in resultados if r.caso == "Resistencia I-a"]
    ib = [r for r in resultados if r.caso == "Resistencia I-b"]
    error_eq = max(
        max(abs(r.viga.error_fuerza_tf), abs(r.viga.error_momento_tf_m))
        for r in resultados
    )
    error_sim = max(
        max(abs(a-b) for a, b in zip(r.viga.reacciones_tf, reversed(r.viga.reacciones_tf)))
        for r in resultados
    )
    return {
        "geometria_B_cierra": abs(GEOM.B1+GEOM.tp2+GEOM.B2-GEOM.B) < 1e-9,
        "profundidades_esperadas": all(
            abs(a-b) < 5e-4 for a, b in zip(profundidades, (13.15, 9.8833333333, 6.6166666667))
        ),
        "resistencia_Ia_Ib_separadas": len(ia) == 3 and len(ib) == 3,
        "resistencia_Ia_Ib_coinciden": all(
            abs(a.presion_diseno_tf_m2-b.presion_diseno_tf_m2) < 1e-12
            for a, b in zip(ia, ib)
        ),
        "equilibrio_matricial": error_eq < 1e-7,
        "max_error_equilibrio": error_eq,
        "simetria": error_sim < 1e-7,
        "max_error_simetria_reacciones": error_sim,
        "cajuela_excluida": abs(p.altura_total_m-p.altura_efectiva_m-3.35) < 1e-9,
        "flexion_cumple": all(a.DCR_flexion <= 1.0 for d in disenos for a in d.refuerzo),
        "cortante_cumple": all(d.cortante_cumple for d in disenos),
        "fisuracion_cumple": all(a.fisuracion_cumple for d in disenos for a in d.refuerzo),
    }


def calcular_diseno(p: ParametrosPantalla | None = None) -> dict:
    p = p or ParametrosPantalla()
    p.validate()
    coef, resultados = ejecutar_casos(p)
    disenos = disenar_franjas(resultados, p)
    diagramas = generar_diagramas_momento(resultados, p)
    vertical = _refuerzo_vertical(p)
    validaciones = _validaciones(p, resultados, disenos)
    db_control = max(BARRAS_INGLESAS_MM[b] for b in p.barras_disponibles)
    d_ext = p.espesor_m*1000-p.recubrimiento_exterior_mm-db_control/2
    d_int = p.espesor_m*1000-p.recubrimiento_interior_mm-db_control/2
    peraltes_efectivos = {
        "exterior_mm": d_ext,
        "interior_mm": d_int,
        "cortante_control_mm": min(d_ext, d_int),
    }
    return {
        "titulo": "Análisis matricial y diseño E.060-MTC de pantalla y alas",
        "normas": {
            "acciones": "Manual de Puentes MTC 2018 / AASHTO LRFD",
            "concreto": "NTE E.060 Concreto Armado, D.S. N.° 010-2009-VIVIENDA",
            "criterio": "se adopta el requisito más restrictivo",
        },
        "alcance": {
            "incluye": "pantalla inferior central y alas mediante tres franjas horizontales",
            "excluye": [
                "cajuela", "diseño de contrafuertes", "zapata",
                "torsión espacial en quiebres", "cargas concentradas de apoyos",
            ],
        },
        "parametros": asdict(p),
        "geometria_agente": {
            "B_m": GEOM.B, "B1_m": GEOM.B1, "tp2_m": GEOM.tp2,
            "B2_m": GEOM.B2, "cierre_m": GEOM.B1+GEOM.tp2+GEOM.B2,
        },
        "materiales": {
            "fc_kg_cm2": MAT.f_c, "fy_kg_cm2": MAT.fy,
            "gamma_relleno_tf_m3": MAT.gamma_r,
            "gamma_concreto_tf_m3": MAT.gamma_c,
            "phi_relleno_grados": MAT.phi_relleno,
            "delta_grados": MAT.delta,
        },
        "sismo": asdict(SEISMIC),
        "coeficientes_presion": coef,
        "niveles": [
            {"franja": n, "altura_sobre_zapata_m": y, "profundidad_m": z}
            for n, y, z in niveles_franjas(p)
        ],
        "peraltes_efectivos_control_mm": peraltes_efectivos,
        "resultados_por_caso": [asdict(r) for r in resultados],
        "diagramas_momento_diseno": diagramas,
        "diseno_por_franja": [asdict(d) for d in disenos],
        "refuerzo_vertical_distribucion": vertical,
        "validaciones": validaciones,
        "advertencias": [
            "El modelo 1D desplegado no representa torsión ni compatibilidad espacial en los quiebres de las alas.",
            "Los contrafuertes se consideran apoyos rígidos; las reacciones se reportan, pero no se diseñan.",
            "La presión se evalúa en el borde inferior de cada tercio, criterio conservador para zonificar el armado.",
            "El factor de barra superior 1.3 se aplica conservadoramente al desarrollo de todas las barras horizontales.",
            "La longitud disponible dentro de contrafuertes y anclajes debe verificarse con el plano definitivo.",
            "El diseño debe ser revisado y aprobado por el ingeniero responsable antes de construcción.",
        ],
    }

def generar_grafico_momentos(r: dict, ruta: Path) -> Path:
    """Dibuja los momentos de las tres franjas en la pantalla desplegada."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ruta.parent.mkdir(parents=True, exist_ok=True)
    vanos = r["parametros"]["vanos_m"]
    apoyos_s = [0.0]
    for L in vanos:
        apoyos_s.append(apoyos_s[-1]+L)

    fig, ejes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    for ax, d in zip(ejes, r["diagramas_momento_diseno"]):
        s = [x["s_m"] for x in d["puntos"]]
        m_ext = [x["Mu_exterior_tf_m"] for x in d["puntos"]]
        m_int = [x["Mu_interior_tf_m"] for x in d["puntos"]]
        ax.plot(s, m_ext, color="#1f77b4", lw=1.8,
                label="Cara exterior/no relleno (M+)")
        ax.fill_between(s, 0, m_ext, color="#1f77b4", alpha=.22)
        ax.plot(s, m_int, color="#d62728", lw=1.8,
                label="Cara interior/relleno (M−)")
        ax.fill_between(s, 0, m_int, color="#d62728", alpha=.22)
        for sa, etiqueta in zip(apoyos_s, APOYOS_FRANJA):
            ax.axvline(sa, color="0.42", lw=.7, ls="--", alpha=.75)
            if ax is ejes[0]:
                ax.annotate(
                    etiqueta, (sa, 1.0), xycoords=("data", "axes fraction"),
                    xytext=(2, -3), textcoords="offset points", rotation=90,
                    va="top", fontsize=7, color="0.3",
                )
        ep, ip = d["maximo_exterior"], d["maximo_interior"]
        ax.scatter([ep["s_m"]], [ep["Mu_tf_m"]],
                   color="#1f77b4", s=28, zorder=4)
        ax.scatter([ip["s_m"]], [-ip["Mu_abs_tf_m"]],
                   color="#d62728", s=28, zorder=4)
        ax.set_title(
            f"Franja {d['franja'].lower()} — z={d['altura_sobre_zapata_m']:.3f} m | "
            f"M+={ep['Mu_tf_m']:.3f} tf·m ({ep['caso']}); "
            f"|M−|={ip['Mu_abs_tf_m']:.3f} tf·m ({ip['caso']})",
            fontsize=10,
        )
        ax.set_ylabel("Mu (tf·m)")
        ax.axhline(0, color="black", lw=.75)
        ax.grid(True, alpha=.23)
        sec = ax.secondary_yaxis(
            "right", functions=(lambda y: y*9.80665, lambda y: y/9.80665),
        )
        sec.set_ylabel("Mu (kN·m)")
    ejes[0].legend(loc="lower right", fontsize=8)
    ejes[-1].set_xlabel("Coordenada desarrollada s (m)")
    fig.suptitle(
        "Diagramas de momento flector de diseño — modelo 1D desplegado\n"
        "Envolvente factorizada: exterior positiva e interior negativa",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(ruta, dpi=180)
    plt.close(fig)
    return ruta


def generar_resumen_texto(r: dict) -> str:
    """Resume en texto plano los resultados relevantes para la consola."""
    validaciones = r["validaciones"]
    claves_estado = (
        "equilibrio_matricial",
        "simetria",
        "flexion_cumple",
        "cortante_cumple",
        "fisuracion_cumple",
    )
    estado = "CUMPLE" if all(validaciones[clave] for clave in claves_estado) else "NO CUMPLE"
    lineas = [
        r["titulo"],
        f"Estado del modelo: {estado}",
        (
            "Equilibrio máximo: "
            f"{validaciones['max_error_equilibrio']:.3e} tf o tf·m"
        ),
        "",
        "Diseño por franja:",
    ]
    for diseno in r["diseno_por_franja"]:
        lineas.append(
            f"- {diseno['franja']}: Vu={diseno['Vu_tf']:.3f} tf; "
            f"D/C corte={diseno['DCR_cortante']:.3f} "
            f"({'cumple' if diseno['cortante_cumple'] else 'NO CUMPLE'})"
        )
        for acero in diseno["refuerzo"]:
            cara = "exterior" if "exterior" in acero["cara"] else "interior"
            lineas.append(
                f"  {cara}: Mu={acero['Mu_tf_m']:.3f} tf·m; "
                f"Ø{acero['barra']} @ {acero['espaciamiento_mm']:.0f} mm; "
                f"D/C flexión={acero['DCR_flexion']:.3f}"
            )
    vertical = r["refuerzo_vertical_distribucion"]
    lineas += [
        "",
        (
            "Refuerzo vertical por cara: "
            f"Ø{vertical['barra']} @ {vertical['espaciamiento_mm']:.0f} mm "
            f"(As={vertical['As_provisto_cm2_m']:.3f} cm²/m)"
        ),
        "Archivos opcionales: --salida-json RESULTADO.json y --salida-png MOMENTOS.png",
    ]
    return "\n".join(lineas)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida-json", type=Path)
    parser.add_argument("--salida-png", type=Path)
    parser.add_argument("--recubrimiento-exterior-mm", type=float,
                        default=RECUBRIMIENTO_EXTERIOR_MM)
    parser.add_argument("--recubrimiento-interior-mm", type=float,
                        default=RECUBRIMIENTO_INTERIOR_MM)
    parser.add_argument("--espesor-m", type=float, default=ESPESOR_PANTALLA_M)
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = parse_args()
    p = ParametrosPantalla(
        recubrimiento_exterior_mm=a.recubrimiento_exterior_mm,
        recubrimiento_interior_mm=a.recubrimiento_interior_mm,
        espesor_m=a.espesor_m,
    )
    resultado = calcular_diseno(p)
    print(generar_resumen_texto(resultado))
    if a.salida_json:
        a.salida_json.parent.mkdir(parents=True, exist_ok=True)
        a.salida_json.write_text(
            json.dumps(resultado, ensure_ascii=False, indent=2)+"\n",
            encoding="utf-8",
        )
    if a.salida_png:
        grafico = generar_grafico_momentos(resultado, a.salida_png)
        print(f"Gráfico: {grafico}")


if __name__ == "__main__":
    main()

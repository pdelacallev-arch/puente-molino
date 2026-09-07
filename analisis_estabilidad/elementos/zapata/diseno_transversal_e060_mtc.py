#!/usr/bin/env python3
"""Diseño transversal de una franja de zapata en el extremo del talón.

La franja de 1.00 m se extiende entre ``x=B-1`` y ``x=B`` y se modela,
en la dirección transversal desplegada, como una viga continua apoyada en
los nueve ejes de contrafuertes. Las presiones y los factores de las cargas
verticales se leen directamente de ``agente_subestructura.py``.

El armado final envuelve demanda, mínimos de flexión, contracción y
temperatura, distribución, fisuración, desarrollo, anclajes y empalmes según
NTE E.060 y Manual de Puentes MTC. Unidades internas: m, tf, tf/m, tf-m,
mm, MPa y cm2/m.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.elementos.estribo.estabilidad_global import (  # noqa: E402
    FALSE_FOOTING,
    GEOM,
    LOADS,
    MAT,
    SEISMIC,
    SubstructureAnalysis,
    get_surcharge_height,
)
from analisis_estabilidad.elementos.pantalla.diseno_e060_mtc import (  # noqa: E402
    analizar_viga_continua,
)


VANOS_M = (3.00, 3.00, 4.77, 2.80, 2.80, 4.77, 3.00, 3.00)
APOYOS = (
    "CF-I1", "CF-I2", "CF-I3", "CF-C1", "CF-C2",
    "CF-C3", "CF-D1", "CF-D2", "CF-D3",
)
CASOS = (
    "case_service_I",
    "case_resistance_Ia",
    "case_resistance_Ib",
    "case_extreme_event_I",
)
CASOS_RESISTENCIA = CASOS[1:]
INTERFAZ = "interface_1"

BARRAS_INGLESAS_MM = {
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
}

TF_M_A_N_MM = 9.80665e6
KGF_CM2_A_MPA = 0.0980665
MPA_A_KSI = 0.1450377377
MM_POR_PULGADA = 25.4


@dataclass(frozen=True)
class ParametrosZapataTransversal:
    vanos_m: tuple[float, ...] = VANOS_M
    ancho_franja_m: float = 1.00
    espesor_m: float = GEOM.hz
    recubrimiento_superior_mm: float = 100.0
    recubrimiento_inferior_mm: float = 100.0
    barras_disponibles: tuple[str, ...] = ('3/4"', '1"')
    espaciamiento_minimo_mm: float = 100.0
    espaciamiento_maximo_mm: float = 400.0
    paso_espaciamiento_mm: float = 10.0
    phi_flexion_e060: float = 0.90
    phi_cortante_e060: float = 0.85
    phi_flexion_mtc: float = 0.90
    phi_cortante_mtc: float = 0.90
    factor_exposicion_fisuracion: float = 1.00

    def validate(self) -> None:
        if len(self.vanos_m) != 8 or any(L <= 0 for L in self.vanos_m):
            raise ValueError("Se requieren los ocho vanos positivos del modelo desplegado")
        if not 0 < self.ancho_franja_m <= GEOM.B1:
            raise ValueError("El ancho de franja debe quedar dentro del talón")
        if self.espesor_m <= 0:
            raise ValueError("El espesor debe ser positivo")
        if any(not 0 < r < self.espesor_m*500 for r in (
            self.recubrimiento_superior_mm, self.recubrimiento_inferior_mm
        )):
            raise ValueError("Recubrimientos incompatibles con el espesor")
        if not 0 < self.espaciamiento_minimo_mm <= self.espaciamiento_maximo_mm:
            raise ValueError("Límites de espaciamiento inválidos")
        if self.paso_espaciamiento_mm <= 0:
            raise ValueError("El paso de espaciamiento debe ser positivo")
        if not self.barras_disponibles:
            raise ValueError("Debe existir al menos una barra disponible")
        if set(self.barras_disponibles) - set(BARRAS_INGLESAS_MM):
            raise ValueError("El catálogo contiene barras desconocidas")


@dataclass(frozen=True)
class CargaFranja:
    caso_clave: str
    caso: str
    x_inicio_m: float
    x_fin_m: float
    q_inicio_tf_m2: float
    q_talon_tf_m2: float
    q_media_tf_m2: float
    reaccion_bruta_tf_m: float
    peso_zapata_tf_m: float
    peso_relleno_tf_m: float
    sobrecarga_tf_m: float
    carga_descendente_tf_m: float
    carga_neta_ascendente_tf_m: float
    factores: dict[str, float]


def presion_lineal(q_punta: float, q_talon: float, x_m: float,
                   ancho_base_m: float = GEOM.B) -> float:
    if not 0 <= x_m <= ancho_base_m:
        raise ValueError("La coordenada está fuera de la base")
    return q_punta+(q_talon-q_punta)*x_m/ancho_base_m


def integrar_presion_lineal(q_punta: float, q_talon: float,
                            x_inicio_m: float, x_fin_m: float,
                            ancho_base_m: float = GEOM.B) -> float:
    """Integra q(x) dx y retorna tf/m transversal."""
    if not 0 <= x_inicio_m < x_fin_m <= ancho_base_m:
        raise ValueError("Intervalo de integración inválido")
    qa = presion_lineal(q_punta, q_talon, x_inicio_m, ancho_base_m)
    qb = presion_lineal(q_punta, q_talon, x_fin_m, ancho_base_m)
    return 0.5*(qa+qb)*(x_fin_m-x_inicio_m)


def _componente(caso: dict, descripcion: str) -> dict:
    encontrados = [x for x in caso["fv_detail"] if x["desc"] == descripcion]
    if len(encontrados) != 1:
        raise ValueError(
            f"Se esperaba una componente '{descripcion}' y se encontraron {len(encontrados)}"
        )
    return encontrados[0]


def calcular_carga_franja(caso_clave: str, caso: dict,
                          p: ParametrosZapataTransversal) -> CargaFranja:
    bearing = caso["bearing"]
    if bearing.get("contacto") != "COMPLETO":
        raise ValueError(f"{caso['name']}: el modelo lineal requiere contacto completo")
    q_punta = bearing.get("q_punta_t_m2")
    q_talon = bearing.get("q_talon_t_m2")
    if q_punta is None or q_talon is None:
        raise ValueError("La interfaz debe proporcionar q_punta y q_talon")

    x_fin = GEOM.B
    x_inicio = x_fin-p.ancho_franja_m
    reaccion = integrar_presion_lineal(q_punta, q_talon, x_inicio, x_fin)
    q_inicio = presion_lineal(q_punta, q_talon, x_inicio)

    zapata = _componente(caso, "Zapata")
    relleno = _componente(caso, "Relleno sobre talón")
    sobrecarga = _componente(caso, "Sobrecarga terreno")
    factores = {
        "DC_zapata": float(zapata["factor"]),
        "EV_relleno": float(relleno["factor"]),
        "LS_sobrecarga": float(sobrecarga["factor"]),
    }
    peso_zapata = factores["DC_zapata"]*MAT.gamma_c*GEOM.hz*p.ancho_franja_m
    # En el borde posterior el polígono de relleno alcanza la altura hp.
    peso_relleno = factores["EV_relleno"]*MAT.gamma_r*GEOM.hp*p.ancho_franja_m
    h_sc = get_surcharge_height(GEOM.H)
    peso_sc = factores["LS_sobrecarga"]*MAT.gamma_r*h_sc*p.ancho_franja_m
    descendente = peso_zapata+peso_relleno+peso_sc
    return CargaFranja(
        caso_clave=caso_clave,
        caso=caso["name"],
        x_inicio_m=x_inicio,
        x_fin_m=x_fin,
        q_inicio_tf_m2=q_inicio,
        q_talon_tf_m2=q_talon,
        q_media_tf_m2=reaccion/p.ancho_franja_m,
        reaccion_bruta_tf_m=reaccion,
        peso_zapata_tf_m=peso_zapata,
        peso_relleno_tf_m=peso_relleno,
        sobrecarga_tf_m=peso_sc,
        carga_descendente_tf_m=descendente,
        carga_neta_ascendente_tf_m=reaccion-descendente,
        factores=factores,
    )


def _rigidez(p: ParametrosZapataTransversal) -> float:
    ec_tf_m2 = 15000.0*math.sqrt(MAT.f_c)*10.0
    inercia = p.ancho_franja_m*p.espesor_m**3/12.0
    return ec_tf_m2*inercia


def analizar_carga_transversal(carga: CargaFranja,
                               p: ParametrosZapataTransversal) -> dict:
    """Resuelve la viga y transforma la convención a carga ascendente positiva."""
    w_up = carga.carga_neta_ascendente_tf_m
    if abs(w_up) < 1e-12:
        raise ValueError(f"{carga.caso}: carga neta nula")
    base = analizar_viga_continua(p.vanos_m, abs(w_up), _rigidez(p))
    # El solucionador usa carga descendente positiva. Una presión ascendente
    # invierte giros, reacciones, cortantes y momentos.
    signo = -1.0 if w_up > 0 else 1.0
    vanos = []
    for v in base.vanos:
        candidatos = [
            (0.0, signo*v.momento_izq_tf_m),
            (v.longitud_m, signo*v.momento_der_tf_m),
        ]
        # El extremo interior exacto se conserva después de invertir el signo.
        if 0 < v.x_momento_max_m < v.longitud_m:
            candidatos.append((v.x_momento_max_m, signo*v.momento_max_tf_m))
        if 0 < v.x_momento_min_m < v.longitud_m:
            candidatos.append((v.x_momento_min_m, signo*v.momento_min_tf_m))
        x_max, m_max = max(candidatos, key=lambda item: item[1])
        x_min, m_min = min(candidatos, key=lambda item: item[1])
        vanos.append({
            "indice": v.indice,
            "longitud_m": v.longitud_m,
            "momento_izq_tf_m": signo*v.momento_izq_tf_m,
            "momento_der_tf_m": signo*v.momento_der_tf_m,
            "cortante_izq_tf": signo*v.cortante_izq_tf,
            "cortante_der_tf": signo*v.cortante_der_tf,
            "momento_max_tf_m": m_max,
            "x_momento_max_m": x_max,
            "momento_min_tf_m": m_min,
            "x_momento_min_m": x_min,
        })
    reacciones = [signo*x for x in base.reacciones_tf]
    longitud = sum(p.vanos_m)
    # Fuerza ascendente positiva y reacción de apoyo positiva hacia arriba.
    error_f = sum(reacciones)+w_up*longitud
    nodos = base.nodos_m
    momento_carga = w_up*sum(
        L*(x0+L/2.0) for x0, L in zip(nodos[:-1], p.vanos_m)
    )
    error_m = sum(R*x for R, x in zip(reacciones, nodos))+momento_carga
    return {
        "caso_clave": carga.caso_clave,
        "caso": carga.caso,
        "carga_neta_ascendente_tf_m": w_up,
        "nodos_m": nodos,
        "giros_rad": [signo*x for x in base.giros_rad],
        "reacciones_verticales_tf": reacciones,
        "vanos": vanos,
        "error_fuerza_tf": error_f,
        "error_momento_tf_m": error_m,
    }


def momento_en(viga: dict, indice_vano: int, x_m: float) -> float:
    v = viga["vanos"][indice_vano]
    w_down = -viga["carga_neta_ascendente_tf_m"]
    return (
        v["momento_izq_tf_m"]+v["cortante_izq_tf"]*x_m
        -w_down*x_m*x_m/2.0
    )


def generar_envolventes(vigas: list[dict],
                         subdivisiones_vano: int = 80) -> dict:
    resistencia = [x for x in vigas if x["caso_clave"] in CASOS_RESISTENCIA]
    servicio = next(x for x in vigas if x["caso_clave"] == "case_service_I")
    puntos = []
    s0 = 0.0
    for i, L in enumerate(VANOS_M):
        xs = {L*j/subdivisiones_vano for j in range(subdivisiones_vano+1)}
        for r in resistencia:
            xs.add(r["vanos"][i]["x_momento_max_m"])
            xs.add(r["vanos"][i]["x_momento_min_m"])
        for x in sorted(xs):
            if i and abs(x) < 1e-12:
                continue
            candidatos = [(momento_en(r, i, x), r["caso"]) for r in resistencia]
            mmax, cmax = max(candidatos)
            mmin, cmin = min(candidatos)
            puntos.append({
                "s_m": s0+x, "vano": i+1, "x_local_m": x,
                "Mu_positivo_tf_m": max(0.0, mmax), "caso_positivo": cmax,
                "Mu_negativo_tf_m": min(0.0, mmin), "caso_negativo": cmin,
                "Ms_tf_m": momento_en(servicio, i, x),
            })
        s0 += L
    max_pos = max(puntos, key=lambda x: x["Mu_positivo_tf_m"])
    min_neg = min(puntos, key=lambda x: x["Mu_negativo_tf_m"])
    max_s_pos = max(puntos, key=lambda x: x["Ms_tf_m"])
    min_s_neg = min(puntos, key=lambda x: x["Ms_tf_m"])
    return {
        "convencion": (
            "M negativo: tracción superior; M positivo: tracción inferior. "
            "La ubicación en vanos o apoyos depende del signo de la carga neta."
        ),
        "maximo_positivo": {
            "Mu_tf_m": max_pos["Mu_positivo_tf_m"], "s_m": max_pos["s_m"],
            "caso": max_pos["caso_positivo"],
        },
        "maximo_negativo": {
            "Mu_abs_tf_m": abs(min_neg["Mu_negativo_tf_m"]), "s_m": min_neg["s_m"],
            "caso": min_neg["caso_negativo"],
        },
        "servicio_positivo": max(0.0, max_s_pos["Ms_tf_m"]),
        "servicio_negativo_abs": abs(min(0.0, min_s_neg["Ms_tf_m"])),
        "puntos": puntos,
    }


def _as_flexion(Mu_tf_m: float, d_mm: float, phi: float) -> float:
    if Mu_tf_m <= 1e-12:
        return 0.0
    b_cm = 100.0
    d_cm = d_mm/10.0
    mu_kg_cm = Mu_tf_m*100_000.0
    disc = d_cm**2-2.0*mu_kg_cm/(phi*0.85*MAT.f_c*b_cm)
    if disc <= 0:
        raise ValueError("La sección excede el dominio de flexión simple")
    a_cm = d_cm-math.sqrt(disc)
    return 0.85*MAT.f_c*b_cm*a_cm/MAT.fy


def _as_min_e060_cara(p: ParametrosZapataTransversal) -> float:
    """E.060 10.5.4: rho >= 0.0012 en la cara traccionada."""
    return 0.0012*100.0*(p.espesor_m*100.0)


def _as_temperatura_e060_total(p: ParametrosZapataTransversal) -> float:
    """E.060 9.7: rho=0.0018 para barras corrugadas fy>=420 MPa."""
    return 0.0018*100.0*(p.espesor_m*100.0)


def _momento_fisuracion_mtc(p: ParametrosZapataTransversal) -> float:
    fc_mpa = MAT.f_c*KGF_CM2_A_MPA
    fr_mpa = 0.63*math.sqrt(fc_mpa)
    modulo_mm3 = (p.ancho_franja_m*1000.0)*(p.espesor_m*1000.0)**2/6.0
    return fr_mpa*modulo_mm3/TF_M_A_N_MM


def _as_min_mtc(mu_tf_m: float, d_mm: float,
                p: ParametrosZapataTransversal) -> tuple[float, float]:
    """MTC 2.9.1.4.4.2: menor entre 1.33Mu y 0.67(1.6Mcr)."""
    mcr = _momento_fisuracion_mtc(p)
    momento_objetivo = min(1.33*mu_tf_m, 0.67*1.60*mcr)
    return _as_flexion(momento_objetivo, d_mm, p.phi_flexion_mtc), momento_objetivo


def _as_temperatura_mtc_cara(p: ParametrosZapataTransversal) -> float:
    """MTC 2.9.1.4.5.8, por cara y dirección, limitada a 0.11-0.60 in2/ft."""
    b_in = 12.0
    h_in = p.espesor_m*1000.0/MM_POR_PULGADA
    fy_ksi = MAT.fy*KGF_CM2_A_MPA*MPA_A_KSI
    as_in2_ft = 1.30*b_in*h_in/(2.0*(b_in+h_in)*fy_ksi)
    as_in2_ft = min(max(as_in2_ft, 0.11), 0.60)
    return as_in2_ft*(6.4516/0.3048)


def _capacidad_flexion(as_cm2_m: float, d_mm: float, phi: float) -> float:
    b_cm = 100.0
    d_cm = d_mm/10.0
    a_cm = as_cm2_m*MAT.fy/(0.85*MAT.f_c*b_cm)
    return phi*as_cm2_m*MAT.fy*(d_cm-a_cm/2.0)/100_000.0


def _esfuerzo_servicio(ms_tf_m: float, as_cm2_m: float, d_mm: float) -> float:
    if ms_tf_m <= 1e-12:
        return 0.0
    return ms_tf_m*TF_M_A_N_MM/(as_cm2_m*100.0*0.90*d_mm)


def _limite_fisuracion(fs_mpa: float, db_mm: float, rec_mm: float,
                       p: ParametrosZapataTransversal) -> float:
    if fs_mpa <= 1e-12:
        return float("inf")
    dc_in = (rec_mm+db_mm/2.0)/MM_POR_PULGADA
    h_in = p.espesor_m*1000.0/MM_POR_PULGADA
    beta_s = 1.0+dc_in/(0.7*(h_in-dc_in))
    fs_ksi = fs_mpa*MPA_A_KSI
    return (
        700.0*p.factor_exposicion_fisuracion/(beta_s*fs_ksi)-2.0*dc_in
    )*MM_POR_PULGADA


def _seleccionar_refuerzo(as_req: float, ms: float, d_mm: float, rec_mm: float,
                          p: ParametrosZapataTransversal) -> dict:
    if as_req <= 0:
        raise ValueError("El modelo no produjo demanda de acero en una de las caras")
    limite_temperatura_mtc = (
        300.0 if p.espesor_m*1000.0 > 18*MM_POR_PULGADA else 450.0
    )
    limite_general = min(
        p.espaciamiento_maximo_mm,
        3.0*p.espesor_m*1000.0,
        1.5*p.espesor_m*1000.0,
        450.0,
        limite_temperatura_mtc,
    )
    for barra in p.barras_disponibles:
        db = BARRAS_INGLESAS_MM[barra]
        area = math.pi*(db/10.0)**2/4.0
        s_area = area*1000.0/as_req
        s = math.floor(min(s_area, limite_general)/p.paso_espaciamiento_mm)*p.paso_espaciamiento_mm
        while s >= p.espaciamiento_minimo_mm-1e-9:
            as_prov = area*1000.0/s
            fs = _esfuerzo_servicio(ms, as_prov, d_mm)
            s_fis = _limite_fisuracion(fs, db, rec_mm, p)
            if s <= s_fis+1e-9 and fs <= 0.60*MAT.fy*KGF_CM2_A_MPA+1e-9:
                return {
                    "barra": barra, "diametro_mm": db,
                    "espaciamiento_mm": s, "As_provisto_cm2_m": as_prov,
                    "fs_servicio_mpa": fs,
                    "separacion_fisuracion_mtc_mm": s_fis,
                }
            s -= p.paso_espaciamiento_mm
    raise ValueError("No existe barra/espaciamiento que satisfaga resistencia y fisuración")


def _ld_e060(db_mm: float, cara: str) -> float:
    fc = MAT.f_c*KGF_CM2_A_MPA
    fy = MAT.fy*KGF_CM2_A_MPA
    denom = 2.6 if db_mm <= 19.05+1e-9 else 2.1
    psi_t = 1.3 if cara == "superior" else 1.0
    return max(fy*psi_t/(denom*min(math.sqrt(fc), 8.3))*db_mm, 300.0)


def _ld_mtc(db_mm: float, cara: str) -> float:
    fy_ksi = MAT.fy*KGF_CM2_A_MPA*MPA_A_KSI
    fc_ksi = MAT.f_c*KGF_CM2_A_MPA*MPA_A_KSI
    psi_t = 1.3 if cara == "superior" else 1.0
    ldb_in = 2.4*(db_mm/MM_POR_PULGADA)*fy_ksi/math.sqrt(fc_ksi)
    return max(psi_t*ldb_in*MM_POR_PULGADA, 12.0*MM_POR_PULGADA)


def _redondear_50(x: float) -> float:
    return math.ceil(x/50.0)*50.0


def _disenar_cara(cara: str, signo: str, mu: float, ms: float, caso: str,
                  rec_mm: float, p: ParametrosZapataTransversal) -> dict:
    db_control = max(BARRAS_INGLESAS_MM[x] for x in p.barras_disponibles)
    d_mm = p.espesor_m*1000.0-rec_mm-db_control/2.0
    as_e = _as_flexion(mu, d_mm, p.phi_flexion_e060)
    as_m_demanda = _as_flexion(mu, d_mm, p.phi_flexion_mtc)
    as_m_min, momento_min_mtc = _as_min_mtc(mu, d_mm, p)
    as_e_min = _as_min_e060_cara(p)
    as_e_temp_cara = _as_temperatura_e060_total(p)/2.0
    as_m_temp = _as_temperatura_mtc_cara(p)
    requisitos = {
        "flexión por demanda E.060": as_e,
        "flexión por demanda MTC": as_m_demanda,
        "mínimo cara traccionada E.060 10.5.4": as_e_min,
        "temperatura E.060 9.7, mitad del total": as_e_temp_cara,
        "mínimo flexión MTC 2.9.1.4.4.2": as_m_min,
        "temperatura MTC 2.9.1.4.5.8": as_m_temp,
    }
    criterio, as_req = max(requisitos.items(), key=lambda item: item[1])
    sel = _seleccionar_refuerzo(as_req, ms, d_mm, rec_mm, p)
    cap_e = _capacidad_flexion(sel["As_provisto_cm2_m"], d_mm, p.phi_flexion_e060)
    cap_m = _capacidad_flexion(sel["As_provisto_cm2_m"], d_mm, p.phi_flexion_mtc)
    ld_e = _ld_e060(sel["diametro_mm"], cara)
    ld_m = _ld_mtc(sel["diametro_mm"], cara)
    ld = _redondear_50(max(ld_e, ld_m))
    limite_fs = 0.60*MAT.fy*KGF_CM2_A_MPA
    return {
        "cara": cara, "signo": signo, "caso_gobernante": caso,
        "Mu_tf_m": mu, "Ms_servicio_tf_m": ms,
        "peralte_efectivo_mm": d_mm, "recubrimiento_mm": rec_mm,
        "As_flexion_E060_cm2_m": as_e,
        "As_flexion_MTC_cm2_m": as_m_demanda,
        "As_min_cara_E060_cm2_m": as_e_min,
        "As_temperatura_E060_cara_cm2_m": as_e_temp_cara,
        "As_min_flexion_MTC_cm2_m": as_m_min,
        "momento_minimo_MTC_tf_m": momento_min_mtc,
        "As_temperatura_MTC_cara_cm2_m": as_m_temp,
        "requisitos_acero_cm2_m": requisitos,
        "As_requerido_cm2_m": as_req,
        "criterio_acero": criterio,
        **sel,
        "phi_Mn_E060_tf_m": cap_e, "phi_Mn_MTC_tf_m": cap_m,
        "phi_Mn_diseno_tf_m": min(cap_e, cap_m),
        "DCR_flexion": mu/min(cap_e, cap_m),
        "limite_fs_servicio_mpa": limite_fs,
        "fisuracion_cumple": (
            sel["fs_servicio_mpa"] <= limite_fs+1e-9
            and sel["espaciamiento_mm"] <= sel["separacion_fisuracion_mtc_mm"]+1e-9
        ),
        "ld_E060_mm": ld_e, "ld_MTC_mm": ld_m, "ld_adoptado_mm": ld,
        "norma_gobernante_desarrollo": "E.060" if ld_e >= ld_m else "MTC/AASHTO",
        "traslape_clase_B_mm": _redondear_50(1.3*ld),
    }


def _disenar_distribucion(cara: str, rec_mm: float,
                          p: ParametrosZapataTransversal) -> dict:
    db_control = max(BARRAS_INGLESAS_MM[x] for x in p.barras_disponibles)
    d_mm = p.espesor_m*1000.0-rec_mm-db_control/2.0
    as_e = _as_temperatura_e060_total(p)/2.0
    as_m = _as_temperatura_mtc_cara(p)
    as_req = max(as_e, as_m)
    sel = _seleccionar_refuerzo(as_req, 0.0, d_mm, rec_mm, p)
    if math.isinf(sel["separacion_fisuracion_mtc_mm"]):
        sel["separacion_fisuracion_mtc_mm"] = None
    return {
        "direccion": "longitudinal, ortogonal a la franja transversal",
        "cara": cara,
        "As_temperatura_E060_cara_cm2_m": as_e,
        "As_temperatura_MTC_cara_cm2_m": as_m,
        "As_requerido_cm2_m": as_req,
        "criterio_acero": "E.060 9.7" if as_e >= as_m else "MTC 2.9.1.4.5.8",
        **sel,
    }


def _ldh_e060(db_mm: float) -> float:
    fc = MAT.f_c*KGF_CM2_A_MPA
    fy = MAT.fy*KGF_CM2_A_MPA
    return max(0.24*fy/math.sqrt(fc)*db_mm, min(8.0*db_mm, 150.0))


def _ldh_mtc(db_mm: float) -> float:
    fc_ksi = MAT.f_c*KGF_CM2_A_MPA*MPA_A_KSI
    db_in = db_mm/MM_POR_PULGADA
    return max(38.0*db_in/math.sqrt(fc_ksi), min(8.0*db_in, 6.0))*MM_POR_PULGADA


def _diametro_doblado(db_mm: float) -> float:
    return (6.0 if db_mm <= 25.4+1e-9 else 8.0)*db_mm


def _detallar_barra(acero: dict, cara: str,
                    p: ParametrosZapataTransversal) -> dict:
    db = acero["diametro_mm"]
    ld = acero.get("ld_adoptado_mm") or _redondear_50(
        max(_ld_e060(db, cara), _ld_mtc(db, cara))
    )
    relacion = acero["As_provisto_cm2_m"]/acero["As_requerido_cm2_m"]
    porcentaje = 50.0
    clase = "A" if relacion >= 2.0 and porcentaje <= 50.0 else "B"
    factor = 1.0 if clase == "A" else 1.3
    traslape = _redondear_50(factor*ld)
    ldh_e, ldh_m = _ldh_e060(db), _ldh_mtc(db)
    ldh = _redondear_50(max(ldh_e, ldh_m))
    extension = _redondear_50(12.0*db)
    disponible = p.espesor_m*1000.0-2.0*max(
        p.recubrimiento_superior_mm, p.recubrimiento_inferior_mm
    )
    return {
        "cara": cara, "barra": acero["barra"], "diametro_mm": db,
        "ld_recto_adoptado_mm": ld,
        "relacion_As_provisto_requerido": relacion,
        "porcentaje_maximo_empalmado": porcentaje,
        "clase_empalme": clase, "factor_empalme": factor,
        "traslape_requerido_mm": factor*ld,
        "traslape_adoptado_mm": traslape,
        "empalmes_escalonados": True,
        "separacion_centros_grupos_empalme_mm": 600.0,
        "ldh_E060_mm": ldh_e, "ldh_MTC_mm": ldh_m,
        "ldh_adoptado_mm": ldh,
        "gancho_estandar": "90 grados",
        "extension_recta_mm": extension,
        "diametro_interior_doblado_mm": _diametro_doblado(db),
        "espacio_vertical_disponible_mm": disponible,
        "gancho_cabe": disponible >= ldh,
        "anclaje_adoptado": (
            "desarrollo recto desde la sección crítica y gancho estándar "
            "de 90 grados en ambos extremos libres"
        ),
    }


def _zonas_traslape(detalle_superior: dict, detalle_inferior: dict) -> list[dict]:
    return [
        {
            "cara": "superior", "centros_s_m": [8.00, 18.80],
            "longitud_traslape_mm": detalle_superior["traslape_adoptado_mm"],
            "ubicacion": "interior de vanos con momento positivo",
            "grupos": "A/B alternados; centros separados 0.60 m",
            "longitud_comercial_maxima_m": 12.0,
        },
        {
            "cara": "inferior", "centros_s_m": [10.77, 16.37],
            "longitud_traslape_mm": detalle_inferior["traslape_adoptado_mm"],
            "ubicacion": "sobre CF-C1 y CF-C3, zonas de momento negativo",
            "grupos": "A/B alternados; centros separados 0.60 m",
            "longitud_comercial_maxima_m": 12.0,
        },
    ]


def _capacidades_cortante(d_mm: float, p: ParametrosZapataTransversal) -> tuple[float, float]:
    fc = MAT.f_c*KGF_CM2_A_MPA
    bw = p.ancho_franja_m*1000.0
    vc_e = 0.17*math.sqrt(fc)*bw*d_mm
    dv = max(0.9*d_mm, 0.72*p.espesor_m*1000.0)
    vc_m = 0.083*2.0*math.sqrt(fc)*bw*dv
    return (
        p.phi_cortante_e060*vc_e/9806.65,
        p.phi_cortante_mtc*vc_m/9806.65,
    )


def _resumen_acero(principal: list[dict], distribucion: list[dict]) -> list[dict]:
    """Consolida el armado con áreas, control normativo y D/C de acero."""
    resumen: list[dict] = []
    for acero in principal:
        as_calculado = max(
            acero["As_flexion_E060_cm2_m"],
            acero["As_flexion_MTC_cm2_m"],
        )
        as_normativo = max(
            acero["As_min_cara_E060_cm2_m"],
            acero["As_temperatura_E060_cara_cm2_m"],
            acero["As_min_flexion_MTC_cm2_m"],
            acero["As_temperatura_MTC_cara_cm2_m"],
        )
        as_requerido = acero["As_requerido_cm2_m"]
        as_dispuesto = acero["As_provisto_cm2_m"]
        resumen.append({
            "armado": f"Principal transversal — cara {acero['cara']}",
            "direccion": "transversal principal",
            "cara": acero["cara"],
            "caso_gobernante": acero["caso_gobernante"],
            "As_calculado_cm2_m": as_calculado,
            "As_normativo_cm2_m": as_normativo,
            "control_normativo": acero["criterio_acero"],
            "As_requerido_cm2_m": as_requerido,
            "barra": acero["barra"],
            "espaciamiento_adoptado_mm": acero["espaciamiento_mm"],
            "As_dispuesto_cm2_m": as_dispuesto,
            "DCR_acero": round(as_requerido/as_dispuesto, 3),
            "DCR_resistencia_flexion": round(acero["DCR_flexion"], 3),
            "cumple": as_dispuesto+1e-9 >= as_requerido,
        })
    for acero in distribucion:
        as_normativo = max(
            acero["As_temperatura_E060_cara_cm2_m"],
            acero["As_temperatura_MTC_cara_cm2_m"],
        )
        as_requerido = acero["As_requerido_cm2_m"]
        as_dispuesto = acero["As_provisto_cm2_m"]
        resumen.append({
            "armado": f"Distribución longitudinal — cara {acero['cara']}",
            "direccion": "longitudinal de distribución",
            "cara": acero["cara"],
            "caso_gobernante": None,
            "As_calculado_cm2_m": 0.0,
            "As_normativo_cm2_m": as_normativo,
            "control_normativo": acero["criterio_acero"],
            "As_requerido_cm2_m": as_requerido,
            "barra": acero["barra"],
            "espaciamiento_adoptado_mm": acero["espaciamiento_mm"],
            "As_dispuesto_cm2_m": as_dispuesto,
            "DCR_acero": round(as_requerido/as_dispuesto, 3),
            "DCR_resistencia_flexion": None,
            "cumple": as_dispuesto+1e-9 >= as_requerido,
        })
    return resumen


def disenar_seccion(envolvente: dict, vigas: list[dict],
                     p: ParametrosZapataTransversal) -> dict:
    sup = _disenar_cara(
        "superior", "momento negativo",
        envolvente["maximo_negativo"]["Mu_abs_tf_m"],
        envolvente["servicio_negativo_abs"],
        envolvente["maximo_negativo"]["caso"],
        p.recubrimiento_superior_mm, p,
    )
    inf = _disenar_cara(
        "inferior", "momento positivo",
        envolvente["maximo_positivo"]["Mu_tf_m"],
        envolvente["servicio_positivo"],
        envolvente["maximo_positivo"]["caso"],
        p.recubrimiento_inferior_mm, p,
    )
    resistencia = [v for v in vigas if v["caso_clave"] in CASOS_RESISTENCIA]
    demandas = []
    for v in resistencia:
        vmax = max(
            abs(x[k]) for x in v["vanos"]
            for k in ("cortante_izq_tf", "cortante_der_tf")
        )
        demandas.append((vmax, v["caso"]))
    vu, caso_v = max(demandas)
    d_control = min(sup["peralte_efectivo_mm"], inf["peralte_efectivo_mm"])
    vc_e, vc_m = _capacidades_cortante(d_control, p)
    vc = min(vc_e, vc_m)
    distribucion = [
        _disenar_distribucion("superior", p.recubrimiento_superior_mm, p),
        _disenar_distribucion("inferior", p.recubrimiento_inferior_mm, p),
    ]
    detalle_sup = _detallar_barra(sup, "superior", p)
    detalle_inf = _detallar_barra(inf, "inferior", p)
    resumen_acero = _resumen_acero([sup, inf], distribucion)
    return {
        "estado_armado": (
            "CUMPLE" if all(x["cumple"] for x in resumen_acero)
            else "NO CUMPLE"
        ),
        "resumen_acero": resumen_acero,
        "refuerzo_principal_transversal": [sup, inf],
        "refuerzo_distribucion_longitudinal": distribucion,
        "desarrollo_traslapes_ganchos": [detalle_sup, detalle_inf],
        "zonas_traslape": _zonas_traslape(detalle_sup, detalle_inf),
        "cortante": {
            "Vu_tf": vu, "caso_gobernante": caso_v,
            "phi_Vc_E060_tf": vc_e, "phi_Vc_MTC_tf": vc_m,
            "phi_Vc_diseno_tf": vc,
            "norma_gobernante": "E.060" if vc_e <= vc_m else "MTC/AASHTO",
            "DCR": vu/vc, "cumple": vu <= vc,
            "seccion_critica": "eje de apoyo; ancho de contrafuerte no confirmado",
        },
        "criterio_armado": (
            "envolvente de demanda, mínimos E.060/MTC, temperatura, "
            "distribución, fisuración, desarrollo, traslapes y ganchos"
        ),
    }


def calcular_diseno(
    p: ParametrosZapataTransversal | None = None,
    resultados_estabilidad: dict | None = None,
) -> dict:
    p = p or ParametrosZapataTransversal()
    p.validate()
    resultados_agente = resultados_estabilidad
    if resultados_agente is None:
        agente = SubstructureAnalysis(GEOM, MAT, LOADS, SEISMIC, FALSE_FOOTING)
        resultados_agente = agente.run_full_analysis()
    interfaz = resultados_agente.get("interfaces", {}).get(INTERFAZ)
    if interfaz is None:
        raise ValueError(f"El agente no produjo {INTERFAZ}")
    cargas = []
    vigas = []
    for clave in CASOS:
        caso = interfaz["cases"].get(clave)
        if caso is None:
            raise ValueError(f"Falta el caso {clave}")
        carga = calcular_carga_franja(clave, caso, p)
        cargas.append(carga)
        vigas.append(analizar_carga_transversal(carga, p))
    envolvente = generar_envolventes(vigas)
    diseno = disenar_seccion(envolvente, vigas, p)
    error_eq = max(
        max(abs(v["error_fuerza_tf"]), abs(v["error_momento_tf_m"]))
        for v in vigas
    )
    error_sim = max(
        max(abs(a-b) for a, b in zip(
            v["reacciones_verticales_tf"], reversed(v["reacciones_verticales_tf"])
        )) for v in vigas
    )
    validaciones = {
        "franja_en_extremo_talon": math.isclose(cargas[0].x_fin_m, GEOM.B),
        "ancho_franja_1m": math.isclose(p.ancho_franja_m, 1.0),
        "nueve_apoyos": len(APOYOS) == 9 and len(p.vanos_m) == 8,
        "contacto_completo_todos_casos": True,
        "cargas_netas_no_nulas": all(abs(c.carga_neta_ascendente_tf_m) > 1e-9 for c in cargas),
        "signo_carga_neta_reportado": True,
        "equilibrio_matricial": error_eq < 1e-7,
        "max_error_equilibrio": error_eq,
        "simetria": error_sim < 1e-7,
        "max_error_simetria": error_sim,
        "flexion_cumple": all(
            x["DCR_flexion"] <= 1 for x in diseno["refuerzo_principal_transversal"]
        ),
        "cortante_cumple": diseno["cortante"]["cumple"],
        "fisuracion_cumple": all(
            x["fisuracion_cumple"] for x in diseno["refuerzo_principal_transversal"]
        ),
        "minimos_y_temperatura_cumplen": all(
            x["As_provisto_cm2_m"]+1e-9 >= x["As_requerido_cm2_m"]
            for x in (
                diseno["refuerzo_principal_transversal"]
                + diseno["refuerzo_distribucion_longitudinal"]
            )
        ),
        "armado_reportado_cumple": all(
            x["cumple"] for x in diseno["resumen_acero"]
        ),
        "temperatura_total_E060_cumple": sum(
            x["As_provisto_cm2_m"] for x in diseno["refuerzo_principal_transversal"]
        )+1e-9 >= _as_temperatura_e060_total(p),
        "traslapes_definidos": all(
            x["traslape_adoptado_mm"] >= x["traslape_requerido_mm"]
            for x in diseno["desarrollo_traslapes_ganchos"]
        ),
        "ganchos_caben": all(
            x["gancho_cabe"] for x in diseno["desarrollo_traslapes_ganchos"]
        ),
    }
    return {
        "titulo": "Diseño transversal de la zapata en el extremo del talón — E.060 y MTC",
        "normas": {
            "cargas": "Manual de Puentes MTC 2018 / combinaciones del agente de subestructura",
            "concreto": "NTE E.060 y Manual de Puentes MTC 2018/AASHTO LRFD",
            "criterio": (
                "se adopta la envolvente de demanda, mínimos, temperatura, "
                "distribución, fisuración, desarrollo y empalmes"
            ),
        },
        "fuente_solicitaciones": f"agente_subestructura.py / {INTERFAZ}",
        "parametros": asdict(p),
        "geometria": {
            "B_m": GEOM.B, "B1_talon_m": GEOM.B1, "espesor_zapata_m": GEOM.hz,
            "x_inicio_franja_m": GEOM.B-p.ancho_franja_m,
            "x_fin_franja_m": GEOM.B,
            "longitud_desplegada_m": sum(p.vanos_m),
            "vanos_m": list(p.vanos_m), "apoyos": list(APOYOS),
        },
        "materiales": {
            "fc_kg_cm2": MAT.f_c, "fy_kg_cm2": MAT.fy,
            "gamma_concreto_tf_m3": MAT.gamma_c,
            "gamma_relleno_tf_m3": MAT.gamma_r,
        },
        "cargas_por_caso": [asdict(x) for x in cargas],
        "analisis_por_caso": vigas,
        "envolvente_momentos": envolvente,
        "diseno": diseno,
        "validaciones": validaciones,
        "limitaciones": [
            "Los contrafuertes se idealizan como apoyos rígidos ubicados en sus ejes.",
            "El ancho real de los contrafuertes no está confirmado; el cortante se reporta conservadoramente en el eje.",
            "No se evalúa punzonamiento ni la unión tridimensional contrafuerte–zapata.",
            "El armado calculado debe compatibilizarse con el acero longitudinal existente.",
            "El diseño requiere revisión y aprobación del ingeniero responsable antes de construcción.",
        ],
    }


def generar_markdown(r: dict) -> str:
    g, m, p = r["geometria"], r["materiales"], r["parametros"]
    lines = [
        "# Diseño transversal de la zapata en el extremo del talón — E.060 y MTC", "",
        "## 1. Objetivo y alcance", "",
        "Diseñar por flexión y cortante una franja transversal de 1.00 m situada en el extremo del talón, mediante una viga continua desplegada sobre los ejes de los contrafuertes.", "",
        "El armado final se obtiene envolviendo demanda, mínimos, temperatura, distribución, fisuración, desarrollo, empalmes y anclajes de E.060 y MTC.", "",
        "## 2. Datos e idealización", "",
        "| Dato | Valor | Unidad | Fuente |", "|---|---:|---|---|",
        f"| Ancho total B | {g['B_m']:.3f} | m | agente |",
        f"| Talón B1 | {g['B1_talon_m']:.3f} | m | agente |",
        f"| Franja x | {g['x_inicio_franja_m']:.3f} a {g['x_fin_franja_m']:.3f} | m | calculado |",
        f"| Espesor de zapata | {g['espesor_zapata_m']:.3f} | m | agente |",
        f"| Longitud desplegada | {g['longitud_desplegada_m']:.3f} | m | geometría de pantalla |",
        f"| Vanos | {', '.join(f'{x:.2f}' for x in g['vanos_m'])} | m | ejes de contrafuertes |",
        f"| f'c | {m['fc_kg_cm2']:.1f} | kgf/cm² | agente |",
        f"| fy | {m['fy_kg_cm2']:.1f} | kgf/cm² | agente |",
        f"| Recubrimiento superior/inferior | {p['recubrimiento_superior_mm']:.0f} / {p['recubrimiento_inferior_mm']:.0f} | mm | adoptado |", "",
        "La presión de contacto se integra exactamente en el último metro del talón. De la reacción bruta se descuentan el peso local factorizado de la zapata, el relleno y la sobrecarga. Las fuerzas de pantalla y contrafuertes quedan representadas por las reacciones de los apoyos.", "",
        "## 3. Cargas de la franja", "",
        "| Caso | q inicio | q talón | q media | Reacción bruta | Zapata | Relleno | Sobrecarga | w neta ascendente |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in r["cargas_por_caso"]:
        lines.append(
            f"| {c['caso']} | {c['q_inicio_tf_m2']:.3f} | {c['q_talon_tf_m2']:.3f} | "
            f"{c['q_media_tf_m2']:.3f} | {c['reaccion_bruta_tf_m']:.3f} | "
            f"{c['peso_zapata_tf_m']:.3f} | {c['peso_relleno_tf_m']:.3f} | "
            f"{c['sobrecarga_tf_m']:.3f} | {c['carga_neta_ascendente_tf_m']:.3f} |"
        )
    lines += [
        "", "Todas las cargas de la tabla están expresadas en tf/m transversal.", "",
        "## 4. Análisis matricial", "",
        "La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.", "",
        "| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for v in r["analisis_por_caso"]:
        mp = max(0.0, *(x["momento_max_tf_m"] for x in v["vanos"]))
        mn = abs(min(0.0, *(x["momento_min_tf_m"] for x in v["vanos"])))
        vv = max(abs(x[k]) for x in v["vanos"] for k in ("cortante_izq_tf", "cortante_der_tf"))
        ee = max(abs(v["error_fuerza_tf"]), abs(v["error_momento_tf_m"]))
        lines.append(f"| {v['caso']} | {v['carga_neta_ascendente_tf_m']:.3f} | {mp:.3f} | {mn:.3f} | {vv:.3f} | {ee:.2e} |")
    lines += ["", "### Resultados por vano", "",
              "| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for v in r["analisis_por_caso"]:
        for x in v["vanos"]:
            lines.append(
                f"| {v['caso']} | {x['indice']} | {x['longitud_m']:.2f} | "
                f"{x['momento_izq_tf_m']:.3f} | {x['momento_der_tf_m']:.3f} | "
                f"{x['momento_max_tf_m']:.3f} | {x['momento_min_tf_m']:.3f} | "
                f"{x['cortante_izq_tf']:.3f} | {x['cortante_der_tf']:.3f} |"
            )
    e = r["envolvente_momentos"]
    lines += [
        "", "## 5. Envolvente de diseño", "",
        "| Demanda | Valor | Posición s | Caso | Cara traccionada |",
        "|---|---:|---:|---|---|",
        f"| M_u negativo | {e['maximo_negativo']['Mu_abs_tf_m']:.3f} tf·m | {e['maximo_negativo']['s_m']:.3f} m | {e['maximo_negativo']['caso']} | superior |",
        f"| M_u positivo | {e['maximo_positivo']['Mu_tf_m']:.3f} tf·m | {e['maximo_positivo']['s_m']:.3f} m | {e['maximo_positivo']['caso']} | inferior |",
        "", "## 6. Diseño E.060–MTC y armado final", "",
        f"**Estado del armado:** {r['diseno']['estado_armado']}.", "",
        "`As normativo` es la mayor exigencia no asociada directamente a la "
        "demanda de flexión entre E.060 y MTC. La relación D/C de acero es "
        "`As requerido / As dispuesto`, con `As requerido = máx(As calculado, "
        "As normativo)`.", "",
        "### Armado propuesto y verificación de áreas", "",
        "| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |",
        "|---|---|---:|---:|---|---:|---|---:|---:|:---:|",
    ]
    for a in r["diseno"]["resumen_acero"]:
        caso = a["caso_gobernante"] or "distribución"
        lines.append(
            f"| {a['armado']} | {caso} | "
            f"{a['As_calculado_cm2_m']:.3f} cm²/m | "
            f"{a['As_normativo_cm2_m']:.3f} cm²/m | "
            f"{a['control_normativo']} | "
            f"{a['As_requerido_cm2_m']:.3f} cm²/m | "
            f"Ø{a['barra']} @ {a['espaciamiento_adoptado_mm']:.0f} mm | "
            f"{a['As_dispuesto_cm2_m']:.3f} cm²/m | "
            f"{a['DCR_acero']:.3f} | {'Sí' if a['cumple'] else 'No'} |"
        )
    lines += [
        "", "### Comparación normativa detallada del refuerzo principal", "",
        "| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|",
    ]
    for a in r["diseno"]["refuerzo_principal_transversal"]:
        lines.append(
            f"| {a['cara']} | {a['Mu_tf_m']:.3f} | {max(a['As_flexion_E060_cm2_m'], a['As_flexion_MTC_cm2_m']):.3f} | "
            f"{a['As_min_cara_E060_cm2_m']:.3f} | {a['As_temperatura_E060_cara_cm2_m']:.3f} | "
            f"{a['As_min_flexion_MTC_cm2_m']:.3f} | {a['As_temperatura_MTC_cara_cm2_m']:.3f} | "
            f"{a['criterio_acero']} | {a['As_requerido_cm2_m']:.3f} | Ø{a['barra']} @ {a['espaciamiento_mm']:.0f} mm | "
            f"{a['As_provisto_cm2_m']:.3f} | {a['DCR_flexion']:.3f} |"
        )
    lines += [
        "", "### Acero longitudinal de distribución y temperatura", "",
        "| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |",
        "|---|---:|---:|---:|---|---|---:|",
    ]
    for a in r["diseno"]["refuerzo_distribucion_longitudinal"]:
        lines.append(
            f"| {a['cara']} | {a['As_temperatura_E060_cara_cm2_m']:.3f} | "
            f"{a['As_temperatura_MTC_cara_cm2_m']:.3f} | {a['As_requerido_cm2_m']:.3f} | "
            f"{a['criterio_acero']} | Ø{a['barra']} @ {a['espaciamiento_mm']:.0f} mm | "
            f"{a['As_provisto_cm2_m']:.3f} |"
        )
    c = r["diseno"]["cortante"]
    lines += [
        "", "### Cortante", "",
        "| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |",
        "|---|---:|---:|---:|---:|---|---:|---|",
        f"| {c['caso_gobernante']} | {c['Vu_tf']:.3f} | {c['phi_Vc_E060_tf']:.3f} | {c['phi_Vc_MTC_tf']:.3f} | {c['phi_Vc_diseno_tf']:.3f} | {c['norma_gobernante']} | {c['DCR']:.3f} | {'CUMPLE' if c['cumple'] else 'NO CUMPLE'} |",
        "", "### Desarrollo, traslapes y ganchos estándar", "",
        "| Cara | Barra | ld adoptado | Clase | Traslape | ldh E.060 | ldh MTC | ldh adoptado | Extensión 90° | Doblado interior |",
        "|---|---:|---:|:---:|---:|---:|---:|---:|---:|---:|",
    ]
    for a in r["diseno"]["desarrollo_traslapes_ganchos"]:
        lines.append(
            f"| {a['cara']} | Ø{a['barra']} | {a['ld_recto_adoptado_mm']:.0f} mm | {a['clase_empalme']} | "
            f"{a['traslape_adoptado_mm']:.0f} mm | {a['ldh_E060_mm']:.0f} mm | {a['ldh_MTC_mm']:.0f} mm | "
            f"{a['ldh_adoptado_mm']:.0f} mm | {a['extension_recta_mm']:.0f} mm | "
            f"{a['diametro_interior_doblado_mm']:.0f} mm |"
        )
    lines += ["", "### Zonas de empalme para barras comerciales de 12 m", ""]
    for z in r["diseno"]["zonas_traslape"]:
        centros = ", ".join(f"s={x:.2f} m" for x in z["centros_s_m"])
        lines.append(
            f"- Cara {z['cara']}: {centros}; {z['ubicacion']}; traslape "
            f"{z['longitud_traslape_mm']:.0f} mm; {z['grupos']}."
        )
    lines += ["", "## 7. Verificaciones automáticas", "",
              "| Verificación | Resultado |", "|---|---|"]
    for nombre, valor in r["validaciones"].items():
        mostrado = ("CONFORME" if valor else "NO CONFORME") if isinstance(valor, bool) else f"{valor:.3e}"
        lines.append(f"| {nombre.replace('_', ' ')} | {mostrado} |")
    estado = all(v for v in r["validaciones"].values() if isinstance(v, bool))
    lines += ["", "## 8. Limitaciones", ""]
    lines.extend(f"- {x}" for x in r["limitaciones"])
    lines += ["", "## 9. Conclusión", "",
              f"**Estado del análisis y diseño: {'CUMPLE' if estado else 'NO CUMPLE'}.**", ""]
    return "\n".join(lines)


def generar_grafico_cargas(r: dict, ruta: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    casos = [x["caso"].replace("Evento Extremo I (Sismo)", "Evento Extremo I") for x in r["cargas_por_caso"]]
    bruta = [x["reaccion_bruta_tf_m"] for x in r["cargas_por_caso"]]
    down = [x["carga_descendente_tf_m"] for x in r["cargas_por_caso"]]
    neta = [x["carga_neta_ascendente_tf_m"] for x in r["cargas_por_caso"]]
    x = list(range(len(casos)))
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ancho = 0.25
    ax.bar([i-ancho for i in x], bruta, ancho, label="Reacción bruta ↑", color="#1976d2")
    ax.bar(x, down, ancho, label="Cargas descendentes ↓", color="#ef6c00")
    ax.bar([i+ancho for i in x], neta, ancho, label="Carga neta (+↑ / −↓)", color="#2e7d32")
    ax.set_xticks(x, casos, rotation=12, ha="right")
    ax.set_ylabel("Carga lineal (tf/m transversal)")
    ax.set_title("FRANJA TRANSVERSAL DE 1 m EN EL EXTREMO DEL TALÓN")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=190)
    plt.close(fig)
    return ruta


def generar_grafico_momentos(r: dict, ruta: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    colores = ("#455a64", "#1565c0", "#ef6c00", "#6a1b9a")
    for v, color in zip(r["analisis_por_caso"], colores):
        ss, mm = [], []
        s0 = 0.0
        for i, L in enumerate(VANOS_M):
            for j in range(61):
                if i and j == 0:
                    continue
                xx = L*j/60.0
                ss.append(s0+xx)
                mm.append(momento_en(v, i, xx))
            s0 += L
        ax.plot(ss, mm, lw=1.6, color=color, label=v["caso"])
    for s, nombre in zip(r["analisis_por_caso"][0]["nodos_m"], APOYOS):
        ax.axvline(s, color="#9e9e9e", lw=0.6, alpha=0.6)
        ax.text(s, ax.get_ylim()[0] if ax.get_ylim()[0] else -1, nombre,
                rotation=90, va="bottom", ha="right", fontsize=7)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Coordenada desplegada s (m)")
    ax.set_ylabel("Momento físico (tf·m)")
    ax.set_title("DIAGRAMAS DE MOMENTO — ZAPATA TRANSVERSAL\nM−: tracción superior; M+: tracción inferior")
    ax.grid(alpha=0.22)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=190)
    plt.close(fig)
    return ruta


def _svg_detalle(r: dict) -> str:
    ref = {x["cara"]: x for x in r["diseno"]["refuerzo_principal_transversal"]}
    det = {x["cara"]: x for x in r["diseno"]["desarrollo_traslapes_ganchos"]}
    dist = {x["cara"]: x for x in r["diseno"]["refuerzo_distribucion_longitudinal"]}
    zonas = {x["cara"]: x for x in r["diseno"]["zonas_traslape"]}
    ancho, alto, margen = 1400, 650, 70
    escala = (ancho-2*margen)/sum(VANOS_M)
    nodos = [0.0]
    for L in VANOS_M:
        nodos.append(nodos[-1]+L)
    xnodes = [margen+x*escala for x in nodos]
    elems = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>.t{font:700 22px Arial}.s{font:14px Arial}.n{font:12px Arial}.sup{stroke:#c62828}.inf{stroke:#1565c0}</style>',
        '<text x="70" y="40" class="t">DETALLE DE ARMADO — FRANJA TRANSVERSAL DE ZAPATA EN EXTREMO DEL TALÓN</text>',
        f'<rect x="{margen}" y="150" width="{ancho-2*margen}" height="150" fill="#eeeeee" stroke="#424242" stroke-width="2"/>',
        f'<path d="M {margen} 245 L {margen} 178 L {ancho-margen} 178 L {ancho-margen} 245" fill="none" class="sup" stroke-width="5"/>',
        f'<path d="M {margen} 205 L {margen} 272 L {ancho-margen} 272 L {ancho-margen} 205" fill="none" class="inf" stroke-width="5"/>',
    ]
    for x, nombre in zip(xnodes, APOYOS):
        elems += [
            f'<polygon points="{x-10},320 {x+10},320 {x},300" fill="#555"/>',
            f'<line x1="{x}" y1="140" x2="{x}" y2="310" stroke="#777" stroke-dasharray="4 4"/>',
            f'<text x="{x}" y="345" class="n" text-anchor="middle">{nombre}</text>',
        ]
    for i, L in enumerate(VANOS_M):
        xm = (xnodes[i]+xnodes[i+1])/2
        elems.append(f'<text x="{xm}" y="375" class="n" text-anchor="middle">L={L:.2f} m</text>')
    for cara, y, color in (("superior", 178, "#ffcdd2"), ("inferior", 272, "#bbdefb")):
        z = zonas[cara]
        ancho_zona = z["longitud_traslape_mm"]/1000.0*escala
        for centro in z["centros_s_m"]:
            xx = margen+centro*escala-ancho_zona/2
            elems += [
                f'<rect x="{xx}" y="{y-12}" width="{ancho_zona}" height="24" fill="{color}" stroke="#555" stroke-dasharray="4 3"/>',
                f'<text x="{xx+ancho_zona/2}" y="{y-18}" class="n" text-anchor="middle">LAP {z["longitud_traslape_mm"]:.0f}</text>',
            ]
    elems += [
        f'<text x="70" y="430" class="s" fill="#c62828">SUPERIOR: Ø{ref["superior"]["barra"]} @ {ref["superior"]["espaciamiento_mm"]:.0f} mm; ld={ref["superior"]["ld_adoptado_mm"]:.0f}; lap {det["superior"]["clase_empalme"]}={det["superior"]["traslape_adoptado_mm"]:.0f} mm</text>',
        f'<text x="70" y="460" class="s" fill="#1565c0">INFERIOR: Ø{ref["inferior"]["barra"]} @ {ref["inferior"]["espaciamiento_mm"]:.0f} mm; ld={ref["inferior"]["ld_adoptado_mm"]:.0f}; lap {det["inferior"]["clase_empalme"]}={det["inferior"]["traslape_adoptado_mm"]:.0f} mm</text>',
        f'<text x="70" y="500" class="s">DISTRIBUCIÓN LONGITUDINAL: superior Ø{dist["superior"]["barra"]} @ {dist["superior"]["espaciamiento_mm"]:.0f} mm; inferior Ø{dist["inferior"]["barra"]} @ {dist["inferior"]["espaciamiento_mm"]:.0f} mm</text>',
        f'<text x="70" y="535" class="s">GANCHO 90° EN EXTREMOS: ldh={max(det["superior"]["ldh_adoptado_mm"], det["inferior"]["ldh_adoptado_mm"]):.0f} mm; extensión={det["superior"]["extension_recta_mm"]:.0f} mm; diámetro interior={det["superior"]["diametro_interior_doblado_mm"]:.0f} mm</text>',
        '<text x="70" y="570" class="n">Empalmar como máximo 50% por sección, en grupos A/B alternados y separados 0.60 m. Barras comerciales máximas: 12 m.</text>',
        '<text x="70" y="600" class="n">Coordinar el acero longitudinal con el diseño general de la zapata y verificar la geometría definitiva de contrafuertes.</text>',
        '</svg>',
    ]
    return "\n".join(elems)


def generar_detalle_armado(r: dict, ruta_svg: Path, ruta_png: Path) -> tuple[Path, Path]:
    ruta_svg.parent.mkdir(parents=True, exist_ok=True)
    ruta_svg.write_text(_svg_detalle(r), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ref = {x["cara"]: x for x in r["diseno"]["refuerzo_principal_transversal"]}
    det = {x["cara"]: x for x in r["diseno"]["desarrollo_traslapes_ganchos"]}
    dist = {x["cara"]: x for x in r["diseno"]["refuerzo_distribucion_longitudinal"]}
    zonas = {x["cara"]: x for x in r["diseno"]["zonas_traslape"]}
    nodos = [0.0]
    for L in VANOS_M:
        nodos.append(nodos[-1]+L)
    color_concreto = "#e5e7eb"
    color_borde = "#111827"
    color_superior = "#1d4ed8"
    color_inferior = "#dc2626"
    color_distribucion = "#059669"
    color_cota = "#374151"
    longitud = sum(VANOS_M)
    h = r["geometria"]["espesor_zapata_m"]
    rec = r["parametros"]["recubrimiento_superior_mm"]/1000.0

    def cota_h(x1: float, x2: float, y: float, texto: str,
               extension_y: float = 0.0) -> None:
        ax.annotate("", xy=(x1, y), xytext=(x2, y),
                    arrowprops=dict(arrowstyle="<->", color=color_cota, lw=0.8))
        ax.plot([x1, x1], [extension_y, y], color=color_cota, lw=0.5)
        ax.plot([x2, x2], [extension_y, y], color=color_cota, lw=0.5)
        ax.text((x1+x2)/2, y+0.10, texto, ha="center", va="bottom",
                fontsize=6.8, color=color_borde,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.35))

    def cota_v(x: float, y1: float, y2: float, texto: str,
               extension_x: float) -> None:
        ax.annotate("", xy=(x, y1), xytext=(x, y2),
                    arrowprops=dict(arrowstyle="<->", color=color_cota, lw=0.8))
        ax.plot([extension_x, x], [y1, y1], color=color_cota, lw=0.5)
        ax.plot([extension_x, x], [y2, y2], color=color_cota, lw=0.5)
        ax.text(x+0.10, (y1+y2)/2, texto, rotation=90, ha="left", va="center",
                fontsize=7, color=color_borde,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.35))

    # Formato panorámico: la longitud desplegada (27.14 m) es mucho mayor que
    # el peralte; así se conserva escala geométrica sin franjas blancas excesivas.
    fig, ax = plt.subplots(figsize=(18, 4.6))
    ax.add_patch(plt.Rectangle((0, 0), longitud, h, facecolor=color_concreto,
                               edgecolor=color_borde, linewidth=1.15, zorder=2))

    # Contrafuertes truncados, como la pantalla truncada del plano patrón.
    ancho_cf = 0.34
    for x, nombre in zip(nodos, APOYOS):
        x0 = min(max(x-ancho_cf/2, 0), longitud-ancho_cf)
        ax.add_patch(plt.Rectangle((x0, h), ancho_cf, 1.00,
                                   facecolor=color_concreto, edgecolor=color_borde,
                                   linewidth=0.85, zorder=2))
        ax.plot([x0, x0+ancho_cf], [h+0.78, h+0.86], color="white", lw=3.5, zorder=3)
        ax.plot([x0, x0+ancho_cf], [h+0.78, h+0.86], color=color_borde,
                lw=0.55, ls="--", zorder=4)
        ax.text(x, h+0.42, nombre, rotation=90, ha="center", va="center",
                fontsize=5.7, fontweight="bold", color=color_borde)

    y_sup, y_inf = h-rec-0.02, rec+0.02
    # Convención cromática idéntica al plano patrón: superior azul, inferior rojo.
    ax.plot([rec, longitud-rec], [y_sup, y_sup], color=color_superior, lw=2.2, zorder=10)
    ax.plot([rec, longitud-rec], [y_inf, y_inf], color=color_inferior, lw=2.2, zorder=10)
    ax.plot([rec, rec], [y_sup, y_sup-0.42], color=color_superior, lw=2.2, zorder=10)
    ax.plot([longitud-rec, longitud-rec], [y_sup, y_sup-0.42], color=color_superior, lw=2.2, zorder=10)
    ax.plot([rec, rec], [y_inf, y_inf+0.42], color=color_inferior, lw=2.2, zorder=10)
    ax.plot([longitud-rec, longitud-rec], [y_inf, y_inf+0.42], color=color_inferior, lw=2.2, zorder=10)

    # Acero longitudinal de distribución visto en corte.
    for y, cara in ((y_sup-0.02, "superior"), (y_inf+0.02, "inferior")):
        for x in [0.9, 4.5, 8.3, 12.0, 15.1, 18.8, 22.6, 26.2]:
            circ = plt.Circle((x, y), 0.055, facecolor="white",
                              edgecolor=color_distribucion, lw=1.3, zorder=12)
            ax.add_patch(circ)
            ax.plot([x-0.035, x+0.035], [y-0.035, y+0.035],
                    color=color_distribucion, lw=0.8, zorder=13)
        did = "D1" if cara == "superior" else "D2"
        ax.text(longitud+0.28, y,
                f'{did} Ø{dist[cara]["barra"]} @ {dist[cara]["espaciamiento_mm"]:.0f}',
                fontsize=7, va="center", color=color_distribucion)

    # Zonas de traslape, dibujadas como barras solapadas y llamadas técnicas.
    for cara, y, color, dy in (("superior", y_sup, color_superior, -0.30),
                               ("inferior", y_inf, color_inferior, 0.30)):
        z = zonas[cara]
        lap_m = z["longitud_traslape_mm"]/1000.0
        for j, centro in enumerate(z["centros_s_m"], start=1):
            x1, x2 = centro-lap_m/2, centro+lap_m/2
            ax.plot([x1, x2], [y+0.055, y+0.055], color=color, lw=1.1,
                    ls="--", zorder=11)
            ax.plot([x1, x2], [y-0.055, y-0.055], color=color, lw=1.1,
                    ls="--", zorder=11)
            ax.annotate(
                f'LAP-{cara[0].upper()}{j}  Clase {det[cara]["clase_empalme"]}\n'
                f'Ltr={z["longitud_traslape_mm"]:.0f} mm',
                xy=(centro, y), xytext=(centro+(0.45 if j == 1 else -1.45), y+dy),
                fontsize=6.4, fontweight="bold", color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=0.65),
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor=color, linewidth=0.6), zorder=25,
            )

    ax.annotate(
        f'T1  Ø{ref["superior"]["barra"]} @ {ref["superior"]["espaciamiento_mm"]:.0f} mm\n'
        f'ld={ref["superior"]["ld_adoptado_mm"]:.0f} mm',
        xy=(5.2, y_sup), xytext=(4.1, h-0.42), fontsize=7, fontweight="bold",
        color=color_superior, arrowprops=dict(arrowstyle="->", color=color_superior, lw=0.7),
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                  edgecolor=color_superior, linewidth=0.6), zorder=25,
    )
    ax.annotate(
        f'T2  Ø{ref["inferior"]["barra"]} @ {ref["inferior"]["espaciamiento_mm"]:.0f} mm\n'
        f'ld={ref["inferior"]["ld_adoptado_mm"]:.0f} mm',
        xy=(5.8, y_inf), xytext=(4.1, 0.40), fontsize=7, fontweight="bold",
        color=color_inferior, arrowprops=dict(arrowstyle="->", color=color_inferior, lw=0.7),
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                  edgecolor=color_inferior, linewidth=0.6), zorder=25,
    )

    # Cotas por vano y dimensión total desplegada.
    for i, (x1, x2, L) in enumerate(zip(nodos[:-1], nodos[1:], VANOS_M), start=1):
        cota_h(x1, x2, -0.50, f"V{i} = {L:.2f} m", 0)
    cota_h(0, longitud, -0.95, f"L DESPLEGADA = {longitud:.2f} m", 0)
    cota_v(longitud+1.18, 0, h, f"h = {h:.2f} m", longitud)
    cota_v(-0.58, rec, h-rec, f"rec. = {rec*1000:.0f} mm", 0)

    nota = (
        f'GANCHO 90° EN AMBOS EXTREMOS: ldh={max(det["superior"]["ldh_adoptado_mm"], det["inferior"]["ldh_adoptado_mm"]):.0f} mm; '
        f'extensión={det["superior"]["extension_recta_mm"]:.0f} mm; '
        f'Ø doblado interior={det["superior"]["diametro_interior_doblado_mm"]:.0f} mm.\n'
        'EMPALMES: máximo 50% por sección; alternar grupos A/B con desfase mínimo de 0.60 m.'
    )
    ax.text(0.25, 2.82, nota, ha="left", va="top", fontsize=6.7, color=color_borde,
            bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                      edgecolor=color_cota, linewidth=0.65))

    ax.set_xlim(-0.95, longitud+1.75)
    ax.set_ylim(-1.18, 3.05)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("SECCIÓN T–T  ·  ARMADURA TRANSVERSAL, EMPALMES Y ANCLAJES",
                 fontsize=10.5, fontweight="bold", loc="left")
    fig.tight_layout(pad=1.0)
    fig.savefig(ruta_svg, format="svg", bbox_inches="tight", pad_inches=0.10)
    fig.savefig(ruta_png, dpi=190, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    return ruta_svg, ruta_png


def escribir_entregables(r: dict, carpeta: Path) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = [
        carpeta/"diseno_zapata_transversal_e060_mtc.md",
        carpeta/"diseno_zapata_transversal_e060_mtc.json",
        carpeta/"cargas_zapata_transversal.png",
        carpeta/"diagramas_momento_zapata_transversal.png",
        carpeta/"detalle_armado_zapata_transversal.svg",
        carpeta/"detalle_armado_zapata_transversal.png",
    ]
    rutas[0].write_text(generar_markdown(r), encoding="utf-8")
    rutas[1].write_text(json.dumps(r, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    generar_grafico_cargas(r, rutas[2])
    generar_grafico_momentos(r, rutas[3])
    generar_detalle_armado(r, rutas[4], rutas[5])
    return rutas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--carpeta-salida", type=Path,
        default=Path(__file__).resolve().parents[2] / ".tmp" / "legacy" / "zapata" / "transversal",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    resultado = calcular_diseno()
    rutas = escribir_entregables(resultado, args.carpeta_salida)
    print(resultado["titulo"])
    for cara in resultado["diseno"]["refuerzo_principal_transversal"]:
        print(
            f"{cara['cara'].capitalize()}: Mu={cara['Mu_tf_m']:.3f} tf·m; "
            f"Ø{cara['barra']} @ {cara['espaciamiento_mm']:.0f} mm; "
            f"D/C={cara['DCR_flexion']:.3f}"
        )
    print(f"Cortante D/C={resultado['diseno']['cortante']['DCR']:.3f}")
    print("Entregables:")
    for ruta in rutas:
        print(f"- {ruta}")


if __name__ == "__main__":
    main()

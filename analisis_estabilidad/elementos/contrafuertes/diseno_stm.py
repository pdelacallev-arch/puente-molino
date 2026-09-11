#!/usr/bin/env python3
"""Diseño del armado común de los contrafuertes centrales mediante STM.

La demanda se lee exclusivamente del JSON producido por
``analizar_contrafuertes_centrales_2d.py``. No se recalculan las reacciones ni
el modelo FEM. El método principal es un modelo de bielas y tirantes (STM) y
las resultantes por cortes horizontales constituyen la comprobación estática
independiente.

Normativa adoptada:

* Manual de Puentes MTC 2018, 2.7.2.3.2 a 2.7.2.3.6;
* NTE E.060 (DS 010-2009-VIVIENDA) para mínimos, desarrollo y detallado.

Unidades internas: kN, m, mm y MPa. Este módulo dimensiona el contrafuerte;
la zapata y la pantalla sólo reciben las demandas locales de anclaje.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Iterable


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


RAIZ = Path(__file__).resolve().parents[2]
ENTRADA_PREDETERMINADA = (
    RAIZ / "historico" / "outputs_raiz" / "calc_est_2026_004"
    / "analisis_contrafuertes_centrales_2d.json"
)
SALIDA_PREDETERMINADA = RAIZ / ".tmp" / "legacy" / "contrafuertes" / "diseno_stm"

BARRAS_MM = {
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
}
# Disponibilidad comercial confirmada para el proyecto: no usar > 1 pulgada.
BARRAS_PRINCIPALES = ('1"',)
BARRAS_MALLA = ('1/2"', '5/8"', '3/4"')
CASOS_DISENO = (
    "Resistencia I-a", "Resistencia I-b",
    "Evento Extremo I-A", "Evento Extremo I-B",
)
CASO_SERVICIO = "Servicio I"
CONTRAFUERTES = ("CF-C1", "CF-C2", "CF-C3")


def _area_barra_mm2(designacion: str) -> float:
    db = BARRAS_MM[designacion]
    return math.pi * db**2 / 4.0


@dataclass(frozen=True)
class ParametrosDisenoContrafuertes:
    """Entradas editables del diseño; las acciones permanecen en el JSON."""

    altura_m: float = 7.85
    longitud_base_m: float = 6.50
    longitud_corona_m: float = 0.40
    espesor_m: float = 0.40
    recubrimiento_mm: float = 75.0
    fc_kg_cm2: float = 280.0
    fy_kg_cm2: float = 4200.0
    es_mpa: float = 200_000.0
    espesor_pantalla_m: float = 0.40
    espesor_zapata_m: float = 1.50
    anclaje_recto_base_disponible_mm: float | None = None
    anclaje_corona_disponible_mm: float | None = None
    longitud_empalme_disponible_mm: float = 2000.0
    barras_principales: tuple[str, ...] = BARRAS_PRINCIPALES
    barras_malla: tuple[str, ...] = BARRAS_MALLA
    barra_principal_forzada: str | None = None
    barra_malla_forzada: str | None = None
    paso_espaciamiento_mm: float = 10.0
    espaciamiento_minimo_mm: float = 100.0
    tamano_agregado_mm: float = 19.0
    maximo_capas_principales: int = 2
    phi_tirante: float = 0.90
    phi_compresion_stm: float = 0.70
    phi_cortante: float = 0.90
    phi_corte_friccion: float = 0.90
    mu_corte_friccion: float = 1.00
    factor_nodo_ccc: float = 0.85
    factor_nodo_cct: float = 0.75
    factor_nodo_ctt: float = 0.65
    rho_fisuracion_mtc_total: float = 0.003
    rho_temp_e060_total: float = 0.0018

    @property
    def fc_mpa(self) -> float:
        return self.fc_kg_cm2 * 0.0980665

    @property
    def fy_mpa(self) -> float:
        return self.fy_kg_cm2 * 0.0980665

    @property
    def pendiente_lomo(self) -> float:
        return (self.longitud_corona_m-self.longitud_base_m)/self.altura_m

    @property
    def angulo_tirante_rad(self) -> float:
        return math.atan(abs(self.pendiente_lomo))

    def longitud(self, z_m: float) -> float:
        return self.longitud_base_m + self.pendiente_lomo*z_m


def _validar_parametros(p: ParametrosDisenoContrafuertes) -> None:
    positivos = (
        p.altura_m, p.longitud_base_m, p.longitud_corona_m, p.espesor_m,
        p.recubrimiento_mm, p.fc_kg_cm2, p.fy_kg_cm2,
        p.espesor_pantalla_m, p.espesor_zapata_m,
        p.paso_espaciamiento_mm, p.espaciamiento_minimo_mm,
        p.maximo_capas_principales,
    )
    if any(x <= 0 for x in positivos):
        raise ValueError("Geometría, materiales y separaciones deben ser positivos")
    if p.longitud_corona_m >= p.longitud_base_m:
        raise ValueError("El lomo debe reducir su longitud hacia la corona")
    if 2*p.recubrimiento_mm >= p.espesor_m*1000:
        raise ValueError("El recubrimiento no deja espacio dentro del espesor")
    for catalogo in (p.barras_principales, p.barras_malla):
        if not catalogo or any(b not in BARRAS_MM for b in catalogo):
            raise ValueError("El catálogo contiene barras no reconocidas")
    if p.barra_principal_forzada not in (None, *p.barras_principales):
        raise ValueError("La barra principal forzada no pertenece al catálogo")
    if p.barra_malla_forzada not in (None, *p.barras_malla):
        raise ValueError("La barra de malla forzada no pertenece al catálogo")


def cargar_analisis(ruta: Path | str = ENTRADA_PREDETERMINADA) -> dict:
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el análisis requerido: {ruta}")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if datos.get("alcance", "").upper().startswith("ANALISIS") is False:
        raise ValueError("El archivo no identifica una etapa de análisis")
    casos = datos.get("casos", [])
    if len(casos) != 15:
        raise ValueError(f"Se esperaban 15 soluciones; se encontraron {len(casos)}")
    pares = {(x.get("contrafuerte"), x.get("caso")) for x in casos}
    esperados = {(cf, c) for cf in CONTRAFUERTES
                 for c in (*CASOS_DISENO, CASO_SERVICIO)}
    if pares != esperados:
        raise ValueError("El análisis no contiene los 3 contrafuertes y 5 casos esperados")
    return datos


def _interpolar_corte(cortes: list[dict], z_m: float, clave: str) -> float:
    if z_m <= cortes[0]["z_corte_m"]:
        return float(cortes[0][clave])
    if z_m >= cortes[-1]["z_corte_m"]:
        return float(cortes[-1][clave])
    for a, b in zip(cortes[:-1], cortes[1:]):
        if a["z_corte_m"] <= z_m <= b["z_corte_m"]:
            dz = b["z_corte_m"]-a["z_corte_m"]
            f = (z_m-a["z_corte_m"])/dz
            return float(a[clave]+f*(b[clave]-a[clave]))
    raise RuntimeError("No fue posible interpolar el corte")


def formar_envolventes(analisis: dict) -> dict:
    """Forma envolventes comunes y por contrafuerte sin alterar la demanda."""
    niveles = [float(z) for z in analisis["modelo"]["niveles_m"]]
    casos = analisis["casos"]

    def envolver(subconjunto: Iterable[dict], nombres: tuple[str, ...]) -> list[dict]:
        subconjunto = [x for x in subconjunto if x["caso"] in nombres]
        salida = []
        for z in niveles:
            candidatos = []
            for x in subconjunto:
                candidatos.append({
                    "contrafuerte": x["contrafuerte"], "caso": x["caso"],
                    "V_kN": _interpolar_corte(x["resultantes_por_corte"], z, "V_abs_kN"),
                    "M_kN_m": _interpolar_corte(x["resultantes_por_corte"], z, "M_abs_kN_m"),
                })
            gobierna_m = max(candidatos, key=lambda q: q["M_kN_m"])
            gobierna_v = max(candidatos, key=lambda q: q["V_kN"])
            salida.append({
                "z_m": z,
                "V_u_kN": gobierna_v["V_kN"],
                "M_u_kN_m": gobierna_m["M_kN_m"],
                "gobierna_V": f"{gobierna_v['contrafuerte']} / {gobierna_v['caso']}",
                "gobierna_M": f"{gobierna_m['contrafuerte']} / {gobierna_m['caso']}",
            })
        return salida

    por_cf = {}
    servicio_cf = {}
    for cf in CONTRAFUERTES:
        propios = [x for x in casos if x["contrafuerte"] == cf]
        por_cf[cf] = envolver(propios, CASOS_DISENO)
        servicio_cf[cf] = envolver(propios, (CASO_SERVICIO,))
    comun = envolver(casos, CASOS_DISENO)
    servicio = envolver(casos, (CASO_SERVICIO,))
    cubre = all(
        _interpolar_corte(x["resultantes_por_corte"], z, "V_abs_kN")
        <= comun[i]["V_u_kN"]+1e-9
        and _interpolar_corte(x["resultantes_por_corte"], z, "M_abs_kN_m")
        <= comun[i]["M_u_kN_m"]+1e-9
        for x in casos for i, z in enumerate(niveles)
    )
    return {
        "niveles_m": niveles,
        "comun_resistencia_evento": comun,
        "comun_servicio": servicio,
        "por_contrafuerte": por_cf,
        "servicio_por_contrafuerte": servicio_cf,
        "numero_resultados_cubiertos": len(casos),
        "cubre_15_resultados": cubre,
    }


def _valor_en_envolvente(envolvente: list[dict], z_m: float, clave: str) -> float:
    cortes = [{"z_corte_m": x["z_m"], clave: x[clave]} for x in envolvente]
    return _interpolar_corte(cortes, z_m, clave)


def _ejes_resistentes(z_m: float, db_mm: float,
                      desplazamiento_centroide_normal_mm: float,
                      p: ParametrosDisenoContrafuertes) -> dict:
    c_bar_m = (p.recubrimiento_mm+db_mm/2
               +desplazamiento_centroide_normal_mm)/1000.0
    # Una línea paralela al lomo separada c_bar en dirección normal presenta,
    # a igual z, este retiro horizontal.
    retiro_lomo_m = c_bar_m*math.sqrt(1+p.pendiente_lomo**2)
    x_t = p.longitud(z_m)-retiro_lomo_m
    x_c = (p.recubrimiento_mm+db_mm/2)/1000.0
    brazo = x_t-x_c
    if brazo <= 0:
        raise ValueError(f"No existe brazo interno positivo en z={z_m:.3f} m")
    return {
        "x_compresion_m": x_c,
        "x_tirante_m": x_t,
        "brazo_perpendicular_m": brazo,
        "retiro_normal_lomo_m": c_bar_m,
        "desplazamiento_centroide_capas_mm": desplazamiento_centroide_normal_mm,
    }


def equilibrio_stm(V_kN: float, M_kN_m: float, z_m: float, db_mm: float,
                    p: ParametrosDisenoContrafuertes,
                    desplazamiento_centroide_normal_mm: float = 0.0) -> dict:
    """Cierra el polígono de fuerzas de un corte con error numérico explícito.

    La componente vertical del tirante, ``Tz=M/j``, forma el par resistente con
    la resultante comprimida. La componente horizontal surge de la inclinación
    real del lomo. La biela es el vector de cierre junto al eje comprimido.
    """
    ejes = _ejes_resistentes(
        z_m, db_mm, desplazamiento_centroide_normal_mm, p
    )
    alpha = p.angulo_tirante_rad
    tz = M_kN_m/ejes["brazo_perpendicular_m"] if M_kN_m else 0.0
    t = tz/math.cos(alpha)
    tx = t*math.sin(alpha)
    # T + C = resultante interna [V, 0].
    cx = V_kN-tx
    cz = -tz
    compresion = math.hypot(cx, cz)
    residual_x = tx+cx-V_kN
    residual_z = tz+cz
    escala = max(abs(V_kN), abs(t), abs(compresion), 1.0)
    error = math.hypot(residual_x, residual_z)/escala
    angulo_biela = math.atan2(abs(cz), abs(cx)) if compresion else math.pi/2
    diferencia = abs((math.pi/2-alpha)-(-angulo_biela))
    diferencia = min(diferencia, math.pi-diferencia)
    return {
        **ejes,
        "angulo_tirante_desde_vertical_grados": math.degrees(alpha),
        "tirante_vector_kN": [tx, tz],
        "fuerza_tirante_kN": t,
        "biela_vector_kN": [cx, cz],
        "fuerza_biela_kN": compresion,
        "resultante_corte_vector_kN": [V_kN, 0.0],
        "angulo_biela_desde_horizontal_grados": math.degrees(angulo_biela),
        "angulo_menor_biela_tirante_grados": math.degrees(diferencia),
        "residual_vector_kN": [residual_x, residual_z],
        "error_relativo_equilibrio": error,
    }


def _distribucion_capas(n: int, numero_capas: int) -> list[int]:
    base, resto = divmod(n, numero_capas)
    return [base+(1 if i < resto else 0) for i in range(numero_capas)]


def _separacion_libre(n_por_capa: int, db_mm: float,
                      p: ParametrosDisenoContrafuertes) -> float:
    disponible = p.espesor_m*1000-2*p.recubrimiento_mm
    if n_por_capa <= 1:
        return disponible-db_mm
    return (disponible-n_por_capa*db_mm)/(n_por_capa-1)


def seleccionar_armado_principal(as_requerida_mm2: float, minimo_barras: int,
                                  p: ParametrosDisenoContrafuertes) -> dict:
    """Selecciona la solución conforme de menor área y luego menor congestión."""
    catalogo = ((p.barra_principal_forzada,)
                if p.barra_principal_forzada else p.barras_principales)
    soluciones = []
    for barra in catalogo:
        db = BARRAS_MM[barra]
        ab = _area_barra_mm2(barra)
        n = max(minimo_barras, math.ceil(as_requerida_mm2/ab-1e-12))
        libre_min = max(25.0, db, 4*p.tamano_agregado_mm/3)
        for numero_capas in range(1, p.maximo_capas_principales+1):
            distribucion = _distribucion_capas(n, numero_capas)
            if min(distribucion) < 2 and numero_capas > 1:
                continue
            libre = _separacion_libre(max(distribucion), db, p)
            if libre+1e-9 < libre_min:
                continue
            separacion_capas = libre_min
            desplazamiento = ((numero_capas-1)*(db+separacion_capas)/2)
            soluciones.append({
                "barra": barra, "diametro_mm": db, "numero_barras": n,
                "area_barra_mm2": ab, "As_provisto_mm2": n*ab,
                "separacion_libre_mm": libre,
                "separacion_libre_minima_mm": libre_min,
                "numero_capas": numero_capas,
                "barras_por_capa": distribucion,
                "separacion_libre_entre_capas_mm": (
                    separacion_capas if numero_capas > 1 else None
                ),
                "desplazamiento_centroide_normal_mm": desplazamiento,
                "constructibilidad_cumple": True,
            })
            break
    if not soluciones:
        raise ValueError("Ningún armado principal satisface área y separación en 0.40 m")
    return min(soluciones, key=lambda q: (q["As_provisto_mm2"], q["numero_barras"], q["diametro_mm"]))


def _fcu_biela_mpa(stm: dict, p: ParametrosDisenoContrafuertes) -> dict:
    eps_s = p.fy_mpa/p.es_mpa
    theta = math.radians(max(stm["angulo_menor_biela_tirante_grados"], 25.0))
    eps_1 = eps_s+(eps_s+0.002)/math.tan(theta)**2
    fcu = min(p.fc_mpa/(0.8+170*eps_1), 0.85*p.fc_mpa)
    return {"epsilon_tirante": eps_s, "epsilon_1": eps_1,
            "fcu_MPa": fcu, "angulo_usado_grados": math.degrees(theta)}


def _longitudes_desarrollo(db_mm: float, p: ParametrosDisenoContrafuertes) -> dict:
    raiz_fc = min(math.sqrt(p.fc_mpa), 8.3)
    denominador = 2.6 if db_mm <= 19.05+1e-9 else 2.1
    ld = max(p.fy_mpa/(denominador*raiz_fc)*db_mm, 300.0)
    # E.060 12.5, normal/no epóxico y reducción 0.7 por recubrimiento adecuado.
    ldh = max(0.24*p.fy_mpa/raiz_fc*db_mm*0.7, 8*db_mm, 150.0)
    diametro_doblado = (6.0 if db_mm <= 25.4+1e-9 else 8.0)*db_mm
    return {
        "ld_recto_mm": ld,
        "ld_gancho_90_mm": ldh,
        "extension_gancho_mm": 12*db_mm,
        "diametro_interior_doblado_mm": diametro_doblado,
        "traslape_clase_b_mm": 1.3*ld,
    }


def _resolver_anclaje(nombre: str, disponible: float, desarrollo: dict, disponible_vertical: float = 7000.0) -> dict:
    if disponible + 1e-9 >= desarrollo["ld_recto_mm"]:
        tipo = "recto"
        requerido = desarrollo["ld_recto_mm"]
    else:
        ldh = desarrollo["ld_gancho_90_mm"]
        cola_vertical = (
            desarrollo["diametro_interior_doblado_mm"]
            + desarrollo["extension_gancho_mm"]
        )
        if disponible + 1e-9 >= ldh and disponible_vertical + 1e-9 >= cola_vertical:
            tipo = "gancho estándar de 90°"
            requerido = ldh
        else:
            tipo = "NO CUMPLE"
            requerido = ldh if disponible_vertical + 1e-9 >= cola_vertical else max(ldh, cola_vertical)
    dcr = requerido / disponible if disponible > 0 else float("inf")
    return {
        "ubicacion": nombre,
        "longitud_disponible_mm": disponible,
        "tipo_adoptado": tipo,
        "longitud_requerida_control_mm": requerido,
        "DCR": dcr,
        "cumple": tipo != "NO CUMPLE",
        **desarrollo,
    }


def _seleccionar_malla(p: ParametrosDisenoContrafuertes,
                       brazo_min_m: float) -> dict:
    # MTC 2.7.2.3.6 exige rho=0.003 total en cada dirección; se reparte
    # simétricamente entre las dos caras. E.060 aporta el mínimo alternativo.
    rho_total = max(p.rho_fisuracion_mtc_total, p.rho_temp_e060_total)
    as_cara_mm2_m = rho_total*p.espesor_m*1000*1000/2
    s_max = min(brazo_min_m*1000/4, 300.0)
    catalogo = ((p.barra_malla_forzada,)
                if p.barra_malla_forzada else p.barras_malla)
    candidatos = []
    for barra in catalogo:
        ab = _area_barra_mm2(barra)
        s_area = ab*1000/as_cara_mm2_m
        s = math.floor(min(s_area, s_max)/p.paso_espaciamiento_mm)*p.paso_espaciamiento_mm
        if s+1e-9 < p.espaciamiento_minimo_mm:
            continue
        candidatos.append({
            "barra": barra, "diametro_mm": BARRAS_MM[barra],
            "espaciamiento_mm": s, "As_requerido_por_cara_mm2_m": as_cara_mm2_m,
            "As_provisto_por_cara_mm2_m": ab*1000/s,
            "rho_total_requerida": rho_total,
            "separacion_maxima_mtc_mm": s_max,
            "caras": 2, "direcciones": ["horizontal", "vertical"],
        })
    if not candidatos:
        raise ValueError("No existe malla distribuida compatible con los límites")
    return min(candidatos, key=lambda q: (q["As_provisto_por_cara_mm2_m"], q["diametro_mm"]))


def _capacidad_cortante_convencional(z_m: float, db_mm: float,
                                      desplazamiento_centroide_normal_mm: float,
                                      p: ParametrosDisenoContrafuertes) -> dict:
    ejes = _ejes_resistentes(
        z_m, db_mm, desplazamiento_centroide_normal_mm, p
    )
    d_mm = ejes["brazo_perpendicular_m"]*1000
    bw_mm = p.espesor_m*1000
    phi_vc = p.phi_cortante*0.17*math.sqrt(p.fc_mpa)*bw_mm*d_mm/1000
    return {"d_efectivo_mm": d_mm, "bw_mm": bw_mm, "phi_Vc_kN": phi_vc}


def _round_nested(obj, digits: int = 6):
    if isinstance(obj, float):
        return round(obj, digits) if math.isfinite(obj) else obj
    if isinstance(obj, dict):
        return {k: _round_nested(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_nested(v, digits) for v in obj]
    return obj


def disenar(analisis: dict,
            p: ParametrosDisenoContrafuertes | None = None) -> dict:
    p = p or ParametrosDisenoContrafuertes()
    _validar_parametros(p)
    # La geometría del JSON es contractual para esta etapa.
    pg = analisis["parametros"]
    for clave, esperado in (
        ("altura_m", p.altura_m), ("longitud_base_m", p.longitud_base_m),
        ("longitud_corona_m", p.longitud_corona_m), ("espesor_m", p.espesor_m),
    ):
        if not math.isclose(float(pg[clave]), esperado, rel_tol=0, abs_tol=1e-9):
            raise ValueError(f"La geometría de diseño no coincide con el análisis: {clave}")

    env = formar_envolventes(analisis)
    limites = [0.0, p.altura_m/3, 2*p.altura_m/3, p.altura_m]

    # Primera pasada conservadora con el diámetro máximo; la selección final
    # recalcula exactamente el brazo con el diámetro realmente elegido.
    preliminares = []
    for i, z in enumerate(limites[:-1], 1):
        vu = _valor_en_envolvente(env["comun_resistencia_evento"], z, "V_u_kN")
        mu = _valor_en_envolvente(env["comun_resistencia_evento"], z, "M_u_kN_m")
        db_ref = max(BARRAS_MM[b] for b in p.barras_principales)
        stm0 = equilibrio_stm(vu, mu, z, db_ref, p)
        stm = stm0
        min_barras = 2
        for _ in range(4):
            as_req = stm["fuerza_tirante_kN"]*1000/(p.phi_tirante*p.fy_mpa)
            armado = seleccionar_armado_principal(as_req, min_barras, p)
            stm = equilibrio_stm(
                vu, mu, z, armado["diametro_mm"], p,
                armado["desplazamiento_centroide_normal_mm"],
            )
        as_req = stm["fuerza_tirante_kN"]*1000/(p.phi_tirante*p.fy_mpa)
        preliminares.append((i, z, vu, mu, stm, as_req, armado))

    # El detalle es escalonado, por lo que una zona inferior nunca puede tener
    # menos barras que una superior. Se conserva un único diámetro común.
    barra_comun = max(
        (q[6]["barra"] for q in preliminares),
        key=lambda b: BARRAS_MM[b],
    )
    if p.barra_principal_forzada:
        barra_comun = p.barra_principal_forzada
    p_barra = ParametrosDisenoContrafuertes(
        **{**asdict(p), "barra_principal_forzada": barra_comun}
    )
    zonas = []
    n_superior = 2
    for i, z, vu, mu, _, _, _ in reversed(preliminares):
        db = BARRAS_MM[barra_comun]
        stm = equilibrio_stm(vu, mu, z, db, p)
        for _ in range(4):
            as_req = stm["fuerza_tirante_kN"]*1000/(p.phi_tirante*p.fy_mpa)
            armado = seleccionar_armado_principal(as_req, n_superior, p_barra)
            stm = equilibrio_stm(
                vu, mu, z, db, p,
                armado["desplazamiento_centroide_normal_mm"],
            )
        as_req = stm["fuerza_tirante_kN"]*1000/(p.phi_tirante*p.fy_mpa)
        n_superior = armado["numero_barras"]
        capacidad_tirante = p.phi_tirante*armado["As_provisto_mm2"]*p.fy_mpa/1000

        biela = _fcu_biela_mpa(stm, p)
        ancho_disponible = min((limites[i]-limites[i-1])*1000/3, 1000.0)
        area_biela = p.espesor_m*1000*ancho_disponible
        cap_biela = p.phi_compresion_stm*biela["fcu_MPa"]*area_biela/1000
        ancho_req_biela = (stm["fuerza_biela_kN"]*1000
                           /(p.phi_compresion_stm*biela["fcu_MPa"]*p.espesor_m*1000))

        ancho_nodo = min(0.60*1000, ancho_disponible)
        factor_nodo = p.factor_nodo_cct
        cap_nodo = p.phi_compresion_stm*factor_nodo*p.fc_mpa*(p.espesor_m*1000)*ancho_nodo/1000
        ancho_req_nodo = (stm["fuerza_biela_kN"]*1000
                          /(p.phi_compresion_stm*factor_nodo*p.fc_mpa*p.espesor_m/1e-3))

        corte = _capacidad_cortante_convencional(
            z, db, armado["desplazamiento_centroide_normal_mm"], p
        )
        servicio_mu = _valor_en_envolvente(env["comun_servicio"], z, "M_u_kN_m")
        servicio_stm = equilibrio_stm(
            _valor_en_envolvente(env["comun_servicio"], z, "V_u_kN"),
            servicio_mu, z, db, p,
            armado["desplazamiento_centroide_normal_mm"],
        )
        fs = servicio_stm["fuerza_tirante_kN"]*1000/armado["As_provisto_mm2"]
        zonas.append({
            "zona": i, "z_inferior_m": z, "z_superior_m": limites[i],
            "demanda": {"V_u_kN": vu, "M_u_kN_m": mu,
                        "M_servicio_kN_m": servicio_mu},
            "stm": stm,
            "tirante": {**armado, "As_requerido_mm2": as_req,
                         "phi_Tn_kN": capacidad_tirante,
                         "DCR": stm["fuerza_tirante_kN"]/capacidad_tirante,
                         "cumple": stm["fuerza_tirante_kN"] <= capacidad_tirante+1e-9},
            "biela": {**biela, "ancho_efectivo_disponible_mm": ancho_disponible,
                       "ancho_efectivo_requerido_mm": ancho_req_biela,
                       "phi_Cn_kN": cap_biela,
                       "DCR": stm["fuerza_biela_kN"]/cap_biela,
                       "cumple": stm["fuerza_biela_kN"] <= cap_biela+1e-9},
            "nodo_cct": {"factor_limite": factor_nodo,
                         "ancho_disponible_mm": ancho_nodo,
                         "ancho_requerido_mm": ancho_req_nodo,
                         "phi_Nn_kN": cap_nodo,
                         "DCR": stm["fuerza_biela_kN"]/cap_nodo,
                         "cumple": stm["fuerza_biela_kN"] <= cap_nodo+1e-9},
            "corte_convencional": {**corte, "V_u_kN": vu,
                                    "DCR": vu/corte["phi_Vc_kN"],
                                    "cumple": vu <= corte["phi_Vc_kN"]+1e-9},
            "servicio": {"f_s_MPa": fs, "limite_0_60_fy_MPa": 0.60*p.fy_mpa,
                         "DCR": fs/(0.60*p.fy_mpa),
                         "cumple": fs <= 0.60*p.fy_mpa+1e-9},
        })
    zonas.sort(key=lambda q: q["zona"])

    db = BARRAS_MM[barra_comun]
    desarrollo = _longitudes_desarrollo(db, p)
    disponible_base = (p.anclaje_recto_base_disponible_mm
                       if p.anclaje_recto_base_disponible_mm is not None
                       else p.espesor_zapata_m*1000-p.recubrimiento_mm)
    disponible_corona = (p.anclaje_corona_disponible_mm
                         if p.anclaje_corona_disponible_mm is not None
                         else p.longitud_corona_m*1000-2*p.recubrimiento_mm)
    anclajes = [
        _resolver_anclaje("contrafuerte–zapata", disponible_base, desarrollo, disponible_vertical=p.longitud_base_m*1000),
        _resolver_anclaje("corona", disponible_corona, desarrollo, disponible_vertical=p.altura_m*1000 - 2*p.recubrimiento_mm),
    ]
    empalme = {
        "tipo": "Clase B; máximo 50% de barras en una sección",
        "longitud_requerida_mm": desarrollo["traslape_clase_b_mm"],
        "longitud_disponible_mm": p.longitud_empalme_disponible_mm,
        "DCR": desarrollo["traslape_clase_b_mm"]/p.longitud_empalme_disponible_mm,
        "cumple": p.longitud_empalme_disponible_mm+1e-9 >= desarrollo["traslape_clase_b_mm"],
        "ubicacion_recomendada": "tercio superior, fuera de nodos y cortes teóricos",
    }
    malla = _seleccionar_malla(p, min(z["stm"]["brazo_perpendicular_m"] for z in zonas))

    # Las barras que dejan de ser necesarias se prolongan ld completo sobre el
    # límite entre zonas, medido sobre el lomo inclinado.
    cortes_barras = []
    cos_alpha = math.cos(p.angulo_tirante_rad)
    for inferior, superior in zip(zonas[:-1], zonas[1:]):
        extras = inferior["tirante"]["numero_barras"]-superior["tirante"]["numero_barras"]
        if extras > 0:
            z_teorico = inferior["z_superior_m"]
            longitud_provista = math.ceil(
                desarrollo["ld_recto_mm"]/p.paso_espaciamiento_mm
            )*p.paso_espaciamiento_mm
            prolong_vertical = longitud_provista/1000*cos_alpha
            z_final = min(p.altura_m, z_teorico+prolong_vertical)
            cortes_barras.append({
                "numero_barras_adicionales": extras,
                "z_corte_teorico_m": z_teorico,
                "ld_medido_sobre_lomo_mm": desarrollo["ld_recto_mm"],
                "z_fin_barra_m": z_final,
                "longitud_provista_sobre_lomo_mm": (z_final-z_teorico)/cos_alpha*1000,
                "DCR": desarrollo["ld_recto_mm"]
                       /max((z_final-z_teorico)/cos_alpha*1000, 1e-12),
                "cumple": ((z_final-z_teorico)/cos_alpha*1000
                            >= desarrollo["ld_recto_mm"]-1e-6),
            })

    as_vertical_malla = (2*malla["As_provisto_por_cara_mm2_m"]
                         *p.longitud_base_m)
    as_cruza_base = zonas[0]["tirante"]["As_provisto_mm2"]*cos_alpha+as_vertical_malla
    phi_vn_fric = p.phi_corte_friccion*p.mu_corte_friccion*as_cruza_base*p.fy_mpa/1000
    corte_friccion = {
        "interfaz": "contrafuerte–zapata monolítica",
        "V_u_kN": zonas[0]["demanda"]["V_u_kN"],
        "As_principal_normal_equivalente_mm2": zonas[0]["tirante"]["As_provisto_mm2"]*cos_alpha,
        "As_malla_vertical_cruza_interfaz_mm2": as_vertical_malla,
        "As_total_normal_mm2": as_cruza_base,
        "mu": p.mu_corte_friccion, "phi_Vn_kN": phi_vn_fric,
        "DCR": zonas[0]["demanda"]["V_u_kN"]/phi_vn_fric,
        "cumple": zonas[0]["demanda"]["V_u_kN"] <= phi_vn_fric+1e-9,
        "anclaje_requerido_ambos_lados": True,
    }

    zonas_nodales = []
    for zona in zonas:
        zonas_nodales.append({
            "ubicacion": f"pantalla–alma / zona {zona['zona']}",
            "tipo": "CCT: ancla tirante en una dirección",
            "fuerza_demanda_kN": zona["stm"]["fuerza_biela_kN"],
            "factor_tension_limite": p.factor_nodo_cct,
            "ancho_efectivo_mm": zona["nodo_cct"]["ancho_disponible_mm"],
            "phi_Nn_kN": zona["nodo_cct"]["phi_Nn_kN"],
            "DCR": zona["nodo_cct"]["DCR"],
            "cumple": zona["nodo_cct"]["cumple"],
        })
    for ubicacion, zona in (("contrafuerte–zapata", zonas[0]),
                            ("corona", zonas[-1])):
        demanda_nodo = max(zona["stm"]["fuerza_biela_kN"],
                           zona["stm"]["fuerza_tirante_kN"])
        ancho_nodo = min(600.0, zona["biela"]["ancho_efectivo_disponible_mm"])
        capacidad = (p.phi_compresion_stm*p.factor_nodo_cct*p.fc_mpa
                     *p.espesor_m*1000*ancho_nodo/1000)
        zonas_nodales.append({
            "ubicacion": ubicacion,
            "tipo": "CCT: anclaje del tirante principal",
            "fuerza_demanda_kN": demanda_nodo,
            "factor_tension_limite": p.factor_nodo_cct,
            "ancho_efectivo_mm": ancho_nodo,
            "phi_Nn_kN": capacidad,
            "DCR": demanda_nodo/capacidad,
            "cumple": demanda_nodo <= capacidad+1e-9,
        })

    individuales = {}
    for cf in CONTRAFUERTES:
        indiv_zonas = []
        for zona in zonas:
            z = zona["z_inferior_m"]
            v = _valor_en_envolvente(env["por_contrafuerte"][cf], z, "V_u_kN")
            m = _valor_en_envolvente(env["por_contrafuerte"][cf], z, "M_u_kN_m")
            stm_cf = equilibrio_stm(
                v, m, z, db, p,
                zona["tirante"]["desplazamiento_centroide_normal_mm"],
            )
            indiv_zonas.append({
                "zona": zona["zona"], "V_u_kN": v, "M_u_kN_m": m,
                "T_u_kN": stm_cf["fuerza_tirante_kN"],
                "DCR_tirante": stm_cf["fuerza_tirante_kN"]/zona["tirante"]["phi_Tn_kN"],
                "DCR_biela": stm_cf["fuerza_biela_kN"]/zona["biela"]["phi_Cn_kN"],
                "DCR_nodo": stm_cf["fuerza_biela_kN"]/zona["nodo_cct"]["phi_Nn_kN"],
                "DCR_corte": v/zona["corte_convencional"]["phi_Vc_kN"],
                "DCR_corte_friccion_base": (
                    v/corte_friccion["phi_Vn_kN"] if zona["zona"] == 1 else None
                ),
            })
        individuales[cf] = indiv_zonas

    mecanismos = []
    for zona in zonas:
        mecanismos.extend([
            zona["tirante"], zona["biela"], zona["nodo_cct"],
            zona["corte_convencional"], zona["servicio"],
        ])
    mecanismos.extend([*zonas_nodales, *anclajes, empalme,
                       corte_friccion, *cortes_barras])
    dcr_max = max(float(x.get("DCR", 0.0)) for x in mecanismos)
    cumple = all(bool(x.get("cumple", True)) for x in mecanismos)
    equilibrio_max = max(z["stm"]["error_relativo_equilibrio"] for z in zonas)

    resultado = {
        "identificacion": "Diseño STM del armado común de contrafuertes centrales",
        "estado": "CUMPLE" if cumple and dcr_max <= 1.0 else "NO CUMPLE",
        "normativa": {
            "principal": "Manual de Puentes MTC 2018, 2.7.2.3.2–2.7.2.3.6",
            "complementaria": "NTE E.060, DS 010-2009-VIVIENDA",
            "nota": "Los factores se mantienen separados de las demandas factorizadas.",
        },
        "fuente_acciones": str(ENTRADA_PREDETERMINADA),
        "parametros": asdict(p),
        "envolventes": env,
        "acciones_base_reproducidas": {
            "V_u_kN": env["comun_resistencia_evento"][0]["V_u_kN"],
            "M_u_kN_m": env["comun_resistencia_evento"][0]["M_u_kN_m"],
        },
        "zonas": zonas,
        "armado_principal_comun": {
            "barra": barra_comun,
            "diametro_mm": db,
            "barras_continuas_corona": zonas[-1]["tirante"]["numero_barras"],
            "distribucion_por_zona": [
                {"zona": z["zona"], "numero_barras": z["tirante"]["numero_barras"],
                 "numero_capas": z["tirante"]["numero_capas"],
                 "barras_por_capa": z["tirante"]["barras_por_capa"],
                 "As_provisto_mm2": z["tirante"]["As_provisto_mm2"]}
                for z in zonas
            ],
        },
        "malla_fisuracion": malla,
        "zonas_nodales": zonas_nodales,
        "corte_friccion": corte_friccion,
        "desarrollo": desarrollo,
        "anclajes": anclajes,
        "empalme": empalme,
        "cortes_barras": cortes_barras,
        "dcr_individuales": individuales,
        "demandas_locales_elementos_adyacentes": {
            "zapata": {
                "V_u_interfaz_kN": zonas[0]["demanda"]["V_u_kN"],
                "T_u_anclaje_kN": zonas[0]["stm"]["fuerza_tirante_kN"],
                "C_u_nodal_kN": zonas[0]["stm"]["fuerza_biela_kN"],
                "alcance": "demanda transferida; la zapata no se rediseña",
            },
            "pantalla": {
                "reaccion_horizontal_base_kN": zonas[0]["demanda"]["V_u_kN"],
                "momento_base_kN_m": zonas[0]["demanda"]["M_u_kN_m"],
                "alcance": "demanda transferida; la pantalla no se rediseña",
            },
        },
        "validaciones": {
            "acciones_base_exactas": (
                math.isclose(env["comun_resistencia_evento"][0]["V_u_kN"],
                             1045.4964939670601, abs_tol=1e-9)
                and math.isclose(env["comun_resistencia_evento"][0]["M_u_kN_m"],
                                 5013.558135197523, abs_tol=1e-9)
            ),
            "equilibrio_max_error_relativo": equilibrio_max,
            "equilibrio_cumple_1e_6": equilibrio_max < 1e-6,
            "envolvente_cubre_15_resultados": env["cubre_15_resultados"],
            "simetria_C1_C3": all(
                math.isclose(a[k], b[k], rel_tol=1e-12, abs_tol=1e-9)
                for a, b in zip(individuales["CF-C1"], individuales["CF-C3"])
                for k in ("V_u_kN", "M_u_kN_m", "T_u_kN")
            ),
            "constructibilidad_0_40_m": all(
                z["tirante"]["constructibilidad_cumple"] for z in zonas
            ),
            "dcr_maximo": dcr_max,
            "todos_los_mecanismos_cumplen": cumple and dcr_max <= 1.0,
        },
        "limitaciones": [
            "El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.",
            "La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.",
            "El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.",
            "El diseño requiere revisión y firma del ingeniero responsable del proyecto.",
        ],
    }
    return _round_nested(resultado)


def generar_markdown(r: dict) -> str:
    p = r["parametros"]
    a = r["acciones_base_reproducidas"]
    ap = r["armado_principal_comun"]
    malla = r["malla_fisuracion"]
    lineas = [
        "# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3", "",
        f"**Resultado global: {r['estado']}**", "",
        "## 1. Objetivo y datos", "",
        "Se dimensiona un único detalle de armado para los tres contrafuertes. "
        "Las acciones se leen del análisis FEM 2D existente y no se recalculan.", "",
        "| Parámetro | Valor | Unidad | Fuente/estado |", "|---|---:|---|---|",
        f"| Altura | {p['altura_m']:.3f} | m | análisis |",
        f"| Longitud base / corona | {p['longitud_base_m']:.3f} / {p['longitud_corona_m']:.3f} | m | análisis |",
        f"| Espesor | {p['espesor_m']:.3f} | m | análisis |",
        f"| f'c | {p['fc_kg_cm2']:.0f} ({p['fc_kg_cm2']*0.0980665:.2f}) | kg/cm² (MPa) | proyecto |",
        f"| fy | {p['fy_kg_cm2']:.0f} ({p['fy_kg_cm2']*0.0980665:.2f}) | kg/cm² (MPa) | proyecto |",
        f"| Recubrimiento | {p['recubrimiento_mm']:.0f} | mm | adoptado |",
        f"| Vu base | {a['V_u_kN']:.3f} | kN | envolvente |",
        f"| Mu base | {a['M_u_kN_m']:.3f} | kN·m | envolvente |", "",
        "## 2. Modelo resistente", "",
        "En cada límite inferior de zona, el momento se equilibra con la componente "
        "vertical del tirante inclinado del lomo y la compresión junto a la pantalla. "
        "La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM "
        "sólo orientan este campo resistente.", "",
        "| Zona | z | Vu | Mu | T | C | error equilibrio |", "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for z in r["zonas"]:
        lineas.append(
            f"| {z['zona']} | {z['z_inferior_m']:.3f} m | {z['demanda']['V_u_kN']:.2f} kN | "
            f"{z['demanda']['M_u_kN_m']:.2f} kN·m | {z['stm']['fuerza_tirante_kN']:.2f} kN | "
            f"{z['stm']['fuerza_biela_kN']:.2f} kN | {z['stm']['error_relativo_equilibrio']:.2e} |"
        )
    lineas += [
        "", "## 3. Armado adoptado", "",
        f"Barras principales comunes: **{ap['barra']}**. Se mantienen "
        f"**{ap['barras_continuas_corona']} barras continuas hasta la corona**.", "",
        "| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for z in r["zonas"]:
        t = z["tirante"]
        lineas.append(
            f"| {z['zona']} | {t['numero_barras']}–{t['barra']} en {t['numero_capas']} capa(s) "
            f"{t['barras_por_capa']} | {t['As_requerido_mm2']:.0f} mm² | "
            f"{t['As_provisto_mm2']:.0f} mm² | {t['DCR']:.3f} | {z['biela']['DCR']:.3f} | "
            f"{z['nodo_cct']['DCR']:.3f} | {z['corte_convencional']['DCR']:.3f} | "
            f"{z['servicio']['f_s_MPa']:.1f} MPa |"
        )
    lineas += [
        "", f"Malla ortogonal en ambas caras: **{malla['barra']} @ {malla['espaciamiento_mm']:.0f} mm** "
        "en dirección horizontal y vertical.", "",
        "## 4. Anclaje, interfaz y cortes", "",
        "| Control | Disponible | Requerido | Solución | DCR | Estado |", "|---|---:|---:|---|---:|---|",
    ]
    for x in r["anclajes"]:
        lineas.append(
            f"| {x['ubicacion']} | {x['longitud_disponible_mm']:.0f} mm | "
            f"{x['longitud_requerida_control_mm']:.0f} mm | {x['tipo_adoptado']} | "
            f"{x['DCR']:.3f} | {'CUMPLE' if x['cumple'] else 'NO CUMPLE'} |"
        )
    e = r["empalme"]
    cf = r["corte_friccion"]
    lineas += [
        f"| Empalme Clase B | {e['longitud_disponible_mm']:.0f} mm | {e['longitud_requerida_mm']:.0f} mm | "
        f"máximo 50% | {e['DCR']:.3f} | {'CUMPLE' if e['cumple'] else 'NO CUMPLE'} |",
        f"| Corte-fricción base | — | φVn={cf['phi_Vn_kN']:.1f} kN | unión monolítica | "
        f"{cf['DCR']:.3f} | {'CUMPLE' if cf['cumple'] else 'NO CUMPLE'} |", "",
        "### Zonas nodales", "",
        "| Ubicación | Tipo | Demanda | φNn | DCR |", "|---|---|---:|---:|---:|",
    ]
    for nodo in r["zonas_nodales"]:
        lineas.append(
            f"| {nodo['ubicacion']} | {nodo['tipo']} | {nodo['fuerza_demanda_kN']:.1f} kN | "
            f"{nodo['phi_Nn_kN']:.1f} kN | {nodo['DCR']:.3f} |"
        )
    lineas.append("")
    if r["cortes_barras"]:
        lineas += ["Las barras adicionales se cortan sólo después de prolongar una longitud "
                   "de desarrollo completa más allá del punto teórico:", ""]
        for x in r["cortes_barras"]:
            lineas.append(
                f"- {x['numero_barras_adicionales']} barra(s): corte teórico z={x['z_corte_teorico_m']:.3f} m; "
                f"fin real z={x['z_fin_barra_m']:.3f} m; DCR={x['DCR']:.3f}."
            )
    lineas += [
        "", "## 5. DCR individuales", "",
        "| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |",
        "|---|---:|---:|---:|",
    ]
    for cf_nombre, zs in r["dcr_individuales"].items():
        lineas.append(
            f"| {cf_nombre} | {max(x['DCR_tirante'] for x in zs):.3f} | "
            f"{max(x['DCR_biela'] for x in zs):.3f} | {max(x['DCR_corte'] for x in zs):.3f} |"
        )
    v = r["validaciones"]
    lineas += [
        "", "## 6. Validaciones y límites", "",
        f"- Envolvente común cubre los 15 resultados: **{'sí' if v['envolvente_cubre_15_resultados'] else 'no'}**.",
        f"- Error máximo de equilibrio STM: `{v['equilibrio_max_error_relativo']:.2e}`.",
        f"- DCR máximo global: **{v['dcr_maximo']:.3f}**.",
        f"- Constructibilidad dentro de 0.40 m: **{'conforme' if v['constructibilidad_0_40_m'] else 'no conforme'}**.", "",
    ]
    lineas.extend(f"- {x}" for x in r["limitaciones"])
    return "\n".join(lineas)+"\n"


def _generar_png_vista_previa(r: dict, png: Path) -> None:
    """Genera la figura de vista previa en formato PNG usando Matplotlib."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle

    p = r["parametros"]
    fig, ax = plt.subplots(figsize=(15, 10.2), dpi=100)
    colores = ("#e8f1fb", "#f4eadb", "#e5f3e8")
    limites = (0, p["altura_m"]/3, 2*p["altura_m"]/3, p["altura_m"])
    longitud = lambda z: p["longitud_base_m"] + (
        p["longitud_corona_m"]-p["longitud_base_m"]
    )*z/p["altura_m"]
    for i, (za, zb) in enumerate(zip(limites[:-1], limites[1:])):
        ax.add_patch(Polygon([(0, za), (longitud(za), za),
                              (longitud(zb), zb), (0, zb)],
                             facecolor=colores[i], edgecolor="none"))
    for z in [0.45+i*0.45 for i in range(21) if 0.45+i*0.45 < p["altura_m"]]:
        ax.plot([0.08, max(0.08, longitud(z)-0.08)], [z, z],
                color="#3f78a8", lw=0.6, alpha=0.65)
    pendiente = abs((p["longitud_corona_m"]-p["longitud_base_m"])/p["altura_m"])
    for xv in [0.25+i*0.42 for i in range(14)]:
        zmax = min(p["altura_m"], (p["longitud_base_m"]-xv)/pendiente)
        if zmax > 0:
            ax.plot([xv, xv], [0.04, zmax-0.04],
                    color="#3f78a8", lw=0.6, alpha=0.65)
    ax.plot([0, p["longitud_base_m"], p["longitud_corona_m"], 0, 0],
            [0, 0, p["altura_m"], p["altura_m"], 0], color="#1c2733", lw=2)
    ax.add_patch(Rectangle((-0.35, -1.25), p["longitud_base_m"]+1.5, 1.25,
                           facecolor="#dedede", edgecolor="#1c2733", lw=1.5))
    ncontinuas = r["armado_principal_comun"]["barras_continuas_corona"]
    grupos = [(ncontinuas, p["altura_m"], "continuas")]
    grupos.extend((x["numero_barras_adicionales"], x["z_fin_barra_m"], "adicional")
                  for x in reversed(r["cortes_barras"]))
    for j, (numero, zfin, etiqueta) in enumerate(grupos):
        off = 0.08+j*0.14
        ax.plot([p["longitud_base_m"]-off, longitud(zfin)-off], [0, zfin],
                color="#b51f2e", lw=4, solid_capstyle="round")
        ax.plot([p["longitud_base_m"]-off]*2, [0, -0.85],
                color="#b51f2e", lw=4)
        zm = zfin*0.53
        ax.text(longitud(zm)-off-0.12, zm, f"{numero} {etiqueta}",
                ha="right", va="center", fontsize=8, color="#72131d")
    for z in limites[1:-1]:
        ax.plot([0, longitud(z)], [z, z], color="#777", lw=1.2, ls="--")
    for zona in r["zonas"]:
        zm = (zona["z_inferior_m"]+zona["z_superior_m"])/2
        t = zona["tirante"]
        ax.text(0.42*longitud(zm), zm,
                f"ZONA {zona['zona']}: {t['numero_barras']}–{t['barra']}",
                ha="center", va="center", fontsize=10)
    ap = r["armado_principal_comun"]
    ma = r["malla_fisuracion"]
    notas = (
        "DETALLE COMÚN CF-C1 / CF-C2 / CF-C3\n\n"
        f"Lomo: {ap['barra']}\n"
        + "  ".join(f"Z{x['zona']}: {x['numero_barras']} barras {x['barras_por_capa']}"
                    for x in ap["distribucion_por_zona"])
        + f"\n\nMalla ambas caras:\nH + V {ma['barra']} @ {ma['espaciamiento_mm']:.0f} mm"
        + f"\n\nRecubrimiento: {p['recubrimiento_mm']:.0f} mm"
        + f"\nEspesor: {p['espesor_m']:.2f} m"
        + f"\nBase: {r['anclajes'][0]['tipo_adoptado']}"
        + f"\nCorona: {r['anclajes'][1]['tipo_adoptado']}"
    )
    # Posición del panel de notas: a la derecha del lomo con margen
    nx_txt = p["longitud_base_m"]+0.8
    ny_txt = p["altura_m"]-0.1
    ax.text(nx_txt, ny_txt, notas, va="top", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.7", fc="#f7f8fa", ec="#9aa5b1"))
    capas_base = r["zonas"][0]["tirante"]["barras_por_capa"]
    nbase = sum(capas_base)
    # Sección transversal: debajo del panel de notas
    sx0 = nx_txt
    sy0 = 0.6
    ax.add_patch(Rectangle((sx0, sy0), 2.5, 0.75, facecolor="none",
                           edgecolor="#1c2733", lw=1.5))
    for fila, n_fila in enumerate(capas_base):
        yy_barra = sy0+0.28+fila*0.19-(len(capas_base)-1)*0.095
        for j in range(n_fila):
            xx = sx0+0.22+(2.06*j/(n_fila-1) if n_fila > 1 else 1.03)
            ax.plot(xx, yy_barra, "o", ms=7, color="#b51f2e")
    ax.text(sx0, sy0+0.9, f"SECCIÓN DEL LOMO (e = {p['espesor_m']:.2f} m)", fontsize=9)
    ax.text(sx0, sy0-0.25, f"{nbase} barras en {len(capas_base)} capas {capas_base}; separación verificada", fontsize=8)
    # Cotas dinámicas
    ax.annotate(f"{p['altura_m']:.2f} m", xy=(-0.28, p["altura_m"]/2), rotation=90,
                ha="center", va="center", fontsize=10)
    ax.annotate(f"{p['longitud_base_m']:.2f} m", xy=(p["longitud_base_m"]/2, -1.05),
                ha="center", va="center", fontsize=10)
    ax.annotate(f"{p['longitud_corona_m']:.2f} m",
                xy=(p["longitud_corona_m"]/2, p["altura_m"]+0.25),
                ha="center", va="center", fontsize=10)
    # Límites adaptativos con margen
    xlim_max = max(p["longitud_base_m"]+4.5, nx_txt+3.5)
    ylim_max = p["altura_m"]+1.2
    ax.set_title("ARMADO DEL CONTRAFUERTE TRAPEZOIDAL — VISTA PREVIA", fontsize=16, weight="bold")
    ax.set_xlim(-0.7, xlim_max)
    ax.set_ylim(-1.5, ylim_max)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(png, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def escribir_entregables(r: dict, carpeta: Path | str = SALIDA_PREDETERMINADA) -> list[Path]:
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = [
        carpeta/"diseno_contrafuertes_centrales_stm.json",
        carpeta/"diseno_contrafuertes_centrales_stm.md",
        carpeta/"detalle_armado_contrafuertes_centrales.png",
    ]
    rutas[0].write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    rutas[1].write_text(generar_markdown(r), encoding="utf-8")
    _generar_png_vista_previa(r, rutas[2])
    return rutas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=ENTRADA_PREDETERMINADA)
    parser.add_argument("--salida", type=Path, default=SALIDA_PREDETERMINADA)
    parser.add_argument("--recubrimiento", type=float, default=75.0)
    parser.add_argument("--espesor-pantalla", type=float, default=0.40)
    parser.add_argument("--espesor-zapata", type=float, default=1.50)
    parser.add_argument("--anclaje-base", type=float, default=None,
                        help="Longitud recta disponible en la base, mm")
    parser.add_argument("--anclaje-corona", type=float, default=None,
                        help="Longitud disponible en la corona, mm")
    parser.add_argument("--barra-principal", choices=BARRAS_PRINCIPALES, default=None)
    parser.add_argument("--barra-malla", choices=BARRAS_MALLA, default=None)
    return parser.parse_args()


def main() -> None:
    a = parse_args()
    p = ParametrosDisenoContrafuertes(
        recubrimiento_mm=a.recubrimiento,
        espesor_pantalla_m=a.espesor_pantalla,
        espesor_zapata_m=a.espesor_zapata,
        anclaje_recto_base_disponible_mm=a.anclaje_base,
        anclaje_corona_disponible_mm=a.anclaje_corona,
        barra_principal_forzada=a.barra_principal,
        barra_malla_forzada=a.barra_malla,
    )
    resultado = disenar(cargar_analisis(a.entrada), p)
    rutas = escribir_entregables(resultado, a.salida)
    print(f"Estado: {resultado['estado']}")
    print(f"DCR máximo: {resultado['validaciones']['dcr_maximo']:.3f}")
    for ruta in rutas:
        print(ruta)


if __name__ == "__main__":
    main()

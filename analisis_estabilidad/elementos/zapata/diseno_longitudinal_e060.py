#!/usr/bin/env python3
"""Diseño por metro lineal de la zapata del estribo según NTE E.060.

Las solicitaciones se leen directamente de ``agente_subestructura.py``.  La
zapata estructural se idealiza como dos voladizos de 1 m de ancho, empotrados
en las caras de la pantalla. La reacción usada es la distribución lineal de la
interfaz 1 (zapata estructural / falsa zapata).

Alcance:
* flexión en las caras de la pantalla (E.060 15.4);
* cortante unidireccional a una distancia d de esas caras (15.5 y 11.12.1.1);
* acero mínimo de zapatas de espesor uniforme (10.5.4 y 9.7);
* desarrollo, anclaje y empalmes por traslape a tracción (Capítulo 12).

No incluye punzonamiento: la pantalla es continua en la franja analizada y no
constituye una columna o reacción concentrada. Contrafuertes, columnas u otras
cargas concentradas requieren una comprobación tridimensional independiente.

Unidades internas: m, tf, kgf/cm2 y cm2/m.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable


RUTA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_SALIDA_PREDETERMINADA = (
    RUTA_PROYECTO / ".tmp" / "legacy" / "zapata" / "longitudinal"
)
SALIDA_MD_PREDETERMINADA = (
    CARPETA_SALIDA_PREDETERMINADA / "diseno_zapata_e060.md"
)
SALIDA_JSON_PREDETERMINADA = (
    CARPETA_SALIDA_PREDETERMINADA / "diseno_zapata_e060.json"
)


if __package__ in (None, ""):
    sys.path.insert(0, str(RUTA_PROYECTO))

from analisis_estabilidad.elementos.estribo.estabilidad_global import (  # noqa: E402
    FALSE_FOOTING,
    GEOM,
    LOADS,
    MAT,
    SEISMIC,
    SubstructureAnalysis,
    get_surcharge_height,
)


# =============================================================================
# DATOS DE ENTRADA EDITABLES
# =============================================================================
# Modifique únicamente este bloque para el uso habitual del programa.
# La geometría, materiales, cargas y combinaciones se leen desde
# agente_subestructura.py. Sus valores se muestran al inicio del informe.
# Las opciones de línea de comandos pueden sobrescribir recubrimiento, barras
# y longitud del estribo sin editar este archivo.

# Diámetros nominales disponibles. La barra de 7/8" se excluye expresamente.
BARRAS_INGLESAS_MM = {
    '3/8"': 9.525,
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
    '2Ø1"': 25.400,
}

# Cantidad de capas/barras que aporta cada posición del arreglo. El diámetro
# de BARRAS_INGLESAS_MM siempre corresponde a cada barra individual.
CANTIDAD_BARRAS_POR_POSICION = {
    '2Ø1"': 2,
}

# Plano de contacto que transmite las reacciones a la zapata estructural.
INTERFAZ_ANALISIS = "interface_1"

# Casos factorizados utilizados para el diseño por resistencia.
CASOS_RESISTENCIA = (
    "case_resistance_Ia",
    "case_resistance_Ib",
    "case_extreme_event_I",
)

# Sobrescrituras opcionales de geometría y materiales.
# None = conservar el valor de agente_subestructura.py.
# Escriba un número únicamente cuando desee reemplazar el dato del agente.
ANCHO_ZAPATA_B_M: float | None = None
LONGITUD_TALON_B1_M: float | None = None
LONGITUD_PUNTA_B2_M: float | None = None
ESPESOR_PANTALLA_TP2_M: float | None = None
ESPESOR_ZAPATA_H_M: float | None = None
ALTURA_PANTALLA_HP_M: float | None = None
FC_KGF_CM2: float | None = None
FY_KGF_CM2: float | None = None
PESO_CONCRETO_TF_M3: float | None = None
PESO_RELLENO_TF_M3: float | None = None

# Geometría complementaria y criterios para la selección automática de acero.
RECUBRIMIENTO_MM = 100.0
LONGITUD_ESTRIBO_M = 6.00
ANCHO_FRANJA_M = 1.00
BARRAS_LONGITUDINALES_DISPONIBLES = ('3/4"', '1"', '2Ø1"')
BARRAS_TRANSVERSALES_DISPONIBLES = ('3/4"',)
ESPACIAMIENTO_MINIMO_CONSTRUCTIVO_MM = 100.0
ESPACIAMIENTO_MAXIMO_E060_MM = 400.0
PASO_ESPACIAMIENTO_MM = 10.0
SEPARACION_LIBRE_VERTICAL_CAPAS_MM = 25.0

# Porcentaje máximo de barras que se proyecta empalmar dentro de la longitud
# de traslape requerida.
# E.060 Tabla 12.3 distingue 50% y 100% para clasificar el empalme.
PORCENTAJE_BARRAS_EMPALMADAS = 50.0

# None = selección automática independiente para cada zona y cara.
# Escriba una designación, por ejemplo '1"', solo para forzar una barra única.
BARRA_LONGITUDINAL_FORZADA: str | None = None
BARRA_TRANSVERSAL_FORZADA: str | None = None

# Factores de reducción de resistencia de la NTE E.060.
PHI_FLEXION = 0.90
PHI_CORTANTE = 0.85

# =============================================================================
# FIN DE DATOS DE ENTRADA EDITABLES
# =============================================================================

# Copias locales: las sobrescrituras no modifican agente_subestructura.py.
GEOM = replace(
    GEOM,
    **{
        nombre: valor
        for nombre, valor in {
            "B": ANCHO_ZAPATA_B_M,
            "B1": LONGITUD_TALON_B1_M,
            "B2": LONGITUD_PUNTA_B2_M,
            "tp2": ESPESOR_PANTALLA_TP2_M,
            "hz": ESPESOR_ZAPATA_H_M,
            "hp": ALTURA_PANTALLA_HP_M,
        }.items()
        if valor is not None
    },
)
MAT = replace(
    MAT,
    **{
        nombre: valor
        for nombre, valor in {
            "f_c": FC_KGF_CM2,
            "fy": FY_KGF_CM2,
            "gamma_c": PESO_CONCRETO_TF_M3,
            "gamma_r": PESO_RELLENO_TF_M3,
        }.items()
        if valor is not None
    },
)


@dataclass(frozen=True)
class ParametrosDiseno:
    recubrimiento_mm: float = RECUBRIMIENTO_MM
    designacion_barra: str | None = BARRA_LONGITUDINAL_FORZADA
    diametro_barra_mm: float | None = None
    designacion_barra_transversal: str | None = BARRA_TRANSVERSAL_FORZADA
    diametro_barra_transversal_mm: float | None = None
    barras_longitudinales_disponibles: tuple[str, ...] = BARRAS_LONGITUDINALES_DISPONIBLES
    barras_transversales_disponibles: tuple[str, ...] = BARRAS_TRANSVERSALES_DISPONIBLES
    espaciamiento_minimo_mm: float = ESPACIAMIENTO_MINIMO_CONSTRUCTIVO_MM
    espaciamiento_maximo_mm: float = ESPACIAMIENTO_MAXIMO_E060_MM
    paso_espaciamiento_mm: float = PASO_ESPACIAMIENTO_MM
    separacion_libre_vertical_capas_mm: float = SEPARACION_LIBRE_VERTICAL_CAPAS_MM
    porcentaje_barras_empalmadas: float = PORCENTAJE_BARRAS_EMPALMADAS
    longitud_estribo_m: float = LONGITUD_ESTRIBO_M
    ancho_franja_m: float = ANCHO_FRANJA_M
    phi_flexion: float = PHI_FLEXION
    phi_cortante: float = PHI_CORTANTE


@dataclass(frozen=True)
class ResultadoZonaCaso:
    caso_clave: str
    caso: str
    zona: str
    q_extremo_tf_m2: float
    q_cara_tf_m2: float
    momento_suelo_tf_m_m: float
    momento_descendente_tf_m_m: float
    Mu_firmado_tf_m_m: float
    Mu_tf_m_m: float
    cara_traccion: str
    As_calculado_cm2_m: float
    Vu_firmado_tf_m: float
    Vu_tf_m: float
    phi_Vc_tf_m: float
    relacion_cortante: float
    cortante_cumple: bool


@dataclass(frozen=True)
class RefuerzoCara:
    zona: str
    cara: str
    signo: str
    caso_gobernante: str | None
    As_calculado_cm2_m: float
    As_min_cara_cm2_m: float
    As_diseno_cm2_m: float
    barra: str
    cantidad_barras_por_posicion: int
    diametro_mm: float
    espaciamiento_requerido_mm: float
    espaciamiento_adoptado_mm: float
    As_provisto_cm2_m: float
    seleccion: str


def _validar_entrada(p: ParametrosDiseno) -> float:
    if GEOM.B <= 0 or GEOM.hz <= 0 or GEOM.B1 <= 0 or GEOM.B2 <= 0:
        raise ValueError("La geometría de la zapata debe ser positiva")
    if not math.isclose(GEOM.B1 + GEOM.tp2 + GEOM.B2, GEOM.B, abs_tol=1e-6):
        raise ValueError("Debe cumplirse B = B1 + tp2 + B2")
    if MAT.f_c <= 0 or MAT.fy <= 0:
        raise ValueError("f'c y fy deben ser positivos")
    if p.recubrimiento_mm < 0:
        raise ValueError("El recubrimiento no puede ser negativo")
    if p.longitud_estribo_m <= 0:
        raise ValueError("La longitud del estribo debe ser positiva")
    if not 0 < p.espaciamiento_minimo_mm <= p.espaciamiento_maximo_mm:
        raise ValueError("Los límites de espaciamiento no son válidos")
    if p.paso_espaciamiento_mm <= 0:
        raise ValueError("El paso de espaciamiento debe ser positivo")
    if p.separacion_libre_vertical_capas_mm < 0:
        raise ValueError("La separación libre vertical no puede ser negativa")
    if not 0 < p.porcentaje_barras_empalmadas <= 100:
        raise ValueError("El porcentaje de barras empalmadas debe estar entre 0 y 100")
    for catalogo in (
        p.barras_longitudinales_disponibles,
        p.barras_transversales_disponibles,
    ):
        if not catalogo:
            raise ValueError("El catálogo de barras no puede estar vacío")
        if '7/8"' in catalogo:
            raise ValueError('La barra de 7/8" está excluida del proyecto')
        if any(barra not in BARRAS_INGLESAS_MM for barra in catalogo):
            raise ValueError("El catálogo contiene una barra no reconocida")
    for designacion, diametro in (
        (p.designacion_barra, p.diametro_barra_mm),
        (p.designacion_barra_transversal, p.diametro_barra_transversal_mm),
    ):
        if designacion is None:
            if diametro is not None:
                raise ValueError("No indique diámetro sin una barra forzada")
            continue
        if designacion == '7/8"':
            raise ValueError('La barra de 7/8" está excluida del proyecto')
        diametro_catalogo = BARRAS_INGLESAS_MM.get(designacion)
        if diametro_catalogo is None:
            permitidas = ", ".join(BARRAS_INGLESAS_MM)
            raise ValueError(f"Barra no admitida. Use una de: {permitidas}")
        if diametro is None or not math.isclose(
            diametro, diametro_catalogo, abs_tol=0.01
        ):
            raise ValueError(
                f"La designación {designacion} corresponde a "
                f"{diametro_catalogo:.3f} mm"
            )
    barras_d = (
        (p.designacion_barra,) if p.designacion_barra
        else p.barras_longitudinales_disponibles
    )
    distancia_centroide_mm = max(
        p.recubrimiento_mm
        + BARRAS_INGLESAS_MM[barra] / 2.0
        + (CANTIDAD_BARRAS_POR_POSICION.get(barra, 1) - 1)
        * (
            BARRAS_INGLESAS_MM[barra]
            + p.separacion_libre_vertical_capas_mm
        ) / 2.0
        for barra in barras_d
    )
    d_m = GEOM.hz - distancia_centroide_mm / 1000.0
    if d_m <= 0:
        raise ValueError("El peralte efectivo calculado no es positivo")
    return d_m


def _q_lineal(q_punta: float, q_talon: float, x: float) -> float:
    """Presión en x, medida desde la punta hacia el talón."""
    if not 0.0 <= x <= GEOM.B:
        raise ValueError(f"x={x} m está fuera de la zapata")
    return q_punta + (q_talon - q_punta) * x / GEOM.B


def _integral_lineal(q0: float, pendiente: float, a: float, b: float) -> float:
    return q0 * (b - a) + 0.5 * pendiente * (b * b - a * a)


def _momento_lineal(q0: float, pendiente: float, a: float, b: float,
                    x_cara: float) -> float:
    """Integral q(x)*|x-x_cara| dx en [a,b]."""
    sentido = 1.0 if a >= x_cara else -1.0
    primitiva = lambda x: (  # noqa: E731
        pendiente * x**3 / 3.0
        + (q0 - pendiente * x_cara) * x**2 / 2.0
        - q0 * x_cara * x
    )
    return sentido * (primitiva(b) - primitiva(a))


def _componente(caso: dict, descripcion: str) -> dict:
    candidatos = [d for d in caso["fv_detail"] if d["desc"] == descripcion]
    if len(candidatos) != 1:
        raise ValueError(
            f"Se esperaba una componente '{descripcion}' y se encontraron "
            f"{len(candidatos)}"
        )
    return candidatos[0]


def _poligono_relleno() -> list[tuple[float, float]]:
    """Polígono local del relleno, igual al metrado del agente."""
    g = GEOM
    h_cajuela = g.c_cajuela + g.d_cajuela
    w_top = max(g.B1 - g.back_face_slope * g.hp, 0.0)
    recess = max(min(g.e_cajuela, w_top), 0.0)
    notch_h = max(min(h_cajuela, g.hp), 0.0)
    x_left_top = g.B1 - w_top
    y_notch = g.hp - notch_h
    x_left_notch = g.back_face_slope * y_notch
    if recess > 0.0 and notch_h > 0.0:
        return [
            (0.0, 0.0), (g.B1, 0.0), (g.B1, g.hp),
            (x_left_top + recess, g.hp),
            (x_left_notch + recess, y_notch),
            (x_left_notch, y_notch),
        ]
    return [(0.0, 0.0), (g.B1, 0.0), (g.B1, g.hp), (x_left_top, g.hp)]


def _area_poligono(puntos: Iterable[tuple[float, float]]) -> float:
    pts = list(puntos)
    if len(pts) < 3:
        return 0.0
    doble = sum(
        pts[i][0] * pts[(i + 1) % len(pts)][1]
        - pts[(i + 1) % len(pts)][0] * pts[i][1]
        for i in range(len(pts))
    )
    return abs(doble) / 2.0


def _recortar_x_minimo(puntos: list[tuple[float, float]], x_min: float
                       ) -> list[tuple[float, float]]:
    """Recorta un polígono por el semiplano x >= x_min."""
    salida: list[tuple[float, float]] = []
    for inicio, fin in zip(puntos, puntos[1:] + puntos[:1]):
        dentro_i = inicio[0] >= x_min
        dentro_f = fin[0] >= x_min
        if dentro_i:
            salida.append(inicio)
        if dentro_i != dentro_f:
            dx = fin[0] - inicio[0]
            if abs(dx) > 1e-12:
                t = (x_min - inicio[0]) / dx
                salida.append((x_min, inicio[1] + t * (fin[1] - inicio[1])))
    return salida


def _cargas_descendentes(caso: dict, zona: str, d_m: float) -> tuple[float, float]:
    """Retorna (momento en la cara, cortante exterior a d) en tf."""
    zapata = _componente(caso, "Zapata")
    w_zapata = zapata["valor"] / GEOM.B

    if zona == "punta":
        longitud = GEOM.B2
        momento = w_zapata * longitud**2 / 2.0
        corte = w_zapata * max(longitud - d_m, 0.0)
        return momento, corte

    x_cara = GEOM.B2 + GEOM.tp2
    longitud = GEOM.B1
    momento = w_zapata * longitud**2 / 2.0
    corte = w_zapata * max(longitud - d_m, 0.0)

    relleno = _componente(caso, "Relleno sobre talón")
    brazo_relleno = relleno["brazo"] - x_cara
    momento += relleno["valor"] * brazo_relleno

    poligono = _poligono_relleno()
    area_total = _area_poligono(poligono)
    corte_local = min(max(d_m, 0.0), GEOM.B1)
    area_exterior = _area_poligono(_recortar_x_minimo(poligono, corte_local))
    if area_total > 0:
        corte += relleno["valor"] * area_exterior / area_total

    sobrecarga = _componente(caso, "Sobrecarga terreno")
    if abs(sobrecarga["valor"]) > 0.0:
        h_sc = get_surcharge_height(GEOM.H)
        w_top = max(GEOM.B1 - GEOM.back_face_slope * GEOM.hp - GEOM.e_cajuela, 0.0)
        if h_sc <= 0 or w_top <= 0:
            raise ValueError("No se pudo reconstruir la distribución de la sobrecarga")
        x_inicio = GEOM.B1 - w_top
        intensidad = sobrecarga["valor"] / w_top
        momento += sobrecarga["valor"] * (sobrecarga["brazo"] - x_cara)
        longitud_exterior = max(GEOM.B1 - max(corte_local, x_inicio), 0.0)
        corte += intensidad * longitud_exterior
    return momento, corte


def _acero_flexion(Mu_tf_m_m: float, d_m: float,
                   phi: float) -> float:
    if Mu_tf_m_m <= 1e-12:
        return 0.0
    b_cm = 100.0
    d_cm = d_m * 100.0
    Mu_kg_cm = Mu_tf_m_m * 100_000.0
    discriminante = d_cm**2 - (
        2.0 * Mu_kg_cm / (phi * 0.85 * MAT.f_c * b_cm)
    )
    if discriminante <= 0:
        raise ValueError("La sección excede el dominio de la ecuación de flexión simple")
    a_cm = d_cm - math.sqrt(discriminante)
    return 0.85 * MAT.f_c * b_cm * a_cm / MAT.fy


def _resistencia_cortante(d_m: float, phi: float) -> float:
    """E.060 (11-3): Vc=0.17*sqrt(fc[MPa])*bw*d; retorna tf/m."""
    fc_mpa = MAT.f_c * 0.0980665
    vc_newton = 0.17 * math.sqrt(fc_mpa) * 1000.0 * (d_m * 1000.0)
    return phi * vc_newton / 9806.65


def _evaluar_zona(caso_clave: str, caso: dict, zona: str,
                  d_m: float, p: ParametrosDiseno) -> ResultadoZonaCaso:
    bearing = caso["bearing"]
    q_punta = bearing["q_punta_t_m2"]
    q_talon = bearing["q_talon_t_m2"]
    if q_punta is None or q_talon is None:
        raise ValueError("La interfaz 1 debe contener presiones lineales en punta y talón")
    pendiente = (q_talon - q_punta) / GEOM.B

    if zona == "punta":
        a, b, x_cara = 0.0, GEOM.B2, GEOM.B2
        a_corte, b_corte = 0.0, max(GEOM.B2 - d_m, 0.0)
        q_extremo = q_punta
    elif zona == "talon":
        x_cara = GEOM.B2 + GEOM.tp2
        a, b = x_cara, GEOM.B
        a_corte, b_corte = min(x_cara + d_m, GEOM.B), GEOM.B
        q_extremo = q_talon
    else:
        raise ValueError(f"Zona no reconocida: {zona}")

    momento_suelo = _momento_lineal(q_punta, pendiente, a, b, x_cara)
    corte_suelo = _integral_lineal(q_punta, pendiente, a_corte, b_corte)
    momento_down, corte_down = _cargas_descendentes(caso, zona, d_m)
    momento_firmado = momento_suelo - momento_down
    corte_firmado = corte_suelo - corte_down
    Mu = abs(momento_firmado)
    Vu = abs(corte_firmado)
    phi_vc = _resistencia_cortante(d_m, p.phi_cortante)

    return ResultadoZonaCaso(
        caso_clave=caso_clave,
        caso=caso["name"],
        zona=zona,
        q_extremo_tf_m2=round(q_extremo, 3),
        q_cara_tf_m2=round(_q_lineal(q_punta, q_talon, x_cara), 3),
        momento_suelo_tf_m_m=round(momento_suelo, 3),
        momento_descendente_tf_m_m=round(momento_down, 3),
        Mu_firmado_tf_m_m=round(momento_firmado, 3),
        Mu_tf_m_m=round(Mu, 3),
        cara_traccion="inferior" if momento_firmado >= 0 else "superior",
        As_calculado_cm2_m=round(_acero_flexion(Mu, d_m, p.phi_flexion), 3),
        Vu_firmado_tf_m=round(corte_firmado, 3),
        Vu_tf_m=round(Vu, 3),
        phi_Vc_tf_m=round(phi_vc, 3),
        relacion_cortante=round(Vu / phi_vc, 3),
        cortante_cumple=Vu <= phi_vc,
    )


def _redondear_espaciamiento_hacia_abajo(s_mm: float,
                                         p: ParametrosDiseno) -> float:
    if s_mm <= 0:
        raise ValueError("El espaciamiento debe ser positivo")
    return math.floor(
        min(s_mm, p.espaciamiento_maximo_mm) / p.paso_espaciamiento_mm
    ) * p.paso_espaciamiento_mm


def _descripcion_barra(designacion: str) -> str:
    """Devuelve una etiqueta legible para barras simples o arreglos por capas."""
    if designacion in CANTIDAD_BARRAS_POR_POSICION:
        return designacion
    return f"Ø{designacion}"


def _seleccionar_barra(as_requerido_cm2_m: float, catalogo: tuple[str, ...],
                       p: ParametrosDiseno,
                       barra_forzada: str | None = None) -> dict:
    """Selecciona el primer arreglo que permite un espaciamiento constructivo.

    Para cada barra se redondea el espaciamiento hacia abajo al paso configurado,
    garantizando As_provisto >= As_requerido. Se adopta el primer arreglo cuyo
    espaciamiento no sea menor que el mínimo constructivo.
    """
    if as_requerido_cm2_m <= 0:
        raise ValueError("El acero requerido debe ser positivo")
    candidatos = (barra_forzada,) if barra_forzada else catalogo
    ultimo: dict | None = None
    for barra in candidatos:
        db_mm = BARRAS_INGLESAS_MM[barra]
        cantidad = CANTIDAD_BARRAS_POR_POSICION.get(barra, 1)
        area_barra_cm2 = math.pi * (db_mm / 10.0) ** 2 / 4.0
        area_posicion_cm2 = cantidad * area_barra_cm2
        s_requerido = area_posicion_cm2 * 1000.0 / as_requerido_cm2_m
        s_adoptado = _redondear_espaciamiento_hacia_abajo(s_requerido, p)
        if s_adoptado <= 0:
            continue
        as_provisto = area_posicion_cm2 * 1000.0 / s_adoptado
        ultimo = {
            "barra": barra,
            "diametro_mm": db_mm,
            "cantidad_barras_por_posicion": cantidad,
            "area_barra_cm2": area_barra_cm2,
            "area_posicion_cm2": area_posicion_cm2,
            "espaciamiento_requerido_mm": s_requerido,
            "espaciamiento_adoptado_mm": s_adoptado,
            "As_provisto_cm2_m": as_provisto,
        }
        if s_adoptado >= p.espaciamiento_minimo_mm:
            return ultimo
    if barra_forzada and ultimo is not None:
        raise ValueError(
            f"El arreglo forzado {_descripcion_barra(barra_forzada)} requiere "
            f"{ultimo['espaciamiento_adoptado_mm']:.0f} mm, "
            f"menor que el mínimo constructivo de {p.espaciamiento_minimo_mm:.0f} mm"
        )
    raise ValueError(
        "Ninguna barra disponible satisface el acero requerido y el "
        "espaciamiento mínimo; amplíe el catálogo o reduzca el mínimo"
    )


def _redondear_longitud_hacia_arriba(longitud_mm: float) -> float:
    return math.ceil(longitud_mm / 50.0) * 50.0


def _refuerzo_transversal(p: ParametrosDiseno) -> list[dict]:
    """Acero perpendicular al voladizo por retracción y temperatura.

    E.060 9.7 exige rho=0.0018 para fy>=420 MPa. Se distribuye la mitad
    en cada cara de la zapata, conservando el total reglamentario.
    """
    as_total = 0.0018 * 100.0 * GEOM.hz * 100.0
    as_cara = as_total / 2.0
    salida = []
    for cara in ("superior", "inferior"):
        seleccion = _seleccionar_barra(
            as_cara, p.barras_transversales_disponibles, p,
            barra_forzada=p.designacion_barra_transversal,
        )
        salida.append({
            "direccion": "perpendicular_al_voladizo",
            "cara": cara,
            "signo": "distribucion_superior" if cara == "superior" else "distribucion_inferior",
            "barra": seleccion["barra"],
            "cantidad_barras_por_posicion": seleccion["cantidad_barras_por_posicion"],
            "diametro_mm": round(seleccion["diametro_mm"], 3),
            "As_requerido_cm2_m": round(as_cara, 3),
            "espaciamiento_requerido_mm": round(
                seleccion["espaciamiento_requerido_mm"], 1),
            "espaciamiento_adoptado_mm": round(
                seleccion["espaciamiento_adoptado_mm"], 1),
            "As_provisto_cm2_m": round(seleccion["As_provisto_cm2_m"], 3),
            "seleccion": "forzada" if p.designacion_barra_transversal else "automatica",
        })
    return salida


def _longitud_desarrollo_traccion(db_mm: float, cara: str) -> float:
    """ld en mm según Tabla 12.1 de E.060, condición favorable.

    Se adoptan barras sin epóxico, concreto normal, recubrimiento >= db y
    espaciamiento libre >= 2db. Las barras superiores usan psi_t=1.3.
    """
    fc_mpa = MAT.f_c * 0.0980665
    fy_mpa = MAT.fy * 0.0980665
    psi_t = 1.3 if cara == "superior" else 1.0
    denominador = 2.6 if db_mm <= 19.05 + 1e-9 else 2.1
    raiz_fc = min(math.sqrt(fc_mpa), 8.3)
    ld = fy_mpa * psi_t / (denominador * raiz_fc) * db_mm
    return max(ld, 300.0)


def _longitud_desarrollo_gancho(db_mm: float) -> float:
    """ldg en mm para gancho estándar, E.060 12.5.

    Usa concreto normal, barra sin epóxico y factor 0.7 por recubrimiento
    lateral >=65 mm y recubrimiento de la extensión >=50 mm.
    """
    fc_mpa = MAT.f_c * 0.0980665
    fy_mpa = MAT.fy * 0.0980665
    raiz_fc = min(math.sqrt(fc_mpa), 8.3)
    ldg = 0.24 * fy_mpa / raiz_fc * db_mm * 0.7
    minimo = min(8.0 * db_mm, 150.0)
    return max(ldg, minimo)


def _diametro_interior_doblado(db_mm: float) -> float:
    """Diámetro interior mínimo de doblado, E.060 Tabla 7.1."""
    return (6.0 if db_mm <= 25.4 + 1e-9 else 8.0) * db_mm


def _desarrollo_y_anclajes(refuerzo_longitudinal: list[RefuerzoCara],
                           refuerzo_transversal: list[dict],
                           p: ParametrosDiseno) -> list[dict]:
    """Comprueba desarrollo recto y define geometría de gancho a 90 grados."""
    salida: list[dict] = []
    rec = p.recubrimiento_mm
    for acero in refuerzo_longitudinal:
        db = acero.diametro_mm
        # Desarrollo desde la cara crítica hacia el interior de la zapata.
        if acero.zona == "punta":
            disponible = (GEOM.B - GEOM.B2) * 1000.0 - rec
        else:
            disponible = (GEOM.B2 + GEOM.tp2) * 1000.0 - rec
        ld = _longitud_desarrollo_traccion(db, acero.cara)
        salida.append({
            "direccion": "longitudinal",
            "zona": acero.zona,
            "cara": acero.cara,
            "barra": acero.barra,
            "ld_requerida_mm": round(ld, 1),
            "ld_adoptada_mm": _redondear_longitud_hacia_arriba(ld),
            "longitud_recta_disponible_mm": round(disponible, 1),
            "desarrollo_recto_cumple": disponible >= ld,
            "ldg_gancho_90_mm": round(_longitud_desarrollo_gancho(db), 1),
            "ldg_adoptada_mm": _redondear_longitud_hacia_arriba(
                _longitud_desarrollo_gancho(db)),
            "extension_recta_gancho_90_mm": round(12.0 * db, 1),
            "extension_adoptada_mm": _redondear_longitud_hacia_arriba(12.0 * db),
            "diametro_interior_doblado_mm": round(_diametro_interior_doblado(db), 1),
            "anclaje_adoptado": (
                "barra continua con desarrollo recto al otro lado de la cara crítica; "
                "gancho estándar de 90° en el borde exterior"
            ),
        })

    for acero in refuerzo_transversal:
        db = acero["diametro_mm"]
        disponible = p.longitud_estribo_m * 500.0 - rec
        ld = _longitud_desarrollo_traccion(db, acero["cara"])
        salida.append({
            "direccion": "transversal",
            "zona": "ancho_total_del_estribo",
            "cara": acero["cara"],
            "barra": acero["barra"],
            "ld_requerida_mm": round(ld, 1),
            "ld_adoptada_mm": _redondear_longitud_hacia_arriba(ld),
            "longitud_recta_disponible_mm": round(disponible, 1),
            "desarrollo_recto_cumple": disponible >= ld,
            "ldg_gancho_90_mm": round(_longitud_desarrollo_gancho(db), 1),
            "ldg_adoptada_mm": _redondear_longitud_hacia_arriba(
                _longitud_desarrollo_gancho(db)),
            "extension_recta_gancho_90_mm": round(12.0 * db, 1),
            "extension_adoptada_mm": _redondear_longitud_hacia_arriba(12.0 * db),
            "diametro_interior_doblado_mm": round(_diametro_interior_doblado(db), 1),
            "anclaje_adoptado": (
                "barra continua en el ancho del estribo; gancho estándar de 90° "
                "en ambos extremos"
            ),
        })
    return salida


def _calcular_empalmes(refuerzo_longitudinal: list[RefuerzoCara],
                       refuerzo_transversal: list[dict],
                       desarrollo_anclaje: list[dict],
                       p: ParametrosDiseno) -> list[dict]:
    """Calcula empalmes por traslape a tracción, E.060 12.15 y Tabla 12.3.

    La Clase A requiere simultáneamente As provisto/As requerido >= 2 y que
    se empalme como máximo el 50% de las barras dentro de la longitud de
    traslape. Los demás casos corresponden a Clase B. Para clasificar el
    empalme se usa el acero requerido de diseño, sin reducir ``ld`` por el
    exceso de acero provisto.
    """
    salida: list[dict] = []

    def agregar(identificador: str, direccion: str, zona: str, cara: str,
                signo: str, barra: str, as_requerido: float,
                as_provisto: float) -> None:
        anc = next(
            r for r in desarrollo_anclaje
            if r["direccion"] == direccion
            and r["zona"] == zona and r["cara"] == cara
        )
        relacion = as_provisto / as_requerido
        clase = (
            "A" if relacion >= 2.0
            and p.porcentaje_barras_empalmadas <= 50.0 else "B"
        )
        factor = 1.0 if clase == "A" else 1.3
        ld_base = anc["ld_requerida_mm"]
        traslape_requerido = max(factor * ld_base, 300.0)
        salida.append({
            "id": identificador,
            "direccion": direccion,
            "zona": zona,
            "cara": cara,
            "signo": signo,
            "barra": barra,
            "As_requerido_cm2_m": round(as_requerido, 3),
            "As_provisto_cm2_m": round(as_provisto, 3),
            "relacion_As_prov_req": round(relacion, 3),
            "porcentaje_barras_empalmadas": p.porcentaje_barras_empalmadas,
            "clase_empalme": clase,
            "factor_empalme": factor,
            "ld_base_mm": ld_base,
            "longitud_traslape_requerida_mm": round(traslape_requerido, 1),
            "longitud_traslape_adoptada_mm": (
                _redondear_longitud_hacia_arriba(traslape_requerido)
            ),
            "criterio": (
                f"Clase {clase}: {factor:.1f}ld, mínimo 300 mm; "
                "ld sin reducción por exceso de acero"
            ),
        })

    for indice, acero in enumerate(refuerzo_longitudinal, start=1):
        agregar(
            f"L{indice}", "longitudinal", acero.zona, acero.cara,
            acero.signo, acero.barra, acero.As_diseno_cm2_m,
            acero.As_provisto_cm2_m,
        )
    for indice, acero in enumerate(refuerzo_transversal, start=1):
        agregar(
            f"T{indice}", "transversal", "ancho_total_del_estribo",
            acero["cara"], "distribución", acero["barra"],
            acero["As_requerido_cm2_m"], acero["As_provisto_cm2_m"],
        )
    return salida


def _detalle_constructivo(refuerzo: list[RefuerzoCara], transversal: list[dict],
                          anclajes: list[dict], empalmes: list[dict],
                          p: ParametrosDiseno) -> list[str]:
    detalles: list[str] = []
    for acero in refuerzo:
        anc = next(
            r for r in anclajes
            if r["direccion"] == "longitudinal"
            and r["zona"] == acero.zona and r["cara"] == acero.cara
        )
        detalles.append(
            f'{acero.zona.capitalize()} — momento {acero.signo}, cara '
            f'{acero.cara}: {_descripcion_barra(acero.barra)} @ '
            f'{acero.espaciamiento_adoptado_mm:.0f} mm; prolongar '
            f'{anc["ld_adoptada_mm"]:.0f} mm después de la cara crítica y '
            f'rematar el borde exterior con gancho de 90° (ldg '
            f'{anc["ldg_adoptada_mm"]:.0f} mm, extensión '
            f'{anc["extension_adoptada_mm"]:.0f} mm, doblado interior '
            f'{anc["diametro_interior_doblado_mm"]:.0f} mm).'
        )
    for acero in transversal:
        anc = next(
            r for r in anclajes
            if r["direccion"] == "transversal" and r["cara"] == acero["cara"]
        )
        detalles.append(
            f'Transversal, cara {acero["cara"]}: '
            f'{_descripcion_barra(acero["barra"])} @ '
            f'{acero["espaciamiento_adoptado_mm"]:.0f} mm, continuo en los '
            f'{p.longitud_estribo_m:.2f} m; gancho de 90° en ambos extremos '
            f'(ldg {anc["ldg_adoptada_mm"]:.0f} mm, extensión '
            f'{anc["extension_adoptada_mm"]:.0f} mm, doblado interior '
            f'{anc["diametro_interior_doblado_mm"]:.0f} mm).'
        )
    for empalme in empalmes:
        detalles.append(
            f'Empalme {empalme["id"]}, '
            f'{_descripcion_barra(empalme["barra"])}, '
            f'{empalme["direccion"]} / {empalme["zona"]}, cara '
            f'{empalme["cara"]}: Clase {empalme["clase_empalme"]}, '
            f'traslape adoptado {empalme["longitud_traslape_adoptada_mm"]:.0f} '
            'mm; ubicar fuera de la sección de máximo momento y alternar los '
            'empalmes conforme al porcentaje especificado.'
        )
    return detalles


def _envolvente_refuerzo(resultados: list[ResultadoZonaCaso],
                         p: ParametrosDiseno) -> list[RefuerzoCara]:
    area_bruta_cm2 = p.ancho_franja_m * 100.0 * GEOM.hz * 100.0
    # Si el acero mínimo se reparte entre ambas caras, E.060 10.5.4 exige
    # rho >= 0.0012 en la cara sometida a tracción.
    as_min_cara = 0.0012 * area_bruta_cm2
    salida: list[RefuerzoCara] = []
    for zona in ("punta", "talon"):
        for cara in ("superior", "inferior"):
            candidatos = [r for r in resultados if r.zona == zona and r.cara_traccion == cara]
            gobernante = max(candidatos, key=lambda r: r.As_calculado_cm2_m, default=None)
            as_calc = 0.0 if gobernante is None else gobernante.As_calculado_cm2_m
            as_diseno = max(as_calc, as_min_cara)
            seleccion = _seleccionar_barra(
                as_diseno, p.barras_longitudinales_disponibles, p,
                barra_forzada=p.designacion_barra,
            )
            salida.append(RefuerzoCara(
                zona=zona,
                cara=cara,
                signo="negativo" if cara == "superior" else "positivo",
                caso_gobernante=None if gobernante is None else gobernante.caso,
                As_calculado_cm2_m=round(as_calc, 3),
                As_min_cara_cm2_m=round(as_min_cara, 3),
                As_diseno_cm2_m=round(as_diseno, 3),
                barra=seleccion["barra"],
                cantidad_barras_por_posicion=seleccion["cantidad_barras_por_posicion"],
                diametro_mm=round(seleccion["diametro_mm"], 3),
                espaciamiento_requerido_mm=round(
                    seleccion["espaciamiento_requerido_mm"], 1),
                espaciamiento_adoptado_mm=round(
                    seleccion["espaciamiento_adoptado_mm"], 1),
                As_provisto_cm2_m=round(seleccion["As_provisto_cm2_m"], 3),
                seleccion="forzada" if p.designacion_barra else "automatica",
            ))
    return salida


def _resumen_acero(refuerzo_longitudinal: list[RefuerzoCara],
                   refuerzo_transversal: list[dict]) -> list[dict]:
    """Consolida áreas, control normativo y D/C para cada armado propuesto."""
    resumen: list[dict] = []
    for acero in refuerzo_longitudinal:
        as_requerido = acero.As_diseno_cm2_m
        as_dispuesto = acero.As_provisto_cm2_m
        controla_flexion = (
            acero.As_calculado_cm2_m > acero.As_min_cara_cm2_m + 1e-9
        )
        resumen.append({
            "armado": (
                f"Longitudinal — {acero.zona}, cara {acero.cara}"
            ),
            "direccion": "longitudinal",
            "zona": acero.zona,
            "cara": acero.cara,
            "caso_gobernante": acero.caso_gobernante,
            "As_calculado_cm2_m": acero.As_calculado_cm2_m,
            "As_normativo_cm2_m": acero.As_min_cara_cm2_m,
            "control_normativo": (
                "demanda de flexión"
                if controla_flexion
                else "mínimo de flexión por cara (E.060 10.5.4)"
            ),
            "As_requerido_cm2_m": as_requerido,
            "barra": acero.barra,
            "espaciamiento_adoptado_mm": acero.espaciamiento_adoptado_mm,
            "As_dispuesto_cm2_m": as_dispuesto,
            "DCR_acero": round(as_requerido / as_dispuesto, 3),
            "cumple": as_dispuesto + 1e-9 >= as_requerido,
            "seleccion": acero.seleccion,
        })
    for acero in refuerzo_transversal:
        as_requerido = acero["As_requerido_cm2_m"]
        as_dispuesto = acero["As_provisto_cm2_m"]
        resumen.append({
            "armado": f"Transversal — cara {acero['cara']}",
            "direccion": "transversal",
            "zona": "ancho_total_del_estribo",
            "cara": acero["cara"],
            "caso_gobernante": None,
            "As_calculado_cm2_m": 0.0,
            "As_normativo_cm2_m": as_requerido,
            "control_normativo": (
                "retracción y temperatura por cara (E.060 9.7)"
            ),
            "As_requerido_cm2_m": as_requerido,
            "barra": acero["barra"],
            "espaciamiento_adoptado_mm": acero["espaciamiento_adoptado_mm"],
            "As_dispuesto_cm2_m": as_dispuesto,
            "DCR_acero": round(as_requerido / as_dispuesto, 3),
            "cumple": as_dispuesto + 1e-9 >= as_requerido,
            "seleccion": acero["seleccion"],
        })
    return resumen


def disenar(
    parametros: ParametrosDiseno | None = None,
    resultados_estabilidad: dict | None = None,
) -> dict:
    p = parametros or ParametrosDiseno()
    d_m = _validar_entrada(p)
    distancia_centroide_control_mm = (GEOM.hz - d_m) * 1000.0
    diametro_control_d = max(
        BARRAS_INGLESAS_MM[barra]
        for barra in (
            (p.designacion_barra,) if p.designacion_barra
            else p.barras_longitudinales_disponibles
        )
    )
    resultados_agente = resultados_estabilidad
    if resultados_agente is None:
        analisis = SubstructureAnalysis(GEOM, MAT, LOADS, SEISMIC, FALSE_FOOTING)
        resultados_agente = analisis.run_full_analysis()
    interfaz = resultados_agente.get("interfaces", {}).get(INTERFAZ_ANALISIS)
    if not interfaz:
        raise ValueError(f"El agente no produjo la interfaz {INTERFAZ_ANALISIS}")

    resultados: list[ResultadoZonaCaso] = []
    for clave in CASOS_RESISTENCIA:
        caso = interfaz["cases"].get(clave)
        if caso is None:
            raise ValueError(f"Falta el caso requerido: {clave}")
        if caso["bearing"].get("contacto") != "COMPLETO":
            raise ValueError(
                f"{caso['name']}: la formulación lineal requiere contacto completo"
            )
        for zona in ("punta", "talon"):
            resultados.append(_evaluar_zona(clave, caso, zona, d_m, p))

    refuerzo = _envolvente_refuerzo(resultados, p)
    refuerzo_transversal = _refuerzo_transversal(p)
    resumen_acero = _resumen_acero(refuerzo, refuerzo_transversal)
    desarrollo_anclaje = _desarrollo_y_anclajes(refuerzo, refuerzo_transversal, p)
    empalmes_traslape = _calcular_empalmes(
        refuerzo, refuerzo_transversal, desarrollo_anclaje, p)
    as_min_total = 0.0018 * 100.0 * GEOM.hz * 100.0
    return {
        "norma": "NTE E.060 Concreto Armado, DS N.° 010-2009-VIVIENDA",
        "fuente_solicitaciones": (
            f"agente_subestructura.py / {INTERFAZ_ANALISIS}"
        ),
        "interfaz_analisis": INTERFAZ_ANALISIS,
        "casos_analizados": list(CASOS_RESISTENCIA),
        "geometria_m": {
            "B": GEOM.B, "B1_talon": GEOM.B1, "B2_punta": GEOM.B2,
            "tp2": GEOM.tp2, "h": GEOM.hz, "hp": GEOM.hp,
            "d": round(d_m, 4),
        },
        "materiales": {
            "fc_kg_cm2": MAT.f_c, "fy_kg_cm2": MAT.fy,
            "gamma_c_tf_m3": MAT.gamma_c, "gamma_r_tf_m3": MAT.gamma_r,
        },
        "fuentes_entrada": {
            "B": "agente" if ANCHO_ZAPATA_B_M is None else "bloque editable",
            "B1": "agente" if LONGITUD_TALON_B1_M is None else "bloque editable",
            "B2": "agente" if LONGITUD_PUNTA_B2_M is None else "bloque editable",
            "tp2": "agente" if ESPESOR_PANTALLA_TP2_M is None else "bloque editable",
            "h": "agente" if ESPESOR_ZAPATA_H_M is None else "bloque editable",
            "hp": "agente" if ALTURA_PANTALLA_HP_M is None else "bloque editable",
            "fc": "agente" if FC_KGF_CM2 is None else "bloque editable",
            "fy": "agente" if FY_KGF_CM2 is None else "bloque editable",
            "gamma_c": "agente" if PESO_CONCRETO_TF_M3 is None else "bloque editable",
            "gamma_r": "agente" if PESO_RELLENO_TF_M3 is None else "bloque editable",
        },
        "parametros": asdict(p),
        "criterio_seleccion": {
            "metodo": (
                "primer arreglo disponible que satisface As requerido con "
                "el espaciamiento configurado"
            ),
            "diametro_control_peralte_mm": round(diametro_control_d, 3),
            "distancia_centroide_control_mm": round(
                distancia_centroide_control_mm, 3),
            "separacion_libre_vertical_capas_mm": (
                p.separacion_libre_vertical_capas_mm
            ),
            "redondeo_espaciamiento": "hacia abajo al paso configurado",
            "barra_7_8": "excluida",
        },
        "As_min_total_E060_cm2_m": round(as_min_total, 3),
        "resultados_por_caso": [asdict(r) for r in resultados],
        "estado_armado": (
            "CUMPLE" if all(r["cumple"] for r in resumen_acero)
            else "NO CUMPLE"
        ),
        "resumen_acero": resumen_acero,
        "refuerzo_envolvente": [asdict(r) for r in refuerzo],
        "refuerzo_transversal": refuerzo_transversal,
        "desarrollo_y_anclajes": desarrollo_anclaje,
        "empalmes_traslape": empalmes_traslape,
        "detalle_constructivo": _detalle_constructivo(
            refuerzo, refuerzo_transversal, desarrollo_anclaje,
            empalmes_traslape, p),
        "advertencias": [
            "Las combinaciones de carga factorizadas proceden del análisis de puente; E.060 se usa para la resistencia de la sección de concreto armado.",
            "El acero mínimo se reparte conservadoramente en ambas caras: rho=0.0012 por cara; la suma supera rho=0.0018 total.",
            f"El peralte efectivo se calculó conservadoramente con una distancia de {distancia_centroide_control_mm:.3f} mm desde la cara de tracción hasta el centroide del arreglo longitudinal de control.",
            "La selección automática adopta el primer arreglo del catálogo que permite cumplir As sin bajar del espaciamiento mínimo constructivo configurado.",
            f"Los arreglos de dos barras se disponen en dos capas con {p.separacion_libre_vertical_capas_mm:.0f} mm de separación libre vertical; el peralte efectivo usa el centroide conjunto.",
            "Las longitudes de desarrollo suponen barras sin recubrimiento epóxico, concreto normal y separaciones favorables según la Tabla 12.1.",
            f"Los empalmes por traslape se calcularon a tracción según E.060 12.15 y Tabla 12.3, suponiendo como máximo {p.porcentaje_barras_empalmadas:.0f}% de barras empalmadas dentro de la longitud de traslape requerida.",
            "La ubicación exacta de los empalmes debe definirse en planos fuera de las secciones de máximo momento y coordinarse con cortes, ganchos y juntas de construcción.",
            f"Confirmar en planos la longitud ingresada del estribo ({p.longitud_estribo_m:.2f} m) y la compatibilidad de los ganchos con las demás armaduras.",
            "Punzonamiento no aplica al modelo de pantalla continua; comprobarlo por separado si existen cargas concentradas o contrafuertes.",
        ],
    }


def generar_markdown(diseno: dict) -> str:
    g = diseno["geometria_m"]
    m = diseno["materiales"]
    p = diseno["parametros"]
    f = diseno["fuentes_entrada"]
    criterio = diseno["criterio_seleccion"]
    lineas = [
        "# Diseño de la zapata del estribo — NTE E.060", "",
        "## Datos de entrada", "",
        "| Categoría | Parámetro | Valor | Unidad | Fuente |",
        "|---|---|---:|---|---|",
        f"| Geometría | Ancho total B | {g['B']:.3f} | m | {f['B']} |",
        f"| Geometría | Punta B2 | {g['B2_punta']:.3f} | m | {f['B2']} |",
        f"| Geometría | Pantalla tp2 | {g['tp2']:.3f} | m | {f['tp2']} |",
        f"| Geometría | Talón B1 | {g['B1_talon']:.3f} | m | {f['B1']} |",
        f"| Geometría | Espesor h | {g['h']:.3f} | m | {f['h']} |",
        f"| Geometría | Altura de pantalla hp | {g['hp']:.3f} | m | {f['hp']} |",
        f"| Geometría | Peralte efectivo d | {g['d']:.4f} | m | calculado |",
        f"| Geometría | Diámetro individual de control para d | {criterio['diametro_control_peralte_mm']:.3f} | mm | criterio conservador |",
        f"| Geometría | Distancia al centroide de acero de control | {criterio['distancia_centroide_control_mm']:.3f} | mm | dos capas cuando corresponda |",
        f"| Material | f'c | {m['fc_kg_cm2']:.1f} | kgf/cm² | {f['fc']} |",
        f"| Material | fy | {m['fy_kg_cm2']:.1f} | kgf/cm² | {f['fy']} |",
        f"| Material | Peso del concreto | {m['gamma_c_tf_m3']:.3f} | tf/m³ | {f['gamma_c']} |",
        f"| Material | Peso del relleno | {m['gamma_r_tf_m3']:.3f} | tf/m³ | {f['gamma_r']} |",
        f"| Diseño | Recubrimiento | {p['recubrimiento_mm']:.1f} | mm | bloque editable |",
        f"| Diseño | Selección longitudinal | {'automática' if p['designacion_barra'] is None else 'forzada ' + _descripcion_barra(p['designacion_barra'])} | — | bloque editable |",
        f"| Diseño | Catálogo longitudinal | {', '.join(p['barras_longitudinales_disponibles'])} | — | bloque editable |",
        f"| Diseño | Selección transversal | {'automática' if p['designacion_barra_transversal'] is None else 'forzada ' + _descripcion_barra(p['designacion_barra_transversal'])} | — | bloque editable |",
        f"| Diseño | Catálogo transversal | {', '.join(p['barras_transversales_disponibles'])} | — | bloque editable |",
        f"| Diseño | Espaciamiento mínimo constructivo | {p['espaciamiento_minimo_mm']:.0f} | mm | bloque editable |",
        f"| Diseño | Separación libre vertical entre capas | {p['separacion_libre_vertical_capas_mm']:.0f} | mm | bloque editable |",
        f"| Diseño | Espaciamiento máximo | {p['espaciamiento_maximo_mm']:.0f} | mm | bloque editable |",
        f"| Diseño | Barras empalmadas dentro de la longitud de traslape | {p['porcentaje_barras_empalmadas']:.0f} | % | bloque editable |",
        f"| Diseño | Longitud del estribo | {p['longitud_estribo_m']:.3f} | m | bloque editable |",
        f"| Diseño | Ancho de franja | {p['ancho_franja_m']:.3f} | m | bloque editable |",
        f"| Resistencia | φ flexión | {p['phi_flexion']:.2f} | — | NTE E.060 |",
        f"| Resistencia | φ cortante | {p['phi_cortante']:.2f} | — | NTE E.060 |",
        f"| Análisis | Interfaz | {diseno['interfaz_analisis']} | — | bloque editable |",
        f"| Análisis | Casos | {', '.join(diseno['casos_analizados'])} | — | bloque editable |",
        "",
        "## Solicitaciones y cortante", "",
        "| Caso | Zona | q borde/cara (tf/m²) | Mu firmado (tf·m/m) | Cara tracción | As calc. (cm²/m) | Vu (tf/m) | φVc (tf/m) | D/C |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for r in diseno["resultados_por_caso"]:
        lineas.append(
            f"| {r['caso']} | {r['zona']} | {r['q_extremo_tf_m2']:.3f} / "
            f"{r['q_cara_tf_m2']:.3f} | {r['Mu_firmado_tf_m_m']:.3f} | "
            f"{r['cara_traccion']} | {r['As_calculado_cm2_m']:.3f} | "
            f"{r['Vu_tf_m']:.3f} | {r['phi_Vc_tf_m']:.3f} | "
            f"{r['relacion_cortante']:.3f} |"
        )
    lineas += [
        "", "Convención: Mu positivo = reacción ascendente dominante y tracción inferior; Mu negativo = cargas descendentes dominantes y tracción superior.",
        "", "## Armado propuesto y verificación de áreas", "",
        f"**Estado del armado:** {diseno['estado_armado']}.", "",
        "`As normativo` es el mínimo asignado al armado correspondiente. "
        "Para el acero longitudinal se usa el mínimo por cara de E.060 10.5.4; "
        "para el transversal, la mitad del acero de retracción y temperatura "
        "de E.060 9.7.", "",
        "La relación D/C de acero es `As requerido / As dispuesto`, con "
        "`As requerido = máx(As calculado, As normativo)`.", "",
        "| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |",
        "|---|---|---:|---:|---|---:|---|---:|---:|:---:|",
    ]
    for r in diseno["resumen_acero"]:
        caso = r["caso_gobernante"] or "mínimo / distribución"
        lineas.append(
            f"| {r['armado']} | {caso} | "
            f"{r['As_calculado_cm2_m']:.3f} cm²/m | "
            f"{r['As_normativo_cm2_m']:.3f} cm²/m | "
            f"{r['control_normativo']} | "
            f"{r['As_requerido_cm2_m']:.3f} cm²/m | "
            f"{_descripcion_barra(r['barra'])} @ {r['espaciamiento_adoptado_mm']:.0f} mm | "
            f"{r['As_dispuesto_cm2_m']:.3f} cm²/m | "
            f"{r['DCR_acero']:.3f} | {'Sí' if r['cumple'] else 'No'} |"
        )
    lineas += [
        "", "## Desarrollo y anclajes", "",
        "| Dirección/zona | Cara | Barra | ld requerida | Recta disponible | Cumple | Gancho 90°: ldg / extensión / doblado | Anclaje adoptado |",
        "|---|---|---:|---:|---:|:---:|---:|---|",
    ]
    for r in diseno["desarrollo_y_anclajes"]:
        nombre = f"{r['direccion']} / {r['zona']}"
        lineas.append(
            f"| {nombre} | {r['cara']} | {_descripcion_barra(r['barra'])} | "
            f"{r['ld_requerida_mm']:.0f} mm | {r['longitud_recta_disponible_mm']:.0f} mm | "
            f"{'Sí' if r['desarrollo_recto_cumple'] else 'No'} | "
            f"{r['ldg_gancho_90_mm']:.0f} / {r['extension_recta_gancho_90_mm']:.0f} / "
            f"{r['diametro_interior_doblado_mm']:.0f} mm | {r['anclaje_adoptado']} |"
        )
    lineas += [
        "", "## Empalmes por traslape", "",
        "| ID | Dirección/zona | Signo/cara | Barra | As prov./req. | % empalmado | Clase | ld base | Factor | Traslape requerido | Traslape adoptado |",
        "|---|---|---|---:|---:|---:|:---:|---:|---:|---:|---:|",
    ]
    for r in diseno["empalmes_traslape"]:
        lineas.append(
            f"| {r['id']} | {r['direccion']} / {r['zona']} | "
            f"{r['signo']} / {r['cara']} | {_descripcion_barra(r['barra'])} | "
            f"{r['As_provisto_cm2_m']:.3f} / {r['As_requerido_cm2_m']:.3f} "
            f"= {r['relacion_As_prov_req']:.3f} | "
            f"{r['porcentaje_barras_empalmadas']:.0f}% | "
            f"{r['clase_empalme']} | {r['ld_base_mm']:.0f} mm | "
            f"{r['factor_empalme']:.1f} | "
            f"{r['longitud_traslape_requerida_mm']:.0f} mm | "
            f"{r['longitud_traslape_adoptada_mm']:.0f} mm |"
        )
    lineas += ["", "## Detalle constructivo recomendado", ""]
    lineas.extend(f"- {detalle}" for detalle in diseno["detalle_constructivo"])
    lineas += [
        "", f"Acero mínimo total E.060: {diseno['As_min_total_E060_cm2_m']:.3f} cm²/m.",
        "", "## Alcance y pendientes", "",
    ]
    lineas.extend(f"- {a}" for a in diseno["advertencias"])
    return "\n".join(lineas) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recubrimiento-mm", type=float, default=RECUBRIMIENTO_MM,
        help=f"Valor del bloque editable (por defecto: {RECUBRIMIENTO_MM:g} mm)",
    )
    parser.add_argument(
        "--barra", choices=tuple(BARRAS_INGLESAS_MM),
        default=BARRA_LONGITUDINAL_FORZADA,
        help='Fuerza una barra longitudinal; omitir para selección automática',
    )
    parser.add_argument(
        "--barra-transversal", choices=tuple(BARRAS_INGLESAS_MM),
        default=BARRA_TRANSVERSAL_FORZADA,
        help='Fuerza una barra transversal; omitir para selección automática',
    )
    parser.add_argument(
        "--longitud-estribo-m", type=float, default=LONGITUD_ESTRIBO_M,
        help=f"Valor del bloque editable (por defecto: {LONGITUD_ESTRIBO_M:g} m)",
    )
    parser.add_argument(
        "--salida-md", type=Path, default=SALIDA_MD_PREDETERMINADA,
        help=f"Informe Markdown (por defecto: {SALIDA_MD_PREDETERMINADA})",
    )
    parser.add_argument(
        "--salida-json", type=Path, default=SALIDA_JSON_PREDETERMINADA,
        help=f"Resultados JSON (por defecto: {SALIDA_JSON_PREDETERMINADA})",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    parametros = ParametrosDiseno(
        recubrimiento_mm=args.recubrimiento_mm,
        designacion_barra=args.barra,
        diametro_barra_mm=(
            None if args.barra is None else BARRAS_INGLESAS_MM[args.barra]),
        designacion_barra_transversal=args.barra_transversal,
        diametro_barra_transversal_mm=(
            None if args.barra_transversal is None
            else BARRAS_INGLESAS_MM[args.barra_transversal]),
        longitud_estribo_m=args.longitud_estribo_m,
    )
    resultado = disenar(parametros)
    markdown = generar_markdown(resultado)
    args.salida_md.parent.mkdir(parents=True, exist_ok=True)
    args.salida_md.write_text(markdown, encoding="utf-8")
    args.salida_json.parent.mkdir(parents=True, exist_ok=True)
    args.salida_json.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Markdown: {args.salida_md.resolve()}")
    print(f"JSON: {args.salida_json.resolve()}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AGENTE DE ANÁLISIS DE SUBESTRUCTURA - PUENTE MOLINOHUAYCCO
============================================================
Implementa la metodología de análisis de subestructura según AASHTO LRFD 2005
y el enfoque seudo-estático de Mononobe-Okabe para cargas sísmicas.

Referencia: analisis_subestructura.md (Sección 3.2.6.6)
Aplica al: Puente Carrozable Molinohuaycco (H=11.90m, Estribo Izquierdo)
"""

import argparse
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


# ============================================================================
# CONFIGURACIÓN: PARÁMETROS DEL PUENTE MOLINOHUAYCCO
# ============================================================================

@dataclass
class AbutmentGeometry:
    """Geometría del estribo - Referencia: analisis_subestructura.md (Sec. 3.2.6.6.2)
    Fuente: Memoria de Cálculo Estructural Estribo derecho, Fig. 3.44
    Valores confirmados del Puente Molinohuaico.
    """
    # Dimensiones principales
    H: float = 17.65 #14.64 #11.90                # Altura total del estribo, Figura 3.44 (m)
    hp: float = 16.15 #13.14 #10.40               # Altura de pantalla, Figura 3.44 (m)
    hz: float = 1.50                # Altura de la zapata (m)
    B: float = 11.95                # Ancho total de la base (m)
    B1: float = 6.10                # Talón posterior (m) - de canto a cara posterior pantalla
    B2: float = 5.45                # Punta (m) - de canto a cara anterior pantalla
    tp1: float = 0.40               # Espesor superior de pantalla (m)
    tp2: float = 0.40 #0.40               # Espesor inferior de pantalla (m)
    ancho_estribo: float = 1.00     # Ancho de análisis (por metro lineal)
    # Cajuela (asiento de viga) - Figura 3.44
    a_cajuela: float = 1.300        # Ancho libre de asiento de la cajuela (m)
    b_cajuela: float = 0.400        # Espesor de pared vertical de cajuela (m)
    c_cajuela: float = 2.350        # Altura de pared vertical de cajuela (m)
    d_cajuela: float = 1.000        # Altura de base de cajuela (m)
    e_cajuela: float = 0.800        # Vuelo posterior de base hacia el talón B1 (m)
    f_cajuela: float = 0.500        # Vuelo delantero de base hacia la punta B2 (m)
    g_cajuela: float = 0.550        # Holgura/asiento interior de cajuela, no suma área de concreto (m)
    # Inclinación de la cara posterior del muro
    back_face_slope: float = 0.0    # Desplazamiento horizontal por metro de altura (m/m)
                                    # 0 = vertical, >0 = inclinación hacia el relleno (reduce ancho de relleno en coronación)
                                    # Ej: para la referencia con B1=3.80, hp=10.00, A=35.64 → slope = 0.0472


@dataclass
class MaterialProperties:
    """Propiedades de materiales y suelo (Paso 3 - confirmados)
    Fuente: Memoria de Cálculo Estructural Estribo Izquierdo, Sec. 3.2.6.6.3
    + Estudio de Suelos (GW - grava limosa).
    """
    # Concreto
    gamma_c: float = 2.40           # Peso específico del concreto armado (Tn/m3)
    f_c: float = 280.0              # Resistencia a compresión (kg/cm2)
    fy: float = 4200.0              # Resistencia del acero (kg/cm2)
    # Relleno
    gamma_r: float = 1.80           # Peso específico del relleno (Tn/m3)
    phi_relleno: float = 39.8       # Ángulo de fricción interna - relleno (grados)
    delta: float = 19.9             # Ángulo de fricción muro-suelo (φ/2 = 19.9°)
    # Suelo de fundación (Estribo Izquierdo - GW)
    gamma_suelo: float = 1.96       # Peso específico del suelo de fundación (Tn/m3)
    phi_base: float = 39.8          # Ángulo de fricción interna - base (grados) φ'
    cohesion: float = 0.0           # Cohesión (kg/cm2) - GW sin cohesión
    mu: float = 0.55                # Coef. fricción concreto-suelo
    capacidad_portante: float = 3.67  # Capacidad portante admisible (kg/cm2)
    capacidad_portante_factorizada: float | None = None
                                    # Resistencia geotécnica factorizada (kg/cm2)


@dataclass
class SuperstructureLoads:
    """Cargas de la superestructura que llegan al estribo (Paso 5 - actualizado)
    Fuente: metrado_tablero.py con parámetros confirmados (ver
    registro_verificacion_datos_3.1_a_3.4.md).
    Longitud del estribo = 6.00 m. Los valores por metro se obtienen dividiendo
    la reacción total entre 6.0 m.
    """
    L: float = 50.00                # Luz del puente (m)
    ancho_distribucion: float = 1.00  # Ancho de análisis (por metro lineal)
    # Reacciones totales (para toda la longitud del estribo = 6.0 m)
    R_DL_total: float = 173.15      # Reacción total DC + DW (Tn) [155.90 + 17.25]
    R_LL_total: float = 77.71       # Reacción total LL+IM (Tn) [metrado_tablero]
    R_BR_total: float = 9.80        # Reacción total por frenado (Tn) [metrado_tablero]
    # Reacciones por metro de ancho (estribo ÷ 6.0 m)
    DC: float = 25.98               # Peso propio superestructura (Tn/m) [155.90/6.0]
    DW: float = 2.88                # Superficie de desgaste (Tn/m) [17.25/6.0]
    PL: float = 3.08                # Carga peatonal (Tn/m) [18.50/6.0]
    LL_IM: float = 12.95            # Sobrecarga HL-93 + IM (Tn/m) [77.71/6.0]
    BR: float = 1.63                # Frenado (Tn/m) [9.80/6.0]
    # Brazo de aplicación (desde punta, eje de apoyo viga)
    # Valores por defecto: confirmados del Puente Molinohuaico (Cuadros Nº 40 y 41).
    # Si se desea auto-derivar desde geometría, fijar como None.
    brazo_super: float | None = None   # Distancia horizontal desde la punta (m)
                                       # None = auto: compute_brazo_super(geom)
    brazo_BR: float | None = None     # Altura de frenado desde base (m)
                                      # None = auto: compute_brazo_BR(geom) = H + 0.90
    brazo_EQ_super: float | None = None
                                    # Altura del centro de masa de superestructura (m)
                                    # desde la base. None = auto-calcular desde geometría
                                    # con compute_eq_super_brazo(geom).


@dataclass
class SeismicParameters:
    """Parámetros de diseño sísmico según MTC - Puente Molinohuaico
    Fuente: MTC Manual de Puentes 2018, Anexo I + E.030 + Estudio de Suelos.
    Zona 2, Perfil S2, Pilar tipo placa (R=1.50, MTC Tabla 2.3).
    """
    A: float = 0.25                 # Coeficiente de aceleración (Ayacucho - Zona 2)
    S: float = 1.20                 # Coeficiente de sitio (Perfil S2)
    R: float = 1.50                 # Factor de modificación de respuesta (Pilar tipo placa)
    Kh: float = 0.125               # Coeficiente sísmico horizontal (A/2, MTC recomendación)
    Kv: float = 0.05                # Coeficiente sísmico vertical (0.00-0.05)


@dataclass
class FalseFootingProperties:
    """Geometría y propiedades de la falsa zapata bajo el estribo.

    Los valores por defecto corresponden al esquema geotécnico vigente usado
    en este proyecto. ``offset_from_toe`` permite representar una falsa zapata
    no centrada; si es ``None`` se adopta centrada bajo la zapata estructural.
    """
    enabled: bool = True
    height: float = 3.50            # Espesor vertical (m), Figuras 4/5
    width: float = 11.95            # Ancho en la sección analizada (m)
    gamma: float = 2.30             # Peso específico (Tn/m3), asumido preliminar
    f_c: float = 140.0              # Resistencia del concreto base (kg/cm2)
    # Junta zapata–falsa zapata: concreto nuevo contra concreto endurecido,
    # superficie limpia y no rugosa intencionalmente.
    concrete_contact_mu: float = 0.60
    concrete_compression_phi: float = 1.00  # Pendiente de confirmar normativamente
    soil_contact_mu: float | None = None    # None = usar MaterialProperties.mu
    offset_from_toe: float | None = None

    def validate(self, structural_width: float) -> None:
        if self.height <= 0 or self.width <= 0:
            raise ValueError("La altura y el ancho de la falsa zapata deben ser positivos")
        if self.width < structural_width:
            raise ValueError(
                "La falsa zapata no puede ser más angosta que la zapata estructural "
                "en este modelo rígido"
            )
        if self.gamma <= 0 or self.f_c <= 0:
            raise ValueError("El peso específico y f'c de la falsa zapata deben ser positivos")
        if not 0 < self.concrete_contact_mu <= 1:
            raise ValueError("El coeficiente de fricción concreto-concreto debe estar entre 0 y 1")
        offset = self.structural_offset(structural_width)
        if offset < 0 or offset + structural_width > self.width:
            raise ValueError("La zapata estructural debe quedar dentro de la falsa zapata")

    def structural_offset(self, structural_width: float) -> float:
        """Distancia desde la punta de la falsa zapata a la punta estructural."""
        if self.offset_from_toe is not None:
            return self.offset_from_toe
        return (self.width - structural_width) / 2.0


# ============================================================================
# INSTANCIAS DE CONFIGURACIÓN (datos confirmados)
# ============================================================================

GEOM = AbutmentGeometry()
MAT = MaterialProperties()
LOADS = SuperstructureLoads()
SEISMIC = SeismicParameters()
FALSE_FOOTING = FalseFootingProperties()

LIMIT_STATE_KEYS = (
    'case_service_I',
    'case_resistance_Ia',
    'case_resistance_Ib',
    'case_extreme_event_I',
)
STABILITY_NOT_APPLICABLE = 'NO APLICA - VERIFICACION SOLO EN SERVICIO I (MTC)'


# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0


def rad2deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def compute_eq_super_brazo(geom: 'AbutmentGeometry') -> float:
    """
    Altura del centro de masa de la superestructura desde la base (m).

    Se estima como la altura del asiento del apoyo dentro de la cajuela:
    el apoyo se ubica en la superficie de la base de la cajuela, cuyo
    centroide vertical está a media altura de dicha base desde el fondo
    de la cajuela. Matemáticamente:

        brazo_EQ_super = hz + hp - c_cajuela - d_cajuela/2

    Para el Puente Molinohuaico: 1.50+10.40-2.35-0.50 = 9.05 m
    (Memoria Cuadro Nº 41: 9.08 m, diferencia despreciable por espesor del apoyo).

    Si se requiere un valor distinto, puede fijarse manualmente en
    SuperstructureLoads.brazo_EQ_super.
    """
    return geom.hz + geom.hp - geom.c_cajuela - geom.d_cajuela / 2.0


def compute_brazo_super(geom: 'AbutmentGeometry') -> float:
    """
    Posición horizontal del centro del asiento del apoyo (bearing)
    desde la punta del estribo (m).

    El bearing se ubica sobre la base de la cajuela, dentro del
    ancho libre de asiento (a_cajuela). Se asume que el bearing
    está centrado en dicho asiento.

    La cara frontal de la base de la cajuela está en:
        x_front = B2 - f_cajuela

    Por tanto el centro del asiento está en:
        brazo_super = (B2 - f_cajuela) + a_cajuela / 2

    Para el Puente Molinohuaico el valor confirmado es 2.98 m
    (Cuadro Nº 40 de la memoria). El valor calculado con esta
    función puede diferir si el bearing no está centrado en el
    asiento; en ese caso debe fijarse manualmente en
    SuperstructureLoads.brazo_super.
    """
    x_front_base = geom.B2 - geom.f_cajuela
    return x_front_base + geom.a_cajuela / 2.0


def compute_brazo_BR(geom: 'AbutmentGeometry') -> float:
    """
    Altura de aplicación de la fuerza de frenado desde la base (m).

    Se estima como H + 0.90 m, donde 0.90 m representa la altura
    típica de la superestructura (losa + viga + altura libre)
    sobre la coronación del estribo, según AASHTO LRFD.

    Para el Puente Molinohuaico: H=11.90 → brazo_BR = 12.80 m
    (Cuadro Nº 41 de la memoria).
    """
    return geom.H + 0.90


def get_surcharge_height(H: float) -> float:
    """
    Altura equivalente de sobrecarga vehicular (m) según AASHTO LRFD
    Tabla 3.11.6.4-1 (equivalente a MTC Manual de Puentes).

    La sobrecarga depende de la altura total del estribo H:
        H ≤ 1.50 m  → h = 1.22 m
        1.50 < H ≤ 3.00 m → h = 0.91 m
        3.00 < H ≤ 6.00 m → h = 0.76 m  (MTC: 0.61 m)
        H > 6.00 m  → h = 0.61 m
    """
    if H <= 1.50:
        return 1.22
    elif H <= 3.00:
        return 0.91
    elif H <= 6.00:
        return 0.76
    else:
        return 0.61


def coulomb_active_coefficient(phi: float, delta: float, theta_w: float = 90.0,
                                beta: float = 0.0, alpha: float = 0.0) -> float:
    """
    Coeficiente de empuje activo - Teoría de Coulomb
    (Ecuación 3.2.6.6.3-b del manual)
    """
    phi_r = deg2rad(phi)
    delta_r = deg2rad(delta)
    theta_r = deg2rad(theta_w)
    beta_r = deg2rad(beta)
    alpha_r = deg2rad(alpha)

    num = math.sin(theta_r + phi_r) ** 2
    den1 = math.sin(theta_r) ** 2 * math.sin(theta_r - delta_r)
    sqrt_term = (
        math.sin(phi_r + delta_r) * math.sin(phi_r - beta_r) /
        (math.sin(theta_r - delta_r) * math.sin(theta_r + beta_r))
    ) ** 0.5
    den2 = (1 + sqrt_term) ** 2
    Ka = num / (den1 * den2)
    return Ka


def mononobe_okabe_coefficient(phi: float, delta: float, theta_seis: float,
                                theta_w: float = 90.0, beta: float = 0.0,
                                alpha: float = 0.0) -> float:
    """
    Coeficiente de empuje activo con sismo - Mononobe-Okabe
    Incluye efecto estático + dinámico
    """
    phi_r = deg2rad(phi)
    delta_r = deg2rad(delta)
    theta_s = deg2rad(theta_seis)
    theta_r = deg2rad(theta_w)
    beta_r = deg2rad(beta)
    alpha_r = deg2rad(alpha)

    num = math.cos(phi_r - alpha_r - theta_s) ** 2
    den1 = math.cos(theta_s) * (math.cos(alpha_r) ** 2) * math.cos(delta_r + alpha_r + theta_s)
    sqrt_term = (
        math.sin(phi_r + delta_r) * math.sin(phi_r - beta_r - theta_s) /
        (math.cos(delta_r + alpha_r + theta_s) * math.cos(beta_r - alpha_r))
    ) ** 0.5
    den2 = (1 + sqrt_term) ** 2
    Kas = num / (den1 * den2)
    return Kas


def cajuela_area_and_centroid(g: 'AbutmentGeometry',
                               brazo_super: float | None = None) -> Tuple[float, float, float]:
    """
    Calcula el área y centroide de la cajuela según la Figura 3.44:
        A_base = (e + tp1 + f) * d
        A_pared = b * c

    Args:
        g: Geometría del estribo (AbutmentGeometry)
        brazo_super: Distancia desde la punta al eje de viga (m). No
            se usa en el cálculo (solo para compatibilidad de firma).
            Puede ser None.

    Returns:
        Tuple[area, brazo_desde_punta, centroide_y_desde_base]

        ``centroide_y_desde_base`` ya incluye el espesor ``hz`` de la
        zapata; no debe trasladarse verticalmente otra vez en el llamador.
    """
    b = g.b_cajuela
    c = g.c_cajuela
    d = g.d_cajuela
    e = g.e_cajuela
    f = g.f_cajuela

    base_width = e + g.tp1 + f
    A_base = base_width * d
    A_pared = b * c
    area = A_base + A_pared
    if area <= 1e-12:
        return 0.0, 0.0, 0.0

    # Eje horizontal del script: desde la punta hacia el talón.
    # La base va desde la cara frontal (B2 - f) hasta la posterior
    # (B2 + tp1 + e). La pared b*c se ubica en el extremo posterior.
    x_front_base = g.B2 - f
    x_back_base = g.B2 + g.tp1 + e
    x_base = x_front_base + base_width / 2.0
    x_pared = x_back_base - b / 2.0

    y_origin = g.hz + max(g.hp - (c + d), 0.0)
    y_base = y_origin + d / 2.0
    y_pared = y_origin + d + c / 2.0

    x_centroid = (A_base * x_base + A_pared * x_pared) / area
    y_centroid = (A_base * y_base + A_pared * y_pared) / area

    return area, x_centroid, y_centroid


def polygon_area_and_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float, float]:
    """Area y centroide de un poligono simple."""
    if len(points) < 3:
        return 0.0, 0.0, 0.0

    twice_area = 0.0
    cx_term = 0.0
    cy_term = 0.0
    for i, (x0, y0) in enumerate(points):
        x1, y1 = points[(i + 1) % len(points)]
        cross = x0 * y1 - x1 * y0
        twice_area += cross
        cx_term += (x0 + x1) * cross
        cy_term += (y0 + y1) * cross

    area_signed = twice_area / 2.0
    area = abs(area_signed)
    if area <= 1e-12:
        return 0.0, 0.0, 0.0

    cx = cx_term / (6.0 * area_signed)
    cy = cy_term / (6.0 * area_signed)
    return area, cx, cy


def fill_trapezoid_area_and_centroid(B1: float, hp: float, slope: float,
                                      B2: float, tp2: float,
                                      cajuela_recess: float = 0.0,
                                      cajuela_height: float = 0.0) -> Tuple[float, float, float]:
    """
    Calcula el área y el centroide del relleno sobre el talón considerando
    la inclinación de la cara posterior del muro.

    La cara posterior del muro se inclina hacia el relleno según el parámetro
    `slope` (desplazamiento horizontal por metro de altura).
    El relleno está limitado por:
      - Cara posterior del muro (inclinada)
      - Plano vertical en el extremo del talón
      - Base (cabeza de zapata)
      - Coronación del muro
      - Muesca superior ocupada por la cajuela, si se indica

    Args:
        B1: Ancho del talón posterior (m)
        hp: Altura de la pantalla (m)
        slope: Inclinación de la cara posterior (m/m, >0 = hacia el relleno)
        B2: Ancho de la punta (m, solo para brazo)
        tp2: Espesor inferior de pantalla (m, solo para brazo)
        cajuela_recess: Profundidad horizontal de la cajuela hacia el talón (m)
        cajuela_height: Altura de la muesca superior de cajuela (m)

    Returns:
        Tuple[area, brazo_desde_punta, width_top_efectivo]
    """
    # Ancho del relleno en la base
    w_base = B1
    # Ancho del relleno en la coronación (reducido si slope > 0)
    w_top = max(B1 - slope * hp, 0.0)
    cajuela_recess = max(min(cajuela_recess, w_top), 0.0)
    cajuela_height = max(min(cajuela_height, hp), 0.0)

    x_left_top = B1 - w_top
    y_notch = hp - cajuela_height
    x_left_notch = slope * y_notch

    # Poligono local: x=0 en la cara posterior de la pantalla en la base,
    # x positivo hacia el extremo del talon. La muesca evita contar relleno
    # donde se ubica la cajuela y su espacio libre.
    if cajuela_recess > 0.0 and cajuela_height > 0.0:
        points = [
            (0.0, 0.0),
            (B1, 0.0),
            (B1, hp),
            (x_left_top + cajuela_recess, hp),
            (x_left_notch + cajuela_recess, y_notch),
            (x_left_notch, y_notch),
        ]
        w_top_effective = max(w_top - cajuela_recess, 0.0)
    else:
        points = [
            (0.0, 0.0),
            (B1, 0.0),
            (B1, hp),
            (x_left_top, hp),
        ]
        w_top_effective = w_top

    area, x_bar, _ = polygon_area_and_centroid(points)

    # Brazo desde la punta (punto O)
    brazo = B2 + tp2 + x_bar

    return area, brazo, w_top_effective


def active_earth_pressure(gamma: float, H: float, Ka: float,
                           h_surcharge: float = 0.0, width: float = 1.0) -> Tuple[float, float]:
    """
    Empuje activo y su punto de aplicación desde la base.

    Si h_surcharge > 0, devuelve el empuje activo combinado con la sobrecarga.
    En la metodología de analisis_subestructura.md se usa h_surcharge = 0 para Ea
    y se calcula Es por separado.
    
    Returns:
        Ea: Fuerza horizontal total (Tn)
        d_aplicacion: Distancia desde la base (m)
    """
    Ea = 0.5 * gamma * H * (H + 2 * h_surcharge) * Ka * width
    if H + 2 * h_surcharge > 0:
        d = (H / 3) * (H + 3 * h_surcharge) / (H + 2 * h_surcharge)
    else:
        d = H / 3
    return Ea, d


def passive_earth_pressure(gamma: float, hr: float, Cp: float,
                            width: float = 1.0) -> float:
    """Empuje pasivo del terreno"""
    Ep = 0.5 * gamma * (hr ** 2) * Cp * width
    return Ep


def passive_coefficient(phi: float) -> float:
    """Coeficiente de empuje pasivo (Rankine)"""
    phi_r = deg2rad(phi)
    Kp = math.tan(45 * math.pi / 180 + phi_r / 2) ** 2
    return Kp


def surcharge_earth_pressure(gamma: float, H: float, Ka: float,
                              h_surcharge: float, width: float = 1.0) -> Tuple[float, float]:
    """Empuje horizontal debido a la sobrecarga"""
    Es = gamma * H * Ka * h_surcharge * width
    d = H / 2.0
    return Es, d


# ============================================================================
# CLASE PRINCIPAL DE ANÁLISIS
# ============================================================================

class SubstructureAnalysis:
    """
    Analizador de subestructura de puente.
    Implementa el flujo completo: geometría -> cargas -> verificación -> diseño.
    """

    def __init__(self, geom: AbutmentGeometry, mat: MaterialProperties,
                 loads: SuperstructureLoads, seismic: SeismicParameters,
                 false_footing: FalseFootingProperties | None = None):
        self.geom = geom
        self.mat = mat
        self.loads = loads
        self.seismic = seismic
        self.false_footing = false_footing
        if false_footing is not None and false_footing.enabled:
            false_footing.validate(geom.B)
        self.results = {}

    def compute_false_footing_weight(self) -> dict:
        """Peso propio de la falsa zapata por el ancho de análisis."""
        fz = self.false_footing
        if fz is None or not fz.enabled:
            return {'enabled': False, 'weight': 0.0, 'detail': None}
        weight = fz.width * fz.height * self.geom.ancho_estribo * fz.gamma
        detail = {
            'tipo': 'DC',
            'desc': 'Falsa zapata',
            'peso': round(weight, 3),
            'brazo': round(fz.width / 2.0, 3),
            'momento': round(weight * fz.width / 2.0, 3),
            'y_cg': round(fz.height / 2.0, 3),
        }
        return {'enabled': True, 'weight': weight, 'detail': detail}

    def check_false_footing_load_spread(self) -> dict:
        """Chequeo geométrico preliminar de difusión 1V:1H.

        No sustituye las verificaciones de flexión, corte o punzonamiento del
        concreto masivo, que requieren geometría tridimensional y resistencias
        de diseño adicionales.
        """
        fz = self.false_footing
        if fz is None or not fz.enabled:
            return {'status': 'NO APLICA'}
        toe = fz.structural_offset(self.geom.B)
        heel = fz.width - self.geom.B - toe
        max_overhang = max(toe, heel)
        if max_overhang <= 1e-12:
            status = 'NO APLICA - SIN VUELO'
            ratio = None
        else:
            ratio = fz.height / max_overhang
            status = 'CONFORME PRELIMINAR' if ratio >= 1.0 else 'NO CONFORME'
        return {
            'toe_overhang': round(toe, 3),
            'heel_overhang': round(heel, 3),
            'height_to_max_overhang': (
                None if ratio is None else round(ratio, 3)),
            'criterion': 'difusión geométrica mínima 1V:1H (preliminar)',
            'status': status,
            'flexure_shear_punching': 'PENDIENTE DE VERIFICACION ESTRUCTURAL',
        }

    def compute_weights_and_moments(self) -> dict:
        """
        Calcula pesos estabilizadores y sus momentos respecto al punto "O"
        (arista inferior de la base en el extremo de la punta - pie del talón delantero)

        Paso 4 - Memoria: Estribo izquierdo, por metro de ancho.
        Punto O en la punta (cara anterior de la zapata).
        Distancia de referencia: desde la punta hacia el talón (hacia atrás).
        Incluye altura del centro de gravedad (y_cg) sobre la base para fuerzas sísmicas.
        """
        g = self.geom
        m = self.mat

        # Almacenamos (tipo, desc, peso, brazo_horiz, brazo_vert)
        # brazo_vert = altura del CG desde la base (m), usado para fuerzas sísmicas
        sections = []

        # --- DC: Peso propio del estribo ---
        # Zapata (rectángulo)
        A_zapata = g.B * g.hz
        peso_zapata = A_zapata * m.gamma_c
        brazo_zapata = g.B / 2.0            # horizontal desde punta
        y_cg_zapata = g.hz / 2.0            # vertical desde base
        sections.append(('DC', 'Zapata', peso_zapata, brazo_zapata, y_cg_zapata))

        # Pantalla - tronco trapezoidal (desde base hasta bajo la cajuela)
        # En la Figura 3.44 la cajuela ocupa la corona con altura c + d.
        h_cajuela_total = g.c_cajuela + g.d_cajuela
        h_stem = max(g.hp - h_cajuela_total, 0.0)
        if h_stem > 0:
            # Ancho del tronco en la base de la cajuela (coronación del tronco)
            if g.tp1 != g.tp2:
                # Proporción lineal para pared ahusada
                w_coronacion = g.tp2 - (g.tp2 - g.tp1) * h_stem / g.hp
            else:
                w_coronacion = g.tp1  # espesor constante
            A_tronco = (g.tp2 + w_coronacion) / 2.0 * h_stem
            peso_tronco = A_tronco * m.gamma_c
            x_c_tronco = (g.tp2**2 + g.tp2*w_coronacion + w_coronacion**2) / (3.0 * (g.tp2 + w_coronacion))
            brazo_tronco = g.B2 + g.tp2 - x_c_tronco
            # Centroide vertical del trapecio desde su base (cara superior de zapata)
            y_tronco_base = h_stem * (g.tp2 + 2*w_coronacion) / (3.0 * (g.tp2 + w_coronacion))
            # Altura desde la base de la zapata
            y_cg_tronco = g.hz + y_tronco_base
            sections.append(('DC', 'Tronco pantalla', peso_tronco, brazo_tronco, y_cg_tronco))
        else:
            w_coronacion = g.tp1
            y_cg_tronco = 0.0

        # Cajuela (asiento de viga) - corona del estribo
        # El parámetro brazo_super no se usa en el cálculo, se pasa None
        A_cajuela, brazo_cajuela, y_cg_cajuela = cajuela_area_and_centroid(g)
        peso_cajuela = A_cajuela * m.gamma_c
        # y_cg_cajuela ya está referido a la cara inferior de la zapata.
        sections.append(('DC', 'Cajuela (asiento viga)', peso_cajuela, brazo_cajuela, y_cg_cajuela))

        # --- EV: Peso del relleno sobre el talón ---
        # Calculado considerando la inclinación de la cara posterior y recortando
        # la muesca superior ocupada por la cajuela.
        A_relleno, brazo_relleno, w_top = fill_trapezoid_area_and_centroid(
            g.B1,
            g.hp,
            g.back_face_slope,
            g.B2,
            g.tp2,
            cajuela_recess=g.e_cajuela,
            cajuela_height=h_cajuela_total,
        )
        peso_relleno = A_relleno * m.gamma_r
        # El relleno no genera inercia sísmica (EV), brazo_vert = 0
        sections.append(('EV', 'Relleno sobre talón', peso_relleno, brazo_relleno, 0.0))

        # --- LS: Sobrecarga del terreno ---
        # Altura equivalente de sobrecarga según AASHTO LRFD Tabla 3.11.6.4-1
        h_sc = get_surcharge_height(g.H)  # m, función de H
        # La sobrecarga se aplica sobre la superficie del relleno
        # usando el ancho superior del trapecio de relleno (w_top en coronación)
        A_sc = h_sc * w_top
        peso_sc = A_sc * m.gamma_r
        # Centroide horizontal: desde la punta = B2 + tp2 + offset_posterior + w_top/2
        # offset_posterior = B1 - w_top (contracción del trapecio en coronación)
        brazo_sc = g.B2 + g.tp2 + (g.B1 - w_top) + w_top / 2.0
        # LS no genera inercia sísmica, brazo_vert = 0
        sections.append(('LS', 'Sobrecarga terreno', peso_sc, brazo_sc, 0.0))

        # --- Cálculo total ---
        total_weight = 0
        total_moment = 0
        total_momento_vert_DC = 0.0
        total_peso_DC = 0.0
        weights_detail = []

        for item in sections:
            load_type, desc, peso, brazo, y_cg = item
            momento = peso * brazo
            total_weight += peso
            total_moment += momento
            # Acumular vertical CG solo para componentes DC (inercia sísmica)
            if load_type == 'DC':
                total_peso_DC += peso
                total_momento_vert_DC += peso * y_cg
            weights_detail.append({
                'tipo': load_type, 'desc': desc,
                'peso': round(peso, 2), 'brazo': round(brazo, 3),
                'momento': round(momento, 2),
                'y_cg': round(y_cg, 3)
            })

        # Centroide vertical del estribo (solo DC) desde la base
        y_cg_DC = total_momento_vert_DC / total_peso_DC if total_peso_DC > 0 else 0.0

        return {
            'total_weight': round(total_weight, 2),
            'total_moment': round(total_moment, 2),
            # Valores sin redondear para los cálculos sísmicos posteriores.
            # Los campos redondeados se conservan para presentación.
            'peso_DC_calculo': total_peso_DC,
            'momento_vert_DC_calculo': total_momento_vert_DC,
            'y_cg_DC': round(y_cg_DC, 2),  # altura del CG del estribo desde la base (m)
            'detail': weights_detail
        }

    def compute_superstructure_reactions(self) -> dict:
        """
        Reacciones de la superestructura por metro de ancho (Paso 5)
        Fuente: Anexo 3 - Memoria de Cálculo Estructural de Estribo Izquierdo y Alas

        Los brazos brazo_super y brazo_BR se auto-derivan desde la geometría
        del estribo si no fueron fijados manualmente en SuperstructureLoads.
        """
        ls = self.loads
        g = self.geom

        # Resolver brazo_super: manual si está fijado, o auto desde geometría
        brazo_super = ls.brazo_super if ls.brazo_super is not None else compute_brazo_super(g)
        brazo_BR = ls.brazo_BR if ls.brazo_BR is not None else compute_brazo_BR(g)

        reacciones = []
        for tipo, desc, reac in [('DC', 'Peso Propio', ls.DC),
                                  ('DW', 'Superf. desgaste', ls.DW),
                                  ('PL', 'Carga peatonal', ls.PL),
                                  ('LL+IM', 'Sobrecarga HL-93', ls.LL_IM)]:
            momento = reac * brazo_super
            reacciones.append({
                'tipo': tipo, 'desc': desc,
                'reaccion': round(reac, 2), 'brazo': round(brazo_super, 2),
                'momento': round(momento, 2)
            })

        # Frenado: fuerza horizontal a altura H + 0.90 m
        reacciones.append({
            'tipo': 'BR', 'desc': 'Frenado',
            'reaccion': round(ls.BR, 2), 'brazo': round(brazo_BR, 2),
            'momento': round(ls.BR * brazo_BR, 2)
        })

        return {
            'reactions': reacciones,
            'brazo': round(brazo_super, 2)
        }

    def compute_seismic_forces(self, estabilizadoras: dict,
                               reference_depth: float = 0.0,
                               false_footing_weight: dict | None = None) -> dict:
        """
        Fuerzas desestabilizadoras por sismo (24% del peso propio según MTC)
        Paso 8 - Memoria
        """
        s = self.seismic
        ls = self.loads
        g = self.geom
        m = self.mat
        porcentaje = 1.20 * (s.A * s.S / s.R) * 100  # = 24%

        # --- Fuerzas de superestructura ---
        # Peso vertical que genera inercia: solo DC + DW (no PL)
        peso_super_sismo = (ls.DC + ls.DW)  # por m
        Fq_super = peso_super_sismo * porcentaje / 100  # Tn/m
        # Brazo de la fuerza sísmica de la superestructura sobre la base.
        # Si el usuario fijó brazo_EQ_super, se usa ese valor;
        # si es None, se auto-calcula desde la geometría del estribo.
        if ls.brazo_EQ_super is not None:
            brazo_Fq_super = ls.brazo_EQ_super
        else:
            brazo_Fq_super = compute_eq_super_brazo(g)
        brazo_Fq_super += reference_depth
        momento_Fq_super = Fq_super * brazo_Fq_super

        # --- Fuerzas del estribo ---
        # Solo componente DC (EV y LS no generan inercia sísmica)
        peso_DC_estribo = estabilizadoras.get(
            'peso_DC_calculo',
            sum(d['peso'] for d in estabilizadoras['detail'] if d['tipo'] == 'DC')
        )
        Fq_estribo = peso_DC_estribo * porcentaje / 100
        # Centro de gravedad VERTICAL del estribo (solo DC) desde la base.
        # El brazo para la fuerza sísmica horizontal es la ALTURA del CG,
        # NO la distancia horizontal desde la punta.
        # Memoria Cuadro Nº 42: 2.43 m (vertical CG del estribo).
        momento_vert_DC = estabilizadoras.get('momento_vert_DC_calculo')
        if momento_vert_DC is not None and peso_DC_estribo > 0:
            brazo_Fq_estribo = momento_vert_DC / peso_DC_estribo
            momento_Fq_estribo = momento_vert_DC * porcentaje / 100
        else:
            brazo_Fq_estribo = estabilizadoras.get('y_cg_DC', 2.43)
            momento_Fq_estribo = Fq_estribo * brazo_Fq_estribo
        brazo_Fq_estribo += reference_depth
        momento_Fq_estribo = Fq_estribo * brazo_Fq_estribo

        # --- Frenado (horizontal) ---
        Fq_BR = ls.BR  # Tn/m, horizontal
        brazo_Fq_BR = ls.brazo_BR if ls.brazo_BR is not None else compute_brazo_BR(g)
        brazo_Fq_BR += reference_depth
        momento_Fq_BR = Fq_BR * brazo_Fq_BR

        fz_force = None
        if false_footing_weight and false_footing_weight.get('enabled'):
            detail = false_footing_weight['detail']
            force = false_footing_weight['weight'] * porcentaje / 100.0
            arm = detail['y_cg']
            fz_force = {
                'peso': round(force, 2),
                'brazo': round(arm, 2),
                'momento': round(force * arm, 2),
            }

        return {
            'porcentaje': round(porcentaje, 1),
            'superestructura': {
                'peso': round(Fq_super, 2),
                'brazo': round(brazo_Fq_super, 2),
                'momento': round(momento_Fq_super, 2)
            },
            'estribo': {
                'peso': round(Fq_estribo, 2),
                'brazo': round(brazo_Fq_estribo, 2),
                'momento': round(momento_Fq_estribo, 2)
            },
            'frenado': {
                'peso': round(Fq_BR, 2),
                'brazo': round(brazo_Fq_BR, 2),
                'momento': round(momento_Fq_BR, 2)
            },
            'falsa_zapata': fz_force,
        }

    def compute_earth_pressures(self, analysis_height: float | None = None) -> dict:
        """
        Cálculo de empujes de tierra (Coulomb y Mononobe-Okabe)
        Pasos 7 y 8 - Memoria
        """
        g = self.geom
        m = self.mat
        H = g.H if analysis_height is None else analysis_height
        if H <= 0:
            raise ValueError("La altura de análisis de empujes debe ser positiva")
        h_surcharge = get_surcharge_height(H)  # m (AASHTO LRFD Tabla 3.11.6.4-1)

        # --- Coeficiente de empuje activo - Coulomb ---
        Ka = coulomb_active_coefficient(
            phi=m.phi_relleno, delta=m.delta,
            theta_w=90.0, beta=0.0, alpha=0.0
        )

        # --- Empuje activo estático SIN sobrecarga ---
        Ea, d_Ea = active_earth_pressure(
            m.gamma_r, H, Ka, 0.0
        )

        # --- Coeficiente de empuje pasivo ---
        Kp = passive_coefficient(m.phi_base)
        # El pasivo frente a la cimentación se moviliza en el suelo de
        # fundación, no en el relleno del trasdós. Por ello se emplean sus
        # parámetros geotécnicos: γ_suelo y φ_base.
        Ep = passive_earth_pressure(m.gamma_suelo, g.hz, Kp)

        # --- Empuje por sobrecarga ---
        Es, d_Es = surcharge_earth_pressure(
            m.gamma_r, H, Ka, h_surcharge
        )

        # --- SISMO: Mononobe-Okabe ---
        s = self.seismic
        psi = math.atan2(s.Kh, 1 - s.Kv)
        psi_deg = rad2deg(psi)

        Kas = mononobe_okabe_coefficient(
            phi=m.phi_relleno, delta=m.delta,
            theta_seis=psi_deg, theta_w=90.0,
            beta=0.0, alpha=0.0
        )

        Eas = 0.5 * m.gamma_r * (H ** 2) * (1 - s.Kv) * Kas
        delta_Eas = Eas - Ea
        d_delta_Eas = 2.0 * H / 3.0

        return {
            'Ka': round(Ka, 3),
            'Kp': round(Kp, 3),
            'Kas': round(Kas, 3),
            'h_surcharge': round(h_surcharge, 3),
            'psi_deg': round(psi_deg, 2),
            'analysis_height': round(H, 3),
            'Ea': {'valor': round(Ea, 2), 'brazo': round(d_Ea, 2),
                   'momento': round(Ea * d_Ea, 2)},
            'Ep': {'valor': round(Ep, 2)},
            'Es': {'valor': round(Es, 2), 'brazo': round(d_Es, 2),
                   'momento': round(Es * d_Es, 2)},
            'Eas': {'valor': round(Eas, 2)},
            'delta_Eas': {'valor': round(delta_Eas, 2),
                          'brazo': round(d_delta_Eas, 2),
                          'momento': round(delta_Eas * d_delta_Eas, 2)}
        }

    # ---- VERIFICACIONES DE ESTABILIDAD ----

    def check_overturning(self, M_estable: float, M_volteo: float,
                           V_total: float, B: float,
                           eccentricity_divisor: float = 6.0) -> dict:
        """
        Verifica estabilidad al volteo/excentricidad
        """
        Xo = (M_estable - M_volteo) / V_total if V_total > 0 else 0
        e = abs(B / 2 - Xo)
        limit = B / eccentricity_divisor
        chequeo = "CONFORME" if e <= limit else "NO CONFORME"
        chequeo_B6 = "CONFORME" if e <= B / 6.0 else "NO CONFORME"
        limit_label = f"B/{eccentricity_divisor:g}"

        return {
            'Xo': round(Xo, 2),
            'e': round(e, 3),
            'B/6': round(B / 6.0, 3),  # compatibilidad con reportes existentes
            'e < B/6': chequeo_B6,
            'eccentricity_limit': round(limit, 3),
            'eccentricity_limit_label': limit_label,
            'eccentricity_check': chequeo,
            'M_estable': round(M_estable, 2),
            'M_volteo': round(M_volteo, 2),
            'V_total': round(V_total, 2)
        }

    def check_sliding(self, V_total: float, F_horizontal: float,
                       mu: float, phi_resist: float = 0.85) -> dict:
        """
        Verifica estabilidad al deslizamiento
        QR = phi * mu * V_total > F_horizontal
        """
        QR = phi_resist * mu * V_total
        chequeo = "CONFORME" if QR > F_horizontal else "NO CONFORME"

        return {
            'QR': round(QR, 2),
            'F_horizontal': round(F_horizontal, 2),
            'phi': phi_resist,
            'mu': mu,
            f'QR > Fh': chequeo
        }

    def check_bearing_capacity(self, V_total: float, e: float,
                                B: float, q_adm: float | None,
                                Xo: float | None = None,
                                method: str = 'linear') -> dict:
        """
        Distribución lineal elástica de presiones de contacto:
            q_max,min = V/B * (1 +/- 6e/B)

        La capacidad se verifica con q_max. Si q_min < 0, la solución elástica
        predice tracción y se reporta pérdida de contacto suelo-zapata.
        """
        e_abs = abs(e)
        if B <= 0:
            raise ValueError("El ancho de apoyo debe ser positivo")
        if method == 'meyerhof':
            effective_width = B - 2.0 * e_abs
            q_act = V_total / effective_width if effective_width > 0 else float('inf')
            q_act_kgcm2 = q_act / 10.0
            capacity_check = (
                'PENDIENTE - FALTA CAPACIDAD FACTORIZADA'
                if q_adm is None else
                ('CONFORME' if effective_width > 0 and q_act_kgcm2 <= q_adm
                 else 'NO CONFORME')
            )
            return {
                'q': round(q_act_kgcm2, 3),
                'q_max': round(q_act_kgcm2, 3),
                'q_min': 0.0,
                'q_max_t_m2': round(q_act, 3),
                'q_min_t_m2': 0.0,
                'q_promedio_t_m2': round(V_total / B, 3),
                'q_talon_t_m2': None,
                'q_punta_t_m2': None,
                'q_admisible': None if q_adm is None else round(q_adm, 2),
                'lado_q_max': 'area efectiva',
                'contacto': 'AREA EFECTIVA',
                'q_min >= 0': 'NO APLICA',
                'effective_width': round(effective_width, 3),
                'metodo': "Meyerhof q=V/[L(B-2e)], con L=1 m",
                'q <= q_adm': capacity_check,
            }
        if method != 'linear':
            raise ValueError(f"Método de presión no reconocido: {method}")
        q_prom = V_total / B if B > 0 else float('inf')
        ratio = 6.0 * e_abs / B if B > 0 else float('inf')
        q_max = q_prom * (1.0 + ratio)
        q_min = q_prom * (1.0 - ratio)
        q_max_kgcm2 = q_max / 10.0
        q_min_kgcm2 = q_min / 10.0
        chequeo = (
            'PENDIENTE - FALTA CAPACIDAD FACTORIZADA'
            if q_adm is None else
            ("CONFORME" if q_max_kgcm2 <= q_adm else "NO CONFORME")
        )
        contacto = "COMPLETO" if q_min >= 0 else "PERDIDA DE CONTACTO"

        # Orden de presiones en la convención gráfica: x=0 talón, x=B punta.
        if Xo is None:
            Xo = B / 2 - e_abs
        if Xo <= B / 2:  # resultante desplazada hacia la punta
            q_talon = q_min
            q_punta = q_max
            lado_max = "punta"
        else:  # resultante desplazada hacia el talón
            q_talon = q_max
            q_punta = q_min
            lado_max = "talon"

        return {
            'q': round(q_max_kgcm2, 3),
            'q_max': round(q_max_kgcm2, 3),
            'q_min': round(q_min_kgcm2, 3),
            'q_max_t_m2': round(q_max, 3),
            'q_min_t_m2': round(q_min, 3),
            'q_promedio_t_m2': round(q_prom, 3),
            'q_talon_t_m2': round(q_talon, 3),
            'q_punta_t_m2': round(q_punta, 3),
            'q_admisible': None if q_adm is None else round(q_adm, 2),
            'lado_q_max': lado_max,
            'contacto': contacto,
            'q_min >= 0': 'CONFORME' if q_min >= 0 else 'NO CONFORME',
            'metodo': 'distribucion lineal elastica q=V/B(1+/-6e/B)',
            'q <= q_adm': chequeo
        }

    # ---- COMBINACIONES DE CARGA ----

    @staticmethod
    def _factored_component(tipo: str, desc: str, nominal: float,
                            brazo: float, momento_nominal: float,
                            factor: float, origen: str,
                            distribucion: str = 'concentrada') -> dict:
        """Normaliza un componente para cálculo, figuras y auditoría."""
        return {
            'tipo': tipo,
            'desc': desc,
            'origen': origen,
            'distribucion': distribucion,
            'factor': factor,
            'nominal': round(nominal, 3),
            'valor': round(nominal * factor, 3),
            'brazo': round(brazo, 3),
            'momento_nominal': round(momento_nominal, 3),
            'momento': round(momento_nominal * factor, 3),
        }

    def _vertical_details(self, W: dict, Super: dict,
                          factors: dict[str, float]) -> list[dict]:
        details = []
        for d in W['detail']:
            f = factors.get(d['tipo'], 0.0)
            details.append(self._factored_component(
                d['tipo'], d['desc'], d['peso'], d['brazo'], d['momento'],
                f, 'estribo'))
        for r in Super['reactions']:
            if r['tipo'] == 'BR':
                continue
            f = factors.get(r['tipo'], 0.0)
            details.append(self._factored_component(
                r['tipo'], r['desc'], r['reaccion'], r['brazo'], r['momento'],
                f, 'superestructura'))
        return details

    def _lower_interface_vertical_inputs(self, W: dict, Super: dict,
                                         false_weight: dict) -> tuple[dict, dict]:
        """Traslada las cargas verticales al origen de la falsa zapata."""
        fz = self.false_footing
        if fz is None or not fz.enabled:
            raise ValueError("No existe una falsa zapata activa")
        offset = fz.structural_offset(self.geom.B)

        shifted_weight_details = []
        for d in W['detail']:
            item = dict(d)
            item['brazo'] = round(d['brazo'] + offset, 3)
            item['momento'] = round(d['peso'] * item['brazo'], 3)
            shifted_weight_details.append(item)
        shifted_weight_details.append(dict(false_weight['detail']))
        W2 = dict(W)
        W2['detail'] = shifted_weight_details

        shifted_reactions = []
        for r in Super['reactions']:
            item = dict(r)
            if r['tipo'] != 'BR':
                item['brazo'] = round(r['brazo'] + offset, 3)
                item['momento'] = round(r['reaccion'] * item['brazo'], 3)
            shifted_reactions.append(item)
        Super2 = dict(Super)
        Super2['reactions'] = shifted_reactions
        return W2, Super2

    def _finalize_case(self, name: str, fv_detail: list[dict],
                       fh_detail: list[dict], phi_slide: float,
                       extra: dict | None = None,
                       interface: dict | None = None,
                       verify_stability: bool = False) -> dict:
        """Calcula acciones y presiones; verifica estabilidad solo si procede.

        Las resultantes, la excentricidad y la distribución de presiones se
        conservan para todos los estados límite. Conforme al criterio MTC
        adoptado para este proyecto, los dictámenes de estabilidad global
        (excentricidad/volteo, deslizamiento y capacidad portante) se emiten
        únicamente para Servicio I.
        """
        Fv = sum(d['valor'] for d in fv_detail)
        Me = sum(d['momento'] for d in fv_detail)
        Fh = sum(d['valor'] for d in fh_detail)
        Mv = sum(d['momento'] for d in fh_detail)

        cfg = interface or {}
        width = cfg.get('width', self.geom.B)
        mu = cfg.get('mu', self.mat.mu)
        q_capacity = cfg.get('q_capacity', self.mat.capacidad_portante)
        pressure_method = cfg.get('pressure_method', 'linear')
        eccentricity_divisor = cfg.get('eccentricity_divisor', 6.0)
        overturn = self.check_overturning(
            Me, Mv, Fv, width, eccentricity_divisor=eccentricity_divisor)
        slide = (
            self.check_sliding(Fv, Fh, mu, phi_resist=phi_slide)
            if verify_stability else
            {
                'QR': None,
                'F_horizontal': round(Fh, 2),
                'phi': None,
                'mu': None,
                'QR > Fh': STABILITY_NOT_APPLICABLE,
            }
        )
        bearing = self.check_bearing_capacity(
            Fv, overturn['e'], width,
            q_capacity if verify_stability else None,
            Xo=overturn['Xo'], method=pressure_method)

        if not verify_stability:
            overturn['e < B/6'] = STABILITY_NOT_APPLICABLE
            overturn['eccentricity_check'] = STABILITY_NOT_APPLICABLE
            slide['QR > Fh'] = STABILITY_NOT_APPLICABLE
            bearing['q <= q_adm'] = STABILITY_NOT_APPLICABLE
            bearing['q_min >= 0'] = STABILITY_NOT_APPLICABLE

        case = {
            'name': name,
            'Fv': round(Fv, 2),
            'Me': round(Me, 2),
            'Fh': round(Fh, 2),
            'Mv': round(Mv, 2),
            'overturning': overturn,
            'sliding': slide,
            'bearing': bearing,
            'fv_detail': fv_detail,
            'fh_detail': fh_detail,
            'interface': cfg.get('name', 'base_zapata_estructural'),
            'support_width': width,
            'stability_verification': verify_stability,
        }
        if extra:
            case.update(extra)
        return case

    def case_service_I(self, W: dict, Super: dict, Earth: dict,
                       SeismicF: dict, interface: dict | None = None) -> dict:
        """Estado Límite de Servicio I - Factores = 1.0"""
        factors = {t: 1.0 for t in ('EV', 'DC', 'DW', 'LS', 'PL', 'LL+IM')}
        fv_detail = self._vertical_details(W, Super, factors)
        fh_detail = [
            self._factored_component('Ea', 'Empuje activo',
                Earth['Ea']['valor'], Earth['Ea']['brazo'], Earth['Ea']['momento'],
                1.0, 'terreno', 'triangular_max_base'),
            self._factored_component('Es', 'Empuje por sobrecarga',
                Earth['Es']['valor'], Earth['Es']['brazo'], Earth['Es']['momento'],
                1.0, 'terreno', 'uniforme'),
            self._factored_component('BR', 'Frenado',
                SeismicF['frenado']['peso'], SeismicF['frenado']['brazo'],
                SeismicF['frenado']['momento'], 1.0, 'superestructura'),
        ]
        return self._finalize_case(
            'Servicio I', fv_detail, fh_detail, 1.0, interface=interface,
            verify_stability=True)

    def case_resistance_Ia(self, W: dict, Super: dict, Earth: dict,
                            SeismicF: dict,
                            interface: dict | None = None) -> dict:
        """
        Resistencia I-a (factores mínimos)
        V = 1.00*EV + 0.90*DC + 0.65*DW + 1.75*(LS+PL+LL+IM)
        F = 1.50*Ea + 1.75*Es + 1.75*BR
        """
        factors = {'EV': 1.00, 'DC': 0.90, 'DW': 0.65,
                   'LS': 1.75, 'PL': 1.75, 'LL+IM': 1.75}
        fv_detail = self._vertical_details(W, Super, factors)
        fh_detail = [
            self._factored_component('Ea', 'Empuje activo',
                Earth['Ea']['valor'], Earth['Ea']['brazo'], Earth['Ea']['momento'],
                1.50, 'terreno', 'triangular_max_base'),
            self._factored_component('Es', 'Empuje por sobrecarga',
                Earth['Es']['valor'], Earth['Es']['brazo'], Earth['Es']['momento'],
                1.75, 'terreno', 'uniforme'),
            self._factored_component('BR', 'Frenado',
                SeismicF['frenado']['peso'], SeismicF['frenado']['brazo'],
                SeismicF['frenado']['momento'], 1.75, 'superestructura'),
        ]
        return self._finalize_case(
            'Resistencia I-a', fv_detail, fh_detail, 0.85,
            interface=interface, verify_stability=False)

    def case_resistance_Ib(self, W: dict, Super: dict, Earth: dict,
                            SeismicF: dict,
                            interface: dict | None = None) -> dict:
        """
        Resistencia I-b (factores máximos)
        V = 1.35*EV + 1.25*DC + 1.50*DW + 1.75*(LS+PL+LL+IM)
        """
        factors = {'EV': 1.35, 'DC': 1.25, 'DW': 1.50,
                   'LS': 1.75, 'PL': 1.75, 'LL+IM': 1.75}
        fv_detail = self._vertical_details(W, Super, factors)
        fh_detail = [
            self._factored_component('Ea', 'Empuje activo',
                Earth['Ea']['valor'], Earth['Ea']['brazo'], Earth['Ea']['momento'],
                1.50, 'terreno', 'triangular_max_base'),
            self._factored_component('Es', 'Empuje por sobrecarga',
                Earth['Es']['valor'], Earth['Es']['brazo'], Earth['Es']['momento'],
                1.75, 'terreno', 'uniforme'),
            self._factored_component('BR', 'Frenado',
                SeismicF['frenado']['peso'], SeismicF['frenado']['brazo'],
                SeismicF['frenado']['momento'], 1.75, 'superestructura'),
        ]
        return self._finalize_case(
            'Resistencia I-b', fv_detail, fh_detail, 0.85,
            interface=interface, verify_stability=False)

    def case_extreme_event_I(self, W: dict, Super: dict, Earth: dict,
                              SeismicF: dict,
                              interface: dict | None = None) -> dict:
        """
        Evento Extremo I (sismo)
        V = 1.00*EV + 0.90*DC + 0.65*DW
        F = 1.00*Ea + 1.00*dEas + 1.00*Eq (NO incluye Es)
        """
        factors = {'EV': 1.00, 'DC': 0.90, 'DW': 0.65,
                   'LS': 0.00, 'PL': 0.00, 'LL+IM': 0.00}
        fv_detail = self._vertical_details(W, Super, factors)
        fh_detail = [
            self._factored_component('Ea', 'Empuje activo estático',
                Earth['Ea']['valor'], Earth['Ea']['brazo'], Earth['Ea']['momento'],
                1.0, 'terreno', 'triangular_max_base'),
            self._factored_component('Delta Eas', 'Incremento sísmico del empuje',
                Earth['delta_Eas']['valor'], Earth['delta_Eas']['brazo'],
                Earth['delta_Eas']['momento'], 1.0, 'terreno',
                'triangular_max_top'),
            self._factored_component('Eq-super', 'Inercia de superestructura',
                SeismicF['superestructura']['peso'],
                SeismicF['superestructura']['brazo'],
                SeismicF['superestructura']['momento'], 1.0,
                'superestructura'),
            self._factored_component('Eq-estribo', 'Inercia del estribo',
                SeismicF['estribo']['peso'], SeismicF['estribo']['brazo'],
                SeismicF['estribo']['momento'], 1.0, 'estribo'),
        ]
        if SeismicF.get('falsa_zapata'):
            sfz = SeismicF['falsa_zapata']
            fh_detail.append(self._factored_component(
                'Eq-falsa-zapata', 'Inercia de la falsa zapata',
                sfz['peso'], sfz['brazo'], sfz['momento'], 1.0,
                'falsa_zapata'))
        Fq = sum(d['valor'] for d in fh_detail if d['tipo'].startswith('Eq-'))
        Mq = sum(d['momento'] for d in fh_detail if d['tipo'].startswith('Eq-'))
        return self._finalize_case(
            'Evento Extremo I (Sismo)', fv_detail, fh_detail, 1.0,
            extra={'Fq': round(Fq, 2), 'Mq': round(Mq, 2)},
            interface=interface, verify_stability=False)

    def _run_cases(self, W: dict, Super: dict, Earth: dict,
                   SeismicF: dict, interface: dict) -> dict:
        """Calcula las cuatro combinaciones y verifica solo Servicio I."""
        service_interface = dict(interface)
        strength_interface = dict(interface)
        strength_interface['q_capacity'] = interface.get(
            'q_capacity_strength', interface.get('q_capacity'))
        return {
            'case_service_I': self.case_service_I(
                W, Super, Earth, SeismicF, service_interface),
            'case_resistance_Ia': self.case_resistance_Ia(
                W, Super, Earth, SeismicF, strength_interface),
            'case_resistance_Ib': self.case_resistance_Ib(
                W, Super, Earth, SeismicF, strength_interface),
            'case_extreme_event_I': self.case_extreme_event_I(
                W, Super, Earth, SeismicF, strength_interface),
        }

    def run_full_analysis(self) -> dict:
        """Ejecuta el análisis completo"""
        results = {
            'bridge': 'Puente Carrozable Molinohuaico',
            'location': 'Chilcas, La Mar, Ayacucho',
            'abutment_type': f'Estribo Izquierdo C°A° Cantilever (H={self.geom.H}m)',
            'span': self.loads.L,
        }

        results['weights'] = self.compute_weights_and_moments()
        results['superstructure'] = self.compute_superstructure_reactions()
        results['earth_pressures'] = self.compute_earth_pressures()
        results['seismic_forces'] = self.compute_seismic_forces(results['weights'])

        results['case_service_I'] = self.case_service_I(
            results['weights'], results['superstructure'],
            results['earth_pressures'], results['seismic_forces']
        )
        results['case_resistance_Ia'] = self.case_resistance_Ia(
            results['weights'], results['superstructure'],
            results['earth_pressures'], results['seismic_forces']
        )
        results['case_resistance_Ib'] = self.case_resistance_Ib(
            results['weights'], results['superstructure'],
            results['earth_pressures'], results['seismic_forces']
        )
        results['case_extreme_event_I'] = self.case_extreme_event_I(
            results['weights'], results['superstructure'],
            results['earth_pressures'], results['seismic_forces']
        )

        fz = self.false_footing
        if fz is not None and fz.enabled:
            false_weight = self.compute_false_footing_weight()
            upper_cfg = {
                'name': 'interfaz_1_zapata_falsa_zapata',
                'width': self.geom.B,
                'mu': fz.concrete_contact_mu,
                'q_capacity': (
                    fz.concrete_compression_phi * 0.85 * fz.f_c
                ),
                'pressure_method': 'linear',
                # B/6 se verifica únicamente en Servicio I. En los demás
                # estados se conserva como referencia para calcular presiones.
                'eccentricity_divisor': 6.0,
            }
            lower_mu = (
                self.mat.mu if fz.soil_contact_mu is None
                else fz.soil_contact_mu
            )
            lower_cfg = {
                'name': 'interfaz_2_falsa_zapata_suelo',
                'width': fz.width,
                'mu': lower_mu,
                'q_capacity': self.mat.capacidad_portante,
                'q_capacity_strength': self.mat.capacidad_portante_factorizada,
                'pressure_method': 'meyerhof',
                'eccentricity_divisor': 6.0,
            }
            W2, Super2 = self._lower_interface_vertical_inputs(
                results['weights'], results['superstructure'], false_weight)
            Earth2 = self.compute_earth_pressures(self.geom.H + fz.height)
            Seismic2 = self.compute_seismic_forces(
                results['weights'], reference_depth=fz.height,
                false_footing_weight=false_weight)
            results['false_footing'] = {
                'properties': {
                    'height': fz.height,
                    'width': fz.width,
                    'gamma': fz.gamma,
                    'f_c': fz.f_c,
                    'offset_from_toe': fz.structural_offset(self.geom.B),
                    'concrete_contact_mu': fz.concrete_contact_mu,
                    'soil_contact_mu': lower_mu,
                },
                'weight': false_weight,
                'internal_checks': self.check_false_footing_load_spread(),
            }
            results['interfaces'] = {
                'interface_1': {
                    'description': 'Zapata estructural / falsa zapata',
                    'earth_pressures': results['earth_pressures'],
                    'seismic_forces': results['seismic_forces'],
                    'cases': self._run_cases(
                        results['weights'], results['superstructure'],
                        results['earth_pressures'], results['seismic_forces'],
                        upper_cfg),
                },
                'interface_2': {
                    'description': 'Falsa zapata / suelo de cimentación',
                    'earth_pressures': Earth2,
                    'seismic_forces': Seismic2,
                    'cases': self._run_cases(
                        W2, Super2, Earth2, Seismic2, lower_cfg),
                },
            }

        self.results = results
        return results


# ============================================================================
# VALIDACIÓN DE DATOS PARA REPORTES Y FIGURAS
# ============================================================================

def validate_case_consistency(case: dict, geom: AbutmentGeometry,
                              tol: float = 0.02) -> dict:
    """Comprueba equilibrio y distribución lineal de una combinación.

    Los generadores gráficos llaman esta función antes de dibujar. Una
    inconsistencia produce ``ok=False`` y debe impedir publicar la figura.
    """
    fv = sum(d['valor'] for d in case['fv_detail'])
    me = sum(d['momento'] for d in case['fv_detail'])
    fh = sum(d['valor'] for d in case['fh_detail'])
    mv = sum(d['momento'] for d in case['fh_detail'])

    bearing = case['bearing']
    q_prom = case['Fv'] / geom.B
    ratio = 6.0 * case['overturning']['e'] / geom.B
    qmax_expected = q_prom * (1.0 + ratio)
    qmin_expected = q_prom * (1.0 - ratio)
    q_talon = bearing['q_talon_t_m2']
    q_punta = bearing['q_punta_t_m2']
    denom = 3.0 * (q_talon + q_punta)
    x_center = (geom.B * (q_talon + 2.0 * q_punta) / denom
                if abs(denom) > 1e-12 else float('inf'))
    x_resultant = geom.B - case['overturning']['Xo']

    expected_arm = {
        'triangular_max_base': geom.H / 3.0,
        'uniforme': geom.H / 2.0,
        'triangular_max_top': 2.0 * geom.H / 3.0,
    }
    theory_arms_ok = all(
        d['distribucion'] not in expected_arm or
        abs(d['brazo'] - expected_arm[d['distribucion']]) <= 0.01
        for d in case['fh_detail'])
    def component_moment_is_consistent(component: dict) -> bool:
        """Admite la propagación del redondeo de fuerza y brazo.

        Algunos componentes se reciben del cálculo de empujes con fuerza,
        brazo y momento redondeados a dos decimales.  El producto de los dos
        valores publicados no puede reproducir exactamente el momento que se
        obtuvo con los valores internos sin redondear.
        """
        force = component['valor']
        arm = component['brazo']
        rounding_tolerance = max(
            0.16,
            0.005 * (abs(force) + abs(arm)) + 0.006,
        )
        return abs(component['momento'] - force * arm) <= rounding_tolerance

    component_moments_ok = all(
        component_moment_is_consistent(d)
        for d in case['fv_detail'] + case['fh_detail'])

    checks = {
        'Fv_detalle': abs(fv - case['Fv']) <= tol,
        'Me_detalle': abs(me - case['Me']) <= tol,
        'Fh_detalle': abs(fh - case['Fh']) <= tol,
        'Mv_detalle': abs(mv - case['Mv']) <= tol,
        'q_max_lineal': abs(qmax_expected - bearing['q_max_t_m2']) <= 0.02,
        'q_min_lineal': abs(qmin_expected - bearing['q_min_t_m2']) <= 0.02,
        'resultante_distribucion_lineal': abs(x_center - x_resultant) <= 0.02,
        'brazos_distribuciones_teoricas': theory_arms_ok,
        'momento_componente_F_por_brazo': component_moments_ok,
    }
    return {
        'ok': all(checks.values()),
        'checks': checks,
        'sumas': {'Fv': round(fv, 3), 'Me': round(me, 3),
                  'Fh': round(fh, 3), 'Mv': round(mv, 3)},
        'x_centro_presiones': round(x_center, 3),
        'x_resultante': round(x_resultant, 3),
    }


# ============================================================================
# REPORTE FORMATEADO
# ============================================================================

def print_header(title: str, char: str = "="):
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def print_subheader(title: str):
    print(f"\n{'-' * 50}")
    print(f"  {title}")
    print(f"{'-' * 50}")


def print_table(rows: List[List[str]], headers: List[str]):
    col_widths = []
    for i, h in enumerate(headers):
        col_widths.append(max(len(h), max((len(str(r[i])) for r in rows), default=0)))

    sep = " | "
    header_line = sep.join(h.center(w) for h, w in zip(headers, col_widths))
    print(f"  {header_line}")
    print(f"  {'-' * len(header_line)}")
    for row in rows:
        line = sep.join(str(v).ljust(w) for v, w in zip(row, col_widths))
        print(f"  {line}")


def markdown_table(headers: List[str], rows: List[List[object]]) -> str:
    """Devuelve una tabla Markdown simple."""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        values = [str(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def case_summary_rows(results: dict) -> List[List[object]]:
    """Fila de verificación normativa de estabilidad (solo Servicio I)."""
    rows = []
    for key in ('case_service_I',):
        case = results[key]
        ov = case['overturning']
        sl = case['sliding']
        be = case['bearing']
        rows.append([
            case['name'],
            case['Fv'],
            case['Me'],
            case['Fh'],
            case['Mv'],
            ov['e'],
            ov['B/6'],
            ov['e < B/6'],
            sl['QR'],
            sl['QR > Fh'],
            be['q'],
            be['q <= q_adm'],
        ])
    return rows


def pressure_summary_rows(results: dict) -> List[List[object]]:
    """Presiones calculadas para todas las combinaciones, sin dictaminarlas."""
    rows = []
    for key in LIMIT_STATE_KEYS:
        case = results[key]
        ov = case['overturning']
        be = case['bearing']
        rows.append([
            case['name'], case['Fv'], case['Me'], case['Fh'], case['Mv'],
            ov['Xo'], ov['e'], be['q_max'], be['q_min'],
        ])
    return rows


def meyerhof_pressure_summary_rows(results: dict) -> List[List[object]]:
    """Presion equivalente de Meyerhof sobre el ancho efectivo."""
    rows = []
    for key in LIMIT_STATE_KEYS:
        case = results[key]
        ov = case['overturning']
        be = case['bearing']
        rows.append([
            case['name'], case['Fv'], case['Me'], case['Fh'], case['Mv'],
            ov['Xo'], ov['e'], be['effective_width'], be['q'], 'No aplica',
        ])
    return rows


def generate_markdown_report(results: dict) -> str:
    """Genera un resumen Markdown de resultados preliminares."""
    ep = results['earth_pressures']
    sf = results['seismic_forces']
    weights = results['weights']
    superstructure = results['superstructure']

    weight_rows = [
        [d['tipo'], d['desc'], d['peso'], d['brazo'], d['momento']]
        for d in weights['detail']
    ]
    weight_rows.append(["", "TOTAL", weights['total_weight'], "", weights['total_moment']])

    reaction_rows = [
        [r['tipo'], r['desc'], r['reaccion'], r['brazo'], r['momento']]
        for r in superstructure['reactions']
    ]

    lines = [
        "# Resumen Preliminar - Analisis de Subestructura",
        "",
        f"**Puente:** {results['bridge']}",
        f"**Ubicacion:** {results['location']}",
        f"**Tipo:** {results['abutment_type']}",
        f"**Luz:** {results['span']} m",
        "",
        "> Reporte generado por `agente_subestructura.py`. Debe incorporarse a la memoria viva solo despues de revisar supuestos y datos de entrada.",
        "",
        "## Empujes de tierra",
        "",
        markdown_table(
            ["Parametro", "Valor", "Unidad"],
            [
                ["Ka", ep['Ka'], "-"],
                ["Kp", ep['Kp'], "-"],
                ["Kas", ep['Kas'], "-"],
                ["h_s/c", ep['h_surcharge'], "m"],
                ["theta sismico", ep['psi_deg'], "grados"],
                ["Ea", ep['Ea']['valor'], "t"],
                ["M_Ea", ep['Ea']['momento'], "t-m"],
                ["Es", ep['Es']['valor'], "t"],
                ["M_Es", ep['Es']['momento'], "t-m"],
                ["Eas", ep['Eas']['valor'], "t"],
                ["Delta Eas", ep['delta_Eas']['valor'], "t"],
                ["M_Delta Eas", ep['delta_Eas']['momento'], "t-m"],
            ],
        ),
        "",
        "## Pesos estabilizadores",
        "",
        markdown_table(
            ["Tipo", "Descripcion", "Peso (t)", "Brazo (m)", "Momento (t-m)"],
            weight_rows,
        ),
        "",
        "## Reacciones de superestructura",
        "",
        markdown_table(
            ["Tipo", "Descripcion", "Reaccion (t)", "Brazo (m)", "Momento (t-m)"],
            reaction_rows,
        ),
        "",
        "## Fuerzas sismicas equivalentes",
        "",
        markdown_table(
            ["Componente", "Fuerza (t)", "Brazo (m)", "Momento (t-m)"],
            [
                ["Superestructura", sf['superestructura']['peso'], sf['superestructura']['brazo'], sf['superestructura']['momento']],
                ["Estribo", sf['estribo']['peso'], sf['estribo']['brazo'], sf['estribo']['momento']],
                ["Frenado", sf['frenado']['peso'], sf['frenado']['brazo'], sf['frenado']['momento']],
            ],
        ),
        "",
        f"Porcentaje sismico usado: **{sf['porcentaje']}%**.",
        "",
        "## Presiones por estado limite",
        "",
        "> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.",
        "",
        markdown_table(
            [
                "Estado limite", "V (t)", "Me (t-m)", "Fh (t)", "Mv (t-m)",
                "Xo (m)", "e (m)", "qmax (kg/cm2)", "qmin (kg/cm2)",
            ],
            pressure_summary_rows(results),
        ),
        "",
        "## Verificacion de estabilidad - Servicio I",
        "",
        markdown_table(
            [
                "Estado limite", "V (t)", "Me (t-m)", "Fh (t)", "Mv (t-m)",
                "e (m)", "B/6 (m)", "Volteo", "QR (t)", "Deslizamiento",
                "q (kg/cm2)", "Capacidad",
            ],
            case_summary_rows(results),
        ),
        "",
        "## Pendientes antes de cerrar resultados",
        "",
        "- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.",
        "- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.",
        "- Confirmar reacciones de superestructura y factores de combinacion aplicables.",
        "- Confirmar parametros geotecnicos y capacidad portante de la version vigente.",
        "- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.",
        "- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.",
        "",
    ]
    if results.get('interfaces'):
        fz = results['false_footing']['properties']
        internal = results['false_footing']['internal_checks']
        interface_lines = [
            "## Analisis de falsa zapata en dos interfaces",
            "",
            markdown_table(
                ["Parametro", "Valor", "Unidad"],
                [
                    ["Ancho falsa zapata", fz['width'], "m"],
                    ["Altura falsa zapata", fz['height'], "m"],
                    ["Peso especifico", fz['gamma'], "t/m3"],
                    ["f'c falsa zapata", fz['f_c'], "kg/cm2"],
                    ["mu concreto-concreto", fz['concrete_contact_mu'], "-"],
                    ["mu concreto-suelo", fz['soil_contact_mu'], "-"],
                ],
            ),
            "",
            f"Difusion de carga 1V:1H: **{internal['status']}**. ",
            "La flexion, el corte y el punzonamiento de la falsa zapata quedan pendientes de verificacion estructural.",
            "",
        ]
        for key in ('interface_1', 'interface_2'):
            interface = results['interfaces'][key]
            is_meyerhof = key == 'interface_2'
            if is_meyerhof:
                pressure_note = (
                    "Presion equivalente uniforme de Meyerhof sobre el ancho "
                    "efectivo B' = B - 2e. qmin no aplica a este modelo "
                    "equivalente; no representa perdida de contacto."
                )
                pressure_headers = [
                    "Estado limite", "V (t)", "Me (t-m)", "Fh (t)",
                    "Mv (t-m)", "Xo (m)", "e (m)", "B efectivo (m)",
                    "q efectiva (kg/cm2)", "qmin (kg/cm2)",
                ]
                pressure_rows = meyerhof_pressure_summary_rows(
                    interface['cases'])
                verification_q_header = "q efectiva (kg/cm2)"
            else:
                pressure_note = (
                    "Presiones calculadas para todos los estados limite "
                    "(sin dictamen de estabilidad):"
                )
                pressure_headers = [
                    "Estado limite", "V (t)", "Me (t-m)", "Fh (t)",
                    "Mv (t-m)", "Xo (m)", "e (m)", "qmax (kg/cm2)",
                    "qmin (kg/cm2)",
                ]
                pressure_rows = pressure_summary_rows(interface['cases'])
                verification_q_header = "q (kg/cm2)"
            interface_lines.extend([
                f"### {interface['description']}",
                "",
                f"Altura de empuje analizada: **{interface['earth_pressures']['analysis_height']} m**.",
                "",
                pressure_note,
                "",
                markdown_table(
                    pressure_headers,
                    pressure_rows,
                ),
                "",
                "Verificacion de estabilidad para Servicio I:",
                "",
                markdown_table(
                    [
                        "Estado limite", "V (t)", "Me (t-m)", "Fh (t)",
                        "Mv (t-m)", "e (m)", "Limite e (m)", "Excentricidad",
                        "QR (t)", "Deslizamiento", verification_q_header,
                        "Capacidad",
                    ],
                    case_summary_rows(interface['cases']),
                ),
                "",
            ])
        pending_index = lines.index("## Pendientes antes de cerrar resultados")
        lines[pending_index:pending_index] = interface_lines
    return "\n".join(lines)


def generate_report(results: dict):
    """Genera reporte completo del análisis"""
    print_header("AGENTE DE ANÁLISIS DE SUBESTRUCTURA", "=")
    print(f"  Puente: {results['bridge']}")
    print(f"  Ubicacion: {results['location']}")
    print(f"  Tipo: {results['abutment_type']}")
    print(f"  Luz: {results['span']} m")

    # ==============================
    # 1. GEOMETRÍA
    # ==============================
    print_header("1. GEOMETRÍA DEL ESTRIBO")
    g = GEOM
    rows = [
        ['Altura total (H)', f"{g.H}", 'm'],
        ['Altura pantalla (hp)', f"{g.hp}", 'm'],
        ['Altura zapata (hz)', f"{g.hz}", 'm'],
        ['Ancho de base (B)', f"{g.B}", 'm'],
        ['Talón posterior (B1)', f"{g.B1}", 'm'],
        ['Punta (B2)', f"{g.B2}", 'm'],
        ['Espesor sup. pantalla (tp1)', f"{g.tp1}", 'm'],
        ['Espesor inf. pantalla (tp2)', f"{g.tp2}", 'm'],
        ['Ancho distribución', f"{g.ancho_estribo}", 'm'],
    ]
    print_table(rows, ['Descripción', 'Valor', 'Unidad'])

    # ==============================
    # 2. MATERIALES
    # ==============================
    print_header("2. PROPIEDADES DE MATERIALES")
    m = MAT
    rows = [
        ['gc (Concreto)', f"{m.gamma_c}", 'Tn/m3'],
        ['gr (Relleno)', f"{m.gamma_r}", 'Tn/m3'],
        ['f (Relleno)', f"{m.phi_relleno}", 'deg'],
        ['d (Muro-suelo)', f"{m.delta}", 'deg'],
        ['f (Base - GW)', f"{m.phi_base}", 'deg'],
        ['mu (Friccion)', f"{m.mu}", '-'],
        ['q_adm (Cap. portante)', f"{m.capacidad_portante}", 'kg/cm2'],
        ['fc', f"{m.f_c}", 'kg/cm2'],
        ['fy', f"{m.fy}", 'kg/cm2'],
    ]
    print_table(rows, ['Parametro', 'Valor', 'Unidad'])

    # ==============================
    # 3. EMPUJES DE TIERRA
    # ==============================
    print_header("3. EMPUJES DE TIERRA")
    ep = results['earth_pressures']
    print(f"\n  Coeficiente de empuje activo (Coulomb): Ka = {ep['Ka']}")
    print(f"  Coeficiente de empuje pasivo: Kp = {ep['Kp']}")
    print(f"  Altura equivalente sobrecarga: h' = {ep['h_surcharge']} m")
    print(f"  Angulo sismico psi = tan^-1(Kh/(1-Kv)) = {ep['psi_deg']} deg")

    print(f"\n  --- Coulomb (Estatico) ---")
    print(f"  Ea = {ep['Ea']['valor']} Tn  (brazo = {ep['Ea']['brazo']} m)")
    print(f"  Ep = {ep['Ep']['valor']} Tn")
    print(f"  Es (sobrecarga) = {ep['Es']['valor']} Tn  (brazo = {ep['Es']['brazo']} m)")

    print(f"\n  --- Mononobe-Okabe (Sismico) ---")
    print(f"  Kas = {ep['Kas']}")
    print(f"  Eas (total dinamico) = {ep['Eas']['valor']} Tn")
    print(f"  Delta Eas (dinamico puro) = {ep['delta_Eas']['valor']} Tn  (brazo = {ep['delta_Eas']['brazo']} m)")

    # ==============================
    # 4. PESOS ESTABILIZADORES
    # ==============================
    print_header("4. PESOS ESTABILIZADORES SOBRE LA ZAPATA")
    w = results['weights']
    rows = []
    for d in w['detail']:
        rows.append([d['tipo'], d['desc'], str(d['peso']),
                     str(d['brazo']), str(d['momento'])])
    rows.append(['', 'TOTAL', str(w['total_weight']),
                 '', str(w['total_moment'])])
    print_table(rows, ['Tipo', 'Descripción', 'Peso (Tn)', 'Brazo (m)', 'Momento (Tn-m)'])

    # ==============================
    # 5. REACCIONES DE SUPERESTRUCTURA
    # ==============================
    print_header("5. REACCIONES DE LA SUPERESTRUCTURA")
    sp = results['superstructure']
    rows = []
    for r in sp['reactions']:
        rows.append([r['tipo'], r['desc'], str(r['reaccion']),
                     str(r['brazo']), str(r['momento'])])
    print_table(rows, ['Tipo', 'Descripción', 'Peso (Tn)', 'Brazo (m)', 'Momento (Tn-m)'])

    # ==============================
    # 6. FUERZAS SÍSMICAS
    # ==============================
    print_header("6. FUERZAS DESESTABILIZADORAS (SISMO)")
    sf = results['seismic_forces']
    print(f"\n  Porcentaje sismico: {sf['porcentaje']}% (1.20*A*S/R)")
    print(f"\n  --- Superestructura ---")
    s = sf['superestructura']
    print(f"  Fuerza = {s['peso']} Tn, Brazo = {s['brazo']} m, Momento = {s['momento']} Tn-m")
    print(f"\n  --- Estribo ---")
    e2 = sf['estribo']
    print(f"  Fuerza = {e2['peso']} Tn, Brazo = {e2['brazo']} m, Momento = {e2['momento']} Tn-m")
    print(f"\n  --- Frenado ---")
    br = sf['frenado']
    print(f"  Fuerza = {br['peso']} Tn, Brazo = {br['brazo']} m, Momento = {br['momento']} Tn-m")

    # ==============================
    # 7. PRESIONES POR CASO Y VERIFICACIÓN DE SERVICIO
    # ==============================
    print_header("7. PRESIONES POR ESTADO LIMITE")

    pressure_rows = []
    for case_name in LIMIT_STATE_KEYS:
        case = results[case_name]
        pressure_rows.append([
            case['name'], case['Fv'], case['Fh'], case['overturning']['e'],
            case['bearing']['q_max'], case['bearing']['q_min'],
        ])
    print_table(pressure_rows, [
        'Estado', 'V (Tn)', 'H (Tn)', 'e (m)', 'qmax (kg/cm2)',
        'qmin (kg/cm2)'])
    print("\n  Nota: las presiones se calculan para todas las combinaciones, sin")
    print("  emitir un dictamen de estabilidad fuera de Servicio I.")

    print_subheader("VERIFICACION DE ESTABILIDAD: SERVICIO I")
    case = results['case_service_I']
    ov = case['overturning']
    sl = case['sliding']
    be = case['bearing']
    print(f"\n  Volteo/excentricidad: e = {ov['e']} m, B/6 = {ov['B/6']} m")
    print(f"  -> {ov['e < B/6']}")
    print(f"\n  Deslizamiento: QR = {sl['QR']} Tn > Fh = {sl['F_horizontal']} Tn")
    print(f"  -> {sl['QR > Fh']}")
    print(f"\n  Capacidad: qmax = {be['q_max']} kg/cm2 <= q_adm = {be['q_admisible']} kg/cm2")
    print(f"  -> {be['q <= q_adm']}")

    if results.get('interfaces'):
        print_header("8. FALSA ZAPATA: VERIFICACIÓN EN DOS INTERFACES")
        for key in ('interface_1', 'interface_2'):
            interface = results['interfaces'][key]
            print_subheader(interface['description'])
            rows = []
            for case_name in LIMIT_STATE_KEYS:
                case = interface['cases'][case_name]
                rows.append([
                    case['name'], case['Fv'], case['Fh'],
                    case['overturning']['e'],
                    case['bearing']['q_max'], case['bearing']['q_min'],
                ])
            print_table(rows, [
                'Estado', 'V (Tn)', 'H (Tn)', 'e (m)', 'qmax (kg/cm2)',
                'qmin (kg/cm2)'])
            service = interface['cases']['case_service_I']
            print("\n  Verificacion Servicio I:")
            print(f"  Excentricidad: {service['overturning']['eccentricity_check']}")
            print(f"  Deslizamiento: {service['sliding']['QR > Fh']}")
            print(f"  Capacidad: {service['bearing']['q <= q_adm']}")

    # ==============================
    # 9. CONCLUSIONES
    # ==============================
    print_header("9. CONCLUSIONES")
    todos_conformes = True
    hay_no_conformes = False
    hay_pendientes = False
    if results.get('interfaces'):
        conclusion_cases = [
            interface['cases']['case_service_I']
            for interface in results['interfaces'].values()
        ]
    else:
        conclusion_cases = [results['case_service_I']]
    for case in conclusion_cases:
        ov = case['overturning']
        sl = case['sliding']
        be = case['bearing']
        checks = [
            ov['eccentricity_check'], sl['QR > Fh'], be['q <= q_adm']]
        if any(check != 'CONFORME' for check in checks):
            todos_conformes = False
            hay_no_conformes = hay_no_conformes or any(
                check == 'NO CONFORME' for check in checks)
            hay_pendientes = hay_pendientes or any(
                check.startswith('PENDIENTE') for check in checks)
            print(
                f"\n  [!] {case['interface']} / {case['name']}: "
                "ALGUNA VERIFICACION NO CONFORME O PENDIENTE")

    if todos_conformes:
        print(f"\n  [OK] El estribo CUMPLE las verificaciones de estabilidad de Servicio I")
        if results.get('interfaces'):
            print("     en ambas interfaces de la falsa zapata")
        print("     Las presiones de los demas estados limite se reportan sin dictamen.")
    elif hay_no_conformes:
        print(f"\n  [!] Se requieren ajustes en el dimensionamiento.")
    elif hay_pendientes:
        print(
            "\n  [!] No se detectaron fallas en las verificaciones cerradas; "
            "falta la capacidad portante factorizada para concluir los "
            "estados de Resistencia y Evento Extremo.")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Analisis preliminar de subestructura del Puente Molinohuaycco. "
            "Los resultados se guardan en un archivo Markdown."
        )
    )
    parser.add_argument(
        "--markdown",
        "-m",
        type=Path,
        default=Path(__file__).resolve().with_name("reporte_subestructura.md"),
        help=(
            "Ruta del informe Markdown (por defecto: "
            "analisis_estabilidad/reporte_subestructura.md)."
        ),
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Muestra adicionalmente el reporte largo en la consola.",
    )
    parser.add_argument(
        "--no-console",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    show_console = args.console and not args.no_console

    if show_console:
        print("\n" + "#" * 70)
        print("  AGENTE DE ANALISIS DE SUBESTRUCTURA - PUENTE MOLINOHUAYCCO")
        print("  Metodologia: AASHTO LRFD 2005 + Mononobe-Okabe (MTC)")
        print("  Referencia: Seccion 3.2.6.6 - Analisis de Subestructura")
        print("#" * 70)

    analyzer = SubstructureAnalysis(GEOM, MAT, LOADS, SEISMIC, FALSE_FOOTING)
    results = analyzer.run_full_analysis()
    if show_console:
        generate_report(results)

    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(generate_markdown_report(results), encoding="utf-8")
    # La ruta del informe se informa siempre, incluso en modo silencioso,
    # para que la ejecución nunca termine sin salida visible.
    print(f"Resumen Markdown generado: {args.markdown}")

    if show_console:
        print(f"\n{'=' * 70}")
        print("  ANÁLISIS COMPLETADO")
        print(f"{'=' * 70}\n")


if __name__ == '__main__':
    main()

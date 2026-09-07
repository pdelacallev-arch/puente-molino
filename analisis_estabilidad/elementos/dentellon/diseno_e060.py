#!/usr/bin/env python3
"""Diseño de un dentellón rectangular de concreto armado según NTE E.060.

El programa toma las fuerzas horizontales y los datos de fricción de
``agente_subestructura.py``; cuando ``QR`` no se reporta fuera de Servicio I,
lo reconstruye como ``phi * mu * Fv``. El dentellón se idealiza como un
voladizo vertical continuo, empotrado en la zapata y cargado por presión pasiva
triangular (más una componente uniforme opcional por sobrecarga).

La estabilidad geotécnica y la resistencia estructural se mantienen separadas:

* el déficit de deslizamiento es ``max(Fh - QR, 0)``;
* la contribución de cálculo a la estabilidad usa el pasivo reducido;
* la sección se diseña para el menor entre ``Fh`` y el pasivo mayorado capaz de
  movilizar el medio, es decir, para la máxima reacción físicamente aplicable.

Unidades internas: m, tf, kgf/cm², cm²/m y MPa donde se indica.
La edición normativa adoptada es la NTE E.060 aprobada por DS 010-2009-VIVIENDA.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_SALIDA_PREDETERMINADA = (
    RUTA_PROYECTO / ".tmp" / "legacy" / "dentellon"
)
SALIDA_MD_PREDETERMINADA = (
    CARPETA_SALIDA_PREDETERMINADA / "diseno_dentellon_e060.md"
)
SALIDA_JSON_PREDETERMINADA = (
    CARPETA_SALIDA_PREDETERMINADA / "diseno_dentellon_e060.json"
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
)


BARRAS_MM = {
    '3/8"': 9.525,
    '1/2"': 12.700,
    '5/8"': 15.875,
    '3/4"': 19.050,
    '1"': 25.400,
    '1 1/8"': 28.575,
    '1 1/4"': 31.750,
    '1 3/8"': 34.925,
}
BARRAS_CLI = {barra.removesuffix('"'): barra for barra in BARRAS_MM}

CASOS = (
    "case_service_I",
    "case_resistance_Ia",
    "case_resistance_Ib",
    "case_extreme_event_I",
)
CASOS_DISENO_ESTRUCTURAL = CASOS[1:]


# =============================================================================
# ENTRADAS EDITABLES DEL DISEÑO
# =============================================================================
# Edite los valores por defecto de ``ParametrosDentellon`` en esta sección.
# Son las entradas usadas al ejecutar directamente este archivo. Los argumentos
# de línea de comandos (por ejemplo, ``--espesor-m 0.80``) las reemplazan solo
# durante esa ejecución.
#
# Unidades: longitud en m, recubrimiento/espaciamiento en mm, peso específico en
# tf/m³, sobrecarga en tf/m² y resistencias de materiales en kgf/cm².
@dataclass(frozen=True)
class ParametrosDentellon:
    """Datos de entrada; la franja de cálculo es 1 m del largo del estribo."""

    # Geometría e interfaz de análisis
    interfaz: str = "interface_1"
    espesor_m: float = 0.70
    profundidad_m: float = 1.30
    longitud_m: float = 6.00
    recubrimiento_mm: float = 75.0

    # Suelo de fundación frente a la cara pasiva (GW, estudio de suelos).
    # No sustituir por el peso específico del relleno del trasdós.
    gamma_medio_tf_m3: float = MAT.gamma_suelo
    phi_medio_grados: float = MAT.phi_base
    sobrecarga_tf_m2: float = 0.0
    profundidad_base_pasivo_m: float | None = None
    medio_granular_confirmado: bool = True

    # Materiales y factores de reducción de resistencia (NTE E.060)
    fc_kg_cm2: float = MAT.f_c
    fy_kg_cm2: float = MAT.fy
    phi_flexion: float = 0.90
    phi_cortante: float = 0.85

    # Factores aplicados al empuje pasivo. MTC 2018, art. 2.8.1.1.12.6,
    # Tabla 2.8.1.1.12.6-1: φp = 0.50 en Estado Límite de Resistencia;
    # la regla general de Evento Extremo I establece φp = 1.00.
    factores_pasivo_confirmados: bool = True
    factor_pasivo_estabilidad_servicio: float = 1.00
    factor_pasivo_estabilidad_resistencia: float = 0.50
    factor_pasivo_estabilidad_extremo: float = 1.00
    # Para la resistencia estructural no se mayoran los empujes pasivos: la
    # reacción se limita por su valor nominal físicamente movilizable.
    factor_pasivo_estructural_servicio: float = 1.00
    factor_pasivo_estructural_resistencia: float = 1.00
    factor_pasivo_estructural_extremo: float = 1.00

    # Reducción de la resistencia por fricción QR = φ·μ·Fv. Se usa para
    # reconstruir QR cuando el agente no lo reporta fuera de Servicio I.
    factor_friccion_servicio: float = 1.00
    factor_friccion_resistencia: float = 0.85
    factor_friccion_extremo: float = 1.00

    # Junta dentellón-zapata y cuantías mínimas
    tipo_conexion: str = "monolitica"
    anclaje_postinstalado_verificado: bool = False
    mu_corte_friccion: float | None = None
    rho_min_losa: float = 0.0018
    rho_min_flexion: float = 0.0012
    rho_distribucion_por_cara: float = 0.0009
    # NTE E.060 9.7.4 y 10.5.4: el acero mínimo total puede disponerse en
    # una o dos caras. Si se usan dos, la cara traccionada conserva al menos
    # rho_min_flexion y el saldo se asigna a la cara opuesta.
    numero_caras_acero_minimo: int = 2

    # Catálogo y selección de refuerzo
    espaciamiento_min_mm: float = 100.0
    espaciamiento_max_mm: float = 400.0
    paso_espaciamiento_mm: float = 10.0
    barras_principales: tuple[str, ...] = ('5/8"', '3/4"', '1"')
    barras_distribucion: tuple[str, ...] = ('5/8"', '3/4"')
    barra_principal_asumida: str | None = None
    barra_opuesta_asumida: str | None = None
    barra_horizontal_asumida: str | None = None
    espaciamiento_principal_asumido_mm: float | None = None
    espaciamiento_opuesto_asumido_mm: float | None = None
    espaciamiento_horizontal_asumido_mm: float | None = None


# Instancia única que alimenta tanto ``disenar()`` como la interfaz de comandos.
ENTRADAS = ParametrosDentellon()
# =========================== FIN DE ENTRADAS ================================


def _validar(p: ParametrosDentellon) -> None:
    positivos = (
        p.espesor_m, p.profundidad_m, p.longitud_m, p.gamma_medio_tf_m3,
        p.fc_kg_cm2, p.fy_kg_cm2, p.espaciamiento_min_mm,
        p.espaciamiento_max_mm, p.paso_espaciamiento_mm,
    )
    if any(x <= 0 for x in positivos):
        raise ValueError("La geometría, materiales y espaciamientos deben ser positivos")
    if not 0 < p.phi_medio_grados < 45:
        raise ValueError("El ángulo de fricción debe estar entre 0 y 45 grados")
    if p.sobrecarga_tf_m2 < 0 or p.recubrimiento_mm < 0:
        raise ValueError("La sobrecarga y el recubrimiento no pueden ser negativos")
    if p.recubrimiento_mm >= 1000 * min(p.espesor_m, p.profundidad_m) / 2:
        raise ValueError("El recubrimiento es incompatible con la geometría")
    if p.espaciamiento_min_mm > p.espaciamiento_max_mm:
        raise ValueError("El espaciamiento mínimo supera al máximo")
    if p.mu_corte_friccion is not None and not 0 < p.mu_corte_friccion <= 1.4:
        raise ValueError("El coeficiente de corte-fricción no es válido")
    if p.numero_caras_acero_minimo not in (1, 2):
        raise ValueError("El acero mínimo debe distribuirse en una o dos caras")
    if not (0 < p.rho_min_flexion <= p.rho_min_losa):
        raise ValueError("Las cuantías mínimas de flexión y losa no son válidas")
    if p.rho_distribucion_por_cara <= 0:
        raise ValueError("La cuantía de distribución por cara debe ser positiva")
    factores_positivos = (
        p.factor_pasivo_estabilidad_servicio,
        p.factor_pasivo_estabilidad_resistencia,
        p.factor_pasivo_estabilidad_extremo,
        p.factor_pasivo_estructural_servicio,
        p.factor_pasivo_estructural_resistencia,
        p.factor_pasivo_estructural_extremo,
        p.factor_friccion_servicio,
        p.factor_friccion_resistencia,
        p.factor_friccion_extremo,
    )
    if any(f <= 0 for f in factores_positivos):
        raise ValueError("Los factores de resistencia y del pasivo deben ser positivos")
    if (p.profundidad_base_pasivo_m is not None
            and p.profundidad_base_pasivo_m < GEOM.hz + p.profundidad_m):
        raise ValueError(
            "La profundidad de la base pasiva no puede ser menor que la "
            "altura total de la zapata más el dentellón"
        )
    if p.tipo_conexion not in ("monolitica", "postinstalada"):
        raise ValueError("La conexión debe ser monolitica o postinstalada")
    if p.anclaje_postinstalado_verificado and p.tipo_conexion != "postinstalada":
        raise ValueError(
            "La confirmación de anclaje postinstalado solo corresponde a esa conexión"
        )
    for catalogo in (p.barras_principales, p.barras_distribucion):
        if not catalogo or any(b not in BARRAS_MM for b in catalogo):
            raise ValueError("El catálogo contiene barras no reconocidas")
    armados_asumidos = (
        ("principal", p.barra_principal_asumida),
        ("opuesto", p.barra_opuesta_asumida),
        ("horizontal", p.barra_horizontal_asumida),
    )
    for nombre, barra in armados_asumidos:
        if barra is not None and barra not in BARRAS_MM:
            raise ValueError(f"Barra asumida no reconocida en armado {nombre}: {barra}")
    armados_con_espaciamiento = (
        ("principal", p.barra_principal_asumida,
         p.espaciamiento_principal_asumido_mm),
        ("opuesto", p.barra_opuesta_asumida,
         p.espaciamiento_opuesto_asumido_mm),
        ("horizontal", p.barra_horizontal_asumida,
         p.espaciamiento_horizontal_asumido_mm),
    )
    for nombre, barra, espaciamiento in armados_con_espaciamiento:
        if espaciamiento is None:
            continue
        if barra is None:
            raise ValueError(
                f"Debe indicar la barra para asumir el espaciamiento del armado {nombre}"
            )
        if espaciamiento <= 0:
            raise ValueError("Los espaciamientos asumidos deben ser positivos")


def _kp_rankine(phi_grados: float) -> float:
    return math.tan(math.radians(45.0 + phi_grados / 2.0)) ** 2


def _redondear_abajo(valor: float, paso: float) -> float:
    return math.floor((valor + 1e-9) / paso) * paso


def _datos_refuerzo(as_req: float, barra: str, espaciamiento_mm: float,
                    seleccion: str, p: ParametrosDentellon) -> dict:
    db = BARRAS_MM[barra]
    area = math.pi * (db / 10.0) ** 2 / 4.0
    as_provisto = area * 1000.0 / espaciamiento_mm
    cumple_area = as_provisto + 1e-9 >= as_req
    cumple_espaciamiento = (
        p.espaciamiento_min_mm - 1e-9 <= espaciamiento_mm
        <= p.espaciamiento_max_mm + 1e-9
    )
    return {
        "barra": barra,
        "diametro_mm": round(db, 3),
        "espaciamiento_requerido_mm": round(area * 1000.0 / as_req, 1),
        "espaciamiento_adoptado_mm": round(espaciamiento_mm, 1),
        "As_provisto_cm2_m": round(as_provisto, 3),
        "seleccion": seleccion,
        "cumple_area": cumple_area,
        "cumple_espaciamiento": cumple_espaciamiento,
        "cumple": cumple_area and cumple_espaciamiento,
    }


def _seleccionar_refuerzo(as_req: float, catalogo: tuple[str, ...],
                          p: ParametrosDentellon,
                          barra_asumida: str | None = None,
                          espaciamiento_asumido_mm: float | None = None) -> dict:
    if as_req <= 1e-12:
        return {
            "barra": None,
            "diametro_mm": 0.0,
            "espaciamiento_requerido_mm": 0.0,
            "espaciamiento_adoptado_mm": 0.0,
            "As_provisto_cm2_m": 0.0,
            "seleccion": "no requerido para el esquema adoptado",
            "cumple_area": True,
            "cumple_espaciamiento": True,
            "cumple": True,
        }
    if barra_asumida is not None:
        db = BARRAS_MM[barra_asumida]
        area = math.pi * (db / 10.0) ** 2 / 4.0
        s_teorico = area * 1000.0 / as_req
        if espaciamiento_asumido_mm is None:
            espaciamiento = _redondear_abajo(
                min(s_teorico, p.espaciamiento_max_mm),
                p.paso_espaciamiento_mm,
            )
            espaciamiento = max(espaciamiento, p.espaciamiento_min_mm)
            seleccion = "barra asumida; espaciamiento calculado"
        else:
            espaciamiento = espaciamiento_asumido_mm
            seleccion = "barra y espaciamiento asumidos"
        return _datos_refuerzo(
            as_req, barra_asumida, espaciamiento, seleccion, p,
        )

    for barra in catalogo:
        db = BARRAS_MM[barra]
        area = math.pi * (db / 10.0) ** 2 / 4.0
        s_teorico = area * 1000.0 / as_req
        s = _redondear_abajo(min(s_teorico, p.espaciamiento_max_mm),
                             p.paso_espaciamiento_mm)
        if s >= p.espaciamiento_min_mm:
            return _datos_refuerzo(
                as_req, barra, s, "selección automática", p,
            )
    raise ValueError(
        "Ninguna barra satisface As y el espaciamiento mínimo; amplíe el catálogo"
    )


def _acero_flexion(mu_tf_m_m: float, d_m: float, p: ParametrosDentellon) -> float:
    """Sección rectangular simple; b=1 m en la dirección del estribo."""
    if mu_tf_m_m <= 1e-12:
        return 0.0
    b_cm = 100.0
    d_cm = d_m * 100.0
    mu_kg_cm = mu_tf_m_m * 100_000.0
    discr = d_cm**2 - 2.0 * mu_kg_cm / (
        p.phi_flexion * 0.85 * p.fc_kg_cm2 * b_cm
    )
    if discr <= 0:
        raise ValueError("La sección excede el dominio de flexión simple")
    a_cm = d_cm - math.sqrt(discr)
    return 0.85 * p.fc_kg_cm2 * b_cm * a_cm / p.fy_kg_cm2


def _phi_vc(d_m: float, p: ParametrosDentellon) -> float:
    fc_mpa = p.fc_kg_cm2 * 0.0980665
    vc_n = 0.17 * math.sqrt(fc_mpa) * 1000.0 * d_m * 1000.0
    return p.phi_cortante * vc_n / 9806.65


def _phi_mn(as_cm2_m: float, d_m: float, p: ParametrosDentellon) -> float:
    """Resistencia de diseño a flexión de la franja de un metro, en tf·m/m."""
    b_cm = 100.0
    d_cm = d_m * 100.0
    a_cm = as_cm2_m * p.fy_kg_cm2 / (0.85 * p.fc_kg_cm2 * b_cm)
    if a_cm >= d_cm:
        raise ValueError("El bloque equivalente de compresión excede el peralte útil")
    mn_kg_cm = as_cm2_m * p.fy_kg_cm2 * (d_cm - a_cm / 2.0)
    return p.phi_flexion * mn_kg_cm / 100_000.0


def _longitud_desarrollo_mm(db_mm: float, p: ParametrosDentellon) -> float:
    """Tabla 12.1 E.060: barra no epóxica, concreto normal, condición favorable."""
    fc_mpa = p.fc_kg_cm2 * 0.0980665
    fy_mpa = p.fy_kg_cm2 * 0.0980665
    denominador = 2.6 if db_mm <= 19.05 + 1e-9 else 2.1
    return max(fy_mpa / (denominador * min(math.sqrt(fc_mpa), 8.3)) * db_mm,
               300.0)


def _factor_caso(clave: str, servicio: float, resistencia: float,
                 extremo: float) -> float:
    if clave == "case_service_I":
        return servicio
    if clave == "case_extreme_event_I":
        return extremo
    return resistencia


def disenar(
    parametros: ParametrosDentellon | None = None,
    resultados_estabilidad: dict | None = None,
) -> dict:
    p = parametros or ENTRADAS
    _validar(p)
    mu_corte_friccion = (
        p.mu_corte_friccion
        if p.mu_corte_friccion is not None
        else (1.4 if p.tipo_conexion == "monolitica" else 0.6)
    )

    resultados_agente = resultados_estabilidad
    if resultados_agente is None:
        analisis = SubstructureAnalysis(GEOM, MAT, LOADS, SEISMIC, FALSE_FOOTING)
        resultados_agente = analisis.run_full_analysis()
    interfaz = resultados_agente.get("interfaces", {}).get(p.interfaz)
    if interfaz is None:
        raise ValueError(f"El agente no produjo {p.interfaz}")

    # Predimensionamiento conservador de d con la mayor barra disponible.
    db_control = (
        BARRAS_MM[p.barra_principal_asumida]
        if p.barra_principal_asumida is not None
        else max(BARRAS_MM[b] for b in p.barras_principales)
    )
    d_m = p.espesor_m - (p.recubrimiento_mm + db_control / 2.0) / 1000.0
    if d_m <= 0:
        raise ValueError("El peralte efectivo del dentellón no es positivo")

    kp = _kp_rankine(p.phi_medio_grados)
    # El agente calcula Ep sobre la altura de la zapata GEOM.hz. Para mantener
    # continua la misma ley triangular hasta el fondo del dentellón, la base
    # pasiva predeterminada se ubica a GEOM.hz + profundidad del dentellón.
    # El usuario puede reemplazarla por una cota geotécnica verificada.
    earth = interfaz.get("earth_pressures", {})
    ep_agente = earth.get("Ep", {}).get("valor")
    kp_agente = earth.get("Kp")
    if ep_agente is None or ep_agente <= 0:
        raise ValueError("El agente no produjo un empuje pasivo Ep positivo")
    if kp_agente is None or kp_agente <= 0:
        raise ValueError("El agente no produjo un coeficiente pasivo Kp positivo")
    altura_pasiva_agente = GEOM.hz
    ep_agente_recalculado = (
        0.5 * MAT.gamma_suelo * float(kp_agente) * altura_pasiva_agente**2
    )
    profundidad_base_pasivo = (
        GEOM.hz + p.profundidad_m
        if p.profundidad_base_pasivo_m is None
        else p.profundidad_base_pasivo_m
    )
    z_coronacion = profundidad_base_pasivo - p.profundidad_m
    presion_top = kp * (
        p.gamma_medio_tf_m3 * z_coronacion + p.sobrecarga_tf_m2
    )
    incremento_presion = (
        kp * p.gamma_medio_tf_m3 * p.profundidad_m
    )
    presion_base = presion_top + incremento_presion
    ep_tri_nom = 0.5 * incremento_presion * p.profundidad_m
    ep_uni_nom = presion_top * p.profundidad_m
    ep_nom = ep_tri_nom + ep_uni_nom
    y_tri_desde_raiz = 2.0 * p.profundidad_m / 3.0
    y_uni_desde_raiz = p.profundidad_m / 2.0

    # El agente verifica formalmente el deslizamiento solo en Servicio I y
    # deja QR=None en los demás estados límite. El diseño del dentellón sí
    # necesita separar, en todos los casos, la fricción y la reacción de la
    # llave. Se toma μ de la misma interfaz verificada en Servicio I y se
    # reconstruyen únicamente los valores ausentes con QR = φ·μ·Fv.
    caso_servicio = interfaz["cases"].get("case_service_I", {})
    mu_interfaz = caso_servicio.get("sliding", {}).get("mu")
    if mu_interfaz is None or float(mu_interfaz) <= 0:
        raise ValueError(
            f"El agente no produjo un coeficiente de fricción válido para {p.interfaz}"
        )
    mu_interfaz = float(mu_interfaz)

    casos = []
    for clave in CASOS:
        caso = interfaz["cases"].get(clave)
        if caso is None:
            raise ValueError(f"Falta el caso {clave} en {p.interfaz}")
        fh = float(caso["Fh"])
        qr_agente = caso.get("sliding", {}).get("QR")
        phi_friccion = _factor_caso(
            clave, p.factor_friccion_servicio,
            p.factor_friccion_resistencia,
            p.factor_friccion_extremo,
        )
        if qr_agente is None:
            fv = float(caso["Fv"])
            qr = phi_friccion * mu_interfaz * fv
            fuente_qr = "recalculado: phi_friccion * mu_interfaz * Fv"
        else:
            qr = float(qr_agente)
            fuente_qr = "agente_subestructura.py"
        deficit = max(fh - qr, 0.0)
        phi_ep = _factor_caso(
            clave, p.factor_pasivo_estabilidad_servicio,
            p.factor_pasivo_estabilidad_resistencia,
            p.factor_pasivo_estabilidad_extremo,
        )
        gamma_ep = _factor_caso(
            clave, p.factor_pasivo_estructural_servicio,
            p.factor_pasivo_estructural_resistencia,
            p.factor_pasivo_estructural_extremo,
        )
        ep_estabilidad = phi_ep * ep_nom
        # Reacción máxima aplicable: no puede exceder ni Fh ni la capacidad
        # pasiva estructuralmente mayorada del medio adyacente.
        vu = min(fh, gamma_ep * ep_nom)
        if ep_nom > 0:
            proporcion_tri = ep_tri_nom / ep_nom
        else:
            proporcion_tri = 0.0
        brazo = (
            proporcion_tri * y_tri_desde_raiz
            + (1.0 - proporcion_tri) * y_uni_desde_raiz
        )
        mu = vu * brazo
        as_calc = _acero_flexion(mu, d_m, p)
        casos.append({
            "caso_clave": clave,
            "caso": caso["name"],
            "Fh_agente_tf_m": round(fh, 3),
            "QR_sin_dentellon_tf_m": round(qr, 3),
            "QR_fuente": fuente_qr,
            "factor_friccion": phi_friccion,
            "mu_interfaz": mu_interfaz,
            "deficit_deslizamiento_tf_m": round(deficit, 3),
            "factor_pasivo_estabilidad": phi_ep,
            "aporte_pasivo_diseno_tf_m": round(ep_estabilidad, 3),
            "QR_con_dentellon_tf_m": round(qr + ep_estabilidad, 3),
            "estabilidad_cumple": qr + ep_estabilidad >= fh,
            "factor_pasivo_estructural": gamma_ep,
            "Vu_dentellon_tf_m": round(vu, 3),
            "brazo_desde_raiz_m": round(brazo, 4),
            "Mu_dentellon_tf_m_m": round(mu, 3),
            "As_calculado_cm2_m": round(as_calc, 3),
        })

    # Servicio I se conserva para estabilidad, pero no gobierna el diseño de
    # resistencia E.060. La envolvente estructural comprende únicamente los
    # estados límite de Resistencia y Evento Extremo I.
    casos_estructurales = [
        caso for caso in casos
        if caso["caso_clave"] in CASOS_DISENO_ESTRUCTURAL
    ]
    gobernante = max(
        casos_estructurales,
        key=lambda x: (x["Mu_dentellon_tf_m_m"], x["Fh_agente_tf_m"]),
    )
    mu_max_estructural = gobernante["Mu_dentellon_tf_m_m"]
    casos_gobernantes = [
        caso["caso"] for caso in casos_estructurales
        if math.isclose(
            caso["Mu_dentellon_tf_m_m"], mu_max_estructural,
            rel_tol=0.0, abs_tol=1e-9,
        )
    ]
    # El dentellón se idealiza como una losa vertical en voladizo de 1 m de
    # ancho. E.060 9.7.4 permite colocar el mínimo total en una o dos caras;
    # E.060 10.5.4 exige rho >= 0.0012 en la cara de tracción cuando se divide.
    area_bruta_cm2_m = 100.0 * p.espesor_m * 100.0
    as_min_losa = p.rho_min_losa * area_bruta_cm2_m
    as_min_flexion = p.rho_min_flexion * area_bruta_cm2_m
    as_distribucion = p.rho_distribucion_por_cara * area_bruta_cm2_m
    if p.numero_caras_acero_minimo == 1:
        as_normativo_traccion = as_min_losa
        as_opuesta_req = 0.0
        as_dist_cara = as_min_losa
        control_traccion = "mínimo total de losa en una cara"
        control_opuesta = "no requerido en esquema de una cara"
        control_distribucion = "mínimo total de losa en una cara"
        armado_distribucion = "Distribución horizontal — cara del pasivo"
    else:
        as_normativo_traccion = as_min_flexion
        as_opuesta_req = max(as_min_losa - as_normativo_traccion, 0.0)
        as_dist_cara = max(as_distribucion, as_min_losa / 2.0)
        control_traccion = "mínimo de flexión en cara traccionada"
        control_opuesta = "saldo del mínimo total de losa"
        control_distribucion = "mitad del mínimo total de losa"
        armado_distribucion = "Distribución horizontal — cada cara"
    # Campo histórico conservado para consumidores existentes: representa el
    # mínimo asignado al armado principal, no un mínimo repetido por cara.
    as_min_por_armado = as_normativo_traccion
    as_diseno_traccion = max(
        gobernante["As_calculado_cm2_m"], as_normativo_traccion,
    )
    principal = _seleccionar_refuerzo(
        as_diseno_traccion, p.barras_principales, p,
        p.barra_principal_asumida,
        p.espaciamiento_principal_asumido_mm,
    )
    # La cara del pasivo es la cara traccionada para las flechas adoptadas.
    d_m = p.espesor_m - (
        p.recubrimiento_mm + principal["diametro_mm"] / 2.0
    ) / 1000.0
    as_calc_actual = _acero_flexion(
        gobernante["Mu_dentellon_tf_m_m"], d_m, p)
    as_diseno_traccion = max(as_calc_actual, as_normativo_traccion)
    principal = _seleccionar_refuerzo(
        as_diseno_traccion, p.barras_principales, p,
        p.barra_principal_asumida,
        p.espaciamiento_principal_asumido_mm,
    )
    vertical_opuesta = _seleccionar_refuerzo(
        as_opuesta_req, p.barras_principales, p,
        p.barra_opuesta_asumida,
        p.espaciamiento_opuesto_asumido_mm,
    )
    phi_mn = _phi_mn(principal["As_provisto_cm2_m"], d_m, p)
    dcr_flexion = gobernante["Mu_dentellon_tf_m_m"] / phi_mn

    phi_vc = _phi_vc(d_m, p)
    vu_max = max(x["Vu_dentellon_tf_m"] for x in casos_estructurales)
    corte = {
        "seccion_verificada": "raiz del voladizo (conservador)",
        "Vu_tf_m": round(vu_max, 3),
        "phi_Vc_tf_m": round(phi_vc, 3),
        "DCR": round(vu_max / phi_vc, 3),
        "cumple": vu_max <= phi_vc,
    }

    distribucion = _seleccionar_refuerzo(
        as_dist_cara, p.barras_distribucion, p,
        p.barra_horizontal_asumida,
        p.espaciamiento_horizontal_asumido_mm,
    )

    # Resumen único y auditable del dimensionamiento de acero.  La relación
    # D/C de esta tabla compara el área requerida (máximo entre la calculada y
    # la normativa) con el área efectivamente dispuesta.
    resumen_acero = [
        {
            "armado": "Principal vertical — cara del pasivo",
            "As_calculado_cm2_m": round(as_calc_actual, 3),
            "As_normativo_cm2_m": round(as_normativo_traccion, 3),
            "control_normativo": control_traccion,
            "As_requerido_cm2_m": round(as_diseno_traccion, 3),
            "As_dispuesto_cm2_m": principal["As_provisto_cm2_m"],
            "DCR_acero": round(
                as_diseno_traccion / principal["As_provisto_cm2_m"], 3),
            "barra": principal["barra"],
            "espaciamiento_adoptado_mm": principal["espaciamiento_adoptado_mm"],
            "cumple": principal["As_provisto_cm2_m"] + 1e-9 >= as_diseno_traccion,
        },
        {
            "armado": "Vertical — cara opuesta",
            "As_calculado_cm2_m": 0.0,
            "As_normativo_cm2_m": round(as_opuesta_req, 3),
            "control_normativo": control_opuesta,
            "As_requerido_cm2_m": round(as_opuesta_req, 3),
            "As_dispuesto_cm2_m": vertical_opuesta["As_provisto_cm2_m"],
            "DCR_acero": round(
                as_opuesta_req / vertical_opuesta["As_provisto_cm2_m"], 3
            ) if as_opuesta_req > 0 else 0.0,
            "barra": vertical_opuesta["barra"],
            "espaciamiento_adoptado_mm": vertical_opuesta["espaciamiento_adoptado_mm"],
            "cumple": vertical_opuesta["As_provisto_cm2_m"] + 1e-9 >= as_opuesta_req,
        },
        {
            "armado": armado_distribucion,
            "As_calculado_cm2_m": 0.0,
            "As_normativo_cm2_m": round(as_dist_cara, 3),
            "control_normativo": control_distribucion,
            "As_requerido_cm2_m": round(as_dist_cara, 3),
            "As_dispuesto_cm2_m": distribucion["As_provisto_cm2_m"],
            "DCR_acero": round(
                as_dist_cara / distribucion["As_provisto_cm2_m"], 3),
            "barra": distribucion["barra"],
            "espaciamiento_adoptado_mm": distribucion["espaciamiento_adoptado_mm"],
            "cumple": distribucion["As_provisto_cm2_m"] + 1e-9 >= as_dist_cara,
        },
    ]

    # Todo el acero vertical que cruza y se desarrolla a ambos lados de la
    # junta puede actuar como Avf. La capacidad es solo teórica hasta acreditar
    # el sistema postinstalado, cuando corresponda.
    avf_req = vu_max * 1000.0 / (
        p.phi_cortante * p.fy_kg_cm2 * mu_corte_friccion
    )
    avf_prov = (
        principal["As_provisto_cm2_m"]
        + vertical_opuesta["As_provisto_cm2_m"]
    )
    vn_fric_tf = avf_prov * p.fy_kg_cm2 * mu_corte_friccion / 1000.0
    # Límite superior conservador de E.060 11.7: 0.2 f'c Ac y 56 Ac.
    ac_cm2 = area_bruta_cm2_m
    vn_lim_tf = min(0.2 * p.fc_kg_cm2 * ac_cm2, 56.0 * ac_cm2) / 1000.0
    phi_vn_fric = p.phi_cortante * min(vn_fric_tf, vn_lim_tf)
    ld_principal = _longitud_desarrollo_mm(principal["diametro_mm"], p)
    ld_opuesta = (
        _longitud_desarrollo_mm(vertical_opuesta["diametro_mm"], p)
        if vertical_opuesta["diametro_mm"] > 0 else 0.0
    )
    disponible_zapata = GEOM.hz * 1000.0 - p.recubrimiento_mm
    desarrollo_geometrico = disponible_zapata >= max(ld_principal, ld_opuesta)
    if p.tipo_conexion == "monolitica":
        anclaje_acreditado = desarrollo_geometrico
    else:
        anclaje_acreditado = (
            desarrollo_geometrico and p.anclaje_postinstalado_verificado)
    corte_friccion_teorico_cumple = vu_max <= phi_vn_fric
    junta = {
        "condicion": (
            "concreto colocado monolíticamente"
            if p.tipo_conexion == "monolitica"
            else "concreto nuevo contra endurecido limpio, no rugoso intencionalmente"
        ),
        "mu": mu_corte_friccion,
        "Avf_requerido_cm2_m": round(avf_req, 3),
        "Avf_provisto_cm2_m": avf_prov,
        "phi_Vn_corte_friccion_tf_m": round(phi_vn_fric, 3),
        "DCR": round(vu_max / phi_vn_fric, 3),
        "cumple_teorico": corte_friccion_teorico_cumple,
        "tipo_conexion": p.tipo_conexion,
        "anclaje_acreditado": anclaje_acreditado,
        "estado": (
            "NO CUMPLE" if not corte_friccion_teorico_cumple
            else ("CUMPLE" if anclaje_acreditado else "PENDIENTE")
        ),
        "ld_principal_requerida_mm": round(ld_principal, 1),
        "ld_cara_opuesta_requerida_mm": round(ld_opuesta, 1),
        "longitud_disponible_en_zapata_mm": round(disponible_zapata, 1),
        "desarrollo_geometrico_cumple": desarrollo_geometrico,
    }

    cumple_numerico = (
        all(x["estabilidad_cumple"] for x in casos)
        and dcr_flexion <= 1.0 and corte["cumple"]
        and corte_friccion_teorico_cumple and desarrollo_geometrico
        and principal["As_provisto_cm2_m"] >= as_diseno_traccion
        and vertical_opuesta["As_provisto_cm2_m"] >= as_opuesta_req
        and distribucion["As_provisto_cm2_m"] >= as_dist_cara
        and principal["cumple"]
        and vertical_opuesta["cumple"]
        and distribucion["cumple"]
    )
    pendientes = []
    if not p.medio_granular_confirmado:
        pendientes.append(
            "Confirmar que la cara cargada del dentellón está en contacto con "
            "suelo granular drenado y validar sus cotas superior e inferior."
        )
    if not p.factores_pasivo_confirmados:
        pendientes.append(
            "Confirmar los factores de resistencia del empuje pasivo: se han "
            "adoptado φp = 0.50 en Resistencia y φp = 1.00 en Evento Extremo I."
        )
    if not anclaje_acreditado:
        pendientes.append(
            "Acreditar el anclaje que desarrolla fy a ambos lados de la junta; "
            "para barras postinstaladas se requiere diseño y sistema aprobado."
        )
    if not cumple_numerico:
        estado_general = "NO CUMPLE"
    elif pendientes:
        estado_general = "PENDIENTE DE CONFIRMACION"
    else:
        estado_general = "CUMPLE"
    return {
        "norma": "NTE E.060 Concreto Armado, DS N.° 010-2009-VIVIENDA",
        "fuente_solicitaciones": f"agente_subestructura.py / {p.interfaz}",
        "fuente_factores_pasivo": (
            "Manual de Puentes MTC 2018, art. 2.8.1.1.12.6 y Tabla "
            "2.8.1.1.12.6-1: φp = 0.50 para la componente pasiva de "
            "resistencia al deslizamiento en Estado Límite de Resistencia. "
            "Servicio usa el valor nominal y en Evento Extremo I se adopta "
            "φp = 1.00 conforme a la regla general de factores de resistencia "
            "para eventos extremos del MTC y AASHTO LRFD."
        ),
        "estado_general": estado_general,
        "estado_estructural_e060": "CUMPLE" if cumple_numerico else "NO CUMPLE",
        "pendientes_cierre": pendientes,
        "parametros": asdict(p),
        "geometria": {
            "idealizacion_estructural": "losa vertical en voladizo; franja de 1 m",
            "espesor_horizontal_m": p.espesor_m,
            "profundidad_vertical_m": p.profundidad_m,
            "longitud_m": p.longitud_m,
            "ancho_franja_m": 1.0,
            "d_flexion_m": round(d_m, 4),
            "espesor_zapata_para_anclaje_m": GEOM.hz,
        },
        "materiales": {
            "fc_kg_cm2": p.fc_kg_cm2,
            "fy_kg_cm2": p.fy_kg_cm2,
            "gamma_medio_tf_m3": p.gamma_medio_tf_m3,
            "phi_medio_grados": p.phi_medio_grados,
            "fuente_suelo_pasivo": (
                "Estudio de Suelos Informe N.° 001-2026/ING-CON-26-E-008/"
                "INGEOTECON-135-26: suelo de fundación GW, γ seco = "
                "19.2 kN/m³ (≈ 1.96 tf/m³), φ' = 39.8°, c' = 0."
            ),
        },
        "pasivo_nominal": {
            "Kp_Rankine": round(kp, 4),
            "Kp_agente": kp_agente,
            "Ep_agente_tf_m": ep_agente,
            "Ep_agente_recalculado_tf_m": round(ep_agente_recalculado, 3),
            "altura_distribucion_pasiva_agente_m": round(
                altura_pasiva_agente, 4),
            "profundidad_base_pasivo_adoptada_m": round(
                profundidad_base_pasivo, 4),
            "profundidad_coronacion_dentellon_m": round(z_coronacion, 4),
            "presion_coronacion_tf_m2": round(presion_top, 3),
            "incremento_presion_dentellon_tf_m2": round(
                incremento_presion, 3),
            "presion_base_tf_m2": round(presion_base, 3),
            "componente_triangular_tf_m": round(ep_tri_nom, 3),
            "componente_uniforme_tf_m": round(ep_uni_nom, 3),
            "Ep_total_tf_m": round(ep_nom, 3),
            "brazo_triangular_desde_raiz_m": round(y_tri_desde_raiz, 4),
        },
        "resultados_por_caso": casos,
        "caso_gobernante": gobernante["caso"],
        "casos_gobernantes_estructurales": casos_gobernantes,
        "criterio_caso_gobernante": (
            "Envolvente de Resistencia I y Evento Extremo I; Servicio I se "
            "usa solo para estabilidad. En empates de Mu se presenta como "
            "caso representativo el de mayor Fh."
        ),
        "resumen_acero": resumen_acero,
        "flexion": {
            "Mu_tf_m_m": gobernante["Mu_dentellon_tf_m_m"],
            "As_calculado_cm2_m": round(as_calc_actual, 3),
            "numero_caras_acero_minimo": p.numero_caras_acero_minimo,
            "As_minimo_total_cm2_m": round(as_min_losa, 3),
            "As_minimo_flexion_cm2_m": round(as_min_flexion, 3),
            "As_minimo_losa_cm2_m": round(as_min_losa, 3),
            "As_distribucion_cm2_m": round(as_distribucion, 3),
            "As_minimo_por_armado_cm2_m": round(as_min_por_armado, 3),
            "As_diseno_cm2_m": round(as_diseno_traccion, 3),
            "As_normativo_cm2_m": round(as_normativo_traccion, 3),
            "DCR_acero": resumen_acero[0]["DCR_acero"],
            **principal,
            "phi_Mn_tf_m_m": round(phi_mn, 3),
            "DCR": round(dcr_flexion, 3),
            "cumple": dcr_flexion <= 1.0,
            "direccion": "vertical; cara en contacto con la presión pasiva",
        },
        "vertical_cara_opuesta": {
            "As_calculado_cm2_m": 0.0,
            "As_normativo_cm2_m": round(as_opuesta_req, 3),
            "As_requerido_cm2_m": round(as_opuesta_req, 3),
            "As_dispuesto_cm2_m": vertical_opuesta["As_provisto_cm2_m"],
            "DCR_acero": resumen_acero[1]["DCR_acero"],
            "criterio": control_opuesta,
            **vertical_opuesta,
            "direccion": "vertical; cara opuesta al medio pasivo",
        },
        "cortante": corte,
        "distribucion_por_cara": {
            "As_calculado_cm2_m": 0.0,
            "numero_caras_activas": p.numero_caras_acero_minimo,
            "As_normativo_cm2_m": round(as_dist_cara, 3),
            "As_requerido_cm2_m": round(as_dist_cara, 3),
            "As_dispuesto_cm2_m": distribucion["As_provisto_cm2_m"],
            "DCR_acero": resumen_acero[2]["DCR_acero"],
            "criterio": control_distribucion,
            **distribucion,
            "direccion": "horizontal, paralela al eje del estribo",
        },
        "junta_zapata_dentellon": junta,
        "advertencias": [
            (
                "El Manual de Puentes MTC 2018, art. 2.8.1.1.12.6 y Tabla "
                "2.8.1.1.12.6-1, respalda φp = 0.50 para la componente pasiva "
                "en Estado Límite de Resistencia; para Evento Extremo I se "
                "adopta φp = 1.00 conforme a la regla general del MTC y "
                "AASHTO LRFD. No se usa un factor 1.50 para mayorar el empuje "
                "en el diseño estructural."
                if p.factores_pasivo_confirmados
                else "Los factores adoptados φp = 0.50 en Resistencia y "
                     "φp = 1.00 en Evento Extremo I requieren confirmación."
            ),
            (
                f"La ley pasiva se prolonga desde la coronación de la zapata hasta la base "
                f"adoptada ({profundidad_base_pasivo:.3f} m); las cotas del dentellón fueron "
                "verificadas en el proyecto."
                if p.medio_granular_confirmado
                else "La profundidad base predeterminada es GEOM.hz más la profundidad del "
                     "dentellón, para prolongar la ley pasiva desde la coronación de la "
                     "zapata; debe sustituirse si las cotas geotécnicas verificadas son "
                     "distintas."
            ),
            (
                "El medio pasivo adoptado es el suelo de fundación GW (γ = 1.96 Tn/m³, "
                "φ' = 39.8°), según el Estudio de Suelos Informe N.° 001-2026/ING-CON-26-"
                "E-008/INGEOTECON-135-26; tanto el agente de subestructura como este "
                "diseño usan el peso específico del suelo de fundación para el pasivo."
                if p.medio_granular_confirmado
                else "Confirmar que la cara pasiva del dentellón queda contra el suelo de "
                     "fundación GW caracterizado en el estudio geotécnico."
            ),
            "El modelo de Rankine solo es válido con suelo granular drenado frente al dentellón; no aplica a una llave embebida en concreto.",
            "El dentellón y la zapata se consideran vaciados monolíticamente; las barras deben desarrollar fy dentro de la zapata.",
            (
                "La cuantía mínima total de losa se coloca en una sola cara, "
                "según la opción de entrada adoptada."
                if p.numero_caras_acero_minimo == 1
                else "La cuantía mínima total de losa se reparte entre dos caras; "
                     "la cara traccionada conserva rho = 0.0012 y la opuesta "
                     "recibe el saldo. El acero horizontal se divide por mitades."
            ),
            "La cara en contacto con el pasivo es la cara traccionada para el sentido de carga adoptado.",
        ],
    }


def generar_markdown(r: dict) -> str:
    g, pas, fl, co, ju = (
        r["geometria"], r["pasivo_nominal"], r["flexion"],
        r["cortante"], r["junta_zapata_dentellon"],
    )
    def detalle_refuerzo(acero: dict) -> str:
        if acero["As_dispuesto_cm2_m"] <= 0:
            return "No requerido"
        return (
            f"Ø{acero['barra']} @ "
            f"{acero['espaciamiento_adoptado_mm']:.0f} mm"
        )

    lineas = [
        "# Diseño del dentellón rectangular — NTE E.060", "",
        f"**Estado general:** {r['estado_general']}", "",
        f"**Estado estructural E.060:** {r['estado_estructural_e060']}", "",
        "## Datos y modelo", "",
        "| Parámetro | Valor |", "|---|---:|",
        f"| Interfaz del agente | {r['parametros']['interfaz']} |",
        f"| Espesor horizontal | {g['espesor_horizontal_m']:.3f} m |",
        f"| Profundidad vertical | {g['profundidad_vertical_m']:.3f} m |",
        f"| Longitud | {g['longitud_m']:.3f} m |",
        f"| Idealización | {g['idealizacion_estructural']} |",
        f"| Peralte efectivo de flexión | {g['d_flexion_m']:.4f} m |",
        f"| Kp Rankine | {pas['Kp_Rankine']:.4f} |",
        f"| γ medio (cara pasiva) | {r['materiales']['gamma_medio_tf_m3']:.3f} Tn/m³ |",
        f"| Empuje pasivo nominal | {pas['Ep_total_tf_m']:.3f} tf/m |", "",
        "## Demanda y estabilidad", "",
        "| Caso | Fh | QR sin dentellón | Déficit | Vu dentellón | Mu | QR con dentellón | Cumple |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for x in r["resultados_por_caso"]:
        lineas.append(
            f"| {x['caso']} | {x['Fh_agente_tf_m']:.3f} | "
            f"{x['QR_sin_dentellon_tf_m']:.3f} | {x['deficit_deslizamiento_tf_m']:.3f} | "
            f"{x['Vu_dentellon_tf_m']:.3f} | {x['Mu_dentellon_tf_m_m']:.3f} | "
            f"{x['QR_con_dentellon_tf_m']:.3f} | {'Sí' if x['estabilidad_cumple'] else 'No'} |"
        )
    lineas += [
        "", "## Diseño E.060", "",
        f"Caso estructural representativo gobernante: **{r['caso_gobernante']}**.",
        f"Casos con la demanda estructural máxima: **{', '.join(r['casos_gobernantes_estructurales'])}**.",
        "Servicio I se emplea únicamente para la verificación de estabilidad; "
        "no participa en la selección del caso de diseño resistente E.060.", "",
        "| Verificación | Demanda | Capacidad / provisión | D/C o resultado |",
        "|---|---:|---:|---:|",
        f"| Flexión | Mu = {fl['Mu_tf_m_m']:.3f} tf·m/m | φMn = {fl['phi_Mn_tf_m_m']:.3f} tf·m/m | {fl['DCR']:.3f} |",
        f"| Corte | Vu = {co['Vu_tf_m']:.3f} tf/m | φVc = {co['phi_Vc_tf_m']:.3f} tf/m | {co['DCR']:.3f} |",
        f"| Corte-fricción | Vu = {co['Vu_tf_m']:.3f} tf/m | φVn = {ju['phi_Vn_corte_friccion_tf_m']:.3f} tf/m | {ju['DCR']:.3f} |",
        f"| Desarrollo en zapata monolítica | ld principal = {ju['ld_principal_requerida_mm']:.0f} mm | disponible = {ju['longitud_disponible_en_zapata_mm']:.0f} mm | {ju['estado']} |",
        "", "### Cuantía mínima y distribución entre caras", "",
        f"- Número de caras adoptado: `{fl['numero_caras_acero_minimo']}`.",
        f"- Mínimo total de losa, ρ = 0.0018: `{fl['As_minimo_total_cm2_m']:.3f} cm²/m`.",
        f"- Referencia mínima de la cara traccionada, ρ = 0.0012: `{fl['As_minimo_flexion_cm2_m']:.3f} cm²/m`.",
        f"- Referencia de distribución por cara al dividir entre dos, ρ = 0.0009: `{fl['As_distribucion_cm2_m']:.3f} cm²/m`.",
        "", "## Armado propuesto y verificación de áreas", "",
        "`As normativo asignado` es la porción del mínimo total que corresponde "
        "a cada armado según el número de caras elegido. La columna "
        "`Control normativo` identifica el criterio de asignación.", "",
        "La relación D/C de acero es `As requerido / As dispuesto`; "
        "`As requerido = máx(As calculado, As normativo asignado)`.", "",
        "| Armado | As calculado | As normativo asignado | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |",
        "|---|---:|---:|---|---:|---|---:|---:|:---:|",
    ]
    for acero in r["resumen_acero"]:
        lineas.append(
            f"| {acero['armado']} | {acero['As_calculado_cm2_m']:.3f} cm²/m | "
            f"{acero['As_normativo_cm2_m']:.3f} cm²/m | "
            f"{acero['control_normativo']} | "
            f"{acero['As_requerido_cm2_m']:.3f} cm²/m | "
            f"{detalle_refuerzo(acero)} | "
            f"{acero['As_dispuesto_cm2_m']:.3f} cm²/m | "
            f"{acero['DCR_acero']:.3f} | {'Sí' if acero['cumple'] else 'No'} |"
        )
    lineas += [
        "",
        "- Las barras verticales que cruzan y se desarrollan en la junta funcionan también como acero de corte-fricción.",
        "", "## Pendientes para cerrar el diseño", "",
    ]
    lineas.extend(f"- {x}" for x in r["pendientes_cierre"])
    if not r["pendientes_cierre"]:
        lineas.append("- Ninguna.")
    lineas += [
        "", "## Alcance y advertencias", "",
    ]
    lineas.extend(f"- {x}" for x in r["advertencias"])
    return "\n".join(lineas) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--interfaz", choices=("interface_1", "interface_2"),
                        default=ENTRADAS.interfaz)
    parser.add_argument("--espesor-m", type=float, default=ENTRADAS.espesor_m)
    parser.add_argument("--profundidad-m", type=float,
                        default=ENTRADAS.profundidad_m)
    parser.add_argument("--longitud-m", type=float, default=ENTRADAS.longitud_m)
    parser.add_argument("--recubrimiento-mm", type=float,
                        default=ENTRADAS.recubrimiento_mm)
    parser.add_argument("--gamma-medio", type=float,
                        default=ENTRADAS.gamma_medio_tf_m3,
                        help="Peso específico del medio en la cara pasiva; "
                             "por defecto suelo de fundación GW (MAT.gamma_suelo)")
    parser.add_argument("--phi-medio", type=float,
                        default=ENTRADAS.phi_medio_grados)
    parser.add_argument("--sobrecarga", type=float,
                        default=ENTRADAS.sobrecarga_tf_m2)
    parser.add_argument(
        "--profundidad-base-pasivo-m", type=float,
        default=ENTRADAS.profundidad_base_pasivo_m,
        help=("Profundidad de la base respecto al origen de la ley pasiva; "
              "por defecto: espesor de zapata + profundidad del dentellón"),
    )
    parser.add_argument("--confirmar-medio-granular", action="store_true",
                        default=ENTRADAS.medio_granular_confirmado)
    parser.add_argument("--confirmar-factores-pasivo", action="store_true",
                        default=ENTRADAS.factores_pasivo_confirmados)
    parser.add_argument(
        "--tipo-conexion", choices=("monolitica", "postinstalada"),
        default=ENTRADAS.tipo_conexion,
    )
    parser.add_argument(
        "--caras-acero-minimo", type=int, choices=(1, 2),
        default=ENTRADAS.numero_caras_acero_minimo,
        help=("Número de caras entre las que se distribuye el mínimo total "
              "de acero de la losa vertical"),
    )
    parser.add_argument(
        "--confirmar-anclaje-postinstalado", action="store_true",
        default=ENTRADAS.anclaje_postinstalado_verificado,
        help="Usar solo con diseño y sistema de anclaje aprobado",
    )
    opciones_barras = tuple(BARRAS_CLI)
    parser.add_argument(
        "--barra-principal", choices=opciones_barras,
        default=(ENTRADAS.barra_principal_asumida or "").removesuffix('"') or None,
        help="Barra vertical de la cara del pasivo, por ejemplo 5/8",
    )
    parser.add_argument(
        "--barra-opuesta", choices=opciones_barras,
        default=(ENTRADAS.barra_opuesta_asumida or "").removesuffix('"') or None,
        help="Barra vertical de la cara opuesta, por ejemplo 1/2",
    )
    parser.add_argument(
        "--barra-horizontal", choices=opciones_barras,
        default=(ENTRADAS.barra_horizontal_asumida or "").removesuffix('"') or None,
        help="Barra horizontal en cada cara, por ejemplo 1/2",
    )
    parser.add_argument(
        "--espaciamiento-principal-mm", type=float,
        default=ENTRADAS.espaciamiento_principal_asumido_mm,
    )
    parser.add_argument(
        "--espaciamiento-opuesto-mm", type=float,
        default=ENTRADAS.espaciamiento_opuesto_asumido_mm,
    )
    parser.add_argument(
        "--espaciamiento-horizontal-mm", type=float,
        default=ENTRADAS.espaciamiento_horizontal_asumido_mm,
    )
    parser.add_argument(
        "--salida-md", type=Path, default=SALIDA_MD_PREDETERMINADA,
        help="Informe de cálculo Markdown",
    )
    parser.add_argument(
        "--salida-json", type=Path, default=SALIDA_JSON_PREDETERMINADA,
        help="Resultados estructurados JSON",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = parse_args()
    p = ParametrosDentellon(
        interfaz=a.interfaz,
        espesor_m=a.espesor_m,
        profundidad_m=a.profundidad_m,
        longitud_m=a.longitud_m,
        recubrimiento_mm=a.recubrimiento_mm,
        gamma_medio_tf_m3=a.gamma_medio,
        phi_medio_grados=a.phi_medio,
        sobrecarga_tf_m2=a.sobrecarga,
        profundidad_base_pasivo_m=a.profundidad_base_pasivo_m,
        medio_granular_confirmado=a.confirmar_medio_granular,
        factores_pasivo_confirmados=a.confirmar_factores_pasivo,
        tipo_conexion=a.tipo_conexion,
        numero_caras_acero_minimo=a.caras_acero_minimo,
        anclaje_postinstalado_verificado=a.confirmar_anclaje_postinstalado,
        barra_principal_asumida=(
            BARRAS_CLI[a.barra_principal] if a.barra_principal else None
        ),
        barra_opuesta_asumida=(
            BARRAS_CLI[a.barra_opuesta] if a.barra_opuesta else None
        ),
        barra_horizontal_asumida=(
            BARRAS_CLI[a.barra_horizontal] if a.barra_horizontal else None
        ),
        espaciamiento_principal_asumido_mm=a.espaciamiento_principal_mm,
        espaciamiento_opuesto_asumido_mm=a.espaciamiento_opuesto_mm,
        espaciamiento_horizontal_asumido_mm=a.espaciamiento_horizontal_mm,
    )
    resultado = disenar(p)
    md = generar_markdown(resultado)
    a.salida_md.parent.mkdir(parents=True, exist_ok=True)
    a.salida_md.write_text(md, encoding="utf-8")
    a.salida_json.parent.mkdir(parents=True, exist_ok=True)
    a.salida_json.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Markdown: {a.salida_md.resolve()}")
    print(f"JSON: {a.salida_json.resolve()}")


if __name__ == "__main__":
    main()

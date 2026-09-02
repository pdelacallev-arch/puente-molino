"""Factores aproximados de distribución lateral MTC 2.6.4.2.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from ..modelos import Configuracion
from .secciones import PropiedadesAcero


@dataclass(frozen=True)
class FactoresDistribucion:
    momento_interior: float
    momento_exterior: float
    corte_interior: float
    corte_exterior: float
    fatiga_interior: float
    fatiga_exterior: float
    advertencias: tuple[str, ...]

    def a_dict(self) -> dict:
        return asdict(self)


def _palanca_exterior(config: Configuracion) -> float:
    """Reacción de la viga exterior para dos líneas de rueda, incluido m=1.20."""
    separacion = config.geometria.separacion_vigas
    de = config.geometria.distancia_borde_calzada_viga_exterior
    r1 = 0.60 - de
    r2 = r1 + 1.80
    reaccion = 0.0
    for r in (r1, r2):
        reaccion += max(0.0, min(1.0, (separacion - r) / separacion)) / 2.0
    return 1.20 * reaccion


def calcular_factores_distribucion(
    config: Configuracion, acero_representativo: PropiedadesAcero
) -> FactoresDistribucion:
    """Aplica las expresiones de MTC/AASHTO para tablero de concreto sobre vigas I.

    Las ecuaciones se evalúan en unidades inglesas, tal como se presentan en la
    tabla MTC 2.6.4.2.2.2b-1. Si el caso queda fuera de rango, se informa y se
    adopta la regla de la palanca para la viga exterior; no se oculta la
    necesidad de un análisis refinado.
    """
    g = config.geometria
    t = config.trafico
    S_ft = g.separacion_vigas / 0.3048
    L_ft = g.luz / 0.3048
    ts_in = config.losa.espesor / 0.0254
    ec = config.materiales.concreto.ec
    if ec is None:
        from .secciones import modulo_elasticidad_concreto

        ec = modulo_elasticidad_concreto(
            config.materiales.concreto.fc,
            config.materiales.concreto.peso_unitario,
        )
    n = config.materiales.acero_estructural.es / ec
    eg_mm = (
        acero_representativo.altura_total
        + config.losa.haunch * 1000.0
        + config.losa.espesor * 500.0
        - acero_representativo.y_inferior
    )
    kg_mm4 = n * (
        acero_representativo.inercia_x + acero_representativo.area * eg_mm**2
    )
    kg_in4 = kg_mm4 / 25.4**4
    advertencias: list[str] = []
    dentro = (
        3.5 <= S_ft <= 16.0
        and 20.0 <= L_ft <= 240.0
        and 4.5 <= ts_in <= 12.0
        and g.numero_vigas >= 4
        and 10_000.0 <= kg_in4 <= 7_000_000.0
    )
    if not dentro:
        advertencias.append(
            "Geometría fuera del rango de MTC Tabla 2.6.4.2.2.2b-1; "
            "los factores aproximados requieren contraste con análisis refinado."
        )
    termino = kg_in4 / (12.0 * L_ft * ts_in**3)
    gm_1 = 0.06 + (S_ft / 14.0) ** 0.4 * (S_ft / L_ft) ** 0.3 * termino**0.1
    gm_2 = 0.075 + (S_ft / 9.5) ** 0.6 * (S_ft / L_ft) ** 0.2 * termino**0.1
    gm_int = max(gm_1, gm_2)
    gv_1 = 0.36 + S_ft / 25.0
    gv_2 = 0.20 + S_ft / 12.0 - (S_ft / 35.0) ** 2
    gv_int = max(gv_1, gv_2)
    palanca = _palanca_exterior(config)
    de_ft = g.distancia_borde_calzada_viga_exterior / 0.3048
    gm_ext = max(palanca, (0.77 + de_ft / 9.1) * gm_int)
    gv_ext = max(palanca, (0.60 + de_ft / 10.0) * gv_int)
    valores = {
        "momento_interior": t.factor_distribucion_momento_interior or gm_int,
        "momento_exterior": t.factor_distribucion_momento_exterior or gm_ext,
        "corte_interior": t.factor_distribucion_corte_interior or gv_int,
        "corte_exterior": t.factor_distribucion_corte_exterior or gv_ext,
        # MTC 2.4.3.2.4.3: para fatiga se elimina la presencia múltiple
        # incluida en las expresiones aproximadas de un carril.
        "fatiga_interior": t.factor_distribucion_fatiga_interior or gm_1 / 1.20,
        "fatiga_exterior": t.factor_distribucion_fatiga_exterior or palanca / 1.20,
    }
    if any(
        x is not None
        for x in (
            t.factor_distribucion_momento_interior,
            t.factor_distribucion_momento_exterior,
            t.factor_distribucion_corte_interior,
            t.factor_distribucion_corte_exterior,
            t.factor_distribucion_fatiga_interior,
            t.factor_distribucion_fatiga_exterior,
        )
    ):
        advertencias.append("Se aplicaron uno o más factores de distribución confirmados por el usuario.")
    return FactoresDistribucion(advertencias=tuple(advertencias), **valores)

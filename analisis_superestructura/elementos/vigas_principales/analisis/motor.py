"""Motor del análisis longitudinal por etapas y tipo de viga."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..modelos import Configuracion
from ..normativa import REFERENCIAS_MTC_2018
from .distribucion import calcular_factores_distribucion
from .moviles import analizar_hl93, respuesta_vehiculo_critico_centro
from .parrilla import analizar_parrilla
from .respuesta import deformada_desde_momento, respuesta_distribuida, valor_segmentado
from .secciones import propiedades_acero, propiedades_por_segmento


@dataclass(frozen=True)
class ResultadoAnalisis:
    configuracion: Configuracion
    x_mm: np.ndarray
    tipos_viga: dict[str, dict]
    factores_distribucion: dict
    advertencias: tuple[str, ...]
    referencias: dict[str, str]
    equilibrio_relativo: float
    detalle_distribucion: dict | None = None


def _anchos_tributarios(config: Configuracion, tipo: str) -> float:
    if tipo == "interior":
        return config.geometria.separacion_vigas
    return config.geometria.separacion_vigas / 2.0 + config.geometria.voladizo_exterior


def _carga_por_tipo(valor, tipo: str) -> float:
    """Devuelve una carga común o la correspondiente al tipo de viga."""
    if isinstance(valor, (int, float)):
        return float(valor)
    return float(getattr(valor, tipo))


def _analizar_tipo(
    config: Configuracion,
    tipo: str,
    x: np.ndarray,
    movil,
    factores,
    propiedades: list[dict],
) -> dict:
    segmentos = config.viga.segmentos
    acero = [p["acero"] for p in propiedades]
    i_acero = valor_segmentado(x, segmentos, [p.inercia_x for p in acero])
    i_corto = valor_segmentado(x, segmentos, [p["corto_plazo"].inercia_x for p in propiedades])
    i_largo = valor_segmentado(x, segmentos, [p["largo_plazo"].inercia_x for p in propiedades])
    peso_acero = valor_segmentado(
        x,
        segmentos,
        [p.area * 1e-6 * config.materiales.acero_estructural.peso_unitario for p in acero],
    )
    ancho_tributario = _anchos_tributarios(config, tipo)
    peso_losa = (
        ancho_tributario
        * config.losa.espesor
        * config.materiales.concreto.peso_unitario
    )
    ancho_haunch = config.losa.ancho_haunch or 0.0
    peso_haunch = (
        ancho_haunch
        * config.losa.haunch
        * config.materiales.concreto.peso_unitario
    )
    peso_concreto = peso_losa + peso_haunch
    construccion = config.construccion
    w_nc = np.zeros_like(x)
    if construccion.incluir_peso_propio_viga:
        w_nc += peso_acero
    w_nc += _carga_por_tipo(config.cargas.dc_no_compuesta_adicional, tipo) + construccion.carga_construccion
    w_dc = np.full_like(x, _carga_por_tipo(config.cargas.dc_compuesta, tipo))
    if construccion.incluir_losa_fresca:
        if construccion.apuntalada:
            w_dc += peso_concreto
        else:
            w_nc += peso_concreto
    w_dw = np.full_like(x, _carga_por_tipo(config.cargas.dw, tipo))
    w_pl = np.full_like(x, _carga_por_tipo(config.cargas.pl, tipo))
    m_nc, v_nc, r1_nc, r2_nc = respuesta_distribuida(x, w_nc)
    m_dc, v_dc, r1_dc, r2_dc = respuesta_distribuida(x, w_dc)
    m_dw, v_dw, r1_dw, r2_dw = respuesta_distribuida(x, w_dw)
    m_pl, v_pl, r1_pl, r2_pl = respuesta_distribuida(x, w_pl)
    if tipo == "interior":
        gm = factores.momento_interior
        gv = factores.corte_interior
        gf = factores.fatiga_interior
    else:
        gm = factores.momento_exterior
        gv = factores.corte_exterior
        gf = factores.fatiga_exterior
    m_ll = movil.momento_nmm * gm
    v_ll_pos = movil.corte_positivo_n * gv
    v_ll_neg = movil.corte_negativo_n * gv
    m_fatiga = movil.fatiga_rango_momento_nmm * gf
    f = config.analisis.factores
    m_res = (
        f.resistencia_dc * (m_nc + m_dc)
        + f.resistencia_dw * m_dw
        + f.resistencia_ll * m_ll
        + f.resistencia_pl * m_pl
    )
    v_permanente = (
        f.resistencia_dc * (v_nc + v_dc)
        + f.resistencia_dw * v_dw
        + f.resistencia_pl * v_pl
    )
    v_res_pos = v_permanente + f.resistencia_ll * v_ll_pos
    v_res_neg = v_permanente + f.resistencia_ll * v_ll_neg
    v_res = np.maximum(np.abs(v_res_pos), np.abs(v_res_neg))
    m_serv = m_nc + m_dc + m_dw + f.servicio_ll * m_ll + f.servicio_pl * m_pl
    v_serv_permanente = (
        f.servicio_dc * (v_nc + v_dc)
        + f.servicio_dw * v_dw
        + f.servicio_pl * v_pl
    )
    v_serv_pos = v_serv_permanente + f.servicio_ll * v_ll_pos
    v_serv_neg = v_serv_permanente + f.servicio_ll * v_ll_neg
    v_serv_abs = np.maximum(np.abs(v_serv_pos), np.abs(v_serv_neg))
    m_vehiculo_critico, _ = respuesta_vehiculo_critico_centro(
        config,
        x,
        movil.posicion_critica_centro_mm,
        movil.separacion_critica_centro_mm,
        movil.vehiculo_control_momento[len(x) // 2],
    )
    m_vehiculo_critico *= gm
    es = config.materiales.acero_estructural.es
    def_nc = deformada_desde_momento(x, m_nc, es, i_acero)
    def_dc = deformada_desde_momento(x, m_dc + m_dw, es, i_largo)
    def_ll = deformada_desde_momento(x, m_vehiculo_critico, es, i_corto)
    error_reacciones = abs(
        (r1_nc + r2_nc + r1_dc + r2_dc + r1_dw + r2_dw + r1_pl + r2_pl)
        - float(np.trapezoid(w_nc + w_dc + w_dw + w_pl, x))
    ) / max(float(np.trapezoid(w_nc + w_dc + w_dw + w_pl, x)), 1.0)
    return {
        "propiedades": propiedades,
        "cargas_lineales_n_mm": {"DC_no_compuesta": w_nc, "DC_compuesta": w_dc, "DW": w_dw, "PL": w_pl},
        "momentos_nmm": {
            "DC_no_compuesta": m_nc,
            "DC_compuesta": m_dc,
            "DW": m_dw,
            "PL": m_pl,
            "LL_IM": m_ll,
            "fatiga_rango": m_fatiga,
            "resistencia_i": m_res,
            "servicio_ii": m_serv,
        },
        "cortantes_n": {
            "DC_no_compuesta": v_nc,
            "DC_compuesta": v_dc,
            "DW": v_dw,
            "PL": v_pl,
            "LL_IM_positivo": v_ll_pos,
            "LL_IM_negativo": v_ll_neg,
            "resistencia_i_positivo": v_res_pos,
            "resistencia_i_negativo": v_res_neg,
            "resistencia_i_abs": v_res,
            "servicio_ii_positivo": v_serv_pos,
            "servicio_ii_negativo": v_serv_neg,
            "servicio_ii_abs": v_serv_abs,
        },
        "deflexiones_mm": {
            "DC_no_compuesta": def_nc,
            "DC_compuesta_DW": def_dc,
            "LL_IM_critica": def_ll,
            "permanente_total": def_nc + def_dc,
        },
        "reacciones_n": {
            "izquierda_permanente": r1_nc + r1_dc + r1_dw + r1_pl,
            "derecha_permanente": r2_nc + r2_dc + r2_dw + r2_pl,
        },
        "factor_momento": gm,
        "factor_corte": gv,
        "factor_fatiga": gf,
        "equilibrio_relativo": error_reacciones,
    }


def analizar_configuracion(config: Configuracion) -> ResultadoAnalisis:
    movil = analizar_hl93(config)
    x = movil.x_mm
    detalle_distribucion = None
    error_distribucion = 0.0
    if config.analisis.metodo_distribucion == "parrilla":
        resultado_parrilla = analizar_parrilla(config)
        factores = resultado_parrilla.factores
        detalle_distribucion = resultado_parrilla.resumen()
        error_distribucion = resultado_parrilla.error_equilibrio_maximo
    else:
        representativo = propiedades_acero(config.viga.segmentos[len(config.viga.segmentos) // 2])
        factores = calcular_factores_distribucion(config, representativo)
    resultados: dict[str, dict] = {}
    advertencias = list(factores.advertencias)
    for tipo in ("interior", "exterior"):
        propiedades = propiedades_por_segmento(config, tipo)
        resultados[tipo] = _analizar_tipo(config, tipo, x, movil, factores, propiedades)
    equilibrio = max(
        movil.equilibrio_relativo,
        error_distribucion,
        *(v["equilibrio_relativo"] for v in resultados.values()),
    )
    if equilibrio > config.analisis.tolerancia_equilibrio:
        advertencias.append(
            f"Error relativo de equilibrio {equilibrio:.3e} mayor que la tolerancia configurada."
        )
    return ResultadoAnalisis(
        configuracion=config,
        x_mm=x,
        tipos_viga=resultados,
        factores_distribucion=factores.a_dict(),
        advertencias=tuple(advertencias),
        referencias=dict(REFERENCIAS_MTC_2018),
        equilibrio_relativo=equilibrio,
        detalle_distribucion=detalle_distribucion,
    )

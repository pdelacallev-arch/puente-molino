"""Metrado preliminar de cargas del tablero - Puente Molinohuaycco.

Sistema de unidades: metro, tonelada-fuerza (tf), tf/m y tf/m2.
El script calcula acciones nominales, sin factores de combinacion LRFD.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Datos:
    # Geometria
    L: float = 50.00
    ancho_tablero: float = 6.00
    ancho_calzada: float = 4.00
    ancho_veredas_total: float = 2.00
    espesor_losa: float = 0.20
    espesor_recrecido_vereda: float = 0.20
    numero_vigas: int = 3

    # Materiales y elementos permanentes
    gamma_concreto: float = 2.40
    gamma_acero: float = 7.85
    area_viga_apoyo: float = 0.06075
    area_viga_centro: float = 0.08155
    area_diafragma_in2: float = 33.04
    numero_lineas_diafragma: int = 9
    paneles_por_linea: int = 2
    longitud_panel_diafragma: float = 2.00
    peso_baranda_por_lado: float = 0.300
    espesor_asfalto: float = 0.075
    gamma_asfalto: float = 2.30

    # Cargas transitorias
    carga_peatonal: float = 0.370
    hl93_frontal: float = 3.6287
    hl93_posterior: float = 14.515
    tandem_eje: float = 11.340
    carga_carril: float = 0.9524
    separacion_rear_min: float = 4.30
    separacion_tandem: float = 1.20
    incremento_dinamico: float = 1.33
    presencia_multiple_1_carril: float = 1.20

    # Viento y sismo preliminar
    velocidad_viento: float = 75.00
    velocidad_base_viento: float = 160.00
    presion_base_vigas_ksf: float = 0.050
    altura_expuesta: float = 2.932
    viento_minimo_kN_m: float = 4.40
    viento_vertical: float = 0.100
    viento_vehicular_klf: float = 0.100
    coeficiente_sismico: float = 0.240


def reaccion_uniforme(w: float, L: float) -> float:
    return w * L / 2.0


def calcular(d: Datos = Datos()) -> dict[str, float | str]:
    in2_a_m2 = 0.00064516
    ksf_a_tf_m2 = 47.88025898 / 9.80665
    klf_a_tf_m = 14.59390294 / 9.80665

    dc_losa = d.ancho_tablero * d.espesor_losa * d.gamma_concreto
    dc_veredas = (
        d.ancho_veredas_total
        * d.espesor_recrecido_vereda
        * d.gamma_concreto
    )
    area_viga_promedio = (d.area_viga_apoyo + d.area_viga_centro) / 2.0
    dc_vigas = d.numero_vigas * area_viga_promedio * d.gamma_acero
    longitud_total_diafragmas = (
        d.numero_lineas_diafragma
        * d.paneles_por_linea
        * d.longitud_panel_diafragma
    )
    dc_diafragmas = (
        d.area_diafragma_in2
        * in2_a_m2
        * longitud_total_diafragmas
        * d.gamma_acero
        / d.L
    )
    dc_barandas = 2.0 * d.peso_baranda_por_lado
    dc_lineal = dc_losa + dc_veredas + dc_vigas + dc_diafragmas + dc_barandas

    dw_lineal = d.ancho_calzada * d.espesor_asfalto * d.gamma_asfalto
    pl_lineal = d.ancho_veredas_total * d.carga_peatonal

    # Linea de influencia de reaccion. Para maximizar el apoyo izquierdo,
    # se coloca un eje posterior en el apoyo, el segundo a 4.30 m y el eje
    # frontal a 8.60 m. El caso derecho es simetrico.
    r_camion_sin_im = (
        d.hl93_posterior
        + d.hl93_posterior * (1.0 - d.separacion_rear_min / d.L)
        + d.hl93_frontal * (1.0 - 2.0 * d.separacion_rear_min / d.L)
    )
    r_camion_im = r_camion_sin_im * d.incremento_dinamico
    r_tandem_im = (
        d.tandem_eje
        + d.tandem_eje * (1.0 - d.separacion_tandem / d.L)
    ) * d.incremento_dinamico
    r_carril = reaccion_uniforme(d.carga_carril, d.L)
    vehiculo_control = "camion" if r_camion_im >= r_tandem_im else "tandem"
    r_ll_im = max(r_camion_im, r_tandem_im) + r_carril
    r_ll_im *= d.presencia_multiple_1_carril

    peso_camion = d.hl93_frontal + 2.0 * d.hl93_posterior
    peso_tandem = 2.0 * d.tandem_eje
    peso_carril = d.carga_carril * d.L
    br_25 = max(0.25 * peso_camion, 0.25 * peso_tandem)
    br_05 = max(0.05 * (peso_camion + peso_carril),
                0.05 * (peso_tandem + peso_carril))
    br = max(br_25, br_05) * d.presencia_multiple_1_carril

    pb = d.presion_base_vigas_ksf * ksf_a_tf_m2
    pd = pb * (d.velocidad_viento / d.velocidad_base_viento) ** 2
    ws_lineal_calculado = pd * d.altura_expuesta
    ws_lineal_minimo = d.viento_minimo_kN_m / 9.80665
    ws_lineal = max(ws_lineal_calculado, ws_lineal_minimo)
    wl_lineal = d.viento_vehicular_klf * klf_a_tf_m

    r_dc = reaccion_uniforme(dc_lineal, d.L)
    r_dw = reaccion_uniforme(dw_lineal, d.L)
    r_pl = reaccion_uniforme(pl_lineal, d.L)
    r_ws = reaccion_uniforme(ws_lineal, d.L)
    r_wl = reaccion_uniforme(wl_lineal, d.L)
    r_wv = -reaccion_uniforme(d.viento_vertical * d.ancho_tablero, d.L)
    r_eq = (r_dc + r_dw) * d.coeficiente_sismico

    return {
        "DC_losa_tf_m": dc_losa,
        "DC_veredas_tf_m": dc_veredas,
        "DC_vigas_tf_m": dc_vigas,
        "DC_diafragmas_tf_m": dc_diafragmas,
        "DC_barandas_tf_m": dc_barandas,
        "DC_total_tf_m": dc_lineal,
        "R_DC_por_estribo_tf": r_dc,
        "DW_total_tf_m": dw_lineal,
        "R_DW_por_estribo_tf": r_dw,
        "PL_total_tf_m": pl_lineal,
        "R_PL_por_estribo_tf": r_pl,
        "vehiculo_control": vehiculo_control,
        "R_camion_IM_tf": r_camion_im,
        "R_tandem_IM_tf": r_tandem_im,
        "R_carril_tf": r_carril,
        "R_LL_IM_por_estribo_tf": r_ll_im,
        "BR_25_antes_FPM_tf": br_25,
        "BR_05_antes_FPM_tf": br_05,
        "BR_total_apoyo_fijo_tf": br,
        "WS_lineal_calculado_tf_m": ws_lineal_calculado,
        "WS_lineal_minimo_tf_m": ws_lineal_minimo,
        "WS_lineal_adoptado_tf_m": ws_lineal,
        "R_WS_transversal_por_estribo_tf": r_ws,
        "R_WL_transversal_por_estribo_tf": r_wl,
        "R_viento_vertical_por_estribo_tf": r_wv,
        "R_EQ_por_estribo_tf": r_eq,
        "R_vertical_nominal_DC_DW_PL_LL_tf": r_dc + r_dw + r_pl + r_ll_im,
    }


if __name__ == "__main__":
    for clave, valor in calcular().items():
        if isinstance(valor, float):
            print(f"{clave:42s} = {valor:10.4f}")
        else:
            print(f"{clave:42s} = {valor}")

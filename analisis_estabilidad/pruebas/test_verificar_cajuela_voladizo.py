import math

from analisis_estabilidad.elementos.cajuela.verificacion_voladizo import Parametros, evaluar


def test_equilibrio_y_fuentes_de_carga():
    r = evaluar(Parametros())
    casos = {x["nombre"]: x for x in r["casos"]}
    resistencia = casos["Resistencia I-a"]
    assert math.isclose(
        resistencia["V_tf_m"],
        resistencia["E_tri_tf_m"]
        + resistencia["E_trap_tf_m"]
        + resistencia["E_uni_tf_m"]
        + resistencia["P_puente_tf_m"],
        rel_tol=1e-12,
    )
    assert resistencia["M_tf_m_m"] > 0
    assert casos["Evento Extremo I"]["P_puente_tf_m"] == 0.24 * (25.98 + 2.88)


def test_fuerza_del_puente_actua_en_mesa_de_apoyo():
    p = Parametros()
    assert p.altura_carga_puente_m == 1.00
    r = evaluar(p)
    servicio = next(x for x in r["casos"] if x["nombre"] == "Servicio I")
    momento_esperado = (
        servicio["E_tri_tf_m"] * p.altura_m / 3.0
        + servicio["E_uni_tf_m"] * p.altura_m / 2.0
        + servicio["P_puente_tf_m"] * 1.00
    )
    assert math.isclose(servicio["M_tf_m_m"], momento_esperado, rel_tol=1e-12)


def test_evento_extremo_recorta_delta_eas_global_como_trapecio():
    p = Parametros()
    r = evaluar(p)
    evento = next(x for x in r["casos"] if x["nombre"] == "Evento Extremo I")
    assert evento["E_tri_tf_m"] > 0.0
    assert evento["E_trap_tf_m"] > 0.0
    assert evento["q_trap_corona_tf_m2"] > evento["q_trap_base_tf_m2"] > 0.0
    assert math.isclose(
        evento["q_trap_base_tf_m2"] / evento["q_trap_corona_tf_m2"],
        (p.altura_global_empuje_m - p.altura_m) / p.altura_global_empuje_m,
        rel_tol=1e-12,
    )
    resultante_trapecio = (
        0.5
        * (evento["q_trap_base_tf_m2"] + evento["q_trap_corona_tf_m2"])
        * p.altura_m
    )
    momento_trapecio = (
        evento["q_trap_base_tf_m2"] * p.altura_m**2 / 2.0
        + (evento["q_trap_corona_tf_m2"] - evento["q_trap_base_tf_m2"])
        * p.altura_m**2
        / 3.0
    )
    assert math.isclose(evento["E_trap_tf_m"], resultante_trapecio, rel_tol=1e-12)
    momento_esperado = (
        evento["E_tri_tf_m"] * p.altura_m / 3.0
        + momento_trapecio
        + evento["E_uni_tf_m"] * p.altura_m / 2.0
        + evento["P_puente_tf_m"] * p.altura_carga_puente_m
    )
    assert math.isclose(evento["M_tf_m_m"], momento_esperado, rel_tol=1e-12)


def test_armado_horizontal_y_cortante_cumplen():
    r = evaluar(Parametros())
    assert r["horizontal"]["cumple"]
    assert r["cumple_cortante"]


def test_resultado_global_con_delta_eas_trapezoidal_no_cumple_a_230_mm():
    r = evaluar(Parametros())
    assert r["caso_gobernante"].startswith("Evento Extremo")
    assert not r["cumple_global"]
    assert r["cumple_cortante"]
    assert r["separacion_maxima_vertical_5_8_mm"] == 155.0


def test_dimensionamiento_por_cara_usa_el_caso_inverso_en_la_frontal():
    p = Parametros()
    r = evaluar(p)
    inv = r["caso_inverso"]
    caras = {x["cara"]: x for x in r["caras_verticales"]}

    # La cara frontal/no relleno se dimensiona con el caso sismico inverso.
    assert math.isclose(
        caras["frontal/no relleno"]["momento_demanda_tf_m_m"],
        inv["M_inverso_tf_m_m"],
        rel_tol=1e-12,
    )
    # La cara posterior/relleno se dimensiona con el caso directo gobernante.
    assert math.isclose(
        caras["posterior/relleno"]["momento_demanda_tf_m_m"],
        r["momento_gobernante_tf_m_m"],
        rel_tol=1e-12,
    )
    # El caso inverso resulta menor que el directo (el vuelco directo gobierna
    # la cara del relleno), pero positivo (tracciona la cara frontal).
    assert 0.0 < inv["M_inverso_tf_m_m"] < r["momento_gobernante_tf_m_m"]
    # El momento inverso es la inercia menos el empuje estatico.
    assert math.isclose(
        inv["M_inverso_tf_m_m"],
        (inv["M_PIR_tf_m_m"] + inv["M_EQsuper_tf_m_m"])
        - (inv["M_Ea_tf_m_m"] + inv["M_Es_tf_m_m"]),
        rel_tol=1e-12,
    )


def test_base_con_peralte_efectivo_1_50_m_cumple_resistencia_pero_no_minimo():
    r = evaluar(Parametros())
    base = r["base_alternativa"]
    assert base["d_mm"] == 1500.0
    assert base["cumple_resistencia_flexion"]
    assert base["cumple_cortante"]
    assert not base["cumple_area"]
    assert not base["cumple"]

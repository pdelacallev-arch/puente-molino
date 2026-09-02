import math

from analisis_estabilidad.disenar_pantalla_e060_mtc import (
    ParametrosPantalla,
    analizar_viga_continua,
    calcular_diseno,
    generar_resumen_texto,
    niveles_franjas,
    presiones_en_profundidad,
)


def test_vano_simple_coincide_con_solucion_analitica():
    r = analizar_viga_continua((4.0,), 2.0, 1000.0)
    v = r.vanos[0]
    assert math.isclose(r.reacciones_tf[0], 4.0, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(r.reacciones_tf[1], 4.0, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(v.momento_izq_tf_m, 0.0, abs_tol=1e-10)
    assert math.isclose(v.momento_der_tf_m, 0.0, abs_tol=1e-10)
    assert math.isclose(v.momento_max_tf_m, 4.0, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(v.x_momento_max_m, 2.0, rel_tol=0, abs_tol=1e-10)


def test_dos_vanos_iguales_momento_analitico_en_apoyo():
    L = 5.0
    w = 3.0
    r = analizar_viga_continua((L, L), w, 2000.0)
    esperado = -w*L**2/8.0
    assert math.isclose(r.vanos[0].momento_der_tf_m, esperado, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(r.vanos[1].momento_izq_tf_m, esperado, rel_tol=0, abs_tol=1e-9)


def test_geometria_niveles_y_combinaciones():
    p = ParametrosPantalla()
    niveles = niveles_franjas(p)
    assert [round(x[2], 3) for x in niveles] == [13.150, 9.883, 6.617]
    pres = presiones_en_profundidad(niveles[0][2], p)
    assert math.isclose(
        pres["Resistencia I-a"]["presion"],
        pres["Resistencia I-b"]["presion"],
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert pres["Evento Extremo I"]["presion"] == max(
        pres["Evento Extremo I-A"]["presion"],
        pres["Evento Extremo I-B"]["presion"],
    )


def test_modelo_completo_es_simetrico_y_equilibrado():
    r = calcular_diseno()
    v = r["validaciones"]
    assert v["geometria_B_cierra"]
    assert v["profundidades_esperadas"]
    assert v["resistencia_Ia_Ib_separadas"]
    assert v["resistencia_Ia_Ib_coinciden"]
    assert v["equilibrio_matricial"]
    assert v["simetria"]
    assert v["cajuela_excluida"]
    assert v["flexion_cumple"]
    assert v["cortante_cumple"]
    assert v["fisuracion_cumple"]


def test_no_hay_cargas_de_cajuela_en_resultado():
    r = calcular_diseno()
    texto = str(r["resultados_por_caso"]).lower()
    assert "frenado" not in texto
    assert "apoyo" not in texto
    assert "impacto" not in texto


def test_diagramas_momento_distinguen_ambas_caras_y_reproducen_diseno():
    r = calcular_diseno()
    diagramas = r["diagramas_momento_diseno"]
    assert [x["franja"] for x in diagramas] == ["Inferior", "Intermedia", "Superior"]
    for diagrama, diseno in zip(diagramas, r["diseno_por_franja"]):
        puntos = diagrama["puntos"]
        assert all(x["Mu_exterior_tf_m"] >= 0 for x in puntos)
        assert all(x["Mu_interior_tf_m"] <= 0 for x in puntos)
        exterior = next(x for x in diseno["refuerzo"] if "exterior" in x["cara"])
        interior = next(x for x in diseno["refuerzo"] if "interior" in x["cara"])
        assert math.isclose(
            diagrama["maximo_exterior"]["Mu_tf_m"], exterior["Mu_tf_m"],
            rel_tol=0, abs_tol=1e-10,
        )
        assert math.isclose(
            diagrama["maximo_interior"]["Mu_abs_tf_m"], interior["Mu_tf_m"],
            rel_tol=0, abs_tol=1e-10,
        )


def test_resumen_en_consola_es_texto_plano_y_contiene_el_diseno():
    resumen = generar_resumen_texto(calcular_diseno())
    assert "Estado del modelo: CUMPLE" in resumen
    assert "Diseño por franja:" in resumen
    assert "Refuerzo vertical por cara:" in resumen
    assert "#" not in resumen

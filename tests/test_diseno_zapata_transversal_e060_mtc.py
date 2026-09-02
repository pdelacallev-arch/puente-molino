import math

import pytest

from analisis_estabilidad.disenar_zapata_transversal_e060_mtc import (
    GEOM,
    ParametrosZapataTransversal,
    calcular_diseno,
    generar_markdown,
    integrar_presion_lineal,
    momento_en,
)


def test_integracion_lineal_coincide_con_trapecio():
    q_punta, q_talon = 10.0, 22.0
    a, b = GEOM.B-1.0, GEOM.B
    qa = q_punta+(q_talon-q_punta)*a/GEOM.B
    esperado = 0.5*(qa+q_talon)*(b-a)
    assert integrar_presion_lineal(q_punta, q_talon, a, b) == esperado


def test_cargas_se_reconstruyen_y_proceden_del_agente():
    r = calcular_diseno()
    assert r["fuente_solicitaciones"].endswith("interface_1")
    for c in r["cargas_por_caso"]:
        assert math.isclose(
            c["reaccion_bruta_tf_m"]-c["carga_descendente_tf_m"],
            c["carga_neta_ascendente_tf_m"], abs_tol=1e-10,
        )
        assert c["x_fin_m"] == GEOM.B
        assert c["x_fin_m"]-c["x_inicio_m"] == 1.0


def test_modelo_es_simetrico_equilibrado_y_tiene_nueve_apoyos():
    r = calcular_diseno()
    v = r["validaciones"]
    assert v["nueve_apoyos"]
    assert v["cargas_netas_no_nulas"]
    assert v["signo_carga_neta_reportado"]
    assert v["equilibrio_matricial"]
    assert v["simetria"]
    for caso in r["analisis_por_caso"]:
        assert len(caso["reacciones_verticales_tf"]) == 9


def test_signos_fisicos_y_envolvente_reproducen_diagramas():
    r = calcular_diseno()
    e = r["envolvente_momentos"]
    assert e["maximo_negativo"]["Mu_abs_tf_m"] > 0
    assert e["maximo_positivo"]["Mu_tf_m"] > 0
    for p in e["puntos"]:
        assert p["Mu_positivo_tf_m"] >= 0
        assert p["Mu_negativo_tf_m"] <= 0
    servicio = next(x for x in r["analisis_por_caso"] if x["caso_clave"] == "case_service_I")
    assert math.isclose(momento_en(servicio, 0, 0), servicio["vanos"][0]["momento_izq_tf_m"])


def test_diseno_dual_incluye_minimos_temperatura_y_distribucion():
    r = calcular_diseno()
    d = r["diseno"]
    assert d["cortante"]["cumple"]
    principal = d["refuerzo_principal_transversal"]
    distribucion = d["refuerzo_distribucion_longitudinal"]
    assert all(x["DCR_flexion"] <= 1 for x in principal)
    assert all(x["fisuracion_cumple"] for x in principal)
    assert all(x["As_min_cara_E060_cm2_m"] == 18.0 for x in principal)
    assert all(x["As_provisto_cm2_m"] >= x["As_requerido_cm2_m"] for x in principal)
    assert all(x["As_provisto_cm2_m"] >= x["As_requerido_cm2_m"] for x in distribucion)


def test_traslapes_ganchos_y_zonas_de_despiece_estan_definidos():
    d = calcular_diseno()["diseno"]
    assert len(d["desarrollo_traslapes_ganchos"]) == 2
    for x in d["desarrollo_traslapes_ganchos"]:
        assert x["traslape_adoptado_mm"] >= x["traslape_requerido_mm"]
        assert x["gancho_estandar"] == "90 grados"
        assert x["gancho_cabe"]
        assert x["extension_recta_mm"] >= 12*x["diametro_mm"]
    assert len(d["zonas_traslape"]) == 2
    assert all(len(x["centros_s_m"]) == 2 for x in d["zonas_traslape"])


def test_resumen_armado_expone_areas_control_dcr_y_cumplimiento():
    resultado = calcular_diseno()
    diseno = resultado["diseno"]
    resumen = diseno["resumen_acero"]

    assert diseno["estado_armado"] == "CUMPLE"
    assert len(resumen) == 4
    for acero in resumen:
        assert acero["As_requerido_cm2_m"] == max(
            acero["As_calculado_cm2_m"],
            acero["As_normativo_cm2_m"],
        )
        assert acero["As_dispuesto_cm2_m"] >= acero["As_requerido_cm2_m"]
        assert acero["DCR_acero"] == pytest.approx(
            acero["As_requerido_cm2_m"] / acero["As_dispuesto_cm2_m"],
            abs=1e-3,
        )
        assert acero["control_normativo"]
        assert acero["cumple"]


def test_markdown_distingue_dcr_acero_de_dcr_flexion():
    reporte = generar_markdown(calcular_diseno())

    assert "Armado propuesto y verificación de áreas" in reporte
    assert "As calculado" in reporte
    assert "As normativo" in reporte
    assert "Control normativo" in reporte
    assert "As dispuesto" in reporte
    assert "D/C acero" in reporte
    assert "D/C flexión" in reporte
    assert "Cumple" in reporte

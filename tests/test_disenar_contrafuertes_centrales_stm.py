from pathlib import Path

import pytest

from analisis_estabilidad.disenar_contrafuertes_centrales_stm import (
    ENTRADA_PREDETERMINADA,
    ParametrosDisenoContrafuertes,
    _longitudes_desarrollo,
    cargar_analisis,
    disenar,
    equilibrio_stm,
    escribir_entregables,
    formar_envolventes,
    generar_svg,
    seleccionar_armado_principal,
)


@pytest.fixture(scope="module")
def analisis():
    return cargar_analisis(ENTRADA_PREDETERMINADA)


@pytest.fixture(scope="module")
def resultado(analisis):
    return disenar(analisis)


def test_envolvente_reproduce_acciones_base_y_cubre_15_casos(analisis):
    env = formar_envolventes(analisis)
    base = env["comun_resistencia_evento"][0]
    assert base["V_u_kN"] == pytest.approx(1045.4964939670601, abs=1e-9)
    assert base["M_u_kN_m"] == pytest.approx(5013.558135197523, abs=1e-9)
    assert env["numero_resultados_cubiertos"] == 15
    assert env["cubre_15_resultados"]


def test_equilibrio_vectorial_stm_es_exacto():
    p = ParametrosDisenoContrafuertes()
    stm = equilibrio_stm(1045.4964939670601, 5013.558135197523,
                         0.0, 25.400, p, 25.400)
    assert stm["error_relativo_equilibrio"] < 1e-12
    tx, tz = stm["tirante_vector_kN"]
    cx, cz = stm["biela_vector_kN"]
    assert tx+cx == pytest.approx(1045.4964939670601)
    assert tz+cz == pytest.approx(0.0)
    assert tz*stm["brazo_perpendicular_m"] == pytest.approx(5013.558135197523)


def test_seleccion_automatica_satisface_area_y_constructibilidad():
    p = ParametrosDisenoContrafuertes()
    acero = seleccionar_armado_principal(2700.0, 2, p)
    assert acero["As_provisto_mm2"] >= 2700.0
    assert acero["separacion_libre_mm"] >= acero["separacion_libre_minima_mm"]
    assert acero["barra"] == '1"'
    assert acero["numero_capas"] == 2
    assert acero["barras_por_capa"] == [3, 3]


def test_desarrollo_y_gancho_son_geometricamente_coherentes():
    p = ParametrosDisenoContrafuertes()
    ld = _longitudes_desarrollo(25.400, p)
    assert ld["ld_recto_mm"] >= 300.0
    assert ld["ld_gancho_90_mm"] >= 8*25.400
    assert ld["extension_gancho_mm"] == pytest.approx(12*25.400)
    assert ld["diametro_interior_doblado_mm"] == pytest.approx(6*25.400)
    assert ld["traslape_clase_b_mm"] == pytest.approx(1.3*ld["ld_recto_mm"])


def test_diseno_comun_cumple_todos_los_mecanismos(resultado):
    assert resultado["estado"] == "CUMPLE"
    assert resultado["validaciones"]["todos_los_mecanismos_cumplen"]
    assert resultado["validaciones"]["dcr_maximo"] <= 1.0
    assert resultado["validaciones"]["equilibrio_max_error_relativo"] < 1e-6
    assert resultado["armado_principal_comun"]["barras_continuas_corona"] >= 2
    assert resultado["armado_principal_comun"]["diametro_mm"] <= 25.4
    assert resultado["armado_principal_comun"]["barra"] == '1"'
    for zona in resultado["zonas"]:
        assert zona["tirante"]["diametro_mm"] <= 25.4
        assert zona["tirante"]["As_provisto_mm2"] >= zona["tirante"]["As_requerido_mm2"]
        for mecanismo in ("tirante", "biela", "nodo_cct", "corte_convencional"):
            assert zona[mecanismo]["DCR"] <= 1.0
    for corte in resultado["cortes_barras"]:
        assert corte["longitud_provista_sobre_lomo_mm"]+1e-6 >= corte["ld_medido_sobre_lomo_mm"]
    ubicaciones = {x["ubicacion"] for x in resultado["zonas_nodales"]}
    assert "contrafuerte–zapata" in ubicaciones
    assert "corona" in ubicaciones
    assert sum(x.startswith("pantalla–alma") for x in ubicaciones) == 3
    assert all(x["DCR"] <= 1.0 for x in resultado["zonas_nodales"])


def test_cf_c1_y_cf_c3_son_simetricos_y_cf_c2_queda_cubierto(resultado):
    assert resultado["validaciones"]["simetria_C1_C3"]
    c1 = resultado["dcr_individuales"]["CF-C1"]
    c2 = resultado["dcr_individuales"]["CF-C2"]
    c3 = resultado["dcr_individuales"]["CF-C3"]
    for a, b, c in zip(c1, c2, c3):
        assert a["T_u_kN"] == pytest.approx(c["T_u_kN"], abs=1e-9)
        assert b["DCR_tirante"] <= a["DCR_tirante"]+1e-9
        assert b["DCR_nodo"] <= a["DCR_nodo"]+1e-9


def test_malla_cumple_rho_y_separacion(resultado):
    m = resultado["malla_fisuracion"]
    assert 2*m["As_provisto_por_cara_mm2_m"] >= (
        m["rho_total_requerida"]
        *resultado["parametros"]["espesor_m"]*1000*1000
    )
    assert m["espaciamiento_mm"] <= m["separacion_maxima_mtc_mm"]


def test_generacion_detalle_svg_y_entregables(tmp_path, resultado):
    svg = generar_svg(resultado)
    assert svg.startswith("<svg")
    assert "DETALLE COMÚN CF-C1 / CF-C2 / CF-C3" in svg
    assert "6.10" in svg and "1.17" in svg and "9.80" in svg
    rutas = escribir_entregables(resultado, tmp_path)
    assert len(rutas) == 4
    assert all(Path(r).exists() and Path(r).stat().st_size > 0 for r in rutas)
    assert rutas[-1].suffix == ".png"

import pytest

from analisis_estabilidad.elementos.zapata.diseno_longitudinal_e060 import (
    ParametrosDiseno,
    disenar,
    generar_markdown,
)


def test_resumen_acero_expone_areas_control_y_dcr():
    resultado = disenar(ParametrosDiseno())
    resumen = resultado["resumen_acero"]

    assert resultado["estado_armado"] == "CUMPLE"
    assert len(resumen) == 6
    assert sum(r["direccion"] == "longitudinal" for r in resumen) == 4
    assert sum(r["direccion"] == "transversal" for r in resumen) == 2

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


def test_controles_distinguen_flexion_minimo_y_distribucion():
    resumen = disenar(ParametrosDiseno())["resumen_acero"]
    por_armado = {r["armado"]: r for r in resumen}

    assert por_armado["Longitudinal — punta, cara inferior"][
        "control_normativo"
    ] == "demanda de flexión"
    assert "mínimo de flexión" in por_armado[
        "Longitudinal — punta, cara superior"
    ]["control_normativo"]
    assert "retracción y temperatura" in por_armado[
        "Transversal — cara superior"
    ]["control_normativo"]


def test_markdown_reporta_armado_como_el_dentellon():
    reporte = generar_markdown(disenar(ParametrosDiseno()))

    assert "Armado propuesto y verificación de áreas" in reporte
    assert "As calculado" in reporte
    assert "As normativo" in reporte
    assert "Control normativo" in reporte
    assert "As requerido" in reporte
    assert "As dispuesto" in reporte
    assert "D/C acero" in reporte
    assert "Cumple" in reporte

import math

import pytest

from analisis_estabilidad.elementos.dentellon.diseno_e060 import (
    ParametrosDentellon,
    disenar,
    generar_markdown,
)


def _caso_proyecto() -> dict:
    return disenar(ParametrosDentellon(espesor_m=0.70, profundidad_m=1.50))


def test_dentellon_es_monolitico_y_se_idealiza_como_losa():
    resultado = _caso_proyecto()
    assert resultado["parametros"]["tipo_conexion"] == "monolitica"
    assert "losa vertical" in resultado["geometria"]["idealizacion_estructural"]
    assert resultado["junta_zapata_dentellon"]["anclaje_acreditado"]


def test_evento_extremo_usa_pasivo_unitario_y_no_deja_pendiente():
    resultado = _caso_proyecto()
    extremo = next(
        caso for caso in resultado["resultados_por_caso"]
        if caso["caso_clave"] == "case_extreme_event_I"
    )
    assert extremo["factor_pasivo_estabilidad"] == 1.0
    assert resultado["parametros"]["factores_pasivo_confirmados"]
    assert not any(
        "factor" in pendiente.lower() and "pasivo" in pendiente.lower()
        for pendiente in resultado["pendientes_cierre"]
    )


def test_servicio_no_se_usa_como_caso_de_diseno_estructural():
    resultado = _caso_proyecto()
    assert resultado["caso_gobernante"] == "Evento Extremo I (Sismo)"
    assert "Servicio I" not in resultado["casos_gobernantes_estructurales"]
    assert resultado["casos_gobernantes_estructurales"] == [
        "Resistencia I-a",
        "Resistencia I-b",
        "Evento Extremo I (Sismo)",
    ]

    reporte = generar_markdown(resultado)
    assert "Servicio I se emplea únicamente" in reporte
    assert "Caso estructural representativo gobernante" in reporte


def test_minimo_de_losa_se_reparte_entre_dos_caras():
    resultado = _caso_proyecto()
    minimo_total = 0.0018 * 100.0 * 70.0
    minimo_traccion = 0.0012 * 100.0 * 70.0
    assert resultado["flexion"]["numero_caras_acero_minimo"] == 2
    assert resultado["flexion"]["As_minimo_total_cm2_m"] == minimo_total
    assert resultado["flexion"]["As_normativo_cm2_m"] == minimo_traccion
    assert resultado["vertical_cara_opuesta"]["As_requerido_cm2_m"] == pytest.approx(
        minimo_total - minimo_traccion)
    assert resultado["distribucion_por_cara"]["As_requerido_cm2_m"] == pytest.approx(
        minimo_total / 2.0)
    assert (
        resultado["flexion"]["As_normativo_cm2_m"]
        + resultado["vertical_cara_opuesta"]["As_normativo_cm2_m"]
    ) == pytest.approx(minimo_total)


def test_minimo_de_losa_puede_colocarse_en_una_cara():
    resultado = disenar(ParametrosDentellon(
        espesor_m=0.70,
        profundidad_m=1.50,
        numero_caras_acero_minimo=1,
    ))
    minimo_total = 0.0018 * 100.0 * 70.0
    assert resultado["flexion"]["As_normativo_cm2_m"] == minimo_total
    assert resultado["vertical_cara_opuesta"]["As_requerido_cm2_m"] == 0.0
    assert resultado["vertical_cara_opuesta"]["As_provisto_cm2_m"] == 0.0
    assert resultado["vertical_cara_opuesta"]["barra"] is None
    assert resultado["distribucion_por_cara"]["numero_caras_activas"] == 1
    assert resultado["distribucion_por_cara"]["As_requerido_cm2_m"] == minimo_total
    assert resultado["estado_estructural_e060"] == "CUMPLE"


def test_reporte_expone_areas_y_relacion_demanda_capacidad_del_acero():
    resultado = _caso_proyecto()
    resumen = resultado["resumen_acero"]
    assert len(resumen) == 3
    for acero in resumen:
        assert acero["As_requerido_cm2_m"] == max(
            acero["As_calculado_cm2_m"], acero["As_normativo_cm2_m"])
        assert acero["As_dispuesto_cm2_m"] > 0.0
        assert acero["control_normativo"]
        assert acero["DCR_acero"] == pytest.approx(
            acero["As_requerido_cm2_m"] / acero["As_dispuesto_cm2_m"],
            abs=1e-3,
        )

    reporte = generar_markdown(resultado)
    assert "As calculado" in reporte
    assert "As normativo asignado" in reporte
    assert "Control normativo" in reporte
    assert "As dispuesto" in reporte
    assert "D/C acero" in reporte


def test_armado_corregido_cumple_corte_friccion():
    resultado = _caso_proyecto()
    assert resultado["flexion"]["barra"] == '5/8"'
    assert resultado["flexion"]["espaciamiento_adoptado_mm"] == 180.0
    assert resultado["vertical_cara_opuesta"]["barra"] == '5/8"'
    assert resultado["vertical_cara_opuesta"]["espaciamiento_adoptado_mm"] == 400.0
    assert resultado["distribucion_por_cara"]["barra"] == '5/8"'
    assert resultado["distribucion_por_cara"]["espaciamiento_adoptado_mm"] == 310.0
    assert resultado["junta_zapata_dentellon"]["cumple_teorico"]
    assert resultado["estado_estructural_e060"] == "CUMPLE"


def test_permite_asumir_barras_y_espaciamientos_desde_los_datos():
    resultado = disenar(ParametrosDentellon(
        espesor_m=0.70,
        profundidad_m=1.50,
        barra_principal_asumida='3/4"',
        espaciamiento_principal_asumido_mm=180.0,
        barra_opuesta_asumida='5/8"',
        espaciamiento_opuesto_asumido_mm=150.0,
        barra_horizontal_asumida='1/2"',
        espaciamiento_horizontal_asumido_mm=100.0,
    ))
    assert resultado["flexion"]["barra"] == '3/4"'
    assert resultado["flexion"]["espaciamiento_adoptado_mm"] == 180.0
    assert resultado["vertical_cara_opuesta"]["barra"] == '5/8"'
    assert resultado["vertical_cara_opuesta"]["espaciamiento_adoptado_mm"] == 150.0
    assert resultado["distribucion_por_cara"]["barra"] == '1/2"'
    assert resultado["distribucion_por_cara"]["espaciamiento_adoptado_mm"] == 100.0
    assert resultado["flexion"]["seleccion"] == "barra y espaciamiento asumidos"


def test_armado_asumido_insuficiente_se_reporta_sin_reemplazarlo():
    resultado = disenar(ParametrosDentellon(
        espesor_m=0.70,
        profundidad_m=1.50,
        barra_principal_asumida='1/2"',
        espaciamiento_principal_asumido_mm=400.0,
    ))
    assert resultado["flexion"]["espaciamiento_adoptado_mm"] == 400.0
    assert not resultado["flexion"]["cumple"]
    assert resultado["estado_estructural_e060"] == "NO CUMPLE"


def test_espaciamiento_asumido_requiere_indicar_barra():
    with pytest.raises(ValueError, match="Debe indicar la barra"):
        disenar(ParametrosDentellon(
            espesor_m=0.70,
            profundidad_m=1.50,
            espaciamiento_horizontal_asumido_mm=150.0,
        ))

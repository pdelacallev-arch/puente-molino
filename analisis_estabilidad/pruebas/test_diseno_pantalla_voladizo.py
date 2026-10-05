"""Pruebas unitarias para el diseño de la pantalla en voladizo (AASHTO LRFD / MTC)."""

from pathlib import Path
import pytest

from analisis_estabilidad.elementos.pantalla.diseno_voladizo import (
    ParametrosPantallaVoladizo,
    calcular_geometria_y_peso,
    calcular_coeficientes_empuje,
    calcular_cargas_base,
    calcular_combinaciones,
    evaluar,
    reporte_markdown,
)
from analisis_estabilidad.elementos.pantalla.diagrama_voladizo import (
    generar_diagrama_cargas,
    generar_diagramas_esfuerzos_y_armado,
)


@pytest.fixture
def parametros_molinohuayco() -> ParametrosPantallaVoladizo:
    return ParametrosPantallaVoladizo(
        altura_total_hp_m=8.37,
        altura_efectiva_m=5.33,
        altura_global_h_m=9.87,
        espesor_sup1_m=0.40,
        espesor_sup2_m=0.40,
        espesor_inf_m=0.987,
        ancho_franja_m=1.00,
        recubrimiento_terreno_mm=50.0,
        recubrimiento_libre_mm=50.0,
        barras_verticales=('5/8"', '3/4"', '1"'),
        barras_temperatura=('1/2"', '5/8"'),
    )


def test_geometria_y_peso(parametros_molinohuayco):
    p = parametros_molinohuayco
    geom = calcular_geometria_y_peso(p)

    assert geom["h_cajuela_m"] == pytest.approx(3.04, abs=0.01)
    assert geom["h_fuste_m"] == pytest.approx(5.33, abs=0.01)
    # Peso total pantalla
    assert geom["peso_pantalla_total_tf_m"] > 10.0
    assert 2.5 < geom["y_cg_pantalla_m"] < 4.5


def test_evaluacion_completa_cumple_todas_las_verificaciones(parametros_molinohuayco):
    resultado = evaluar(parametros_molinohuayco)

    assert resultado["estado"] == "OK"
    assert resultado["cumple_global"] is True

    # Paso 3: Combinaciones
    comb = resultado["combinaciones"]
    assert comb["Evento_Extremo_I"]["M_u_tf_m_m"] > comb["Resistencia_I"]["M_u_tf_m_m"]
    assert comb["Evento_Extremo_I"]["V_u_tf_m"] > 20.0

    # Paso 4: Flexión
    flex = resultado["diseno_flexion"]["adoptado"]
    assert flex["cumple"] is True
    assert flex["DCR_flexion"] <= 1.0
    assert flex["As_provisto_cm2_m"] >= flex["As_requerido_cm2_m"]

    # Paso 5: Acero mínimo
    minimo = resultado["acero_minimo"]
    assert minimo["cumple"] is True
    assert minimo["Mn_provisto_tf_m_m"] >= minimo["M_minimo_exigido_tf_m_m"]

    # Paso 6: Acero de temperatura
    temp = resultado["acero_temperatura"]["adoptado"]
    assert temp["cumple"] is True
    assert temp["As_provisto_cm2_m"] >= resultado["acero_temperatura"]["As_temp_normativo_cm2_m"]

    # Paso 7: Fisuración bajo servicio
    fis = resultado["fisuracion_servicio"]
    assert fis["cumple"] is True
    assert fis["s_adoptado_cm"] <= fis["s_max_fisuracion_cm"]

    # Paso 8: Corte sin estribos
    cort = resultado["cortante"]
    assert cort["cumple"] is True
    assert cort["requiere_estribos"] is False
    assert cort["Vr_tf_m"] >= cort["Vu_tf_m"]


def test_reporte_markdown_generado(parametros_molinohuayco):
    resultado = evaluar(parametros_molinohuayco)
    md = reporte_markdown(resultado)

    assert "# MEMORIA DE CÁLCULO: DISEÑO DE LA PANTALLA DE ESTRIBO EN VOLADIZO" in md
    assert "PASO 1" in md or "Paso 1" in md
    assert "PASO 4" in md or "Paso 4" in md
    assert "PASO 8" in md or "Paso 8" in md
    assert "CUMPLE" in md


def test_generacion_figuras(parametros_molinohuayco, tmp_path):
    resultado = evaluar(parametros_molinohuayco)
    f1 = generar_diagrama_cargas(resultado, tmp_path / "cargas.png", dpi=80)
    f2 = generar_diagramas_esfuerzos_y_armado(resultado, tmp_path / "esfuerzos.png", dpi=80)

    assert f1.exists()
    assert f1.stat().st_size > 10_000
    assert f2.exists()
    assert f2.stat().st_size > 10_000

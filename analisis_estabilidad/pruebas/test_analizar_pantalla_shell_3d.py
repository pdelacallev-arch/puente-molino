import math

import numpy as np
import pytest

from analisis_estabilidad.elementos.pantalla import analisis_shell_3d as shell
from analisis_estabilidad.elementos.pantalla.analisis_shell_3d import (
    ParametrosShell,
    calcular,
    coeficientes_presion,
    generar_malla,
    longitud_poligonal,
    presion_caso,
    rigidez_elemento,
    vector_carga,
)


@pytest.fixture(scope="module")
def resultado_grueso():
    return calcular(ParametrosShell(tamano_malla_m=1.20), incluir_convergencia=False)


def test_geometria_conserva_controles_y_longitud():
    p = ParametrosShell(tamano_malla_m=0.90)
    m = generar_malla(p)
    controles = {(x, y, tipo, nombre) for x, y, tipo, nombre in p.puntos_planta}
    obtenidos = {(e.x_m, e.y_m, e.tipo, e.etiqueta)
                 for e in m.estaciones if e.etiqueta}
    assert obtenidos == controles
    assert longitud_poligonal(p.puntos_planta) == pytest.approx(27.19354831445)
    assert sum(e.es_contrafuerte for e in m.estaciones) == 9


def test_rigidez_shell_es_simetrica_y_semidefinida():
    p = ParametrosShell(tamano_malla_m=1.0)
    m = generar_malla(p)
    ke, _, _ = rigidez_elemento(m.nodos[m.elementos[0]], p)
    assert np.max(np.abs(ke-ke.T)) < 1e-6
    valores = np.linalg.eigvalsh(ke)
    assert valores.min() > -1e-5
    assert np.count_nonzero(np.abs(valores) < 1e-5) >= 6


def test_resultante_de_presion_coincide_con_integracion_analitica():
    p = ParametrosShell(tamano_malla_m=0.9)
    m = generar_malla(p)
    c = coeficientes_presion(p)
    f, _ = vector_carga(m, p, "Servicio I", c)
    obtenida = f.reshape((-1, 6))[:, :3].sum(axis=0)
    q0 = presion_caso(0.0, "Servicio I", p, c)[0]
    qh = presion_caso(p.altura_modelada_m, "Servicio I", p, c)[0]
    integral_vertical_kn_m = 0.5*(q0+qh)*p.altura_modelada_m*9.80665
    esperada = np.zeros(3)
    for a, b in zip(p.puntos_planta, p.puntos_planta[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        L = math.hypot(dx, dy)
        # +normal del shell = tangente en planta × vertical.
        normal = np.array([dy/L, -dx/L, 0.0])
        esperada += normal*L*integral_vertical_kn_m
    assert obtenida == pytest.approx(esperada, rel=1e-10, abs=1e-8)


def test_modelo_cierra_equilibrio_simetria_y_casos(resultado_grueso):
    v = resultado_grueso["validaciones"]
    assert v["equilibrio_cumple"]
    assert v["simetria_cumple"]
    assert v["cajuela_excluida"]
    assert v["resistencia_ia_ib_independientes"]
    assert v["resistencia_ia_ib_coinciden"]
    assert len(resultado_grueso["casos"]) == 5
    assert {x["caso"] for x in resultado_grueso["casos"]} >= {
        "Evento Extremo I-A", "Evento Extremo I-B",
    }


def test_modelo_factoriza_una_sola_vez_para_todos_los_casos(monkeypatch):
    original = shell.factorized
    llamadas = 0

    def contar_factorizacion(*args, **kwargs):
        nonlocal llamadas
        llamadas += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(shell, "factorized", contar_factorizacion)
    shell.analizar_modelo(ParametrosShell(tamano_malla_m=1.50))

    assert llamadas == 1


def test_diseno_dual_cumple_y_no_disena_contrafuertes(resultado_grueso):
    assert resultado_grueso["estado"] == "CUMPLE"
    assert len(resultado_grueso["diseno_refuerzo"]) == 36
    assert max(x["DCR_interaccion"] for x in resultado_grueso["diseno_refuerzo"]) <= 1
    assert max(x["DCR_cortante"] for x in resultado_grueso["cortante_compresion"]) <= 1
    assert "diseño de contrafuertes" in resultado_grueso["alcance_excluido"]


def test_lineas_diseno_siguen_tres_niveles_y_coordenada_desarrollada(resultado_grueso):
    lineas = resultado_grueso["lineas_diseno"]
    assert [x["franja"] for x in lineas] == ["Inferior", "Intermedia", "Superior"]
    h = resultado_grueso["parametros"]["altura_modelada_m"]
    assert [x["z_sobre_zapata_m"] for x in lineas] == pytest.approx([
        0.0, h/3.0, 2*h/3.0,
    ])
    for linea in lineas:
        puntos = linea["puntos"]
        assert len(puntos) == len(resultado_grueso["malla"]["estaciones"])-1
        s = [x["s_m"] for x in puntos]
        assert s == sorted(s)
        assert all(x["Mu_exterior_kNm_m"] >= 0 for x in puntos)
        assert all(x["Mu_interior_kNm_m"] >= 0 for x in puntos)
        assert linea["maximo_exterior"]["Mu_kNm_m"] == pytest.approx(
            max(x["Mu_exterior_kNm_m"] for x in puntos)
        )
        assert linea["maximo_interior"]["Mu_kNm_m"] == pytest.approx(
            max(x["Mu_interior_kNm_m"] for x in puntos)
        )


def test_presiones_resistencia_ia_decrecen_con_la_altura(resultado_grueso):
    presiones = resultado_grueso["presiones_franjas_resistencia_ia"]
    assert [x["franja"] for x in presiones] == ["Inferior", "Intermedia", "Superior"]
    totales = [x["presion_total_tf_m2"] for x in presiones]
    assert totales == sorted(totales, reverse=True)
    for x in presiones:
        assert x["presion_total_tf_m2"] == pytest.approx(
            x["EH_factorizado_tf_m2"]+x["LS_factorizado_tf_m2"]
        )
        assert x["presion_total_kN_m2"] == pytest.approx(
            9.80665*x["presion_total_tf_m2"]
        )

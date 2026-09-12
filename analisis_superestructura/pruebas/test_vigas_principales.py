from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from analisis_superestructura.elementos.vigas_principales.analisis.moviles import (
    analizar_hl93,
    influencia_corte,
    influencia_momento,
)
from analisis_superestructura.elementos.vigas_principales.analisis.parrilla import analizar_parrilla
from analisis_superestructura.elementos.vigas_principales.analisis.respuesta import (
    deformada_desde_momento,
    respuesta_distribuida,
)
from analisis_superestructura.elementos.vigas_principales.analisis.secciones import (
    propiedades_acero,
    propiedades_por_segmento,
)
from analisis_superestructura.elementos.vigas_principales.configuracion import (
    validar_configuracion,
)
from analisis_superestructura.elementos.vigas_principales.modelos import Busqueda, GrupoBusqueda
from analisis_superestructura.elementos.vigas_principales.orquestador import (
    analizar,
    buscar_secciones,
    verificar,
)
from analisis_superestructura.elementos.vigas_principales.reportes.exportar import exportar_analisis
from analisis_superestructura.elementos.vigas_principales.unidades import normalizar_a_si


RAIZ = Path(__file__).parents[2]
EJEMPLO = RAIZ / "analisis_superestructura/casos/bartra/R00/entrada.yaml"


def test_propiedades_seccion_bartra_reproducen_tabla_11():
    config = validar_configuracion(EJEMPLO)
    # Segmento central S1: Bartra p. 117 reporta A=0.0698 m2 e Ix=0.0479 m4.
    p = propiedades_acero(config.viga.segmentos[2])
    assert p.area / 1e6 == pytest.approx(0.0698, rel=1e-8)
    assert p.inercia_x / 1e12 == pytest.approx(0.0479, rel=2e-3)
    assert p.y_inferior / 1000.0 == pytest.approx(0.8692, rel=2e-4)
    assert p.modulo_inferior / 1e9 == pytest.approx(0.0551, rel=2e-3)


def test_propiedades_compuestas_separan_corto_y_largo_plazo():
    config = validar_configuracion(EJEMPLO)
    p = propiedades_por_segmento(config, "interior")[2]
    assert p["n"] > 1.0
    assert p["largo_plazo"].relacion_modular == pytest.approx(
        p["n"] * config.losa.factor_largo_plazo
    )
    assert p["corto_plazo"].inercia_x > p["largo_plazo"].inercia_x
    assert p["largo_plazo"].inercia_x > p["acero"].inercia_x


def test_lineas_influencia_viga_simple():
    L = 10_000.0
    x = np.array([5_000.0])
    z = np.array([2_500.0, 5_000.0, 7_500.0])
    m = influencia_momento(L, x, z)[0]
    v = influencia_corte(L, x, z)[0]
    assert m.tolist() == pytest.approx([1250.0, 2500.0, 1250.0])
    assert v.tolist() == pytest.approx([-0.25, -0.5, 0.25])


def test_hl93_incluye_maximo_continuo_segun_barre():
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/MODIFICADO-R01/entrada.yaml"
    config = validar_configuracion(ejemplo)
    resultado = analizar_hl93(config)

    # Camión normal con separación posterior mínima. La carga de carril desplaza
    # ligeramente hacia el centro la sección de Barré correspondiente al eje
    # interior (segundo eje).
    camion = config.trafico.camion
    im = 1.0 + config.trafico.incremento_dinamico
    cargas = np.array(
        [camion.eje_frontal, camion.eje_posterior, camion.eje_posterior]
    ) * im
    offsets = np.array(
        [
            0.0,
            camion.separacion_frontal,
            camion.separacion_frontal + camion.separacion_posterior_min,
        ]
    )
    resultante = float(np.dot(cargas, offsets) / np.sum(cargas))
    denominador = float(
        np.sum(cargas) + config.trafico.carga_carril * config.geometria.luz / 2.0
    )
    x_barre = config.geometria.luz / 2.0 - float(
        np.sum(cargas) * (resultante - offsets[1]) / (2.0 * denominador)
    )

    indice_maximo = int(np.argmax(resultado.momento_nmm))
    assert resultado.x_mm[indice_maximo] / 1000.0 == pytest.approx(x_barre, abs=1e-9)
    assert resultado.momento_nmm[indice_maximo] / 1e6 == pytest.approx(
        7797.6417147649, rel=1e-11
    )

    centro = int(np.argmin(np.abs(resultado.x_mm - config.geometria.luz * 500.0)))
    assert resultado.vehiculo_control_momento[centro] == "camion"
    assert (
        resultado.posicion_critica_centro_mm
        + camion.separacion_frontal * 1000.0
    ) == pytest.approx(config.geometria.luz * 500.0, abs=1e-8)


def test_maximo_hl93_no_depende_del_paso_longitudinal():
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/MODIFICADO-R01/entrada.yaml"
    config = validar_configuracion(ejemplo)
    grueso = config.model_copy(
        update={"analisis": config.analisis.model_copy(update={"paso_vehiculo": 2.0})}
    )
    fino = config.model_copy(
        update={"analisis": config.analisis.model_copy(update={"paso_vehiculo": 0.05})}
    )
    maximo_grueso = float(np.max(analizar_hl93(grueso).momento_nmm))
    maximo_fino = float(np.max(analizar_hl93(fino).momento_nmm))
    assert maximo_grueso == pytest.approx(maximo_fino, rel=1e-12)


def test_viga_prismatica_carga_uniforme_y_deflexion():
    L = 20_000.0
    x = np.linspace(0.0, L, 1001)
    w = np.full_like(x, 10.0)  # N/mm
    momento, _, r1, r2 = respuesta_distribuida(x, w)
    assert r1 == pytest.approx(w[0] * L / 2.0, rel=1e-12)
    assert r2 == pytest.approx(w[0] * L / 2.0, rel=1e-12)
    assert momento[len(x) // 2] == pytest.approx(w[0] * L**2 / 8.0, rel=2e-6)
    e = 200_000.0
    inercia = np.full_like(x, 5.0e10)
    y = deformada_desde_momento(x, momento, e, inercia)
    exacta = 5.0 * w[0] * L**4 / (384.0 * e * inercia[0])
    assert abs(y[len(x) // 2]) == pytest.approx(exacta, rel=2e-5)
    assert y[0] == pytest.approx(0.0, abs=1e-12)
    assert y[-1] == pytest.approx(0.0, abs=1e-9)


def test_conversion_mks_a_si_es_explicita():
    datos = {
        "proyecto": {"sistema_unidades": "MKS"},
        "materiales": {
            "concreto": {"fc": 280.0, "ec": 284_000.0, "peso_unitario": 2.5},
            "acero_estructural": {"fy": 3500.0, "fu": 4500.0, "es": 2_000_000.0, "peso_unitario": 7.85},
            "acero_refuerzo": {"fy": 4200.0, "es": 2_000_000.0},
        },
        "construccion": {"carga_construccion": 0.2},
        "cargas": {"dw": 0.3},
        "trafico": {"tandem_eje": 11.2, "carga_carril": 0.95, "camion": {"eje_frontal": 3.6, "eje_posterior": 14.5}},
    }
    si = normalizar_a_si(datos)
    assert si["materiales"]["concreto"]["fc"] == pytest.approx(27.45862)
    assert si["materiales"]["acero_estructural"]["peso_unitario"] == pytest.approx(76.9822025)
    assert si["trafico"]["camion"]["eje_posterior"] == pytest.approx(142.196425)
    assert si["proyecto"]["sistema_unidades"] == "SI"


def test_conversion_mks_admite_cargas_diferenciadas_por_tipo():
    datos = {
        "proyecto": {"sistema_unidades": "MKS"},
        "materiales": {
            "concreto": {"fc": 280.0, "peso_unitario": 2.4},
            "acero_estructural": {"fy": 3500.0, "fu": 4500.0, "peso_unitario": 7.85},
        },
        "cargas": {"pl": {"interior": 0.0, "exterior": 0.37}},
    }
    si = normalizar_a_si(datos)
    assert si["cargas"]["pl"]["interior"] == 0.0
    assert si["cargas"]["pl"]["exterior"] == pytest.approx(0.37 * 9.80665)


def test_molinohuayco_aplica_cargas_diferenciadas_por_tipo():
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml"
    resultado = analizar(validar_configuracion(ejemplo))
    interior = resultado.tipos_viga["interior"]["cargas_lineales_n_mm"]
    exterior = resultado.tipos_viga["exterior"]["cargas_lineales_n_mm"]
    assert interior["DW"][0] == pytest.approx(3.38)
    assert exterior["DW"][0] == pytest.approx(1.69)
    assert interior["PL"][0] == pytest.approx(0.0)
    assert exterior["PL"][0] == pytest.approx(3.63)
    # Con apuntalamiento, el peso de la losa se incorpora a DC compuesta.
    assert interior["DC_compuesta"][0] == pytest.approx(9.6 + 0.54)
    assert exterior["DC_compuesta"][0] == pytest.approx(9.6 + 0.54 + 7.74)


def test_parrilla_conserva_equilibrio_y_simetria_transversal():
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml"
    config = validar_configuracion(ejemplo)
    resultado = analizar_parrilla(config)
    assert resultado.error_equilibrio_maximo < 1e-8
    assert resultado.participacion_momento.shape[1] == config.geometria.numero_vigas
    assert resultado.participacion_corte.shape == resultado.participacion_momento.shape
    assert np.sum(resultado.participacion_momento, axis=1) == pytest.approx(1.0, abs=1e-9)
    assert np.sum(resultado.participacion_corte, axis=1) == pytest.approx(1.0, abs=1e-9)
    centro = int(np.argmin(np.abs(resultado.centros_carril_mm)))
    assert resultado.participacion_momento[centro, 0] == pytest.approx(
        resultado.participacion_momento[centro, -1], rel=1e-9
    )
    assert 0.0 < resultado.factores.momento_interior < 1.20
    assert 0.0 < resultado.factores.momento_exterior < 1.20


def test_motor_usa_factores_de_parrilla_configurados():
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml"
    config = validar_configuracion(ejemplo)
    resultado = analizar(config)
    assert resultado.detalle_distribucion is not None
    assert resultado.factores_distribucion["momento_interior"] == pytest.approx(
        resultado.detalle_distribucion["factores"]["momento_interior"]
    )
    assert resultado.equilibrio_relativo < 1e-8


def test_envolvente_cortante_con_signo_y_maximo_en_apoyos():
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml"
    resultado = analizar(validar_configuracion(ejemplo))
    for datos in resultado.tipos_viga.values():
        cortantes = datos["cortantes_n"]
        positivo = cortantes["resistencia_i_positivo"]
        negativo = cortantes["resistencia_i_negativo"]
        absoluto = cortantes["resistencia_i_abs"]
        assert absoluto == pytest.approx(
            np.maximum(np.abs(positivo), np.abs(negativo)), rel=1e-12
        )
        indice_critico = int(np.argmax(absoluto))
        assert indice_critico in (0, len(absoluto) - 1)
        assert absoluto[len(absoluto) // 2] < min(absoluto[0], absoluto[-1])
        assert cortantes["servicio_ii_abs"] == pytest.approx(
            np.maximum(
                np.abs(cortantes["servicio_ii_positivo"]),
                np.abs(cortantes["servicio_ii_negativo"]),
            ),
            rel=1e-12,
        )


def test_exportacion_separa_acciones_envolventes_y_combinaciones(tmp_path):
    ejemplo = RAIZ / "analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml"
    resultado = analizar(validar_configuracion(ejemplo))
    salida = exportar_analisis(resultado, tmp_path)
    esperados = (
        "diagramas_acciones_permanentes.png",
        "envolvente_carga_movil_LL_IM.png",
        "combinacion_resistencia_i.png",
        "combinacion_servicio_ii.png",
        "envolvente_fatiga.png",
        "envolventes.png",
        "envolventes.csv",
    )
    assert all((salida / nombre).stat().st_size > 0 for nombre in esperados)
    encabezado = (salida / "envolventes.csv").read_text(encoding="utf-8").splitlines()[0]
    assert "M_LL_IM_interior_kNm" in encabezado
    assert "Vmax_resistencia_exterior_kN" in encabezado
    assert "Vmin_servicio_ii_interior_kN" in encabezado


def test_integracion_bartra_equilibrio_y_estado_condicional_o_falla():
    config = validar_configuracion(EJEMPLO)
    resultado = analizar(config)
    assert resultado.equilibrio_relativo < 1e-12
    assert 0.0 < resultado.factores_distribucion["momento_exterior"] < 2.0
    diseno = verificar(config, resultado)
    assert diseno.estado != "CUMPLE"
    assert diseno.pendientes
    assert all(np.isfinite(v.dcr) for checks in diseno.verificaciones.values() for v in checks)


def test_busqueda_un_candidato_es_determinista():
    config = validar_configuracion(EJEMPLO)
    busqueda = Busqueda(
        habilitada=True,
        peraltes_alma=(2000.0,),
        espesores_alma=(16.0,),
        anchos_ala_superior=(400.0,),
        espesores_ala_superior=(32.0,),
        anchos_ala_inferior=(500.0,),
        espesores_ala_inferior=(50.0,),
        grupos=(GrupoBusqueda(segmentos=(0, 1, 2, 3, 4)),),
        maximo_candidatos=2,
        mejores_alternativas=1,
    )
    cfg = config.model_copy(update={"busqueda": busqueda})
    a = buscar_secciones(cfg)
    b = buscar_secciones(cfg)
    assert a.evaluados == b.evaluados == 1
    lista_a = a.factibles or a.mejores_no_factibles
    lista_b = b.factibles or b.mejores_no_factibles
    assert lista_a[0].masa_kg == pytest.approx(lista_b[0].masa_kg)
    assert lista_a[0].maximo_dcr == pytest.approx(lista_b[0].maximo_dcr)

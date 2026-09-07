import json
import shutil
import uuid
from pathlib import Path

import pytest

from analisis_estabilidad.nucleo.configuracion import cargar_configuracion
from analisis_estabilidad.nucleo.contratos import (
    DependenciaEntrada,
    EntradaElemento,
    TrazabilidadEntrada,
    escribir_json_atomico,
    leer_resultado,
    sha256_archivo,
)
from analisis_estabilidad.nucleo.motores import ejecutar_entrada
from analisis_estabilidad.nucleo.orquestador import (
    DEPENDENCIAS,
    _aplicar_override,
    _huella_overrides,
    _seccion_objetivo,
)
from analisis_estabilidad.nucleo.rutas import RAIZ_CASOS, RAIZ_TEMPORAL, asegurar_interna


CONFIG = RAIZ_CASOS / "molinohuayco" / "R00" / "entrada.yaml"


@pytest.fixture()
def carpeta_contrato():
    ruta = asegurar_interna(RAIZ_TEMPORAL / "pytest_contratos" / uuid.uuid4().hex)
    ruta.mkdir(parents=True)
    yield ruta
    shutil.rmtree(ruta, ignore_errors=True)


def _entrada(config, huella, objetivo, ejecucion, dependencias=()):
    elemento, calculo = objetivo.split(".", 1)
    return EntradaElemento(
        ejecucion_id=ejecucion,
        elemento=elemento,
        calculo=calculo,
        parametros=_seccion_objetivo(config, objetivo),
        dependencias=list(dependencias),
        trazabilidad=TrazabilidadEntrada(configuracion_sha256=huella),
    )


def test_yaml_contiene_configuracion_para_todos_los_motores():
    config, _ = cargar_configuracion(CONFIG)
    for objetivo in DEPENDENCIAS:
        assert _seccion_objetivo(config, objetivo)


def test_override_json_tiene_prioridad_sobre_yaml(carpeta_contrato):
    objetivo = "zapata.diseno_longitudinal_e060"
    ruta_override = (
        carpeta_contrato
        / "entradas"
        / "zapata"
        / "diseno_longitudinal_e060.override.json"
    )
    ruta_override.parent.mkdir(parents=True)
    ruta_override.write_text(
        json.dumps({"recubrimiento_mm": 123.0}), encoding="utf-8"
    )

    resueltos, huella = _aplicar_override(
        carpeta_contrato,
        objetivo,
        {"elemento": {"recubrimiento_mm": 100.0, "phi_flexion": 0.9}},
    )

    assert resueltos["elemento"]["recubrimiento_mm"] == 123.0
    assert resueltos["elemento"]["phi_flexion"] == 0.9
    assert huella == sha256_archivo(ruta_override)


def test_override_cambia_huella_de_la_ejecucion(carpeta_contrato):
    inicial = _huella_overrides(carpeta_contrato)
    ruta = carpeta_contrato / "entradas" / "pantalla" / "diseno.override.json"
    ruta.parent.mkdir(parents=True)
    ruta.write_text('{"espesor_m": 0.45}', encoding="utf-8")

    assert _huella_overrides(carpeta_contrato) != inicial


def test_zapata_consume_resultado_sin_recalcular_estabilidad(
    carpeta_contrato, monkeypatch
):
    config, huella = cargar_configuracion(CONFIG)
    entrada_est = _entrada(config, huella, "estribo.estabilidad_global", "prueba")
    carpeta_est = carpeta_contrato / "estribo"
    ruta_entrada_est = carpeta_est / "entrada.json"
    escribir_json_atomico(ruta_entrada_est, entrada_est)
    resultado_est = ejecutar_entrada(
        "estribo.estabilidad_global", ruta_entrada_est, carpeta_est
    )
    assert resultado_est.archivos_generados
    assert all(
        (carpeta_est / ruta).is_file() for ruta in resultado_est.archivos_generados
    )
    ruta_resultado_est = carpeta_est / "resultado.json"

    from analisis_estabilidad.elementos.zapata import diseno_longitudinal_e060 as zapata

    def prohibido(*args, **kwargs):
        raise AssertionError("La zapata intentó recalcular la estabilidad")

    monkeypatch.setattr(zapata.SubstructureAnalysis, "run_full_analysis", prohibido)
    dep = DependenciaEntrada(
        elemento="estribo",
        calculo="estabilidad_global",
        resultado="../../estribo/resultado.json",
        sha256=sha256_archivo(ruta_resultado_est),
    )
    entrada_zapata = _entrada(
        config, huella, "zapata.diseno_longitudinal_e060", "prueba", (dep,)
    )
    carpeta_zapata = carpeta_contrato / "zapata" / "calculo"
    ruta_entrada_zapata = carpeta_zapata / "entrada.json"
    escribir_json_atomico(ruta_entrada_zapata, entrada_zapata)
    resultado = ejecutar_entrada(
        "zapata.diseno_longitudinal_e060", ruta_entrada_zapata, carpeta_zapata
    )
    assert resultado.dependencias_consumidas[0].elemento == "estribo"
    assert resultado.resultados["resultados_por_caso"]
    assert resultado.archivos_generados
    assert all(
        (carpeta_zapata / ruta).is_file() for ruta in resultado.archivos_generados
    )


def test_rechaza_dependencia_alterada(carpeta_contrato):
    config, huella = cargar_configuracion(CONFIG)
    falso = carpeta_contrato / "falso.json"
    falso.write_text("{}", encoding="utf-8")
    dep = DependenciaEntrada(
        elemento="estribo",
        calculo="estabilidad_global",
        resultado="falso.json",
        sha256="0" * 64,
    )
    entrada = _entrada(
        config, huella, "zapata.diseno_longitudinal_e060", "prueba", (dep,)
    )
    ruta = carpeta_contrato / "entrada.json"
    escribir_json_atomico(ruta, entrada)
    with pytest.raises(ValueError, match="Huella incorrecta"):
        ejecutar_entrada("zapata.diseno_longitudinal_e060", ruta, carpeta_contrato)


def test_rutas_externas_son_rechazadas():
    with pytest.raises(ValueError, match="debe permanecer dentro"):
        asegurar_interna(RAIZ_CASOS.parent.parent / "fuera.json")

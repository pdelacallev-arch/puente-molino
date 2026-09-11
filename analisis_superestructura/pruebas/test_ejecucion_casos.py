from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest

from analisis_superestructura.elementos.vigas_principales.configuracion import (
    validar_configuracion,
)
from analisis_superestructura.nucleo.contratos import leer_entrada, leer_resultado
from analisis_superestructura.nucleo.motores import OBJETIVOS
from analisis_superestructura.nucleo.orquestador import _estado, ejecutar_en_carpeta
from analisis_superestructura.nucleo.rutas import RAIZ_TEMPORAL, asegurar_interna


RAIZ = Path(__file__).parents[2]
EJEMPLO = RAIZ / "analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml"
HUELLA = "0" * 64


@pytest.fixture()
def ejecucion_temporal():
    ruta = asegurar_interna(RAIZ_TEMPORAL / "pytest_ejecucion" / uuid.uuid4().hex)
    ruta.mkdir(parents=True)
    yield ruta
    shutil.rmtree(ruta, ignore_errors=True)


def test_registro_declara_contrato_completo():
    for motor in OBJETIVOS.values():
        assert motor.elemento and motor.calculo
        assert callable(motor.calcular)
        assert callable(motor.serializar)
        assert callable(motor.artefactos)
        assert callable(motor.reporte)


def test_ejecucion_escribe_entrada_resultado_reporte_y_figuras(ejecucion_temporal):
    config = validar_configuracion(EJEMPLO)
    contrato, ruta_resultado = ejecutar_en_carpeta(
        "vigas_principales.analisis", config, HUELLA, ejecucion_temporal
    )
    carpeta = ejecucion_temporal / "elementos" / "vigas_principales" / "analisis"

    assert ruta_resultado == carpeta / "resultado.json"
    assert (carpeta / "entrada.json").is_file()
    assert (carpeta / "reporte.md").is_file()
    assert contrato.estado in ("OK", "ADVERTENCIA", "NO_CUMPLE")

    entrada = leer_entrada(carpeta / "entrada.json")
    assert entrada.elemento == "vigas_principales"
    assert entrada.calculo == "analisis"
    assert entrada.unidades == "SI"
    assert entrada.parametros["proyecto"]["id"] == "puente-molinohuayco"

    resultado = leer_resultado(ruta_resultado)
    assert resultado.entrada_sha256 == contrato.entrada_sha256
    assert "figuras/envolvente_fatiga.png" in resultado.archivos_generados
    assert "envolventes.csv" in resultado.archivos_generados
    assert all((carpeta / ruta).is_file() for ruta in resultado.archivos_generados)


def test_estado_traduce_estados_del_elemento():
    assert _estado({"estado": "NO_CUMPLE"}, "diseno") == "NO_CUMPLE"
    assert _estado({"estado": "CONDICIONAL"}, "diseno") == "ADVERTENCIA"
    assert _estado({"estado": "CUMPLE"}, "diseno") == "OK"
    assert _estado({"advertencias": ["x"]}, "analisis") == "ADVERTENCIA"
    assert _estado({"factibles": [1]}, "busqueda") == "OK"
    assert _estado({"factibles": []}, "busqueda") == "NO_CUMPLE"

from pathlib import Path

import pytest

from analisis_estabilidad.nucleo.configuracion import ErrorConfiguracion, cargar_configuracion
from analisis_estabilidad.nucleo.orquestador import _aplicar_override, _seccion_objetivo


CASO = Path(__file__).parents[1] / "casos" / "molinohuayco" / "estribo_derecho" / "entrada.yaml"


def test_configuracion_del_estribo_derecho_es_coherente():
    config, _ = cargar_configuracion(CASO)

    geometria = config.elementos.estribo["geometria"]
    assert geometria["H"] == pytest.approx(geometria["hz"] + geometria["hp"])


def test_rechaza_altura_global_incompatible_con_corona(tmp_path):
    texto = CASO.read_text(encoding="utf-8").replace("H: 14.65", "H: 14.64", 1)
    ruta = tmp_path / "entrada_incompatible.yaml"
    ruta.write_text(texto, encoding="utf-8")

    with pytest.raises(ErrorConfiguracion, match="geometria.H"):
        cargar_configuracion(ruta)


def test_override_de_estribo_con_altura_incompatible_es_rechazado(tmp_path):
    config, _ = cargar_configuracion(CASO)
    ruta = tmp_path / "entradas" / "estribo" / "estabilidad_global.override.json"
    ruta.parent.mkdir(parents=True)
    ruta.write_text('{"geometria": {"H": 14.64}}', encoding="utf-8")

    parametros, huella = _aplicar_override(
        tmp_path,
        "estribo.estabilidad_global",
        _seccion_objetivo(config, "estribo.estabilidad_global"),
    )
    datos = config.model_dump(mode="python")
    datos["elementos"]["estribo"] = parametros

    assert huella is not None
    with pytest.raises(ErrorConfiguracion, match="geometria.H"):
        cargar_configuracion_equivalente(datos)


def cargar_configuracion_equivalente(datos):
    """Valida un caso resuelto sin convertirlo en un archivo de producción."""
    from analisis_estabilidad.nucleo.configuracion import (
        ConfiguracionCaso,
        validar_coherencia_geometrica,
    )

    config = ConfiguracionCaso.model_validate(datos)
    validar_coherencia_geometrica(config)
    return config

from __future__ import annotations

import pytest

from analisis_superestructura.nucleo.motores import OBJETIVOS, VALIDADORES
from analisis_superestructura.nucleo.orquestador import validar_caso
from analisis_superestructura.nucleo.rutas import carpeta_caso


def test_registro_expone_elemento_y_calculos_de_vigas():
    assert "vigas_principales" in VALIDADORES
    assert {
        "vigas_principales.analisis",
        "vigas_principales.parrilla",
        "vigas_principales.diseno",
        "vigas_principales.busqueda",
    } <= OBJETIVOS.keys()


def test_caso_bartra_se_resuelve_desde_el_nucleo():
    config = validar_caso("vigas_principales", "bartra", "R00")
    assert config.proyecto.id == "bartra-mtc2018"


def test_rutas_de_casos_no_admiten_escape():
    with pytest.raises(ValueError, match="fuera de analisis_superestructura"):
        carpeta_caso("..", "..")


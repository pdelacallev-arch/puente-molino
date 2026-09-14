from pathlib import Path

from analisis_estabilidad.elementos.cajuela.diagrama_cargas import (
    _mapa_casos,
    auditar_equilibrio,
    dibujar_caso,
)
from analisis_estabilidad.elementos.cajuela.verificacion_voladizo import (
    Parametros,
    coeficientes,
    construir_casos,
)


def test_todos_los_casos_cierran_equilibrio():
    p = Parametros()
    for caso in construir_casos(p, coeficientes(p)):
        assert auditar_equilibrio(caso, p).cumple


def test_mapa_contiene_cinco_combinaciones_de_calculo():
    p = Parametros()
    casos = _mapa_casos(construir_casos(p, coeficientes(p)))
    assert set(casos) == {
        "servicio-i",
        "resistencia-i-a",
        "resistencia-i-b",
        "evento-extremo-i-a",
        "evento-extremo-i-b",
    }


def test_genera_png(tmp_path: Path):
    p = Parametros()
    caso = construir_casos(p, coeficientes(p))[0]
    salida = tmp_path / "servicio.png"
    dibujar_caso(caso, p, salida, dpi=80)
    assert salida.exists()
    assert salida.stat().st_size > 10_000

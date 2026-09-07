import numpy as np
import pytest

from analisis_estabilidad.elementos.contrafuertes.analisis_2d import (
    ParametrosContrafuerte,
    ReaccionesNodales,
    ensamblar_rigidez,
    generar_malla,
    resultantes_por_corte,
    rigidez_elemento,
    vector_carga,
)


@pytest.fixture
def modelo_sintetico():
    p = ParametrosContrafuerte(divisiones_horizontales=4)
    niveles = np.linspace(0.0, p.altura_m, 6)
    malla = generar_malla(p, niveles)
    cargas = ReaccionesNodales(
        contrafuerte="CF-C2",
        caso="Prueba",
        z_m=niveles[1:],
        reaccion_pantalla_kn=np.array([10.0, 20.0, 30.0, 40.0, 50.0]),
    )
    return p, malla, cargas


def test_geometria_trapezoidal_conserva_base_y_corona(modelo_sintetico):
    p, malla, _ = modelo_sintetico
    assert p.longitud(0.0) == pytest.approx(6.10)
    assert p.longitud(p.altura_m) == pytest.approx(p.longitud_corona_m)
    assert malla.nodos[malla.nodos_base, 0].max() == pytest.approx(6.10)
    assert malla.nodos[-1, 0] == pytest.approx(p.longitud_corona_m)


def test_rigidez_q4_es_simetrica_y_semidefinida(modelo_sintetico):
    p, malla, _ = modelo_sintetico
    ke = rigidez_elemento(malla.nodos[malla.elementos[0]], p, 25.0e6)
    assert np.max(np.abs(ke-ke.T)) < 1e-7
    valores = np.linalg.eigvalsh(ke)
    assert valores.min() > -1e-6
    assert np.count_nonzero(np.abs(valores) < 1e-6) >= 3


def test_vector_aplica_accion_opuesta_y_conserva_momento(modelo_sintetico):
    _, malla, cargas = modelo_sintetico
    f = vector_carga(malla, cargas)
    fuerzas = f.reshape((-1, 2))
    assert fuerzas[:, 0].sum() == pytest.approx(-150.0)
    momento = np.sum(
        malla.nodos[:, 0]*fuerzas[:, 1]-malla.nodos[:, 1]*fuerzas[:, 0]
    )
    assert momento == pytest.approx(np.dot(cargas.reaccion_pantalla_kn, cargas.z_m))


def test_resultantes_por_corte_cierran_base(modelo_sintetico):
    _, malla, cargas = modelo_sintetico
    cortes = resultantes_por_corte(cargas, malla.niveles_m)
    assert cortes[0]["V_abs_kN"] == pytest.approx(cargas.resultante_abs_kn)
    assert cortes[0]["M_abs_kN_m"] == pytest.approx(cargas.momento_base_abs_kn_m)
    assert cortes[-1]["V_abs_kN"] == pytest.approx(0.0)
    assert cortes[-1]["M_abs_kN_m"] == pytest.approx(0.0)


def test_modelo_global_restringido_es_definido_positivo(modelo_sintetico):
    p, malla, _ = modelo_sintetico
    k = ensamblar_rigidez(malla, p, 25.0e6).toarray()
    restringidos = np.array([2*int(n)+d for n in malla.nodos_base for d in range(2)])
    libres = np.setdiff1d(np.arange(k.shape[0]), restringidos)
    valores = np.linalg.eigvalsh(k[np.ix_(libres, libres)])
    assert valores.min() > 0.0

"""Líneas de influencia y barrido interno de HL-93 para una viga simple."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from ..modelos import Configuracion


@dataclass(frozen=True)
class ResultadoMovil:
    x_mm: np.ndarray
    momento_nmm: np.ndarray
    corte_positivo_n: np.ndarray
    corte_negativo_n: np.ndarray
    fatiga_rango_momento_nmm: np.ndarray
    vehiculo_control_momento: tuple[str, ...]
    posicion_critica_centro_mm: float
    separacion_critica_centro_mm: float
    equilibrio_relativo: float

    def resumen(self) -> dict:
        data = asdict(self)
        for clave in (
            "x_mm",
            "momento_nmm",
            "corte_positivo_n",
            "corte_negativo_n",
            "fatiga_rango_momento_nmm",
        ):
            data[clave] = data[clave].tolist()
        return data


def influencia_momento(L: float, x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Ordenada M/N en cada sección x para cargas ubicadas en z; unidades mm."""
    xx = x[:, None]
    zz = z[None, :]
    return np.where(zz <= xx, zz * (L - xx) / L, xx * (L - zz) / L)


def influencia_corte(L: float, x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Ordenada de corte en la cara izquierda de la sección."""
    xx = x[:, None]
    zz = z[None, :]
    return np.where(zz <= xx, -zz / L, (L - zz) / L)


def _respuesta_puntual(
    L: float, x: np.ndarray, posiciones: np.ndarray, cargas: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    mascara = (posiciones >= 0.0) & (posiciones <= L)
    z = posiciones[mascara]
    p = cargas[mascara]
    if not len(z):
        return np.zeros_like(x), np.zeros_like(x), 0.0
    m = influencia_momento(L, x, z) @ p
    v = influencia_corte(L, x, z) @ p
    r1 = float(np.sum(p * (L - z) / L))
    r2 = float(np.sum(p * z / L))
    error = abs((r1 + r2) - float(np.sum(p))) / max(float(np.sum(p)), 1.0)
    return m, v, error


def _vehiculos(config: Configuracion, fatiga: bool = False):
    trafico = config.trafico
    camion = trafico.camion
    im = 1.0 + (trafico.incremento_dinamico_fatiga if fatiga else trafico.incremento_dinamico)
    p_frontal = camion.eje_frontal * 1000.0 * im
    p_posterior = camion.eje_posterior * 1000.0 * im
    separaciones = np.arange(
        camion.separacion_posterior_min,
        camion.separacion_posterior_max + config.analisis.paso_separacion_ejes / 2.0,
        config.analisis.paso_separacion_ejes,
    )
    if fatiga:
        separaciones = np.array([camion.separacion_posterior_min])
    for sep in separaciones * 1000.0:
        offsets = np.array([0.0, camion.separacion_frontal * 1000.0, camion.separacion_frontal * 1000.0 + sep])
        cargas = np.array([p_frontal, p_posterior, p_posterior])
        yield "camion", sep, offsets, cargas
        yield "camion_invertido", sep, offsets, cargas[::-1]
    if not fatiga:
        offsets = np.array([0.0, trafico.separacion_tandem * 1000.0])
        cargas = np.array([trafico.tandem_eje, trafico.tandem_eje]) * 1000.0 * im
        yield "tandem", trafico.separacion_tandem * 1000.0, offsets, cargas


def analizar_hl93(config: Configuracion) -> ResultadoMovil:
    L = config.geometria.luz * 1000.0
    n = config.analisis.numero_estaciones
    x = np.linspace(0.0, L, n)
    paso = config.analisis.paso_vehiculo * 1000.0
    q = config.trafico.carga_carril  # kN/m == N/mm
    m_carril = q * x * (L - x) / 2.0
    # Para corte, la carga de carril se aplica solo sobre la zona del mismo
    # signo de la línea de influencia (MTC 2.4.3.2.3).
    v_carril_positivo = q * (L - x) ** 2 / (2.0 * L)
    v_carril_negativo = -q * x**2 / (2.0 * L)
    max_m = np.full(n, -np.inf)
    max_v = np.full(n, -np.inf)
    min_v = np.full(n, np.inf)
    control = np.full(n, "", dtype=object)
    centro = n // 2
    posicion_centro = 0.0
    separacion_centro = 0.0
    error_max = 0.0
    for nombre, sep, offsets, cargas in _vehiculos(config):
        frente_min = -float(np.max(offsets))
        for frente in np.arange(frente_min, L + paso / 2.0, paso):
            m, v, error = _respuesta_puntual(L, x, frente + offsets, cargas)
            m += m_carril
            mejora = m > max_m
            max_m[mejora] = m[mejora]
            control[mejora] = nombre
            if mejora[centro]:
                posicion_centro = frente
                separacion_centro = sep
            max_v = np.maximum(max_v, v + v_carril_positivo)
            min_v = np.minimum(min_v, v + v_carril_negativo)
            error_max = max(error_max, error)
    # Fatiga: rango de momento del camión único, sin carga de carril.
    max_f = np.full(n, -np.inf)
    min_f = np.full(n, np.inf)
    for _, _, offsets, cargas in _vehiculos(config, fatiga=True):
        frente_min = -float(np.max(offsets))
        for frente in np.arange(frente_min, L + paso / 2.0, paso):
            m, _, error = _respuesta_puntual(L, x, frente + offsets, cargas)
            max_f = np.maximum(max_f, m)
            min_f = np.minimum(min_f, m)
            error_max = max(error_max, error)
    rango_f = np.maximum(0.0, max_f - np.minimum(min_f, 0.0))
    return ResultadoMovil(
        x_mm=x,
        momento_nmm=max_m,
        corte_positivo_n=max_v,
        corte_negativo_n=min_v,
        fatiga_rango_momento_nmm=rango_f,
        vehiculo_control_momento=tuple(str(v) for v in control),
        posicion_critica_centro_mm=posicion_centro,
        separacion_critica_centro_mm=separacion_centro,
        equilibrio_relativo=error_max,
    )


def respuesta_vehiculo_critico_centro(
    config: Configuracion,
    x: np.ndarray,
    posicion_frente: float,
    separacion: float,
    vehiculo: str = "camion",
) -> tuple[np.ndarray, np.ndarray]:
    im = 1.0 + config.trafico.incremento_dinamico
    if vehiculo == "tandem":
        offsets = np.array([0.0, config.trafico.separacion_tandem * 1000.0])
        cargas = np.array([config.trafico.tandem_eje, config.trafico.tandem_eje]) * 1000.0 * im
    else:
        camion = config.trafico.camion
        offsets = np.array(
            [0.0, camion.separacion_frontal * 1000.0, camion.separacion_frontal * 1000.0 + separacion]
        )
        cargas = np.array([camion.eje_frontal, camion.eje_posterior, camion.eje_posterior]) * 1000.0 * im
        if vehiculo == "camion_invertido":
            cargas = cargas[::-1]
    m, v, _ = _respuesta_puntual(config.geometria.luz * 1000.0, x, posicion_frente + offsets, cargas)
    L = config.geometria.luz * 1000.0
    q = config.trafico.carga_carril
    return m + q * x * (L - x) / 2.0, v + q * (L / 2.0 - x)

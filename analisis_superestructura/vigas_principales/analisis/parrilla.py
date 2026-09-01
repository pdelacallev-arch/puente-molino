"""Parrilla espacial para distribución transversal de carga viva.

La formulación usa tres grados de libertad por nodo: desplazamiento vertical
``w`` y giros ``theta_x`` y ``theta_y``. Las vigas longitudinales emplean la
rigidez compuesta de corto plazo; las barras transversales representan franjas
de losa. El solver trabaja internamente en N, mm y MPa.

El objetivo del modelo es obtener factores de distribución globales de vigas,
no esfuerzos locales de la losa ni fuerzas de diseño de diafragmas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from ..modelos import Configuracion, SegmentoViga
from .distribucion import FactoresDistribucion
from .secciones import modulo_elasticidad_concreto, propiedades_por_segmento


@dataclass(frozen=True)
class CasoLongitudinal:
    nombre: str
    posicion_frente_mm: float
    offsets_mm: np.ndarray
    cargas_eje_n: np.ndarray
    carga_carril_n_mm: float
    respuesta_referencia: float

    def a_dict(self) -> dict:
        datos = asdict(self)
        datos["offsets_mm"] = self.offsets_mm.tolist()
        datos["cargas_eje_n"] = self.cargas_eje_n.tolist()
        return datos


@dataclass(frozen=True)
class ResultadoParrilla:
    factores: FactoresDistribucion
    x_nodos_mm: np.ndarray
    y_nodos_mm: np.ndarray
    y_vigas_mm: np.ndarray
    centros_carril_mm: np.ndarray
    participacion_momento: np.ndarray
    participacion_corte: np.ndarray
    participacion_fatiga: np.ndarray
    casos_criticos: dict[str, CasoLongitudinal]
    error_equilibrio_maximo: float
    numero_grados_libertad: int
    advertencias: tuple[str, ...]

    def resumen(self) -> dict:
        return {
            "factores": self.factores.a_dict(),
            "x_nodos_mm": self.x_nodos_mm.tolist(),
            "y_nodos_mm": self.y_nodos_mm.tolist(),
            "y_vigas_mm": self.y_vigas_mm.tolist(),
            "centros_carril_mm": self.centros_carril_mm.tolist(),
            "participacion_momento": self.participacion_momento.tolist(),
            "participacion_corte": self.participacion_corte.tolist(),
            "participacion_fatiga": self.participacion_fatiga.tolist(),
            "casos_criticos": {k: v.a_dict() for k, v in self.casos_criticos.items()},
            "error_equilibrio_maximo": self.error_equilibrio_maximo,
            "numero_grados_libertad": self.numero_grados_libertad,
            "advertencias": list(self.advertencias),
        }


@dataclass(frozen=True)
class _Elemento:
    nodo_i: int
    nodo_j: int
    direccion: str
    longitud_mm: float
    rigidez: np.ndarray
    indice_viga: int | None = None


@dataclass(frozen=True)
class _ModeloParrilla:
    x_mm: np.ndarray
    y_mm: np.ndarray
    y_vigas_mm: np.ndarray
    nodos: dict[tuple[int, int], int]
    elementos: tuple[_Elemento, ...]
    rigidez: np.ndarray
    libres: np.ndarray
    restringidos: np.ndarray
    apoyos_por_viga: tuple[int, ...]
    elementos_longitudinales: dict[int, tuple[_Elemento, ...]]


def _rigidez_elemento(longitud: float, ei: float, gj: float, direccion: str) -> np.ndarray:
    if longitud <= 0.0 or ei <= 0.0 or gj <= 0.0:
        raise ValueError("longitud, EI y GJ deben ser positivos")
    l = longitud
    kb = ei / l**3 * np.array(
        [
            [12.0, 6.0 * l, -12.0, 6.0 * l],
            [6.0 * l, 4.0 * l**2, -6.0 * l, 2.0 * l**2],
            [-12.0, -6.0 * l, 12.0, -6.0 * l],
            [6.0 * l, 2.0 * l**2, -6.0 * l, 4.0 * l**2],
        ]
    )
    kt = gj / l * np.array([[1.0, -1.0], [-1.0, 1.0]])
    k = np.zeros((6, 6))
    if direccion == "x":
        flexion = (0, 2, 3, 5)  # w, theta_y
        torsion = (1, 4)  # theta_x
    elif direccion == "y":
        flexion = (0, 1, 3, 4)  # w, theta_x
        torsion = (2, 5)  # theta_y
    else:
        raise ValueError("direccion debe ser 'x' o 'y'")
    k[np.ix_(flexion, flexion)] = kb
    k[np.ix_(torsion, torsion)] = kt
    return k


def _grados_elemento(elemento: _Elemento) -> np.ndarray:
    return np.array(
        [
            3 * elemento.nodo_i,
            3 * elemento.nodo_i + 1,
            3 * elemento.nodo_i + 2,
            3 * elemento.nodo_j,
            3 * elemento.nodo_j + 1,
            3 * elemento.nodo_j + 2,
        ],
        dtype=int,
    )


def _segmento_en(config: Configuracion, x_m: float) -> tuple[int, SegmentoViga]:
    for indice, segmento in enumerate(config.viga.segmentos):
        if segmento.x_inicio - 1e-9 <= x_m <= segmento.x_fin + 1e-9:
            return indice, segmento
    raise ValueError(f"no existe segmento de viga en x={x_m:.6f} m")


def _constante_torsion_i(segmento: SegmentoViga) -> float:
    """Constante de Saint-Venant de una I abierta de placas, en mm4."""
    return (
        segmento.ancho_ala_superior * segmento.espesor_ala_superior**3
        + segmento.ancho_ala_inferior * segmento.espesor_ala_inferior**3
        + segmento.altura_alma * segmento.espesor_alma**3
    ) / 3.0


def _ejes_transversales(config: Configuracion) -> tuple[np.ndarray, np.ndarray]:
    g = config.geometria
    y_vigas = (
        np.arange(g.numero_vigas, dtype=float) - (g.numero_vigas - 1.0) / 2.0
    ) * g.separacion_vigas * 1000.0
    borde = g.ancho_tablero * 500.0
    if y_vigas[0] < -borde - 1e-6 or y_vigas[-1] > borde + 1e-6:
        raise ValueError("los ejes de vigas quedan fuera del ancho del tablero")
    y = np.unique(np.concatenate(([-borde], y_vigas, [borde])))
    return y, y_vigas


def _malla_longitudinal(config: Configuracion) -> np.ndarray:
    p = config.analisis.parrilla
    base = np.linspace(0.0, config.geometria.luz * 1000.0, p.numero_tramos_longitudinales + 1)
    obligatorios = [config.geometria.luz * 500.0]
    obligatorios.extend(v * 1000.0 for v in config.arriostramiento.posiciones)
    obligatorios.extend(s.x_inicio * 1000.0 for s in config.viga.segmentos)
    obligatorios.extend(s.x_fin * 1000.0 for s in config.viga.segmentos)
    return np.unique(np.concatenate((base, np.asarray(obligatorios))))


def _anchos_tributarios(x: np.ndarray) -> np.ndarray:
    anchos = np.empty_like(x)
    anchos[0] = (x[1] - x[0]) / 2.0
    anchos[-1] = (x[-1] - x[-2]) / 2.0
    anchos[1:-1] = (x[2:] - x[:-2]) / 2.0
    return anchos


def construir_modelo_parrilla(config: Configuracion) -> _ModeloParrilla:
    x = _malla_longitudinal(config)
    y, y_vigas = _ejes_transversales(config)
    nodos = {(ix, iy): ix * len(y) + iy for ix in range(len(x)) for iy in range(len(y))}
    ndof = 3 * len(nodos)
    k_global = np.zeros((ndof, ndof))
    elementos: list[_Elemento] = []
    longitudinales: dict[int, list[_Elemento]] = {i: [] for i in range(len(y_vigas))}

    es = config.materiales.acero_estructural.es
    ec = config.materiales.concreto.ec or modulo_elasticidad_concreto(
        config.materiales.concreto.fc, config.materiales.concreto.peso_unitario
    )
    ps = config.analisis.parrilla
    gs = es / (2.0 * (1.0 + ps.coeficiente_poisson_acero))
    gc = ec / (2.0 * (1.0 + ps.coeficiente_poisson_concreto))
    t = config.losa.espesor * 1000.0
    propiedades_i = propiedades_por_segmento(config, "interior")
    propiedades_e = propiedades_por_segmento(config, "exterior")

    indices_y_viga = [int(np.argmin(np.abs(y - yv))) for yv in y_vigas]
    for ig, iy in enumerate(indices_y_viga):
        tipo = "exterior" if ig in (0, len(y_vigas) - 1) else "interior"
        propiedades = propiedades_e if tipo == "exterior" else propiedades_i
        for ix in range(len(x) - 1):
            xm = (x[ix] + x[ix + 1]) / 2000.0
            iseg, segmento = _segmento_en(config, xm)
            compuesto = propiedades[iseg]["corto_plazo"]
            be = compuesto.ancho_efectivo
            j_losa = be * t**3 / 3.0
            gj = ps.factor_rigidez_torsional * (
                gs * _constante_torsion_i(segmento) + gc * j_losa
            )
            elemento = _Elemento(
                nodo_i=nodos[(ix, iy)],
                nodo_j=nodos[(ix + 1, iy)],
                direccion="x",
                longitud_mm=x[ix + 1] - x[ix],
                rigidez=_rigidez_elemento(
                    x[ix + 1] - x[ix], es * compuesto.inercia_x, gj, "x"
                ),
                indice_viga=ig,
            )
            elementos.append(elemento)
            longitudinales[ig].append(elemento)

    bx = _anchos_tributarios(x)
    for ix in range(len(x)):
        ei_t = (
            ps.factor_rigidez_flexion_transversal * ec * bx[ix] * t**3 / 12.0
        )
        gj_t = ps.factor_rigidez_torsional * gc * bx[ix] * t**3 / 3.0
        for iy in range(len(y) - 1):
            elemento = _Elemento(
                nodo_i=nodos[(ix, iy)],
                nodo_j=nodos[(ix, iy + 1)],
                direccion="y",
                longitud_mm=y[iy + 1] - y[iy],
                rigidez=_rigidez_elemento(y[iy + 1] - y[iy], ei_t, gj_t, "y"),
            )
            elementos.append(elemento)

    for elemento in elementos:
        grados = _grados_elemento(elemento)
        k_global[np.ix_(grados, grados)] += elemento.rigidez

    restringidos: list[int] = []
    apoyos: list[int] = []
    for ig, iy in enumerate(indices_y_viga):
        nodo_izq = nodos[(0, iy)]
        nodo_der = nodos[(len(x) - 1, iy)]
        restringidos.extend((3 * nodo_izq, 3 * nodo_der))
        apoyos.append(3 * nodo_izq)
    restringidos_array = np.array(sorted(set(restringidos)), dtype=int)
    libres = np.setdiff1d(np.arange(ndof), restringidos_array)
    return _ModeloParrilla(
        x_mm=x,
        y_mm=y,
        y_vigas_mm=y_vigas,
        nodos=nodos,
        elementos=tuple(elementos),
        rigidez=k_global,
        libres=libres,
        restringidos=restringidos_array,
        apoyos_por_viga=tuple(apoyos),
        elementos_longitudinales={k: tuple(v) for k, v in longitudinales.items()},
    )


def _agregar_carga_transversal(
    modelo: _ModeloParrilla, vector: np.ndarray, indice_x: int, y_carga: float, carga_n: float
) -> None:
    y = modelo.y_mm
    yc = float(np.clip(y_carga, y[0], y[-1]))
    coincidencia = np.flatnonzero(np.isclose(y, yc, atol=1e-8))
    if len(coincidencia):
        nodo = modelo.nodos[(indice_x, int(coincidencia[0]))]
        vector[3 * nodo] += carga_n
        return
    iy = int(np.searchsorted(y, yc) - 1)
    longitud = y[iy + 1] - y[iy]
    xi = (yc - y[iy]) / longitud
    n1 = 1.0 - 3.0 * xi**2 + 2.0 * xi**3
    n2 = longitud * (xi - 2.0 * xi**2 + xi**3)
    n3 = 3.0 * xi**2 - 2.0 * xi**3
    n4 = longitud * (-xi**2 + xi**3)
    ni = modelo.nodos[(indice_x, iy)]
    nj = modelo.nodos[(indice_x, iy + 1)]
    vector[[3 * ni, 3 * ni + 1, 3 * nj, 3 * nj + 1]] += carga_n * np.array(
        [n1, n2, n3, n4]
    )


def _agregar_carga_puntual(
    modelo: _ModeloParrilla, vector: np.ndarray, x_carga: float, y_carga: float, carga_n: float
) -> None:
    x = modelo.x_mm
    xc = float(np.clip(x_carga, x[0], x[-1]))
    coincidencia = np.flatnonzero(np.isclose(x, xc, atol=1e-8))
    if len(coincidencia):
        _agregar_carga_transversal(modelo, vector, int(coincidencia[0]), y_carga, carga_n)
        return
    ix = int(np.searchsorted(x, xc) - 1)
    peso_der = (xc - x[ix]) / (x[ix + 1] - x[ix])
    _agregar_carga_transversal(modelo, vector, ix, y_carga, carga_n * (1.0 - peso_der))
    _agregar_carga_transversal(modelo, vector, ix + 1, y_carga, carga_n * peso_der)


def _centros_carril(config: Configuracion) -> np.ndarray:
    p = config.analisis.parrilla
    limite = config.geometria.ancho_calzada / 2.0 - p.ancho_carril_diseno / 2.0
    if limite < -1e-9:
        raise ValueError("el ancho del carril de diseño supera el ancho de calzada")
    if limite <= 1e-9:
        return np.array([0.0])
    paso = p.paso_posicion_transversal
    centros = np.arange(-limite, limite + paso / 2.0, paso)
    return np.unique(np.round(np.concatenate((centros, [-limite, 0.0, limite])), 9)) * 1000.0


def _vehiculos(config: Configuracion, fatiga: bool = False):
    t = config.trafico
    c = t.camion
    im = 1.0 + (t.incremento_dinamico_fatiga if fatiga else t.incremento_dinamico)
    separaciones = [c.separacion_posterior_min]
    if not fatiga:
        separaciones = np.arange(
            c.separacion_posterior_min,
            c.separacion_posterior_max + config.analisis.paso_separacion_ejes / 2.0,
            config.analisis.paso_separacion_ejes,
        )
    for separacion in separaciones:
        offsets = np.array([0.0, c.separacion_frontal, c.separacion_frontal + separacion]) * 1000.0
        cargas = np.array([c.eje_frontal, c.eje_posterior, c.eje_posterior]) * 1000.0 * im
        yield "camion", offsets, cargas
        yield "camion_invertido", offsets, cargas[::-1]
    if not fatiga:
        offsets = np.array([0.0, t.separacion_tandem]) * 1000.0
        cargas = np.array([t.tandem_eje, t.tandem_eje]) * 1000.0 * im
        yield "tandem", offsets, cargas


def _caso_critico(config: Configuracion, efecto: str) -> CasoLongitudinal:
    l = config.geometria.luz * 1000.0
    x_eval = l / 2.0
    p = config.analisis.parrilla
    q = 0.0 if efecto == "fatiga" else config.trafico.carga_carril
    base_carril = q * l**2 / 8.0 if efecto != "corte" else q * l / 2.0
    mejor: tuple[float, str, float, np.ndarray, np.ndarray] | None = None
    for nombre, offsets, cargas in _vehiculos(config, fatiga=efecto == "fatiga"):
        frente_min = -float(np.max(offsets))
        posiciones = np.arange(
            frente_min,
            l + p.paso_busqueda_longitudinal * 500.0,
            p.paso_busqueda_longitudinal * 1000.0,
        )
        for frente in posiciones:
            z = frente + offsets
            mascara = (z >= 0.0) & (z <= l)
            if efecto == "corte":
                respuesta = float(np.sum(cargas[mascara] * (l - z[mascara]) / l)) + base_carril
            else:
                zz = z[mascara]
                ordenadas = np.where(
                    zz <= x_eval,
                    zz * (l - x_eval) / l,
                    x_eval * (l - zz) / l,
                )
                respuesta = float(np.sum(cargas[mascara] * ordenadas)) + base_carril
            if mejor is None or respuesta > mejor[0]:
                mejor = (respuesta, nombre, frente, offsets.copy(), cargas.copy())
    if mejor is None:
        raise RuntimeError("no se encontró un caso longitudinal crítico")
    return CasoLongitudinal(
        nombre=mejor[1],
        posicion_frente_mm=mejor[2],
        offsets_mm=mejor[3],
        cargas_eje_n=mejor[4],
        carga_carril_n_mm=q,
        respuesta_referencia=mejor[0],
    )


def _vector_carga(
    config: Configuracion,
    modelo: _ModeloParrilla,
    caso: CasoLongitudinal,
    centro_carril_mm: float,
) -> np.ndarray:
    vector = np.zeros(modelo.rigidez.shape[0])
    p = config.analisis.parrilla
    mitad_ruedas = p.separacion_lineas_rueda * 500.0
    for x_eje, carga_eje in zip(
        caso.posicion_frente_mm + caso.offsets_mm, caso.cargas_eje_n
    ):
        if 0.0 <= x_eje <= config.geometria.luz * 1000.0:
            _agregar_carga_puntual(
                modelo, vector, x_eje, centro_carril_mm - mitad_ruedas, carga_eje / 2.0
            )
            _agregar_carga_puntual(
                modelo, vector, x_eje, centro_carril_mm + mitad_ruedas, carga_eje / 2.0
            )
    if caso.carga_carril_n_mm > 0.0:
        anchos_x = _anchos_tributarios(modelo.x_mm)
        n = p.puntos_integracion_carga_carril
        if n == 1:
            posiciones_y = np.array([centro_carril_mm])
        else:
            ancho = p.ancho_carril_diseno * 1000.0
            posiciones_y = np.linspace(
                centro_carril_mm - ancho / 2.0,
                centro_carril_mm + ancho / 2.0,
                n,
            )
        for ix, ancho_x in enumerate(anchos_x):
            carga_punto = caso.carga_carril_n_mm * ancho_x / len(posiciones_y)
            for yp in posiciones_y:
                _agregar_carga_transversal(modelo, vector, ix, yp, carga_punto)
    return vector


def _resolver(modelo: _ModeloParrilla, cargas: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if cargas.ndim == 1:
        cargas = cargas[:, None]
    desplazamientos = np.zeros_like(cargas)
    kff = modelo.rigidez[np.ix_(modelo.libres, modelo.libres)]
    desplazamientos[modelo.libres] = np.linalg.solve(kff, cargas[modelo.libres])
    residuos = modelo.rigidez @ desplazamientos - cargas
    return desplazamientos, residuos


def _momento_en_centro(
    modelo: _ModeloParrilla, desplazamientos: np.ndarray, indice_viga: int
) -> np.ndarray:
    centro = modelo.x_mm[-1] / 2.0
    # El centro se incluyó obligatoriamente en la malla. Se promedian las
    # magnitudes de los momentos de extremo de los elementos adyacentes.
    valores: list[np.ndarray] = []
    for ix, elemento in enumerate(modelo.elementos_longitudinales[indice_viga]):
        xi = modelo.x_mm[ix]
        xj = modelo.x_mm[ix + 1]
        if abs(xj - centro) < 1e-8 or abs(xi - centro) < 1e-8:
            grados = _grados_elemento(elemento)
            fuerzas = elemento.rigidez @ desplazamientos[grados]
            valores.append(np.abs(fuerzas[5] if abs(xj - centro) < 1e-8 else fuerzas[2]))
    if not valores:
        raise RuntimeError("el centro de luz no coincide con un nodo de la parrilla")
    return np.mean(np.vstack(valores), axis=0)


def _participaciones(
    config: Configuracion,
    modelo: _ModeloParrilla,
    caso: CasoLongitudinal,
    centros: np.ndarray,
    efecto: str,
) -> tuple[np.ndarray, float]:
    matrices = np.column_stack(
        [_vector_carga(config, modelo, caso, centro) for centro in centros]
    )
    u, residuos = _resolver(modelo, matrices)
    if efecto == "corte":
        respuesta = np.vstack(
            [-residuos[dof, :] for dof in modelo.apoyos_por_viga]
        ).T
    else:
        respuesta = np.vstack(
            [_momento_en_centro(modelo, u, ig) for ig in range(len(modelo.y_vigas_mm))]
        ).T
    participacion = respuesta / caso.respuesta_referencia
    cargas_totales = np.sum(matrices[0::3, :], axis=0)
    reacciones = -np.sum(residuos[modelo.restringidos, :], axis=0)
    error = float(
        np.max(np.abs(reacciones - cargas_totales) / np.maximum(np.abs(cargas_totales), 1.0))
    )
    return participacion, error


def analizar_parrilla(config: Configuracion) -> ResultadoParrilla:
    """Calcula factores de momento, corte y fatiga mediante la parrilla."""
    modelo = construir_modelo_parrilla(config)
    centros = _centros_carril(config)
    casos = {
        "momento": _caso_critico(config, "momento"),
        "corte": _caso_critico(config, "corte"),
        "fatiga": _caso_critico(config, "fatiga"),
    }
    pm, em = _participaciones(config, modelo, casos["momento"], centros, "momento")
    pv, ev = _participaciones(config, modelo, casos["corte"], centros, "corte")
    pf, ef = _participaciones(config, modelo, casos["fatiga"], centros, "fatiga")

    n_vigas = config.geometria.numero_vigas
    exteriores = [0, n_vigas - 1]
    interiores = list(range(1, n_vigas - 1)) or exteriores
    m = config.analisis.parrilla.factor_presencia_multiple
    valores = {
        "momento_interior": m * float(np.max(pm[:, interiores])),
        "momento_exterior": m * float(np.max(pm[:, exteriores])),
        "corte_interior": m * float(np.max(pv[:, interiores])),
        "corte_exterior": m * float(np.max(pv[:, exteriores])),
        "fatiga_interior": float(np.max(pf[:, interiores])),
        "fatiga_exterior": float(np.max(pf[:, exteriores])),
    }
    advertencias = [
        "Factores obtenidos con parrilla elástica lineal; no representan esfuerzos locales de losa.",
        "La rigidez compuesta supone interacción total y debe conciliarse con los conectores de corte.",
        "Los diafragmas se representan solo mediante la continuidad transversal de la losa; incorporar su rigidez explícita si se confirma su geometría.",
    ]
    ancho_simetrico = (
        (config.geometria.numero_vigas - 1) * config.geometria.separacion_vigas
        + 2.0 * config.geometria.voladizo_exterior
    )
    if abs(ancho_simetrico - config.geometria.ancho_tablero) > 1e-6:
        advertencias.append(
            "La malla centra vigas y tablero, pero ancho_tablero no coincide con la separación de vigas más dos voladizos; revisar la geometría transversal."
        )
    if config.geometria.numero_carriles > 1:
        advertencias.append(
            "La versión actual desplaza un carril cargado; para varios carriles debe ampliarse la generación de combinaciones transversales."
        )
    reemplazos = 0
    for nombre in tuple(valores):
        confirmado = getattr(config.trafico, f"factor_distribucion_{nombre}")
        if confirmado is not None:
            valores[nombre] = confirmado
            reemplazos += 1
    if reemplazos:
        advertencias.append(
            f"Se reemplazaron {reemplazos} factores de parrilla por valores confirmados en la configuración."
        )
    factores = FactoresDistribucion(advertencias=tuple(advertencias), **valores)
    return ResultadoParrilla(
        factores=factores,
        x_nodos_mm=modelo.x_mm,
        y_nodos_mm=modelo.y_mm,
        y_vigas_mm=modelo.y_vigas_mm,
        centros_carril_mm=centros,
        participacion_momento=pm,
        participacion_corte=pv,
        participacion_fatiga=pf,
        casos_criticos=casos,
        error_equilibrio_maximo=max(em, ev, ef),
        numero_grados_libertad=modelo.rigidez.shape[0],
        advertencias=tuple(advertencias),
    )

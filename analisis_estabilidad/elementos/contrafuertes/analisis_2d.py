#!/usr/bin/env python3
"""Análisis FEM 2D de los contrafuertes centrales CF-C1, CF-C2 y CF-C3.

El alma de cada contrafuerte se representa mediante elementos isoparamétricos
Q4 en esfuerzo plano. La geometría es trapezoidal: su longitud, medida desde
la pantalla hacia el talón, varía linealmente entre 6.10 m en la base y
1.17 m en la corona. La base se considera empotrada en la zapata.

Las cargas son las acciones, iguales y opuestas, de las reacciones nodales
obtenidas por ``analizar_pantalla_shell_3d.py`` en cada eje de contrafuerte.
Se ensambla y factoriza una sola matriz de rigidez; únicamente se cambia el
vector de cargas para los tres contrafuertes y los cinco casos del shell.

Este archivo realiza análisis, no diseño. No calcula áreas de acero ni DCR.
Unidades internas: kN, m, kN/m².
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.linalg import factorized


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.elementos.pantalla.analisis_shell_3d import (  # noqa: E402
    CASOS,
    ParametrosShell,
    analizar_modelo,
)


CONTRAFUERTES = ("CF-C1", "CF-C2", "CF-C3")
RUTA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_SALIDA = RUTA_PROYECTO/".tmp"/"legacy"/"contrafuertes"/"analisis_2d"


@dataclass(frozen=True)
class ParametrosContrafuerte:
    altura_m: float = 7.85
    longitud_base_m: float = 6.10
    longitud_corona_m: float = 0.50
    espesor_m: float = 0.40
    poisson: float = 0.20
    divisiones_horizontales: int = 14
    tamano_malla_shell_m: float = 0.50

    def validar(self) -> None:
        if self.altura_m <= 0:
            raise ValueError("La altura debe ser positiva")
        if self.longitud_base_m <= 0 or self.longitud_corona_m <= 0:
            raise ValueError("Las longitudes del trapecio deben ser positivas")
        if self.longitud_corona_m >= self.longitud_base_m:
            raise ValueError("La longitud de corona debe ser menor que la de base")
        if self.espesor_m <= 0:
            raise ValueError("El espesor debe ser positivo")
        if not 0 < self.poisson < 0.5:
            raise ValueError("El coeficiente de Poisson debe estar entre 0 y 0.5")
        if self.divisiones_horizontales < 2:
            raise ValueError("Se requieren al menos dos divisiones horizontales")

    def longitud(self, z_m: float) -> float:
        """Longitud horizontal del alma a la elevación ``z_m``."""
        if not -1e-9 <= z_m <= self.altura_m+1e-9:
            raise ValueError("Elevación fuera del contrafuerte")
        r = min(1.0, max(0.0, z_m/self.altura_m))
        return self.longitud_base_m+r*(self.longitud_corona_m-self.longitud_base_m)


@dataclass
class MallaContrafuerte:
    nodos: np.ndarray
    elementos: np.ndarray
    niveles_m: np.ndarray
    nodos_pantalla: np.ndarray
    nodos_base: np.ndarray
    nx: int


@dataclass
class ReaccionesNodales:
    contrafuerte: str
    caso: str
    z_m: np.ndarray
    reaccion_pantalla_kn: np.ndarray

    @property
    def carga_contrafuerte_kn(self) -> np.ndarray:
        """Acción de la pantalla sobre el contrafuerte, positiva hacia exterior."""
        return -self.reaccion_pantalla_kn

    @property
    def resultante_abs_kn(self) -> float:
        return float(abs(np.sum(self.reaccion_pantalla_kn)))

    @property
    def momento_base_abs_kn_m(self) -> float:
        return float(abs(np.dot(self.reaccion_pantalla_kn, self.z_m)))


def generar_malla(p: ParametrosContrafuerte, niveles_m: np.ndarray) -> MallaContrafuerte:
    """Genera una malla estructurada que se adapta al trapecio real."""
    p.validar()
    niveles = np.asarray(niveles_m, dtype=float)
    if len(niveles) < 2 or not np.all(np.diff(niveles) > 0):
        raise ValueError("Los niveles deben ser estrictamente crecientes")
    if abs(niveles[0]) > 1e-9 or abs(niveles[-1]-p.altura_m) > 1e-8:
        raise ValueError("Los niveles deben abarcar de 0 a la altura del contrafuerte")

    nx = p.divisiones_horizontales
    nz = len(niveles)-1
    nodos = np.zeros(((nx+1)*(nz+1), 2), dtype=float)
    mapa = np.zeros((nz+1, nx+1), dtype=int)
    for j, z in enumerate(niveles):
        longitud = p.longitud(float(z))
        for i in range(nx+1):
            tag = j*(nx+1)+i
            # x=0 corresponde a la unión con la pantalla.
            nodos[tag] = (longitud*i/nx, z)
            mapa[j, i] = tag

    elementos = []
    for j in range(nz):
        for i in range(nx):
            elementos.append([
                int(mapa[j, i]), int(mapa[j, i+1]),
                int(mapa[j+1, i+1]), int(mapa[j+1, i]),
            ])
    return MallaContrafuerte(
        nodos=nodos,
        elementos=np.asarray(elementos, dtype=int),
        niveles_m=niveles,
        nodos_pantalla=mapa[:, 0].copy(),
        nodos_base=mapa[0, :].copy(),
        nx=nx,
    )


def _funciones_forma(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = 0.25*np.array([
        (1-xi)*(1-eta), (1+xi)*(1-eta),
        (1+xi)*(1+eta), (1-xi)*(1+eta),
    ])
    dxi = 0.25*np.array([-(1-eta), 1-eta, 1+eta, -(1+eta)])
    deta = 0.25*np.array([-(1-xi), -(1+xi), 1+xi, 1-xi])
    return n, dxi, deta


def matriz_constitutiva(ec_kn_m2: float, nu: float) -> np.ndarray:
    """Matriz elástica de esfuerzo plano."""
    return ec_kn_m2/(1-nu**2)*np.array([
        [1.0, nu, 0.0],
        [nu, 1.0, 0.0],
        [0.0, 0.0, (1-nu)/2],
    ])


def matriz_b(coords: np.ndarray, xi: float, eta: float) -> tuple[np.ndarray, float]:
    _, dxi, deta = _funciones_forma(xi, eta)
    j = np.array([
        [np.dot(dxi, coords[:, 0]), np.dot(dxi, coords[:, 1])],
        [np.dot(deta, coords[:, 0]), np.dot(deta, coords[:, 1])],
    ])
    detj = float(np.linalg.det(j))
    if detj <= 1e-12:
        raise ValueError("Elemento Q4 invertido o degenerado")
    derivadas = np.linalg.solve(j, np.vstack((dxi, deta)))
    dx, dy = derivadas[0], derivadas[1]
    b = np.zeros((3, 8))
    for i in range(4):
        b[0, 2*i] = dx[i]
        b[1, 2*i+1] = dy[i]
        b[2, 2*i] = dy[i]
        b[2, 2*i+1] = dx[i]
    return b, detj


def rigidez_elemento(coords: np.ndarray, p: ParametrosContrafuerte,
                     ec_kn_m2: float) -> np.ndarray:
    d = matriz_constitutiva(ec_kn_m2, p.poisson)
    ke = np.zeros((8, 8))
    g = 1/math.sqrt(3)
    for xi in (-g, g):
        for eta in (-g, g):
            b, detj = matriz_b(coords, xi, eta)
            ke += b.T@d@b*p.espesor_m*detj
    return ke


def ensamblar_rigidez(malla: MallaContrafuerte, p: ParametrosContrafuerte,
                      ec_kn_m2: float) -> csr_matrix:
    filas: list[int] = []
    columnas: list[int] = []
    datos: list[float] = []
    for conn in malla.elementos:
        ke = rigidez_elemento(malla.nodos[conn], p, ec_kn_m2)
        dofs = np.array([2*n+d for n in conn for d in range(2)], dtype=int)
        ii, jj = np.meshgrid(dofs, dofs, indexing="ij")
        filas.extend(ii.ravel())
        columnas.extend(jj.ravel())
        datos.extend(ke.ravel())
    ndof = 2*len(malla.nodos)
    return coo_matrix((datos, (filas, columnas)), shape=(ndof, ndof)).tocsr()


def extraer_reacciones_shell(
        p: ParametrosContrafuerte, resultado_shell: dict | None = None) -> tuple[
        ParametrosShell, np.ndarray, list[ReaccionesNodales]]:
    """Ejecuta el shell una vez y extrae sus fuerzas de interfaz por nivel."""
    ps = ParametrosShell(
        altura_modelada_m=p.altura_m,
        tamano_malla_m=p.tamano_malla_shell_m,
    )
    if resultado_shell is not None:
        registros = resultado_shell.get("reacciones_nodales_contrafuertes")
        if not registros:
            raise ValueError(
                "El resultado shell no contiene reacciones_nodales_contrafuertes"
            )
        seleccionados = [x for x in registros if x["contrafuerte"] in CONTRAFUERTES]
        if not seleccionados:
            raise ValueError("El resultado shell no contiene los contrafuertes centrales")
        niveles = np.asarray([0.0, *seleccionados[0]["z_m"]], dtype=float)
        salida = [
            ReaccionesNodales(
                contrafuerte=x["contrafuerte"],
                caso=x["caso"],
                z_m=np.asarray(x["z_m"], dtype=float),
                reaccion_pantalla_kn=np.asarray(x["reaccion_pantalla_kN"], dtype=float),
            )
            for x in seleccionados
        ]
        return ps, niveles, salida
    malla, _, resultados = analizar_modelo(ps)
    niveles = np.asarray(malla.niveles_m, dtype=float)
    salida: list[ReaccionesNodales] = []
    for nombre in CONTRAFUERTES:
        ie = next(i for i, e in enumerate(malla.estaciones) if e.etiqueta == nombre)
        e = malla.estaciones[ie]
        normal = np.array([-e.tangente_xy[1], e.tangente_xy[0], 0.0])
        for resultado in resultados:
            r = []
            for j in range(1, len(niveles)):
                nodo = int(malla.nodo_por_estacion_nivel[ie, j])
                fuerza = resultado.reacciones[6*nodo:6*nodo+3]
                r.append(float(np.dot(fuerza, normal)))
            salida.append(ReaccionesNodales(
                contrafuerte=nombre,
                caso=resultado.caso,
                z_m=niveles[1:].copy(),
                reaccion_pantalla_kn=np.asarray(r),
            ))
    return ps, niveles, salida


def vector_carga(malla: MallaContrafuerte, cargas: ReaccionesNodales) -> np.ndarray:
    """Aplica en el borde vertical la acción opuesta a la reacción del shell."""
    if len(cargas.z_m) != len(malla.niveles_m)-1:
        raise ValueError("Número de reacciones incompatible con la malla")
    if not np.allclose(cargas.z_m, malla.niveles_m[1:], atol=1e-9):
        raise ValueError("Los niveles de carga no coinciden con la malla")
    f = np.zeros(2*len(malla.nodos))
    # +x va de la pantalla hacia el talón. La pantalla tira del contrafuerte
    # hacia el exterior, por eso se aplica -R_pantalla en el gdl x.
    for nodo, px in zip(malla.nodos_pantalla[1:], cargas.carga_contrafuerte_kn):
        f[2*int(nodo)] += px
    return f


def _esfuerzos_gauss(malla: MallaContrafuerte, p: ParametrosContrafuerte,
                     ec_kn_m2: float, u: np.ndarray) -> list[dict]:
    d = matriz_constitutiva(ec_kn_m2, p.poisson)
    g = 1/math.sqrt(3)
    salida: list[dict] = []
    for ie, conn in enumerate(malla.elementos):
        coords = malla.nodos[conn]
        dofs = np.array([2*n+k for n in conn for k in range(2)])
        ue = u[dofs]
        for xi in (-g, g):
            for eta in (-g, g):
                n, _, _ = _funciones_forma(xi, eta)
                b, detj = matriz_b(coords, xi, eta)
                sx, sy, txy = d@b@ue
                prom = 0.5*(sx+sy)
                radio = math.hypot(0.5*(sx-sy), txy)
                s1, s2 = prom+radio, prom-radio
                ang = 0.5*math.degrees(math.atan2(2*txy, sx-sy))
                xy = n@coords
                salida.append({
                    "elemento": ie,
                    "x_m": float(xy[0]), "z_m": float(xy[1]),
                    "sigma_x_kN_m2": float(sx),
                    "sigma_z_kN_m2": float(sy),
                    "tau_xz_kN_m2": float(txy),
                    "sigma_1_kN_m2": float(s1),
                    "sigma_2_kN_m2": float(s2),
                    "angulo_sigma_1_grados": float(ang),
                    "peso_integracion_m2": float(detj),
                })
    return salida


def resultantes_por_corte(cargas: ReaccionesNodales,
                          niveles: np.ndarray) -> list[dict]:
    """Equilibrio de las cargas ubicadas por encima de cada corte."""
    salida = []
    acciones = cargas.carga_contrafuerte_kn
    for z in niveles:
        mascara = cargas.z_m > z+1e-10
        v = float(np.sum(acciones[mascara]))
        m = float(np.dot(acciones[mascara], cargas.z_m[mascara]-z))
        salida.append({
            "z_corte_m": float(z),
            "V_kN": v,
            "M_kN_m": m,
            "V_abs_kN": abs(v),
            "M_abs_kN_m": abs(m),
        })
    return salida


def resolver_modelo(
    p: ParametrosContrafuerte, resultado_shell: dict | None = None
) -> dict:
    """Resuelve los tres contrafuertes reutilizando una única factorización."""
    ps, niveles, cargas = extraer_reacciones_shell(p, resultado_shell)
    malla = generar_malla(p, niveles)
    k = ensamblar_rigidez(malla, p, ps.ec_kn_m2)
    restringidos = np.array(sorted(
        2*int(n)+d for n in malla.nodos_base for d in range(2)
    ), dtype=int)
    todos = np.arange(k.shape[0])
    libres = np.setdiff1d(todos, restringidos, assume_unique=True)
    resolver = factorized(k[libres][:, libres].tocsc())

    casos = []
    for carga in cargas:
        f = vector_carga(malla, carga)
        u = np.zeros_like(f)
        u[libres] = resolver(f[libres])
        if not np.all(np.isfinite(u)):
            raise RuntimeError("La solución FEM contiene valores no finitos")
        reacciones = np.asarray(k@u-f).ravel()
        esfuerzos = _esfuerzos_gauss(malla, p, ps.ec_kn_m2, u)
        desplazamientos = u.reshape((-1, 2))
        dmax = float(np.max(np.linalg.norm(desplazamientos, axis=1))*1000)

        carga_xy = f.reshape((-1, 2)).sum(axis=0)
        reaccion_xy = reacciones.reshape((-1, 2))[malla.nodos_base].sum(axis=0)
        m_carga = float(np.sum(
            malla.nodos[:, 0]*f.reshape((-1, 2))[:, 1]
            - malla.nodos[:, 1]*f.reshape((-1, 2))[:, 0]
        ))
        rb = reacciones.reshape((-1, 2))[malla.nodos_base]
        xb = malla.nodos[malla.nodos_base]
        m_reaccion = float(np.sum(xb[:, 0]*rb[:, 1]-xb[:, 1]*rb[:, 0]))
        s1 = np.array([x["sigma_1_kN_m2"] for x in esfuerzos])
        s2 = np.array([x["sigma_2_kN_m2"] for x in esfuerzos])

        casos.append({
            "contrafuerte": carga.contrafuerte,
            "caso": carga.caso,
            "reacciones_nodales": [
                {"z_m": float(z), "R_pantalla_kN": float(r),
                 "P_contrafuerte_kN": float(-r)}
                for z, r in zip(carga.z_m, carga.reaccion_pantalla_kn)
            ],
            "resultante_abs_kN": carga.resultante_abs_kn,
            "momento_base_abs_kN_m": carga.momento_base_abs_kn_m,
            "resultantes_por_corte": resultantes_por_corte(carga, niveles),
            "desplazamiento_max_mm": dmax,
            "sigma_1_max_MPa": float(np.max(s1)/1000),
            "sigma_1_p95_MPa": float(np.percentile(s1, 95)/1000),
            "sigma_2_min_MPa": float(np.min(s2)/1000),
            "sigma_2_p05_MPa": float(np.percentile(s2, 5)/1000),
            "carga_total_kN": carga_xy.tolist(),
            "reaccion_base_kN": reaccion_xy.tolist(),
            "momento_carga_kN_m": m_carga,
            "momento_reaccion_kN_m": m_reaccion,
            "error_fuerza_kN": float(np.linalg.norm(carga_xy+reaccion_xy)),
            "error_momento_kN_m": abs(m_carga+m_reaccion),
            "desplazamientos_m": desplazamientos.tolist(),
            "esfuerzos_gauss": esfuerzos,
        })

    return {
        "identificacion": "FEM 2D en esfuerzo plano de contrafuertes centrales trapezoidales",
        "alcance": "ANALISIS; no incluye diseño ni dimensionamiento de refuerzo",
        "parametros": asdict(p),
        "material": {
            "Ec_kN_m2": ps.ec_kn_m2,
            "poisson": p.poisson,
            "fc_MPa": ps.fc_mpa,
            "fy_MPa": ps.fy_mpa,
        },
        "modelo": {
            "tipo": "Q4 isoparamétrico, esfuerzo plano, integración 2x2",
            "ejes": "+x desde pantalla hacia talón; +z vertical",
            "apoyo": "borde basal empotrado en zapata",
            "transferencia": "acción opuesta a reacciones nodales del shell 3D",
            "matriz_unica": True,
            "factorizaciones": 1,
            "nodos": malla.nodos.tolist(),
            "elementos": malla.elementos.tolist(),
            "niveles_m": niveles.tolist(),
        },
        "casos": casos,
        "validaciones": {
            "geometria_base_m": p.longitud(0.0),
            "geometria_corona_m": p.longitud(p.altura_m),
            "numero_contrafuertes": len({x["contrafuerte"] for x in casos}),
            "numero_casos": len(casos),
            "max_error_fuerza_kN": max(x["error_fuerza_kN"] for x in casos),
            "max_error_momento_kN_m": max(x["error_momento_kN_m"] for x in casos),
            "equilibrio_cumple": all(
                x["error_fuerza_kN"] < 1e-6 and x["error_momento_kN_m"] < 1e-6
                for x in casos
            ),
            "simetria_C1_C3_cumple": _validar_simetria(casos),
        },
    }


def _validar_simetria(casos: list[dict]) -> bool:
    for caso in CASOS:
        a = next(x for x in casos if x["contrafuerte"] == "CF-C1" and x["caso"] == caso)
        b = next(x for x in casos if x["contrafuerte"] == "CF-C3" and x["caso"] == caso)
        escala = max(a["resultante_abs_kN"], b["resultante_abs_kN"], 1.0)
        if abs(a["resultante_abs_kN"]-b["resultante_abs_kN"])/escala > 1e-9:
            return False
        if abs(a["desplazamiento_max_mm"]-b["desplazamiento_max_mm"]) > 1e-9:
            return False
    return True


def generar_markdown(r: dict) -> str:
    p = r["parametros"]
    lineas = [
        "# Análisis FEM 2D de contrafuertes centrales trapezoidales", "",
        "## 1. Objetivo y alcance", "",
        "Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando "
        "únicamente las reacciones nodales transferidas por la pantalla shell 3D. "
        "Este documento no dimensiona acero ni verifica resistencias.", "",
        "## 2. Geometría y modelo", "",
        "| Parámetro | Valor | Unidad |", "|---|---:|---|",
        f"| Altura cargada | {p['altura_m']:.3f} | m |",
        f"| Longitud en base | {p['longitud_base_m']:.3f} | m |",
        f"| Longitud en corona | {p['longitud_corona_m']:.3f} | m |",
        f"| Espesor | {p['espesor_m']:.3f} | m |",
        f"| Divisiones horizontales | {p['divisiones_horizontales']} | — |", "",
        "Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración "
        "2×2 y comportamiento lineal elástico no fisurado. El borde basal está "
        "empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.", "",
        "La longitud varía linealmente con la altura:", "",
        "`L(z) = 6.10 + (1.17 - 6.10) z / 9.80`.", "",
        "## 3. Acciones transferidas y respuesta", "",
        "| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for x in r["casos"]:
        lineas.append(
            f"| {x['contrafuerte']} | {x['caso']} | {x['resultante_abs_kN']:.2f} kN | "
            f"{x['momento_base_abs_kN_m']:.2f} kN·m | {x['desplazamiento_max_mm']:.4f} mm | "
            f"{x['sigma_1_max_MPa']:.3f} MPa | {x['sigma_1_p95_MPa']:.3f} MPa | "
            f"{x['sigma_2_min_MPa']:.3f} MPa | {x['error_fuerza_kN']:.2e} kN | "
            f"{x['error_momento_kN_m']:.2e} kN·m |"
        )
    v = r["validaciones"]
    lineas += [
        "", "## 4. Verificaciones del análisis", "",
        "| Control | Resultado |", "|---|---|",
        f"| Un solo modelo/factorización | {'Conforme' if r['modelo']['matriz_unica'] else 'No conforme'} |",
        f"| Tres contrafuertes y 15 soluciones | {v['numero_contrafuertes']} / {v['numero_casos']} |",
        f"| Equilibrio | {'Conforme' if v['equilibrio_cumple'] else 'No conforme'} |",
        f"| Simetría CF-C1 / CF-C3 | {'Conforme' if v['simetria_C1_C3_cumple'] else 'No conforme'} |",
        "", "## 5. Interpretación y límites", "",
        "- Los picos puntuales de esfuerzo junto a cargas nodales y al empotramiento "
        "son dependientes de la malla; por eso se reportan también percentiles P95/P05.",
        "- Las resultantes por cortes horizontales se conservan en el JSON y serán la "
        "base del posterior modelo de bielas y tirantes.",
        "- El modelo supone unión monolítica, base rígida y concreto no fisurado. "
        "No representa aún la flexibilidad de la zapata ni redistribuye las reacciones "
        "hacia la pantalla global.",
        "- El diseño del refuerzo, bielas, nodos, interfaces y anclajes queda expresamente "
        "reservado para la siguiente etapa.",
    ]
    return "\n".join(lineas)+"\n"


def generar_graficos(r: dict, carpeta: Path) -> list[Path]:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.collections import PolyCollection
    except ImportError as exc:  # pragma: no cover
        raise ImportError("matplotlib es necesario para generar gráficos") from exc

    carpeta.mkdir(parents=True, exist_ok=True)
    nodos = np.asarray(r["modelo"]["nodos"])
    elementos = np.asarray(r["modelo"]["elementos"], dtype=int)
    casos_ri = [
        next(x for x in r["casos"] if x["contrafuerte"] == cf and x["caso"] == "Resistencia I-a")
        for cf in CONTRAFUERTES
    ]

    promedios: list[np.ndarray] = []
    for caso in casos_ri:
        valores = np.zeros(len(elementos))
        conteos = np.zeros(len(elementos))
        for gp in caso["esfuerzos_gauss"]:
            ie = gp["elemento"]
            valores[ie] += gp["sigma_1_kN_m2"]/1000
            conteos[ie] += 1
        promedios.append(valores/conteos)
    vmax = max(float(np.max(x)) for x in promedios)
    factor_deformada = 500.0
    nxfila = r["parametros"]["divisiones_horizontales"]+1
    nzfila = len(r["modelo"]["niveles_m"])
    mapa = np.arange(len(nodos)).reshape((nzfila, nxfila))
    frontera = np.concatenate((
        mapa[0, :], mapa[1:, -1], mapa[-1, -2::-1], mapa[-2:0:-1, 0],
        mapa[0, :1],
    ))

    fig, axes = plt.subplots(1, 3, figsize=(15, 6), constrained_layout=True)
    for ax, caso, valores in zip(axes, casos_ri, promedios):
        poligonos = [nodos[c] for c in elementos]
        coleccion = PolyCollection(
            poligonos, array=valores, cmap="viridis", edgecolors="none",
            clim=(0.0, vmax),
        )
        ax.add_collection(coleccion)
        u = np.asarray(caso["desplazamientos_m"])
        deformada = nodos+factor_deformada*u
        ax.plot(nodos[frontera, 0], nodos[frontera, 1], "k-", lw=1.0,
                label="No deformada")
        ax.plot(deformada[frontera, 0], deformada[frontera, 1], "r--", lw=1.2,
                label=f"Deformada ×{factor_deformada:.0f}")
        ax.autoscale()
        ax.set_aspect("equal")
        ax.set_title(f"{caso['contrafuerte']} — Resistencia I-a")
        ax.set_xlabel("x hacia talón (m)")
        ax.set_ylabel("z (m)")
        ax.legend(loc="upper right", fontsize=8)
    cb = fig.colorbar(coleccion, ax=axes, orientation="horizontal", pad=0.08,
                      fraction=0.06)
    cb.set_label("σ1 promedio del elemento (MPa), escala común")
    ruta1 = carpeta/"contrafuertes_centrales_sigma1.png"
    fig.savefig(ruta1, dpi=180)
    plt.close(fig)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for caso in casos_ri:
        z = [x["z_m"] for x in caso["reacciones_nodales"]]
        pnod = [abs(x["P_contrafuerte_kN"]) for x in caso["reacciones_nodales"]]
        cortes = caso["resultantes_por_corte"]
        ax1.plot(pnod, z, marker="o", ms=3, label=caso["contrafuerte"])
        ax2.plot([x["M_abs_kN_m"] for x in cortes],
                 [x["z_corte_m"] for x in cortes], label=caso["contrafuerte"])
    ax1.set(xlabel="Fuerza nodal |P| (kN)", ylabel="z (m)",
            title="Acciones de interfaz — Resistencia I-a")
    ax2.set(xlabel="|M(z)| (kN·m)", ylabel="z (m)",
            title="Momento por equilibrio de cargas superiores")
    for ax in (ax1, ax2):
        ax.grid(True, alpha=0.3)
        ax.legend()
    ruta2 = carpeta/"contrafuertes_centrales_acciones.png"
    fig.savefig(ruta2, dpi=180)
    plt.close(fig)
    return [ruta1, ruta2]


def _json_default(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Tipo no serializable: {type(obj).__name__}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--divisiones-horizontales", type=int, default=14)
    parser.add_argument("--salida-md", type=Path,
                        default=CARPETA_SALIDA/"analisis_contrafuertes_centrales_2d.md")
    parser.add_argument("--salida-json", type=Path,
                        default=CARPETA_SALIDA/"analisis_contrafuertes_centrales_2d.json")
    parser.add_argument("--sin-graficos", action="store_true")
    return parser.parse_args()


def main() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = parse_args()
    p = ParametrosContrafuerte(divisiones_horizontales=args.divisiones_horizontales)
    resultado = resolver_modelo(p)
    args.salida_md.parent.mkdir(parents=True, exist_ok=True)
    args.salida_json.parent.mkdir(parents=True, exist_ok=True)
    args.salida_md.write_text(generar_markdown(resultado), encoding="utf-8")
    args.salida_json.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )
    graficos = [] if args.sin_graficos else generar_graficos(resultado, args.salida_md.parent)
    v = resultado["validaciones"]
    print("ANÁLISIS FEM 2D DE CONTRAFUERTES CENTRALES")
    print(f"Modelo único: {len(resultado['modelo']['nodos'])} nodos, "
          f"{len(resultado['modelo']['elementos'])} elementos, 1 factorización")
    print(f"Soluciones: {v['numero_casos']} (CF-C1, CF-C2 y CF-C3)")
    print(f"Equilibrio: {'CONFORME' if v['equilibrio_cumple'] else 'NO CONFORME'}")
    print(f"Simetría CF-C1/CF-C3: {'CONFORME' if v['simetria_C1_C3_cumple'] else 'NO CONFORME'}")
    print(f"Markdown: {args.salida_md.resolve()}")
    print(f"JSON: {args.salida_json.resolve()}")
    for ruta in graficos:
        print(f"Gráfico: {ruta.resolve()}")


if __name__ == "__main__":
    main()

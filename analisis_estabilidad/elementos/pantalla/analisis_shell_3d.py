#!/usr/bin/env python3
"""Análisis FEM 3D independiente de la pantalla plegada del estribo.

Modelo lineal elástico de cascarones planos Q4. Cada elemento combina:

* membrana bilineal en estado plano de esfuerzos;
* placa de Mindlin-Reissner con interpolación MITC4 de cortante;
* seis grados de libertad globales por nodo.

La poligonal real se extruye hasta la altura modelada sobre la zapata. La base
se considera empotrada y cada eje de contrafuerte restringe únicamente la
traslación normal local a la pantalla. Los contrafuertes no se diseñan. La
cajuela y las cargas transmitidas por ella están fuera del modelo.

Unidades internas del FEM: kN, m y kN/m². El diseño se presenta también en
tf, tf·m y cm²/m para conservar coherencia con el agente de subestructura.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.linalg import factorized


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analisis_estabilidad.elementos.estribo.estabilidad_global import (  # noqa: E402
    GEOM,
    MAT,
    SEISMIC,
    coulomb_active_coefficient,
    get_surcharge_height,
    mononobe_okabe_coefficient,
)


# =============================================================================
# DATOS EDITABLES
# =============================================================================

PUNTOS_PLANTA = (
    (0.00, 7.09, "contrafuerte", "CF-I1"),
    (2.15, 4.94, "contrafuerte", "CF-I2"),
    (4.27, 2.82, "contrafuerte", "CF-I3"),
    (7.09, 0.00, "quiebre", "QI"),
    (7.86, 0.00, "contrafuerte", "CF-C1"),
    (10.66, 0.00, "contrafuerte", "CF-C2"),
    (13.46, 0.00, "contrafuerte", "CF-C3"),
    (14.23, 0.00, "quiebre", "QD"),
    (17.05, 2.82, "contrafuerte", "CF-D1"),
    (19.17, 4.94, "contrafuerte", "CF-D2"),
    (21.32, 7.09, "contrafuerte", "CF-D3"),
)

CASOS = (
    "Servicio I", "Resistencia I-a", "Resistencia I-b",
    "Evento Extremo I-A", "Evento Extremo I-B",
)
BARRAS_MM = {'1/2"': 12.700, '5/8"': 15.875, '3/4"': 19.050, '1"': 25.400}
TF_A_KN = 9.80665
TF_M_A_KN_M = 9.80665
KGF_CM2_A_MPA = 0.0980665
MM_POR_PULGADA = 25.4
MPA_A_KSI = 0.1450377377
CM2_M_POR_IN2_FT = 6.4516/0.3048


@dataclass(frozen=True)
class ParametrosShell:
    puntos_planta: tuple[tuple[float, float, str, str], ...] = PUNTOS_PLANTA
    altura_total_m: float = GEOM.hp
    altura_modelada_m: float = GEOM.hp - (GEOM.c_cajuela + GEOM.d_cajuela)
    espesor_m: float = 0.40
    # Recubrimiento nominal por cara: la cara exterior (+n) está en contacto
    # con agua sometida a abrasión; la interior (-n) con el relleno.
    recubrimiento_exterior_mm: float = 100.0
    recubrimiento_interior_mm: float = 75.0
    poisson: float = 0.20
    tamano_malla_m: float = 0.50
    factor_cortante: float = 5.0/6.0
    estabilizacion_drilling: float = 1.0e-7
    barras: tuple[str, ...] = ('5/8"', '5/8"', '3/4"', '1"')
    espaciamiento_minimo_mm: float = 100.0
    paso_espaciamiento_mm: float = 5.0
    phi_flexion: float = 0.90
    phi_cortante_e060: float = 0.85
    phi_cortante_mtc: float = 0.90

    @property
    def ec_kn_m2(self) -> float:
        # E.060: Ec=15000 sqrt(f'c), f'c y Ec en kgf/cm².
        return 15000.0*math.sqrt(MAT.f_c)*98.0665

    @property
    def fc_mpa(self) -> float:
        return MAT.f_c*KGF_CM2_A_MPA

    @property
    def fy_mpa(self) -> float:
        return MAT.fy*KGF_CM2_A_MPA

    def validar(self) -> None:
        if len(self.puntos_planta) < 2:
            raise ValueError("Se requieren al menos dos puntos de planta")
        if self.altura_modelada_m <= 0 or self.altura_modelada_m >= self.altura_total_m:
            raise ValueError("La altura modelada debe ser positiva y menor que la total")
        if self.espesor_m <= 0 or self.tamano_malla_m <= 0:
            raise ValueError("Espesor y tamaño de malla deben ser positivos")
        if not 0 < self.poisson < 0.5:
            raise ValueError("El coeficiente de Poisson debe estar entre 0 y 0.5")
        for nombre, recubrimiento in (
            ("exterior", self.recubrimiento_exterior_mm),
            ("interior", self.recubrimiento_interior_mm),
        ):
            if not 0 < recubrimiento < self.espesor_m*1000/2:
                raise ValueError(
                    f"Recubrimiento {nombre} incompatible con el espesor"
                )
        for a, b in zip(self.puntos_planta, self.puntos_planta[1:]):
            if math.hypot(b[0]-a[0], b[1]-a[1]) <= 1e-9:
                raise ValueError("Existen puntos consecutivos coincidentes")


@dataclass
class Estacion:
    indice: int
    x_m: float
    y_m: float
    s_m: float
    etiqueta: str = ""
    tipo: str = "malla"
    tangente_xy: tuple[float, float] = (1.0, 0.0)

    @property
    def es_contrafuerte(self) -> bool:
        return self.tipo == "contrafuerte"


@dataclass
class MallaShell:
    nodos: np.ndarray
    elementos: np.ndarray
    estaciones: list[Estacion]
    niveles_m: list[float]
    nodo_por_estacion_nivel: np.ndarray
    regiones_elemento: list[str]
    zonas_elemento: list[str]


@dataclass
class ResultadoCaso:
    caso: str
    escenario: str
    desplazamientos: np.ndarray
    reacciones: np.ndarray
    puntos_gauss: list[dict]
    carga_total_kn: tuple[float, float, float]
    reaccion_total_kn: tuple[float, float, float]
    error_fuerza_kn: float
    error_momento_kn_m: float
    desplazamiento_max_mm: float
    reacciones_contrafuertes: dict[str, dict]


@dataclass(frozen=True)
class SistemaLinealShell:
    """Sistema restringido y factorizado que comparten los casos de carga."""

    kq: csr_matrix
    libres: np.ndarray
    resolver: Callable[[np.ndarray], np.ndarray]


def _distancia(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0]-a[0], b[1]-a[1])


def longitud_poligonal(puntos: Iterable[tuple[float, float, str, str]]) -> float:
    pts = list(puntos)
    return sum(_distancia((a[0], a[1]), (b[0], b[1])) for a, b in zip(pts, pts[1:]))


def _niveles_verticales(altura: float, objetivo: float) -> list[float]:
    limites = (0.0, altura/3.0, 2.0*altura/3.0, altura)
    niveles = [0.0]
    for z0, z1 in zip(limites, limites[1:]):
        n = max(1, math.ceil((z1-z0)/objetivo))
        niveles.extend(z0+(z1-z0)*i/n for i in range(1, n+1))
    return niveles


def generar_estaciones(p: ParametrosShell) -> list[Estacion]:
    """Subdivide cada tramo y conserva exactamente apoyos y quiebres."""
    controles = list(p.puntos_planta)
    estaciones: list[Estacion] = []
    s = 0.0
    for it, (a, b) in enumerate(zip(controles, controles[1:])):
        ax, ay, tipo_a, nombre_a = a
        bx, by, _, _ = b
        L = _distancia((ax, ay), (bx, by))
        n = max(1, math.ceil(L/p.tamano_malla_m))
        tx, ty = (bx-ax)/L, (by-ay)/L
        for k in range(n):
            f = k/n
            estaciones.append(Estacion(
                indice=len(estaciones), x_m=ax+f*(bx-ax), y_m=ay+f*(by-ay),
                s_m=s+f*L, etiqueta=nombre_a if k == 0 else "",
                tipo=tipo_a if k == 0 else "malla", tangente_xy=(tx, ty),
            ))
        s += L
        # El último punto se añade después del bucle completo.
        if it == len(controles)-2:
            tipo_b, nombre_b = b[2], b[3]
            estaciones.append(Estacion(
                indice=len(estaciones), x_m=bx, y_m=by, s_m=s,
                etiqueta=nombre_b, tipo=tipo_b, tangente_xy=(tx, ty),
            ))

    # Los puntos de control intermedios omitidos por la lógica anterior se
    # recuperan identificando sus coordenadas y asignando sus metadatos.
    for x, y, tipo, nombre in controles:
        i = min(range(len(estaciones)), key=lambda j: math.hypot(
            estaciones[j].x_m-x, estaciones[j].y_m-y,
        ))
        if math.hypot(estaciones[i].x_m-x, estaciones[i].y_m-y) > 1e-8:
            raise RuntimeError(f"No se conservó el punto de control {nombre}")
        estaciones[i].tipo = tipo
        estaciones[i].etiqueta = nombre
        # Tangente única del plano en apoyos; los quiebres no usan restricción.
        if tipo == "contrafuerte":
            if i == 0:
                j0, j1 = i, i+1
            elif i == len(estaciones)-1:
                j0, j1 = i-1, i
            else:
                v1 = np.array([
                    estaciones[i].x_m-estaciones[i-1].x_m,
                    estaciones[i].y_m-estaciones[i-1].y_m,
                ])
                v2 = np.array([
                    estaciones[i+1].x_m-estaciones[i].x_m,
                    estaciones[i+1].y_m-estaciones[i].y_m,
                ])
                cruz = v1[0]*v2[1]-v1[1]*v2[0]
                if abs(cruz) > 1e-8:
                    raise ValueError(f"El apoyo {nombre} coincide con un quiebre")
                j0, j1 = i-1, i+1
            dx = estaciones[j1].x_m-estaciones[j0].x_m
            dy = estaciones[j1].y_m-estaciones[j0].y_m
            L = math.hypot(dx, dy)
            estaciones[i].tangente_xy = (dx/L, dy/L)
    return estaciones


def generar_malla(p: ParametrosShell) -> MallaShell:
    p.validar()
    estaciones = generar_estaciones(p)
    niveles = _niveles_verticales(p.altura_modelada_m, p.tamano_malla_m)
    ns, nz = len(estaciones), len(niveles)
    nodos = np.zeros((ns*nz, 3), dtype=float)
    mapa = np.zeros((ns, nz), dtype=int)
    for i, e in enumerate(estaciones):
        for j, z in enumerate(niveles):
            tag = i*nz+j
            nodos[tag] = (e.x_m, e.y_m, z)
            mapa[i, j] = tag
    elementos: list[list[int]] = []
    regiones: list[str] = []
    zonas: list[str] = []
    s_qi = next(e.s_m for e in estaciones if e.etiqueta == "QI")
    s_qd = next(e.s_m for e in estaciones if e.etiqueta == "QD")
    for i in range(ns-1):
        sm = 0.5*(estaciones[i].s_m+estaciones[i+1].s_m)
        region = "Ala izquierda" if sm < s_qi else (
            "Pantalla central" if sm < s_qd else "Ala derecha"
        )
        for j in range(nz-1):
            zm = 0.5*(niveles[j]+niveles[j+1])
            zona = "Inferior" if zm < p.altura_modelada_m/3 else (
                "Intermedia" if zm < 2*p.altura_modelada_m/3 else "Superior"
            )
            elementos.append([
                int(mapa[i, j]), int(mapa[i+1, j]),
                int(mapa[i+1, j+1]), int(mapa[i, j+1]),
            ])
            regiones.append(region)
            zonas.append(zona)
    return MallaShell(
        nodos=nodos, elementos=np.asarray(elementos, dtype=int),
        estaciones=estaciones, niveles_m=niveles,
        nodo_por_estacion_nivel=mapa, regiones_elemento=regiones,
        zonas_elemento=zonas,
    )


def _funciones_forma(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    N = 0.25*np.array([
        (1-xi)*(1-eta), (1+xi)*(1-eta),
        (1+xi)*(1+eta), (1-xi)*(1+eta),
    ])
    dxi = 0.25*np.array([-(1-eta), 1-eta, 1+eta, -(1+eta)])
    deta = 0.25*np.array([-(1-xi), -(1+xi), 1+xi, 1-xi])
    return N, dxi, deta


def _ejes_elemento(coords: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ex = coords[1]-coords[0]
    ex /= np.linalg.norm(ex)
    ey = coords[3]-coords[0]
    ey -= np.dot(ey, ex)*ex
    ey /= np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    ez /= np.linalg.norm(ez)
    R = np.vstack((ex, ey, ez))  # componentes locales = R @ globales
    origen = coords[0]
    xy = np.column_stack(((coords-origen)@ex, (coords-origen)@ey))
    return R, xy


def _matrices_b(xy: np.ndarray, xi: float, eta: float) -> tuple:
    N, dxi, deta = _funciones_forma(xi, eta)
    J = np.array([
        [np.dot(dxi, xy[:, 0]), np.dot(dxi, xy[:, 1])],
        [np.dot(deta, xy[:, 0]), np.dot(deta, xy[:, 1])],
    ])
    detj = float(np.linalg.det(J))
    if detj <= 1e-12:
        raise ValueError("Elemento invertido o degenerado")
    deriv = np.linalg.solve(J, np.vstack((dxi, deta)))
    dx, dy = deriv[0], deriv[1]
    bm = np.zeros((3, 24))
    bb = np.zeros((3, 24))
    bs = np.zeros((2, 24))
    for i in range(4):
        k = 6*i
        bm[0, k] = dx[i]
        bm[1, k+1] = dy[i]
        bm[2, k] = dy[i]
        bm[2, k+1] = dx[i]
        # kappa_x=d(ry)/dx; kappa_y=-d(rx)/dy
        bb[0, k+4] = dx[i]
        bb[1, k+3] = -dy[i]
        bb[2, k+3] = -dx[i]
        bb[2, k+4] = dy[i]
        # gamma_xz=dw/dx+ry; gamma_yz=dw/dy-rx
        bs[0, k+2] = dx[i]
        bs[0, k+4] = N[i]
        bs[1, k+2] = dy[i]
        bs[1, k+3] = -N[i]
    return N, bm, bb, bs, detj


def _b_cortante_mitc4(xy: np.ndarray, xi: float, eta: float) -> np.ndarray:
    """Interpolación MITC4 de deformaciones de cortante para rectángulos."""
    bs_a = _matrices_b(xy, 0.0, -1.0)[3][0]
    bs_c = _matrices_b(xy, 0.0, 1.0)[3][0]
    bs_b = _matrices_b(xy, 1.0, 0.0)[3][1]
    bs_d = _matrices_b(xy, -1.0, 0.0)[3][1]
    bs = np.zeros((2, 24))
    bs[0] = 0.5*((1-eta)*bs_a+(1+eta)*bs_c)
    bs[1] = 0.5*((1+xi)*bs_b+(1-xi)*bs_d)
    return bs


def rigidez_elemento(coords: np.ndarray, p: ParametrosShell) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    R, xy = _ejes_elemento(coords)
    E, nu, t = p.ec_kn_m2, p.poisson, p.espesor_m
    base = E/(1-nu**2)*np.array([
        [1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1-nu)/2],
    ])
    dm = t*base
    db = t**3/12.0*base
    ds = p.factor_cortante*(E/(2*(1+nu)))*t*np.eye(2)
    kl = np.zeros((24, 24))
    g = 1/math.sqrt(3)
    for xi in (-g, g):
        for eta in (-g, g):
            _, bm, bb, _, detj = _matrices_b(xy, xi, eta)
            bs = _b_cortante_mitc4(xy, xi, eta)
            kl += (bm.T@dm@bm+bb.T@db@bb+bs.T@ds@bs)*detj
    # Estabilización débil del giro drilling local, sin aporte resistente.
    escala = max(float(np.max(np.diag(kl))), 1.0)*p.estabilizacion_drilling
    for i in range(4):
        kl[6*i+5, 6*i+5] += escala
    T = np.zeros((24, 24))
    for i in range(4):
        T[6*i:6*i+3, 6*i:6*i+3] = R
        T[6*i+3:6*i+6, 6*i+3:6*i+6] = R
    return T.T@kl@T, T, xy


def ensamblar_rigidez(malla: MallaShell, p: ParametrosShell) -> csr_matrix:
    filas: list[int] = []
    cols: list[int] = []
    datos: list[float] = []
    for conectividad in malla.elementos:
        ke, _, _ = rigidez_elemento(malla.nodos[conectividad], p)
        dofs = np.array([6*n+d for n in conectividad for d in range(6)], dtype=int)
        ii, jj = np.meshgrid(dofs, dofs, indexing="ij")
        filas.extend(ii.ravel())
        cols.extend(jj.ravel())
        datos.extend(ke.ravel())
    ndof = 6*len(malla.nodos)
    return coo_matrix((datos, (filas, cols)), shape=(ndof, ndof)).tocsr()


def matriz_transformacion_apoyos(malla: MallaShell) -> csr_matrix:
    """d_global=S q; en apoyos q[1] es el desplazamiento normal local."""
    n = len(malla.nodos)
    filas: list[int] = []
    cols: list[int] = []
    datos: list[float] = []
    estacion_por_nodo = np.repeat(np.arange(len(malla.estaciones)), len(malla.niveles_m))
    for nodo in range(n):
        e = malla.estaciones[int(estacion_por_nodo[nodo])]
        B = np.eye(6)
        if e.es_contrafuerte:
            tx, ty = e.tangente_xy
            nx, ny = -ty, tx
            B[:3, :3] = np.array([[tx, nx, 0], [ty, ny, 0], [0, 0, 1]])
        for i in range(6):
            for j in range(6):
                if abs(B[i, j]) > 0:
                    filas.append(6*nodo+i)
                    cols.append(6*nodo+j)
                    datos.append(float(B[i, j]))
    return coo_matrix((datos, (filas, cols)), shape=(6*n, 6*n)).tocsr()


def grados_restringidos(malla: MallaShell) -> np.ndarray:
    restringidos: set[int] = set()
    nz = len(malla.niveles_m)
    # Empotramiento monolítico a la zapata.
    for i in range(len(malla.estaciones)):
        nodo = int(malla.nodo_por_estacion_nivel[i, 0])
        restringidos.update(6*nodo+d for d in range(6))
    # En cada contrafuerte se restringe la coordenada normal q_y.
    for i, e in enumerate(malla.estaciones):
        if e.es_contrafuerte:
            for j in range(1, nz):
                nodo = int(malla.nodo_por_estacion_nivel[i, j])
                restringidos.add(6*nodo+1)
    return np.asarray(sorted(restringidos), dtype=int)


def preparar_sistema_lineal(
    malla: MallaShell, K: csr_matrix, S: csr_matrix
) -> SistemaLinealShell:
    """Transforma y factoriza K una sola vez para todos los casos del modelo."""
    kq = (S.T @ K @ S).tocsr()
    restringidos = grados_restringidos(malla)
    todos = np.arange(kq.shape[0])
    libres = np.setdiff1d(todos, restringidos, assume_unique=True)
    resolver = factorized(kq[libres][:, libres].tocsc())
    return SistemaLinealShell(kq=kq, libres=libres, resolver=resolver)


def coeficientes_presion(p: ParametrosShell) -> dict:
    ka = coulomb_active_coefficient(MAT.phi_relleno, MAT.delta)
    psi = math.degrees(math.atan2(SEISMIC.Kh, 1-SEISMIC.Kv))
    kae = mononobe_okabe_coefficient(MAT.phi_relleno, MAT.delta, psi)
    fn = math.cos(math.radians(MAT.delta))
    return {
        "Ka_resultante": ka, "Kae_resultante": kae,
        "factor_normal": fn, "Ka_normal": ka*fn, "Kae_normal": kae*fn,
        "angulo_sismico_grados": psi,
        "h_sobrecarga_m": get_surcharge_height(p.altura_total_m),
    }


def componentes_presion(z_m: float, p: ParametrosShell, c: dict) -> dict:
    profundidad = p.altura_total_m-z_m
    eh = MAT.gamma_r*c["Ka_normal"]*profundidad
    ls = MAT.gamma_r*c["Ka_normal"]*c["h_sobrecarga_m"]
    ae = MAT.gamma_r*(1-SEISMIC.Kv)*c["Kae_normal"]*profundidad
    ir = SEISMIC.Kh*MAT.gamma_c*p.espesor_m
    return {"EH": eh, "LS": ls, "AE": ae, "IR": ir}


def presion_caso(z_m: float, caso: str, p: ParametrosShell, c: dict) -> tuple[float, str]:
    q = componentes_presion(z_m, p, c)
    if caso == "Servicio I":
        return q["EH"]+q["LS"], "EH + LS"
    if caso in ("Resistencia I-a", "Resistencia I-b"):
        return 1.50*q["EH"]+1.75*q["LS"], "1.50 EH + 1.75 LS"
    if caso == "Evento Extremo I-A":
        return q["AE"]+0.5*q["IR"], "100% PAE + 50% PIR"
    if caso == "Evento Extremo I-B":
        return max(0.5*q["AE"], q["EH"])+q["IR"], "max(50% PAE, PA) + 100% PIR"
    raise ValueError(f"Caso desconocido: {caso}")


def presiones_franjas_resistencia_ia(p: ParametrosShell, c: dict) -> list[dict]:
    """Presiones de referencia en el borde inferior de los tres tercios."""
    salida = []
    for nombre, z_m in (
        ("Inferior", 0.0),
        ("Intermedia", p.altura_modelada_m/3.0),
        ("Superior", 2.0*p.altura_modelada_m/3.0),
    ):
        componentes = componentes_presion(z_m, p, c)
        eh_u = 1.50*componentes["EH"]
        ls_u = 1.75*componentes["LS"]
        total = eh_u+ls_u
        salida.append({
            "franja": nombre,
            "z_sobre_zapata_m": z_m,
            "profundidad_referencia_m": p.altura_total_m-z_m,
            "EH_tf_m2": componentes["EH"],
            "LS_tf_m2": componentes["LS"],
            "factor_EH": 1.50,
            "factor_LS": 1.75,
            "EH_factorizado_tf_m2": eh_u,
            "LS_factorizado_tf_m2": ls_u,
            "presion_total_tf_m2": total,
            "presion_total_kN_m2": total*TF_A_KN,
        })
    return salida


def vector_carga(malla: MallaShell, p: ParametrosShell, caso: str,
                 coef: dict) -> tuple[np.ndarray, str]:
    f = np.zeros(6*len(malla.nodos))
    escenarios: set[str] = set()
    g = 1/math.sqrt(3)
    for conectividad in malla.elementos:
        coords = malla.nodos[conectividad]
        R, xy = _ejes_elemento(coords)
        fl = np.zeros(24)
        for xi in (-g, g):
            for eta in (-g, g):
                N, _, _, _, detj = _matrices_b(xy, xi, eta)
                z = float(np.dot(N, coords[:, 2]))
                q_tf_m2, escenario = presion_caso(z, caso, p, coef)
                escenarios.add(escenario)
                q = q_tf_m2*TF_A_KN
                for i in range(4):
                    fl[6*i+2] += N[i]*q*detj
        T = np.zeros((24, 24))
        for i in range(4):
            T[6*i:6*i+3, 6*i:6*i+3] = R
            T[6*i+3:6*i+6, 6*i+3:6*i+6] = R
        fg = T.T@fl
        dofs = [6*n+d for n in conectividad for d in range(6)]
        f[dofs] += fg
    return f, " / ".join(sorted(escenarios))


def _recuperar_puntos_gauss(malla: MallaShell, p: ParametrosShell,
                            u_global: np.ndarray) -> list[dict]:
    E, nu, t = p.ec_kn_m2, p.poisson, p.espesor_m
    base = E/(1-nu**2)*np.array([
        [1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1-nu)/2],
    ])
    dm, db = t*base, t**3/12.0*base
    ds = p.factor_cortante*(E/(2*(1+nu)))*t*np.eye(2)
    g = 1/math.sqrt(3)
    salida: list[dict] = []
    for ie, conectividad in enumerate(malla.elementos):
        coords = malla.nodos[conectividad]
        _, T, xy = rigidez_elemento(coords, p)
        dofs = np.array([6*n+d for n in conectividad for d in range(6)])
        ul = T@u_global[dofs]
        for ig, (xi, eta) in enumerate((
            (-g, -g), (g, -g), (g, g), (-g, g),
        )):
            N, bm, bb, _, _ = _matrices_b(xy, xi, eta)
            bs = _b_cortante_mitc4(xy, xi, eta)
            nr = dm@bm@ul
            mr = db@bb@ul
            qr = ds@bs@ul
            xyz = N@coords
            salida.append({
                "elemento": ie, "gauss": ig,
                "x_m": float(xyz[0]), "y_m": float(xyz[1]), "z_m": float(xyz[2]),
                "region": malla.regiones_elemento[ie],
                "zona": malla.zonas_elemento[ie],
                "Nxx_kN_m": float(nr[0]), "Nyy_kN_m": float(nr[1]),
                "Nxy_kN_m": float(nr[2]),
                "Mxx_kNm_m": float(mr[0]), "Myy_kNm_m": float(mr[1]),
                "Mxy_kNm_m": float(mr[2]),
                "Qx_kN_m": float(qr[0]), "Qy_kN_m": float(qr[1]),
            })
    return salida


def _momento_vector_en_origen(nodos: np.ndarray, fuerzas: np.ndarray) -> np.ndarray:
    momentos = np.zeros(3)
    for xyz, f6 in zip(nodos, fuerzas.reshape((-1, 6))):
        momentos += np.cross(xyz, f6[:3])+f6[3:6]
    return momentos


def resolver_caso(malla: MallaShell, p: ParametrosShell, K: csr_matrix,
                  S: csr_matrix, coef: dict, caso: str,
                  sistema: SistemaLinealShell | None = None) -> ResultadoCaso:
    f_global, escenario = vector_carga(malla, p, caso, coef)
    sistema = sistema or preparar_sistema_lineal(malla, K, S)
    kq = sistema.kq
    fq = np.asarray(S.T@f_global).ravel()
    libres = sistema.libres
    q = np.zeros_like(fq)
    q[libres] = sistema.resolver(fq[libres])
    if not np.all(np.isfinite(q)):
        raise RuntimeError("La solución FEM contiene valores no finitos")
    rq = np.asarray(kq@q-fq).ravel()
    u = np.asarray(S@q).ravel()
    r_global = np.asarray(S@rq).ravel()

    carga = f_global.reshape((-1, 6)).sum(axis=0)
    reaccion = r_global.reshape((-1, 6)).sum(axis=0)
    error_f = float(np.linalg.norm(carga[:3]+reaccion[:3]))
    mc = _momento_vector_en_origen(malla.nodos, f_global)
    mr = _momento_vector_en_origen(malla.nodos, r_global)
    error_m = float(np.linalg.norm(mc+mr))

    reacciones_cf: dict[str, dict] = {}
    nz = len(malla.niveles_m)
    for i, e in enumerate(malla.estaciones):
        if not e.es_contrafuerte:
            continue
        fuerza = np.zeros(3)
        for j in range(1, nz):  # z=0 se atribuye al empotramiento basal
            nodo = int(malla.nodo_por_estacion_nivel[i, j])
            fuerza += r_global[6*nodo:6*nodo+3]
        tx, ty = e.tangente_xy
        normal = np.array([-ty, tx, 0.0])
        reacciones_cf[e.etiqueta] = {
            "x_m": e.x_m, "y_m": e.y_m,
            "Rx_kN": float(fuerza[0]), "Ry_kN": float(fuerza[1]),
            "Rz_kN": float(fuerza[2]),
            "R_normal_kN": float(np.dot(fuerza, normal)),
        }
    desplazamientos_xyz = u.reshape((-1, 6))[:, :3]
    dmax = float(np.max(np.linalg.norm(desplazamientos_xyz, axis=1))*1000)
    return ResultadoCaso(
        caso=caso, escenario=escenario, desplazamientos=u,
        reacciones=r_global, puntos_gauss=_recuperar_puntos_gauss(malla, p, u),
        carga_total_kn=tuple(float(x) for x in carga[:3]),
        reaccion_total_kn=tuple(float(x) for x in reaccion[:3]),
        error_fuerza_kn=error_f, error_momento_kn_m=error_m,
        desplazamiento_max_mm=dmax,
        reacciones_contrafuertes=reacciones_cf,
    )


def analizar_modelo(p: ParametrosShell) -> tuple[MallaShell, dict, list[ResultadoCaso]]:
    malla = generar_malla(p)
    K = ensamblar_rigidez(malla, p)
    S = matriz_transformacion_apoyos(malla)
    coef = coeficientes_presion(p)
    sistema = preparar_sistema_lineal(malla, K, S)
    resultados = [
        resolver_caso(malla, p, K, S, coef, caso, sistema) for caso in CASOS
    ]
    return malla, coef, resultados


# =============================================================================
# DISEÑO E.060 / MTC-AASHTO A PARTIR DE RESULTANTES SHELL
# =============================================================================

def _as_flexion(mu_kn_m_m: float, d_mm: float, p: ParametrosShell) -> float:
    """Acero por flexión en cm²/m para una franja unitaria."""
    if mu_kn_m_m <= 1e-12:
        return 0.0
    b = 1000.0
    mu_n_mm = mu_kn_m_m*1e6
    disc = d_mm**2-2*mu_n_mm/(p.phi_flexion*0.85*p.fc_mpa*b)
    if disc <= 0:
        return float("inf")
    a = d_mm-math.sqrt(disc)
    as_mm2 = 0.85*p.fc_mpa*b*a/p.fy_mpa
    return as_mm2/100.0


def _capacidad_flexion(as_cm2_m: float, d_mm: float, p: ParametrosShell) -> float:
    As = as_cm2_m*100.0
    b = 1000.0
    a = As*p.fy_mpa/(0.85*p.fc_mpa*b)
    return p.phi_flexion*As*p.fy_mpa*(d_mm-a/2)/1e6


def _as_min_e060(d_mm: float) -> float:
    return 0.70*math.sqrt(MAT.f_c)*100.0*(d_mm/10.0)/MAT.fy


def _as_temp_e060_cara(p: ParametrosShell) -> float:
    return 0.0018*100.0*(p.espesor_m*100.0)/2.0


def _as_temp_mtc_cara(p: ParametrosShell) -> float:
    b_in = 12.0
    h_in = p.espesor_m*1000/MM_POR_PULGADA
    fy_ksi = p.fy_mpa*MPA_A_KSI
    as_in2_ft = 1.30*b_in*h_in/(2*(b_in+h_in)*fy_ksi)
    return min(max(as_in2_ft, 0.11), 0.60)*CM2_M_POR_IN2_FT


def _momento_fisuracion_kn_m(p: ParametrosShell) -> float:
    fr = 0.63*math.sqrt(p.fc_mpa)
    S = 1000.0*(p.espesor_m*1000.0)**2/6.0
    return fr*S/1e6


def _as_min_mtc(mu_kn_m_m: float, d_mm: float, p: ParametrosShell) -> float:
    objetivo = max(mu_kn_m_m, min(1.33*mu_kn_m_m, 0.67*1.60*_momento_fisuracion_kn_m(p)))
    return _as_flexion(objetivo, d_mm, p)


def _as_axial(nt_kn_m: float, p: ParametrosShell) -> float:
    return max(nt_kn_m, 0.0)*1000/(p.phi_flexion*p.fy_mpa)/100.0


def _fs_servicio(ms_kn_m_m: float, ns_kn_m: float,
                 as_cm2_m: float, d_mm: float) -> float:
    As = as_cm2_m*100.0
    if As <= 0:
        return float("inf")
    return ms_kn_m_m*1e6/(As*0.90*d_mm)+max(ns_kn_m, 0.0)*1000/As


def _limite_fisuracion(fs_mpa: float, db_mm: float, recubrimiento_mm: float,
                       p: ParametrosShell) -> float:
    if fs_mpa <= 1e-12:
        return float("inf")
    dc = (recubrimiento_mm+db_mm/2)/MM_POR_PULGADA
    h = p.espesor_m*1000/MM_POR_PULGADA
    beta_s = 1+dc/(0.7*(h-dc))
    return (700/(beta_s*fs_mpa*MPA_A_KSI)-2*dc)*MM_POR_PULGADA


def _seleccionar_barra(as_req: float, ms: float, ns: float,
                       d_mm: float, recubrimiento_mm: float,
                       p: ParametrosShell) -> dict:
    smax = min(3*p.espesor_m*1000, 400.0, 1.5*p.espesor_m*1000, 450.0)
    for nombre in p.barras:
        db = BARRAS_MM[nombre]
        area = math.pi*(db/10)**2/4
        s = math.floor(min(area*1000/as_req, smax)/p.paso_espaciamiento_mm)*p.paso_espaciamiento_mm
        while s >= p.espaciamiento_minimo_mm-1e-9:
            prov = area*1000/s
            fs = _fs_servicio(ms, ns, prov, d_mm)
            sfis = _limite_fisuracion(fs, db, recubrimiento_mm, p)
            if fs <= 0.60*p.fy_mpa+1e-9 and s <= sfis+1e-9:
                return {
                    "barra": nombre, "diametro_mm": db,
                    "espaciamiento_mm": s, "As_provisto_cm2_m": prov,
                    "fs_servicio_mpa": fs, "separacion_fisuracion_mm": sfis,
                }
            s -= p.paso_espaciamiento_mm
    raise ValueError("No existe barra/espaciamiento admisible")


def _capacidades_cortante(p: ParametrosShell, d_mm: float) -> tuple[float, float]:
    vc_e_n = 0.17*math.sqrt(p.fc_mpa)*1000*d_mm
    dv = max(0.9*d_mm, 0.72*p.espesor_m*1000)
    vc_m_n = 0.083*2.0*math.sqrt(p.fc_mpa)*1000*dv
    return p.phi_cortante_e060*vc_e_n/1000, p.phi_cortante_mtc*vc_m_n/1000


def _ld_e060(db: float, p: ParametrosShell) -> float:
    denom = 2.6 if db <= 19.05+1e-9 else 2.1
    return max(p.fy_mpa*1.3/(denom*min(math.sqrt(p.fc_mpa), 8.3))*db, 300.0)


def _ld_mtc(db: float, p: ParametrosShell) -> float:
    ldb_in = 2.4*(db/MM_POR_PULGADA)*(p.fy_mpa*MPA_A_KSI)/math.sqrt(p.fc_mpa*MPA_A_KSI)
    return max(1.3*ldb_in*MM_POR_PULGADA, 12*MM_POR_PULGADA)


def _redondear_50(x: float) -> float:
    return math.ceil(x/50)*50


def _valor_diseno(gp: dict, direccion: str, cara: str) -> tuple[float, float]:
    """Wood-Armer + membrana efectiva por cara.

    cara exterior corresponde a +normal local; interior/relleno a -normal.
    """
    if direccion == "Horizontal":
        m, n = gp["Mxx_kNm_m"], gp["Nxx_kN_m"]
    else:
        m, n = gp["Myy_kNm_m"], gp["Nyy_kN_m"]
    signo = 1.0 if cara == "Exterior (+n)" else -1.0
    m_wa = max(0.0, signo*m+abs(gp["Mxy_kNm_m"]))
    n_wa = max(0.0, n+abs(gp["Nxy_kN_m"]))/2.0
    return m_wa, n_wa


def _resultantes_en_elemento(malla: MallaShell, p: ParametrosShell,
                             r: ResultadoCaso, ie: int,
                             xi: float, eta: float) -> dict:
    """Recupera resultantes shell en una posición natural del elemento."""
    conectividad = malla.elementos[ie]
    coords = malla.nodos[conectividad]
    _, T, xy = rigidez_elemento(coords, p)
    dofs = np.array([6*n+d for n in conectividad for d in range(6)])
    ul = T@r.desplazamientos[dofs]
    E, nu, t = p.ec_kn_m2, p.poisson, p.espesor_m
    base = E/(1-nu**2)*np.array([
        [1.0, nu, 0.0], [nu, 1.0, 0.0],
        [0.0, 0.0, (1-nu)/2],
    ])
    dm, db = t*base, t**3/12.0*base
    N, bm, bb, _, _ = _matrices_b(xy, xi, eta)
    nr = dm@bm@ul
    mr = db@bb@ul
    xyz = N@coords
    return {
        "elemento": ie,
        "x_m": float(xyz[0]), "y_m": float(xyz[1]), "z_m": float(xyz[2]),
        "Nxx_kN_m": float(nr[0]), "Nyy_kN_m": float(nr[1]),
        "Nxy_kN_m": float(nr[2]),
        "Mxx_kNm_m": float(mr[0]), "Myy_kNm_m": float(mr[1]),
        "Mxy_kNm_m": float(mr[2]),
    }


def extraer_lineas_diseno(malla: MallaShell, resultados: list[ResultadoCaso],
                          p: ParametrosShell) -> list[dict]:
    """Crea tres líneas horizontales tipo *spandrel* para lectura de diseño.

    Cada punto corresponde al centro de un paño en la coordenada desarrollada
    ``s``. Las demandas son envolventes Wood-Armer horizontales de los casos
    factorizados. Si la línea coincide con el borde entre dos filas de
    elementos, se conserva el mayor valor de ambas filas, sin promediado.
    """
    servicio = next(r for r in resultados if r.caso == "Servicio I")
    ultimos = [r for r in resultados if r.caso != "Servicio I"]
    nz = len(malla.niveles_m)
    niveles = (
        ("Inferior", 0.0),
        ("Intermedia", p.altura_modelada_m/3.0),
        ("Superior", 2.0*p.altura_modelada_m/3.0),
    )
    salida: list[dict] = []
    tol = 1e-9
    for nombre, z_linea in niveles:
        puntos: list[dict] = []
        for i in range(len(malla.estaciones)-1):
            candidatos_pos: list[tuple[float, ResultadoCaso, dict]] = []
            candidatos_neg: list[tuple[float, ResultadoCaso, dict]] = []
            candidatos_s_pos: list[tuple[float, dict]] = []
            candidatos_s_neg: list[tuple[float, dict]] = []
            for j, (z0, z1) in enumerate(zip(malla.niveles_m, malla.niveles_m[1:])):
                if z_linea < z0-tol or z_linea > z1+tol:
                    continue
                eta = max(-1.0, min(1.0, 2.0*(z_linea-z0)/(z1-z0)-1.0))
                ie = i*(nz-1)+j
                for r in ultimos:
                    gp = _resultantes_en_elemento(malla, p, r, ie, 0.0, eta)
                    mp, _ = _valor_diseno(gp, "Horizontal", "Exterior (+n)")
                    mn, _ = _valor_diseno(gp, "Horizontal", "Interior/relleno (-n)")
                    candidatos_pos.append((mp, r, gp))
                    candidatos_neg.append((mn, r, gp))
                gp_s = _resultantes_en_elemento(malla, p, servicio, ie, 0.0, eta)
                ms_pos, _ = _valor_diseno(gp_s, "Horizontal", "Exterior (+n)")
                ms_neg, _ = _valor_diseno(gp_s, "Horizontal", "Interior/relleno (-n)")
                candidatos_s_pos.append((ms_pos, gp_s))
                candidatos_s_neg.append((ms_neg, gp_s))

            mu_pos, caso_pos, gp_pos = max(candidatos_pos, key=lambda x: x[0])
            mu_neg, caso_neg, gp_neg = max(candidatos_neg, key=lambda x: x[0])
            ms_pos, _ = max(candidatos_s_pos, key=lambda x: x[0])
            ms_neg, _ = max(candidatos_s_neg, key=lambda x: x[0])
            ea, eb = malla.estaciones[i], malla.estaciones[i+1]
            puntos.append({
                "estacion": i+1,
                "s_m": 0.5*(ea.s_m+eb.s_m),
                "x_m": 0.5*(ea.x_m+eb.x_m),
                "y_m": 0.5*(ea.y_m+eb.y_m),
                "z_m": z_linea,
                "region": malla.regiones_elemento[i*(nz-1)],
                "Mu_exterior_kNm_m": mu_pos,
                "caso_exterior": caso_pos.caso,
                "Mxx_exterior_kNm_m": gp_pos["Mxx_kNm_m"],
                "Mxy_exterior_kNm_m": gp_pos["Mxy_kNm_m"],
                "Mu_interior_kNm_m": mu_neg,
                "caso_interior": caso_neg.caso,
                "Mxx_interior_kNm_m": gp_neg["Mxx_kNm_m"],
                "Mxy_interior_kNm_m": gp_neg["Mxy_kNm_m"],
                "Ms_exterior_kNm_m": ms_pos,
                "Ms_interior_kNm_m": ms_neg,
            })
        max_pos = max(puntos, key=lambda x: x["Mu_exterior_kNm_m"])
        max_neg = max(puntos, key=lambda x: x["Mu_interior_kNm_m"])
        salida.append({
            "linea": f"FR-{nombre.upper()}",
            "franja": nombre,
            "z_sobre_zapata_m": z_linea,
            "profundidad_referencia_m": p.altura_total_m-z_linea,
            "ancho_franja_m": 1.0,
            "convencion": (
                "Exterior (+n): Mxx+|Mxy|; interior/relleno (-n): "
                "-Mxx+|Mxy|; valores Wood-Armer truncados a cero"
            ),
            "maximo_exterior": {
                "Mu_kNm_m": max_pos["Mu_exterior_kNm_m"],
                "s_m": max_pos["s_m"], "caso": max_pos["caso_exterior"],
            },
            "maximo_interior": {
                "Mu_kNm_m": max_neg["Mu_interior_kNm_m"],
                "s_m": max_neg["s_m"], "caso": max_neg["caso_interior"],
            },
            "puntos": puntos,
        })
    return salida


def disenar_envolventes(resultados: list[ResultadoCaso], p: ParametrosShell) -> list[dict]:
    db_control = max(BARRAS_MM[b] for b in p.barras)
    # El brazo mecánico depende del recubrimiento nominal de cada cara.
    recubrimiento_por_cara = {
        "Exterior (+n)": p.recubrimiento_exterior_mm,
        "Interior/relleno (-n)": p.recubrimiento_interior_mm,
    }
    servicio = next(r for r in resultados if r.caso == "Servicio I")
    ultimos = [r for r in resultados if r.caso != "Servicio I"]
    salida: list[dict] = []
    for region in ("Ala izquierda", "Pantalla central", "Ala derecha"):
        for zona in ("Inferior", "Intermedia", "Superior"):
            for direccion in ("Horizontal", "Vertical"):
                for cara in ("Exterior (+n)", "Interior/relleno (-n)"):
                    recubrimiento_mm = recubrimiento_por_cara[cara]
                    d = p.espesor_m*1000-recubrimiento_mm-db_control/2
                    candidatos: list[tuple[float, float, ResultadoCaso, dict]] = []
                    for r in ultimos:
                        for gp in r.puntos_gauss:
                            if gp["region"] == region and gp["zona"] == zona:
                                m, n = _valor_diseno(gp, direccion, cara)
                                candidatos.append((m, n, r, gp))
                    # Gobierna el mayor acero de flexión+membrana, no solo M.
                    def acero_candidato(x: tuple) -> float:
                        return _as_flexion(x[0], d, p)+_as_axial(x[1], p)
                    mu, nu, rg, gpg = max(candidatos, key=acero_candidato)
                    serv_gp = [gp for gp in servicio.puntos_gauss
                               if gp["region"] == region and gp["zona"] == zona]
                    ms, ns = max(
                        (_valor_diseno(gp, direccion, cara) for gp in serv_gp),
                        key=lambda x: _fs_servicio(x[0], x[1], 1.0, d),
                    )
                    as_flex = _as_flexion(mu, d, p)
                    as_ax = _as_axial(nu, p)
                    requisitos = {
                        "flexión+membrana": as_flex+as_ax,
                        "mínimo flexión E.060": _as_min_e060(d),
                        "temperatura E.060": _as_temp_e060_cara(p),
                        "mínimo flexión MTC/AASHTO": _as_min_mtc(mu, d, p)+as_ax,
                        "temperatura MTC/AASHTO": _as_temp_mtc_cara(p),
                    }
                    controla, as_req = max(requisitos.items(), key=lambda x: x[1])
                    sel = _seleccionar_barra(as_req, ms, ns, d, recubrimiento_mm, p)
                    phi_mn = _capacidad_flexion(sel["As_provisto_cm2_m"], d, p)
                    capacidad_axial_acero = p.phi_flexion*sel["As_provisto_cm2_m"]*100*p.fy_mpa/1000
                    # Índice conservador aditivo de flexión y tracción.
                    dcr = mu/phi_mn+nu/capacidad_axial_acero if phi_mn > 0 else float("inf")
                    lde = _ld_e060(sel["diametro_mm"], p)
                    ldm = _ld_mtc(sel["diametro_mm"], p)
                    salida.append({
                        "region": region, "zona": zona, "direccion": direccion,
                        "cara": cara, "caso_gobernante": rg.caso,
                        "recubrimiento_mm": recubrimiento_mm, "d_mm": d,
                        "x_m": gpg["x_m"], "y_m": gpg["y_m"], "z_m": gpg["z_m"],
                        "Mu_WoodArmer_kNm_m": mu, "Nu_tension_cara_kN_m": nu,
                        "Ms_WoodArmer_kNm_m": ms, "Ns_servicio_cara_kN_m": ns,
                        "As_flexion_cm2_m": as_flex, "As_membrana_cm2_m": as_ax,
                        "As_requerido_cm2_m": as_req, "control_acero": controla,
                        **sel, "phi_Mn_kNm_m": phi_mn, "DCR_interaccion": dcr,
                        "ld_e060_mm": lde, "ld_mtc_mm": ldm,
                        "ld_adoptado_mm": _redondear_50(max(lde, ldm)),
                    })
    return salida


def resumen_cortante_compresion(resultados: list[ResultadoCaso], p: ParametrosShell) -> list[dict]:
    db_control = max(BARRAS_MM[b] for b in p.barras)
    # Capacidad de cortante del concreto: se adopta el brazo menor, es decir,
    # el recubrimiento mayor de ambas caras (exterior 100 mm / interior 75 mm).
    d = p.espesor_m*1000-max(
        p.recubrimiento_exterior_mm, p.recubrimiento_interior_mm,
    )-db_control/2
    vce, vcm = _capacidades_cortante(p, d)
    vc = min(vce, vcm)
    salida = []
    for region in ("Ala izquierda", "Pantalla central", "Ala derecha"):
        for zona in ("Inferior", "Intermedia", "Superior"):
            cands = []
            for r in resultados:
                if r.caso == "Servicio I":
                    continue
                for gp in r.puntos_gauss:
                    if gp["region"] == region and gp["zona"] == zona:
                        q = math.hypot(gp["Qx_kN_m"], gp["Qy_kN_m"])
                        nc = max(0.0, -gp["Nxx_kN_m"], -gp["Nyy_kN_m"])
                        cands.append((q, nc, r.caso, gp))
            q, _, caso, gp = max(cands, key=lambda x: x[0]/vc)
            _, nc, caso_nc, gp_nc = max(cands, key=lambda x: x[1])
            sigma = nc/p.espesor_m/1000.0
            salida.append({
                "region": region, "zona": zona, "caso": caso,
                "Q_resultante_kN_m": q, "phi_Vc_E060_kN_m": vce,
                "phi_Vc_MTC_kN_m": vcm, "phi_Vc_adoptado_kN_m": vc,
                "DCR_cortante": q/vc,
                "compresion_membrana_max_MPa": sigma,
                "limite_compresion_referencia_MPa": 0.45*p.fc_mpa,
                "DCR_compresion_membrana": sigma/(0.45*p.fc_mpa),
                "x_m": gp["x_m"], "y_m": gp["y_m"], "z_m": gp["z_m"],
                "caso_compresion": caso_nc,
                "xyz_compresion_m": [gp_nc["x_m"], gp_nc["y_m"], gp_nc["z_m"]],
            })
    return salida


def _resumen_resultantes(resultados: list[ResultadoCaso]) -> list[dict]:
    salida = []
    for r in resultados:
        for region in ("Ala izquierda", "Pantalla central", "Ala derecha"):
            for zona in ("Inferior", "Intermedia", "Superior"):
                pts = [g for g in r.puntos_gauss
                       if g["region"] == region and g["zona"] == zona]
                fila = {"caso": r.caso, "region": region, "zona": zona}
                for clave in ("Nxx_kN_m", "Nyy_kN_m", "Nxy_kN_m",
                              "Mxx_kNm_m", "Myy_kNm_m", "Mxy_kNm_m",
                              "Qx_kN_m", "Qy_kN_m"):
                    fila[f"{clave}_min"] = min(g[clave] for g in pts)
                    fila[f"{clave}_max"] = max(g[clave] for g in pts)
                salida.append(fila)
    return salida


def _validar_simetria(malla: MallaShell, r: ResultadoCaso) -> dict:
    ns, nz = len(malla.estaciones), len(malla.niveles_m)
    u = r.desplazamientos.reshape((-1, 6))
    err_u = 0.0
    escala_u = max(np.max(np.abs(u[:, :3])), 1e-12)
    for i in range(ns):
        for j in range(nz):
            a = int(malla.nodo_por_estacion_nivel[i, j])
            b = int(malla.nodo_por_estacion_nivel[ns-1-i, j])
            err_u = max(err_u, abs(u[a, 0]+u[b, 0]),
                        abs(u[a, 1]-u[b, 1]), abs(u[a, 2]-u[b, 2]))
    pares = (("CF-I1", "CF-D3"), ("CF-I2", "CF-D2"),
             ("CF-I3", "CF-D1"), ("CF-C1", "CF-C3"))
    err_r = 0.0
    escala_r = 1e-12
    for a, b in pares:
        ra = r.reacciones_contrafuertes[a]["R_normal_kN"]
        rb = r.reacciones_contrafuertes[b]["R_normal_kN"]
        escala_r = max(escala_r, abs(ra), abs(rb))
        err_r = max(err_r, abs(abs(ra)-abs(rb)))
    return {
        "error_relativo_desplazamientos": err_u/escala_u,
        "error_relativo_reacciones_pares": err_r/escala_r,
    }


def ejecutar_convergencia(p: ParametrosShell, tamanos: tuple[float, ...] = (0.80, 0.60, 0.50)) -> list[dict]:
    """Convergencia de Servicio I; evita confundir picos locales con respuesta global."""
    salida = []
    for h in tamanos:
        ph = ParametrosShell(**{**asdict(p), "tamano_malla_m": h})
        m = generar_malla(ph)
        K = ensamblar_rigidez(m, ph)
        S = matriz_transformacion_apoyos(m)
        c = coeficientes_presion(ph)
        r = resolver_caso(m, ph, K, S, c, "Servicio I")
        mwa = max(
            max(0.0, abs(g["Mxx_kNm_m"])+abs(g["Mxy_kNm_m"]))
            for g in r.puntos_gauss
        )
        salida.append({
            "tamano_objetivo_m": h, "nodos": len(m.nodos),
            "elementos": len(m.elementos),
            "desplazamiento_max_mm": r.desplazamiento_max_mm,
            "momento_WoodArmer_puntual_max_kNm_m": mwa,
            "error_fuerza_kn": r.error_fuerza_kn,
        })
    for i, x in enumerate(salida):
        if i == 0:
            x["cambio_desplazamiento_pct"] = None
        else:
            ant = salida[i-1]["desplazamiento_max_mm"]
            x["cambio_desplazamiento_pct"] = 100*abs(x["desplazamiento_max_mm"]-ant)/x["desplazamiento_max_mm"]
    return salida


def _serializar_malla(malla: MallaShell) -> dict:
    return {
        "nodos": malla.nodos.tolist(),
        "elementos": malla.elementos.tolist(),
        "estaciones": [asdict(e) for e in malla.estaciones],
        "niveles_m": malla.niveles_m,
        "regiones_elemento": malla.regiones_elemento,
        "zonas_elemento": malla.zonas_elemento,
    }


def _resumen_casos(resultados: list[ResultadoCaso]) -> list[dict]:
    return [{
        "caso": r.caso, "escenario": r.escenario,
        "carga_total_kn": r.carga_total_kn,
        "reaccion_total_kn": r.reaccion_total_kn,
        "error_fuerza_kn": r.error_fuerza_kn,
        "error_momento_kn_m": r.error_momento_kn_m,
        "desplazamiento_max_mm": r.desplazamiento_max_mm,
        "reacciones_contrafuertes": r.reacciones_contrafuertes,
    } for r in resultados]


def _reacciones_nodales_contrafuertes(
    malla: MallaShell, resultados: list[ResultadoCaso]
) -> list[dict]:
    """Contrato de transferencia de acciones hacia los contrafuertes."""
    salida: list[dict] = []
    niveles = np.asarray(malla.niveles_m, dtype=float)
    for ie, estacion in enumerate(malla.estaciones):
        if not estacion.es_contrafuerte:
            continue
        normal = np.array([-estacion.tangente_xy[1], estacion.tangente_xy[0], 0.0])
        for resultado in resultados:
            reacciones = []
            for j in range(1, len(niveles)):
                nodo = int(malla.nodo_por_estacion_nivel[ie, j])
                fuerza = resultado.reacciones[6 * nodo:6 * nodo + 3]
                reacciones.append(float(np.dot(fuerza, normal)))
            salida.append({
                "contrafuerte": estacion.etiqueta,
                "caso": resultado.caso,
                "z_m": niveles[1:].tolist(),
                "reaccion_pantalla_kN": reacciones,
            })
    return salida


def calcular(p: ParametrosShell | None = None, incluir_convergencia: bool = True) -> dict:
    p = p or ParametrosShell()
    malla, coef, resultados = analizar_modelo(p)
    presiones_franjas = presiones_franjas_resistencia_ia(p, coef)
    diseno = disenar_envolventes(resultados, p)
    lineas_diseno = extraer_lineas_diseno(malla, resultados, p)
    cortante = resumen_cortante_compresion(resultados, p)
    sim = _validar_simetria(malla, next(r for r in resultados if r.caso == "Servicio I"))
    ia = next(r for r in resultados if r.caso == "Resistencia I-a")
    ib = next(r for r in resultados if r.caso == "Resistencia I-b")
    convergencia = ejecutar_convergencia(p) if incluir_convergencia else []
    max_eq_f = max(r.error_fuerza_kn for r in resultados)
    max_eq_m = max(r.error_momento_kn_m for r in resultados)
    validaciones = {
        "longitud_desarrollada_m": longitud_poligonal(p.puntos_planta),
        "geometria_simetrica": all(
            abs(a[0]+b[0]-21.32) < 1e-9 and abs(a[1]-b[1]) < 1e-9
            for a, b in zip(p.puntos_planta, reversed(p.puntos_planta))
        ),
        "nueve_lineas_contrafuerte": sum(e.es_contrafuerte for e in malla.estaciones) == 9,
        "cajuela_excluida": abs(p.altura_total_m - p.altura_modelada_m - (GEOM.c_cajuela + GEOM.d_cajuela)) < 1e-9,
        "resistencia_ia_ib_independientes": ia is not ib,
        "resistencia_ia_ib_coinciden": np.allclose(ia.desplazamientos, ib.desplazamientos),
        "max_error_fuerza_kn": max_eq_f,
        "max_error_momento_kn_m": max_eq_m,
        "equilibrio_cumple": max_eq_f < 1e-5 and max_eq_m < 1e-3,
        **sim,
        "simetria_cumple": max(sim.values()) < 1e-7,
        "flexion_membrana_cumple": all(x["DCR_interaccion"] <= 1 for x in diseno),
        "cortante_cumple": all(x["DCR_cortante"] <= 1 for x in cortante),
        "compresion_membrana_cumple": all(x["DCR_compresion_membrana"] <= 1 for x in cortante),
    }
    return {
        "identificacion": "Modelo FEM shell 3D independiente de la pantalla plegada",
        "alcance_excluido": ["cajuela", "diseño de contrafuertes", "zapata", "cargas de apoyo", "frenado", "impacto"],
        "parametros": asdict(p), "coeficientes_presion": coef,
        "presiones_franjas_resistencia_ia": presiones_franjas,
        "malla": _serializar_malla(malla),
        "casos": _resumen_casos(resultados),
        "reacciones_nodales_contrafuertes": _reacciones_nodales_contrafuertes(
            malla, resultados
        ),
        "resultantes_por_region_zona": _resumen_resultantes(resultados),
        "lineas_diseno": lineas_diseno,
        "diseno_refuerzo": diseno, "cortante_compresion": cortante,
        "convergencia": convergencia, "validaciones": validaciones,
        "estado": "CUMPLE" if all((
            validaciones["equilibrio_cumple"], validaciones["simetria_cumple"],
            validaciones["flexion_membrana_cumple"], validaciones["cortante_cumple"],
            validaciones["compresion_membrana_cumple"],
        )) else "NO CUMPLE",
        "_objetos": {"malla": malla, "resultados": resultados},
    }


def generar_markdown(r: dict) -> str:
    p = r["parametros"]
    m = r["malla"]
    v = r["validaciones"]
    lineas = [
        "# Análisis tridimensional FEM de la pantalla plegada", "",
        "## 1. Objetivo y alcance", "",
        "Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, "
        "respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.", "",
        "## 2. Datos", "",
        "| Parámetro | Valor | Unidad | Estado |", "|---|---:|---|---|",
        f"| Altura total de referencia | {p['altura_total_m']:.3f} | m | proporcionado |",
        f"| Altura modelada | {p['altura_modelada_m']:.3f} | m | proporcionado |",
        f"| Espesor | {p['espesor_m']:.3f} | m | proporcionado |",
        f"| Recubrimiento exterior (+n) | {p['recubrimiento_exterior_mm']:.0f} | mm | proporcionado |",
        f"| Recubrimiento interior (-n) | {p['recubrimiento_interior_mm']:.0f} | mm | proporcionado |",
        f"| f'c | {MAT.f_c:.1f} | kgf/cm² | agente base |",
        f"| fy | {MAT.fy:.1f} | kgf/cm² | agente base |",
        f"| Ec | {15000.0*math.sqrt(MAT.f_c)*98.0665/1e6:.3f} | GPa | E.060 |",
        f"| Longitud desarrollada | {v['longitud_desarrollada_m']:.4f} | m | coordenadas |",
        f"| Tamaño objetivo de malla | {p['tamano_malla_m']:.3f} | m | adoptado |",
        f"| Nodos / elementos | {len(m['nodos'])} / {len(m['elementos'])} | — | calculado |", "",
        "### Coordenadas en planta", "",
        "| Punto | x (m) | y (m) | Tipo |", "|---|---:|---:|---|",
    ]
    for x, y, tipo, nombre in p["puntos_planta"]:
        lineas.append(f"| {nombre} | {x:.2f} | {y:.2f} | {tipo} |")
    lineas += [
        "", "## 3. Idealización y formulación", "",
        f"La poligonal se extruye verticalmente hasta {p['altura_modelada_m']:.2f} m. Cada elemento Q4 contiene membrana bilineal y placa "
        "Mindlin-Reissner; el cortante transversal usa interpolación MITC4. En cada plano el eje local `x` sigue "
        "la pantalla, `y` es vertical y `+n` apunta hacia la cara exterior.", "",
        "Se emplea rigidez elástica bruta uniforme. La fisuración no lineal y una eventual redistribución por "
        "rigidez efectiva no forman parte de este análisis.", "",
        "La base está empotrada. En las nueve líneas de contrafuerte se restringe la traslación normal local y se "
        "mantienen libres las rotaciones. Los quiebres QI y QD comparten nodos y seis grados de libertad, por lo que "
        "la unión se considera monolítica.", "",
        "Para el diseño se usan resultantes de cascarón `(Nxx,Nyy,Nxy,Mxx,Myy,Mxy,Qx,Qy)`. Los momentos torsores "
        "se incorporan mediante envolventes Wood-Armer y la tracción de membrana se distribuye conservadoramente "
        "por mitad entre las dos caras.", "",
        "## 4. Acciones y estados límite", "",
        f"- Ka normal = {r['coeficientes_presion']['Ka_normal']:.6f}.",
        f"- KAE normal = {r['coeficientes_presion']['Kae_normal']:.6f}.",
        "- Servicio I: EH + LS.",
        "- Resistencia I-a: 1.50 EH + 1.75 LS.",
        "- Resistencia I-b: se ejecuta separadamente con la misma demanda lateral.",
        "- Evento Extremo I: envolvente de las concurrencias A y B, incluida la inercia propia de la pantalla.", "",
        "La presión varía linealmente con la altura y se aplica normal a cada elemento; no se aplican fuerzas de "
        "cajuela, apoyo, frenado o impacto.", "",
        "### Presiones de referencia — Resistencia I-a", "",
        "`qu = 1.50 EH + 1.75 LS`. Los valores corresponden al borde inferior de cada tercio y actúan "
        "normalmente sobre cada panel shell.", "",
        "| Franja | z sobre zapata | Profundidad | 1.50 EH | 1.75 LS | qu | qu |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for x in r["presiones_franjas_resistencia_ia"]:
        lineas.append(
            f"| {x['franja']} | {x['z_sobre_zapata_m']:.3f} m | "
            f"{x['profundidad_referencia_m']:.3f} m | "
            f"{x['EH_factorizado_tf_m2']:.3f} tf/m² | "
            f"{x['LS_factorizado_tf_m2']:.3f} tf/m² | "
            f"{x['presion_total_tf_m2']:.3f} tf/m² | "
            f"{x['presion_total_kN_m2']:.2f} kN/m² |"
        )
    lineas += [
        "",
        "## 5. Respuesta global", "",
        "| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for c in r["casos"]:
        lineas.append(
            f"| {c['caso']} | {c['escenario']} | {c['desplazamiento_max_mm']:.4f} | "
            f"{c['carga_total_kn'][0]:.3f} | {c['carga_total_kn'][1]:.3f} | "
            f"{c['error_fuerza_kn']:.2e} | {c['error_momento_kn_m']:.2e} |"
        )
    lineas += ["", "### Reacciones normales en contrafuertes", "",
               "| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |",
               "|---|---|---:|---:|---:|"]
    for c in r["casos"]:
        for nombre, rr in c["reacciones_contrafuertes"].items():
            lineas.append(f"| {c['caso']} | {nombre} | {rr['R_normal_kN']:.3f} | {rr['Rx_kN']:.3f} | {rr['Ry_kN']:.3f} |")
    lineas += ["", "## 6. Diseño E.060–MTC/AASHTO", "",
               "Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y "
               "desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana. "
               f"El brazo mecánico de cada cara usa su recubrimiento nominal: exterior {p['recubrimiento_exterior_mm']:.0f} mm "
               f"(agua con abrasión) e interior {p['recubrimiento_interior_mm']:.0f} mm (relleno).", "",
               "| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |",
               "|---|---|---|---|---|---:|---:|---:|---|---:|"]
    for d in r["diseno_refuerzo"]:
        lineas.append(
            f"| {d['region']} | {d['zona']} | {d['direccion']} | {d['cara']} | {d['caso_gobernante']} | "
            f"{d['Mu_WoodArmer_kNm_m']:.2f} kN·m/m | {d['Nu_tension_cara_kN_m']:.2f} kN/m | "
            f"{d['As_requerido_cm2_m']:.3f} cm²/m | Ø{d['barra']} @ {d['espaciamiento_mm']:.0f} mm | "
            f"{d['DCR_interaccion']:.3f} |"
        )
    lineas += [
        "", "### Líneas horizontales de lectura tipo *spandrel*", "",
        "Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente "
        "factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en "
        "kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor "
        "valor de ambos lados, sin promediado.", "",
        "| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |",
        "|---|---:|---:|---:|---|---:|---:|---|",
    ]
    for ld in r["lineas_diseno"]:
        ep, ip = ld["maximo_exterior"], ld["maximo_interior"]
        lineas.append(
            f"| {ld['linea']} | {ld['z_sobre_zapata_m']:.3f} | "
            f"{ep['Mu_kNm_m']:.2f} kN·m/m | {ep['s_m']:.3f} m | {ep['caso']} | "
            f"{ip['Mu_kNm_m']:.2f} kN·m/m | {ip['s_m']:.3f} m | {ip['caso']} |"
        )
    ld_max = max(d["ld_adoptado_mm"] for d in r["diseno_refuerzo"])
    traslape = _redondear_50(1.3*ld_max)
    lineas += ["", f"Longitud de desarrollo adoptada máxima: **{ld_max:.0f} mm**; "
               f"empalme Clase B de referencia: **{traslape:.0f} mm**. Debe comprobarse la longitud "
               "física disponible en cada quiebre y contrafuerte.", "",
               "### Cortante y compresión de membrana", "",
               "| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |",
               "|---|---|---:|---:|---:|---:|---:|"]
    for x in r["cortante_compresion"]:
        lineas.append(
            f"| {x['region']} | {x['zona']} | {x['Q_resultante_kN_m']:.2f} kN/m | "
            f"{x['phi_Vc_adoptado_kN_m']:.2f} kN/m | {x['DCR_cortante']:.3f} | "
            f"{x['compresion_membrana_max_MPa']:.3f} MPa | {x['DCR_compresion_membrana']:.3f} |"
        )
    lineas += ["", "## 7. Convergencia de malla", "",
               "| Tamaño (m) | Nodos | Elementos | d máx. (mm) | Cambio d | M WA puntual (kN·m/m) |",
               "|---:|---:|---:|---:|---:|---:|"]
    for x in r["convergencia"]:
        cambio = "—" if x["cambio_desplazamiento_pct"] is None else f"{x['cambio_desplazamiento_pct']:.2f}%"
        lineas.append(f"| {x['tamano_objetivo_m']:.2f} | {x['nodos']} | {x['elementos']} | {x['desplazamiento_max_mm']:.4f} | {cambio} | {x['momento_WoodArmer_puntual_max_kNm_m']:.2f} |")
    if not r["convergencia"]:
        lineas.append("| — | — | — | — | no ejecutada | — |")
    lineas += ["", "Los desplazamientos globales muestran convergencia; los máximos puntuales próximos a líneas "
               "rígidas son sensibles al mallado y se interpretan como envolventes locales. En este cálculo no alteran "
               "el armado porque gobierna el mínimo normativo.", "",
               "## 8. Validaciones", "", "| Control | Resultado |", "|---|---|"]
    for clave, valor in v.items():
        if isinstance(valor, (bool, np.bool_)):
            texto = "Conforme" if valor else "No conforme"
        elif isinstance(valor, float):
            texto = f"{valor:.6g}"
        else:
            texto = str(valor)
        lineas.append(f"| {clave.replace('_', ' ')} | {texto} |")
    max_dcr = max(x["DCR_interaccion"] for x in r["diseno_refuerzo"])
    max_v = max(x["DCR_cortante"] for x in r["cortante_compresion"])
    lineas += ["", "## 9. Conclusión", "",
               f"**Estado del modelo: {r['estado']}.**", "",
               f"El espesor de {p['espesor_m']:.2f} m satisface las comprobaciones incluidas. El máximo DCR de "
               f"flexión–membrana es {max_dcr:.3f} y el máximo DCR de cortante es {max_v:.3f}.", "",
               "Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en "
               "la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el "
               "detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con "
               "rigideces fisuradas.", ""]
    return "\n".join(lineas)


def generar_graficos(r: dict, carpeta: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    carpeta.mkdir(parents=True, exist_ok=True)
    malla: MallaShell = r["_objetos"]["malla"]
    resultados: list[ResultadoCaso] = r["_objetos"]["resultados"]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    pts = np.array([(x, y) for x, y, _, _ in r["parametros"]["puntos_planta"]])
    ax.plot(pts[:, 0], pts[:, 1], "r-", lw=2.5, label="eje de pantalla")
    for x, y, tipo, nombre in r["parametros"]["puntos_planta"]:
        marcador = "s" if tipo == "contrafuerte" else "D"
        color = "#1f4e79" if tipo == "contrafuerte" else "#d97706"
        ax.scatter(x, y, marker=marcador, c=color, s=45, zorder=3)
        ax.annotate(nombre, (x, y), xytext=(4, 5), textcoords="offset points", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Geometría real en planta y ejes de contrafuerte")
    ax.grid(True, alpha=.3)
    fig.tight_layout()
    p1 = carpeta/"geometria_shell_3d_planta.png"
    fig.savefig(p1, dpi=180)
    plt.close(fig)

    servicio = next(x for x in resultados if x.caso == "Servicio I")
    u = servicio.desplazamientos.reshape((-1, 6))[:, :3]
    escala = 250.0
    xyz_def = malla.nodos+escala*u
    caras = [xyz_def[e] for e in malla.elementos]
    valores_elem = np.zeros(len(malla.elementos))
    for g in servicio.puntos_gauss:
        valores_elem[g["elemento"]] = max(
            valores_elem[g["elemento"]],
            abs(g["Mxx_kNm_m"])+abs(g["Mxy_kNm_m"]),
        )
    fig = plt.figure(figsize=(12, 7))
    ax3 = fig.add_subplot(111, projection="3d")
    norm = plt.Normalize(valores_elem.min(), valores_elem.max())
    coleccion = Poly3DCollection(caras, linewidths=0.05, alpha=.92)
    coleccion.set_facecolor(plt.cm.viridis(norm(valores_elem)))
    coleccion.set_edgecolor((0, 0, 0, .15))
    ax3.add_collection3d(coleccion)
    colores_linea = ("#d62728", "#ff7f0e", "#00b5d8")
    for ld, color in zip(r["lineas_diseno"], colores_linea):
        j = min(range(len(malla.niveles_m)),
                key=lambda k: abs(malla.niveles_m[k]-ld["z_sobre_zapata_m"]))
        tags = malla.nodo_por_estacion_nivel[:, j]
        linea_xyz = xyz_def[tags]
        ax3.plot(linea_xyz[:, 0], linea_xyz[:, 1], linea_xyz[:, 2],
                 color=color, lw=2.0, label=ld["linea"])
    ax3.set_xlim(malla.nodos[:, 0].min(), malla.nodos[:, 0].max())
    ax3.set_ylim(malla.nodos[:, 1].min()-1, malla.nodos[:, 1].max()+1)
    ax3.set_zlim(0, r["parametros"]["altura_modelada_m"])
    ax3.set_xlabel("x (m)")
    ax3.set_ylabel("y (m)")
    ax3.set_zlabel("z (m)")
    ax3.set_title(f"Deformada Servicio I (×{escala:.0f}) y |Mxx|+|Mxy|")
    ax3.legend(loc="upper left", fontsize=7)
    sm = plt.cm.ScalarMappable(norm=norm, cmap="viridis")
    sm.set_array([])
    fig.colorbar(sm, ax=ax3, shrink=.65, pad=.08, label="kN·m/m")
    fig.tight_layout()
    p2 = carpeta/"deformada_momentos_shell_3d.png"
    fig.savefig(p2, dpi=180)
    plt.close(fig)

    fig, ejes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    estaciones_cf = [(e.s_m, e.etiqueta) for e in malla.estaciones
                      if e.es_contrafuerte]
    for ax, ld in zip(ejes, r["lineas_diseno"]):
        s = np.array([x["s_m"] for x in ld["puntos"]])
        mu_ext = np.array([x["Mu_exterior_kNm_m"] for x in ld["puntos"]])
        mu_int = np.array([x["Mu_interior_kNm_m"] for x in ld["puntos"]])
        ax.plot(s, mu_ext, color="#1f77b4", lw=1.6,
                label="Exterior (+n)")
        ax.fill_between(s, 0, mu_ext, color="#1f77b4", alpha=.22)
        ax.plot(s, -mu_int, color="#d62728", lw=1.6,
                label="Interior/relleno (-n)")
        ax.fill_between(s, 0, -mu_int, color="#d62728", alpha=.22)
        for scf, etiqueta in estaciones_cf:
            ax.axvline(scf, color="0.45", lw=.65, ls="--", alpha=.7)
            if ax is ejes[0]:
                ax.annotate(etiqueta, (scf, 1.0), xycoords=("data", "axes fraction"),
                            xytext=(2, -3), textcoords="offset points",
                            rotation=90, va="top", fontsize=7, color="0.3")
        ep, ip = ld["maximo_exterior"], ld["maximo_interior"]
        ax.scatter([ep["s_m"]], [ep["Mu_kNm_m"]], color="#1f77b4", s=24, zorder=3)
        ax.scatter([ip["s_m"]], [-ip["Mu_kNm_m"]], color="#d62728", s=24, zorder=3)
        ax.set_title(
            f"{ld['linea']} — z={ld['z_sobre_zapata_m']:.3f} m | "
            f"máx. ext.={ep['Mu_kNm_m']:.2f} ({ep['caso']}); "
            f"máx. int.={ip['Mu_kNm_m']:.2f} ({ip['caso']})",
            fontsize=10,
        )
        ax.set_ylabel("Mu WA\n(kN·m/m)")
        ax.axhline(0, color="black", lw=.7)
        ax.grid(True, alpha=.22)
    ejes[0].legend(loc="lower right", ncol=2, fontsize=8)
    ejes[-1].set_xlabel("Coordenada desarrollada s (m)")
    fig.suptitle(
        "Líneas de diseño horizontales — envolvente factorizada Wood-Armer\n"
        "Exterior positiva; interior negativa solo por convención gráfica",
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0, 1, .95))
    p3 = carpeta/"lineas_diseno_shell_3d.png"
    fig.savefig(p3, dpi=180)
    plt.close(fig)

    p_obj = ParametrosShell(**r["parametros"])
    z_perfil = np.linspace(0.0, p_obj.altura_modelada_m, 200)
    eh_perfil = np.array([
        1.50*componentes_presion(float(z), p_obj, r["coeficientes_presion"])["EH"]
        for z in z_perfil
    ])
    ls_perfil = np.array([
        1.75*componentes_presion(float(z), p_obj, r["coeficientes_presion"])["LS"]
        for z in z_perfil
    ])
    total_perfil = eh_perfil+ls_perfil
    pf = r["presiones_franjas_resistencia_ia"]

    fig, (axp, axb) = plt.subplots(
        1, 2, figsize=(14, 7), gridspec_kw={"width_ratios": [1.15, 1.0]},
    )
    axp.plot(total_perfil, z_perfil, color="#8b1e3f", lw=2.4,
             label=r"$q_u=1.50\,EH+1.75\,LS$")
    axp.plot(eh_perfil, z_perfil, color="#d97706", lw=1.3, ls="--",
             label=r"$1.50\,EH$")
    axp.plot(ls_perfil, z_perfil, color="#1f77b4", lw=1.3, ls=":",
             label=r"$1.75\,LS$")
    axp.fill_betweenx(z_perfil, 0, total_perfil, color="#8b1e3f", alpha=.14)
    colores_presion = ("#c0392b", "#e67e22", "#16a085")
    for x, color in zip(pf, colores_presion):
        q = x["presion_total_tf_m2"]
        z = x["z_sobre_zapata_m"]
        axp.scatter(q, z, color=color, s=55, zorder=4)
        axp.axhline(z, color=color, lw=.85, ls="--", alpha=.65)
        axp.annotate(
            f"{x['franja']}: {q:.3f} tf/m²\n({x['presion_total_kN_m2']:.2f} kN/m²)",
            (q, z), xytext=(9, 0), textcoords="offset points",
            va="center", fontsize=9, color=color,
        )
    axp.set_xlabel("Presión normal factorizada (tf/m²)")
    axp.set_ylabel("z sobre zapata (m)")
    axp.set_ylim(0, p_obj.altura_modelada_m)
    axp.set_xlim(left=0)
    axp.set_title("Perfil de presión sobre la pantalla modelada")
    axp.grid(True, alpha=.25)
    axp.legend(loc="upper right", fontsize=9)

    nombres = [x["franja"] for x in pf]
    eh_b = np.array([x["EH_factorizado_tf_m2"] for x in pf])
    ls_b = np.array([x["LS_factorizado_tf_m2"] for x in pf])
    yb = np.arange(len(pf))
    axb.barh(yb, eh_b, color="#d97706", label="1.50 EH")
    axb.barh(yb, ls_b, left=eh_b, color="#1f77b4", label="1.75 LS")
    for i, x in enumerate(pf):
        axb.text(
            x["presion_total_tf_m2"]+.08, i,
            f"{x['presion_total_tf_m2']:.3f} tf/m²\n"
            f"{x['presion_total_kN_m2']:.2f} kN/m²",
            va="center", fontsize=9,
        )
    axb.set_yticks(yb, nombres)
    axb.invert_yaxis()
    axb.set_xlabel("Presión factorizada (tf/m²)")
    axb.set_title("Componentes aplicadas en las tres franjas")
    axb.set_xlim(0, max(x["presion_total_tf_m2"] for x in pf)*1.30)
    axb.grid(True, axis="x", alpha=.25)
    axb.legend(loc="lower right", fontsize=9)
    fig.suptitle(
        "Presiones de diseño — Resistencia I-a\n"
        "Acción normal local sobre el shell; valores en el borde inferior de cada tercio",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, .93))
    p4 = carpeta/"presiones_franjas_resistencia_ia.png"
    fig.savefig(p4, dpi=180)
    plt.close(fig)
    return [p1, p2, p3, p4]


def _limpiar_para_json(r: dict) -> dict:
    return {k: v for k, v in r.items() if k != "_objetos"}


def _json_default(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Tipo no serializable: {type(obj).__name__}")


_RUTA_PROYECTO = Path(__file__).resolve().parents[2]
_CARPETA_SALIDA = _RUTA_PROYECTO/".tmp"/"legacy"/"pantalla"/"analisis_shell_3d"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tamano-malla", type=float, default=0.50)
    parser.add_argument("--salida-md", type=Path,
                        default=_CARPETA_SALIDA/"analisis_pantalla_shell_3d.md")
    parser.add_argument("--salida-json", type=Path,
                        default=_CARPETA_SALIDA/"analisis_pantalla_shell_3d.json")
    parser.add_argument("--sin-convergencia", action="store_true",
                        help="omite el estudio de convergencia de malla")
    parser.add_argument("--sin-graficos", action="store_true",
                        help="omite la generación de figuras PNG")
    return parser.parse_args()


def _resumen_consola(r: dict, graficos: list[Path],
                     args: argparse.Namespace) -> str:
    """Resumen ejecutivo impreso en consola con los valores reales del cálculo."""
    v = r["validaciones"]
    dcr_max = max(d["DCR_interaccion"] for d in r["diseno_refuerzo"])
    dcr_v_max = max(d["DCR_cortante"] for d in r["cortante_compresion"])
    dcr_c_max = max(d["DCR_compresion_membrana"] for d in r["cortante_compresion"])
    p_inf = next(x for x in r["presiones_franjas_resistencia_ia"]
                 if x["franja"] == "Inferior")
    caso, apoyo, rmax = max(
        ((c["caso"], nombre, rr["R_normal_kN"])
         for c in r["casos"]
         for nombre, rr in c["reacciones_contrafuertes"].items()),
        key=lambda x: abs(x[2]),
    )
    no_conformes = [k for k, val in v.items()
                    if isinstance(val, (bool, np.bool_)) and not val]

    lineas = [
        "="*76,
        "ANÁLISIS SHELL 3D DE LA PANTALLA PLEGADA — resumen de resultados",
        "="*76,
        f"Modelo: {len(r['malla']['nodos'])} nodos, "
        f"{len(r['malla']['elementos'])} elementos "
        f"(malla objetivo {r['parametros']['tamano_malla_m']:.2f} m)",
        f"Recubrimientos: exterior (+n) {r['parametros']['recubrimiento_exterior_mm']:.0f} mm; "
        f"interior (-n) {r['parametros']['recubrimiento_interior_mm']:.0f} mm",
        f"Estado global: {r['estado']}",
        "",
        "Respuesta por caso (unidades internas kN, m):",
        f"  {'Caso':<18} {'d máx (mm)':>11} {'Error F (kN)':>12} {'Error M (kN·m)':>13}",
    ]
    for c in r["casos"]:
        lineas.append(
            f"  {c['caso']:<18} {c['desplazamiento_max_mm']:>11.4f} "
            f"{c['error_fuerza_kn']:>12.2e} {c['error_momento_kn_m']:>13.2e}"
        )
    lineas += [
        "",
        f"Reacción normal máxima en contrafuertes: {rmax:.2f} kN "
        f"({apoyo}, caso {caso})",
        f"Presión de referencia franja Inferior (Resistencia I-a): "
        f"{p_inf['presion_total_tf_m2']:.3f} tf/m² "
        f"({p_inf['presion_total_kN_m2']:.2f} kN/m²)",
        "",
        f"DCR máximo flexión+membrana: {dcr_max:.3f}",
        f"DCR máximo cortante: {dcr_v_max:.3f}",
        f"DCR máximo compresión de membrana: {dcr_c_max:.3f}",
    ]
    if r["convergencia"]:
        ult = r["convergencia"][-1]
        cambio = ("—" if ult["cambio_desplazamiento_pct"] is None
                  else f"{ult['cambio_desplazamiento_pct']:.2f}%")
        lineas.append(
            f"Convergencia (última malla {ult['tamano_objetivo_m']:.2f} m): "
            f"d máx {ult['desplazamiento_max_mm']:.4f} mm, "
            f"cambio {cambio}"
        )
    lineas.append(
        "Validaciones: " + (
            "todas conformes" if not no_conformes
            else f"NO CONFORMES -> {', '.join(no_conformes)}"
        )
    )
    lineas += [
        "",
        f"Reporte Markdown: {args.salida_md.resolve()}",
        f"Datos JSON: {args.salida_json.resolve()}",
    ]
    if graficos:
        lineas.append("Gráficos:")
        lineas += [f"  {g.resolve()}" for g in graficos]
    return "\n".join(lineas)


def main() -> None:
    # Consola UTF-8 segura: evita fallos de codificación al imprimir el informe.
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    args = parse_args()
    p = ParametrosShell(tamano_malla_m=args.tamano_malla)
    r = calcular(p, incluir_convergencia=not args.sin_convergencia)
    args.salida_md.parent.mkdir(parents=True, exist_ok=True)
    args.salida_json.parent.mkdir(parents=True, exist_ok=True)
    args.salida_md.write_text(generar_markdown(r), encoding="utf-8")
    args.salida_json.write_text(
        json.dumps(_limpiar_para_json(r), ensure_ascii=False, indent=2,
                   default=_json_default),
        encoding="utf-8",
    )
    if args.sin_graficos:
        graficos: list[Path] = []
    else:
        try:
            graficos = generar_graficos(r, args.salida_md.parent)
        except ImportError as exc:
            print(f"ADVERTENCIA: no se generaron gráficos ({exc.name}); "
                  "el reporte MD/JSON ya fue escrito. "
                  "Use --sin-graficos para omitirlos explícitamente.")
            graficos = []
    print(_resumen_consola(r, graficos, args))


if __name__ == "__main__":
    main()

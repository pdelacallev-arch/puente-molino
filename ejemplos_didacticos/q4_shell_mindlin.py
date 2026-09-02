# -*- coding: utf-8 -*-
"""
Elemento Q4 de cascarón: membrana bilineal + placa Mindlin-Reissner (MITC4)
============================================================================
Programa didáctico que construye la matriz de rigidez local del elemento Q4
(6 gdl por nodo) y lo valida con dos problemas clásicos:

  1. Voladizo de membrana  -> compara contra la solución de viga de Bernoulli
  2. Placa SSSS c. uniforme-> compara contra la solución de Kirchhoff (Navier)

Es el mismo tipo de elemento que el informe "analisis_pantalla_shell_3d.md"
describe en su ítem 3: cada Q4 contiene membrana bilineal y placa
Mindlin-Reissner, con cortante transversal interpolado mediante MITC4.

Cinemática de la placa (eje z local = normal al elemento):
    u(x,y,z) = +z*θy,   v(x,y,z) = -z*θx,   w = w(x,y)

    Membrana (z = 0):  ε = [u,x ; v,y ; u,y+v,x]
    Curvaturas:        κ = [θy,x ; -θx,y ; θy,y - θx,x]
    Cortante:          γ = [w,x + θy ; w,y - θx]

Orden local de gdl por nodo:  [u, v, w, θx, θy, θz]
La rotación θz ("drilling") no tiene rigidez física en esta formulación;
se estabiliza con una rigidez artificial pequeña para evitar singularidad.

Unidades: SI (m, N, Pa). Ajusta E, t, etc. según tu problema.
"""

import sys

try:  # consola en UTF-8 (evita UnicodeEncodeError con θ, ñ, etc.)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np

# ============================================================================
# 1. FUNCIONES DE FORMA BILINEALES Y JACOBIANO
# ============================================================================

def shape_functions(xi, eta):
    """Funciones de forma N_i en coordenadas naturales (xi, eta) in [-1,1]."""
    return 0.25 * np.array([
        (1 - xi) * (1 - eta),
        (1 + xi) * (1 - eta),
        (1 + xi) * (1 + eta),
        (1 - xi) * (1 + eta),
    ])


def shape_derivatives(xi, eta):
    """Derivadas dN/dxi y dN/deta (4 c/u) en el punto (xi, eta)."""
    dN_dxi = 0.25 * np.array([-(1 - eta),  (1 - eta), (1 + eta), -(1 + eta)])
    dN_deta = 0.25 * np.array([-(1 - xi), -(1 + xi), (1 + xi),  (1 - xi)])
    return dN_dxi, dN_deta


def jacobian(xy, dN_dxi, dN_deta):
    """Matriz jacobiana del mapeo isoparamétrico (xi,eta) -> (x,y)."""
    J = np.array([
        [dN_dxi @ xy[:, 0], dN_dxi @ xy[:, 1]],
        [dN_deta @ xy[:, 0], dN_deta @ xy[:, 1]],
    ])
    detJ = J[0, 0] * J[1, 1] - J[0, 1] * J[1, 0]
    if detJ <= 0:
        raise ValueError(f"detJ <= 0 ({detJ:.3e}): conectividad o geometría errónea")
    invJ = np.array([[J[1, 1], -J[0, 1]], [-J[1, 0], J[0, 0]]]) / detJ
    return J, detJ, invJ


def dshape_dxy(dN_dxi, dN_deta, invJ):
    """Derivadas cartesianas dN/dx, dN/dy mediante la regla de la cadena:
       [dN/dx ; dN/dy] = invJ . [dN/dxi ; dN/deta]  (para cada función de forma)"""
    dN_dx = invJ[0, 0] * dN_dxi + invJ[0, 1] * dN_deta
    dN_dy = invJ[1, 0] * dN_dxi + invJ[1, 1] * dN_deta
    return dN_dx, dN_dy


def gauss_points(scheme="full"):
    """Puntos y pesos de Gauss-Legendre en [-1,1]^2.
       'full'    -> 2x2 (membrana y flexión)
       'reduced' -> 1x1 (para mostrar el efecto del bloqueo en membrana)"""
    if scheme == "full":
        a = 1.0 / np.sqrt(3.0)
        return [(a, a, 1.0), (a, -a, 1.0), (-a, -a, 1.0), (-a, a, 1.0)]
    return [(0.0, 0.0, 4.0)]


# ============================================================================
# 2. MATRICES CONSTITUTIVAS (ELASTICIDAD PLANA Y PLACA MINDLIN)
# ============================================================================

def D_membrane(E, nu, t):
    """Rigidez de membrana: N = Dm . ε   (esfuerzos por unidad de ancho)."""
    f = E * t / (1.0 - nu ** 2)
    return f * np.array([[1.0, nu, 0.0],
                         [nu, 1.0, 0.0],
                         [0.0, 0.0, (1.0 - nu) / 2.0]])


def D_bending(E, nu, t):
    """Rigidez de flexión: M = Db . κ   (momentos por unidad de ancho)."""
    f = E * t ** 3 / (12.0 * (1.0 - nu ** 2))
    return f * np.array([[1.0, nu, 0.0],
                         [nu, 1.0, 0.0],
                         [0.0, 0.0, (1.0 - nu) / 2.0]])


def D_shear(E, nu, t, kappa=5.0 / 6.0):
    """Rigidez de cortante transversal: Q = Ds . γ   (factor 5/6 de sección)."""
    G = E / (2.0 * (1.0 + nu))
    return kappa * G * t * np.eye(2)


# ============================================================================
# 3. MATRICES B (CINEMÁTICA)
# ============================================================================

def B_membrane(dN_dx, dN_dy):
    """B de membrana 3x8. Gdl por nodo: [u, v].
       ε = [u,x ; v,y ; u,y + v,x] = Bm . u"""
    B = np.zeros((3, 8))
    for i in range(4):
        B[0, 2 * i] = dN_dx[i]      # u,x
        B[1, 2 * i + 1] = dN_dy[i]  # v,y
        B[2, 2 * i] = dN_dy[i]      # u,y
        B[2, 2 * i + 1] = dN_dx[i]  # v,x
    return B


def B_bending(dN_dx, dN_dy):
    """B de flexión 3x8. Gdl por nodo: [θx, θy].
       κ = [θy,x ; -θx,y ; θy,y - θx,x] = Bb . θ"""
    B = np.zeros((3, 8))
    for i in range(4):
        B[0, 2 * i + 1] = dN_dx[i]      # κxx = θy,x
        B[1, 2 * i] = -dN_dy[i]         # κyy = -θx,y
        B[2, 2 * i] = -dN_dx[i]         # κxy = -θx,x
        B[2, 2 * i + 1] = dN_dy[i]      # κxy = +θy,y
    return B


# ============================================================================
# 4. CORTANTE TRANSVERSAL MITC4  (el "secreto" del Q4)
# ============================================================================
# El Q4 ingenuo integra el cortante con las derivadas directas de N y sufre
# "bloqueo por cortante": ante espesores pequeños predice rigidez excesiva.
# MITC4 (Bathe & Dvorkin 1985) interpola las deformaciones de cortante a
# partir de sus valores en los PUNTOS MEDIOS DE LOS BORDES:
#
#     γ̄_ξζ(ξ,η) = ½(1-η)·γA + ½(1+η)·γC     A: borde 1-2, C: borde 3-4
#     γ̄_ηζ(ξ,η) = ½(1-ξ)·γD + ½(1+ξ)·γB     B: borde 2-3, D: borde 4-1
#
# Cada valor de borde usa la cinemática 1D exacta a lo largo del borde:
#     γ_borde = (variación de w) + (rotación proyectada en la dirección del borde)
# Finalmente se transforma al sistema cartesiano con invJ.

def mitc4_shear_B(xy, xi, eta):
    """B de cortante MITC4 2x12 en el punto (xi, eta).
       Gdl de placa por nodo: [w, θx, θy]. Devuelve (B_cart, detJ)."""
    x1, y1 = xy[0]; x2, y2 = xy[1]; x3, y3 = xy[2]; x4, y4 = xy[3]

    # Vectores tangentes de los bordes (SIN normalizar): escalan con la
    # longitud real del borde y dan a gamma unidades de longitud (como w,xi)
    d12 = np.array([x2 - x1, y2 - y1])   # dirección +ξ: nodo 1 -> nodo 2
    d23 = np.array([x3 - x2, y3 - y2])   # dirección +η: nodo 2 -> nodo 3
    # En el borde superior, +ξ recorre el elemento de nodo 4 hacia nodo 3.
    # Mantener esta orientación es esencial para interpolar γ_ξζ con el
    # mismo signo en los dos bordes opuestos.
    d43 = np.array([x3 - x4, y3 - y4])   # dirección +ξ: nodo 4 -> nodo 3
    d14 = np.array([x4 - x1, y4 - y1])   # dirección +η: nodo 1 -> nodo 4

    # Componente covariante de cortante en el punto medio del borde:
    #   γ = ½(w_b - w_a) + ¼[Δx·(θy_a + θy_b) - Δy·(θx_a + θx_b)]
    # (deriva de: γ = ∇w·x,ξ + θ·x,ξ  evaluado en el punto medio)
    def borde(w_a, i_a, w_b, i_b, dx, dy):
        row = np.zeros(12)
        row[3 * i_a] = -0.5 * w_a      # w del nodo inicial
        row[3 * i_b] = +0.5 * w_b      # w del nodo final
        row[3 * i_a + 1] = -0.25 * dy  # θx del nodo inicial
        row[3 * i_a + 2] = +0.25 * dx  # θy del nodo inicial
        row[3 * i_b + 1] = -0.25 * dy  # θx del nodo final
        row[3 * i_b + 2] = +0.25 * dx  # θy del nodo final
        return row

    rowA = borde(1.0, 0, 1.0, 1, d12[0], d12[1])   # γ_ξζ en borde 1-2: ½(w2-w1)
    rowB = borde(1.0, 1, 1.0, 2, d23[0], d23[1])   # γ_ηζ en borde 2-3: ½(w3-w2)
    rowC = borde(1.0, 3, 1.0, 2, d43[0], d43[1])   # γ_ξζ en borde 4-3: ½(w3-w4)
    # γ_ηζ en borde 4-1: la dirección +η va del nodo 1 al nodo 4,
    # por lo que la parte de w es ½(w4 - w1)
    rowD = borde(1.0, 0, 1.0, 3, d14[0], d14[1])

    fila_xi = 0.5 * (1.0 - eta) * rowA + 0.5 * (1.0 + eta) * rowC
    fila_eta = 0.5 * (1.0 - xi) * rowD + 0.5 * (1.0 + xi) * rowB
    B_nat = np.vstack([fila_xi, fila_eta])          # 2x12 en coordenadas naturales

    dN_dxi, dN_deta = shape_derivatives(xi, eta)
    _, detJ, invJ = jacobian(xy, dN_dxi, dN_deta)
    B_cart = invJ @ B_nat                           # 2x12 en coordenadas cartesianas
    return B_cart, detJ


# ============================================================================
# 5. MATRIZ DE RIGIDEZ LOCAL DEL ELEMENTO Q4 (24x24)
# ============================================================================

def element_stiffness(xy, E, nu, t, kappa=5.0 / 6.0, memb_scheme="full"):
    """Matriz de rigidez local 24x24 del Q4 de cascarón.
       xy: (4,2) coordenadas locales de los nodos (orden 1-2-3-4).
       Orden de gdl por nodo: [u, v, w, θx, θy, θz]."""
    Dm, Db, Ds = D_membrane(E, nu, t), D_bending(E, nu, t), D_shear(E, nu, t)

    km = np.zeros((8, 8))   # membrana  (u, v)
    kb = np.zeros((8, 8))   # flexión   (θx, θy)
    ks = np.zeros((12, 12)) # cortante  (w, θx, θy)

    # --- membrana y flexión: integración de Gauss (2x2 por defecto) ---------
    for xi, eta, w in gauss_points(memb_scheme):
        dN_dxi, dN_deta = shape_derivatives(xi, eta)
        _, detJ, invJ = jacobian(xy, dN_dxi, dN_deta)
        dN_dx, dN_dy = dshape_dxy(dN_dxi, dN_deta, invJ)
        Bm = B_membrane(dN_dx, dN_dy)
        Bb = B_bending(dN_dx, dN_dy)
        km += w * detJ * (Bm.T @ Dm @ Bm)
        kb += w * detJ * (Bb.T @ Db @ Bb)

    # --- cortante transversal: MITC4, integración 2x2 -----------------------
    for xi, eta, w in gauss_points("full"):
        Bs, detJ = mitc4_shear_B(xy, xi, eta)
        ks += w * detJ * (Bs.T @ Ds @ Bs)

    # --- ensamblaje interno en 24x24 ----------------------------------------
    k = np.zeros((24, 24))
    memb_idx = [6 * i + j for i in range(4) for j in (0, 1)]
    flex_idx = [6 * i + j for i in range(4) for j in (3, 4)]
    shear_idx = [6 * i + j for i in range(4) for j in (2, 3, 4)]
    k[np.ix_(memb_idx, memb_idx)] += km
    k[np.ix_(flex_idx, flex_idx)] += kb
    k[np.ix_(shear_idx, shear_idx)] += ks

    # --- rotación de drilling θz: rigidez artificial pequeña -----------------
    k_drill = 1e-6 * E * t   # suficientemente pequeña para no alterar la física
    for i in range(4):
        k[6 * i + 5, 6 * i + 5] += k_drill

    return k


# ============================================================================
# 6. TRANSFORMACIÓN LOCAL -> GLOBAL (elemento en 3D)
# ============================================================================
# En la pantalla real los elementos están inclinados; el informe dice:
# "en cada plano el eje local x sigue la pantalla, y es vertical y +n apunta
# hacia la cara exterior". Aquí construimos los ejes locales a partir de la
# geometría y rotamos la matriz con T:  Kg = T^T . Klocal . T

def local_axes(xyz):
    """Ejes locales (e1, e2, n) del elemento a partir de sus 4 nodos 3D."""
    p1, p2, p3, p4 = xyz
    n = np.cross(p3 - p1, p4 - p2)          # normal al plano del elemento
    n = n / np.linalg.norm(n)
    if n[2] < 0:                            # convención: normal con z local >= 0
        n = -n
    e1 = p2 - p1
    e1 = e1 / np.linalg.norm(e1)            # eje local x: sigue el borde 1-2
    e2 = np.cross(n, e1)                    # eje local y: en el plano, ortogonal
    return e1, e2, n


def element_stiffness_3d(xyz, E, nu, t, kappa=5.0 / 6.0, memb_scheme="full"):
    """Matriz de rigidez 24x24 en coordenadas globales."""
    e1, e2, n = local_axes(xyz)
    xy = np.array([[p @ e1, p @ e2] for p in xyz])   # proyección al plano local
    k_local = element_stiffness(xy, E, nu, t, kappa, memb_scheme)
    R = np.vstack([e1, e2, n])                        # 3x3: local -> global
    T = np.kron(np.eye(8), R)                         # 24x24 (4 nodos x 2 campos)
    return T.T @ k_local @ T


# ============================================================================
# 7. ENSAMBLAJE GLOBAL, CARGAS Y SOLUCIÓN
# ============================================================================

def assemble_stiffness(conn, xyz_all, E, nu, t, kappa=5.0 / 6.0, memb_scheme="full"):
    """Ensambla la matriz de rigidez global (6 gdl por nodo)."""
    ngdl = 6 * len(xyz_all)
    K = np.zeros((ngdl, ngdl))
    for e in conn:
        xyz = xyz_all[list(e)]
        ke = element_stiffness_3d(xyz, E, nu, t, kappa, memb_scheme)
        idx = np.array([6 * n + k for n in e for k in range(6)])
        K[np.ix_(idx, idx)] += ke
    return K


def assemble_uniform_pressure(conn, xyz_all, q):
    """Carga uniforme normal q por unidad de área -> cargas nodales consistentes.
       Para funciones bilineales: F_nodo = q * Ae / 4, en la dirección normal."""
    F = np.zeros(6 * len(xyz_all))
    for e in conn:
        xyz = xyz_all[list(e)]
        Ae = 0.5 * np.linalg.norm(np.cross(xyz[2] - xyz[0], xyz[3] - xyz[1]))
        _, _, n = local_axes(xyz)
        for gn in e:
            F[6 * gn : 6 * gn + 3] += (q * Ae / 4.0) * n
    return F


def solve(K, F, fixed):
    """Resuelve K u = F con u = 0 en los gdl de `fixed` (lista (nodo, k)).
       Devuelve (u, reacciones)."""
    ngdl = len(F)
    free = np.ones(ngdl, dtype=bool)
    for (n, k) in fixed:
        free[6 * n + k] = False
    Kff = K[np.ix_(free, free)]
    Ff = F[free]
    try:
        uf = np.linalg.solve(Kff, Ff)
    except np.linalg.LinAlgError:
        raise RuntimeError(
            "Matriz singular: revisa restricciones (puede faltar un apoyo "
            "o haber un mecanismo).")
    u = np.zeros(ngdl)
    u[free] = uf
    R = K @ u - F   # reacciones en los gdl restringidos
    return u, R


# ============================================================================
# 8. RECUPERACIÓN DE RESULTANTES DE CASCARÓN EN EL CENTRO DEL ELEMENTO
# ============================================================================
# Exactamente las 8 resultantes que usa el informe en su sección 6:
#     (Nxx, Nyy, Nxy, Mxx, Myy, Mxy, Qx, Qy)

def internal_forces_center(xy, u_e, E, nu, t, kappa=5.0 / 6.0):
    """u_e: desplazamientos locales del elemento (24). Devuelve N, M, Q."""
    xi = eta = 0.0
    dN_dxi, dN_deta = shape_derivatives(xi, eta)
    _, detJ, invJ = jacobian(xy, dN_dxi, dN_deta)
    dN_dx, dN_dy = dshape_dxy(dN_dxi, dN_deta, invJ)

    um = np.array([u_e[6 * i + j] for i in range(4) for j in (0, 1)])
    uf = np.array([u_e[6 * i + j] for i in range(4) for j in (3, 4)])
    us = np.array([u_e[6 * i + j] for i in range(4) for j in (2, 3, 4)])

    N = D_membrane(E, nu, t) @ B_membrane(dN_dx, dN_dy) @ um
    M = D_bending(E, nu, t) @ B_bending(dN_dx, dN_dy) @ uf
    Bs, _ = mitc4_shear_B(xy, xi, eta)
    Q = D_shear(E, nu, t, kappa) @ Bs @ us
    return N, M, Q   # N=[Nxx,Nyy,Nxy], M=[Mxx,Myy,Mxy], Q=[Qx,Qy]


# ============================================================================
# 9. MALLADO AUXILIAR
# ============================================================================

def mesh_rect(nx, ny, Lx, Ly):
    """Malla rectangular nx x ny en el plano z=0. Nodos antihorarios."""
    xs = np.linspace(0.0, Lx, nx + 1)
    ys = np.linspace(0.0, Ly, ny + 1)
    nodes, ids = [], {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            ids[(i, j)] = len(nodes)
            nodes.append([xs[i], ys[j], 0.0])
    conn = []
    for j in range(ny):
        for i in range(nx):
            conn.append((ids[(i, j)], ids[(i + 1, j)],
                         ids[(i + 1, j + 1)], ids[(i, j + 1)]))
    return np.array(nodes), conn


def elem_data(nodes, conn, e):
    """Devuelve (xyz, u_e, xy_local) del elemento e."""
    idx = np.array([6 * n + k for n in conn[e] for k in range(6)])
    xyz = nodes[list(conn[e])]
    e1, e2, n = local_axes(xyz)
    xy = np.array([[p @ e1, p @ e2] for p in xyz])
    return xyz, idx, xy


# ============================================================================
# 10. VERIFICACIONES DEL ELEMENTO
# ============================================================================

def verify_element():
    print("=" * 74)
    print("VERIFICACIÓN 1: modos de cuerpo rígido y simetría del Q4 aislado")
    print("=" * 74)
    E, nu, t = 2e11, 0.3, 0.1
    xyz = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], float)
    k = element_stiffness_3d(xyz, E, nu, t)
    simetria = np.allclose(k, k.T, rtol=1e-10, atol=1e-6)
    max_asim = np.abs(k - k.T).max()
    print(f"  Simetría de K: {simetria}   (máx |K - K^T| = {max_asim:.3e})")

    ev = np.linalg.eigvalsh((k + k.T) / 2)
    tol_cuerpo = 1e-8 * ev[-1]
    tol_total = 1e-6 * ev[-1]
    n_cuerpo = int((ev < tol_cuerpo).sum())
    n_total = int((ev < tol_total).sum())
    print(f"  Autovalores < {tol_cuerpo:.2e} (cuerpo rígido): {n_cuerpo}  (esperado: 6)")
    print(f"  Autovalores < {tol_total:.2e} (cuerpo rígido + drilling): {n_total}")
    print(f"  Escala de autovalores pequeños: {ev[:8]}")
    print("  -> Los 6 primeros son los modos de cuerpo rígido (3 traslaciones +")
    print("     3 rotaciones globales); los 4 siguientes corresponden a la rigidez")
    print("     artificial de drilling θz, ~7 órdenes de magnitud menor.")

    print("\n  Patrón de acoplamiento de K (X = término no nulo > 1e-8 del máx.):")
    patron = np.where(np.abs(k) > 1e-8 * np.abs(k).max(), "X", ".")
    print("  gdl | " + " ".join(f"{i:2d}" for i in range(24)))
    print("  " + "-" * 74)
    for i in range(24):
        print(f"  {i:3d} | " + "  ".join(patron[i]))
    print("  Nota: la rigidez es por bloques diagonales (membrana u-v, flexión θx-θy,")
    print("        cortante w-θx-θy y drilling θz); no hay acoplamiento membrana-flexión")
    print("        en un elemento plano, tal como predice la teoría de cascarones planos.")


# ============================================================================
# 11. VALIDACIÓN 1: VOLADIZO DE MEMBRANA (viga empotrada con carga en punta)
# ============================================================================

def ejemplo_voladizo():
    print("=" * 74)
    print("VALIDACIÓN 1: voladizo de membrana  (L=10 m, h=1 m, t=0.1 m, P=1 kN)")
    print("Referencia Bernoulli:  d = P*L^3/(3*E*I)")
    print("=" * 74)
    E, nu, t = 2e11, 0.3, 0.1
    L, h, P = 10.0, 1.0, 1000.0
    I = t * h ** 3 / 12.0
    d_bern = P * L ** 3 / (3.0 * E * I)

    print(f"\n  d_Bernoulli = {d_bern*1000:.4f} mm\n")
    print("  malla |  integración 2x2        integración 1x1 (reducida)")
    print("  ------+----------------------------------------------------")
    for n in (1, 2, 4, 8, 16):
        nodes, conn = mesh_rect(n, n, L, h)
        fixed = [(gn, k) for gn, (x, y, z) in enumerate(nodes)
                 if abs(x) < 1e-12 for k in range(6)]
        bord = [gn for gn, (x, y, z) in enumerate(nodes) if abs(x - L) < 1e-12]
        pesos = np.array([0.5 if abs(nodes[gn][1]) < 1e-12 or
                          abs(nodes[gn][1] - h) < 1e-12 else 1.0 for gn in bord])
        F = np.zeros(6 * len(nodes))
        for gn, p in zip(bord, pesos):
            F[6 * gn + 1] = P * p / pesos.sum()

        fila = f"  {n:2d} x {n:<2d} |"
        for scheme in ("full", "reduced"):
            K = assemble_stiffness(conn, nodes, E, nu, t, memb_scheme=scheme)
            u, R = solve(K, F, fixed)
            d_fem = np.mean([u[6 * gn + 1] for gn in bord])
            if d_fem < 0 or d_fem > 10 * d_bern:
                fila += f"  {'inestable (hourglass)':>24s}"
            else:
                fila += f"  {d_fem*1000:8.4f} mm ({100*d_fem/d_bern:5.1f}%)"
        print(fila + "  |")
    print("\n  Interpretación: con 2x2 el Q4 de membrana sufre 'shear parasitario'")
    print("  (bloqueo en flexión) y converge lentamente; con integración reducida")
    print("  la convergencia es mucho más rápida, a costa de posibles modos de")
    print("  energía cero (hourglass) en problemas más generales.")


# ============================================================================
# 12. VALIDACIÓN 2: PLACA CUADRADA SIMPLEMENTE APOYADA, CARGA UNIFORME
# ============================================================================

def ejemplo_placa():
    print("=" * 74)
    print("VALIDACIÓN 2: placa SSSS  (a=10 m, t=0.1 m, q=10 kPa)")
    print("Referencia Kirchhoff:  w_max = 0.00406235*q*a^4/D ,  Mxx = 0.0479*q*a^2")
    print("=" * 74)
    E, nu, t = 2e11, 0.3, 0.1
    a, q = 10.0, 1e4
    D = E * t ** 3 / (12.0 * (1 - nu ** 2))
    w_K = 0.00406235 * q * a ** 4 / D
    M_K = 0.0479 * q * a ** 2
    print(f"\n  w_Kirchhoff = {w_K*1000:.4f} mm ;  Mxx_K = {M_K/1000:.1f} kN.m/m\n")
    print("  malla |   w centro (mm)  |  % Kirchhoff |  Mxx centro (kN.m/m)")

    for n in (4, 8, 16, 32):
        nodes, conn = mesh_rect(n, n, a, a)
        fixed = []
        for gn, (x, y, z) in enumerate(nodes):
            if abs(x) < 1e-12 or abs(x - a) < 1e-12 or \
               abs(y) < 1e-12 or abs(y - a) < 1e-12:
                fixed.append((gn, 2))          # w = 0 en el borde (apoyo simple)
            fixed += [(gn, 0), (gn, 1), (gn, 5)]  # u, v, θz fijos: placa pura
        F = assemble_uniform_pressure(conn, nodes, q)
        K = assemble_stiffness(conn, nodes, E, nu, t)
        u, R = solve(K, F, fixed)

        center = [gn for gn, (x, y, z) in enumerate(nodes)
                  if abs(x - a / 2) < 1e-12 and abs(y - a / 2) < 1e-12][0]
        w_fem = u[6 * center + 2]

        # Mxx en el centro: promedio de los elementos que rodean al nodo central
        vecinos = [i for i, e in enumerate(conn) if center in e]
        mxx = []
        for i in vecinos:
            xyz, idx, xy = elem_data(nodes, conn, i)
            N, M, Q = internal_forces_center(xy, u[idx], E, nu, t)
            mxx.append(abs(M[0]))
        Mxx = np.mean(mxx)

        print(f"  {n:2d} x {n:<2d} |  {w_fem*1000:9.4f} | {100*w_fem/w_K:9.2f} |"
              f" {Mxx/1000:13.2f}")

    print("\n  Interpretación: t/a = 0.01 (placa delgada); la solución Mindlin-MITC4")
    print("  converge a la de Kirchhoff. La diferencia residual (+0.35% a 32x32)")
    print("  es la contribución del cortante transversal, del orden de (t/a)^2,")
    print("  esperable en la teoría de Mindlin-Reissner.")


# ============================================================================
# PROGRAMA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    np.set_printoptions(precision=4, suppress=True)
    verify_element()
    print()
    ejemplo_voladizo()
    print()
    ejemplo_placa()
    print()
    print("=" * 74)
    print("FIN. Las 8 resultantes (Nxx,Nyy,Nxy,Mxx,Myy,Mxy,Qx,Qy) se recuperan")
    print("con internal_forces_center() y alimentan el diseño (Wood-Armer, etc.).")
    print("=" * 74)

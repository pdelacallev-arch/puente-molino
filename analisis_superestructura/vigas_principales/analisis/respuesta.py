"""Respuesta de viga simple para cargas permanentes y deflexión por curvaturas."""

from __future__ import annotations

import numpy as np


def respuesta_distribuida(x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
    """M y V para w(x) usando integración; w en N/mm, x en mm."""
    L = float(x[-1])
    total = float(np.trapezoid(w, x))
    momento_carga = float(np.trapezoid(w * x, x))
    r2 = momento_carga / L
    r1 = total - r2
    acumulada_w = np.zeros_like(x)
    acumulada_wx = np.zeros_like(x)
    dx = np.diff(x)
    acumulada_w[1:] = np.cumsum((w[:-1] + w[1:]) * dx / 2.0)
    acumulada_wx[1:] = np.cumsum((w[:-1] * x[:-1] + w[1:] * x[1:]) * dx / 2.0)
    v = r1 - acumulada_w
    m = r1 * x - x * acumulada_w + acumulada_wx
    return m, v, r1, r2


def deformada_desde_momento(
    x: np.ndarray, momento: np.ndarray, e_mpa: float, inercia: np.ndarray
) -> np.ndarray:
    """Integra kappa=M/EI imponiendo y(0)=y(L)=0."""
    if np.any(inercia <= 0.0):
        raise ValueError("todas las inercias deben ser positivas")
    kappa = momento / (e_mpa * inercia)
    L = float(x[-1])
    theta0 = -float(np.trapezoid((L - x) * kappa, x)) / L
    int_k = np.zeros_like(x)
    int_xk = np.zeros_like(x)
    dx = np.diff(x)
    int_k[1:] = np.cumsum((kappa[:-1] + kappa[1:]) * dx / 2.0)
    int_xk[1:] = np.cumsum((x[:-1] * kappa[:-1] + x[1:] * kappa[1:]) * dx / 2.0)
    return theta0 * x + x * int_k - int_xk


def valor_segmentado(x: np.ndarray, segmentos: tuple, valores: list[float]) -> np.ndarray:
    salida = np.empty_like(x, dtype=float)
    for i, (segmento, valor) in enumerate(zip(segmentos, valores)):
        inicio = segmento.x_inicio * 1000.0
        fin = segmento.x_fin * 1000.0
        mascara = (x >= inicio) & (x <= fin if i == len(segmentos) - 1 else x < fin)
        salida[mascara] = valor
    return salida

"""Conversion explicita de MKS tecnico a SI de ingenieria."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

TF_A_KN = 9.80665
KGF_CM2_A_MPA = 0.0980665


def normalizar_a_si(datos: dict[str, Any]) -> dict[str, Any]:
    """Convierte un documento MKS a m-kN-MPa sin aceptar mezclas implicitas."""
    salida = deepcopy(datos)
    sistema = salida.get("proyecto", {}).get("sistema_unidades", "SI")
    if sistema == "SI":
        return salida
    if sistema != "MKS":
        raise ValueError("sistema_unidades debe ser SI o MKS")

    mats = salida["materiales"]
    for nombre in ("concreto", "acero_estructural", "acero_refuerzo"):
        material = mats.get(nombre, {})
        for clave in ("fc", "fy", "fu", "ec", "es"):
            if material.get(clave) is not None:
                material[clave] *= KGF_CM2_A_MPA
    for nombre in ("concreto", "acero_estructural"):
        if "peso_unitario" not in mats[nombre]:
            raise ValueError(
                f"materiales.{nombre}.peso_unitario es obligatorio para entradas MKS"
            )
        mats[nombre]["peso_unitario"] *= TF_A_KN

    construccion = salida.get("construccion", {})
    if "carga_construccion" in construccion:
        construccion["carga_construccion"] *= TF_A_KN
    for clave, valor in salida.get("cargas", {}).items():
        if isinstance(valor, dict):
            salida["cargas"][clave] = {
                tipo: carga * TF_A_KN for tipo, carga in valor.items()
            }
        else:
            salida["cargas"][clave] = valor * TF_A_KN
    trafico = salida.get("trafico", {})
    for clave in ("tandem_eje", "carga_carril"):
        if clave in trafico:
            trafico[clave] *= TF_A_KN
    camion = trafico.get("camion", {})
    for clave in ("eje_frontal", "eje_posterior"):
        if clave in camion:
            camion[clave] *= TF_A_KN
    salida["proyecto"]["sistema_unidades"] = "SI"
    return salida


def kn_a_n(valor: float) -> float:
    return valor * 1000.0


def m_a_mm(valor: float) -> float:
    return valor * 1000.0


def kn_m_a_n_mm(valor: float) -> float:
    return valor * 1_000_000.0

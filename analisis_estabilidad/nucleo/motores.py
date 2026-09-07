"""Adaptadores entre los contratos JSON y los motores estructurales existentes."""

from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any, Callable

from .contratos import (
    DependenciaConsumida,
    EntradaElemento,
    ResultadoElemento,
    escribir_json_atomico,
    leer_entrada,
    leer_resultado,
    sha256_archivo,
    sha256_datos,
)
from .rutas import asegurar_interna


def _argumentos_dataclass(clase: type, datos: dict[str, Any]) -> dict[str, Any]:
    permitidos = {campo.name for campo in fields(clase)}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(
            f"Parámetros desconocidos para {clase.__name__}: {sorted(desconocidos)}"
        )
    return {clave: valor for clave, valor in datos.items() if clave in permitidos}


def _dependencias(entrada: EntradaElemento, ruta_entrada: Path) -> dict[str, dict]:
    salida: dict[str, dict] = {}
    for dependencia in entrada.dependencias:
        ruta = asegurar_interna(ruta_entrada.parent / dependencia.resultado)
        if not ruta.exists():
            raise ValueError(f"Dependencia ausente: {ruta}")
        huella = sha256_archivo(ruta)
        if huella != dependencia.sha256:
            raise ValueError(f"Huella incorrecta en dependencia: {ruta}")
        contrato = leer_resultado(ruta)
        if contrato.elemento != dependencia.elemento or contrato.calculo != dependencia.calculo:
            raise ValueError(f"Identidad incompatible en dependencia: {ruta}")
        if contrato.estado in ("ERROR", "OBSOLETO"):
            raise ValueError(f"Dependencia no consumible ({contrato.estado}): {ruta}")
        salida[f"{contrato.elemento}.{contrato.calculo}"] = contrato.resultados
    return salida


def _estado(resultado: dict[str, Any]) -> str:
    estado = str(resultado.get("estado", resultado.get("estado_general", "OK"))).upper()
    if "NO CUMPLE" in estado or "NO_CUMPLE" in estado:
        return "NO_CUMPLE"
    advertencias = resultado.get("advertencias", [])
    return "ADVERTENCIA" if advertencias else "OK"


def _normalizar_json(valor: Any) -> Any:
    """Convierte escalares y arreglos científicos a tipos JSON nativos."""
    def convertir(objeto: Any) -> Any:
        if hasattr(objeto, "item"):
            return objeto.item()
        if hasattr(objeto, "tolist"):
            return objeto.tolist()
        raise TypeError(f"Tipo no serializable: {type(objeto).__name__}")

    return json.loads(json.dumps(valor, ensure_ascii=False, default=convertir))


def _comunes_desde_estabilidad(dependencias: dict[str, dict]) -> dict[str, Any]:
    resultado = dependencias.get("estribo.estabilidad_global")
    if resultado is None:
        raise ValueError("Falta el resultado estribo.estabilidad_global")
    try:
        return resultado["configuracion_resuelta"]
    except KeyError as exc:
        raise ValueError("La estabilidad global no exportó configuracion_resuelta") from exc


def _configurar_globales(modulo: Any, comunes: dict[str, Any]) -> None:
    from analisis_estabilidad.elementos.estribo import estabilidad_global as eg

    if hasattr(modulo, "GEOM"):
        modulo.GEOM = eg.AbutmentGeometry(**comunes["geometria"])
    if hasattr(modulo, "MAT"):
        modulo.MAT = eg.MaterialProperties(**comunes["materiales"])
    if hasattr(modulo, "LOADS"):
        modulo.LOADS = eg.SuperstructureLoads(**comunes["cargas_superestructura"])
    if hasattr(modulo, "SEISMIC"):
        modulo.SEISMIC = eg.SeismicParameters(**comunes["sismo"])
    if hasattr(modulo, "FALSE_FOOTING"):
        modulo.FALSE_FOOTING = eg.FalseFootingProperties(**comunes["falsa_zapata"])


def _estribo_estabilidad(entrada: EntradaElemento, _: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.estribo import estabilidad_global as m

    p = entrada.parametros
    geometria = m.AbutmentGeometry(**p["geometria"])
    materiales = m.MaterialProperties(**p["materiales"])
    cargas = m.SuperstructureLoads(**p["cargas_superestructura"])
    sismo = m.SeismicParameters(**p["sismo"])
    falsa = m.FalseFootingProperties(**p["falsa_zapata"])
    resultado = m.SubstructureAnalysis(
        geometria, materiales, cargas, sismo, falsa
    ).run_full_analysis()
    resultado["configuracion_resuelta"] = {
        "geometria": p["geometria"],
        "materiales": p["materiales"],
        "cargas_superestructura": p["cargas_superestructura"],
        "sismo": p["sismo"],
        "falsa_zapata": p["falsa_zapata"],
    }
    return resultado


def _pantalla_shell(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.pantalla import analisis_shell_3d as m

    comunes = _comunes_desde_estabilidad(dependencias)
    _configurar_globales(m, comunes)
    parametros = m.ParametrosShell(
        **_argumentos_dataclass(m.ParametrosShell, entrada.parametros["elemento"])
    )
    return m._limpiar_para_json(m.calcular(parametros, incluir_convergencia=False))


def _pantalla_diseno(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.pantalla import diseno_e060_mtc as m

    comunes = _comunes_desde_estabilidad(dependencias)
    _configurar_globales(m, comunes)
    parametros = m.ParametrosPantalla(
        **_argumentos_dataclass(m.ParametrosPantalla, entrada.parametros["elemento"])
    )
    return m.calcular_diseno(parametros)


def _contrafuertes_analisis(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.contrafuertes import analisis_2d as m

    resultado_shell = dependencias["pantalla.reacciones_contrafuertes"]
    parametros = m.ParametrosContrafuerte(
        **_argumentos_dataclass(m.ParametrosContrafuerte, entrada.parametros["elemento"])
    )
    resultado = m.resolver_modelo(parametros, resultado_shell)
    return json.loads(json.dumps(resultado, ensure_ascii=False, default=m._json_default))


def _contrafuertes_diseno(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.contrafuertes import diseno_stm as m

    analisis = dependencias["contrafuertes.analisis_2d"]
    parametros = m.ParametrosDisenoContrafuertes(
        **_argumentos_dataclass(
            m.ParametrosDisenoContrafuertes, entrada.parametros["elemento"]
        )
    )
    return m.disenar(analisis, parametros)


def _zapata_longitudinal(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.zapata import diseno_longitudinal_e060 as m

    estabilidad = dependencias["estribo.estabilidad_global"]
    _configurar_globales(m, _comunes_desde_estabilidad(dependencias))
    parametros = m.ParametrosDiseno(
        **_argumentos_dataclass(m.ParametrosDiseno, entrada.parametros["elemento"])
    )
    return m.disenar(parametros, estabilidad)


def _zapata_transversal(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.zapata import diseno_transversal_e060_mtc as m

    estabilidad = dependencias["estribo.estabilidad_global"]
    _configurar_globales(m, _comunes_desde_estabilidad(dependencias))
    parametros = m.ParametrosZapataTransversal(
        **_argumentos_dataclass(
            m.ParametrosZapataTransversal, entrada.parametros["elemento"]
        )
    )
    return m.calcular_diseno(parametros, estabilidad)


def _dentellon(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.dentellon import diseno_e060 as m

    estabilidad = dependencias["estribo.estabilidad_global"]
    _configurar_globales(m, _comunes_desde_estabilidad(dependencias))
    parametros = m.ParametrosDentellon(
        **_argumentos_dataclass(m.ParametrosDentellon, entrada.parametros["elemento"])
    )
    return m.disenar(parametros, estabilidad)


def _cajuela(entrada: EntradaElemento, dependencias: dict[str, dict]) -> dict:
    from analisis_estabilidad.elementos.cajuela import verificacion_voladizo as m

    comunes = _comunes_desde_estabilidad(dependencias)
    datos = dict(entrada.parametros["elemento"])
    mat = comunes["materiales"]
    cargas = comunes["cargas_superestructura"]
    sismo = comunes["sismo"]
    datos.update({
        "fc_kgf_cm2": mat["f_c"],
        "fy_kgf_cm2": mat["fy"],
        "gamma_relleno_tf_m3": mat["gamma_r"],
        "gamma_concreto_tf_m3": mat["gamma_c"],
        "phi_relleno_grados": mat["phi_relleno"],
        "delta_grados": mat["delta"],
        "dc_tf_m": cargas["DC"],
        "dw_tf_m": cargas["DW"],
        "pl_tf_m": cargas["PL"],
        "ll_im_tf_m": cargas["LL_IM"],
        "br_tf_m": cargas["BR"],
        "kh": sismo["Kh"],
        "kv": sismo["Kv"],
    })
    parametros = m.Parametros(**_argumentos_dataclass(m.Parametros, datos))
    return m.evaluar(parametros)


MOTORES: dict[str, Callable[[EntradaElemento, dict[str, dict]], dict]] = {
    "estribo.estabilidad_global": _estribo_estabilidad,
    "pantalla.analisis_shell_3d": _pantalla_shell,
    "pantalla.reacciones_contrafuertes": _pantalla_shell,
    "pantalla.diseno_e060_mtc": _pantalla_diseno,
    "contrafuertes.analisis_2d": _contrafuertes_analisis,
    "contrafuertes.diseno_stm": _contrafuertes_diseno,
    "zapata.diseno_longitudinal_e060": _zapata_longitudinal,
    "zapata.diseno_transversal_e060_mtc": _zapata_transversal,
    "dentellon.diseno_e060": _dentellon,
    "cajuela.verificacion_voladizo": _cajuela,
}


def ejecutar_entrada(
    objetivo: str, ruta_entrada: str | Path, carpeta_salida: str | Path
) -> ResultadoElemento:
    if objetivo not in MOTORES:
        raise ValueError(f"Objetivo desconocido: {objetivo}")
    ruta_entrada = asegurar_interna(ruta_entrada)
    carpeta_salida = asegurar_interna(carpeta_salida)
    entrada = leer_entrada(ruta_entrada)
    if objetivo != f"{entrada.elemento}.{entrada.calculo}":
        raise ValueError("El objetivo no coincide con la identidad de entrada.json")
    dependencias = _dependencias(entrada, ruta_entrada)
    resultado_bruto = _normalizar_json(MOTORES[objetivo](entrada, dependencias))
    contrato = ResultadoElemento(
        ejecucion_id=entrada.ejecucion_id,
        elemento=entrada.elemento,
        calculo=entrada.calculo,
        entrada_sha256=sha256_datos(entrada),
        dependencias_consumidas=[
            DependenciaConsumida(
                elemento=x.elemento, calculo=x.calculo, sha256=x.sha256
            )
            for x in entrada.dependencias
        ],
        estado=_estado(resultado_bruto),
        resultados=resultado_bruto,
        advertencias=[str(x) for x in resultado_bruto.get("advertencias", [])],
    )
    escribir_json_atomico(carpeta_salida / "resultado.json", contrato)
    _escribir_reporte(objetivo, resultado_bruto, carpeta_salida / "reporte.md")
    return contrato


def _escribir_reporte(objetivo: str, resultado: dict, ruta: Path) -> None:
    generadores: dict[str, Callable[[dict], str]] = {}
    if objetivo == "estribo.estabilidad_global":
        from analisis_estabilidad.elementos.estribo.estabilidad_global import generate_markdown_report
        generadores[objetivo] = generate_markdown_report
    elif objetivo in ("pantalla.analisis_shell_3d", "pantalla.reacciones_contrafuertes"):
        from analisis_estabilidad.elementos.pantalla.analisis_shell_3d import generar_markdown
        generadores[objetivo] = generar_markdown
    elif objetivo == "pantalla.diseno_e060_mtc":
        from analisis_estabilidad.elementos.pantalla.diseno_e060_mtc import generar_resumen_texto
        generadores[objetivo] = generar_resumen_texto
    elif objetivo == "contrafuertes.analisis_2d":
        from analisis_estabilidad.elementos.contrafuertes.analisis_2d import generar_markdown
        generadores[objetivo] = generar_markdown
    elif objetivo == "contrafuertes.diseno_stm":
        from analisis_estabilidad.elementos.contrafuertes.diseno_stm import generar_markdown
        generadores[objetivo] = generar_markdown
    elif objetivo == "zapata.diseno_longitudinal_e060":
        from analisis_estabilidad.elementos.zapata.diseno_longitudinal_e060 import generar_markdown
        generadores[objetivo] = generar_markdown
    elif objetivo == "zapata.diseno_transversal_e060_mtc":
        from analisis_estabilidad.elementos.zapata.diseno_transversal_e060_mtc import generar_markdown
        generadores[objetivo] = generar_markdown
    elif objetivo == "dentellon.diseno_e060":
        from analisis_estabilidad.elementos.dentellon.diseno_e060 import generar_markdown
        generadores[objetivo] = generar_markdown
    elif objetivo == "cajuela.verificacion_voladizo":
        from analisis_estabilidad.elementos.cajuela.verificacion_voladizo import reporte_markdown
        generadores[objetivo] = reporte_markdown
    generador = generadores.get(objetivo)
    if generador:
        ruta.write_text(generador(resultado), encoding="utf-8")

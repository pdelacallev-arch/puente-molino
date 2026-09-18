"""Generación de JSON, CSV, Markdown y figuras desde un único resultado canónico."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
from pydantic import BaseModel

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..analisis.motor import ResultadoAnalisis
from ..analisis.parrilla import ResultadoParrilla
from ..configuracion import huella_configuracion
from ..diseno.verificaciones import ResultadoDiseno
from ..orquestador import ResultadoBusqueda

KN_POR_TF = 9.80665
MPA_POR_KGF_CM2 = 0.0980665


def _serializable(valor: Any) -> Any:
    if isinstance(valor, np.ndarray):
        return valor.tolist()
    if isinstance(valor, np.generic):
        return valor.item()
    if isinstance(valor, BaseModel):
        return valor.model_dump(mode="json")
    if is_dataclass(valor):
        return {k: _serializable(v) for k, v in asdict(valor).items()}
    if isinstance(valor, dict):
        return {str(k): _serializable(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_serializable(v) for v in valor]
    return valor


def directorio_salida(analisis: ResultadoAnalisis, base: str | Path = "outputs/vigas_principales") -> Path:
    p = Path(base) / analisis.configuracion.proyecto.id / analisis.configuracion.proyecto.revision
    p.mkdir(parents=True, exist_ok=True)
    return p


def analisis_a_dict(resultado: ResultadoAnalisis) -> dict:
    tipos = {}
    for tipo, datos in resultado.tipos_viga.items():
        copia = {k: v for k, v in datos.items() if k != "propiedades"}
        copia["propiedades"] = [
            {
                "segmento": p["segmento"],
                "acero": p["acero"].a_dict(),
                "corto_plazo": p["corto_plazo"].a_dict(),
                "largo_plazo": p["largo_plazo"].a_dict(),
                "plastico": p["plastico"].a_dict(),
                "ancho_efectivo_mm": p["ancho_efectivo_mm"],
                "ec_mpa": p["ec_mpa"],
                "n": p["n"],
            }
            for p in datos["propiedades"]
        ]
        tipos[tipo] = _serializable(copia)
    return {
        "metadatos": {
            "proyecto": resultado.configuracion.proyecto.model_dump(mode="json"),
            "sha256_configuracion_normalizada": huella_configuracion(resultado.configuracion),
            "metodo": "Bartra pp. 113-165 actualizado a MTC 2018",
            "alcance": "Viga I recta simplemente apoyada; conectores, rigidizadores y diafragmas excluidos",
        },
        "configuracion_normalizada_si": resultado.configuracion.model_dump(mode="json"),
        "x_mm": resultado.x_mm.tolist(),
        "tipos_viga": tipos,
        "factores_distribucion": resultado.factores_distribucion,
        "detalle_distribucion": resultado.detalle_distribucion,
        "equilibrio_relativo": resultado.equilibrio_relativo,
        "advertencias": list(resultado.advertencias),
        "referencias": resultado.referencias,
    }


def diseno_a_dict(resultado: ResultadoDiseno) -> dict:
    contenido = {
        "analisis": analisis_a_dict(resultado.analisis),
        "estado": resultado.estado,
        "estado_gobernante": resultado.estado_gobernante.model_dump(mode="json"),
        "verificaciones": {
            tipo: [v.model_dump(mode="json") for v in verificaciones]
            for tipo, verificaciones in resultado.verificaciones.items()
        },
        "pendientes": list(resultado.pendientes),
        "advertencias": list(resultado.advertencias),
    }
    if resultado.analisis.configuracion.analisis.reportar_mks:
        contenido["verificaciones_mks"] = {
            tipo: [_check_mks(v) for v in verificaciones]
            for tipo, verificaciones in resultado.verificaciones.items()
        }
    return contenido


def _check_mks(check) -> dict:
    factor, unidad = 1.0, check.unidad
    if check.unidad == "kN.m":
        factor, unidad = 1.0 / KN_POR_TF, "tf.m"
    elif check.unidad == "kN":
        factor, unidad = 1.0 / KN_POR_TF, "tf"
    elif check.unidad == "MPa":
        factor, unidad = 1.0 / MPA_POR_KGF_CM2, "kgf/cm2"
    return {
        "nombre": check.nombre,
        "demanda": check.demanda * factor,
        "capacidad": check.capacidad * factor,
        "unidad": unidad,
        "dcr": check.dcr,
        "cumple": check.cumple,
    }


def _figuras_analisis(resultado: ResultadoAnalisis, figuras: Path) -> list[Path]:
    """Genera las figuras del análisis en la carpeta indicada."""
    figuras.mkdir(parents=True, exist_ok=True)
    rutas: list[Path] = []
    ruta = figuras / "diagramas_acciones_permanentes.png"
    _figura_casos_carga(resultado, ruta)
    rutas.append(ruta)
    ruta = figuras / "envolvente_carga_movil_LL_IM.png"
    _figura_carga_movil(resultado, ruta)
    rutas.append(ruta)
    resistencia = (figuras / "combinacion_resistencia_i.png", figuras / "envolventes.png")
    _figura_combinacion(
        resultado,
        resistencia,
        momento_clave="resistencia_i",
        cortante_positivo_clave="resistencia_i_positivo",
        cortante_negativo_clave="resistencia_i_negativo",
        titulo="Combinación Resistencia I",
        simbolo_momento="$M_u$",
        simbolo_cortante="$V_u$",
    )
    rutas.extend(resistencia)
    ruta = figuras / "combinacion_servicio_ii.png"
    _figura_combinacion(
        resultado,
        (ruta,),
        momento_clave="servicio_ii",
        cortante_positivo_clave="servicio_ii_positivo",
        cortante_negativo_clave="servicio_ii_negativo",
        titulo="Combinación Servicio II",
        simbolo_momento="$M_{serv}$",
        simbolo_cortante="$V_{serv}$",
    )
    rutas.append(ruta)
    ruta = figuras / "envolvente_fatiga.png"
    _figura_fatiga(resultado, ruta)
    rutas.append(ruta)
    return rutas


def artefactos_analisis(resultado: ResultadoAnalisis, carpeta: str | Path) -> list[Path]:
    """Escribe CSV y figuras del análisis dentro de la carpeta del cálculo."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas: list[Path] = [carpeta / "envolventes.csv"]
    _exportar_csv(resultado, carpeta / "envolventes.csv")
    rutas.extend(_figuras_analisis(resultado, carpeta / "figuras"))
    return rutas


def artefactos_diseno(resultado: ResultadoDiseno, carpeta: str | Path) -> list[Path]:
    """Escribe los artefactos del diseño, incluidos los del análisis."""
    carpeta = Path(carpeta)
    rutas = artefactos_analisis(resultado.analisis, carpeta)
    ruta = carpeta / "figuras" / "dcr.png"
    _figura_dcr(resultado, ruta)
    rutas.append(ruta)
    return rutas


def exportar_analisis(resultado: ResultadoAnalisis, base: str | Path = "outputs/vigas_principales") -> Path:
    salida = directorio_salida(resultado, base)
    (salida / "analisis.json").write_text(
        json.dumps(analisis_a_dict(resultado), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _exportar_csv(resultado, salida / "envolventes.csv")
    _figuras_analisis(resultado, salida)
    return salida


def exportar_diseno(resultado: ResultadoDiseno, base: str | Path = "outputs/vigas_principales") -> Path:
    salida = exportar_analisis(resultado.analisis, base)
    (salida / "diseno.json").write_text(
        json.dumps(diseno_a_dict(resultado), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (salida / "memoria.md").write_text(_memoria(resultado), encoding="utf-8")
    _figura_dcr(resultado, salida / "dcr.png")
    return salida


def busqueda_a_dict(resultado: ResultadoBusqueda) -> dict:
    def alt(a):
        return {
            "masa_kg": a.masa_kg,
            "maximo_dcr": a.maximo_dcr,
            "estado": a.estado,
            "segmentos": [s.model_dump(mode="json") for s in a.segmentos],
            "gobernante": a.resultado.estado_gobernante.model_dump(mode="json"),
        }

    return {
        "evaluados": resultado.evaluados,
        "truncado": resultado.truncado,
        "factibles": [alt(a) for a in resultado.factibles],
        "mejores_no_factibles": [alt(a) for a in resultado.mejores_no_factibles],
    }


def exportar_busqueda(resultado: ResultadoBusqueda, salida: Path) -> None:
    (salida / "busqueda.json").write_text(
        json.dumps(busqueda_a_dict(resultado), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if resultado.factibles:
        (salida / "diseno_optimo.json").write_text(
            json.dumps(
                diseno_a_dict(resultado.factibles[0].resultado),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (salida / "memoria_optima.md").write_text(
            _memoria(resultado.factibles[0].resultado), encoding="utf-8"
        )


def artefactos_busqueda(resultado: ResultadoBusqueda, carpeta: str | Path) -> list[Path]:
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    exportar_busqueda(resultado, carpeta)
    rutas = [carpeta / "busqueda.json"]
    if resultado.factibles:
        rutas += [carpeta / "diseno_optimo.json", carpeta / "memoria_optima.md"]
    return rutas


def reporte_analisis(resultado: ResultadoAnalisis) -> str:
    cfg = resultado.configuracion
    lineas = [
        f"# Análisis de vigas principales - {cfg.proyecto.nombre}",
        "",
        f"- Revisión: `{cfg.proyecto.revision}`",
        f"- Luz: {cfg.geometria.luz:g} m",
        f"- Número de vigas: {cfg.geometria.numero_vigas}",
        f"- Método de distribución: {cfg.analisis.metodo_distribucion}",
        f"- Equilibrio relativo: {resultado.equilibrio_relativo:.3e}",
        "",
        "## Factores de distribución",
        "",
        "| Factor | Valor |",
        "|---|---:|",
    ]
    for nombre, valor in resultado.factores_distribucion.items():
        if nombre != "advertencias":
            lineas.append(f"| {nombre} | {valor:.5f} |")
    lineas += ["", "## Advertencias", ""]
    lineas.extend(f"- {a}" for a in resultado.advertencias)
    lineas += ["", "Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.", ""]
    return "\n".join(lineas)


def reporte_diseno(resultado: ResultadoDiseno) -> str:
    return _memoria(resultado)


def reporte_busqueda(resultado: ResultadoBusqueda) -> str:
    return "\n".join([
        "# Búsqueda discreta de secciones de vigas principales",
        "",
        f"- Candidatos evaluados: {resultado.evaluados}",
        f"- Búsqueda truncada: {'sí' if resultado.truncado else 'no'}",
        f"- Alternativas factibles: {len(resultado.factibles)}",
        "",
        "Las alternativas factibles se ordenan por masa ascendente y máximo DCR.",
        "Nunca debe adoptarse como óptimo un candidato no factible.",
        "",
    ])


def reporte_parrilla(resultado: ResultadoParrilla) -> str:
    lineas = [
        "# Distribución transversal por parrilla espacial",
        "",
        f"- Grados de libertad: {resultado.numero_grados_libertad}",
        f"- Error de equilibrio máximo: {resultado.error_equilibrio_maximo:.3e}",
        "",
        "| Factor | Valor |",
        "|---|---:|",
    ]
    for nombre, valor in resultado.factores.a_dict().items():
        if isinstance(valor, (int, float)):
            lineas.append(f"| {nombre} | {valor:.5f} |")
    lineas.append("")
    return "\n".join(lineas)


def _exportar_csv(resultado: ResultadoAnalisis, ruta: Path) -> None:
    campos = ["x_m"]
    for tipo in ("interior", "exterior"):
        campos += [
            f"M_DC_no_compuesta_{tipo}_kNm",
            f"M_DC_compuesta_{tipo}_kNm",
            f"M_DW_{tipo}_kNm",
            f"M_PL_{tipo}_kNm",
            f"M_LL_IM_{tipo}_kNm",
            f"M_fatiga_rango_{tipo}_kNm",
            f"M_resistencia_{tipo}_kNm",
            f"M_servicio_ii_{tipo}_kNm",
            f"V_DC_no_compuesta_{tipo}_kN",
            f"V_DC_compuesta_{tipo}_kN",
            f"V_DW_{tipo}_kN",
            f"V_PL_{tipo}_kN",
            f"Vmax_LL_IM_{tipo}_kN",
            f"Vmin_LL_IM_{tipo}_kN",
            f"Vmax_resistencia_{tipo}_kN",
            f"Vmin_resistencia_{tipo}_kN",
            f"Vabs_resistencia_{tipo}_kN",
            f"Vmax_servicio_ii_{tipo}_kN",
            f"Vmin_servicio_ii_{tipo}_kN",
            f"Vabs_servicio_ii_{tipo}_kN",
            # Alias conservado para archivos consumidores existentes.
            f"V_resistencia_{tipo}_kN",
            f"def_LL_{tipo}_mm",
            f"def_LL_PL_servicio_i_{tipo}_mm",
        ]
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for i, x in enumerate(resultado.x_mm):
            fila = {"x_m": x / 1000.0}
            for tipo in ("interior", "exterior"):
                datos = resultado.tipos_viga[tipo]
                momentos = datos["momentos_nmm"]
                cortantes = datos["cortantes_n"]
                for clave in ("DC_no_compuesta", "DC_compuesta", "DW", "PL", "LL_IM"):
                    fila[f"M_{clave}_{tipo}_kNm"] = momentos[clave][i] / 1e6
                    if clave != "LL_IM":
                        fila[f"V_{clave}_{tipo}_kN"] = cortantes[clave][i] / 1000.0
                fila[f"M_fatiga_rango_{tipo}_kNm"] = momentos["fatiga_rango"][i] / 1e6
                fila[f"M_resistencia_{tipo}_kNm"] = momentos["resistencia_i"][i] / 1e6
                fila[f"M_servicio_ii_{tipo}_kNm"] = momentos["servicio_ii"][i] / 1e6
                fila[f"Vmax_LL_IM_{tipo}_kN"] = cortantes["LL_IM_positivo"][i] / 1000.0
                fila[f"Vmin_LL_IM_{tipo}_kN"] = cortantes["LL_IM_negativo"][i] / 1000.0
                fila[f"Vmax_resistencia_{tipo}_kN"] = cortantes["resistencia_i_positivo"][i] / 1000.0
                fila[f"Vmin_resistencia_{tipo}_kN"] = cortantes["resistencia_i_negativo"][i] / 1000.0
                fila[f"Vabs_resistencia_{tipo}_kN"] = cortantes["resistencia_i_abs"][i] / 1000.0
                fila[f"Vmax_servicio_ii_{tipo}_kN"] = cortantes["servicio_ii_positivo"][i] / 1000.0
                fila[f"Vmin_servicio_ii_{tipo}_kN"] = cortantes["servicio_ii_negativo"][i] / 1000.0
                fila[f"Vabs_servicio_ii_{tipo}_kN"] = cortantes["servicio_ii_abs"][i] / 1000.0
                fila[f"V_resistencia_{tipo}_kN"] = cortantes["resistencia_i_abs"][i] / 1000.0
                fila[f"def_LL_{tipo}_mm"] = datos["deflexiones_mm"]["LL_IM_critica"][i]
                fila[f"def_LL_PL_servicio_i_{tipo}_mm"] = datos["deflexiones_mm"][
                    "servicio_i_vehicular_peatonal"
                ][i]
            escritor.writerow(fila)


COLORES_VIGA = {"interior": "#1f77b4", "exterior": "#ff7f0e"}


def _figura_combinacion(
    resultado: ResultadoAnalisis,
    rutas: tuple[Path, ...],
    *,
    momento_clave: str,
    cortante_positivo_clave: str,
    cortante_negativo_clave: str,
    titulo: str,
    simbolo_momento: str,
    simbolo_cortante: str,
) -> None:
    x = resultado.x_mm / 1000.0
    fig, (ax_m, ax_v) = plt.subplots(
        2, 1, figsize=(10, 8), sharex=True, layout="constrained"
    )
    for indice_tipo, tipo in enumerate(("interior", "exterior")):
        datos = resultado.tipos_viga[tipo]
        color = COLORES_VIGA[tipo]
        momento = datos["momentos_nmm"][momento_clave] / 1e6
        cortantes = datos["cortantes_n"]
        v_pos = cortantes[cortante_positivo_clave] / 1000.0
        v_neg = cortantes[cortante_negativo_clave] / 1000.0

        ax_m.plot(x, momento, color=color, linewidth=2.0, label=tipo)
        i_m = int(np.argmax(np.abs(momento)))
        ax_m.scatter(x[i_m], momento[i_m], color=color, zorder=4)
        ax_m.annotate(
            f"{momento[i_m]:,.0f} kN·m\nx={x[i_m]:.2f} m",
            (x[i_m], momento[i_m]),
            xytext=((-86 if indice_tipo == 0 else 12), (-34 if indice_tipo == 0 else -38)),
            textcoords="offset points",
            fontsize=8,
            color=color,
            arrowprops={"arrowstyle": "->", "color": color, "lw": 0.8},
        )

        ax_v.plot(x, v_pos, color=color, linewidth=1.8, label=f"{tipo}: $V_{{max}}$")
        ax_v.plot(
            x,
            v_neg,
            color=color,
            linewidth=1.8,
            linestyle="--",
            label=f"{tipo}: $V_{{min}}$",
        )
        v_critico = v_pos if np.max(np.abs(v_pos)) >= np.max(np.abs(v_neg)) else v_neg
        i_v = int(np.argmax(np.abs(v_critico)))
        ax_v.scatter(x[i_v], v_critico[i_v], color=color, zorder=4)
        desplazamiento_v = (
            (12, 36 - 28 * indice_tipo)
            if x[i_v] < x[-1] / 2.0
            else (-142, 76 - 30 * indice_tipo)
        )
        ax_v.annotate(
            f"|V|max={abs(v_critico[i_v]):,.0f} kN\nx={x[i_v]:.2f} m",
            (x[i_v], v_critico[i_v]),
            xytext=desplazamiento_v,
            textcoords="offset points",
            fontsize=8,
            color=color,
            arrowprops={"arrowstyle": "->", "color": color, "lw": 0.8},
        )
    ax_m.set_ylabel(f"{simbolo_momento} (kN·m)")
    ax_m.set_title("Momento flector combinado")
    ax_m.margins(y=0.10)
    ax_v.axhline(0.0, color="black", linewidth=0.8)
    ax_v.set_ylabel(f"{simbolo_cortante} (kN)")
    ax_v.set_title("Cortante combinado con signo; máximo absoluto marcado")
    ax_v.margins(y=0.15)
    ax_v.set_xlabel("x (m)")
    for ax in (ax_m, ax_v):
        ax.grid(True, alpha=0.3)
        ax.legend(ncol=2, fontsize=8)
    fig.suptitle(f"Envolvente de solicitaciones — {titulo}")
    for ruta in rutas:
        fig.savefig(ruta, dpi=180)
    plt.close(fig)


def _figura_casos_carga(resultado: ResultadoAnalisis, ruta: Path) -> None:
    x = resultado.x_mm / 1000.0
    fig, ejes = plt.subplots(
        2, 2, figsize=(12, 8), sharex=True, layout="constrained"
    )
    acciones = (
        ("DC_no_compuesta", "$DC_{nc}$"),
        ("DC_compuesta", "$DC_{comp}$"),
        ("DW", "$DW$"),
        ("PL", "$PL$"),
    )
    for columna, tipo in enumerate(("interior", "exterior")):
        datos = resultado.tipos_viga[tipo]
        for clave, etiqueta in acciones:
            ejes[0, columna].plot(x, datos["momentos_nmm"][clave] / 1e6, label=etiqueta)
            ejes[1, columna].plot(x, datos["cortantes_n"][clave] / 1000.0, label=etiqueta)
        ejes[0, columna].set_title(f"Viga {tipo}")
        ejes[1, columna].axhline(0.0, color="black", linewidth=0.8)
        ejes[1, columna].set_xlabel("x (m)")
        for fila in range(2):
            ejes[fila, columna].grid(True, alpha=0.3)
            ejes[fila, columna].legend(ncol=2, fontsize=8)
    ejes[0, 0].set_ylabel("M por acción (kN·m)")
    ejes[1, 0].set_ylabel("V por acción (kN)")
    fig.suptitle("Diagramas por acciones permanentes y peatonal — sin combinar")
    fig.savefig(ruta, dpi=180)
    plt.close(fig)


def _figura_carga_movil(resultado: ResultadoAnalisis, ruta: Path) -> None:
    x = resultado.x_mm / 1000.0
    fig, (ax_m, ax_v) = plt.subplots(
        2, 1, figsize=(10, 8), sharex=True, layout="constrained"
    )
    for tipo in ("interior", "exterior"):
        datos = resultado.tipos_viga[tipo]
        color = COLORES_VIGA[tipo]
        ax_m.plot(x, datos["momentos_nmm"]["LL_IM"] / 1e6, color=color, label=tipo)
        ax_v.plot(
            x,
            datos["cortantes_n"]["LL_IM_positivo"] / 1000.0,
            color=color,
            label=f"{tipo}: $V_{{max}}$",
        )
        ax_v.plot(
            x,
            datos["cortantes_n"]["LL_IM_negativo"] / 1000.0,
            color=color,
            linestyle="--",
            label=f"{tipo}: $V_{{min}}$",
        )
    ax_m.set_ylabel("$M_{LL+IM,max}$ (kN·m)")
    ax_m.set_title("Envolvente de momento vehicular")
    ax_v.axhline(0.0, color="black", linewidth=0.8)
    ax_v.set_ylabel("$V_{LL+IM}$ (kN)")
    ax_v.set_title("Envolventes positiva y negativa de cortante vehicular")
    ax_v.set_xlabel("x (m)")
    for ax in (ax_m, ax_v):
        ax.grid(True, alpha=0.3)
        ax.legend(ncol=2, fontsize=8)
    fig.suptitle("Envolventes de carga móvil $LL+IM$ — sin factores de combinación")
    fig.savefig(ruta, dpi=180)
    plt.close(fig)


def _figura_fatiga(resultado: ResultadoAnalisis, ruta: Path) -> None:
    x = resultado.x_mm / 1000.0
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    for tipo in ("interior", "exterior"):
        rango = resultado.tipos_viga[tipo]["momentos_nmm"]["fatiga_rango"] / 1e6
        color = COLORES_VIGA[tipo]
        ax.plot(x, rango, color=color, linewidth=2.0, label=tipo)
        indice = int(np.argmax(rango))
        ax.scatter(x[indice], rango[indice], color=color, zorder=4)
        ax.annotate(
            f"{rango[indice]:,.0f} kN·m\nx={x[indice]:.2f} m",
            (x[indice], rango[indice]),
            xytext=((-88 if tipo == "interior" else 12), (-34 if tipo == "interior" else -42)),
            textcoords="offset points",
            fontsize=8,
            color=color,
            arrowprops={"arrowstyle": "->", "color": color, "lw": 0.8},
        )
    ax.set_xlabel("x (m)")
    ax.set_ylabel("$\\Delta M_{fatiga}$ (kN·m)")
    ax.set_title("Rango de momento por camión de fatiga")
    ax.margins(y=0.12)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(ruta, dpi=180)
    plt.close(fig)


def _figura_dcr(resultado: ResultadoDiseno, ruta: Path) -> None:
    etiquetas: list[str] = []
    valores: list[float] = []
    for tipo, checks in resultado.verificaciones.items():
        for check in checks:
            etiquetas.append(f"{tipo}: {check.nombre}")
            valores.append(check.dcr)
    fig, ax = plt.subplots(figsize=(10, max(5, len(etiquetas) * 0.35)))
    y = np.arange(len(etiquetas))
    ax.barh(y, valores, color=["#2b8cbe" if v <= 1.0 else "#d7301f" for v in valores])
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_yticks(y, etiquetas)
    ax.invert_yaxis()
    ax.set_xlabel("DCR = demanda / capacidad")
    ax.set_title("Verificaciones de vigas principales")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=180)
    plt.close(fig)


def _memoria(resultado: ResultadoDiseno) -> str:
    cfg = resultado.analisis.configuracion
    lineas = [
        f"# Análisis y diseño de vigas principales - {cfg.proyecto.nombre}",
        "",
        f"- Revisión: `{cfg.proyecto.revision}`",
        f"- Norma: {cfg.normativa.manual} {cfg.normativa.edicion}",
        "- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.",
        f"- Estado: **{resultado.estado}**",
        "",
        "## Hipótesis y alcance",
        "",
        "Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.",
        "",
        "## Factores de distribución",
        "",
        "| Factor | Valor |",
        "|---|---:|",
    ]
    for nombre, valor in resultado.analisis.factores_distribucion.items():
        if nombre != "advertencias":
            lineas.append(f"| {nombre} | {valor:.5f} |")
    lineas += ["", "## Verificaciones", "", "| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |", "|---|---|---:|---:|---:|---|"]
    for tipo, checks in resultado.verificaciones.items():
        for check in checks:
            estado = "Cumple" if check.cumple else "No cumple"
            lineas.append(
                f"| {tipo} | {check.nombre} | {check.demanda:.4g} {check.unidad} | {check.capacidad:.4g} {check.unidad} | {check.dcr:.3f} | {estado} |"
            )
    if cfg.analisis.reportar_mks:
        lineas += ["", "### Equivalencias MKS", "", "| Viga | Estado límite | Demanda | Capacidad |", "|---|---|---:|---:|"]
        for tipo, checks in resultado.verificaciones.items():
            for check in checks:
                convertido = _check_mks(check)
                lineas.append(
                    f"| {tipo} | {check.nombre} | {convertido['demanda']:.4g} {convertido['unidad']} | {convertido['capacidad']:.4g} {convertido['unidad']} |"
                )
    lineas += [
        "",
        "## Resultado gobernante",
        "",
        f"Controla **{resultado.estado_gobernante.nombre}**, DCR = {resultado.estado_gobernante.dcr:.3f}.",
        "",
        "## Pendientes y limitaciones",
        "",
    ]
    lineas.extend(f"- {p}" for p in resultado.pendientes)
    lineas.extend(f"- {a}" for a in resultado.advertencias)
    lineas += ["", "Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.", ""]
    return "\n".join(lineas)

"""API pública de análisis, verificación y búsqueda discreta."""

from __future__ import annotations

import itertools
from dataclasses import dataclass

from .analisis.motor import ResultadoAnalisis, analizar_configuracion
from .analisis.parrilla import ResultadoParrilla, analizar_parrilla
from .analisis.secciones import propiedades_acero
from .diseno.verificaciones import ResultadoDiseno, verificar_analisis
from .modelos import Configuracion, GrupoBusqueda, SegmentoViga


@dataclass(frozen=True)
class Alternativa:
    masa_kg: float
    maximo_dcr: float
    estado: str
    segmentos: tuple[SegmentoViga, ...]
    resultado: ResultadoDiseno


@dataclass(frozen=True)
class ResultadoBusqueda:
    factibles: tuple[Alternativa, ...]
    mejores_no_factibles: tuple[Alternativa, ...]
    evaluados: int
    truncado: bool


def analizar(configuracion: Configuracion) -> ResultadoAnalisis:
    return analizar_configuracion(configuracion)


def analizar_distribucion_parrilla(configuracion: Configuracion) -> ResultadoParrilla:
    """Ejecuta únicamente el modelo refinado de distribución transversal."""
    return analizar_parrilla(configuracion)


def verificar(configuracion: Configuracion, analisis: ResultadoAnalisis | None = None) -> ResultadoDiseno:
    return verificar_analisis(analisis or analizar(configuracion))


def _masa(config: Configuracion) -> float:
    return sum(
        propiedades_acero(s).masa_lineal_kg_m * (s.x_fin - s.x_inicio)
        for s in config.viga.segmentos
    )


def _dimensiones(busqueda) -> list[tuple[float, float, float, float, float, float]]:
    listas = (
        busqueda.peraltes_alma,
        busqueda.espesores_alma,
        busqueda.anchos_ala_superior,
        busqueda.espesores_ala_superior,
        busqueda.anchos_ala_inferior,
        busqueda.espesores_ala_inferior,
    )
    if any(not valores for valores in listas):
        raise ValueError("la búsqueda requiere las seis listas de dimensiones")
    return list(itertools.product(*listas))


def _prefiltro(d: tuple[float, ...], fy: float, es: float) -> bool:
    hw, tw, bts, tts, bti, tti = d
    if hw / tw > 200.0:
        return False
    limite_ala = 0.56 * (es / fy) ** 0.5
    return bts / (2.0 * tts) <= limite_ala and bti / (2.0 * tti) <= limite_ala


def buscar_secciones(configuracion: Configuracion) -> ResultadoBusqueda:
    b = configuracion.busqueda
    if not b.habilitada:
        raise ValueError("busqueda.habilitada debe ser true")
    dimensiones = [d for d in _dimensiones(b) if _prefiltro(d, configuracion.materiales.acero_estructural.fy, configuracion.materiales.acero_estructural.es)]
    grupos = b.grupos or (GrupoBusqueda(segmentos=tuple(range(len(configuracion.viga.segmentos)))),)
    combinaciones = itertools.product(dimensiones, repeat=len(grupos))
    factibles: list[Alternativa] = []
    no_factibles: list[Alternativa] = []
    evaluados = 0
    truncado = False
    for seleccion in combinaciones:
        if evaluados >= b.maximo_candidatos:
            truncado = True
            break
        nuevos = list(configuracion.viga.segmentos)
        for grupo, dims in zip(grupos, seleccion):
            for indice in grupo.segmentos:
                original = nuevos[indice]
                nuevos[indice] = original.model_copy(
                    update={
                        "altura_alma": dims[0],
                        "espesor_alma": dims[1],
                        "ancho_ala_superior": dims[2],
                        "espesor_ala_superior": dims[3],
                        "ancho_ala_inferior": dims[4],
                        "espesor_ala_inferior": dims[5],
                    }
                )
        cfg = configuracion.model_copy(
            update={"viga": configuracion.viga.model_copy(update={"segmentos": tuple(nuevos)})}
        )
        resultado = verificar(cfg)
        alternativa = Alternativa(
            masa_kg=_masa(cfg),
            maximo_dcr=resultado.estado_gobernante.dcr,
            estado=resultado.estado,
            segmentos=tuple(nuevos),
            resultado=resultado,
        )
        if all(c.cumple for checks in resultado.verificaciones.values() for c in checks):
            factibles.append(alternativa)
        else:
            no_factibles.append(alternativa)
        evaluados += 1
    factibles.sort(key=lambda a: (a.masa_kg, a.maximo_dcr, tuple(s.nombre for s in a.segmentos)))
    no_factibles.sort(key=lambda a: (a.maximo_dcr, a.masa_kg))
    return ResultadoBusqueda(
        factibles=tuple(factibles[: b.mejores_alternativas]),
        mejores_no_factibles=tuple(no_factibles[: b.mejores_alternativas]),
        evaluados=evaluados,
        truncado=truncado,
    )

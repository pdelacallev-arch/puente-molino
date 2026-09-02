"""Propiedades de vigas I y secciones compuestas transformadas."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from ..modelos import Configuracion, SegmentoViga


@dataclass(frozen=True)
class PropiedadesAcero:
    area: float
    inercia_x: float
    y_inferior: float
    y_superior: float
    modulo_inferior: float
    modulo_superior: float
    altura_total: float
    masa_lineal_kg_m: float

    def a_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class PropiedadesCompuestas:
    area_transformada: float
    inercia_x: float
    eje_neutro: float
    modulo_acero_inferior: float
    modulo_acero_superior: float
    modulo_losa_superior_transformado: float
    relacion_modular: float
    ancho_efectivo: float
    altura_total: float

    def a_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class ResultadoPlastico:
    momento_plastico: float
    eje_neutro_plastico: float
    dp_sobre_dt: float
    alma_compresion_plastica: float

    def a_dict(self) -> dict[str, float]:
        return asdict(self)


def propiedades_acero(segmento: SegmentoViga, densidad_kg_m3: float = 7850.0) -> PropiedadesAcero:
    """Calcula A, Ix y modulos de una I armada; dimensiones en mm."""
    hw = segmento.altura_alma
    tw = segmento.espesor_alma
    bts = segmento.ancho_ala_superior
    tts = segmento.espesor_ala_superior
    bti = segmento.ancho_ala_inferior
    tti = segmento.espesor_ala_inferior
    piezas = (
        (bti * tti, tti / 2.0, bti * tti**3 / 12.0),
        (tw * hw, tti + hw / 2.0, tw * hw**3 / 12.0),
        (bts * tts, tti + hw + tts / 2.0, bts * tts**3 / 12.0),
    )
    area = sum(p[0] for p in piezas)
    y_barra = sum(a * y for a, y, _ in piezas) / area
    inercia = sum(i0 + a * (y - y_barra) ** 2 for a, y, i0 in piezas)
    altura = tti + hw + tts
    masa = area * 1e-6 * densidad_kg_m3
    return PropiedadesAcero(
        area=area,
        inercia_x=inercia,
        y_inferior=y_barra,
        y_superior=altura - y_barra,
        modulo_inferior=inercia / y_barra,
        modulo_superior=inercia / (altura - y_barra),
        altura_total=altura,
        masa_lineal_kg_m=masa,
    )


def modulo_elasticidad_concreto(fc_mpa: float, peso_kN_m3: float) -> float:
    """MTC 2018 2.5.3: Ec=0.043*gamma^1.5*sqrt(fc), gamma en kg/m3."""
    densidad = peso_kN_m3 * 1000.0 / 9.80665
    return 0.043 * densidad**1.5 * fc_mpa**0.5


def ancho_efectivo(config: Configuracion, segmento: SegmentoViga, tipo: str) -> float:
    """Ancho efectivo en mm siguiendo el criterio usado por MTC/Bartra.

    Puede ser reemplazado por un ancho confirmado en el YAML. Para una viga
    exterior se suma media separacion y el voladizo efectivo.
    """
    g = config.geometria
    losa = config.losa
    L = g.luz * 1000.0
    S = g.separacion_vigas * 1000.0
    ts = losa.espesor * 1000.0
    bf = segmento.ancho_ala_superior
    tw = segmento.espesor_alma
    if tipo == "interior":
        if losa.ancho_efectivo_interior is not None:
            return losa.ancho_efectivo_interior * 1000.0
        return min(L / 4.0, S, 12.0 * ts + max(tw, bf / 2.0))
    if tipo != "exterior":
        raise ValueError("tipo debe ser interior o exterior")
    if losa.ancho_efectivo_exterior is not None:
        return losa.ancho_efectivo_exterior * 1000.0
    lado_exterior = min(
        L / 8.0,
        g.voladizo_exterior * 1000.0,
        6.0 * ts + max(tw / 2.0, bf / 4.0),
    )
    return S / 2.0 + lado_exterior


def propiedades_compuestas(
    segmento: SegmentoViga,
    acero: PropiedadesAcero,
    ancho_losa: float,
    espesor_losa: float,
    haunch: float,
    relacion_modular: float,
) -> PropiedadesCompuestas:
    """Transforma el concreto a acero y calcula propiedades elásticas en mm."""
    b_transformado = ancho_losa / relacion_modular
    area_losa = b_transformado * espesor_losa
    y_losa = acero.altura_total + haunch + espesor_losa / 2.0
    area_total = acero.area + area_losa
    y_barra = (acero.area * acero.y_inferior + area_losa * y_losa) / area_total
    i_losa = b_transformado * espesor_losa**3 / 12.0
    inercia = (
        acero.inercia_x
        + acero.area * (acero.y_inferior - y_barra) ** 2
        + i_losa
        + area_losa * (y_losa - y_barra) ** 2
    )
    altura_total = acero.altura_total + haunch + espesor_losa
    return PropiedadesCompuestas(
        area_transformada=area_total,
        inercia_x=inercia,
        eje_neutro=y_barra,
        modulo_acero_inferior=inercia / y_barra,
        modulo_acero_superior=inercia / abs(acero.altura_total - y_barra),
        modulo_losa_superior_transformado=inercia / (altura_total - y_barra),
        relacion_modular=relacion_modular,
        ancho_efectivo=ancho_losa,
        altura_total=altura_total,
    )


def momento_plastico_compuesto(
    segmento: SegmentoViga,
    ancho_losa: float,
    espesor_losa: float,
    haunch: float,
    fy: float,
    fc: float,
) -> ResultadoPlastico:
    """Equilibrio plástico de acero y bloque 0.85 f'c en flexión positiva."""
    tfi = segmento.espesor_ala_inferior
    hw = segmento.altura_alma
    tfs = segmento.espesor_ala_superior
    h_acero = tfi + hw + tfs
    h_total = h_acero + haunch + espesor_losa
    capas_acero = (
        (0.0, tfi, segmento.ancho_ala_inferior),
        (tfi, tfi + hw, segmento.espesor_alma),
        (tfi + hw, h_acero, segmento.ancho_ala_superior),
    )

    def fuerza_neta(pna: float) -> float:
        tension = 0.0
        compresion = 0.0
        for y0, y1, ancho in capas_acero:
            bajo = max(0.0, min(y1, pna) - y0)
            sobre = max(0.0, y1 - max(y0, pna))
            tension += bajo * ancho * fy
            compresion += sobre * ancho * fy
        profundidad_concreto = max(0.0, h_total - max(pna, h_acero + haunch))
        compresion += 0.85 * fc * ancho_losa * profundidad_concreto
        return tension - compresion

    inferior, superior = 0.0, h_total
    for _ in range(100):
        medio = (inferior + superior) / 2.0
        if fuerza_neta(medio) > 0.0:
            superior = medio
        else:
            inferior = medio
    pna = (inferior + superior) / 2.0
    momento = 0.0
    for y0, y1, ancho in capas_acero:
        if pna > y0:
            ya = y0
            yb = min(y1, pna)
            if yb > ya:
                fuerza = (yb - ya) * ancho * fy
                momento += fuerza * abs((ya + yb) / 2.0 - pna)
        if pna < y1:
            ya = max(y0, pna)
            yb = y1
            if yb > ya:
                fuerza = (yb - ya) * ancho * fy
                momento += fuerza * abs((ya + yb) / 2.0 - pna)
    y0c = max(pna, h_acero + haunch)
    if h_total > y0c:
        fuerza_c = 0.85 * fc * ancho_losa * (h_total - y0c)
        momento += fuerza_c * abs((y0c + h_total) / 2.0 - pna)
    dp = max(0.0, h_total - pna)
    return ResultadoPlastico(
        momento_plastico=momento,
        eje_neutro_plastico=pna,
        dp_sobre_dt=dp / h_total,
        alma_compresion_plastica=max(0.0, min(hw, tfi + hw - pna)),
    )


def propiedades_por_segmento(config: Configuracion, tipo: str) -> list[dict]:
    concreto = config.materiales.concreto
    estructural = config.materiales.acero_estructural
    ec = concreto.ec or modulo_elasticidad_concreto(concreto.fc, concreto.peso_unitario)
    n = estructural.es / ec
    resultados: list[dict] = []
    for segmento in config.viga.segmentos:
        acero = propiedades_acero(segmento)
        be = ancho_efectivo(config, segmento, tipo)
        corto = propiedades_compuestas(
            segmento,
            acero,
            be,
            config.losa.espesor * 1000.0,
            config.losa.haunch * 1000.0,
            n,
        )
        largo = propiedades_compuestas(
            segmento,
            acero,
            be,
            config.losa.espesor * 1000.0,
            config.losa.haunch * 1000.0,
            n * config.losa.factor_largo_plazo,
        )
        plastico = momento_plastico_compuesto(
            segmento,
            be,
            config.losa.espesor * 1000.0,
            config.losa.haunch * 1000.0,
            estructural.fy,
            concreto.fc,
        )
        resultados.append(
            {
                "segmento": segmento.nombre,
                "acero": acero,
                "corto_plazo": corto,
                "largo_plazo": largo,
                "plastico": plastico,
                "ancho_efectivo_mm": be,
                "ec_mpa": ec,
                "n": n,
            }
        )
    return resultados

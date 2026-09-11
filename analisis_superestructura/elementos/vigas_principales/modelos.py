"""Modelos tipados de entrada y salida de las vigas principales.

Las entradas usan unidades de ingenieria declaradas por ``sistema_unidades``.
El cargador las convierte a SI de ingenieria (m, kN, MPa); el motor numerico
convierte despues a N-mm-MPa para evitar mezclas dimensionales.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Modelo(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Proyecto(Modelo):
    id: str
    nombre: str
    revision: str = "R00"
    responsable: str = "Pendiente"
    sistema_unidades: Literal["SI", "MKS"] = "SI"


class Normativa(Modelo):
    manual: str = "Manual de Puentes MTC"
    edicion: int = 2018
    base_aashto: str = "AASHTO LRFD 2014, 7a ed., Interim 2015"


class Geometria(Modelo):
    luz: float = Field(gt=0, description="m")
    numero_vigas: int = Field(ge=2)
    separacion_vigas: float = Field(gt=0, description="m")
    ancho_calzada: float = Field(gt=0, description="m")
    ancho_veredas_total: float = Field(ge=0, description="m")
    ancho_tablero: float = Field(gt=0, description="m")
    voladizo_exterior: float = Field(ge=0, description="distancia viga-borde de losa, m")
    distancia_borde_calzada_viga_exterior: float = Field(
        ge=0, description="distancia borde de calzada-eje de viga exterior, m"
    )
    numero_carriles: int = Field(ge=1)

    @model_validator(mode="after")
    def validar_ancho(self) -> "Geometria":
        if self.ancho_calzada + self.ancho_veredas_total > self.ancho_tablero + 1e-9:
            raise ValueError("calzada + veredas no puede superar el ancho del tablero")
        return self


class Losa(Modelo):
    espesor: float = Field(gt=0, description="m")
    haunch: float = Field(ge=0, description="m")
    ancho_haunch: float | None = Field(default=None, gt=0, description="m")
    ancho_efectivo_interior: float | None = Field(default=None, gt=0)
    ancho_efectivo_exterior: float | None = Field(default=None, gt=0)
    factor_largo_plazo: float = Field(default=3.0, ge=1.0)


class Concreto(Modelo):
    fc: float = Field(gt=0, description="MPa o kgf/cm2")
    ec: float | None = Field(default=None, gt=0, description="MPa o kgf/cm2")
    peso_unitario: float = Field(default=24.0, gt=0, description="kN/m3 o tf/m3")


class AceroEstructural(Modelo):
    fy: float = Field(gt=0, description="MPa o kgf/cm2")
    fu: float = Field(gt=0, description="MPa o kgf/cm2")
    es: float = Field(default=200_000.0, gt=0, description="MPa o kgf/cm2")
    peso_unitario: float = Field(default=77.0, gt=0, description="kN/m3 o tf/m3")
    grado: str = "ASTM A709 Gr. 50"


class AceroRefuerzo(Modelo):
    fy: float = Field(default=420.0, gt=0)
    es: float = Field(default=200_000.0, gt=0)


class Materiales(Modelo):
    concreto: Concreto
    acero_estructural: AceroEstructural
    acero_refuerzo: AceroRefuerzo = AceroRefuerzo()


class SegmentoViga(Modelo):
    nombre: str
    x_inicio: float = Field(ge=0, description="m")
    x_fin: float = Field(gt=0, description="m")
    altura_alma: float = Field(gt=0, description="mm")
    espesor_alma: float = Field(gt=0, description="mm")
    ancho_ala_superior: float = Field(gt=0, description="mm")
    espesor_ala_superior: float = Field(gt=0, description="mm")
    ancho_ala_inferior: float = Field(gt=0, description="mm")
    espesor_ala_inferior: float = Field(gt=0, description="mm")

    @model_validator(mode="after")
    def validar_intervalo(self) -> "SegmentoViga":
        if self.x_fin <= self.x_inicio:
            raise ValueError("x_fin debe ser mayor que x_inicio")
        return self


class Viga(Modelo):
    segmentos: tuple[SegmentoViga, ...]
    categoria_fatiga: Literal[
        "A", "B", "B_PRIMA", "C", "C_PRIMA", "D", "E", "E_PRIMA"
    ] = "C"
    alma_rigidizada: bool = False
    separacion_rigidizadores: float | None = Field(default=None, gt=0, description="m")


class Arriostramiento(Modelo):
    posiciones: tuple[float, ...]
    confirmado: bool = False


class Construccion(Modelo):
    apuntalada: bool = False
    carga_construccion: float = Field(default=0.0, ge=0, description="kN/m o tf/m")
    incluir_losa_fresca: bool = True
    incluir_peso_propio_viga: bool = True


class CargaPorTipoViga(Modelo):
    """Carga lineal diferenciada para vigas interiores y exteriores."""

    interior: float = Field(ge=0, description="kN/m o tf/m")
    exterior: float = Field(ge=0, description="kN/m o tf/m")


class Cargas(Modelo):
    dc_no_compuesta_adicional: float | CargaPorTipoViga = Field(default=0.0)
    dc_compuesta: float | CargaPorTipoViga = Field(default=0.0)
    dw: float | CargaPorTipoViga = Field(default=0.0)
    pl: float | CargaPorTipoViga = Field(default=0.0)


class CamionDiseno(Modelo):
    eje_frontal: float = Field(default=35.0, gt=0, description="kN o tf")
    eje_posterior: float = Field(default=145.0, gt=0, description="kN o tf")
    separacion_frontal: float = Field(default=4.3, gt=0, description="m")
    separacion_posterior_min: float = Field(default=4.3, gt=0, description="m")
    separacion_posterior_max: float = Field(default=9.0, gt=0, description="m")


class Trafico(Modelo):
    camion: CamionDiseno = CamionDiseno()
    tandem_eje: float = Field(default=110.0, gt=0, description="kN o tf")
    separacion_tandem: float = Field(default=1.2, gt=0, description="m")
    carga_carril: float = Field(default=9.3, gt=0, description="kN/m o tf/m")
    incremento_dinamico: float = Field(default=0.33, ge=0)
    incremento_dinamico_fatiga: float = Field(default=0.15, ge=0)
    adtt_carril: float = Field(default=1000.0, ge=0)
    factor_distribucion_momento_interior: float | None = Field(default=None, gt=0)
    factor_distribucion_momento_exterior: float | None = Field(default=None, gt=0)
    factor_distribucion_corte_interior: float | None = Field(default=None, gt=0)
    factor_distribucion_corte_exterior: float | None = Field(default=None, gt=0)
    factor_distribucion_fatiga_interior: float | None = Field(default=None, gt=0)
    factor_distribucion_fatiga_exterior: float | None = Field(default=None, gt=0)


class FactoresCombinacion(Modelo):
    resistencia_dc: float = 1.25
    resistencia_dw: float = 1.50
    resistencia_ll: float = 1.75
    resistencia_pl: float = 1.75
    servicio_dc: float = 1.00
    servicio_dw: float = 1.00
    servicio_ll: float = 1.30
    servicio_pl: float = 1.00
    fatiga_i: float = 1.75
    fatiga_ii: float = 0.80


class ParrillaConfig(Modelo):
    """Opciones del modelo refinado de distribución transversal."""

    numero_tramos_longitudinales: int = Field(default=20, ge=4, le=200)
    paso_posicion_transversal: float = Field(default=0.10, gt=0, description="m")
    paso_busqueda_longitudinal: float = Field(default=0.25, gt=0, description="m")
    ancho_carril_diseno: float = Field(default=3.0, gt=0, description="m")
    separacion_lineas_rueda: float = Field(default=1.80, gt=0, description="m")
    factor_presencia_multiple: float = Field(default=1.20, gt=0)
    coeficiente_poisson_concreto: float = Field(default=0.20, ge=0, lt=0.50)
    coeficiente_poisson_acero: float = Field(default=0.30, ge=0, lt=0.50)
    factor_rigidez_flexion_transversal: float = Field(default=1.0, gt=0)
    factor_rigidez_torsional: float = Field(default=1.0, gt=0)
    puntos_integracion_carga_carril: int = Field(default=5, ge=1, le=21)

    @model_validator(mode="after")
    def validar_carril(self) -> "ParrillaConfig":
        if self.separacion_lineas_rueda > self.ancho_carril_diseno:
            raise ValueError(
                "parrilla.separacion_lineas_rueda no puede superar el ancho del carril"
            )
        return self


class AnalisisConfig(Modelo):
    numero_estaciones: int = Field(default=101, ge=21)
    paso_vehiculo: float = Field(default=0.10, gt=0, description="m")
    paso_separacion_ejes: float = Field(default=0.30, gt=0, description="m")
    metodo_distribucion: Literal["aproximado", "parrilla"] = "aproximado"
    parrilla: ParrillaConfig = ParrillaConfig()
    factores: FactoresCombinacion = FactoresCombinacion()
    tolerancia_equilibrio: float = Field(default=1e-8, gt=0)
    limite_deflexion_divisor: float = Field(default=800.0, gt=0)
    reportar_mks: bool = False


class GrupoBusqueda(Modelo):
    segmentos: tuple[int, ...]


class Busqueda(Modelo):
    habilitada: bool = False
    peraltes_alma: tuple[float, ...] = ()
    espesores_alma: tuple[float, ...] = ()
    anchos_ala_superior: tuple[float, ...] = ()
    espesores_ala_superior: tuple[float, ...] = ()
    anchos_ala_inferior: tuple[float, ...] = ()
    espesores_ala_inferior: tuple[float, ...] = ()
    grupos: tuple[GrupoBusqueda, ...] = ()
    maximo_candidatos: int = Field(default=20_000, ge=1)
    mejores_alternativas: int = Field(default=10, ge=1, le=100)


class ValidacionesExternas(Modelo):
    conectores_confirmados: bool = False
    rigidizadores_confirmados: bool = False
    arriostramiento_confirmado: bool = False


class Configuracion(Modelo):
    proyecto: Proyecto
    normativa: Normativa = Normativa()
    geometria: Geometria
    losa: Losa
    materiales: Materiales
    viga: Viga
    arriostramiento: Arriostramiento
    construccion: Construccion = Construccion()
    cargas: Cargas = Cargas()
    trafico: Trafico = Trafico()
    analisis: AnalisisConfig = AnalisisConfig()
    busqueda: Busqueda = Busqueda()
    validaciones_externas: ValidacionesExternas = ValidacionesExternas()
    fuentes: dict[str, str] = Field(default_factory=dict)
    estados_datos: dict[str, Literal["confirmado", "calculado", "asumido", "pendiente"]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validar_sistema(self) -> "Configuracion":
        if self.normativa.edicion != 2018:
            raise ValueError("esta version implementa exclusivamente MTC 2018")
        segmentos = sorted(self.viga.segmentos, key=lambda s: s.x_inicio)
        if not segmentos:
            raise ValueError("se requiere al menos un segmento de viga")
        if abs(segmentos[0].x_inicio) > 1e-9:
            raise ValueError("el primer segmento debe iniciar en x=0")
        if abs(segmentos[-1].x_fin - self.geometria.luz) > 1e-8:
            raise ValueError("los segmentos deben cubrir toda la luz")
        for anterior, siguiente in zip(segmentos, segmentos[1:]):
            if abs(anterior.x_fin - siguiente.x_inicio) > 1e-8:
                raise ValueError("los segmentos deben ser contiguos y no superponerse")
        posiciones = self.arriostramiento.posiciones
        if len(posiciones) < 2 or abs(posiciones[0]) > 1e-9 or abs(posiciones[-1] - self.geometria.luz) > 1e-8:
            raise ValueError("arriostramiento.posiciones debe incluir 0 y la luz")
        if tuple(sorted(posiciones)) != posiciones:
            raise ValueError("las posiciones de arriostramiento deben estar ordenadas")
        return self


class EstadoVerificacion(Modelo):
    nombre: str
    demanda: float
    capacidad: float
    dcr: float
    cumple: bool
    unidad: str
    referencia: str
    observacion: str = ""

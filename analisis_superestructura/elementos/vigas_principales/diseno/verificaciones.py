"""Verificaciones de viga principal conforme al alcance vigente."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..analisis.motor import ResultadoAnalisis
from ..analisis.respuesta import valor_segmentado
from ..modelos import EstadoVerificacion
from ..normativa import CAFL_MPA, REFERENCIAS_MTC_2018


@dataclass(frozen=True)
class ResultadoDiseno:
    analisis: ResultadoAnalisis
    estado: str
    verificaciones: dict[str, tuple[EstadoVerificacion, ...]]
    estado_gobernante: EstadoVerificacion
    pendientes: tuple[str, ...]
    advertencias: tuple[str, ...]


def _estado(nombre: str, demanda: float, capacidad: float, unidad: str, referencia: str, observacion: str = "") -> EstadoVerificacion:
    dcr = demanda / capacidad if capacidad > 0.0 else float("inf")
    return EstadoVerificacion(
        nombre=nombre,
        demanda=demanda,
        capacidad=capacidad,
        dcr=dcr,
        cumple=dcr <= 1.0 + 1e-12,
        unidad=unidad,
        referencia=referencia,
        observacion=observacion,
    )


def _longitud_no_arriostrada(config, x_centro_m: float) -> float:
    posiciones = config.arriostramiento.posiciones
    for a, b in zip(posiciones, posiciones[1:]):
        if a <= x_centro_m <= b:
            return (b - a) * 1000.0
    return max(np.diff(posiciones)) * 1000.0


def verificar_analisis(analisis: ResultadoAnalisis) -> ResultadoDiseno:
    config = analisis.configuracion
    fy = config.materiales.acero_estructural.fy
    es = config.materiales.acero_estructural.es
    verificaciones: dict[str, tuple[EstadoVerificacion, ...]] = {}
    todas: list[EstadoVerificacion] = []
    advertencias = list(analisis.advertencias)
    for tipo, datos in analisis.tipos_viga.items():
        x = analisis.x_mm
        props = datos["propiedades"]
        segmentos = config.viga.segmentos
        mp = valor_segmentado(x, segmentos, [p["plastico"].momento_plastico for p in props])
        razon_dp = valor_segmentado(x, segmentos, [p["plastico"].dp_sobre_dt for p in props])
        reduccion_ductilidad = np.minimum(1.0, np.where(razon_dp <= 0.10, 1.0, 1.07 - 0.70 * razon_dp))
        capacidad_m = mp * np.maximum(0.0, reduccion_ductilidad)
        m_res = datos["momentos_nmm"]["resistencia_i"]
        idx_m = int(np.argmax(m_res / capacidad_m))
        checks: list[EstadoVerificacion] = [
            _estado(
                "Flexión positiva - Resistencia I",
                float(m_res[idx_m]) / 1e6,
                float(capacidad_m[idx_m]) / 1e6,
                "kN.m",
                REFERENCIAS_MTC_2018["flexion"],
                f"Sección x={x[idx_m]/1000:.3f} m; reducción por ductilidad incluida.",
            )
        ]
        # Ductilidad y compacidad del alma en el estado plástico.
        idx_dp = int(np.argmax(razon_dp))
        checks.append(
            _estado(
                "Ductilidad Dp/Dt",
                float(razon_dp[idx_dp]),
                0.42,
                "-",
                REFERENCIAS_MTC_2018["flexion"],
            )
        )
        esbeltez_real = []
        esbeltez_limite = []
        for seg, prop in zip(segmentos, props):
            dcp = prop["plastico"].alma_compresion_plastica
            esbeltez_real.append(2.0 * dcp / seg.espesor_alma)
            esbeltez_limite.append(3.76 * (es / fy) ** 0.5)
        i_esb = int(np.argmax(np.array(esbeltez_real) / np.array(esbeltez_limite)))
        checks.append(
            _estado(
                "Compacidad del alma en flexión positiva",
                esbeltez_real[i_esb],
                esbeltez_limite[i_esb],
                "-",
                REFERENCIAS_MTC_2018["flexion"],
                f"Segmento {segmentos[i_esb].nombre}.",
            )
        )
        # Corte del alma: modelo de alma no rigidizada, k=5; si se declara
        # rigidizada se mantiene este valor conservador hasta validar paneles.
        capacidades_v = []
        for seg in segmentos:
            esbeltez = seg.altura_alma / seg.espesor_alma
            k = 5.0
            lp = 1.12 * (es * k / fy) ** 0.5
            lr = 1.40 * (es * k / fy) ** 0.5
            if esbeltez <= lp:
                c = 1.0
            elif esbeltez <= lr:
                c = lp / esbeltez
            else:
                c = 1.57 * es * k / (fy * esbeltez**2)
            capacidades_v.append(0.58 * fy * seg.altura_alma * seg.espesor_alma * c)
        cap_v = valor_segmentado(x, segmentos, capacidades_v)
        v_res = datos["cortantes_n"]["resistencia_i_abs"]
        idx_v = int(np.argmax(v_res / cap_v))
        checks.append(
            _estado(
                "Corte del alma",
                float(v_res[idx_v]) / 1000.0,
                float(cap_v[idx_v]) / 1000.0,
                "kN",
                REFERENCIAS_MTC_2018["corte"],
                "Capacidad conservadora sin acción de campo de tensión.",
            )
        )
        # Esfuerzos elásticos acumulados por secuencia de carga.
        s_acero_sup = valor_segmentado(x, segmentos, [p["acero"].modulo_superior for p in props])
        s_acero_inf = valor_segmentado(x, segmentos, [p["acero"].modulo_inferior for p in props])
        s_largo_sup = valor_segmentado(x, segmentos, [abs(p["largo_plazo"].modulo_acero_superior) for p in props])
        s_largo_inf = valor_segmentado(x, segmentos, [p["largo_plazo"].modulo_acero_inferior for p in props])
        s_corto_sup = valor_segmentado(x, segmentos, [abs(p["corto_plazo"].modulo_acero_superior) for p in props])
        s_corto_inf = valor_segmentado(x, segmentos, [p["corto_plazo"].modulo_acero_inferior for p in props])
        momentos = datos["momentos_nmm"]
        sigma_sup = (
            momentos["DC_no_compuesta"] / s_acero_sup
            + (momentos["DC_compuesta"] + momentos["DW"]) / s_largo_sup
            + 1.30 * momentos["LL_IM"] / s_corto_sup
            + momentos["PL"] / s_largo_sup
        )
        sigma_inf = (
            momentos["DC_no_compuesta"] / s_acero_inf
            + (momentos["DC_compuesta"] + momentos["DW"]) / s_largo_inf
            + 1.30 * momentos["LL_IM"] / s_corto_inf
            + momentos["PL"] / s_largo_inf
        )
        sigma_serv = np.maximum(np.abs(sigma_sup), np.abs(sigma_inf))
        idx_s = int(np.argmax(sigma_serv))
        checks.append(
            _estado(
                "Esfuerzo elástico - Servicio II",
                float(sigma_serv[idx_s]),
                0.95 * fy,
                "MPa",
                REFERENCIAS_MTC_2018["servicio"],
                "Superposición explícita de etapas no compuesta, largo y corto plazo.",
            )
        )
        # Fatiga de la fibra extrema de acero; la categoría debe representar el detalle real.
        rango_sigma = np.maximum(
            momentos["fatiga_rango"] / s_corto_sup,
            momentos["fatiga_rango"] / s_corto_inf,
        ) * config.analisis.factores.fatiga_i
        idx_f = int(np.argmax(rango_sigma))
        checks.append(
            _estado(
                f"Fatiga categoría {config.viga.categoria_fatiga}",
                float(rango_sigma[idx_f]),
                CAFL_MPA[config.viga.categoria_fatiga],
                "MPa",
                REFERENCIAS_MTC_2018["fatiga"],
                "Chequeo contra umbral de amplitud constante; confirmar categoría del detalle.",
            )
        )
        # Estabilidad de construcción: cribado elástico conservador del ala comprimida.
        m_nc = momentos["DC_no_compuesta"]
        ratios_ltb = np.zeros_like(x)
        caps_ltb = np.zeros_like(x)
        for i, xi in enumerate(x):
            j = next(k for k, s in enumerate(segmentos) if s.x_inicio * 1000.0 - 1e-8 <= xi <= s.x_fin * 1000.0 + 1e-8)
            seg = segmentos[j]
            lb = _longitud_no_arriostrada(config, xi / 1000.0)
            rt = seg.ancho_ala_superior / 12.0**0.5
            fcr = min(fy, np.pi**2 * es / max((lb / rt) ** 2, 1.0))
            caps_ltb[i] = fcr * props[j]["acero"].modulo_superior
            ratios_ltb[i] = m_nc[i] / caps_ltb[i] if caps_ltb[i] > 0 else np.inf
        idx_ltb = int(np.argmax(ratios_ltb))
        checks.append(
            _estado(
                "Estabilidad lateral durante construcción",
                float(m_nc[idx_ltb]) / 1e6,
                float(caps_ltb[idx_ltb]) / 1e6,
                "kN.m",
                REFERENCIAS_MTC_2018["construibilidad"],
                "Cribado elástico conservador con Cb=1.0; requiere confirmación del arriostramiento temporal.",
            )
        )
        def_ll = datos["deflexiones_mm"]["LL_IM_critica"]
        idx_d = int(np.argmax(np.abs(def_ll)))
        checks.append(
            _estado(
                "Deflexión por carga viva",
                float(abs(def_ll[idx_d])),
                config.geometria.luz * 1000.0 / config.analisis.limite_deflexion_divisor,
                "mm",
                REFERENCIAS_MTC_2018["servicio"],
                f"Límite configurable L/{config.analisis.limite_deflexion_divisor:g}.",
            )
        )
        verificaciones[tipo] = tuple(checks)
        todas.extend(checks)
    gobernante = max(todas, key=lambda c: c.dcr)
    pendientes: list[str] = []
    ext = config.validaciones_externas
    if not ext.conectores_confirmados:
        pendientes.append("Acción compuesta condicionada a la verificación externa de conectores.")
    if not ext.rigidizadores_confirmados:
        pendientes.append("Rigidizadores de apoyo/intermedios fuera de alcance y pendientes de confirmación.")
    if not ext.arriostramiento_confirmado or not config.arriostramiento.confirmado:
        pendientes.append("Arriostramiento permanente y temporal pendiente de confirmación externa.")
    if any(not c.cumple for c in todas):
        estado = "NO_CUMPLE"
    elif pendientes:
        estado = "CONDICIONAL"
    else:
        estado = "CUMPLE"
    if config.viga.alma_rigidizada:
        advertencias.append(
            "El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión."
        )
    return ResultadoDiseno(
        analisis=analisis,
        estado=estado,
        verificaciones=verificaciones,
        estado_gobernante=gobernante,
        pendientes=tuple(pendientes),
        advertencias=tuple(advertencias),
    )

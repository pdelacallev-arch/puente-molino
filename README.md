# Puente Molinohuaico — Diseño de Zapata Izquierda

**Ubicación:** Ayacucho, Perú  
**Tipo:** Puente — Estribo de concreto armado en voladizo (cantilever)  
**Elemento:** Subestructura — Zapata izquierda (cimentación)  
**Fase:** Diseño  
**Estado:** En desarrollo y verificación

## Normas y ediciones aplicables

| Ámbito | Norma | Edición |
|---|---|---|
| Cargas | AASHTO LRFD | 2005 |
| Cargas (complemento) | MTC Manual de Puentes | 2018 |
| Materiales (concreto) | ACI 318 | 2019 |
| Materiales (concreto) | Norma E.060 | — |
| Sismo | Norma E.030 / MTC Anexo I | — |
| Geotecnia | Estudio de Suelos GW φ'=39.8° | — |

## Sistema de unidades

MKS: t, m, t-m, kg/cm²

## Herramientas previstas

- Python 3 (scripts de verificación)
- Markdown (memoria de cálculo)

## Estructura del repositorio

```
├── README.md
├── analisis_estabilidad/    # Subsistema autocontenido por elementos estructurales
├── metrado_cargas/          # Metrados y cargas de la superestructura
├── tests/                   # Pruebas automatizadas de los cálculos
├── herramientas/            # Renderizado y verificación de documentos
│   ├── documentos/
│   └── verificacion/
├── fuentes/                 # Registro y trazabilidad de fuentes
├── normativa/               # Normativa y criterios de diseño
├── referencias/             # Bibliografía y documentos de consulta
├── estudio_suelos/          # Estudios geotécnicos
├── estudio_hidrologico/     # Estudios hidrológicos e hidráulicos
├── memoria_estructuras/     # Memorias estructurales recibidas
├── plantillas/              # Plantillas DOCX
├── imagenes/                # Imágenes empleadas en informes
├── panel_foto/              # Fotografías de campo
├── informes_actividades/    # Informes periódicos de actividades
├── informes_rfis/           # Informes de remisión y seguimiento de RFI
├── entregables/             # Documentos en preparación o emitidos
└── outputs/                 # Resultados de subsistemas externos a estabilidad
```

La carpeta `salidas/` conserva resultados históricos de trabajo. Los cálculos
nuevos deben escribirse en `outputs/<identificador>/` para mantener trazabilidad.

## Ubicación de archivos clave

| Contenido | Ruta |
|---|---|
| Registro de fuentes | `fuentes/registro_fuentes.csv` |
| Análisis de estabilidad | `analisis_estabilidad/README.md` |
| Parámetros de referencia | `analisis_estabilidad/parametros_referencia_analisis_subestructura.txt` |
| Parámetros sísmicos | `analisis_estabilidad/parametros_sismicos_mtc_2018.md` |
| Guía de verificación | `analisis_estabilidad/guia_verificacion_estabilidad.md` |
| Herramientas documentales | `herramientas/README.md` |

## Verificación rápida

Desde la raíz del proyecto:

```bash
python -m pytest -q
python -m analisis_estabilidad validar --caso molinohuayco --revision R00
python -m analisis_estabilidad ejecutar zapata.longitudinal --caso molinohuayco --revision R00
```

Los antiguos comandos `python render_*.py` y `python verificar*.py` se mantienen
como accesos compatibles; las implementaciones se encuentran organizadas en
`herramientas/`.

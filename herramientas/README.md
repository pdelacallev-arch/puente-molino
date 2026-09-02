# Herramientas auxiliares

Esta carpeta agrupa utilidades que producen o verifican documentos, separadas
de los scripts de cálculo estructural.

## Renderizado

Las implementaciones están en `herramientas/documentos/`:

- `render_calc.py`: memoria de cálculo.
- `render_ies.py`: informe de estado situacional.
- `render_informe_rfi.py`: informe de remisión de RFI.
- `render_panel_foto.py`: panel fotográfico.
- `render_rfi.py`: documento RFI.

Pueden ejecutarse como módulos desde la raíz:

```bash
python -m herramientas.documentos.render_calc
python -m herramientas.documentos.render_ies
```

También se conservan los comandos históricos, por ejemplo
`python render_calc.py`, para no romper automatizaciones existentes.

## Verificación

Las comprobaciones de documentos DOCX están en `herramientas/verificacion/`.
Los accesos históricos `python verificar.py`, `python verificar_calc.py` y
`python verificar_rfi.py` siguen disponibles.

Todas las rutas se resuelven respecto de la raíz del repositorio; las
utilidades ya no dependen de la ubicación absoluta del proyecto en el equipo.

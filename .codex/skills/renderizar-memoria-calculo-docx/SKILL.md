---
name: renderizar-memoria-calculo-docx
description: "Renderiza y verifica memorias de cálculo estructural del proyecto desde Markdown a DOCX, conservando tablas, imágenes y fórmulas LaTeX como ecuaciones OMML nativas de Word. Usar únicamente cuando el usuario solicite expresamente un DOCX, su renderizado o su verificación visual."
---

# Renderizar memoria de cálculo DOCX

Generar el DOCX con el renderizador y la plantilla versionados del proyecto únicamente cuando el usuario solicite expresamente el DOCX, su renderizado o su verificación visual. La creación o actualización de una memoria `CALC-EST-*.md`, por sí sola, no activa este skill ni obliga a generar un DOCX. Conservar el Markdown fuente sin cambios salvo que el usuario pida corregir su contenido.

## Flujo obligatorio

1. Resolver todas las rutas de imágenes respecto de la carpeta del Markdown. Detenerse si alguna no existe.
2. Renderizar desde la raíz del proyecto:

```powershell
uv run --with python-docx --with lxml --with matplotlib python render_calc.py --input "ruta\CALC-EST-AAAA-NNN-R00.md" --output "ruta\CALC-EST-AAAA-NNN-R00.docx"
```

Usar `plantillas/plantilla_IES2.docx` por defecto. Pasar `--template` solo cuando el usuario solicite otra plantilla.

3. Ejecutar la verificación estructural del skill:

```powershell
uv run --no-project python .codex\skills\renderizar-memoria-calculo-docx\scripts\verificar_calc_docx.py "ruta\CALC-EST-AAAA-NNN-R00.md" "ruta\CALC-EST-AAAA-NNN-R00.docx"
```

Exigir coincidencia exacta entre las imágenes del Markdown y los dibujos del cuerpo del DOCX, y entre las expresiones LaTeX y los objetos OMML. Rechazar delimitadores `$...$`, comandos LaTeX, comillas invertidas u otros marcadores Markdown visibles.

4. Renderizar el DOCX a PNG con el skill `documents` y `render_docx.py --emit_pdf`. Localizar el script si cambió la ruta versionada. Si LibreOffice no está disponible, usar Word en segundo plano para exportar a PDF y convertir todas las páginas a PNG; declarar el impedimento si tampoco está disponible.
5. Inspeccionar todas las páginas al 100 %. Verificar imágenes nítidas y sin recortes, ecuaciones completas, tablas sin desborde, títulos junto a su contenido y encabezados/pies dentro de los márgenes.
6. Corregir y repetir las verificaciones estructural y visual hasta eliminar los defectos. Entregar el DOCX además del Markdown cuando el usuario haya solicitado ambos; si solicitó únicamente el DOCX, entregar únicamente el DOCX salvo que pida los archivos de QA.

## Reglas fijas

- Usar A4 vertical, márgenes de 2.5 cm, Calibri 11 e interlineado 1.15 conforme a `plantillas/confi_aspecto.txt`.
- Insertar ecuaciones como OMML nativo; no usar capturas de fórmulas ni dejar LaTeX literal.
- Insertar imágenes en línea, centradas y con ancho máximo de 14 cm.
- Mantener encabezados de tabla repetibles y evitar dividir filas.
- No declarar éxito basándose solo en que se creó el archivo: exigir verificación estructural y visual.

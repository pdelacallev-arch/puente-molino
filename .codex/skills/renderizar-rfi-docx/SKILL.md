---
name: renderizar-rfi-docx
description: "Renderiza y verifica solicitudes de información estructurales (RFI) del proyecto desde Markdown a DOCX. Usar al crear, actualizar o volver a renderizar archivos RFI-EST-*.md, especialmente cuando la solicitud debe ocupar exactamente la página 1 y el pronunciamiento exactamente la página 2."
---

# Renderizar RFI DOCX

Generar el DOCX con la plantilla y el renderizador versionados del proyecto. No clonar otro RFI ni usar una plantilla personal.

## Flujo obligatorio

1. Confirmar que el Markdown contiene un único separador `---` antes de `PRONUNCIAMIENTO DE LA SUPERVISIÓN`.
2. Renderizar desde la raíz del proyecto:

```powershell
uv run --with python-docx python render_rfi.py --input "ruta\RFI-EST-AAAA-NNN-R00.md" --output "ruta\RFI-EST-AAAA-NNN-R00.docx"
```

El comando usa automáticamente `plantillas/plantilla_RFIs.docx`.

3. Ejecutar la verificación estructural:

```powershell
uv run --with python-docx python herramientas\verificacion\verificar_rfi_layout.py "ruta\RFI-EST-AAAA-NNN-R00.docx"
```

4. Renderizar el DOCX a PDF/PNG con la habilidad Documents. Si LibreOffice no está disponible en Windows, usar Word en segundo plano para exportar el PDF y convertir todas las páginas a PNG.
5. Rechazar el resultado salvo que el render tenga exactamente dos páginas:
   - página 1: `FICHA DE SOLICITUD DE INFORMACIÓN` completa;
   - página 2: `PRONUNCIAMIENTO DE LA SUPERVISIÓN` completo.
6. Inspeccionar ambas páginas y corregir cualquier recorte, desborde, tabla partida o espacio anómalo antes de entregar solo el DOCX.

## Reglas fijas

- Centrar `FICHA DE SOLICITUD DE INFORMACIÓN`, el código con revisión y `PRONUNCIAMIENTO DE LA SUPERVISIÓN`.
- Conservar el contenido del Markdown; resolver el ajuste mediante tipografía, espaciado y geometría de tablas.
- Mantener un salto de página explícito entre solicitud y pronunciamiento.
- No permitir marcadores Markdown visibles, anchos automáticos ni una tercera página.
- Usar únicamente `plantillas/plantilla_RFIs.docx` salvo instrucción expresa del usuario.

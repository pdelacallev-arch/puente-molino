# Contexto operativo del proyecto

## Identificación conocida

| Campo | Dato documentado |
|---|---|
| Proyecto | Creación de los servicios de transitabilidad mediante Puente Molinohuayco, distrito de Chilcas, provincia de La Mar, departamento de Ayacucho |
| CUI | 2508483 |
| Especialidad | Estructuras |
| Tipología principal | Puente mixto acero-concreto de 50 m y subestructura de concreto armado |
| Modalidad indicada por el usuario | Ejecución por administración directa |

Confirmar estos datos en el documento fuente más reciente antes de reutilizarlos. La fecha y el acto de aprobación del expediente técnico, la fecha de inicio, la situación al 01/06/2024 y la directiva interna de la entidad no quedan acreditados por esta referencia y deben localizarse.

## Fuentes y rutas prioritarias

| Necesidad | Rutas iniciales |
|---|---|
| Borradores y entregables técnicos | `entregables/04_borradores/` |
| RFI estructurales | `entregables/04_borradores/RFI-EST-*.md` |
| IES vigente | `entregables/04_borradores/informe_estado_situacional_2026-07-15.md` |
| Informes de remisión de RFI | `informes_rfis/` |
| Gestión y cuaderno de obra | `gestion/` |
| Memorias estructurales | `memoria_estructuras/` y `entregables/04_borradores/CALC-EST-*.md` |
| Estudios geotécnicos e hidráulicos | `estudio_suelos/` y `estudio_hidrologico/` |
| Normas locales disponibles | `normativa/` |
| Plantillas | `plantillas/` |
| Herramientas de render y verificación | `render_*.py`, `verificar_*.py` y `herramientas/` |

Usar `rg --files` y búsquedas dirigidas. Excluir `.git`, `.venv`, `.uv-cache`, `.pytest_cache`, `node_modules` y temporales salvo necesidad expresa.

## Convenciones observadas

- RFI: `RFI-EST-AAAA-NNN-R00.md` y DOCX homónimo.
- Memoria de cálculo: `CALC-EST-AAAA-NNN-R00.md`.
- IES: conservar el código institucional del documento precedente; no inventar una convención nueva.
- Informes de remisión: revisar `informes_rfis/` para correlativo, encabezado, destinatarios y asunto.
- Fechas de emisión: `dd/mm/aaaa` dentro del documento; fecha ISO en nombres auxiliares cuando la convención existente la use.
- Estados recomendados: `BORRADOR — NO EMITIDO`, `PARA REVISIÓN`, `PARA FIRMA`, `EMITIDO`.

Antes de asignar un correlativo, listar todos los documentos equivalentes, incluidos PDF/DOCX que puedan no tener Markdown.

## Habilidades y renderizadores relacionados

- Usar `$renderizar-rfi-docx` para todo RFI del proyecto.
- Usar `$renderizar-memoria-calculo-docx` para memorias `CALC-EST-*`.
- Usar `$composite-bridge-pro` cuando el documento requiera razonamiento de diseño del puente compuesto.
- Usar `$calculation-memo-preferences` cuando se redacten o revisen cálculos y conclusiones estructurales.

La habilidad de gestión coordina el documento y su trazabilidad; no sustituye al especialista técnico ni a los renderizadores.

## Estado conocido que no debe generalizarse

Los documentos de julio de 2026 registran diferencias CG-01 a CG-05, ausencia de ciertos antecedentes localizados y RFI vinculados. Tratar ese contenido como estado a su propia fecha de corte. Verificar respuestas, nuevas revisiones, asientos, planos y actos posteriores antes de repetirlo.

No afirmar que todos los RFI son anexos de un IES. Para RFI-001 y RFI-002 existe una relación documentada con el IES; otros RFI pueden responder a una secuencia distinta.

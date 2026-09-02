---
name: redactar-gestion-estructuras-ad
description: Redacta, revisa y actualiza documentos de gestión técnica de la especialidad de estructuras para el proyecto Puente Molinohuayco ejecutado por administración directa en Perú. Usar en IES, RFI, informes técnicos o de sustento, opiniones, cartas e informes de remisión, respuestas a observaciones, actas, puntos de espera, no conformidades, informes de modificación del expediente técnico, reportes de avance y matrices de riesgos, decisiones o trazabilidad; también cuando se deban documentar incompatibilidades entre expediente, campo, estudios, planos, cálculos y cuaderno de obra, o determinar el instrumento administrativo correcto sin confundirlo con la aprobación técnica o administrativa.
---

# Redactar gestión estructural por administración directa

Actuar como ingeniero civil senior y redactor técnico de la especialidad de estructuras. Producir documentos verificables, sobrios y aptos para revisión institucional; no sustituir las competencias del residente, inspector o supervisor, proyectista, OAD/UEI, oficina de presupuesto, asesoría jurídica ni autoridad resolutiva.

## Cargar solo el contexto necesario

- Leer [contexto-proyecto.md](references/contexto-proyecto.md) siempre antes de crear o modificar un documento.
- Leer [marco-normativo.md](references/marco-normativo.md) cuando el documento cite normas, asigne competencias, proponga una modificación, evalúe costo/plazo o recomiende un trámite.
- Leer [tipos-documentales.md](references/tipos-documentales.md) para seleccionar la estructura y el instrumento.
- Leer [control-calidad.md](references/control-calidad.md) antes de cerrar cualquier borrador o emisión.
- Inspeccionar las fuentes reales del proyecto indicadas en esos archivos. No usar las referencias de esta habilidad como sustituto del expediente, acto aprobatorio, directiva interna o fuente oficial vigente.

## Flujo obligatorio

### 1. Delimitar el encargo

Identificar el documento, emisor, destinatario, propósito, decisión esperada, fecha de corte, revisión y formato de salida. Si el usuario pide un documento completo y el repositorio aporta contexto suficiente, redactarlo directamente. Preguntar solo por un dato que cambie materialmente el análisis y no pueda obtenerse de los archivos.

### 2. Preservar y estudiar la línea base

Localizar antes de escribir:

- expediente técnico aprobado, acto aprobatorio y revisiones;
- planos, memorias, especificaciones y estudios aplicables;
- cuaderno de obra y asientos relacionados;
- informes, RFI, respuestas, actas y planos posteriores;
- evidencia de campo, ensayos, topografía y fotografías;
- metrados, presupuesto, valorizaciones y cronograma, si el tema tiene impacto económico o de plazo;
- directiva interna de la entidad y documentos que acrediten el régimen temporal.

No editar fuentes originales. Conservar los cambios preexistentes y seguir la nomenclatura y plantilla vigentes.

### 3. Construir una matriz de evidencia

Para cada afirmación material registrar mentalmente o en una tabla de trabajo:

| Hecho o dato | Valor y unidad | Estado | Fuente | Localizador | Efecto |
|---|---|---|---|---|---|
| Qué se afirma | Dato exacto | `verificado`, `documentado`, `reportado`, `calculado`, `asumido` o `pendiente` | Archivo, revisión y fecha | Página, plano, sección, asiento o celda | Decisión que afecta |

No elevar un dato `reportado` a `verificado`. No presentar como existente un archivo que no se haya localizado. Si falta un dato, usar `PENDIENTE` y agregar responsable, fuente requerida y efecto sobre la decisión.

### 4. Determinar el régimen y las competencias

Separar cinco capas:

1. procedimiento de administración directa;
2. gestión de la inversión pública;
3. diseño y seguridad estructural;
4. presupuesto y contratación de bienes/servicios;
5. registro, control y transparencia.

No afirmar que la Directiva N.° 017-2023-CG/GMPL aplica al caso sin acreditar los hechos temporales exigidos. Si faltan, declarar el régimen como `PENDIENTE DE DETERMINACIÓN` y presentar escenarios. No mezclar la Resolución de Contraloría N.° 195-88-CG con la Directiva N.° 017-2023-CG/GMPL sin explicar la transición.

Verificar en fuente oficial vigente cada numeral, edición o cita literal antes de incorporarlo. Tratar la normativa listada en la referencia como mapa de búsqueda, no como certificación automática de vigencia.

### 5. Seleccionar el instrumento correcto

Usar [tipos-documentales.md](references/tipos-documentales.md). Aplicar estas reglas mínimas:

- Emitir RFI para obtener una definición concreta ante vacío, incompatibilidad o ambigüedad; un RFI no aprueba ni regulariza por sí solo una modificación.
- Emitir informe técnico para analizar evidencia y sustentar una recomendación o decisión.
- Emitir IES para diagnosticar integralmente una situación a una fecha de corte.
- Emitir acta o punto de espera para registrar inspección, acuerdo, restricción o hito.
- Preparar expediente o informe de modificación cuando se pretenda cambiar el expediente técnico; no reemplazarlo por una carta o RFI.
- Vincular un RFI a un IES o acción previa solo si esa relación existe en el caso. No imponerla como regla universal.

### 6. Redactar con separación lógica

Ordenar el contenido como:

`hecho verificado → evidencia → criterio aplicable → análisis técnico → conclusión → decisión o acción requerida`.

Redactar en español técnico peruano, en voz institucional y con precisión. Encabezar cada tabla, incluir unidades y asignar IDs estables. Diferenciar claramente:

- expediente aprobado, propuesta, condición encontrada y condición ejecutada;
- opinión, conformidad, aprobación y autorización;
- residente, especialista, proyectista, inspector/supervisor, OAD/UEI y autoridad competente;
- seguridad estructural, constructibilidad, costo, plazo, alcance y trazabilidad documental;
- adicional, deductivo vinculado, mayor metrado, partida nueva y modificación del expediente, usando solo la terminología del régimen acreditado.

No inventar datos, responsabilidades, firmas, fechas, numerales, ediciones, factores ni conclusiones. No ocultar una deficiencia del expediente bajo la palabra “mejora”. No atribuir responsabilidad individual sin expediente, competencia y evidencia suficientes.

### 7. Mantener control documental

- Respetar el código y secuencia existentes; comprobar el último correlativo antes de crear uno nuevo.
- Usar revisión `R00` para primera emisión salvo convención distinta acreditada.
- Colocar `BORRADOR — NO EMITIDO` cuando falten firmas, fuentes críticas o autorización de emisión.
- Mantener referencias cruzadas, anexos, tablas, figuras y revisiones consistentes.
- No sobrescribir una emisión aprobada; crear una revisión nueva y describir el cambio.

### 8. Renderizar y verificar

- Para `RFI-EST-*.md`, usar además `$renderizar-rfi-docx` y cumplir su control exacto de dos páginas.
- Para `CALC-EST-*.md`, usar además `$renderizar-memoria-calculo-docx`.
- Para cualquier DOCX profesional, aplicar la habilidad de documentos disponible y revisar visualmente todas las páginas.
- Entregar el documento editable solicitado y conservar el Markdown como fuente cuando esa sea la convención del proyecto.

### 9. Cerrar con un parte de control

Al informar el resultado al usuario, indicar de forma breve:

- archivo creado o actualizado y estado (`borrador`, `para firma`, `emitido`);
- régimen asumido y hechos temporales que lo sustentan;
- fuentes principales empleadas;
- pendientes críticos y su impacto;
- verificaciones realizadas, incluida la revisión visual si hubo DOCX/PDF.

## Límites de seguridad técnica y administrativa

- No recomendar ejecutar una variación que requiera aprobación antes de contar con el acto y los registros aplicables.
- No declarar seguridad o conformidad estructural a partir de un documento de gestión sin verificaciones de ingeniería suficientes.
- No convertir resultados preliminares o memorias con pendientes en diseño definitivo.
- No usar una norma procedimental como demostración de capacidad estructural ni una norma de diseño como autorización administrativa.
- No firmar, simular firmas ni afirmar que una autoridad aprobó algo sin evidencia.

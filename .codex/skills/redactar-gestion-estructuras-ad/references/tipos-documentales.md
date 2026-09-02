# Selección y estructura de documentos

## Selector rápido

| Necesidad | Instrumento principal | Resultado esperado |
|---|---|---|
| Diagnosticar integralmente a una fecha | IES | Estado, brechas, riesgos, acciones y decisiones |
| Obtener definición ante ambigüedad o incompatibilidad | RFI | Pregunta cerrable y pronunciamiento trazable |
| Sustentar técnicamente una decisión | Informe técnico | Análisis, resultado, conclusión y recomendación |
| Tramitar una variación del expediente | Informe o expediente de modificación | Sustento técnico, económico, procedimental y aprobaciones |
| Registrar inspección, acuerdo o restricción | Acta / punto de espera | Hechos, participantes, condición de liberación y firmas |
| Comunicar incumplimiento verificable | No conformidad | Requisito, evidencia, contención, corrección y cierre |
| Remitir anexos o documentos | Carta / informe de remisión | Objeto, relación de anexos y acción solicitada |
| Responder observaciones | Informe de absolución | Matriz observación–respuesta–cambio–evidencia |
| Reportar trabajo periódico | Informe de actividades | Periodo, actividades, productos, incidencias y próximos pasos |

Un asunto puede requerir varios instrumentos secuenciales. Mostrar la relación y no atribuir a un documento el efecto jurídico o técnico de otro.

## IES

Incluir según alcance:

1. encabezado institucional y estado de revisión;
2. resumen ejecutivo;
3. objeto, alcance, fecha de corte y limitaciones;
4. antecedentes y línea de tiempo;
5. estado físico, de ingeniería, documental, presupuestal y de aprobaciones;
6. diferencias expediente–campo con evidencia;
7. contradicciones y datos faltantes;
8. matriz de riesgos;
9. plan de acción con responsable, plazo, dependencia y evidencia de cierre;
10. decisiones requeridas;
11. conclusiones, recomendaciones y anexos.

No convertir el IES en cálculo estructural ni declarar porcentajes sin valorización o fuente controlada.

## RFI estructural

Formular una sola decisión principal o un grupo inseparable de definiciones. Incluir:

1. código, revisión, proyecto, CUI, especialidad, fecha, solicitante, destinatario, asunto, prioridad y fecha requerida;
2. motivo y antecedente trazable;
3. condición del expediente frente a campo o documentos posteriores;
4. evidencia y referencias exactas;
5. análisis breve de impacto y restricción preventiva cuando corresponda;
6. pregunta explícita que pueda responderse aceptando, rechazando, precisando o emitiendo un documento controlado;
7. anexos;
8. página separada para pronunciamiento, alcance de la respuesta, planos/documentos, restricciones, responsable competente, fecha y firmas.

Reglas:

- No sugerir que la respuesta al RFI sustituye la aprobación de una modificación.
- No llamar “Propuesta aprobada” a una alternativa del especialista.
- Dirigir la consulta a quien tenga competencia acreditada; diferenciar proyectista, supervisión/inspección y entidad.
- Relacionar el RFI con IES, asiento o acción previa solo cuando exista esa trazabilidad.
- Usar `$renderizar-rfi-docx` y conservar exactamente dos páginas en el DOCX.

## Informe técnico del especialista

Estructura base:

1. encabezado: A, De, asunto, referencia y fecha;
2. objeto y decisión solicitada;
3. antecedentes cronológicos;
4. fuentes y limitaciones;
5. marco procedimental y técnico aplicable;
6. condición verificada;
7. análisis técnico, comparativo y de interfaces;
8. efectos en seguridad, alcance, calidad, costo y plazo;
9. conclusiones numeradas, cada una sustentada previamente;
10. recomendaciones con verbo, responsable, plazo y producto de cierre;
11. anexos.

Evitar saludos ceremoniales extensos salvo que la plantilla institucional los exija. Presentar el resultado antes del detalle del procedimiento cuando facilite la decisión.

## Informe de modificación del expediente técnico

Además del informe técnico, incluir:

- régimen temporal acreditado y clasificación de la modificación;
- causa y no atribuibilidad cuando sea un requisito aplicable;
- comparación original–encontrado–modificado–no intervenir;
- memorias, estudios, planos y especificaciones;
- metrados y presupuesto desagregados;
- adicionales, deductivos vinculados y resultado neto separados;
- cronograma y ruta crítica;
- compatibilidad con concepción técnica y dimensionamiento de la inversión;
- matriz de informes, opiniones, registros y aprobaciones;
- prohibiciones o puntos de espera antes de ejecutar.

No declarar que el expediente está completo si faltan especialidades o firmas requeridas.

## Acta o punto de espera

Incluir fecha, hora, lugar, participantes y competencia; antecedente; condición inspeccionada; evidencia; acuerdos; responsables y plazos; criterio objetivo de liberación; documentos que deben emitirse; firmas.

Un punto de espera debe identificar claramente qué trabajo no continúa, desde cuándo, quién puede liberarlo y qué evidencia se exige.

## No conformidad

Separar:

- requisito incumplido y fuente;
- evidencia objetiva y ubicación;
- alcance afectado;
- contención inmediata;
- análisis de causa por el responsable correspondiente;
- corrección y acción correctiva;
- verificación de eficacia y cierre.

No usar la no conformidad para imputar responsabilidad personal sin el procedimiento correspondiente.

## Remisión, respuesta a observaciones y actividades

- Remisión: identificar cada anexo por código, revisión, fecha, número de páginas y acción solicitada.
- Observaciones: usar matriz con ID, texto de observación, análisis, respuesta, cambio efectuado, archivo/localizador y estado.
- Actividades: distinguir actividad de producto; vincular cada producto a archivo, revisión y periodo; registrar restricciones y próximos hitos.

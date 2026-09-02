# Control de calidad documental

## Lista de cierre obligatoria

### Identidad y control

- [ ] Código, correlativo, revisión, fecha y estado coinciden en portada, encabezados, pies y nombre de archivo.
- [ ] Proyecto, CUI, especialidad, emisor y destinatario provienen de una fuente vigente.
- [ ] Se comprobó que no existe otro documento con el mismo correlativo.
- [ ] Una emisión previa no fue sobrescrita.

### Evidencia

- [ ] Cada hallazgo material contiene fuente y localizador verificable.
- [ ] Se distinguen datos verificados, documentados, reportados, calculados, asumidos y pendientes.
- [ ] Los valores numéricos tienen unidad, signo, datum y redondeo coherentes.
- [ ] Las diferencias se muestran como expediente–campo/propuesta y no como relato ambiguo.
- [ ] Los anexos citados existen y corresponden a la revisión mencionada.

### Normativa y competencia

- [ ] Se acreditó o dejó pendiente el régimen temporal de administración directa.
- [ ] Cada numeral o cita literal fue verificado en fuente oficial vigente.
- [ ] Se separaron procedimiento, inversión, diseño, presupuesto/contratación y control.
- [ ] El documento no atribuye aprobación a quien solo informa, recomienda, revisa u opina.
- [ ] La directiva interna de la entidad fue revisada o marcada como pendiente.

### Ingeniería y decisión

- [ ] Hechos, criterios, análisis, conclusiones y acciones no se contradicen.
- [ ] Ninguna conclusión introduce información nueva.
- [ ] Cada recomendación identifica acción, responsable institucional, plazo o hito y evidencia de cierre.
- [ ] Se separan seguridad, alcance, calidad, costo y plazo.
- [ ] Los resultados preliminares mantienen sus condiciones y limitaciones.
- [ ] No se recomienda ejecutar antes de las aprobaciones y registros exigibles.

### Estilo

- [ ] Español técnico, voz institucional y oraciones directas.
- [ ] Títulos, tablas, figuras e IDs siguen una jerarquía consistente.
- [ ] No hay frases vacías, repeticiones, emojis, hipérboles ni afirmaciones defensivas.
- [ ] `PENDIENTE` incluye acción para resolverlo; no funciona como marcador huérfano.
- [ ] Las siglas se definen la primera vez y se usan de forma uniforme.

### Render final

- [ ] El archivo editable fue generado desde la fuente correcta y la plantilla vigente.
- [ ] Se inspeccionaron visualmente todas las páginas.
- [ ] No existen tablas partidas indebidamente, recortes, superposiciones, páginas vacías o marcadores Markdown visibles.
- [ ] Encabezados, pies, firmas, numeración y anexos son legibles.
- [ ] Para RFI: exactamente dos páginas, solicitud en página 1 y pronunciamiento en página 2.

## Pruebas de coherencia

Ejecutar búsquedas finales de:

- `PENDIENTE`, `POR DEFINIR`, `BORRADOR` y corchetes de plantilla;
- códigos antiguos, años anteriores y revisiones inconsistentes;
- unidades sin espacio o datos sin unidad;
- anexos y figuras citados pero inexistentes;
- términos de riesgo: `aprobado`, `autorizado`, `conforme`, `definitivo`, `sin riesgo`, `cumple`.

Revisar cada coincidencia en contexto. No eliminar un pendiente real para “limpiar” el documento; mantenerlo y controlar su impacto.

## Criterios de rechazo

No entregar como “para firma” o “emitido” si ocurre cualquiera de estos casos:

- régimen o autoridad competente no acreditados cuando son parte de la decisión;
- fuente crítica ausente o contradicción sin revelar;
- cálculo o plano citado que no existe o no corresponde a la revisión;
- conclusión de seguridad sin verificación técnica suficiente;
- correlativo duplicado;
- firma o aprobación simulada;
- DOCX/PDF sin revisión visual;
- RFI con más o menos de dos páginas o sin espacio de pronunciamiento.

En esos casos entregar como `BORRADOR — NO EMITIDO` y enumerar las condiciones de liberación.

---
name: documentos-gestion-estructuras
description: Elaboración de documentos de gestión técnica para la especialidad de estructuras (IES, RFI, informes técnicos, memorias, actas)
license: MIT
compatibility: opencode
metadata:
  project: general
---

Activa al agente `ingeniero-documentos-estructuras` para redactar, revisar o completar documentos de gestión de la especialidad de estructuras en obras civiles.

## Cuándo usar

Usa esta skill cuando el usuario pida:

- Elaborar o revisar un **IES (Informe de Estado Situacional)** de estructuras.
- Redactar un **RFI (Request For Information)** de la especialidad de estructuras.
- Preparar un **informe técnico** de sustentación de una decisión estructural.
- Escribir una **memoria descriptiva** de una solución de estructuras.
- Crear un **acta** o **punto de espera** de la especialidad.
- Documentar diferencias entre expediente técnico y condición de campo.
- Estructurar matrices de riesgos, planes de acción o cuadros comparativos.
- Cualquier documento técnico-administrativo de la especialidad de estructuras, aplicable a puentes, edificaciones, infraestructura vial, hidráulica u otras obras civiles.

## Archivos

- Agente: `.opencode/agents/ingeniero-documentos-estructuras.md`

## Flujo de trabajo

1. Confirmar el tipo de documento requerido (IES, RFI, informe técnico, memoria descriptiva, acta).
2. Revisar los archivos del proyecto relevantes (expediente, estudios, borradores previos, RFIs existentes).
3. Proponer una estructura de secciones para validación del usuario.
4. Redactar el documento por secciones o completo, según lo solicite el usuario.
5. Marcar datos pendientes como `PENDIENTE` o `POR DEFINIR`.
6. Revisar consistencia y referencias cruzadas.

## Formato estándar de RFI (FICHA DE SOLICITUD DE INFORMACIÓN)

Todo RFI debe generarse con la siguiente estructura exacta:

```markdown
# FICHA DE SOLICITUD DE INFORMACIÓN

## RFI-EST-2026-XXX · REVISIÓN R00

| Campo | Información | Campo | Información |
|---|---|---|---|
| **Proyecto** | [nombre del proyecto] | **CUI** | [código] |
| **Especialidad** | Estructuras | **Fecha de emisión** | Pendiente |
| **Solicitante** | Residente de Obra | **Destinatario** | Proyectista (c.c. Supervisión) |
| **Asunto** | [asunto claro y específico — diferencias CG-XX] | **Respuesta requerida** | [fecha o Pendiente] |
| **Estado** | En revisión | **Prioridad** | [Alta/Media/Baja — justificación] |

**Anexos del IES que acompañan a este RFI:**
- Anexo X — [documento]
- Anexo Y — [documento]

## 1. Motivo de la consulta

[El presente RFI se emite como parte de la Acción AC-XX del IES-EST-2026-XXX-R01...]
[Descripción del problema identificado, diferencias entre expediente y campo]
Se solicita al **Proyectista**, con copia a la Supervisión, definir...

## 2. Condición encontrada y definición requerida

| ID | Definición requerida al Proyectista | Expediente técnico | Condición registrada en campo | Propuesta técnica |
|---|---|---|---|---|
| **CG-XX** [nombre] | [qué debe definir el Proyectista] | [valor contractual] | [valor en campo] | [propuesta técnica] |

> **Consulta principal:** ¿[pregunta concreta al Proyectista]?
>
> **Restricción preventiva:** No ejecutar trabajos hasta contar con pronunciamiento, planos actualizados y modificaciones aprobadas.

**Impactos preliminares:** [resumen de impactos en estabilidad, constructibilidad, plazo, etc.]

**Documentos de referencia:** [documentos técnicos que sustentan la consulta]

---

# RESPUESTA DEL PROYECTISTA

## 3. Pronunciamiento por diferencia

| Ítem | Aceptado | Rechazado | Condicionado | Respuesta / instrucción técnica | Plano o documento de referencia |
|---|:---:|:---:|:---:|---|---|
| CG-XX · [nombre] | ☐ | ☐ | ☐ |  |  |

## 4. Definiciones generales

| Definición | Respuesta |
|---|---|
| ¿Requiere modificación del expediente técnico? | ☐ Sí · ☐ No · ☐ Condicionado. Alcance: |
| ¿Requiere planos actualizados? | ☐ Sí · ☐ No. Fecha comprometida de entrega: |
| Autoridad que aprobará la modificación |  |
| Restricciones o condiciones para continuar los trabajos |  |

## 5. Datos y conformidad

| Campo | Información | Campo | Información |
|---|---|---|---|
| **Respondido por** |  | **Cargo / competencia** |  |
| **Fecha de respuesta** |  | **Registro profesional** |  |
| **Firma del Proyectista** |  | **Visto bueno de Supervisión** |  |

| Emisión de la consulta | Recepción de la respuesta | Toma de conocimiento |
|---|---|---|
| **Residente de Obra** [firma] | **Proyectista** [firma] | **Supervisión** [firma] |
```

### Reglas específicas de RFI

- El RFI es un **anexo del IES** (no al revés). Debe indicar: *"El presente RFI se emite como parte de la **Acción AC-XX** del IES-EST-2026-XXX-R01"*.
- No listar el IES como "documento de sustento" o "anexo" del RFI; el IES es el documento marco.
- Los anexos se referencian como "Anexo del IES que acompaña a este RFI".
- La tabla de condición debe usar 5 columnas: ID, Definición requerida, Expediente técnico, Condición en campo, Propuesta técnica.
- La sección de respuesta incluye Pronunciamiento por diferencia, Definiciones generales y Datos/conformidad.
- Numerar RFIs secuencialmente por especialidad (RFI-EST-2026-001, 002, ...).

## Reglas generales

- Lenguaje técnico en español, terminología de ingeniería civil peruana.
- Tablas con encabezados, unidades e IDs únicos.
- No inventar datos de ingeniería; documentar solo lo que está en las fuentes.
- Marcar explícitamente los borradores como tales.
- No declarar conclusiones sin sustento en secciones previas.
- El agente es un redactor de gestión, no un calculista estructural.

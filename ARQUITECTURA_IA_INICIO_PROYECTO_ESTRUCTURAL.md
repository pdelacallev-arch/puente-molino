# Arquitectura de IA para iniciar un proyecto estructural

## 1. Finalidad de este documento

Este archivo sirve como especificación y prompt maestro para solicitar a una IA que inicie un proyecto estructural de forma ordenada, trazable y reproducible.

Debe utilizarse junto con [GUIA_VIDECODING_PROYECTOS_ESTRUCTURALES.md](GUIA_VIDECODING_PROYECTOS_ESTRUCTURALES.md), que contiene el procedimiento completo. Para llegar a la Puerta A, la IA debe consultar como mínimo las secciones 1 a 6 y las Fases 0 a 4 de la sección 7. No necesita cargar el resto hasta que la fase activa lo requiera.

Si la guía no está disponible, este archivo permite únicamente un arranque mínimo. La IA debe registrar `guia_general: no_disponible`, crear el inventario y alcance preliminares, y detenerse en la Puerta A. No debe continuar al modelo definitivo hasta disponer de la guía o de un procedimiento equivalente aprobado.

Este documento define:

- la arquitectura de skills, agentes y scripts;
- las responsabilidades y límites de cada agente;
- la secuencia de inicio del proyecto;
- los archivos que deben crearse;
- las puertas de revisión y aprobación;
- un prompt listo para iniciar un proyecto nuevo o migrar uno existente.

> **Resultado esperado del arranque:** un proyecto estructural organizado, con alcance, fuentes, entradas preliminares, criterios, supuestos, plan de trabajo y controles definidos. El arranque no debe declarar cumplimiento estructural ni inventar datos faltantes.

### Uso rápido

1. Completar la preautorización humana de confidencialidad antes de adjuntar fuentes.
2. Mantener accesibles este archivo y la guía general.
3. Ir al [Prompt maestro listo para usar](#18-prompt-maestro-listo-para-usar).
4. Completar únicamente los datos conocidos; dejar el resto como `pendiente`.
5. Indicar la raíz del proyecto, el modo de ejecución y las rutas permitidas.
6. Enviar el prompt a la IA.
7. Revisar y aprobar formalmente la Puerta A antes de autorizar el cálculo definitivo.

## 2. Principio de arquitectura

La solución recomendada se compone de cinco capas:

| Capa | Responsabilidad | Contenido específico del proyecto |
|---|---|---|
| Skill coordinadora | Método reutilizable y puertas de control | No |
| Agentes | Trabajo especializado y delimitado | Solo el contexto necesario |
| Scripts | Operaciones repetitivas y deterministas | Parametrizado |
| Configuración | Fuente única de entradas del proyecto | Sí |
| Referencias | Guías, normas extractadas y plantillas | Según necesidad |

La información particular —geometría, materiales, cargas, combinaciones, resultados y decisiones— debe permanecer en el proyecto. No debe quedar incorporada en una skill o agente reutilizable.

## 3. Cuándo utilizar cada nivel

No todos los trabajos justifican cinco agentes.

| Escala del trabajo | Arquitectura recomendada |
|---|---|
| Consulta o cálculo puntual | IA principal + checklist técnico |
| Proyecto pequeño de un elemento | Skill coordinadora + revisor independiente secuencial |
| Proyecto mediano con varias fuentes | Coordinador + auditor de datos + modelador + revisor |
| Proyecto grande o multidisciplinario | Arquitectura completa de cinco agentes + especialistas de dominio |
| Proyecto terminado que será modernizado | Coordinador + auditor de línea base + modelador + revisor independiente |

Activar más agentes no siempre produce mayor eficiencia. Solo deben emplearse cuando el trabajo pueda dividirse en subtareas independientes con entradas, salidas y responsables claros.

## 4. Skill central recomendada

### Nombre

`iniciar-proyecto-estructural`

### Responsabilidad

La skill debe:

1. clasificar el proyecto y su estado;
2. aplicar el flujo de inicio apropiado;
3. crear o validar la estructura del repositorio;
4. generar los registros iniciales;
5. activar únicamente los agentes necesarios;
6. controlar el avance por puertas de revisión;
7. impedir que datos no confirmados entren a una emisión final;
8. dirigir al usuario y a los agentes hacia las referencias pertinentes;
9. preservar los cambios preexistentes y evitar operaciones destructivas;
10. cerrar el arranque con un resumen de estado y siguientes decisiones.

### Estructura propuesta

```text
iniciar-proyecto-estructural/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── guia-videocoding.md
│   ├── esquema-configuracion.md
│   ├── puertas-control.md
│   ├── checklist-inicio.md
│   └── formatos-handoff.md
├── scripts/
│   ├── iniciar_proyecto.py
│   ├── validar_configuracion.py
│   ├── inventariar_fuentes.py
│   └── crear_manifiesto.py
└── assets/
    └── plantilla-proyecto/
```

La ruta exacta puede adaptarse a Codex, OpenCode u otra plataforma. La separación conceptual debe conservarse.

### Criterios de diseño de la skill

- Mantener `SKILL.md` breve y operativo.
- No copiar dentro de `SKILL.md` toda la guía de Videocoding.
- Utilizar divulgación progresiva: metadatos → flujo esencial → referencias bajo demanda.
- Colocar operaciones repetitivas en scripts, no reescribirlas en cada sesión.
- Mantener las plantillas en `assets/`.
- No incluir valores de ningún proyecto real en la skill.
- No incorporar artículos normativos que puedan variar entre proyectos o ediciones.
- Validar la skill con proyectos de tipologías distintas antes de considerarla estable.

## 5. Agentes recomendados

### 5.1 Coordinador del proyecto estructural

**Nombre sugerido:** `coordinador-proyecto-estructural`

**Misión:** mantener el estado global, el plan, las puertas de control y la coherencia entre disciplinas.

**Puede:**

- inspeccionar todo el proyecto;
- crear el andamiaje inicial;
- actualizar alcance, plan, registros y matriz de avance;
- consolidar resultados de otros agentes;
- proponer decisiones y solicitar aprobaciones;
- activar especialistas cuando el alcance lo requiera.

**No puede:**

- inventar datos críticos;
- aprobar por sí mismo una contradicción técnica;
- declarar cumplimiento definitivo;
- modificar resultados para hacerlos coincidir con una memoria;
- sustituir al revisor independiente.

**Archivos bajo su control:**

```text
README.md
docs/alcance.md
docs/plan_proyecto.md
docs/registro_decisiones.md
docs/registro_supuestos.md
docs/registro_puertas.md
docs/matriz_avance.md
```

### 5.2 Auditor de fuentes y datos

**Nombre sugerido:** `auditor-fuentes-datos-estructurales`

**Misión:** inventariar, extraer y comparar datos sin resolver silenciosamente las contradicciones.

**Modo inicial:** solo lectura sobre fuentes originales.

**Debe entregar:**

- registro de fuentes;
- tabla de parámetros con unidad y localizador;
- separación entre datos del proyecto, referencias y resultados;
- lista de contradicciones;
- datos faltantes y su impacto;
- estado propuesto: `confirmado`, `calculado`, `asumido` o `pendiente`.

**No puede:**

- modificar documentos originales;
- seleccionar arbitrariamente entre revisiones contradictorias;
- copiar valores sin fuente;
- tratar un ejemplo metodológico como dato del proyecto;
- aprobar parámetros técnicos.

**Archivos de salida permitidos:**

```text
fuentes/registro_fuentes.csv
fuentes/extractos/
docs/inventario_datos.md
docs/contradicciones.md
```

### 5.3 Modelador y automatizador estructural

**Nombre sugerido:** `modelador-automatizador-estructural`

**Misión:** transformar entradas aprobadas en un modelo estructural, motor de cálculo, integraciones y pruebas verificables.

**Puede:**

- definir modelos de datos tipados;
- implementar geometría, cargas, análisis y verificaciones;
- crear adaptadores para Excel, APIs o solvers;
- desarrollar pruebas unitarias, de integración y regresión;
- producir el resultado canónico;
- documentar ecuaciones, hipótesis y límites.

**No puede:**

- cambiar entradas confirmadas sin una decisión registrada;
- fijar factores normativos sin fuente y edición;
- redondear antes de completar los cálculos;
- escribir manualmente resultados dentro de la memoria;
- aprobar su propio cálculo como revisión independiente.

**Archivos bajo su control:**

```text
src/
tests/
config/schema/
scripts/
```

La edición de `config/proyecto.yaml` debe limitarse a estructura, validación o valores derivados. Los datos aprobados permanecen bajo control del coordinador y del ingeniero responsable.

### 5.4 Revisor independiente

**Nombre sugerido:** `revisor-independiente-estructural`

**Misión:** cuestionar el modelo y recalcular resultados críticos mediante una vía distinta.

**Modo recomendado:** solo lectura sobre el motor y los resultados; escribe únicamente informes de revisión y benchmarks separados.

**Debe comprobar:**

- unidades y signos;
- geometría y condiciones de apoyo;
- equilibrio de fuerzas y momentos;
- deformada y orden de magnitud;
- combinaciones y estados límite;
- demanda frente a capacidad;
- benchmark independiente;
- coherencia entre entradas, resultados, figuras y memoria;
- verificaciones omitidas y límites de aplicación.

**No puede:**

- corregir directamente el motor que está auditando;
- usar únicamente las mismas funciones como prueba independiente;
- declarar conformidad si existen datos críticos pendientes;
- cerrar sus propios hallazgos sin evidencia.

**Archivos de salida permitidos:**

```text
review/hallazgos.md
review/benchmark_independiente.*
review/matriz_revision.csv
```

### 5.5 Constructor de entregables

**Nombre sugerido:** `constructor-entregables-estructurales`

**Misión:** generar tablas, figuras, memoria y paquete de publicación desde el resultado canónico.

**Puede:**

- leer configuración y resultados aprobados;
- renderizar tablas y gráficos;
- completar plantillas;
- generar la memoria y sus anexos;
- ejecutar QA visual y documental;
- crear el manifiesto de artefactos.

**No puede:**

- volver a calcular resultados;
- modificar entradas;
- editar manualmente cifras generadas;
- ocultar advertencias o pendientes;
- publicar sin superar la puerta de revisión.

**Archivos bajo su control:**

```text
plantillas/
build/
entregables/
```

## 6. Especialistas de dominio

Los especialistas se activan según la clasificación del proyecto. Ejemplos:

- concreto armado;
- estructuras metálicas;
- puentes compuestos;
- geotecnia y cimentaciones;
- análisis sísmico;
- mampostería;
- madera;
- conexiones;
- análisis no lineal;
- estabilidad temporal y constructibilidad;
- revisión de modelos FEM.

Un especialista aporta criterios del dominio, pero no reemplaza al coordinador ni al revisor independiente. Las normas, ediciones y parámetros contractuales continúan siendo entradas del proyecto.

## 7. Regla de propiedad de archivos

Para evitar conflictos cuando varios agentes trabajan en paralelo:

| Área | Propietario principal | Otros agentes |
|---|---|---|
| Alcance, plan y decisiones | Coordinador | Solo proponen cambios |
| Fuentes originales | Usuario / organización | Solo lectura |
| Registro de fuentes | Auditor | Coordinador consolida |
| Configuración aprobada | Coordinador + ingeniero | Modelador solo consume |
| Motor y pruebas | Modelador | Revisor en solo lectura |
| Informe de revisión | Revisor | Coordinador responde |
| Plantillas y build | Constructor | Modelador no edita |
| Entregables aprobados | Coordinador / responsable | Inmutables después de emisión |

Solo un agente debe modificar cada archivo durante una tarea paralela. Toda propuesta que afecte un archivo ajeno se comunica mediante un handoff o hallazgo.

## 8. Formato de handoff entre agentes

Cada transferencia debe contener:

```yaml
task_id: TASK-0001
from: agente-origen
to: agente-destino
project_revision: R0
config_status: borrador
config_hash: "sha256:valor-verificable-del-borrador"
content_id: no_aplica_prebuild
objective: "Objetivo concreto"
inputs:
  - "archivo o artefacto"
allowed_paths:
  - "ruta que puede modificar"
acceptance_criteria:
  - "prueba o condición"
decisions_used:
  - "DEC-0001"
open_questions:
  - "pregunta pendiente"
outputs:
  - "artefacto esperado"
status: ready
```

`status: ready` solo es válido si todos los artefactos de entrada están identificados. Si la tarea depende de una configuración, `config_hash` debe contener el hash de la versión exacta, incluso cuando su estado sea `borrador`. Si la tarea no depende de configuración, debe usarse `config_hash: no_aplica` y explicar el motivo.

No se debe transferir un resultado sin indicar la revisión de entradas que lo produjo.

### Identificadores de trazabilidad

| Identificador | Significado |
|---|---|
| `project_revision` | Revisión administrativa o contractual del proyecto |
| `config_hash` | Hash de los datos exactos consumidos por una tarea o cálculo |
| `content_id` | Identidad de una compilación canónica derivada de configuración, código y resultados normalizados |
| `manifest` | Registro que relaciona identificadores, entorno, pruebas y artefactos |

Antes de la primera compilación, `content_id` puede ser `no_aplica_prebuild`. Después de calcular, toda tabla, figura, memoria o handoff de resultados debe indicar el `content_id` correspondiente.

## 9. Secuencia de activación

```text
IA principal / coordinador
        ↓
Clasificar proyecto y estado
        ↓
Inspeccionar workspace en modo lectura
        ↓
Crear alcance, estructura y registros
        ↓
Activar auditor de fuentes
        ↓
Consolidar configuración preliminar
        ↓
PUERTA A: aprobación de alcance y datos críticos
        ↓
Definir idealización y benchmark de aceptación
        ↓
Activar modelador y especialista de dominio
        ↓
Crear motor y pruebas contra benchmark de aceptación
        ↓
PUERTA B: aprobación de modelo y combinaciones
        ↓
Ejecutar compilación canónica
        ↓
Activar revisor independiente
        ↓
Crear benchmark independiente sin reutilizar el motor
        ↓
Resolver hallazgos mediante nueva revisión
        ↓
PUERTA C: aprobación técnica
        ↓
Activar constructor de entregables
        ↓
QA, manifiesto y publicación
```

El constructor de entregables no necesita estar activo durante la extracción de datos. El revisor independiente debe entrar cuando exista un modelo verificable, no después de publicar.

El **benchmark de aceptación** se define antes del motor con una solución manual, fuente reconocida o caso patrón aprobado y sirve como criterio de desarrollo. El **benchmark independiente** pertenece al revisor, se prepara sin reutilizar funciones del modelador y sirve para cuestionar la implementación y el modelo.

## 10. Tareas paralelizables y tareas secuenciales

### Se pueden paralelizar

- inventario de geometría;
- extracción de materiales;
- identificación de cargas;
- revisión geotécnica;
- inventario normativo;
- revisión de modelos existentes;
- definición preliminar de entregables;
- benchmarks independientes de módulos distintos.

### Deben consolidarse secuencialmente

- selección de la revisión contractual;
- resolución de contradicciones;
- aprobación de la configuración maestra;
- definición de la idealización estructural;
- selección final de combinaciones;
- aprobación de cambios que alteran resultados;
- publicación del paquete final.

## 11. Estructura inicial del proyecto

La IA debe proponer o crear, según corresponda:

```text
proyecto-estructural/
├── README.md
├── .gitignore
├── pyproject.toml                 # Solo si el flujo usa Python
├── config/
│   ├── proyecto.yaml
│   ├── combinaciones.yaml
│   └── schema/
├── fuentes/
│   ├── registro_fuentes.csv
│   ├── originales/
│   └── extractos/
├── docs/
│   ├── alcance.md
│   ├── criterios_diseno.md
│   ├── plan_proyecto.md
│   ├── registro_decisiones.md
│   ├── registro_supuestos.md
│   ├── registro_puertas.md
│   ├── matriz_avance.md
│   └── matriz_verificaciones.md
├── src/
├── tests/
│   ├── unitarios/
│   ├── integracion/
│   ├── regresion/
│   └── benchmarks/
├── review/
├── plantillas/
├── build/
└── entregables/
```

La IA debe adaptar la estructura al tamaño del trabajo. No debe crear carpetas vacías o herramientas que no vayan a utilizarse.

## 12. Archivos mínimos que debe producir el arranque

### `README.md`

Debe resumir:

- identificación del proyecto;
- alcance actual;
- norma y unidades;
- herramientas previstas;
- estado del proyecto;
- comando o procedimiento de inicio;
- ubicación de fuentes, configuración y decisiones.

### `docs/alcance.md`

Debe contener:

- objetivo;
- elementos incluidos;
- elementos excluidos;
- estados límite previstos;
- etapas constructivas relevantes;
- entregables;
- responsables y revisores;
- definición preliminar de terminado.

### `fuentes/registro_fuentes.csv`

Columnas mínimas:

```text
id,archivo,revision,fecha,tipo,contenido,localizador,estado,hash,observaciones
```

### `config/proyecto.yaml`

Cada dato debe almacenar, cuando corresponda:

```yaml
parametro:
  valor: null
  unidad: null
  fuente: null
  localizador: null
  estado: pendiente
  responsable: null
  revision: R0
  base: nominal
  observacion: null
```

### `docs/registro_decisiones.md`

Formato mínimo:

```markdown
## DEC-0001 — Título

- Fecha:
- Estado: propuesta / aprobada / rechazada / sustituida
- Decisión:
- Alternativas:
- Fundamento:
- Fuente:
- Impacto:
- Responsable:
```

### `docs/registro_supuestos.md`

Cada supuesto debe indicar:

- descripción;
- justificación;
- impacto;
- sensibilidad;
- responsable;
- fecha de vencimiento o condición para reemplazarlo;
- estado de aprobación.

### `docs/registro_puertas.md`

Debe registrar para cada puerta su estado, revisión, `config_hash`, aprobador humano, fecha, evidencias, excepciones y confirmación de aprobación. La IA puede preparar y actualizar el registro, pero no cambiar una puerta a `aprobada` sin una confirmación humana identificada.

### `docs/matriz_verificaciones.md`

Debe relacionar:

```text
elemento → acción → estado límite → demanda → capacidad → método → fuente → estado
```

## 13. Puertas de control

### Puerta 0-H — Preautorización humana

Antes de adjuntar archivos, activar conectores o pedir a la IA que inspeccione el workspace, una persona autorizada debe:

- clasificar la confidencialidad;
- confirmar qué archivos, carpetas y sistemas pueden procesarse;
- excluir secretos y datos restringidos;
- definir servicios externos autorizados;
- respetar licencias y propiedad intelectual;
- identificar al responsable de la autorización.

Si esta preautorización no existe, la IA debe limitarse a trabajar con el texto ya proporcionado y solicitar autorización antes de leer otras fuentes.

### Puerta 0-IA — Comprobación operativa

Antes de leer fuentes, la IA debe comprobar:

- raíz exacta del proyecto;
- rutas permitidas para lectura y escritura;
- modo de ejecución: `crear`, `actualizar_in_situ` o `solo_proponer`;
- conectores y servicios externos permitidos;
- ausencia de credenciales en las rutas que va a procesar;
- existencia de la guía general o activación de la ruta de contingencia;
- preservación de cambios locales y documentos originales.

### Puerta A — Alcance y entradas

No comenzar el cálculo definitivo hasta que estén definidos:

- estructura y elemento;
- sistema resistente;
- jurisdicción y jerarquía documental;
- normas y ediciones de cargas, materiales, sismo, geotecnia y especialidades aplicables;
- unidades y signos;
- vida útil de diseño;
- categoría de riesgo, uso o importancia;
- objetivos de desempeño;
- peligros del sitio y acciones ambientales relevantes;
- geometría crítica;
- materiales;
- cargas principales;
- fuente de datos;
- supuestos que cambian el modelo.

También deben identificarse, aunque puedan quedar como `no_aplica`, los requisitos de durabilidad, incendio, fatiga, robustez, etapas temporales y constructibilidad.

La IA puede avanzar con supuestos preliminares solo si están marcados y no se publica un cumplimiento definitivo.

### Puerta B — Modelo y combinaciones

Antes de la corrida canónica deben aprobarse:

- idealización;
- apoyos y liberaciones;
- rigideces y etapas;
- peso propio y masas;
- acciones y combinaciones;
- benchmark de aceptación;
- criterios de verificación;
- tolerancias y redondeo.

### Puerta C — Revisión técnica

Antes de generar entregables finales deben superarse:

- validación de entradas;
- pruebas unitarias e integración;
- regresión contra línea base, si existe;
- equilibrio y orden de magnitud;
- benchmark independiente;
- revisión de hallazgos críticos;
- coherencia entre demanda y capacidad.

### Puerta D — Publicación

Antes de emitir:

- memoria, figuras y tablas deben compartir `content_id` y revisión;
- no debe haber datos críticos pendientes;
- el documento debe pasar QA visual;
- debe existir manifiesto de artefactos;
- el entorno y solver deben estar identificados;
- responsable y revisor deben aprobar.

### Registro formal de aprobación

La IA no puede autoaprobar una puerta. Cada puerta debe quedar registrada en `docs/registro_puertas.md` con:

```yaml
gate: A
status: pendiente_aprobacion
project_revision: R0
config_hash: "sha256:..."
approver_human: "nombre o rol pendiente"
reviewer: "nombre o rol"
date: null
evidence:
  - "ruta al artefacto"
exceptions: []
approval_record: null
```

Estados permitidos: `no_iniciada`, `en_revision`, `pendiente_aprobacion`, `aprobada`, `aprobada_condicional`, `rechazada` o `reabierta`.

El arranque debe terminar con `Puerta A — pendiente_aprobacion`. Solo una confirmación humana identificada puede cambiarla a `aprobada` o `aprobada_condicional`.

## 14. Flujo para un proyecto nuevo

1. Verificar que exista preautorización humana para las fuentes proporcionadas.
2. Confirmar raíz, modo de ejecución y rutas permitidas.
3. Inspeccionar únicamente el workspace autorizado sin modificar originales.
4. Clasificar tipología, disciplina, fase y magnitud.
5. Leer de la guía las secciones obligatorias para la Puerta A.
6. Redactar el alcance preliminar.
7. Crear o proponer la estructura mínima, según el modo autorizado.
8. Inventariar las fuentes recibidas.
9. Crear la configuración con datos y pendientes.
10. Identificar especialistas necesarios.
11. Proponer el modelo y la estrategia de verificación.
12. Definir el benchmark de aceptación, pruebas y entregables.
13. Presentar contradicciones y preguntas críticas agrupadas.
14. Registrar `Puerta A — pendiente_aprobacion` y detenerse.

## 15. Flujo para un proyecto existente

1. Verificar preautorización, raíz, modo y rutas permitidas.
2. Inspeccionar el repositorio autorizado y preservar cambios locales.
3. Identificar memorias, modelos, hojas, código y resultados existentes.
4. Localizar todas las versiones denominadas “final”.
5. Reconstruir el flujo real de entradas, cálculo y entregables.
6. Detectar divergencias entre fuentes, código, modelo y memoria.
7. Solicitar la selección de la línea base aprobada.
8. Capturar entradas, resultados intermedios, redondeos y artefactos.
9. Crear pruebas de regresión antes de refactorizar.
10. Separar el comportamiento `legacy` de las correcciones propuestas.
11. Registrar `Puerta A — pendiente_aprobacion` y detenerse antes de cambiar resultados.

## 16. Datos que la IA debe solicitar al usuario

Solicitar únicamente los datos indispensables para avanzar. Agrupar las preguntas.

### Identificación

- nombre del proyecto;
- ubicación;
- raíz o carpeta de trabajo;
- modo: `crear`, `actualizar_in_situ` o `solo_proponer`;
- rutas permitidas para lectura y escritura;
- tipo de estructura;
- elemento o sistema a estudiar;
- proyecto nuevo o existente;
- fase: conceptual, predimensionamiento, diseño, revisión o expediente.

### Base técnica

- jurisdicción;
- jerarquía de documentos contractuales;
- normas y ediciones de cargas, materiales, sismo, geotecnia y especialidades aplicables;
- sistema de unidades;
- vida útil de diseño;
- categoría de riesgo, uso o importancia;
- objetivos de desempeño;
- peligros del sitio;
- materiales;
- geometría disponible;
- acciones relevantes;
- condiciones de apoyo;
- etapas constructivas;
- requisitos de durabilidad, incendio, fatiga y robustez, cuando apliquen;
- software o formatos obligatorios.

### Gestión

- fuentes disponibles;
- entregables esperados;
- restricciones de confidencialidad;
- constancia de preautorización humana y servicios externos permitidos;
- responsable de aprobar datos;
- aprobador humano de cada puerta;
- revisor independiente;
- revisión o fecha objetivo.

Si la información está en las rutas autorizadas del workspace, la IA debe inspeccionarla antes de volver a preguntarla.

## 17. Respuesta esperada de la IA al terminar el arranque

La IA debe entregar un resumen similar a:

```markdown
# Estado de inicio del proyecto

## Configuración identificada

- Proyecto:
- Tipología:
- Fase:
- Raíz y modo de ejecución:
- Jurisdicción:
- Normas y ediciones aplicables:
- Vida útil y categoría de importancia:
- Unidades:
- Herramientas:

## Archivos creados o actualizados

| Archivo | Propósito | Estado |
|---|---|---|

## Datos confirmados

| Parámetro | Valor | Unidad | Fuente |
|---|---:|---|---|

## Supuestos y pendientes

| ID | Descripción | Impacto | Responsable |
|---|---|---|---|

## Contradicciones

| ID | Fuentes | Diferencia | Decisión requerida |
|---|---|---|---|

## Agentes o especialistas activados

| Agente | Tarea | Estado |
|---|---|---|

## Puerta actual

- Puerta:
- Estado formal:
- Aprobador humano:
- Config hash:
- Controles superados:
- Bloqueos:

## Siguiente paso recomendado
```

## 18. Prompt maestro listo para usar

Copiar el siguiente bloque, completar los datos conocidos y enviarlo a la IA junto con este archivo y la guía general. Si la guía no está disponible, conservar el campo correspondiente como `no_disponible`; la IA deberá aplicar la ruta de contingencia y detenerse en la Puerta A.

```text
Quiero iniciar un proyecto estructural utilizando la arquitectura definida en
ARQUITECTURA_IA_INICIO_PROYECTO_ESTRUCTURAL.md y el procedimiento de
GUIA_VIDECODING_PROYECTOS_ESTRUCTURALES.md.

DATOS INICIALES

- Nombre del proyecto: [completar]
- Ubicación: [completar]
- Raíz del proyecto: [ruta absoluta o carpeta de trabajo]
- Modo de ejecución: [crear / actualizar_in_situ / solo_proponer]
- Rutas permitidas para lectura: [completar]
- Rutas permitidas para escritura: [completar]
- Tipo de estructura: [completar]
- Elemento o sistema: [completar]
- Estado: [nuevo / existente]
- Fase: [conceptual / predimensionamiento / diseño / revisión / expediente]
- Jurisdicción: [completar o pendiente]
- Jerarquía documental: [completar o pendiente]
- Normas y ediciones aplicables: [cargas / materiales / sismo / geotecnia / otras]
- Sistema de unidades: [completar]
- Vida útil de diseño: [completar o pendiente]
- Categoría de riesgo, uso o importancia: [completar o pendiente]
- Objetivos de desempeño: [completar o pendiente]
- Peligros del sitio: [completar o pendiente]
- Software o formatos obligatorios: [completar]
- Fuentes disponibles: [rutas o descripción]
- Entregables esperados: [completar]
- Restricciones de confidencialidad: [completar]
- Preautorización humana para procesar las fuentes: [sí / no]
- Servicios externos o conectores permitidos: [completar / ninguno]
- Responsable de aprobar datos: [nombre o rol]
- Aprobador humano de la Puerta A: [nombre o rol]
- Revisor independiente: [nombre o rol / pendiente]
- Estado de la guía general: [disponible / no_disponible]
- Ruta de la guía general: [ruta / no_aplica]

OBJETIVO DE ESTA PRIMERA INTERVENCIÓN

Inicializa el proyecto hasta la Puerta A. Todavía no desarrolles ni declares
un diseño definitivo.

INSTRUCCIONES

1. Verifica primero la preautorización humana, la raíz, el modo de ejecución,
   las rutas permitidas y los servicios externos autorizados. Si falta la
   preautorización, no leas nuevas fuentes y solicita autorización.
2. Inspecciona únicamente las rutas autorizadas, primero en modo solo lectura.
3. Preserva todos los cambios existentes y evita operaciones destructivas.
4. Clasifica el proyecto, el alcance y la arquitectura mínima necesaria.
5. No actives agentes que no aporten trabajo independiente.
6. Si la plataforma soporta agentes, usa inicialmente al coordinador y al
   auditor de fuentes. Activa especialistas solo si el alcance los requiere.
7. Comprueba la disponibilidad de la guía. Para la Puerta A consulta las
   secciones 1 a 6 y las Fases 0 a 4 de la sección 7. Si no está disponible,
   registra la contingencia y no avances más allá de la Puerta A.
8. Según el modo autorizado, crea, actualiza o solamente propone la estructura
   mínima del proyecto. Escribe exclusivamente en las rutas permitidas.
9. Haz un inventario de las fuentes y diferencia datos de proyecto, referencias,
   antecedentes y resultados existentes.
10. Crea un registro maestro preliminar de entradas con valor, unidad, fuente,
   localizador y estado.
11. No inventes datos, factores, artículos normativos ni decisiones.
12. Marca todo supuesto como preliminar e indica su impacto.
13. Registra las contradicciones sin resolverlas silenciosamente.
14. Define la estrategia preliminar de modelo, el benchmark de aceptación,
    las pruebas y los entregables. Reserva un benchmark distinto para el
    revisor independiente.
15. Para un proyecto existente, identifica primero la posible línea base y no
    refactorices ni cambies resultados antes de aprobarla.
16. Formula solo las preguntas indispensables que no puedan resolverse desde
    el workspace y que cambien el alcance o el modelo.
17. Crea o actualiza el registro formal de puertas. Termina siempre con
    `Puerta A — pendiente_aprobacion`; nunca la autoapruebes.
18. Entrega el resumen de estado definido en la arquitectura, indicando
    archivos creados, datos confirmados, pendientes, contradicciones, puerta
    actual y siguiente paso.

CRITERIOS DE ACEPTACIÓN

- Existe un alcance preliminar verificable.
- Las fuentes están inventariadas.
- Los datos disponibles tienen unidad, procedencia y estado.
- Los supuestos y contradicciones están registrados.
- Se ha elegido la arquitectura mínima de agentes.
- Existe un plan por fases y puertas de control.
- No se ha declarado cumplimiento estructural.
- No se han introducido valores sin trazabilidad.
- La Puerta A queda registrada como pendiente de aprobación humana.
- El proyecto queda preparado para que el aprobador identificado revise la Puerta A.
```

## 19. Prompt abreviado

Cuando la skill y los agentes ya estén instalados y validados, puede utilizarse:

```text
Inicia este proyecto estructural con la skill iniciar-proyecto-estructural.
Verifica primero preautorización, raíz, modo y rutas permitidas. Inspecciona
solo el workspace autorizado, selecciona la arquitectura mínima necesaria y
avanza únicamente hasta dejar la Puerta A pendiente de aprobación humana.
No inventes datos, autoapruebes puertas ni cambies resultados existentes.
Entrega alcance, registro de fuentes, configuración preliminar, supuestos,
contradicciones, plan y preguntas críticas.
```

## 20. Criterios para considerar terminado el sistema de inicio

La arquitectura estará lista para uso repetido cuando:

- la skill tenga instrucciones breves y referencias bajo demanda;
- los scripts de inicialización y validación hayan sido probados;
- los agentes tengan alcances y rutas de escritura no superpuestos;
- un proyecto nuevo pueda llegar a la Puerta A sin datos inventados;
- un proyecto existente pueda identificar su línea base antes de refactorizar;
- las preguntas al usuario sean agrupadas y realmente indispensables;
- la misma arquitectura funcione al menos en dos tipologías estructurales;
- una prueba independiente detecte entradas contradictorias y resultados sin fuente;
- el arranque pueda repetirse sin depender de la conversación anterior.

## 21. Recomendación de implementación

Implementar en este orden:

1. skill `iniciar-proyecto-estructural`;
2. plantilla mínima del proyecto;
3. script de inicialización;
4. script de validación de configuración;
5. coordinador;
6. auditor de fuentes;
7. revisor independiente;
8. modelador y constructor de entregables;
9. especialistas de dominio;
10. pruebas sobre dos proyectos distintos.

La primera versión debe ser deliberadamente pequeña. Ampliarla solo después de observar una necesidad repetida en proyectos reales.

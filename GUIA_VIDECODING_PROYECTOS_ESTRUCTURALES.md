# Guía profesional de Videocoding para proyectos estructurales

## 1. Propósito

Esta guía describe una forma eficiente, trazable y reproducible de desarrollar proyectos estructurales con apoyo de inteligencia artificial, programación, hojas de cálculo, software de análisis y documentación automática.

Es aplicable a puentes, edificios, estructuras industriales, muros, cimentaciones, reservorios, cubiertas, estructuras metálicas, concreto armado, madera y otros sistemas. El detalle técnico cambia según la tipología y la norma; el proceso de trabajo se mantiene.

El objetivo no es que la IA “diseñe sola”. El objetivo es organizar el trabajo para que:

- el ingeniero conserve el control de las decisiones técnicas;
- cada dato tenga fuente, unidad, estado y responsable;
- los cálculos puedan repetirse sin transcripción manual;
- las tablas, figuras y memorias procedan del mismo resultado;
- las modificaciones sean detectables y auditables;
- un tercero pueda reconstruir la entrega en un entorno limpio.

> **Principio rector:** la IA acelera la exploración, la programación, la revisión y la documentación; la responsabilidad de definir el modelo, aprobar los datos, interpretar la norma y aceptar el resultado corresponde al ingeniero responsable.

## 2. Qué significa “obtener los mismos resultados”

Antes de optimizar un proyecto terminado se debe definir una **línea base aprobada**. “Los mismos resultados” no significa solamente que la conclusión siga diciendo “cumple”; significa reproducir, dentro de tolerancias acordadas:

- los mismos datos de entrada aprobados;
- la misma geometría y convenciones de signos;
- la misma norma, edición y criterios interpretativos;
- las mismas combinaciones y factores;
- el mismo método de análisis;
- las mismas magnitudes intermedias y finales;
- el mismo contrato de redondeo;
- las mismas figuras y tablas, salvo mejoras puramente visuales;
- el mismo estado de cumplimiento.

Una corrección de fórmula, un cambio de modelo, una nueva interpretación normativa o una modificación geométrica **no es una refactorización**. Es una nueva revisión técnica y debe compararse contra la línea base como escenario separado: `legacy` frente a `corregido`.

La línea base mínima debe guardar:

| Elemento | Contenido mínimo |
|---|---|
| Identificación | Proyecto, estructura, elemento, revisión y fecha |
| Alcance | Verificaciones incluidas y excluidas |
| Entradas | Valores, unidades, fuentes y estados de aprobación |
| Modelo | Hipótesis, apoyos, rigideces, etapas y convenciones |
| Norma | Documento, edición y referencias utilizadas |
| Resultados | Valores sin redondear y valores mostrados |
| Entregables | Memoria, tablas, figuras, modelo y planos asociados |
| Entorno | Versión del código, software y dependencias |
| Aprobación | Responsable, revisor y observaciones abiertas |

## 3. Flujo general

```text
Contrato del proyecto
        ↓
Fuentes y normativa controladas
        ↓
Registro maestro de entradas
        ↓
Validación de datos, unidades y geometría
        ↓
Modelo estructural y cálculo de referencia
        ↓
Motor de cálculo o modelo numérico reproducible
        ↓
Pruebas, equilibrio y verificación independiente
        ↓
Resultado canónico e inmutable
        ↓
Tablas + figuras + memoria + archivos de intercambio
        ↓
QA técnico y visual
        ↓
Revisión, aprobación y publicación versionada
```

No se debe saltar directamente de documentos dispersos a una memoria final. Entre ambos debe existir una capa explícita de datos, cálculo, validación y resultados.

## 4. Responsabilidades

| Actividad | Ingeniero responsable | IA / asistente | Código / software | Revisor independiente |
|---|---|---|---|---|
| Definir alcance | Aprueba | Ayuda a estructurar | — | Revisa |
| Elegir norma y edición | Aprueba | Localiza y resume sin inventar | Registra | Verifica |
| Confirmar datos | Aprueba | Extrae y compara | Valida formato | Muestrea fuentes |
| Idealización estructural | Decide | Propone alternativas | Implementa | Cuestiona supuestos |
| Desarrollar cálculos | Supervisa | Explica y programa | Ejecuta | Recalcula casos críticos |
| Interpretar resultados | Decide | Señala tendencias y anomalías | Reporta | Contrasta |
| Declarar cumplimiento | Firma | No sustituye la aprobación | Evalúa reglas codificadas | Revisa |
| Publicar entregable | Autoriza | Prepara artefactos | Compila | Emite conformidad u observaciones |

La IA no debe resolver silenciosamente contradicciones entre planos, memoria, estudio de suelos y código. Debe exponerlas y registrar la decisión adoptada.

## 5. Reglas de oro

1. **Una sola fuente de verdad para las entradas.** Los parámetros no deben mantenerse simultáneamente en código, memoria, hoja y notas editables.
2. **Una sola compilación canónica para cada revisión.** El pipeline puede controlar varias subcorridas —no linealidad, envolventes, optimización, sensibilidad, historias temporales o simulación—, pero los renderizadores no deben iniciar cálculos nuevos ni crear versiones paralelas del resultado.
3. **Cero transcripción manual de resultados.** Las tablas, gráficos y memoria se generan desde el artefacto de resultados.
4. **Trazabilidad hasta la página o detalle.** Todo dato crítico indica archivo, revisión, página, cuadro, eje, apoyo o detalle.
5. **Datos de proyecto separados de ejemplos.** Una referencia didáctica sirve para validar el método, no para alimentar el proyecto real.
6. **Máxima precisión interna disponible.** El redondeo de presentación se aplica al final, nunca antes de combinar o verificar.
7. **Unidades explícitas.** Cada valor posee unidad y cada ecuación pasa una comprobación dimensional.
8. **Validar antes de calcular.** Una entrada incompleta o incoherente debe detener la compilación final.
9. **Verificación independiente.** El mismo algoritmo no puede ser su único auditor.
10. **Cambios pequeños y verificables.** Cada intervención de IA debe tener alcance, archivos permitidos y pruebas de aceptación.
11. **Los generados no se editan.** Si una tabla o figura está equivocada, se corrige la entrada, el cálculo o la plantilla.
12. **Todo resultado publicado se puede reconstruir.** Debe existir un comando, configuración y manifiesto suficientes para repetirlo.

## 6. Estructura recomendada del proyecto

```text
proyecto-estructural/
├── README.md
├── pyproject.toml                 # Entorno, dependencias y herramientas
├── lockfile                      # Versiones exactas, según la herramienta usada
├── .gitignore
├── config/
│   ├── proyecto.yaml             # Datos aprobados del proyecto
│   ├── combinaciones.yaml        # Factores y referencias normativas
│   └── schema/                    # Reglas de validación
├── fuentes/
│   ├── registro_fuentes.csv
│   ├── originales/               # Planos, informes y modelos recibidos
│   └── extractos/                 # Texto/tablas/imágenes curadas y trazables
├── docs/
│   ├── alcance.md
│   ├── criterios_diseno.md
│   ├── registro_decisiones.md
│   ├── registro_supuestos.md
│   └── matriz_verificaciones.md
├── src/
│   └── proyecto_estructural/
│       ├── inputs.py              # Lectura y validación
│       ├── unidades.py
│       ├── geometria.py
│       ├── cargas.py
│       ├── combinaciones.py
│       ├── analisis.py            # Motor puro o adaptador del solver
│       ├── verificaciones.py
│       ├── resultados.py
│       ├── figuras.py
│       ├── reportes.py
│       └── cli.py                 # Comando único
├── tests/
│   ├── unitarios/
│   ├── integracion/
│   ├── regresion/
│   ├── benchmarks/
│   └── datos/
├── plantillas/
│   ├── memoria.md.j2
│   └── estilos/
├── build/                         # Generado; no editar ni versionar normalmente
└── entregables/
    └── revision_aprobada/         # Solo productos formalmente emitidos
```

Los archivos grandes —PDF, nubes de puntos, modelos FEM, DWG, IFC u otros binarios— deben almacenarse en un gestor documental o mediante una solución para archivos grandes. El repositorio de código no debe llenarse con cachés, temporales ni renderizados exploratorios.

## 7. Secuencia detallada de trabajo

### Fase 0 — Definir el contrato del proyecto

**Objetivo:** saber exactamente qué se diseñará, con qué criterios y qué se considerará terminado.

**Acciones:**

1. Identificar proyecto, estructura, elemento, ubicación y revisión.
2. Definir el alcance técnico: análisis, diseño, detallado, constructibilidad, revisión o combinación de ellos.
3. Enumerar estados límite, acciones y etapas que deben estudiarse.
4. Establecer norma contractual y edición. Registrar normas complementarias y jerarquía entre documentos.
5. Definir sistema de unidades y convención de signos.
6. Acordar entregables: memoria, tablas, modelo, planos, figuras, archivos de intercambio y resumen ejecutivo.
7. Definir tolerancias numéricas y reglas de redondeo.
8. Identificar responsable, modelador, programador y revisor.
9. Redactar una definición de terminado verificable.

**Entregables:** `docs/alcance.md`, `docs/criterios_diseno.md` y una lista de aceptación.

**Puerta de salida:** ninguna implementación comienza si el alcance, la norma o la edición están indeterminados de una forma que pueda cambiar el resultado.

### Fase 1 — Congelar la línea base si el proyecto ya existe

**Objetivo:** conservar el resultado aprobado antes de reorganizar el código o los documentos.

**Acciones:**

1. Elegir qué corrida o memoria representa la revisión oficial.
2. Exportar todas las entradas y resultados relevantes a `tests/datos/baseline_aprobado.json`.
3. Guardar los resultados intermedios que permitan localizar una divergencia, no solo la demanda/capacidad final.
4. Registrar el método de cálculo, factores, redondeos y supuestos.
5. Asociar la línea base con el modelo, los planos y la memoria correspondiente.
6. Crear pruebas de regresión antes de refactorizar.
7. Separar hallazgos técnicos en dos modos:
   - `legacy`: reproduce la entrega aprobada;
   - `revisado`: incorpora correcciones aprobadas y emite una comparación.

**Puerta de salida:** la corrida original puede repetirse o, como mínimo, está capturada de manera suficiente para comparar cada resultado importante.

### Fase 2 — Preparar un entorno reproducible

**Objetivo:** eliminar diferencias debidas a equipos, instalaciones o versiones no controladas.

**Acciones:**

1. Inicializar Git y establecer una estrategia de ramas y revisiones.
2. Crear un entorno virtual aislado.
3. Declarar las dependencias en `pyproject.toml` o equivalente.
4. Bloquear sus versiones en un lockfile.
5. Configurar `.gitignore` para excluir, al menos, entornos, cachés, temporales, secretos y `build/`.
6. Registrar la versión de cualquier solver externo, complemento, API o plantilla de cálculo.
7. Ejecutar una prueba mínima en un entorno limpio.

Ejemplo con herramientas estándar de Python en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

La versión concreta de Python y de las bibliotecas debe definirse por proyecto. Una actualización de entorno se trata como un cambio controlado y se valida contra la línea base.

#### Niveles de reproducibilidad

No todos los análisis pueden ni necesitan producir archivos idénticos byte a byte. Defina el nivel exigido:

| Nivel | Criterio |
|---|---|
| Numérico | Las magnitudes coinciden dentro de tolerancias justificadas |
| Funcional | Se obtienen los mismos casos críticos, verificaciones y conclusiones |
| Documental | Tablas, figuras y memoria contienen la misma información aprobada |
| Binario | Los artefactos tienen exactamente los mismos bytes y hashes |

Para controlar el determinismo registre, cuando corresponda, semilla aleatoria, hardware, precisión numérica, número de hilos, paralelismo, tolerancias del solver, locale, zona horaria, codificación, fuentes tipográficas y orden estable de filas o claves.

Separe la **identidad del contenido** de los metadatos variables. Un `content_id` puede derivarse de configuración, código y resultados normalizados; la fecha de compilación se guarda aparte. Si una imagen incorpora fecha o `run_id` variable, no se debe exigir identidad binaria salvo que esos metadatos también estén fijados.

### Fase 3 — Inventariar y jerarquizar las fuentes

**Objetivo:** impedir que un dato válido sea reemplazado por un ejemplo, una revisión antigua o una interpretación informal.

**Acciones:**

1. Inventariar planos, memorias, estudios, especificaciones, modelos, actas y normas.
2. Calcular un hash o identificador de revisión para cada fuente recibida.
3. Clasificar cada documento como:
   - contractual;
   - dato de proyecto;
   - criterio normativo;
   - referencia metodológica;
   - antecedente histórico;
   - ejemplo de validación.
4. Definir la precedencia cuando dos fuentes se contradigan.
5. Extraer solo las páginas, tablas y figuras necesarias a una carpeta curada.
6. Registrar toda contradicción; no resolverla mediante promedio ni selección silenciosa.

Formato sugerido para `fuentes/registro_fuentes.csv`:

| ID | Archivo | Revisión | Fecha | Tipo | Contenido usado | Localizador | Estado |
|---|---|---|---|---|---|---|---|
| F-001 | plano_general.pdf | R2 | AAAA-MM-DD | contractual | geometría | plano E-03, detalle 4 | vigente |
| F-002 | estudio_suelos.pdf | R0 | AAAA-MM-DD | dato | capacidad y perfil | pp. 45-48 | vigente |
| F-003 | ejemplo_diseno.pdf | — | AAAA-MM-DD | referencia | metodología | cap. 6 | no usar como entrada |

**Puerta de salida:** todos los datos críticos poseen una fuente vigente o están explícitamente marcados como supuestos pendientes.

#### Gobierno de datos y uso seguro de IA

Antes de cargar documentos en una herramienta de IA, conector o servicio externo:

1. clasificar la información como pública, interna, confidencial o restringida;
2. confirmar las condiciones contractuales, políticas del cliente y autorización de transferencia;
3. identificar datos personales, coordenadas sensibles, precios, firmas, credenciales y secretos;
4. aplicar redacción o anonimización cuando sea necesaria;
5. limitar el acceso por rol y principio de mínimo privilegio;
6. registrar qué archivos o extractos se transfirieron, a qué servicio y con qué finalidad;
7. definir retención, eliminación y respaldo;
8. respetar licencias y derechos de autor de normas, libros, planos y modelos;
9. evitar que claves, tokens o contraseñas entren al repositorio o al prompt;
10. conservar localmente una fuente autorizada de toda evidencia utilizada.

Cuando una fuente no pueda salir del entorno controlado, la IA debe trabajar con extractos aprobados o ejecutarse en una infraestructura autorizada. La eficiencia nunca justifica incumplir confidencialidad o propiedad intelectual.

### Fase 4 — Crear el registro maestro de entradas

**Objetivo:** tener un único conjunto de datos legible por personas y máquinas.

Cada entrada debe incluir:

- símbolo o identificador estable;
- descripción;
- valor;
- unidad;
- categoría;
- fuente y localizador;
- estado: `confirmado`, `calculado`, `asumido` o `pendiente`;
- responsable de aprobación;
- fecha y revisión;
- comentario o rango de validez;
- base del valor: media, nominal, característica, admisible o de diseño, cuando aplique;
- rango o incertidumbre;
- distribución probabilística y correlación, si el análisis las utiliza.

Ejemplo genérico en YAML:

```yaml
proyecto:
  id: estructura-ejemplo
  revision: R0
  norma:
    nombre: "Norma contractual"
    edicion: "AAAA"
  sistema_unidades: SI

geometria:
  luz_principal:
    valor: 30.0
    unidad: m
    fuente: F-001
    localizador: "plano E-03, eje 1-2"
    estado: confirmado

materiales:
  concreto_fc:
    valor: 28.0
    unidad: MPa
    fuente: F-004
    localizador: "especificación 03 30 00"
    estado: confirmado

supuestos:
  diafragma_rigido:
    valor: true
    justificacion: "Hipótesis del modelo global"
    estado: asumido
    requiere_aprobacion: true
```

No mantenga dos campos editables para una misma magnitud derivable. Por ejemplo, si una carga por unidad de longitud procede de una reacción total y un ancho, registre los datos fuente y calcule el cociente; no permita editar independientemente los tres.

**Validaciones mínimas:**

- unidades compatibles;
- valores finitos y rangos físicos;
- dimensiones positivas;
- cierres geométricos;
- coherencia entre cargas totales y distribuidas;
- compatibilidad entre materiales, secciones y norma;
- ausencia de parámetros críticos pendientes para una compilación final;
- nombres, ejes y apoyos inequívocos;
- separación entre datos confirmados y derivados.

### Fase 5 — Definir el modelo estructural antes de programar

**Objetivo:** evitar que el código o el software decidan implícitamente la idealización.

Documentar, como mínimo:

- geometría resistente e idealizaciones;
- apoyos, vínculos, liberaciones y continuidad;
- ejes globales y locales;
- rigidez efectiva, fisuración y no linealidad cuando correspondan;
- etapas constructivas y activación de elementos;
- condiciones de borde e interacción suelo-estructura;
- fuente de masas y peso propio automático;
- acciones, patrones, combinaciones y envolventes;
- convención de signos y puntos de referencia;
- método de análisis y límites de aplicabilidad;
- criterios de servicio, resistencia, estabilidad, fatiga y evento extremo;
- simplificaciones y efectos excluidos.

Para modelos en software comercial, registrar además:

- versión exacta y unidades activas;
- archivo de modelo y hash;
- origen geométrico y orientación;
- secciones, materiales y modificadores;
- mallado y estudio de convergencia;
- restricciones, diafragmas, links y resortes;
- casos de carga, solver y opciones de análisis;
- secuencia reproducible de extracción de resultados.

Un modelo no se considera validado porque “corrió sin errores”. Debe pasar equilibrio, deformada esperada, reacciones, orden de magnitud, sensibilidad y comparación con un modelo simplificado.

### Fase 6 — Resolver un caso patrón de forma independiente

**Objetivo:** disponer de una referencia técnica antes de automatizar todo.

**Acciones:**

1. Elegir un caso sencillo pero representativo.
2. Presentar ecuaciones generales antes de sustituir valores.
3. Resolverlo manualmente, en una hoja controlada o con una segunda formulación.
4. Guardar entradas, resultados intermedios y tolerancias.
5. Verificar dimensiones y equilibrio.
6. Convertirlo en un benchmark automatizado.

Un benchmark útil incluye valores como áreas, centroides, propiedades, cargas, reacciones, fuerzas internas, deformaciones, resistencias y relaciones demanda/capacidad. Una única cifra final no permite diagnosticar errores.

### Fase 7 — Diseñar una arquitectura de cálculo limpia

**Objetivo:** separar las decisiones técnicas de la presentación y de los archivos particulares del proyecto.

El núcleo debe seguir esta relación:

```text
Entradas validadas → cálculo puro → resultados tipados
```

Buenas prácticas:

- usar funciones puras siempre que sea posible;
- evitar variables globales mutables;
- mantener los valores particulares fuera del código;
- separar geometría, cargas, combinaciones y verificaciones;
- codificar las combinaciones como datos auditables, con referencia normativa;
- no leer ni escribir archivos dentro de las funciones numéricas;
- no redondear valores internos;
- devolver también los componentes y resultados intermedios;
- representar explícitamente demanda nominal, factorizada y resistencia de diseño;
- incluir una instantánea de las entradas dentro del resultado;
- usar adaptadores para Excel, APIs y programas externos;
- gestionar errores con mensajes técnicos y códigos de salida distintos de cero.

Una estructura monolítica que calcula, grafica y redacta en la misma función es rápida para un prototipo, pero costosa de revisar y reutilizar.

#### Si el motor principal es Excel o una hoja de cálculo

La misma arquitectura se puede aplicar aunque no se migre todo a Python. El libro debe tratarse como un motor de cálculo controlado:

- una hoja de portada y control de revisión;
- una hoja exclusiva de entradas con valor, unidad, fuente y estado;
- hojas de cálculo protegidas, sin datos de entrada escondidos dentro de fórmulas;
- rangos o tablas con nombres estables;
- una hoja de verificaciones con equilibrio, límites y mensajes de error;
- una hoja de resultados apta para exportación estructurada;
- ausencia de enlaces externos absolutos o, si son indispensables, un registro explícito de ellos;
- macros versionadas y firmadas cuando correspondan;
- motor y versión de recálculo registrados;
- comparación automática de celdas críticas contra el benchmark;
- exportación de resultados a CSV o JSON para alimentar figuras y memoria.

Los colores de celda ayudan a la lectura, pero no sustituyen los campos machine-readable `confirmado`, `asumido` o `pendiente`. Una celda crítica pendiente debe bloquear la emisión final.

#### Si el motor principal es un software estructural comercial

Mantenga el archivo nativo como fuente del análisis, pero automatice o documente de forma inequívoca su preparación y extracción. Un adaptador debe transformar la configuración aprobada en entradas del modelo —cuando la API lo permita— y convertir la salida del solver en el mismo esquema canónico de resultados. Las tablas de la memoria no deben copiarse manualmente desde la interfaz gráfica.

### Fase 8 — Implementar mediante ciclos cortos de Videocoding

**Objetivo:** aprovechar la velocidad de la IA sin perder control técnico.

Cada ciclo debe contener:

1. una tarea pequeña y delimitada;
2. los archivos y fuentes autorizados;
3. ecuaciones o criterios de aceptación;
4. una lista de archivos que se pueden modificar;
5. pruebas que deben pasar;
6. revisión del diff;
7. ejecución y comparación;
8. un commit lógico.

Secuencia recomendada para cada módulo:

```text
Inspeccionar → reconstruir el método → proponer el cambio
→ implementar → probar → comparar → revisar → registrar decisión
```

No pida “haz todo el diseño” si el proyecto tiene datos o criterios todavía inestables. Divida por bloques independientes: geometría, materiales, cargas, análisis, combinaciones, verificaciones, figuras y memoria.

#### Plantilla de prompt para implementación

```text
Rol: actúa como ingeniero estructural y desarrollador revisor.

Objetivo: implementar únicamente [módulo o verificación].

Fuentes autorizadas:
- [archivo, revisión, página o sección]
- [criterio normativo y edición]

Entradas:
- leerlas desde [archivo maestro]; no crear valores faltantes.

Convenciones:
- unidades: [...]
- signos/ejes: [...]
- etapa o estado límite: [...]

Restricciones:
- no modificar [archivos fuera de alcance];
- no redondear dentro del motor;
- no inventar referencias normativas;
- conservar cambios existentes no relacionados.

Criterios de aceptación:
- ecuación o resultado patrón [...];
- equilibrio/tolerancia [...];
- pruebas [...];
- salida esperada [...].

Antes de editar, reconstruye el procedimiento actual y señala cualquier contradicción.
Después de editar, ejecuta las pruebas y resume el resultado.
```

#### Plantilla de prompt para extracción de datos

```text
Inspecciona las fuentes en modo solo lectura.
Extrae únicamente [categoría de datos].
Para cada valor informa símbolo, valor, unidad, archivo, revisión,
página/cuadro/detalle, estado y cualquier contradicción.
Separa datos del proyecto, datos de referencia y resultados calculados.
No resuelvas contradicciones ni modifiques archivos.
```

#### Plantilla de prompt para revisión independiente

```text
Revisa [módulo/resultado] como auditor independiente.
Reconstruye el cálculo sin asumir que el resultado es correcto.
Comprueba unidades, signos, equilibrio, orden de magnitud,
hipótesis, combinación, estado límite y fuente normativa.
Clasifica hallazgos como Crítico, Importante, Menor o Recomendación.
No implementes correcciones; presenta el efecto y el recálculo clave.
```

### Fase 9 — Construir una estrategia de pruebas

**Objetivo:** demostrar corrección matemática, coherencia física y estabilidad del resultado.

| Nivel | Qué comprueba | Ejemplos |
|---|---|---|
| Validación de entrada | Calidad y coherencia | unidades, rangos, geometría cerrada, datos confirmados |
| Unitario | Una ecuación o función | propiedades de sección, coeficientes, resistencias |
| Propiedad/invariante | Ley física o matemática | equilibrio, simetría, conservación, monotonía |
| Benchmark | Caso resuelto por otra vía | manual, literatura, hoja independiente |
| Regresión | Conservación de línea base | valores aprobados con tolerancias |
| Integración | Flujo entre módulos | entrada → análisis → verificación |
| Interfaz de solver | Correspondencia con software | unidades, ejes, casos, resultados exportados |
| Sensibilidad | Respuesta razonable | variación de rigidez, carga, malla o parámetros |
| Visual | Calidad de figuras | textos, escalas, signos, lados, unidades |
| Reproducibilidad | Nivel acordado entre ejecuciones | tolerancia numérica, función, contenido o identidad binaria |

Pruebas indispensables para cualquier estructura:

- suma de cargas y reacciones;
- equilibrio global de fuerzas y momentos;
- deformada compatible con apoyos y cargas;
- orden de magnitud mediante solución simplificada;
- signos y ejes locales;
- combinaciones completas y sin duplicación;
- valores límite y entradas inválidas;
- comparación demanda/capacidad con magnitudes compatibles;
- confirmación de que una modificación esperada produce una tendencia física razonable;
- comparación de resultados crudos, no solo de textos redondeados.

Las tolerancias deben combinar un término absoluto y otro relativo cuando corresponda. Deben justificarse por método numérico, discretización y precisión de los datos; no elegirse solo para que la prueba pase.

### Fase 10 — Crear un resultado canónico

**Objetivo:** impedir que cada tabla o figura vuelva a calcular una versión distinta.

Una compilación exitosa debe producir un manifiesto canónico, por ejemplo `build/results.json`, que contenga o referencie todos los resultados aprobados:

```json
{
  "schema_version": "1.0",
  "run": {
    "content_id": "sha256:...",
    "created_at": "2026-07-11T16:00:00-05:00",
    "release_revision": "R0",
    "config_hash": "...",
    "code_commit": "...",
    "environment": "..."
  },
  "inputs": {},
  "assumptions": [],
  "raw_results": {},
  "display_results": {},
  "datasets": [],
  "checks": [],
  "warnings": [],
  "artifacts": []
}
```

`raw_results` conserva la máxima precisión disponible. `display_results` aplica el contrato de redondeo. Las figuras, CSV, tablas Markdown y memoria leen ese manifiesto o el mismo objeto inmutable en memoria.

JSON es adecuado para metadatos y resultados pequeños. Un modelo FEM grande, una historia temporal o un análisis probabilístico puede requerir HDF5, Parquet, una base de datos o el formato nativo del solver. En ese caso, `results.json` funciona como manifiesto: referencia cada dataset mediante ruta relativa, formato, esquema, tamaño y hash.

La configuración y los resultados deben declarar `schema_version`. Todo cambio incompatible necesita una regla de migración o una nueva versión; no se deben reinterpretar silenciosamente artefactos antiguos.

El resultado debe indicar qué verificaciones no se realizaron. La ausencia de una comprobación no equivale a cumplimiento.

### Fase 11 — Automatizar figuras, tablas y memoria

**Objetivo:** que todos los entregables representen exactamente la misma corrida.

**Orden correcto:**

1. validar entradas;
2. ejecutar el análisis una vez;
3. realizar auditorías numéricas;
4. exportar el resultado canónico;
5. generar tablas y figuras;
6. componer la memoria desde plantilla;
7. renderizar el documento final;
8. ejecutar QA visual y documental.

Las figuras deben:

- usar escalas y ejes declarados;
- mostrar unidades y convención de signos;
- distinguir valores nominales, factorizados y de diseño;
- derivar posiciones desde la geometría, no de coordenadas fijas;
- incluir revisión y un `content_id` corto cuando sean entregables;
- fallar si los datos del caso no pasan la auditoría;
- ser revisadas visualmente después del renderizado.

La memoria se genera desde una plantilla y debe incluir:

- alcance y exclusiones;
- registro de datos y fuentes;
- hipótesis del modelo;
- norma y edición;
- ecuaciones y criterios;
- resultados intermedios relevantes;
- verificaciones y relaciones demanda/capacidad;
- figuras de la misma corrida;
- supuestos, pendientes y limitaciones;
- revisión, fecha, responsable y manifiesto.

### Fase 12 — Orquestar todo con un único comando

**Objetivo:** sustituir una secuencia manual y frágil por una compilación repetible.

Interfaz ideal:

```powershell
python -m proyecto_estructural validate --config config/proyecto.yaml
python -m pytest
python -m proyecto_estructural build --config config/proyecto.yaml --out build
python -m proyecto_estructural qa --manifest build/manifest.json
```

Cuando el proceso sea estable, puede exponerse como:

```powershell
python -m proyecto_estructural release --config config/proyecto.yaml
```

El comando `release` debe:

1. comprobar que el árbol y la configuración están identificados;
2. validar datos y estados de aprobación;
3. ejecutar pruebas rápidas antes de generar productos;
4. ejecutar una sola compilación canónica, incluidas sus subcorridas controladas;
5. contrastar la línea base cuando aplique;
6. generar los artefactos en una carpeta temporal;
7. ejecutar QA numérico, documental y visual;
8. crear el manifiesto;
9. promover atómicamente la carpeta temporal a `entregables/` solo si todo pasa;
10. devolver un código distinto de cero ante cualquier fallo.

Así se evita dejar una entrega parcialmente actualizada cuando una etapa falla.

#### Integración continua y compilación independiente

Además de la ejecución local, configure una compilación automática desde un checkout limpio:

- ramas protegidas y revisión obligatoria;
- validación de esquema, formato y pruebas en cada cambio;
- comparación de regresión contra la línea base;
- generación de un paquete de revisión sin publicarlo automáticamente;
- publicación solo desde una etiqueta o revisión autorizada;
- firma o hash del paquete emitido;
- conservación de logs y evidencia de las pruebas;
- fallo de la emisión si el árbol está sucio o si no se puede identificar exactamente el parche.

La integración continua no aprueba la ingeniería; demuestra que el proceso configurado es repetible en un entorno distinto del equipo del autor.

#### Puerta manual para software no automatizable

Algunos solvers requieren licencia flotante, interfaz gráfica, hardware particular o intervención de un operador. En esos casos, el comando único puede detenerse en una puerta formal y generar una solicitud de ejecución. Para continuar se debe registrar:

- operador y fecha;
- versión, licencia y opciones del solver;
- hash del modelo de entrada;
- procedimiento seguido;
- logs, capturas o archivo de evidencia requerido;
- exportación estructurada de resultados;
- hash de la salida;
- revisión de unidades, ejes y casos.

Una vez aceptada esa evidencia, el resto del pipeline continúa automáticamente desde la salida importada. La intervención manual debe ser controlada, no informal.

### Fase 13 — Revisar y publicar

**Objetivo:** separar “el programa terminó” de “la ingeniería está aprobada”.

La revisión debe cubrir cuatro capas:

1. **Datos:** trazabilidad, vigencia, unidades y supuestos.
2. **Modelo:** idealización, rigidez, apoyos, etapas y límites.
3. **Cálculo:** ecuaciones, combinaciones, equilibrio y verificaciones.
4. **Entregable:** coherencia entre memoria, tablas, figuras, modelo y planos.

El manifiesto de publicación debe registrar:

- `content_id`, `schema_version` y revisión de emisión;
- fecha y zona horaria;
- revisión del proyecto;
- hash de configuración y fuentes principales;
- commit del código;
- versiones del entorno y solver;
- comandos ejecutados;
- pruebas y controles superados;
- lista y hash de artefactos;
- advertencias abiertas;
- herramienta o modelo de IA utilizado en cada cambio relevante, objetivo, archivos afectados, pruebas ejecutadas y revisor humano;
- estado del árbol de trabajo; una emisión normal debe proceder de un commit limpio y una excepción debe incorporar el parche exacto;
- responsable y revisor.

Una entrega aprobada se copia a una carpeta inmutable o se etiqueta en el sistema de control documental. Los archivos de `build/` siguen siendo reemplazables.

#### Preservación a largo plazo

Una carpeta marcada como inmutable no garantiza que el proyecto pueda recuperarse dentro de varios años. La política de archivo debe definir:

- ubicación primaria y respaldo independiente;
- periodo de retención contractual;
- prueba periódica de restauración;
- hashes y control de integridad;
- fuentes, configuración, resultados, memoria, planos y manifiesto que deben conservarse;
- imagen de contenedor, entorno o instrucciones suficientes para reconstruirlo;
- inventario de componentes de software —SBOM cuando corresponda—;
- disponibilidad futura de instaladores, complementos, licencias y llaves del solver;
- formatos abiertos de intercambio para resultados esenciales;
- estrategia de migración cuando un formato o software quede obsoleto.

El archivo debe permitir comprender el resultado aun cuando el programa original ya no esté disponible.

### Fase 14 — Gestionar cambios

**Objetivo:** conocer por qué cambió un resultado y qué partes deben recalcularse.

Clasifique cada modificación:

| Tipo | Ejemplo | Tratamiento |
|---|---|---|
| Entrada | cambio de geometría o material | nueva configuración y corrida completa afectada |
| Criterio | nueva interpretación normativa | decisión aprobada, nueva revisión y comparación |
| Modelo | cambio de apoyo o rigidez | revalidación técnica y de benchmarks |
| Corrección | error de fórmula | preservar legacy, documentar impacto y emitir revisión |
| Presentación | color o formato | comprobar que no cambia el resultado canónico |
| Entorno | actualización de solver o biblioteca | regresión contra baseline |

Nunca modifique directamente una cifra en la memoria para “hacerla coincidir”. La corrección debe propagarse desde la fuente adecuada.

## 8. Cómo migrar profesionalmente un proyecto ya terminado

Esta es la secuencia recomendada para reorganizar un proyecto existente sin cambiar inicialmente sus resultados:

1. Hacer inventario de fuentes, código, hojas, modelos, tablas, figuras y memorias.
2. Identificar todas las versiones que hoy se llaman “final”.
3. Seleccionar y aprobar una línea base única.
4. Capturar entradas, resultados intermedios, resultados finales y redondeos.
5. Escribir pruebas de regresión que reproduzcan la línea base.
6. Extraer los parámetros hardcodeados a una configuración versionada.
7. Añadir validaciones sin modificar todavía el algoritmo.
8. Separar el motor numérico de archivos, gráficos y reportes.
9. Eliminar globales y duplicaciones conservando las pruebas en verde.
10. Orquestar una compilación canónica y exportar su manifiesto de resultados; las subcorridas necesarias quedan dentro de esa ejecución controlada.
11. Hacer que tablas y figuras consuman ese mismo resultado.
12. Generar la memoria desde una plantilla.
13. Añadir verificaciones independientes y pruebas de sensibilidad.
14. Crear un comando único de compilación y un manifiesto.
15. Comparar automáticamente el paquete nuevo con la línea base.
16. Tratar por separado las correcciones técnicas detectadas.
17. Emitir una nueva revisión solo después de la aprobación del ingeniero.

El orden es importante: **primero se congela el comportamiento; luego se mejora la arquitectura; finalmente se corrige la ingeniería en una revisión explícita**.

## 9. Antipatrones y su reemplazo

| Antipatrón | Problema | Reemplazo profesional |
|---|---|---|
| Datos dentro del script | cambios invisibles y duplicación | configuración validada con fuentes |
| Memoria como calculadora manual | cifras desactualizadas | plantilla alimentada por resultados |
| Varias carpetas `final`, `final2` | no existe revisión inequívoca | `content_id`, revisión, manifiesto y etiqueta |
| Auditoría con la misma función | confirma coherencia consigo misma | benchmark o formulación independiente |
| Redondear antes de combinar | acumula error | máxima precisión disponible + capa de presentación |
| Figuras que recalculan | versiones distintas | figuras que consumen el manifiesto canónico |
| Generar y luego validar | deja artefactos parciales | validar primero y publicar atómicamente |
| Un script monolítico | difícil de probar y reutilizar | módulos puros y adaptadores |
| Coordenadas gráficas fijas | fallan al cambiar geometría | layout derivado y QA visual |
| Valores `None` con defaults ocultos | decisiones técnicas silenciosas | dato explícito o derivación auditada |
| Copiar cargas entre disciplinas | pierde versión, signo y etapa | archivo de interfaz versionado |
| Versionar cachés y temporales | repositorio pesado y confuso | `.gitignore` y almacenamiento adecuado |
| Rutas absolutas del equipo | falta de portabilidad | rutas relativas a la raíz |
| Pedir a la IA cambios masivos | difícil revisión | ciclos pequeños con pruebas |
| Declarar “cumple” con pendientes | falsa sensación de cierre | matriz de alcance y verificaciones |

## 10. Interfaz entre disciplinas y modelos

En proyectos con varios modelos, cada transferencia debe ser un contrato de datos. Por ejemplo, las reacciones entregadas por superestructura a cimentaciones deben incluir:

- estructura, apoyo y coordenadas;
- ejes y convención de signos;
- fuerza o momento y unidad;
- caso, combinación o envolvente;
- valor máximo y mínimo;
- simultaneidad de componentes;
- etapa constructiva;
- condición de servicio, resistencia o evento extremo;
- versión del modelo fuente;
- fecha, responsable y estado de aprobación.

El archivo de interfaz debe ser legible por el modelo consumidor. Evite copiar números desde capturas de pantalla o PDF si el software permite exportación estructurada.

## 11. Contexto eficiente para trabajar con IA

La IA trabaja mejor con un paquete pequeño y autoritativo que con miles de archivos sin jerarquía. Al iniciar una sesión, proporcione:

1. `README.md`;
2. alcance y criterios;
3. configuración aprobada;
4. registro de decisiones y supuestos;
5. módulo que se desea modificar;
6. pruebas y benchmark pertinentes;
7. fuentes exactas necesarias para la tarea.

No es eficiente releer todos los PDF en cada iteración. Extraiga una vez los fragmentos necesarios, consérvelos con referencia a la fuente y haga que la IA consulte el original solo ante dudas o cambios de revisión.

Para tareas independientes —por ejemplo, geometría, cargas y revisión normativa— se pueden usar agentes en paralelo. La consolidación final debe realizarse contra el registro maestro, evitando que cada agente introduzca su propio conjunto de datos.

## 12. Qué no se debe delegar por completo

- selección definitiva de la norma y edición;
- interpretación contractual;
- aceptación de una contradicción entre fuentes;
- elección de un modelo que cambie el comportamiento resistente;
- aprobación de parámetros geotécnicos o sísmicos;
- omisión de estados límite;
- decisión de constructibilidad o secuencia temporal crítica;
- clasificación de un detalle de fatiga o ductilidad sin revisión;
- aceptación de resultados por el solo hecho de provenir de software;
- firma y declaración final de cumplimiento.

## 13. Lista de aceptación de una entrega

### Entradas

- [ ] Norma y edición confirmadas.
- [ ] Sistema de unidades y signos documentados.
- [ ] Datos críticos con fuente y localizador.
- [ ] Supuestos explícitos y aprobados.
- [ ] Geometría cerrada y validada.
- [ ] Interfaz entre disciplinas versionada.
- [ ] No existen parámetros críticos pendientes.
- [ ] Configuración identificada por hash y revisión.
- [ ] Clasificación, confidencialidad, licencias y autorización de uso con IA verificadas.

### Modelo y cálculo

- [ ] Idealización estructural documentada.
- [ ] Apoyos, ejes, liberaciones y etapas revisados.
- [ ] Peso propio y masas comprobados.
- [ ] Combinaciones trazables a la norma adoptada.
- [ ] Precisión interna sin redondeo prematuro.
- [ ] Equilibrio de fuerzas y momentos satisfactorio.
- [ ] Deformada y orden de magnitud razonables.
- [ ] Benchmark independiente superado.
- [ ] Pruebas unitarias, integración y regresión superadas.
- [ ] Sensibilidad o convergencia revisada cuando corresponde.

### Verificaciones técnicas

- [ ] Demandas y capacidades usan bases compatibles.
- [ ] Se revisaron todos los estados límite incluidos en el alcance.
- [ ] Se distinguieron etapas constructivas cuando afectan el resultado.
- [ ] Se documentaron exclusiones y verificaciones pendientes.
- [ ] El estado “cumple/no cumple” deriva de reglas auditables.
- [ ] Los casos críticos fueron recalculados por una vía independiente.

### Entregables

- [ ] Tablas, figuras y memoria proceden del mismo `content_id` y revisión.
- [ ] Ningún resultado generado fue editado manualmente.
- [ ] Las figuras muestran unidades, escalas y signos correctos.
- [ ] El documento final fue renderizado y revisado visualmente.
- [ ] Los enlaces, referencias, ecuaciones y numeración son correctos.
- [ ] La memoria coincide con el modelo y los planos.
- [ ] Existe un manifiesto de artefactos.
- [ ] La asistencia de IA relevante tiene objetivo, alcance, pruebas y revisor registrados.

### Reproducibilidad y publicación

- [ ] El entorno y las dependencias están bloqueados.
- [ ] Un único comando reconstruye la entrega o activa una puerta manual formal y reproducible.
- [ ] La ejecución fue probada en un entorno limpio.
- [ ] El nivel exigido de reproducibilidad —numérico, funcional, documental o binario— está definido y comprobado.
- [ ] Semillas, paralelismo, locale y tolerancias del solver están registrados cuando afectan el resultado.
- [ ] El repositorio no contiene cachés ni temporales accidentales.
- [ ] La compilación independiente o CI superó sus controles.
- [ ] El árbol o commit de publicación está identificado.
- [ ] Respaldo, retención y restauración del paquete están definidos.
- [ ] Responsable y revisor aprobaron la revisión.

## 14. Indicadores de eficiencia y calidad

Conviene medir:

- tiempo desde un cambio de entrada hasta una memoria actualizada;
- número de transcripciones manuales de resultados —objetivo: cero—;
- porcentaje de entradas críticas con fuente completa —objetivo: 100 %—;
- cobertura de módulos críticos por benchmarks;
- recálculos iniciados por tablas o figuras —objetivo: cero—;
- subcorridas del solver documentadas y orquestadas por una única compilación canónica;
- divergencias entre memoria, tablas y figuras —objetivo: cero—;
- capacidad de reconstrucción en un equipo limpio;
- cantidad de advertencias o supuestos abiertos al publicar;
- tiempo de revisión del diff por cambio;
- número de hallazgos detectados antes de la emisión.

## 15. Aplicación de las lecciones del presente proyecto

El proyecto actual ya contiene componentes valiosos: un motor central de análisis, generadores parametrizados de figuras, una auditoría de equilibrio, una memoria viva y un registro de decisiones. La siguiente evolución profesional debe concentrarse en unirlos mediante una fuente de verdad y una compilación única.

Las lecciones generalizables observadas son:

1. El código operativo puede separarse de la memoria y terminar representando otra revisión.
2. Una auditoría interna puede pasar aunque la memoria, la geometría o el criterio técnico hayan cambiado.
3. Los archivos denominados “final” no sustituyen un `content_id`, una revisión ni un manifiesto.
4. Recalcular para cada figura desperdicia tiempo y permite divergencias.
5. Los ejemplos metodológicos deben estar aislados de las entradas del proyecto.
6. Un cambio de método de presión, rigidez, combinación o brazo de aplicación debe tratarse como decisión técnica, no como ajuste gráfico.
7. Las dependencias, el entorno y los archivos generados también forman parte de la reproducibilidad.

Por ello, antes de refactorizar este u otro proyecto terminado, se debe seleccionar formalmente la revisión que constituye la línea base. Solo después se pueden garantizar “los mismos resultados” durante la modernización.

## 16. Secuencia resumida para futuros proyectos

1. Definir alcance, norma, unidades, entregables y aceptación.
2. Preparar repositorio, entorno reproducible y control documental.
3. Inventariar y jerarquizar fuentes.
4. Crear un registro único de entradas trazables.
5. Resolver contradicciones mediante decisiones registradas.
6. Validar entradas, geometría y unidades.
7. Documentar la idealización estructural.
8. Resolver un benchmark independiente.
9. Implementar el motor por módulos pequeños.
10. Construir pruebas unitarias, físicas, de integración y regresión.
11. Orquestar una compilación canónica, con todas las subcorridas necesarias controladas.
12. Exportar un resultado canónico.
13. Generar tablas, figuras y memoria desde ese resultado.
14. Ejecutar QA numérico, técnico, visual y documental.
15. Crear manifiesto, revisar, aprobar y publicar.
16. Gestionar todo cambio como una nueva revisión trazable.

Si este flujo se respeta, el Videocoding deja de ser una sucesión de prompts y se convierte en un proceso de ingeniería: rápido para iterar, estricto para verificar y suficientemente claro para ser auditado y reutilizado.

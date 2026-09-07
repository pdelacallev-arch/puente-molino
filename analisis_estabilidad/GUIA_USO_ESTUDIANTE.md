# Guía de uso del sistema de análisis de estabilidad

## 1. ¿Para qué sirve este sistema?

`analisis_estabilidad` reúne los cálculos del estribo izquierdo del Puente
Molinohuayco. El sistema permite analizar cada elemento estructural por
separado, pero conserva la relación física entre ellos mediante archivos de
entrada y salida verificables.

La idea central es sencilla:

1. El estudiante define la geometría, los materiales y las cargas una sola vez.
2. El programa calcula primero los resultados que sirven de base.
3. Los demás elementos consumen esos resultados automáticamente.
4. Cada cálculo conserva su entrada, resultado, reporte y trazabilidad.

Este sistema ayuda a evitar dos problemas frecuentes en trabajos académicos y
profesionales: volver a escribir el mismo dato en varios programas y perder la
relación entre un resultado intermedio y el cálculo que lo utilizó.

> **Alcance técnico.** Los programas apoyan el análisis y la verificación, pero
> no reemplazan el criterio del ingeniero responsable. Antes de usar los
> resultados en planos o construcción deben contrastarse con el expediente, el
> estudio de suelos, el modelo completo y la normativa vigente.

## 2. Modelo mental: entradas, proceso y salidas

Cada cálculo se puede entender como una función:

```text
entrada propia + resultados de dependencias → cálculo → resultado + reporte
```

Por ejemplo, la zapata no necesita repetir el análisis global del estribo. Su
archivo `entrada.json` indica dónde está el resultado de estabilidad que debe
consumir y cuál es su huella SHA-256. Antes de calcular, el sistema comprueba
que el archivo no haya sido modificado.

### Flujo estructural implementado

```text
                         ┌─→ pantalla: shell 3D
                         ├─→ pantalla: diseño E.060/MTC
estribo: estabilidad ────┼─→ zapata: diseño longitudinal
global                   ├─→ zapata: diseño transversal
                         ├─→ dentellón: diseño E.060
                         ├─→ cajuela: verificación del voladizo
                         └─→ pantalla: reacciones para contrafuertes
                                      ↓
                            contrafuertes: análisis 2D
                                      ↓
                            contrafuertes: diseño STM
```

La flecha significa «el cálculo de la derecha consume el resultado del cálculo
de la izquierda». No representa solamente un orden conveniente de ejecución,
sino una dependencia técnica.

## 3. Organización de carpetas

```text
analisis_estabilidad/
├── casos/                   # Entradas y ejecuciones reproducibles
│   └── molinohuayco/
│       └── R00/
│           ├── entrada.yaml
│           ├── entradas/    # Overrides JSON opcionales
│           └── ejecuciones/ # Resultados ordenados por fecha
├── elementos/
│   ├── estribo/
│   ├── pantalla/
│   ├── contrafuertes/
│   ├── zapata/
│   ├── dentellon/
│   └── cajuela/
├── nucleo/                  # Configuración, contratos y orquestación
├── pruebas/                 # Pruebas automáticas
├── historico/               # Resultados del sistema anterior
├── documentos/
└── .tmp/                    # Pruebas o ejecuciones temporales
```

Los archivos de `historico/` sirven como referencia, pero no tienen los mismos
contratos ni garantías de reproducibilidad del sistema actual.

## 4. Requisitos y preparación

Los ejemplos siguientes están escritos para PowerShell y deben ejecutarse
desde la raíz del proyecto:

```text
D:\TRABAJOS\PUENTE AYACUCHO\VIDECOD PUENTE MOLINO
```

Se requiere:

- Python 3.10 o posterior.
- `uv` para administrar el entorno y las dependencias.
- Las bibliotecas declaradas en `pyproject.toml`.

Para preparar el entorno de ejecución:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv sync
```

Para incluir también las dependencias de pruebas:

```powershell
uv sync --extra dev
```

La variable `UV_CACHE_DIR` mantiene la caché dentro del proyecto y evita que los
archivos auxiliares se mezclen con los resultados estructurales.

## 5. La entrada maestra `entrada.yaml`

La configuración vigente del caso de ejemplo está en:

```text
analisis_estabilidad/casos/molinohuayco/R00/entrada.yaml
```

Sus secciones principales son:

| Sección | Contenido |
|---|---|
| `proyecto` | Identificador, nombre, revisión y responsable |
| `normativa` | Documentos normativos declarados para el cálculo |
| `unidades` | Sistema general de unidades |
| `datos_comunes` | Materiales, cargas de superestructura y sismo |
| `elementos` | Parámetros particulares de cada elemento y cálculo |
| `trazabilidad` | Fuente y estado de verificación de los datos |

Ejemplo simplificado:

```yaml
proyecto:
  id: molinohuayco
  revision: R00

unidades: MKS

datos_comunes:
  materiales:
    gamma_c: 2.40
    f_c: 280.0

elementos:
  zapata:
    diseno_longitudinal_e060:
      recubrimiento_mm: 100.0
      ancho_franja_m: 1.0
```

### Atención con las unidades

Aunque el contrato general se identifica como `MKS`, varios parámetros
históricos expresan explícitamente su unidad en el nombre:

- `_m`: metros.
- `_mm`: milímetros.
- `_kg_cm2` o `_kgf_cm2`: kgf/cm².
- `_tf_m3`: tf/m³.
- `_tf_m`: tf·m.
- `_grados`: grados sexagesimales.

No convierta un valor sólo por intuición. Revise el nombre completo del campo,
el reporte generado y la formulación del módulo. Un error de unidades puede
producir resultados numéricamente válidos pero físicamente incorrectos.

### Recomendaciones al editar el YAML

1. Cambie un grupo pequeño de parámetros cada vez.
2. Mantenga la indentación con espacios; YAML depende de ella.
3. No cambie los nombres de las claves.
4. No escriba unidades dentro del valor: use `100.0`, no `100 mm`.
5. Registre la fuente del dato en `trazabilidad`.
6. Ejecute `validar` antes de iniciar los cálculos.

## 6. Primer recorrido completo

### Paso 1: validar la configuración

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_estabilidad validar `
  --caso molinohuayco `
  --revision R00
```

Una respuesta correcta tiene esta forma:

```json
{
  "estado": "VALIDA",
  "proyecto": "molinohuayco",
  "revision": "R00",
  "sha256": "..."
}
```

La huella `sha256` identifica exactamente el contenido de la configuración.

### Paso 2: ejecutar todo el sistema

```powershell
uv run python -m analisis_estabilidad ejecutar todo `
  --caso molinohuayco `
  --revision R00
```

El orquestador resuelve automáticamente las dependencias y crea una carpeta
como:

```text
casos/molinohuayco/R00/ejecuciones/20260907T084847-0500/
```

El identificador representa fecha, hora y zona horaria. Dentro se conserva la
configuración resuelta y una carpeta para cada cálculo.

### Paso 3: consolidar

```powershell
uv run python -m analisis_estabilidad consolidar `
  --caso molinohuayco `
  --revision R00
```

Esto crea `consolidado.json`, un índice resumido de los estados, advertencias y
resultados de todos los módulos ejecutados.

### Paso 4: consultar el estado

```powershell
uv run python -m analisis_estabilidad estado `
  --caso molinohuayco `
  --revision R00
```

El comando muestra `manifiesto.json`. Allí puede verificar qué módulos se
ejecutaron, dónde están sus archivos y cuál es la huella de cada resultado.

## 7. Ejecutar solamente un elemento

No es necesario ejecutar manualmente los cálculos previos. Por ejemplo:

```powershell
uv run python -m analisis_estabilidad ejecutar contrafuertes.diseno `
  --caso molinohuayco `
  --revision R00
```

El sistema ejecutará esta cadena si sus resultados aún no existen:

```text
estabilidad global → reacciones de pantalla → análisis 2D → diseño STM
```

### Nombres disponibles

| Objetivo corto | Cálculo ejecutado |
|---|---|
| `estribo.estabilidad` | Estabilidad global e interfaces |
| `pantalla.shell` | Modelo shell 3D |
| `pantalla.reacciones` | Reacciones transferidas a contrafuertes |
| `pantalla.diseno` | Diseño E.060/MTC de la pantalla |
| `contrafuertes.analisis` | Análisis bidimensional |
| `contrafuertes.diseno` | Diseño mediante bielas y tirantes (STM) |
| `zapata.longitudinal` | Diseño longitudinal de la zapata |
| `zapata.transversal` | Diseño transversal de la zapata |
| `dentellon.diseno` | Diseño E.060 del dentellón |
| `cajuela.verificacion` | Verificación del voladizo de cajuela |
| `todo` | Todos los cálculos anteriores |

## 8. Preparar una entrada sin ejecutar el cálculo objetivo

El comando `preparar` genera el `entrada.json` de un objetivo. También ejecuta
las dependencias necesarias para poder referenciarlas de forma válida:

```powershell
uv run python -m analisis_estabilidad preparar zapata.longitudinal `
  --caso molinohuayco `
  --revision R00
```

Esto es útil para estudiar exactamente qué recibirá el módulo antes de
ejecutarlo. Abra el archivo indicado por la respuesta y revise:

- `parametros`: datos propios del cálculo.
- `dependencias`: resultados externos que consumirá.
- `trazabilidad`: huellas y fuentes de datos.

## 9. Usar un override JSON

Un override permite modificar temporalmente los parámetros de un solo cálculo
sin duplicar todo el YAML maestro.

Para cambiar el recubrimiento de la zapata longitudinal, cree:

```text
casos/molinohuayco/R00/entradas/zapata/diseno_longitudinal_e060.override.json
```

con el contenido:

```json
{
  "recubrimiento_mm": 110.0
}
```

El valor `110.0` tendrá prioridad sobre el valor del YAML. Los campos no
mencionados conservarán sus valores originales.

Para la estabilidad global del estribo, el contrato agrupa varios conjuntos de
datos. Un override de geometría tendría esta forma:

```text
casos/molinohuayco/R00/entradas/estribo/estabilidad_global.override.json
```

```json
{
  "geometria": {
    "B": 12.80
  }
}
```

La huella del override queda guardada en el `entrada.json`. De este modo siempre
puede comprobarse si el cálculo utilizó solamente el YAML o también un ajuste.

> Un override no debe convertirse en un cambio oculto permanente. Si el dato ya
> fue aprobado para toda la revisión, incorpórelo al YAML maestro y documente su
> fuente.

## 10. Continuar o iniciar una ejecución nueva

El sistema calcula una huella combinada de la configuración y del código.

- Si ambos permanecen iguales, reutiliza la ejecución compatible más reciente.
- Si cambia el YAML, un override o el código, crea una nueva carpeta fechada.
- Si desea forzar una nueva carpeta aun sin cambios, use
  `--nueva-ejecucion`.

Ejemplo:

```powershell
uv run python -m analisis_estabilidad ejecutar todo `
  --caso molinohuayco `
  --revision R00 `
  --nueva-ejecucion
```

No edite manualmente los archivos de una ejecución terminada. Para estudiar una
variante, cambie la entrada maestra, utilice un override o cree una nueva
revisión.

## 11. Ejecutar un paquete de forma independiente

Cada carpeta de elemento posee una interfaz de bajo nivel con `--entrada` y
`--salida`. Ejemplo para la zapata:

```powershell
uv run python -m analisis_estabilidad.elementos.zapata `
  diseno_longitudinal_e060 `
  --entrada analisis_estabilidad/casos/molinohuayco/R00/ejecuciones/<id>/elementos/zapata/diseno_longitudinal_e060/entrada.json `
  --salida analisis_estabilidad/.tmp/zapata_independiente
```

Reemplace `<id>` por el nombre real de una ejecución.

Esta modalidad es útil para:

- aprender qué hace un módulo aislado;
- depurar un cálculo;
- repetir el cálculo usando exactamente la misma entrada;
- comprobar que las conexiones no dependen de variables ocultas.

La salida debe permanecer dentro de `analisis_estabilidad/`. El sistema rechaza
rutas externas para evitar resultados dispersos.

### Interfaces independientes

| Paquete | Argumentos de cálculo admitidos |
|---|---|
| `analisis_estabilidad.elementos.estribo` | `estabilidad_global` |
| `analisis_estabilidad.elementos.pantalla` | `analisis_shell_3d`, `reacciones_contrafuertes`, `diseno_e060_mtc` |
| `analisis_estabilidad.elementos.contrafuertes` | `analisis_2d`, `diseno_stm` |
| `analisis_estabilidad.elementos.zapata` | `diseno_longitudinal_e060`, `diseno_transversal_e060_mtc` |
| `analisis_estabilidad.elementos.dentellon` | `diseno_e060` |
| `analisis_estabilidad.elementos.cajuela` | `verificacion_voladizo` |

## 12. Cómo leer los archivos de una ejecución

Cada cálculo genera:

```text
elementos/<elemento>/<calculo>/
├── entrada.json
├── resultado.json
├── reporte.md
└── figuras/
    ├── *.png
    └── *.svg
```

Las figuras se generan a partir del mismo resultado estructural y no mediante
un segundo cálculo. El campo `archivos_generados` permite comprobar cuáles
pertenecen exactamente a esa ejecución.

### `entrada.json`

Contiene la entrada inmutable que recibió el programa:

| Campo | Significado |
|---|---|
| `version_esquema` | Versión del contrato de intercambio |
| `ejecucion_id` | Ejecución a la que pertenece |
| `elemento`, `calculo` | Identidad del módulo |
| `unidades` | Sistema general declarado |
| `parametros` | Datos propios resueltos después del override |
| `dependencias` | Rutas y hashes de resultados consumidos |
| `trazabilidad` | Huella de configuración y fuentes |

### `resultado.json`

Contiene datos que otros módulos pueden consumir:

| Campo | Significado |
|---|---|
| `entrada_sha256` | Huella de la entrada usada |
| `dependencias_consumidas` | Resultados externos realmente utilizados |
| `estado` | Estado general del cálculo |
| `resultados` | Magnitudes y decisiones calculadas |
| `validaciones` | Comprobaciones internas |
| `advertencias` | Hipótesis, límites o revisiones pendientes |
| `archivos_generados` | Productos adicionales |
| `generado_en` | Fecha y hora de generación |

### `reporte.md`

Es la versión legible para revisión humana. Úsela para comprender el cálculo,
pero recuerde que la comunicación automática entre módulos se realiza con
`resultado.json`, no copiando valores desde el reporte.

### `manifiesto.json`

Es el índice de la ejecución. Registra el estado y las rutas de cada módulo, la
huella del código, la huella de configuración y la huella de cada resultado.

### `consolidado.json`

Resume todos los módulos y sus advertencias. Es un buen punto de inicio para una
revisión general, pero no sustituye la lectura de cada reporte.

## 13. Interpretación de estados

| Estado | Interpretación práctica |
|---|---|
| `OK` | El cálculo terminó y no registró advertencias generales |
| `ADVERTENCIA` | Terminó, pero existen hipótesis o verificaciones que deben revisarse |
| `NO_CUMPLE` | Alguna verificación estructural no satisface el criterio implementado |
| `ERROR` | El programa no pudo completar el cálculo |
| `OBSOLETO` | El resultado ya no es compatible con su entrada o dependencias |

`ADVERTENCIA` no significa automáticamente que el elemento falle, y `OK` no
equivale a aprobación profesional. Revise siempre:

1. equilibrio y coherencia física;
2. unidades y convención de signos;
3. orden de magnitud de fuerzas y deformaciones;
4. hipótesis del modelo;
5. validaciones y advertencias;
6. compatibilidad con geometría y detalles constructivos.

## 14. Crear una nueva revisión académica

Para estudiar una variante sin alterar `R00`:

1. Copie la carpeta de entrada a una revisión nueva, por ejemplo `R01`.
2. En el nuevo `entrada.yaml`, cambie `proyecto.revision` a `R01`.
3. Modifique sólo los parámetros justificados.
4. Actualice las fuentes y el estado de los datos.
5. Valide y ejecute usando `--revision R01`.

Ejemplo en PowerShell:

```powershell
New-Item `
  -ItemType Directory `
  -Path 'analisis_estabilidad/casos/molinohuayco/R01'
Copy-Item `
  -LiteralPath 'analisis_estabilidad/casos/molinohuayco/R00/entrada.yaml' `
  -Destination 'analisis_estabilidad/casos/molinohuayco/R01/entrada.yaml'
```

No copie las ejecuciones de `R00`: la nueva revisión debe producir su propia
trazabilidad.

## 15. Pruebas automáticas

Las pruebas comprueban formulaciones existentes, contratos, dependencias,
rechazo de rutas externas y prioridad de overrides.

```powershell
$env:UV_CACHE_DIR='.uv-cache'
$env:MPLCONFIGDIR='analisis_estabilidad/.tmp/mplconfig'
$env:PYTEST_ADDOPTS='-p no:cacheprovider'
uv run python -m pytest -q `
  --basetemp=analisis_estabilidad/.tmp/pytest-estudiante
```

Una prueba aprobada verifica que el código conserva el comportamiento esperado;
no demuestra por sí sola que todos los datos de entrada representen la obra
real.

## 16. Errores frecuentes

### «La configuración no es válida»

Posibles causas:

- una clave está mal escrita;
- la indentación YAML cambió;
- falta un campo obligatorio;
- un número fue escrito como texto;
- `proyecto.id` o `proyecto.revision` no coincide con la ruta usada.

Ejecute primero `validar` y lea el campo `error` completo.

### «La ruta debe permanecer dentro de analisis_estabilidad»

La entrada o salida apunta fuera del subsistema. Use una ruta dentro de
`analisis_estabilidad/casos/` o `analisis_estabilidad/.tmp/`.

### «Huella incorrecta»

Un resultado dependiente fue alterado después de preparar la entrada. No cambie
manualmente `resultado.json`. Genere nuevamente la entrada mediante el
orquestador.

### El sistema reutilizó una ejecución anterior

Es el comportamiento esperado cuando el código y la configuración tienen la
misma huella. Use `--nueva-ejecucion` si necesita repetir todo en otra carpeta.

### Aparece `ADVERTENCIA`

Abra primero `reporte.md` y luego revise `advertencias` y `validaciones` en
`resultado.json`. Determine si se trata de una hipótesis del modelo, un dato por
confirmar, una limitación constructiva o una comprobación cercana al límite.

### Un resultado parece físicamente extraño

Antes de modificar el código, revise:

1. unidades de entrada;
2. geometría y brazos de palanca;
3. dirección y signo de cargas;
4. combinaciones utilizadas;
5. apoyos e idealización;
6. equilibrio global y orden de magnitud.

## 17. Lista de control para entregar un trabajo

Antes de usar los resultados en una memoria o exposición:

- [ ] La configuración fue validada.
- [ ] Se identificó el caso y la revisión.
- [ ] Se documentó la fuente de geometría, cargas y suelo.
- [ ] Se revisaron unidades y signos.
- [ ] Se ejecutaron las pruebas automáticas.
- [ ] El manifiesto contiene todos los módulos requeridos.
- [ ] Se leyeron todas las advertencias.
- [ ] Se verificó equilibrio y orden de magnitud.
- [ ] Se revisó la compatibilidad entre elementos.
- [ ] Los resultados fueron contrastados con normativa y planos.
- [ ] El ingeniero responsable revisó las conclusiones para uso profesional.

## 18. Secuencia recomendada para aprender el sistema

1. Lea el YAML y ubique un parámetro conocido en los planos.
2. Ejecute solamente `estribo.estabilidad`.
3. Compare `entrada.json`, `resultado.json` y `reporte.md`.
4. Ejecute `zapata.longitudinal` y observe su dependencia del estribo.
5. Prepare, pero no ejecute, `contrafuertes.diseno` y siga la cadena de hashes.
6. Cree un override pequeño y compare la nueva entrada con la anterior.
7. Ejecute todo y revise el consolidado.
8. Finalmente, estudie las funciones Python del elemento que le interese.

Con esta secuencia se aprende primero el comportamiento físico y el flujo de
información; después se aborda la implementación numérica.

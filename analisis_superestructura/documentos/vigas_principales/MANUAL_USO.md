# Manual de uso — análisis y diseño de vigas principales

## 1. Propósito y alcance

Este paquete analiza, verifica y busca secciones para las vigas principales de un puente recto, simplemente apoyado, con vigas I de placas soldadas y tablero de concreto. Sigue la secuencia de Bartra, páginas impresas 113–165, actualizada con el Manual de Puentes MTC 2018.

Incluye:

- propiedades de la sección metálica y de las secciones compuestas de corto y largo plazo;
- cargas por etapas constructivas;
- carga móvil HL-93 y distribución transversal mediante expresiones aproximadas o parrilla espacial;
- verificaciones de flexión, corte, estabilidad durante la construcción, servicio, fatiga y deflexión;
- contraflecha teórica por cargas permanentes;
- búsqueda discreta y determinística de la sección factible de menor masa;
- resultados trazables en JSON, CSV, Markdown y gráficos.

No diseña conectores de corte, rigidizadores, diafragmas ni arriostramientos. Estos elementos se registran como validaciones externas.

## 2. Requisitos e instalación

Se requiere Python 3.10 o superior. El proyecto utiliza NumPy, Matplotlib, PyYAML y Pydantic 2. Las dependencias de desarrollo también incluyen pytest y SciPy.

Desde la raíz del repositorio, la instalación recomendada es:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv sync --extra dev
```

También puede emplearse otro entorno Python con las dependencias declaradas en `pyproject.toml`.

## 3. Inicio rápido

El paquete incluye estas configuraciones de referencia:

- `analisis_superestructura/casos/bartra/R00/entrada.yaml`: benchmark basado en la secuencia de Bartra, actualizado al MTC 2018.
- `analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/entrada.yaml`: caso preliminar del puente Molinohuayco.

Para ejecutar el análisis paso a paso sin terminal, abra
`notebooks/analisis_parrilla.ipynb` en JupyterLab, VS Code o cualquier entorno
compatible con notebooks y ejecute todas las celdas. La primera celda de
opciones permite seleccionar el YAML, la malla, los pasos de barrido, el
estudio de convergencia y la exportación.

Para validar, analizar y diseñar el benchmark de Bartra:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_superestructura.elementos.vigas_principales validate analisis_superestructura/casos/bartra/R00/entrada.yaml
uv run python -m analisis_superestructura.elementos.vigas_principales analyze analisis_superestructura/casos/bartra/R00/entrada.yaml
uv run python -m analisis_superestructura.elementos.vigas_principales design analisis_superestructura/casos/bartra/R00/entrada.yaml
```

Estos comandos escriben dentro de `casos/<caso>/<revision>/ejecuciones/`, junto
a la entrada. El comando modular equivalente, con control de ejecuciones y
consolidación, es:

```powershell
uv run python -m analisis_superestructura ejecutar vigas_principales.analisis --caso bartra --revision R00
uv run python -m analisis_superestructura ejecutar vigas_principales.diseno --caso bartra --revision R00
uv run python -m analisis_superestructura consolidar --caso bartra --revision R00
```

Para crear un caso, copie uno de los YAML de ejemplo y sustituya sus datos por la información confirmada del proyecto.

## 4. Flujo de trabajo

### 4.1 Validar

```text
python -m analisis_superestructura.elementos.vigas_principales validate caso.yaml
```

La validación revisa el esquema, las unidades, la geometría, la continuidad de los segmentos, las posiciones de arriostramiento y la edición normativa. No continúe hasta corregir los errores. Las advertencias permiten ejecutar el cálculo, pero deben revisarse en la memoria.

### 4.2 Analizar

```text
python -m analisis_superestructura.elementos.vigas_principales analyze caso.yaml
```

Este comando calcula las propiedades, cargas por etapas, factores de distribución, posiciones críticas de los vehículos, solicitaciones y deformaciones. Si el YAML está dentro de `casos/`, el resultado se escribe en su carpeta de ejecución. Para un YAML externo puede cambiarse la carpeta de resultados:

```text
python -m analisis_superestructura.elementos.vigas_principales analyze caso.yaml --output ruta/de/salida
```

### 4.3 Diseñar

```text
python -m analisis_superestructura.elementos.vigas_principales design caso.yaml
```

Si `busqueda.habilitada` es `false`, se verifica la sección declarada en `viga.segmentos`. Si es `true`, también se evalúan las dimensiones de `busqueda` y se selecciona la alternativa factible de menor masa.

Para un YAML externo a `casos/`, puede emplearse igualmente `--output ruta/de/salida`.

## 5. Configuración YAML

El YAML es la fuente única de verdad. El esquema no admite claves desconocidas: un campo mal escrito genera un error en vez de ser ignorado.

### 5.1 Identificación y normativa

```yaml
proyecto:
  id: puente_ejemplo
  nombre: Puente de ejemplo
  revision: R00
  responsable: Ingeniero responsable
  sistema_unidades: SI

normativa:
  manual: Manual de Puentes MTC
  edicion: 2018
  base_aashto: AASHTO LRFD 2014, 7.a edición, Interim 2015
```

`sistema_unidades` admite `SI` o `MKS`. La edición contractual implementada es MTC 2018.

### 5.2 Geometría

```yaml
geometria:
  luz: 50.0
  numero_vigas: 3
  separacion_vigas: 2.0
  ancho_calzada: 4.2
  ancho_veredas_total: 1.2
  ancho_tablero: 6.4
  voladizo_exterior: 1.2
  distancia_borde_calzada_viga_exterior: 0.1
  numero_carriles: 1
```

Las longitudes globales están en metros. `voladizo_exterior` se mide desde el eje de la viga exterior hasta el borde del tablero. La suma de la calzada y las veredas no debe exceder el ancho del tablero.

### 5.3 Losa y materiales

```yaml
losa:
  espesor: 0.22
  haunch: 0.05
  ancho_haunch: 0.45
  ancho_efectivo_interior: null
  ancho_efectivo_exterior: null
  factor_largo_plazo: 3.0

materiales:
  concreto:
    fc: 28.0
    ec: null
    peso_unitario: 24.0
  acero_estructural:
    fy: 345.0
    fu: 450.0
    es: 200000.0
    peso_unitario: 76.98
    grado: ASTM A709 Gr. 50
  acero_refuerzo:
    fy: 420.0
    es: 200000.0
```

Si `ec` es `null`, el programa lo calcula. Los anchos efectivos pueden proporcionarse o dejarse en `null` para calcularlos con los límites implementados. En SI, las resistencias y módulos están en MPa y los pesos unitarios en kN/m³.

### 5.4 Sección y segmentos

```yaml
viga:
  categoria_fatiga: C
  alma_rigidizada: false
  separacion_rigidizadores: null
  segmentos:
    - nombre: tramo_completo
      x_inicio: 0.0
      x_fin: 50.0
      altura_alma: 2400.0
      espesor_alma: 20.0
      ancho_ala_superior: 600.0
      espesor_ala_superior: 30.0
      ancho_ala_inferior: 800.0
      espesor_ala_inferior: 45.0
```

Las coordenadas longitudinales están en metros y todas las dimensiones de placa en milímetros. Los segmentos deben comenzar en cero, ser contiguos y terminar exactamente en la luz. Para una viga variable se agregan varios segmentos con dimensiones constantes en cada tramo.

Las categorías admitidas son `A`, `B`, `B_PRIMA`, `C`, `C_PRIMA`, `D`, `E` y `E_PRIMA`. La categoría debe representar el detalle real investigado.

### 5.5 Arriostramiento y construcción

```yaml
arriostramiento:
  posiciones: [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
  confirmado: false

construccion:
  apuntalada: false
  carga_construccion: 1.0
  incluir_losa_fresca: true
  incluir_peso_propio_viga: true
```

Las posiciones están en metros, ordenadas, e incluyen ambos apoyos. Definen las longitudes no arriostradas de la etapa no compuesta. La carga de construcción se ingresa como carga lineal por viga.

### 5.6 Cargas permanentes y peatonales

```yaml
cargas:
  dc_no_compuesta_adicional: 0.0
  dc_compuesta: {interior: 0.0, exterior: 0.0}
  dw: {interior: 3.0, exterior: 2.0}
  pl: {interior: 0.0, exterior: 3.6}
```

Son cargas lineales por viga:

- `dc_no_compuesta_adicional`: carga estructural anterior a la acción compuesta;
- `dc_compuesta`: carga estructural posterior a la acción compuesta;
- `dw`: superficie de rodadura, servicios y cargas permanentes no estructurales;
- `pl`: carga peatonal ya distribuida a la viga.

Cada acción puede ingresarse como un único valor, común a todas las vigas, o
como un objeto con valores `interior` y `exterior`. Esta segunda forma debe
usarse cuando veredas, barandas, carpeta de rodadura u otros elementos tengan
anchos tributarios diferentes.

El peso propio de la viga y el concreto fresco se obtienen de la geometría y los pesos unitarios cuando sus opciones están activadas. Cuando `haunch` y `ancho_haunch` están definidos, su peso se suma al concreto de la losa en la misma etapa constructiva.

### 5.7 Tráfico HL-93

```yaml
trafico:
  camion:
    eje_frontal: 35.0
    eje_posterior: 145.0
    separacion_frontal: 4.3
    separacion_posterior_min: 4.3
    separacion_posterior_max: 9.0
  tandem_eje: 110.0
  separacion_tandem: 1.2
  carga_carril: 9.3
  incremento_dinamico: 0.33
  incremento_dinamico_fatiga: 0.15
  adtt_carril: 1000.0
```

En SI, los ejes están en kN, las separaciones en metros y la carga de carril en kN/m. El incremento dinámico se aplica al camión o tándem, no a la carga de carril.

Pueden suministrarse factores obtenidos de un análisis transversal independiente:

```yaml
  factor_distribucion_momento_interior: null
  factor_distribucion_momento_exterior: null
  factor_distribucion_corte_interior: null
  factor_distribucion_corte_exterior: null
  factor_distribucion_fatiga_interior: null
  factor_distribucion_fatiga_exterior: null
```

Si se dejan en `null`, se calculan con las expresiones implementadas. El reporte advierte si la geometría queda fuera de sus límites de aplicación.

### 5.8 Parámetros de análisis

```yaml
analisis:
  numero_estaciones: 201
  paso_vehiculo: 0.10
  paso_separacion_ejes: 0.10
  metodo_distribucion: parrilla
  parrilla:
    numero_tramos_longitudinales: 20
    paso_posicion_transversal: 0.10
    paso_busqueda_longitudinal: 0.25
    ancho_carril_diseno: 3.00
    separacion_lineas_rueda: 1.80
    factor_presencia_multiple: 1.20
    coeficiente_poisson_concreto: 0.20
    coeficiente_poisson_acero: 0.30
    factor_rigidez_flexion_transversal: 1.0
    factor_rigidez_torsional: 1.0
    puntos_integracion_carga_carril: 5
  tolerancia_equilibrio: 1.0e-8
  limite_deflexion_divisor: 800.0
  reportar_mks: false
  factores:
    resistencia_dc: 1.25
    resistencia_dw: 1.50
    resistencia_ll: 1.75
    resistencia_pl: 1.75
    servicio_dc: 1.00
    servicio_dw: 1.00
    servicio_ll: 1.30
    servicio_pl: 1.00
    fatiga_i: 1.75
    fatiga_ii: 0.80
```

`metodo_distribucion` admite `aproximado` o `parrilla`. El segundo ensambla
una parrilla espacial con tres grados de libertad por nodo, rigidez compuesta
de corto plazo en las vigas longitudinales y franjas transversales de losa.
Desplaza el carril dentro de la calzada y obtiene las participaciones de cada
viga para momento, reacción/corte y fatiga. El factor de presencia múltiple se
aplica a momento y corte, pero no a fatiga.

`numero_estaciones` debe ser al menos 21. Un paso menor mejora la resolución de la posición crítica y aumenta el tiempo de cálculo. En la parrilla, aumente `numero_tramos_longitudinales` hasta que los factores converjan; el notebook automatiza esta comparación. Los factores son entradas trazables y deben revisarse para las combinaciones contractuales aplicables.

### 5.9 Búsqueda de secciones

```yaml
busqueda:
  habilitada: false
  peraltes_alma: [2200.0, 2400.0, 2600.0]
  espesores_alma: [16.0, 18.0, 20.0]
  anchos_ala_superior: [500.0, 600.0]
  espesores_ala_superior: [25.0, 30.0]
  anchos_ala_inferior: [650.0, 750.0, 850.0]
  espesores_ala_inferior: [35.0, 40.0, 45.0]
  grupos:
    - segmentos: [0]
  maximo_candidatos: 5000
  mejores_alternativas: 10
```

Las dimensiones están en milímetros. Los índices de `grupos.segmentos` comienzan en cero; los segmentos de un mismo grupo reciben la misma sección candidata.

La búsqueda genera candidatos de forma determinística, aplica filtros geométricos y constructivos, revisa primero la etapa no compuesta y después ejecuta las verificaciones completas. Las alternativas factibles se ordenan por masa, máximo DCR y número de cambios de sección. Si no existe una solución factible, se informan los candidatos más cercanos y sus incumplimientos.

`maximo_candidatos` limita el producto de combinaciones evaluadas. Para una exploración extensa, conviene ejecutar primero una malla gruesa y después refinar las listas alrededor de las mejores alternativas.

### 5.10 Validaciones externas y fuentes

```yaml
validaciones_externas:
  conectores_confirmados: false
  rigidizadores_confirmados: false
  arriostramiento_confirmado: false

fuentes:
  geometria: Planos del proyecto, revisión vigente
  materiales: Especificaciones técnicas del proyecto

estados_datos:
  geometria: confirmado
  cargas: asumido
  conectores: pendiente
```

Los estados admitidos son `confirmado`, `calculado`, `asumido` y `pendiente`. Una validación debe marcarse como confirmada solo cuando exista una comprobación externa compatible con las demandas del análisis.

## 6. Unidades

El cálculo interno utiliza N, mm y MPa. La entrada depende de `proyecto.sistema_unidades`:

| Magnitud | SI | MKS técnico |
|---|---:|---:|
| Geometría global | m | m |
| Dimensiones de placas | mm | mm |
| Fuerzas | kN | tf |
| Cargas lineales | kN/m | tf/m |
| Pesos unitarios | kN/m³ | tf/m³ |
| Esfuerzos y resistencias | MPa | kgf/cm² |

No mezcle sistemas dentro de un archivo. `analisis.reportar_mks: true` añade equivalencias MKS al reporte, pero no cambia las unidades de entrada.

## 7. Resultados

Cuando el YAML pertenece a un caso (`casos/<caso>/<revision>/entrada.yaml`), los
resultados se guardan dentro de la carpeta del caso, junto a la entrada:

```text
casos/<caso>/<revision>/ejecuciones/<id>/elementos/vigas_principales/<calculo>/
├── entrada.json
├── resultado.json
├── reporte.md
├── envolventes.csv
└── figuras/*.png
```

El comando modular es la vía recomendada:

```text
uv run python -m analisis_superestructura ejecutar vigas_principales.diseno --caso <caso> --revision <revision>
uv run python -m analisis_superestructura consolidar --caso <caso> --revision <revision>
```

El comando histórico `analyze`/`design` sobre un YAML de caso escribe en la misma
carpeta de ejecución. Si el YAML está fuera de `casos/`, se conserva la salida
histórica en `outputs/vigas_principales/<proyecto.id>/<proyecto.revision>/`.

Archivos del análisis:

- `analisis.json`: entradas normalizadas, propiedades, cargas, factores y resultados intermedios;
- `envolventes.csv`: acciones, envolventes móviles y combinaciones por estación;
- `diagramas_acciones_permanentes.png`: diagramas separados de $DC_{nc}$, $DC_{comp}$, $DW$ y $PL$;
- `envolvente_carga_movil_LL_IM.png`: envolventes sin combinar de $LL+IM$;
- `combinacion_resistencia_i.png`: $M_u$, $V_{u,max}$ y $V_{u,min}$ para Resistencia I;
- `combinacion_servicio_ii.png`: solicitaciones combinadas de Servicio II;
- `envolvente_fatiga.png`: rango de momento del camión de fatiga;
- `envolventes.png`: alias compatible de `combinacion_resistencia_i.png`.

Archivos del diseño:

- `diseno.json`: demandas, capacidades, DCR y verificación gobernante;
- `memoria.md`: memoria automática del caso;
- `dcr.png`: resumen gráfico de utilizaciones.

Con búsqueda habilitada se agregan:

- `busqueda.json`: clasificación de candidatos y causas de descarte;
- `diseno_optimo.json`: detalle de la alternativa factible de menor masa;
- `memoria_optima.md`: memoria de la alternativa seleccionada.

Los resultados incluyen revisión y hash de configuración. Si cambia el YAML, cambia el hash de la corrida.

## 8. Interpretación

La utilización se expresa como `DCR = demanda / capacidad`:

- `DCR <= 1.0`: satisface el límite implementado;
- `DCR > 1.0`: no satisface el límite.

Estados principales:

- `CUMPLE`: pasan las verificaciones implementadas y están confirmadas las validaciones externas críticas;
- `CONDICIONAL`: pasan las verificaciones numéricas de la viga, pero quedan validaciones externas críticas pendientes;
- `NO_CUMPLE`: falla una o más verificaciones;
- `VALIDA`: la entrada pasó el esquema;
- `ANALIZADO`: terminó el análisis, sin implicar por sí mismo cumplimiento.

Revise siempre la verificación gobernante, su DCR, la estación crítica, las advertencias de distribución, la etapa no compuesta, la categoría de fatiga, las deflexiones, la contraflecha y las validaciones externas pendientes.

## 9. API de Python

```python
from analisis_superestructura.elementos.vigas_principales import (
    analizar,
    analizar_distribucion_parrilla,
    buscar_secciones,
    validar_configuracion,
    verificar,
)

configuracion = validar_configuracion("caso.yaml")
resultado_parrilla = analizar_distribucion_parrilla(configuracion)
resultado_analisis = analizar(configuracion)
resultado_diseno = verificar(configuracion, resultado_analisis)

if configuracion.busqueda.habilitada:
    resultado_busqueda = buscar_secciones(configuracion)
```

No modifique manualmente resultados intermedios antes de verificar: hacerlo rompe la trazabilidad entre entrada, cálculo y memoria.

## 10. Problemas frecuentes

### Campo desconocido

Revise la ortografía y ubicación de la clave. El esquema rechaza campos no definidos.

### Los segmentos no cubren la luz

Verifique que el primer `x_inicio` sea cero, cada `x_fin` coincida con el siguiente `x_inicio` y el último `x_fin` sea igual a `geometria.luz`.

### Arriostramientos inválidos

Ordene las posiciones, elimine duplicados e incluya cero y la luz total.

### Advertencia de distribución transversal

La geometría puede quedar fuera del dominio de las expresiones aproximadas.
Seleccione `metodo_distribucion: parrilla` para obtener factores refinados y
revise el equilibrio, la convergencia de malla y las hipótesis de rigidez. Los
factores ingresados explícitamente en `trafico` conservan prioridad sobre los
calculados.

### Resultado `CONDICIONAL`

Revise `validaciones_externas`. No confirme conectores, rigidizadores o arriostramiento sin su diseño y documentación independiente.

### No hay alternativas factibles

Consulte `busqueda.json`, identifique las restricciones gobernantes y amplíe justificadamente las dimensiones o modifique el esquema. Nunca adopte como óptimo un candidato no factible.

### Búsqueda lenta

Reduzca los valores de las listas, disminuya `maximo_candidatos` o realice una búsqueda gruesa seguida por otra refinada.

## 11. Pruebas

Para verificar la instalación:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run --extra dev python -m pytest -q
```

Las pruebas cubren secciones, unidades, líneas de influencia, HL-93, distribución aproximada y por parrilla, equilibrio, simetría, combinaciones, verificaciones resistentes, deflexiones, vigas segmentadas y determinismo de la búsqueda.

## 12. Limitaciones y responsabilidad

La versión actual se limita a vigas I rectas y simplemente apoyadas. No cubre puentes continuos, curvos o esviados ni reemplaza un modelo global cuando el comportamiento lo requiera.

- La parrilla desplaza actualmente un carril cargado. Para puentes de varios carriles debe ampliarse la generación de combinaciones transversales y sus factores de presencia múltiple.
- Los diafragmas no tienen rigidez de sección explícita mientras sus propiedades no estén confirmadas; la continuidad transversal proviene de las franjas de losa.
- La rigidez longitudinal compuesta presupone interacción total acero–concreto y debe conciliarse con el diseño de conectores.

- La estabilidad lateral de construcción usa una comprobación elástica conservadora con `Cb = 1`; no sustituye un análisis detallado de montaje.
- La resistencia al corte no incluye acción de campo de tensión.
- La fatiga depende de la categoría suministrada, que debe representar el detalle construido.
- Conectores, rigidizadores, diafragmas y arriostramientos se diseñan externamente.
- El caso Molinohuayco es preliminar mientras se concilien las inconsistencias de sus fuentes.

Los resultados son una ayuda de cálculo y requieren revisión, juicio y aprobación del ingeniero estructural responsable.

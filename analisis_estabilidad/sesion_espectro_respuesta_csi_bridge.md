# Sesion de Clase: Espectro de Respuesta Sismica para CSI Bridge
## Puente Molinohuaico / Molinohuaycco - MTC 2018 / AASHTO LRFD

---

## 1. Objetivos de la sesion

Al finalizar esta sesion, el participante sera capaz de:

1. **Identificar** los parametros sismicos de sitio necesarios para construir un
   espectro de respuesta segun el Manual de Puentes MTC 2018.
2. **Calcular** las ordenadas espectrales `As`, `SDS`, `SD1` y los periodos
   caracteristicos `To`, `Ts` a partir de datos de un estudio de suelos.
3. **Construir** la funcion de espectro de respuesta elastico (3 ramas) y el
   espectro reducido con factor `R`.
4. **Implementar** el espectro en CSI Bridge como funcion definida por el usuario
   (User Defined Response Spectrum Function).
5. **Verificar** que el espectro generado coincida con los puntos de control de
   la Figura 17 del estudio de suelos.
6. **Discernir** entre espectro elastico (para demanda) y espectro reducido
   (para fuerzas de diseno), y entender cuando usar cada uno.

---

## 2. Marco teorico

### 2.1 El metodo de los 3 puntos (AASHTO LRFD / MTC 2018)

El Manual de Puentes MTC 2018, en su Art. 2.4.3.11.2.1, adopta el procedimiento
espectral de AASHTO LRFD para definir la accion sismica de diseno. La demanda
sismica se caracteriza mediante **tres ordenadas espectrales** obtenidas de mapas
de isoaceleraciones para el territorio peruano, correspondientes a un sitio de
referencia tipo roca (Clase B, segun la clasificacion NEHRP/AASHTO):

| Ordenada | Descripcion | Periodo de referencia |
|:---------|:------------|:---------------------|
| `PGA` | Aceleracion pico del terreno | `T = 0.0 s` |
| `Ss` | Aceleracion espectral para periodo corto | `T = 0.2 s` |
| `S1` | Aceleracion espectral para periodo largo (1 s) | `T = 1.0 s` |

Estos valores se corrigen mediante **factores de sitio** que dependen de la
clasificacion del suelo (Clase A, B, C, D, E o F segun `Vs30`, `N-SPT` o `Su`):

| Factor | Aplica a | Expresion |
|:-------|:---------|:----------|
| `Fpga` | PGA | Corrige la aceleracion pico |
| `Fa` | Ss | Corrige la aceleracion de periodo corto |
| `Fv` | S1 | Corrige la aceleracion de periodo largo |

Los coeficientes espectrales ajustados por sitio son:

> **Ecuacion 1:** Coeficiente de aceleracion en periodo cero
> $$A_s = F_{pga} \cdot PGA$$

> **Ecuacion 2:** Coeficiente de aceleracion espectral de periodo corto (meseta)
> $$S_{DS} = F_a \cdot S_s$$

> **Ecuacion 3:** Coeficiente de aceleracion espectral de periodo largo
> (rampa descendente)
> $$S_{D1} = F_v \cdot S_1$$

### 2.2 Forma espectral completa

Con estos tres coeficientes, el espectro de coeficiente sismico elastico
`Csm(T)` se define por tramos. La Figura 1 muestra la forma general:

![Figura 1: Forma conceptual del espectro de respuesta MTC 2018 / AASHTO LRFD](../imagenes/figura_espectro_conceptual.png)

Los periodos caracteristicos se calculan como:

> **Ecuacion 4:** Periodo de transicion al inicio de la meseta
> $$T_o = 0.20 \cdot T_s$$

> **Ecuacion 5:** Periodo de transicion al final de la meseta
> $$T_s = \frac{S_{D1}}{S_{DS}}$$

Con estos valores, el espectro se define analiticamente asi:

| Tramo | Rango de `T` | Ecuacion `Csm(T)` |
|:------|:-------------|:------------------|
| 1 | `T = 0` | `Csm = As` |
| 2 | `0 < T < To` | `Csm = As + (SDS - As)(T / To)` |
| 3 | `To <= T <= Ts` | `Csm = SDS` |
| 4 | `T > Ts` | `Csm = SD1 / T` |

### 2.3 Espectro reducido vs. espectro elastico

En CSI Bridge se pueden usar dos tipos de espectro:

| Tipo | Definicion | Uso |
|:-----|:-----------|:----|
| **Espectro elastico** | `Csm(T)` sin dividir entre `R` | Para obtener fuerzas demandadas en elementos no-lineales o para analisis de demanda/capacidad (pushover). |
| **Espectro reducido** | `Csm_diseno(T) = Csm(T) / R` | Para diseno por fuerzas (analisis lineal elastico con factor de reduccion). |

El factor `R` (factor de modificacion de respuesta) depende del tipo de elemento
estructural (Art. 2.4.3.11.2.1.4 del MTC 2018):

| Tipo estructural | R |
|:-----------------|:--|
| Pilares tipo placa | 1.50 |
| Pilares tipo columna | 2.00 - 3.00 |
| Estribos | 1.50 - 2.00 (segun categoria) |
| Elementos de fundacion | 1.00 |

> **Importante para CSI Bridge:** Cuando se define el espectro reducido (de
> diseno) como funcion de usuario, la aceleracion espectral de entrada YA debe
> estar dividida entre `R`. No se debe aplicar un factor de escala adicional
> `1/R` en el caso de carga.

---

## 3. Datos de partida - Puente Molinohuaico

### 3.1 Parametros de sitio (del estudio de suelos)

Los siguientes datos provienen del estudio de suelos anterior
(`estudio_suelos_anterior.pdf`, Cuadros 6 a 8):

| Simbolo | Descripcion | Valor | Unidad | Fuente |
|:--------|:------------|------:|:-------|:-------|
| `PGA` | Aceleracion pico del terreno (sitio B) | 0.360 | g | Cuadro 7 |
| `Ss` | Aceleracion espectral T=0.2s (sitio B) | 0.900 | g | Cuadro 7 |
| `S1` | Aceleracion espectral T=1.0s (sitio B) | 0.226 | g | Cuadro 7 |
| `Fpga` | Factor de sitio para PGA | 1.040 | - | Cuadro 6 |
| `Fa` | Factor de sitio para periodo corto | 1.040 | - | Cuadro 6 |
| `Fv` | Factor de sitio para periodo largo | 1.550 | - | Cuadro 6 |
| Clase de sitio | Suelo muy denso y roca blanda | C | - | Cuadro 6 |
| `Vs30` promedio | Velocidad de onda de corte promedio | 373.05 | m/s | Promedio MASW |
| `R` | Factor de modificacion de respuesta (preliminar) | 3.00 | - | Figura 17 |

### 3.2 Coeficientes espectrales derivados

Aplicando las Ecuaciones 1 a 3:

| Simbolo | Operacion | Resultado | Unidad |
|:--------|:----------|----------:|:-------|
| `As` | `1.04 x 0.360` | **0.3744** | g |
| `SDS` | `1.04 x 0.900` | **0.9360** | g |
| `SD1` | `1.55 x 0.226` | **0.3503** | g |

### 3.3 Periodos caracteristicos

Aplicando Ecuaciones 4 y 5:

| Simbolo | Operacion | Resultado | Unidad |
|:--------|:----------|----------:|:-------|
| `Ts` | `0.3503 / 0.9360` | **0.3743** | s |
| `To` | `0.20 x 0.3743` | **0.0749** | s |

---

## 4. Calculo paso a paso del espectro de respuesta

### 4.1 Espectro elastico (Csm)

Construimos el espectro evaluando `Csm(T)` para un conjunto representativo
de periodos.

**Rama 1: Periodo cero**

```
T = 0.000 s
Csm(0) = As = 0.3744
```

**Rama 2: Ascenso lineal (0 < T < To)**

```
T = 0.020 s
Csm = As + (SDS - As) x (T / To)
    = 0.3744 + (0.9360 - 0.3744) x (0.020 / 0.0749)
    = 0.3744 + 0.5616 x 0.2670
    = 0.3744 + 0.1499
    = 0.5244
```

Verificacion adicional en `T = 0.050 s` (punto de la Figura 17 del estudio):

```
Csm(0.050) = 0.3744 + 0.5616 x (0.050 / 0.0749)
           = 0.3744 + 0.5616 x 0.6676
           = 0.3744 + 0.3749
           = 0.7494  (Coincide con 0.7495 de Figura 17 - diferencia 0.0001)
```

**Rama 3: Meseta (To <= T <= Ts)**

Periodos dentro de la meseta (0.0749 s a 0.3743 s):

```
T = 0.100 s  -> Csm = SDS = 0.9360
T = 0.200 s  -> Csm = 0.9360
T = 0.300 s  -> Csm = 0.9360
T = 0.3743 s -> Csm = 0.9360 (fin de la meseta = Ts)
```

**Rama 4: Descenso hiperbolico (T > Ts)**

```
T = 0.400 s  -> Csm = 0.3503 / 0.400 = 0.8758
T = 0.500 s  -> Csm = 0.3503 / 0.500 = 0.7006
T = 0.700 s  -> Csm = 0.3503 / 0.700 = 0.5004
T = 1.000 s  -> Csm = 0.3503 / 1.000 = 0.3503
T = 2.000 s  -> Csm = 0.3503 / 2.000 = 0.1752
T = 3.000 s  -> Csm = 0.3503 / 3.000 = 0.1168
```

### 4.2 Espectro reducido para diseno (Csm_d)

Dividimos cada ordenada entre `R = 3.0`:

| T (s) | Tramo | Csm elastico | Csm_d = Csm / 3.0 |
|------:|:------|-------------:|------------------:|
| 0.000 | Inicio | 0.3744 | 0.1248 |
| 0.020 | Ascenso | 0.5244 | 0.1748 |
| 0.050 | Ascenso | 0.7494 | 0.2498 |
| 0.0749 | Fin ascenso (To) | 0.9360 | 0.3120 |
| 0.100 | Meseta | 0.9360 | 0.3120 |
| 0.200 | Meseta | 0.9360 | 0.3120 |
| 0.300 | Meseta | 0.9360 | 0.3120 |
| 0.3743 | Fin meseta (Ts) | 0.9360 | 0.3120 |
| 0.400 | Descenso | 0.8758 | 0.2919 |
| 0.500 | Descenso | 0.7006 | 0.2335 |
| 0.700 | Descenso | 0.5004 | 0.1668 |
| 1.000 | Descenso | 0.3503 | 0.1168 |
| 1.500 | Descenso | 0.2335 | 0.0778 |
| 2.000 | Descenso | 0.1752 | 0.0584 |
| 3.000 | Descenso | 0.1168 | 0.0389 |
| 4.000 | Descenso | 0.0876 | 0.0292 |
| 5.000 | Descenso | 0.0701 | 0.0234 |

### 4.3 Puntos de control (verificacion con el estudio)

La Figura 17 del estudio de suelos presenta una tabla con valores de `Csm` para
varios periodos. Comprobemos que nuestro calculo reproduce esos valores:

| T (s) | Csm Figura 17 | Csm calculado | Diferencia | Verificacion |
|------:|--------------:|--------------:|-----------:|:------------|
| 0.000 | 0.3744 | 0.3744 | 0.0000 | PASA |
| 0.050 | 0.7495 | 0.7494 | 0.0001 | PASA |
| 0.100 | 0.9360 | 0.9360 | 0.0000 | PASA |
| 0.350 | 0.9360 | 0.9360 | 0.0000 | PASA |
| 0.400 | 0.8758 | 0.8758 | 0.0000 | PASA |
| 1.000 | 0.3503 | 0.3503 | 0.0000 | PASA |
| 3.000 | 0.1168 | 0.1168 | 0.0000 | PASA |

Todas las diferencias son inferiores a 0.001. **Espectro elastico verificado
contra el estudio de suelos.**

---

## 5. Script Python generador del espectro

Se ha preparado el script `generar_espectro_csi_bridge.py` en el directorio
`analisis_estabilidad/` que:

1. Define los parametros sismicos de entrada.
2. Calcula el espectro elastico `Csm(T)` punto a punto.
3. Calcula el espectro reducido `Csm_d(T) = Csm(T)/R`.
4. Genera una **tabla Markdown** con los valores.
5. Genera un **archivo CSV** de importacion para CSI Bridge con el formato:
   `Period, Accel` (columnas separadas por coma, punto decimal con punto).
6. Opcionalmente, genera un **grafico PNG** del espectro.
7. Verifica los puntos de control contra la Figura 17 del estudio.

### 5.1 Estructura del script

```
generar_espectro_csi_bridge.py
+-- Datos de entrada (INPUTS)
|   +-- PGA, Ss, S1
|   +-- Fpga, Fa, Fv
|   +-- R
+-- Funciones de calculo
|   +-- calc_spectrum_params()  -> As, SDS, SD1, To, Ts
|   +-- csm_elastic(T)         -> Csm elastico
|   +-- csm_design(T, R)       -> Csm reducido
|   +-- generate_spectrum()    -> Tabla completa
+-- Salidas
|   +-- Tabla Markdown
|   +-- archivo CSV (CSI Bridge)
|   +-- archivo TXT (pares T, Csm)
|   +-- grafico PNG (opcional)
+-- Verificacion
    +-- Puntos de control Vs. Figura 17
```

### 5.2 Corrida del script

El script se ejecuta desde la terminal:

```bash
python analisis_estabilidad/generar_espectro_csi_bridge.py
```

o con opciones:

```bash
# Guardar tabla Markdown
python analisis_estabilidad/generar_espectro_csi_bridge.py --markdown

# Guardar CSV para CSI Bridge
python analisis_estabilidad/generar_espectro_csi_bridge.py --csv

# Guardar grafico PNG
python analisis_estabilidad/generar_espectro_csi_bridge.py --plot

# Todo
python analisis_estabilidad/generar_espectro_csi_bridge.py --all
```

### 5.3 Salida del script (ejemplo de consola)

```
=================================================================
  ESPECTRO DE RESPUESTA SISMICA - PUENTE MOLINOHUAICO
  MTC 2018 / AASHTO LRFD - Metodo de 3 puntos
=================================================================

  As  = Fpga x PGA = 0.3744 g
  SDS = Fa x Ss    = 0.9360 g
  SD1 = Fv x S1    = 0.3503 g
  Ts  = SD1/SDS    = 0.3743 s
  To  = 0.20 x Ts  = 0.0749 s
  R   = 3.00

-----------------------------------------------------------------
   T(s)        Tramo   Csm_elast  Csm_diseno
-----------------------------------------------------------------
  0.0000       Inicio     0.3744      0.1248
  0.0050      Ascenso     0.4120      0.1373
  0.0100      Ascenso     0.4495      0.1498
  0.0200      Ascenso     0.5244      0.1748
  0.0500      Ascenso     0.7494      0.2498
  0.0749  Ascenso(To)     0.9360      0.3120
  0.1000       Meseta     0.9360      0.3120
  0.2000       Meseta     0.9360      0.3120
  0.3000       Meseta     0.9360      0.3120
  0.3743   Meseta(Ts)     0.9360      0.3120
  0.4000     Descenso     0.8758      0.2919
  0.5000     Descenso     0.7006      0.2335
  0.7000     Descenso     0.5004      0.1668
  1.0000     Descenso     0.3503      0.1168
  2.0000     Descenso     0.1752      0.0584
  3.0000     Descenso     0.1168      0.0389
  5.0000     Descenso     0.0701      0.0234
-----------------------------------------------------------------
```

---

## 6. Implementacion en CSI Bridge

### 6.1 Tipo de funcion espectral

CSI Bridge acepta funciones de espectro de respuesta definidas por el usuario.
El flujo de trabajo es:

```
Define > Functions > Response Spectrum > Add New Function > Choose "User"
```

Alli se especifica:

| Parametro | Valor | Comentario |
|:-----------|:------|:-----------|
| Function Name | `Espectro_MTC_Puente_Molinohuaico` | Nombre descriptivo |
| Function Damping Ratio | `0.05` | Amortiguamiento del 5% (valor por defecto AASHTO) |
| Period / Accel pairs | Ver tabla CSV | Pares (T, Csm_d) del espectro reducido |

### 6.2 Espectro elastico vs. reducido en CSI Bridge

Esta es una decision conceptual importante:

**Opcion A: Espectro reducido (RECOMENDADO para diseno lineal)**

```
Period(s)   Accel(g)    (Ya dividido entre R)
0.000       0.1248
0.020       0.1748
0.050       0.2498
0.075       0.3120
0.100       0.3120
0.200       0.3120
0.374       0.3120
0.400       0.2919
0.500       0.2335
...
```

Pasos en CSI Bridge:
1. Definir la funcion con los valores de `Csm_d` (reducidos).
2. En el caso de carga sismica, usar `Scale Factor = 1.0` (la reduccion ya esta
   incorporada en la funcion).
3. No multiplicar adicionalmente por `g` si el espectro ya esta en unidades de `g`.

**Opcion B: Espectro elastico + factor R en el caso de carga**

```
Period(s)   Accel(g)    (Elastico, sin dividir)
0.000       0.3744
0.020       0.5244
0.050       0.7494
0.075       0.9360
...
```

Pasos en CSI Bridge:
1. Definir la funcion con los valores elasticos.
2. En el caso de carga sismica, usar `Scale Factor = 1/R = 1/3.0`.
3. Esto equivale matematicamente a la Opcion A, pero conceptualmente es menos
   directo.

> **Recomendacion profesional:** Usar la **Opcion A** (espectro reducido en la
> funcion, scale factor = 1.0). Esto hace que el modelo sea mas facil de auditar,
> pues los valores de la funcion coinciden directamente con las fuerzas de diseno
> esperadas. Ademas, evita confusiones cuando se combinan varios casos de carga
> con factores de escala diferentes.

### 6.3 Direcciones de aplicacion del sismo

En CSI Bridge, para un modelo de subestructura de puente, se deben definir
casos de carga sismica en las direcciones relevantes:

| Direccion | Componente | Funcion a usar | Escala |
|:----------|:-----------|:---------------|:-------|
| Longitudinal (eje X del puente) | 100% espectro | `Espectro_MTC_*` | 1.0 |
| Transversal (eje Y del puente) | 100% espectro | `Espectro_MTC_*` | 1.0 |
| Vertical (eje Z) | 0% o 30% del espectro, segun MTC | `Espectro_MTC_*` | 0.3 (tipico) |

Para la combinacion direccional, AASHTO LRFD (Art. 3.10.8) y MTC 2018
recomiendan:

- Caso 1: `100% longitudinal + 30% transversal`
- Caso 2: `30% longitudinal + 100% transversal`

CSI Bridge permite aplicar estas combinaciones mediante factores de escala en
los casos de carga sismica o mediante envelopes.

### 6.4 Combinacion modal

Para el analisis espectral, CSI Bridge ofrece varios metodos de combinacion
modal. Se recomienda:

| Parametro | Valor recomendado | Fundamento |
|:----------|:-----------------|:-----------|
| Metodo de combinacion modal | CQC (Complete Quadratic Combination) | AASHTO LRFD Art. 4.7.4.3.1 |
| Amortiguamiento | 5% | Valor por defecto para puentes de concreto |
| Numero de modos | Suficientes para capturar >= 90% de masa participante | MTC 2018 Art. 2.4.3.11.2.3 |
| Combinacion direccional | SRSS o 30%+100% | AASHTO LRFD Art. 3.10.8 |

---

## 7. Verificacion de consistencia

### 7.1 Verificacion rapida (regla del pulgar)

Para una verificacion rapida del espectro generado, recordar que:

1. **En T=0**: El espectro INICIA en `As`, NO en `PGA`. Para este proyecto:
   - `PGA = 0.360` pero `As = 0.3744` (mayor que PGA por efecto de Fpga)
   - Esto refleja que el suelo amplifica las altas frecuencias

2. **En la meseta**: `SDS = 0.9360` es aproximadamente **2.6 veces PGA**.
   Esta amplificacion es tipica para Clase C con periodos cortos.

3. **En T=1.0s**: El valor debe ser exactamente `SD1 = 0.3503`, que es el
   coeficiente de periodo largo ajustado por sitio.

4. **El espectro reducido** con R=3.0 tiene una meseta en `0.3120 g`,
   que es un valor razonable para diseo de subestructura en Zona 3.

### 7.2 Verificacion con el estudio de suelos

Los valores calculados deben coincidir con los Cuadros 8 y 9 del estudio:

| Cuadro | Parametro | Valor estudio | Valor calculado | Diferencia |
|:-------|:----------|:-------------:|:---------------:|:----------:|
| Cuadro 8 | As | 0.3744 | 0.3744 | 0.0000 |
| Cuadro 8 | SDS | 0.9360 | 0.9360 | 0.0000 |
| Cuadro 8 | SD1 | 0.3503 | 0.3503 | 0.0000 |
| Cuadro 9 | Zona sismica | 3 | 3 | - |

### 7.3 Verificacion con codigo Python

Ejecutar:

```bash
python analisis_estabilidad/generar_espectro_csi_bridge.py
```

Revisar que la seccion de verificacion indique que todos los puntos de control
`PASAN` la verificacion.

---

## 8. Ejercicios propuestos

### Ejercicio 1: Variacion del factor R

Suponga que se decide cambiar el factor de modificacion de respuesta a `R = 1.50`
(sin embargo para estribos tipo placa, segun MTC 2018). Recalcule el espectro
reducido para este nuevo R.

**Solucion:** Ejecutar el script con R modificado en `SeismicInput.R = 1.50`.

### Ejercicio 2: Clase de sitio D

Si se adoptara una clasificacion conservadora de sitio D (para la zona del
MASW-02 con Vs30 = 287.4 m/s), los factores serian (segun MTC 2018 Art.
2.4.3.11.2.1.2):

- Fpga = 1.29
- Fa = 1.29
- Fv = 1.97

Recalcule el espectro comparandolo con el de Clase C.

### Ejercicio 3: Verificacion con espectro de la norma E.030

Compare el espectro de diseno MTC 2018 / AASHTO LRFD desarrollado en esta
sesion con el espectro de la Norma E.030 (Z=0.25, S2, S=1.20, Tp=0.60, TL=2.00).
Identifique las diferencias conceptuales entre ambos enfoques.

### Ejercicio 4: Torsion accidental en CSI Bridge

Investigue como CSI Bridge aplica la torsion accidental en puentes (desplazamiento
del centro de masa en +-5% de la dimension transversal) y como se combina con el
analisis espectral.

---

## 9. Resumen y conclusiones

1. Los parametros sismicos del Puente Molinohuaico (Clase C, Zona 3) producen un
   espectro elastico con meseta `SDS = 0.9360 g` y periodo de transicion
   `Ts = 0.3743 s`.

2. El espectro reducido (diseno) con `R = 3.0` tiene una meseta de `0.3120 g`.
   Este valor se usa en el analisis lineal elastico de subestructura.

3. Se ha verificado que el espectro calculado coincide exactamente con los puntos
   de control de la Figura 17 del estudio de suelos.

4. CSI Bridge permite la importacion directa del espectro mediante archivo CSV
   con pares (Period, Accel).

5. Se recomienda usar el espectro reducido como funcion de usuario y factor de
   escala unitario en el caso de carga sismica.

6. Queda pendiente la confirmacion definitiva del factor `R` segun el tipo
   resistente de la subestructura y la categoria del puente.

---

## 10. Referencias

1. **Manual de Puentes MTC 2018**, Art. 2.4.3.11.2.1 (Procedimiento espectral),
   Art. 2.4.3.11.2.1.2 (Factores de sitio), Art. 2.4.3.11.2.1.4 (Factor de
   modificacion de respuesta R).

2. **Estudio de Suelos Anterior** (`estudio_suelos_anterior.pdf`), Cuadros 6 a 9
   y Figura 17.

3. **AASHTO LRFD Bridge Design Specifications**, 5th Edition, Seccion 3.10.

4. **CSI Bridge Manual**, Response Spectrum Analysis, User Defined Functions.

5. **parametros_sismicos_mtc_2018.md** - Documento base de parametros sismicos
   del proyecto.

---

*Documento preparado como sesion de clase para el analisis de subestructura del
Puente Molinohuaico / Molinohuaycco.*

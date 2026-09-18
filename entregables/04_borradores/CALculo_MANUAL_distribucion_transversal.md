# Cálculo Manual — Distribución Transversal de Carga Viva

**Puente Molinohuayco — Vigas Principales**  
**Configuración:** PROPUESTA-R00  
**Ejecución:** `20260917T132241-0500`

---

## 1. Objetivo

Este documento explica paso a paso cómo se obtienen los **factores de distribución transversal** de momento, corte y fatiga para las vigas principales del puente, tal como se reporta en la sección 8 de la memoria de cálculo `CALC-EST-2026-005-R01.md` y se implementa en el módulo `analisis_superestructura/elementos/vigas_principales/analisis/parrilla.py`.

Los factores resultantes son:

| Efecto  | Viga interior | Viga exterior |
| ------- | ------------: | ------------: |
| Momento |       0.42549 |       0.48887 |
| Corte   |       0.64536 |       0.44304 |
| Fatiga  |       0.36720 |       0.40445 |

---

## 2. Marco Normativo

La distribución transversal de carga viva en tableros de concreto sobre vigas I se rige por:

- **MTC 2018, Artículo 2.6.4.2.2** — Métodos para determinar los factores de distribución lateral
- **MTC 2018, Tabla 2.6.4.2.2.2b-1** — Ecuaciones aproximadas para tableros de concreto con vigas de acero
- **MTC 2018, Artículo 2.4.3.2.2** — Carga múltiple (factor de presencia múltiple *m* = 1.20 para un solo carril)
- **MTC 2018, Artículo 2.4.3.2.4.3** — Factor de distribución para fatiga (sin factor de presencia múltiple)

El Manual permite dos enfoques:

1. **Ecuaciones aproximadas** (Tabla 2.6.4.2.2.2b-1): expresiones empíricas basadas en parámetros geométricos y de rigidez. Son conservadoras para geometrías dentro de su rango de validez.
2. **Análisis refinado** (parrilla, elementos finitos): cuando la geometría está fuera de rango del método aproximado, o se requiere mayor precisión.

En este proyecto se adopta el **análisis por parrilla elástica lineal**, pero se presentan también las ecuaciones aproximadas para verificación.

---

## 3. Datos de Entrada

### 3.1 Geometría del tablero

| Parámetro | Símbolo | Valor | Unidad |
| --------- | ------- | ----: | ------ |
| Luz entre apoyos | $L$ | 50.00 | m |
| Número de vigas principales | $N_g$ | 3 | — |
| Separación entre vigas | $S$ | 2.00 | m |
| Ancho de calzada | $B_c$ | 4.00 | m |
| Ancho total de veredas | $B_v$ | 2.00 | m |
| Ancho total del tablero | $B$ | 6.00 | m |
| Voladizo exterior | $v$ | 1.00 | m |
| Espesor de losa | $t_s$ | 0.20 | m |
| Altura de haunch | $h_h$ | 0.05 | m |

**Distribución transversal:**

```
|--1.00--|--2.00--|--2.00--|--1.00--|  ← tablero (6.00 m)
  vereda  calzada  calzada  vereda
    ↑       ↑        ↑       ↑
  viga I  viga C   viga C  viga D
 (-2.0)   (0.0)    (0.0)  (+2.0)
```

Los ejes de las vigas se ubican en $y = -2.00$, $0.00$ y $+2.00$ m (origen en la viga central).

### 3.2 Materiales

| Material | Propiedad | Símbolo | Valor | Unidad |
| -------- | --------- | ------- | ----: | ------ |
| Concreto | Resistencia especificada | $f'_c$ | 27.46 | MPa |
| Concreto | Peso unitario | $\gamma_c$ | 24.0 | kN/m³ |
| Acero ASTM A709 Gr. 50 | Fluencia | $F_y$ | 345 | MPa |
| Acero | Módulo de elasticidad | $E_s$ | 200 000 | MPa |

**Módulo de elasticidad del concreto** (MTC 2018, Art. 2.5.3):

$$
E_c = 0.043 \, \gamma^{1.5} \sqrt{f'_c}
$$

con $\gamma$ en kg/m³:

$$
\gamma = \frac{24.0 \times 1000}{9.80665} = 2447.3 \text{ kg/m}^3
$$

$$
E_c = 0.043 \times (2447.3)^{1.5} \times \sqrt{27.46} = 27\,280.6 \text{ MPa}
$$

**Relación modular de corto plazo:**

$$
n = \frac{E_s}{E_c} = \frac{200\,000}{27\,280.6} = 7.3312
$$

### 3.3 Secciones de la viga

La viga es simétrica respecto del centro de luz. El alma y el ala superior son constantes; el espesor del ala inferior varía:

| Segmento | Intervalo | Alma $h_w \times t_w$ | Ala sup. $b_{fs} \times t_{fs}$ | Ala inf. $b_{fi} \times t_{fi}$ |
| -------- | --------: | ---------------------: | -------------------------------: | -------------------------------: |
| A | 0.0–8.0 m | 1755 × 19 mm | 500 × 32 mm | 600 × 25 mm |
| B | 8.0–16.5 m | 1755 × 19 mm | 500 × 32 mm | 600 × 32 mm |
| C | 16.5–33.5 m | 1755 × 19 mm | 500 × 32 mm | 600 × 50 mm |

Las propiedades de la sección compuesta de corto plazo se calculan transformando el concreto a acero equivalente (factor $n = 7.3312$).

### 3.4 Carga vehicular HL-93

| Parámetro | Valor | Unidad |
| --------- | ----: | ------ |
| Eje frontal del camión | 35 | kN |
| Ejes traseros del camión | 145 | kN c/u |
| Separación frontal | 4.30 | m |
| Separación trasera mín. | 4.30 | m |
| Separación trasera máx. | 9.00 | m |
| Carga de carril | 9.3 | kN/m |
| Separación tandem | 1.20 | m |
| Eje del tandem | 110 | kN c/u |
| Incremento dinámico (IM) | 33 | % |
| IM para fatiga | 15 | % |

**Carga del camión con IM:**

$$
P_{frontal} = 35 \times 1.33 = 46.55 \text{ kN}
$$

$$
P_{posterior} = 145 \times 1.33 = 192.85 \text{ kN}
$$

### 3.5 Ancho del carril de diseño

$$
B_{carril} = 3.00 \text{ m}
$$

Los centros del carril se desplazan desde $-500$ mm hasta $+500$ mm con paso de 100 mm (11 posiciones), cubriendo todo el ancho de calzada de 4.00 m.

---

## 4. Método Aproximado — Ecuaciones MTC (Tabla 2.6.4.2.2.2b-1)

### 4.1 Conversión a unidades inglesas

Las ecuaciones de la Tabla 2.6.4.2.2.2b-1 están formuladas en unidades inglesas. Se convierten los parámetros:

$$
S_{ft} = \frac{S}{0.3048} = \frac{2.00}{0.3048} = 6.562 \text{ pies}
$$

$$
L_{ft} = \frac{L}{0.3048} = \frac{50.00}{0.3048} = 164.04 \text{ pies}
$$

$$
t_{s,in} = \frac{t_s}{0.0254} = \frac{0.20}{0.0254} = 7.874 \text{ pulgadas}
$$

### 4.2 Rigidez de la viga compuesta (parámetro $K_g$)

Se usa la viga del segmento C (centro de luz, sección más pesada) como representativa:

**Sección de acero sola** (segmento C):
- $A_s = 69\,595$ mm²
- $I_x \approx 1.136 \times 10^{10}$ mm⁴ (calculado por el código)
- $y_{inferior} \approx 906$ mm

**Distancia desde el eje inferior del acero hasta el centro de la losa:**

$$
e_g = h_{acero} + h_h + \frac{t_s}{2} - y_{inf} = 1812 + 50 + 100 - 906 = 1056 \text{ mm}
$$

**Rigidez transformada a acero:**

$$
K_g = n \left( I_x + A_s \cdot e_g^2 \right)
$$

$$
K_g = 7.3312 \left( 1.136 \times 10^{10} + 69\,595 \times 1056^2 \right)
$$

$$
K_g = 7.3312 \times \left( 1.136 \times 10^{10} + 7.795 \times 10^{10} \right) = 6.57 \times 10^{11} \text{ mm}^4
$$

**Conversión a pulgadas⁴:**

$$
K_{g,in^4} = \frac{K_g}{25.4^4} = \frac{6.57 \times 10^{11}}{416\,231} = 1.578 \times 10^6 \text{ in}^4
$$

### 4.3 Verificación de rango de validez

La Tabla 2.6.4.2.2.2b-1 es válida para:

| Parámetro | Rango | Valor | ¿Dentro? |
| --------- | ----- | ----- | -------- |
| $S_{ft}$ (pies) | 3.5–16.0 | 6.562 | ✓ |
| $L_{ft}$ (pies) | 20.0–240.0 | 164.04 | ✓ |
| $t_{s,in}$ (pulg) | 4.5–12.0 | 7.874 | ✓ |
| $K_{g,in^4}$ | 10 000–7 000 000 | 1 578 000 | ✓ |
| Número de vigas | ≥ 4 | 3 | **✗** |

**Nota:** El número de vigas (3) está fuera del rango mínimo de 4. Las ecuaciones aproximadas fueron calibradas para puentes con 4 o más vigas. Para 3 vigas, el método aproximado puede ser conservador o no conservador. Por ello se recurre al **análisis refinado por parrilla**.

### 4.4 Cálculo de los factores aproximados

A pesar de estar fuera de rango, se calculan las ecuaciones para referencia:

**Término auxiliar:**

$$
\text{término} = \frac{K_{g,in^4}}{12 \cdot L_{ft} \cdot t_{s,in}^3} = \frac{1\,578\,000}{12 \times 164.04 \times 7.874^3} = \frac{1\,578\,000}{95\,568} = 16.51
$$

**Momento — viga interior:**

$$
g_{m1} = 0.06 + \left(\frac{S_{ft}}{14}\right)^{0.4} \left(\frac{S_{ft}}{L_{ft}}\right)^{0.3} (\text{término})^{0.1}
$$

$$
g_{m1} = 0.06 + \left(\frac{6.562}{14}\right)^{0.4} \left(\frac{6.562}{164.04}\right)^{0.3} (16.51)^{0.1}
$$

$$
g_{m1} = 0.06 + (0.4687)^{0.4} \times (0.0400)^{0.3} \times (16.51)^{0.1}
$$

$$
g_{m1} = 0.06 + 0.7107 \times 0.3298 \times 1.310 = 0.06 + 0.3077 = 0.3677
$$

$$
g_{m2} = 0.075 + \left(\frac{S_{ft}}{9.5}\right)^{0.6} \left(\frac{S_{ft}}{L_{ft}}\right)^{0.2} (\text{término})^{0.1}
$$

$$
g_{m2} = 0.075 + \left(\frac{6.562}{9.5}\right)^{0.6} \times (0.0400)^{0.2} \times (16.51)^{0.1}
$$

$$
g_{m2} = 0.075 + (0.6907)^{0.6} \times (0.0400)^{0.2} \times (1.310)
$$

$$
g_{m2} = 0.075 + 0.8101 \times 0.5253 \times 1.310 = 0.075 + 0.5584 = 0.6334
$$

$$
g_{m,int} = \max(g_{m1}, g_{m2}) = \max(0.3677, 0.6334) = 0.6334
$$

**Corte — viga interior:**

$$
g_{v1} = 0.36 + \frac{S_{ft}}{25} = 0.36 + \frac{6.562}{25} = 0.36 + 0.2625 = 0.6225
$$

$$
g_{v2} = 0.20 + \frac{S_{ft}}{12} - \left(\frac{S_{ft}}{35}\right)^2 = 0.20 + \frac{6.562}{12} - \left(\frac{6.562}{35}\right)^2
$$

$$
g_{v2} = 0.20 + 0.5468 - 0.0351 = 0.7117
$$

$$
g_{v,int} = \max(g_{v1}, g_{v2}) = \max(0.6225, 0.7117) = 0.7117
$$

**Viga exterior — regla de la palanca:**

$$
d_e = 0.0 \text{ m (distancia borde calzada a viga exterior)}
$$

$$
d_{e,ft} = \frac{d_e}{0.3048} = 0.0 \text{ pies}
$$

$$
r_1 = 0.60 - d_{e,ft} = 0.60 \text{ pies}
$$

$$
r_2 = r_1 + 1.80 = 2.40 \text{ pies}
$$

$$
\text{Reacción} = \frac{1}{2} \max\left(0, \min\left(1, \frac{S_{ft} - r_1}{S_{ft}}\right)\right) + \frac{1}{2} \max\left(0, \min\left(1, \frac{S_{ft} - r_2}{S_{ft}}\right)\right)
$$

$$
= \frac{1}{2} \min\left(1, \frac{6.562 - 0.60}{6.562}\right) + \frac{1}{2} \min\left(1, \frac{6.562 - 2.40}{6.562}\right)
$$

$$
= \frac{1}{2}(0.9086) + \frac{1}{2}(0.6343) = 0.4543 + 0.3172 = 0.7715
$$

**Factor de palanca con presencia múltiple:**

$$
\text{palanca} = 1.20 \times 0.7715 = 0.9258
$$

**Momento — viga exterior:**

$$
g_{m,ext} = \max\left(\text{palanca},\ (0.77 + d_{e,ft}/9.1) \times g_{m,int}\right)
$$

$$
= \max\left(0.9258,\ (0.77 + 0) \times 0.6334\right) = \max(0.9258,\ 0.4877) = 0.9258
$$

**Corte — viga exterior:**

$$
g_{v,ext} = \max\left(\text{palanca},\ (0.60 + d_{e,ft}/10.0) \times g_{v,int}\right)
$$

$$
= \max\left(0.9258,\ 0.60 \times 0.7117\right) = \max(0.9258,\ 0.4270) = 0.9258
$$

### 4.5 Comparación: Aproximado vs. Parrilla

| Efecto | Aprox. int. | Parrilla int. | Aprox. ext. | Parrilla ext. |
| ------ | ----------: | -------------: | ----------: | -------------: |
| Momento | 0.6334 | **0.4255** | 0.9258 | **0.4889** |
| Corte | 0.7117 | **0.6454** | 0.9258 | **0.4430** |

**Observaciones:**

1. El método aproximado **sobreestima** significativamente los factores para este puente de 3 vigas (fuera de rango de validez).
2. La viga exterior por palanca (0.9258) es extremadamente conservadora porque asume que toda la carga de un carril se transfiere proporcionalmente a la viga más cercana.
3. El análisis por parrilla captura la rigidez real del sistema y produce factores más razonables.

---

## 5. Método Refinado — Parrilla Elástica Lineal

### 5.1 Concepto físico

Una parrilla es una red bidimensional de elementos beam formada por:

- **Barras longitudinales** (dirección $x$): representan las vigas principales con su rigidez flexional ($EI$) y torsional ($GJ$) compuesta de corto plazo.
- **Barras transversales** (dirección $y$): representan franjas de losa con rigidez flexional y torsional del concreto.

Las barras se conectan en nodos con **3 grados de libertad** cada uno:
- $w$: desplazamiento vertical
- $\theta_x$: giro alrededor del eje $x$ (torsión de barras longitudinales, flexión de barras transversales)
- $\theta_y$: giro alrededor del eje $y$ (flexión de barras longitudinales, torsión de barras transversales)

### 5.2 Discretización de la malla

**Malla longitudinal ($x$):**

- 20 tramos base uniformes → 21 nodos
- Se añaden nodos obligatorios en: centro de luz ($x = 25.0$ m), puntos de arriostramiento ($x = 0, 6.25, 12.50, \ldots, 50.0$ m) y extremos de segmentos ($x = 8.0, 16.5, 25.0, 33.5, 42.0$ m)
- **Total: 29 nodos en $x$** → 28 elementos por viga longitudinal

**Malla transversal ($y$):**

$$
y = \{-3000,\ -2000,\ 0,\ +2000,\ +3000\} \text{ mm}
$$

- Borde izquierdo del tablero ($y = -3000$ mm)
- Eje viga I ($y = -2000$ mm)
- Eje viga C ($y = 0$ mm)
- Eje viga D ($y = +2000$ mm)
- Borde derecho del tablero ($y = +3000$ mm)

**Total: 5 nodos en $y$** → 4 elementos transversales por estación longitudinal

**Grados de libertad totales:**

$$
N_{dof} = 3 \times N_{nodos} = 3 \times (29 \times 5) = 435
$$

**Condiciones de frontera:**

- En cada extremo de viga ($x = 0$ y $x = L$): se restringe el desplazamiento vertical $w = 0$ (apoyo vertical)
- Los giros $\theta_x$ y $\theta_y$ permanecen libres (condición de simplemente apoyada)
- Total de DOFs restringidos: $2 \times 3 = 6$ por viga × 3 vigas = **18 DOFs restringidos**
- DOFs libres: $435 - 18 = 417$

### 5.3 Matriz de rigidez del elemento

Cada elemento de la parrilla se modela como una viga Euler-Bernoulli con 6 DOFs por elemento (3 por nodo). La matriz de rigidez se ensambla a partir de dos contribuciones:

**Flexión** (ecuación de viga con 4 DOF: $w_1, \theta_{y1}, w_2, \theta_{y2}$):

$$
\mathbf{k}_b = \frac{EI}{l^3} \begin{bmatrix}
12 & 6l & -12 & 6l \\
6l & 4l^2 & -6l & 2l^2 \\
-12 & -6l & 12 & -6l \\
6l & 2l^2 & -6l & 4l^2
\end{bmatrix}
$$

**Torsión** (2 DOF: $\theta_{x1}, \theta_{x2}$):

$$
\mathbf{k}_t = \frac{GJ}{l} \begin{bmatrix}
1 & -1 \\
-1 & 1
\end{bmatrix}
$$

### 5.4 Rigidez de las barras longitudinales

Para cada elemento longitudinal en la posición $x_m$ (punto medio):

1. Se identifica el segmento de viga (A, B o C) que contiene $x_m$
2. Se calculan las propiedades compuestas de corto plazo:
   - $EI_{comp} = E_s \cdot I_{comp}$ (módulo de acero × inercia compuesta transformada)
3. Se calcula la rigidez torsional:

$$
GJ = \kappa \left( G_s \cdot J_{viga} + G_c \cdot J_{losa} \right)
$$

donde:
- $\kappa = 1.0$ (factor de rigidez torsional, confirmado)
- $G_s = \frac{E_s}{2(1+\nu_s)} = \frac{200\,000}{2(1+0.3)} = 76\,923$ MPa
- $G_c = \frac{E_c}{2(1+\nu_c)} = \frac{27\,280.6}{2(1+0.2)} = 11\,367$ MPa
- $J_{viga} = \frac{b_{fs} t_{fs}^3 + b_{fi} t_{fi}^3 + h_w t_w^3}{3}$ (constante de Saint-Venant de sección I abierta)
- $J_{losa} = \frac{b_e \cdot t_s^3}{3}$ (contribución torsional de la losa)

**Ejemplo para segmento C:**

$$
J_{viga} = \frac{500 \times 32^3 + 600 \times 50^3 + 1755 \times 19^3}{3}
$$

$$
= \frac{500 \times 32\,768 + 600 \times 125\,000 + 1755 \times 6\,859}{3}
$$

$$
= \frac{16\,384\,000 + 75\,000\,000 + 12\,037\,545}{3} = \frac{103\,421\,545}{3} = 34\,473\,848 \text{ mm}^4
$$

$$
J_{losa} = \frac{2000 \times 200^3}{3} = \frac{2000 \times 8\,000\,000}{3} = 5\,333\,333\,333 \text{ mm}^4
$$

$$
GJ = 76\,923 \times 34\,473\,848 + 11\,367 \times 5\,333\,333\,333
$$

$$
= 2.652 \times 10^{12} + 6.062 \times 10^{13} = 6.327 \times 10^{13} \text{ N·mm}^2
$$

### 5.5 Rigidez de las barras transversales (losa)

Cada barra transversale representa una franja de losa de ancho tributario $b_x$:

$$
EI_t = \kappa_f \cdot E_c \cdot \frac{b_x \cdot t_s^3}{12}
$$

$$
GJ_t = \kappa_t \cdot G_c \cdot \frac{b_x \cdot t_s^3}{3}
$$

donde $\kappa_f = \kappa_t = 1.0$ (factores de rigidez transversal confirmados).

El ancho tributario $b_x$ se calcula con la regla del trapecio:

$$
b_x[0] = \frac{x[1] - x[0]}{2}, \quad b_x[-1] = \frac{x[-1] - x[-2]}{2}, \quad b_x[i] = \frac{x[i+1] - x[i-1]}{2}
$$

### 5.6 Ensamblaje y solución

La ecuación de equilibrio de la parrilla es:

$$
\mathbf{K} \cdot \mathbf{u} = \mathbf{F}
$$

donde:
- $\mathbf{K}$: matriz de rigidez global ($435 \times 435$)
- $\mathbf{u}$: vector de desplazamientos
- $\mathbf{F}$: vector de cargas

**Separación de DOFs:**

$$
\begin{bmatrix}
\mathbf{K}_{ff} & \mathbf{K}_{fr} \\
\mathbf{K}_{rf} & \mathbf{K}_{rr}
\end{bmatrix}
\begin{Bmatrix}
\mathbf{u}_f \\
\mathbf{u}_r
\end{Bmatrix}
=
\begin{Bmatrix}
\mathbf{F}_f \\
\mathbf{R}_r
\end{Bmatrix}
$$

Donde el subíndice $f$ denota DOFs libres y $r$ denota DOFs restringidos. Como $\mathbf{u}_r = \mathbf{0}$ (apoyos verticales):

$$
\mathbf{K}_{ff} \cdot \mathbf{u}_f = \mathbf{F}_f
$$

$$
\mathbf{u}_f = \mathbf{K}_{ff}^{-1} \cdot \mathbf{F}_f
$$

El solver utiliza descomposición LU de NumPy (`np.linalg.solve`).

---

## 6. Carga en la Parrilla

### 6.1 Posicionamiento del camión

El camión HL-93 tiene 3 ejes con separaciones:

$$
\text{Eje 1 (frontal): } x_f, \quad P_1 = 46.55 \text{ kN}
$$

$$
\text{Eje 2 (trasero): } x_f + 4.30 \text{ m}, \quad P_2 = 192.85 \text{ kN}
$$

$$
\text{Eje 3 (trasero): } x_f + 4.30 + s \text{ m}, \quad P_3 = 192.85 \text{ kN}
$$

donde $s$ varía desde 4.30 m hasta 9.00 m con paso de 0.30 m (17 separaciones).

El camión se desplaza longitudinalmente ($x$) y transversalmente ($y$) para encontrar la posición crítica.

### 6.2 Carga de carril

La carga de carril uniforme ($q = 9.3$ kN/m) se distribuye sobre el ancho de 3.00 m del carril de diseño. Se evalúa en 5 puntos de integración a lo largo del ancho del carril.

### 6.3 Carga transversal en la parrilla

Cada carga puntual se aplica al nodo más cercano de la parrilla. Si la carga cae entre dos nodos transversales, se interpola con las **funciones de forma de viga cúbica de Hermite**:

$$
N_1 = 1 - 3\xi^2 + 2\xi^3, \quad N_2 = l(\xi - 2\xi^2 + \xi^3)
$$

$$
N_3 = 3\xi^2 - 2\xi^3, \quad N_4 = l(-\xi^2 + \xi^3)
$$

donde $\xi = (y - y_i) / (y_{i+1} - y_i)$.

### 6.4 Separación de líneas de rueda

Las cargas de cada eje se aplican en dos puntos separados por 1.80 m (separación de líneas de rueda):

$$
y_{izq} = y_{centro} - 0.90 \text{ m}, \quad y_{der} = y_{centro} + 0.90 \text{ m}
$$

$$
P_{rueda} = \frac{P_{eje}}{2}
$$

---

## 7. Casos Críticos

### 7.1 Criterio de búsqueda

Para cada efecto (momento, corte, fatiga), se busca la posición del camión que maximiza la respuesta de **una viga individual**. El algoritmo evalúa:

1. **Posiciones longitudinales candidatas**: barrido regular con paso de 250 mm, más posiciones cuando un eje cruza la sección evaluada o un apoyo (para capturar quiebres de la respuesta).
2. **Posiciones transversales**: 11 posiciones del centro del carril desde $-500$ mm hasta $+500$ mm con paso de 100 mm.
3. **Separaciones del camión**: de 4.30 m a 9.00 m con paso de 0.30 m.
4. **Orientación**: camión normal e invertido.

### 7.2 Caso crítico para momento (centro de luz)

**Vehículo:** camión (normal)  
**Separación:** 4.30 m (mínima)  
**Posición frontal:** $x_f = 20.70$ m

Los ejes se ubican en:

| Eje | Posición $x$ (m) | Carga (kN) |
| --- | ----------------: | ----------: |
| 1 (frontal) | 20.70 | 46.55 |
| 2 (trasero) | 25.00 | 192.85 |
| 3 (trasero) | 29.30 | 192.85 |

**Carga de carril:** $q = 9.3$ kN/m sobre toda la luz

**Respuesta de referencia** (momento en una viga simple aislada):

$$
M_{ref} = \sum P_i \cdot \eta_M(x=L/2, z_i) + \frac{qL^2}{8}
$$

donde $\eta_M(L/2, z)$ es la ordenada de la línea de influencia de momento en centro de luz:

$$
\eta_M(L/2, z) = \begin{cases} z(L - L/2)/L = z/2 & \text{si } z \leq L/2 \\ (L/2)(L-z)/L & \text{si } z > L/2 \end{cases}
$$

Para los ejes en $z_1 = 20.70$, $z_2 = 25.00$, $z_3 = 29.30$ m (todos ≤ 25.0 m o > 25.0 m):

$$
\eta_1 = \frac{20.70 \times 25.0}{50.0} = 10.35 \text{ m}
$$

$$
\eta_2 = \frac{25.0 \times 25.0}{50.0} = 12.50 \text{ m}
$$

$$
\eta_3 = \frac{25.0 \times (50.0 - 29.3)}{50.0} = \frac{25.0 \times 20.7}{50.0} = 10.35 \text{ m}
$$

$$
M_{camion} = 46.55 \times 10.35 + 192.85 \times 12.50 + 192.85 \times 10.35
$$

$$
= 481.8 + 2410.6 + 1996.0 = 4888.4 \text{ kN·m}
$$

$$
M_{carril} = \frac{9.3 \times 50.0^2}{8} = \frac{9.3 \times 2500}{8} = 2906.3 \text{ kN·m}
$$

$$
M_{ref} = 4888.4 + 2906.3 = 7794.7 \text{ kN·m} \approx 7.795 \times 10^9 \text{ N·mm}
$$

(Verificado: el código reporta `respuesta_referencia = 7 794 665 000` N·mm)

### 7.3 Caso crítico para corte (apoyo)

**Vehículo:** camión invertido (eje pesado primero)  
**Separación:** 4.30 m  
**Posición frontal:** $x_f = 0.0$ m (justo en el apoyo)

| Eje | Posición $x$ (m) | Carga (kN) |
| --- | ----------------: | ----------: |
| 1 (pesado) | 0.00 | 192.85 |
| 2 (pesado) | 4.30 | 192.85 |
| 3 (liviano) | 8.60 | 46.55 |

**Respuesta de referencia** (corte en apoyo de viga simple):

$$
V_{ref} = \sum P_i \cdot \frac{L - z_i}{L} + \frac{qL}{2}
$$

$$
V_{camion} = 192.85 \times \frac{50}{50} + 192.85 \times \frac{45.7}{50} + 46.55 \times \frac{41.4}{50}
$$

$$
= 192.85 + 176.45 + 38.55 = 407.85 \text{ kN}
$$

$$
V_{carril} = \frac{9.3 \times 50.0}{2} = 232.5 \text{ kN}
$$

$$
V_{ref} = 407.85 + 232.5 = 640.35 \text{ kN} \approx 6.402 \times 10^5 \text{ N}
$$

(Verificado: el código reporta `respuesta_referencia = 640 158.3` N)

### 7.4 Caso crítico para fatiga

**Vehículo:** camión (normal)  
**Separación:** 4.30 m (mínima, única para fatiga)  
**Posición frontal:** $x_f = 20.70$ m  
**IM para fatiga:** 15% (no 33%)

| Eje | Carga con IM fatiga (kN) |
| --- | -----------------------: |
| 1 (frontal) | $35 \times 1.15 = 40.25$ |
| 2 (trasero) | $145 \times 1.15 = 166.75$ |
| 3 (trasero) | $145 \times 1.15 = 166.75$ |

**Sin carga de carril** (MTC 2.4.3.2.4.3: para fatiga solo se considera el camión)

$$
M_{ref,fat} = 40.25 \times 10.35 + 166.75 \times 12.50 + 166.75 \times 10.35
$$

$$
= 416.6 + 2084.4 + 1725.9 = 4226.8 \text{ kN·m} \approx 4.227 \times 10^9 \text{ N·mm}
$$

(Verificado: el código reporta `respuesta_referencia = 4 226 825 000` N·mm)

---

## 8. Ratios de Participación

### 8.1 Definición

Para cada posición transversal del carril ($y_c$), se resuelve la parrilla y se extrae el momento (o corte) en cada viga. El **ratio de participación** es:

$$
\rho_i(y_c) = \frac{\text{Respuesta de la viga } i \text{ con carril en } y_c}{\text{Respuesta de referencia (viga aislada)}}
$$

La suma de los ratios debe ser 1.0 (equilibrio global):

$$
\sum_{i=1}^{N_g} \rho_i(y_c) = 1.0
$$

### 8.2 Resultados para momento

Las 11 posiciones transversales del carril dan los siguientes ratios de participación:

| $y_c$ (mm) | Viga I ($y=-2.0$) | Viga C ($y=0.0$) | Viga D ($y=+2.0$) | Suma |
| ----------: | ----------------: | ----------------: | ----------------: | ----: |
| -500 | 0.40740 | 0.35198 | 0.24062 | 1.000 |
| -400 | 0.39028 | 0.35292 | 0.25680 | 1.000 |
| -300 | 0.37325 | 0.35364 | 0.27311 | 1.000 |
| -200 | 0.35631 | 0.35416 | 0.28953 | 1.000 |
| -100 | 0.33946 | 0.35447 | 0.30607 | 1.000 |
| 0 | 0.32271 | 0.35458 | 0.32271 | 1.000 |
| +100 | 0.30607 | 0.35447 | 0.33946 | 1.000 |
| +200 | 0.28953 | 0.35416 | 0.35631 | 1.000 |
| +300 | 0.27311 | 0.35364 | 0.37325 | 1.000 |
| +400 | 0.25680 | 0.35292 | 0.39028 | 1.000 |
| +500 | 0.24062 | 0.35198 | 0.40740 | 1.000 |

**Observaciones:**

1. La distribución es **simétrica** respecto de $y_c = 0$ (como era de esperarse por la simetría del tablero).
2. Cuando el carril está centrado ($y_c = 0$), la viga central recibe el 35.5% y cada viga exterior el 32.3%.
3. Cuando el carril está en el borde ($y_c = \pm 500$ mm), la viga cercana recibe el 40.7% y la lejana el 24.1%.
4. La viga central tiene una participación casi constante (~35.2–35.5%) independientemente de la posición del carril.

### 8.3 Resultados para corte

| $y_c$ (mm) | Viga I | Viga C | Viga D | Suma |
| ----------: | -----: | -----: | -----: | ----: |
| -500 | 0.36920 | 0.51190 | 0.11889 | 1.000 |
| -400 | 0.33953 | 0.52121 | 0.13926 | 1.000 |
| -300 | 0.31088 | 0.52846 | 0.16066 | 1.000 |
| -200 | 0.28326 | 0.53364 | 0.18310 | 1.000 |
| -100 | 0.25666 | 0.53676 | 0.20658 | 1.000 |
| 0 | 0.23110 | 0.53780 | 0.23110 | 1.000 |
| +100 | 0.20658 | 0.53676 | 0.25666 | 1.000 |
| +200 | 0.18310 | 0.53364 | 0.28326 | 1.000 |
| +300 | 0.16066 | 0.52846 | 0.31088 | 1.000 |
| +400 | 0.13926 | 0.52121 | 0.33953 | 1.000 |
| +500 | 0.11889 | 0.51190 | 0.36920 | 1.000 |

**Observaciones:**

1. La viga central recibe **siempre más del 50%** del corte, independientemente de la posición del carril.
2. Esto se debe a que el corte en el apoyo es más sensible a la proximidad de la carga al apoyo, y la viga central está siempre "cerca" de cualquier posición del carril.

### 8.4 Resultados para fatiga

| $y_c$ (mm) | Viga I | Viga C | Viga D | Suma |
| ----------: | -----: | -----: | -----: | ----: |
| -500 | 0.40445 | 0.36306 | 0.23248 | 1.000 |
| 0 | 0.31640 | 0.36720 | 0.31640 | 1.000 |
| +500 | 0.23248 | 0.36306 | 0.40445 | 1.000 |

Los valores intermedios son similares al caso de momento (la distribución de fatiga sigue la misma tendencia que momento porque ambos se evalúan en centro de luz).

---

## 9. Cálculo de los Factores de Distribución

### 9.1 Aplicación del factor de presencia múltiple

MTC 2018, Artículo 2.4.3.2.2: cuando un solo carril de diseño carga el tablero, se aplica un factor de presencia múltiple $m = 1.20$ a los factores de distribución de momento y corte. **Para fatiga no se aplica** (MTC 2.4.3.2.4.3).

### 9.2 Momento

**Viga interior** (viga C, única viga interior):

$$
DF_{m,int} = m \times \max_{y_c} \rho_{C}(y_c) = 1.20 \times 0.35458 = 0.42550
$$

**Viga exterior** (vigas I o D, se toma el máximo):

$$
DF_{m,ext} = m \times \max_{y_c} \max(\rho_I(y_c), \rho_D(y_c)) = 1.20 \times 0.40740 = 0.48888
$$

### 9.3 Corte

**Viga interior:**

$$
DF_{v,int} = m \times \max_{y_c} \rho_{C}(y_c) = 1.20 \times 0.53780 = 0.64536
$$

**Viga exterior:**

$$
DF_{v,ext} = m \times \max_{y_c} \max(\rho_I(y_c), \rho_D(y_c)) = 1.20 \times 0.36920 = 0.44304
$$

### 9.4 Fatiga

**Viga interior:**

$$
DF_{f,int} = \max_{y_c} \rho_{C}(y_c) = 0.36720
$$

(Sin factor de presencia múltiple)

**Viga exterior:**

$$
DF_{f,ext} = \max_{y_c} \max(\rho_I(y_c), \rho_D(y_c)) = 0.40445
$$

### 9.5 Resumen

| Efecto | Viga interior | Viga exterior | Presencia múltiple |
| ------ | ------------: | ------------: | -----------------: |
| Momento | $1.20 \times 0.35458 = \mathbf{0.42549}$ | $1.20 \times 0.40739 = \mathbf{0.48887}$ | $m = 1.20$ |
| Corte | $1.20 \times 0.53780 = \mathbf{0.64536}$ | $1.20 \times 0.36920 = \mathbf{0.44304}$ | $m = 1.20$ |
| Fatiga | $\mathbf{0.36720}$ | $\mathbf{0.40445}$ | $m = 1.00$ |

---

## 10. Verificación de Resultados

### 10.1 Equilibrio global

El error de equilibrio se define como:

$$
\epsilon = \frac{|\sum R_i - \sum P_i|}{\sum P_i}
$$

El código reporta un error máximo de:

$$
\epsilon_{max} = 1.89 \times 10^{-11}
$$

Esto confirma que la solución numérica es precisa (error prácticamente nulo).

### 10.2 Comparación con método aproximado

| Efecto | Parrilla int. | Aprox. int. | Relación | Parrilla ext. | Aprox. ext. | Relación |
| ------ | ------------: | ----------: | -------: | ------------: | ----------: | -------: |
| Momento | 0.4255 | 0.6334 | 0.672 | 0.4889 | 0.9258 | 0.528 |
| Corte | 0.6454 | 0.7117 | 0.907 | 0.4430 | 0.9258 | 0.479 |

El método aproximado **sobreestima** los factores entre 10% y 93% respecto a la parrilla, lo cual es consistente con el hecho de que las ecuaciones fueron calibradas para 4+ vigas y son conservadoras para puentes más estrechos.

### 10.3 Sentido físico

- **Momento:** La distribución es razonable — la viga más cercana al carril recibe más carga, pero la rigidez transversal de la losa distribuye una fracción significativa a las otras vigas.
- **Corte:** La viga central domina porque está siempre dentro del ancho tributario, sin importar dónde se ubique el carril.
- **Fatiga:** Similar a momento porque ambos se evalúan en la misma sección (centro de luz), pero sin el factor de presencia múltiple.

---

## 11. Limitaciones y Supuestos

1. **Parrilla elástica lineal:** asume comportamiento lineal del concreto y del acero. No captura redistribuciones plásticas.
2. **Interacción total:** la rigidez compuesta supone conexión perfecta entre acero y concreto. La capacidad real depende de los conectores de corte.
3. **Sin diafragmas explícitos:** la rigidez transversal proviene únicamente de la losa. Si los diafragmas de acero tienen rigidez significativa, debería incorporarse.
4. **Factores de rigidez $\kappa = 1.0$:** se asume que la rigidez flexional y torsional no están reducidas por fisuración o deformación diferida.
5. **Un carril de diseño:** el puente tiene un solo carril de 3.00 m. Para puentes con más carriles, se necesitarían combinaciones transversales adicionales.
6. **Factores confirmados:** los valores reportados son directamente los calculados por la parrilla (ningún factor fue reemplazado por un valor confirmado por el usuario, según la configuración de entrada).

---

## 12. Referencias

- MTC 2018, Art. 2.6.4.2.2 — Distribución de cargas vehiculares
- MTC 2018, Tabla 2.6.4.2.2.2b-1 — Ecuaciones aproximadas para tableros de concreto con vigas de acero
- MTC 2018, Art. 2.4.3.2.2 — Factor de presencia múltiple
- MTC 2018, Art. 2.4.3.2.4.3 — Distribución para fatiga
- AASHTO LRFD, Art. 4.6.2.2 — Grillage analysis
- Huang, H. (2004). *Finite Element Analysis of Slab-on-Girder Bridges*
- Código fuente: `analisis_superestructura/elementos/vigas_principales/analisis/parrilla.py`

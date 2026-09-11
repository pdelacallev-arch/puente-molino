# Guía de cálculo manual — Flujo del sistema de vigas principales

**Caso de estudio:** Puente Molinohuayco, revisión `MODIFICADO-R01`
(construcción **no apuntalada**).

**Módulo analizado:** `analisis_superestructura/elementos/vigas_principales/`

**Nivel:** pregrado de Ingeniería Civil (Análisis Estructural / Puentes).

**Objetivo:** reconstruir, a mano y paso a paso, el mismo cálculo que ejecuta el
sistema de cómputo, usando los datos reales del caso `MODIFICADO-R01`, para
comprender **qué calcula el programa, en qué orden, con qué fórmulas y de dónde
sale cada número**.

---

## 0. Cómo leer esta guía

El sistema es, en esencia, una cadena de transformaciones:

```text
entrada.yaml
   │  (1) leer + normalizar + validar
   ▼
Configuracion (objeto tipado)
   │  (2) propiedades de sección
   │  (3) cargas por etapas
   │  (4) respuesta de viga simple (M, V, deformada)
   │  (5) carga móvil HL-93
   │  (6) distribución transversal
   │  (7) combinaciones de carga
   ▼
ResultadoAnalisis
   │  (8) verificaciones de estados límite
   ▼
ResultadoDiseno
   │  (9) estado, trazabilidad y reportes (JSON/CSV/MD/PNG)
   ▼
ejecuciones/<id>/elementos/vigas_principales/{analisis,diseno,parrilla}/
```

Cada etapa de esta guía tiene la misma estructura:

1. **Qué hace el sistema** y en qué archivo/función vive.
2. **La teoría** (fórmulas de pregrado).
3. **El cálculo manual** con los números del caso.
4. **El resultado del programa**, para contrastar.

> Convención de unidades internas del motor: **N, mm, MPa**. La entrada del caso
> está en SI de ingeniería (m, kN, kN/m, MPa) y **no requiere conversión**.

---

## 1. Panorama: qué hace el sistema y en qué orden

| Etapa                          | Archivo                                             | Función principal                                  | Producto                           |
| ------------------------------ | --------------------------------------------------- | -------------------------------------------------- | ---------------------------------- |
| 1. Leer / normalizar / validar | `configuracion.py`, `unidades.py`, `modelos.py`     | `validar_configuracion`                            | objeto `Configuracion`             |
| 2. Propiedades de sección      | `analisis/secciones.py`                             | `propiedades_por_segmento`                         | A, Ix, W, compuestas, Mp           |
| 3. Cargas por etapas           | `analisis/motor.py`                                 | `_analizar_tipo`                                   | w de cada etapa                    |
| 4. Respuesta de viga simple    | `analisis/respuesta.py`                             | `respuesta_distribuida`, `deformada_desde_momento` | M, V, δ                            |
| 5. Carga móvil HL-93           | `analisis/moviles.py`                               | `analizar_hl93`                                    | envolvente LL+IM                   |
| 6. Distribución transversal    | `analisis/parrilla.py` o `analisis/distribucion.py` | `analizar_parrilla`                                | g_m, g_v, g_f                      |
| 7. Combinaciones               | `analisis/motor.py`                                 | `_analizar_tipo`                                   | Resistencia I, Servicio II, Fatiga |
| 8. Verificaciones              | `diseno/verificaciones.py`                          | `verificar_analisis`                               | DCR por estado límite              |
| 9. Reportes / orquestación     | `reportes/exportar.py`, `nucleo/orquestador.py`     | `ejecutar_objetivo`                                | JSON, CSV, MD, PNG                 |

El punto de entrada de alto nivel es
`orquestador.py::analizar(configuracion) → motor.py::analizar_configuracion`.

---

## 2. Datos de entrada del caso `MODIFICADO-R01`

### 2.1 Geometría

| Dato                     | Símbolo |                Valor |
| ------------------------ | ------- | -------------------: |
| Luz                      | $L$     |               50.0 m |
| Número de vigas          | —       |                    3 |
| Separación entre vigas   | $S$     |                2.0 m |
| Ancho de calzada         | —       |                4.0 m |
| Ancho de veredas (total) | —       | 2.0 m (1.0 m c/lado) |
| Ancho de tablero         | —       |                6.0 m |
| Voladizo exterior        | $v$     |                1.0 m |
| Número de carriles       | —       |                    1 |

### 2.2 Losa y materiales

| Dato                   | Símbolo    |       Valor |
| ---------------------- | ---------- | ----------: |
| Espesor de losa        | $t_s$      |      0.20 m |
| Haunch (sobreespesor)  | —          |      0.05 m |
| Ancho de haunch        | —          |      0.45 m |
| Factor de largo plazo  | —          |         3.0 |
| $f'_c$                 | —          |   27.46 MPa |
| Peso unitario concreto | $\gamma_c$ |  24.0 kN/m³ |
| $F_y$                  | —          |     345 MPa |
| $F_u$                  | —          |     450 MPa |
| $E_s$                  | —          | 200 000 MPa |
| Peso unitario acero    | $\gamma_s$ |  77.0 kN/m³ |

### 2.3 Sección de la viga (mm)

| Segmento | $x$ (m)     | Alma $h_w \times t_w$ | Ala superior $b_{ts}\times t_{ts}$ | Ala inferior $b_{ti}\times t_{ti}$ |
| -------- | ----------- | --------------------- | ---------------------------------: | ---------------------------------: |
| A-I      | 0.0 – 8.0   | 1755 × 16             |                           500 × 25 |                       600 × **25** |
| B-I      | 8.0 – 16.5  | 1755 × 16             |                           500 × 25 |                       600 × **32** |
| C-I      | 16.5 – 25.0 | 1755 × 16             |                           500 × 25 |                       600 × **50** |
| C-D      | 25.0 – 33.5 | 1755 × 16             |                           500 × 25 |                       600 × **50** |
| B-D      | 33.5 – 42.0 | 1755 × 16             |                           500 × 25 |                       600 × **32** |
| A-D      | 42.0 – 50.0 | 1755 × 16             |                           500 × 25 |                       600 × **25** |

> La viga es **simétrica**: A-B-C | C-B-A. El alma y el ala superior son
> constantes; **solo varía el espesor del ala inferior** (25 → 32 → 50 mm) para
> acompañar el diagrama de momentos.

### 2.4 Construcción, cargas y tráfico

| Grupo        | Dato                           |                      Valor |
| ------------ | ------------------------------ | -------------------------: |
| Construcción | `apuntalada`                   |                  **false** |
|              | `carga_construccion`           |                   0.0 kN/m |
|              | `incluir_losa_fresca`          |                       true |
|              | `incluir_peso_propio_viga`     |                       true |
| Cargas       | `dc_no_compuesta_adicional`    | int. 1.24 / ext. 0.94 kN/m |
|              | `dc_compuesta`                 |  int. 0.0 / ext. 7.74 kN/m |
|              | `dw`                           | int. 3.38 / ext. 1.69 kN/m |
|              | `pl`                           |  int. 0.0 / ext. 3.63 kN/m |
| Tráfico      | Camión                         |          35 + 145 + 145 kN |
|              | Sep. frontal / posterior       |          4.3 m / 4.3–9.0 m |
|              | Tándem                         |     110 kN c/u, sep. 1.2 m |
|              | Carga de carril                |                   9.3 kN/m |
|              | Incremento dinámico            |         0.33 (fatiga 0.15) |
| Análisis     | N.º estaciones                 |                        101 |
|              | Método de distribución         |               **parrilla** |
|              | Tramos longitudinales parrilla |                         20 |

---

## 3. Etapa 1 — Lectura, normalización y validación

**Archivos:** `configuracion.py`, `unidades.py`, `modelos.py`.

1. `cargar_yaml` lee el texto y calcula una **huella SHA-256** del archivo
   (sirve para la trazabilidad y para nombrar la carpeta de ejecución).
2. `normalizar_a_si` convierte MKS → SI. Como el caso declara
   `sistema_unidades: SI`, **no se modifica nada**.
3. `Configuracion.model_validate` aplica las validaciones de `modelos.py`:
   - el primer segmento empieza en $x=0$ y el último termina en $L$;
   - los segmentos son contiguos y no se superponen;
   - `calzada + veredas ≤ ancho_tablero` → $4.0 + 2.0 = 6.0$ ✔;
   - las posiciones de arriostramiento incluyen 0 y $L$ y están ordenadas;
   - `normativa.edicion == 2018`.

**Resultado:** estado `VALIDA`. Huella de configuración
`4d3b48b1…9188` (revisión R01), distinta de la de R00.

> **Punto didáctico.** El sistema es *content-addressed*: la carpeta de
> ejecución se identifica con `SHA256(huella_config : huella_codigo)`. Cambiar
> `apuntalada: true → false` cambia la huella y obliga a una ejecución nueva.

---

## 4. Etapa 2 — Propiedades de las secciones

**Archivo:** `analisis/secciones.py`.

### 4.1 Módulo de elasticidad del concreto y relación modular

MTC 2018, 2.5.3:

$$
E_c = 0.043\,\gamma^{1.5}\sqrt{f'_c}
\quad\text{con }\gamma\text{ en kg/m}^3
$$

Convertimos el peso unitario: $\gamma = 24\,\text{kN/m}^3 \cdot
\dfrac{1000}{9.80665} = 2447.3\ \text{kg/m}^3$.

$$
E_c = 0.043\,(2447.3)^{1.5}\sqrt{27.46} = 27\,280.6\ \text{MPa}
$$

$$
n = \frac{E_s}{E_c} = \frac{200\,000}{27\,280.6} = 7.3312
\qquad
n_{lp} = 3n = 21.9936
$$

> El factor de largo plazo (3) simula la fluencia del concreto: para cargas
> sostenidas se usa un concreto "más blando", reduciendo el ancho transformado.

### 4.2 Ancho efectivo del ala de concreto

Criterio implementado (`ancho_efectivo`):

**Viga interior:**

$$
b_{e,int} = \min\!\left(\frac{L}{4},\; S,\; 12t_s + \max\!\left(t_w,\frac{b_{ts}}{2}\right)\right)
$$

$$
b_{e,int} = \min\!\left(\frac{12\,500}{1},\; 2000,\; 12(200)+\max(16,250)\right)
= \min(12\,500,\ 2000,\ 2650) = \mathbf{2000\ mm}
$$

**Viga exterior:**

$$
b_{e,ext} = \frac{S}{2} + \min\!\left(\frac{L}{8},\; v,\; 6t_s + \max\!\left(\frac{t_w}{2},\frac{b_{ts}}{4}\right)\right)
$$

$$
b_{e,ext} = 1000 + \min(6250,\ 1000,\ 1200+125)
= 1000 + 1000 = \mathbf{2000\ mm}
$$

> Curiosidad del caso: interior y exterior resultan con el mismo ancho efectivo
> (2000 mm), porque el voladizo de 1.0 m es el que controla el lado exterior.

### 4.3 Propiedades del acero (ejemplo completo: segmento A)

El ala inferior, el alma y el ala superior son tres rectángulos. Tomamos $y$
desde la **fibra inferior**:

| Pieza           | $A_i$ (mm²) |              $y_i$ (mm) |     $I_{0,i}$ (mm⁴) |
| --------------- | ----------: | ----------------------: | ------------------: |
| Ala inf. 600×25 |      15 000 |                    12.5 |             781 250 |
| Alma 16×1755    |      28 080 |      $25+877.5 = 902.5$ | $7.208\times10^{9}$ |
| Ala sup. 500×25 |      12 500 | $25+1755+12.5 = 1792.5$ |             651 042 |

$$
A = \sum A_i = 55\,580\ \text{mm}^2
$$

$$
\bar y = \frac{\sum A_i y_i}{\sum A_i}
= \frac{15\,000(12.5)+28\,080(902.5)+12\,500(1792.5)}{55\,580}
= 862.47\ \text{mm}
$$

$$
I_x = \sum\!\left[I_{0,i} + A_i(\bar y - y_i)^2\right] = 2.8902\times10^{10}\ \text{mm}^4
$$

Módulos resistentes, peso lineal y masa lineal (el sistema distingue peso en
kN/m y masa en kg/m):

$$
W_{inf} = \frac{I_x}{\bar y} = 3.3511\times10^{7}\ \text{mm}^3,\qquad
W_{sup} = \frac{I_x}{h_s-\bar y} = 3.0665\times10^{7}\ \text{mm}^3
$$

$$
w_{ac} = A\cdot10^{-6}\cdot\gamma_s = 55\,580\cdot10^{-6}\cdot 77 = 4.28\ \text{kN/m}
$$

$$
m' = A\cdot10^{-6}\cdot\rho_{ac} = 55\,580\cdot10^{-6}\cdot 7850 = 436.3\ \text{kg/m}
$$

### 4.4 Propiedades compuestas transformadas (ejemplo: segmento A)

Se **transforma el concreto a acero** dividiendo su ancho por $n$ (sección
transformada). Para la losa: $b_{tr}=b_e/n$, $A_{losa}=b_{tr}t_s$,
$y_{losa}=h_s + \text{haunch} + t_s/2$.

**Corto plazo** ($n=7.3312$):

$$
b_{tr} = \frac{2000}{7.3312} = 272.80\ \text{mm},\quad
A_{losa} = 272.80(200) = 54\,560\ \text{mm}^2
$$

$$
y_{losa} = 1805 + 50 + 100 = 1955\ \text{mm}
$$

$$
A_{tr} = 55\,580 + 54\,560 = 110\,140\ \text{mm}^2
$$

$$
\bar y = \frac{55\,580(862.47)+54\,560(1955)}{110\,140} = 1403.7\ \text{mm}
$$

$$
I = I_{acero} + A_{ac}(\bar y - \bar y_{ac})^2
      + \frac{b_{tr}t_s^3}{12} + A_{losa}(y_{losa}-\bar y)^2
  = 6.1948\times10^{10}\ \text{mm}^4
$$

**Largo plazo** ($n_{lp}=21.9936$): el ancho transformado baja a
$b_{tr}=90.94$ mm, $A_{losa}=18\,187$ mm², y resulta
$\bar y = 1131.8$ mm, $I = 4.5319\times10^{10}$ mm⁴.

> **Interpretación física.** La sección compuesta es **mucho más rígida** que
> el acero solo (≈2.1× a corto plazo), porque el ala de concreto trabaja a
> compresión. El eje neutro sube hacia la losa (de 862 a 1404 mm).

### 4.5 Momento plástico y ductilidad (ejemplo: segmento C)

Para flexión positiva se forma una **rótula plástica**: el acero inferior
trabaja a tracción, la losa a compresión (bloque rectangular $0.85f'_c$). El
programa busca por bisección el **eje neutro plástico (PNA)** que equilibra
fuerzas, y calcula $M_p = \sum F_i d_i$.

Para el segmento C:

$$
M_p = 2.6763\times10^{10}\ \text{N·mm} = 26\,763\ \text{kN·m},\qquad
\text{PNA} = 1226.31\ \text{mm}
$$

La altura total compuesta es $D_t = 1830 + 50 + 200 = 2080$ mm, luego:

$$
\frac{D_p}{D_t} = \frac{D_t - \text{PNA}}{D_t}
= \frac{2080-1226.31}{2080} = 0.4104
$$

> Este $D_p/D_t$ será el **estado gobernante** del caso (§10.2).

### 4.6 Resumen de propiedades por segmento

| Seg. | $A_{ac}$ (mm²) | $I_{ac}$ (mm⁴) | $W_{inf,ac}$ (mm³) | $W_{sup,ac}$ (mm³) | $m'$ (kg/m) | $M_p$ (kN·m) | $D_p/D_t$ |
| ---- | -------------: | -------------: | -----------------: | -----------------: | ----------: | -----------: | --------: |
| A    |         55 580 |      2.8902e10 |           3.3511e7 |           3.0665e7 |       436.3 |       19 269 |    0.1873 |
| B    |         59 780 |      3.1831e10 |           3.9364e7 |           3.1724e7 |       469.3 |       21 599 |    0.2503 |
| C    |         70 580 |      3.7946e10 |           5.4092e7 |           3.3626e7 |       554.1 |       26 763 |    0.4104 |

---

## 5. Etapa 3 — Cargas por etapas

**Archivo:** `analisis/motor.py::_analizar_tipo`.

### 5.1 Peso propio de la viga

$$
w_{ac} = A\cdot10^{-6}\cdot\gamma_s \quad [\text{kN/m}]
$$

| Segmento | $A$ (mm²) | $w_{ac}$ (kN/m) |
| -------- | --------: | --------------: |
| A        |    55 580 |           4.280 |
| B        |    59 780 |           4.603 |
| C        |    70 580 |           5.435 |

### 5.2 Concreto fresco + haunch

Ancho tributario por viga:

$$
b_{trib,int} = S = 2.0\ \text{m},\qquad
b_{trib,ext} = \frac{S}{2}+v = 1.0+1.0 = 2.0\ \text{m}
$$

$$
w_{losa} = b_{trib}\,t_s\,\gamma_c = 2.0(0.20)(24) = 9.60\ \text{kN/m}
$$

$$
w_{haunch} = 0.45(0.05)(24) = 0.54\ \text{kN/m}
\quad\Rightarrow\quad
w_{concreto} = 10.14\ \text{kN/m}
$$

### 5.3 La decisión clave: apuntalada vs. no apuntalada

El código hace (líneas 80–84 de `motor.py`):

```python
if construccion.incluir_losa_fresca:
    if construccion.apuntalada:
        w_dc += peso_concreto      # el concreto fresco carga la sección COMPUESTA
    else:
        w_nc += peso_concreto      # el concreto fresco carga la sección de ACERO sola
```

- **Apuntalada (R00):** el apuntalamiento soporta el concreto fresco; la viga de
  acero no lo ve. El peso pasa luego a la sección compuesta.
- **No apuntalada (R01):** la **viga de acero sola** debe soportar su peso y el
  concreto fresco mientras el concreto endurece. Esto ocurre **antes** de que
  exista acción compuesta.

Por eso, en R01:

$$
w_{nc} = w_{ac} + w_{dc,adicional} + w_{concreto}
\qquad
w_{dc,comp} = \text{solo lo aplicado después}
$$

### 5.4 Cargas lineales resultantes (a la entrada del centro de luz, segmento C)

| Etapa                                    |                 Viga interior (kN/m) |                 Viga exterior (kN/m) |
| ---------------------------------------- | -----------------------------------: | -----------------------------------: |
| $DC_{nc}$ (acero + adicional + concreto) | $5.435+1.24+10.14 = \mathbf{16.815}$ | $5.435+0.94+10.14 = \mathbf{16.515}$ |
| $DC_{comp}$                              |                                  0.0 |                                 7.74 |
| $DW$                                     |                                 3.38 |                                 1.69 |
| $PL$                                     |                                  0.0 |                                 3.63 |

> El sistema reporta los valores en el nudo $x=0$ (segmento A):
> $DC_{nc,int}=15.660$ y $DC_{nc,ext}=15.360$ kN/m. La carga es **escalonada**
> porque la sección cambia por segmentos.

---

## 6. Etapa 4 — Respuesta de la viga simple (M y V)

**Archivo:** `analisis/respuesta.py`.

El sistema integra numéricamente (regla del trapecio) las cargas para obtener
cortante y momento, y luego integra $\kappa = M/EI$ para la deformada.

Para una carga uniforme $w$ en una viga simplemente apoyada:

$$
V(x) = w\!\left(\frac{L}{2}-x\right),
\qquad
M(x) = \frac{wx(L-x)}{2},
\qquad
M_{max} = \frac{wL^2}{8}
$$

$$
\delta_{max} = \frac{5wL^4}{384EI}
$$

**Ejemplo (estimación manual, viga interior, segmento C):**

$$
M_{DC,nc} \approx \frac{16.815(50)^2}{8} = 5255\ \text{kN·m}
$$

El programa obtiene $5131$ kN·m porque la carga es algo menor cerca de los
apoyos (segmento A). Para $DW$:

$$
M_{DW} = \frac{3.38(50)^2}{8} = 1056\ \text{kN·m}
$$

### Resultados del sistema (máximos, kN·m)

| Acción                       | Interior | Exterior |
| ---------------------------- | -------: | -------: |
| $M_{DC,nc}$                  |    5 131 |    5 037 |
| $M_{DC,comp}$                |        0 |    2 419 |
| $M_{DW}$                     |    1 056 |      528 |
| $M_{PL}$                     |        0 |    1 134 |
| $M_{LL+IM}$ (ya distribuido) |    3 313 |    3 803 |

### Deformaciones permanentes

| Componente               | Interior (mm) | Exterior (mm) |
| ------------------------ | ------------: | ------------: |
| $DC_{nc}$ (acero solo)   |         188.2 |         184.7 |
| $DC_{comp}+DW$           |          24.2 |          67.4 |
| **Permanente total**     |     **212.4** |     **252.2** |
| $LL+IM$ (corta duración) |          48.6 |          55.8 |

> **Interpretación.** En construcción no apuntalada el concreto fresco se
> deforma sobre la sección de acero (poco rígida), por eso la flecha permanente
> es grande (212–252 mm). Esta es la **contraflecha teórica** a ordenar en
> taller.

---

## 7. Etapa 5 — Carga móvil HL-93

**Archivo:** `analisis/moviles.py`.

### 7.1 Línea de influencia de momento

Para una carga puntual unitaria en $z$, la ordenada de momento en la sección
$x$ es:

$$
\eta_M(x,z) =
\begin{cases}
\dfrac{z(L-x)}{L}, & z \le x\\[2mm]
\dfrac{x(L-z)}{L}, & z > x
\end{cases}
$$

El momento por el tren de cargas es $M(x)=\sum_i P_i\,\eta_M(x,z_i)$.

### 7.2 Cargas HL-93

- **Camión de diseño:** ejes $35 + 145 + 145$ kN, separación frontal 4.3 m y
  posterior variable entre 4.3 y 9.0 m.
- **Tándem:** dos ejes de 110 kN separados 1.2 m.
- **Carga de carril:** $q = 9.3$ kN/m sobre toda la luz.
- **Incremento dinámico:** $IM = 1.33$ para momento/corte; $1.15$ para fatiga.

El sistema **barre** la posición del vehículo (paso 0.25 m) y la separación
posterior (paso 0.30 m) tomando el máximo.

### 7.3 Cálculo manual del momento por carril

Colocamos el eje trasero sobre el centro de luz (posición que maximiza), con
separación posterior 4.3 m. Cargas mayoradas por $IM$:

$$
P_{frontal}=35(1.33)=46.55\ \text{kN},\qquad
P_{trasero}=145(1.33)=192.85\ \text{kN}
$$

Posiciones: 20.7, 25.0 y 29.3 m. Ordenadas:

$$
\eta(20.7)=10.35,\quad \eta(25.0)=12.50,\quad \eta(29.3)=10.35
$$

$$
M_{camion} = 46.55(10.35)+192.85(12.50)+192.85(10.35) = 4888\ \text{kN·m}
$$

$$
M_{carril} = \frac{qL^2}{8} = \frac{9.3(50)^2}{8} = 2906\ \text{kN·m}
$$

$$
M_{LL,carril} = 4888 + 2906 = \mathbf{7795\ kN·m}
$$

El sistema obtiene $7796$ kN·m (diferencia por el paso de barrido). Este valor
es **por carril**, antes de distribuir transversalmente.

---

## 8. Etapa 6 — Distribución transversal

**Archivo:** `analisis/parrilla.py` (método elegido: `parrilla`).

### 8.1 Idea del modelo

Se construye una **parrilla espacial** con **3 grados de libertad por nodo**
($w$, $\theta_x$, $\theta_y$):

- **Vigas longitudinales:** rigidez compuesta de corto plazo $EI$ y torsión
  $GJ$ (Saint-Venant de la I + losa).
- **Barras transversales:** franjas de losa de ancho tributario, con
  $EI_t = E_c b_x t_s^3/12$.
- Apoyos: desplazamiento vertical restringido en los extremos de cada viga.

Se carga el carril en distintas posiciones transversales y se obtiene la
**participación** de cada viga:

$$
g_i = \frac{\text{respuesta de la viga } i}{\text{respuesta de referencia (una viga)}}
$$

Luego se aplica el **factor de presencia múltiple** $m=1.20$ a momento y corte
(no a fatiga).

### 8.2 Factores obtenidos

| Factor           |  Valor |
| ---------------- | -----: |
| $g_{m,interior}$ | 0.4250 |
| $g_{m,exterior}$ | 0.4878 |
| $g_{v,interior}$ | 0.6429 |
| $g_{v,exterior}$ | 0.4441 |
| $g_{f,interior}$ | 0.3665 |
| $g_{f,exterior}$ | 0.4037 |

**Ejemplo:** momento de carga viva distribuido, viga interior:

$$
M_{LL+IM} = g_{m,int}\,M_{LL,carril} = 0.4250(7795) = 3313\ \text{kN·m}
$$

Viga exterior:

$$
M_{LL+IM} = 0.4878(7795) = 3803\ \text{kN·m}
$$

> El programa reporta exactamente 3313 y 3803 kN·m.

---

## 9. Etapa 7 — Combinaciones de carga (MTC 2018)

**Archivo:** `analisis/motor.py` (factores en `modelos.py::FactoresCombinacion`).

$$
\text{Resistencia I} = 1.25(DC_{nc}+DC_{comp}) + 1.50\,DW + 1.75(LL+IM) + 1.75\,PL
$$

$$
\text{Servicio II} = (DC_{nc}+DC_{comp}) + DW + 1.30(LL+IM) + PL
$$

$$
\text{Fatiga I} = 1.75\,\Delta(LL)
$$

**Ejemplo (viga interior, centro de luz):**

$$
M_u = 1.25(5131+0) + 1.50(1056) + 1.75(3313) + 0
= 6414 + 1584 + 5798 = \mathbf{13\,796\ kN·m}
$$

El sistema reporta $13\,794$ kN·m (máximo calculado estación por estación, no en
un solo punto). ✔

**Servicio II:**

$$
M_{ser} = (5131+0)+1056+1.30(3313)+0 = 10\,493\ \text{kN·m}
$$

El sistema reporta $10\,492.7$ kN·m. ✔

---

## 10. Etapa 8 — Verificaciones de diseño

**Archivo:** `diseno/verificaciones.py::verificar_analisis`.
Definición de utilización: $DCR = \text{demanda}/\text{capacidad}$.

### 10.1 Flexión positiva — Resistencia I

Capacidad: momento plástico con **reducción por ductilidad**:

$$
\phi M_n = M_p\cdot\max\!\left(0,\;1.07 - 0.70\frac{D_p}{D_t}\right)
$$

Para el segmento C ($D_p/D_t = 0.4104$):

$$
\phi M_n = 26\,763\,[1.07-0.70(0.4104)] = 26\,763(0.7827)
= \mathbf{20\,947\ kN·m}
$$

| Viga     | Demanda (kN·m) | Capacidad (kN·m) |   DCR |
| -------- | -------------: | ---------------: | ----: |
| Interior |         13 794 |           20 947 | 0.659 |
| Exterior |         18 750 |           20 947 | 0.895 |

### 10.2 Ductilidad $D_p/D_t$

$$
\frac{D_p}{D_t} = 0.4104 \le 0.42 \quad\Rightarrow\quad DCR = 0.977
$$

**Este es el estado gobernante del caso.**

### 10.3 Compacidad del alma

$$
\text{esbeltez} = \frac{2D_{cp}}{t_w} = \frac{2(578.69)}{16} = 72.34
\le 3.76\sqrt{\frac{E_s}{F_y}} = 90.53
\quad\Rightarrow\quad DCR = 0.799
$$

### 10.4 Corte del alma

Alma no rigidizada (conservador), $k=5$:

$$
\frac{h_w}{t_w} = 109.69 > \ell_r = 1.40\sqrt{\frac{E_s k}{F_y}} = 75.4
$$

$$
C = \frac{1.57\,E_s k}{F_y (h_w/t_w)^2} = 0.3782
$$

$$
V_n = 0.58\,F_y\,h_w t_w\,C = 0.58(345)(1755)(16)(0.3782)
= 2.125\times10^6\ \text{N} = \mathbf{2125\ kN}
$$

| Viga     | $V_u$ (kN) | $V_n$ (kN) |   DCR |
| -------- | ---------: | ---------: | ----: |
| Interior |      1 352 |      2 125 | 0.636 |
| Exterior |      1 457 |      2 125 | 0.686 |

### 10.5 Servicio II — esfuerzo elástico

Superposición por etapas (el sistema usa el módulo de sección que corresponde a
cada etapa):

$$
\sigma = \frac{M_{nc}}{W_{ac}} + \frac{M_{comp}+M_{DW}}{W_{lp}}
        + \frac{1.30\,M_{LL}}{W_{cp}} + \frac{M_{PL}}{W_{lp}}
$$

Límite: $0.95F_y = 327.8$ MPa.

El máximo ocurre en **$x=33.5$ m** (cambio de sección C→B), no en el centro de
luz, porque ahí el módulo es menor aunque el momento sea algo menor:

$$
\sigma_{inf} = \frac{4522\times10^6}{3.9364\times10^7}
+ \frac{934\times10^6}{4.6806\times10^7}
+ \frac{1.30(2950\times10^6)}{5.1479\times10^7}
= 114.9+20.0+74.5 = \mathbf{209.3\ MPa}
$$

| Viga     | $\sigma$ (MPa) | Límite (MPa) |   DCR |
| -------- | -------------: | -----------: | ----: |
| Interior |          209.3 |        327.8 | 0.639 |
| Exterior |          275.4 |        327.8 | 0.840 |

### 10.6 Fatiga (categoría C)

$$
\Delta\sigma = \max\!\left(\frac{\Delta M}{W_{cp,sup}},\frac{\Delta M}{W_{cp,inf}}\right)(1.75)
\le \text{CAFL} = 69\ \text{MPa}
$$

| Viga     | $\Delta\sigma$ (MPa) | CAFL (MPa) |   DCR |
| -------- | -------------------: | ---------: | ----: |
| Interior |                47.11 |         69 | 0.683 |
| Exterior |                51.89 |         69 | 0.752 |

### 10.7 Estabilidad lateral durante construcción

Cribado elástico del ala comprimida ($C_b=1$), con longitud no arriostrada
$L_b = 6.25$ m (separación de riostras):

$$
r_t = \frac{b_{ts}}{\sqrt{12}} = 144.34\ \text{mm},\qquad
\frac{L_b}{r_t} = 43.30
$$

$$
F_{cr} = \min\!\left(F_y,\ \frac{\pi^2 E_s}{(L_b/r_t)^2}\right)
= \min(345,\ 1053) = 345\ \text{MPa}
$$

$$
M_{cap} = F_{cr}W_{sup} = 345(3.3626\times10^7) = 1.16\times10^{10}\ \text{N·mm}
= \mathbf{11\,600\ kN·m}
$$

| Viga     | $M_{nc}$ (kN·m) | $M_{cap}$ (kN·m) |   DCR |
| -------- | --------------: | ---------------: | ----: |
| Interior |           5 131 |           11 600 | 0.442 |
| Exterior |           5 037 |           11 600 | 0.434 |

> **Efecto de la no apuntalada.** Este chequeo usa $M_{nc}$ (sección de acero
> sola). En R00 (apuntalada) valía $M_{nc}\approx1962$ kN·m y el $DCR$ era
> 0.169. En R01 el concreto fresco entra en $M_{nc}$ y el $DCR$ sube a 0.442.

### 10.8 Deflexión por carga viva

$$
\delta_{LL} \le \frac{L}{800} = \frac{50\,000}{800} = 62.5\ \text{mm}
$$

| Viga     | $\delta$ (mm) | Límite (mm) |   DCR |
| -------- | ------------: | ----------: | ----: |
| Interior |         48.63 |        62.5 | 0.778 |
| Exterior |         55.82 |        62.5 | 0.893 |

### 10.9 Resumen de verificaciones

| Estado límite                    | Interior DCR | Exterior DCR |
| -------------------------------- | -----------: | -----------: |
| Flexión positiva — Resistencia I |        0.659 |        0.895 |
| **Ductilidad $D_p/D_t$**         |    **0.977** |    **0.977** |
| Compacidad del alma              |        0.799 |        0.799 |
| Corte del alma                   |        0.636 |        0.686 |
| Servicio II                      |        0.639 |        0.840 |
| Fatiga cat. C                    |        0.683 |        0.752 |
| Estabilidad en construcción      |        0.442 |        0.434 |
| Deflexión por carga viva         |        0.778 |        0.893 |

**Gobernante:** Ductilidad $D_p/D_t$, $DCR = 0.977$.

---

## 11. Etapa 9 — Estado, trazabilidad y reportes

**Archivos:** `reportes/exportar.py`, `nucleo/orquestador.py`.

- El estado es **CONDICIONAL**: todas las verificaciones numéricas cumplen,
  pero quedan **validaciones externas pendientes** (conectores, rigidizadores y
  arriostramiento no confirmados). Si alguna validación faltante no existiera,
  el estado sería `CUMPLE`; si algún $DCR>1$, sería `NO_CUMPLE`.
- Cada ejecución guarda:
  - `entrada.json` (configuración resuelta),
  - `resultado.json` (contrato + verificaciones),
  - `reporte.md`, `envolventes.csv`,
  - `figuras/*.png` (diagramas, envolventes, DCR),
  - `manifiesto.json` con `configuracion_sha256` y `codigo_sha256`.

> **Regla de oro:** no editar a mano los resultados intermedios; rompe la
> trazabilidad entre entrada, cálculo y memoria.

---

## 12. Verificación de coherencia

| Comprobación            |        Manual |   Sistema |   ✔   |
| ----------------------- | ------------: | --------: | :---: |
| $E_c$                   |  27 280.6 MPa |  27 280.6 |   ✔   |
| $n$                     |        7.3312 |    7.3312 |   ✔   |
| $b_{e}$ interior        |       2000 mm |      2000 |   ✔   |
| $A$ segmento A          |    55 580 mm² |    55 580 |   ✔   |
| $I$ acero seg. A        | 2.8902e10 mm⁴ | 2.8902e10 |   ✔   |
| $I$ compuesto CP seg. A | 6.1948e10 mm⁴ | 6.1948e10 |   ✔   |
| $M_p$ segmento C        |   26 763 kN·m |    26 763 |   ✔   |
| $M_{LL}$ por carril     |     7795 kN·m |      7796 |   ✔   |
| $M_u$ interior          |   13 796 kN·m |    13 794 |   ✔   |
| $V_n$                   |       2125 kN |      2125 |   ✔   |
| $\phi M_n$ seg. C       |   20 947 kN·m |    20 947 |   ✔   |

**Errores frecuentes de interpretación**

- Confundir $W_{sup}$ del acero (hasta el borde superior del ala) con el de la
  losa: el sistema usa $I/(h_{acero}-\bar y)$ para el acero.
- Creer que Servicio II se maximiza en el centro de luz: **no**, puede
  maximizarse donde cambia la sección.
- Olvidar que $M_{LL}$ ya viene multiplicado por $g$: el valor por carril es
  $M_{LL}/g$.
- Usar la sección compuesta para la estabilidad de construcción: en no
  apuntalada se usa la **sección de acero sola**.

---

## 13. Reproducción en Python (código mínimo)

```python
from analisis_superestructura.elementos.vigas_principales import (
    validar_configuracion,
    analizar,
    verificar,
)

# 1) Leer, normalizar y validar el YAML del caso
config = validar_configuracion(
    "analisis_superestructura/casos/molinohuayco/MODIFICADO-R01/entrada.yaml"
)

# 2) Análisis: secciones, cargas, HL-93, parrilla, combinaciones
resultado = analizar(config)
interior = resultado.tipos_viga["interior"]

# 3) Diseño: verificaciones de estados límite
diseno = verificar(config, resultado)
print("Estado:", diseno.estado)
print("Gobernante:", diseno.estado_gobernante.nombre,
      round(diseno.estado_gobernante.dcr, 4))
```

Para ejecutarlo como el sistema completo (con carpeta de ejecución,
manifiesto y consolidación):

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_superestructura ejecutar todo --caso molinohuayco --revision MODIFICADO-R01
uv run python -m analisis_superestructura consolidar --caso molinohuayco --revision MODIFICADO-R01
```

---

## 14. Conclusión

El sistema automatiza una secuencia de análisis estructural clásica, pero la
hace **explícita y trazable**:

1. **Idealización** de la sección I soldada y del tablero compuesto.
2. **Propiedades** no compuestas y compuestas (transformadas por $n$).
3. **Cargas por etapas**, donde la variable `apuntalada` decide qué sección
   resiste el concreto fresco.
4. **Respuesta** de viga simple por integración (M, V, δ).
5. **Carga móvil HL-93** por líneas de influencia y barrido.
6. **Distribución transversal** por parrilla espacial (o expresiones
   aproximadas).
7. **Combinaciones** LRFD del MTC 2018.
8. **Verificaciones** de resistencia, servicio, fatiga, estabilidad de montaje
   y deflexión, con $DCR$ por chequeo.

En el caso `MODIFICADO-R01` (construcción no apuntalada), el cambio más
significativo respecto de `MODIFICADO-R00` (apuntalada) es la **estabilidad
lateral durante construcción**, cuyo $DCR$ pasó de 0.17 a 0.44, porque la viga
de acero sola ahora soporta el concreto fresco. La sección **sigue cumpliendo**
($DCR$ gobernante 0.977) y el resultado es **CONDICIONAL** por las validaciones
externas pendientes.

> Los resultados son una ayuda de cálculo: deben ser revisados, juzgados y
> aprobados por el ingeniero estructural responsable, y contrastados con la
> normativa vigente, los planos y las especificaciones del proyecto.

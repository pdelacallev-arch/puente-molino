# Metrado manual de cargas lineales de las vigas principales

## Puente Molinohuayco

| Campo | Descripción |
|---|---|
| Sistema estructural | Puente de sección compuesta acero–concreto, simplemente apoyado |
| Luz | 50.00 m |
| Vigas principales | 3 vigas metálicas tipo I |
| Sistema de unidades | m, kN y kN/m |
| Condición constructiva | Vigas metálicas apuntaladas durante el vaciado |
| Estado | Metrado nominal; no constituye combinación de diseño |

## 1. Resultado del metrado

Las cargas lineales que deben asignarse a cada tipo de viga son:

| Parámetro | Viga interior (kN/m) | Viga exterior (kN/m) | Etapa resistente |
|---|---:|---:|---|
| `dc_no_compuesta_adicional` | **1.24** | **0.94** | Viga metálica |
| `dc_compuesta` | **0.00** | **7.74** | Sección compuesta |
| `dw` | **3.38** | **1.69** | Sección compuesta, largo plazo |
| `pl` | **0.00** | **3.63** | Sección compuesta |
| `carga_construccion` | **0.00** | **0.00** | Se verifica en el apuntalamiento |

Además de los valores anteriores:

- el peso propio de cada sección de la viga metálica se obtiene de sus placas;
- el peso de la losa se obtiene con el ancho tributario correspondiente;
- el peso del haunch se obtiene con su ancho y espesor;
- por tratarse de una construcción apuntalada, los pesos de losa y haunch se aplican a la sección compuesta después del endurecimiento del concreto y antes de retirar los puntales.

El peso permanente nominal total de la superestructura considerado en este metrado es:

$$
\boxed{w_{DC,\mathrm{puente}}=61.750\ \text{kN/m}}
$$

equivalente a:

$$
\boxed{w_{DC,\mathrm{puente}}=6.297\ \text{tf/m}}
$$

Este resultado es un inventario de carga nominal. No incluye factores de carga ni permite declarar cumplimiento estructural.

## 2. Objetivo

Determinar manualmente las cargas lineales permanentes y peatonales necesarias para el análisis longitudinal de una viga principal interior y una viga principal exterior, manteniendo separadas las acciones que corresponden a:

1. la viga metálica antes de la acción compuesta;
2. la sección compuesta después del endurecimiento de la losa;
3. las cargas permanentes no estructurales;
4. la carga peatonal.

## 3. Datos de entrada

### 3.1 Geometría y materiales

| Símbolo | Descripción | Valor | Unidad | Fuente | Estado |
|---|---|---:|---|---|---|
| $L$ | Luz entre apoyos | 50.00 | m | Datos del proyecto | Confirmado |
| $n_v$ | Número de vigas | 3 | — | Planos | Confirmado |
| $S$ | Separación entre vigas | 2.00 | m | Planos | Confirmado |
| $B$ | Ancho total del tablero | 6.00 | m | Planos | Confirmado |
| $B_c$ | Ancho de calzada | 4.00 | m | Planos | Confirmado |
| $B_v$ | Ancho total de veredas | 2.00 | m | Planos | Confirmado |
| $t_s$ | Espesor de losa | 0.20 | m | Planos | Confirmado |
| $b_h$ | Ancho del haunch | 0.45 | m | Confirmación del proyecto | Confirmado |
| $h_h$ | Espesor del haunch | 0.05 | m | Confirmación del proyecto | Confirmado |
| $\gamma_c$ | Peso unitario del concreto | 24.00 | kN/m³ | Datos del proyecto | Confirmado |
| $\gamma_s$ | Peso unitario del acero | 77.00 | kN/m³ | Datos del proyecto | Confirmado |
| $t_a$ | Espesor de carpeta asfáltica | 0.075 | m | Metrado del tablero | Confirmado |
| $\gamma_a$ | Peso unitario del asfalto | 22.555 | kN/m³ | $2.30\ \text{tf/m}^3$ | Confirmado |
| $q_{PL}$ | Carga peatonal superficial | 3.628 | kN/m² | $0.370\ \text{tf/m}^2$ | Confirmado |
| $w_b$ | Peso de una baranda | 2.942 | kN/m | $0.300\ \text{tf/m}$ | Confirmado |

### 3.2 Elementos metálicos adicionales

| Elemento | Cantidad por viga | Geometría principal | Estado |
|---|---:|---|---|
| Conector tipo canal | 265 | Canal de 127 mm, longitud 150 mm | Confirmado |
| Rigidizadores | 33 pares | Dos placas de $1748\times200\times16$ mm por ubicación | Confirmado |
| Diafragmas | 9 líneas | Dos paneles de 2.00 m por línea | Confirmado |
| Placas de empalme | 0 | No existen placas de empalme | Confirmado |

## 4. Hipótesis de distribución y etapas

1. La losa cubre el ancho total de 6.00 m. Cada viga tiene un ancho tributario de 2.00 m.
2. La calzada de 4.00 m se encuentra entre los ejes de las vigas exteriores. La viga interior recibe 2.00 m de carpeta y cada exterior recibe 1.00 m.
3. Cada vereda de 1.00 m descarga sobre la viga exterior adyacente.
4. Cada baranda descarga sobre la viga exterior correspondiente.
5. Los conectores y rigidizadores se distribuyen uniformemente a lo largo de 50.00 m para obtener una carga equivalente.
6. Los diafragmas son cargas concentradas en nueve líneas. Para su representación mediante carga uniforme equivalente, cada panel entrega la mitad de su peso a cada viga conectada. La viga interior recibe el equivalente de un panel por línea y cada exterior medio panel por línea.
7. Las vigas metálicas son sostenidas por puntales durante el vaciado. Después de que el concreto alcanza la resistencia requerida, la descarga de los puntales transfiere el peso de la losa y del haunch a la sección compuesta.
8. La carga temporal de construcción se diseña en el sistema de apuntalamiento y no se duplica como carga lineal sobre la viga definitiva.
9. Las posiciones y rigideces de los puntales no forman parte de este metrado. Son indispensables para analizar esfuerzos, reacciones y deformaciones durante la etapa temporal.

## 5. Peso propio de las vigas metálicas

Para una sección I armada, el área de acero es:

$$
A_s=b_{fs}t_{fs}+h_wt_w+b_{fi}t_{fi}
$$

y su peso lineal es:

$$
w_s=A_s\gamma_s
$$

Las secciones tienen ala superior de $450\times20$ mm, alma de $1755\times14$ mm y ala inferior de 600 mm con espesor variable.

### 5.1 Corte A–A

$$
A_A=
450(20)+1755(14)+600(25)
$$

$$
A_A=48\,570\ \text{mm}^2=0.048570\ \text{m}^2
$$

$$
\boxed{w_A=0.048570(77)=3.740\ \text{kN/m}}
$$

### 5.2 Corte B–B

$$
A_B=
450(20)+1755(14)+600(32)
$$

$$
A_B=52\,770\ \text{mm}^2=0.052770\ \text{m}^2
$$

$$
\boxed{w_B=0.052770(77)=4.063\ \text{kN/m}}
$$

### 5.3 Corte C–C

$$
A_C=
450(20)+1755(14)+600(50)
$$

$$
A_C=63\,570\ \text{mm}^2=0.063570\ \text{m}^2
$$

$$
\boxed{w_C=0.063570(77)=4.895\ \text{kN/m}}
$$

### 5.4 Peso medio longitudinal

La secuencia es A–B–C–C–B–A. Las longitudes acumuladas son 16.00 m para A, 17.00 m para B y 17.00 m para C.

$$
\overline{w}_s=
\frac{16w_A+17w_B+17w_C}{50}
$$

$$
\boxed{\overline{w}_s=4.243\ \text{kN/m por viga}}
$$

El peso propio de la viga se obtiene directamente de las dimensiones de cada segmento; no se incluye dentro de `dc_no_compuesta_adicional`.

## 6. Peso de los conectores de corte

El área aproximada del canal se calcula descontando de la altura total los dos espesores de ala:

$$
A_{con}=t_w(d-2t_f)+2b_ft_f
$$

$$
A_{con}=
4.83(127-2\times8.13)+2(44.50)(8.13)
$$

$$
A_{con}=1258.44\ \text{mm}^2
=0.00125844\ \text{m}^2
$$

Peso de un conector de 150 mm:

$$
W_{con,1}=A_{con}L_{con}\gamma_s
$$

$$
W_{con,1}=0.00125844(0.150)(77)
=0.01454\ \text{kN}
$$

Para 265 conectores por viga:

$$
w_{con}=
\frac{265W_{con,1}}{L}
$$

$$
\boxed{w_{con}=0.077\ \text{kN/m por viga}}
$$

Este cálculo determina únicamente el peso. La resistencia y la fatiga de los conectores requieren una verificación independiente.

## 7. Peso de los rigidizadores

El volumen de un par de rigidizadores es:

$$
V_{rig,par}=2h_rb_rt_r
$$

$$
V_{rig,par}=2(1.748)(0.200)(0.016)
=0.0111872\ \text{m}^3
$$

Para 33 pares por viga:

$$
w_{rig}=
\frac{33V_{rig,par}\gamma_s}{L}
$$

$$
\boxed{w_{rig}=0.569\ \text{kN/m por viga}}
$$

## 8. Peso equivalente de diafragmas

El área de un diafragma es:

$$
A_d=33.04(0.00064516)
=0.0213161\ \text{m}^2
$$

Peso de un panel de 2.00 m:

$$
W_{d,p}=A_dL_p\gamma_s
$$

$$
W_{d,p}=0.0213161(2.00)(77)
=3.283\ \text{kN}
$$

La viga interior recibe un panel equivalente por línea:

$$
w_{d,int}=\frac{9W_{d,p}}{50}
$$

$$
\boxed{w_{d,int}=0.591\ \text{kN/m}}
$$

Cada viga exterior recibe medio panel equivalente por línea:

$$
w_{d,ext}=\frac{9(0.5)W_{d,p}}{50}
$$

$$
\boxed{w_{d,ext}=0.295\ \text{kN/m}}
$$

La carga uniforme es una equivalencia para el análisis longitudinal. Un análisis refinado debe representar los diafragmas en sus posiciones reales.

## 9. Carga DC no compuesta adicional

Los componentes adicionales anteriores a la acción compuesta son conectores, rigidizadores y diafragmas. No se incluyen placas de empalme.

### 9.1 Viga interior

$$
w_{DC,nc,int}=w_{con}+w_{rig}+w_{d,int}
$$

$$
w_{DC,nc,int}=0.077+0.569+0.591
$$

$$
\boxed{w_{DC,nc,int}=1.236\approx1.24\ \text{kN/m}}
$$

### 9.2 Viga exterior

$$
w_{DC,nc,ext}=w_{con}+w_{rig}+w_{d,ext}
$$

$$
w_{DC,nc,ext}=0.077+0.569+0.295
$$

$$
\boxed{w_{DC,nc,ext}=0.941\approx0.94\ \text{kN/m}}
$$

## 10. Peso de losa y haunch

### 10.1 Losa

El ancho tributario es 2.00 m para las tres vigas:

$$
w_{losa}=b_tt_s\gamma_c
$$

$$
w_{losa}=2.00(0.20)(24)
$$

$$
\boxed{w_{losa}=9.60\ \text{kN/m por viga}}
$$

### 10.2 Haunch

$$
w_h=b_hh_h\gamma_c
$$

$$
w_h=0.45(0.05)(24)
$$

$$
\boxed{w_h=0.54\ \text{kN/m por viga}}
$$

Por la condición apuntalada, la carga que se transfiere a cada sección compuesta al retirar los puntales es:

$$
\boxed{w_{losa+h}=9.60+0.54=10.14\ \text{kN/m}}
$$

## 11. DC compuesta posterior

La losa estructural de 0.20 m ya se considera en todo el tablero. Sobre cada viga exterior se añade el recrecido de una vereda de 1.00 m de ancho y 0.20 m de espesor:

$$
w_{ver}=b_vt_v\gamma_c
$$

$$
w_{ver}=1.00(0.20)(24)
=4.80\ \text{kN/m}
$$

El peso de una baranda es:

$$
w_b=0.300(9.80665)
=2.942\ \text{kN/m}
$$

Por tanto:

$$
w_{DC,c,ext}=w_{ver}+w_b
$$

$$
\boxed{w_{DC,c,ext}=4.80+2.942=7.742\approx7.74\ \text{kN/m}}
$$

La viga interior no recibe directamente vereda ni baranda:

$$
\boxed{w_{DC,c,int}=0.00\ \text{kN/m}}
$$

## 12. Carga permanente DW

El peso unitario del asfalto en SI es:

$$
\gamma_a=2.30(9.80665)
=22.555\ \text{kN/m}^3
$$

### 12.1 Viga interior

$$
w_{DW,int}=b_{a,int}t_a\gamma_a
$$

$$
w_{DW,int}=2.00(0.075)(22.555)
$$

$$
\boxed{w_{DW,int}=3.383\approx3.38\ \text{kN/m}}
$$

### 12.2 Viga exterior

$$
w_{DW,ext}=b_{a,ext}t_a\gamma_a
$$

$$
w_{DW,ext}=1.00(0.075)(22.555)
$$

$$
\boxed{w_{DW,ext}=1.692\approx1.69\ \text{kN/m}}
$$

Control transversal:

$$
w_{DW,int}+2w_{DW,ext}
=3.383+2(1.692)
=6.767\ \text{kN/m}
$$

que coincide con el metrado global:

$$
4.00(0.075)(22.555)=6.767\ \text{kN/m}
$$

## 13. Carga peatonal PL

Cada vereda tiene 1.00 m de ancho y descarga sobre su viga exterior:

$$
w_{PL,ext}=b_vq_{PL}
$$

$$
w_{PL,ext}=1.00(3.628)
$$

$$
\boxed{w_{PL,ext}=3.628\approx3.63\ \text{kN/m}}
$$

Para la viga interior:

$$
\boxed{w_{PL,int}=0.00\ \text{kN/m}}
$$

Control transversal:

$$
2w_{PL,ext}=2(3.628)=7.257\ \text{kN/m}
$$

$$
B_vq_{PL}=2.00(3.628)=7.257\ \text{kN/m}
$$

## 14. Carga temporal de construcción

Los puntales sostienen las vigas metálicas, el encofrado y el concreto fresco durante el vaciado. En el modelo de la estructura definitiva se adopta:

$$
\boxed{w_{construccion}=0.00\ \text{kN/m por viga}}
$$

Esta asignación evita duplicar sobre la viga definitiva una carga que debe resistir el sistema temporal. No significa que la carga de construcción sea físicamente nula: debe incluirse en el diseño específico de puntales, cabezales, arriostramientos, cimentaciones temporales y secuencia de retiro.

## 15. Control global de carga permanente DC

El peso permanente total se obtiene sumando las tres vigas, conectores, rigidizadores, diafragmas, losa, haunch, veredas y barandas:

$$
\begin{aligned}
w_{DC}={}&3\overline{w}_s
+3w_{con}
+3w_{rig}
+\left(w_{d,int}+2w_{d,ext}\right)\\
&+3w_{losa}
+3w_h
+2w_{DC,c,ext}
\end{aligned}
$$

$$
\begin{aligned}
w_{DC}={}&3(4.2425)+3(0.0770)+3(0.5685)\\
&+[0.5909+2(0.2954)]+3(9.60)+3(0.54)+2(7.742)
\end{aligned}
$$

$$
\boxed{w_{DC}=61.750\ \text{kN/m}}
$$

Para una luz de 50.00 m, el peso total es:

$$
W_{DC}=w_{DC}L=61.750(50)
$$

$$
\boxed{W_{DC}=3087.5\ \text{kN}}
$$

Si se considera una distribución longitudinal simétrica, la reacción nominal en cada estribo es:

$$
R_{DC}=\frac{W_{DC}}{2}
$$

$$
\boxed{R_{DC}=1543.8\ \text{kN por estribo}}
$$

## 16. Parámetros de entrada

```yaml
losa:
  espesor: 0.20
  haunch: 0.05
  ancho_haunch: 0.45

construccion:
  apuntalada: true
  carga_construccion: 0.0
  incluir_losa_fresca: true
  incluir_peso_propio_viga: true

cargas:
  dc_no_compuesta_adicional:
    interior: 1.24
    exterior: 0.94
  dc_compuesta:
    interior: 0.00
    exterior: 7.74
  dw:
    interior: 3.38
    exterior: 1.69
  pl:
    interior: 0.00
    exterior: 3.63
```

## 17. Verificaciones pendientes

1. Definir el número, posición, rigidez y secuencia de retiro de los puntales que sostienen las vigas metálicas.
2. Verificar las vigas durante montaje, antes de instalar todos los puntales y arriostramientos.
3. Diseñar el sistema de apuntalamiento para concreto fresco, encofrado, personal, equipos y efectos de vaciado no simétrico.
4. Verificar resistencia, separación y fatiga de los 265 conectores por viga.
5. Verificar resistencia y soldaduras de los 33 pares de rigidizadores por viga.
6. Representar los diafragmas como cargas concentradas en un análisis longitudinal refinado.
7. Confirmar la secuencia de colocación de veredas, barandas y carpeta asfáltica.
8. Aplicar los factores y combinaciones correspondientes solamente después de completar el inventario de cargas nominales.

## 18. Conclusión

Las cargas lineales necesarias quedan determinadas por separado para vigas interiores y exteriores. La carga no compuesta adicional está controlada por rigidizadores y diafragmas; la carga compuesta exterior está controlada por el recrecido de vereda y la baranda; `DW` corresponde a la carpeta asfáltica y `PL` se aplica únicamente a las vigas exteriores.

El supuesto crítico es que las vigas metálicas permanecen sostenidas por puntales hasta que la losa alcance la resistencia requerida. El metrado puede utilizarse para el inventario de cargas de la estructura definitiva, pero el análisis de la etapa temporal requiere incorporar las posiciones y rigideces reales del apuntalamiento.

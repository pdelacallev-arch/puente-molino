# Reporte detallado del metrado de cargas del tablero

## Puente Molinohuaycco

| Campo | Descripción |
|---|---|
| Proyecto | Creación de los Servicios de Transitabilidad mediante Puente Molinohuaycco |
| Ubicación | Chilcas, La Mar, Ayacucho |
| Sistema estructural | Puente mixto acero-concreto, simplemente apoyado, un tramo recto |
| Luz de cálculo | 50.00 m |
| Archivo analizado | `metrado_cargas/metrado_tablero.py` |
| Tipo de documento | Reporte técnico de cálculo reproducible |
| Sistema de unidades | m, tf, tf/m y tf/m² |
| Estado | Preliminar, sujeto a conciliación con planos y modelo estructural |
| Fecha del reporte | 21 de julio de 2026 |

> **Nota de alcance:** el programa calcula acciones nominales y reacciones características. No aplica factores de carga ni genera combinaciones LRFD. Por ello, los resultados de este reporte no son demandas últimas ni permiten declarar por sí solos el cumplimiento de un elemento estructural.

### Revisión de datos incorporada

Esta versión incorpora los seis cambios confirmados en `registro_verificacion_datos_3.1_a_3.4.md`: ancho de tablero de 6.00 m, concreto de 2.40 tf/m³, áreas de viga de 0.06075 m² y 0.08155 m², nueve líneas de diafragmas y velocidad de viento de 75.00 km/h.

---

## 1. Objetivo

Documentar y explicar en forma auditable los cálculos implementados en `metrado_tablero.py` para determinar:

- cargas permanentes estructurales `DC`;
- carga permanente de superficie de rodadura `DW`;
- carga peatonal `PL`;
- reacción máxima de la sobrecarga vehicular `LL+IM` del modelo HL-93;
- fuerza longitudinal de frenado `BR`;
- viento sobre la estructura `WS`;
- viento sobre vehículos `WL`;
- viento vertical ascendente;
- estimación sísmica equivalente `EQ`;
- acciones nominales que llegan a cada estribo.

El documento también identifica los supuestos del programa, comprueba el equilibrio y señala las verificaciones que deben completarse antes del diseño definitivo.

## 2. Descripción del algoritmo

El código está organizado en tres componentes:

1. La clase inmutable `Datos`, que concentra geometría, pesos específicos y parámetros de carga.
2. La función `reaccion_uniforme(w, L)`, que calcula la reacción de una viga simplemente apoyada sometida a una carga uniforme.
3. La función `calcular(d)`, que ejecuta el metrado y devuelve un diccionario con los resultados.

El flujo implementado es:

```text
Lectura de parámetros
        ↓
Conversión de unidades inglesas
        ↓
Metrado de DC, DW y PL
        ↓
Línea de influencia para camión y tándem HL-93
        ↓
Selección del vehículo que controla
        ↓
Cálculo de BR
        ↓
Cálculo de WS, WL y viento vertical
        ↓
Estimación sísmica C(DC + DW)
        ↓
Resumen de reacciones nominales por estribo
```

---

## 3. Datos de entrada

### 3.1 Geometría

| Variable del código | Símbolo | Descripción | Valor | Unidad | Estado |
|---|---|---|---:|---|---|
| `L` | `L` | Luz entre apoyos | 50.00 | m | Confirmado en memorias |
| `ancho_tablero` | `B` | Ancho total del tablero | 6.00 | m | Confirmado en registro de verificación |
| `ancho_calzada` | `B_c` | Ancho de calzada cargada | 4.00 | m | Memoria de sección |
| `ancho_veredas_total` | `B_v` | Ancho total de veredas | 2.00 | m | 2 veredas de 1.00 m |
| `espesor_losa` | `t_s` | Espesor de losa estructural | 0.20 | m | Confirmado |
| `espesor_recrecido_vereda` | `t_v` | Recrecido considerado para veredas | 0.20 | m | Asumido según memoria de sección |
| `numero_vigas` | `n_v` | Número de vigas principales | 3 | unid. | Confirmado |

### 3.2 Materiales y elementos permanentes

| Variable del código | Descripción | Valor | Unidad | Estado |
|---|---|---:|---|---|
| `gamma_concreto` | Peso específico del concreto | 2.40 | tf/m³ | Confirmado en registro de verificación |
| `gamma_acero` | Peso específico del acero | 7.85 | tf/m³ | Memoria de sección |
| `area_viga_apoyo` | Área de cada viga en apoyo | 0.06075 | m² | Confirmado en registro de verificación |
| `area_viga_centro` | Área de cada viga en centro | 0.08155 | m² | Confirmado en registro de verificación |
| `area_diafragma_in2` | Área de sección del diafragma | 33.04 | in² | Memoria de diafragmas |
| `numero_lineas_diafragma` | Líneas transversales de diafragma | 9 | unid. | Confirmado en registro de verificación |
| `paneles_por_linea` | Paneles entre tres vigas | 2 | unid. | Geometría adoptada |
| `longitud_panel_diafragma` | Longitud de cada panel | 2.00 | m | Separación adoptada de vigas |
| `peso_baranda_por_lado` | Peso lineal de una baranda | 0.300 | tf/m | Memoria de sección |
| `espesor_asfalto` | Espesor promedio de carpeta | 0.075 | m | Adoptado |
| `gamma_asfalto` | Peso específico del asfalto | 2.30 | tf/m³ | Criterio de subestructura |

### 3.3 Cargas transitorias

| Variable del código | Descripción | Valor | Unidad | Estado |
|---|---|---:|---|---|
| `carga_peatonal` | Carga superficial peatonal | 0.370 | tf/m² | Memoria de sección |
| `hl93_frontal` | Eje frontal del camión | 3.6287 | tf | Modelo HL-93 |
| `hl93_posterior` | Cada eje posterior del camión | 14.515 | tf | Modelo HL-93 |
| `tandem_eje` | Cada eje del tándem | 11.340 | tf | Modelo HL-93 |
| `carga_carril` | Carga distribuida de carril | 0.9524 | tf/m | Modelo HL-93 |
| `separacion_rear_min` | Separación posterior adoptada | 4.30 | m | Posición crítica asumida |
| `separacion_tandem` | Separación entre ejes de tándem | 1.20 | m | Modelo HL-93 |
| `incremento_dinamico` | Factor aplicado a ejes | 1.33 | - | Expediente |
| `presencia_multiple_1_carril` | Factor para un carril | 1.20 | - | Expediente |

### 3.4 Viento y sismo preliminar

| Variable del código | Descripción | Valor | Unidad | Estado |
|---|---|---:|---|---|
| `velocidad_viento` | Velocidad ajustada del proyecto | 75.00 | km/h | Confirmado en registro; verificar naturaleza del valor |
| `velocidad_base_viento` | Velocidad asociada a presión básica | 160.00 | km/h | Criterio MTC del expediente |
| `presion_base_vigas_ksf` | Presión básica para vigas | 0.050 | ksf | Manual MTC 2018 |
| `altura_expuesta` | Altura lateral expuesta | 2.932 | m | Preliminar |
| `viento_minimo_kN_m` | Carga lineal mínima de viento | 4.40 | kN/m | Manual MTC 2018 |
| `viento_vertical` | Presión vertical ascendente adoptada | 0.100 | tf/m² | Memoria global |
| `viento_vehicular_klf` | Viento transversal sobre vehículos | 0.100 | klf | Manual MTC 2018 |
| `coeficiente_sismico` | Coeficiente equivalente | 0.240 | - | Documentación de subestructura |

---

## 4. Hipótesis de cálculo

1. La superestructura se idealiza longitudinalmente como una viga simplemente apoyada de 50.00 m.
2. Las cargas permanentes, peatonales y de viento se consideran uniformes a lo largo de la luz.
3. Las reacciones de cargas uniformes se reparten 50/50 entre estribos.
4. Las áreas de las vigas varían lineal y simétricamente entre apoyo y centro de luz; se usa el promedio aritmético.
5. Existen nueve líneas de diafragmas, con dos paneles de 2.00 m por línea.
6. La losa se metrará con 6.00 m de ancho total.
7. El recrecido de veredas se suma sobre la losa general.
8. Se considera un carril de diseño con factor de presencia múltiple 1.20.
9. Para maximizar la reacción, un eje posterior del camión se ubica directamente en el apoyo.
10. El incremento dinámico 1.33 se aplica a los ejes del camión o tándem, no a la carga de carril ni a `PL`.
11. La fuerza de frenado se asigna al apoyo fijo. El código calcula la magnitud total, pero no identifica cuál estribo es fijo.
12. La estimación sísmica usa `C(DC + DW)` y no sustituye un análisis espectral.
13. No se aplican factores de carga ni combinaciones LRFD.
14. No se calcula la distribución transversal entre las tres vigas o apoyos individuales.

### 4.1 Etapas de comportamiento compuesto

El programa metrará el peso global transmitido a los estribos, pero no evalúa esfuerzos por etapas. Para el diseño de las vigas deben diferenciarse:

- etapa no compuesta: acero, diafragmas, encofrado y concreto fresco actuando sobre las vigas metálicas;
- etapa compuesta de corto plazo: cargas aplicadas después de que el concreto alcance la resistencia requerida;
- etapa compuesta de largo plazo: cargas permanentes posteriores y efectos diferidos.

Esta limitación no invalida el equilibrio global de reacciones, pero impide usar el script para verificar tensiones, deflexiones o estabilidad durante el vaciado.

---

## 5. Conversión de unidades

El código utiliza las siguientes conversiones:

### 5.1 Área

$$
1\ \text{in}^2=0.00064516\ \text{m}^2
$$

### 5.2 Presión de viento

$$
1\ \text{ksf}=47.88025898\ \text{kPa}
$$

Como:

$$
1\ \text{tf}=9.80665\ \text{kN}
$$

entonces:

$$
1\ \text{ksf}=\frac{47.88025898}{9.80665}=4.88243\ \text{tf/m}^2
$$

### 5.3 Carga lineal inglesa

$$
1\ \text{klf}=14.59390294\ \text{kN/m}
$$

$$
1\ \text{klf}=\frac{14.59390294}{9.80665}=1.48816\ \text{tf/m}
$$

---

## 6. Cálculo de carga permanente `DC`

### 6.1 Losa de concreto

La expresión general es:

$$
w_{losa}=B t_s \gamma_c
$$

Sustituyendo:

$$
w_{losa}=6.00(0.20)(2.40)=2.8800\ \text{tf/m}
$$

### 6.2 Recrecido de veredas

$$
w_{ver}=B_v t_v \gamma_c
$$

$$
w_{ver}=2.00(0.20)(2.40)=0.9600\ \text{tf/m}
$$

### 6.3 Vigas metálicas principales

Área promedio de una viga:

$$
A_{prom}=\frac{A_{apoyo}+A_{centro}}{2}
$$

$$
A_{prom}=\frac{0.06075+0.08155}{2}=0.07115\ \text{m}^2
$$

Peso lineal de tres vigas:

$$
w_{vigas}=n_v A_{prom}\gamma_s
$$

$$
w_{vigas}=3(0.07115)(7.85)=1.6756\ \text{tf/m}
$$

### 6.4 Diafragmas

Área convertida:

$$
A_d=33.04(0.00064516)=0.02132\ \text{m}^2
$$

Longitud total de elementos:

$$
L_{d,total}=9(2)(2.00)=36.00\ \text{m}
$$

Peso total de diafragmas:

$$
W_d=A_d L_{d,total}\gamma_s
$$

$$
W_d=0.02132(36)(7.85)=6.0239\ \text{tf}
$$

Carga equivalente distribuida:

$$
w_d=\frac{W_d}{L}=\frac{6.0239}{50}=0.1205\ \text{tf/m}
$$

### 6.5 Barandas

$$
w_b=2w_{b,lado}
$$

$$
w_b=2(0.300)=0.6000\ \text{tf/m}
$$

### 6.6 Suma de `DC`

$$
w_{DC}=w_{losa}+w_{ver}+w_{vigas}+w_d+w_b
$$

$$
w_{DC}=2.8800+0.9600+1.6756+0.1205+0.6000
$$

$$
\boxed{w_{DC}=6.2361\ \text{tf/m}}
$$

| Componente | Carga (tf/m) | Porcentaje de `DC` |
|---|---:|---:|
| Losa | 2.8800 | 46.18% |
| Veredas | 0.9600 | 15.39% |
| Vigas principales | 1.6756 | 26.87% |
| Diafragmas | 0.1205 | 1.93% |
| Barandas | 0.6000 | 9.62% |
| **Total** | **6.2361** | **100.00%** |

### 6.7 Reacción de `DC`

Para carga uniforme sobre una viga simplemente apoyada:

$$
R_A=R_B=\frac{wL}{2}
$$

$$
R_{DC}=\frac{6.236061(50)}{2}
$$

$$
\boxed{R_{DC}=155.9015\ \text{tf por estribo}}
$$

### 6.8 Control de equilibrio

Peso total:

$$
W_{DC}=w_{DC}L=6.236061(50)=311.8031\ \text{tf}
$$

Suma de reacciones:

$$
\sum R=2(155.9015)=311.8031\ \text{tf}
$$

El equilibrio vertical se satisface.

---

## 7. Carga de superficie de rodadura `DW`

$$
w_{DW}=B_c t_a \gamma_a
$$

$$
w_{DW}=4.00(0.075)(2.30)
$$

$$
\boxed{w_{DW}=0.6900\ \text{tf/m}}
$$

$$
R_{DW}=\frac{0.6900(50)}{2}
$$

$$
\boxed{R_{DW}=17.2500\ \text{tf por estribo}}
$$

El programa considera `DW` separada de `DC`, lo cual permite aplicar posteriormente los factores de carga específicos de la combinación normativa.

---

## 8. Carga peatonal `PL`

$$
w_{PL}=B_v q_{PL}
$$

$$
w_{PL}=2.00(0.370)
$$

$$
\boxed{w_{PL}=0.7400\ \text{tf/m}}
$$

$$
R_{PL}=\frac{0.7400(50)}{2}
$$

$$
\boxed{R_{PL}=18.5000\ \text{tf por estribo}}
$$

No se aplica incremento dinámico a `PL`.

---

## 9. Reacción máxima por HL-93

### 9.1 Línea de influencia

Para la reacción del apoyo izquierdo de una viga simplemente apoyada:

$$
y_{R_A}(x)=1-\frac{x}{L}
$$

Para un conjunto de cargas concentradas:

$$
R_A=\sum_i P_i y_{R_A}(x_i)
$$

La reacción se maximiza ubicando los ejes más pesados en las ordenadas mayores, es decir, próximos al apoyo analizado.

### 9.2 Camión de diseño

El código adopta las posiciones:

| Eje | Carga (tf) | Posición desde el apoyo (m) | Ordenada |
|---|---:|---:|---:|
| Posterior 1 | 14.5150 | 0.00 | 1.0000 |
| Posterior 2 | 14.5150 | 4.30 | 0.9140 |
| Frontal | 3.6287 | 8.60 | 0.8280 |

Reacción sin incremento dinámico:

$$
R_{cam}=14.515(1.0000)+14.515(0.9140)+3.6287(0.8280)
$$

$$
R_{cam}=30.7863\ \text{tf}
$$

Aplicando `IM = 1.33`:

$$
R_{cam+IM}=1.33(30.7863)
$$

$$
\boxed{R_{cam+IM}=40.9457\ \text{tf}}
$$

### 9.3 Tándem de diseño

| Eje | Carga (tf) | Posición (m) | Ordenada |
|---|---:|---:|---:|
| Tándem 1 | 11.3400 | 0.00 | 1.0000 |
| Tándem 2 | 11.3400 | 1.20 | 0.9760 |

$$
R_{tan}=11.340(1.0000)+11.340(0.9760)
$$

$$
R_{tan}=22.4078\ \text{tf}
$$

Aplicando incremento dinámico:

$$
R_{tan+IM}=1.33(22.4078)
$$

$$
\boxed{R_{tan+IM}=29.8024\ \text{tf}}
$$

### 9.4 Carga de carril

La carga de carril ocupa todo el tramo, cuya línea de influencia de reacción es positiva:

$$
R_{carril}=w_{carril}\frac{L}{2}
$$

$$
R_{carril}=0.9524\frac{50}{2}
$$

$$
\boxed{R_{carril}=23.8100\ \text{tf}}
$$

El incremento dinámico no se aplica a esta carga distribuida.

### 9.5 Vehículo que controla

| Alternativa | Ejes con `IM` (tf) | Carril (tf) | Total antes de presencia múltiple (tf) |
|---|---:|---:|---:|
| Camión + carril | 40.9457 | 23.8100 | 64.7557 |
| Tándem + carril | 29.8024 | 23.8100 | 53.6124 |

El código selecciona automáticamente el máximo mediante:

```python
max(r_camion_im, r_tandem_im)
```

Por tanto, controla el camión de diseño.

### 9.6 Presencia múltiple

$$
R_{LL+IM}=m\left[\max(R_{cam+IM},R_{tan+IM})+R_{carril}\right]
$$

$$
R_{LL+IM}=1.20(40.9457+23.8100)
$$

$$
\boxed{R_{LL+IM}=77.7069\ \text{tf por estribo}}
$$

El máximo del estribo derecho tiene igual magnitud, pero requiere una posición simétrica diferente del vehículo. Los dos máximos no ocurren simultáneamente.

---

## 10. Fuerza de frenado `BR`

El código calcula el mayor de dos criterios antes de aplicar presencia múltiple.

### 10.1 Pesos asociados

Camión:

$$
W_{cam}=3.6287+2(14.515)=32.6587\ \text{tf}
$$

Tándem:

$$
W_{tan}=2(11.340)=22.6800\ \text{tf}
$$

Carga de carril:

$$
W_{carril}=0.9524(50)=47.6200\ \text{tf}
$$

### 10.2 Criterio del 25%

$$
BR_{25}=\max(0.25W_{cam},0.25W_{tan})
$$

$$
BR_{25}=\max(8.1647,5.6700)
$$

$$
\boxed{BR_{25}=8.1647\ \text{tf}}
$$

### 10.3 Criterio del 5%

$$
BR_{5}=\max[0.05(W_{cam}+W_{carril}),0.05(W_{tan}+W_{carril})]
$$

$$
BR_{5}=\max[0.05(32.6587+47.6200),0.05(22.6800+47.6200)]
$$

$$
\boxed{BR_{5}=4.0139\ \text{tf}}
$$

### 10.4 Resultado con presencia múltiple

Controla el criterio del 25%:

$$
BR=m\max(BR_{25},BR_{5})
$$

$$
BR=1.20(8.1647)
$$

$$
\boxed{BR=9.7976\ \text{tf}}
$$

Esta es la fuerza longitudinal total calculada por el programa. Su reparto entre estribos no está resuelto dentro del código. Para el cuadro preliminar del proyecto se supone que el apoyo fijo recibe la totalidad.

---

## 11. Viento sobre la estructura `WS`

### 11.1 Presión básica convertida

$$
P_B=0.050(4.88243)=0.24412\ \text{tf/m}^2
$$

### 11.2 Presión ajustada por velocidad

$$
P_D=P_B\left(\frac{V}{V_B}\right)^2
$$

$$
P_D=0.24412\left(\frac{75.00}{160.00}\right)^2
$$

$$
P_D=0.05364\ \text{tf/m}^2
$$

### 11.3 Carga lineal calculada

$$
w_{WS,calc}=P_D h_{exp}
$$

$$
w_{WS,calc}=0.05364(2.932)
$$

$$
\boxed{w_{WS,calc}=0.1573\ \text{tf/m}}
$$

### 11.4 Carga lineal mínima

$$
w_{WS,min}=\frac{4.40}{9.80665}
$$

$$
\boxed{w_{WS,min}=0.4487\ \text{tf/m}}
$$

El código adopta:

$$
w_{WS}=\max(w_{WS,calc},w_{WS,min})
$$

$$
\boxed{w_{WS}=0.4487\ \text{tf/m}}
$$

Controla la carga mínima, que es aproximadamente 2.85 veces la carga calculada con la velocidad ajustada.

### 11.5 Reacción transversal

$$
R_{WS}=\frac{0.448675(50)}{2}
$$

$$
\boxed{R_{WS}=11.2169\ \text{tf por estribo}}
$$

---

## 12. Viento sobre vehículos `WL`

Conversión de la carga lineal:

$$
w_{WL}=0.100(1.48816)=0.14882\ \text{tf/m}
$$

Reacción:

$$
R_{WL}=\frac{0.14882(50)}{2}
$$

$$
\boxed{R_{WL}=3.7204\ \text{tf por estribo}}
$$

`WL` es una acción interrumpible porque depende de la presencia de vehículos sobre el puente.

---

## 13. Viento vertical

La carga ascendente lineal es:

$$
w_{WSv}=p_v B
$$

$$
w_{WSv}=0.100(6.00)=0.6000\ \text{tf/m}
$$

La reacción ascendente se registra con signo negativo:

$$
R_{WSv}=-\frac{0.6000(50)}{2}
$$

$$
\boxed{R_{WSv}=-15.0000\ \text{tf por estribo}}
$$

Este valor no se suma indiscriminadamente con `WL`; debe usarse únicamente en los estados límite y combinaciones donde corresponda.

---

## 14. Estimación sísmica `EQ`

El script usa un método estático equivalente aplicado a las reacciones permanentes:

$$
R_{EQ}=C(R_{DC}+R_{DW})
$$

$$
R_{EQ}=0.240(155.9015+17.2500)
$$

$$
\boxed{R_{EQ}=41.5564\ \text{tf por estribo}}
$$

La masa considerada corresponde solamente a `DC + DW`. El resultado es una comprobación preliminar y debe contrastarse con las reacciones del análisis espectral.

---

## 15. Resultados consolidados

### 15.1 Cargas lineales

| Acción | Carga lineal (tf/m) | Sentido |
|---|---:|---|
| `DC` | 6.2361 | Vertical descendente |
| `DW` | 0.6900 | Vertical descendente |
| `PL` | 0.7400 | Vertical descendente |
| `WS` adoptado | 0.4487 | Transversal |
| `WL` | 0.1488 | Transversal |
| Viento vertical | 0.6000 | Vertical ascendente |

### 15.2 Reacciones nominales por estribo

| Dirección | Acción | Resultado del script (tf) | Aplicación preliminar |
|---|---|---:|---|
| Vertical | `DC` | 155.9015 | Ambos estribos |
| Vertical | `DW` | 17.2500 | Ambos estribos |
| Vertical | `PL` | 18.5000 | Ambos estribos |
| Vertical | `LL+IM` | 77.7069 | Máximo de cada estribo, no simultáneo |
| Vertical | Viento vertical | -15.0000 | Ambos estribos |
| Longitudinal | `BR` | 9.7976 | Total sobre apoyo fijo, supuesto |
| Transversal | `WS` | 11.2169 | Ambos estribos |
| Transversal | `WL` | 3.7204 | Ambos estribos |
| Horizontal | `EQ` | 41.5564 | Por estribo, estimación preliminar |

### 15.3 Suma nominal de cargas verticales descendentes

El programa reporta:

$$
R_{nom}=R_{DC}+R_{DW}+R_{PL}+R_{LL+IM}
$$

$$
R_{nom}=155.9015+17.2500+18.5000+77.7069
$$

$$
\boxed{R_{nom}=269.3584\ \text{tf por estribo}}
$$

Esta suma es un control de inventario. No es una combinación de diseño.

### 15.4 Aproximación por apoyo de viga

Si las tres líneas de apoyo recibieran la misma carga vertical:

| Acción | Reacción total del estribo (tf) | Reacción media por apoyo (tf) |
|---|---:|---:|
| `DC` | 155.9015 | 51.9672 |
| `DW` | 17.2500 | 5.7500 |
| `PL` | 18.5000 | 6.1667 |
| `LL+IM` | 77.7069 | 25.9023 |

Esta división no reemplaza la distribución transversal real.

---

## 16. Verificaciones realizadas

### 16.1 Equilibrio de cargas uniformes

Para `DC`, `DW`, `PL`, `WS`, `WL` y viento vertical, la suma de las dos reacciones coincide con la carga total aplicada:

$$
2R=wL
$$

### 16.2 Coherencia de `IM`

El código aplica `IM` únicamente a los ejes del camión o tándem. La carga de carril y `PL` permanecen sin amplificación dinámica.

### 16.3 Comparación camión-tándem

$$
R_{cam+IM}=40.9457\ \text{tf}>R_{tan+IM}=29.8024\ \text{tf}
$$

El camión controla correctamente el resultado programado.

### 16.4 Control de viento mínimo

$$
w_{WS,calc}=0.1573\ \text{tf/m}<w_{WS,min}=0.4487\ \text{tf/m}
$$

El código adopta correctamente el máximo.

### 16.5 Ejecución del programa

El archivo fue ejecutado sin errores y produjo los valores documentados en este reporte.

---

## 17. Contraste con documentos del proyecto

| Concepto | Script | Referencia del expediente | Diferencia | Comentario |
|---|---:|---:|---:|---|
| `R_DC` por estribo | 155.902 tf | 163.86 tf, Anexo 3 | -7.958 tf, -4.86% | Conciliar componentes incluidos |
| Peso propio equivalente por estribo | 155.902 tf | 170.321 tf, modelo global | -14.419 tf, -8.47% respecto al modelo | Conciliar componentes modelados |
| `R_LL+IM` | 77.707 tf | 80.19 tf, Anexo 3 | -2.483 tf, -3.10% | Revisar posición y factores contractuales |
| `BR` | 9.798 tf | 20.05 tf, Anexo 3 | -10.252 tf, -51.1% | Posible consideración de dos carriles o duplicación |

El contraste no constituye una validación contractual. Su objetivo es mostrar qué resultados requieren reconstrucción adicional.

---

## 18. Hallazgos de revisión técnica

### 18.1 Resuelto - ancho transversal confirmado

Aunque las memorias contienen anchos contradictorios, el registro de verificación confirma un tablero de 6.00 m: calzada de 4.00 m y dos veredas de 1.00 m. El script ya incorpora este valor.

**Sensibilidad:** si se usara 7.50 m en lugar de 6.00 m, manteniendo los demás datos, la reacción `DC` aumentaría aproximadamente en:

$$
\Delta R=\frac{1.50(0.20)(2.40)(50)}{2}=18.00\ \text{tf por estribo}
$$

### 18.2 Importante - frenado contractual

El valor de 20.05 tf del Anexo 3 es aproximadamente el doble del resultado de una vía obtenido por el script.

**Acción requerida:** confirmar número de carriles futuros, factor de presencia múltiple y ruta de transferencia longitudinal.

### 18.3 Importante - condición de apoyos

El script calcula la magnitud de `BR`, pero no modela la rigidez de los apoyos ni reparte fuerzas longitudinales.

**Acción requerida:** confirmar cuál estribo es fijo, orientación de las guías y rigidez cortante de los neoprenos.

### 18.4 Importante - sismo simplificado

`EQ = 0.24(DC + DW)` es solo un control estático. No incluye modos, rigideces, combinación modal, direcciones ortogonales ni criterios mínimos de conexión.

**Acción requerida:** sustituir o contrastar con reacciones espectrales del modelo aprobado.

### 18.5 Menor - promedio de áreas de vigas

El promedio aritmético es correcto si la variación de área es lineal y simétrica. Si existen tramos escalonados de alas, debe metrarse cada segmento con su longitud real.

### 18.6 Recomendación - validación de entradas

La clase `Datos` permite valores físicamente inválidos, como luz cero, espesores negativos o factores menores que cero.

**Mejora propuesta:** agregar una función de validación que detenga el cálculo ante entradas inválidas.

### 18.7 Recomendación - posición vehicular generalizada

El código usa directamente una posición crítica asumida, no desplaza el vehículo con un paso configurable.

**Mejora propuesta:** implementar un barrido longitudinal del camión y tándem para generar envolventes y reportar la posición crítica.

---

## 19. Límites de aplicación

El programa no incluye:

- factores ni combinaciones LRFD;
- distribución transversal de carga viva;
- reacciones diferenciadas de vigas interiores y exteriores;
- esviaje, curvatura o pendiente longitudinal;
- etapas constructivas y concreto fresco;
- peso de conectores, rigidizadores, empalmes o servicios no definidos;
- frenado repartido por rigidez de apoyos;
- viento longitudinal u oblicuo;
- temperatura, gradiente térmico, retracción o fluencia;
- análisis espectral sísmico;
- fuerzas mínimas de diseño de conexiones sísmicas;
- verificación de capacidad de apoyos, cajuela o estribos;
- demanda/capacidad o declaración de cumplimiento.

---

## 20. Interpretación ingenieril

1. La carga permanente `DC` está controlada por la losa, que aporta aproximadamente 50% del total.
2. El metrado manual de `DC` concuerda razonablemente con la reacción del Anexo 3, lo que valida el orden de magnitud.
3. Para la reacción de apoyo, el camión controla frente al tándem.
4. La carga de carril aporta 23.81 tf antes de presencia múltiple y no debe recibir `IM`.
5. El frenado obtenido corresponde a una vía; su diferencia con el expediente debe resolverse antes del diseño.
6. En viento transversal controla la carga lineal mínima, no la presión reducida por la velocidad local adoptada.
7. El viento vertical reduce la compresión en los apoyos y puede influir en levantamiento o estabilidad.
8. La estimación sísmica es útil como control de orden de magnitud, no como demanda final.
9. El supuesto más sensible es la geometría transversal, seguido por el número de carriles y la condición fija-móvil de los apoyos.

---

## 21. Conclusiones

1. El programa calcula una carga permanente estructural de:

   $$
   \boxed{w_{DC}=6.2361\ \text{tf/m}}
   $$

   que produce:

   $$
   \boxed{R_{DC}=155.9015\ \text{tf por estribo}}
   $$

2. Las reacciones permanentes y peatonales adicionales son:

   $$
   \boxed{R_{DW}=17.2500\ \text{tf}},\qquad
   \boxed{R_{PL}=18.5000\ \text{tf}}
   $$

3. Para HL-93 controla el camión más carga de carril:

   $$
   \boxed{R_{LL+IM}=77.7069\ \text{tf por estribo}}
   $$

4. La fuerza de frenado nominal para un carril es:

   $$
   \boxed{BR=9.7976\ \text{tf}}
   $$

5. Las acciones de viento calculadas son:

   $$
   \boxed{R_{WS}=11.2169\ \text{tf}},\quad
   \boxed{R_{WL}=3.7204\ \text{tf}},\quad
   \boxed{R_{WSv}=-15.0000\ \text{tf}}
   $$

6. La estimación sísmica preliminar resulta:

   $$
   \boxed{R_{EQ}=41.5564\ \text{tf por estribo}}
   $$

7. La suma nominal descendente `DC + DW + PL + LL+IM` es 269.3584 tf por estribo, pero no representa una combinación LRFD.

8. El resultado es preliminar. No puede afirmarse cumplimiento porque no se han evaluado factores, combinaciones, resistencias ni relaciones demanda/capacidad.

---

## 22. Verificaciones pendientes y siguiente paso

Antes de utilizar las cargas en el diseño definitivo se requiere:

1. confirmar el ancho total, ancho de veredas y separación de vigas en planos aprobados;
2. obtener del modelo el desglose completo del peso propio;
3. reconciliar `R_LL+IM` y `BR` con el Anexo 3;
4. confirmar el número de carriles de diseño;
5. identificar el apoyo fijo, el móvil y sus rigideces;
6. extraer reacciones por cada línea de apoyo;
7. reemplazar la estimación sísmica por reacciones espectrales verificadas;
8. construir las combinaciones LRFD aplicables al estribo;
9. transferir las fuerzas a sus cotas reales para calcular momentos y deslizamiento.

El siguiente cálculo lógico es elaborar la matriz de combinaciones de carga del estribo manteniendo separadas las acciones nominales documentadas en este reporte.

---

## 23. Reproducibilidad

El cálculo se ejecuta desde la raíz del proyecto con:

```powershell
python .\metrado_cargas\metrado_tablero.py
```

El programa no requiere dependencias externas y utiliza solamente la biblioteca estándar de Python.

### Archivos relacionados

- `metrado_cargas/metrado_tablero.py`
- `metrado_cargas/resultados_preliminares.csv`
- `metrado_cargas/README.md`

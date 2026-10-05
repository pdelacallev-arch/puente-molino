# MEMORIA DE CÁLCULO: DISEÑO DE LA PANTALLA DE ESTRIBO EN VOLADIZO

**Norma aplicable:** AASHTO LRFD Bridge Design Specifications / Manual de Puentes MTC  
**Referencia didáctica:** *Puentes – AASHTO LRFD* · MSc. Ing. Arturo Rodríguez Serquén (Págs. 270, 282-288)  
**Estado global:** **CUMPLE**

---

## 1. PRE-DIMENSIONADO Y GEOMETRÍA (Paso 1)

| Parámetro | Símbolo | Valor | Unidad | Criterio / Ubicación |
|:---|:---:|:---:|:---:|:---|
| Altura total de relleno | $H$ | 9.87 | m | Superficie de terreno a base zapata |
| Altura libre sobre zapata | $h_p$ | 8.37 | m | Altura total de pantalla voladizo |
| Altura de garganta / mesa | $h_{ef}$ | 5.33 | m | Cima de fuste inferior |
| Altura de pared cajuela | $h_{caj}$ | 3.04 | m | $h_p - h_{ef}$ |
| Espesor corona cajuela | $t_{sup1}$ | 0.40 | m | Nivel $y = h_p$ |
| Espesor nivel garganta | $t_{sup2}$ | 0.40 | m | Nivel $y = h_{ef}$ |
| Espesor inferior base | $t_{inf}$ | 0.99 | m | Nivel $y = 0$ (Punto P, empotramiento) |
| Peso propio pantalla | $W_{est}$ | 11.79 | tf/m | Sin suelo sobre talón (Art. C11.6.5.1) |
| Centro de gravedad vertical | $Y_{P,PIR}$ | 3.42 | m | Medido desde Punto P |

---

## 2. CARGAS ACTUANTES SOBRE LA PANTALLA (Paso 2)

La pantalla se analiza como una viga en voladizo empotrada en el Punto P (cara superior de zapata).

| Carga | Tipo / Distribución | Fuerza $V$ (tf/m) | Brazo $Y_P$ (m) | Momento $M$ (tf-m/m) | Ecuación / Justificación |
|:---|:---|:---:|:---:|:---:|:---|
| **LS** (Sobrecarga viva de terreno) | uniforme | 1.85 | 4.18 | 7.74 | p'' = 0.2208 tf/m2 sobre h=8.37 m |
| **EH** (Empuje activo estático) | triangular_max_base | 12.68 | 2.79 | 35.38 | p = 3.0302 tf/m2 en base, resultante a h/3 |
| **EQterr** (Empuje sísmico del suelo) | uniforme_equivalente | 4.60 | 4.18 | 19.24 | p' = 0.5*(Kae-Ka)*h*gamma = 0.5493 tf/m2 |
| **0.5PIR** (Inercia pantalla (50%)) | inercial | 0.74 | 3.42 | 2.52 | 0.5 * Kh * West = 0.5 * 0.125 * 11.79 tf/m |
| **PEQi** (Inercia superestructura) | concentrada_apoyo | 6.93 | 5.68 | 39.34 | 24.0% * (DC+DW) en apoyo |
| **BR** (Fuerza de frenado) | concentrada_cima | 1.63 | 9.27 | 15.11 | BR = 1.63 tf/m aplicado a hp+0.90=9.27 m |

> **Parámetros geotécnicos y sísmicos empleados:**
> - $K_a = 0.2011$, $K_{ae} = 0.2740$, $\gamma_r = 1.80 \text{ tf/m}^3$, $\phi = 39.80^\circ$, $\delta = 19.90^\circ$.
> - $K_h = 0.125$, $K_v = 0.050$, $h_{eq} = 0.61 \text{ m}$.

---

## 3. COMBINACIONES DE CARGA Y MOMENTO ÚLTIMO (Paso 3)

| Estado Límite | $M_u$ (tf-m/m) | $V_u$ (tf/m) | $\phi_f$ | $M_u / \phi_f$ (tf-m/m) | ¿Rige flexión? |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Resistencia I** | 93.05 | 25.11 | 0.90 | 103.39 | — |
| **Evento Extremo I** | 107.90 | 26.68 | 1.00 | 107.90 | RIGE |
| **Servicio I** | 58.23 | 16.16 | 1.00 | 58.23 | (Para fisuración) |

> **Momento de diseño que rige:** **Evento Extremo I** con solicitación normalizada $M_u/\phi_f = 107.90 \text{ tf-m/m}$.

---

## 4. DISEÑO POR FLEXIÓN: ACERO VERTICAL PRINCIPAL (Paso 4)

El acero principal se coloca en la **cara del terreno** (cara sometida a tracción).

| Parámetro | Símbolo | Valor | Unidad | Observaciones |
|:---|:---:|:---:|:---:|:---|
| Espesor en la base | $t_{inf}$ | 98.7 | cm | Empotramiento en zapata |
| Recubrimiento | $r$ | 5.0 | cm | Cara terreno |
| Peralte efectivo | $d$ | 92.43 | cm | $t_{inf} - r - \varnothing/2$ |
| $A_s$ requerido Resistencia I | $A_{s,Res}$ | 27.35 | cm²/m | $\phi_f = 0.90$ |
| $A_s$ requerido Evento Extremo I | $A_{s,Ext}$ | 28.58 | cm²/m | $\phi_f = 1.00$ |
| **$A_s$ de diseño requerido** | $A_{s,req}$ | **28.58** | **cm²/m** | Rige Evento Extremo I |
| **Refuerzo adoptado** | — | **1" @ 18 cm** | — | **1" @ 175 mm** |
| $A_s$ provisto | $A_{s,prov}$ | **28.95** | cm²/m | $A_{s,prov} \geq A_{s,req}$ ✓ |
| Profundidad bloque compresión | $a$ | 5.11 | cm | $0.85 f'_c b$ |
| Resistencia nominal | $M_n$ | 109.30 | tf-m/m | Par interno $d - a/2$ |
| Ratio Demanda/Capacidad | DCR | 0.987 | — | ✅ Cumple |

---

## 5. VERIFICACIÓN DE ACERO MÍNIMO (Paso 5 - Art. 5.6.3.3)

| Parámetro | Fórmula / Referencia | Valor | Unidad |
|:---|:---|:---:|:---:|
| Módulo de rotura del concreto | $f_r = 0.63\sqrt{f'_c}$ | 3.30 MPa (33.66 kg/cm²) | — |
| Módulo de sección bruta | $S = b \cdot h^2 / 6$ | 162361.50 | cm³ |
| Momento de fisuración | $M_{cr} = 1.1 f_r S$ | 60.12 | tf-m/m |
| 1.33 veces Momento último | $1.33 M_u$ | 143.51 | tf-m/m |
| Mínimo normativo exigido | $\min(M_{cr}, 1.33 M_u)$ | **60.12** | tf-m/m |
| Capacidad provista | $M_n$ | **109.30** | tf-m/m |
| **Estado verificación** | $M_n \geq \min(M_{cr}, 1.33M_u)$ | **✅ CUMPLE** | — |

---

## 6. ACERO DE TEMPERATURA Y RETRACCIÓN (Paso 6 - Art. 5.10.6)

| Parámetro | Fórmula / Criterio | Valor | Unidad |
|:---|:---|:---:|:---:|
| Espesor promedio | $t_{prom} = (t_{sup1} + t_{inf})/2$ | 69.35 | cm |
| Altura de aplicación | $h_{temp}$ | 587.00 | cm |
| Cuantía calculada | $A_{s,temp} = \frac{0.18 b h}{2(b+h)}$ | 5.58 | cm²/m en cada cara |
| Límite AASHTO LRFD | $2.33 \leq A_s \leq 12.70$ | 5.58 | cm²/m en cada cara |
| **Refuerzo adoptado** | Ambas caras / Ambas direcciones | **1/2" @ 22 cm** | **1/2" @ 225 mm** |
| Área provista | $A_{s,prov}$ | 5.63 | cm²/m |
| Separación máxima permitida | $s_{max} = \min(3t, 45\text{ cm})$ | 45.00 | cm |
| **Estado verificación** | $s_{adopt} \leq s_{max}$ | **✅ CUMPLE** | — |

---

## 7. CONTROL DE FISURACIÓN BAJO SERVICIO I (Paso 7 - Art. 5.6.7)

| Parámetro | Fórmula / Símbolo | Valor | Límite / Criterio | Estado |
|:---|:---|:---:|:---:|:---:|
| Momento de Servicio I | $M_s$ | 58.23 tf-m/m | — | — |
| Relación modular | $n = E_s / E_c$ | 7.97 | — | — |
| Eje neutro elástico | $y_{cr}$ | 18.47 cm | — | — |
| Brazo del par interno | $jd = d - y/3$ | 86.27 cm | — | — |
| Esfuerzo en el acero | $f_{ss} = \frac{M_s}{A_s \cdot jd}$ | 2330.9 kg/cm² | $\leq 2520.0$ kg/cm² (0.60 fy) | ✅ OK |
| Factor geométrico | $\beta_s = 1 + \frac{d_c}{0.7(h-d_c)}$ | 1.097 | — | — |
| Factor de exposición | $\gamma_e$ | 0.75 | Severa (contacto con suelo) | — |
| Espaciamiento máximo | $s_{max} = \frac{125000\gamma_e}{\beta_s f_{ss}} - 2d_c$ | **24.1 cm** | $s_{adopt} = 18 \text{ cm}$ | ✅ CUMPLE |

---

## 8. REVISIÓN POR CORTE — MÉTODO GENERAL AASHTO (Paso 8 - Art. 5.7.3.4.2)

| Parámetro | Símbolo / Fórmula | Valor | Unidad | Criterio |
|:---|:---|:---:|:---:|:---|
| Cortante último actuante | $V_u$ | 26.68 | tf/m | Rige Evento Extremo I |
| Peralte efectivo de corte | $d_v = \max(d-a/2, 0.9d, 0.72h)$ | 89.88 | cm | $d_v \geq 83.19 \text{ cm}$ ✓ |
| Deformación longitudinal | $\varepsilon_s = \frac{|M_u/d_v + V_u|}{E_s A_s}$ | 0.002485 | — | Tracción longitudinal |
| Espaciamiento fisuras equiv. | $s_{xe}$ | 35.38 | pulg | $12 \leq s_{xe} \leq 80$ ✓ |
| Factor de resistencia concreto | $\beta$ | **1.149** | — | Ec. 5.7.3.4.2-2 |
| Resistencia del concreto | $V_c$ | 45.81 | tf/m | Ec. 5.7.3.3-3 |
| Resistencia nominal | $V_n = \min(V_c, 0.25 f'_c b d_v)$ | 45.81 | tf/m | — |
| Resistencia de diseño | $V_r = \phi_v V_n$ ($\phi_v = 0.90$) | **41.23** | **tf/m** | Capacidad sin estribos |
| Ratio Demanda/Capacidad | DCR corte | 0.647 | — | ✅ CUMPLE |

> **Conclusión de corte:** $V_r = 41.23 \text{ tf/m} > V_u = 26.68 \text{ tf/m}$. **La pantalla NO requiere estribos transversales.** ✅

---

## 9. CUADRO RESUMEN DE ARMADURAS Y ESPECIFICACIONES

| Elemento / Dirección | Refuerzo Adoptado | Espaciamiento | Cara de Colocación | Área Provista | Estado |
|:---|:---:|:---:|:---|:---:|:---:|
| **Acero principal vertical** | **1"** | **@ 18 cm** | Cara terreno (posterior) | 28.95 cm²/m | ✅ Conforme |
| **Acero temperatura vertical** | **1/2"** | **@ 22 cm** | Cara libre (frontal) | 5.63 cm²/m | ✅ Conforme |
| **Acero horizontal (ambas caras)** | **1/2"** | **@ 22 cm** | Ambas caras | 5.63 cm²/m | ✅ Conforme |

---

## 10. VERIFICACIONES NORMATIVAS CONSOLIDADAS

| Verificación | Artículo AASHTO | Demanda | Capacidad / Límite | DCR | Estado |
|:---|:---:|:---:|:---:|:---:|:---:|
| Flexión (Resistencia / Extremo) | Art. 5.6.3.2 | $M_u/\phi = 28.6 \text{ cm}^2$ | $A_s = 29.0 \text{ cm}^2$ | 0.987 | ✅ OK |
| Acero Mínimo | Art. 5.6.3.3 | $M_{min} = 60.12 \text{ tf-m}$ | $M_n = 109.30 \text{ tf-m}$ | 0.550 | ✅ OK |
| Control de Fisuración | Art. 5.6.7 | $s = 18 \text{ cm}$ | $s_{max} = 24.1 \text{ cm}$ | 0.725 | ✅ OK |
| Cortante sin estribos | Art. 5.7.3.3 | $V_u = 26.68 \text{ tf}$ | $V_r = 41.23 \text{ tf}$ | 0.647 | ✅ OK |


# Metrado de cargas del tablero - Puente Molinohuaycco

## 1. Objetivo y alcance

Determinar, en forma auditable y preliminar, las cargas verticales y horizontales que la superestructura transmite a cada estribo del puente mixto simplemente apoyado de 50.00 m. Los resultados son acciones nominales; no constituyen por si solos combinaciones LRFD.

El cálculo reproducible se encuentra en `metrado_tablero.py` y el resumen de fuerzas en `resultados_preliminares.csv`.

## 2. Base adoptada

| Parámetro | Valor adoptado | Estado / fuente |
|---|---:|---|
| Luz entre apoyos | 50.00 m | Memorias del proyecto |
| Ancho total del tablero | 6.00 m | Confirmado en registro de verificación 3.1 a 3.4 |
| Calzada para cargas | 4.00 m | Memoria de sección del puente |
| Veredas efectivas | 2 x 1.00 m | Memoria de sección del puente |
| Losa estructural | 0.20 m | Memorias del proyecto |
| Vigas principales | 3 | Memorias del proyecto |
| Separación de vigas | 2.00 m | Memoria de sección del puente |
| Concreto | 2.40 tf/m3 | Confirmado en registro de verificación 3.1 a 3.4 |
| Acero estructural | 7.85 tf/m3 | Memoria de sección |
| Asfalto | 2.30 tf/m3 | Criterio usado en la memoria viva de subestructura |
| Carga peatonal | 0.370 tf/m2 | Memoria de sección; equivalente a 0.075 ksf |
| Sobrecarga vehicular | HL-93 | MTC 2018 / expediente |
| Incremento dinámico | 1.33 | Solo ejes de camión o tándem |
| Presencia múltiple | 1.20 | Un carril cargado |

## 3. Metrado de carga permanente DC

Se considera la losa de 6.00 m de ancho, un recrecido de veredas de 0.20 m sobre 2.00 m de ancho total, tres vigas de sección variable, nueve líneas de diafragmas con dos paneles de 2.00 m y dos barandas. El área promedio de cada viga se obtiene promediando las áreas verificadas en apoyo y centro de luz.

| Componente | Expresión | Carga lineal (tf/m) |
|---|---|---:|
| Losa | 6.00 x 0.20 x 2.40 | 2.880 |
| Recrecido de veredas | 2.00 x 0.20 x 2.40 | 0.960 |
| 3 vigas principales | 3 x (0.06075 + 0.08155)/2 x 7.85 | 1.676 |
| Diafragmas | 33.04 in2 x 36 m x 7.85 / 50 m | 0.120 |
| 2 barandas | 2 x 0.300 | 0.600 |
| **DC total** | Suma | **6.236** |

Para carga uniforme y estructura simplemente apoyada:

`R = w L / 2`

Por tanto, `R_DC = 6.23606 x 50 / 2 = 155.902 tf` en cada estribo.

## 4. Carga DW y carga peatonal PL

- Carpeta asfáltica: `w_DW = 4.00 x 0.075 x 2.30 = 0.690 tf/m`; por estribo, `R_DW = 17.250 tf`.
- Peatones: `w_PL = 2.00 x 0.370 = 0.740 tf/m`; por estribo, `R_PL = 18.500 tf`.

PL actúa simultáneamente con la carga vehicular según el Manual de Puentes MTC 2018. No se aplica incremento dinámico a PL.

## 5. Reacción máxima HL-93

Se usa la línea de influencia de reacción del apoyo. Para maximizar el apoyo izquierdo se coloca un eje posterior del camión en el apoyo, el segundo eje posterior a 4.30 m y el eje frontal a 8.60 m. Para el estribo derecho la posición es simétrica.

| Efecto | Reacción (tf) |
|---|---:|
| Camión de diseño con IM | 40.946 |
| Tándem de diseño con IM | 29.802 |
| Carga de carril, sin IM | 23.810 |

Controla el camión. Incluyendo presencia múltiple para un carril:

`R_LL+IM = 1.20 x (40.946 + 23.810) = 77.707 tf` por estribo.

Los máximos de ambos estribos corresponden a posiciones diferentes del vehículo y no son simultáneos.

## 6. Acciones horizontales

### 6.1 Frenado BR

Manual MTC 2018: mayor entre 25% de los pesos por eje del camión o tándem y 5% del vehículo más carga de carril; se incluye presencia múltiple y no se incluye IM.

- 25% del camión, antes de presencia múltiple: 8.165 tf.
- 5% del camión más carril, antes de presencia múltiple: 4.014 tf.
- `BR = 1.20 x 8.165 = 9.798 tf`.

Asignación preliminar: el total se transmite al estribo con apoyo fijo. Se ha supuesto estribo izquierdo fijo y derecho móvil; debe confirmarse con el plano de apoyos. La fuerza vehicular se idealiza a 1.80 m sobre la superficie de rodadura antes de su transferencia al sistema de apoyos.

### 6.2 Viento WS y WL

Con `V_DZ = 75.00 km/h`, presión básica de vigas `P_B = 0.050 ksf` y altura expuesta preliminar de 2.932 m, la carga calculada es 0.157 tf/m. Controla el mínimo normativo de 4.4 kN/m = 0.449 tf/m.

- Viento transversal sobre la estructura: `R_WS = 0.449 x 50 / 2 = 11.217 tf` por estribo.
- Viento transversal sobre vehículos: `R_WL = 3.720 tf` por estribo.
- Viento vertical: `R_WSv = -0.100 x 6.00 x 50 / 2 = -15.000 tf` por estribo; signo negativo = levantamiento.

WS vertical se aplica solamente en los estados límite indicados por MTC y no junto con WL.

### 6.3 Sismo EQ - estimación inicial

Con el coeficiente preliminar usado en la documentación de subestructura, `C = 0.24`, aplicado a la masa permanente `DC + DW`:

`R_EQ = 0.24 x (R_DC + R_DW) = 41.556 tf` por estribo.

Este valor es una comprobación estática preliminar. Para diseño debe sustituirse o contrastarse con las reacciones del análisis espectral del modelo, incluyendo la rigidez real de los apoyos y el criterio de combinación modal.

## 7. Resumen nominal por estribo

| Dirección | Acción | Estribo izquierdo (tf) | Estribo derecho (tf) | Observación |
|---|---|---:|---:|---|
| Vertical | DC | 155.902 | 155.902 | Hacia abajo |
| Vertical | DW | 17.250 | 17.250 | Hacia abajo |
| Vertical | PL | 18.500 | 18.500 | Hacia abajo |
| Vertical | LL+IM | 77.707 | 77.707 | Máximo no simultáneo |
| Vertical | WSv | -15.000 | -15.000 | Levantamiento |
| Longitudinal | BR | 9.798 | 0.000 | Supuesto: izquierdo fijo |
| Transversal | WS | 11.217 | 11.217 | Controla mínimo normativo |
| Transversal | WL | 3.720 | 3.720 | Viento sobre vehículos |
| Horizontal | EQ | 41.556 | 41.556 | Estimación estática C = 0.24 |

La suma nominal `DC + DW + PL + LL+IM = 269.358 tf` por estribo es solo un control de inventario, no una combinación LRFD.

Si las tres líneas de apoyo reciben la misma reacción vertical, los valores por apoyo serían 51.967 tf (DC), 5.750 tf (DW), 6.167 tf (PL) y 25.902 tf (LL+IM). La distribución real debe comprobarse con las reacciones de cada viga del modelo transversal.

## 8. Contradicciones y verificaciones pendientes

1. **Ancho del tablero resuelto.** El registro de verificación confirma 6.00 m: calzada de 4.00 m y dos veredas de 1.00 m. Este valor reemplaza los anchos contradictorios de las memorias originales.
2. **DC frente al expediente.** El metrado actualizado produce `R_DC = 155.902 tf`. El Anexo 3 reporta 163.86 tf (el metrado es 4.86% menor) y el modelo global equivale a 170.321 tf por estribo (el metrado es 8.47% menor). Se debe extraer el desglose de componentes del modelo y del Anexo 3 para conciliar la diferencia.
3. **Frenado.** Para una vía resulta `BR = 9.798 tf`; el Anexo 3 usa 20.05 tf. Ese valor equivale aproximadamente a duplicar la acción de una vía. Confirmar si el proyecto exige dos carriles futuros y, de ser así, revisar el ancho disponible y el factor de presencia múltiple correspondiente.
4. **Geometría de vigas.** La memoria de vigas metálicas menciona separación de 3.20 m, incompatible con los paneles de diafragma de 2.00 m confirmados en el registro. El metrado usa 2.00 m.
5. **Diafragmas y barandas.** Se confirmaron nueve líneas de diafragmas y 0.300 tf/m por baranda. Aun así, conviene contrastar el peso con planos de fabricación y el metrado real de acero.
6. **Apoyos.** Confirmar qué estribo es fijo, la orientación de guías y la rigidez de los neoprenos. Esto controla el reparto longitudinal de BR, viento y sismo.
7. **Sismo.** Reemplazar el método `C x peso` por reacciones espectrales verificadas cuando se disponga de la tabla de reacciones del modelo.

## 9. Fuentes del expediente

- `memoria_estructuras/1_memoria_descriptiva_puente_molino.pdf`
- `memoria_estructuras/2_analisis_diseno_puente_molino.pdf`
- `memoria_estructuras/4 Anexo 2 MEMORIA DE CALCULO ESTRUCTURAL DE VIGAS METALICAS.pdf`
- `memoria_estructuras/7 Anexo 5 DISEÑO DE VIGA DIAFRAGMAS.pdf`
- `memoria_estructuras/8 Anexo 6 DISEÑO DE APOYOS ELASTOMERICO.pdf`
- `memoria_estructuras/11_memoria_seccion_puente.pdf`
- `memoria_estructuras/Anexo_3_Estribo_Izquierdo.pdf`
- `normativa/manual_puentes_MTC_2018.pdf`

## 10. Ejecución

```powershell
python .\metrado_cargas\metrado_tablero.py
```

El cálculo es preliminar y debe ser validado por el ingeniero responsable con los planos finales, la edición contractual de AASHTO/MTC y las reacciones del modelo estructural aprobado.

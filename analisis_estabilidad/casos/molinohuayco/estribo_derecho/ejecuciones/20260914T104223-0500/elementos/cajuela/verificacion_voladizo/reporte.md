# Verificacion de la pared de cajuela en voladizo

## Modelo

- Franja: 1.00 m; altura local: 3.04 m; altura global de empuje: 12.39 m; espesor: 0.40 m.
- Armado evaluado: Ø5/8" @ 230 mm vertical y @ 230 mm horizontal, en ambas caras.
- Escenario complementario en la base: peralte efectivo local d = 1.50 m, sin modificar las demandas del voladizo.
- BR se aplica con brazo de 1.00 m y EQ-super con brazo de 0.70 m, medidos desde el arranque local.
- La compresion axial del puente se cuantifica, pero no se acredita para aumentar la capacidad a flexion.
- Evento Extremo I aplica las dos concurrencias del MTC 2018, Art. 2.8.1.1.14.1; I-A e I-B son etiquetas internas del calculo.
- EQ-super se conserva al 100% en ambas concurrencias mientras no se demuestre una ruta de carga alternativa.

## Demandas

| Caso | Combinacion | V (tf/m) | M base (tf·m/m) | P axial (tf/m) |
|---|---|---:|---:|---:|
| Servicio I | Ea + Es + BR | 3.834 | 4.183 | 44.890 |
| Resistencia I-a | 1.50 Ea + 1.75 Es + 1.75 BR | 6.317 | 6.923 | 53.306 |
| Resistencia I-b | 1.50 Ea + 1.75 Es + 1.75 BR | 6.317 | 6.923 | 64.847 |
| Evento Extremo I-A | 100% PAE + 50% PIR + 100% EQ-super | 11.993 | 11.988 | 25.254 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR + 100% EQ-super [50% PAE] | 9.734 | 8.834 | 25.254 |

Gobierna **Evento Extremo I-A**, con M_u = 11.988 tf·m/m (cara posterior/relleno).

### Casos sísmicos inversos (inercia hacia el relleno)

Para la cara frontal/no relleno también se evalúan I-A e I-B. La componente de terreno permanece hacia el vacío y las inercias PIR + EQ-super actúan hacia el relleno; un momento inverso positivo tracciona la cara frontal.

| Caso | Terreno opuesto | M terreno | M(PIR) | M(EQ-super) | M inverso | V inverso |
|---|---|---:|---:|---:|---:|---:|
| Evento Extremo I-A inverso | 100% PAE | 6.862 | 0.277 | 4.848 | -1.737 | 2.224 |
| Evento Extremo I-B inverso | max(50% PAE, PA) | 3.431 | 0.554 | 4.848 | 1.972 | 4.849 |

## Acero vertical por cara

Cada cara se dimensiona para su demanda de tracción gobernante: la posterior/relleno con el caso directo y la frontal/no relleno con el caso inverso.

| Cara | d (mm) | M demanda (tf·m/m) | Dirección | As calc. | As norm. gobernante | As req. | As disp. | D/C acero | φMn | D/C flexión | Estado |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| frontal/no relleno | 342.1 | 1.972 | inverso (hacia el relleno) | 1.531 cm²/m | 9.540 cm²/m (mín. flexión) | 9.540 cm²/m | 8.606 cm²/m | 1.109 | 10.880 tf·m/m | 0.181 | No cumple |
| posterior/relleno | 317.1 | 11.988 | directo (hacia el vacio) | 10.298 cm²/m | 8.842 cm²/m (mín. flexión) | 10.298 cm²/m | 8.606 cm²/m | 1.197 | 10.067 tf·m/m | 1.191 | No cumple |

### Fisuración bajo Servicio I

| Cara | f_s | Límite de f_s | Separación dispuesta | Separación límite | Estado |
|---|---:|---:|---:|---:|---|
| frontal/no relleno | 154.9 MPa | 247.1 MPa | 230 mm | 522 mm | Cumple |
| posterior/relleno | 167.1 MPa | 247.1 MPa | 230 mm | 368 mm | Cumple |

La fisuración de la sección actual se verifica adicionalmente con el momento de Servicio I; no gobierna el resultado de las dos caras.

## Verificación complementaria en la base con d = 1.50 m

Esta comprobación representa únicamente una sección local engrosada en el arranque. Se mantienen el momento, el cortante y el armado Ø5/8" @ 230 mm de la evaluación principal. El cambio no se extiende a la rigidez del fuste ni modifica la distribución de cargas. La geometría final deberá proporcionar efectivamente d = 1.50 m y permitir el desarrollo y anclaje del refuerzo.

| Control | Demanda o requisito | Capacidad o disposición | D/C | Estado |
|---|---:|---:|---:|---|
| Área por flexión calculada | 2.117 cm²/m | 8.606 cm²/m | 0.246 | Cumple |
| Acero mínimo a flexión adoptado | 41.833 cm²/m | 8.606 cm²/m | 4.861 | No cumple |
| Resistencia a flexión | M_u = 11.988 tf·m/m | φM_n = 48.548 tf·m/m | 0.247 | Cumple |
| Cortante | V_u = 11.993 tf/m | φV_n = 107.771 tf/m | 0.111 | Cumple |

**Resultado de la sección local con d = 1.50 m: NO CUMPLE.** La resistencia a flexión y a cortante es suficiente, pero el cumplimiento global exige además satisfacer el acero mínimo asociado al nuevo peralte.

## Otros controles

| Control | Demanda/requisito | Capacidad/provision | D/C | Estado |
|---|---:|---:|---:|---|
| Acero horizontal por cara | 3.600 cm²/m | 8.606 cm²/m | 0.418 | Cumple |
| Cortante | 11.993 tf/m | 22.991 tf/m | 0.522 | Cumple |
| Compresion axial media | 0.619 MPa | f'c = 27.459 MPa | 0.023 | Informativo |

Con Ø5/8", la separación vertical máxima que satisface la envolvente calculada es **190 mm**. Para el acero horizontal por mínimos, el límite calculado es **400 mm** (además de los límites generales de espaciamiento).

## Resultado

**Estado global: NO CUMPLE.**

El resultado incluye la fuerza sismica de la superestructura indicada por el modelo vigente. Si esa fuerza se transfiere por otro elemento y no por la pared de cajuela, debe documentarse la ruta de carga y volver a ejecutar el script con el caso correspondiente; no debe eliminarse sin sustento.

Pendiente para cierre definitivo: verificar distribucion horizontal/local alrededor de apoyos y juntas con sus posiciones, dimensiones de placas, excentricidades y detalle de anclaje al cuello de la pantalla.

# Verificacion de la pared de cajuela en voladizo

## Modelo

- Franja: 1.00 m; altura local: 3.40 m; altura global de empuje: 14.65 m; espesor: 0.40 m.
- Armado evaluado: Ø5/8" @ 230 mm vertical y @ 230 mm horizontal, en ambas caras.
- Escenario complementario en la base: peralte efectivo local d = 1.50 m, sin modificar las demandas del voladizo.
- La fuerza horizontal del puente se aplica en la mesa de apoyo, a 1.00 m sobre el arranque.
- La compresion axial del puente se cuantifica, pero no se acredita para aumentar la capacidad a flexion.

## Demandas

| Caso | Combinacion | V (tf/m) | M base (tf·m/m) | P axial (tf/m) |
|---|---|---:|---:|---:|
| Servicio I | Ea + Es + BR | 4.304 | 5.060 | 44.890 |
| Resistencia I-a | 1.50 Ea + 1.75 Es + 1.75 BR | 7.039 | 8.298 | 53.306 |
| Resistencia I-b | 1.50 Ea + 1.75 Es + 1.75 BR | 7.039 | 8.298 | 64.847 |
| Evento Extremo I | Ea + Delta Eas trapezoidal + PIR + EQ-super | 13.715 | 17.680 | 25.254 |

Gobierna **Evento Extremo I**, con M_u = 17.680 tf·m/m.

## Acero vertical por cara

| Cara | d (mm) | As calc. | As norm. gobernante | As req. | As disp. | D/C acero | φMn | D/C flexión | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| frontal/no relleno | 342.1 | 14.193 cm²/m | 9.540 cm²/m (mín. flexión) | 14.193 cm²/m | 8.606 cm²/m | 1.649 | 10.880 tf·m/m | 1.625 | No cumple |
| posterior/relleno | 317.1 | 15.413 cm²/m | 8.842 cm²/m (mín. flexión) | 15.413 cm²/m | 8.606 cm²/m | 1.791 | 10.067 tf·m/m | 1.756 | No cumple |

### Fisuración bajo Servicio I

| Cara | f_s | Límite de f_s | Separación dispuesta | Separación límite | Estado |
|---|---:|---:|---:|---:|---|
| frontal/no relleno | 187.3 MPa | 247.1 MPa | 230 mm | 411 mm | Cumple |
| posterior/relleno | 202.1 MPa | 247.1 MPa | 230 mm | 276 mm | Cumple |

La fisuración de la sección actual se verifica adicionalmente con el momento de Servicio I; no gobierna el resultado de las dos caras.

## Verificación complementaria en la base con d = 1.50 m

Esta comprobación representa únicamente una sección local engrosada en el arranque. Se mantienen el momento, el cortante y el armado Ø5/8" @ 230 mm de la evaluación principal. El cambio no se extiende a la rigidez del fuste ni modifica la distribución de cargas. La geometría final deberá proporcionar efectivamente d = 1.50 m y permitir el desarrollo y anclaje del refuerzo.

| Control | Demanda o requisito | Capacidad o disposición | D/C | Estado |
|---|---:|---:|---:|---|
| Área por flexión calculada | 3.124 cm²/m | 8.606 cm²/m | 0.363 | Cumple |
| Acero mínimo a flexión adoptado | 41.833 cm²/m | 8.606 cm²/m | 4.861 | No cumple |
| Resistencia a flexión | M_u = 17.680 tf·m/m | φM_n = 48.548 tf·m/m | 0.364 | Cumple |
| Cortante | V_u = 13.715 tf/m | φV_n = 107.771 tf/m | 0.127 | Cumple |

**Resultado de la sección local con d = 1.50 m: NO CUMPLE.** La resistencia a flexión y a cortante es suficiente, pero el cumplimiento global exige además satisfacer el acero mínimo asociado al nuevo peralte.

## Otros controles

| Control | Demanda/requisito | Capacidad/provision | D/C | Estado |
|---|---:|---:|---:|---|
| Acero horizontal por cara | 3.600 cm²/m | 8.606 cm²/m | 0.418 | Cumple |
| Cortante | 13.715 tf/m | 22.991 tf/m | 0.597 | Cumple |
| Compresion axial media | 0.619 MPa | f'c = 27.459 MPa | 0.023 | Informativo |

Con Ø5/8", la separación vertical máxima que satisface la envolvente calculada es **125 mm**. Para el acero horizontal por mínimos, el límite calculado es **400 mm** (además de los límites generales de espaciamiento).

## Resultado

**Estado global: NO CUMPLE.**

El resultado incluye la fuerza sismica de la superestructura indicada por el modelo vigente. Si esa fuerza se transfiere por otro elemento y no por la pared de cajuela, debe documentarse la ruta de carga y volver a ejecutar el script con el caso correspondiente; no debe eliminarse sin sustento.

Pendiente para cierre definitivo: verificar distribucion horizontal/local alrededor de apoyos y juntas con sus posiciones, dimensiones de placas, excentricidades y detalle de anclaje al cuello de la pantalla.

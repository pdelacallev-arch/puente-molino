# Análisis FEM 2D de contrafuertes centrales trapezoidales

## 1. Objetivo y alcance

Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando únicamente las reacciones nodales transferidas por la pantalla shell 3D. Este documento no dimensiona acero ni verifica resistencias.

## 2. Geometría y modelo

| Parámetro | Valor | Unidad |
|---|---:|---|
| Altura cargada | 10.800 | m |
| Longitud en base | 6.500 | m |
| Longitud en corona | 0.400 | m |
| Espesor | 0.400 | m |
| Divisiones horizontales | 14 | — |

Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración 2×2 y comportamiento lineal elástico no fisurado. El borde basal está empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.

La longitud varía linealmente con la altura:

`L(z) = 6.10 + (1.17 - 6.10) z / 9.80`.

## 3. Acciones transferidas y respuesta

| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CF-C1 | Servicio I | 800.83 kN | 4180.99 kN·m | 1.9503 mm | 1.567 MPa | 1.250 MPa | -2.504 MPa | 2.71e-10 kN | 2.13e-09 kN·m |
| CF-C1 | Resistencia I-a | 1215.79 kN | 6359.90 kN·m | 2.9731 mm | 2.386 MPa | 1.906 MPa | -3.807 MPa | 4.12e-10 kN | 3.24e-09 kN·m |
| CF-C1 | Resistencia I-b | 1215.79 kN | 6359.90 kN·m | 2.9731 mm | 2.386 MPa | 1.906 MPa | -3.807 MPa | 4.12e-10 kN | 3.24e-09 kN·m |
| CF-C1 | Evento Extremo I-A | 978.06 kN | 5056.23 kN·m | 2.3327 mm | 1.885 MPa | 1.507 MPa | -3.039 MPa | 3.26e-10 kN | 2.56e-09 kN·m |
| CF-C1 | Evento Extremo I-B | 776.26 kN | 4031.69 kN·m | 1.8698 mm | 1.507 MPa | 1.203 MPa | -2.419 MPa | 2.59e-10 kN | 2.04e-09 kN·m |
| CF-C2 | Servicio I | 711.52 kN | 3169.80 kN·m | 1.2431 mm | 1.097 MPa | 0.864 MPa | -2.018 MPa | 1.84e-10 kN | 1.45e-09 kN·m |
| CF-C2 | Resistencia I-a | 1079.41 kN | 4821.52 kN·m | 1.8982 mm | 1.671 MPa | 1.314 MPa | -3.067 MPa | 2.82e-10 kN | 2.21e-09 kN·m |
| CF-C2 | Resistencia I-b | 1079.41 kN | 4821.52 kN·m | 1.8982 mm | 1.671 MPa | 1.314 MPa | -3.067 MPa | 2.82e-10 kN | 2.21e-09 kN·m |
| CF-C2 | Evento Extremo I-A | 872.20 kN | 3834.27 kN·m | 1.4739 mm | 1.318 MPa | 1.040 MPa | -2.454 MPa | 2.21e-10 kN | 1.74e-09 kN·m |
| CF-C2 | Evento Extremo I-B | 691.04 kN | 3056.99 kN·m | 1.1863 mm | 1.054 MPa | 0.832 MPa | -1.952 MPa | 1.77e-10 kN | 1.39e-09 kN·m |
| CF-C3 | Servicio I | 800.83 kN | 4180.99 kN·m | 1.9503 mm | 1.567 MPa | 1.250 MPa | -2.504 MPa | 2.71e-10 kN | 2.13e-09 kN·m |
| CF-C3 | Resistencia I-a | 1215.79 kN | 6359.90 kN·m | 2.9731 mm | 2.386 MPa | 1.906 MPa | -3.807 MPa | 4.12e-10 kN | 3.24e-09 kN·m |
| CF-C3 | Resistencia I-b | 1215.79 kN | 6359.90 kN·m | 2.9731 mm | 2.386 MPa | 1.906 MPa | -3.807 MPa | 4.12e-10 kN | 3.24e-09 kN·m |
| CF-C3 | Evento Extremo I-A | 978.06 kN | 5056.23 kN·m | 2.3327 mm | 1.885 MPa | 1.507 MPa | -3.039 MPa | 3.27e-10 kN | 2.57e-09 kN·m |
| CF-C3 | Evento Extremo I-B | 776.26 kN | 4031.69 kN·m | 1.8698 mm | 1.507 MPa | 1.203 MPa | -2.419 MPa | 2.61e-10 kN | 2.05e-09 kN·m |

## 4. Verificaciones del análisis

| Control | Resultado |
|---|---|
| Un solo modelo/factorización | Conforme |
| Tres contrafuertes y 15 soluciones | 3 / 15 |
| Equilibrio | Conforme |
| Simetría CF-C1 / CF-C3 | Conforme |

## 5. Interpretación y límites

- Los picos puntuales de esfuerzo junto a cargas nodales y al empotramiento son dependientes de la malla; por eso se reportan también percentiles P95/P05.
- Las resultantes por cortes horizontales se conservan en el JSON y serán la base del posterior modelo de bielas y tirantes.
- El modelo supone unión monolítica, base rígida y concreto no fisurado. No representa aún la flexibilidad de la zapata ni redistribuye las reacciones hacia la pantalla global.
- El diseño del refuerzo, bielas, nodos, interfaces y anclajes queda expresamente reservado para la siguiente etapa.

# Análisis FEM 2D de contrafuertes centrales trapezoidales

## 1. Objetivo y alcance

Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando únicamente las reacciones nodales transferidas por la pantalla shell 3D. Este documento no dimensiona acero ni verifica resistencias.

## 2. Geometría y modelo

| Parámetro | Valor | Unidad |
|---|---:|---|
| Altura cargada | 8.280 | m |
| Longitud en base | 6.500 | m |
| Longitud en corona | 0.400 | m |
| Espesor | 0.400 | m |
| Divisiones horizontales | 14 | — |

Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración 2×2 y comportamiento lineal elástico no fisurado. El borde basal está empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.

La longitud varía linealmente con la altura:

`L(z) = 6.50 + (0.40 - 6.50) z / 8.28`.

## 3. Acciones transferidas y respuesta

| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CF-C1 | Servicio I | 478.96 kN | 1942.07 kN·m | 0.6335 mm | 0.792 MPa | 0.637 MPa | -1.349 MPa | 1.07e-11 kN | 9.32e-11 kN·m |
| CF-C1 | Resistencia I-a | 728.44 kN | 2959.61 kN·m | 0.9676 mm | 1.208 MPa | 0.972 MPa | -2.054 MPa | 1.63e-11 kN | 1.41e-10 kN·m |
| CF-C1 | Resistencia I-b | 728.44 kN | 2959.61 kN·m | 0.9676 mm | 1.208 MPa | 0.972 MPa | -2.054 MPa | 1.63e-11 kN | 1.41e-10 kN·m |
| CF-C1 | Evento Extremo I-A | 579.73 kN | 2326.78 kN·m | 0.7501 mm | 0.941 MPa | 0.756 MPa | -1.623 MPa | 1.25e-11 kN | 1.09e-10 kN·m |
| CF-C1 | Evento Extremo I-B | 462.07 kN | 1863.55 kN·m | 0.6041 mm | 0.756 MPa | 0.610 MPa | -1.297 MPa | 1.02e-11 kN | 8.80e-11 kN·m |
| CF-C2 | Servicio I | 473.80 kN | 1733.96 kN·m | 0.5105 mm | 0.665 MPa | 0.526 MPa | -1.263 MPa | 8.25e-12 kN | 6.93e-11 kN·m |
| CF-C2 | Resistencia I-a | 720.22 kN | 2642.35 kN·m | 0.7805 mm | 1.015 MPa | 0.803 MPa | -1.923 MPa | 1.24e-11 kN | 1.08e-10 kN·m |
| CF-C2 | Resistencia I-b | 720.22 kN | 2642.35 kN·m | 0.7805 mm | 1.015 MPa | 0.803 MPa | -1.923 MPa | 1.24e-11 kN | 1.08e-10 kN·m |
| CF-C2 | Evento Extremo I-A | 574.99 kN | 2077.93 kN·m | 0.6012 mm | 0.791 MPa | 0.627 MPa | -1.523 MPa | 9.75e-12 kN | 8.41e-11 kN·m |
| CF-C2 | Evento Extremo I-B | 457.73 kN | 1664.06 kN·m | 0.4855 mm | 0.636 MPa | 0.504 MPa | -1.216 MPa | 7.76e-12 kN | 6.71e-11 kN·m |
| CF-C3 | Servicio I | 478.96 kN | 1942.07 kN·m | 0.6335 mm | 0.792 MPa | 0.637 MPa | -1.349 MPa | 1.07e-11 kN | 9.32e-11 kN·m |
| CF-C3 | Resistencia I-a | 728.44 kN | 2959.61 kN·m | 0.9676 mm | 1.208 MPa | 0.972 MPa | -2.054 MPa | 1.64e-11 kN | 1.43e-10 kN·m |
| CF-C3 | Resistencia I-b | 728.44 kN | 2959.61 kN·m | 0.9676 mm | 1.208 MPa | 0.972 MPa | -2.054 MPa | 1.64e-11 kN | 1.43e-10 kN·m |
| CF-C3 | Evento Extremo I-A | 579.73 kN | 2326.78 kN·m | 0.7501 mm | 0.941 MPa | 0.756 MPa | -1.623 MPa | 1.27e-11 kN | 1.08e-10 kN·m |
| CF-C3 | Evento Extremo I-B | 462.07 kN | 1863.55 kN·m | 0.6041 mm | 0.756 MPa | 0.610 MPa | -1.297 MPa | 1.04e-11 kN | 8.94e-11 kN·m |

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

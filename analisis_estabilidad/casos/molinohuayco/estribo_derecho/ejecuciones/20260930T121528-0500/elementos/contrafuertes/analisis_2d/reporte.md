# Análisis FEM 2D de contrafuertes centrales trapezoidales

## 1. Objetivo y alcance

Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando únicamente las reacciones nodales transferidas por la pantalla shell 3D. Este documento no dimensiona acero ni verifica resistencias.

## 2. Geometría y modelo

| Parámetro | Valor | Unidad |
|---|---:|---|
| Altura cargada | 10.110 | m |
| Longitud en base | 6.500 | m |
| Longitud en corona | 0.400 | m |
| Espesor | 0.400 | m |
| Divisiones horizontales | 14 | — |

Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración 2×2 y comportamiento lineal elástico no fisurado. El borde basal está empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.

La longitud varía linealmente con la altura:

`L(z) = 6.50 + (0.40 - 6.50) z / 10.11`.

## 3. Acciones transferidas y respuesta

| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CF-C1 | Servicio I | 703.80 kN | 3451.62 kN·m | 1.4620 mm | 1.314 MPa | 1.053 MPa | -2.121 MPa | 8.94e-11 kN | 3.53e-10 kN·m |
| CF-C1 | Resistencia I-a | 1068.96 kN | 5252.83 kN·m | 2.2298 mm | 2.002 MPa | 1.605 MPa | -3.226 MPa | 1.36e-10 kN | 5.45e-10 kN·m |
| CF-C1 | Resistencia I-b | 1068.96 kN | 5252.83 kN·m | 2.2298 mm | 2.002 MPa | 1.605 MPa | -3.226 MPa | 1.36e-10 kN | 5.45e-10 kN·m |
| CF-C1 | Evento Extremo I-A | 857.66 kN | 4164.57 kN·m | 1.7443 mm | 1.577 MPa | 1.262 MPa | -2.569 MPa | 1.07e-10 kN | 4.24e-10 kN·m |
| CF-C1 | Evento Extremo I-B | 681.41 kN | 3324.33 kN·m | 1.3998 mm | 1.262 MPa | 1.011 MPa | -2.047 MPa | 8.62e-11 kN | 3.41e-10 kN·m |
| CF-C2 | Servicio I | 641.92 kN | 2725.59 kN·m | 0.9888 mm | 0.963 MPa | 0.753 MPa | -1.774 MPa | 6.37e-11 kN | 2.61e-10 kN·m |
| CF-C2 | Resistencia I-a | 974.31 kN | 4147.74 kN·m | 1.5105 mm | 1.467 MPa | 1.148 MPa | -2.697 MPa | 9.78e-11 kN | 3.98e-10 kN·m |
| CF-C2 | Resistencia I-b | 974.31 kN | 4147.74 kN·m | 1.5105 mm | 1.467 MPa | 1.148 MPa | -2.697 MPa | 9.78e-11 kN | 3.98e-10 kN·m |
| CF-C2 | Evento Extremo I-A | 784.95 kN | 3289.26 kN·m | 1.1705 mm | 1.156 MPa | 0.902 MPa | -2.152 MPa | 7.66e-11 kN | 3.11e-10 kN·m |
| CF-C2 | Evento Extremo I-B | 622.63 kN | 2625.36 kN·m | 0.9429 mm | 0.925 MPa | 0.722 MPa | -1.714 MPa | 6.17e-11 kN | 2.54e-10 kN·m |
| CF-C3 | Servicio I | 703.80 kN | 3451.62 kN·m | 1.4620 mm | 1.314 MPa | 1.053 MPa | -2.121 MPa | 8.89e-11 kN | 3.49e-10 kN·m |
| CF-C3 | Resistencia I-a | 1068.96 kN | 5252.83 kN·m | 2.2298 mm | 2.002 MPa | 1.605 MPa | -3.226 MPa | 1.36e-10 kN | 5.41e-10 kN·m |
| CF-C3 | Resistencia I-b | 1068.96 kN | 5252.83 kN·m | 2.2298 mm | 2.002 MPa | 1.605 MPa | -3.226 MPa | 1.36e-10 kN | 5.41e-10 kN·m |
| CF-C3 | Evento Extremo I-A | 857.66 kN | 4164.57 kN·m | 1.7443 mm | 1.577 MPa | 1.262 MPa | -2.569 MPa | 1.07e-10 kN | 4.28e-10 kN·m |
| CF-C3 | Evento Extremo I-B | 681.41 kN | 3324.33 kN·m | 1.3998 mm | 1.262 MPa | 1.011 MPa | -2.047 MPa | 8.56e-11 kN | 3.38e-10 kN·m |

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

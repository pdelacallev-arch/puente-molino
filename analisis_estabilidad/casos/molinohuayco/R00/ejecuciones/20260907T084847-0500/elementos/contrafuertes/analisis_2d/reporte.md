# Análisis FEM 2D de contrafuertes centrales trapezoidales

## 1. Objetivo y alcance

Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando únicamente las reacciones nodales transferidas por la pantalla shell 3D. Este documento no dimensiona acero ni verifica resistencias.

## 2. Geometría y modelo

| Parámetro | Valor | Unidad |
|---|---:|---|
| Altura cargada | 7.850 | m |
| Longitud en base | 6.100 | m |
| Longitud en corona | 0.500 | m |
| Espesor | 0.400 | m |
| Divisiones horizontales | 14 | — |

Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración 2×2 y comportamiento lineal elástico no fisurado. El borde basal está empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.

La longitud varía linealmente con la altura:

`L(z) = 6.10 + (1.17 - 6.10) z / 9.80`.

## 3. Acciones transferidas y respuesta

| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CF-C1 | Servicio I | 570.61 kN | 2275.77 kN·m | 0.7859 mm | 1.048 MPa | 0.843 MPa | -1.740 MPa | 4.89e-11 kN | 6.87e-11 kN·m |
| CF-C1 | Resistencia I-a | 865.19 kN | 3454.57 kN·m | 1.1944 mm | 1.592 MPa | 1.280 MPa | -2.640 MPa | 7.40e-11 kN | 9.87e-11 kN·m |
| CF-C1 | Resistencia I-b | 865.19 kN | 3454.57 kN·m | 1.1944 mm | 1.592 MPa | 1.280 MPa | -2.640 MPa | 7.40e-11 kN | 9.87e-11 kN·m |
| CF-C1 | Evento Extremo I-A | 701.26 kN | 2781.22 kN·m | 0.9549 mm | 1.276 MPa | 1.026 MPa | -2.131 MPa | 5.92e-11 kN | 7.96e-11 kN·m |
| CF-C1 | Evento Extremo I-B | 554.93 kN | 2206.70 kN·m | 0.7597 mm | 1.014 MPa | 0.816 MPa | -1.689 MPa | 4.71e-11 kN | 6.37e-11 kN·m |
| CF-C2 | Servicio I | 571.81 kN | 2094.38 kN·m | 0.6721 mm | 0.918 MPa | 0.728 MPa | -1.664 MPa | 4.35e-11 kN | 6.68e-11 kN·m |
| CF-C2 | Resistencia I-a | 866.77 kN | 3179.13 kN·m | 1.0218 mm | 1.394 MPa | 1.107 MPa | -2.524 MPa | 6.56e-11 kN | 9.87e-11 kN·m |
| CF-C2 | Resistencia I-b | 866.77 kN | 3179.13 kN·m | 1.0218 mm | 1.394 MPa | 1.107 MPa | -2.524 MPa | 6.56e-11 kN | 9.87e-11 kN·m |
| CF-C2 | Evento Extremo I-A | 703.70 kN | 2559.88 kN·m | 0.8148 mm | 1.117 MPa | 0.884 MPa | -2.040 MPa | 5.25e-11 kN | 8.37e-11 kN·m |
| CF-C2 | Evento Extremo I-B | 556.51 kN | 2030.95 kN·m | 0.6489 mm | 0.888 MPa | 0.703 MPa | -1.616 MPa | 4.20e-11 kN | 6.55e-11 kN·m |
| CF-C3 | Servicio I | 570.61 kN | 2275.77 kN·m | 0.7859 mm | 1.048 MPa | 0.843 MPa | -1.740 MPa | 4.84e-11 kN | 6.64e-11 kN·m |
| CF-C3 | Resistencia I-a | 865.19 kN | 3454.57 kN·m | 1.1944 mm | 1.592 MPa | 1.280 MPa | -2.640 MPa | 7.36e-11 kN | 1.00e-10 kN·m |
| CF-C3 | Resistencia I-b | 865.19 kN | 3454.57 kN·m | 1.1944 mm | 1.592 MPa | 1.280 MPa | -2.640 MPa | 7.36e-11 kN | 1.00e-10 kN·m |
| CF-C3 | Evento Extremo I-A | 701.26 kN | 2781.22 kN·m | 0.9549 mm | 1.276 MPa | 1.026 MPa | -2.131 MPa | 5.90e-11 kN | 8.23e-11 kN·m |
| CF-C3 | Evento Extremo I-B | 554.93 kN | 2206.70 kN·m | 0.7597 mm | 1.014 MPa | 0.816 MPa | -1.689 MPa | 4.68e-11 kN | 6.28e-11 kN·m |

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

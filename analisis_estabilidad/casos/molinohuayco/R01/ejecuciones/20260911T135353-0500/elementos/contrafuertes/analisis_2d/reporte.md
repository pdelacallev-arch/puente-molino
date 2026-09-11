# Análisis FEM 2D de contrafuertes centrales trapezoidales

## 1. Objetivo y alcance

Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando únicamente las reacciones nodales transferidas por la pantalla shell 3D. Este documento no dimensiona acero ni verifica resistencias.

## 2. Geometría y modelo

| Parámetro | Valor | Unidad |
|---|---:|---|
| Altura cargada | 7.850 | m |
| Longitud en base | 6.500 | m |
| Longitud en corona | 0.400 | m |
| Espesor | 0.400 | m |
| Divisiones horizontales | 14 | — |

Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración 2×2 y comportamiento lineal elástico no fisurado. El borde basal está empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.

La longitud varía linealmente con la altura:

`L(z) = 6.50 + (0.40 - 6.50) z / 7.85`.

## 3. Acciones transferidas y respuesta

| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CF-C1 | Servicio I | 433.05 kN | 1669.49 kN·m | 0.5122 mm | 0.698 MPa | 0.560 MPa | -1.209 MPa | 6.10e-11 kN | 4.08e-10 kN·m |
| CF-C1 | Resistencia I-a | 658.85 kN | 2545.15 kN·m | 0.7826 mm | 1.065 MPa | 0.854 MPa | -1.841 MPa | 9.32e-11 kN | 6.24e-10 kN·m |
| CF-C1 | Resistencia I-b | 658.85 kN | 2545.15 kN·m | 0.7826 mm | 1.065 MPa | 0.854 MPa | -1.841 MPa | 9.32e-11 kN | 6.24e-10 kN·m |
| CF-C1 | Evento Extremo I-A | 523.20 kN | 1996.45 kN·m | 0.6052 mm | 0.828 MPa | 0.665 MPa | -1.453 MPa | 7.20e-11 kN | 4.83e-10 kN·m |
| CF-C1 | Evento Extremo I-B | 417.37 kN | 1600.42 kN·m | 0.4879 mm | 0.666 MPa | 0.536 MPa | -1.162 MPa | 5.85e-11 kN | 3.91e-10 kN·m |
| CF-C2 | Servicio I | 437.51 kN | 1537.69 kN·m | 0.4311 mm | 0.606 MPa | 0.485 MPa | -1.166 MPa | 5.27e-11 kN | 3.50e-10 kN·m |
| CF-C2 | Resistencia I-a | 665.33 kN | 2344.10 kN·m | 0.6592 mm | 0.925 MPa | 0.740 MPa | -1.775 MPa | 8.03e-11 kN | 5.34e-10 kN·m |
| CF-C2 | Resistencia I-b | 665.33 kN | 2344.10 kN·m | 0.6592 mm | 0.925 MPa | 0.740 MPa | -1.775 MPa | 8.03e-11 kN | 5.34e-10 kN·m |
| CF-C2 | Evento Extremo I-A | 529.87 kN | 1839.31 kN·m | 0.5070 mm | 0.720 MPa | 0.574 MPa | -1.403 MPa | 6.19e-11 kN | 4.12e-10 kN·m |
| CF-C2 | Evento Extremo I-B | 422.21 kN | 1474.27 kN·m | 0.4097 mm | 0.579 MPa | 0.463 MPa | -1.121 MPa | 4.99e-11 kN | 3.32e-10 kN·m |
| CF-C3 | Servicio I | 433.05 kN | 1669.49 kN·m | 0.5122 mm | 0.698 MPa | 0.560 MPa | -1.209 MPa | 6.11e-11 kN | 4.08e-10 kN·m |
| CF-C3 | Resistencia I-a | 658.85 kN | 2545.15 kN·m | 0.7826 mm | 1.065 MPa | 0.854 MPa | -1.841 MPa | 9.30e-11 kN | 6.24e-10 kN·m |
| CF-C3 | Resistencia I-b | 658.85 kN | 2545.15 kN·m | 0.7826 mm | 1.065 MPa | 0.854 MPa | -1.841 MPa | 9.30e-11 kN | 6.24e-10 kN·m |
| CF-C3 | Evento Extremo I-A | 523.20 kN | 1996.45 kN·m | 0.6052 mm | 0.828 MPa | 0.665 MPa | -1.453 MPa | 7.27e-11 kN | 4.87e-10 kN·m |
| CF-C3 | Evento Extremo I-B | 417.37 kN | 1600.42 kN·m | 0.4879 mm | 0.666 MPa | 0.536 MPa | -1.162 MPa | 5.83e-11 kN | 3.91e-10 kN·m |

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

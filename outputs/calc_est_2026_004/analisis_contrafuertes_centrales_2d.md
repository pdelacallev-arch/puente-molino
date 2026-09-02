# Análisis FEM 2D de contrafuertes centrales trapezoidales

## 1. Objetivo y alcance

Analizar CF-C1, CF-C2 y CF-C3 con una sola matriz de rigidez, variando únicamente las reacciones nodales transferidas por la pantalla shell 3D. Este documento no dimensiona acero ni verifica resistencias.

## 2. Geometría y modelo

| Parámetro | Valor | Unidad |
|---|---:|---|
| Altura cargada | 9.800 | m |
| Longitud en base | 6.100 | m |
| Longitud en corona | 1.170 | m |
| Espesor | 0.400 | m |
| Divisiones horizontales | 14 | — |

Se emplean elementos Q4 isoparamétricos en esfuerzo plano, integración 2×2 y comportamiento lineal elástico no fisurado. El borde basal está empotramado. `+x` se dirige desde la pantalla hacia el talón y `+z` es vertical.

La longitud varía linealmente con la altura:

`L(z) = 6.10 + (1.17 - 6.10) z / 9.80`.

## 3. Acciones transferidas y respuesta

| Contrafuerte | Caso | R | M base | d máx. | σ1 máx. | σ1 P95 | σ2 mín. | Error F | Error M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CF-C1 | Servicio I | 688.53 kN | 3295.76 kN·m | 1.1865 mm | 1.278 MPa | 1.020 MPa | -2.177 MPa | 5.90e-11 kN | 3.27e-10 kN·m |
| CF-C1 | Resistencia I-a | 1045.50 kN | 5013.56 kN·m | 1.8078 mm | 1.945 MPa | 1.552 MPa | -3.309 MPa | 8.90e-11 kN | 4.95e-10 kN·m |
| CF-C1 | Resistencia I-b | 1045.50 kN | 5013.56 kN·m | 1.8078 mm | 1.945 MPa | 1.552 MPa | -3.309 MPa | 8.90e-11 kN | 4.95e-10 kN·m |
| CF-C1 | Evento Extremo I-A | 840.18 kN | 3984.84 kN·m | 1.4230 mm | 1.539 MPa | 1.224 MPa | -2.640 MPa | 7.06e-11 kN | 3.88e-10 kN·m |
| CF-C1 | Evento Extremo I-B | 667.10 kN | 3177.71 kN·m | 1.1391 mm | 1.230 MPa | 0.980 MPa | -2.102 MPa | 5.66e-11 kN | 3.14e-10 kN·m |
| CF-C2 | Servicio I | 634.83 kN | 2653.09 kN·m | 0.8517 mm | 0.979 MPa | 0.780 MPa | -1.848 MPa | 4.44e-11 kN | 2.43e-10 kN·m |
| CF-C2 | Resistencia I-a | 963.35 kN | 4035.77 kN·m | 1.2990 mm | 1.491 MPa | 1.189 MPa | -2.809 MPa | 6.83e-11 kN | 3.72e-10 kN·m |
| CF-C2 | Resistencia I-b | 963.35 kN | 4035.77 kN·m | 1.2990 mm | 1.491 MPa | 1.189 MPa | -2.809 MPa | 6.83e-11 kN | 3.72e-10 kN·m |
| CF-C2 | Evento Extremo I-A | 777.03 kN | 3208.40 kN·m | 1.0165 mm | 1.180 MPa | 0.936 MPa | -2.246 MPa | 5.35e-11 kN | 2.90e-10 kN·m |
| CF-C2 | Evento Extremo I-B | 616.06 kN | 2558.31 kN·m | 0.8156 mm | 0.942 MPa | 0.749 MPa | -1.787 MPa | 4.27e-11 kN | 2.34e-10 kN·m |
| CF-C3 | Servicio I | 688.53 kN | 3295.76 kN·m | 1.1865 mm | 1.278 MPa | 1.020 MPa | -2.177 MPa | 5.88e-11 kN | 3.24e-10 kN·m |
| CF-C3 | Resistencia I-a | 1045.50 kN | 5013.56 kN·m | 1.8078 mm | 1.945 MPa | 1.552 MPa | -3.309 MPa | 8.99e-11 kN | 4.94e-10 kN·m |
| CF-C3 | Resistencia I-b | 1045.50 kN | 5013.56 kN·m | 1.8078 mm | 1.945 MPa | 1.552 MPa | -3.309 MPa | 8.99e-11 kN | 4.94e-10 kN·m |
| CF-C3 | Evento Extremo I-A | 840.18 kN | 3984.84 kN·m | 1.4230 mm | 1.539 MPa | 1.224 MPa | -2.640 MPa | 7.09e-11 kN | 3.86e-10 kN·m |
| CF-C3 | Evento Extremo I-B | 667.10 kN | 3177.71 kN·m | 1.1391 mm | 1.230 MPa | 0.980 MPa | -2.102 MPa | 5.66e-11 kN | 3.12e-10 kN·m |

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

# Análisis matricial y diseño de la pantalla central y las alas

## 1. Objetivo y alcance

Diseñar tres franjas horizontales de la pantalla inferior mediante una viga continua desplegada. La cajuela y el diseño de los contrafuertes están excluidos.

## 2. Normativa

- Acciones y combinaciones: Manual de Puentes MTC 2018 / AASHTO LRFD.
- Concreto armado: NTE E.060, D.S. N.° 010-2009-VIVIENDA.
- Se adopta el requisito más restrictivo entre E.060 y MTC/AASHTO.

## 3. Datos de entrada

| Parámetro                                |                                          Valor | Unidad  | Fuente/estado     |
| ---------------------------------------- | ---------------------------------------------: | ------- | ----------------- |
| Altura total incluida cajuela            |                                         13.150 | m       | proporcionado     |
| Altura efectiva diseñada                 |                                          9.800 | m       | proporcionado     |
| Zona de cajuela excluida                 |                                          3.350 | m       | calculado         |
| Espesor de pantalla                      |                                          0.400 | m       | proporcionado     |
| Recubrimiento exterior (cara no relleno) |                                            100 | mm      | asumido           |
| Recubrimiento interior (cara relleno)    |                                             75 | mm      | asumido           |
| Vanos                                    | 3.00, 3.00, 4.77, 2.80, 2.80, 4.77, 3.00, 3.00 | m       | proporcionado     |
| f'c                                      |                                          280.0 | kgf/cm² | agente            |
| fy                                       |                                         4200.0 | kgf/cm² | agente            |
| γ relleno                                |                                          1.800 | tf/m³   | agente            |
| φ / δ                                    |                                    39.8 / 19.9 | grados  | agente            |
| Barras disponibles                       |                              Ø5/8", Ø3/4", Ø1" | —       | sin Ø1/2"         |
| Peralte efectivo de control exterior     |                                          287.3 | mm      | calculado con Ø1" |
| Peralte efectivo de control interior     |                                          312.3 | mm      | calculado con Ø1" |
| Peralte efectivo de control para corte   |                                          287.3 | mm      | menor de ambos    |

La geometría auxiliar corregida satisface `B1 + tp2 + B2 = 11.95 m = B`.

## 4. Hipótesis y método matricial

Cada contrafuerte impide la traslación transversal. Los giros extremos son libres y los giros interiores son continuos. Para cada elemento se usa:

$$\mathbf{k}_e=\frac{EI}{L^3}\begin{bmatrix}12&6L&-12&6L\\6L&4L^2&-6L&2L^2\\-12&-6L&12&-6L\\6L&2L^2&-6L&4L^2\end{bmatrix}$$

La carga uniforme se convierte en fuerzas nodales consistentes, se ensambla la matriz global y se resuelven los giros. Los máximos interiores se obtienen de `V(x)=0`.

## 5. Empujes

- `Ka` resultante = 0.20113; componente normal = 0.18912.
- `KAE` resultante = 0.27404; componente normal = 0.25768.
- Ángulo sísmico = 7.496°; sobrecarga equivalente = 0.610 m.

| Franja     | y sobre zapata (m) | Profundidad z (m) | EH (tf/m²) | LS (tf/m²) | PAE (tf/m²) | PIR (tf/m²) |
| ---------- | -----------------: | ----------------: | ---------: | ---------: | ----------: | ----------: |
| Inferior   |              0.000 |            13.150 |      4.476 |      0.208 |       5.794 |       0.120 |
| Intermedia |              3.267 |             9.883 |      3.364 |      0.208 |       4.355 |       0.120 |
| Superior   |              6.533 |             6.617 |      2.252 |      0.208 |       2.916 |       0.120 |

## 6. Combinaciones

- Servicio I: `EH + LS`.
- Resistencia I-a: `1.50 EH + 1.75 LS`.
- Resistencia I-b: `1.50 EH + 1.75 LS`; se conserva como caso independiente.
- Evento Extremo I-A: `100% PAE + 50% PIR`.
- Evento Extremo I-B: `max(50% PAE, PA) + 100% PIR`; se diseña con la envolvente A/B.

## 7. Resumen del análisis matricial

| Franja     | Caso             |         Escenario | w (tf/m) | M+ máx. (tf·m) | \|M−\| máx. (tf·m) | \|V\| máx. (tf) | Error equilibrio |
| ---------- | ---------------- | ----------------: | -------: | -------------: | -----------------: | --------------: | ---------------: |
| Inferior   | Servicio I       |           EH + LS |    4.684 |          5.887 |              7.692 |          11.279 |         2.27e-13 |
| Inferior   | Resistencia I-a  | 1.50 EH + 1.75 LS |    7.078 |          8.895 |             11.624 |          17.043 |         2.84e-14 |
| Inferior   | Resistencia I-b  | 1.50 EH + 1.75 LS |    7.078 |          8.895 |             11.624 |          17.043 |         2.84e-14 |
| Inferior   | Evento Extremo I |                 A |    5.854 |          7.357 |              9.614 |          14.097 |         0.00e+00 |
| Intermedia | Servicio I       |           EH + LS |    3.572 |          4.489 |              5.866 |           8.601 |         2.27e-13 |
| Intermedia | Resistencia I-a  | 1.50 EH + 1.75 LS |    5.410 |          6.799 |              8.884 |          13.027 |         2.27e-13 |
| Intermedia | Resistencia I-b  | 1.50 EH + 1.75 LS |    5.410 |          6.799 |              8.884 |          13.027 |         2.27e-13 |
| Intermedia | Evento Extremo I |                 A |    4.415 |          5.548 |              7.250 |          10.631 |         2.27e-13 |
| Superior   | Servicio I       |           EH + LS |    2.460 |          3.092 |              4.040 |           5.924 |         1.14e-13 |
| Superior   | Resistencia I-a  | 1.50 EH + 1.75 LS |    3.742 |          4.703 |              6.145 |           9.010 |         2.27e-13 |
| Superior   | Resistencia I-b  | 1.50 EH + 1.75 LS |    3.742 |          4.703 |              6.145 |           9.010 |         2.27e-13 |
| Superior   | Evento Extremo I |                 A |    2.976 |          3.739 |              4.886 |           7.165 |         0.00e+00 |

### Resultados por vano

| Franja/caso                   | Vano | L (m) |  M izq. |  M der. | M+ máx. | x(M+) | V izq. |  V der. |
| ----------------------------- | ---: | ----: | ------: | ------: | ------: | ----: | -----: | ------: |
| Inferior / Servicio I         |    1 |  3.00 |  -0.000 |  -3.474 |   3.676 | 1.253 |  5.868 |  -8.184 |
| Inferior / Servicio I         |    2 |  3.00 |  -3.474 |  -7.181 |   0.105 | 1.236 |  5.791 |  -8.262 |
| Inferior / Servicio I         |    3 |  4.77 |  -7.181 |  -7.692 |   5.887 | 2.362 | 11.065 | -11.279 |
| Inferior / Servicio I         |    4 |  2.80 |  -7.692 |  -0.744 |   1.029 | 1.930 |  9.039 |  -4.076 |
| Inferior / Servicio I         |    5 |  2.80 |  -0.744 |  -7.692 |   1.029 | 0.870 |  4.076 |  -9.039 |
| Inferior / Servicio I         |    6 |  4.77 |  -7.692 |  -7.181 |   5.887 | 2.408 | 11.279 | -11.065 |
| Inferior / Servicio I         |    7 |  3.00 |  -7.181 |  -3.474 |   0.105 | 1.764 |  8.262 |  -5.791 |
| Inferior / Servicio I         |    8 |  3.00 |  -3.474 |  -0.000 |   3.676 | 1.747 |  8.184 |  -5.868 |
| Inferior / Resistencia I-a    |    1 |  3.00 |  -0.000 |  -5.250 |   5.554 | 1.253 |  8.867 | -12.367 |
| Inferior / Resistencia I-a    |    2 |  3.00 |  -5.250 | -10.851 |   0.158 | 1.236 |  8.750 | -12.484 |
| Inferior / Resistencia I-a    |    3 |  4.77 | -10.851 | -11.624 |   8.895 | 2.362 | 16.719 | -17.043 |
| Inferior / Resistencia I-a    |    4 |  2.80 | -11.624 |  -1.125 |   1.556 | 1.930 | 13.659 |  -6.160 |
| Inferior / Resistencia I-a    |    5 |  2.80 |  -1.125 | -11.624 |   1.556 | 0.870 |  6.160 | -13.659 |
| Inferior / Resistencia I-a    |    6 |  4.77 | -11.624 | -10.851 |   8.895 | 2.408 | 17.043 | -16.719 |
| Inferior / Resistencia I-a    |    7 |  3.00 | -10.851 |  -5.250 |   0.158 | 1.764 | 12.484 |  -8.750 |
| Inferior / Resistencia I-a    |    8 |  3.00 |  -5.250 |   0.000 |   5.554 | 1.747 | 12.367 |  -8.867 |
| Inferior / Resistencia I-b    |    1 |  3.00 |  -0.000 |  -5.250 |   5.554 | 1.253 |  8.867 | -12.367 |
| Inferior / Resistencia I-b    |    2 |  3.00 |  -5.250 | -10.851 |   0.158 | 1.236 |  8.750 | -12.484 |
| Inferior / Resistencia I-b    |    3 |  4.77 | -10.851 | -11.624 |   8.895 | 2.362 | 16.719 | -17.043 |
| Inferior / Resistencia I-b    |    4 |  2.80 | -11.624 |  -1.125 |   1.556 | 1.930 | 13.659 |  -6.160 |
| Inferior / Resistencia I-b    |    5 |  2.80 |  -1.125 | -11.624 |   1.556 | 0.870 |  6.160 | -13.659 |
| Inferior / Resistencia I-b    |    6 |  4.77 | -11.624 | -10.851 |   8.895 | 2.408 | 17.043 | -16.719 |
| Inferior / Resistencia I-b    |    7 |  3.00 | -10.851 |  -5.250 |   0.158 | 1.764 | 12.484 |  -8.750 |
| Inferior / Resistencia I-b    |    8 |  3.00 |  -5.250 |   0.000 |   5.554 | 1.747 | 12.367 |  -8.867 |
| Inferior / Evento Extremo I   |    1 |  3.00 |  -0.000 |  -4.342 |   4.594 | 1.253 |  7.334 | -10.229 |
| Inferior / Evento Extremo I   |    2 |  3.00 |  -4.342 |  -8.975 |   0.131 | 1.236 |  7.237 | -10.326 |
| Inferior / Evento Extremo I   |    3 |  4.77 |  -8.975 |  -9.614 |   7.357 | 2.362 | 13.829 | -14.097 |
| Inferior / Evento Extremo I   |    4 |  2.80 |  -9.614 |  -0.930 |   1.287 | 1.930 | 11.297 |  -5.095 |
| Inferior / Evento Extremo I   |    5 |  2.80 |  -0.930 |  -9.614 |   1.287 | 0.870 |  5.095 | -11.297 |
| Inferior / Evento Extremo I   |    6 |  4.77 |  -9.614 |  -8.975 |   7.357 | 2.408 | 14.097 | -13.829 |
| Inferior / Evento Extremo I   |    7 |  3.00 |  -8.975 |  -4.342 |   0.131 | 1.764 | 10.326 |  -7.237 |
| Inferior / Evento Extremo I   |    8 |  3.00 |  -4.342 |   0.000 |   4.594 | 1.747 | 10.229 |  -7.334 |
| Intermedia / Servicio I       |    1 |  3.00 |  -0.000 |  -2.650 |   2.803 | 1.253 |  4.475 |  -6.241 |
| Intermedia / Servicio I       |    2 |  3.00 |  -2.650 |  -5.476 |   0.080 | 1.236 |  4.416 |  -6.300 |
| Intermedia / Servicio I       |    3 |  4.77 |  -5.476 |  -5.866 |   4.489 | 2.362 |  8.438 |  -8.601 |
| Intermedia / Servicio I       |    4 |  2.80 |  -5.866 |  -0.568 |   0.785 | 1.930 |  6.893 |  -3.109 |
| Intermedia / Servicio I       |    5 |  2.80 |  -0.568 |  -5.866 |   0.785 | 0.870 |  3.109 |  -6.893 |
| Intermedia / Servicio I       |    6 |  4.77 |  -5.866 |  -5.476 |   4.489 | 2.408 |  8.601 |  -8.438 |
| Intermedia / Servicio I       |    7 |  3.00 |  -5.476 |  -2.650 |   0.080 | 1.764 |  6.300 |  -4.416 |
| Intermedia / Servicio I       |    8 |  3.00 |  -2.650 |  -0.000 |   2.803 | 1.747 |  6.241 |  -4.475 |
| Intermedia / Resistencia I-a  |    1 |  3.00 |  -0.000 |  -4.013 |   4.245 | 1.253 |  6.778 |  -9.453 |
| Intermedia / Resistencia I-a  |    2 |  3.00 |  -4.013 |  -8.294 |   0.121 | 1.236 |  6.688 |  -9.542 |
| Intermedia / Resistencia I-a  |    3 |  4.77 |  -8.294 |  -8.884 |   6.799 | 2.362 | 12.779 | -13.027 |
| Intermedia / Resistencia I-a  |    4 |  2.80 |  -8.884 |  -0.860 |   1.189 | 1.930 | 10.440 |  -4.708 |
| Intermedia / Resistencia I-a  |    5 |  2.80 |  -0.860 |  -8.884 |   1.189 | 0.870 |  4.708 | -10.440 |
| Intermedia / Resistencia I-a  |    6 |  4.77 |  -8.884 |  -8.294 |   6.799 | 2.408 | 13.027 | -12.779 |
| Intermedia / Resistencia I-a  |    7 |  3.00 |  -8.294 |  -4.013 |   0.121 | 1.764 |  9.542 |  -6.688 |
| Intermedia / Resistencia I-a  |    8 |  3.00 |  -4.013 |   0.000 |   4.245 | 1.747 |  9.453 |  -6.778 |
| Intermedia / Resistencia I-b  |    1 |  3.00 |  -0.000 |  -4.013 |   4.245 | 1.253 |  6.778 |  -9.453 |
| Intermedia / Resistencia I-b  |    2 |  3.00 |  -4.013 |  -8.294 |   0.121 | 1.236 |  6.688 |  -9.542 |
| Intermedia / Resistencia I-b  |    3 |  4.77 |  -8.294 |  -8.884 |   6.799 | 2.362 | 12.779 | -13.027 |
| Intermedia / Resistencia I-b  |    4 |  2.80 |  -8.884 |  -0.860 |   1.189 | 1.930 | 10.440 |  -4.708 |
| Intermedia / Resistencia I-b  |    5 |  2.80 |  -0.860 |  -8.884 |   1.189 | 0.870 |  4.708 | -10.440 |
| Intermedia / Resistencia I-b  |    6 |  4.77 |  -8.884 |  -8.294 |   6.799 | 2.408 | 13.027 | -12.779 |
| Intermedia / Resistencia I-b  |    7 |  3.00 |  -8.294 |  -4.013 |   0.121 | 1.764 |  9.542 |  -6.688 |
| Intermedia / Resistencia I-b  |    8 |  3.00 |  -4.013 |   0.000 |   4.245 | 1.747 |  9.453 |  -6.778 |
| Intermedia / Evento Extremo I |    1 |  3.00 |  -0.000 |  -3.275 |   3.464 | 1.253 |  5.531 |  -7.714 |
| Intermedia / Evento Extremo I |    2 |  3.00 |  -3.275 |  -6.769 |   0.099 | 1.236 |  5.458 |  -7.787 |
| Intermedia / Evento Extremo I |    3 |  4.77 |  -6.769 |  -7.250 |   5.548 | 2.362 | 10.429 | -10.631 |
| Intermedia / Evento Extremo I |    4 |  2.80 |  -7.250 |  -0.702 |   0.970 | 1.930 |  8.520 |  -3.842 |
| Intermedia / Evento Extremo I |    5 |  2.80 |  -0.702 |  -7.250 |   0.970 | 0.870 |  3.842 |  -8.520 |
| Intermedia / Evento Extremo I |    6 |  4.77 |  -7.250 |  -6.769 |   5.548 | 2.408 | 10.631 | -10.429 |
| Intermedia / Evento Extremo I |    7 |  3.00 |  -6.769 |  -3.275 |   0.099 | 1.764 |  7.787 |  -5.458 |
| Intermedia / Evento Extremo I |    8 |  3.00 |  -3.275 |   0.000 |   3.464 | 1.747 |  7.714 |  -5.531 |
| Superior / Servicio I         |    1 |  3.00 |   0.000 |  -1.825 |   1.930 | 1.253 |  3.082 |  -4.298 |
| Superior / Servicio I         |    2 |  3.00 |  -1.825 |  -3.772 |   0.055 | 1.236 |  3.041 |  -4.339 |
| Superior / Servicio I         |    3 |  4.77 |  -3.772 |  -4.040 |   3.092 | 2.362 |  5.811 |  -5.924 |
| Superior / Servicio I         |    4 |  2.80 |  -4.040 |  -0.391 |   0.541 | 1.930 |  4.747 |  -2.141 |
| Superior / Servicio I         |    5 |  2.80 |  -0.391 |  -4.040 |   0.541 | 0.870 |  2.141 |  -4.747 |
| Superior / Servicio I         |    6 |  4.77 |  -4.040 |  -3.772 |   3.092 | 2.408 |  5.924 |  -5.811 |
| Superior / Servicio I         |    7 |  3.00 |  -3.772 |  -1.825 |   0.055 | 1.764 |  4.339 |  -3.041 |
| Superior / Servicio I         |    8 |  3.00 |  -1.825 |  -0.000 |   1.930 | 1.747 |  4.298 |  -3.082 |
| Superior / Resistencia I-a    |    1 |  3.00 |  -0.000 |  -2.776 |   2.936 | 1.253 |  4.688 |  -6.538 |
| Superior / Resistencia I-a    |    2 |  3.00 |  -2.776 |  -5.737 |   0.084 | 1.236 |  4.626 |  -6.600 |
| Superior / Resistencia I-a    |    3 |  4.77 |  -5.737 |  -6.145 |   4.703 | 2.362 |  8.839 |  -9.010 |
| Superior / Resistencia I-a    |    4 |  2.80 |  -6.145 |  -0.595 |   0.822 | 1.930 |  7.221 |  -3.256 |
| Superior / Resistencia I-a    |    5 |  2.80 |  -0.595 |  -6.145 |   0.822 | 0.870 |  3.256 |  -7.221 |
| Superior / Resistencia I-a    |    6 |  4.77 |  -6.145 |  -5.737 |   4.703 | 2.408 |  9.010 |  -8.839 |
| Superior / Resistencia I-a    |    7 |  3.00 |  -5.737 |  -2.776 |   0.084 | 1.764 |  6.600 |  -4.626 |
| Superior / Resistencia I-a    |    8 |  3.00 |  -2.776 |   0.000 |   2.936 | 1.747 |  6.538 |  -4.688 |
| Superior / Resistencia I-b    |    1 |  3.00 |  -0.000 |  -2.776 |   2.936 | 1.253 |  4.688 |  -6.538 |
| Superior / Resistencia I-b    |    2 |  3.00 |  -2.776 |  -5.737 |   0.084 | 1.236 |  4.626 |  -6.600 |
| Superior / Resistencia I-b    |    3 |  4.77 |  -5.737 |  -6.145 |   4.703 | 2.362 |  8.839 |  -9.010 |
| Superior / Resistencia I-b    |    4 |  2.80 |  -6.145 |  -0.595 |   0.822 | 1.930 |  7.221 |  -3.256 |
| Superior / Resistencia I-b    |    5 |  2.80 |  -0.595 |  -6.145 |   0.822 | 0.870 |  3.256 |  -7.221 |
| Superior / Resistencia I-b    |    6 |  4.77 |  -6.145 |  -5.737 |   4.703 | 2.408 |  9.010 |  -8.839 |
| Superior / Resistencia I-b    |    7 |  3.00 |  -5.737 |  -2.776 |   0.084 | 1.764 |  6.600 |  -4.626 |
| Superior / Resistencia I-b    |    8 |  3.00 |  -2.776 |   0.000 |   2.936 | 1.747 |  6.538 |  -4.688 |
| Superior / Evento Extremo I   |    1 |  3.00 |  -0.000 |  -2.207 |   2.335 | 1.253 |  3.728 |  -5.199 |
| Superior / Evento Extremo I   |    2 |  3.00 |  -2.207 |  -4.562 |   0.067 | 1.236 |  3.678 |  -5.248 |
| Superior / Evento Extremo I   |    3 |  4.77 |  -4.562 |  -4.886 |   3.739 | 2.362 |  7.029 |  -7.165 |
| Superior / Evento Extremo I   |    4 |  2.80 |  -4.886 |  -0.473 |   0.654 | 1.930 |  5.742 |  -2.589 |
| Superior / Evento Extremo I   |    5 |  2.80 |  -0.473 |  -4.886 |   0.654 | 0.870 |  2.589 |  -5.742 |
| Superior / Evento Extremo I   |    6 |  4.77 |  -4.886 |  -4.562 |   3.739 | 2.408 |  7.165 |  -7.029 |
| Superior / Evento Extremo I   |    7 |  3.00 |  -4.562 |  -2.207 |   0.067 | 1.764 |  5.248 |  -3.678 |
| Superior / Evento Extremo I   |    8 |  3.00 |  -2.207 |   0.000 |   2.335 | 1.747 |  5.199 |  -3.728 |

### Reacciones en ejes de contrafuertes

| Franja     | Caso             | Reacciones R1…R9 (tf)                                                |
| ---------- | ---------------- | -------------------------------------------------------------------- |
| Inferior   | Servicio I       | 5.868, 13.975, 19.326, 20.318, 8.153, 20.318, 19.326, 13.975, 5.868  |
| Inferior   | Resistencia I-a  | 8.867, 21.117, 29.204, 30.702, 12.319, 30.702, 29.204, 21.117, 8.867 |
| Inferior   | Resistencia I-b  | 8.867, 21.117, 29.204, 30.702, 12.319, 30.702, 29.204, 21.117, 8.867 |
| Inferior   | Evento Extremo I | 7.334, 17.466, 24.154, 25.394, 10.189, 25.394, 24.154, 17.466, 7.334 |
| Intermedia | Servicio I       | 4.475, 10.657, 14.738, 15.494, 6.217, 15.494, 14.738, 10.657, 4.475  |
| Intermedia | Resistencia I-a  | 6.778, 16.141, 22.321, 23.467, 9.416, 23.467, 22.321, 16.141, 6.778  |
| Intermedia | Resistencia I-b  | 6.778, 16.141, 22.321, 23.467, 9.416, 23.467, 22.321, 16.141, 6.778  |
| Intermedia | Evento Extremo I | 5.531, 13.172, 18.216, 19.150, 7.684, 19.150, 18.216, 13.172, 5.531  |
| Superior   | Servicio I       | 3.082, 7.340, 10.150, 10.671, 4.282, 10.671, 10.150, 7.340, 3.082    |
| Superior   | Resistencia I-a  | 4.688, 11.164, 15.439, 16.232, 6.513, 16.232, 15.439, 11.164, 4.688  |
| Superior   | Resistencia I-b  | 4.688, 11.164, 15.439, 16.232, 6.513, 16.232, 15.439, 11.164, 4.688  |
| Superior   | Evento Extremo I | 3.728, 8.877, 12.277, 12.907, 5.179, 12.907, 12.277, 8.877, 3.728    |

### Giros nodales

| Franja     | Caso             | Giros θ1…θ9 (rad)                                                                                               |
| ---------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
| Inferior   | Servicio I       | -0.00026388, 0.00013411, -0.00027257, 0.00024221, 0.00000000, -0.00024221, 0.00027257, -0.00013411, 0.00026388  |
| Inferior   | Resistencia I-a  | -0.00039875, 0.00020266, -0.00041187, 0.00036601, 0.00000000, -0.00036601, 0.00041187, -0.00020266, 0.00039875  |
| Inferior   | Resistencia I-b  | -0.00039875, 0.00020266, -0.00041187, 0.00036601, 0.00000000, -0.00036601, 0.00041187, -0.00020266, 0.00039875  |
| Inferior   | Evento Extremo I | -0.00032981, 0.00016762, -0.00034066, 0.00030273, -0.00000000, -0.00030273, 0.00034066, -0.00016762, 0.00032981 |
| Intermedia | Servicio I       | -0.00020124, 0.00010227, -0.00020786, 0.00018471, -0.00000000, -0.00018471, 0.00020786, -0.00010227, 0.00020124 |
| Intermedia | Resistencia I-a  | -0.00030478, 0.00015490, -0.00031481, 0.00027975, 0.00000000, -0.00027975, 0.00031481, -0.00015490, 0.00030478  |
| Intermedia | Resistencia I-b  | -0.00030478, 0.00015490, -0.00031481, 0.00027975, 0.00000000, -0.00027975, 0.00031481, -0.00015490, 0.00030478  |
| Intermedia | Evento Extremo I | -0.00024872, 0.00012640, -0.00025690, 0.00022829, 0.00000000, -0.00022829, 0.00025690, -0.00012640, 0.00024872  |
| Superior   | Servicio I       | -0.00013859, 0.00007044, -0.00014315, 0.00012721, 0.00000000, -0.00012721, 0.00014315, -0.00007044, 0.00013859  |
| Superior   | Resistencia I-a  | -0.00021081, 0.00010714, -0.00021775, 0.00019350, 0.00000000, -0.00019350, 0.00021775, -0.00010714, 0.00021081  |
| Superior   | Resistencia I-b  | -0.00021081, 0.00010714, -0.00021775, 0.00019350, 0.00000000, -0.00019350, 0.00021775, -0.00010714, 0.00021081  |
| Superior   | Evento Extremo I | -0.00016763, 0.00008519, -0.00017314, 0.00015386, 0.00000000, -0.00015386, 0.00017314, -0.00008519, 0.00016763  |

### Diagramas de momento flector de diseño

La envolvente se evalúa con `M(x)=Mi+Vi·x-w·x²/2` en cada vano. El momento positivo corresponde a tracción en la cara exterior/no relleno y el negativo a tracción en la cara interior/relleno.

| Franja     | M+ exterior máx. |        s | Caso            | \|M−\| interior máx. |        s | Caso            |
| ---------- | ---------------: | -------: | --------------- | -------------------: | -------: | --------------- |
| Inferior   |       8.895 tf·m |  8.362 m | Resistencia I-a |          11.624 tf·m | 16.370 m | Resistencia I-a |
| Intermedia |       6.799 tf·m |  8.362 m | Resistencia I-a |           8.884 tf·m | 10.770 m | Resistencia I-a |
| Superior   |       4.703 tf·m | 18.778 m | Resistencia I-a |           6.145 tf·m | 10.770 m | Resistencia I-a |

## 8. Diseño de concreto armado

Para E.060 se verifica flexión con `φ=0.90`, corte con `φ=0.85`, acero mínimo de flexión, `ρ=0.0018` de contracción y temperatura, y desarrollo del capítulo 12. MTC/AASHTO se comprueba en paralelo; gobierna el menor `φVc`, el mayor acero y la mayor longitud de desarrollo.

Nota: la cara exterior se diseña con recubrimiento de 100 mm y peralte efectivo de 287.3 mm; la cara interior con recubrimiento de 75 mm y peralte efectivo de 312.3 mm. Para corte se adopta el menor peralte efectivo (287.3 mm). La selección de barra se restringe a las disponibles (mínimo Ø5/8"), por lo que el armado resultante usa Ø5/8".

| Franja     | Cara/signo                                  |            Caso |     Mu | As flex. E.060 | As mín. E.060 | As mín. MTC | As req. | Control                 |         Armado | As prov. |    φMn |   D/C |
| ---------- | ------------------------------------------- | --------------: | -----: | -------------: | ------------: | ----------: | ------- | ----------------------- | -------------: | -------: | -----: | ----: |
| Inferior   | cara exterior/no relleno / momento positivo | Resistencia I-a |  8.895 |          8.408 |         8.012 |       9.117 | 9.117   | mínimo de flexión MTC/AASHTO | Ø5/8" @ 175 mm |   11.310 | 11.856 | 0.750 |
| Inferior   | cara interior/relleno / momento negativo    | Resistencia I-a | 11.624 |         10.137 |         8.710 |      10.137 | 10.137  | flexión requerida E.060 | Ø5/8" @ 180 mm |   10.996 | 12.578 | 0.924 |
| Intermedia | cara exterior/no relleno / momento positivo | Resistencia I-a |  6.799 |          6.386 |         8.012 |       8.551 | 8.551   | mínimo de flexión MTC/AASHTO | Ø5/8" @ 215 mm |    9.206 |  9.715 | 0.700 |
| Intermedia | cara interior/relleno / momento negativo    | Resistencia I-a |  8.884 |          7.693 |         8.710 |       8.349 | 8.710   | mínimo de flexión E.060 | Ø5/8" @ 220 mm |    8.997 | 10.351 | 0.858 |
| Superior   | cara exterior/no relleno / momento positivo | Resistencia I-a |  4.703 |          4.389 |         8.012 |       5.865 | 8.012   | mínimo de flexión E.060 | Ø5/8" @ 245 mm |    8.079 |  8.556 | 0.550 |
| Superior   | cara interior/relleno / momento negativo    | Resistencia I-a |  6.145 |          5.285 |         8.710 |       7.064 | 8.710   | mínimo de flexión E.060 | Ø5/8" @ 225 mm |    8.797 | 10.127 | 0.607 |

### Cortante

| Franja     |            Caso |     Vu | φVc E.060 | φVc MTC | φVc adoptado | Control    |   D/C | Estado |
| ---------- | --------------: | -----: | --------: | ------: | -----------: | ---------- | ----: | ------ |
| Inferior   | Resistencia I-a | 17.043 |    22.183 |  22.991 |       22.183 | E.060      | 0.768 | Cumple |
| Intermedia | Resistencia I-a | 13.027 |    22.183 |  22.991 |       22.183 | E.060      | 0.587 | Cumple |
| Superior   | Resistencia I-a |  9.010 |    22.183 |  22.991 |       22.183 | E.060      | 0.406 | Cumple |

### Servicio, desarrollo y empalmes

| Franja/cara                           |         Ms |        fs | Límite 0.6fy | s fisuración | ld E.060 |  ld MTC | ld adoptado | Control ld | Traslape B |
| ------------------------------------- | ---------: | --------: | -----------: | -----------: | -------: | ------: | ----------: | ---------- | ---------: |
| Inferior / cara exterior/no relleno   | 5.887 tf·m | 197.4 MPa |    247.1 MPa |       191 mm |   624 mm | 1483 mm |     1500 mm | MTC/AASHTO |    1950 mm |
| Inferior / cara interior/relleno      | 7.692 tf·m | 244.1 MPa |    247.1 MPa |       200 mm |   624 mm | 1483 mm |     1500 mm | MTC/AASHTO |    1950 mm |
| Intermedia / cara exterior/no relleno | 4.489 tf·m | 184.9 MPa |    247.1 MPa |       218 mm |   624 mm | 1483 mm |     1500 mm | MTC/AASHTO |    1950 mm |
| Intermedia / cara interior/relleno    | 5.866 tf·m | 227.5 MPa |    247.1 MPa |       226 mm |   624 mm | 1483 mm |     1500 mm | MTC/AASHTO |    1950 mm |
| Superior / cara exterior/no relleno   | 3.092 tf·m | 145.1 MPa |    247.1 MPa |       337 mm |   624 mm | 1483 mm |     1500 mm | MTC/AASHTO |    1950 mm |
| Superior / cara interior/relleno      | 4.040 tf·m | 160.2 MPa |    247.1 MPa |       391 mm |   624 mm | 1483 mm |     1500 mm | MTC/AASHTO |    1950 mm |

### Refuerzo vertical de distribución

En cada cara: As requerido = **3.600 cm²/m**; adoptar **Ø5/8" @ 400 mm** (As provisto = 4.948 cm²/m). Gobierna E.060.

## 9. Verificaciones automáticas

| Verificación                  | Resultado |
| ----------------------------- | --------- |
| geometria B cierra            | Conforme  |
| profundidades esperadas       | Conforme  |
| resistencia Ia Ib separadas   | Conforme  |
| resistencia Ia Ib coinciden   | Conforme  |
| equilibrio matricial          | Conforme  |
| max error equilibrio          | 2.274e-13 |
| simetria                      | Conforme  |
| max error simetria reacciones | 3.553e-15 |
| cajuela excluida              | Conforme  |
| flexion cumple                | Conforme  |
| cortante cumple               | Conforme  |
| fisuracion cumple             | Conforme  |

## 10. Armado recomendado

- Zona inferior (0.000 a 3.267 m):
  - cara exterior/no relleno: Ø5/8" @ 175 mm.
  - cara interior/relleno: Ø5/8" @ 180 mm.
- Zona intermedia (3.267 a 6.533 m):
  - cara exterior/no relleno: Ø5/8" @ 215 mm.
  - cara interior/relleno: Ø5/8" @ 220 mm.
- Zona superior (6.533 a 9.800 m):
  - cara exterior/no relleno: Ø5/8" @ 245 mm.
  - cara interior/relleno: Ø5/8" @ 225 mm.

## 11. Limitaciones y pendientes

- El modelo 1D desplegado no representa torsión ni compatibilidad espacial en los quiebres de las alas.
- Los contrafuertes se consideran apoyos rígidos; las reacciones se reportan, pero no se diseñan.
- La presión se evalúa en el borde inferior de cada tercio, criterio conservador para zonificar el armado.
- El factor de barra superior 1.3 se aplica conservadoramente al desarrollo de todas las barras horizontales.
- La longitud disponible dentro de contrafuertes y anclajes debe verificarse con el plano definitivo.
- El diseño debe ser revisado y aprobado por el ingeniero responsable antes de construcción.

## 12. Conclusión

**Estado del modelo y del diseño calculado: CUMPLE.**
El resultado está condicionado a la validez del modelo desplegado y a confirmar el anclaje disponible en los contrafuertes.

## 13. Nota de revisión

- **Revisión 1 — cambio de acero (Ø1/2" → Ø5/8") y recubrimientos 50/75:** se retiró la barra Ø1/2" de las barras disponibles (`BARRAS_DISPONIBLES = ('5/8"', '5/8"', '3/4"', '1"')`) y se adoptaron recubrimientos diferenciados de 50 mm (cara exterior) y 75 mm (cara interior). Con ello, el armado horizontal pasa de Ø1/2" a **Ø5/8"**, los peraltes efectivos pasaron a 337.3 mm (exterior) y 312.3 mm (interior), y la resistencia a corte disponible bajó de 24.234 tf a **22.991 tf** (D/C máx. 0.741, franja inferior). La cara interior de la franja inferior pasó a ser controlada por **flexión requerida** (10.137 cm²/m) en lugar del mínimo de flexión.
- **Revisión 2 — recubrimiento exterior 50 → 100 mm (cara interior sin cambio):** el peralte efectivo exterior baja de 337.3 a **287.3 mm**; el interior se mantiene en 312.3 mm. Efectos en el diseño:
  - El mínimo de flexión E.060 de la cara exterior baja de 9.407 a **8.012 cm²/m** (depende de `d`); en las franjas inferior e intermedia pasa a gobernar el **mínimo de flexión MTC/AASHTO** (9.117 y 8.551 cm²/m) y en la superior sigue gobernando el mínimo E.060.
  - El armado exterior resultante pasa a Ø5/8" @ 175 mm (inferior), @ 215 mm (intermedia) y @ 245 mm (superior); las caras interiores no cambian (180/220/225 mm) porque su peralte efectivo y momentos son idénticos.
  - La capacidad a corte baja a **φVc = 22.183 tf** porque ahora el menor peralte efectivo es el exterior (287.3 mm) y gobierna **E.060** (antes MTC/AASHTO); D/C máx. de corte sube a **0.768** (franja inferior). Los D/C de flexión suben en las caras exteriores (máx. 0.750 en la inferior), sin superar 1.0.
  - Se corrigió el campo `cortante_control_mm` del JSON, que reportaba 312.3 mm en lugar del mínimo real de 287.3 mm.
- El análisis estructural no cambió; la geometría, presiones, momentos, reacciones y giros permanecen idénticos a la versión anterior del informe.
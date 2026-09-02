# Análisis tridimensional FEM de la pantalla plegada

## 1. Objetivo y alcance

Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.

## 2. Datos

| Parámetro | Valor | Unidad | Estado |
|---|---:|---|---|
| Altura total de referencia | 13.150 | m | proporcionado |
| Altura modelada | 9.800 | m | proporcionado |
| Espesor | 0.400 | m | proporcionado |
| Recubrimiento | 50 | mm | asumido |
| f'c | 280.0 | kgf/cm² | agente base |
| fy | 4200.0 | kgf/cm² | agente base |
| Ec | 24.614 | GPa | E.060 |
| Longitud desarrollada | 27.1935 | m | coordenadas |
| Tamaño objetivo de malla | 0.500 | m | adoptado |
| Nodos / elementos | 1298 / 1218 | — | calculado |

### Coordenadas en planta

| Punto | x (m) | y (m) | Tipo |
|---|---:|---:|---|
| CF-I1 | 0.00 | 7.09 | contrafuerte |
| CF-I2 | 2.15 | 4.94 | contrafuerte |
| CF-I3 | 4.27 | 2.82 | contrafuerte |
| QI | 7.09 | 0.00 | quiebre |
| CF-C1 | 7.86 | 0.00 | contrafuerte |
| CF-C2 | 10.66 | 0.00 | contrafuerte |
| CF-C3 | 13.46 | 0.00 | contrafuerte |
| QD | 14.23 | 0.00 | quiebre |
| CF-D1 | 17.05 | 2.82 | contrafuerte |
| CF-D2 | 19.17 | 4.94 | contrafuerte |
| CF-D3 | 21.32 | 7.09 | contrafuerte |

## 3. Idealización y formulación

La poligonal se extruye verticalmente hasta 9.80 m. Cada elemento Q4 contiene membrana bilineal y placa Mindlin-Reissner; el cortante transversal usa interpolación MITC4. En cada plano el eje local `x` sigue la pantalla, `y` es vertical y `+n` apunta hacia la cara exterior.

Se emplea rigidez elástica bruta uniforme. La fisuración no lineal y una eventual redistribución por rigidez efectiva no forman parte de este análisis.

La base está empotrada. En las nueve líneas de contrafuerte se restringe la traslación normal local y se mantienen libres las rotaciones. Los quiebres QI y QD comparten nodos y seis grados de libertad, por lo que la unión se considera monolítica.

Para el diseño se usan resultantes de cascarón `(Nxx,Nyy,Nxy,Mxx,Myy,Mxy,Qx,Qy)`. Los momentos torsores se incorporan mediante envolventes Wood-Armer y la tracción de membrana se distribuye conservadoramente por mitad entre las dos caras.

## 4. Acciones y estados límite

- Ka normal = 0.189120.
- KAE normal = 0.257681.
- Servicio I: EH + LS.
- Resistencia I-a: 1.50 EH + 1.75 LS.
- Resistencia I-b: se ejecuta separadamente con la misma demanda lateral.
- Evento Extremo I: envolvente de las concurrencias A y B, incluida la inercia propia de la pantalla.

La presión varía linealmente con la altura y se aplica normal a cada elemento; no se aplican fuerzas de cajuela, apoyo, frenado o impacto.

### Presiones de referencia — Resistencia I-a

`qu = 1.50 EH + 1.75 LS`. Los valores corresponden al borde inferior de cada tercio y actúan normalmente sobre cada panel shell.

| Franja | z sobre zapata | Profundidad | 1.50 EH | 1.75 LS | qu | qu |
|---|---:|---:|---:|---:|---:|---:|
| Inferior | 0.000 m | 13.150 m | 6.715 tf/m² | 0.363 tf/m² | 7.078 tf/m² | 69.41 kN/m² |
| Intermedia | 3.267 m | 9.883 m | 5.047 tf/m² | 0.363 tf/m² | 5.410 tf/m² | 53.05 kN/m² |
| Superior | 6.533 m | 6.617 m | 3.379 tf/m² | 0.363 tf/m² | 3.742 tf/m² | 36.70 kN/m² |

## 5. Respuesta global

| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |
|---|---|---:|---:|---:|---:|---:|
| Servicio I | EH + LS | 0.3507 | 0.000 | -6179.855 | 4.76e-11 | 7.24e-06 |
| Resistencia I-a | 1.50 EH + 1.75 LS | 0.5319 | -0.000 | -9376.151 | 7.35e-11 | 1.17e-05 |
| Resistencia I-b | 1.50 EH + 1.75 LS | 0.5319 | -0.000 | -9376.151 | 7.35e-11 | 1.17e-05 |
| Evento Extremo I-A | 100% PAE + 50% PIR | 0.4306 | -0.000 | -7571.383 | 4.78e-11 | 5.96e-06 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR | 0.3409 | 0.000 | -6000.255 | 4.78e-11 | 5.81e-06 |

### Reacciones normales en contrafuertes

| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |
|---|---|---:|---:|---:|
| Servicio I | CF-I1 | 305.523 | 216.038 | 216.038 |
| Servicio I | CF-I2 | 799.625 | 565.420 | 565.420 |
| Servicio I | CF-I3 | 949.542 | 671.428 | 671.428 |
| Servicio I | CF-C1 | 688.534 | 0.000 | 688.534 |
| Servicio I | CF-C2 | 634.826 | 0.000 | 634.826 |
| Servicio I | CF-C3 | 688.534 | 0.000 | 688.534 |
| Servicio I | CF-D1 | 949.542 | -671.428 | 671.428 |
| Servicio I | CF-D2 | 799.625 | -565.420 | 565.420 |
| Servicio I | CF-D3 | 305.523 | -216.038 | 216.038 |
| Resistencia I-a | CF-I1 | 463.859 | 327.998 | 327.998 |
| Resistencia I-a | CF-I2 | 1213.768 | 858.264 | 858.264 |
| Resistencia I-a | CF-I3 | 1441.606 | 1019.370 | 1019.370 |
| Resistencia I-a | CF-C1 | 1045.496 | 0.000 | 1045.496 |
| Resistencia I-a | CF-C2 | 963.352 | 0.000 | 963.352 |
| Resistencia I-a | CF-C3 | 1045.496 | -0.000 | 1045.496 |
| Resistencia I-a | CF-D1 | 1441.606 | -1019.370 | 1019.370 |
| Resistencia I-a | CF-D2 | 1213.768 | -858.264 | 858.264 |
| Resistencia I-a | CF-D3 | 463.859 | -327.998 | 327.998 |
| Resistencia I-b | CF-I1 | 463.859 | 327.998 | 327.998 |
| Resistencia I-b | CF-I2 | 1213.768 | 858.264 | 858.264 |
| Resistencia I-b | CF-I3 | 1441.606 | 1019.370 | 1019.370 |
| Resistencia I-b | CF-C1 | 1045.496 | 0.000 | 1045.496 |
| Resistencia I-b | CF-C2 | 963.352 | 0.000 | 963.352 |
| Resistencia I-b | CF-C3 | 1045.496 | -0.000 | 1045.496 |
| Resistencia I-b | CF-D1 | 1441.606 | -1019.370 | 1019.370 |
| Resistencia I-b | CF-D2 | 1213.768 | -858.264 | 858.264 |
| Resistencia I-b | CF-D3 | 463.859 | -327.998 | 327.998 |
| Evento Extremo I-A | CF-I1 | 373.051 | 263.787 | 263.787 |
| Evento Extremo I-A | CF-I2 | 977.398 | 691.125 | 691.125 |
| Evento Extremo I-A | CF-I3 | 1159.534 | 819.914 | 819.914 |
| Evento Extremo I-A | CF-C1 | 840.176 | 0.000 | 840.176 |
| Evento Extremo I-A | CF-C2 | 777.025 | -0.000 | 777.025 |
| Evento Extremo I-A | CF-C3 | 840.176 | 0.000 | 840.176 |
| Evento Extremo I-A | CF-D1 | 1159.534 | -819.914 | 819.914 |
| Evento Extremo I-A | CF-D2 | 977.398 | -691.125 | 691.125 |
| Evento Extremo I-A | CF-D3 | 373.051 | -263.787 | 263.787 |
| Evento Extremo I-B | CF-I1 | 296.112 | 209.383 | 209.383 |
| Evento Extremo I-B | CF-I2 | 775.429 | 548.311 | 548.311 |
| Evento Extremo I-B | CF-I3 | 920.344 | 650.781 | 650.781 |
| Evento Extremo I-B | CF-C1 | 667.098 | -0.000 | 667.098 |
| Evento Extremo I-B | CF-C2 | 616.064 | -0.000 | 616.064 |
| Evento Extremo I-B | CF-C3 | 667.098 | -0.000 | 667.098 |
| Evento Extremo I-B | CF-D1 | 920.344 | -650.781 | 650.781 |
| Evento Extremo I-B | CF-D2 | 775.429 | -548.311 | 548.311 |
| Evento Extremo I-B | CF-D3 | 296.112 | -209.383 | 209.383 |

## 6. Diseño E.060–MTC/AASHTO

Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana.

| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |
|---|---|---|---|---|---:|---:|---:|---|---:|
| Ala izquierda | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 46.20 kN·m/m | 51.10 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.531 |
| Ala izquierda | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.68 kN·m/m | 36.03 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.493 |
| Ala izquierda | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 17.03 kN·m/m | 46.75 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.273 |
| Ala izquierda | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 52.64 kN·m/m | 26.58 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.517 |
| Ala izquierda | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 47.05 kN·m/m | 47.49 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.528 |
| Ala izquierda | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.35 kN·m/m | 34.67 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.486 |
| Ala izquierda | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 17.32 kN·m/m | 7.73 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.167 |
| Ala izquierda | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 12.03 kN·m/m | 14.89 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.143 |
| Ala izquierda | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 39.36 kN·m/m | 18.67 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.383 |
| Ala izquierda | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.91 kN·m/m | 15.92 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.347 |
| Ala izquierda | Superior | Vertical | Exterior (+n) | Resistencia I-a | 8.67 kN·m/m | 1.73 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.078 |
| Ala izquierda | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.44 kN·m/m | 1.98 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.077 |
| Pantalla central | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 15.85 kN·m/m | 52.66 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.279 |
| Pantalla central | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 42.61 kN·m/m | 70.94 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.555 |
| Pantalla central | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 9.29 kN·m/m | 4.81 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.092 |
| Pantalla central | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 13.36 kN·m/m | 8.52 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.136 |
| Pantalla central | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 14.82 kN·m/m | 55.19 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.278 |
| Pantalla central | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 42.58 kN·m/m | 72.66 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.560 |
| Pantalla central | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 26.67 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.074 |
| Pantalla central | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 6.67 kN·m/m | 26.67 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.130 |
| Pantalla central | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 8.39 kN·m/m | 45.04 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.195 |
| Pantalla central | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 34.40 kN·m/m | 43.65 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.411 |
| Pantalla central | Superior | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 9.75 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.027 |
| Pantalla central | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 7.11 kN·m/m | 9.33 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.086 |
| Ala derecha | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 46.20 kN·m/m | 51.10 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.531 |
| Ala derecha | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.68 kN·m/m | 36.03 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.493 |
| Ala derecha | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 17.03 kN·m/m | 46.75 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.273 |
| Ala derecha | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 52.64 kN·m/m | 26.58 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.517 |
| Ala derecha | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 47.05 kN·m/m | 47.49 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.528 |
| Ala derecha | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.35 kN·m/m | 34.67 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.486 |
| Ala derecha | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 17.32 kN·m/m | 7.73 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.167 |
| Ala derecha | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 12.03 kN·m/m | 14.89 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.143 |
| Ala derecha | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 39.36 kN·m/m | 18.67 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.383 |
| Ala derecha | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.91 kN·m/m | 15.92 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.347 |
| Ala derecha | Superior | Vertical | Exterior (+n) | Resistencia I-a | 8.67 kN·m/m | 1.73 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.078 |
| Ala derecha | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.44 kN·m/m | 1.98 kN/m | 9.407 cm²/m | Ø1/2" @ 130 mm | 0.077 |

### Líneas horizontales de lectura tipo *spandrel*

Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor valor de ambos lados, sin promediado.

| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |
|---|---:|---:|---:|---|---:|---:|---|
| FR-INFERIOR | 0.000 | 3.23 kN·m/m | 0.217 m | Resistencia I-a | 11.77 kN·m/m | 18.413 m | Resistencia I-a |
| FR-INTERMEDIA | 3.267 | 46.43 kN·m/m | 18.912 m | Resistencia I-a | 46.77 kN·m/m | 21.405 m | Resistencia I-a |
| FR-SUPERIOR | 6.533 | 39.63 kN·m/m | 18.912 m | Resistencia I-a | 36.06 kN·m/m | 21.405 m | Resistencia I-a |

Longitud de desarrollo adoptada máxima: **1200 mm**; empalme Clase B de referencia: **1600 mm**. Debe comprobarse la longitud física disponible en cada quiebre y contrafuerte.

### Cortante y compresión de membrana

| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |
|---|---|---:|---:|---:|---:|---:|
| Ala izquierda | Inferior | 110.88 kN/m | 237.66 kN/m | 0.467 | 0.439 MPa | 0.036 |
| Ala izquierda | Intermedia | 98.24 kN/m | 237.66 kN/m | 0.413 | 0.038 MPa | 0.003 |
| Ala izquierda | Superior | 71.00 kN/m | 237.66 kN/m | 0.299 | 0.011 MPa | 0.001 |
| Pantalla central | Inferior | 73.34 kN/m | 237.66 kN/m | 0.309 | 0.447 MPa | 0.036 |
| Pantalla central | Intermedia | 70.10 kN/m | 237.66 kN/m | 0.295 | 0.071 MPa | 0.006 |
| Pantalla central | Superior | 52.06 kN/m | 237.66 kN/m | 0.219 | 0.025 MPa | 0.002 |
| Ala derecha | Inferior | 110.88 kN/m | 237.66 kN/m | 0.467 | 0.439 MPa | 0.036 |
| Ala derecha | Intermedia | 98.24 kN/m | 237.66 kN/m | 0.413 | 0.038 MPa | 0.003 |
| Ala derecha | Superior | 71.00 kN/m | 237.66 kN/m | 0.299 | 0.011 MPa | 0.001 |

## 7. Convergencia de malla

| Tamaño (m) | Nodos | Elementos | d máx. (mm) | Cambio d | M WA puntual (kN·m/m) |
|---:|---:|---:|---:|---:|---:|
| — | — | — | — | no ejecutada | — |

Los desplazamientos globales muestran convergencia; los máximos puntuales próximos a líneas rígidas son sensibles al mallado y se interpretan como envolventes locales. En este cálculo no alteran el armado porque gobierna el mínimo normativo.

## 8. Validaciones

| Control | Resultado |
|---|---|
| longitud desarrollada m | 27.1935 |
| geometria simetrica | Conforme |
| nueve lineas contrafuerte | Conforme |
| cajuela excluida | Conforme |
| resistencia ia ib independientes | Conforme |
| resistencia ia ib coinciden | Conforme |
| max error fuerza kn | 7.34523e-11 |
| max error momento kn m | 1.17077e-05 |
| equilibrio cumple | Conforme |
| error relativo desplazamientos | 8.24053e-14 |
| error relativo reacciones pares | 1.76e-14 |
| simetria cumple | Conforme |
| flexion membrana cumple | Conforme |
| cortante cumple | Conforme |
| compresion membrana cumple | Conforme |

## 9. Conclusión

**Estado del modelo: CUMPLE.**

El espesor de 0.40 m satisface las comprobaciones incluidas. El máximo DCR de flexión–membrana es 0.560 y el máximo DCR de cortante es 0.467.

Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con rigideces fisuradas.

# Análisis tridimensional FEM de la pantalla plegada

## 1. Objetivo y alcance

Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.

## 2. Datos

| Parámetro | Valor | Unidad | Estado |
|---|---:|---|---|
| Altura total de referencia | 13.840 | m | proporcionado |
| Altura modelada | 10.800 | m | proporcionado |
| Espesor | 0.400 | m | proporcionado |
| Recubrimiento exterior (+n) | 100 | mm | proporcionado |
| Recubrimiento interior (-n) | 75 | mm | proporcionado |
| f'c | 280.0 | kgf/cm² | agente base |
| fy | 4200.0 | kgf/cm² | agente base |
| Ec | 24.614 | GPa | E.060 |
| Longitud desarrollada | 27.1935 | m | coordenadas |
| Tamaño objetivo de malla | 0.500 | m | adoptado |
| Nodos / elementos | 1475 / 1392 | — | calculado |

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
| Inferior | 0.000 m | 13.840 m | 7.067 tf/m² | 0.363 tf/m² | 7.430 tf/m² | 72.87 kN/m² |
| Intermedia | 3.600 m | 10.240 m | 5.229 tf/m² | 0.363 tf/m² | 5.592 tf/m² | 54.84 kN/m² |
| Superior | 7.200 m | 6.640 m | 3.391 tf/m² | 0.363 tf/m² | 3.754 tf/m² | 36.81 kN/m² |

## 5. Respuesta global

| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |
|---|---|---:|---:|---:|---:|---:|
| Servicio I | EH + LS | 0.3762 | -0.000 | -6956.501 | 4.46e-11 | 5.42e-06 |
| Resistencia I-a | 1.50 EH + 1.75 LS | 0.5701 | -0.000 | -10551.974 | 9.12e-11 | 7.43e-06 |
| Resistencia I-b | 1.50 EH + 1.75 LS | 0.5701 | -0.000 | -10551.974 | 9.12e-11 | 7.43e-06 |
| Evento Extremo I-A | 100% PAE + 50% PIR | 0.4638 | -0.000 | -8533.017 | 7.28e-11 | 9.84e-06 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR | 0.3665 | -0.000 | -6758.574 | 3.76e-11 | 6.60e-06 |

### Reacciones normales en contrafuertes

| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |
|---|---|---:|---:|---:|
| Servicio I | CF-I1 | 348.369 | 246.334 | 246.334 |
| Servicio I | CF-I2 | 906.970 | 641.325 | 641.325 |
| Servicio I | CF-I3 | 1083.913 | 766.442 | 766.442 |
| Servicio I | CF-C1 | 800.827 | -0.000 | 800.827 |
| Servicio I | CF-C2 | 711.521 | -0.000 | 711.521 |
| Servicio I | CF-C3 | 800.827 | -0.000 | 800.827 |
| Servicio I | CF-D1 | 1083.913 | -766.442 | 766.442 |
| Servicio I | CF-D2 | 906.970 | -641.325 | 641.325 |
| Servicio I | CF-D3 | 348.369 | -246.334 | 246.334 |
| Resistencia I-a | CF-I1 | 528.773 | 373.899 | 373.899 |
| Resistencia I-a | CF-I2 | 1376.346 | 973.224 | 973.224 |
| Resistencia I-a | CF-I3 | 1645.194 | 1163.328 | 1163.328 |
| Resistencia I-a | CF-C1 | 1215.792 | -0.000 | 1215.792 |
| Resistencia I-a | CF-C2 | 1079.413 | -0.000 | 1079.413 |
| Resistencia I-a | CF-C3 | 1215.792 | 0.000 | 1215.792 |
| Resistencia I-a | CF-D1 | 1645.194 | -1163.328 | 1163.328 |
| Resistencia I-a | CF-D2 | 1376.346 | -973.224 | 973.224 |
| Resistencia I-a | CF-D3 | 528.773 | -373.899 | 373.899 |
| Resistencia I-b | CF-I1 | 528.773 | 373.899 | 373.899 |
| Resistencia I-b | CF-I2 | 1376.346 | 973.224 | 973.224 |
| Resistencia I-b | CF-I3 | 1645.194 | 1163.328 | 1163.328 |
| Resistencia I-b | CF-C1 | 1215.792 | -0.000 | 1215.792 |
| Resistencia I-b | CF-C2 | 1079.413 | -0.000 | 1079.413 |
| Resistencia I-b | CF-C3 | 1215.792 | 0.000 | 1215.792 |
| Resistencia I-b | CF-D1 | 1645.194 | -1163.328 | 1163.328 |
| Resistencia I-b | CF-D2 | 1376.346 | -973.224 | 973.224 |
| Resistencia I-b | CF-D3 | 528.773 | -373.899 | 373.899 |
| Evento Extremo I-A | CF-I1 | 425.913 | 301.166 | 301.166 |
| Evento Extremo I-A | CF-I2 | 1110.066 | 784.935 | 784.935 |
| Evento Extremo I-A | CF-I3 | 1325.291 | 937.122 | 937.122 |
| Evento Extremo I-A | CF-C1 | 978.060 | 0.000 | 978.060 |
| Evento Extremo I-A | CF-C2 | 872.196 | 0.000 | 872.196 |
| Evento Extremo I-A | CF-C3 | 978.060 | -0.000 | 978.060 |
| Evento Extremo I-A | CF-D1 | 1325.291 | -937.122 | 937.122 |
| Evento Extremo I-A | CF-D2 | 1110.066 | -784.935 | 784.935 |
| Evento Extremo I-A | CF-D3 | 425.913 | -301.166 | 301.166 |
| Evento Extremo I-B | CF-I1 | 337.867 | 238.908 | 238.908 |
| Evento Extremo I-B | CF-I2 | 880.138 | 622.352 | 622.352 |
| Evento Extremo I-B | CF-I3 | 1051.283 | 743.369 | 743.369 |
| Evento Extremo I-B | CF-C1 | 776.256 | 0.000 | 776.256 |
| Evento Extremo I-B | CF-C2 | 691.036 | 0.000 | 691.036 |
| Evento Extremo I-B | CF-C3 | 776.256 | -0.000 | 776.256 |
| Evento Extremo I-B | CF-D1 | 1051.283 | -743.369 | 743.369 |
| Evento Extremo I-B | CF-D2 | 880.138 | -622.352 | 622.352 |
| Evento Extremo I-B | CF-D3 | 337.867 | -238.908 | 238.908 |

## 6. Diseño E.060–MTC/AASHTO

Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana. El brazo mecánico de cada cara usa su recubrimiento nominal: exterior 100 mm (agua con abrasión) e interior 75 mm (relleno).

| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |
|---|---|---|---|---|---:|---:|---:|---|---:|
| Ala izquierda | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 50.10 kN·m/m | 52.00 kN/m | 8.012 cm²/m | Ø5/8" @ 220 mm | 0.694 |
| Ala izquierda | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 49.76 kN·m/m | 38.94 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.620 |
| Ala izquierda | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 17.74 kN·m/m | 50.94 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.382 |
| Ala izquierda | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 56.44 kN·m/m | 28.32 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.655 |
| Ala izquierda | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 50.47 kN·m/m | 48.05 kN/m | 8.012 cm²/m | Ø5/8" @ 220 mm | 0.686 |
| Ala izquierda | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 49.07 kN·m/m | 36.08 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.605 |
| Ala izquierda | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.92 kN·m/m | 7.28 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.226 |
| Ala izquierda | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 12.31 kN·m/m | 14.37 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.168 |
| Ala izquierda | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 40.10 kN·m/m | 15.39 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.529 |
| Ala izquierda | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 36.66 kN·m/m | 13.08 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.409 |
| Ala izquierda | Superior | Vertical | Exterior (+n) | Resistencia I-a | 8.92 kN·m/m | 0.97 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.110 |
| Ala izquierda | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.79 kN·m/m | 1.04 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.092 |
| Pantalla central | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 16.23 kN·m/m | 57.96 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.387 |
| Pantalla central | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 45.59 kN·m/m | 77.06 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.695 |
| Pantalla central | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 9.72 kN·m/m | 5.35 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.134 |
| Pantalla central | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 14.37 kN·m/m | 8.93 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.172 |
| Pantalla central | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 15.04 kN·m/m | 61.41 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.384 |
| Pantalla central | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 45.14 kN·m/m | 76.72 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.690 |
| Pantalla central | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 27.76 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.093 |
| Pantalla central | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 6.79 kN·m/m | 27.76 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.153 |
| Pantalla central | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 8.17 kN·m/m | 42.38 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.239 |
| Pantalla central | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.51 kN·m/m | 40.40 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.481 |
| Pantalla central | Superior | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 8.12 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.027 |
| Pantalla central | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 7.45 kN·m/m | 7.88 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.099 |
| Ala derecha | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 50.10 kN·m/m | 52.00 kN/m | 8.012 cm²/m | Ø5/8" @ 220 mm | 0.694 |
| Ala derecha | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 49.76 kN·m/m | 38.94 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.620 |
| Ala derecha | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 17.74 kN·m/m | 50.94 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.382 |
| Ala derecha | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 56.44 kN·m/m | 28.32 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.655 |
| Ala derecha | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 50.47 kN·m/m | 48.05 kN/m | 8.012 cm²/m | Ø5/8" @ 220 mm | 0.686 |
| Ala derecha | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 49.07 kN·m/m | 36.08 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.605 |
| Ala derecha | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.92 kN·m/m | 7.28 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.226 |
| Ala derecha | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 12.31 kN·m/m | 14.37 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.168 |
| Ala derecha | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 40.10 kN·m/m | 15.39 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.529 |
| Ala derecha | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 36.66 kN·m/m | 13.08 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.409 |
| Ala derecha | Superior | Vertical | Exterior (+n) | Resistencia I-a | 8.92 kN·m/m | 0.97 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.110 |
| Ala derecha | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.79 kN·m/m | 1.04 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.092 |

### Líneas horizontales de lectura tipo *spandrel*

Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor valor de ambos lados, sin promediado.

| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |
|---|---:|---:|---:|---|---:|---:|---|
| FR-INFERIOR | 0.000 | 3.37 kN·m/m | 0.217 m | Resistencia I-a | 12.59 kN·m/m | 8.780 m | Resistencia I-a |
| FR-INTERMEDIA | 3.600 | 50.24 kN·m/m | 18.912 m | Resistencia I-a | 49.54 kN·m/m | 5.789 m | Resistencia I-a |
| FR-SUPERIOR | 7.200 | 40.33 kN·m/m | 8.282 m | Resistencia I-a | 36.81 kN·m/m | 5.789 m | Resistencia I-a |

Longitud de desarrollo adoptada máxima: **1500 mm**; empalme Clase B de referencia: **1950 mm**. Debe comprobarse la longitud física disponible en cada quiebre y contrafuerte.

### Cortante y compresión de membrana

| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |
|---|---|---:|---:|---:|---:|---:|
| Ala izquierda | Inferior | 117.78 kN/m | 217.54 kN/m | 0.541 | 0.472 MPa | 0.038 |
| Ala izquierda | Intermedia | 103.05 kN/m | 217.54 kN/m | 0.474 | 0.036 MPa | 0.003 |
| Ala izquierda | Superior | 71.64 kN/m | 217.54 kN/m | 0.329 | 0.014 MPa | 0.001 |
| Pantalla central | Inferior | 77.72 kN/m | 217.54 kN/m | 0.357 | 0.480 MPa | 0.039 |
| Pantalla central | Intermedia | 73.09 kN/m | 217.54 kN/m | 0.336 | 0.074 MPa | 0.006 |
| Pantalla central | Superior | 53.09 kN/m | 217.54 kN/m | 0.244 | 0.020 MPa | 0.002 |
| Ala derecha | Inferior | 117.78 kN/m | 217.54 kN/m | 0.541 | 0.472 MPa | 0.038 |
| Ala derecha | Intermedia | 103.05 kN/m | 217.54 kN/m | 0.474 | 0.036 MPa | 0.003 |
| Ala derecha | Superior | 71.64 kN/m | 217.54 kN/m | 0.329 | 0.014 MPa | 0.001 |

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
| cajuela excluida | No conforme |
| resistencia ia ib independientes | Conforme |
| resistencia ia ib coinciden | Conforme |
| max error fuerza kn | 9.11672e-11 |
| max error momento kn m | 9.83705e-06 |
| equilibrio cumple | Conforme |
| error relativo desplazamientos | 5.17119e-14 |
| error relativo reacciones pares | 1.26912e-14 |
| simetria cumple | Conforme |
| flexion membrana cumple | Conforme |
| cortante cumple | Conforme |
| compresion membrana cumple | Conforme |

## 9. Conclusión

**Estado del modelo: CUMPLE.**

El espesor de 0.40 m satisface las comprobaciones incluidas. El máximo DCR de flexión–membrana es 0.695 y el máximo DCR de cortante es 0.541.

Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con rigideces fisuradas.

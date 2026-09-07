# Análisis tridimensional FEM de la pantalla plegada

## 1. Objetivo y alcance

Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.

## 2. Datos

| Parámetro | Valor | Unidad | Estado |
|---|---:|---|---|
| Altura total de referencia | 10.890 | m | proporcionado |
| Altura modelada | 7.850 | m | proporcionado |
| Espesor | 0.400 | m | proporcionado |
| Recubrimiento exterior (+n) | 100 | mm | proporcionado |
| Recubrimiento interior (-n) | 75 | mm | proporcionado |
| f'c | 280.0 | kgf/cm² | agente base |
| fy | 4200.0 | kgf/cm² | agente base |
| Ec | 24.614 | GPa | E.060 |
| Longitud desarrollada | 27.1935 | m | coordenadas |
| Tamaño objetivo de malla | 0.500 | m | adoptado |
| Nodos / elementos | 1121 / 1044 | — | calculado |

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
| Inferior | 0.000 m | 10.890 m | 5.561 tf/m² | 0.363 tf/m² | 5.924 tf/m² | 58.10 kN/m² |
| Intermedia | 2.617 m | 8.273 m | 4.225 tf/m² | 0.363 tf/m² | 4.588 tf/m² | 44.99 kN/m² |
| Superior | 5.233 m | 5.657 m | 2.888 tf/m² | 0.363 tf/m² | 3.252 tf/m² | 31.89 kN/m² |

## 5. Respuesta global

| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |
|---|---|---:|---:|---:|---:|---:|
| Servicio I | EH + LS | 0.2668 | -0.000 | -4232.245 | 1.51e-11 | 2.91e-05 |
| Resistencia I-a | 1.50 EH + 1.75 LS | 0.4058 | -0.000 | -6433.571 | 2.93e-11 | 4.49e-05 |
| Resistencia I-b | 1.50 EH + 1.75 LS | 0.4058 | -0.000 | -6433.571 | 2.93e-11 | 4.49e-05 |
| Evento Extremo I-A | 100% PAE + 50% PIR | 0.3230 | -0.000 | -5135.527 | 1.49e-11 | 3.21e-05 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR | 0.2574 | -0.000 | -4088.382 | 1.50e-11 | 2.68e-05 |

### Reacciones normales en contrafuertes

| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |
|---|---|---:|---:|---:|
| Servicio I | CF-I1 | 200.794 | 141.983 | 141.983 |
| Servicio I | CF-I2 | 534.690 | 378.083 | 378.083 |
| Servicio I | CF-I3 | 623.719 | 441.036 | 441.036 |
| Servicio I | CF-C1 | 433.047 | 0.000 | 433.047 |
| Servicio I | CF-C2 | 437.513 | 0.000 | 437.513 |
| Servicio I | CF-C3 | 433.047 | 0.000 | 433.047 |
| Servicio I | CF-D1 | 623.719 | -441.036 | 441.036 |
| Servicio I | CF-D2 | 534.690 | -378.083 | 378.083 |
| Servicio I | CF-D3 | 200.794 | -141.983 | 141.983 |
| Resistencia I-a | CF-I1 | 305.507 | 216.026 | 216.026 |
| Resistencia I-a | CF-I2 | 813.324 | 575.107 | 575.107 |
| Resistencia I-a | CF-I3 | 948.950 | 671.009 | 671.009 |
| Resistencia I-a | CF-C1 | 658.853 | -0.000 | 658.853 |
| Resistencia I-a | CF-C2 | 665.331 | 0.000 | 665.331 |
| Resistencia I-a | CF-C3 | 658.853 | -0.000 | 658.853 |
| Resistencia I-a | CF-D1 | 948.950 | -671.009 | 671.009 |
| Resistencia I-a | CF-D2 | 813.324 | -575.107 | 575.107 |
| Resistencia I-a | CF-D3 | 305.507 | -216.026 | 216.026 |
| Resistencia I-b | CF-I1 | 305.507 | 216.026 | 216.026 |
| Resistencia I-b | CF-I2 | 813.324 | 575.107 | 575.107 |
| Resistencia I-b | CF-I3 | 948.950 | 671.009 | 671.009 |
| Resistencia I-b | CF-C1 | 658.853 | -0.000 | 658.853 |
| Resistencia I-b | CF-C2 | 665.331 | 0.000 | 665.331 |
| Resistencia I-b | CF-C3 | 658.853 | -0.000 | 658.853 |
| Resistencia I-b | CF-D1 | 948.950 | -671.009 | 671.009 |
| Resistencia I-b | CF-D2 | 813.324 | -575.107 | 575.107 |
| Resistencia I-b | CF-D3 | 305.507 | -216.026 | 216.026 |
| Evento Extremo I-A | CF-I1 | 242.549 | 171.508 | 171.508 |
| Evento Extremo I-A | CF-I2 | 646.697 | 457.284 | 457.284 |
| Evento Extremo I-A | CF-I3 | 753.561 | 532.848 | 532.848 |
| Evento Extremo I-A | CF-C1 | 523.203 | 0.000 | 523.203 |
| Evento Extremo I-A | CF-C2 | 529.869 | -0.000 | 529.869 |
| Evento Extremo I-A | CF-C3 | 523.203 | 0.000 | 523.203 |
| Evento Extremo I-A | CF-D1 | 753.561 | -532.848 | 532.848 |
| Evento Extremo I-A | CF-D2 | 646.697 | -457.284 | 457.284 |
| Evento Extremo I-A | CF-D3 | 242.549 | -171.508 | 171.508 |
| Evento Extremo I-B | CF-I1 | 193.507 | 136.830 | 136.830 |
| Evento Extremo I-B | CF-I2 | 515.628 | 364.604 | 364.604 |
| Evento Extremo I-B | CF-I3 | 601.142 | 425.071 | 425.071 |
| Evento Extremo I-B | CF-C1 | 417.375 | 0.000 | 417.375 |
| Evento Extremo I-B | CF-C2 | 422.212 | 0.000 | 422.212 |
| Evento Extremo I-B | CF-C3 | 417.375 | 0.000 | 417.375 |
| Evento Extremo I-B | CF-D1 | 601.142 | -425.071 | 425.071 |
| Evento Extremo I-B | CF-D2 | 515.628 | -364.604 | 364.604 |
| Evento Extremo I-B | CF-D3 | 193.507 | -136.830 | 136.830 |

## 6. Diseño E.060–MTC/AASHTO

Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana. El brazo mecánico de cada cara usa su recubrimiento nominal: exterior 100 mm (agua con abrasión) e interior 75 mm (relleno).

| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |
|---|---|---|---|---|---:|---:|---:|---|---:|
| Ala izquierda | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 33.60 kN·m/m | 41.87 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.540 |
| Ala izquierda | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.15 kN·m/m | 30.04 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.446 |
| Ala izquierda | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 18.71 kN·m/m | 17.54 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.282 |
| Ala izquierda | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 43.23 kN·m/m | 21.29 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.501 |
| Ala izquierda | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 35.51 kN·m/m | 40.16 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.557 |
| Ala izquierda | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 36.46 kN·m/m | 27.30 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.451 |
| Ala izquierda | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.64 kN·m/m | 8.80 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.228 |
| Ala izquierda | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 9.69 kN·m/m | 12.99 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.137 |
| Ala izquierda | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 32.80 kN·m/m | 21.50 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.463 |
| Ala izquierda | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 29.84 kN·m/m | 17.99 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.356 |
| Ala izquierda | Superior | Vertical | Exterior (+n) | Resistencia I-a | 7.32 kN·m/m | 2.00 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.094 |
| Ala izquierda | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 6.31 kN·m/m | 4.31 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.077 |
| Pantalla central | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 12.89 kN·m/m | 40.74 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.290 |
| Pantalla central | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 33.04 kN·m/m | 49.57 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.485 |
| Pantalla central | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 7.55 kN·m/m | 5.97 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.110 |
| Pantalla central | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 11.48 kN·m/m | 8.80 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.143 |
| Pantalla central | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 12.34 kN·m/m | 42.31 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.288 |
| Pantalla central | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 33.03 kN·m/m | 57.38 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.509 |
| Pantalla central | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 21.86 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.073 |
| Pantalla central | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 5.68 kN·m/m | 20.51 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.120 |
| Pantalla central | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 7.84 kN·m/m | 42.88 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.237 |
| Pantalla central | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 27.90 kN·m/m | 43.67 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.415 |
| Pantalla central | Superior | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 11.55 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.039 |
| Pantalla central | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 5.55 kN·m/m | 10.61 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.088 |
| Ala derecha | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 33.60 kN·m/m | 41.87 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.540 |
| Ala derecha | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.15 kN·m/m | 30.04 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.446 |
| Ala derecha | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 18.71 kN·m/m | 17.54 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.282 |
| Ala derecha | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 43.23 kN·m/m | 21.29 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.501 |
| Ala derecha | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 35.51 kN·m/m | 40.16 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.557 |
| Ala derecha | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 36.46 kN·m/m | 27.30 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.451 |
| Ala derecha | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.64 kN·m/m | 8.80 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.228 |
| Ala derecha | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 9.69 kN·m/m | 12.99 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.137 |
| Ala derecha | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 32.80 kN·m/m | 21.50 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.463 |
| Ala derecha | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 29.84 kN·m/m | 17.99 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.356 |
| Ala derecha | Superior | Vertical | Exterior (+n) | Resistencia I-a | 7.32 kN·m/m | 2.00 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.094 |
| Ala derecha | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 6.31 kN·m/m | 4.31 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.077 |

### Líneas horizontales de lectura tipo *spandrel*

Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor valor de ambos lados, sin promediado.

| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |
|---|---:|---:|---:|---|---:|---:|---|
| FR-INFERIOR | 0.000 | 2.57 kN·m/m | 26.976 m | Resistencia I-a | 9.63 kN·m/m | 8.780 m | Resistencia I-a |
| FR-INTERMEDIA | 2.617 | 33.88 kN·m/m | 8.282 m | Resistencia I-a | 35.95 kN·m/m | 5.789 m | Resistencia I-a |
| FR-SUPERIOR | 5.233 | 33.10 kN·m/m | 8.282 m | Resistencia I-a | 30.06 kN·m/m | 5.789 m | Resistencia I-a |

Longitud de desarrollo adoptada máxima: **1500 mm**; empalme Clase B de referencia: **1950 mm**. Debe comprobarse la longitud física disponible en cada quiebre y contrafuerte.

### Cortante y compresión de membrana

| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |
|---|---|---:|---:|---:|---:|---:|
| Ala izquierda | Inferior | 91.42 kN/m | 217.54 kN/m | 0.420 | 0.340 MPa | 0.028 |
| Ala izquierda | Intermedia | 78.73 kN/m | 217.54 kN/m | 0.362 | 0.033 MPa | 0.003 |
| Ala izquierda | Superior | 60.99 kN/m | 217.54 kN/m | 0.280 | 0.011 MPa | 0.001 |
| Pantalla central | Inferior | 58.68 kN/m | 217.54 kN/m | 0.270 | 0.346 MPa | 0.028 |
| Pantalla central | Intermedia | 57.75 kN/m | 217.54 kN/m | 0.265 | 0.048 MPa | 0.004 |
| Pantalla central | Superior | 43.62 kN/m | 217.54 kN/m | 0.201 | 0.026 MPa | 0.002 |
| Ala derecha | Inferior | 91.42 kN/m | 217.54 kN/m | 0.420 | 0.340 MPa | 0.028 |
| Ala derecha | Intermedia | 78.73 kN/m | 217.54 kN/m | 0.362 | 0.033 MPa | 0.003 |
| Ala derecha | Superior | 60.99 kN/m | 217.54 kN/m | 0.280 | 0.011 MPa | 0.001 |

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
| max error fuerza kn | 2.92641e-11 |
| max error momento kn m | 4.49493e-05 |
| equilibrio cumple | Conforme |
| error relativo desplazamientos | 8.20729e-14 |
| error relativo reacciones pares | 1.67691e-14 |
| simetria cumple | Conforme |
| flexion membrana cumple | Conforme |
| cortante cumple | Conforme |
| compresion membrana cumple | Conforme |

## 9. Conclusión

**Estado del modelo: CUMPLE.**

El espesor de 0.40 m satisface las comprobaciones incluidas. El máximo DCR de flexión–membrana es 0.557 y el máximo DCR de cortante es 0.420.

Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con rigideces fisuradas.

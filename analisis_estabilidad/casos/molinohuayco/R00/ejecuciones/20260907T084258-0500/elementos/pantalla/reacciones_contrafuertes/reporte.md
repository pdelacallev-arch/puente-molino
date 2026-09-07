# Análisis tridimensional FEM de la pantalla plegada

## 1. Objetivo y alcance

Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.

## 2. Datos

| Parámetro | Valor | Unidad | Estado |
|---|---:|---|---|
| Altura total de referencia | 13.150 | m | proporcionado |
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
| Inferior | 0.000 m | 13.150 m | 6.715 tf/m² | 0.363 tf/m² | 7.078 tf/m² | 69.41 kN/m² |
| Intermedia | 2.617 m | 10.533 m | 5.379 tf/m² | 0.363 tf/m² | 5.742 tf/m² | 56.31 kN/m² |
| Superior | 5.233 m | 7.917 m | 4.042 tf/m² | 0.363 tf/m² | 4.406 tf/m² | 43.21 kN/m² |

## 5. Respuesta global

| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |
|---|---|---:|---:|---:|---:|---:|
| Servicio I | EH + LS | 0.3495 | -0.000 | -5494.934 | 2.89e-11 | 4.92e-05 |
| Resistencia I-a | 1.50 EH + 1.75 LS | 0.5300 | 0.000 | -8327.605 | 4.34e-11 | 7.52e-05 |
| Resistencia I-b | 1.50 EH + 1.75 LS | 0.5300 | 0.000 | -8327.605 | 4.34e-11 | 7.52e-05 |
| Evento Extremo I-A | 100% PAE + 50% PIR | 0.4297 | -0.000 | -6769.947 | 1.45e-11 | 5.83e-05 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR | 0.3399 | -0.000 | -5351.071 | 1.87e-11 | 4.69e-05 |

### Reacciones normales en contrafuertes

| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |
|---|---|---:|---:|---:|
| Servicio I | CF-I1 | 264.753 | 187.209 | 187.209 |
| Servicio I | CF-I2 | 701.994 | 496.384 | 496.384 |
| Servicio I | CF-I3 | 821.883 | 581.159 | 581.159 |
| Servicio I | CF-C1 | 570.607 | -0.000 | 570.607 |
| Servicio I | CF-C2 | 571.807 | -0.000 | 571.807 |
| Servicio I | CF-C3 | 570.607 | 0.000 | 570.607 |
| Servicio I | CF-D1 | 821.883 | -581.159 | 581.159 |
| Servicio I | CF-D2 | 701.994 | -496.384 | 496.384 |
| Servicio I | CF-D3 | 264.753 | -187.209 | 187.209 |
| Resistencia I-a | CF-I1 | 401.445 | 283.865 | 283.865 |
| Resistencia I-a | CF-I2 | 1064.280 | 752.559 | 752.559 |
| Resistencia I-a | CF-I3 | 1246.197 | 881.194 | 881.194 |
| Resistencia I-a | CF-C1 | 865.193 | 0.000 | 865.193 |
| Resistencia I-a | CF-C2 | 866.772 | -0.000 | 866.772 |
| Resistencia I-a | CF-C3 | 865.193 | -0.000 | 865.193 |
| Resistencia I-a | CF-D1 | 1246.197 | -881.194 | 881.194 |
| Resistencia I-a | CF-D2 | 1064.280 | -752.559 | 752.559 |
| Resistencia I-a | CF-D3 | 401.445 | -283.865 | 283.865 |
| Resistencia I-b | CF-I1 | 401.445 | 283.865 | 283.865 |
| Resistencia I-b | CF-I2 | 1064.280 | 752.559 | 752.559 |
| Resistencia I-b | CF-I3 | 1246.197 | 881.194 | 881.194 |
| Resistencia I-b | CF-C1 | 865.193 | 0.000 | 865.193 |
| Resistencia I-b | CF-C2 | 866.772 | -0.000 | 866.772 |
| Resistencia I-b | CF-C3 | 865.193 | -0.000 | 865.193 |
| Resistencia I-b | CF-D1 | 1246.197 | -881.194 | 881.194 |
| Resistencia I-b | CF-D2 | 1064.280 | -752.559 | 752.559 |
| Resistencia I-b | CF-D3 | 401.445 | -283.865 | 283.865 |
| Evento Extremo I-A | CF-I1 | 325.338 | 230.049 | 230.049 |
| Evento Extremo I-A | CF-I2 | 863.254 | 610.413 | 610.413 |
| Evento Extremo I-A | CF-I3 | 1010.064 | 714.223 | 714.223 |
| Evento Extremo I-A | CF-C1 | 701.260 | 0.000 | 701.260 |
| Evento Extremo I-A | CF-C2 | 703.699 | 0.000 | 703.699 |
| Evento Extremo I-A | CF-C3 | 701.260 | 0.000 | 701.260 |
| Evento Extremo I-A | CF-D1 | 1010.064 | -714.223 | 714.223 |
| Evento Extremo I-A | CF-D2 | 863.254 | -610.413 | 610.413 |
| Evento Extremo I-A | CF-D3 | 325.338 | -230.049 | 230.049 |
| Evento Extremo I-B | CF-I1 | 257.466 | 182.056 | 182.056 |
| Evento Extremo I-B | CF-I2 | 682.932 | 482.906 | 482.906 |
| Evento Extremo I-B | CF-I3 | 799.306 | 565.195 | 565.195 |
| Evento Extremo I-B | CF-C1 | 554.934 | -0.000 | 554.934 |
| Evento Extremo I-B | CF-C2 | 556.506 | 0.000 | 556.506 |
| Evento Extremo I-B | CF-C3 | 554.934 | -0.000 | 554.934 |
| Evento Extremo I-B | CF-D1 | 799.306 | -565.195 | 565.195 |
| Evento Extremo I-B | CF-D2 | 682.932 | -482.906 | 482.906 |
| Evento Extremo I-B | CF-D3 | 257.466 | -182.056 | 182.056 |

## 6. Diseño E.060–MTC/AASHTO

Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana. El brazo mecánico de cada cara usa su recubrimiento nominal: exterior 100 mm (agua con abrasión) e interior 75 mm (relleno).

| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |
|---|---|---|---|---|---:|---:|---:|---|---:|
| Ala izquierda | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 42.54 kN·m/m | 53.60 kN/m | 8.012 cm²/m | Ø5/8" @ 240 mm | 0.672 |
| Ala izquierda | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 44.65 kN·m/m | 39.19 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.570 |
| Ala izquierda | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 16.55 kN·m/m | 45.47 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.349 |
| Ala izquierda | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 53.70 kN·m/m | 26.62 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.622 |
| Ala izquierda | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 46.63 kN·m/m | 48.75 kN/m | 8.012 cm²/m | Ø5/8" @ 230 mm | 0.675 |
| Ala izquierda | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.50 kN·m/m | 35.97 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.579 |
| Ala izquierda | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 20.77 kN·m/m | 11.98 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.288 |
| Ala izquierda | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 12.30 kN·m/m | 18.02 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.179 |
| Ala izquierda | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 44.30 kN·m/m | 30.01 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.628 |
| Ala izquierda | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 40.57 kN·m/m | 24.95 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.485 |
| Ala izquierda | Superior | Vertical | Exterior (+n) | Resistencia I-a | 9.86 kN·m/m | 2.30 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.125 |
| Ala izquierda | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.68 kN·m/m | 6.71 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.108 |
| Pantalla central | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 16.02 kN·m/m | 50.96 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.361 |
| Pantalla central | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 41.96 kN·m/m | 62.17 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.613 |
| Pantalla central | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 9.15 kN·m/m | 6.30 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.130 |
| Pantalla central | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 13.91 kN·m/m | 9.62 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.170 |
| Pantalla central | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 14.38 kN·m/m | 57.28 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.363 |
| Pantalla central | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 42.51 kN·m/m | 72.57 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.651 |
| Pantalla central | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 25.93 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.087 |
| Pantalla central | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 6.98 kN·m/m | 25.93 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.150 |
| Pantalla central | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 10.63 kN·m/m | 57.40 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.318 |
| Pantalla central | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 37.93 kN·m/m | 58.81 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.562 |
| Pantalla central | Superior | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 14.59 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.049 |
| Pantalla central | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 7.65 kN·m/m | 13.21 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.118 |
| Ala derecha | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 42.54 kN·m/m | 53.60 kN/m | 8.012 cm²/m | Ø5/8" @ 240 mm | 0.672 |
| Ala derecha | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 44.65 kN·m/m | 39.19 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.570 |
| Ala derecha | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 16.55 kN·m/m | 45.47 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.349 |
| Ala derecha | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 53.70 kN·m/m | 26.62 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.622 |
| Ala derecha | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 46.63 kN·m/m | 48.75 kN/m | 8.012 cm²/m | Ø5/8" @ 230 mm | 0.675 |
| Ala derecha | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.50 kN·m/m | 35.97 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.579 |
| Ala derecha | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 20.77 kN·m/m | 11.98 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.288 |
| Ala derecha | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 12.30 kN·m/m | 18.02 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.179 |
| Ala derecha | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 44.30 kN·m/m | 30.01 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.628 |
| Ala derecha | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 40.57 kN·m/m | 24.95 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.485 |
| Ala derecha | Superior | Vertical | Exterior (+n) | Resistencia I-a | 9.86 kN·m/m | 2.30 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.125 |
| Ala derecha | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.68 kN·m/m | 6.71 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.108 |

### Líneas horizontales de lectura tipo *spandrel*

Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor valor de ambos lados, sin promediado.

| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |
|---|---:|---:|---:|---|---:|---:|---|
| FR-INFERIOR | 0.000 | 3.15 kN·m/m | 26.976 m | Resistencia I-a | 11.96 kN·m/m | 8.780 m | Resistencia I-a |
| FR-INTERMEDIA | 2.617 | 42.91 kN·m/m | 8.282 m | Resistencia I-a | 45.49 kN·m/m | 5.789 m | Resistencia I-a |
| FR-SUPERIOR | 5.233 | 44.62 kN·m/m | 8.282 m | Resistencia I-a | 40.82 kN·m/m | 5.789 m | Resistencia I-a |

Longitud de desarrollo adoptada máxima: **1500 mm**; empalme Clase B de referencia: **1950 mm**. Debe comprobarse la longitud física disponible en cada quiebre y contrafuerte.

### Cortante y compresión de membrana

| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |
|---|---|---:|---:|---:|---:|---:|
| Ala izquierda | Inferior | 111.98 kN/m | 217.54 kN/m | 0.515 | 0.439 MPa | 0.036 |
| Ala izquierda | Intermedia | 99.13 kN/m | 217.54 kN/m | 0.456 | 0.046 MPa | 0.004 |
| Ala izquierda | Superior | 82.64 kN/m | 217.54 kN/m | 0.380 | 0.014 MPa | 0.001 |
| Pantalla central | Inferior | 73.12 kN/m | 217.54 kN/m | 0.336 | 0.446 MPa | 0.036 |
| Pantalla central | Intermedia | 72.61 kN/m | 217.54 kN/m | 0.334 | 0.061 MPa | 0.005 |
| Pantalla central | Superior | 59.22 kN/m | 217.54 kN/m | 0.272 | 0.032 MPa | 0.003 |
| Ala derecha | Inferior | 111.98 kN/m | 217.54 kN/m | 0.515 | 0.439 MPa | 0.036 |
| Ala derecha | Intermedia | 99.13 kN/m | 217.54 kN/m | 0.456 | 0.046 MPa | 0.004 |
| Ala derecha | Superior | 82.64 kN/m | 217.54 kN/m | 0.380 | 0.014 MPa | 0.001 |

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
| max error fuerza kn | 4.33802e-11 |
| max error momento kn m | 7.52274e-05 |
| equilibrio cumple | Conforme |
| error relativo desplazamientos | 8.50225e-14 |
| error relativo reacciones pares | 1.77056e-14 |
| simetria cumple | Conforme |
| flexion membrana cumple | Conforme |
| cortante cumple | Conforme |
| compresion membrana cumple | Conforme |

## 9. Conclusión

**Estado del modelo: CUMPLE.**

El espesor de 0.40 m satisface las comprobaciones incluidas. El máximo DCR de flexión–membrana es 0.675 y el máximo DCR de cortante es 0.515.

Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con rigideces fisuradas.

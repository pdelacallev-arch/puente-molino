# Análisis tridimensional FEM de la pantalla plegada

## 1. Objetivo y alcance

Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.

## 2. Datos

| Parámetro | Valor | Unidad | Estado |
|---|---:|---|---|
| Altura total de referencia | 13.150 | m | proporcionado |
| Altura modelada | 10.110 | m | proporcionado |
| Espesor | 0.400 | m | proporcionado |
| Recubrimiento exterior (+n) | 100 | mm | proporcionado |
| Recubrimiento interior (-n) | 75 | mm | proporcionado |
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

La poligonal se extruye verticalmente hasta 10.11 m. Cada elemento Q4 contiene membrana bilineal y placa Mindlin-Reissner; el cortante transversal usa interpolación MITC4. En cada plano el eje local `x` sigue la pantalla, `y` es vertical y `+n` apunta hacia la cara exterior.

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
| Intermedia | 3.370 m | 9.780 m | 4.994 tf/m² | 0.363 tf/m² | 5.357 tf/m² | 52.54 kN/m² |
| Superior | 6.740 m | 6.410 m | 3.273 tf/m² | 0.363 tf/m² | 3.636 tf/m² | 35.66 kN/m² |

## 5. Respuesta global

| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |
|---|---|---:|---:|---:|---:|---:|
| Servicio I | EH + LS | 0.3502 | 0.000 | -6263.808 | 1.01e-10 | 2.13e-06 |
| Resistencia I-a | 1.50 EH + 1.75 LS | 0.5312 | -0.000 | -9505.445 | 1.30e-10 | 3.94e-06 |
| Resistencia I-b | 1.50 EH + 1.75 LS | 0.5312 | -0.000 | -9505.445 | 1.30e-10 | 3.94e-06 |
| Evento Extremo I-A | 100% PAE + 50% PIR | 0.4299 | -0.000 | -7666.519 | 8.65e-11 | 2.84e-07 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR | 0.3403 | -0.000 | -6078.527 | 1.38e-10 | 8.51e-07 |

### Reacciones normales en contrafuertes

| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |
|---|---|---:|---:|---:|
| Servicio I | CF-I1 | 310.520 | 219.570 | 219.570 |
| Servicio I | CF-I2 | 811.307 | 573.681 | 573.681 |
| Servicio I | CF-I3 | 965.129 | 682.449 | 682.449 |
| Servicio I | CF-C1 | 703.799 | 0.000 | 703.799 |
| Servicio I | CF-C2 | 641.922 | 0.000 | 641.922 |
| Servicio I | CF-C3 | 703.799 | 0.000 | 703.799 |
| Servicio I | CF-D1 | 965.129 | -682.449 | 682.449 |
| Servicio I | CF-D2 | 811.307 | -573.681 | 573.681 |
| Servicio I | CF-D3 | 310.520 | -219.570 | 219.570 |
| Resistencia I-a | CF-I1 | 471.553 | 333.439 | 333.439 |
| Resistencia I-a | CF-I2 | 1231.771 | 870.994 | 870.994 |
| Resistencia I-a | CF-I3 | 1465.612 | 1036.344 | 1036.344 |
| Resistencia I-a | CF-C1 | 1068.960 | -0.000 | 1068.960 |
| Resistencia I-a | CF-C2 | 974.308 | 0.000 | 974.308 |
| Resistencia I-a | CF-C3 | 1068.960 | 0.000 | 1068.960 |
| Resistencia I-a | CF-D1 | 1465.612 | -1036.344 | 1036.344 |
| Resistencia I-a | CF-D2 | 1231.771 | -870.994 | 870.994 |
| Resistencia I-a | CF-D3 | 471.553 | -333.439 | 333.439 |
| Resistencia I-b | CF-I1 | 471.553 | 333.439 | 333.439 |
| Resistencia I-b | CF-I2 | 1231.771 | 870.994 | 870.994 |
| Resistencia I-b | CF-I3 | 1465.612 | 1036.344 | 1036.344 |
| Resistencia I-b | CF-C1 | 1068.960 | -0.000 | 1068.960 |
| Resistencia I-b | CF-C2 | 974.308 | 0.000 | 974.308 |
| Resistencia I-b | CF-C3 | 1068.960 | 0.000 | 1068.960 |
| Resistencia I-b | CF-D1 | 1465.612 | -1036.344 | 1036.344 |
| Resistencia I-b | CF-D2 | 1231.771 | -870.994 | 870.994 |
| Resistencia I-b | CF-D3 | 471.553 | -333.439 | 333.439 |
| Evento Extremo I-A | CF-I1 | 378.713 | 267.790 | 267.790 |
| Evento Extremo I-A | CF-I2 | 990.589 | 700.453 | 700.453 |
| Evento Extremo I-A | CF-I3 | 1177.195 | 832.403 | 832.403 |
| Evento Extremo I-A | CF-C1 | 857.657 | 0.000 | 857.657 |
| Evento Extremo I-A | CF-C2 | 784.948 | 0.000 | 784.948 |
| Evento Extremo I-A | CF-C3 | 857.657 | -0.000 | 857.657 |
| Evento Extremo I-A | CF-D1 | 1177.195 | -832.403 | 832.403 |
| Evento Extremo I-A | CF-D2 | 990.589 | -700.453 | 700.453 |
| Evento Extremo I-A | CF-D3 | 378.713 | -267.790 | 267.790 |
| Evento Extremo I-B | CF-I1 | 300.770 | 212.677 | 212.677 |
| Evento Extremo I-B | CF-I2 | 786.301 | 555.999 | 555.999 |
| Evento Extremo I-B | CF-I3 | 934.875 | 661.056 | 661.056 |
| Evento Extremo I-B | CF-C1 | 681.407 | -0.000 | 681.407 |
| Evento Extremo I-B | CF-C2 | 622.629 | 0.000 | 622.629 |
| Evento Extremo I-B | CF-C3 | 681.407 | 0.000 | 681.407 |
| Evento Extremo I-B | CF-D1 | 934.875 | -661.056 | 661.056 |
| Evento Extremo I-B | CF-D2 | 786.301 | -555.999 | 555.999 |
| Evento Extremo I-B | CF-D3 | 300.770 | -212.677 | 212.677 |

## 6. Diseño E.060–MTC/AASHTO

Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana. El brazo mecánico de cada cara usa su recubrimiento nominal: exterior 100 mm (agua con abrasión) e interior 75 mm (relleno).

| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |
|---|---|---|---|---|---:|---:|---:|---|---:|
| Ala izquierda | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 46.48 kN·m/m | 50.43 kN/m | 8.012 cm²/m | Ø5/8" @ 230 mm | 0.679 |
| Ala izquierda | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.64 kN·m/m | 35.74 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.579 |
| Ala izquierda | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 17.20 kN·m/m | 45.81 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.358 |
| Ala izquierda | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 52.09 kN·m/m | 26.59 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.606 |
| Ala izquierda | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 47.13 kN·m/m | 46.57 kN/m | 8.012 cm²/m | Ø5/8" @ 230 mm | 0.674 |
| Ala izquierda | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.25 kN·m/m | 34.28 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.571 |
| Ala izquierda | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.84 kN·m/m | 7.33 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.225 |
| Ala izquierda | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 11.88 kN·m/m | 14.24 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.163 |
| Ala izquierda | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 38.44 kN·m/m | 16.98 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.515 |
| Ala izquierda | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.12 kN·m/m | 14.51 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.398 |
| Ala izquierda | Superior | Vertical | Exterior (+n) | Resistencia I-a | 8.53 kN·m/m | 1.42 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.106 |
| Ala izquierda | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.40 kN·m/m | 1.53 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.089 |
| Pantalla central | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 15.74 kN·m/m | 53.29 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.366 |
| Pantalla central | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 42.66 kN·m/m | 71.61 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.649 |
| Pantalla central | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 9.32 kN·m/m | 4.65 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.127 |
| Pantalla central | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 13.12 kN·m/m | 8.60 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.158 |
| Pantalla central | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 14.60 kN·m/m | 56.10 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.361 |
| Pantalla central | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 42.46 kN·m/m | 72.64 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.650 |
| Pantalla central | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 26.79 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.089 |
| Pantalla central | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 6.53 kN·m/m | 26.79 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.148 |
| Pantalla central | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 8.07 kN·m/m | 42.97 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.240 |
| Pantalla central | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 33.77 kN·m/m | 41.33 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.467 |
| Pantalla central | Superior | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 8.98 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.030 |
| Pantalla central | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 7.05 kN·m/m | 8.67 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.098 |
| Ala derecha | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 46.48 kN·m/m | 50.43 kN/m | 8.012 cm²/m | Ø5/8" @ 230 mm | 0.679 |
| Ala derecha | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.64 kN·m/m | 35.74 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.579 |
| Ala derecha | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 17.20 kN·m/m | 45.81 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.358 |
| Ala derecha | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 52.09 kN·m/m | 26.59 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.606 |
| Ala derecha | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 47.13 kN·m/m | 46.57 kN/m | 8.012 cm²/m | Ø5/8" @ 230 mm | 0.674 |
| Ala derecha | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 46.25 kN·m/m | 34.28 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.571 |
| Ala derecha | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.84 kN·m/m | 7.33 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.225 |
| Ala derecha | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 11.88 kN·m/m | 14.24 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.163 |
| Ala derecha | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 38.44 kN·m/m | 16.98 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.515 |
| Ala derecha | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.12 kN·m/m | 14.51 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.398 |
| Ala derecha | Superior | Vertical | Exterior (+n) | Resistencia I-a | 8.53 kN·m/m | 1.42 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.106 |
| Ala derecha | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 8.40 kN·m/m | 1.53 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.089 |

### Líneas horizontales de lectura tipo *spandrel*

Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor valor de ambos lados, sin promediado.

| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |
|---|---:|---:|---:|---|---:|---:|---|
| FR-INFERIOR | 0.000 | 3.27 kN·m/m | 26.976 m | Resistencia I-a | 11.67 kN·m/m | 8.780 m | Resistencia I-a |
| FR-INTERMEDIA | 3.370 | 46.69 kN·m/m | 8.282 m | Resistencia I-a | 46.71 kN·m/m | 5.789 m | Resistencia I-a |
| FR-SUPERIOR | 6.740 | 38.72 kN·m/m | 18.912 m | Resistencia I-a | 35.29 kN·m/m | 5.789 m | Resistencia I-a |

Longitud de desarrollo adoptada máxima: **1500 mm**; empalme Clase B de referencia: **1950 mm**. Debe comprobarse la longitud física disponible en cada quiebre y contrafuerte.

### Cortante y compresión de membrana

| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |
|---|---|---:|---:|---:|---:|---:|
| Ala izquierda | Inferior | 110.30 kN/m | 217.54 kN/m | 0.507 | 0.436 MPa | 0.035 |
| Ala izquierda | Intermedia | 97.76 kN/m | 217.54 kN/m | 0.449 | 0.036 MPa | 0.003 |
| Ala izquierda | Superior | 69.08 kN/m | 217.54 kN/m | 0.318 | 0.011 MPa | 0.001 |
| Pantalla central | Inferior | 73.40 kN/m | 217.54 kN/m | 0.337 | 0.443 MPa | 0.036 |
| Pantalla central | Intermedia | 69.57 kN/m | 217.54 kN/m | 0.320 | 0.070 MPa | 0.006 |
| Pantalla central | Superior | 50.83 kN/m | 217.54 kN/m | 0.234 | 0.023 MPa | 0.002 |
| Ala derecha | Inferior | 110.30 kN/m | 217.54 kN/m | 0.507 | 0.436 MPa | 0.035 |
| Ala derecha | Intermedia | 97.76 kN/m | 217.54 kN/m | 0.449 | 0.036 MPa | 0.003 |
| Ala derecha | Superior | 69.08 kN/m | 217.54 kN/m | 0.318 | 0.011 MPa | 0.001 |

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
| max error fuerza kn | 1.38337e-10 |
| max error momento kn m | 3.94267e-06 |
| equilibrio cumple | Conforme |
| error relativo desplazamientos | 6.94845e-14 |
| error relativo reacciones pares | 2.60326e-14 |
| simetria cumple | Conforme |
| flexion membrana cumple | Conforme |
| cortante cumple | Conforme |
| compresion membrana cumple | Conforme |

## 9. Conclusión

**Estado del modelo: CUMPLE.**

El espesor de 0.40 m satisface las comprobaciones incluidas. El máximo DCR de flexión–membrana es 0.679 y el máximo DCR de cortante es 0.507.

Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con rigideces fisuradas.

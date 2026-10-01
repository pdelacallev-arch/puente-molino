# Análisis tridimensional FEM de la pantalla plegada

## 1. Objetivo y alcance

Analizar de forma independiente la pantalla central y las alas con elementos finitos tipo cascarón, respetando los cambios de dirección reales en planta. Se excluyen la cajuela y el diseño de los contrafuertes.

## 2. Datos

| Parámetro | Valor | Unidad | Estado |
|---|---:|---|---|
| Altura total de referencia | 11.320 | m | proporcionado |
| Altura modelada | 8.280 | m | proporcionado |
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

La poligonal se extruye verticalmente hasta 8.28 m. Cada elemento Q4 contiene membrana bilineal y placa Mindlin-Reissner; el cortante transversal usa interpolación MITC4. En cada plano el eje local `x` sigue la pantalla, `y` es vertical y `+n` apunta hacia la cara exterior.

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
| Inferior | 0.000 m | 11.320 m | 5.780 tf/m² | 0.363 tf/m² | 6.144 tf/m² | 60.25 kN/m² |
| Intermedia | 2.760 m | 8.560 m | 4.371 tf/m² | 0.363 tf/m² | 4.734 tf/m² | 46.43 kN/m² |
| Superior | 5.520 m | 5.800 m | 2.962 tf/m² | 0.363 tf/m² | 3.325 tf/m² | 32.61 kN/m² |

## 5. Respuesta global

| Caso | Escenario | d máx. (mm) | Fx carga (kN) | Fy carga (kN) | Error F (kN) | Error M (kN·m) |
|---|---|---:|---:|---:|---:|---:|
| Servicio I | EH + LS | 0.2820 | -0.000 | -4590.778 | 1.03e-11 | 2.23e-05 |
| Resistencia I-a | 1.50 EH + 1.75 LS | 0.4287 | -0.000 | -6976.038 | 1.44e-11 | 3.46e-05 |
| Resistencia I-b | 1.50 EH + 1.75 LS | 0.4287 | -0.000 | -6976.038 | 1.44e-11 | 3.46e-05 |
| Evento Extremo I-A | 100% PAE + 50% PIR | 0.3430 | -0.000 | -5580.840 | 2.22e-11 | 2.41e-05 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR | 0.2727 | 0.000 | -4439.034 | 3.24e-11 | 2.03e-05 |

### Reacciones normales en contrafuertes

| Caso | Apoyo | R normal (kN) | Rx (kN) | Ry (kN) |
|---|---|---:|---:|---:|
| Servicio I | CF-I1 | 219.995 | 155.560 | 155.560 |
| Servicio I | CF-I2 | 583.113 | 412.323 | 412.323 |
| Servicio I | CF-I3 | 683.136 | 483.050 | 483.050 |
| Servicio I | CF-C1 | 478.957 | -0.000 | 478.957 |
| Servicio I | CF-C2 | 473.801 | 0.000 | 473.801 |
| Servicio I | CF-C3 | 478.957 | -0.000 | 478.957 |
| Servicio I | CF-D1 | 683.136 | -483.050 | 483.050 |
| Servicio I | CF-D2 | 583.113 | -412.323 | 412.323 |
| Servicio I | CF-D3 | 219.995 | -155.560 | 155.560 |
| Resistencia I-a | CF-I1 | 334.585 | 236.587 | 236.587 |
| Resistencia I-a | CF-I2 | 886.627 | 626.940 | 626.940 |
| Resistencia I-a | CF-I3 | 1038.933 | 734.636 | 734.636 |
| Resistencia I-a | CF-C1 | 728.440 | -0.000 | 728.440 |
| Resistencia I-a | CF-C2 | 720.223 | -0.000 | 720.223 |
| Resistencia I-a | CF-C3 | 728.440 | 0.000 | 728.440 |
| Resistencia I-a | CF-D1 | 1038.933 | -734.636 | 734.636 |
| Resistencia I-a | CF-D2 | 886.627 | -626.940 | 626.940 |
| Resistencia I-a | CF-D3 | 334.585 | -236.587 | 236.587 |
| Resistencia I-b | CF-I1 | 334.585 | 236.587 | 236.587 |
| Resistencia I-b | CF-I2 | 886.627 | 626.940 | 626.940 |
| Resistencia I-b | CF-I3 | 1038.933 | 734.636 | 734.636 |
| Resistencia I-b | CF-C1 | 728.440 | -0.000 | 728.440 |
| Resistencia I-b | CF-C2 | 720.223 | -0.000 | 720.223 |
| Resistencia I-b | CF-C3 | 728.440 | 0.000 | 728.440 |
| Resistencia I-b | CF-D1 | 1038.933 | -734.636 | 734.636 |
| Resistencia I-b | CF-D2 | 886.627 | -626.940 | 626.940 |
| Resistencia I-b | CF-D3 | 334.585 | -236.587 | 236.587 |
| Evento Extremo I-A | CF-I1 | 266.287 | 188.294 | 188.294 |
| Evento Extremo I-A | CF-I2 | 706.686 | 499.703 | 499.703 |
| Evento Extremo I-A | CF-I3 | 827.022 | 584.793 | 584.793 |
| Evento Extremo I-A | CF-C1 | 579.727 | 0.000 | 579.727 |
| Evento Extremo I-A | CF-C2 | 574.994 | 0.000 | 574.994 |
| Evento Extremo I-A | CF-C3 | 579.727 | -0.000 | 579.727 |
| Evento Extremo I-A | CF-D1 | 827.022 | -584.793 | 584.793 |
| Evento Extremo I-A | CF-D2 | 706.686 | -499.703 | 499.703 |
| Evento Extremo I-A | CF-D3 | 266.287 | -188.294 | 188.294 |
| Evento Extremo I-B | CF-I1 | 212.239 | 150.076 | 150.076 |
| Evento Extremo I-B | CF-I2 | 562.922 | 398.046 | 398.046 |
| Evento Extremo I-B | CF-I3 | 659.111 | 466.062 | 466.062 |
| Evento Extremo I-B | CF-C1 | 462.066 | -0.000 | 462.066 |
| Evento Extremo I-B | CF-C2 | 457.725 | -0.000 | 457.725 |
| Evento Extremo I-B | CF-C3 | 462.066 | 0.000 | 462.066 |
| Evento Extremo I-B | CF-D1 | 659.111 | -466.062 | 466.062 |
| Evento Extremo I-B | CF-D2 | 562.922 | -398.046 | 398.046 |
| Evento Extremo I-B | CF-D3 | 212.239 | -150.076 | 150.076 |

## 6. Diseño E.060–MTC/AASHTO

Se adopta el mayor acero requerido, la menor capacidad de cortante y los límites de separación y desarrollo más exigentes. El índice DCR combina conservadoramente flexión Wood-Armer y tracción de membrana. El brazo mecánico de cada cara usa su recubrimiento nominal: exterior 100 mm (agua con abrasión) e interior 75 mm (relleno).

| Región | Zona | Dirección | Cara | Caso | Mu WA | Nu cara | As req. | Armado | DCR |
|---|---|---|---|---|---:|---:|---:|---|---:|
| Ala izquierda | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 36.14 kN·m/m | 43.89 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.577 |
| Ala izquierda | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 38.00 kN·m/m | 29.41 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.473 |
| Ala izquierda | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 19.98 kN·m/m | 18.13 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.299 |
| Ala izquierda | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 44.48 kN·m/m | 22.30 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.516 |
| Ala izquierda | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 37.83 kN·m/m | 41.65 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.590 |
| Ala izquierda | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 38.37 kN·m/m | 28.78 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.475 |
| Ala izquierda | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.69 kN·m/m | 8.66 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.228 |
| Ala izquierda | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 10.23 kN·m/m | 13.33 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.144 |
| Ala izquierda | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 33.92 kN·m/m | 20.79 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.474 |
| Ala izquierda | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 30.81 kN·m/m | 17.30 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.363 |
| Ala izquierda | Superior | Vertical | Exterior (+n) | Resistencia I-a | 7.54 kN·m/m | 2.02 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.097 |
| Ala izquierda | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 7.02 kN·m/m | 2.58 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.079 |
| Pantalla central | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 13.36 kN·m/m | 43.55 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.305 |
| Pantalla central | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 35.02 kN·m/m | 53.46 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.517 |
| Pantalla central | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 7.95 kN·m/m | 5.42 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.113 |
| Pantalla central | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 11.59 kN·m/m | 8.65 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.143 |
| Pantalla central | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 12.65 kN·m/m | 44.83 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.300 |
| Pantalla central | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 34.71 kN·m/m | 60.39 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.535 |
| Pantalla central | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 22.98 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.077 |
| Pantalla central | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 5.84 kN·m/m | 22.18 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.127 |
| Pantalla central | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 7.87 kN·m/m | 43.28 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.238 |
| Pantalla central | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 29.04 kN·m/m | 43.42 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.426 |
| Pantalla central | Superior | Vertical | Exterior (+n) | Resistencia I-a | 0.00 kN·m/m | 11.19 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.037 |
| Pantalla central | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 5.87 kN·m/m | 10.43 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.091 |
| Ala derecha | Inferior | Horizontal | Exterior (+n) | Resistencia I-a | 36.14 kN·m/m | 43.89 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.577 |
| Ala derecha | Inferior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 38.00 kN·m/m | 29.41 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.473 |
| Ala derecha | Inferior | Vertical | Exterior (+n) | Resistencia I-a | 19.98 kN·m/m | 18.13 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.299 |
| Ala derecha | Inferior | Vertical | Interior/relleno (-n) | Resistencia I-a | 44.48 kN·m/m | 22.30 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.516 |
| Ala derecha | Intermedia | Horizontal | Exterior (+n) | Resistencia I-a | 37.83 kN·m/m | 41.65 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.590 |
| Ala derecha | Intermedia | Horizontal | Interior/relleno (-n) | Resistencia I-a | 38.37 kN·m/m | 28.78 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.475 |
| Ala derecha | Intermedia | Vertical | Exterior (+n) | Resistencia I-a | 16.69 kN·m/m | 8.66 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.228 |
| Ala derecha | Intermedia | Vertical | Interior/relleno (-n) | Resistencia I-a | 10.23 kN·m/m | 13.33 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.144 |
| Ala derecha | Superior | Horizontal | Exterior (+n) | Resistencia I-a | 33.92 kN·m/m | 20.79 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.474 |
| Ala derecha | Superior | Horizontal | Interior/relleno (-n) | Resistencia I-a | 30.81 kN·m/m | 17.30 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.363 |
| Ala derecha | Superior | Vertical | Exterior (+n) | Resistencia I-a | 7.54 kN·m/m | 2.02 kN/m | 8.012 cm²/m | Ø5/8" @ 245 mm | 0.097 |
| Ala derecha | Superior | Vertical | Interior/relleno (-n) | Resistencia I-a | 7.02 kN·m/m | 2.58 kN/m | 8.710 cm²/m | Ø5/8" @ 225 mm | 0.079 |

### Líneas horizontales de lectura tipo *spandrel*

Las tres líneas siguen la coordenada desarrollada `s` de la pantalla. Se reporta la envolvente factorizada Wood-Armer horizontal por cara; para una franja de 1.00 m el valor numérico en kN·m/m coincide con el momento de la franja en kN·m. En bordes entre filas se adopta el mayor valor de ambos lados, sin promediado.

| Línea | z (m) | Mu exterior máx. | s | Caso | Mu interior máx. | s | Caso |
|---|---:|---:|---:|---|---:|---:|---|
| FR-INFERIOR | 0.000 | 2.73 kN·m/m | 26.976 m | Resistencia I-a | 9.94 kN·m/m | 18.413 m | Resistencia I-a |
| FR-INTERMEDIA | 2.760 | 36.44 kN·m/m | 18.912 m | Resistencia I-a | 38.18 kN·m/m | 21.405 m | Resistencia I-a |
| FR-SUPERIOR | 5.520 | 34.23 kN·m/m | 18.912 m | Resistencia I-a | 30.94 kN·m/m | 21.405 m | Resistencia I-a |

Longitud de desarrollo adoptada máxima: **1500 mm**; empalme Clase B de referencia: **1950 mm**. Debe comprobarse la longitud física disponible en cada quiebre y contrafuerte.

### Cortante y compresión de membrana

| Región | Zona | Q máx. | φVc adoptado | DCR V | σc membrana | DCR comp. |
|---|---|---:|---:|---:|---:|---:|
| Ala izquierda | Inferior | 94.56 kN/m | 217.54 kN/m | 0.435 | 0.356 MPa | 0.029 |
| Ala izquierda | Intermedia | 82.62 kN/m | 217.54 kN/m | 0.380 | 0.035 MPa | 0.003 |
| Ala izquierda | Superior | 62.50 kN/m | 217.54 kN/m | 0.287 | 0.011 MPa | 0.001 |
| Pantalla central | Inferior | 61.56 kN/m | 217.54 kN/m | 0.283 | 0.362 MPa | 0.029 |
| Pantalla central | Intermedia | 60.08 kN/m | 217.54 kN/m | 0.276 | 0.053 MPa | 0.004 |
| Pantalla central | Superior | 44.96 kN/m | 217.54 kN/m | 0.207 | 0.026 MPa | 0.002 |
| Ala derecha | Inferior | 94.56 kN/m | 217.54 kN/m | 0.435 | 0.356 MPa | 0.029 |
| Ala derecha | Intermedia | 82.62 kN/m | 217.54 kN/m | 0.380 | 0.035 MPa | 0.003 |
| Ala derecha | Superior | 62.50 kN/m | 217.54 kN/m | 0.287 | 0.011 MPa | 0.001 |

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
| max error fuerza kn | 3.24407e-11 |
| max error momento kn m | 3.45895e-05 |
| equilibrio cumple | Conforme |
| error relativo desplazamientos | 7.45324e-14 |
| error relativo reacciones pares | 1.00684e-14 |
| simetria cumple | Conforme |
| flexion membrana cumple | Conforme |
| cortante cumple | Conforme |
| compresion membrana cumple | Conforme |

## 9. Conclusión

**Estado del modelo: CUMPLE.**

El espesor de 0.40 m satisface las comprobaciones incluidas. El máximo DCR de flexión–membrana es 0.590 y el máximo DCR de cortante es 0.435.

Este resultado supone base empotrada, unión monolítica en los quiebres y contrafuertes rígidos en la dirección normal. La rigidez real de zapata y contrafuertes debe confirmarse antes de emitir el detalle constructivo definitivo; para esa etapa también conviene contrastar una variante con rigideces fisuradas.

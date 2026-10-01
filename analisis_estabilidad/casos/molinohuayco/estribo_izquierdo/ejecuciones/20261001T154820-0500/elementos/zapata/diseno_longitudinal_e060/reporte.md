# Diseño de la zapata del estribo — NTE E.060

## Datos de entrada

| Categoría | Parámetro | Valor | Unidad | Fuente |
|---|---|---:|---|---|
| Geometría | Ancho total B | 11.950 | m | agente |
| Geometría | Punta B2 | 5.450 | m | agente |
| Geometría | Pantalla tp2 | 0.400 | m | agente |
| Geometría | Talón B1 | 6.100 | m | agente |
| Geometría | Espesor h | 1.500 | m | agente |
| Geometría | Altura de pantalla hp | 11.320 | m | agente |
| Geometría | Peralte efectivo d | 1.3621 | m | calculado |
| Geometría | Diámetro individual de control para d | 25.400 | mm | criterio conservador |
| Geometría | Distancia al centroide de acero de control | 137.900 | mm | dos capas cuando corresponda |
| Material | f'c | 280.0 | kgf/cm² | agente |
| Material | fy | 4200.0 | kgf/cm² | agente |
| Material | Peso del concreto | 2.400 | tf/m³ | agente |
| Material | Peso del relleno | 1.800 | tf/m³ | agente |
| Diseño | Recubrimiento | 100.0 | mm | bloque editable |
| Diseño | Selección longitudinal | automática | — | bloque editable |
| Diseño | Catálogo longitudinal | 5/8", 3/4", 1", 2Ø1" | — | bloque editable |
| Diseño | Selección transversal | automática | — | bloque editable |
| Diseño | Catálogo transversal | 3/4" | — | bloque editable |
| Diseño | Espaciamiento mínimo constructivo | 75 | mm | bloque editable |
| Diseño | Separación libre vertical entre capas | 25 | mm | bloque editable |
| Diseño | Espaciamiento máximo | 400 | mm | bloque editable |
| Diseño | Barras empalmadas dentro de la longitud de traslape | 50 | % | bloque editable |
| Diseño | Longitud del estribo | 6.000 | m | bloque editable |
| Diseño | Ancho de franja | 1.000 | m | bloque editable |
| Resistencia | φ flexión | 0.90 | — | NTE E.060 |
| Resistencia | φ cortante | 0.85 | — | NTE E.060 |
| Análisis | Interfaz | interface_1 | — | bloque editable |
| Análisis | Casos | case_resistance_Ia, case_resistance_Ib, case_extreme_event_I | — | bloque editable |

## Solicitaciones y cortante

| Caso | Zona | q borde/cara (tf/m²) | Mu firmado (tf·m/m) | Cara tracción | As calc. (cm²/m) | Vu (tf/m) | φVc (tf/m) | D/C |
|---|---|---:|---:|---|---:|---:|---:|---:|
| Resistencia I-a | punta | 14.774 / 19.160 | 193.005 | inferior | 38.443 | 53.873 | 105.171 | 0.512 |
| Resistencia I-a | talon | 24.390 / 19.481 | -49.647 | superior | 9.704 | 14.463 | 105.171 | 0.138 |
| Resistencia I-b | punta | 15.766 / 24.830 | 212.184 | inferior | 42.374 | 59.950 | 105.171 | 0.570 |
| Resistencia I-b | talon | 35.640 / 25.495 | -28.390 | superior | 5.534 | 10.555 | 105.171 | 0.100 |
| Evento Extremo I (Sismo) | punta | 14.336 / 16.196 | 173.996 | inferior | 34.568 | 48.211 | 105.171 | 0.458 |
| Evento Extremo I (Sismo) | talon | 18.414 / 16.332 | -108.114 | superior | 21.292 | 28.477 | 105.171 | 0.271 |

Convención: Mu positivo = reacción ascendente dominante y tracción inferior; Mu negativo = cargas descendentes dominantes y tracción superior.

## Armado propuesto y verificación de áreas

**Estado del armado:** CUMPLE.

`As normativo` es el mínimo asignado al armado correspondiente. Para el acero longitudinal se usa el mínimo por cara de E.060 10.5.4; para el transversal, la mitad del acero de retracción y temperatura de E.060 9.7.

La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Longitudinal — punta, cara superior | mínimo / distribución | 0.000 cm²/m | 18.000 cm²/m | mínimo de flexión por cara (E.060 10.5.4) | 18.000 cm²/m | Ø5/8" @ 100 mm | 19.793 cm²/m | 0.909 | Sí |
| Longitudinal — punta, cara inferior | Resistencia I-b | 42.374 cm²/m | 18.000 cm²/m | demanda de flexión | 42.374 cm²/m | Ø1" @ 110 mm | 46.064 cm²/m | 0.920 | Sí |
| Longitudinal — talon, cara superior | Evento Extremo I (Sismo) | 21.292 cm²/m | 18.000 cm²/m | demanda de flexión | 21.292 cm²/m | Ø5/8" @ 90 mm | 21.993 cm²/m | 0.968 | Sí |
| Longitudinal — talon, cara inferior | mínimo / distribución | 0.000 cm²/m | 18.000 cm²/m | mínimo de flexión por cara (E.060 10.5.4) | 18.000 cm²/m | Ø5/8" @ 100 mm | 19.793 cm²/m | 0.909 | Sí |
| Transversal — cara superior | mínimo / distribución | 0.000 cm²/m | 13.500 cm²/m | retracción y temperatura por cara (E.060 9.7) | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |
| Transversal — cara inferior | mínimo / distribución | 0.000 cm²/m | 13.500 cm²/m | retracción y temperatura por cara (E.060 9.7) | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |

## Desarrollo y anclajes

| Dirección/zona | Cara | Barra | ld requerida | Recta disponible | Cumple | Gancho 90°: ldg / extensión / doblado | Anclaje adoptado |
|---|---|---:|---:|---:|:---:|---:|---|
| longitudinal / punta | superior | Ø5/8" | 624 mm | 6400 mm | Sí | 210 / 190 / 95 mm | barra continua con desarrollo recto al otro lado de la cara crítica; gancho estándar de 90° en el borde exterior |
| longitudinal / punta | inferior | Ø1" | 951 mm | 6400 mm | Sí | 335 / 305 / 152 mm | barra continua con desarrollo recto al otro lado de la cara crítica; gancho estándar de 90° en el borde exterior |
| longitudinal / talon | superior | Ø5/8" | 624 mm | 5750 mm | Sí | 210 / 190 / 95 mm | barra continua con desarrollo recto al otro lado de la cara crítica; gancho estándar de 90° en el borde exterior |
| longitudinal / talon | inferior | Ø5/8" | 480 mm | 5750 mm | Sí | 210 / 190 / 95 mm | barra continua con desarrollo recto al otro lado de la cara crítica; gancho estándar de 90° en el borde exterior |
| transversal / ancho_total_del_estribo | superior | Ø3/4" | 749 mm | 2900 mm | Sí | 252 / 229 / 114 mm | barra continua en el ancho del estribo; gancho estándar de 90° en ambos extremos |
| transversal / ancho_total_del_estribo | inferior | Ø3/4" | 576 mm | 2900 mm | Sí | 252 / 229 / 114 mm | barra continua en el ancho del estribo; gancho estándar de 90° en ambos extremos |

## Empalmes por traslape

| ID | Dirección/zona | Signo/cara | Barra | As prov./req. | % empalmado | Clase | ld base | Factor | Traslape requerido | Traslape adoptado |
|---|---|---|---:|---:|---:|:---:|---:|---:|---:|---:|
| L1 | longitudinal / punta | negativo / superior | Ø5/8" | 19.793 / 18.000 = 1.100 | 50% | B | 624 mm | 1.3 | 811 mm | 850 mm |
| L2 | longitudinal / punta | positivo / inferior | Ø1" | 46.064 / 42.374 = 1.087 | 50% | B | 951 mm | 1.3 | 1236 mm | 1250 mm |
| L3 | longitudinal / talon | negativo / superior | Ø5/8" | 21.993 / 21.292 = 1.033 | 50% | B | 624 mm | 1.3 | 811 mm | 850 mm |
| L4 | longitudinal / talon | positivo / inferior | Ø5/8" | 19.793 / 18.000 = 1.100 | 50% | B | 480 mm | 1.3 | 624 mm | 650 mm |
| T1 | transversal / ancho_total_del_estribo | distribución / superior | Ø3/4" | 13.573 / 13.500 = 1.005 | 50% | B | 749 mm | 1.3 | 973 mm | 1000 mm |
| T2 | transversal / ancho_total_del_estribo | distribución / inferior | Ø3/4" | 13.573 / 13.500 = 1.005 | 50% | B | 576 mm | 1.3 | 749 mm | 750 mm |

## Detalle constructivo recomendado

- Punta — momento negativo, cara superior: Ø5/8" @ 100 mm; prolongar 650 mm después de la cara crítica y rematar el borde exterior con gancho de 90° (ldg 250 mm, extensión 200 mm, doblado interior 95 mm).
- Punta — momento positivo, cara inferior: Ø1" @ 110 mm; prolongar 1000 mm después de la cara crítica y rematar el borde exterior con gancho de 90° (ldg 350 mm, extensión 350 mm, doblado interior 152 mm).
- Talon — momento negativo, cara superior: Ø5/8" @ 90 mm; prolongar 650 mm después de la cara crítica y rematar el borde exterior con gancho de 90° (ldg 250 mm, extensión 200 mm, doblado interior 95 mm).
- Talon — momento positivo, cara inferior: Ø5/8" @ 100 mm; prolongar 500 mm después de la cara crítica y rematar el borde exterior con gancho de 90° (ldg 250 mm, extensión 200 mm, doblado interior 95 mm).
- Transversal, cara superior: Ø3/4" @ 210 mm, continuo en los 6.00 m; gancho de 90° en ambos extremos (ldg 300 mm, extensión 250 mm, doblado interior 114 mm).
- Transversal, cara inferior: Ø3/4" @ 210 mm, continuo en los 6.00 m; gancho de 90° en ambos extremos (ldg 300 mm, extensión 250 mm, doblado interior 114 mm).
- Empalme L1, Ø5/8", longitudinal / punta, cara superior: Clase B, traslape adoptado 850 mm; ubicar fuera de la sección de máximo momento y alternar los empalmes conforme al porcentaje especificado.
- Empalme L2, Ø1", longitudinal / punta, cara inferior: Clase B, traslape adoptado 1250 mm; ubicar fuera de la sección de máximo momento y alternar los empalmes conforme al porcentaje especificado.
- Empalme L3, Ø5/8", longitudinal / talon, cara superior: Clase B, traslape adoptado 850 mm; ubicar fuera de la sección de máximo momento y alternar los empalmes conforme al porcentaje especificado.
- Empalme L4, Ø5/8", longitudinal / talon, cara inferior: Clase B, traslape adoptado 650 mm; ubicar fuera de la sección de máximo momento y alternar los empalmes conforme al porcentaje especificado.
- Empalme T1, Ø3/4", transversal / ancho_total_del_estribo, cara superior: Clase B, traslape adoptado 1000 mm; ubicar fuera de la sección de máximo momento y alternar los empalmes conforme al porcentaje especificado.
- Empalme T2, Ø3/4", transversal / ancho_total_del_estribo, cara inferior: Clase B, traslape adoptado 750 mm; ubicar fuera de la sección de máximo momento y alternar los empalmes conforme al porcentaje especificado.

Acero mínimo total E.060: 27.000 cm²/m.

## Alcance y pendientes

- Las combinaciones de carga factorizadas proceden del análisis de puente; E.060 se usa para la resistencia de la sección de concreto armado.
- El acero mínimo se reparte conservadoramente en ambas caras: rho=0.0012 por cara; la suma supera rho=0.0018 total.
- El peralte efectivo se calculó conservadoramente con una distancia de 137.900 mm desde la cara de tracción hasta el centroide del arreglo longitudinal de control.
- La selección automática adopta el primer arreglo del catálogo que permite cumplir As sin bajar del espaciamiento mínimo constructivo configurado.
- Los arreglos de dos barras se disponen en dos capas con 25 mm de separación libre vertical; el peralte efectivo usa el centroide conjunto.
- Las longitudes de desarrollo suponen barras sin recubrimiento epóxico, concreto normal y separaciones favorables según la Tabla 12.1.
- Los empalmes por traslape se calcularon a tracción según E.060 12.15 y Tabla 12.3, suponiendo como máximo 50% de barras empalmadas dentro de la longitud de traslape requerida.
- La ubicación exacta de los empalmes debe definirse en planos fuera de las secciones de máximo momento y coordinarse con cortes, ganchos y juntas de construcción.
- Confirmar en planos la longitud ingresada del estribo (6.00 m) y la compatibilidad de los ganchos con las demás armaduras.
- Punzonamiento no aplica al modelo de pantalla continua; comprobarlo por separado si existen cargas concentradas o contrafuertes.

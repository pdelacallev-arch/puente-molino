# Diseño transversal de la zapata en el extremo del talón — E.060 y MTC

## 1. Objetivo y alcance

Diseñar por flexión y cortante una franja transversal de 1.00 m situada en el extremo del talón, mediante una viga continua desplegada sobre los ejes de los contrafuertes.

El armado final se obtiene envolviendo demanda, mínimos, temperatura, distribución, fisuración, desarrollo, empalmes y anclajes de E.060 y MTC.

## 2. Datos e idealización

| Dato | Valor | Unidad | Fuente |
|---|---:|---|---|
| Ancho total B | 11.950 | m | agente |
| Talón B1 | 6.100 | m | agente |
| Franja x | 10.950 a 11.950 | m | calculado |
| Espesor de zapata | 1.500 | m | agente |
| Longitud desplegada | 27.140 | m | geometría de pantalla |
| Vanos | 3.00, 3.00, 4.77, 2.80, 2.80, 4.77, 3.00, 3.00 | m | ejes de contrafuertes |
| f'c | 280.0 | kgf/cm² | agente |
| fy | 4200.0 | kgf/cm² | agente |
| Recubrimiento superior/inferior | 100 / 100 | mm | adoptado |

La presión de contacto se integra exactamente en el último metro del talón. De la reacción bruta se descuentan el peso local factorizado de la zapata, el relleno y la sobrecarga. Las fuerzas de pantalla y contrafuertes quedan representadas por las reacciones de los apoyos.

## 3. Cargas de la franja

| Caso | q inicio | q talón | q media | Reacción bruta | Zapata | Relleno | Sobrecarga | w neta ascendente |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 26.845 | 28.812 | 27.424 | 27.424 | 3.600 | 24.912 | 1.098 | -2.186 |
| Resistencia I-a | 23.239 | 23.665 | 23.364 | 23.364 | 3.240 | 24.912 | 1.921 | -6.709 |
| Resistencia I-b | 34.859 | 36.982 | 35.483 | 35.483 | 4.500 | 33.631 | 1.921 | -4.570 |
| Evento Extremo I (Sismo) | 17.584 | 17.110 | 17.444 | 17.444 | 3.240 | 24.912 | 0.000 | -10.708 |

Todas las cargas de la tabla están expresadas en tf/m transversal.

## 4. Análisis matricial

La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.

| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |
|---|---:|---:|---:|---:|---:|
| Servicio I | -2.186 | 2.748 | 3.590 | 5.264 | 7.11e-15 |
| Resistencia I-a | -6.709 | 8.432 | 11.018 | 16.155 | 0.00e+00 |
| Resistencia I-b | -4.570 | 5.743 | 7.504 | 11.003 | 0.00e+00 |
| Evento Extremo I (Sismo) | -10.708 | 13.456 | 17.584 | 25.783 | 5.68e-14 |

### Resultados por vano

| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 1 | 3.00 | -0.000 | -1.622 | 1.716 | -1.622 | 2.739 | -3.820 |
| Servicio I | 2 | 3.00 | -1.622 | -3.352 | 0.049 | -3.352 | 2.703 | -3.856 |
| Servicio I | 3 | 4.77 | -3.352 | -3.590 | 2.748 | -3.590 | 5.164 | -5.264 |
| Servicio I | 4 | 2.80 | -3.590 | -0.347 | 0.480 | -3.590 | 4.219 | -1.903 |
| Servicio I | 5 | 2.80 | -0.347 | -3.590 | 0.480 | -3.590 | 1.903 | -4.219 |
| Servicio I | 6 | 4.77 | -3.590 | -3.352 | 2.748 | -3.590 | 5.264 | -5.164 |
| Servicio I | 7 | 3.00 | -3.352 | -1.622 | 0.049 | -3.352 | 3.856 | -2.703 |
| Servicio I | 8 | 3.00 | -1.622 | -0.000 | 1.716 | -1.622 | 3.820 | -2.739 |
| Resistencia I-a | 1 | 3.00 | -0.000 | -4.976 | 5.265 | -4.976 | 8.405 | -11.723 |
| Resistencia I-a | 2 | 3.00 | -4.976 | -10.286 | 0.150 | -10.286 | 8.294 | -11.834 |
| Resistencia I-a | 3 | 4.77 | -10.286 | -11.018 | 8.432 | -11.018 | 15.848 | -16.155 |
| Resistencia I-a | 4 | 2.80 | -11.018 | -1.066 | 1.474 | -11.018 | 12.947 | -5.839 |
| Resistencia I-a | 5 | 2.80 | -1.066 | -11.018 | 1.474 | -11.018 | 5.839 | -12.947 |
| Resistencia I-a | 6 | 4.77 | -11.018 | -10.286 | 8.432 | -11.018 | 16.155 | -15.848 |
| Resistencia I-a | 7 | 3.00 | -10.286 | -4.976 | 0.150 | -10.286 | 11.834 | -8.294 |
| Resistencia I-a | 8 | 3.00 | -4.976 | 0.000 | 5.265 | -4.976 | 11.723 | -8.405 |
| Resistencia I-b | 1 | 3.00 | -0.000 | -3.389 | 3.586 | -3.389 | 5.724 | -7.984 |
| Resistencia I-b | 2 | 3.00 | -3.389 | -7.006 | 0.102 | -7.006 | 5.649 | -8.060 |
| Resistencia I-b | 3 | 4.77 | -7.006 | -7.504 | 5.743 | -7.504 | 10.794 | -11.003 |
| Resistencia I-b | 4 | 2.80 | -7.504 | -0.726 | 1.004 | -7.504 | 8.818 | -3.977 |
| Resistencia I-b | 5 | 2.80 | -0.726 | -7.504 | 1.004 | -7.504 | 3.977 | -8.818 |
| Resistencia I-b | 6 | 4.77 | -7.504 | -7.006 | 5.743 | -7.504 | 11.003 | -10.794 |
| Resistencia I-b | 7 | 3.00 | -7.006 | -3.389 | 0.102 | -7.006 | 8.060 | -5.649 |
| Resistencia I-b | 8 | 3.00 | -3.389 | -0.000 | 3.586 | -3.389 | 7.984 | -5.724 |
| Evento Extremo I (Sismo) | 1 | 3.00 | -0.000 | -7.942 | 8.402 | -7.942 | 13.414 | -18.709 |
| Evento Extremo I (Sismo) | 2 | 3.00 | -7.942 | -16.416 | 0.240 | -16.416 | 13.237 | -18.886 |
| Evento Extremo I (Sismo) | 3 | 4.77 | -16.416 | -17.584 | 13.456 | -17.584 | 25.293 | -25.783 |
| Evento Extremo I (Sismo) | 4 | 2.80 | -17.584 | -1.701 | 2.353 | -17.584 | 20.663 | -9.318 |
| Evento Extremo I (Sismo) | 5 | 2.80 | -1.701 | -17.584 | 2.353 | -17.584 | 9.318 | -20.663 |
| Evento Extremo I (Sismo) | 6 | 4.77 | -17.584 | -16.416 | 13.456 | -17.584 | 25.783 | -25.293 |
| Evento Extremo I (Sismo) | 7 | 3.00 | -16.416 | -7.942 | 0.240 | -16.416 | 18.886 | -13.237 |
| Evento Extremo I (Sismo) | 8 | 3.00 | -7.942 | 0.000 | 8.402 | -7.942 | 18.709 | -13.414 |

## 5. Envolvente de diseño

| Demanda | Valor | Posición s | Caso | Cara traccionada |
|---|---:|---:|---|---|
| M_u negativo | 17.584 tf·m | 16.370 m | Evento Extremo I (Sismo) | superior |
| M_u positivo | 13.456 tf·m | 18.778 m | Evento Extremo I (Sismo) | inferior |

## 6. Diseño E.060–MTC y armado final

**Estado del armado:** CUMPLE.

`As normativo` es la mayor exigencia no asociada directamente a la demanda de flexión entre E.060 y MTC. La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

### Armado propuesto y verificación de áreas

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal transversal — cara superior | Evento Extremo I (Sismo) | 3.360 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Principal transversal — cara inferior | Evento Extremo I (Sismo) | 2.570 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Distribución longitudinal — cara superior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |
| Distribución longitudinal — cara inferior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |

### Comparación normativa detallada del refuerzo principal

| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| superior | 17.584 | 3.360 | 18.000 | 13.500 | 4.472 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.179 |
| inferior | 13.456 | 2.570 | 18.000 | 13.500 | 3.420 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.137 |

### Acero longitudinal de distribución y temperatura

| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |
|---|---:|---:|---:|---|---|---:|
| superior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |
| inferior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |

### Cortante

| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |
|---|---:|---:|---:|---:|---|---:|---|
| Evento Extremo I (Sismo) | 25.783 | 107.117 | 99.674 | 99.674 | MTC/AASHTO | 0.259 | CUMPLE |

### Desarrollo, traslapes y ganchos estándar

| Cara | Barra | ld adoptado | Clase | Traslape | ldh E.060 | ldh MTC | ldh adoptado | Extensión 90° | Doblado interior |
|---|---:|---:|:---:|---:|---:|---:|---:|---:|---:|
| superior | Ø3/4" | 1800 mm | B | 2350 mm | 359 mm | 363 mm | 400 mm | 250 mm | 114 mm |
| inferior | Ø3/4" | 1400 mm | B | 1850 mm | 359 mm | 363 mm | 400 mm | 250 mm | 114 mm |

### Zonas de empalme para barras comerciales de 12 m

- Cara superior: s=8.00 m, s=18.80 m; interior de vanos con momento positivo; traslape 2350 mm; A/B alternados; centros separados 0.60 m.
- Cara inferior: s=10.77 m, s=16.37 m; sobre CF-C1 y CF-C3, zonas de momento negativo; traslape 1850 mm; A/B alternados; centros separados 0.60 m.

## 7. Verificaciones automáticas

| Verificación | Resultado |
|---|---|
| franja en extremo talon | CONFORME |
| ancho franja 1m | CONFORME |
| nueve apoyos | CONFORME |
| contacto completo todos casos | CONFORME |
| cargas netas no nulas | CONFORME |
| signo carga neta reportado | CONFORME |
| equilibrio matricial | CONFORME |
| max error equilibrio | 5.684e-14 |
| simetria | CONFORME |
| max error simetria | 3.553e-15 |
| flexion cumple | CONFORME |
| cortante cumple | CONFORME |
| fisuracion cumple | CONFORME |
| minimos y temperatura cumplen | CONFORME |
| armado reportado cumple | CONFORME |
| temperatura total E060 cumple | CONFORME |
| traslapes definidos | CONFORME |
| ganchos caben | CONFORME |

## 8. Limitaciones

- Los contrafuertes se idealizan como apoyos rígidos ubicados en sus ejes.
- El ancho real de los contrafuertes no está confirmado; el cortante se reporta conservadoramente en el eje.
- No se evalúa punzonamiento ni la unión tridimensional contrafuerte–zapata.
- El armado calculado debe compatibilizarse con el acero longitudinal existente.
- El diseño requiere revisión y aprobación del ingeniero responsable antes de construcción.

## 9. Conclusión

**Estado del análisis y diseño: CUMPLE.**

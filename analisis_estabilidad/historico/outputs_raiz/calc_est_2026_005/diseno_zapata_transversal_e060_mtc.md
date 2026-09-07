# Diseño transversal de la zapata en el extremo del talón — E.060 y MTC

## 1. Objetivo y alcance

Diseñar por flexión y cortante una franja transversal de 1.00 m situada en el extremo del talón, mediante una viga continua desplegada sobre los ejes de los contrafuertes.

El armado final se obtiene envolviendo demanda, mínimos, temperatura, distribución, fisuración, desarrollo, empalmes y anclajes de E.060 y MTC.

## 2. Datos e idealización

| Dato | Valor | Unidad | Fuente |
|---|---:|---|---|
| Ancho total B | 12.650 | m | agente |
| Talón B1 | 6.100 | m | agente |
| Franja x | 11.650 a 12.650 | m | calculado |
| Espesor de zapata | 1.500 | m | agente |
| Longitud desplegada | 27.140 | m | geometría de pantalla |
| Vanos | 3.00, 3.00, 4.77, 2.80, 2.80, 4.77, 3.00, 3.00 | m | ejes de contrafuertes |
| f'c | 280.0 | kgf/cm² | agente |
| fy | 4200.0 | kgf/cm² | agente |
| Recubrimiento superior/inferior | 75 / 75 | mm | adoptado |

La presión de contacto se integra exactamente en el último metro del talón. De la reacción bruta se descuentan el peso local factorizado de la zapata, el relleno y la sobrecarga. Las fuerzas de pantalla y contrafuertes quedan representadas por las reacciones de los apoyos.

## 3. Cargas de la franja

| Caso | q inicio | q talón | q media | Reacción bruta | Zapata | Relleno | Sobrecarga | w neta ascendente |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 27.907 | 29.413 | 28.660 | 28.660 | 3.600 | 23.670 | 1.098 | 0.292 |
| Resistencia I-a | 24.773 | 25.592 | 25.183 | 25.183 | 3.240 | 23.670 | 1.921 | -3.649 |
| Resistencia I-b | 36.456 | 38.254 | 37.355 | 37.355 | 4.500 | 31.955 | 1.921 | -1.021 |
| Evento Extremo I (Sismo) | 18.875 | 19.154 | 19.014 | 19.014 | 3.240 | 23.670 | 0.000 | -7.896 |

Todas las cargas de la tabla están expresadas en tf/m transversal.

## 4. Análisis matricial

La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.

| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |
|---|---:|---:|---:|---:|---:|
| Servicio I | 0.292 | 0.479 | 0.367 | 0.703 | 8.88e-16 |
| Resistencia I-a | -3.649 | 4.586 | 5.992 | 8.786 | 2.27e-13 |
| Resistencia I-b | -1.021 | 1.283 | 1.677 | 2.459 | 0.00e+00 |
| Evento Extremo I (Sismo) | -7.896 | 9.922 | 12.966 | 19.011 | 0.00e+00 |

### Resultados por vano

| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 1 | 3.00 | 0.000 | 0.217 | 0.217 | -0.229 | -0.366 | 0.510 |
| Servicio I | 2 | 3.00 | 0.217 | 0.448 | 0.448 | -0.007 | -0.361 | 0.515 |
| Servicio I | 3 | 4.77 | 0.448 | 0.479 | 0.479 | -0.367 | -0.690 | 0.703 |
| Servicio I | 4 | 2.80 | 0.479 | 0.046 | 0.479 | -0.064 | -0.563 | 0.254 |
| Servicio I | 5 | 2.80 | 0.046 | 0.479 | 0.479 | -0.064 | -0.254 | 0.563 |
| Servicio I | 6 | 4.77 | 0.479 | 0.448 | 0.479 | -0.367 | -0.703 | 0.690 |
| Servicio I | 7 | 3.00 | 0.448 | 0.217 | 0.448 | -0.007 | -0.515 | 0.361 |
| Servicio I | 8 | 3.00 | 0.217 | -0.000 | 0.217 | -0.229 | -0.510 | 0.366 |
| Resistencia I-a | 1 | 3.00 | -0.000 | -2.707 | 2.863 | -2.707 | 4.571 | -6.376 |
| Resistencia I-a | 2 | 3.00 | -2.707 | -5.594 | 0.082 | -5.594 | 4.511 | -6.436 |
| Resistencia I-a | 3 | 4.77 | -5.594 | -5.992 | 4.586 | -5.992 | 8.619 | -8.786 |
| Resistencia I-a | 4 | 2.80 | -5.992 | -0.580 | 0.802 | -5.992 | 7.042 | -3.176 |
| Resistencia I-a | 5 | 2.80 | -0.580 | -5.992 | 0.802 | -5.992 | 3.176 | -7.042 |
| Resistencia I-a | 6 | 4.77 | -5.992 | -5.594 | 4.586 | -5.992 | 8.786 | -8.619 |
| Resistencia I-a | 7 | 3.00 | -5.594 | -2.707 | 0.082 | -5.594 | 6.436 | -4.511 |
| Resistencia I-a | 8 | 3.00 | -2.707 | 0.000 | 2.863 | -2.707 | 6.376 | -4.571 |
| Resistencia I-b | 1 | 3.00 | -0.000 | -0.757 | 0.801 | -0.757 | 1.279 | -1.784 |
| Resistencia I-b | 2 | 3.00 | -0.757 | -1.565 | 0.023 | -1.565 | 1.262 | -1.801 |
| Resistencia I-b | 3 | 4.77 | -1.565 | -1.677 | 1.283 | -1.677 | 2.412 | -2.459 |
| Resistencia I-b | 4 | 2.80 | -1.677 | -0.162 | 0.224 | -1.677 | 1.970 | -0.889 |
| Resistencia I-b | 5 | 2.80 | -0.162 | -1.677 | 0.224 | -1.677 | 0.889 | -1.970 |
| Resistencia I-b | 6 | 4.77 | -1.677 | -1.565 | 1.283 | -1.677 | 2.459 | -2.412 |
| Resistencia I-b | 7 | 3.00 | -1.565 | -0.757 | 0.023 | -1.565 | 1.801 | -1.262 |
| Resistencia I-b | 8 | 3.00 | -0.757 | 0.000 | 0.801 | -0.757 | 1.784 | -1.279 |
| Evento Extremo I (Sismo) | 1 | 3.00 | 0.000 | -5.856 | 6.196 | -5.856 | 9.891 | -13.795 |
| Evento Extremo I (Sismo) | 2 | 3.00 | -5.856 | -12.105 | 0.177 | -12.105 | 9.761 | -13.926 |
| Evento Extremo I (Sismo) | 3 | 4.77 | -12.105 | -12.966 | 9.922 | -12.966 | 18.650 | -19.011 |
| Evento Extremo I (Sismo) | 4 | 2.80 | -12.966 | -1.255 | 1.735 | -12.966 | 15.236 | -6.871 |
| Evento Extremo I (Sismo) | 5 | 2.80 | -1.255 | -12.966 | 1.735 | -12.966 | 6.871 | -15.236 |
| Evento Extremo I (Sismo) | 6 | 4.77 | -12.966 | -12.105 | 9.922 | -12.966 | 19.011 | -18.650 |
| Evento Extremo I (Sismo) | 7 | 3.00 | -12.105 | -5.856 | 0.177 | -12.105 | 13.926 | -9.761 |
| Evento Extremo I (Sismo) | 8 | 3.00 | -5.856 | 0.000 | 6.196 | -5.856 | 13.795 | -9.891 |

## 5. Envolvente de diseño

| Demanda | Valor | Posición s | Caso | Cara traccionada |
|---|---:|---:|---|---|
| M_u negativo | 12.966 tf·m | 16.370 m | Evento Extremo I (Sismo) | superior |
| M_u positivo | 9.922 tf·m | 18.778 m | Evento Extremo I (Sismo) | inferior |

## 6. Diseño E.060–MTC y armado final

**Estado del armado:** CUMPLE.

`As normativo` es la mayor exigencia no asociada directamente a la demanda de flexión entre E.060 y MTC. La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

### Armado propuesto y verificación de áreas

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal transversal — cara superior | Evento Extremo I (Sismo) | 2.432 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Principal transversal — cara inferior | Evento Extremo I (Sismo) | 1.861 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Distribución longitudinal — cara superior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |
| Distribución longitudinal — cara inferior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |

### Comparación normativa detallada del refuerzo principal

| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| superior | 12.966 | 2.432 | 18.000 | 13.500 | 3.237 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.129 |
| inferior | 9.922 | 1.861 | 18.000 | 13.500 | 2.476 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.099 |

### Acero longitudinal de distribución y temperatura

| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |
|---|---:|---:|---:|---|---|---:|
| superior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |
| inferior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |

### Cortante

| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |
|---|---:|---:|---:|---:|---|---:|---|
| Evento Extremo I (Sismo) | 19.011 | 109.047 | 101.470 | 101.470 | MTC/AASHTO | 0.187 | CUMPLE |

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
| max error equilibrio | 2.274e-13 |
| simetria | CONFORME |
| max error simetria | 0.000e+00 |
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

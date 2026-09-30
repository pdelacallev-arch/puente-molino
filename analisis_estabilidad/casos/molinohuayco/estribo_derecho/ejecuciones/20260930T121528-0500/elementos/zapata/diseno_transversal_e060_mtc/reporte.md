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
| Recubrimiento superior/inferior | 100 / 100 | mm | adoptado |

La presión de contacto se integra exactamente en el último metro del talón. De la reacción bruta se descuentan el peso local factorizado de la zapata, el relleno y la sobrecarga. Las fuerzas de pantalla y contrafuertes quedan representadas por las reacciones de los apoyos.

## 3. Cargas de la franja

| Caso | q inicio | q talón | q media | Reacción bruta | Zapata | Relleno | Sobrecarga | w neta ascendente |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 27.923 | 29.439 | 28.681 | 28.681 | 3.600 | 23.670 | 1.098 | 0.313 |
| Resistencia I-a | 24.804 | 25.633 | 25.219 | 25.219 | 3.240 | 23.670 | 1.921 | -3.613 |
| Resistencia I-b | 36.486 | 38.296 | 37.391 | 37.391 | 4.500 | 31.955 | 1.921 | -0.985 |
| Evento Extremo I (Sismo) | 18.942 | 19.239 | 19.091 | 19.091 | 3.240 | 23.670 | 0.000 | -7.819 |

Todas las cargas de la tabla están expresadas en tf/m transversal.

## 4. Análisis matricial

La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.

| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |
|---|---:|---:|---:|---:|---:|
| Servicio I | 0.313 | 0.514 | 0.394 | 0.754 | 1.42e-14 |
| Resistencia I-a | -3.613 | 4.540 | 5.933 | 8.699 | 0.00e+00 |
| Resistencia I-b | -0.985 | 1.238 | 1.618 | 2.372 | 5.68e-14 |
| Evento Extremo I (Sismo) | -7.819 | 9.827 | 12.841 | 18.828 | 0.00e+00 |

### Resultados por vano

| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 1 | 3.00 | 0.000 | 0.232 | 0.232 | -0.246 | -0.392 | 0.547 |
| Servicio I | 2 | 3.00 | 0.232 | 0.480 | 0.480 | -0.007 | -0.387 | 0.552 |
| Servicio I | 3 | 4.77 | 0.480 | 0.514 | 0.514 | -0.394 | -0.740 | 0.754 |
| Servicio I | 4 | 2.80 | 0.514 | 0.050 | 0.514 | -0.069 | -0.604 | 0.273 |
| Servicio I | 5 | 2.80 | 0.050 | 0.514 | 0.514 | -0.069 | -0.273 | 0.604 |
| Servicio I | 6 | 4.77 | 0.514 | 0.480 | 0.514 | -0.394 | -0.754 | 0.740 |
| Servicio I | 7 | 3.00 | 0.480 | 0.232 | 0.480 | -0.007 | -0.552 | 0.387 |
| Servicio I | 8 | 3.00 | 0.232 | -0.000 | 0.232 | -0.246 | -0.547 | 0.392 |
| Resistencia I-a | 1 | 3.00 | -0.000 | -2.680 | 2.835 | -2.680 | 4.526 | -6.313 |
| Resistencia I-a | 2 | 3.00 | -2.680 | -5.539 | 0.081 | -5.539 | 4.466 | -6.372 |
| Resistencia I-a | 3 | 4.77 | -5.539 | -5.933 | 4.540 | -5.933 | 8.534 | -8.699 |
| Resistencia I-a | 4 | 2.80 | -5.933 | -0.574 | 0.794 | -5.933 | 6.972 | -3.144 |
| Resistencia I-a | 5 | 2.80 | -0.574 | -5.933 | 0.794 | -5.933 | 3.144 | -6.972 |
| Resistencia I-a | 6 | 4.77 | -5.933 | -5.539 | 4.540 | -5.933 | 8.699 | -8.534 |
| Resistencia I-a | 7 | 3.00 | -5.539 | -2.680 | 0.081 | -5.539 | 6.372 | -4.466 |
| Resistencia I-a | 8 | 3.00 | -2.680 | 0.000 | 2.835 | -2.680 | 6.313 | -4.526 |
| Resistencia I-b | 1 | 3.00 | -0.000 | -0.731 | 0.773 | -0.731 | 1.234 | -1.721 |
| Resistencia I-b | 2 | 3.00 | -0.731 | -1.510 | 0.022 | -1.510 | 1.218 | -1.737 |
| Resistencia I-b | 3 | 4.77 | -1.510 | -1.618 | 1.238 | -1.618 | 2.327 | -2.372 |
| Resistencia I-b | 4 | 2.80 | -1.618 | -0.157 | 0.216 | -1.618 | 1.901 | -0.857 |
| Resistencia I-b | 5 | 2.80 | -0.157 | -1.618 | 0.216 | -1.618 | 0.857 | -1.901 |
| Resistencia I-b | 6 | 4.77 | -1.618 | -1.510 | 1.238 | -1.618 | 2.372 | -2.327 |
| Resistencia I-b | 7 | 3.00 | -1.510 | -0.731 | 0.022 | -1.510 | 1.737 | -1.218 |
| Resistencia I-b | 8 | 3.00 | -0.731 | 0.000 | 0.773 | -0.731 | 1.721 | -1.234 |
| Evento Extremo I (Sismo) | 1 | 3.00 | -0.000 | -5.800 | 6.136 | -5.800 | 9.796 | -13.662 |
| Evento Extremo I (Sismo) | 2 | 3.00 | -5.800 | -11.988 | 0.175 | -11.988 | 9.666 | -13.792 |
| Evento Extremo I (Sismo) | 3 | 4.77 | -11.988 | -12.841 | 9.827 | -12.841 | 18.470 | -18.828 |
| Evento Extremo I (Sismo) | 4 | 2.80 | -12.841 | -1.242 | 1.718 | -12.841 | 15.090 | -6.805 |
| Evento Extremo I (Sismo) | 5 | 2.80 | -1.242 | -12.841 | 1.718 | -12.841 | 6.805 | -15.090 |
| Evento Extremo I (Sismo) | 6 | 4.77 | -12.841 | -11.988 | 9.827 | -12.841 | 18.828 | -18.470 |
| Evento Extremo I (Sismo) | 7 | 3.00 | -11.988 | -5.800 | 0.175 | -11.988 | 13.792 | -9.666 |
| Evento Extremo I (Sismo) | 8 | 3.00 | -5.800 | 0.000 | 6.136 | -5.800 | 13.662 | -9.796 |

## 5. Envolvente de diseño

| Demanda | Valor | Posición s | Caso | Cara traccionada |
|---|---:|---:|---|---|
| M_u negativo | 12.841 tf·m | 10.770 m | Evento Extremo I (Sismo) | superior |
| M_u positivo | 9.827 tf·m | 18.778 m | Evento Extremo I (Sismo) | inferior |

## 6. Diseño E.060–MTC y armado final

**Estado del armado:** CUMPLE.

`As normativo` es la mayor exigencia no asociada directamente a la demanda de flexión entre E.060 y MTC. La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

### Armado propuesto y verificación de áreas

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal transversal — cara superior | Evento Extremo I (Sismo) | 2.453 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Principal transversal — cara inferior | Evento Extremo I (Sismo) | 1.876 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Distribución longitudinal — cara superior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |
| Distribución longitudinal — cara inferior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |

### Comparación normativa detallada del refuerzo principal

| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| superior | 12.841 | 2.453 | 18.000 | 13.500 | 3.264 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.130 |
| inferior | 9.827 | 1.876 | 18.000 | 13.500 | 2.496 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.100 |

### Acero longitudinal de distribución y temperatura

| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |
|---|---:|---:|---:|---|---|---:|
| superior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |
| inferior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |

### Cortante

| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |
|---|---:|---:|---:|---:|---|---:|---|
| Evento Extremo I (Sismo) | 18.828 | 107.117 | 99.674 | 99.674 | MTC/AASHTO | 0.189 | CUMPLE |

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

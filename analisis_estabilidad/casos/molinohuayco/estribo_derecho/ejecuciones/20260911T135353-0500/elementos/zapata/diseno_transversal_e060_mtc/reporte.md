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
| Servicio I | 25.914 | 27.453 | 26.684 | 26.684 | 3.600 | 19.602 | 1.098 | 2.384 |
| Resistencia I-a | 24.245 | 25.366 | 24.805 | 24.805 | 3.240 | 19.602 | 1.921 | 0.042 |
| Resistencia I-b | 34.281 | 36.215 | 35.248 | 35.248 | 4.500 | 26.463 | 1.921 | 2.364 |
| Evento Extremo I (Sismo) | 18.771 | 19.433 | 19.102 | 19.102 | 3.240 | 19.602 | 0.000 | -3.740 |

Todas las cargas de la tabla están expresadas en tf/m transversal.

## 4. Análisis matricial

La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.

| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |
|---|---:|---:|---:|---:|---:|
| Servicio I | 2.384 | 3.914 | 2.996 | 5.739 | 0.00e+00 |
| Resistencia I-a | 0.042 | 0.069 | 0.053 | 0.101 | 1.78e-15 |
| Resistencia I-b | 2.364 | 3.882 | 2.971 | 5.692 | 1.14e-13 |
| Evento Extremo I (Sismo) | -3.740 | 4.700 | 6.142 | 9.005 | 0.00e+00 |

### Resultados por vano

| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 1 | 3.00 | -0.000 | 1.768 | 1.768 | -1.870 | -2.986 | 4.165 |
| Servicio I | 2 | 3.00 | 1.768 | 3.654 | 3.654 | -0.053 | -2.947 | 4.204 |
| Servicio I | 3 | 4.77 | 3.654 | 3.914 | 3.914 | -2.996 | -5.630 | 5.739 |
| Servicio I | 4 | 2.80 | 3.914 | 0.379 | 3.914 | -0.524 | -4.600 | 2.074 |
| Servicio I | 5 | 2.80 | 0.379 | 3.914 | 3.914 | -0.524 | -2.074 | 4.600 |
| Servicio I | 6 | 4.77 | 3.914 | 3.654 | 3.914 | -2.996 | -5.739 | 5.630 |
| Servicio I | 7 | 3.00 | 3.654 | 1.768 | 3.654 | -0.053 | -4.204 | 2.947 |
| Servicio I | 8 | 3.00 | 1.768 | -0.000 | 1.768 | -1.870 | -4.165 | 2.986 |
| Resistencia I-a | 1 | 3.00 | 0.000 | 0.031 | 0.031 | -0.033 | -0.053 | 0.073 |
| Resistencia I-a | 2 | 3.00 | 0.031 | 0.064 | 0.064 | -0.001 | -0.052 | 0.074 |
| Resistencia I-a | 3 | 4.77 | 0.064 | 0.069 | 0.069 | -0.053 | -0.099 | 0.101 |
| Resistencia I-a | 4 | 2.80 | 0.069 | 0.007 | 0.069 | -0.009 | -0.081 | 0.037 |
| Resistencia I-a | 5 | 2.80 | 0.007 | 0.069 | 0.069 | -0.009 | -0.037 | 0.081 |
| Resistencia I-a | 6 | 4.77 | 0.069 | 0.064 | 0.069 | -0.053 | -0.101 | 0.099 |
| Resistencia I-a | 7 | 3.00 | 0.064 | 0.031 | 0.064 | -0.001 | -0.074 | 0.052 |
| Resistencia I-a | 8 | 3.00 | 0.031 | -0.000 | 0.031 | -0.033 | -0.073 | 0.053 |
| Resistencia I-b | 1 | 3.00 | 0.000 | 1.753 | 1.753 | -1.855 | -2.962 | 4.131 |
| Resistencia I-b | 2 | 3.00 | 1.753 | 3.624 | 3.624 | -0.053 | -2.922 | 4.170 |
| Resistencia I-b | 3 | 4.77 | 3.624 | 3.882 | 3.882 | -2.971 | -5.584 | 5.692 |
| Resistencia I-b | 4 | 2.80 | 3.882 | 0.376 | 3.882 | -0.520 | -4.562 | 2.057 |
| Resistencia I-b | 5 | 2.80 | 0.376 | 3.882 | 3.882 | -0.520 | -2.057 | 4.562 |
| Resistencia I-b | 6 | 4.77 | 3.882 | 3.624 | 3.882 | -2.971 | -5.692 | 5.584 |
| Resistencia I-b | 7 | 3.00 | 3.624 | 1.753 | 3.624 | -0.053 | -4.170 | 2.922 |
| Resistencia I-b | 8 | 3.00 | 1.753 | -0.000 | 1.753 | -1.855 | -4.131 | 2.962 |
| Evento Extremo I (Sismo) | 1 | 3.00 | 0.000 | -2.774 | 2.935 | -2.774 | 4.685 | -6.535 |
| Evento Extremo I (Sismo) | 2 | 3.00 | -2.774 | -5.734 | 0.084 | -5.734 | 4.623 | -6.597 |
| Evento Extremo I (Sismo) | 3 | 4.77 | -5.734 | -6.142 | 4.700 | -6.142 | 8.834 | -9.005 |
| Evento Extremo I (Sismo) | 4 | 2.80 | -6.142 | -0.594 | 0.822 | -6.142 | 7.217 | -3.255 |
| Evento Extremo I (Sismo) | 5 | 2.80 | -0.594 | -6.142 | 0.822 | -6.142 | 3.255 | -7.217 |
| Evento Extremo I (Sismo) | 6 | 4.77 | -6.142 | -5.734 | 4.700 | -6.142 | 9.005 | -8.834 |
| Evento Extremo I (Sismo) | 7 | 3.00 | -5.734 | -2.774 | 0.084 | -5.734 | 6.597 | -4.623 |
| Evento Extremo I (Sismo) | 8 | 3.00 | -2.774 | 0.000 | 2.935 | -2.774 | 6.535 | -4.685 |

## 5. Envolvente de diseño

| Demanda | Valor | Posición s | Caso | Cara traccionada |
|---|---:|---:|---|---|
| M_u negativo | 6.142 tf·m | 16.370 m | Evento Extremo I (Sismo) | superior |
| M_u positivo | 4.700 tf·m | 8.362 m | Evento Extremo I (Sismo) | inferior |

## 6. Diseño E.060–MTC y armado final

**Estado del armado:** CUMPLE.

`As normativo` es la mayor exigencia no asociada directamente a la demanda de flexión entre E.060 y MTC. La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

### Armado propuesto y verificación de áreas

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal transversal — cara superior | Evento Extremo I (Sismo) | 1.172 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Principal transversal — cara inferior | Evento Extremo I (Sismo) | 0.897 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |
| Distribución longitudinal — cara superior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |
| Distribución longitudinal — cara inferior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø3/4" @ 210 mm | 13.573 cm²/m | 0.995 | Sí |

### Comparación normativa detallada del refuerzo principal

| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| superior | 6.142 | 1.172 | 18.000 | 13.500 | 1.559 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.062 |
| inferior | 4.700 | 0.897 | 18.000 | 13.500 | 1.193 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø3/4" @ 150 mm | 19.002 | 0.048 |

### Acero longitudinal de distribución y temperatura

| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |
|---|---:|---:|---:|---|---|---:|
| superior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |
| inferior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø3/4" @ 210 mm | 13.573 |

### Cortante

| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |
|---|---:|---:|---:|---:|---|---:|---|
| Evento Extremo I (Sismo) | 9.005 | 107.117 | 99.674 | 99.674 | MTC/AASHTO | 0.090 | CUMPLE |

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
| max error equilibrio | 1.137e-13 |
| simetria | CONFORME |
| max error simetria | 1.776e-15 |
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

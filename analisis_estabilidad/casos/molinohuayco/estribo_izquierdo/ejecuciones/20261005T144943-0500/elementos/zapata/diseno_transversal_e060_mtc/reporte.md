# Diseño transversal de la zapata en el extremo del talón — E.060 y MTC

## 1. Objetivo y alcance

Diseñar por flexión y cortante una franja transversal de 1.00 m situada en el extremo del talón, mediante una viga continua desplegada sobre los ejes de los contrafuertes.

El armado final se obtiene envolviendo demanda, mínimos, temperatura, distribución, fisuración, desarrollo, empalmes y anclajes de E.060 y MTC.

## 2. Datos e idealización

| Dato | Valor | Unidad | Fuente |
|---|---:|---|---|
| Ancho total B | 8.000 | m | agente |
| Talón B1 | 5.000 | m | agente |
| Franja x | 7.000 a 8.000 | m | calculado |
| Espesor de zapata | 1.200 | m | agente |
| Longitud desplegada | 27.140 | m | geometría de pantalla |
| Vanos | 3.00, 3.00, 4.77, 2.80, 2.80, 4.77, 3.00, 3.00 | m | ejes de contrafuertes |
| f'c | 280.0 | kgf/cm² | agente |
| fy | 4200.0 | kgf/cm² | agente |
| Recubrimiento superior/inferior | 100 / 100 | mm | adoptado |

La presión de contacto se integra exactamente en el último metro del talón. De la reacción bruta se descuentan el peso local factorizado de la zapata, el relleno y la sobrecarga. Las fuerzas de pantalla y contrafuertes quedan representadas por las reacciones de los apoyos.

## 3. Cargas de la franja

| Caso | q inicio | q talón | q media | Reacción bruta | Zapata | Relleno | Sobrecarga | w neta ascendente |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 22.589 | 16.883 | 22.084 | 22.084 | 2.880 | 20.916 | 1.098 | -2.810 |
| Resistencia I-a | 22.665 | 8.903 | 21.447 | 21.447 | 2.592 | 20.916 | 1.921 | -3.982 |
| Resistencia I-b | 30.454 | 19.783 | 29.509 | 29.509 | 3.600 | 28.237 | 1.921 | -4.249 |
| Evento Extremo I (Sismo) | 17.954 | 2.661 | 16.601 | 16.601 | 2.592 | 20.916 | 0.000 | -6.907 |

Todas las cargas de la tabla están expresadas en tf/m transversal.

## 4. Análisis matricial

La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.

| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |
|---|---:|---:|---:|---:|---:|
| Servicio I | -2.810 | 3.531 | 4.614 | 6.765 | 2.27e-13 |
| Resistencia I-a | -3.982 | 5.005 | 6.540 | 9.589 | 0.00e+00 |
| Resistencia I-b | -4.249 | 5.339 | 6.977 | 10.230 | 0.00e+00 |
| Evento Extremo I (Sismo) | -6.907 | 8.680 | 11.343 | 16.631 | 0.00e+00 |

### Resultados por vano

| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 1 | 3.00 | -0.000 | -2.084 | 2.205 | -2.084 | 3.520 | -4.909 |
| Servicio I | 2 | 3.00 | -2.084 | -4.308 | 0.063 | -4.308 | 3.473 | -4.956 |
| Servicio I | 3 | 4.77 | -4.308 | -4.614 | 3.531 | -4.614 | 6.637 | -6.765 |
| Servicio I | 4 | 2.80 | -4.614 | -0.446 | 0.617 | -4.614 | 5.422 | -2.445 |
| Servicio I | 5 | 2.80 | -0.446 | -4.614 | 0.617 | -4.614 | 2.445 | -5.422 |
| Servicio I | 6 | 4.77 | -4.614 | -4.308 | 3.531 | -4.614 | 6.765 | -6.637 |
| Servicio I | 7 | 3.00 | -4.308 | -2.084 | 0.063 | -4.308 | 4.956 | -3.473 |
| Servicio I | 8 | 3.00 | -2.084 | 0.000 | 2.205 | -2.084 | 4.909 | -3.520 |
| Resistencia I-a | 1 | 3.00 | -0.000 | -2.954 | 3.125 | -2.954 | 4.989 | -6.958 |
| Resistencia I-a | 2 | 3.00 | -2.954 | -6.106 | 0.089 | -6.106 | 4.923 | -7.024 |
| Resistencia I-a | 3 | 4.77 | -6.106 | -6.540 | 5.005 | -6.540 | 9.407 | -9.589 |
| Resistencia I-a | 4 | 2.80 | -6.540 | -0.633 | 0.875 | -6.540 | 7.685 | -3.466 |
| Resistencia I-a | 5 | 2.80 | -0.633 | -6.540 | 0.875 | -6.540 | 3.466 | -7.685 |
| Resistencia I-a | 6 | 4.77 | -6.540 | -6.106 | 5.005 | -6.540 | 9.589 | -9.407 |
| Resistencia I-a | 7 | 3.00 | -6.106 | -2.954 | 0.089 | -6.106 | 7.024 | -4.923 |
| Resistencia I-a | 8 | 3.00 | -2.954 | 0.000 | 3.125 | -2.954 | 6.958 | -4.989 |
| Resistencia I-b | 1 | 3.00 | 0.000 | -3.151 | 3.334 | -3.151 | 5.323 | -7.424 |
| Resistencia I-b | 2 | 3.00 | -3.151 | -6.514 | 0.095 | -6.514 | 5.252 | -7.494 |
| Resistencia I-b | 3 | 4.77 | -6.514 | -6.977 | 5.339 | -6.977 | 10.036 | -10.230 |
| Resistencia I-b | 4 | 2.80 | -6.977 | -0.675 | 0.934 | -6.977 | 8.199 | -3.697 |
| Resistencia I-b | 5 | 2.80 | -0.675 | -6.977 | 0.934 | -6.977 | 3.697 | -8.199 |
| Resistencia I-b | 6 | 4.77 | -6.977 | -6.514 | 5.339 | -6.977 | 10.230 | -10.036 |
| Resistencia I-b | 7 | 3.00 | -6.514 | -3.151 | 0.095 | -6.514 | 7.494 | -5.252 |
| Resistencia I-b | 8 | 3.00 | -3.151 | -0.000 | 3.334 | -3.151 | 7.424 | -5.323 |
| Evento Extremo I (Sismo) | 1 | 3.00 | -0.000 | -5.123 | 5.420 | -5.123 | 8.653 | -12.068 |
| Evento Extremo I (Sismo) | 2 | 3.00 | -5.123 | -10.589 | 0.155 | -10.589 | 8.538 | -12.182 |
| Evento Extremo I (Sismo) | 3 | 4.77 | -10.589 | -11.343 | 8.680 | -11.343 | 16.315 | -16.631 |
| Evento Extremo I (Sismo) | 4 | 2.80 | -11.343 | -1.097 | 1.518 | -11.343 | 13.329 | -6.011 |
| Evento Extremo I (Sismo) | 5 | 2.80 | -1.097 | -11.343 | 1.518 | -11.343 | 6.011 | -13.329 |
| Evento Extremo I (Sismo) | 6 | 4.77 | -11.343 | -10.589 | 8.680 | -11.343 | 16.631 | -16.315 |
| Evento Extremo I (Sismo) | 7 | 3.00 | -10.589 | -5.123 | 0.155 | -10.589 | 12.182 | -8.538 |
| Evento Extremo I (Sismo) | 8 | 3.00 | -5.123 | 0.000 | 5.420 | -5.123 | 12.068 | -8.653 |

## 5. Envolvente de diseño

| Demanda | Valor | Posición s | Caso | Cara traccionada |
|---|---:|---:|---|---|
| M_u negativo | 11.343 tf·m | 10.770 m | Evento Extremo I (Sismo) | superior |
| M_u positivo | 8.680 tf·m | 18.778 m | Evento Extremo I (Sismo) | inferior |

## 6. Diseño E.060–MTC y armado final

**Estado del armado:** CUMPLE.

`As normativo` es la mayor exigencia no asociada directamente a la demanda de flexión entre E.060 y MTC. La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

### Armado propuesto y verificación de áreas

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal transversal — cara superior | Evento Extremo I (Sismo) | 2.766 cm²/m | 14.400 cm²/m | mínimo cara traccionada E.060 10.5.4 | 14.400 cm²/m | Ø5/8" @ 130 mm | 15.226 cm²/m | 0.946 | Sí |
| Principal transversal — cara inferior | Evento Extremo I (Sismo) | 2.116 cm²/m | 14.400 cm²/m | mínimo cara traccionada E.060 10.5.4 | 14.400 cm²/m | Ø5/8" @ 130 mm | 15.226 cm²/m | 0.946 | Sí |
| Distribución longitudinal — cara superior | distribución | 0.000 cm²/m | 10.800 cm²/m | E.060 9.7 | 10.800 cm²/m | Ø5/8" @ 180 mm | 10.996 cm²/m | 0.982 | Sí |
| Distribución longitudinal — cara inferior | distribución | 0.000 cm²/m | 10.800 cm²/m | E.060 9.7 | 10.800 cm²/m | Ø5/8" @ 180 mm | 10.996 cm²/m | 0.982 | Sí |

### Comparación normativa detallada del refuerzo principal

| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| superior | 11.343 | 2.766 | 14.400 | 10.800 | 3.682 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 14.400 | Ø5/8" @ 130 mm | 15.226 | 0.184 |
| inferior | 8.680 | 2.116 | 14.400 | 10.800 | 2.815 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 14.400 | Ø5/8" @ 130 mm | 15.226 | 0.140 |

### Acero longitudinal de distribución y temperatura

| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |
|---|---:|---:|---:|---|---|---:|
| superior | 10.800 | 2.328 | 10.800 | E.060 9.7 | Ø5/8" @ 180 mm | 10.996 |
| inferior | 10.800 | 2.328 | 10.800 | E.060 9.7 | Ø5/8" @ 180 mm | 10.996 |

### Cortante

| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |
|---|---:|---:|---:|---:|---|---:|---|
| Evento Extremo I (Sismo) | 16.631 | 83.953 | 78.120 | 78.120 | MTC/AASHTO | 0.213 | CUMPLE |

### Desarrollo, traslapes y ganchos estándar

| Cara | Barra | ld adoptado | Clase | Traslape | ldh E.060 | ldh MTC | ldh adoptado | Extensión 90° | Doblado interior |
|---|---:|---:|:---:|---:|---:|---:|---:|---:|---:|
| superior | Ø5/8" | 1500 mm | B | 1950 mm | 299 mm | 302 mm | 350 mm | 200 mm | 95 mm |
| inferior | Ø5/8" | 1150 mm | B | 1500 mm | 299 mm | 302 mm | 350 mm | 200 mm | 95 mm |

### Zonas de empalme para barras comerciales de 12 m

- Cara superior: s=8.00 m, s=18.80 m; interior de vanos con momento positivo; traslape 1950 mm; A/B alternados; centros separados 0.60 m.
- Cara inferior: s=10.77 m, s=16.37 m; sobre CF-C1 y CF-C3, zonas de momento negativo; traslape 1500 mm; A/B alternados; centros separados 0.60 m.

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
| max error simetria | 8.882e-16 |
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

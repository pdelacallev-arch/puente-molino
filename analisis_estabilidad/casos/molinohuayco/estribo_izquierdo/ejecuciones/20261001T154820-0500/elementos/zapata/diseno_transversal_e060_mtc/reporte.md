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
| Servicio I | 25.017 | 27.237 | 25.670 | 25.670 | 3.600 | 20.376 | 1.098 | 0.596 |
| Resistencia I-a | 23.098 | 24.390 | 23.478 | 23.478 | 3.240 | 20.376 | 1.921 | -2.060 |
| Resistencia I-b | 32.969 | 35.640 | 33.755 | 33.755 | 4.500 | 27.508 | 1.921 | -0.174 |
| Evento Extremo I (Sismo) | 17.866 | 18.414 | 18.027 | 18.027 | 3.240 | 20.376 | 0.000 | -5.589 |

Todas las cargas de la tabla están expresadas en tf/m transversal.

## 4. Análisis matricial

La presión neta es uniforme a lo largo de la franja desplegada. Los desplazamientos verticales son nulos en los nueve apoyos y los giros permanecen libres. El signo físico se conserva: `w>0` es ascendente y `w<0` es descendente. En los casos calculados gobiernan localmente las cargas descendentes.

| Caso | w neta (+ ascendente) | M+ máx. | |M−| máx. | |V| máx. | Error equilibrio |
|---|---:|---:|---:|---:|---:|
| Servicio I | 0.596 | 0.978 | 0.749 | 1.435 | 0.00e+00 |
| Resistencia I-a | -2.060 | 2.588 | 3.382 | 4.959 | 1.14e-13 |
| Resistencia I-b | -0.174 | 0.219 | 0.286 | 0.420 | 8.88e-16 |
| Evento Extremo I (Sismo) | -5.589 | 7.024 | 9.178 | 13.457 | 0.00e+00 |

### Resultados por vano

| Caso | Vano | L | M izq. | M der. | M máx. | M mín. | V izq. | V der. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Servicio I | 1 | 3.00 | 0.000 | 0.442 | 0.442 | -0.468 | -0.746 | 1.041 |
| Servicio I | 2 | 3.00 | 0.442 | 0.913 | 0.913 | -0.013 | -0.737 | 1.051 |
| Servicio I | 3 | 4.77 | 0.913 | 0.978 | 0.978 | -0.749 | -1.407 | 1.435 |
| Servicio I | 4 | 2.80 | 0.978 | 0.095 | 0.978 | -0.131 | -1.150 | 0.518 |
| Servicio I | 5 | 2.80 | 0.095 | 0.978 | 0.978 | -0.131 | -0.518 | 1.150 |
| Servicio I | 6 | 4.77 | 0.978 | 0.913 | 0.978 | -0.749 | -1.435 | 1.407 |
| Servicio I | 7 | 3.00 | 0.913 | 0.442 | 0.913 | -0.013 | -1.051 | 0.737 |
| Servicio I | 8 | 3.00 | 0.442 | -0.000 | 0.442 | -0.468 | -1.041 | 0.746 |
| Resistencia I-a | 1 | 3.00 | -0.000 | -1.528 | 1.616 | -1.528 | 2.580 | -3.599 |
| Resistencia I-a | 2 | 3.00 | -1.528 | -3.158 | 0.046 | -3.158 | 2.546 | -3.633 |
| Resistencia I-a | 3 | 4.77 | -3.158 | -3.382 | 2.588 | -3.382 | 4.865 | -4.959 |
| Resistencia I-a | 4 | 2.80 | -3.382 | -0.327 | 0.453 | -3.382 | 3.975 | -1.792 |
| Resistencia I-a | 5 | 2.80 | -0.327 | -3.382 | 0.453 | -3.382 | 1.792 | -3.975 |
| Resistencia I-a | 6 | 4.77 | -3.382 | -3.158 | 2.588 | -3.382 | 4.959 | -4.865 |
| Resistencia I-a | 7 | 3.00 | -3.158 | -1.528 | 0.046 | -3.158 | 3.633 | -2.546 |
| Resistencia I-a | 8 | 3.00 | -1.528 | -0.000 | 1.616 | -1.528 | 3.599 | -2.580 |
| Resistencia I-b | 1 | 3.00 | -0.000 | -0.129 | 0.137 | -0.129 | 0.218 | -0.305 |
| Resistencia I-b | 2 | 3.00 | -0.129 | -0.267 | 0.004 | -0.267 | 0.216 | -0.308 |
| Resistencia I-b | 3 | 4.77 | -0.267 | -0.286 | 0.219 | -0.286 | 0.412 | -0.420 |
| Resistencia I-b | 4 | 2.80 | -0.286 | -0.028 | 0.038 | -0.286 | 0.337 | -0.152 |
| Resistencia I-b | 5 | 2.80 | -0.028 | -0.286 | 0.038 | -0.286 | 0.152 | -0.337 |
| Resistencia I-b | 6 | 4.77 | -0.286 | -0.267 | 0.219 | -0.286 | 0.420 | -0.412 |
| Resistencia I-b | 7 | 3.00 | -0.267 | -0.129 | 0.004 | -0.267 | 0.308 | -0.216 |
| Resistencia I-b | 8 | 3.00 | -0.129 | 0.000 | 0.137 | -0.129 | 0.305 | -0.218 |
| Evento Extremo I (Sismo) | 1 | 3.00 | -0.000 | -4.145 | 4.386 | -4.145 | 7.001 | -9.765 |
| Evento Extremo I (Sismo) | 2 | 3.00 | -4.145 | -8.568 | 0.125 | -8.568 | 6.909 | -9.858 |
| Evento Extremo I (Sismo) | 3 | 4.77 | -8.568 | -9.178 | 7.024 | -9.178 | 13.202 | -13.457 |
| Evento Extremo I (Sismo) | 4 | 2.80 | -9.178 | -0.888 | 1.228 | -9.178 | 10.785 | -4.864 |
| Evento Extremo I (Sismo) | 5 | 2.80 | -0.888 | -9.178 | 1.228 | -9.178 | 4.864 | -10.785 |
| Evento Extremo I (Sismo) | 6 | 4.77 | -9.178 | -8.568 | 7.024 | -9.178 | 13.457 | -13.202 |
| Evento Extremo I (Sismo) | 7 | 3.00 | -8.568 | -4.145 | 0.125 | -8.568 | 9.858 | -6.909 |
| Evento Extremo I (Sismo) | 8 | 3.00 | -4.145 | 0.000 | 4.386 | -4.145 | 9.765 | -7.001 |

## 5. Envolvente de diseño

| Demanda | Valor | Posición s | Caso | Cara traccionada |
|---|---:|---:|---|---|
| M_u negativo | 9.178 tf·m | 16.370 m | Evento Extremo I (Sismo) | superior |
| M_u positivo | 7.024 tf·m | 8.362 m | Evento Extremo I (Sismo) | inferior |

## 6. Diseño E.060–MTC y armado final

**Estado del armado:** CUMPLE.

`As normativo` es la mayor exigencia no asociada directamente a la demanda de flexión entre E.060 y MTC. La relación D/C de acero es `As requerido / As dispuesto`, con `As requerido = máx(As calculado, As normativo)`.

### Armado propuesto y verificación de áreas

| Armado | Caso gobernante | As calculado | As normativo | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal transversal — cara superior | Evento Extremo I (Sismo) | 1.752 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø5/8" @ 100 mm | 19.793 cm²/m | 0.909 | Sí |
| Principal transversal — cara inferior | Evento Extremo I (Sismo) | 1.341 cm²/m | 18.000 cm²/m | mínimo cara traccionada E.060 10.5.4 | 18.000 cm²/m | Ø5/8" @ 100 mm | 19.793 cm²/m | 0.909 | Sí |
| Distribución longitudinal — cara superior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø5/8" @ 140 mm | 14.138 cm²/m | 0.955 | Sí |
| Distribución longitudinal — cara inferior | distribución | 0.000 cm²/m | 13.500 cm²/m | E.060 9.7 | 13.500 cm²/m | Ø5/8" @ 140 mm | 14.138 cm²/m | 0.955 | Sí |

### Comparación normativa detallada del refuerzo principal

| Cara | Mu | As demanda | As mín. E.060 | As temp. E.060 | As mín. MTC | As temp. MTC | Control | As requerida | Armado | As prov. | D/C flexión |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| superior | 9.178 | 1.752 | 18.000 | 13.500 | 2.331 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø5/8" @ 100 mm | 19.793 | 0.090 |
| inferior | 7.024 | 1.341 | 18.000 | 13.500 | 1.783 | 2.328 | mínimo cara traccionada E.060 10.5.4 | 18.000 | Ø5/8" @ 100 mm | 19.793 | 0.069 |

### Acero longitudinal de distribución y temperatura

| Cara | As E.060 | As MTC | As requerida | Control | Armado | As prov. |
|---|---:|---:|---:|---|---|---:|
| superior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø5/8" @ 140 mm | 14.138 |
| inferior | 13.500 | 2.328 | 13.500 | E.060 9.7 | Ø5/8" @ 140 mm | 14.138 |

### Cortante

| Caso | Vu | φVc E.060 | φVc MTC | φVc diseño | Control | D/C | Estado |
|---|---:|---:|---:|---:|---|---:|---|
| Evento Extremo I (Sismo) | 13.457 | 107.117 | 99.674 | 99.674 | MTC/AASHTO | 0.135 | CUMPLE |

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
| max error equilibrio | 1.137e-13 |
| simetria | CONFORME |
| max error simetria | 4.441e-16 |
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

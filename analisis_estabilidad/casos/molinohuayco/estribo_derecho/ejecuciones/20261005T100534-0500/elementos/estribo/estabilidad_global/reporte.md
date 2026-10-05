# Resumen Preliminar - Analisis de Subestructura

**Puente:** Puente Carrozable Molinohuaico
**Ubicacion:** Chilcas, La Mar, Ayacucho
**Tipo:** Estribo Izquierdo C°A° Cantilever (H=9.87m)
**Luz:** 50.0 m

> Reporte generado por `agente_subestructura.py`. Debe incorporarse a la memoria viva solo despues de revisar supuestos y datos de entrada.

## Empujes de tierra

| Parametro | Valor | Unidad |
| --- | --- | --- |
| Ka | 0.201 | - |
| Kp | 4.557 | - |
| Kas | 0.274 | - |
| h_s/c | 0.61 | m |
| theta sismico | 7.5 | grados |
| Ea | 17.63 | t |
| M_Ea | 58.02 | t-m |
| Es | 2.18 | t |
| M_Es | 10.76 | t-m |
| Eas | 22.83 | t |
| Delta Eas | 5.19 | t |
| M_Delta Eas | 34.16 | t-m |

## Pesos estabilizadores

| Tipo | Descripcion | Peso (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Zapata | 45.54 | 6.325 | 288.04 |
| DC | Tronco pantalla | 5.12 | 6.35 | 32.49 |
| DC | Cajuela (asiento viga) | 4.85 | 6.791 | 32.94 |
| EV | Relleno sobre talón | 87.8 | 9.725 | 853.84 |
| LS | Sobrecarga terreno | 5.87 | 9.975 | 58.6 |
|  | TOTAL | 149.18 |  | 1265.91 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 6.33 | 164.32 |
| DW | Superf. desgaste | 2.88 | 6.33 | 18.22 |
| PL | Carga peatonal | 3.08 | 6.33 | 19.48 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 6.33 | 81.91 |
| BR | Frenado | 1.63 | 10.77 | 17.56 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 7.18 | 49.73 |
| Estribo | 13.32 | 1.69 | 22.49 |
| Frenado | 1.63 | 10.77 | 17.56 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 194.07 | 1549.84 | 21.44 | 86.34 | 7.54 | 1.216 | 2.419 | 0.649 |
| Resistencia I-a | 201.34 | 1611.68 | 33.11 | 136.59 | 7.33 | 1.001 | 2.347 | 0.836 |
| Resistencia I-b | 263.04 | 2107.24 | 33.11 | 136.59 | 7.49 | 1.167 | 3.23 | 0.928 |
| Evento Extremo I (Sismo) | 163.01 | 1331.69 | 43.07 | 164.4 | 7.16 | 0.836 | 1.8 | 0.778 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 194.07 | 1549.84 | 21.44 | 86.34 | 1.216 | 2.108 | CONFORME | 106.74 | CONFORME | 2.419 | CONFORME |

## Analisis de falsa zapata en dos interfaces

| Parametro | Valor | Unidad |
| --- | --- | --- |
| Ancho falsa zapata | 12.65 | m |
| Altura falsa zapata | 3.6 | m |
| Peso especifico | 2.3 | t/m3 |
| f'c falsa zapata | 140.0 | kg/cm2 |
| mu concreto-concreto | 0.6 | - |
| mu concreto-suelo | 0.55 | - |

Difusion de carga 1V:1H: **NO APLICA - SIN VUELO**. 
La flexion, el corte y el punzonamiento de la falsa zapata quedan pendientes de verificacion estructural.

### Zapata estructural / falsa zapata

Altura de empuje analizada: **9.87 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 194.07 | 1549.84 | 21.44 | 86.34 | 7.54 | 1.216 | 2.419 | 0.649 |
| Resistencia I-a | 201.34 | 1611.68 | 33.11 | 136.59 | 7.33 | 1.001 | 2.347 | 0.836 |
| Resistencia I-b | 263.04 | 2107.24 | 33.11 | 136.59 | 7.49 | 1.167 | 3.23 | 0.928 |
| Evento Extremo I (Sismo) | 163.01 | 1331.69 | 43.07 | 164.4 | 7.16 | 0.836 | 1.8 | 0.778 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 194.07 | 1549.84 | 21.44 | 86.34 | 1.216 | 2.108 | CONFORME | 116.44 | CONFORME | 2.419 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **13.47 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 298.81 | 2212.54 | 37.44 | 190.92 | 6.77 | 0.441 | 11.768 | 2.539 | No aplica |
| Resistencia I-a | 295.61 | 2208.14 | 57.31 | 297.24 | 6.46 | 0.139 | 12.372 | 2.389 | No aplica |
| Resistencia I-b | 393.96 | 2935.63 | 57.31 | 297.24 | 6.7 | 0.372 | 11.906 | 3.309 | No aplica |
| Evento Extremo I (Sismo) | 257.28 | 1928.1 | 87.9 | 424.67 | 5.84 | 0.481 | 11.688 | 2.201 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 298.81 | 2212.54 | 37.44 | 190.92 | 0.441 | 2.108 | CONFORME | 164.35 | CONFORME | 2.539 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

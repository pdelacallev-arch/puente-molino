# Resumen Preliminar - Analisis de Subestructura

**Puente:** Puente Carrozable Molinohuaico
**Ubicacion:** Chilcas, La Mar, Ayacucho
**Tipo:** Estribo Izquierdo C°A° Cantilever (H=17.65m)
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
| Ea | 56.39 | t |
| M_Ea | 331.77 | t-m |
| Es | 3.9 | t |
| M_Es | 34.4 | t-m |
| Eas | 72.99 | t |
| Delta Eas | 16.6 | t |
| M_Delta Eas | 195.34 | t-m |

## Pesos estabilizadores

| Tipo | Descripcion | Peso (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Zapata | 43.02 | 5.975 | 257.04 |
| DC | Tronco pantalla | 12.29 | 5.65 | 69.43 |
| DC | Cajuela (asiento viga) | 6.34 | 6.031 | 38.22 |
| EV | Relleno sobre talón | 172.5 | 8.974 | 1548.06 |
| LS | Sobrecarga terreno | 5.82 | 9.3 | 54.12 |
|  | TOTAL | 239.97 |  | 1966.87 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 5.6 | 145.49 |
| DW | Superf. desgaste | 2.88 | 5.6 | 16.13 |
| PL | Carga peatonal | 3.08 | 5.6 | 17.25 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 5.6 | 72.52 |
| BR | Frenado | 1.63 | 18.55 | 30.24 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 14.8 | 102.51 |
| Estribo | 14.79 | 3.68 | 54.45 |
| Frenado | 1.63 | 18.55 | 30.24 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 284.86 | 2218.26 | 61.92 | 396.41 | 6.4 | 0.421 | 2.888 | 1.88 |
| Resistencia I-a | 291.48 | 2269.51 | 94.26 | 610.77 | 5.69 | 0.284 | 2.787 | 2.091 |
| Resistencia I-b | 384.97 | 3003.61 | 94.26 | 610.77 | 6.22 | 0.241 | 3.611 | 2.832 |
| Evento Extremo I (Sismo) | 253.24 | 2017.71 | 94.71 | 684.07 | 5.27 | 0.709 | 2.874 | 1.365 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 284.86 | 2218.26 | 61.92 | 396.41 | 0.421 | 1.992 | CONFORME | 156.67 | CONFORME | 2.888 | CONFORME |

## Analisis de falsa zapata en dos interfaces

| Parametro | Valor | Unidad |
| --- | --- | --- |
| Ancho falsa zapata | 11.95 | m |
| Altura falsa zapata | 3.5 | m |
| Peso especifico | 2.3 | t/m3 |
| f'c falsa zapata | 140.0 | kg/cm2 |
| mu concreto-concreto | 0.6 | - |
| mu concreto-suelo | 0.55 | - |

Difusion de carga 1V:1H: **NO APLICA - SIN VUELO**. 
La flexion, el corte y el punzonamiento de la falsa zapata quedan pendientes de verificacion estructural.

### Zapata estructural / falsa zapata

Altura de empuje analizada: **17.65 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 284.86 | 2218.26 | 61.92 | 396.41 | 6.4 | 0.421 | 2.888 | 1.88 |
| Resistencia I-a | 291.48 | 2269.51 | 94.26 | 610.77 | 5.69 | 0.284 | 2.787 | 2.091 |
| Resistencia I-b | 384.97 | 3003.61 | 94.26 | 610.77 | 6.22 | 0.241 | 3.611 | 2.832 |
| Evento Extremo I (Sismo) | 253.24 | 2017.71 | 94.71 | 684.07 | 5.27 | 0.709 | 2.874 | 1.365 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 284.86 | 2218.26 | 61.92 | 396.41 | 0.421 | 1.992 | CONFORME | 170.92 | CONFORME | 2.888 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **21.15 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 381.06 | 2793.03 | 87.27 | 656.19 | 5.61 | 0.367 | 11.216 | 3.397 | No aplica |
| Resistencia I-a | 378.05 | 2786.8 | 132.48 | 1005.62 | 4.71 | 1.264 | 9.422 | 4.012 | No aplica |
| Resistencia I-b | 505.21 | 3722.06 | 132.48 | 1005.62 | 5.38 | 0.598 | 10.754 | 4.698 | No aplica |
| Evento Extremo I (Sismo) | 339.82 | 2534.99 | 149.62 | 1180.36 | 3.99 | 1.989 | 7.972 | 4.263 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 381.06 | 2793.03 | 87.27 | 656.19 | 0.367 | 1.992 | CONFORME | 209.58 | CONFORME | 3.397 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

# Resumen Preliminar - Analisis de Subestructura

**Puente:** Puente Carrozable Molinohuaico
**Ubicacion:** Chilcas, La Mar, Ayacucho
**Tipo:** Estribo Izquierdo C°A° Cantilever (H=12.82m)
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
| Ea | 29.75 | t |
| M_Ea | 127.13 | t-m |
| Es | 2.83 | t |
| M_Es | 18.15 | t-m |
| Eas | 38.51 | t |
| Delta Eas | 8.76 | t |
| M_Delta Eas | 74.86 | t-m |

## Pesos estabilizadores

| Tipo | Descripcion | Peso (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Zapata | 43.02 | 5.975 | 257.04 |
| DC | Tronco pantalla | 7.95 | 5.65 | 44.91 |
| DC | Cajuela (asiento viga) | 4.85 | 6.091 | 29.55 |
| EV | Relleno sobre talón | 120.19 | 8.991 | 1080.67 |
| LS | Sobrecarga terreno | 5.87 | 9.275 | 54.48 |
|  | TOTAL | 181.88 |  | 1466.65 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 5.62 | 146.14 |
| DW | Superf. desgaste | 2.88 | 5.62 | 16.2 |
| PL | Carga peatonal | 3.08 | 5.62 | 17.32 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 5.62 | 72.84 |
| BR | Frenado | 1.63 | 13.72 | 22.36 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 10.13 | 70.16 |
| Estribo | 13.4 | 2.32 | 31.11 |
| Frenado | 1.63 | 13.72 | 22.36 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 226.77 | 1719.15 | 34.21 | 167.64 | 6.84 | 0.867 | 2.724 | 1.072 |
| Resistencia I-a | 234.01 | 1774.2 | 52.43 | 261.59 | 6.46 | 0.489 | 2.439 | 1.477 |
| Resistencia I-b | 307.15 | 2333.38 | 52.43 | 261.59 | 6.75 | 0.77 | 3.564 | 1.577 |
| Evento Extremo I (Sismo) | 195.68 | 1521.08 | 58.84 | 303.26 | 6.22 | 0.248 | 1.841 | 1.434 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 226.77 | 1719.15 | 34.21 | 167.64 | 0.867 | 1.992 | CONFORME | 124.72 | CONFORME | 2.724 | CONFORME |

## Analisis de falsa zapata en dos interfaces

| Parametro | Valor | Unidad |
| --- | --- | --- |
| Ancho falsa zapata | 11.95 | m |
| Altura falsa zapata | 3.56 | m |
| Peso especifico | 2.3 | t/m3 |
| f'c falsa zapata | 140.0 | kg/cm2 |
| mu concreto-concreto | 0.6 | - |
| mu concreto-suelo | 0.55 | - |

Difusion de carga 1V:1H: **NO APLICA - SIN VUELO**. 
La flexion, el corte y el punzonamiento de la falsa zapata quedan pendientes de verificacion estructural.

### Zapata estructural / falsa zapata

Altura de empuje analizada: **12.82 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 226.77 | 1719.15 | 34.21 | 167.64 | 6.84 | 0.867 | 2.724 | 1.072 |
| Resistencia I-a | 234.01 | 1774.2 | 52.43 | 261.59 | 6.46 | 0.489 | 2.439 | 1.477 |
| Resistencia I-b | 307.15 | 2333.38 | 52.43 | 261.59 | 6.75 | 0.77 | 3.564 | 1.577 |
| Evento Extremo I (Sismo) | 195.68 | 1521.08 | 58.84 | 303.26 | 6.22 | 0.248 | 1.841 | 1.434 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 226.77 | 1719.15 | 34.21 | 167.64 | 0.867 | 1.992 | CONFORME | 136.06 | CONFORME | 2.724 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **16.38 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 324.62 | 2303.49 | 53.82 | 322.98 | 6.1 | 0.126 | 11.698 | 2.775 | No aplica |
| Resistencia I-a | 322.07 | 2300.01 | 82.04 | 498.92 | 5.59 | 0.383 | 11.184 | 2.88 | No aplica |
| Resistencia I-b | 429.46 | 3063.74 | 82.04 | 498.92 | 5.97 | 0.003 | 11.944 | 3.596 | No aplica |
| Evento Extremo I (Sismo) | 283.74 | 2047.08 | 106.68 | 636.75 | 4.97 | 1.005 | 9.94 | 2.855 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 324.62 | 2303.49 | 53.82 | 322.98 | 0.126 | 1.992 | CONFORME | 178.54 | CONFORME | 2.775 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

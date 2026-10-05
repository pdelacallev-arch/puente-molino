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
| DC | Zapata | 23.04 | 4.0 | 92.16 |
| DC | Tronco pantalla | 8.24 | 2.8 | 23.06 |
| DC | Cajuela (asiento viga) | 4.85 | 3.241 | 15.72 |
| EV | Relleno sobre talón | 100.48 | 5.587 | 561.34 |
| LS | Sobrecarga terreno | 4.67 | 5.875 | 27.42 |
|  | TOTAL | 141.27 |  | 719.7 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 2.78 | 72.09 |
| DW | Superf. desgaste | 2.88 | 2.78 | 7.99 |
| PL | Carga peatonal | 3.08 | 2.78 | 8.55 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 2.78 | 35.94 |
| BR | Frenado | 1.63 | 13.72 | 22.36 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 10.13 | 70.16 |
| Estribo | 8.67 | 3.09 | 26.78 |
| Frenado | 1.63 | 13.72 | 22.36 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 186.17 | 844.27 | 34.21 | 167.64 | 3.63 | 0.366 | 2.966 | 1.688 |
| Resistencia I-a | 194.47 | 875.1 | 52.43 | 261.59 | 3.15 | 0.845 | 3.972 | 0.89 |
| Resistencia I-b | 253.83 | 1149.42 | 52.43 | 261.59 | 3.5 | 0.502 | 4.367 | 1.978 |
| Evento Extremo I (Sismo) | 158.25 | 749.26 | 54.11 | 298.93 | 2.85 | 1.154 | 3.69 | 0.266 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 186.17 | 844.27 | 34.21 | 167.64 | 0.366 | 1.333 | CONFORME | 102.39 | CONFORME | 2.966 | CONFORME |

## Analisis de falsa zapata en dos interfaces

| Parametro | Valor | Unidad |
| --- | --- | --- |
| Ancho falsa zapata | 11.95 | m |
| Altura falsa zapata | 3.56 | m |
| Peso especifico | 2.3 | t/m3 |
| f'c falsa zapata | 140.0 | kg/cm2 |
| mu concreto-concreto | 0.6 | - |
| mu concreto-suelo | 0.55 | - |

Difusion de carga 1V:1H: **CONFORME PRELIMINAR**. 
La flexion, el corte y el punzonamiento de la falsa zapata quedan pendientes de verificacion estructural.

### Zapata estructural / falsa zapata

Altura de empuje analizada: **12.82 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 186.17 | 844.27 | 34.21 | 167.64 | 3.63 | 0.366 | 2.966 | 1.688 |
| Resistencia I-a | 194.47 | 875.1 | 52.43 | 261.59 | 3.15 | 0.845 | 3.972 | 0.89 |
| Resistencia I-b | 253.83 | 1149.42 | 52.43 | 261.59 | 3.5 | 0.502 | 4.367 | 1.978 |
| Evento Extremo I (Sismo) | 158.25 | 749.26 | 54.11 | 298.93 | 2.85 | 1.154 | 3.69 | 0.266 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 186.17 | 844.27 | 34.21 | 167.64 | 0.366 | 1.333 | CONFORME | 111.7 | CONFORME | 2.966 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **16.38 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 284.02 | 1959.78 | 53.82 | 322.98 | 5.76 | 0.212 | 11.526 | 2.464 | No aplica |
| Resistencia I-a | 282.54 | 1955.87 | 82.04 | 498.92 | 5.16 | 0.818 | 10.314 | 2.739 | No aplica |
| Resistencia I-b | 376.14 | 2604.05 | 82.04 | 498.92 | 5.6 | 0.378 | 11.194 | 3.36 | No aplica |
| Evento Extremo I (Sismo) | 246.31 | 1726.63 | 101.95 | 615.59 | 4.51 | 1.464 | 9.022 | 2.73 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 284.02 | 1959.78 | 53.82 | 322.98 | 0.212 | 1.992 | CONFORME | 156.21 | CONFORME | 2.464 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

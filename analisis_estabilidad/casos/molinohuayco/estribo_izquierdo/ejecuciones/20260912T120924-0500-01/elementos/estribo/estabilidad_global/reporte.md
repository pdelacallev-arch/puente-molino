# Resumen Preliminar - Analisis de Subestructura

**Puente:** Puente Carrozable Molinohuaico
**Ubicacion:** Chilcas, La Mar, Ayacucho
**Tipo:** Estribo Izquierdo C°A° Cantilever (H=15.34m)
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
| Ea | 42.6 | t |
| M_Ea | 217.81 | t-m |
| Es | 3.39 | t |
| M_Es | 25.98 | t-m |
| Eas | 55.14 | t |
| Delta Eas | 12.54 | t |
| M_Delta Eas | 128.24 | t-m |

## Pesos estabilizadores

| Tipo | Descripcion | Peso (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Zapata | 43.02 | 5.975 | 257.04 |
| DC | Tronco pantalla | 10.37 | 5.65 | 58.58 |
| DC | Cajuela (asiento viga) | 4.85 | 6.091 | 29.55 |
| EV | Relleno sobre talón | 147.86 | 8.974 | 1326.93 |
| LS | Sobrecarga terreno | 5.87 | 9.275 | 54.48 |
|  | TOTAL | 211.97 |  | 1726.58 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 5.62 | 146.14 |
| DW | Superf. desgaste | 2.88 | 5.62 | 16.2 |
| PL | Carga peatonal | 3.08 | 5.62 | 17.32 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 5.62 | 72.84 |
| BR | Frenado | 1.63 | 16.24 | 26.47 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 12.65 | 87.62 |
| Estribo | 13.98 | 2.89 | 40.46 |
| Frenado | 1.63 | 16.24 | 26.47 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 256.86 | 1979.08 | 47.62 | 270.26 | 6.65 | 0.678 | 2.881 | 1.418 |
| Resistencia I-a | 263.86 | 2032.76 | 72.69 | 418.5 | 6.12 | 0.143 | 2.367 | 2.049 |
| Resistencia I-b | 347.53 | 2682.91 | 72.69 | 418.5 | 6.52 | 0.541 | 3.698 | 2.118 |
| Evento Extremo I (Sismo) | 225.53 | 1779.64 | 76.05 | 474.13 | 5.79 | 0.186 | 2.064 | 1.711 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 256.86 | 1979.08 | 47.62 | 270.26 | 0.678 | 1.992 | CONFORME | 141.27 | CONFORME | 2.881 | CONFORME |

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

Altura de empuje analizada: **15.34 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 256.86 | 1979.08 | 47.62 | 270.26 | 6.65 | 0.678 | 2.881 | 1.418 |
| Resistencia I-a | 263.86 | 2032.76 | 72.69 | 418.5 | 6.12 | 0.143 | 2.367 | 2.049 |
| Resistencia I-b | 347.53 | 2682.91 | 72.69 | 418.5 | 6.52 | 0.541 | 3.698 | 2.118 |
| Evento Extremo I (Sismo) | 225.53 | 1779.64 | 76.05 | 474.13 | 5.79 | 0.186 | 2.064 | 1.711 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 256.86 | 1979.08 | 47.62 | 270.26 | 0.678 | 1.992 | CONFORME | 154.12 | CONFORME | 2.881 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **18.9 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 354.71 | 2563.43 | 70.46 | 479.08 | 5.88 | 0.099 | 11.752 | 3.018 | No aplica |
| Resistencia I-a | 351.92 | 2558.59 | 107.14 | 736.55 | 5.18 | 0.798 | 10.354 | 3.399 | No aplica |
| Resistencia I-b | 469.84 | 3413.29 | 107.14 | 736.55 | 5.7 | 0.278 | 11.394 | 4.124 | No aplica |
| Evento Extremo I (Sismo) | 313.59 | 2305.65 | 128.09 | 891.52 | 4.51 | 1.466 | 9.018 | 3.477 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 354.71 | 2563.43 | 70.46 | 479.08 | 0.099 | 1.992 | CONFORME | 195.09 | CONFORME | 3.018 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

# Resumen Preliminar - Analisis de Subestructura

**Puente:** Puente Carrozable Molinohuaico
**Ubicacion:** Chilcas, La Mar, Ayacucho
**Tipo:** Estribo Izquierdo C°A° Cantilever (H=14.65m)
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
| Ea | 38.85 | t |
| M_Ea | 189.72 | t-m |
| Es | 3.24 | t |
| M_Es | 23.7 | t-m |
| Eas | 50.29 | t |
| Delta Eas | 11.44 | t |
| M_Delta Eas | 111.71 | t-m |

## Pesos estabilizadores

| Tipo | Descripcion | Peso (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Zapata | 45.54 | 6.325 | 288.04 |
| DC | Tronco pantalla | 9.71 | 6.35 | 61.63 |
| DC | Cajuela (asiento viga) | 4.85 | 6.791 | 32.94 |
| EV | Relleno sobre talón | 140.28 | 9.678 | 1357.7 |
| LS | Sobrecarga terreno | 5.87 | 9.975 | 58.6 |
|  | TOTAL | 206.25 |  | 1798.9 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 6.33 | 164.32 |
| DW | Superf. desgaste | 2.88 | 6.33 | 18.22 |
| PL | Carga peatonal | 3.08 | 6.33 | 19.48 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 6.33 | 81.91 |
| BR | Frenado | 1.63 | 15.55 | 25.35 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 11.96 | 82.84 |
| Estribo | 14.42 | 2.65 | 38.21 |
| Frenado | 1.63 | 15.55 | 25.35 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 251.14 | 2082.84 | 43.72 | 238.77 | 7.34 | 1.018 | 2.944 | 1.027 |
| Resistencia I-a | 257.95 | 2141.76 | 66.8 | 370.42 | 6.87 | 0.542 | 2.563 | 1.515 |
| Resistencia I-b | 339.62 | 2823.87 | 66.8 | 370.42 | 7.22 | 0.899 | 3.83 | 1.54 |
| Evento Extremo I (Sismo) | 219.62 | 1861.78 | 71.64 | 422.48 | 6.55 | 0.228 | 1.924 | 1.548 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 251.14 | 2082.84 | 43.72 | 238.77 | 1.018 | 2.108 | CONFORME | 138.13 | CONFORME | 2.944 | CONFORME |

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

Altura de empuje analizada: **14.65 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 251.14 | 2082.84 | 43.72 | 238.77 | 7.34 | 1.018 | 2.944 | 1.027 |
| Resistencia I-a | 257.95 | 2141.76 | 66.8 | 370.42 | 6.87 | 0.542 | 2.563 | 1.515 |
| Resistencia I-b | 339.62 | 2823.87 | 66.8 | 370.42 | 7.22 | 0.899 | 3.83 | 1.54 |
| Evento Extremo I (Sismo) | 219.62 | 1861.78 | 71.64 | 422.48 | 6.55 | 0.228 | 1.924 | 1.548 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 251.14 | 2082.84 | 43.72 | 238.77 | 1.018 | 2.108 | CONFORME | 150.68 | CONFORME | 2.944 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **18.25 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 355.88 | 2745.47 | 65.95 | 434.75 | 6.49 | 0.168 | 12.314 | 2.89 | No aplica |
| Resistencia I-a | 352.22 | 2738.14 | 100.34 | 669.12 | 5.87 | 0.451 | 11.748 | 2.998 | No aplica |
| Resistencia I-b | 470.55 | 3652.16 | 100.34 | 669.12 | 6.34 | 0.014 | 12.622 | 3.728 | No aplica |
| Evento Extremo I (Sismo) | 313.89 | 2458.1 | 124.53 | 825.86 | 5.2 | 1.125 | 10.4 | 3.018 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 355.88 | 2745.47 | 65.95 | 434.75 | 0.168 | 2.108 | CONFORME | 195.74 | CONFORME | 2.89 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

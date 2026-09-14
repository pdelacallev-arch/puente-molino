# Resumen Preliminar - Analisis de Subestructura

**Puente:** Puente Carrozable Molinohuaico
**Ubicacion:** Chilcas, La Mar, Ayacucho
**Tipo:** Estribo Izquierdo C°A° Cantilever (H=12.39m)
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
| Ea | 27.79 | t |
| M_Ea | 114.77 | t-m |
| Es | 2.74 | t |
| M_Es | 16.95 | t-m |
| Eas | 35.97 | t |
| Delta Eas | 8.18 | t |
| M_Delta Eas | 67.57 | t-m |

## Pesos estabilizadores

| Tipo | Descripcion | Peso (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Zapata | 45.54 | 6.325 | 288.04 |
| DC | Tronco pantalla | 7.54 | 6.35 | 47.85 |
| DC | Cajuela (asiento viga) | 4.85 | 6.791 | 32.94 |
| EV | Relleno sobre talón | 115.47 | 9.695 | 1119.47 |
| LS | Sobrecarga terreno | 5.87 | 9.975 | 58.6 |
|  | TOTAL | 179.27 |  | 1546.9 |

## Reacciones de superestructura

| Tipo | Descripcion | Reaccion (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- | --- |
| DC | Peso Propio | 25.98 | 6.33 | 164.32 |
| DW | Superf. desgaste | 2.88 | 6.33 | 18.22 |
| PL | Carga peatonal | 3.08 | 6.33 | 19.48 |
| LL+IM | Sobrecarga HL-93 | 12.95 | 6.33 | 81.91 |
| BR | Frenado | 1.63 | 13.29 | 21.66 |

## Fuerzas sismicas equivalentes

| Componente | Fuerza (t) | Brazo (m) | Momento (t-m) |
| --- | --- | --- | --- |
| Superestructura | 6.93 | 9.7 | 67.19 |
| Estribo | 13.9 | 2.17 | 30.12 |
| Frenado | 1.63 | 13.29 | 21.66 |

Porcentaje sismico usado: **24.0%**.

## Presiones por estado limite

> Se calculan acciones, resultantes y presiones para todas las combinaciones; esta tabla no emite un dictamen de estabilidad.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 224.16 | 1830.83 | 32.16 | 153.38 | 7.48 | 1.158 | 2.745 | 0.799 |
| Resistencia I-a | 231.19 | 1891.13 | 49.33 | 239.72 | 7.14 | 0.818 | 2.537 | 1.118 |
| Resistencia I-b | 303.42 | 2485.03 | 49.33 | 239.72 | 7.4 | 1.075 | 3.622 | 1.176 |
| Evento Extremo I (Sismo) | 192.86 | 1611.15 | 56.8 | 279.65 | 6.9 | 0.579 | 1.943 | 1.106 |

## Verificacion de estabilidad - Servicio I

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | B/6 (m) | Volteo | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 224.16 | 1830.83 | 32.16 | 153.38 | 1.158 | 2.108 | CONFORME | 123.29 | CONFORME | 2.745 | CONFORME |

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

Altura de empuje analizada: **12.39 m**.

Presiones calculadas para todos los estados limite (sin dictamen de estabilidad):

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | qmax (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 224.16 | 1830.83 | 32.16 | 153.38 | 7.48 | 1.158 | 2.745 | 0.799 |
| Resistencia I-a | 231.19 | 1891.13 | 49.33 | 239.72 | 7.14 | 0.818 | 2.537 | 1.118 |
| Resistencia I-b | 303.42 | 2485.03 | 49.33 | 239.72 | 7.4 | 1.075 | 3.622 | 1.176 |
| Evento Extremo I (Sismo) | 192.86 | 1611.15 | 56.8 | 279.65 | 6.9 | 0.579 | 1.943 | 1.106 |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 224.16 | 1830.83 | 32.16 | 153.38 | 1.158 | 2.108 | CONFORME | 134.5 | CONFORME | 2.745 | CONFORME |

### Falsa zapata / suelo de cimentación

Altura de empuje analizada: **15.99 m**.

Presion equivalente uniforme de Meyerhof sobre el ancho efectivo B' = B - 2e. qmin no aplica a este modelo equivalente; no representa perdida de contacto.

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | Xo (m) | e (m) | B efectivo (m) | q efectiva (kg/cm2) | qmin (kg/cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 328.9 | 2493.54 | 51.44 | 302.45 | 6.66 | 0.337 | 11.976 | 2.746 | No aplica |
| Resistencia I-a | 325.45 | 2487.59 | 78.45 | 467.62 | 6.21 | 0.118 | 12.414 | 2.622 | No aplica |
| Resistencia I-b | 434.34 | 3313.44 | 78.45 | 467.62 | 6.55 | 0.227 | 12.196 | 3.561 | No aplica |
| Evento Extremo I (Sismo) | 287.13 | 2207.55 | 105.88 | 609.48 | 5.57 | 0.759 | 11.132 | 2.579 | No aplica |

Verificacion de estabilidad para Servicio I:

| Estado limite | V (t) | Me (t-m) | Fh (t) | Mv (t-m) | e (m) | Limite e (m) | Excentricidad | QR (t) | Deslizamiento | q efectiva (kg/cm2) | Capacidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Servicio I | 328.9 | 2493.54 | 51.44 | 302.45 | 0.337 | 2.108 | CONFORME | 180.9 | CONFORME | 2.746 | CONFORME |

## Pendientes antes de cerrar resultados

- Confirmar si el analisis debe hacerse por metro de ancho o por ancho total.
- Confirmar geometria real del estribo y contrafuertes contra planos/memoria.
- Confirmar reacciones de superestructura y factores de combinacion aplicables.
- Confirmar parametros geotecnicos y capacidad portante de la version vigente.
- Confirmar mu de la junta, factor de compresion del concreto y preparacion real de la interfaz.
- Verificar flexion, corte y punzonamiento de la falsa zapata con su geometria tridimensional.

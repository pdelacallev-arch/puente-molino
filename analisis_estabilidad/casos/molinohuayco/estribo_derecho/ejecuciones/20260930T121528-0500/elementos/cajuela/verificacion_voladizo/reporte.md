# Diseño normativo de la pared de cajuela en voladizo

## Modelo

- Franja: 1.00 m; altura local: 3.04 m; altura global de empuje: 14.65 m; espesor: 0.40 m.
- El acero vertical se selecciona entre 5/8", 3/4", 1". Para el acero horizontal se adopta 1/2" @ 300 mm.
- La sección de análisis está en la base, inmediatamente debajo de la mesa de apoyo. BR se aplica con brazo de 1.00 m y EQ-super con brazo de 0.70 m, medidos desde dicha sección.
- La compresion axial del puente se cuantifica, pero no se acredita para aumentar la capacidad a flexion.
- Evento Extremo I aplica las dos concurrencias del MTC 2018, Art. 2.8.1.1.14.1; I-A e I-B son etiquetas internas del calculo.
- EQ-super se conserva al 100% en ambas concurrencias mientras no se demuestre una ruta de carga alternativa.

## Criterios de diseño

El acero requerido por cara se obtiene como la envolvente entre el acero calculado por flexión, el mínimo de flexión E.060 y los mínimos de retracción y temperatura E.060 y MTC:

$$A_{s,req}=\max(A_{s,calc},A_{s,min,E.060},A_{s,rt,E.060},A_{s,rt,MTC})$$

Para cada barra disponible se determina el espaciamiento por área, se redondea hacia abajo al paso constructivo y se comprueban $A_{s,disp}\ge A_{s,req}$, $M_u\le\phi M_n$, esfuerzo del acero y separación por fisuración. Se adopta además el menor límite general de espaciamiento aplicable.

## Demandas

| Caso | Combinacion | V (tf/m) | M base (tf·m/m) | P axial (tf/m) |
|---|---|---:|---:|---:|
| Servicio I | Ea + Es + BR | 3.834 | 4.183 | 44.890 |
| Resistencia I-a | 1.50 Ea + 1.75 Es + 1.75 BR | 6.317 | 6.923 | 53.306 |
| Resistencia I-b | 1.50 Ea + 1.75 Es + 1.75 BR | 6.317 | 6.923 | 64.847 |
| Evento Extremo I-A | 100% PAE + 50% PIR + 100% EQ-super | 12.682 | 13.035 | 25.254 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR + 100% EQ-super [50% PAE] | 10.078 | 9.357 | 25.254 |

Gobierna **Evento Extremo I-A**, con M_u = 13.035 tf·m/m (cara posterior/relleno).

### Casos sísmicos inversos (inercia hacia el relleno)

Para la cara frontal/no relleno también se evalúan I-A e I-B. La componente de terreno permanece hacia el vacío y las inercias PIR + EQ-super actúan hacia el relleno; un momento inverso positivo tracciona la cara frontal.

| Caso | Terreno opuesto | M terreno | M(PIR) | M(EQ-super) | M inverso | V inverso |
|---|---|---:|---:|---:|---:|---:|
| Evento Extremo I-A inverso | 100% PAE | 7.909 | 0.277 | 4.848 | -2.783 | 1.536 |
| Evento Extremo I-B inverso | max(50% PAE, PA) | 3.954 | 0.554 | 4.848 | 1.449 | 4.505 |

## Diseño del acero vertical por cara

Cada cara se dimensiona para su demanda de tracción gobernante: la posterior/relleno con el caso directo y la frontal/no relleno con el caso inverso.

| Cara | Caso/dirección | M_u | A_s,calc | A_s,norm | Control normativo | A_s,req | Refuerzo dispuesto | A_s,disp | D/C acero | φM_n | D/C flexión | Estado |
|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---|
| frontal/no relleno | inverso (hacia el relleno) | 1.449 tf·m/m | 1.124 cm²/m | 9.540 cm²/m | mínimo de flexión E.060 | 9.540 cm²/m | 5/8" @ 205 mm | 9.655 cm²/m | 0.988 | 12.173 tf·m/m | 0.119 | Cumple |
| posterior/relleno | directo (hacia el vacio) | 13.035 tf·m/m | 11.227 cm²/m | 8.842 cm²/m | mínimo de flexión E.060 | 11.227 cm²/m | 5/8" @ 175 mm | 11.310 cm²/m | 0.993 | 13.129 tf·m/m | 0.993 | Cumple |

### Fisuración bajo Servicio I

| Cara | f_s | Límite de f_s | Separación dispuesta | Separación límite | Estado |
|---|---:|---:|---:|---:|---|
| frontal/no relleno | 138.0 MPa | 247.1 MPa | 205 mm | 599 mm | Cumple |
| posterior/relleno | 127.1 MPa | 247.1 MPa | 175 mm | 536 mm | Cumple |

La fisuración se verifica con Servicio I para el refuerzo finalmente dispuesto.

## Otros controles

| Control | Demanda/requisito | Capacidad/provision | D/C | Estado |
|---|---:|---:|---:|---|
| Acero horizontal por cara | 3.600 cm²/m | 1/2" @ 300 mm = 4.223 cm²/m | 0.853 | Cumple |
| Cortante | 12.682 tf/m | 22.991 tf/m | 0.552 | Cumple |
| Compresion axial media | 0.619 MPa | f'c = 27.459 MPa | 0.023 | Informativo |

## Armado normativo adoptado

- Acero vertical, cara frontal/no relleno: 5/8" @ 205 mm.
- Acero vertical, cara posterior/relleno: 5/8" @ 175 mm.
- Acero horizontal, ambas caras: 1/2" @ 300 mm.

## Resultado

**Estado global: CUMPLE.**

El resultado incluye la fuerza sismica de la superestructura al 100% en ambas concurrencias, aplicada en la mesa de apoyo a 0.70 m sobre la seccion de base analizada.

Pendiente para cierre definitivo: verificar distribucion horizontal/local alrededor de apoyos y juntas con sus posiciones, dimensiones de placas, excentricidades y detalle de anclaje al cuello de la pantalla.

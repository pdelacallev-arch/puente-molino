# Verificacion de la pared de cajuela en voladizo

## Modelo

- Franja: 1.00 m; altura: 3.40 m; espesor: 0.40 m.
- Armado evaluado: Ø5/8" @ 150 mm vertical y @ 150 mm horizontal, en ambas caras.
- La fuerza horizontal del puente se aplica a 3.40 m sobre el arranque.
- La compresion axial del puente se cuantifica, pero no se acredita para aumentar la capacidad a flexion.

## Demandas

| Caso | Combinacion | V (tf/m) | M base (tf·m/m) | P axial (tf/m) |
|---|---|---:|---:|---:|
| Servicio I | EH + LS + BR | 4.304 | 8.972 | 44.890 |
| Resistencia I-a | 1.50 EH + 1.75 LS + 1.75 BR | 7.039 | 15.144 | 53.306 |
| Resistencia I-b | 1.50 EH + 1.75 LS + 1.75 BR | 7.039 | 15.144 | 64.847 |
| Evento Extremo I-A | 100% PAE + 50% PIR + EQ-super | 2.751 | 3.233 | 25.254 |
| Evento Extremo I-B | max(50% PAE, PA) + 100% PIR + EQ-super | 2.376 | 2.924 | 25.254 |

Gobierna **Resistencia I-a**, con M_u = 15.144 tf·m/m.

## Acero vertical por cara

| Cara | d (mm) | As req. | As prov. | D/C área | φMn | D/C flexión | fs serv. | s fis. límite | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| frontal/no relleno | 342.1 | 12.089 cm²/m | 13.196 cm²/m | 0.916 | 16.481 tf·m/m | 0.919 | 216.6 MPa | 340 mm | Cumple |
| posterior/relleno | 317.1 | 13.114 cm²/m | 13.196 cm²/m | 0.994 | 15.234 tf·m/m | 0.994 | 233.7 MPa | 216 mm | Cumple |

## Otros controles

| Control | Demanda/requisito | Capacidad/provision | D/C | Estado |
|---|---:|---:|---:|---|
| Acero horizontal por cara | 3.600 cm²/m | 13.196 cm²/m | 0.273 | Cumple |
| Cortante | 7.039 tf/m | 22.991 tf/m | 0.306 | Cumple |
| Compresion axial media | 1.307 MPa | f'c = 27.459 MPa | 0.048 | Informativo |

Con Ø5/8", la separación vertical máxima que satisface la envolvente calculada es **150 mm**. Para el acero horizontal por mínimos, el límite calculado es **400 mm** (además de los límites generales de espaciamiento).

## Resultado

**Estado global: CUMPLE.**

Escenario de sensibilidad sin transferencia de EQ-super a la pared. Solo es util si la ruta alternativa de esa fuerza queda demostrada mediante el detalle de apoyos, cajuela y contrafuertes.

Pendiente para cierre definitivo: verificar distribucion horizontal/local alrededor de apoyos y juntas con sus posiciones, dimensiones de placas, excentricidades y detalle de anclaje al cuello de la pantalla.

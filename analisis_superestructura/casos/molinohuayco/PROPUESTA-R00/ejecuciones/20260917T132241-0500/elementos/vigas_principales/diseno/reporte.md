# Análisis y diseño de vigas principales - Puente Molinohuayco - piloto de vigas principales (PROPUESTA-R00)

- Revisión: `PROPUESTA-R00`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **CUMPLE**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.42549 |
| momento_exterior | 0.48887 |
| corte_interior | 0.64536 |
| corte_exterior | 0.44304 |
| fatiga_interior | 0.36720 |
| fatiga_exterior | 0.40445 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.409e+04 kN.m | 2.265e+04 kN.m | 0.622 | Cumple |
| interior | Ductilidad Dp/Dt | 0.3909 - | 0.42 - | 0.931 | Cumple |
| interior | Compacidad del alma en flexión positiva | 56.19 - | 90.53 - | 0.621 | Cumple |
| interior | Corte del alma | 1378 kN | 3559 kN | 0.387 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 202 MPa | 327.8 MPa | 0.616 | Cumple |
| interior | Fatiga categoría C | 44.78 MPa | 69 MPa | 0.649 | Cumple |
| interior | Estabilidad lateral durante construcción | 5361 kN.m | 1.409e+04 kN.m | 0.381 | Cumple |
| interior | Deflexión vehicular - Servicio I | 27.55 mm | 62.5 mm | 0.441 | Cumple |
| interior | Deflexión vehicular y peatonal - Servicio I | 27.55 mm | 50 mm | 0.551 | Cumple |
| exterior | Flexión positiva - Resistencia I | 1.905e+04 kN.m | 2.265e+04 kN.m | 0.841 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.3909 - | 0.42 - | 0.931 | Cumple |
| exterior | Compacidad del alma en flexión positiva | 56.19 - | 90.53 - | 0.621 | Cumple |
| exterior | Corte del alma | 1479 kN | 3559 kN | 0.416 | Cumple |
| exterior | Esfuerzo elástico - Servicio II | 263 MPa | 327.8 MPa | 0.803 | Cumple |
| exterior | Fatiga categoría C | 49.32 MPa | 69 MPa | 0.715 | Cumple |
| exterior | Estabilidad lateral durante construcción | 5267 kN.m | 1.409e+04 kN.m | 0.374 | Cumple |
| exterior | Deflexión vehicular - Servicio I | 31.65 mm | 62.5 mm | 0.506 | Cumple |
| exterior | Deflexión vehicular y peatonal - Servicio I | 49.21 mm | 50 mm | 0.984 | Cumple |

## Resultado gobernante

Controla **Deflexión vehicular y peatonal - Servicio I**, DCR = 0.984.

## Pendientes y limitaciones

- Factores obtenidos con parrilla elástica lineal; no representan esfuerzos locales de losa.
- La rigidez compuesta supone interacción total y debe conciliarse con los conectores de corte.
- Los diafragmas se representan solo mediante la continuidad transversal de la losa; incorporar su rigidez explícita si se confirma su geometría.
- El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

# Análisis y diseño de vigas principales - Puente Molinohuayco - piloto de vigas principales (PROPUESTA-R00)

- Revisión: `PROPUESTA-R00`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **NO_CUMPLE**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.42528 |
| momento_exterior | 0.48844 |
| corte_interior | 0.64500 |
| corte_exterior | 0.44320 |
| fatiga_interior | 0.36693 |
| fatiga_exterior | 0.40415 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.398e+04 kN.m | 2.119e+04 kN.m | 0.660 | Cumple |
| interior | Ductilidad Dp/Dt | 0.4331 - | 0.42 - | 1.031 | No cumple |
| interior | Compacidad del alma en flexión positiva | 65.88 - | 90.53 - | 0.728 | Cumple |
| interior | Corte del alma | 1369 kN | 3559 kN | 0.385 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 204.6 MPa | 327.8 MPa | 0.624 | Cumple |
| interior | Fatiga categoría C | 44.95 MPa | 69 MPa | 0.652 | Cumple |
| interior | Estabilidad lateral durante construcción | 5276 kN.m | 1.226e+04 kN.m | 0.430 | Cumple |
| interior | Deflexión vehicular - Servicio I | 28.04 mm | 62.5 mm | 0.449 | Cumple |
| interior | Deflexión vehicular y peatonal - Servicio I | 28.04 mm | 50 mm | 0.561 | Cumple |
| exterior | Flexión positiva - Resistencia I | 1.894e+04 kN.m | 2.119e+04 kN.m | 0.894 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.4331 - | 0.42 - | 1.031 | No cumple |
| exterior | Compacidad del alma en flexión positiva | 65.88 - | 90.53 - | 0.728 | Cumple |
| exterior | Corte del alma | 1471 kN | 3559 kN | 0.413 | Cumple |
| exterior | Esfuerzo elástico - Servicio II | 268.1 MPa | 327.8 MPa | 0.818 | Cumple |
| exterior | Fatiga categoría C | 49.51 MPa | 69 MPa | 0.718 | Cumple |
| exterior | Estabilidad lateral durante construcción | 5183 kN.m | 1.226e+04 kN.m | 0.423 | Cumple |
| exterior | Deflexión vehicular - Servicio I | 32.2 mm | 62.5 mm | 0.515 | Cumple |
| exterior | Deflexión vehicular y peatonal - Servicio I | 50.08 mm | 50 mm | 1.002 | No cumple |

## Resultado gobernante

Controla **Ductilidad Dp/Dt**, DCR = 1.031.

## Pendientes y limitaciones

- Factores obtenidos con parrilla elástica lineal; no representan esfuerzos locales de losa.
- La rigidez compuesta supone interacción total y debe conciliarse con los conectores de corte.
- Los diafragmas se representan solo mediante la continuidad transversal de la losa; incorporar su rigidez explícita si se confirma su geometría.
- El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

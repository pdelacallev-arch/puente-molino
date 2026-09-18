# Análisis y diseño de vigas principales - Puente Molinohuayco - piloto de vigas principales (MODIFICADO-R01)

- Revisión: `MODIFICADO-R01`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **NO_CUMPLE**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.42505 |
| momento_exterior | 0.48774 |
| corte_interior | 0.64412 |
| corte_exterior | 0.44358 |
| fatiga_interior | 0.36665 |
| fatiga_exterior | 0.40366 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.38e+04 kN.m | 2.095e+04 kN.m | 0.659 | Cumple |
| interior | Ductilidad Dp/Dt | 0.4104 - | 0.42 - | 0.977 | Cumple |
| interior | Compacidad del alma en flexión positiva | 72.34 - | 90.53 - | 0.799 | Cumple |
| interior | Corte del alma | 1353 kN | 2125 kN | 0.637 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 209.4 MPa | 327.8 MPa | 0.639 | Cumple |
| interior | Fatiga categoría C | 47.13 MPa | 69 MPa | 0.683 | Cumple |
| interior | Estabilidad lateral durante construcción | 5131 kN.m | 1.16e+04 kN.m | 0.442 | Cumple |
| interior | Deflexión vehicular - Servicio I | 28.76 mm | 62.5 mm | 0.460 | Cumple |
| interior | Deflexión vehicular y peatonal - Servicio I | 28.76 mm | 50 mm | 0.575 | Cumple |
| exterior | Flexión positiva - Resistencia I | 1.875e+04 kN.m | 2.095e+04 kN.m | 0.895 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.4104 - | 0.42 - | 0.977 | Cumple |
| exterior | Compacidad del alma en flexión positiva | 72.34 - | 90.53 - | 0.799 | Cumple |
| exterior | Corte del alma | 1457 kN | 2125 kN | 0.685 | Cumple |
| exterior | Esfuerzo elástico - Servicio II | 273.5 MPa | 327.8 MPa | 0.834 | Cumple |
| exterior | Fatiga categoría C | 51.88 MPa | 69 MPa | 0.752 | Cumple |
| exterior | Estabilidad lateral durante construcción | 5037 kN.m | 1.16e+04 kN.m | 0.434 | Cumple |
| exterior | Deflexión vehicular - Servicio I | 33 mm | 62.5 mm | 0.528 | Cumple |
| exterior | Deflexión vehicular y peatonal - Servicio I | 51.36 mm | 50 mm | 1.027 | No cumple |

## Resultado gobernante

Controla **Deflexión vehicular y peatonal - Servicio I**, DCR = 1.027.

## Pendientes y limitaciones

- Factores obtenidos con parrilla elástica lineal; no representan esfuerzos locales de losa.
- La rigidez compuesta supone interacción total y debe conciliarse con los conectores de corte.
- Los diafragmas se representan solo mediante la continuidad transversal de la losa; incorporar su rigidez explícita si se confirma su geometría.
- El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

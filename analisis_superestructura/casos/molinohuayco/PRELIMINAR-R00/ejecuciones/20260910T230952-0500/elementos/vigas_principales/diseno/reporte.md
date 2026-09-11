# Análisis y diseño de vigas principales - Puente Molinohuayco - piloto de vigas principales

- Revisión: `PRELIMINAR-R00`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **NO_CUMPLE**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.42460 |
| momento_exterior | 0.48683 |
| corte_interior | 0.64196 |
| corte_exterior | 0.44452 |
| fatiga_interior | 0.36607 |
| fatiga_exterior | 0.40303 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.358e+04 kN.m | 1.918e+04 kN.m | 0.708 | Cumple |
| interior | Ductilidad Dp/Dt | 0.4487 - | 0.42 - | 1.068 | No cumple |
| interior | Compacidad del alma en flexión positiva | 94.43 - | 90.53 - | 1.043 | No cumple |
| interior | Corte del alma | 1334 kN | 1424 kN | 0.937 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 202.6 MPa | 327.8 MPa | 0.618 | Cumple |
| interior | Fatiga categoría C | 48.81 MPa | 69 MPa | 0.707 | Cumple |
| interior | Estabilidad lateral durante construcción | 1794 kN.m | 9248 kN.m | 0.194 | Cumple |
| interior | Deflexión por carga viva | 50.31 mm | 62.5 mm | 0.805 | Cumple |
| exterior | Flexión positiva - Resistencia I | 1.853e+04 kN.m | 1.918e+04 kN.m | 0.966 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.4487 - | 0.42 - | 1.068 | No cumple |
| exterior | Compacidad del alma en flexión positiva | 94.43 - | 90.53 - | 1.043 | No cumple |
| exterior | Corte del alma | 1441 kN | 1424 kN | 1.012 | No cumple |
| exterior | Esfuerzo elástico - Servicio II | 270.9 MPa | 327.8 MPa | 0.826 | Cumple |
| exterior | Fatiga categoría C | 53.74 MPa | 69 MPa | 0.779 | Cumple |
| exterior | Estabilidad lateral durante construcción | 1700 kN.m | 9248 kN.m | 0.184 | Cumple |
| exterior | Deflexión por carga viva | 57.68 mm | 62.5 mm | 0.923 | Cumple |

## Resultado gobernante

Controla **Ductilidad Dp/Dt**, DCR = 1.068.

## Pendientes y limitaciones

- Acción compuesta condicionada a la verificación externa de conectores.
- Rigidizadores de apoyo/intermedios fuera de alcance y pendientes de confirmación.
- Arriostramiento permanente y temporal pendiente de confirmación externa.
- Factores obtenidos con parrilla elástica lineal; no representan esfuerzos locales de losa.
- La rigidez compuesta supone interacción total y debe conciliarse con los conectores de corte.
- Los diafragmas se representan solo mediante la continuidad transversal de la losa; incorporar su rigidez explícita si se confirma su geometría.
- El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

# Análisis y diseño de vigas principales - Benchmark Bartra actualizado a MTC 2018

- Revisión: `R00`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **CONDICIONAL**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.54388 |
| momento_exterior | 0.51000 |
| corte_interior | 0.71166 |
| corte_exterior | 0.51000 |
| fatiga_interior | 0.31114 |
| fatiga_exterior | 0.42500 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.681e+04 kN.m | 2.35e+04 kN.m | 0.715 | Cumple |
| interior | Ductilidad Dp/Dt | 0.3344 - | 0.42 - | 0.796 | Cumple |
| interior | Compacidad del alma en flexión positiva | 66.4 - | 90.76 - | 0.732 | Cumple |
| interior | Corte del alma | 1540 kN | 1865 kN | 0.826 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 207 MPa | 326.1 MPa | 0.635 | Cumple |
| interior | Fatiga categoría C | 32.91 MPa | 69 MPa | 0.477 | Cumple |
| interior | Estabilidad lateral durante construcción | 5611 kN.m | 1.355e+04 kN.m | 0.414 | Cumple |
| interior | Deflexión por carga viva | 51.16 mm | 62.5 mm | 0.819 | Cumple |
| exterior | Flexión positiva - Resistencia I | 1.73e+04 kN.m | 2.533e+04 kN.m | 0.683 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.2786 - | 0.42 - | 0.663 | Cumple |
| exterior | Compacidad del alma en flexión positiva | 50.46 - | 90.76 - | 0.556 | Cumple |
| exterior | Corte del alma | 1391 kN | 1865 kN | 0.746 | Cumple |
| exterior | Esfuerzo elástico - Servicio II | 215 MPa | 326.1 MPa | 0.659 | Cumple |
| exterior | Fatiga categoría C | 44.52 MPa | 69 MPa | 0.645 | Cumple |
| exterior | Estabilidad lateral durante construcción | 6377 kN.m | 1.355e+04 kN.m | 0.471 | Cumple |
| exterior | Deflexión por carga viva | 46.08 mm | 62.5 mm | 0.737 | Cumple |

## Resultado gobernante

Controla **Corte del alma**, DCR = 0.826.

## Pendientes y limitaciones

- Acción compuesta condicionada a la verificación externa de conectores.
- Rigidizadores de apoyo/intermedios fuera de alcance y pendientes de confirmación.
- Arriostramiento permanente y temporal pendiente de confirmación externa.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

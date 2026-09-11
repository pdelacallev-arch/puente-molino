# Análisis y diseño de vigas principales - Puente Molinohuayco - piloto de vigas principales

- Revisión: `FINAL-R00`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **NO_CUMPLE**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.53973 |
| momento_exterior | 0.42000 |
| corte_interior | 0.71166 |
| corte_exterior | 0.42700 |
| fatiga_interior | 0.30882 |
| fatiga_exterior | 0.35000 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.515e+04 kN.m | 1.918e+04 kN.m | 0.790 | Cumple |
| interior | Ductilidad Dp/Dt | 0.4487 - | 0.42 - | 1.068 | No cumple |
| interior | Compacidad del alma en flexión positiva | 94.43 - | 90.53 - | 1.043 | No cumple |
| interior | Corte del alma | 1412 kN | 1424 kN | 0.992 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 223.5 MPa | 327.8 MPa | 0.682 | Cumple |
| interior | Fatiga categoría C | 41.18 MPa | 69 MPa | 0.597 | Cumple |
| interior | Estabilidad lateral durante construcción | 1794 kN.m | 9248 kN.m | 0.194 | Cumple |
| interior | Deflexión por carga viva | 63.95 mm | 62.5 mm | 1.023 | No cumple |
| exterior | Flexión positiva - Resistencia I | 1.761e+04 kN.m | 1.918e+04 kN.m | 0.919 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.4487 - | 0.42 - | 1.068 | No cumple |
| exterior | Compacidad del alma en flexión positiva | 94.43 - | 90.53 - | 1.043 | No cumple |
| exterior | Corte del alma | 1421 kN | 1424 kN | 0.998 | Cumple |
| exterior | Esfuerzo elástico - Servicio II | 258.7 MPa | 327.8 MPa | 0.789 | Cumple |
| exterior | Fatiga categoría C | 46.67 MPa | 69 MPa | 0.676 | Cumple |
| exterior | Estabilidad lateral durante construcción | 1700 kN.m | 9248 kN.m | 0.184 | Cumple |
| exterior | Deflexión por carga viva | 49.76 mm | 62.5 mm | 0.796 | Cumple |

## Resultado gobernante

Controla **Ductilidad Dp/Dt**, DCR = 1.068.

## Pendientes y limitaciones

- Geometría fuera del rango de MTC Tabla 2.6.4.2.2.2b-1; los factores aproximados requieren contraste con análisis refinado.
- El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

# Análisis y diseño de vigas principales - Puente Molinohuayco - piloto de vigas principales (MODIFICADO-R00)

- Revisión: `MODIFICADO-R00`
- Norma: Manual de Puentes MTC 2018
- Método: Bartra pp. 113-165, actualizado y reorganizado por etapas conforme a MTC 2018.
- Estado: **CONDICIONAL**

## Hipótesis y alcance

Puente recto y simplemente apoyado con vigas I de placas. El diseño de conectores, rigidizadores y diafragmas no forma parte de este cálculo.

## Factores de distribución

| Factor | Valor |
|---|---:|
| momento_interior | 0.42496 |
| momento_exterior | 0.48776 |
| corte_interior | 0.64288 |
| corte_exterior | 0.44412 |
| fatiga_interior | 0.36652 |
| fatiga_exterior | 0.40369 |

## Verificaciones

| Viga | Estado límite | Demanda | Capacidad | DCR | Estado |
|---|---|---:|---:|---:|---|
| interior | Flexión positiva - Resistencia I | 1.379e+04 kN.m | 2.095e+04 kN.m | 0.659 | Cumple |
| interior | Ductilidad Dp/Dt | 0.4104 - | 0.42 - | 0.977 | Cumple |
| interior | Compacidad del alma en flexión positiva | 72.34 - | 90.53 - | 0.799 | Cumple |
| interior | Corte del alma | 1352 kN | 2125 kN | 0.636 | Cumple |
| interior | Esfuerzo elástico - Servicio II | 198 MPa | 327.8 MPa | 0.604 | Cumple |
| interior | Fatiga categoría C | 47.11 MPa | 69 MPa | 0.683 | Cumple |
| interior | Estabilidad lateral durante construcción | 1962 kN.m | 1.16e+04 kN.m | 0.169 | Cumple |
| interior | Deflexión por carga viva | 48.63 mm | 62.5 mm | 0.778 | Cumple |
| exterior | Flexión positiva - Resistencia I | 1.875e+04 kN.m | 2.095e+04 kN.m | 0.895 | Cumple |
| exterior | Ductilidad Dp/Dt | 0.4104 - | 0.42 - | 0.977 | Cumple |
| exterior | Compacidad del alma en flexión positiva | 72.34 - | 90.53 - | 0.799 | Cumple |
| exterior | Corte del alma | 1457 kN | 2125 kN | 0.686 | Cumple |
| exterior | Esfuerzo elástico - Servicio II | 264.1 MPa | 327.8 MPa | 0.806 | Cumple |
| exterior | Fatiga categoría C | 51.89 MPa | 69 MPa | 0.752 | Cumple |
| exterior | Estabilidad lateral durante construcción | 1869 kN.m | 1.16e+04 kN.m | 0.161 | Cumple |
| exterior | Deflexión por carga viva | 55.82 mm | 62.5 mm | 0.893 | Cumple |

## Resultado gobernante

Controla **Ductilidad Dp/Dt**, DCR = 0.977.

## Pendientes y limitaciones

- Acción compuesta condicionada a la verificación externa de conectores.
- Rigidizadores de apoyo/intermedios fuera de alcance y pendientes de confirmación.
- Arriostramiento permanente y temporal pendiente de confirmación externa.
- Factores obtenidos con parrilla elástica lineal; no representan esfuerzos locales de losa.
- La rigidez compuesta supone interacción total y debe conciliarse con los conectores de corte.
- Los diafragmas se representan solo mediante la continuidad transversal de la losa; incorporar su rigidez explícita si se confirma su geometría.
- El alma se declaró rigidizada, pero la capacidad se evaluó conservadoramente sin campo de tensión.

Los resultados deben ser revisados y aprobados por el ingeniero estructural responsable.

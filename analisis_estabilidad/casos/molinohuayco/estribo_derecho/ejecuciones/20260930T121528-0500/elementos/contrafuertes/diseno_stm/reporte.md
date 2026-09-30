# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3

**Resultado global: NO CUMPLE**

## 1. Objetivo y datos

Se dimensiona un único detalle de armado para los tres contrafuertes. Las acciones se leen del análisis FEM 2D existente y no se recalculan.

| Parámetro | Valor | Unidad | Fuente/estado |
|---|---:|---|---|
| Altura | 10.110 | m | análisis |
| Longitud base / corona | 6.500 / 0.400 | m | análisis |
| Espesor | 0.400 | m | análisis |
| f'c | 280 (27.46) | kg/cm² (MPa) | proyecto |
| fy | 4200 (411.88) | kg/cm² (MPa) | proyecto |
| Recubrimiento | 75 | mm | adoptado |
| Vu base | 1068.960 | kN | envolvente |
| Mu base | 5252.826 | kN·m | envolvente |

## 2. Modelo resistente

En cada límite inferior de zona, el momento se equilibra con la componente vertical del tirante inclinado del lomo y la compresión junto a la pantalla. La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM sólo orientan este campo resistente.

| Zona | z | Vu | Mu | T | C | error equilibrio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.000 m | 1068.96 kN | 5252.83 kN·m | 976.86 kN | 1008.97 kN | 0.00e+00 |
| 2 | 3.370 m | 669.49 kN | 2155.62 kN·m | 588.70 kN | 622.55 kN | 0.00e+00 |
| 3 | 6.740 m | 281.35 kN | 482.82 kN·m | 251.38 kN | 263.20 kN | 0.00e+00 |

## 3. Armado adoptado

Barras principales comunes: **1"**. Se mantienen **2 barras continuas hasta la corona**.

| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6–1" en 2 capa(s) [3, 3] | 2635 mm² | 3040 mm² | 0.867 | 0.170 | 0.292 | 0.531 | 211.1 MPa |
| 2 | 4–1" en 1 capa(s) [4] | 1588 mm² | 2027 mm² | 0.784 | 0.103 | 0.180 | 0.488 | 190.5 MPa |
| 3 | 2–1" en 1 capa(s) [2] | 678 mm² | 1013 mm² | 0.669 | 0.044 | 0.076 | 0.391 | 162.3 MPa |

Malla ortogonal en ambas caras: **1/2" @ 210 mm** en dirección horizontal y vertical.

## 4. Anclaje, interfaz y cortes

| Control | Disponible | Requerido | Solución | DCR | Estado |
|---|---:|---:|---|---:|---|
| contrafuerte–zapata | 1425 mm | 951 mm | recto | 0.667 | CUMPLE |
| corona | 250 mm | 335 mm | NO CUMPLE | 1.342 | NO CUMPLE |
| Empalme Clase B | 2000 mm | 1236 mm | máximo 50% | 0.618 | CUMPLE |
| Corte-fricción base | — | φVn=3871.9 kN | unión monolítica | 0.276 | CUMPLE |

### Zonas nodales

| Ubicación | Tipo | Demanda | φNn | DCR |
|---|---|---:|---:|---:|
| pantalla–alma / zona 1 | CCT: ancla tirante en una dirección | 1009.0 kN | 3459.8 kN | 0.292 |
| pantalla–alma / zona 2 | CCT: ancla tirante en una dirección | 622.5 kN | 3459.8 kN | 0.180 |
| pantalla–alma / zona 3 | CCT: ancla tirante en una dirección | 263.2 kN | 3459.8 kN | 0.076 |
| contrafuerte–zapata | CCT: anclaje del tirante principal | 1009.0 kN | 3459.8 kN | 0.292 |
| corona | CCT: anclaje del tirante principal | 263.2 kN | 3459.8 kN | 0.076 |

Las barras adicionales se cortan sólo después de prolongar una longitud de desarrollo completa más allá del punto teórico:

- 2 barra(s): corte teórico z=3.370 m; fin real z=4.192 m; DCR=0.990.
- 2 barra(s): corte teórico z=6.740 m; fin real z=7.562 m; DCR=0.990.

## 5. DCR individuales

| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |
|---|---:|---:|---:|
| CF-C1 | 0.867 | 0.170 | 0.531 |
| CF-C2 | 0.684 | 0.148 | 0.484 |
| CF-C3 | 0.867 | 0.170 | 0.531 |

## 6. Validaciones y límites

- Envolvente común cubre los 15 resultados: **sí**.
- Error máximo de equilibrio STM: `0.00e+00`.
- DCR máximo global: **1.342**.
- Constructibilidad dentro de 0.40 m: **conforme**.

- El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.
- La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.
- El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.
- El diseño requiere revisión y firma del ingeniero responsable del proyecto.

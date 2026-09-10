# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3

**Resultado global: NO CUMPLE**

## 1. Objetivo y datos

Se dimensiona un único detalle de armado para los tres contrafuertes. Las acciones se leen del análisis FEM 2D existente y no se recalculan.

| Parámetro | Valor | Unidad | Fuente/estado |
|---|---:|---|---|
| Altura | 10.800 | m | análisis |
| Longitud base / corona | 6.500 / 0.400 | m | análisis |
| Espesor | 0.400 | m | análisis |
| f'c | 280 (27.46) | kg/cm² (MPa) | proyecto |
| fy | 4200 (411.88) | kg/cm² (MPa) | proyecto |
| Recubrimiento | 75 | mm | adoptado |
| Vu base | 1215.792 | kN | envolvente |
| Mu base | 6359.901 | kN·m | envolvente |

## 2. Modelo resistente

En cada límite inferior de zona, el momento se equilibra con la componente vertical del tirante inclinado del lomo y la compresión junto a la pantalla. La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM sólo orientan este campo resistente.

| Zona | z | Vu | Mu | T | C | error equilibrio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.000 m | 1215.79 kN | 6359.90 kN·m | 1162.65 kN | 1199.82 kN | 0.00e+00 |
| 2 | 3.600 m | 762.50 kN | 2613.18 kN·m | 701.50 kN | 739.86 kN | 0.00e+00 |
| 3 | 7.200 m | 323.01 kN | 586.94 kN·m | 300.27 kN | 314.80 kN | 0.00e+00 |

## 3. Armado adoptado

Barras principales comunes: **1"**. Se mantienen **2 barras continuas hasta la corona**.

| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7–1" en 2 capa(s) [4, 3] | 3136 mm² | 3547 mm² | 0.884 | 0.210 | 0.347 | 0.603 | 215.5 MPa |
| 2 | 4–1" en 1 capa(s) [4] | 1892 mm² | 2027 mm² | 0.934 | 0.127 | 0.214 | 0.556 | 227.1 MPa |
| 3 | 2–1" en 1 capa(s) [2] | 810 mm² | 1013 mm² | 0.799 | 0.054 | 0.091 | 0.449 | 194.0 MPa |

Malla ortogonal en ambas caras: **1/2" @ 210 mm** en dirección horizontal y vertical.

## 4. Anclaje, interfaz y cortes

| Control | Disponible | Requerido | Solución | DCR | Estado |
|---|---:|---:|---|---:|---|
| contrafuerte–zapata | 1425 mm | 951 mm | recto | 0.667 | CUMPLE |
| corona | 250 mm | 335 mm | NO CUMPLE | 1.342 | NO CUMPLE |
| Empalme Clase B | 2000 mm | 1236 mm | máximo 50% | 0.618 | CUMPLE |
| Corte-fricción base | — | φVn=4051.8 kN | unión monolítica | 0.300 | CUMPLE |

### Zonas nodales

| Ubicación | Tipo | Demanda | φNn | DCR |
|---|---|---:|---:|---:|
| pantalla–alma / zona 1 | CCT: ancla tirante en una dirección | 1199.8 kN | 3459.8 kN | 0.347 |
| pantalla–alma / zona 2 | CCT: ancla tirante en una dirección | 739.9 kN | 3459.8 kN | 0.214 |
| pantalla–alma / zona 3 | CCT: ancla tirante en una dirección | 314.8 kN | 3459.8 kN | 0.091 |
| contrafuerte–zapata | CCT: anclaje del tirante principal | 1199.8 kN | 3459.8 kN | 0.347 |
| corona | CCT: anclaje del tirante principal | 314.8 kN | 3459.8 kN | 0.091 |

Las barras adicionales se cortan sólo después de prolongar una longitud de desarrollo completa más allá del punto teórico:

- 3 barra(s): corte teórico z=3.600 m; fin real z=4.436 m; DCR=0.990.
- 2 barra(s): corte teórico z=7.200 m; fin real z=8.036 m; DCR=0.990.

## 5. DCR individuales

| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |
|---|---:|---:|---:|
| CF-C1 | 0.934 | 0.210 | 0.603 |
| CF-C2 | 0.670 | 0.176 | 0.536 |
| CF-C3 | 0.934 | 0.210 | 0.603 |

## 6. Validaciones y límites

- Envolvente común cubre los 15 resultados: **sí**.
- Error máximo de equilibrio STM: `0.00e+00`.
- DCR máximo global: **1.342**.
- Constructibilidad dentro de 0.40 m: **conforme**.

- El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.
- La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.
- El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.
- El diseño requiere revisión y firma del ingeniero responsable del proyecto.

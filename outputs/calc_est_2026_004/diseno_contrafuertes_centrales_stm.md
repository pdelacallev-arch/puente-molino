# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3

**Resultado global: CUMPLE**

## 1. Objetivo y datos

Se dimensiona un único detalle de armado para los tres contrafuertes. Las acciones se leen del análisis FEM 2D existente y no se recalculan.

| Parámetro | Valor | Unidad | Fuente/estado |
|---|---:|---|---|
| Altura | 9.800 | m | análisis |
| Longitud base / corona | 6.100 / 1.170 | m | análisis |
| Espesor | 0.400 | m | análisis |
| f'c | 280 (27.46) | kg/cm² (MPa) | proyecto |
| fy | 4200 (411.88) | kg/cm² (MPa) | proyecto |
| Recubrimiento | 75 | mm | adoptado |
| Vu base | 1045.496 | kN | envolvente |
| Mu base | 5013.558 | kN·m | envolvente |

## 2. Modelo resistente

En cada límite inferior de zona, el momento se equilibra con la componente vertical del tirante inclinado del lomo y la compresión junto a la pantalla. La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM sólo orientan este campo resistente.

| Zona | z | Vu | Mu | T | C | error equilibrio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.000 m | 1045.50 kN | 5013.56 kN·m | 953.53 kN | 1051.79 kN | 0.00e+00 |
| 2 | 3.267 m | 659.78 kN | 2067.40 kN·m | 541.88 kN | 638.44 kN | 0.00e+00 |
| 3 | 6.533 m | 279.32 kN | 465.66 kN·m | 198.39 kN | 259.95 kN | 0.00e+00 |

## 3. Armado adoptado

Barras principales comunes: **1"**. Se mantienen **2 barras continuas hasta la corona**.

| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6–1" en 2 capa(s) [3, 3] | 2572 mm² | 3040 mm² | 0.846 | 0.183 | 0.304 | 0.554 | 206.2 MPa |
| 2 | 3–1" en 1 capa(s) [3] | 1462 mm² | 1520 mm² | 0.962 | 0.105 | 0.185 | 0.482 | 233.9 MPa |
| 3 | 2–1" en 1 capa(s) [2] | 535 mm² | 1013 mm² | 0.528 | 0.041 | 0.075 | 0.331 | 128.2 MPa |

Malla ortogonal en ambas caras: **1/2" @ 210 mm** en dirección horizontal y vertical.

## 4. Anclaje, interfaz y cortes

| Control | Disponible | Requerido | Solución | DCR | Estado |
|---|---:|---:|---|---:|---|
| contrafuerte–zapata | 1425 mm | 951 mm | recto | 0.667 | CUMPLE |
| corona | 1020 mm | 951 mm | recto | 0.932 | CUMPLE |
| Empalme Clase B | 2000 mm | 1236 mm | máximo 50% | 0.618 | CUMPLE |
| Corte-fricción base | — | φVn=3734.8 kN | unión monolítica | 0.280 | CUMPLE |

### Zonas nodales

| Ubicación | Tipo | Demanda | φNn | DCR |
|---|---|---:|---:|---:|
| pantalla–alma / zona 1 | CCT: ancla tirante en una dirección | 1051.8 kN | 3459.8 kN | 0.304 |
| pantalla–alma / zona 2 | CCT: ancla tirante en una dirección | 638.4 kN | 3459.8 kN | 0.185 |
| pantalla–alma / zona 3 | CCT: ancla tirante en una dirección | 259.9 kN | 3459.8 kN | 0.075 |
| contrafuerte–zapata | CCT: anclaje del tirante principal | 1051.8 kN | 3459.8 kN | 0.304 |
| corona | CCT: anclaje del tirante principal | 259.9 kN | 3459.8 kN | 0.075 |

Las barras adicionales se cortan sólo después de prolongar una longitud de desarrollo completa más allá del punto teórico:

- 3 barra(s): corte teórico z=3.267 m; fin real z=4.124 m; DCR=0.990.
- 1 barra(s): corte teórico z=6.533 m; fin real z=7.391 m; DCR=0.990.

## 5. DCR individuales

| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |
|---|---:|---:|---:|
| CF-C1 | 0.962 | 0.183 | 0.554 |
| CF-C2 | 0.681 | 0.160 | 0.510 |
| CF-C3 | 0.962 | 0.183 | 0.554 |

## 6. Validaciones y límites

- Envolvente común cubre los 15 resultados: **sí**.
- Error máximo de equilibrio STM: `0.00e+00`.
- DCR máximo global: **0.990**.
- Constructibilidad dentro de 0.40 m: **conforme**.

- El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.
- La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.
- El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.
- El diseño requiere revisión y firma del ingeniero responsable del proyecto.

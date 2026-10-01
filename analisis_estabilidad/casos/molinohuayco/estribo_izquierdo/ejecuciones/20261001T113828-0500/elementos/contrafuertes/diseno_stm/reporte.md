# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3

**Resultado global: NO CUMPLE**

## 1. Objetivo y datos

Se dimensiona un único detalle de armado para los tres contrafuertes. Las acciones se leen del análisis FEM 2D existente y no se recalculan.

| Parámetro | Valor | Unidad | Fuente/estado |
|---|---:|---|---|
| Altura | 8.280 | m | análisis |
| Longitud base / corona | 6.500 / 0.400 | m | análisis |
| Espesor | 0.400 | m | análisis |
| f'c | 280 (27.46) | kg/cm² (MPa) | proyecto |
| fy | 4200 (411.88) | kg/cm² (MPa) | proyecto |
| Recubrimiento | 75 | mm | adoptado |
| Vu base | 728.440 | kN | envolvente |
| Mu base | 2959.614 | kN·m | envolvente |

## 2. Modelo resistente

En cada límite inferior de zona, el momento se equilibra con la componente vertical del tirante inclinado del lomo y la compresión junto a la pantalla. La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM sólo orientan este campo resistente.

| Zona | z | Vu | Mu | T | C | error equilibrio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.000 m | 728.44 kN | 2959.61 kN·m | 583.19 kN | 605.63 kN | 0.00e+00 |
| 2 | 2.760 m | 459.29 kN | 1210.26 kN·m | 352.04 kN | 378.25 kN | 0.00e+00 |
| 3 | 5.520 m | 189.36 kN | 268.12 kN·m | 148.89 kN | 156.78 kN | 0.00e+00 |

## 3. Armado adoptado

Barras principales comunes: **1"**. Se mantienen **2 barras continuas hasta la corona**.

| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4–1" en 1 capa(s) [4] | 1573 mm² | 2027 mm² | 0.776 | 0.102 | 0.175 | 0.360 | 188.8 MPa |
| 2 | 2–1" en 1 capa(s) [2] | 950 mm² | 1013 mm² | 0.937 | 0.063 | 0.109 | 0.335 | 227.5 MPa |
| 3 | 2–1" en 1 capa(s) [2] | 402 mm² | 1013 mm² | 0.396 | 0.026 | 0.045 | 0.264 | 96.0 MPa |

Malla ortogonal en ambas caras: **1/2" @ 210 mm** en dirección horizontal y vertical.

## 4. Anclaje, interfaz y cortes

| Control | Disponible | Requerido | Solución | DCR | Estado |
|---|---:|---:|---|---:|---|
| contrafuerte–zapata | 1425 mm | 951 mm | recto | 0.667 | CUMPLE |
| corona | 250 mm | 335 mm | NO CUMPLE | 1.342 | NO CUMPLE |
| Empalme Clase B | 2000 mm | 1236 mm | máximo 50% | 0.618 | CUMPLE |
| Corte-fricción base | — | φVn=3511.8 kN | unión monolítica | 0.207 | CUMPLE |

### Zonas nodales

| Ubicación | Tipo | Demanda | φNn | DCR |
|---|---|---:|---:|---:|
| pantalla–alma / zona 1 | CCT: ancla tirante en una dirección | 605.6 kN | 3459.8 kN | 0.175 |
| pantalla–alma / zona 2 | CCT: ancla tirante en una dirección | 378.3 kN | 3459.8 kN | 0.109 |
| pantalla–alma / zona 3 | CCT: ancla tirante en una dirección | 156.8 kN | 3459.8 kN | 0.045 |
| contrafuerte–zapata | CCT: anclaje del tirante principal | 605.6 kN | 3459.8 kN | 0.175 |
| corona | CCT: anclaje del tirante principal | 156.8 kN | 3459.8 kN | 0.045 |

Las barras adicionales se cortan sólo después de prolongar una longitud de desarrollo completa más allá del punto teórico:

- 2 barra(s): corte teórico z=2.760 m; fin real z=3.533 m; DCR=0.990.

## 5. DCR individuales

| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |
|---|---:|---:|---:|
| CF-C1 | 0.937 | 0.102 | 0.360 |
| CF-C2 | 0.752 | 0.099 | 0.356 |
| CF-C3 | 0.937 | 0.102 | 0.360 |

## 6. Validaciones y límites

- Envolvente común cubre los 15 resultados: **sí**.
- Error máximo de equilibrio STM: `0.00e+00`.
- DCR máximo global: **1.342**.
- Constructibilidad dentro de 0.40 m: **conforme**.

- El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.
- La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.
- El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.
- El diseño requiere revisión y firma del ingeniero responsable del proyecto.

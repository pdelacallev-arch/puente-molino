# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3

**Resultado global: NO CUMPLE**

## 1. Objetivo y datos

Se dimensiona un único detalle de armado para los tres contrafuertes. Las acciones se leen del análisis FEM 2D existente y no se recalculan.

| Parámetro | Valor | Unidad | Fuente/estado |
|---|---:|---|---|
| Altura | 7.850 | m | análisis |
| Longitud base / corona | 6.500 / 0.400 | m | análisis |
| Espesor | 0.400 | m | análisis |
| f'c | 280 (27.46) | kg/cm² (MPa) | proyecto |
| fy | 4200 (411.88) | kg/cm² (MPa) | proyecto |
| Recubrimiento | 75 | mm | adoptado |
| Vu base | 665.331 | kN | envolvente |
| Mu base | 2545.148 | kN·m | envolvente |

## 2. Modelo resistente

En cada límite inferior de zona, el momento se equilibra con la componente vertical del tirante inclinado del lomo y la compresión junto a la pantalla. La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM sólo orientan este campo resistente.

| Zona | z | Vu | Mu | T | C | error equilibrio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.000 m | 665.33 kN | 2545.15 kN·m | 511.53 kN | 535.42 kN | 0.00e+00 |
| 2 | 2.617 m | 417.43 kN | 1040.49 kN·m | 308.75 kN | 333.79 kN | 0.00e+00 |
| 3 | 5.233 m | 171.54 kN | 229.82 kN·m | 130.25 kN | 137.74 kN | 0.00e+00 |

## 3. Armado adoptado

Barras principales comunes: **1"**. Se mantienen **2 barras continuas hasta la corona**.

| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3–1" en 1 capa(s) [3] | 1380 mm² | 1520 mm² | 0.908 | 0.094 | 0.155 | 0.329 | 220.7 MPa |
| 2 | 2–1" en 1 capa(s) [2] | 833 mm² | 1013 mm² | 0.822 | 0.059 | 0.096 | 0.305 | 199.4 MPa |
| 3 | 2–1" en 1 capa(s) [2] | 351 mm² | 1013 mm² | 0.347 | 0.024 | 0.040 | 0.239 | 83.9 MPa |

Malla ortogonal en ambas caras: **1/2" @ 210 mm** en dirección horizontal y vertical.

## 4. Anclaje, interfaz y cortes

| Control | Disponible | Requerido | Solución | DCR | Estado |
|---|---:|---:|---|---:|---|
| contrafuerte–zapata | 1425 mm | 951 mm | recto | 0.667 | CUMPLE |
| corona | 250 mm | 335 mm | NO CUMPLE | 1.342 | NO CUMPLE |
| Empalme Clase B | 2000 mm | 1236 mm | máximo 50% | 0.618 | CUMPLE |
| Corte-fricción base | — | φVn=3351.9 kN | unión monolítica | 0.198 | CUMPLE |

### Zonas nodales

| Ubicación | Tipo | Demanda | φNn | DCR |
|---|---|---:|---:|---:|
| pantalla–alma / zona 1 | CCT: ancla tirante en una dirección | 535.4 kN | 3459.8 kN | 0.155 |
| pantalla–alma / zona 2 | CCT: ancla tirante en una dirección | 333.8 kN | 3459.8 kN | 0.096 |
| pantalla–alma / zona 3 | CCT: ancla tirante en una dirección | 137.7 kN | 3459.8 kN | 0.040 |
| contrafuerte–zapata | CCT: anclaje del tirante principal | 535.4 kN | 3459.8 kN | 0.155 |
| corona | CCT: anclaje del tirante principal | 137.7 kN | 3459.8 kN | 0.040 |

Las barras adicionales se cortan sólo después de prolongar una longitud de desarrollo completa más allá del punto teórico:

- 1 barra(s): corte teórico z=2.617 m; fin real z=3.375 m; DCR=0.990.

## 5. DCR individuales

| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |
|---|---:|---:|---:|
| CF-C1 | 0.908 | 0.093 | 0.326 |
| CF-C2 | 0.836 | 0.093 | 0.329 |
| CF-C3 | 0.908 | 0.093 | 0.326 |

## 6. Validaciones y límites

- Envolvente común cubre los 15 resultados: **sí**.
- Error máximo de equilibrio STM: `0.00e+00`.
- DCR máximo global: **1.342**.
- Constructibilidad dentro de 0.40 m: **conforme**.

- El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.
- La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.
- El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.
- El diseño requiere revisión y firma del ingeniero responsable del proyecto.

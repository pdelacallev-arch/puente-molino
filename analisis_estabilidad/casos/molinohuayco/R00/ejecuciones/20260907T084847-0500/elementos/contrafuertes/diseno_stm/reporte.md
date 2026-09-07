# Diseño STM del armado común de CF-C1, CF-C2 y CF-C3

**Resultado global: CUMPLE**

## 1. Objetivo y datos

Se dimensiona un único detalle de armado para los tres contrafuertes. Las acciones se leen del análisis FEM 2D existente y no se recalculan.

| Parámetro | Valor | Unidad | Fuente/estado |
|---|---:|---|---|
| Altura | 7.850 | m | análisis |
| Longitud base / corona | 6.100 / 0.500 | m | análisis |
| Espesor | 0.400 | m | análisis |
| f'c | 280 (27.46) | kg/cm² (MPa) | proyecto |
| fy | 4200 (411.88) | kg/cm² (MPa) | proyecto |
| Recubrimiento | 75 | mm | adoptado |
| Vu base | 866.772 | kN | envolvente |
| Mu base | 3454.570 | kN·m | envolvente |

## 2. Modelo resistente

En cada límite inferior de zona, el momento se equilibra con la componente vertical del tirante inclinado del lomo y la compresión junto a la pantalla. La biela diagonal cierra vectorialmente el cortante del corte. Los picos FEM sólo orientan este campo resistente.

| Zona | z | Vu | Mu | T | C | error equilibrio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.000 m | 866.77 kN | 3454.57 kN·m | 718.68 kN | 737.74 kN | 0.00e+00 |
| 2 | 2.617 m | 567.61 kN | 1458.25 kN·m | 443.62 kN | 475.93 kN | 0.00e+00 |
| 3 | 5.233 m | 246.10 kN | 335.98 kN·m | 190.08 kN | 205.82 kN | 0.00e+00 |

## 3. Armado adoptado

Barras principales comunes: **1"**. Se mantienen **2 barras continuas hasta la corona**.

| Zona | Armado y capas | As requerido | As provisto | DCR tirante | DCR biela | DCR nodo | DCR corte | fs Servicio I |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4–1" en 1 capa(s) [4] | 1939 mm² | 2027 mm² | 0.957 | 0.134 | 0.213 | 0.458 | 233.6 MPa |
| 2 | 3–1" en 1 capa(s) [3] | 1197 mm² | 1520 mm² | 0.787 | 0.085 | 0.138 | 0.438 | 192.0 MPa |
| 3 | 2–1" en 1 capa(s) [2] | 513 mm² | 1013 mm² | 0.506 | 0.036 | 0.059 | 0.353 | 123.3 MPa |

Malla ortogonal en ambas caras: **1/2" @ 210 mm** en dirección horizontal y vertical.

## 4. Anclaje, interfaz y cortes

| Control | Disponible | Requerido | Solución | DCR | Estado |
|---|---:|---:|---|---:|---|
| contrafuerte–zapata | 1425 mm | 951 mm | recto | 0.667 | CUMPLE |
| corona | 350 mm | 335 mm | gancho estándar de 90° | 0.958 | CUMPLE |
| Empalme Clase B | 2000 mm | 1236 mm | máximo 50% | 0.618 | CUMPLE |
| Corte-fricción base | — | φVn=3339.7 kN | unión monolítica | 0.260 | CUMPLE |

### Zonas nodales

| Ubicación | Tipo | Demanda | φNn | DCR |
|---|---|---:|---:|---:|
| pantalla–alma / zona 1 | CCT: ancla tirante en una dirección | 737.7 kN | 3459.8 kN | 0.213 |
| pantalla–alma / zona 2 | CCT: ancla tirante en una dirección | 475.9 kN | 3459.8 kN | 0.138 |
| pantalla–alma / zona 3 | CCT: ancla tirante en una dirección | 205.8 kN | 3459.8 kN | 0.059 |
| contrafuerte–zapata | CCT: anclaje del tirante principal | 737.7 kN | 3459.8 kN | 0.213 |
| corona | CCT: anclaje del tirante principal | 205.8 kN | 3459.8 kN | 0.059 |

Las barras adicionales se cortan sólo después de prolongar una longitud de desarrollo completa más allá del punto teórico:

- 1 barra(s): corte teórico z=2.617 m; fin real z=3.398 m; DCR=0.990.
- 1 barra(s): corte teórico z=5.233 m; fin real z=6.015 m; DCR=0.990.

## 5. DCR individuales

| Contrafuerte | DCR máximo tirante | DCR máximo biela | DCR máximo corte |
|---|---:|---:|---:|
| CF-C1 | 0.957 | 0.133 | 0.457 |
| CF-C2 | 0.880 | 0.131 | 0.458 |
| CF-C3 | 0.957 | 0.133 | 0.457 |

## 6. Validaciones y límites

- Envolvente común cubre los 15 resultados: **sí**.
- Error máximo de equilibrio STM: `0.00e+00`.
- DCR máximo global: **0.990**.
- Constructibilidad dentro de 0.40 m: **conforme**.

- El catálogo principal se limita a barras comerciales de diámetro máximo 1 pulgada.
- La zapata y la pantalla no se rediseñan; deben aceptar las demandas locales reportadas.
- El ancho efectivo de bielas y nodos debe confirmarse con el detalle definitivo y secuencia de vaciado.
- El diseño requiere revisión y firma del ingeniero responsable del proyecto.

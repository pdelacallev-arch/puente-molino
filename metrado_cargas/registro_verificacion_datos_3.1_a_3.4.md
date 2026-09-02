# Registro de verificación de datos — Secciones 3.1 a 3.4

**Proyecto:** Puente Molinohuaycco  
**Archivo verificado:** `reporte_detallado_metrado_tablero.md`  
**Fecha de verificación:** 21 de julio de 2026  
**Metodología:** Verificación interactiva dato por dato con el usuario

---

## Resumen de cambios respecto al reporte original

| Ítem | Variable | Reporte original | Valor confirmado | Unidad | Tipo de cambio |
|:---|:---------|:----------------:|:----------------:|:------:|:--------------:|
| 3.1.2 | `ancho_tablero` (B) | 6.60 | **6.00** | m | 🔴 Corregido |
| 3.2.1 | `gamma_concreto` | 2.50 | **2.40** | tf/m³ | 🔴 Corregido |
| 3.2.3 | `area_viga_apoyo` | 0.05425 | **0.06075** | m² | 🔴 Corregido |
| 3.2.4 | `area_viga_centro` | 0.07505 | **0.08155** | m² | 🔴 Corregido |
| 3.2.6 | `numero_lineas_diafragma` | 11 | **9** | unid. | 🔴 Corregido |
| 3.4.1 | `velocidad_viento` | 46.05 | **75.00** | km/h | 🔴 Corregido |

Los 29 datos restantes se confirmaron sin cambios.

---

## 3.1 Geometría

| # | Variable | Símbolo | Descripción | Valor | Unidad | Estado | Observaciones |
|:-:|:---------|:--------|:------------|:-----:|:------:|:------:|:--------------|
| 1 | `L` | `L` | Luz entre apoyos | 50.00 | m | ✅ Confirmado | Sin cambios |
| 2 | `ancho_tablero` | `B` | Ancho total del tablero | **6.00** | m | ✅ Confirmado | Corregido de 6.60 m |
| 3 | `ancho_calzada` | `B_c` | Ancho de calzada cargada | 4.00 | m | ✅ Confirmado | Consistente con B=6.00 m y B_v=2.00 m |
| 4 | `ancho_veredas_total` | `B_v` | Ancho total de veredas | 2.00 | m | ✅ Confirmado | 2 veredas × 1.00 m |
| 5 | `espesor_losa` | `t_s` | Espesor de losa estructural | 0.20 | m | ✅ Confirmado | Sin cambios |
| 6 | `espesor_recrecido_vereda` | `t_v` | Recrecido considerado para veredas | 0.20 | m | ✅ Confirmado | Sin cambios |
| 7 | `numero_vigas` | `n_v` | Número de vigas principales | 3 | unid. | ✅ Confirmado | Sin cambios |

---

## 3.2 Materiales y elementos permanentes

| # | Variable | Descripción | Valor | Unidad | Estado | Observaciones |
|:-:|:---------|:------------|:-----:|:------:|:------:|:--------------|
| 8 | `gamma_concreto` | Peso específico del concreto | **2.40** | tf/m³ | ✅ Confirmado | Corregido de 2.50 tf/m³ |
| 9 | `gamma_acero` | Peso específico del acero | 7.85 | tf/m³ | ✅ Confirmado | Sin cambios |
| 10 | `area_viga_apoyo` | Área de cada viga en apoyo | **0.06075** | m² | ✅ Confirmado | Corregido de 0.05425 m² |
| 11 | `area_viga_centro` | Área de cada viga en centro de luz | **0.08155** | m² | ✅ Confirmado | Corregido de 0.07505 m² |
| 12 | `area_diafragma_in2` | Área de sección del diafragma | 33.04 (213.16 cm²) | in² | ✅ Confirmado | Sin cambios; expresado también en cm² |
| 13 | `numero_lineas_diafragma` | Líneas transversales de diafragma | **9** | unid. | ✅ Confirmado | Corregido de 11 |
| 14 | `paneles_por_linea` | Paneles entre tres vigas | 2 | unid. | ✅ Confirmado | Sin cambios |
| 15 | `longitud_panel_diafragma` | Longitud de cada panel | 2.00 | m | ✅ Confirmado | Sin cambios |
| 16 | `peso_baranda_por_lado` | Peso lineal de una baranda | 0.300 | tf/m | ✅ Confirmado | Sin cambios |
| 17 | `espesor_asfalto` | Espesor promedio de carpeta | 0.075 | m | ✅ Confirmado | Sin cambios |
| 18 | `gamma_asfalto` | Peso específico del asfalto | 2.30 | tf/m³ | ✅ Confirmado | Sin cambios |

---

## 3.3 Cargas transitorias

| # | Variable | Descripción | Valor | Unidad | Estado | Observaciones |
|:-:|:---------|:------------|:-----:|:------:|:------:|:--------------|
| 19 | `carga_peatonal` | Carga superficial peatonal | 0.370 | tf/m² | ✅ Confirmado | Sin cambios |
| 20 | `hl93_frontal` | Eje frontal del camión HL-93 | 3.6287 | tf | ✅ Confirmado | 8 kip |
| 21 | `hl93_posterior` | Cada eje posterior del camión HL-93 | 14.515 | tf | ✅ Confirmado | 32 kip c/u |
| 22 | `tandem_eje` | Cada eje del tándem de diseño | 11.340 | tf | ✅ Confirmado | 25 kip c/u |
| 23 | `carga_carril` | Carga distribuida de carril HL-93 | 0.9524 | tf/m | ✅ Confirmado | 0.64 klf |
| 24 | `separacion_rear_min` | Separación posterior del camión (pos. crítica) | 4.30 | m | ✅ Confirmado | Mínima para máxima reacción |
| 25 | `separacion_tandem` | Separación entre ejes de tándem | 1.20 | m | ✅ Confirmado | Sin cambios |
| 26 | `incremento_dinamico` | Factor IM aplicado a ejes | 1.33 | — | ✅ Confirmado | 33% |
| 27 | `presencia_multiple_1_carril` | Factor de presencia múltiple (1 carril) | 1.20 | — | ✅ Confirmado | Sin cambios |

---

## 3.4 Viento y sismo preliminar

| # | Variable | Descripción | Valor | Unidad | Estado | Observaciones |
|:-:|:---------|:------------|:-----:|:------:|:------:|:--------------|
| 28 | `velocidad_viento` | Velocidad ajustada del proyecto | **75.00** | km/h | ✅ Confirmado | Corregido de 46.05 km/h |
| 29 | `velocidad_base_viento` | Velocidad base para presión básica | 160.00 | km/h | ✅ Confirmado | Sin cambios |
| 30 | `presion_base_vigas_ksf` | Presión básica para vigas | 0.050 | ksf | ✅ Confirmado | Sin cambios |
| 31 | `altura_expuesta` | Altura lateral expuesta | 2.932 | m | ✅ Confirmado | Sin cambios |
| 32 | `viento_minimo_kN_m` | Carga lineal mínima de viento | 4.40 | kN/m | ✅ Confirmado | Sin cambios |
| 33 | `viento_vertical` | Presión vertical ascendente | 0.100 | tf/m² | ✅ Confirmado | Sin cambios |
| 34 | `viento_vehicular_klf` | Viento transversal sobre vehículos | 0.100 | klf | ✅ Confirmado | Sin cambios |
| 35 | `coeficiente_sismico` | Coeficiente sísmico equivalente | 0.240 | — | ✅ Confirmado | Sin cambios |

---

## Impacto de los cambios en resultados clave del metrado

### Peso de losa (w_losa)
$$w_{losa} = 6.00 \times 0.20 \times 2.40 = 2.880\ \text{tf/m}$$
*(Original: 6.60 × 0.20 × 2.50 = 3.300 tf/m)*

### Peso de veredas (w_ver)
$$w_{ver} = 2.00 \times 0.20 \times 2.40 = 0.960\ \text{tf/m}$$
*(Original: 2.00 × 0.20 × 2.50 = 1.000 tf/m)*

### Peso de vigas principales (w_vigas)
$$A_{prom} = \frac{0.06075 + 0.08155}{2} = 0.07115\ \text{m}^2$$
$$w_{vigas} = 3 \times 0.07115 \times 7.85 = 1.6756\ \text{tf/m}$$
*(Original: A_prom = 0.06465 m², w = 1.5225 tf/m)*

### Peso de diafragmas (w_d)
$$W_d = 0.021316 \times (9 \times 2 \times 2.00) \times 7.85 = 6.0250\ \text{tf}$$
$$w_d = 6.0250 / 50 = 0.1205\ \text{tf/m}$$
*(Original: 11 líneas, w = 0.1473 tf/m)*

### Nueva suma DC
$$w_{DC} = 2.8800 + 0.9600 + 1.6756 + 0.1205 + 0.6000 = \mathbf{6.2361\ \text{tf/m}}$$
*(Original: 6.5698 tf/m)*

### Presión de viento ajustada (con V=75 km/h)
$$P_D = 0.24412 \left(\frac{75}{160}\right)^2 = 0.05364\ \text{tf/m}^2$$
$$w_{WS,calc} = 0.05364 \times 2.932 = 0.1573\ \text{tf/m}$$
El mínimo de 0.4487 tf/m sigue controlando, pero con menor diferencia que antes.

---

## Pendientes detectadas durante la verificación

1. El número de **carriles de diseño** no fue explícitamente consultado; se asume **1 carril** por consistencia con factor de presencia múltiple 1.20.
2. Las **reacciones de superestructura** deben recalcularse con los 6 valores corregidos antes de su uso en combinaciones de diseño.
3. La **velocidad de viento de 75 km/h** es un valor redondeado significativamente mayor al original (46.05 km/h); verificar si corresponde a la velocidad ajustada del proyecto o a la velocidad básica de la zona.

---

*Fin del registro de verificación*

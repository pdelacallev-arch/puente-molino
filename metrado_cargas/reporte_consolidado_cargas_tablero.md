# Reporte consolidado de cargas del tablero

| Campo | Información |
|---|---|
| Proyecto | Creación de los Servicios de Transitabilidad mediante Puente Molinohuayco |
| CUI | 2508483 |
| Especialidad | Estructuras |
| Sistema estructural | Puente mixto acero-concreto, simplemente apoyado |
| Luz entre apoyos | 50.00 m |
| Fecha de corte de las fuentes | 21/07/2026 |
| Sistema de unidades | m, tf, tf/m y tf/m² |
| Estado | **BORRADOR — NO EMITIDO** |

## 1. Resultado ejecutivo

Se consolidan las acciones nominales de la superestructura que se transfieren a cada estribo. Con la geometría verificada de tablero de 6.00 m y las propiedades adoptadas, la reacción permanente estructural es **155.902 tf por estribo** y la reacción vertical nominal de inventario `DC + DW + PL + LL+IM` es **269.358 tf por estribo**.

Los resultados son preliminares y no constituyen combinaciones LRFD, reacciones definitivas por línea de apoyo ni verificaciones de capacidad de los estribos, apoyos o cimentaciones. Antes de emplearlos en diseño debe conciliarse, principalmente, la fuerza de frenado y el peso propio con los antecedentes del expediente.

## 2. Objeto, alcance y fuentes

El presente reporte integra el metrado de cargas del tablero, el registro de verificación de datos y el contraste con las cargas de superestructura consignadas en el Anexo 3. Su alcance es establecer una base única de acciones nominales por estribo, sus supuestos y las acciones pendientes de conciliación.

Las fuentes consolidadas son:

| ID | Fuente | Aporte al reporte |
|---|---|---|
| F-01 | Reporte detallado del metrado de cargas del tablero | Metodología, acciones nominales y límites de aplicación. |
| F-02 | Registro de verificación de datos — secciones 3.1 a 3.4 | Confirmación de 35 datos de entrada y seis correcciones incorporadas. |
| F-03 | Comparación de cargas de superestructura | Contraste con valores atribuidos al Anexo 3 / Cuadros N.° 40 y 41. |
| F-04 | Resumen tabular de resultados preliminares | Reacciones por estribo y sentido de aplicación. |

## 3. Base de cálculo consolidada

| Grupo | Parámetro adoptado | Valor | Estado |
|---|---|---:|---|
| Geometría | Luz entre apoyos | 50.00 m | Documentado |
| Geometría | Ancho total del tablero | 6.00 m | Verificado |
| Geometría | Calzada / veredas | 4.00 m / 2 x 1.00 m | Verificado |
| Geometría | Losa estructural / recrecido de veredas | 0.20 m / 0.20 m | Verificado / documentado |
| Superestructura | Vigas principales / diafragmas | 3 / 9 líneas | Verificado |
| Materiales | Peso específico del concreto / acero | 2.40 / 7.85 tf/m³ | Verificado / documentado |
| Superficie | Carpeta asfáltica | 0.075 m; 2.30 tf/m³ | Documentado |
| Transitorias | Carga peatonal | 0.370 tf/m² | Documentado |
| Transitorias | Modelo vehicular | HL-93; IM = 1.33; FPM de un carril = 1.20 | Documentado |
| Viento | Velocidad ajustada / mínimo transversal | 75.00 km/h / 4.40 kN/m | Verificado / documentado |
| Sismo | Coeficiente equivalente | 0.240 | Preliminar |

La condición de transmisión longitudinal se ha asumido como estribo izquierdo fijo y derecho móvil. Este supuesto no está confirmado y solo se usa para asignar preliminarmente la acción de frenado.

## 4. Acciones permanentes y transitorias

### 4.1 Carga permanente estructural `DC`

| Componente | Carga lineal (tf/m) | Participación |
|---|---:|---:|
| Losa de concreto | 2.880 | 46.18% |
| Recrecido de veredas | 0.960 | 15.39% |
| Tres vigas principales | 1.676 | 26.87% |
| Diafragmas | 0.120 | 1.93% |
| Dos barandas | 0.600 | 9.62% |
| **Total `DC`** | **6.236** | **100.00%** |

Para carga uniforme y apoyos simples, la reacción es `R = wL/2`; por tanto, `R_DC = 155.902 tf` por estribo.

### 4.2 Otras acciones verticales

| Acción | Carga lineal (tf/m) | Reacción por estribo (tf) | Condición de aplicación |
|---|---:|---:|---|
| `DW` — carpeta asfáltica | 0.690 | 17.250 | Vertical descendente. |
| `PL` — carga peatonal | 0.740 | 18.500 | Vertical descendente; sin incremento dinámico. |
| `LL+IM` — HL-93 | — | 77.707 | Máximo por estribo; máximos izquierdo y derecho no simultáneos. Controla el camión más carga de carril. |
| `WSv` — viento vertical | 0.600 ascendente | -15.000 | Aplicar únicamente en las combinaciones pertinentes. |

La suma descendente `DC + DW + PL + LL+IM` es **269.358 tf por estribo**. Es un control de inventario y no una combinación de diseño.

## 5. Acciones horizontales

| Dirección | Acción | Estribo izquierdo (tf) | Estribo derecho (tf) | Estado y observación |
|---|---|---:|---:|---|
| Longitudinal | `BR` — frenado | 9.798 | 0.000 | Preliminar; total asignado al apoyo fijo asumido. |
| Transversal | `WS` — viento sobre estructura | 11.217 | 11.217 | Controla la carga lineal mínima de 4.40 kN/m. |
| Transversal | `WL` — viento sobre vehículos | 3.720 | 3.720 | Acción interrumpible; no combinar con `WSv`. |
| Horizontal | `EQ` — sismo equivalente | 41.556 | 41.556 | Estimación estática con `C = 0.24` sobre `DC + DW`. |

## 6. Contraste con los antecedentes de subestructura

| Acción | Metrado consolidado (tf) | Anexo 3 (tf) | Diferencia | Estado de conciliación |
|---|---:|---:|---:|---|
| `DC` | 155.902 | 146.58* | +9.32 tf (+6.4%) | Pendiente de identificar componentes incluidos y excluidos. |
| `DW` | 17.250 | 17.28* | -0.03 tf (-0.2%) | Consistente. |
| `PL` | 18.500 | 18.00* | +0.50 tf (+2.7%) | Diferencia menor por intensidad adoptada. |
| `LL+IM` | 77.707 | 80.19 | -2.48 tf (-3.1%) | Pendiente de revisar posición crítica y factores aplicados. |
| `BR` | 9.798 | 20.05 | -10.25 tf (-51.1%) | **Crítico: requiere conciliación previa al diseño.** |

\* Valores de `DC`, `DW` y `PL` deducidos en el contraste a partir de cargas por metro de ancho; no se han verificado directamente contra el Anexo 3 original.

Como antecedente adicional, el reporte detallado registra `R_DC = 163.86 tf` en el Anexo 3 y una reacción equivalente de 170.321 tf por estribo en el modelo global. Estas referencias no son directamente consistentes con el desglose comparativo de `DC = 146.58 tf`; por ello, no deben adoptarse hasta revisar el detalle original de componentes, convenciones y combinaciones.

## 7. Limitaciones de uso

Este reporte no incluye factores ni combinaciones LRFD, distribución transversal de carga viva, reacciones por viga, rigidez real de apoyos, esviaje, curvatura, etapas constructivas, cargas accesorias no definidas, temperatura, retracción, fluencia ni análisis espectral.

En consecuencia, no permite afirmar capacidad, estabilidad, cumplimiento normativo ni conformidad de apoyos, estribos, cajuelas o cimentaciones. La acción sísmica presentada es solo una comprobación estática de orden de magnitud.

## 8. Acciones requeridas para cierre

| ID | Acción | Responsable técnico propuesto | Evidencia de cierre |
|---|---|---|---|
| AC-01 | Confirmar en planos aprobados el ancho, veredas, separación de vigas y áreas por tramo de las vigas. | Especialista de estructuras | Planos y memoria con revisión vigente. |
| AC-02 | Extraer del modelo y del Anexo 3 el desglose de peso propio, cargas de superestructura y reacciones. | Modelador / especialista de estructuras | Cuadro de conciliación firmado o revisado. |
| AC-03 | Definir carriles de diseño, factor de presencia múltiple, posición crítica y criterio de frenado. | Proyectista o especialista competente | Criterio documentado y metrado actualizado. |
| AC-04 | Confirmar apoyo fijo, apoyo móvil, guías y rigidez de neoprenos; redistribuir `BR` conforme al sistema real. | Especialista de estructuras | Plano de apoyos y modelo de transferencia longitudinal. |
| AC-05 | Sustituir o contrastar `EQ` con reacciones del análisis espectral aprobado. | Especialista de estructuras | Extracto de reacciones espectrales y combinaciones. |
| AC-06 | Elaborar combinaciones de carga aplicables y verificar demanda/capacidad de subestructura. | Especialista de estructuras | Memoria de cálculo y modelo verificados. |

## 9. Conclusiones

1. La base consolidada adopta un tablero de 6.00 m y produce una carga permanente estructural de **6.236 tf/m**, equivalente a **155.902 tf por estribo**.
2. Las acciones nominales por estribo son `DW = 17.250 tf`, `PL = 18.500 tf`, `LL+IM = 77.707 tf`, `WS = 11.217 tf`, `WL = 3.720 tf`, `WSv = -15.000 tf` y `EQ = 41.556 tf`.
3. La fuerza de frenado preliminar es **9.798 tf** y está condicionada a un carril y a la asignación asumida de apoyo fijo izquierdo. No es compatible aún con el valor de **20.05 tf** atribuido al Anexo 3.
4. Las diferencias de `DC`, `LL+IM` y, principalmente, `BR` deben resolverse antes de usar estas acciones en el diseño definitivo de subestructura.
5. El reporte queda como **BORRADOR — NO EMITIDO** hasta completar la conciliación documental y las verificaciones de ingeniería indicadas.

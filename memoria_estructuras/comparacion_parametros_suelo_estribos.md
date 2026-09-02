# Comparación de parámetros de suelo para el diseño de los estribos

**Proyecto:** Puente carrozable Molinohuaycco  
**Objeto:** contrastar los parámetros geotécnicos del estudio de suelos anterior con los valores empleados en las memorias de cálculo de los estribos.  
**Fecha de revisión:** 9 de agosto de 2026

## Fuentes revisadas

- [Resultados del estudio de suelos anterior](../estudio_suelos/resultados_suelos_anterior.md), transcripción del Informe N.° 342-2022-LABINGEOMAX / IGM-PV-015-2022, septiembre de 2022.
- [Anexo 3 - Estribo izquierdo](Anexo_3_Estribo_Izquierdo.pdf), noviembre de 2022, 14 páginas.
- [Anexo 4 - Estribo derecho](Anexo_4_Estribo_derecho.pdf), noviembre de 2022, 14 páginas.

> **Criterio de comparación:** los parámetros de cimentación y los del relleno del trasdós se presentan por separado porque representan materiales y mecanismos distintos. Los valores del estudio se conservan tal como fueron transcritos; las conversiones solo se incluyen para facilitar la comparación.

## Tabla comparativa principal

| Aplicación | Parámetro | Estudio de suelos - estribo izquierdo | Memoria - estribo izquierdo | Estudio de suelos - estribo derecho | Memoria - estribo derecho | Evaluación |
|---|---|---:|---:|---:|---:|---|
| Cimentación | Condición de apoyo | Zapata superficial sobre mejoramiento por reemplazo de material | Se declara «estribo apoyado sobre roca» | Zapata superficial sobre mejoramiento por reemplazo de material | Se declara «estribo apoyado sobre roca» | **Incompatible.** La memoria no representa el sistema de apoyo definido por el estudio geotécnico. |
| Cimentación | Planta de la zapata | 11.95 × 6.60 m | 11.95 × 6.60 m | 11.95 × 6.60 m | 11.95 × 6.60 m | Coincide. El estudio denomina `B = 11.95 m` y `L = 6.60 m`. |
| Cimentación | Cota de cimentación | 2356.40 msnm | No indicada | 2356.40 msnm | No indicada | No verificable en las memorias. |
| Cimentación | Profundidad bajo la socavación, `Df` | 3.10 m | La figura muestra `L = 3.10 m`; no lo identifica expresamente como `Df` | 5.60 m | La figura muestra `L = 3.10 m`; no lo identifica expresamente como `Df` | **Revisar el estribo derecho:** la memoria repite 3.10 m, mientras el estudio exige 5.60 m desde la cota de socavación. |
| Cimentación | Peso unitario, `γ` | 1985 kg/m³ = 1.985 t/m³ ≈ 19.47 kN/m³ | No indicado para el material de apoyo | 1985 kg/m³ = 1.985 t/m³ ≈ 19.47 kN/m³ | No indicado para el material de apoyo | Falta trazabilidad en ambas memorias. |
| Cimentación | Ángulo de fricción, `φ` | 36.8° | 19.0° («Ø Base») | 36.8° | 18.0° («Ø Base») | **No coincide:** diferencias de -17.8° y -18.8°, respectivamente. |
| Cimentación | Cohesión, `c` | 0.00 kg/cm² | 0.70 kg/cm² ≈ 68.65 kPa | 0.00 kg/cm² | 0.65 kg/cm² ≈ 63.75 kPa | **No coincide.** La memoria introduce una contribución cohesiva que el estudio no reconoce para la cimentación mejorada. |
| Cimentación | Resistencia nominal | 16.30 kg/cm² | No indicada | 40.70 kg/cm² | No indicada | Las memorias no distinguen resistencia nominal y resistencia de servicio. |
| Cimentación | Capacidad en ELR (`φb = 0.45`) | 7.33 kg/cm² | No indicada | 18.31 kg/cm² | No indicada | No comparada explícitamente en las memorias. |
| Cimentación | Capacidad en ELS, limitada por asentamiento | 2.21 kg/cm² | 2.44 kg/cm² | 2.21 kg/cm² | 2.02 kg/cm² | **No coincide:** la memoria izquierda usa +0.23 kg/cm² (+10.4 %) y la derecha -0.19 kg/cm² (-8.6 %) respecto del estudio. |
| Cimentación | Asentamiento límite | 2.54 cm = 25.4 mm | No indicado | 2.54 cm = 25.4 mm | No indicado | La condición que gobierna los 2.21 kg/cm² no se documenta en las memorias. |
| Deslizamiento | Fricción en la interfaz de cimentación | `tan δ = 0.55` | Nota «C = 0.7 concreto sobre roca»; la simbología se mezcla con la cohesión | `tan δ = 0.55` | Nota «C = 0.7 concreto sobre roca»; la simbología se mezcla con la cohesión | **Inconsistente y dimensionalmente ambigua.** Si `0.70` es coeficiente de fricción, supera en 27.3 % al valor geotécnico. Debe reconstruirse la verificación con `tan δ = 0.55` y sin cohesión, salvo sustento específico. |
| Relleno del trasdós | Material de referencia | Material de préstamo | Relleno genérico | Material de préstamo | Relleno genérico | La memoria no identifica cantera, clasificación ni condición de compactación. |
| Relleno del trasdós | Peso unitario húmedo, `γ` | 21.20 kN/m³ ≈ 2.16 t/m³ | 1.80 t/m³ ≈ 17.65 kN/m³ | 21.20 kN/m³ ≈ 2.16 t/m³ | 1.80 t/m³ ≈ 17.65 kN/m³ | **No coincide:** la memoria usa un peso unitario aproximadamente 16.7 % menor. |
| Relleno del trasdós | Ángulo de fricción, `φ` | 34.8° | 30.0° | 34.8° | 30.0° | **No coincide:** la memoria reduce el ángulo en 4.8°. |
| Relleno del trasdós | Cohesión, `c` | 0.00 kN/m² | No indicada para el relleno | 0.00 kN/m² | No indicada para el relleno | Conviene declarar expresamente `c = 0` en el cálculo de empujes. |
| Empuje de tierras | Coeficiente activo estático, `Ka` | 0.27 | 0.333 | 0.27 | 0.333 | **No coincide:** la memoria usa un valor 23.3 % mayor, derivado de `φ = 30°`. |
| Empuje de tierras | Coeficiente pasivo estático, `Kp` | 3.66 | 3.00 | 3.66 | 3.00 | **No coincide:** la memoria usa un valor 18.0 % menor. Debe verificarse además si corresponde movilizar empuje pasivo y con qué reducción. |
| Empuje de tierras | Reducción del pasivo, `R` | 0.48 | No indicada | 0.48 | No indicada | La memoria suma `Ep` a la resistencia al deslizamiento sin documentar la reducción prescrita por el estudio. |
| Sismo / sitio | Clase de sitio | C | No indicada | C | No indicada | Falta trazabilidad del efecto de sitio. |
| Sismo / sitio | PGA | 0.360 g | No indicada; se adopta una fuerza horizontal de 20 % del peso propio de la superestructura | 0.360 g | No indicada; se adopta una fuerza horizontal de 20 % del peso propio de la superestructura | El criterio sísmico de la memoria no se vincula con los parámetros geotécnicos reportados. |
| Mejoramiento | Espesor de reemplazo | 3.50 m | No incorporado en los datos de diseño | 3.50 m | No incorporado en los datos de diseño | **Omisión importante.** Afecta la condición de apoyo, el control de obra y la interpretación de los parámetros resistentes. |
| Mejoramiento | Compactación | ≥ 95 % de la MDS del Próctor Modificado, en capas de 0.30 m | No indicada | ≥ 95 % de la MDS del Próctor Modificado, en capas de 0.30 m | No indicada | Debe incorporarse como requisito de diseño y construcción. |
| Mejoramiento | Control geotécnico | Ensayo de placa de carga recomendado | No indicado | Ensayo de placa de carga recomendado | No indicado | Debe establecerse como verificación de campo antes de aceptar la cimentación. |

## Comprobación de presiones consignadas en las memorias

La presión máxima crítica reportada en ambas memorias es `qmax = 2.01 kg/cm²`, correspondiente al caso con puente, relleno sobrecargado y sismo.

| Estribo | `qmax` de la memoria | Límite usado por la memoria | `qmax / qadm` de la memoria | ELS del estudio | `qmax / qELS` del estudio | Lectura |
|---|---:|---:|---:|---:|---:|---|
| Izquierdo | 2.01 kg/cm² | 2.44 kg/cm² | 0.824 | 2.21 kg/cm² | 0.910 | Cumple con ambos límites, pero la memoria acredita una holgura mayor al usar una capacidad no coincidente con el estudio. |
| Derecho | 2.01 kg/cm² | 2.02 kg/cm² | 0.995 | 2.21 kg/cm² | 0.910 | Cumple por margen mínimo con el límite de la memoria y con mayor margen frente al ELS del estudio. |

> Esta comprobación solo contrasta los números reportados. No valida la distribución de presiones ni sustituye el recálculo de estabilidad con los parámetros geotécnicos correctos.

## Hallazgos y criterio recomendado

1. **Crítico - condición de apoyo:** el estudio prescribe una zapata sobre 3.50 m de suelo mejorado, mientras las memorias justifican el deslizamiento como si el estribo estuviera apoyado sobre roca. Se debe definir una única condición física y recalcular con ella.
2. **Crítico - resistencia al deslizamiento:** las memorias mezclan el símbolo `C` para cohesión y para una aparente fricción «concreto sobre roca». Debe emplearse una formulación dimensionalmente consistente y trazable. Con el estudio disponible, corresponde revisar el cálculo con suelo granular, `c = 0` y `tan δ = 0.55`, además de aplicar la reducción del pasivo `R = 0.48` cuando este pueda movilizarse.
3. **Importante - empujes:** para el material de préstamo, el estudio reporta `γ = 21.20 kN/m³`, `φ = 34.8°` y `Ka = 0.27`; las memorias usan `γ ≈ 17.65 kN/m³`, `φ = 30°` y `Ka = 0.333`. Aunque algunos efectos pueden compensarse parcialmente, la combinación no es trazable al estudio y debe actualizarse de manera conjunta.
4. **Importante - cimentación derecha:** el estudio obtiene `Df = 5.60 m` bajo la cota de socavación, pero el anexo derecho repite una figura con `L = 3.10 m`. Se deben conciliar cotas, socavación, espesor del mejoramiento y geometría efectiva.
5. **Importante - capacidad portante:** debe adoptarse y citarse el límite de servicio de `2.21 kg/cm²` para ambos estribos, gobernado por un asentamiento máximo de 25.4 mm. También debe conservarse la distinción frente a las capacidades en ELR de 7.33 y 18.31 kg/cm².
6. **Recomendación:** actualizar ambas memorias con una tabla única de parámetros geotécnicos, fuente y estado límite; luego repetir empujes, volteo, deslizamiento, excentricidad, presiones de contacto y asentamiento.

## Notas de conversión y alcance

- Se usó `1 t/m³ = 9.80665 kN/m³`.
- Se usó `1 kg/cm² = 98.0665 kPa`.
- Los valores `Ka`, `Kp`, `R` y `tan δ` del estudio corresponden a su cuadro general de parámetros para empujes. Antes del recálculo definitivo debe confirmarse que su geometría, condición de drenaje y estado de movilización sean aplicables a cada estribo.
- Esta revisión es documental. No reemplaza el pronunciamiento del especialista geotécnico ni la aprobación del ingeniero responsable del diseño.

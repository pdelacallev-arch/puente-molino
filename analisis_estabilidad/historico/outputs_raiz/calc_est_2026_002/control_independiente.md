# Control independiente de resultados — CALC-EST-2026-002-R00

## 1. Compatibilidad y alcance

- Se verificó `H = hp + hz = 13.15 + 1.50 = 14.65 m`.
- Se verificó `B = B2 + tp2 + B1 = 5.10 + 0.75 + 6.10 = 11.95 m`.
- El dentellón `0.70 × 1.50 m` tiene peralte efectivo positivo y su profundidad es menor que los `3.74 m` de falsa zapata modelada.
- La comprobación dimensional no confirma que exista un medio granular frente al dentellón ni acredita su anclaje en el concreto existente.

## 2. Equilibrio y presiones

- Las sumas de fuerzas y momentos de los cuatro casos coinciden con los detalles del agente al nivel de redondeo reportado.
- En la interfaz 1 se reprodujeron la posición de la resultante y las presiones mediante `q = V/B(1 ± 6e/B)`.
- El validador interno marca una diferencia de `0.198 tf·m/m` en el componente `Ea` de Resistencia I-a e I-b debido a que el brazo se almacena redondeado a `4.88 m`; el momento total, la resultante y las presiones sí cierran. Se clasifica como efecto de redondeo de presentación.
- En la interfaz 2 se reprodujo `q = V/(B-2e)` para los cuatro casos. El validador lineal interno no es aplicable porque esta interfaz usa área efectiva de Meyerhof y no entrega `q_talón/q_punta`.

## 3. Dentellón

La integración independiente de la ley pasiva entre profundidades `z = 1.50 m` y `z = 3.00 m`, con `Kp = 4.5572` y `γ = 1.80 tf/m³`, reproduce:

- `E_p = 27.685 tf/m`.
- Para Resistencia I: `V_u = 1.50 E_p = 41.528 tf/m`.
- `M_u = 34.607 tf·m/m` respecto de la raíz.

Con el armado automático se verificó:

| Estado | D/C | Resultado |
|---|---:|---|
| Flexión | 0.996 | Cumple con margen mínimo |
| Corte unidireccional | 0.872 | Cumple |
| Corte-fricción, junta postinstalada no rugosa | 1.054 | No cumple |

La demanda de corte-fricción requiere `A_vf = 19.387 cm²/m`, frente a `18.393 cm²/m` provistos por el armado automático.

Como sensibilidad sin modificar algoritmos se evaluó Ø3/4" @ 180 mm en la cara del pasivo y Ø3/4" @ 400 mm en la opuesta. Proporciona `A_vf = 22.961 cm²/m`, `D/C_flexión = 0.961`, `D/C_corte = 0.874` y `D/C_corte-fricción = 0.844`. Esta alternativa sigue pendiente de un sistema de anclaje postinstalado aprobado y de definir el medio real de contacto.

## 4. Conclusión del control

Los resultados de estabilidad y zapata son coherentes con las ecuaciones implementadas. El dentellón solicitado no puede declararse conforme con el armado automático ni con la conexión no acreditada. La alternativa reforzada satisface teóricamente E.060, pero no cierra la compatibilidad física o constructiva.

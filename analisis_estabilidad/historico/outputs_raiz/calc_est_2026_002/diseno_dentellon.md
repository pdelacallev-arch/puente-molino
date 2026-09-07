# Diseño del dentellón rectangular — NTE E.060

**Estado general:** CUMPLE

**Estado estructural E.060:** CUMPLE

## Datos y modelo

| Parámetro | Valor |
|---|---:|
| Interfaz del agente | interface_1 |
| Espesor horizontal | 0.700 m |
| Profundidad vertical | 1.500 m |
| Longitud | 6.000 m |
| Idealización | losa vertical en voladizo; franja de 1 m |
| Peralte efectivo de flexión | 0.6171 m |
| Kp Rankine | 4.5572 |
| γ medio (cara pasiva) | 1.960 Tn/m³ |
| Empuje pasivo nominal | 30.146 tf/m |

## Demanda y estabilidad

| Caso | Fh | QR sin dentellón | Déficit | Vu dentellón | Mu | QR con dentellón | Cumple |
|---|---:|---:|---:|---:|---:|---:|:---:|
| Servicio I | 43.720 | 149.420 | 0.000 | 30.146 | 25.122 | 179.566 | Sí |
| Resistencia I-a | 66.800 | 130.530 | 0.000 | 45.219 | 37.683 | 145.603 | Sí |
| Resistencia I-b | 66.800 | 171.820 | 0.000 | 45.219 | 37.683 | 186.893 | Sí |
| Evento Extremo I (Sismo) | 71.320 | 130.620 | 0.000 | 30.146 | 25.122 | 160.766 | Sí |

## Diseño E.060

Caso gobernante: **Resistencia I-a**.

| Verificación | Demanda | Capacidad / provisión | D/C o resultado |
|---|---:|---:|---:|
| Flexión | Mu = 37.683 tf·m/m | φMn = 40.891 tf·m/m | 0.922 |
| Corte | Vu = 45.219 tf/m | φVc = 47.645 tf/m | 0.949 |
| Corte-fricción | Vu = 45.219 tf/m | φVn = 155.888 tf/m | 0.290 |
| Desarrollo en zapata monolítica | ld principal = 480 mm | disponible = 1425 mm | CUMPLE |

### Cuantías mínimas por armado

- Mínimo de losa: `12.600 cm²/m`.
- Mínimo de flexión: `8.400 cm²/m`.
- Acero de distribución: `6.300 cm²/m`.
- Mínimo adoptado completo, sin repartir entre caras: `12.600 cm²/m`.

## Armado propuesto

- Principal vertical, cara del pasivo: Ø5/8" @ 110 mm (selección automática; cumple).
- Vertical, cara opuesta: Ø5/8" @ 150 mm (barra asumida; espaciamiento calculado; cumple).
- Distribución horizontal en cada cara: Ø5/8" @ 150 mm (barra asumida; espaciamiento calculado; cumple).
- Las barras verticales que cruzan y se desarrollan en la junta funcionan también como acero de corte-fricción.

## Pendientes para cerrar el diseño

- Ninguna.

## Alcance y advertencias

- Los factores del pasivo (φ_ep y γ_ep) son externos a E.060; su fuente contractual es AASHTO LRFD 2005 (edición contractual del proyecto, complementada por el Manual de Puentes MTC 2018), conforme al agente de subestructura, y han sido confirmados para este diseño.
- La ley pasiva se prolonga desde la coronación de la zapata hasta la base adoptada (3.000 m); las cotas del dentellón fueron verificadas en el proyecto.
- El medio pasivo adoptado es el suelo de fundación GW (γ = 1.96 Tn/m³, φ' = 39.8°), según el Estudio de Suelos Informe N.° 001-2026/ING-CON-26-E-008/INGEOTECON-135-26; la ley pasiva del agente sobre la altura de la zapata usa γ = 1.80 Tn/m³ (relleno), por lo que la ley global presenta una discontinuidad en la coronación del dentellón que no afecta la estabilidad (QR no depende de Ep) ni la demanda del dentellón, calculada con su propia ley.
- El modelo de Rankine solo es válido con suelo granular drenado frente al dentellón; no aplica a una llave embebida en concreto.
- El dentellón y la zapata se consideran vaciados monolíticamente; las barras deben desarrollar fy dentro de la zapata.
- La cuantía mínima de losa se aplica completa a cada armado controlado y no se reparte entre caras.
- La cara en contacto con el pasivo es la cara traccionada para el sentido de carga adoptado.

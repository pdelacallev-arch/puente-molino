# Diseño del dentellón rectangular — NTE E.060

**Estado general:** CUMPLE

**Estado estructural E.060:** CUMPLE

## Datos y modelo

| Parámetro | Valor |
|---|---:|
| Interfaz del agente | interface_1 |
| Espesor horizontal | 0.700 m |
| Profundidad vertical | 1.300 m |
| Longitud | 6.000 m |
| Idealización | losa vertical en voladizo; franja de 1 m |
| Peralte efectivo de flexión | 0.6171 m |
| Kp Rankine | 4.5572 |
| γ medio (cara pasiva) | 1.960 Tn/m³ |
| Empuje pasivo nominal | 24.966 tf/m |

## Demanda y estabilidad

| Caso | Fh | QR sin dentellón | Déficit | Vu dentellón | Mu | QR con dentellón | Cumple |
|---|---:|---:|---:|---:|---:|---:|:---:|
| Servicio I | 43.720 | 150.940 | 0.000 | 24.966 | 17.863 | 175.906 | Sí |
| Resistencia I-a | 66.800 | 131.687 | 0.000 | 24.966 | 17.863 | 144.170 | Sí |
| Resistencia I-b | 66.800 | 173.425 | 0.000 | 24.966 | 17.863 | 185.908 | Sí |
| Evento Extremo I (Sismo) | 71.930 | 131.982 | 0.000 | 24.966 | 17.863 | 156.948 | Sí |

## Diseño E.060

Caso estructural representativo gobernante: **Evento Extremo I (Sismo)**.
Casos con la demanda estructural máxima: **Resistencia I-a, Resistencia I-b, Evento Extremo I (Sismo)**.
Servicio I se emplea únicamente para la verificación de estabilidad; no participa en la selección del caso de diseño resistente E.060.

| Verificación | Demanda | Capacidad / provisión | D/C o resultado |
|---|---:|---:|---:|
| Flexión | Mu = 17.863 tf·m/m | φMn = 30.199 tf·m/m | 0.592 |
| Corte | Vu = 24.966 tf/m | φVc = 47.645 tf/m | 0.524 |
| Corte-fricción | Vu = 24.966 tf/m | φVn = 131.907 tf/m | 0.189 |
| Desarrollo en zapata monolítica | ld principal = 480 mm | disponible = 1425 mm | CUMPLE |

### Cuantías mínimas por armado

- Mínimo de losa: `12.600 cm²/m`.
- Mínimo de flexión: `8.400 cm²/m`.
- Acero de distribución: `6.300 cm²/m`.
- Mínimo adoptado completo, sin repartir entre caras: `12.600 cm²/m`.

## Armado propuesto y verificación de áreas

`As normativo gobernante` es el mayor entre el mínimo de losa, el mínimo de flexión y el acero de distribución. La columna `Control normativo` identifica cuál de ellos gobierna.

La relación D/C de acero es `As requerido / As dispuesto`; `As requerido = máx(As calculado, As normativo gobernante)`.

| Armado | As calculado | As normativo gobernante | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal vertical — cara del pasivo | 7.744 cm²/m | 12.600 cm²/m | mínimo de losa | 12.600 cm²/m | Ø5/8" @ 150 mm | 13.196 cm²/m | 0.955 | Sí |
| Vertical — cara opuesta | 0.000 cm²/m | 12.600 cm²/m | mínimo de losa | 12.600 cm²/m | Ø5/8" @ 150 mm | 13.196 cm²/m | 0.955 | Sí |
| Distribución horizontal — cada cara | 0.000 cm²/m | 12.600 cm²/m | mínimo de losa | 12.600 cm²/m | Ø5/8" @ 150 mm | 13.196 cm²/m | 0.955 | Sí |

- Las barras verticales que cruzan y se desarrollan en la junta funcionan también como acero de corte-fricción.

## Pendientes para cerrar el diseño

- Ninguna.

## Alcance y advertencias

- El Manual de Puentes MTC 2018, art. 2.8.1.1.12.6 y Tabla 2.8.1.1.12.6-1, respalda φp = 0.50 para la componente pasiva en Estado Límite de Resistencia; para Evento Extremo I se adopta φp = 1.00 conforme a la regla general del MTC y AASHTO LRFD. No se usa un factor 1.50 para mayorar el empuje en el diseño estructural.
- La ley pasiva se prolonga desde la coronación de la zapata hasta la base adoptada (2.800 m); las cotas del dentellón fueron verificadas en el proyecto.
- El medio pasivo adoptado es el suelo de fundación GW (γ = 1.96 Tn/m³, φ' = 39.8°), según el Estudio de Suelos Informe N.° 001-2026/ING-CON-26-E-008/INGEOTECON-135-26; tanto el agente de subestructura como este diseño usan el peso específico del suelo de fundación para el pasivo.
- El modelo de Rankine solo es válido con suelo granular drenado frente al dentellón; no aplica a una llave embebida en concreto.
- El dentellón y la zapata se consideran vaciados monolíticamente; las barras deben desarrollar fy dentro de la zapata.
- La cuantía mínima de losa se aplica completa a cada armado controlado y no se reparte entre caras.
- La cara en contacto con el pasivo es la cara traccionada para el sentido de carga adoptado.

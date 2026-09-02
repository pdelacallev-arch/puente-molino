# Diseño del dentellón rectangular — NTE E.060

**Estado general:** CUMPLE

**Estado estructural E.060:** CUMPLE

## Datos y modelo

| Parámetro | Valor |
|---|---:|
| Interfaz del agente | interface_1 |
| Espesor horizontal | 2.000 m |
| Profundidad vertical | 1.000 m |
| Longitud | 6.000 m |
| Idealización | losa vertical en voladizo; franja de 1 m |
| Peralte efectivo de flexión | 1.9155 m |
| Kp Rankine | 4.5572 |
| γ medio (cara pasiva) | 1.960 Tn/m³ |
| Empuje pasivo nominal | 17.864 tf/m |

## Demanda y estabilidad

| Caso | Fh | QR sin dentellón | Déficit | Vu dentellón | Mu | QR con dentellón | Cumple |
|---|---:|---:|---:|---:|---:|---:|:---:|
| Servicio I | 43.720 | 150.940 | 0.000 | 17.864 | 9.677 | 168.804 | Sí |
| Resistencia I-a | 66.800 | 131.687 | 0.000 | 17.864 | 9.677 | 140.619 | Sí |
| Resistencia I-b | 66.800 | 173.425 | 0.000 | 17.864 | 9.677 | 182.358 | Sí |
| Evento Extremo I (Sismo) | 71.930 | 131.982 | 0.000 | 17.864 | 9.677 | 149.846 | Sí |

## Diseño E.060

Caso estructural representativo gobernante: **Evento Extremo I (Sismo)**.
Casos con la demanda estructural máxima: **Resistencia I-a, Resistencia I-b, Evento Extremo I (Sismo)**.
Servicio I se emplea únicamente para la verificación de estabilidad; no participa en la selección del caso de diseño resistente E.060.

| Verificación | Demanda | Capacidad / provisión | D/C o resultado |
|---|---:|---:|---:|
| Flexión | Mu = 9.677 tf·m/m | φMn = 185.369 tf·m/m | 0.052 |
| Corte | Vu = 17.864 tf/m | φVc = 147.898 tf/m | 0.121 |
| Corte-fricción | Vu = 17.864 tf/m | φVn = 191.438 tf/m | 0.093 |
| Desarrollo en zapata monolítica | ld principal = 576 mm | disponible = 1425 mm | CUMPLE |

### Cuantía mínima y distribución entre caras

- Número de caras adoptado: `2`.
- Mínimo total de losa, ρ = 0.0018: `36.000 cm²/m`.
- Referencia mínima de la cara traccionada, ρ = 0.0012: `24.000 cm²/m`.
- Referencia de distribución por cara al dividir entre dos, ρ = 0.0009: `18.000 cm²/m`.

## Armado propuesto y verificación de áreas

`As normativo asignado` es la porción del mínimo total que corresponde a cada armado según el número de caras elegido. La columna `Control normativo` identifica el criterio de asignación.

La relación D/C de acero es `As requerido / As dispuesto`; `As requerido = máx(As calculado, As normativo asignado)`.

| Armado | As calculado | As normativo asignado | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal vertical — cara del pasivo | 1.337 cm²/m | 24.000 cm²/m | mínimo de flexión en cara traccionada | 24.000 cm²/m | Ø3/4" @ 110 mm | 25.911 cm²/m | 0.926 | Sí |
| Vertical — cara opuesta | 0.000 cm²/m | 12.000 cm²/m | saldo del mínimo total de losa | 12.000 cm²/m | Ø3/4" @ 230 mm | 12.392 cm²/m | 0.968 | Sí |
| Distribución horizontal — cada cara | 0.000 cm²/m | 18.000 cm²/m | mitad del mínimo total de losa | 18.000 cm²/m | Ø3/4" @ 150 mm | 19.002 cm²/m | 0.947 | Sí |

- Las barras verticales que cruzan y se desarrollan en la junta funcionan también como acero de corte-fricción.

## Pendientes para cerrar el diseño

- Ninguna.

## Alcance y advertencias

- El Manual de Puentes MTC 2018, art. 2.8.1.1.12.6 y Tabla 2.8.1.1.12.6-1, respalda φp = 0.50 para la componente pasiva en Estado Límite de Resistencia; para Evento Extremo I se adopta φp = 1.00 conforme a la regla general del MTC y AASHTO LRFD. No se usa un factor 1.50 para mayorar el empuje en el diseño estructural.
- La ley pasiva se prolonga desde la coronación de la zapata hasta la base adoptada (2.500 m); las cotas del dentellón fueron verificadas en el proyecto.
- El medio pasivo adoptado es el suelo de fundación GW (γ = 1.96 Tn/m³, φ' = 39.8°), según el Estudio de Suelos Informe N.° 001-2026/ING-CON-26-E-008/INGEOTECON-135-26; tanto el agente de subestructura como este diseño usan el peso específico del suelo de fundación para el pasivo.
- El modelo de Rankine solo es válido con suelo granular drenado frente al dentellón; no aplica a una llave embebida en concreto.
- El dentellón y la zapata se consideran vaciados monolíticamente; las barras deben desarrollar fy dentro de la zapata.
- La cuantía mínima total de losa se reparte entre dos caras; la cara traccionada conserva rho = 0.0012 y la opuesta recibe el saldo. El acero horizontal se divide por mitades.
- La cara en contacto con el pasivo es la cara traccionada para el sentido de carga adoptado.

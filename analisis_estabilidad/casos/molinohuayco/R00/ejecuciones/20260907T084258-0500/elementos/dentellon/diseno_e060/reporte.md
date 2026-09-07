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
| Servicio I | 32.160 | 134.500 | 0.000 | 24.966 | 17.863 | 159.466 | Sí |
| Resistencia I-a | 49.330 | 117.907 | 0.000 | 24.966 | 17.863 | 130.390 | Sí |
| Resistencia I-b | 49.330 | 154.744 | 0.000 | 24.966 | 17.863 | 167.227 | Sí |
| Evento Extremo I (Sismo) | 56.800 | 115.716 | 0.000 | 24.966 | 17.863 | 140.682 | Sí |

## Diseño E.060

Caso estructural representativo gobernante: **Evento Extremo I (Sismo)**.
Casos con la demanda estructural máxima: **Resistencia I-a, Resistencia I-b, Evento Extremo I (Sismo)**.
Servicio I se emplea únicamente para la verificación de estabilidad; no participa en la selección del caso de diseño resistente E.060.

| Verificación | Demanda | Capacidad / provisión | D/C o resultado |
|---|---:|---:|---:|
| Flexión | Mu = 17.863 tf·m/m | φMn = 19.826 tf·m/m | 0.901 |
| Corte | Vu = 24.966 tf/m | φVc = 47.645 tf/m | 0.524 |
| Corte-fricción | Vu = 24.966 tf/m | φVn = 67.743 tf/m | 0.369 |
| Desarrollo en zapata monolítica | ld principal = 480 mm | disponible = 1425 mm | CUMPLE |

### Cuantía mínima y distribución entre caras

- Número de caras adoptado: `2`.
- Mínimo total de losa, ρ = 0.0018: `12.600 cm²/m`.
- Referencia mínima de la cara traccionada, ρ = 0.0012: `8.400 cm²/m`.
- Referencia de distribución por cara al dividir entre dos, ρ = 0.0009: `6.300 cm²/m`.

## Armado propuesto y verificación de áreas

`As normativo asignado` es la porción del mínimo total que corresponde a cada armado según el número de caras elegido. La columna `Control normativo` identifica el criterio de asignación.

La relación D/C de acero es `As requerido / As dispuesto`; `As requerido = máx(As calculado, As normativo asignado)`.

| Armado | As calculado | As normativo asignado | Control normativo | As requerido | Refuerzo dispuesto | As dispuesto | D/C acero | Cumple |
|---|---:|---:|---|---:|---|---:|---:|:---:|
| Principal vertical — cara del pasivo | 7.744 cm²/m | 8.400 cm²/m | mínimo de flexión en cara traccionada | 8.400 cm²/m | Ø5/8" @ 230 mm | 8.606 cm²/m | 0.976 | Sí |
| Vertical — cara opuesta | 0.000 cm²/m | 4.200 cm²/m | saldo del mínimo total de losa | 4.200 cm²/m | Ø5/8" @ 400 mm | 4.948 cm²/m | 0.849 | Sí |
| Distribución horizontal — cada cara | 0.000 cm²/m | 6.300 cm²/m | mitad del mínimo total de losa | 6.300 cm²/m | Ø5/8" @ 310 mm | 6.385 cm²/m | 0.987 | Sí |

- Las barras verticales que cruzan y se desarrollan en la junta funcionan también como acero de corte-fricción.

## Pendientes para cerrar el diseño

- Ninguna.

## Alcance y advertencias

- El Manual de Puentes MTC 2018, art. 2.8.1.1.12.6 y Tabla 2.8.1.1.12.6-1, respalda φp = 0.50 para la componente pasiva en Estado Límite de Resistencia; para Evento Extremo I se adopta φp = 1.00 conforme a la regla general del MTC y AASHTO LRFD. No se usa un factor 1.50 para mayorar el empuje en el diseño estructural.
- La ley pasiva se prolonga desde la coronación de la zapata hasta la base adoptada (2.800 m); las cotas del dentellón fueron verificadas en el proyecto.
- El medio pasivo adoptado es el suelo de fundación GW (γ = 1.96 Tn/m³, φ' = 39.8°), según el Estudio de Suelos Informe N.° 001-2026/ING-CON-26-E-008/INGEOTECON-135-26; tanto el agente de subestructura como este diseño usan el peso específico del suelo de fundación para el pasivo.
- El modelo de Rankine solo es válido con suelo granular drenado frente al dentellón; no aplica a una llave embebida en concreto.
- El dentellón y la zapata se consideran vaciados monolíticamente; las barras deben desarrollar fy dentro de la zapata.
- La cuantía mínima total de losa se reparte entre dos caras; la cara traccionada conserva rho = 0.0012 y la opuesta recibe el saldo. El acero horizontal se divide por mitades.
- La cara en contacto con el pasivo es la cara traccionada para el sentido de carga adoptado.

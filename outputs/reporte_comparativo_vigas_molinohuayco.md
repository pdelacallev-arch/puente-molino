# Reporte comparativo — Vigas principales del Puente Molinohuayco

**Proyecto:** Puente Molinohuayco (L = 50.00 m, 3 vigas, tablero de concreto)
**Fecha:** 10 de septiembre de 2026
**Elaborado con:** sistema `analisis_superestructura`, módulo `vigas_principales`

---

## 1. Objeto y fuentes

Comparar la sección y los resultados de verificación de tres referencias:

| Fuente           | Descripción                                                           | Unidades / método                                         |
| ---------------- | --------------------------------------------------------------------- | --------------------------------------------------------- |
| **Anexo 2 (ET)** | Memoria de cálculo estructural de vigas metálicas, nov-2022 (15 pág.) | MKS; LRFD con coeficiente de concentración / N.° de vigas |
| **PLANO E-02**   | Caso del software, sección original                                   | SI; MTC 2018; distribución por parrilla                   |
| **MODIFICADO**   | Caso del software, ala 500 × 25 mm y alma 16 mm                       | SI; MTC 2018; distribución por parrilla                   |

> **Advertencia metodológica.** Las tres fuentes **no** usan el mismo método de distribución de carga viva ni las mismas unidades. La comparación de geometría y de estado de verificaciones es directa; la comparación de demandas es solo referencial.

---

## 2. Sección transversal (zona central, corte C–C)

| Parámetro       |                         Anexo 2 (ET) |            PLANO E-02 |            MODIFICADO |
| --------------- | -----------------------------------: | --------------------: | --------------------: |
| Ala superior    |                          450 × 25 mm |           450 × 20 mm |       **500 × 25 mm** |
| Alma            |                         1750 × 19 mm |          1755 × 14 mm |      **1755 × 16 mm** |
| Ala inferior    | 650 × 25 mm + platabanda 650 × 32 mm | 600 mm (t = 25/32/50) | 600 mm (t = 25/32/50) |
| Canto del acero |                            ≈ 1832 mm |               1825 mm |               1830 mm |
| Área de acero | 815.5 cm² | 635.7 cm² | 705.8 cm² |

![Comparación de las secciones metálicas](comparacion_secciones_vigas.png)

*Figura 1. Corte C–C (centro de luz) a escala. En PLANO E-02 y MODIFICADO el ala inferior varía a lo largo de la luz (t = 25/32/50 mm); se dibuja la zona central (50 mm). En el Anexo 2 (ET), la platabanda de 650 × 32 mm existe solo en el tramo central.*

---

## 3. Propiedades de sección (centro de luz)

| Propiedad                  |   Anexo 2 (ET) |    PLANO E-02 |    MODIFICADO |
| -------------------------- | -------------: | ------------: | ------------: |
| Ix del acero               |  4 083 547 cm⁴ | 3 210 579 cm⁴ | 3 794 614 cm⁴ |
| Ix compuesto (corto plazo) | 12 198 352 cm⁴ | 8 562 075 cm⁴ | 8 842 670 cm⁴ |
| Ancho efectivo             |        1600 mm |       2000 mm |       2000 mm |
| Relación modular n         |            8.0 |           7.3 |           7.3 |
| Momento plástico Mp        |              — |     25.37 t·m |     26.76 t·m |
| Dp/Dt (ductilidad)         |              — |        0.4487 |        0.4104 |

> Las propiedades compuestas del Anexo 2 se calcularon con n = 8 y be = 1.60 m; las del software, con n = Es/Ec y be = 2.00 m. Por eso la comparación de Ix compuesto no es directa.

---

## 4. Verificaciones (viga exterior, la gobernante)

Se muestra el DCR = demanda / capacidad del software; para el Anexo 2, el resultado tal como figura en su memoria.

| Verificación                          | Anexo 2 (ET)           | PLANO E-02       | MODIFICADO       |
| ------------------------------------- | ---------------------- | ---------------- | ---------------- |
| Flexión positiva (plástica)           | OK (øMp > Mu)          | OK — 0.966       | OK — 0.895       |
| **Ductilidad Dp/Dt**                  | No reportada           | **NO — 1.068**   | **OK — 0.977**   |
| **Pandeo / compacidad del alma**      | OK (hc/tw = 92.1 < 93) | **NO — 1.043**   | **OK — 0.799**   |
| **Corte del alma**                    | OK (fv ≤ 0.33 Fy)      | **NO — 1.012**   | **OK — 0.686**   |
| Esfuerzo elástico (Servicio II)       | —                      | OK — 0.826       | OK — 0.806       |
| Fatiga                                | No reportada           | OK — 0.779       | OK — 0.752       |
| Estabilidad en construcción           | OK (fb < 0.9 Fy)       | OK — 0.184       | OK — 0.161       |
| Deflexión por carga viva              | OK (L/1000)            | OK — 0.923       | OK — 0.893       |
| Atiesadores / diafragmas / conectores | Diseñados              | Fuera de alcance | Fuera de alcance |

Viga interior (referencia del software):

| Verificación             | PLANO E-02 | MODIFICADO |
| ------------------------ | ---------: | ---------: |
| Flexión positiva         |      0.708 |      0.659 |
| Ductilidad Dp/Dt         | 1.068 (NO) | 0.977 (OK) |
| Compacidad del alma      | 1.043 (NO) | 0.799 (OK) |
| Corte del alma           |      0.937 |      0.636 |
| Servicio II              |      0.618 |      0.604 |
| Fatiga                   |      0.707 |      0.683 |
| Deflexión por carga viva |      0.805 |      0.778 |

---

## 5. Estado final

|                         | Anexo 2 (ET)            | PLANO E-02               | MODIFICADO               |
| ----------------------- | ----------------------- | ------------------------ | ------------------------ |
| Incumplimientos         | Ninguno (por su método) | 3                        | 0                        |
| Verificación gobernante | —                       | Ductilidad Dp/Dt (1.068) | Ductilidad Dp/Dt (0.977) |
| Estado                  | OK                      | **NO_CUMPLE**            | **CONDICIONAL**          |

---

## 6. Conclusiones

1. **Anexo 2 (ET)** verificó su sección (As = 815.5 cm², con platabanda central) como satisfactoria, pero con un método MKS y una distribución de carga viva por coeficiente de concentración dividido entre el número de vigas, distinto del que usa el software.
2. **PLANO E-02** (ala 450 × 20, alma 14 mm) **no cumple**: falla en ductilidad Dp/Dt, compacidad del alma y corte.
3. **MODIFICADO** (ala 500 × 25, alma 16 mm) **corrige los tres incumplimientos** y pasa todas las verificaciones numéricas.
4. El cambio decisivo fue **ensanchar y engrosar el ala superior** (450 → 500 mm; 20 → 25 mm): eleva el eje neutro plástico y reduce Dp/Dt de 0.4487 a 0.4104 (límite 0.42). El alma a 16 mm resuelve además compacidad y corte.
5. La sección de MODIFICADO (705.8 cm²) es **más liviana** que la del Anexo 2 (815.5 cm²) y, con el método MTC 2018 del software, resulta factible.

---

### Trazabilidad

- Ejecuciones del software (las carpetas conservan el nombre original de la revisión):
  - PLANO E-02 → `analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/ejecuciones/20260910T230952-0500/`
  - MODIFICADO → `analisis_superestructura/casos/molinohuayco/MODIFICADO-R00/ejecuciones/20260910T232234-0500/`
- Fuente del Anexo 2: `memoria_estructuras/anexo_2_vigas_metalicas.pdf`

> Los resultados son una ayuda de cálculo y requieren revisión y aprobación del ingeniero estructural responsable.

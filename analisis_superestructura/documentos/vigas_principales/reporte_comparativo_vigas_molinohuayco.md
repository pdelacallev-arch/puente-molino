# Reporte comparativo — Vigas principales del Puente Molinohuayco

**Proyecto:** Puente Molinohuayco (L = 50.00 m, 3 vigas, tablero de concreto)
**Fecha:** 18 de septiembre de 2026
**Elaborado con:** sistema `analisis_superestructura`, módulo `vigas_principales`

---

## 1. Objeto y fuentes

Comparar la sección y los resultados de verificación de tres referencias:

| Fuente           | Descripción                                                           | Unidades / método                                         |
| ---------------- | --------------------------------------------------------------------- | --------------------------------------------------------- |
| **Anexo 2 (ET)** | Memoria de cálculo estructural de vigas metálicas, nov-2022 (15 pág.) | MKS; LRFD con coeficiente de concentración / N.° de vigas |
| **PLANO E-02**   | Caso del software, sección original                                   | SI; MTC 2018; distribución por parrilla                   |
| **PROPUESTA**    | Caso del software, ala 500 × 32 mm y alma 19 mm                       | SI; MTC 2018; distribución por parrilla                   |

> **Advertencia metodológica.** Las tres fuentes **no** usan el mismo método de distribución de carga viva ni las mismas unidades. La comparación de geometría y de estado de verificaciones es directa; la comparación de demandas es solo referencial.

---

## 2. Sección transversal (zona central, corte C–C)

| Parámetro       |                         Anexo 2 (ET) |            PLANO E-02 |             PROPUESTA |
| --------------- | -----------------------------------: | --------------------: | --------------------: |
| Ala superior    |                          450 × 25 mm |           450 × 20 mm |       **500 × 32 mm** |
| Alma            |                         1750 × 19 mm |          1755 × 14 mm |      **1743 × 19 mm** |
| Ala inferior    | 650 × 25 mm + platabanda 650 × 32 mm | 600 mm (t = 25/32/50) | 600 mm (t = 25/32/50) |
| Canto del acero |                            ≈ 1832 mm |               1825 mm |               1825 mm |
| Área de acero | 815.5 cm² | 635.7 cm² | 791.2 cm² |

![Comparación de las secciones metálicas](comparacion_secciones_vigas.png)

*Figura 1. Corte C–C (centro de luz) a escala. En PLANO E-02 y PROPUESTA el ala inferior varía a lo largo de la luz (t = 25/32/50 mm); se dibuja la zona central (50 mm). En el Anexo 2 (ET), la platabanda de 650 × 32 mm existe solo en el tramo central.*

---

## 3. Propiedades de sección (centro de luz)

| Propiedad                  |   Anexo 2 (ET) |    PLANO E-02 |     PROPUESTA |
| -------------------------- | -------------: | ------------: | ------------: |
| Ix del acero               |  4 083 547 cm⁴ | 3 210 579 cm⁴ | 4 371 676 cm⁴ |
| Ix compuesto (corto plazo) | 12 198 352 cm⁴ | 8 562 075 cm⁴ | 9 206 221 cm⁴ |
| Ancho efectivo             |        1600 mm |       2000 mm |       2000 mm |
| Relación modular n         |            8.0 |           7.3 |           7.3 |
| Momento plástico Mp        |              — |     25.37 t·m |     28.44 t·m |
| Dp/Dt (ductilidad)         |              — |        0.4487 |        0.3909 |

> Las propiedades compuestas del Anexo 2 se calcularon con n = 8 y be = 1.60 m; las del software, con n = Es/Ec y be = 2.00 m. Por eso la comparación de Ix compuesto no es directa.

---

## 4. Verificaciones (viga exterior, la gobernante)

Se muestra el DCR = demanda / capacidad del software; para el Anexo 2, el resultado tal como figura en su memoria.

| Verificación                          | Anexo 2 (ET)           | PLANO E-02       | PROPUESTA        |
| ------------------------------------- | ---------------------- | ---------------- | ---------------- |
| Flexión positiva (plástica)           | OK (øMp > Mu)          | OK — 0.966       | OK — 0.841       |
| **Ductilidad Dp/Dt**                  | No reportada           | **NO — 1.068**   | **OK — 0.931**   |
| **Pandeo / compacidad del alma**      | OK (hc/tw = 92.1 < 93) | **NO — 1.043**   | **OK — 0.621**   |
| **Corte del alma**                    | OK (fv ≤ 0.33 Fy)      | **NO — 1.012**   | **OK — 0.416**   |
| Esfuerzo elástico (Servicio II)       | —                      | OK — 0.826       | OK — 0.803       |
| Fatiga                                | No reportada           | OK — 0.779       | OK — 0.715       |
| Estabilidad en construcción           | OK (fb < 0.9 Fy)       | OK — 0.184       | OK — 0.374       |
| Deflexión vehicular (L/800)           | OK (L/1000)            | OK — 0.923       | OK — 0.506       |
| **Deflexión veh. + peat. (L/1000)**   | —                      | —                | **OK — 0.984**   |
| Atiesadores / diafragmas / conectores | Diseñados              | Fuera de alcance | Fuera de alcance |

Viga interior (referencia del software):

| Verificación                    | PLANO E-02 | PROPUESTA  |
| ------------------------------- | ---------: | ---------: |
| Flexión positiva                |      0.708 |      0.622 |
| Ductilidad Dp/Dt                | 1.068 (NO) | 0.931 (OK) |
| Compacidad del alma             | 1.043 (NO) | 0.621 (OK) |
| Corte del alma                  |      0.937 |      0.387 |
| Servicio II                     |      0.618 |      0.616 |
| Fatiga                          |      0.707 |      0.649 |
| Deflexión vehicular (L/800)     |      0.805 |      0.441 |
| Deflexión veh. + peat. (L/1000) |      —     |      0.551 |

---

## 5. Estado final

|                         | Anexo 2 (ET)            | PLANO E-02               | PROPUESTA                             |
| ----------------------- | ----------------------- | ------------------------ | ------------------------------------- |
| Incumplimientos         | Ninguno (por su método) | 3                        | 0                                     |
| Verificación gobernante | —                       | Ductilidad Dp/Dt (1.068) | Deflexión veh. + peat. S-I (0.984)    |
| Estado                  | OK                      | **NO_CUMPLE**            | **CUMPLE**                            |

---

## 6. Conclusiones

1. **Anexo 2 (ET)** verificó su sección (As = 815.5 cm², con platabanda central) como satisfactoria, pero con un método MKS y una distribución de carga viva por coeficiente de concentración dividido entre el número de vigas, distinto del que usa el software.
2. **PLANO E-02** (ala 450 × 20, alma 14 mm) **no cumple**: falla en ductilidad Dp/Dt, compacidad del alma y corte.
3. **PROPUESTA** (ala 500 × 32, alma 19 mm) **corrige todos los incumplimientos** y pasa todas las verificaciones numéricas.
4. El cambio decisivo respecto al PLANO E-02 fue **ensanchar el ala superior, aumentar su espesor y engrosar el alma** (450 → 500 mm; 20 → 32 mm; 14 → 19 mm): eleva el eje neutro plástico y reduce Dp/Dt de 0.4487 a 0.3909 (límite 0.42). El alma a 19 mm resuelve compacidad y corte con mayor margen. El espesor del ala superior de 32 mm fue necesario para controlar la deflexión combinada vehicular + peatonal bajo Servicio I (DCR = 0.984, límite L/1000 = 50 mm).
5. La sección de PROPUESTA (791.2 cm²) es **más liviana** que la del Anexo 2 (815.5 cm²) y, con el método MTC 2018 del software, resulta factible. La verificación gobernante es la deflexión combinada (veh. + peat.) de Servicio I en la viga exterior (49.21 mm ≤ 50.00 mm).

---

### Trazabilidad

- Ejecuciones del software (las carpetas conservan el nombre original de la revisión):
  - PLANO E-02 → `analisis_superestructura/casos/molinohuayco/PRELIMINAR-R00/ejecuciones/20260910T230952-0500/`
  - PROPUESTA → `analisis_superestructura/casos/molinohuayco/PROPUESTA-R00/ejecuciones/20260917T132241-0500/`
- Fuente del Anexo 2: `memoria_estructuras/anexo_2_vigas_metalicas.pdf`

> Los resultados son una ayuda de cálculo y requieren revisión y aprobación del ingeniero estructural responsable.

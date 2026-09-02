# Comparación de cargas de superestructura

**Fuente 1:** `metrado_tablero.py` — cálculo reproducible con parámetros confirmados (ver `registro_verificacion_datos_3.1_a_3.4.md`)  
**Fuente 2:** `agente_subestructura.py` — valores del Anexo 3 / Cuadros Nº 40 y 41 de la Memoria

---

## 1. Reacciones totales por estribo

| Carga | `metrado_tablero.py` (tf) | `agente_subestructura.py` (tf) | Diferencia (tf) | Diferencia (%) | Nota |
|:---|---:|---:|---:|---:|:-----|
| DC | 155.90 | 146.58¹ | −9.32 | −6.0% | El metrado da mayor peso propio |
| DW | 17.25 | 17.28¹ | +0.03 | +0.2% | Prácticamente igual |
| PL | 18.50 | 18.00¹ | −0.50 | −2.7% | Diferencia por carga peatonal (0.370 vs 0.360 tf/m²) |
| LL+IM | 77.71 | 80.19² | +2.48 | +3.2% | El Anexo 3 da mayor sobrecarga |
| BR | 9.80 | 20.05² | +10.25 | +104.6% | **Diferencia significativa** |

¹ Calculado: `valor_por_metro × 6.0 m`  
² Valor directo del Anexo 3 / Cuadro Nº 40-41

---

## 2. Cargas por metro de ancho de estribo (tf/m)

| Carga | `metrado_tablero.py` | `agente_subestructura.py` | Diferencia |
|:---|---:|---:|---:|
| DC | 25.98 | 24.43 | −1.55 |
| DW | 2.88 | 2.88 | 0.00 |
| PL | 3.08 | 3.00 | −0.08 |
| LL+IM | 12.95 | 13.37 | +0.42 |
| BR | 1.63 | 3.34 | +1.71 |

---

## 3. Desglose de discrepancias

### 3.1 DC (Carga permanente)

`metrado_tablero.py` calcula desde la geometría con los valores verificados:

| Componente | Carga (tf/m) |
|:---|---:|
| Losa (6.00 × 0.20 × 2.40) | 2.880 |
| Veredas (2.00 × 0.20 × 2.40) | 0.960 |
| Vigas (3 × 0.07115 × 7.85) | 1.676 |
| Diafragmas (9 líneas) | 0.121 |
| Barandas (2 × 0.300) | 0.600 |
| **Total w_DC** | **6.236** |
| **R_DC = 6.236 × 50 / 2** | **155.90 tf** |

`agente_subestructura.py` usa: 163.86 tf (Anexo 3) − 17.28 tf(DW) = **146.58 tf** (para DC puro).  
El metrado da **155.90 tf**, un **+6.4%** superior. Posible causa: el Anexo 3 podría no incluir algunos componentes (diafragmas, barandas, veredas).

### 3.2 DW (Superficie de rodadura)

Ambos calculan: `0.075 × 4.00 × 2.30 × 50 / 2 = 17.25 tf`. **Coinciden.**

### 3.3 PL (Carga peatonal)

- `metrado_tablero.py`: `2.00 × 0.370 × 50 / 2 = 18.50 tf`
- `agente_subestructura.py`: `2 × 1.0 × 0.36 × 25 = 18.00 tf`  
  *Nota: usa 0.36 tf/m² en lugar de 0.370 tf/m², y 25 m (media luz) en lugar de la fórmula completa. Diferencia menor.*

### 3.4 LL+IM (Sobrecarga vehicular)

- `metrado_tablero.py` con parámetros HL-93 + IM 1.33 + FPM 1.20: **77.71 tf**
- `agente_subestructura.py` (Anexo 3, Cuadro Nº 40): **80.19 tf**  
  *Diferencia del +3.2%. Posible causa: factores de presencia múltiple distintos, o posición vehicular diferente.*

### 3.5 BR (Frenado)

- `metrado_tablero.py` con 1 carril + FPM 1.20: **9.80 tf**
- `agente_subestructura.py` (Anexo 3, Cuadro Nº 41): **20.05 tf**  
  *Diferencia del +104.6%. Como señala el reporte (Sección 18.2), el valor del Anexo 3 duplica el de un carril. **Requiere conciliación:** puede deberse a 2 carriles de diseño o a un factor adicional.*

---

## 4. Impacto en el análisis de subestructura

Si se usaran los valores de `metrado_tablero.py` (datos confirmados) en lugar de los del Anexo 3:

| Efecto | Sentido |
|:-------|:--------|
| Mayor DC (+9.32 tf/estribo) | Aumenta estabilización vertical y fricción → favorable |
| PL similar (−0.50 tf) | Despreciable |
| Menor LL+IM (−2.48 tf) | Reduce efecto desestabilizador → favorable |
| Menor BR (−10.25 tf) | **Reduce significativamente** las fuerzas horizontales desestabilizadoras → favorable |

**Conclusión:** usar las cargas de `metrado_tablero.py` resultaría en verificaciones de estabilidad **más favorables** que las actuales del `agente_subestructura.py`, excepto por el mayor DC que requeriría verificar capacidad portante. **La discrepancia de BR debe resolverse antes del diseño definitivo.**

---

## 5. Resumen gráfico

```
DC:      metrado  ████████████████████████████████████████░░░░ 155.90 tf
         Anexo 3  ██████████████████████████████████░░░░░░░░░░ 146.58 tf

DW:      metrado  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  17.25 tf
         Anexo 3  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  17.28 tf

PL:      metrado  █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  18.50 tf
         Anexo 3  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  18.00 tf

LL+IM:   metrado  ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░  77.71 tf
         Anexo 3  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░  80.19 tf

BR:      metrado  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   9.80 tf
         Anexo 3  ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20.05 tf
```

*Cada bloque █ representa aprox. 4 tf*

---

*Generado el 21 de julio de 2026 con los datos confirmados en la verificación interactiva.*

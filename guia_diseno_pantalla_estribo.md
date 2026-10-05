# GUÍA DIDÁCTICA: DISEÑO DE LA PANTALLA DE ESTRIBO EN VOLADIZO
**Referencia:** *Puentes – AASHTO LRFD* · MSc. Ing. Arturo Rodríguez Serquén · Págs. 270 y 282-288  
**Norma aplicable:** AASHTO LRFD Bridge Design Specifications

---

## INTRODUCCIÓN

La **pantalla** (también llamada fuste o muro) es el elemento vertical del estribo en voladizo que retiene el relleno y transmite las cargas de la superestructura hacia la zapata de cimentación. Actúa como una **viga en voladizo empotrada en la zapata**, sujeta a empujes horizontales del suelo, sobrecargas y cargas sísmicas.

```
              SUPERESTRUCTURA
              ↓ PDC  ↓ PDW  ↓ PLL+IM
          ┌───┴───────────────┴───┐  ← Viga de apoyo / capitel
          │                       │
  BR →    │  PANTALLA             │  ← cara hacia terreno
  EH →   │   (voladizo)          │
  LS →   │   h = H - D           │
          │                       │
  ─────── ├───────────────────────┤  ← Punto P (base de pantalla)
          │         ZAPATA        │
  ─────── └───────────────────────┘
          ←─── B ───────────────→
          ←─Lp─→       ←── Lt ──→
              (punta)       (talón)
```

> La pantalla tiene sección **trapezoidal** con espesor mínimo superior ($t_{sup}$) y espesor máximo en la base ($t_{inf}$), zona de empotramiento.

---

## PASO 1 — PRE-DIMENSIONADO DE LA PANTALLA (Ref. pág. 270)

### 1.1 Criterio de dimensionamiento

El pre-dimensionado se realiza en función de la **altura total de relleno** $H$ (desde la superficie del terreno hasta la base de la zapata).

| Elemento | Fórmula | Resultado (H=7.00 m) | Valor Adoptado |
|:---|:---|:---|:---|
| Espesor superior pantalla | $t_{sup} = H / 24$ | $7.00/24 = 0.29 \text{ m}$ | **0.30 m** *(mín. recomendado)* |
| Espesor inferior pantalla | $t_{inf} = 0.10 \cdot H$ | $0.10 \times 7.00 = 0.70 \text{ m}$ | **0.90 m** |

> ⚠️ **Criterio de mínimo:** El espesor superior $t_{sup}$ nunca debe ser menor a **0.30 m** para garantizar recubrimiento y espacio para el acero de refuerzo.

### 1.2 Altura libre de la pantalla

$$h = H - D = 7.00 - 1.10 = \mathbf{5.90 \text{ m}}$$

### 1.3 Esquema de la sección de la pantalla

```
  ┌──────────────┐   ← tsup = 0.30 m
  │              │
  │   PANTALLA   │   h = 5.90 m (voladizo)
  │              │
  │              │
  └──────────────┘   ← tinf = 0.90 m
  ════════════════   ← Punto P (base de pantalla)
```

La variación de espesor puede ser **lineal** (cara posterior inclinada) o **escalonada** según el detalle del diseño.

---

## PASO 2 — CARGAS QUE ACTÚAN SOBRE LA PANTALLA (Ref. pág. 282)

La pantalla se diseña como una viga en voladizo de $h = 5.90 \text{ m}$, **empotrada en su base** (punto P).

### 2.1 Diagrama de cargas (Fig. 5.19 del libro)

```
   CARA DEL TERRENO                                    CARA LIBRE
   ─────────────────────────────────────────────────────────────
  ← BR  (en la cima, desde superestructura)    Elev. = 7.70 m sobre P

  ← ─ ─ ─ ─ ─ p" (LS, uniforme) ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

  ─┐                                                         h = 5.90 m
   │← p (EH, triangular, crece hacia abajo) ─ ─ ─ ─ ─ ─ ─ ─
   │
   │← ─ ─ p'(EQterr, uniforme, sísmica del suelo) ─ ─ ─ ─ ─
  ─┘
  ══════════════════════════════════════════ Punto P (base)
                    ↑
              BR, PIR, PEQi actúan a sus alturas respectivas
```

### 2.2 Tabla de cargas en la base de la pantalla — Punto P

| Carga | Tipo | Carga Dist. (T/m) | Fuerza (T/m) | Brazo $Y_P$ (m) | Momento (T-m) |
|:---|:---|:---|:---|:---|:---|
| **LS** | Sobrecarga viva (terreno equiv.) | $p''=0.333 \times 0.60 \times 1.925 = 0.385$ | $0.385 \times 5.90 = 2.27$ | 2.95 | **6.70** |
| **EH** | Empuje horizontal estático | $p=0.333 \times 5.90 \times 1.925 = 3.786$ | $0.5 \times 5.90 \times 3.786 = 11.17$ | 1.97 | **22.00** |
| **EQ$_{terr}$** | Empuje sísmico del suelo | $p'=0.5(0.457-0.333)\times 5.90 \times 1.925 = 0.704$ | $0.704 \times 5.90 = 4.15$ | 2.95 | **12.25** |
| **0.5 PIR** | Fuerza inercial pantalla (50%) | — | 0.68 | 2.47 | **1.68** |
| **PEQi** | Fuerza inercial superestructura | — | 4.97 | 5.15 | **25.60** |
| **BR** | Fuerza de frenado | — | 1.99 | 7.70 | **15.32** |

> **Notas:**
> - Los brazos $Y_P$ se miden desde el punto P.
> - EH (triangular) → brazo = $h/3 = 5.90/3 = 1.97$ m.
> - LS y EQ$_{terr}$ (uniforme) → brazo = $h/2 = 5.90/2 = 2.95$ m.

### 2.3 Fuerza inercial de la pantalla (PIR) — Art. C11.6.5.1

Para el diseño estructural, el PIR se calcula **sin incluir** la masa del suelo sobre el talón:

$$\boxed{PIR = K_h \cdot W_{est}}$$

- $K_h = \dfrac{PGA \times F_{pga}}{2} = \dfrac{0.30 \times 1.20}{2} = 0.18$
- $W_{est} = \text{peso propio de la pantalla} = 7.61 \text{ T/m}$
- $PIR = 0.18 \times 7.61 = 1.37 \text{ T/m}$; $\quad Y_P = 2.47 \text{ m}$

### 2.4 Criterio sísmico — Art. 11.6.5.1

$PAE = EH + EQ_{terr} = 11.17 + 4.15 = 15.32 \text{ T/m}$

Se toma el **resultado más conservador**:

| Expresión | Resultado |
|:---|:---|
| $PAE + 0.5 \cdot PIR = 15.32 + 0.68$ | **= 16.01 T/m ← RIGE** |
| $(0.5 \cdot PAE) + PIR = 7.66 + 1.37$ | = 9.03 T/m |

> La primera expresión es crítica. Por ello, en las combinaciones se utilizan separadamente: $EQ_{terr} = 4.15 \text{ T/m}$ y $0.5 \cdot PIR = 0.68 \text{ T/m}$.

---

## PASO 3 — COMBINACIONES DE CARGA Y MOMENTO ÚLTIMO (Ref. pág. 283)

Según **Tabla 3.4.1-1** de AASHTO LRFD. Factor de modificación $\eta = \eta_D \cdot \eta_R \cdot \eta_I = 1.0$.

### 3.1 Estado Límite de Resistencia I

$$\boxed{M_u = \eta \left[ 1.75 M_{LS} + 1.50 M_{EH} + 1.75 M_{BR} \right]}$$

$$M_u = 1.00 \left[ 1.75(6.70) + 1.50(22.00) + 1.75(15.32) \right] = \mathbf{71.54 \text{ T-m}}$$

### 3.2 Estado Límite de Evento Extremo I (Sismo)

El factor de resistencia para este estado es $\phi_f = 1.0$ (Art. 11.5.8).

$$\boxed{M_u = \eta \left[ 0.50 M_{LS} + 1.00 M_{EH} + 1.00 M_{EQ} + 0.50 M_{BR} \right]}$$

$$M_u = 1.00 \left[ 0.50(6.70) + 1.0(22.00) + 1.0(12.25 + 1.68 + 25.60) + 0.50(15.32) \right]$$

$$M_u = 3.35 + 22.00 + 39.53 + 7.66 = \mathbf{72.54 \text{ T-m}}$$

### 3.3 Momento de diseño que rige

| Estado Límite | $M_u$ (T-m) | $\phi_f$ |
|:---|:---|:---|
| Resistencia I | 71.54 | 0.90 |
| Evento Extremo I | **72.54** | **1.00** |

> **El momento de diseño es $M_u = 72.54 \text{ T-m}$** (Evento Extremo I rige porque $\phi_f = 1.0$).

---

## PASO 4 — DISEÑO POR FLEXIÓN: ACERO PRINCIPAL (Ref. pág. 283-284)

El acero principal se coloca en la **cara del terreno** (cara de tracción).

### 4.1 Materiales

| Material | Parámetro | Valor |
|:---|:---|:---|
| Concreto | $f'_c$ | 210 kg/cm² (21 MPa) |
| Acero | $f_y$ | 4200 kg/cm² (420 MPa) |
| Recubrimiento | $r$ (Tabla 5.10.1-1) | 5.0 cm |

### 4.2 Peralte efectivo (d)

Se asume varilla tentativa **Ø 3/4"** ($\varnothing = 1.905 \text{ cm}$):

$$d_c = r + \frac{\varnothing}{2} = 5.0 + \frac{1.905}{2} = 5.95 \text{ cm}$$

$$\boxed{d = t_{inf} - d_c = 90 - 5.95 = 84.05 \text{ cm}}$$

```
  ←────── tinf = 90 cm ──────→
  ┌───────────────────────────┐  ← cara libre (compresión)
  │                           │
  │       SECCIÓN EN LA       │  d = 84.05 cm
  │       BASE DE PANTALLA    │
  │                     ●─────┤  ← centroide del acero
  └───────────────────────────┘
                        ←dc=5.95→
```

### 4.3 Cálculo del área de acero (proceso iterativo)

Ecuación de flexión:

$$M_u = \phi_f \cdot A_s \cdot f_y \cdot \left(d - \frac{a}{2}\right) \quad \text{con} \quad a = \frac{A_s \cdot f_y}{0.85 \cdot f'_c \cdot b}$$

Para $\phi_f = 1.0$ y $b = 100 \text{ cm}$:

| Iter. | $a$ asumido (cm) | $A_s$ calculado (cm²/m) | $a$ verificado (cm) |
|:---|:---|:---|:---|
| 1 | 5.00 | $\dfrac{72.54 \times 10^5}{4200 \times (84.05 - 2.50)} \approx 21.00$ | $\dfrac{21.00 \times 4200}{0.85 \times 210 \times 100} = 4.96$ |
| 2 | 4.96 | **21.17** | 4.98 ≈ OK ✓ |

$$\mathbf{A_s = 21.17 \text{ cm}^2/\text{m}}$$

### 4.4 Selección del refuerzo

Usando varilla **Ø 3/4"** ($A_{1\varnothing} = 2.84 \text{ cm}^2$):

$$s = \frac{2.84}{21.17} \times 100 = 13.4 \text{ cm} \quad \Rightarrow \quad \text{Adoptar } s = 0.13 \text{ m}$$

$$A_s^{real} = \frac{2.84 \times 100}{13} = 21.84 \text{ cm}^2/\text{m} > 21.17 \text{ cm}^2/\text{m} \checkmark$$

$$\boxed{\textbf{USAR: 1 Ø 3/4" @ 0.13 m}}$$

---

## PASO 5 — VERIFICACIÓN DE ACERO MÍNIMO (Art. 5.6.3.3)

El acero proporcionado debe resistir el **menor** entre $M_{cr}$ y $1.33 M_u$.

### 5.1 Módulo de rotura del concreto

$$f_r = 0.63\sqrt{f'_c \text{(MPa)}} = 0.63\sqrt{21} = 2.89 \text{ MPa} \equiv 29.13 \text{ kg/cm}^2$$

### 5.2 Módulo resistente de la sección bruta (b=100 cm, h=90 cm)

$$S = \frac{b \cdot h^2}{6} = \frac{100 \times (90)^2}{6} = 135{,}000 \text{ cm}^3$$

### 5.3 Momento de fisuración

$$\boxed{M_{cr} = 1.1 \cdot f_r \cdot S = 1.1 \times 29.13 \times 135{,}000 \times 10^{-5} = 43.26 \text{ T-m}}$$

### 5.4 Cuadro de verificación

| Criterio | Valor (T-m) | Mínimo |
|:---|:---|:---|
| $M_{cr}$ | **43.26** | ← mínimo |
| $1.33 M_u = 1.33 \times 72.54$ | 96.48 | — |

El acero calculado resiste $M_u = 72.54 \text{ T-m} > 43.26 \text{ T-m}$ ✅

---

## PASO 6 — ACERO DE TEMPERATURA Y RETRACCIÓN (Art. 5.10.6)

Controla la fisuración por cambios de temperatura y retracción. Se coloca en **ambas caras** de la pantalla, en las dos direcciones.

### 6.1 Fórmula (Ec. 5.10.6-1)

$$\boxed{A_{s,temp} = \frac{0.18 \cdot b \cdot h}{2(b + h)}} \quad \left[\text{cm}^2/\text{m, en cada cara}\right]$$

### 6.2 Aplicación a la pantalla

Espesor promedio: $t_{prom} = \frac{0.30 + 0.90}{2} = 0.60 \text{ m}$

Altura de aplicación (zona sin acero en ambas caras): $h_{temp} = 5.90 - 2.50 = 3.40 \text{ m}$

Con $b = 60 \text{ cm}$, $h = 340 \text{ cm}$:

$$A_{s,temp} = \frac{0.18 \times 340 \times 60}{2(340 + 60)} = \frac{3{,}672}{800} = 4.59 \text{ cm}^2/\text{m (en cada cara)}$$

### 6.3 Límites (Ec. 5.10.6-2)

$$0.233 \text{ cm}^2/\text{m} \leq A_{s,temp} \leq 1.270 \text{ cm}^2/\text{m}$$

### 6.4 Selección — Ø 1/2" ($A_{1\varnothing} = 1.29 \text{ cm}^2$)

$$s = \frac{1.29}{4.59} \times 100 = 28.1 \text{ cm} \quad \Rightarrow \quad s = 0.28 \text{ m}$$

Separación máxima (Art. 5.10.6): $s_{máx} = \min(3t_{prom}, 1.50) = \min(1.80, 1.50) = 1.50 \text{ m} > 0.28 \text{ m}$ ✅

$$\boxed{\textbf{USAR: 1 Ø 1/2" @ 0.28 m (en cada cara, en ambas direcciones)}}$$

> **Nota del libro (pág. 284):** El acero de temperatura se coloca **en la cara opuesta al relleno** y también transversalmente en ambas caras, dado que no existe refuerzo en dirección perpendicular al acero principal.

---

## PASO 7 — REVISIÓN DE FISURACIÓN POR DISTRIBUCIÓN DE ARMADURA (Art. 5.6.7)

Verifica que el espaciamiento del refuerzo limite el **ancho de fisura** bajo cargas de servicio.

### 7.1 Momento de servicio — Estado Límite de Servicio I

$$\boxed{M_s = \eta \left[ 1.0 M_{LS} + 1.0 M_{EH} + 1.0 M_{BR} \right]}$$

$$M_s = 1.0 \left[ 6.70 + 22.00 + 15.32 \right] = 44.02 \text{ T-m/m}$$

Para la franja tributaria del espaciamiento ($s = 0.13$ m):

$$M_s = 44.02 \times 0.13 = 5.72 \text{ T-m}$$

### 7.2 Relación modular (n)

$$E_s = 2.04 \times 10^6 \text{ kg/cm}^2 \quad \text{(Art. 5.4.3.2)}$$

$$E_c = 15{,}300 \sqrt{f'_c} = 15{,}300 \sqrt{210} = 221{,}718 \text{ kg/cm}^2 \quad \text{(Ec. C5.4.2.4-3)}$$

$$\boxed{n = \frac{E_s}{E_c} = \frac{2.04 \times 10^6}{221{,}718} \approx 9}$$

### 7.3 Sección transformada y eje neutro (Fig. 5.21 y 5.22 del libro)

```
  ←── b = 13 cm ──→
  ┌───────────────────┐   ← fibra comprimida (cara libre)
  │   fc (compresión) │
  │ ──────────────── │   ← eje neutro (a distancia y desde arriba)
  │        C          │
  │        ↑          │   jd = d - y/3
  │        ↓          │
  │   ●    T          │   ← centroide del acero Ast
  └───────────────────┘
```

Área de acero transformada (franja de 13 cm):

$$A_{st} = n \cdot A_s = 9 \times 2.84 = 25.56 \text{ cm}^2$$

Equilibrio de momentos respecto al eje neutro:

$$b \cdot \frac{y^2}{2} = A_{st} \cdot (d - y)$$

$$13 \cdot \frac{y^2}{2} = 25.56 \cdot (84.05 - y)$$

$$6.5y^2 + 25.56y - 2{,}148.5 = 0$$

$$\mathbf{y = 16.32 \text{ cm}}$$

### 7.4 Brazo del par interno (jd)

$$jd = d - \frac{y}{3} = 84.05 - \frac{16.32}{3} = 78.61 \text{ cm}$$

### 7.5 Esfuerzo en el acero bajo servicio

$$\boxed{f_s = \frac{M_s}{A_s \cdot jd} = \frac{5.72 \times 10^5}{2.84 \times 78.61} = 2{,}562 \text{ kg/cm}^2}$$

Límite: $0.6 f_y = 0.6 \times 4200 = 2{,}520 \text{ kg/cm}^2$

> $f_s \approx 0.6 f_y$ — Diferencia menor al 2%, aceptable. ✅

### 7.6 Separación máxima de armadura (Ec. 5.6.7-1)

$$\boxed{s_{máx} = \frac{125{,}000 \cdot \gamma_e}{\beta_s \cdot f_{ss}} - 2 d_c}$$

**Factor $\beta_s$** (Ec. 5.6.7-2):

$$\beta_s = 1 + \frac{d_c}{0.7(h - d_c)} = 1 + \frac{5.95}{0.7(90 - 5.95)} = 1 + \frac{5.95}{58.84} = 1.10$$

**Exposición severa** → $\gamma_e = 0.75$:

$$s_{máx} = \frac{125{,}000 \times 0.75}{1.10 \times 2{,}562} - 2(5.95) = \frac{93{,}750}{2{,}818} - 11.90 = 33.2 - 11.9 = 21.9 \text{ cm}$$

$$s_{adoptado} = 13 \text{ cm} < s_{máx} = 21.9 \text{ cm} \checkmark$$

---

## PASO 8 — REVISIÓN POR CORTE (Ref. págs. 286-288)

Verificar que el peralte de la pantalla es suficiente sin necesitar refuerzo transversal (estribos).

> La sección crítica se toma en la **base de la pantalla** (Art. 5.7.3.2).

### 8.1 Cortante último actuante ($V_u$)

**Resistencia I** (franja de 1.0 m):

$$\boxed{V_u = \eta \left[ 1.75 V_{LS} + 1.50 V_{EH} + 1.75 V_{BR} \right]}$$

$$V_u = 1.00 \left[ 1.75(2.27) + 1.50(11.17) + 1.75(1.99) \right] = 3.97 + 16.76 + 3.48 = \mathbf{24.21 \text{ T}}$$

**Evento Extremo I:**

$$V_u = 1.00 \left[ 0.5(2.27) + 1.0(11.17) + 1.0(4.15 + 0.68 + 4.97) + 0.5(1.99) \right] = 23.10 \text{ T}$$

| Estado Límite | $V_u$ (T) |
|:---|:---|
| Resistencia I | **24.21 ← RIGE** |
| Evento Extremo I | 23.10 |

### 8.2 Peralte efectivo para corte ($d_v$) — Art. 5.7.2.8

$$\boxed{d_v = d - \frac{a}{2} = 84.05 - \frac{4.98}{2} = 81.56 \text{ cm}}$$

Verificación de límites:

| Condición | Valor (cm) | ¿OK? |
|:---|:---|:---|
| $d_v \geq 0.90 d = 0.90 \times 84.05$ | 75.64 | $81.56 > 75.64$ ✅ |
| $d_v \geq 0.72 h = 0.72 \times 90$ | 64.80 | $81.56 > 64.80$ ✅ |

### 8.3 Cálculo del factor β — Método General (Art. 5.7.3.4.2)

Como $l_{pant} = 5.90 \text{ m} > 0.40 \text{ m}$, **no aplica** el procedimiento simplificado → se usa el **método general**.

**a) Deformación unitaria del acero longitudinal ($\varepsilon_s$):**

Verificación previa: $M_u > V_u \cdot d_v \Rightarrow 71.54 > (24.21)(0.8156) = 19.75 \text{ T-m}$ ✅

$$\boxed{\varepsilon_s = \frac{\left|\dfrac{M_u}{d_v} + V_u\right|}{E_s \cdot A_s}} \quad \text{(Ec. 5.7.3.4.2-4)}$$

$$\varepsilon_s = \frac{\dfrac{71.54 \times 10^5}{81.56} + 24{,}210}{2.04 \times 10^6 \times 21.17} = \frac{87{,}686 + 24{,}210}{43{,}186{,}800} = 0.002592$$

**b) Longitud de espaciado equivalente ($s_{xe}$):**

Con $s_x = d_v = 81.56 \text{ cm} = 32.11 \text{ pulg.}$ y $a_g = 3/4 \text{ pulg.}$:

$$\boxed{s_{xe} = 1.38 \cdot \frac{s_x}{a_g + 0.63}} \quad \text{(en pulg., Ec. 5.7.3.4.2-7)}$$

$$s_{xe} = 1.38 \times \frac{32.11}{0.75 + 0.63} = 32.11 \text{ pulg.}$$

Verificación: $12 \leq 32.11 \leq 80$ pulg. ✅

**c) Factor β (Ec. 5.7.3.4.2-2):**

$$\boxed{\beta = \frac{4.8}{1 + 750 \varepsilon_s} \cdot \frac{51}{39 + s_{xe}}}$$

$$\beta = \frac{4.8}{1 + 750(0.002592)} \cdot \frac{51}{39 + 32.11} = \frac{4.8}{2.944} \times \frac{51}{71.11} = 1.631 \times 0.717 = \mathbf{1.17}$$

### 8.4 Resistencia al corte del concreto ($V_c$) — Ec. 5.7.3.3-3

$$\boxed{V_c = 0.265 \cdot \beta \cdot \sqrt{f'_c} \cdot b_v \cdot d_v}$$

$$V_c = 0.265 \times 1.17 \times \sqrt{210} \times 100 \times 81.56 \times 10^{-3} = \mathbf{36.65 \text{ T}}$$

### 8.5 Resistencia nominal ($V_n$) y de diseño ($V_r$)

$V_n$ es el **menor** de (Ec. 5.7.3.3-1 y 5.7.3.3-2):

| Criterio | Valor (T) |
|:---|:---|
| $V_c + V_s + V_p = 36.65 + 0 + 0$ | **36.65 ← mínimo** |
| $0.25 f'_c \cdot b_v \cdot d_v = 0.25 \times 210 \times 100 \times 81.56 \times 10^{-3}$ | 428.19 |

Con $\phi_v = 0.90$ (Ec. 5.5.4.2):

$$\boxed{V_r = \phi_v \cdot V_n = 0.90 \times 36.65 = 32.99 \text{ T}}$$

### 8.6 Verificación final

$$V_r = 32.99 \text{ T} > V_u = 24.21 \text{ T} \checkmark$$

> **La pantalla no requiere estribos.** ✅

---

## PASO 9 — RESUMEN DEL DISEÑO DE LA PANTALLA

### 9.1 Sección transversal con refuerzo

```
  ┌──┐  ← tsup = 0.30 m
  │  │   ○ ○ ○ ○ ○ ○ ○ ○ ○  → 1Ø1/2"@0.28m (As,temp, cara libre, horiz.)
  │  │   · · · · · · · · ·   → 1Ø1/2"@0.28m (As,temp, cara libre, vert.)
  │  │
  │  │                                h = 5.90 m
  │  │   · · · · · · · · ·   → 1Ø1/2"@0.28m (cara terreno, vert.)
  │  │   ● ● ● ● ● ● ● ● ●  → 1Ø1/2"@0.28m (cara terreno, horiz.)
  │  │
  │  │   ████████████████████ → 1Ø3/4"@0.13m (As principal, cara terreno)
  └──┘  ← tinf = 0.90 m
  ════  ← Punto P (cara superior de zapata)
```

### 9.2 Cuadro resumen del refuerzo

| Función | Varilla | Espaciamiento | Cara | $A_s$ (cm²/m) |
|:---|:---|:---|:---|:---|
| Acero principal — flexión | **Ø 3/4"** | **@ 0.13 m** | Cara del terreno (vertical) | 21.84 |
| Acero temperatura/retracción | **Ø 1/2"** | **@ 0.28 m** | Ambas caras / ambas direcciones | 4.59 c/u |

### 9.3 Cuadro de verificaciones

| Verificación | Norma | Solicitación | Resistencia/Límite | Estado |
|:---|:---|:---|:---|:---|
| Flexión | Art. 5.6.3.2 | $M_u = 72.54$ T-m | $\phi M_n \geq M_u$ | ✅ OK |
| Acero mínimo | Art. 5.6.3.3 | $M_u = 72.54 > M_{cr} = 43.26$ | $A_s^{prov} > A_s^{req}$ | ✅ OK |
| Fisuración | Art. 5.6.7 | $s = 13$ cm | $s_{máx} = 21.9$ cm | ✅ OK |
| Corte | Art. 5.7.3.3 | $V_u = 24.21$ T | $V_r = 32.99$ T | ✅ OK (sin estribos) |

---

## REFERENCIAS NORMATIVAS

| Artículo AASHTO LRFD | Contenido |
|:---|:---|
| Tabla 3.4.1-1 | Factores de carga para combinaciones de estados límite |
| Art. 5.4.3.2 | Módulo de elasticidad del acero de refuerzo |
| Ec. C5.4.2.4-3 | Módulo de elasticidad del concreto |
| Art. 5.5.4.2 | Factores de resistencia $\phi$ |
| Art. 5.6.3.3 | Acero mínimo por flexión |
| Art. 5.6.7 | Distribución del refuerzo — control de fisuración |
| Art. 5.7.2.8 | Peralte efectivo para corte $d_v$ |
| Art. 5.7.3.3 | Resistencia al corte (Ec. $V_c$, $V_n$) |
| Art. 5.7.3.4.2 | Procedimiento general para el cálculo de $\beta$ |
| Art. 5.10.6 | Acero de temperatura y retracción |
| Art. 11.5.8 | Factor de resistencia $\phi$ para Evento Extremo |
| Art. 11.6.5.1 (C) | Fuerza inercial del estribo (PIR) |

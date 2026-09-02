# Sesión de clase: evaluación sísmica en CSiBridge del Puente Agua Flor
## Superestructura reticulada de un tramo, luz de 60 m y tablero de concreto armado de 8.40 m

---

## 0. Ficha de la sesión

| Campo | Contenido |
|---|---|
| Tema | Espectro de respuesta y verificaciones sísmicas de una superestructura reticulada de un solo tramo |
| Caso | Puente Agua Flor — Chanchamayo, Junín |
| Configuración | Un tramo de 60.00 m; idealización simplemente apoyada inferida de la disposición de apoyos |
| Ancho del tablero | 8.40 m |
| Tablero | Losa de concreto armado |
| Apoyo izquierdo | Dos apoyos fijos |
| Apoyo derecho | Dos apoyos móviles |
| Duración | 4 horas cronológicas (240 minutos) |
| Nivel | Intermedio–avanzado |
| Norma base asumida | Manual de Puentes MTC 2018 |
| Software | CSiBridge y hoja de cálculo para controles independientes |

> **Naturaleza de la sesión:** documento pedagógico aplicado a la geometría
> confirmada del Puente Agua Flor. Los parámetros espectrales, espesor de losa,
> peso de la armadura, propiedades de apoyos y dimensiones de asiento aún deben
> obtenerse de los estudios y planos aprobados.

### Relación con la sesión general

Esta sesión desarrolla el caso particular de un solo tramo y complementa la
[`sesión general para la superestructura reticulada`](sesion_espectro_respuesta_superestructura_puente_reticulado_agua_flor.md).
La presente versión profundiza en apoyos, fuerzas mínimas de conexión, movimiento
térmico, ancho de asiento y reparto de reacciones.

---

## 1. Propósito

Modelar y evaluar la respuesta sísmica de la superestructura reticulada del Puente
Agua Flor sin perder de vista una condición normativa fundamental: para un puente
convencional de un solo tramo, el MTC 2018 no exige un análisis sísmico global,
pero sí exige verificar las conexiones superestructura–estribo, los apoyos,
anclajes, topes, juntas y el ancho mínimo de asiento.

Por ello la clase separa dos niveles:

1. **Verificaciones normativas obligatorias:** fuerzas mínimas de unión, capacidad
   de apoyos y anclajes, desplazamiento disponible y longitud de asiento.
2. **Análisis espectral complementario:** modelo tridimensional para estudiar
   distribución de fuerzas, torsión, desplazamientos y demanda en miembros.

---

## 2. Resultados de aprendizaje

Al finalizar, el participante podrá:

1. Explicar por qué no se exige análisis sísmico global mínimo para un puente de
   un solo tramo y qué verificaciones permanecen obligatorias.
2. Representar los cuatro apoyos mediante grados de libertad y rigideces, sin
   depender de las etiquetas ambiguas “fijo” y “móvil”.
3. Determinar la trayectoria longitudinal y transversal de la fuerza sísmica.
4. Calcular el área del tablero y formular su peso y masa a partir del espesor.
5. Construir una fuente de masa sin duplicar el peso propio.
6. Definir un caso modal y casos espectrales longitudinal y transversal.
7. Aplicar correctamente el factor dimensional `g` en CSiBridge.
8. Comparar la demanda espectral de una unión con la fuerza mínima normativa.
9. Revisar fuerzas en cordones, diagonales, vigas de piso, arriostramientos y
   apoyos.
10. Verificar movimiento térmico, recorrido de apoyos móviles y ancho de asiento.

---

## 3. Secuencia didáctica

| Bloque | Tiempo | Actividad | Producto |
|---|---:|---|---|
| Apertura | 20 min | Presentación del caso y alcance normativo | Mapa de decisiones |
| Geometría y apoyos | 40 min | Idealización de los cuatro apoyos | Matriz de grados de libertad |
| Masa y espectro | 40 min | Cálculo paramétrico del tablero y función espectral | Tabla de masa y espectro |
| CSiBridge | 65 min | Construcción y ejecución guiada | Modelo modal/espectral |
| Resultados | 45 min | Reacciones, conexiones, miembros y asiento | Matriz de verificaciones |
| Evaluación | 30 min | Taller y preguntas de salida | Lista de control completa |

---

## 4. Datos del caso

### 4.1 Datos confirmados

| Símbolo | Descripción | Valor | Unidad | Fuente | Estado |
|---|---|---:|---|---|---|
| `n` | Número de tramos | 1 | — | Usuario | Confirmado |
| `L` | Luz del tramo | 60.00 | m | Usuario | Confirmado |
| `B` | Ancho total de tablero | 8.40 | m | Usuario | Confirmado |
| — | Sistema principal | Reticulado | — | Usuario | Confirmado |
| — | Tipo de tablero | Losa de concreto armado | — | Usuario | Confirmado |
| `N_f` | Apoyos fijos en extremo izquierdo | 2 | — | Usuario | Confirmado |
| `N_m` | Apoyos móviles en extremo derecho | 2 | — | Usuario | Confirmado |

### 4.2 Datos pendientes para el cálculo definitivo

| Categoría | Dato pendiente | Influencia |
|---|---|---|
| Peligro sísmico | `PGA`, `Ss`, `S1` | Ordenadas espectrales |
| Geotecnia | Clase de sitio, `Fpga`, `Fa`, `Fv` | Amplificación del sitio |
| Importancia | Crítico, esencial u otro | Criterios normativos |
| Geometría | Altura y panelización de armadura | Rigidez y modos |
| Geometría | Distancia transversal entre apoyos `s_b` | Torsión y reparto |
| Geometría | Esviaje `S` | Ancho de asiento y respuesta transversal |
| Losa | Espesor `t_s` | Peso, masa y rigidez |
| Losa | `f'_c`, `E_c`, peso unitario | Rigidez y masa |
| Acero | Secciones, `F_y`, `E_s`, densidad | Rigidez, masa y resistencia |
| Cargas | Asfalto, defensas, veredas y servicios | Masa permanente |
| Apoyos | Tipo, rigidez, capacidad y recorrido | Camino de carga |
| Uniones | Pernos, anclajes, placas y topes | Capacidad sísmica |
| Estribos | Ancho real de asiento y cajuela | Riesgo de descalce |

### 4.3 Sistema de coordenadas de la clase

Se adopta:

- `X`: longitudinal, de izquierda a derecha;
- `Y`: transversal;
- `Z`: vertical positiva hacia arriba.

Esta convención debe coincidir con el modelo o transformarse explícitamente.

---

## 5. Decisión normativa para un solo tramo

### 5.1 Regla principal

El artículo 2.6.5.4.2 del Manual de Puentes MTC 2018 establece que para puentes
de un solo tramo no se requiere análisis sísmico global, independientemente de la
zona sísmica.

Esto no significa que “el sismo no actúa”. Significa que la norma permite omitir
el análisis global siempre que se satisfagan las disposiciones mínimas de seguridad.

### 5.2 Verificaciones que permanecen vigentes

- fuerzas mínimas en la conexión entre superestructura y estribos;
- capacidad horizontal y vertical de los apoyos;
- placas, pernos y anclajes;
- topes y restrictores sísmicos;
- ancho mínimo de asiento;
- recorrido del apoyo móvil y de la junta;
- estabilidad contra pérdida de apoyo;
- transferencia continua de fuerza hasta la cimentación.

### 5.3 Uso del análisis espectral en esta clase

El análisis espectral se usa como herramienta complementaria para:

- conocer la distribución entre los dos apoyos fijos;
- evaluar el efecto torsional de la masa excéntrica;
- estimar fuerzas en arriostramientos y pórticos extremos;
- estudiar el movimiento relativo entre tablero y estribos;
- comparar la demanda calculada con el mínimo normativo;
- detectar vulnerabilidades de la armadura y sus conexiones.

La memoria final debe distinguir claramente:

```text
Exigencia mínima MTC 2018
        versus
evaluación dinámica adicional adoptada por el proyectista/propietario
```

---

## 6. Geometría básica del tablero

### 6.1 Área en planta

$$
A_{tab}=L B
$$

$$
A_{tab}=60.00(8.40)=504.00\;m^2
$$

Este valor está confirmado geométricamente, pero no determina por sí solo el peso
porque falta el espesor de la losa.

### 6.2 Volumen y peso de la losa

Para espesor uniforme `t_s`:

$$
V_s=504.00t_s
$$

$$
W_s=504.00t_s\gamma_c
$$

donde `γc` es el peso unitario del concreto.

Por unidad de longitud:

$$
w_s=B t_s\gamma_c=8.40t_s\gamma_c
$$

### 6.3 Ejemplo pedagógico, no dato del proyecto

Si únicamente para practicar se adopta:

$$
t_s=0.20\;m,\qquad \gamma_c=24\;kN/m^3
$$

entonces:

$$
w_s=8.40(0.20)(24)=40.32\;kN/m
$$

$$
W_s=40.32(60)=2419.20\;kN
$$

$$
m_s=\frac{2419.20}{9.80665}=246.69\;t
$$

> Este valor incluye solo la losa hipotética. No incluye armadura, vigas de piso,
> arriostramientos, asfalto, defensas, veredas ni servicios.

### 6.4 Peso permanente total

$$
W_{perm}=W_{losa}+W_{armadura}+W_{vigas\ de\ piso}+W_{arriostramientos}
+W_{asfalto}+W_{defensas}+W_{servicios}
$$

La fuerza mínima de conexión debe usar la carga permanente tributaria completa,
no únicamente el peso de la losa.

---

## 7. Interpretación de los cuatro apoyos

### 7.1 Nomenclatura

Se definen:

- `FI-1`: apoyo fijo izquierdo bajo la armadura 1;
- `FI-2`: apoyo fijo izquierdo bajo la armadura 2;
- `MD-1`: apoyo móvil derecho bajo la armadura 1;
- `MD-2`: apoyo móvil derecho bajo la armadura 2.

Sus coordenadas transversales deben tomarse de planos. Si la separación entre
apoyos es `s_b`, sus posiciones conceptuales son `Y=±s_b/2`.

### 7.2 La etiqueta no es suficiente

Un apoyo “fijo” normalmente restringe traslaciones y permite rotaciones, mientras
un apoyo “móvil” permite al menos el movimiento longitudinal. Sin embargo, el
comportamiento real depende del dispositivo:

- apoyo móvil unidireccional o guiado;
- apoyo móvil multidireccional;
- neopreno sin anclaje;
- apoyo pot, esférico o de deslizamiento;
- presencia de topes independientes;
- holgura antes de activar el tope;
- fricción de la superficie deslizante.

### 7.3 Matriz conceptual inicial

La siguiente tabla usa ejes globales y no reemplaza la ficha del fabricante:

| Apoyo | `UX` longitudinal | `UY` transversal | `UZ` vertical | `RX, RY, RZ` |
|---|---|---|---|---|
| `FI-1` | Restringido | Por confirmar | Restringido | Generalmente libres o elásticas |
| `FI-2` | Restringido | Por confirmar | Restringido | Generalmente libres o elásticas |
| `MD-1` | Libre o elástico | Por confirmar | Restringido | Generalmente libres o elásticas |
| `MD-2` | Libre o elástico | Por confirmar | Restringido | Generalmente libres o elásticas |

### 7.4 Dos variantes transversales que deben estudiarse

#### Variante A — apoyos móviles guiados longitudinalmente

Los apoyos derechos permiten `UX`, pero restringen `UY`. Los cuatro apoyos pueden
participar en el sismo transversal.

#### Variante B — apoyos móviles multidireccionales

Los apoyos derechos permiten `UX` y `UY`. La resistencia transversal se concentra
en los apoyos fijos o en topes independientes del extremo izquierdo.

Estas variantes producen reacciones y torsiones muy diferentes. La clase debe
ejecutar ambas como análisis de sensibilidad mientras no se disponga del detalle.

### 7.5 Posible sobrerrestricción

Dos apoyos completamente fijos en el mismo extremo pueden introducir redundancia
transversal. No necesariamente es incorrecto, pero debe comprobarse:

- compatibilidad de deformaciones;
- tolerancias de montaje;
- dilatación transversal del tablero;
- rigidez desigual de apoyos;
- reparto de fuerza entre armaduras;
- fuerzas por temperatura y retracción.

---

## 8. Camino de carga sísmica

### 8.1 Dirección longitudinal `X`

```text
masa del tablero y armadura
        ↓
vigas de piso y arriostramiento
        ↓
diafragma/pórtico extremo izquierdo
        ↓
FI-1 y FI-2
        ↓
estribo izquierdo y cimentación
```

En el modelo ideal, `MD-1` y `MD-2` no transmiten fuerza longitudinal si son
perfectamente móviles y sin fricción. En la realidad pueden transmitir fuerza por:

- fricción;
- rigidez del elastómero;
- topes;
- suciedad o bloqueo;
- desalineación;
- agotamiento del recorrido.

### 8.2 Dirección transversal `Y`

El camino depende de la variante de apoyo:

- variante A: participan los cuatro apoyos;
- variante B: participan principalmente `FI-1` y `FI-2` o topes del extremo fijo.

### 8.3 Reparto longitudinal simplificado

Si el tablero extremo se comporta rígidamente y los dos apoyos fijos tienen
rigideces `k_1` y `k_2`:

$$
H_1=\frac{k_1}{k_1+k_2}H_X
$$

$$
H_2=\frac{k_2}{k_1+k_2}H_X
$$

Solo si `k_1=k_2`, la geometría y la masa son simétricas y no existe torsión:

$$
H_1=H_2=\frac{H_X}{2}
$$

No debe imponerse un reparto 50/50 sin verificar estas condiciones.

---

## 9. Movimiento térmico como control del apoyo móvil

El recorrido longitudinal requerido no depende únicamente del sismo. Para una
variación uniforme de temperatura:

$$
\Delta_T=\alpha L\Delta T
$$

Ejemplo exclusivamente didáctico:

$$
\alpha=12\times10^{-6}/^{\circ}C,\qquad \Delta T=30^{\circ}C
$$

$$
\Delta_T=12\times10^{-6}(60)(30)=0.0216\;m=21.6\;mm
$$

El recorrido del apoyo y la junta debe considerar, según corresponda:

- temperatura positiva y negativa;
- retracción y fluencia del tablero;
- tolerancias de instalación;
- frenado;
- desplazamiento sísmico;
- movimiento irreversible o residual;
- margen de seguridad del dispositivo.

La posición de instalación del apoyo móvil debe verificarse para la temperatura
de montaje; no basta con comprobar el recorrido total del catálogo.

---

## 10. Ancho mínimo de asiento

El MTC 2018, artículo 2.6.5.4.4, establece un ancho empírico de asiento `N` y un
porcentaje dependiente de la zona sísmica. La ecuación del Manual utiliza `L` y
`H` en pies y entrega `N` en pulgadas:

$$
N=(8+0.02L+0.08H)(1+0.000125S^2)
$$

donde:

- `L`: longitud del tablero hasta la junta; para este caso, `60 m`;
- `H=0` para un puente de un solo tramo;
- `S`: esviaje del apoyo en grados, pendiente de confirmar.

### 10.1 Demostración para puente recto

Asumiendo solo para la demostración `S=0`:

$$
L=60.00\;m=196.85\;ft
$$

$$
N_{base}=8+0.02(196.85)=11.94\;in=303\;mm
$$

Si el porcentaje normativo aplicable fuera `150 %`:

$$
N_{req}=1.50(11.94)=17.91\;in\approx455\;mm
$$

> **No adoptar todavía 455 mm como valor de diseño.** Faltan la zona sísmica,
> el esviaje, la geometría real de la cajuela y los movimientos adicionales.
> Además, el ancho total debe permitir el desplazamiento calculado y los efectos
> de temperatura, retracción y demás movimientos aplicables.

---

## 11. Espectro de respuesta del sitio

### 11.1 Datos requeridos

| Parámetro | Descripción | Estado Agua Flor |
|---|---|---|
| `PGA` | Aceleración pico en roca de referencia | Pendiente |
| `Ss` | Aceleración espectral a 0.2 s | Pendiente |
| `S1` | Aceleración espectral a 1.0 s | Pendiente |
| `Fpga` | Factor de sitio para período cero | Pendiente |
| `Fa` | Factor de sitio para período corto | Pendiente |
| `Fv` | Factor de sitio para período largo | Pendiente |

No se deben reutilizar los parámetros de Molinohuaico.

### 11.2 Cálculo general

$$
A_s=F_{pga}PGA
$$

$$
S_{DS}=F_aS_s
$$

$$
S_{D1}=F_vS_1
$$

$$
T_s=\frac{S_{D1}}{S_{DS}},\qquad T_0=0.20T_s
$$

$$
C_{sm}(T)=
\begin{cases}
A_s+(S_{DS}-A_s)T/T_0, & 0\le T<T_0\\
S_{DS}, & T_0\le T\le T_s\\
S_{D1}/T, & T>T_s
\end{cases}
$$

### 11.3 Controles

$$
C_{sm}(0)=A_s
$$

$$
C_{sm}(T_0)=C_{sm}(T_s)=S_{DS}
$$

$$
C_{sm}(1.0)=S_{D1}
$$

---

## 12. Fuerza mínima de la conexión

Para un puente de un solo tramo, la mínima solicitación de diseño en una unión
superestructura–subestructura, en una dirección restringida, no debe ser menor
que el producto del coeficiente de aceleración `As` por la carga permanente
tributaria.

### 12.1 Dirección longitudinal

Como la línea izquierda es la línea fija:

$$
H_{X,min}=A_sW_{perm,total}
$$

Este valor se distribuye entre `FI-1` y `FI-2` según rigidez, geometría y torsión.

### 12.2 Dirección transversal

Si un apoyo está restringido transversalmente, su fuerza mínima se relaciona con
la reacción permanente tributaria que soporta:

$$
H_{Y,min,i}=A_sR_{perm,i}
$$

La lista de apoyos que participan depende de si `MD-1` y `MD-2` son guiados o
multidireccionales.

### 12.3 Comparación con la respuesta espectral

La Tabla 2.4.3.11.6.1-2 del MTC asigna a la unión
superestructura–estribo:

$$
R_{union}=0.8
$$

Por tanto:

$$
E_{union}=\frac{E_{el}}{0.8}=1.25E_{el}
$$

La demanda de diseño de la unión será, conceptualmente:

$$
H_{diseño}=\max\left(H_{min},\frac{E_{el}}{0.8}\right)
$$

La expresión debe evaluarse separadamente para cada dirección y cada unión.

### 12.4 Ejemplo didáctico limitado a la losa

Usando únicamente la losa hipotética de la Sección 6 y suponiendo `As=0.33`:

$$
H_{X,min,losa}=0.33(2419.20)=798.34\;kN
$$

Si dos apoyos idénticos comparten la demanda:

$$
H_{FI-1}=H_{FI-2}=399.17\;kN
$$

Este resultado **no es la fuerza de diseño del Puente Agua Flor**, porque faltan
el peso total permanente, el `As` real, la rigidez de apoyos y la torsión.

---

## 13. Idealización tridimensional en CSiBridge

### 13.1 Componentes

- cordones superiores e inferiores: elementos `Frame`;
- diagonales y montantes: elementos `Frame`;
- vigas de piso y largueros: elementos `Frame`;
- arriostramiento superior e inferior: elementos `Frame`;
- losa de 8.40 m: elementos `Shell`;
- diafragmas o pórticos extremos: representación explícita;
- apoyos: propiedades `Bearing` o `Link/Support`;
- estribos: apoyos de base o modelo de subestructura, según alcance.

Una armadura puede modelarse con objetos generales de barras y áreas; no es
obligatorio forzarla dentro de una plantilla paramétrica de viga del Bridge Wizard.

### 13.2 Mallado de la losa

El mallado debe coincidir con:

- vigas de piso;
- largueros;
- líneas de armadura;
- diafragmas extremos;
- ubicación de masas y barreras.

Un mallado excesivamente grueso puede ocultar torsión y distribución transversal.
Uno excesivamente fino puede introducir numerosos modos locales que dificultan
la convergencia sin mejorar la respuesta global.

### 13.3 Acción compuesta

Debe confirmarse cómo la losa se conecta a las vigas de piso y largueros. No se
adoptará acción compuesta total sin verificar el detalle. Para el estado terminado:

- si existe unión efectiva, modelar compatibilidad correspondiente;
- si no existe acción compuesta longitudinal, evitar sobre-rigidizar;
- considerar fisuración de la losa cuando afecte significativamente la rigidez.

### 13.4 Liberaciones

No liberar automáticamente todos los momentos. Comparar:

1. armadura ideal articulada;
2. modelo con continuidad real de cordones y vigas de piso;
3. sensibilidad a excentricidades de cartelas.

---

## 14. Definición de los apoyos en CSiBridge

La ayuda oficial permite definir cada uno de los seis grados de libertad como
fijo, libre o parcialmente restringido. Para análisis lineal espectral se utilizan
las propiedades lineales del apoyo.

### 14.1 Propiedades sugeridas para estudio

Crear propiedades separadas:

```text
BRG_FIJO_IZQ
BRG_MOVIL_DER_GUIADO
BRG_MOVIL_DER_LIBRE
```

### 14.2 Ejes locales

Antes de asignar rigideces:

1. mostrar los ejes locales del `Link`;
2. identificar cuál eje es longitudinal;
3. identificar cuál eje es transversal;
4. comprobarlo con una carga unitaria;
5. documentar la transformación entre ejes locales y globales.

Un apoyo móvil con su eje local rotado 90° puede liberar la dirección equivocada.

### 14.3 Rigidez finita frente a restricción perfecta

Para el modelo inicial pueden compararse:

- restricción ideal;
- rigidez horizontal del apoyo real;
- fricción linealizada;
- topes con rigidez equivalente activada.

El análisis espectral lineal no representa correctamente apertura de holguras,
deslizamiento con fricción, impacto, levantamiento o contacto unilateral. Si estos
efectos gobiernan, se requiere un análisis no lineal complementario.

---

## 15. Fuente de masa específica

### 15.1 Componentes

| Componente | Inclusión | Método posible |
|---|---|---|
| Losa de concreto | Sí | Densidad del material de `Shell` |
| Armaduras principales | Sí | Densidad del acero de `Frame` |
| Vigas de piso/largueros | Sí | Densidad del acero |
| Arriostramientos | Sí | Densidad del acero |
| Asfalto | Sí | Patrón `DW` o masa de área |
| Defensas/veredas | Sí | Carga lineal convertida a masa |
| Servicios | Sí | Línea, área o nudos tributarios |
| Carga viva | Según criterio aprobado | No incluir automáticamente 100 % |

### 15.2 Configuración

En CSiBridge, la fuente de masa puede combinar:

- masa propia y masa adicional de elementos;
- patrones de carga especificados.

Si se usan ambos métodos, verificar que el peso propio no se duplique. CSiBridge
divide internamente los patrones de peso seleccionados entre `g`; no se introduce
`g` como multiplicador del patrón en la fuente de masa.

### 15.3 Control manual

$$
m_{manual}=\frac{W_{perm}}{g}
$$

Comparar con la tabla de masa ensamblada de CSiBridge y explicar toda diferencia.

---

## 16. Caso modal

### 16.1 Configuración

- comenzar con análisis `Eigen`;
- incluir suficientes modos para estabilizar resultados;
- animar todos los modos relevantes;
- repetir con más modos hasta lograr convergencia de reacciones y desplazamientos.

### 16.2 Modos esperados

En una armadura de 60 m pueden aparecer:

- flexión vertical global;
- traslación transversal;
- torsión del tablero;
- deformación longitudinal condicionada por apoyos;
- distorsión entre planos de armadura;
- modos locales de arriostramientos o losa.

El primer modo no necesariamente será el más importante para la reacción en un
apoyo o para una conexión extrema.

### 16.3 Registro

| Modo | `T` (s) | Descripción | Masa `X` | Masa `Y` | Masa `Z` | ¿Global/local? |
|---:|---:|---|---:|---:|---:|---|
| 1 | — | — | — | — | — | — |
| 2 | — | — | — | — | — | — |
| 3 | — | — | — | — | — | — |

---

## 17. Función y casos de espectro

### 17.1 Función normalizada

CSiBridge considera normalizadas las aceleraciones de la función. Nombrar:

```text
RS_MTC2018_AGUA_FLOR_EL_5PCT
```

Incluir `T=0` y extender la tabla por encima del período modal máximo esperado.

### 17.2 Factor de escala

Si `Csm` se introduce como múltiplo adimensional de `g`:

$$
SF=g
$$

| Sistema | `Scale Factor` elástico |
|---|---:|
| `kN–m–s` | `9.80665` |
| `N–mm–s` | `9806.65` |

### 17.3 Casos

```text
RSX_EL -> aceleración longitudinal X, SF=g
RSY_EL -> aceleración transversal Y, SF=g
```

Utilizar el caso modal validado y combinación modal `CQC` cuando existan modos
próximos.

### 17.4 Direcciones

Para la evaluación complementaria:

$$
E_1=|E_X|+0.30|E_Y|
$$

$$
E_2=0.30|E_X|+|E_Y|
$$

El `30 %` corresponde a direcciones horizontales ortogonales; no es una regla
automática para construir un espectro vertical.

---

## 18. Procedimiento guiado en CSiBridge

### Paso 1 — Geometría

1. Definir unidades.
2. Crear ejes `X=0` y `X=60 m`.
3. Ubicar los planos de armadura con la separación real.
4. Crear paneles según planos.
5. Incorporar losa de 8.40 m y elementos transversales.

### Paso 2 — Materiales y secciones

1. Definir concreto y acero con propiedades de proyecto.
2. Asignar secciones a cada familia.
3. Revisar densidad de masa y peso.

### Paso 3 — Conectividad

1. Comprobar coincidencia de nudos.
2. Definir offsets y brazos rígidos solo donde correspondan.
3. Revisar liberaciones y ejes locales.

### Paso 4 — Apoyos

1. Crear los dos apoyos fijos izquierdos.
2. Crear variante guiada y libre para los móviles derechos.
3. Mostrar ejes locales.
4. Ejecutar casos unitarios `FX=1` y `FY=1` para comprobar restricciones.

### Paso 5 — Masa

1. Crear fuente de masa.
2. Evitar duplicación entre densidad y patrones.
3. Comparar masa ensamblada con cálculo manual.

### Paso 6 — Modal

1. Crear caso `MODAL_EIGEN`.
2. Ejecutarlo solo.
3. Animar deformadas.
4. Corregir mecanismos o modos espurios.

### Paso 7 — Espectro

1. Definir función normalizada MTC.
2. Crear `RSX_EL` y `RSY_EL`.
3. Asignar `SF=g` en unidades activas.
4. Usar `CQC` y amortiguamiento sustentado.

### Paso 8 — Análisis de sensibilidad

Ejecutar:

- modelo con móviles guiados;
- modelo con móviles multidireccionales;
- rigidez ideal y rigidez real de apoyos;
- diferentes números de modos.

### Paso 9 — Resultados

Exportar:

- períodos y masa participante;
- reacciones por apoyo;
- desplazamientos por extremo;
- fuerzas de `Link`;
- axial y flexión de miembros;
- fuerzas en diafragmas y arriostramientos.

---

## 19. Resultados y verificaciones

### 19.1 Reacciones longitudinales

| Apoyo | `RSX_EL` | `E_el/0.8` | Mínimo normativo | Demanda adoptada |
|---|---:|---:|---:|---:|
| `FI-1` | — | — | — | — |
| `FI-2` | — | — | — | — |
| `MD-1` | — | — | No aplicable si libre | — |
| `MD-2` | — | — | No aplicable si libre | — |

Si `MD-1` o `MD-2` muestra reacción longitudinal importante en el modelo ideal
móvil, revisar ejes, rigidez, constraints y conectividad.

### 19.2 Reacciones transversales

Preparar dos tablas, una por variante. Comparar:

- reparto entre extremos;
- torsión;
- máximo por apoyo;
- demanda en topes;
- compatibilidad con anclajes.

### 19.3 Miembros de la armadura

Hasta justificar un mecanismo dúctil específico, revisar los miembros con efectos
elásticos, sin aplicar indiscriminadamente un `R` de subestructura:

- cordón superior: compresión y pandeo;
- cordón inferior: tracción e inversión de esfuerzo;
- diagonales: tracción/compresión y esbeltez;
- montantes: axial y flexión secundaria;
- vigas de piso: flexión, corte y transferencia transversal;
- arriostramientos: fuerza axial y conexiones;
- cartelas: equilibrio, bloque de cortante y pandeo.

### 19.4 Desplazamientos

| Punto | `UX` | `UY` | Uso |
|---|---:|---:|---|
| Extremo fijo | — | — | Deformación de apoyo/topes |
| Extremo móvil | — | — | Recorrido y junta |
| Centro de luz | — | — | Respuesta global |

Combinar el movimiento sísmico con los demás movimientos según el criterio
normativo y de dispositivo; no sumar máximos incompatibles sin justificación.

### 19.5 Levantamiento

Revisar la reacción vertical mínima en los cuatro apoyos bajo Evento Extremo I.
Si aparece tracción:

- confirmar si el apoyo puede tomar levantamiento;
- revisar anclajes;
- considerar contacto unilateral;
- reconocer que un espectro lineal no modela apertura y reimpacto.

---

## 20. Combinaciones de Evento Extremo I

La combinación definitiva debe tomarse de la tabla contractual aplicable. La
estructura conceptual es:

$$
Q=\sum\eta_i\gamma_iQ_i
$$

Evaluar ambos signos sísmicos:

$$
Q_{+}=Q_{perm}+E_Q
$$

$$
Q_{-}=Q_{perm}-E_Q
$$

Esto es importante para:

- diagonales con inversión de esfuerzo;
- cordones;
- levantamiento en apoyos;
- apertura y cierre de juntas;
- fuerzas alternantes en anclajes.

---

## 21. Verificaciones independientes

### 21.1 Masa

$$
\varepsilon_m=\frac{|m_{CSI}-m_{manual}|}{m_{manual}}100\%
$$

Explicar la diferencia componente por componente.

### 21.2 Reacción vertical permanente

Para un sistema simétrico ideal:

$$
R_{extremo}=\frac{W_{perm}}{2}
$$

y, si los dos apoyos de cada extremo son equivalentes:

$$
R_{apoyo}=\frac{W_{perm}}{4}
$$

Las excentricidades, el ancho real y la rigidez del tablero pueden modificar este
reparto.

### 21.3 Reparto longitudinal

Comprobar:

$$
H_{FI-1}+H_{FI-2}\approx H_X
$$

y que los apoyos móviles no reciban fuerza longitudinal ideal no prevista.

### 21.4 Período aproximado

Aplicar una carga estática horizontal `F` y medir `Δ`:

$$
K_{eq}=\frac{F}{\Delta}
$$

$$
T_{aprox}=2\pi\sqrt{\frac{m_{eq}}{K_{eq}}}
$$

Comparar con el modo dominante de CSiBridge.

### 21.5 Ancho de asiento

Comparar:

- ancho real disponible;
- ancho empírico MTC;
- desplazamiento sísmico;
- desplazamiento térmico;
- tolerancias y movimientos diferidos.

---

## 22. Taller aplicado

### Ejercicio 1 — Peso de la losa

Calcular `W_s` para `t_s=0.22 m` y `γc=24 kN/m³`.

**Solución:**

$$
W_s=60(8.40)(0.22)(24)=2661.12\;kN
$$

### Ejercicio 2 — Movimiento térmico

Calcular el movimiento para `α=12×10⁻⁶/°C` y `ΔT=40°C`.

**Solución:**

$$
\Delta_T=12\times10^{-6}(60)(40)=28.8\;mm
$$

### Ejercicio 3 — Reparto entre apoyos fijos

Si `H_X=1200 kN`, `k_1=600 MN/m` y `k_2=400 MN/m`:

$$
H_1=\frac{600}{1000}(1200)=720\;kN
$$

$$
H_2=\frac{400}{1000}(1200)=480\;kN
$$

### Ejercicio 4 — Demanda de conexión

Si `E_el=900 kN` y `H_min=800 kN`:

$$
E_{union}=900/0.8=1125\;kN
$$

$$
H_{diseño}=\max(800,1125)=1125\;kN
$$

### Ejercicio 5 — Diagnóstico del modelo

En `RSX_EL`, un apoyo móvil derecho recibe 35 % del cortante longitudinal. Enumerar
posibles causas:

- eje local mal orientado;
- rigidez longitudinal asignada;
- restricción duplicada;
- constraint rígido hacia el estribo;
- fricción o tope activado;
- apoyo modelado como guiado en la dirección incorrecta.

---

## 23. Evaluación

### 23.1 Preguntas de salida

1. ¿Qué exige el MTC para un puente de un solo tramo aunque no se realice análisis
   sísmico global?
2. ¿Qué diferencia existe entre un apoyo móvil guiado y uno multidireccional?
3. ¿Por qué los dos apoyos fijos no necesariamente comparten 50/50?
4. ¿Qué peso tributario se usa en la fuerza mínima longitudinal?
5. ¿Por qué `R=0.8` aumenta la demanda de la unión?
6. ¿Qué error se produce al usar `Scale Factor=1` con un espectro normalizado?
7. ¿Cómo se verifica que el apoyo móvil esté liberado en la dirección correcta?

### 23.2 Rúbrica

| Criterio | Peso |
|---|---:|
| Matriz de apoyos y ejes locales | 20 % |
| Fuente de masa | 15 % |
| Función y escala espectral | 15 % |
| Modelo modal | 15 % |
| Fuerza mínima y `R` de unión | 20 % |
| Ancho de asiento y movimientos | 15 % |

---

## 24. Lista de control

### Geometría

- [ ] Luz de 60.00 m verificada en el modelo.
- [ ] Ancho total de 8.40 m verificado.
- [ ] Separación real entre armaduras y apoyos incorporada.
- [ ] Espesor real de losa ingresado.
- [ ] Esviaje confirmado.

### Apoyos

- [ ] `FI-1` y `FI-2` definidos por grados de libertad.
- [ ] `MD-1` y `MD-2` clasificados como guiados o multidireccionales.
- [ ] Ejes locales mostrados y documentados.
- [ ] Rigideces, capacidad y recorrido tomados de datos aprobados.
- [ ] Topes y holguras identificados.

### Masa y análisis

- [ ] Peso de losa, acero, asfalto y accesorios incluidos.
- [ ] No existe duplicación entre masa propia y patrones.
- [ ] Modos animados y clasificados.
- [ ] Resultados convergen al aumentar modos.
- [ ] Espectro usa parámetros propios de Agua Flor.
- [ ] `Scale Factor` tiene unidades de aceleración correctas.

### Verificación

- [ ] Fuerza mínima longitudinal calculada con todo `Wperm`.
- [ ] Fuerzas transversales asignadas solo a apoyos restringidos.
- [ ] `Eel/0.8` comparado con el mínimo normativo.
- [ ] Fuerzas en miembros revisadas con criterio elástico.
- [ ] Recorrido térmico y sísmico verificado.
- [ ] Ancho de asiento real comparado con el requerido.
- [ ] Levantamiento y anclajes revisados.

---

## 25. Conclusiones

1. El Puente Agua Flor es un puente de un solo tramo de 60 m; por el MTC 2018,
   no requiere análisis sísmico global como exigencia mínima.
2. La seguridad sísmica no se omite: deben diseñarse las conexiones, apoyos,
   anclajes, topes, juntas y asiento.
3. En dirección longitudinal, la demanda se conduce principalmente a los dos
   apoyos fijos del extremo izquierdo.
4. En dirección transversal, el camino depende de si los apoyos móviles son
   guiados o multidireccionales; este dato debe confirmarse.
5. El tablero posee un área confirmada de `504 m²`; su masa definitiva depende del
   espesor y de las demás cargas permanentes.
6. La demanda de la unión superestructura–estribo se compara con el mínimo
   normativo y con `Eel/0.8`; gobierna la mayor.
7. El análisis espectral complementario es valioso para distribuir fuerzas,
   estudiar torsión y controlar desplazamientos, pero debe presentarse con su
   carácter adicional.
8. La validación requiere controles independientes de masa, reacciones, período,
   movimientos y ancho de asiento.

### Estado de la aplicación

- **Resultado principal:** procedimiento específico definido para la geometría y
  disposición general de apoyos de Agua Flor.
- **Cumplimiento:** no evaluable todavía; faltan demandas y capacidades reales.
- **Supuesto crítico:** comportamiento direccional de los apoyos móviles.
- **Verificación pendiente:** parámetros sísmicos, espesor de losa, peso total,
  apoyos, esviaje y cajuela.
- **Siguiente paso:** completar la matriz de propiedades de `FI-1`, `FI-2`, `MD-1`
  y `MD-2` y obtener el estudio sísmico del emplazamiento.

---

## 26. Referencias

1. **Ministerio de Transportes y Comunicaciones.** *Manual de Puentes MTC 2018*:
   artículos 2.4.3.11.6 a 2.4.3.11.8 y 2.6.5.4.1 a 2.6.5.4.4.
   Archivo local: [`../normativa/manual_puentes_MTC_2018.pdf`](../normativa/manual_puentes_MTC_2018.pdf).
2. **Computers and Structures, Inc.**
   [Define Response Spectrum Functions](https://docs.csiamerica.com/help-files/csibridge/Loads_tab/Functions/Response_Spectrum/Define_Response_Spectrum_Functions.htm).
3. **Computers and Structures, Inc.**
   [Mass Source](https://docs.csiamerica.com/help-files/csibridge/Advanced_tab/Define_panel/mass_source.htm).
4. **Computers and Structures, Inc.**
   [Define Bridge Bearings](https://docs.csiamerica.com/help-files/csibridge/Components_tab/Substructure_Item_panel/Define_Bridge_Bearings_Form.htm).
5. **Computers and Structures, Inc.**
   [Link/Support Properties](https://docs.csiamerica.com/help-files/csibridge/Components_tab/Properties_Type_panel/Link_Support_Properties/Link_Support_Properties.htm).

---

*Sesión pedagógica específica para el Puente Agua Flor. No sustituye planos,
estudio sísmico, fichas de apoyo ni memoria de cálculo aprobados.*

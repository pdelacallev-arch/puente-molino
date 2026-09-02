# Sesión de clase: Espectro de respuesta sísmica para CSiBridge
## Aplicación a la superestructura reticulada del Puente Agua Flor — Chanchamayo, Junín

---

## 0. Ficha de la sesión

| Campo | Descripción |
|---|---|
| Tema | Análisis sísmico espectral de una superestructura reticulada en CSiBridge |
| Caso de aplicación | Puente Agua Flor, Chanchamayo, Junín |
| Duración sugerida | 4 horas cronológicas (240 minutos) |
| Nivel | Intermedio–avanzado |
| Modalidad | Exposición, demostración guiada y taller de modelación |
| Software | CSiBridge; hoja de cálculo o Python para verificación independiente |
| Norma base asumida | Manual de Puentes MTC 2018 |
| Estado de los datos | Metodología completa; parámetros sísmicos y geometría del puente pendientes de documentación del proyecto |

> **Alcance:** esta sesión desarrolla el procedimiento para construir, introducir,
> ejecutar y verificar un espectro de respuesta aplicado a una armadura metálica de
> puente. No constituye por sí sola la memoria de cálculo definitiva del Puente Agua
> Flor. Los parámetros de peligro sísmico deben reemplazarse por los del estudio de
> peligro sísmico y geotécnico aprobado para el emplazamiento.

---

## 1. Propósito y resultados de aprendizaje

### 1.1 Propósito

Comprender cómo la aceleración del terreno se convierte en fuerzas inerciales,
desplazamientos, reacciones y esfuerzos en la superestructura de un puente
reticulado, y cómo implementar el proceso de manera trazable en CSiBridge sin
aplicar indiscriminadamente un único factor de modificación de respuesta `R` a
toda la estructura.

### 1.2 Resultados de aprendizaje

Al finalizar la sesión, el participante será capaz de:

1. Identificar si el análisis sísmico global es exigible según el número de tramos,
   zona sísmica, importancia y regularidad del puente.
2. Organizar los parámetros `PGA`, `Ss`, `S1`, `Fpga`, `Fa` y `Fv` provenientes
   del estudio de peligro sísmico y de la clasificación del sitio.
3. Calcular `As`, `SDS`, `SD1`, `T0` y `Ts` y construir el espectro elástico
   `Csm(T)` del MTC 2018.
4. Explicar la diferencia entre espectro elástico, fuerzas de diseño modificadas
   y verificaciones de conexiones.
5. Idealizar una armadura metálica, tablero, arriostramientos, apoyos y fuente de
   masa para un análisis modal tridimensional.
6. Definir una función espectral normalizada y casos de respuesta espectral en
   CSiBridge con factores de escala dimensionalmente correctos.
7. Combinar modos mediante `CQC` y direcciones mediante la regla `100 % + 30 %`.
8. Revisar fuerzas axiales de cordones y diagonales, fuerzas en diafragmas,
   reacciones en apoyos, desplazamientos de juntas y ancho de asiento.
9. Ejecutar controles independientes de masa, período, cortante basal, equilibrio,
   deformada y orden de magnitud.
10. Documentar datos confirmados, supuestos y verificaciones pendientes.

### 1.3 Prerrequisitos

- Estática y dinámica estructural básica.
- Conceptos de masa, rigidez, período, modo y amortiguamiento.
- Comportamiento de armaduras: cordones, diagonales, montantes y nudos.
- Manejo básico de CSiBridge o SAP2000.
- Lectura de planos y conocimiento de sistemas de apoyo de puentes.

---

## 2. Organización pedagógica

| Bloque | Tiempo | Actividad | Evidencia de aprendizaje |
|---|---:|---|---|
| 1 | 20 min | Contexto, alcance y puerta de aplicabilidad normativa | Decisión: ¿se requiere análisis global? |
| 2 | 40 min | Fundamentos del espectro y cálculo por tramos | Tabla `T–Csm` verificada |
| 3 | 40 min | Idealización sísmica de la armadura y fuente de masa | Esquema del modelo y lista de masas |
| 4 | 60 min | Implementación guiada en CSiBridge | Función, caso modal y casos espectrales |
| 5 | 50 min | Interpretación, aplicación de `R` y verificaciones | Matriz componente–demanda–criterio |
| 6 | 30 min | Taller, evaluación y cierre | Lista de control firmada |

---

## 3. Caso de estudio: Puente Agua Flor

### 3.1 Información disponible

La denominación y el tipo estructural se toman de la solicitud del usuario. Una
fuente pública del Estado ubica el centro poblado o anexo Agua Flor en el distrito
de San Ramón, provincia de Chanchamayo, región Junín. Esa fuente no documenta la
geometría ni los parámetros de diseño del puente.

| Categoría | Dato | Estado | Uso en esta sesión |
|---|---|---|---|
| Identificación | Puente Agua Flor | Confirmado por el usuario | Nombre del caso |
| Ubicación general | Chanchamayo, Junín | Confirmado por el usuario | Contexto regional |
| Entorno local | Anexo Agua Flor, distrito de San Ramón | Referencia pública; confirmar con planos | Contexto, no cálculo |
| Sistema resistente | Superestructura reticulada | Confirmado por el usuario | Base de idealización |
| Número de tramos | No disponible | Pendiente | Define exigencia y método mínimo |
| Luz o luces | No disponible | Pendiente | Controla masa, rigidez y períodos |
| Ancho del tablero | No disponible | Pendiente | Controla masa y modos torsionales |
| Tipo de tablero | No disponible | Pendiente | Controla rigidez y acción compuesta |
| Disposición de apoyos | No disponible | Pendiente | Controla camino de carga sísmica |
| Categoría de importancia | No disponible | Pendiente | Controla método y `R` de subestructura |
| `PGA`, `Ss`, `S1` | No disponibles | Pendiente | Construcción del espectro |
| Clase de sitio | No disponible | Pendiente | Factores `Fpga`, `Fa`, `Fv` |
| Amortiguamiento | No confirmado | Pendiente | Entrada del caso espectral |

### 3.2 Datos indispensables antes del diseño definitivo

1. Coordenadas del eje del puente.
2. Estudio de peligro sísmico o valores mapeados aprobados: `PGA`, `Ss`, `S1`.
3. Perfil geotécnico y clasificación de sitio mediante `Vs30`, `N-SPT` o `Su`.
4. Número de tramos, continuidad y longitud de cada tramo.
5. Planta, elevación y sección transversal de la armadura.
6. Secciones y materiales de cordones, diagonales, montantes, vigas de piso,
   largueros y arriostramientos.
7. Espesor, material y forma de vinculación del tablero.
8. Inventario de cargas permanentes.
9. Tipo, ubicación, orientación y propiedades de apoyos y topes.
10. Categoría de importancia y criterios particulares del propietario.

> **Regla de trazabilidad:** ningún parámetro sísmico del Puente Molinohuaico debe
> transferirse al Puente Agua Flor. Cada puente requiere sus propios datos de peligro,
> suelo, geometría, importancia y sistema resistente.

---

## 4. Puerta de aplicabilidad normativa

Antes de abrir CSiBridge debe responderse la siguiente pregunta:

```text
¿El Puente Agua Flor tiene un solo tramo?
|
+-- Sí --> El MTC 2018 no exige análisis sísmico global para un puente
|          convencional de un solo tramo.
|          Sí exige fuerzas mínimas en conexiones superestructura–estribo,
|          diseño de apoyos/restrictores y ancho mínimo de asiento.
|
+-- No --> Clasificar zona sísmica, importancia, regularidad y número de tramos.
           Seleccionar UL, SM, MM o TH según la tabla normativa.
```

### 4.1 Puente de un solo tramo

El artículo 2.6.5.4.2 del MTC 2018 indica que no se requiere análisis sísmico
global para puentes de un solo tramo, independientemente de la zona sísmica.
Sin embargo, deben verificarse:

- conexión entre superestructura y estribos;
- apoyos y sus anclajes;
- topes o restrictores sísmicos;
- juntas;
- ancho mínimo de asiento;
- estabilidad frente a pérdida de apoyo;
- fuerzas mínimas establecidas para la dirección restringida.

Un análisis espectral puede realizarse como evaluación adicional, por requerimiento
del propietario, por irregularidades, para estudiar desplazamientos o para diseñar
dispositivos; no debe presentarse automáticamente como exigencia mínima del MTC.

### 4.2 Puente de múltiples tramos

Para puentes multitramos se emplea la Tabla 2.6.5.4.3.1-1 del MTC 2018. El método
mínimo depende de:

- zona sísmica;
- puente regular o irregular;
- categoría: crítico, esencial u otro;
- número y relación de luces;
- curvatura y variación de rigideces.

Una superestructura reticulada tridimensional con acoplamiento longitudinal,
transversal y torsional suele justificar el método espectral multimodal `MM`, aun
cuando un método más simple pudiera ser el mínimo para una configuración regular.

### 4.3 Alcance de la presente sesión

La demostración adopta el método espectral multimodal porque permite enseñar el
flujo completo y es adecuado para capturar:

- traslación longitudinal del tablero;
- traslación transversal;
- torsión global;
- deformación lateral de los planos de armadura;
- participación de pórticos transversales y arriostramientos;
- interacción entre tablero, vigas de piso y apoyos.

---

## 5. Fundamento físico

### 5.1 ¿De dónde proviene la fuerza sísmica?

El terreno impone una aceleración en la base. La masa del puente desarrolla fuerzas
de inercia que deben encontrar un camino continuo hasta la cimentación:

```text
masa del tablero y armadura
        ↓
vigas de piso / largueros / diafragmas
        ↓
planos de armadura y arriostramientos
        ↓
apoyos, topes y anclajes
        ↓
estribos o pilares
        ↓
cimentación y terreno
```

En forma conceptual:

$$
F_I(t)=-M\,\ddot u_g(t)
$$

donde:

- `M` es la matriz de masa;
- `\ddot u_g(t)` es la aceleración del terreno;
- el signo negativo expresa la oposición inercial al movimiento impuesto.

### 5.2 Ecuación de movimiento

Para un sistema lineal de múltiples grados de libertad:

$$
M\ddot u+C\dot u+Ku=-M r\ddot u_g(t)
$$

donde:

- `K` es la matriz de rigidez;
- `C` es la matriz de amortiguamiento;
- `r` es el vector de influencia de la dirección excitada;
- `u`, `\dot u` y `\ddot u` son desplazamiento, velocidad y aceleración relativos.

### 5.3 Problema modal

Los modos y frecuencias naturales se obtienen de:

$$
\left(K-\omega_n^2 M\right)\phi_n=0
$$

y el período modal es:

$$
T_n=\frac{2\pi}{\omega_n}
$$

El espectro entrega la máxima respuesta de un oscilador con período `T_n` y un
amortiguamiento especificado. No entrega una historia temporal ni conserva la
simultaneidad exacta de máximos.

### 5.4 Participación modal

Para una dirección de excitación, el factor de participación del modo `n` puede
expresarse como:

$$
\Gamma_n=\frac{\phi_n^T M r}{\phi_n^T M\phi_n}
$$

La masa modal efectiva permite saber cuánto de la masa total participa en cada
modo. En un puente reticulado no basta con observar únicamente el primer modo:
pueden existir modos torsionales o de distorsión con participación relevante en
reacciones, arriostramientos y conexiones aunque su masa global parezca menor.

---

## 6. Construcción del espectro elástico MTC 2018

### 6.1 Parámetros de entrada

| Símbolo | Descripción | Fuente para el diseño real |
|---|---|---|
| `PGA` | Aceleración pico del terreno en sitio de referencia | Mapas o estudio de peligro sísmico |
| `Ss` | Aceleración espectral a `T = 0.2 s` | Mapas o estudio de peligro sísmico |
| `S1` | Aceleración espectral a `T = 1.0 s` | Mapas o estudio de peligro sísmico |
| `Fpga` | Factor de sitio para período cero | Clase de sitio y `PGA` |
| `Fa` | Factor de sitio para período corto | Clase de sitio y `Ss` |
| `Fv` | Factor de sitio para período largo | Clase de sitio y `S1` |
| `ξ` | Fracción de amortiguamiento crítico | Norma, material y sistema |

El procedimiento general del MTC considera 5 % de amortiguamiento para los mapas
y el espectro base. Si el sistema real requiere otro amortiguamiento, la modificación
debe sustentarse y ser compatible con la norma y con el modelo.

### 6.2 Coeficientes ajustados por sitio

$$
A_s=F_{pga}\,PGA
$$

$$
S_{DS}=F_a\,S_s
$$

$$
S_{D1}=F_v\,S_1
$$

### 6.3 Períodos de transición

$$
T_s=\frac{S_{D1}}{S_{DS}}
$$

$$
T_0=0.20T_s
$$

### 6.4 Función por tramos

$$
C_{sm}(T)=
\begin{cases}
A_s+\left(S_{DS}-A_s\right)\dfrac{T}{T_0}, & 0\leq T<T_0\\[6pt]
S_{DS}, & T_0\leq T\leq T_s\\[6pt]
\dfrac{S_{D1}}{T}, & T>T_s
\end{cases}
$$

Controles obligatorios:

$$
C_{sm}(0)=A_s
$$

$$
C_{sm}(T_0)=C_{sm}(T_s)=S_{DS}
$$

$$
C_{sm}(1.0\,s)=S_{D1}
$$

---

## 7. Ejemplo numérico exclusivamente didáctico

> **Advertencia:** los siguientes valores no pertenecen al Puente Agua Flor. Se
> eligen únicamente para practicar la aritmética. Deben sustituirse íntegramente
> cuando se disponga del estudio aprobado del sitio.

### 7.1 Datos ilustrativos

| Parámetro | Valor didáctico | Unidad | Estado |
|---|---:|---|---|
| `PGA` | 0.30 | `g` | Supuesto pedagógico |
| `Ss` | 0.75 | `g` | Supuesto pedagógico |
| `S1` | 0.30 | `g` | Supuesto pedagógico |
| Clase de sitio | C | — | Supuesto pedagógico |
| `Fpga` | 1.10 | — | Valor de tabla para el ejemplo |
| `Fa` | 1.10 | — | Valor de tabla para el ejemplo |
| `Fv` | 1.50 | — | Valor de tabla para el ejemplo |
| `ξ` | 0.05 | — | Supuesto pedagógico |

### 7.2 Cálculo de coeficientes

$$
A_s=1.10(0.30)=0.3300
$$

$$
S_{DS}=1.10(0.75)=0.8250
$$

$$
S_{D1}=1.50(0.30)=0.4500
$$

### 7.3 Períodos característicos

$$
T_s=\frac{0.4500}{0.8250}=0.5455\;s
$$

$$
T_0=0.20(0.5455)=0.1091\;s
$$

### 7.4 Tabla de control

| `T` (s) | Rama | Operación | `Csm` |
|---:|---|---|---:|
| 0.0000 | Inicio | `As` | 0.3300 |
| 0.0500 | Ascenso | `0.33+(0.825-0.33)(0.05/0.1091)` | 0.5569 |
| 0.1000 | Ascenso | `0.33+(0.825-0.33)(0.10/0.1091)` | 0.7838 |
| 0.1091 | Inicio meseta | `SDS` | 0.8250 |
| 0.2000 | Meseta | `SDS` | 0.8250 |
| 0.5000 | Meseta | `SDS` | 0.8250 |
| 0.5455 | Fin meseta | `SDS` | 0.8250 |
| 0.6000 | Descenso | `0.45/0.60` | 0.7500 |
| 1.0000 | Descenso | `0.45/1.00` | 0.4500 |
| 2.0000 | Descenso | `0.45/2.00` | 0.2250 |
| 3.0000 | Descenso | `0.45/3.00` | 0.1500 |
| 5.0000 | Descenso | `0.45/5.00` | 0.0900 |

### 7.5 Interpretación

- Los modos con `T < 0.1091 s` se ubican en el ascenso.
- Los modos entre `0.1091 s` y `0.5455 s` reciben la meseta máxima del ejemplo.
- Los modos con períodos mayores reciben una aceleración menor, pero pueden
  generar desplazamientos espectrales mayores.
- El hecho de que un modo tenga menor aceleración no significa automáticamente
  que sea irrelevante para juntas, apoyos o pérdida de asiento.

---

## 8. Espectro elástico y factor de modificación de respuesta `R`

### 8.1 Lectura correcta de la norma

El MTC 2018 establece que las solicitaciones sísmicas de diseño para
subestructuras y uniones se obtienen dividiendo las solicitaciones elásticas por
el `R` correspondiente de sus tablas. La tabla de subestructuras no asigna un
`R` general a cordones, diagonales o vigas de piso de una armadura metálica.

Por tanto, no es correcto afirmar:

```text
"La superestructura es de acero; entonces toda la armadura usa R = 3".
```

Para reducir fuerzas en miembros de la armadura sería necesario un fundamento
normativo y un mecanismo dúctil explícitamente detallado, verificable e inspeccionable.
La sola presencia de acero no garantiza un sistema dúctil: una diagonal comprimida,
una cartela, una conexión o un elemento esbelto pueden fallar de forma frágil o por
inestabilidad antes de desarrollar disipación estable.

### 8.2 Criterio provisional para la clase

Hasta contar con una justificación de diseño específica:

| Grupo | Demanda propuesta para la enseñanza | Justificación |
|---|---|---|
| Cordones, diagonales y montantes | `E_el` | No se asigna un `R` de superestructura no documentado |
| Vigas de piso y largueros | `E_el` | Mantener camino de carga esencialmente elástico |
| Arriostramientos y diafragmas | `E_el` | Elementos críticos para estabilidad y transferencia |
| Unión superestructura–estribo | `E_el/0.8 = 1.25E_el` | Tabla de uniones del MTC 2018 |
| Junta de expansión en el tramo | `E_el/0.8 = 1.25E_el` | Tabla de uniones del MTC 2018 |
| Pilar–viga cabezal o superestructura | `E_el/1.0` | Tabla de uniones del MTC 2018 |
| Pilar–fundación | `E_el/1.0` | Tabla de uniones del MTC 2018 |
| Subestructura | `E_el/R_sub` | Según tipo e importancia |

`R = 1.0` para los miembros de la armadura en esta sesión es un **criterio
conservador provisional de no reducción**, no un valor tabulado por el MTC para
“puente reticulado”.

### 8.3 Estrategia recomendada

Mantener una única función espectral elástica y aplicar la modificación a los
resultados o mediante casos claramente nombrados:

| Caso conceptual | Multiplicador respecto de `E_el` | Uso |
|---|---:|---|
| `EQ_TRUSS_EL` | 1.000 | Miembros de armadura y tablero |
| `EQ_UNION_R08` | 1.250 | Conexión superestructura–estribo y juntas |
| `EQ_SUB_R15` | 0.667 | Ejemplo de subestructura con `R=1.5`, si corresponde |

No se suman estos casos entre sí. Cada uno sirve para verificar el grupo de
componentes al cual corresponde.

### 8.4 Desplazamientos

No debe dividirse automáticamente el desplazamiento elástico entre `R`. Los
desplazamientos para juntas, apoyos, topes y ancho de asiento deben seguir el
procedimiento normativo aplicable. Una reducción pensada para fuerzas no es una
reducción automática de demanda cinemática.

---

## 9. Idealización de la superestructura reticulada

### 9.1 Modelo estructural recomendado

Como base se propone un modelo tridimensional:

- cordones, diagonales, montantes, vigas de piso, largueros y arriostramientos
  mediante elementos `Frame`;
- tablero mediante elementos `Shell`, si su rigidez y distribución de masa son
  relevantes;
- uniones entre tablero y vigas mediante conectividad compartida, brazos rígidos
  u otra idealización compatible con el detalle real;
- apoyos mediante elementos `Link/Support` con rigidez y grados de libertad
  compatibles con los dispositivos reales;
- estribos o pilares mediante elementos estructurales o resortes equivalentes,
  según el alcance del modelo.

### 9.2 Nudos y excentricidades

Los ejes centroidales de cordones, diagonales y vigas de piso rara vez concurren
perfectamente en un único punto físico. Se debe decidir si:

- se ignoran excentricidades por ser secundarias;
- se modelan mediante offsets;
- se usan brazos rígidos;
- se modelan cartelas y uniones con mayor detalle.

Una cadena excesiva de brazos rígidos puede sobre-rigidizar la armadura y reducir
artificialmente períodos y desplazamientos.

### 9.3 Liberaciones en miembros

No debe liberarse automáticamente el momento en ambos extremos de todos los
elementos solo porque el sistema se denomine “reticulado”. Revisar:

- geometría real de cartelas;
- continuidad de cordones;
- rigidez de vigas de piso;
- conexión de arriostramientos;
- flexión secundaria por excentricidades;
- compatibilidad con el modelo usado para diseñar conexiones.

Una alternativa pedagógica es comparar:

1. modelo ideal de armadura articulada;
2. modelo de barras con continuidad parcial;
3. modelo refinado de nudos críticos.

### 9.4 Tablero y acción compuesta

Debe definirse si el tablero:

- actúa como diafragma rígido;
- se representa con rigidez de membrana real;
- participa en flexión longitudinal;
- está conectado a largueros o vigas de piso;
- presenta fisuración que modifica la rigidez;
- se encuentra en etapa compuesta o no compuesta.

El modelo sísmico de servicio terminado no debe confundirse con las etapas de
montaje o vaciado. Si se evalúa una etapa temporal, deben cambiar masa, rigidez,
apoyos y arriostramientos de acuerdo con esa etapa.

### 9.5 Arriostramientos

Modelar expresamente:

- arriostramiento inferior;
- arriostramiento superior, si existe;
- pórticos de entrada;
- diafragmas extremos;
- arriostramientos intermedios;
- conexiones que transmiten fuerzas transversales hacia los apoyos.

Omitir estos elementos puede producir modos ficticios o impedir la transferencia
real de las fuerzas transversales.

### 9.6 Apoyos y vínculos

Preparar una matriz por cada apoyo:

| Apoyo | Longitudinal | Transversal | Vertical | Rotaciones | Observación |
|---|---|---|---|---|---|
| A1 | Libre/restringido | Libre/restringido | Restringido | Según dispositivo | Completar |
| A2 | Libre/restringido | Libre/restringido | Restringido | Según dispositivo | Completar |

En un análisis espectral lineal, los apoyos no lineales, fricción, holguras,
levantamiento y contacto se representan de manera linealizada. Si esos fenómenos
controlan la respuesta, debe complementarse con un análisis no lineal apropiado.

---

## 10. Fuente de masa

### 10.1 Componentes habituales

| Componente | Patrón frecuente | ¿Incluir en masa? | Observación |
|---|---|---|---|
| Armadura metálica | `DC` | Sí | Evitar duplicar peso propio |
| Vigas de piso y largueros | `DC` | Sí | Incluidas por material o carga |
| Tablero | `DC` | Sí | Masa distribuida o por elementos |
| Barandas y defensas | `DC` | Sí | Distribuir en su ubicación real |
| Superficie de rodadura | `DW` | Sí | Masa permanente no estructural |
| Servicios permanentes | `DC/DW` | Sí | Según inventario |
| Carga viva | `LL` | Según criterio aprobado | No incluir automáticamente el 100 % |

El comentario del MTC al método de carga uniforme señala que normalmente no se
incluyen los efectos inerciales de la carga viva, pero deben considerarse cuando
sea probable una carga viva importante durante el sismo, por ejemplo, congestión
urbana con relación elevada entre carga viva y muerta.

### 10.2 Errores frecuentes

1. Activar multiplicador de peso propio en `DC` y volver a introducir manualmente
   el peso de los mismos elementos.
2. Asignar densidad de masa al tablero y además convertir su peso completo en
   masas nodales.
3. Omitir defensas, carpeta de rodadura o vigas transversales.
4. Concentrar toda la masa en el centro del tablero, eliminando modos torsionales.
5. Usar unidades de peso como si fueran unidades de masa sin que CSiBridge haga
   la conversión correspondiente.

### 10.3 Control independiente de masa

Calcular fuera del software:

$$
m_{total}=\sum_i\frac{W_i}{g}
$$

y comparar con la masa reportada por CSiBridge en cada dirección. La diferencia
debe explicarse componente por componente.

---

## 11. Configuración del análisis modal en CSiBridge

### 11.1 Caso modal

Definir primero un caso modal, pues el análisis espectral utiliza sus modos como
base. Dos alternativas son:

- `Eigen`: apropiado para reconocer modos naturales globales y locales;
- `Ritz`: puede ser eficiente cuando los vectores iniciales representan las
  direcciones de excitación y los patrones dominantes.

Para la clase puede iniciarse con `Eigen` y comparar después con `Ritz`.

### 11.2 Número de modos

El MTC 2018 indica, para el método multimodal, un mínimo recomendado de tres veces
el número de tramos. Ese mínimo no sustituye una revisión de suficiencia modal.
Se aumentará el número de modos hasta estabilizar:

- masa participante acumulada;
- cortante basal;
- reacciones en apoyos;
- fuerzas en diagonales y arriostramientos;
- desplazamientos de juntas.

### 11.3 Revisión visual de modos

Para cada modo significativo registrar:

| Modo | `T` (s) | Tipo de deformada | Masa X | Masa Y | Masa Z | Observación |
|---:|---:|---|---:|---:|---:|---|
| 1 | — | Longitudinal/transversal/torsional/local | — | — | — | Completar |
| 2 | — | — | — | — | — | Completar |
| 3 | — | — | — | — | — | Completar |

Se deben investigar modos de período muy largo o muy corto que no correspondan al
comportamiento esperado. Posibles causas:

- apoyo liberado por error;
- nodo desconectado;
- sección o módulo elástico incorrecto;
- masa duplicada;
- brazo rígido excesivo;
- miembro sin arriostramiento;
- unidades inconsistentes.

---

## 12. Definición de la función espectral en CSiBridge

### 12.1 Función normalizada

Según la ayuda oficial de CSiBridge, las aceleraciones de la función de espectro
se consideran **normalizadas y sin unidades**. Las unidades de aceleración se
incorporan mediante el `Scale Factor` del caso de respuesta espectral.

Ruta de interfaz, sujeta a la versión instalada:

```text
Loads > Functions Type > Response Spectrum > New
```

Elegir `User Spectrum` o `Spectrum from File`.

Nombre recomendado:

```text
RS_MTC2018_AGUA_FLOR_EL_5PCT
```

### 12.2 Extensión del período

CSiBridge mantiene constante el primer valor para períodos menores que el primero
y mantiene constante el último valor para períodos mayores que el último. Por ello:

- incluir explícitamente `T = 0`;
- extender la tabla más allá del mayor período modal esperado;
- no terminar la función en un período demasiado corto;
- verificar visualmente la rama descendente.

### 12.3 Formato de archivo

Ejemplo didáctico:

```csv
Period,Accel
0.0000,0.3300
0.0500,0.5569
0.1000,0.7838
0.1091,0.8250
0.2000,0.8250
0.5000,0.8250
0.5455,0.8250
0.6000,0.7500
1.0000,0.4500
2.0000,0.2250
3.0000,0.1500
5.0000,0.0900
```

Si se usa `Spectrum from File`, conservar el archivo junto al modelo o convertir
la función a definida por el usuario para no perder el vínculo al mover el modelo.

---

## 13. Factor de escala y unidades

### 13.1 Regla dimensional

Si las ordenadas `Csm` se ingresan normalizadas como múltiplos de `g`, el factor
del caso espectral debe tener unidades de aceleración:

$$
SF= g
$$

Ejemplos:

| Unidades activas de longitud y tiempo | `g` para `Scale Factor` |
|---|---:|
| m, s | `9.80665 m/s²` |
| mm, s | `9806.65 mm/s²` |
| in, s | `386.089 in/s²` |

El valor `Scale Factor = 1.0` solo es correcto si la función fue ingresada en las
unidades reales de aceleración activas. En la definición estándar normalizada de
CSiBridge, usar `1.0` con valores como `0.825` subescala la acción por un factor `g`.

### 13.2 Casos elásticos sugeridos

```text
RSX_EL  -> U1, función RS_MTC2018_AGUA_FLOR_EL_5PCT, SF = g
RSY_EL  -> U2, función RS_MTC2018_AGUA_FLOR_EL_5PCT, SF = g
```

La correspondencia `U1/U2` con longitudinal/transversal depende del sistema de
coordenadas del modelo. Debe verificarse mediante una deformada sencilla.

### 13.3 Casos modificados, si se implementan por escala

En unidades `m–kN–s`, para el ejemplo:

| Caso | Expresión | `Scale Factor` |
|---|---|---:|
| Armadura elástica | `g/1.0` | 9.80665 |
| Unión `R=0.8` | `g/0.8` | 12.25831 |
| Subestructura `R=1.5` | `g/1.5` | 6.53777 |

Es preferible conservar casos elásticos principales y modificar resultados de
manera trazable; crear demasiados casos escalados puede inducir errores de uso.

---

## 14. Caso de respuesta espectral

Ruta de interfaz, sujeta a versión:

```text
Analysis > Load Cases > Response Spectrum > New
```

### 14.1 Parámetros básicos

| Campo | Selección inicial | Revisión necesaria |
|---|---|---|
| Modal Load Case | Caso modal validado | Períodos y masa participante |
| Modal Combination | `CQC` | Adecuado para modos próximos |
| Modal Damping | Valor sustentado; ejemplo 5 % | No adoptar por rutina sin revisar sistema |
| Load Type | `Accel` | Dirección correcta |
| Function | Espectro elástico MTC | Nombre y tabla correctos |
| Scale Factor | `g` en unidades activas | Control dimensional |

### 14.2 Combinación modal

El MTC 2018 admite estimar respuestas multimodales mediante `CQC`. Es especialmente
conveniente para una armadura tridimensional porque puede haber frecuencias próximas.
`SRSS` es más apropiado para modos bien separados.

Conceptualmente:

$$
R_{CQC}=\sqrt{\sum_i\sum_j\rho_{ij}R_iR_j}
$$

donde `ρij` representa la correlación entre modos y depende de frecuencias y
amortiguamiento.

### 14.3 Direcciones sísmicas

El MTC exige considerar la acción lateral en cualquier dirección y combinar las
respuestas elásticas ortogonales como:

$$
E_1=|E_X|+0.30|E_Y|
$$

$$
E_2=0.30|E_X|+|E_Y|
$$

Para facilitar la auditoría se recomienda crear `RSX_EL` y `RSY_EL` por separado
y luego construir las envolventes direccionales. CSiBridge también dispone de
combinaciones direccionales `SRSS`, `CQC3` y `ABS`; el método elegido debe reproducir
el criterio normativo adoptado y quedar documentado.

### 14.4 Componente vertical

No debe introducirse automáticamente una componente vertical igual al 30 % del
espectro horizontal. El `30 %` citado anteriormente corresponde a la combinación
de **dos direcciones horizontales ortogonales**. La necesidad y definición del
espectro vertical debe provenir del MTC, del estudio específico o del criterio del
propietario aplicable al proyecto.

---

## 15. Ejecución del análisis

### 15.1 Secuencia

1. Guardar una copia controlada del modelo.
2. Verificar unidades activas.
3. Ejecutar `Check Model`.
4. Revisar mensajes de inestabilidad o grados de libertad sin rigidez.
5. Ejecutar primero solo el caso modal.
6. Animar y clasificar modos.
7. Aumentar modos si la respuesta no converge.
8. Ejecutar `RSX_EL` y `RSY_EL`.
9. Revisar deformadas espectrales y reacciones.
10. Crear combinaciones direccionales y de Evento Extremo.
11. Exportar tablas para verificación independiente.

### 15.2 Señales de alerta

- períodos extremadamente largos en una estructura aparentemente rígida;
- primer modo local de una barra en vez de un modo global;
- masa participante casi nula en una dirección horizontal;
- reacciones sísmicas en apoyos declarados libres;
- ausencia de torsión cuando la masa está distribuida transversalmente;
- grandes fuerzas en un único nudo por masas concentradas artificiales;
- aceleraciones aproximadamente `1/9.81` de lo esperado por error de escala.

---

## 16. Resultados para la superestructura reticulada

### 16.1 Miembros principales

Extraer envolventes de:

- fuerza axial `P` en cordón superior e inferior;
- fuerza axial y posible flexión secundaria en diagonales;
- esfuerzos en montantes;
- flexión y corte de vigas de piso;
- fuerzas en largueros;
- fuerza axial en arriostramiento superior e inferior;
- solicitaciones en pórticos de entrada y diafragmas extremos.

En cada familia identificar:

| Elemento | Caso gobernante | `P` | `M2` | `M3` | `V2` | `V3` | Observación |
|---|---|---:|---:|---:|---:|---:|---|
| Cordón superior | — | — | — | — | — | — | Compresión/pandeo |
| Cordón inferior | — | — | — | — | — | — | Tracción/inversión |
| Diagonal | — | — | — | — | — | — | Cambio de signo |
| Viga de piso | — | — | — | — | — | — | Transferencia transversal |

### 16.2 Conexiones

Las fuerzas de barras no bastan para diseñar una cartela. Deben reconstruirse:

- equilibrio del nudo;
- combinación de fuerzas concurrentes;
- excentricidades;
- bloques de cortante;
- aplastamiento y desgarro;
- pernos o soldaduras;
- pandeo de cartelas;
- trayectoria de fuerza hacia vigas de piso o apoyos.

### 16.3 Apoyos y dispositivos

Extraer por cada apoyo:

- `Fx`, `Fy`, `Fz`;
- levantamiento o pérdida de compresión;
- desplazamiento longitudinal y transversal;
- rotaciones;
- demanda en topes y anclajes;
- compatibilidad con capacidad y recorrido del dispositivo.

Para un puente de un tramo, comparar la demanda obtenida —si se realiza análisis—
con la fuerza mínima normativa de la unión. Gobierna la mayor.

### 16.4 Desplazamientos

Revisar:

- desplazamiento absoluto del tablero;
- desplazamiento relativo tablero–estribo;
- apertura y cierre de juntas;
- recorrido disponible en apoyos;
- ancho de asiento;
- desplazamiento transversal y riesgo de descalce;
- distorsión entre los dos planos de armadura.

---

## 17. Combinaciones de carga

La acción sísmica pertenece al estado límite de Evento Extremo I. Los factores
definitivos deben tomarse de la tabla contractual aplicable y no se reproducen aquí
sin conocer la configuración aprobada del proyecto.

La estructura general es:

$$
Q=\sum_i\eta_i\gamma_i Q_i
$$

Para capturar ambos sentidos:

$$
Q_{EE,+}=Q_{perm}+E_Q
$$

$$
Q_{EE,-}=Q_{perm}-E_Q
$$

Debido a que la respuesta espectral es estadística y no conserva signos físicos
simultáneos, debe revisarse cuidadosamente cómo CSiBridge genera máximos y mínimos
y cómo se combinan con cargas permanentes. Preparar envolventes para ambos signos
es especialmente importante en:

- diagonales que alternan tracción y compresión;
- apoyos con posible levantamiento;
- juntas y topes;
- cordones sometidos a cambio de demanda axial.

---

## 18. Verificaciones independientes

### 18.1 Masa total

Comparar masa manual y masa del modelo:

$$
\varepsilon_m=\frac{|m_{CSI}-m_{manual}|}{m_{manual}}\times100\%
$$

Toda diferencia relevante debe explicarse; no basta con declarar un porcentaje
“aceptable” sin conocer su origen.

### 18.2 Período aproximado

Para una dirección puede obtenerse una rigidez equivalente `K_eq` mediante una
carga estática y un desplazamiento representativo:

$$
K_{eq}=\frac{F}{\Delta}
$$

$$
T_{aprox}=2\pi\sqrt{\frac{m_{eq}}{K_{eq}}}
$$

Comparar con el período modal dominante de CSiBridge.

### 18.3 Cortante basal

Calcular:

$$
V_{RS}=\sum |R_{apoyo,h}|
$$

y compararlo con una estimación:

$$
V_{aprox}=C_{sm}(T_{dom})W_{ef}
$$

No deben coincidir exactamente en un sistema multimodal, pero el orden de magnitud
y la tendencia deben ser coherentes.

### 18.4 Equilibrio y camino de carga

Verificar que la suma de reacciones horizontales pueda explicarse mediante las
fuerzas de inercia y que los apoyos libres no atraigan fuerzas incompatibles con
su idealización.

### 18.5 Sensibilidad

Repetir el análisis variando de manera controlada:

- número de modos;
- rigidez del tablero;
- rigidez de apoyos;
- liberaciones de nudos;
- inclusión de excentricidades;
- participación de carga viva;
- amortiguamiento, si existe justificación.

Registrar qué resultados cambian y por qué.

---

## 19. Taller guiado

### Actividad 1 — Puerta normativa

**Enunciado:** clasifique el procedimiento si Agua Flor resulta ser:

1. un tramo simplemente apoyado;
2. tres tramos, regular, zona sísmica 3 y categoría “otros”;
3. tres tramos, irregular, zona sísmica 3.

**Respuesta esperada:**

- Caso 1: no se exige análisis sísmico global; sí conexiones y asiento.
- Casos 2 y 3: consultar la Tabla 2.6.5.4.3.1-1; para el caso irregular de zona 3,
  el método multimodal es el mínimo indicado para “otros puentes”.

### Actividad 2 — Construcción del espectro

Reproducir el ejemplo de la Sección 7 y comprobar:

$$
C_{sm}(0)=0.3300
$$

$$
C_{sm}(T_0)=C_{sm}(T_s)=0.8250
$$

$$
C_{sm}(1.0)=0.4500
$$

### Actividad 3 — Factor de escala

**Pregunta:** si el modelo usa `kN–mm–s` y la función contiene valores
normalizados, ¿qué escala se usa para la armadura elástica?

**Respuesta:**

$$
SF=9806.65\;mm/s^2
$$

Para la unión con `R=0.8`:

$$
SF=\frac{9806.65}{0.8}=12258.31\;mm/s^2
$$

### Actividad 4 — Fuente de masa

Preparar una tabla con el peso de cada componente y explicar si la masa proviene
de densidad del material, carga distribuida o masa nodal. Identificar duplicaciones.

### Actividad 5 — Interpretación modal

Animar los primeros modos y clasificarlos como longitudinal, transversal, torsional
o local. Explicar qué elemento controla la rigidez de cada modo.

### Actividad 6 — Matriz de diseño

Asignar a cada resultado el criterio correspondiente:

| Resultado | Caso de demanda | Verificación |
|---|---|---|
| Axial de diagonal | `EQ_TRUSS_EL` | Resistencia y pandeo |
| Fuerza en apoyo de estribo | `EQ_UNION_R08` y mínimo normativo | Capacidad de apoyo/anclaje |
| Desplazamiento en junta | Desplazamiento normativo | Recorrido y asiento |
| Fuerza del estribo | `EQ_SUB/R_sub` | Diseño de subestructura |

---

## 20. Evaluación de la sesión

### 20.1 Preguntas de salida

1. ¿Por qué la masa de la superestructura participa aunque `R` esté tabulado para
   subestructuras y uniones?
2. ¿Por qué no puede asignarse `R=3` a toda armadura solo por ser de acero?
3. ¿Qué diferencia existe entre una función normalizada y su `Scale Factor`?
4. ¿Cuándo `CQC` es preferible a `SRSS`?
5. ¿Qué se verifica obligatoriamente en un puente de un solo tramo aunque no se
   exija análisis sísmico global?
6. ¿Por qué debe extenderse la tabla espectral más allá del mayor período modal?
7. ¿Qué resultado usaría para diseñar la unión superestructura–estribo?

### 20.2 Rúbrica

| Criterio | Peso | Logro esperado |
|---|---:|---|
| Datos y supuestos | 15 % | Distingue confirmados, asumidos y pendientes |
| Espectro | 20 % | Ecuaciones y tabla sin errores |
| Modelo y masa | 20 % | Camino de carga, apoyos y masa coherentes |
| Configuración CSiBridge | 20 % | Función normalizada, escala y CQC correctos |
| Aplicación de `R` | 15 % | No aplica un único `R` indiscriminado |
| Verificación independiente | 10 % | Masa, período, cortante y equilibrio revisados |

---

## 21. Lista de control para entrega

### 21.1 Datos

- [ ] Coordenadas confirmadas.
- [ ] Estudio de peligro sísmico aprobado.
- [ ] Clase de sitio sustentada.
- [ ] Importancia del puente definida.
- [ ] Número de tramos y regularidad confirmados.
- [ ] Inventario de cargas permanentes completo.

### 21.2 Modelo

- [ ] Ejes y unidades documentados.
- [ ] Secciones y materiales verificados.
- [ ] Nudos de armadura conectados.
- [ ] Liberaciones justificadas.
- [ ] Tablero y excentricidades revisados.
- [ ] Arriostramientos y diafragmas incluidos.
- [ ] Apoyos y topes representan los dispositivos reales.
- [ ] Masa manual comparada con masa de CSiBridge.

### 21.3 Análisis

- [ ] Modos animados y clasificados.
- [ ] Número de modos convergente.
- [ ] Función espectral extendida al rango necesario.
- [ ] `Scale Factor` compatible con unidades.
- [ ] `CQC` y amortiguamiento documentados.
- [ ] Dos direcciones horizontales consideradas.
- [ ] Regla `100 % + 30 %` aplicada.

### 21.4 Resultados

- [ ] Axiales de cordones, diagonales y montantes revisados.
- [ ] Vigas de piso y arriostramientos revisados.
- [ ] Fuerzas de conexión evaluadas con su criterio de `R`.
- [ ] Reacciones y desplazamientos por apoyo tabulados.
- [ ] Ancho de asiento y recorrido de juntas comprobados.
- [ ] Evento Extremo I evaluado en ambos sentidos.
- [ ] Control de masa, período, cortante basal y equilibrio completado.

---

## 22. Conclusiones de la clase

1. El sismo actúa sobre la masa de toda la superestructura; la armadura, tablero,
   vigas de piso, apoyos y subestructura forman un único camino de carga.
2. La primera decisión no es el valor de `R`, sino determinar si el análisis global
   es exigible y qué método mínimo corresponde.
3. Para métodos modales, el MTC parte del espectro elástico `Csm(T)`.
4. CSiBridge interpreta la función espectral como normalizada; el `Scale Factor`
   aporta las unidades de aceleración.
5. En una armadura tridimensional, `CQC` permite combinar modos próximos y debe
   acompañarse de una revisión de convergencia y deformadas modales.
6. Las tablas MTC de `R` no justifican aplicar automáticamente `R=3` a todos los
   miembros de la superestructura reticulada.
7. Las uniones superestructura–estribo y juntas poseen un criterio específico
   `R=0.8`, por lo que su demanda puede superar la respuesta elástica.
8. Un resultado de CSiBridge solo es aceptable después de verificar masa, unidades,
   períodos, camino de carga, equilibrio y orden de magnitud.

### Resultado principal

La sesión deja definido un procedimiento completo y auditable para construir el
modelo sísmico del Puente Agua Flor. El cálculo definitivo permanece condicionado
a recibir la geometría, los apoyos, la importancia y los parámetros sísmicos y
geotécnicos específicos del sitio.

---

## 23. Referencias

1. **Ministerio de Transportes y Comunicaciones.** *Manual de Puentes, 2018*:
   artículos 2.4.3.11.1 a 2.4.3.11.8 y 2.6.5.4.1 a 2.6.5.4.4.
   Archivo local: [`../normativa/manual_puentes_MTC_2018.pdf`](../normativa/manual_puentes_MTC_2018.pdf).
2. **Computers and Structures, Inc.**
   [Define Response Spectrum Functions](https://docs.csiamerica.com/help-files/csibridge/Loads_tab/Functions/Response_Spectrum/Define_Response_Spectrum_Functions.htm).
3. **Computers and Structures, Inc.**
   [Load Case Data — Response Spectrum](https://docs.csiamerica.com/help-files/csibridge/Analysis_tab/Load_Cases/Load_Case_Data_Response_Spectrum_Form.htm).
4. **Computers and Structures, Inc.**
   [Spectrum from File](https://docs.csiamerica.com/help-files/csibridge/Loads_tab/Functions/Response_Spectrum/Spectrum_from_File_Response_Spectrum_Function_Definition_Form.htm).
5. **MINCETUR.**
   [Inventario turístico — Quebrada Agua Flor, San Ramón, Chanchamayo, Junín](https://consultasenlinea.mincetur.gob.pe/fichaInventario/index.aspx?cod_Ficha=5301).

---

*Documento pedagógico. Revisión inicial preparada para adaptar al modelo y al
estudio de peligro sísmico del Puente Agua Flor.*

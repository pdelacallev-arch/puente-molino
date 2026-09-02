# Sesión 2 — Del contrafuerte trapezoidal al elemento Q4

## Propósito

En la sesión 1 usamos las resultantes entregadas por el análisis. Ahora
entraremos al interior de `analizar_contrafuertes_centrales_2d.py` para entender
cómo se construye la malla y cómo un elemento Q4 relaciona las coordenadas
naturales \((\xi,\eta)\) con las coordenadas físicas \((x,z)\).

Al finalizar podrás reproducir manualmente:

1. las coordenadas, conectividad y grados de libertad del primer elemento de la
   malla real;
2. sus funciones de forma, matriz jacobiana y derivadas físicas en un punto de
   Gauss.

> Esta sesión contiene exactamente dos ejercicios manuales. La matriz
> constitutiva, la matriz completa de rigidez y los esfuerzos se desarrollarán
> en la sesión 3.

## 1. Modelo que representa el programa

El alma del contrafuerte se idealiza como un continuo bidimensional en esfuerzo
plano:

```text
             z
             ↑
   pantalla  │──────────────●  L(9.80) = 1.17 m
     x = 0   │             /
             │            /   alma de espesor 0.40 m
             │           /
             │          /
             │─────────●────────→ x
             └──────────────────
              L(0) = 6.10 m
              borde basal empotrado
```

La longitud horizontal cambia linealmente:

\[
L(z)=L_b+\frac{L_t-L_b}{H}z
=6.10+\frac{1.17-6.10}{9.80}z.
\]

La malla tiene 14 divisiones horizontales. En cada nivel, el programa distribuye
15 nodos entre \(x=0\) y \(x=L(z)\). Los niveles verticales provienen de la
malla de la pantalla shell 3D; los dos primeros son:

\[
z_0=0,\qquad z_1=0.4666667\ \text{m}.
\]

![Acciones nodales y variación de las resultantes](../../outputs/calc_est_2026_004/contrafuertes_centrales_acciones.png)

---

## Ejercicio manual 1 — Construcción del primer elemento de la malla

### Enunciado

Construir el elemento Q4 ubicado junto a la pantalla y la zapata, es decir, el
elemento de la primera división horizontal entre los niveles \(z_0\) y \(z_1\).
Determinar:

- las coordenadas de sus cuatro nodos;
- su conectividad global;
- sus ocho grados de libertad;
- su área física.

### Paso 1: calcular la longitud en ambos niveles

En la base:

\[
L(z_0)=L(0)=6.10\ \text{m}.
\]

En el nivel superior:

\[
\begin{aligned}
L(z_1)
&=6.10+\frac{-4.93}{9.80}(0.4666667)\\
&=5.8652381\ \text{m}.
\end{aligned}
\]

La longitud disminuye porque el borde libre se inclina hacia la pantalla al
subir.

### Paso 2: obtener el ancho de la primera división

Como existen \(n_x=14\) divisiones:

\[
\Delta x_0=\frac{L(z_0)}{14}
=\frac{6.10}{14}=0.4357143\ \text{m},
\]

\[
\Delta x_1=\frac{L(z_1)}{14}
=\frac{5.8652381}{14}=0.4189456\ \text{m}.
\]

El lado superior es ligeramente menor que el inferior. Por ello el elemento es
un trapecio y no un rectángulo perfecto.

### Paso 3: numerar los nodos globales

El programa usa:

\[
\text{tag}(j,i)=j(n_x+1)+i=15j+i,
\]

donde \(j\) identifica el nivel e \(i\) la posición horizontal.

La numeración local Q4 es antihoraria:

```text
       z = 0.4666667 m

 nodo 15 = local 4  ●────────────●  local 3 = nodo 16
                     │           /
                     │ elemento 0
                     │         /
  nodo 0 = local 1  ●────────●  local 2 = nodo 1

       z = 0 m          → x
```

| Nodo local | Nodo global | \((\xi,\eta)\) | \((x,z)\) en m |
|---:|---:|---:|---:|
| 1 | 0 | \((-1,-1)\) | \((0,0)\) |
| 2 | 1 | \((+1,-1)\) | \((0.4357143,0)\) |
| 3 | 16 | \((+1,+1)\) | \((0.4189456,0.4666667)\) |
| 4 | 15 | \((-1,+1)\) | \((0,0.4666667)\) |

Por tanto, la conectividad guardada es:

\[
\boxed{[0,\ 1,\ 16,\ 15]}.
\]

### Paso 4: identificar los grados de libertad

Cada nodo tiene dos traslaciones:

\[
\mathbf u_i=\begin{bmatrix}u_{x,i} & u_{z,i}\end{bmatrix}^T.
\]

El programa asigna al nodo global \(n\):

\[
g_x=2n,\qquad g_z=2n+1.
\]

Así, el vector elemental y sus índices globales son:

\[
\mathbf u_e=
\begin{bmatrix}
u_{x,0}&u_{z,0}&u_{x,1}&u_{z,1}&
u_{x,16}&u_{z,16}&u_{x,15}&u_{z,15}
\end{bmatrix}^T,
\]

\[
\boxed{\text{gdl}_e=[0,1,2,3,32,33,30,31]}.
\]

Los nodos 0 y 1 pertenecen al borde basal; sus grados de libertad quedan
restringidos por el empotramiento de la zapata.

### Paso 5: calcular el área física

El elemento es un trapecio de altura \(h=0.4666667\ \text{m}\):

\[
A_e=\frac{\Delta x_0+\Delta x_1}{2}h.
\]

Sustituyendo:

\[
\begin{aligned}
A_e
&=\frac{0.4357143+0.4189456}{2}(0.4666667)\\
&=0.1994206\ \text{m}^2.
\end{aligned}
\]

### Resultado y correspondencia con Python

| Magnitud | Cálculo manual | Modelo JSON |
|---|---:|---:|
| Conectividad | `[0, 1, 16, 15]` | `[0, 1, 16, 15]` |
| Ancho inferior | 0.4357143 m | 0.4357143 m |
| Ancho superior | 0.4189456 m | 0.4189456 m |
| Área | 0.1994206 m² | 0.1994206 m² |

Este procedimiento corresponde a `ParametrosContrafuerte.longitud(...)` y
`generar_malla(...)` en
[`analizar_contrafuertes_centrales_2d.py`](../../analisis_estabilidad/analizar_contrafuertes_centrales_2d.py).

### Interpretación

La conectividad conserva el recorrido antihorario. Esto es esencial: invertir
el orden de los nodos puede producir un jacobiano negativo, lo que indica un
elemento invertido. El programa rechaza esos elementos.

---

## Ejercicio manual 2 — Funciones de forma, jacobiano y derivadas físicas

### Enunciado

Para el elemento del ejercicio 1, evaluar el punto de Gauss inferior izquierdo:

\[
\xi=\eta=-\frac{1}{\sqrt 3}=-0.5773503.
\]

Calcular:

1. las cuatro funciones de forma;
2. las coordenadas físicas del punto;
3. las derivadas naturales;
4. la matriz jacobiana y su determinante;
5. las derivadas respecto a \(x,z\).

### Paso 1: evaluar las funciones de forma Q4

Las funciones bilineales son:

\[
\begin{aligned}
N_1&=\tfrac14(1-\xi)(1-\eta), &
N_2&=\tfrac14(1+\xi)(1-\eta),\\
N_3&=\tfrac14(1+\xi)(1+\eta), &
N_4&=\tfrac14(1-\xi)(1+\eta).
\end{aligned}
\]

Para \(\xi=\eta=-0.5773503\):

\[
\boxed{\mathbf N=
\begin{bmatrix}
0.6220085&0.1666667&0.0446582&0.1666667
\end{bmatrix}}.
\]

Verificación de partición de la unidad:

\[
\sum N_i=0.6220085+0.1666667+0.0446582+0.1666667=1.0000001\approx1.
\]

El nodo 1 tiene el mayor peso porque el punto está en el cuadrante natural
inferior izquierdo.

### Paso 2: ubicar físicamente el punto de Gauss

La interpolación isoparamétrica usa las mismas funciones para la geometría:

\[
x=\sum N_i x_i,\qquad z=\sum N_i z_i.
\]

Para \(x\):

\[
\begin{aligned}
x={}&0.6220085(0)+0.1666667(0.4357143)\\
   &+0.0446582(0.4189456)+0.1666667(0)\\
  ={}&0.0913284\ \text{m}.
\end{aligned}
\]

Para \(z\):

\[
\begin{aligned}
z={}&(0.0446582+0.1666667)(0.4666667)\\
  ={}&0.0986183\ \text{m}.
\end{aligned}
\]

Por tanto:

\[
\boxed{(x_G,z_G)=(0.0913284,\ 0.0986183)\ \text{m}}.
\]

### Paso 3: calcular las derivadas naturales

Las derivadas respecto a \(\xi\) son:

\[
\begin{aligned}
N_{1,\xi}&=-\tfrac14(1-\eta),&
N_{2,\xi}&=+\tfrac14(1-\eta),\\
N_{3,\xi}&=+\tfrac14(1+\eta),&
N_{4,\xi}&=-\tfrac14(1+\eta).
\end{aligned}
\]

Las derivadas respecto a \(\eta\) son:

\[
\begin{aligned}
N_{1,\eta}&=-\tfrac14(1-\xi),&
N_{2,\eta}&=-\tfrac14(1+\xi),\\
N_{3,\eta}&=+\tfrac14(1+\xi),&
N_{4,\eta}&=+\tfrac14(1-\xi).
\end{aligned}
\]

Numéricamente:

\[
\boxed{
\frac{\partial\mathbf N}{\partial\xi}=
\begin{bmatrix}
-0.3943376&0.3943376&0.1056624&-0.1056624
\end{bmatrix}},
\]

\[
\boxed{
\frac{\partial\mathbf N}{\partial\eta}=
\begin{bmatrix}
-0.3943376&-0.1056624&0.1056624&0.3943376
\end{bmatrix}}.
\]

Ambas filas suman cero. Esto es coherente con derivar
\(N_1+N_2+N_3+N_4=1\).

### Paso 4: construir la matriz jacobiana

La regla de la cadena se escribe como:

\[
\begin{bmatrix}
N_{i,\xi}\\N_{i,\eta}
\end{bmatrix}
=
\underbrace{
\begin{bmatrix}
x_{,\xi}&z_{,\xi}\\
x_{,\eta}&z_{,\eta}
\end{bmatrix}}_{\mathbf J}
\begin{bmatrix}
N_{i,x}\\N_{i,z}
\end{bmatrix}.
\]

Cada término geométrico se obtiene sumando derivada por coordenada nodal. Por
ejemplo:

\[
x_{,\xi}=\sum_i N_{i,\xi}x_i
=0.3943376(0.4357143)+0.1056624(0.4189456)
=0.2160853\ \text{m},
\]

\[
z_{,\xi}=\sum_i N_{i,\xi}z_i=0,
\]

\[
x_{,\eta}=\sum_i N_{i,\eta}x_i=-0.0017718\ \text{m},
\]

\[
z_{,\eta}=\sum_i N_{i,\eta}z_i=0.2333333\ \text{m}.
\]

Entonces:

\[
\boxed{
\mathbf J=
\begin{bmatrix}
0.2160853&0\\
-0.0017718&0.2333333
\end{bmatrix}\ \text{m}}.
\]

Su determinante es:

\[
\begin{aligned}
\det\mathbf J
&=(0.2160853)(0.2333333)-0(-0.0017718)\\
&=0.05041991\ \text{m}^2>0.
\end{aligned}
\]

El signo positivo confirma que la numeración no invierte el elemento. El
determinante también convierte un área diferencial natural en área física:

\[
dA=\det(\mathbf J)\,d\xi\,d\eta.
\]

### Paso 5: transformar las derivadas al sistema físico

Se resuelve, para los cuatro nodos a la vez:

\[
\begin{bmatrix}
\mathbf N_{,x}\\
\mathbf N_{,z}
\end{bmatrix}
=\mathbf J^{-1}
\begin{bmatrix}
\mathbf N_{,\xi}\\
\mathbf N_{,\eta}
\end{bmatrix}.
\]

La inversa es:

\[
\mathbf J^{-1}=
\begin{bmatrix}
4.6278016&0\\
0.0351413&4.2857143
\end{bmatrix}\ \text{m}^{-1}.
\]

Por ejemplo, para el nodo 1:

\[
N_{1,x}=4.6278016(-0.3943376)=-1.8249160\ \text{m}^{-1},
\]

\[
\begin{aligned}
N_{1,z}
&=0.0351413(-0.3943376)+4.2857143(-0.3943376)\\
&=-1.7038757\ \text{m}^{-1}.
\end{aligned}
\]

Repitiendo para los cuatro nodos:

\[
\boxed{
\mathbf N_{,x}=
\begin{bmatrix}
-1.8249160&1.8249160&0.4889848&-0.4889848
\end{bmatrix}\ \text{m}^{-1}},
\]

\[
\boxed{
\mathbf N_{,z}=
\begin{bmatrix}
-1.7038757&-0.4389815&0.4565521&1.6863050
\end{bmatrix}\ \text{m}^{-1}}.
\]

Verificaciones:

\[
\sum_i N_{i,x}=0,
\qquad
\sum_i N_{i,z}=0.
\]

### Paso 6: comprobar el área mediante integración de Gauss

Los cuatro determinantes en la integración \(2\times2\) son:

| Punto \((\xi,\eta)\) | \(\det\mathbf J\) (m²) |
|---:|---:|
| \((-g,-g)\) | 0.05041991 |
| \((-g,+g)\) | 0.04929041 |
| \((+g,-g)\) | 0.05041991 |
| \((+g,+g)\) | 0.04929041 |

Como los cuatro pesos de Gauss valen 1:

\[
A_e\approx\sum_{p=1}^{4}\det\mathbf J_p
=0.19942064\ \text{m}^2.
\]

El resultado coincide exactamente con el área trapezoidal del ejercicio 1.
Esta es una comprobación independiente de la transformación isoparamétrica.

### Resultado y correspondencia con Python

| Magnitud | Manual | Función del programa |
|---|---:|---:|
| \(\sum N_i\) | 1.000000 | `_funciones_forma` |
| \((x_G,z_G)\) | (0.0913284, 0.0986183) m | `n @ coords` |
| \(\det\mathbf J\) | 0.05041991 m² | `matriz_b` |
| \(\sum N_{i,x}\) | 0 | `matriz_b` |
| \(\sum N_{i,z}\) | 0 | `matriz_b` |
| Área integrada | 0.19942064 m² | integración 2×2 |

Este ejercicio reproduce `_funciones_forma(...)` y la transformación incluida
en `matriz_b(...)` del script de análisis.

## 2. Qué significan estos resultados

- Las funciones \(N_i\) interpolan tanto la geometría como los desplazamientos;
  por eso el elemento es **isoparamétrico**.
- \(\mathbf J\) describe localmente cuánto se estira, inclina o distorsiona el
  cuadrado natural al convertirse en el trapecio físico.
- Las derivadas naturales son adimensionales; las derivadas físicas tienen
  unidades \(\text{m}^{-1}\).
- Las derivadas físicas son las que permiten pasar de desplazamientos nodales a
  deformaciones.
- El término pequeño \(x_{,\eta}=-0.0017718\ \text{m}\) refleja la inclinación
  del lado derecho del elemento.

## 3. Errores frecuentes

1. Dividir siempre 6.10 m entre 14. En los niveles superiores debe dividirse
   \(L(z)\), que es menor.
2. Confundir nodo local con nodo global. El nodo local 3 es el nodo global 16.
3. Ordenar la conectividad como `[0, 1, 15, 16]`; eso cruza el elemento.
4. Usar \(\mathbf J\) directamente para transformar derivadas. Debe resolverse
   el sistema o multiplicarse por \(\mathbf J^{-1}\).
5. Interpretar \(\det\mathbf J\) como un área completa. Es un factor de cambio
   de área evaluado en un punto; el área se obtiene integrándolo.
6. Omitir unidades: \(N_i\) no tiene unidades, \(\mathbf J\) tiene unidades de
   longitud y \(N_{i,x},N_{i,z}\) tienen unidades inversas de longitud.

## 4. Autoevaluación

1. ¿Por qué el lado superior del elemento es menor que el inferior?
2. ¿Qué indica físicamente \(\det\mathbf J>0\)?
3. ¿Por qué las sumas de las derivadas de las funciones de forma deben ser cero?
4. ¿Qué resultado enlazará esta sesión con el cálculo de esfuerzos?

Respuestas esperadas:

1. porque \(L(z)\) disminuye linealmente hacia la corona;
2. que la transformación conserva la orientación y el elemento no está
   invertido;
3. porque la derivada de \(\sum N_i=1\) es cero;
4. las derivadas físicas, con las que se construye la matriz deformación–
   desplazamiento \(\mathbf B\).

## 5. Puente hacia la sesión 3

La siguiente sesión tomará las dos filas obtenidas,
\(\mathbf N_{,x}\) y \(\mathbf N_{,z}\), para construir:

\[
\boldsymbol\varepsilon
=\mathbf B\mathbf u_e
=\begin{bmatrix}\varepsilon_x&\varepsilon_z&\gamma_{xz}\end{bmatrix}^T,
\]

y después:

\[
\boldsymbol\sigma=\mathbf D\boldsymbol\varepsilon.
\]

Así se podrá explicar el origen de los campos de esfuerzo principal mostrados
por el análisis:

![Esfuerzo principal de tracción del modelo Q4](../../outputs/calc_est_2026_004/contrafuertes_centrales_sigma1.png)

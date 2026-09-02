# Sesión 1 — Funciones de forma del elemento Q4

## Objetivo

Aprender a interpolar un desplazamiento vertical dentro de un elemento
cuadrilateral de cuatro nodos (Q4). Al terminar, podrás leer y comprobar la
función <code>shape_functions(xi, eta)</code> de <code>q4_shell_mindlin.py</code>.

En esta sesión todavía no calculamos rigideces, esfuerzos ni momentos. Solo
respondemos una pregunta fundamental: **si conozco el desplazamiento en los
cuatro nodos, ¿qué desplazamiento predice el elemento en un punto interior?**

---

## 1. Elemento de referencia y notación

Usamos el elemento rectangular siguiente, con la numeración antihoraria que
emplea el programa:

~~~text
      y
      ^
  4 o-----------o 3
    |           |
    |    Q4     |     dimensiones: 2 m x 1 m
    |           |
  1 o-----------o 2 --> x
    (0,0)     (2,0)
~~~

| Nodo | Coordenadas físicas <code>(x, y)</code> | Coordenadas naturales <code>(xi, eta)</code> |
|---:|---:|---:|
| 1 | <code>(0, 0)</code> | <code>(-1, -1)</code> |
| 2 | <code>(2, 0)</code> | <code>(+1, -1)</code> |
| 3 | <code>(2, 1)</code> | <code>(+1, +1)</code> |
| 4 | <code>(0, 1)</code> | <code>(-1, +1)</code> |

Las funciones de forma bilineales son:

\[
\begin{aligned}
N_1 &= \tfrac14(1-\xi)(1-\eta), &
N_2 &= \tfrac14(1+\xi)(1-\eta),\\
N_3 &= \tfrac14(1+\xi)(1+\eta), &
N_4 &= \tfrac14(1-\xi)(1+\eta).
\end{aligned}
\]

El desplazamiento vertical interpolado es:

\[
w(\xi,\eta)=N_1w_1+N_2w_2+N_3w_3+N_4w_4.
\]

<code>w</code> puede representar la traslación transversal de una placa o
cascarón; se medirá en milímetros en los ejemplos. Las funciones \(N_i\) no
tienen unidades.

Una propiedad que siempre debe cumplirse es la **partición de la unidad**:

\[
N_1+N_2+N_3+N_4=1.
\]

---

## Ejemplo 1 — Desplazamiento en el centro del elemento

### Datos

Evaluar el punto central:

\[
\xi=0,\qquad\eta=0.
\]

Los desplazamientos nodales son:

\[
\left[w_1,w_2,w_3,w_4\right]=[0,\,2,\,4,\,2]\ \text{mm}.
\]

### Paso 1: calcular las funciones de forma

Sustituyendo <code>xi = 0</code> y <code>eta = 0</code>:

\[
N_1=\tfrac14(1-0)(1-0)=\tfrac14.
\]

De la misma manera:

\[
N_2=N_3=N_4=\tfrac14.
\]

Por tanto:

\[
\mathbf N(0,0)=
\begin{bmatrix}
0.25 & 0.25 & 0.25 & 0.25
\end{bmatrix}.
\]

### Paso 2: verificar la partición de la unidad

\[
0.25+0.25+0.25+0.25=1.00.
\]

La verificación es correcta. En el centro, los cuatro nodos influyen por
igual.

### Paso 3: interpolar el desplazamiento

\[
\begin{aligned}
w(0,0)&=0.25(0)+0.25(2)+0.25(4)+0.25(2)\\
&=0+0.5+1.0+0.5\\
&=2.0\ \text{mm}.
\end{aligned}
\]

> **Resultado:** el elemento predice \(w=2.0\ \text{mm}\) en su centro.

### Interpretación física

El resultado es el promedio de los cuatro valores nodales porque el punto está
exactamente en el centro geométrico. No es una regla general de promediar:
ocurre aquí porque los cuatro pesos \(N_i\) valen \(0.25\).

---

## Ejemplo 2 — Punto interior próximo al nodo 2

### Datos

Evaluar el punto natural:

\[
\xi=+0.5,\qquad\eta=-0.5.
\]

Para el rectángulo de \(2\ \text{m}\times1\ \text{m}\), este punto está en:

\[
x=1+\xi=1.5\ \text{m},\qquad
y=\tfrac12(1+\eta)=0.25\ \text{m}.
\]

Es decir: está cerca del nodo 2. Usemos ahora:

\[
\left[w_1,w_2,w_3,w_4\right]=[0,\,4,\,8,\,0]\ \text{mm}.
\]

### Paso 1: calcular los pesos nodales

\[
\begin{aligned}
N_1&=\tfrac14(1-0.5)(1-(-0.5))
    =\tfrac14(0.5)(1.5)=0.1875,\\
N_2&=\tfrac14(1+0.5)(1-(-0.5))
    =\tfrac14(1.5)(1.5)=0.5625,\\
N_3&=\tfrac14(1+0.5)(1+(-0.5))
    =\tfrac14(1.5)(0.5)=0.1875,\\
N_4&=\tfrac14(1-0.5)(1+(-0.5))
    =\tfrac14(0.5)(0.5)=0.0625.
\end{aligned}
\]

Así:

\[
\mathbf N(0.5,-0.5)=
\begin{bmatrix}
0.1875 & 0.5625 & 0.1875 & 0.0625
\end{bmatrix}.
\]

### Paso 2: verificar la partición de la unidad

\[
0.1875+0.5625+0.1875+0.0625=1.0000.
\]

La comprobación es correcta. El mayor peso es \(N_2=0.5625\), como debe ser:
el punto está más próximo al nodo 2.

### Paso 3: interpolar el desplazamiento

\[
\begin{aligned}
w(0.5,-0.5)
 &=0.1875(0)+0.5625(4)+0.1875(8)+0.0625(0)\\
 &=0+2.25+1.50+0\\
 &=3.75\ \text{mm}.
\end{aligned}
\]

> **Resultado:** en el punto físico \((x,y)=(1.5,0.25)\ \text{m}\), el
> elemento predice \(w=3.75\ \text{mm}\).

### Interpretación física

No se obtiene el promedio de los nodos. El valor interior es una combinación
ponderada: el nodo 2 aporta más que todos los demás por cercanía, y el nodo 3
también aporta porque comparte el borde derecho.

---

## Correspondencia directa con Python

En <code>q4_shell_mindlin.py</code>, las líneas 42--49 implementan exactamente
las cuatro expresiones anteriores:

~~~python
def shape_functions(xi, eta):
    return 0.25 * np.array([
        (1 - xi) * (1 - eta),
        (1 + xi) * (1 - eta),
        (1 + xi) * (1 + eta),
        (1 - xi) * (1 + eta),
    ])
~~~

Para verificar el segundo ejemplo en Python:

~~~python
N = shape_functions(0.5, -0.5)
w_nodal = np.array([0.0, 4.0, 8.0, 0.0])  # mm
w = N @ w_nodal

# N = [0.1875, 0.5625, 0.1875, 0.0625]
# w = 3.75 mm
~~~

El operador <code>@</code> es el producto fila por columna:

\[
w=\mathbf N\mathbf w_e.
\]

---

## Ideas que debes conservar

1. Las funciones de forma convierten cuatro valores nodales en un campo
   continuo dentro del elemento.
2. Cada \(N_i\) es el peso del nodo \(i\) en el punto evaluado.
3. En su propio nodo, una función vale 1 y las otras valen 0. Por ejemplo,
   en el nodo 2: \(N_2(+1,-1)=1\).
4. La suma de funciones de forma debe ser 1; si no lo es, hay un error de
   formulación o de cálculo.
5. La siguiente sesión derivará estas funciones respecto a \(x,y\), porque
   las deformaciones dependen de gradientes de desplazamiento, no solo de
   desplazamientos.

# Sesión 3 — De los desplazamientos Q4 a los esfuerzos principales

## Propósito

En la sesión 2 construimos el primer elemento Q4 y obtuvimos las derivadas
físicas de sus funciones de forma. En esta sesión usaremos esas derivadas para
reproducir la recuperación de esfuerzos realizada por
`analizar_contrafuertes_centrales_2d.py`.

Al finalizar podrás calcular manualmente:

1. la matriz deformación–desplazamiento \(\mathbf B\) y la matriz constitutiva
   de esfuerzo plano \(\mathbf D\);
2. las deformaciones, esfuerzos cartesianos, esfuerzos principales y su
   orientación usando desplazamientos nodales reales del modelo.

> Esta sesión contiene exactamente dos ejercicios manuales. Se estudia la
> recuperación de esfuerzos después de resolver el sistema FEM; el ensamblaje y
> la solución global se abordarán en una sesión posterior.

## 1. Punto del modelo que analizaremos

Se conserva el elemento y el punto de Gauss de la sesión anterior:

| Dato | Valor |
|---|---:|
| Contrafuerte | CF-C1 |
| Caso | Resistencia I-a |
| Elemento global | 0 |
| Conectividad | `[0, 1, 16, 15]` |
| Punto de Gauss | \(\xi=\eta=-1/\sqrt3\) |
| Coordenada física | \((x,z)=(0.0913284,0.0986183)\ \text{m}\) |
| Módulo elástico | \(E_c=24\,614.4961\ \text{MPa}\) |
| Coeficiente de Poisson | \(\nu=0.20\) |

El programa supone concreto lineal elástico no fisurado y **esfuerzo plano**:

\[
\sigma_y=\tau_{xy}=\tau_{yz}=0,
\]

donde la dirección \(y\) es perpendicular al plano \(x-z\) del contrafuerte.
Esto no significa que la deformación \(\varepsilon_y\) sea cero.

![Campo de esfuerzo principal del modelo](../../outputs/calc_est_2026_004/contrafuertes_centrales_sigma1.png)

---

## Ejercicio manual 1 — Construcción de las matrices B y D

### Enunciado

Usando las derivadas físicas obtenidas en la sesión 2, construir:

1. la matriz \(\mathbf B\) del elemento Q4 en el punto de Gauss;
2. la matriz constitutiva \(\mathbf D\) para esfuerzo plano;
3. verificar sus dimensiones, unidades y propiedades básicas.

### Paso 1: organizar las derivadas físicas

Para los nodos locales \([1,2,3,4]\):

\[
\mathbf N_{,x}=
\begin{bmatrix}
-1.8249160&1.8249160&0.4889848&-0.4889848
\end{bmatrix}\ \text{m}^{-1},
\]

\[
\mathbf N_{,z}=
\begin{bmatrix}
-1.7038757&-0.4389815&0.4565521&1.6863050
\end{bmatrix}\ \text{m}^{-1}.
\]

Las deformaciones pequeñas del continuo 2D son:

\[
\varepsilon_x=\frac{\partial u_x}{\partial x},
\qquad
\varepsilon_z=\frac{\partial u_z}{\partial z},
\qquad
\gamma_{xz}=\frac{\partial u_x}{\partial z}
+\frac{\partial u_z}{\partial x}.
\]

Se usa la deformación cortante de ingeniería \(\gamma_{xz}\), no la componente
tensorial \(\varepsilon_{xz}=\gamma_{xz}/2\).

### Paso 2: derivar el bloque de un nodo

La interpolación de desplazamientos es:

\[
u_x=\sum_iN_i u_{x,i},
\qquad
u_z=\sum_iN_i u_{z,i}.
\]

La contribución del nodo \(i\) a las deformaciones se escribe:

\[
\mathbf B_i=
\begin{bmatrix}
N_{i,x}&0\\
0&N_{i,z}\\
N_{i,z}&N_{i,x}
\end{bmatrix}.
\]

Por ejemplo, para el nodo local 1:

\[
\mathbf B_1=
\begin{bmatrix}
-1.8249160&0\\
0&-1.7038757\\
-1.7038757&-1.8249160
\end{bmatrix}\ \text{m}^{-1}.
\]

### Paso 3: ensamblar la matriz B del elemento

El vector elemental tiene ocho componentes:

\[
\mathbf u_e=
\begin{bmatrix}
u_{x,1}&u_{z,1}&u_{x,2}&u_{z,2}&
u_{x,3}&u_{z,3}&u_{x,4}&u_{z,4}
\end{bmatrix}^T.
\]

Uniendo los cuatro bloques:

\[
\boxed{
\mathbf B=
\begin{bmatrix}
-1.824916&0&1.824916&0&0.488985&0&-0.488985&0\\
0&-1.703876&0&-0.438981&0&0.456552&0&1.686305\\
-1.703876&-1.824916&-0.438981&1.824916&0.456552&0.488985&1.686305&-0.488985
\end{bmatrix}\ \text{m}^{-1}}.
\]

La relación cinemática es:

\[
\boxed{\boldsymbol\varepsilon=\mathbf B\mathbf u_e},
\qquad
\boldsymbol\varepsilon=
\begin{bmatrix}\varepsilon_x&\varepsilon_z&\gamma_{xz}\end{bmatrix}^T.
\]

Comprobación dimensional:

\[
[\mathbf B][\mathbf u_e]=\text{m}^{-1}(\text{m})=1.
\]

Las deformaciones son adimensionales.

### Paso 4: formular la matriz constitutiva de esfuerzo plano

Para un material elástico isótropo:

\[
\mathbf D=\frac{E_c}{1-\nu^2}
\begin{bmatrix}
1&\nu&0\\
\nu&1&0\\
0&0&\dfrac{1-\nu}{2}
\end{bmatrix}.
\]

El factor común es:

\[
\frac{E_c}{1-\nu^2}
=\frac{24\,614.4961}{1-0.20^2}
=25\,640.1002\ \text{MPa}.
\]

Por tanto:

\[
\boxed{
\mathbf D=
\begin{bmatrix}
25\,640.1002&5\,128.0200&0\\
5\,128.0200&25\,640.1002&0\\
0&0&10\,256.0401
\end{bmatrix}\ \text{MPa}}.
\]

El término cortante también puede comprobarse con:

\[
G=\frac{E_c}{2(1+\nu)}
=\frac{24\,614.4961}{2(1.20)}
=10\,256.0401\ \text{MPa}.
\]

### Verificaciones del ejercicio 1

| Control | Resultado |
|---|---:|
| Dimensión de \(\mathbf B\) | \(3\times8\) |
| Dimensión de \(\mathbf D\) | \(3\times3\) |
| Simetría de \(\mathbf D\) | cumple |
| \(D_{12}=\nu D_{11}\) | \(5\,128.0200\ \text{MPa}\) |
| \(D_{33}=G\) | \(10\,256.0401\ \text{MPa}\) |

Estas operaciones corresponden a `matriz_constitutiva(...)` y `matriz_b(...)`
en
[`analizar_contrafuertes_centrales_2d.py`](../../analisis_estabilidad/analizar_contrafuertes_centrales_2d.py).

### Interpretación

- \(\mathbf B\) contiene la geometría y convierte movimiento nodal en
  deformación local.
- \(\mathbf D\) contiene el comportamiento del material y convierte
  deformación en esfuerzo.
- La geometría y el material se mantienen separados hasta formar
  \(\boldsymbol\sigma=\mathbf D\mathbf B\mathbf u_e\).

---

## Ejercicio manual 2 — De desplazamientos reales a esfuerzos principales

### Enunciado

Usar los desplazamientos del elemento 0 para el caso
`CF-C1 / Resistencia I-a` y calcular:

1. \(\varepsilon_x,\varepsilon_z,\gamma_{xz}\);
2. \(\sigma_x,\sigma_z,\tau_{xz}\);
3. los esfuerzos principales \(\sigma_1,\sigma_2\);
4. el ángulo de \(\sigma_1\).

### Paso 1: construir el vector de desplazamientos

Los desplazamientos recuperados del JSON son:

| Nodo local | Nodo global | \(u_x\) (mm) | \(u_z\) (mm) |
|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 |
| 2 | 1 | 0 | 0 |
| 3 | 16 | -0.0284713 | -0.0385504 |
| 4 | 15 | -0.0382535 | -0.0629184 |

Los nodos 0 y 1 no se desplazan porque pertenecen al borde basal empotrado.
Para multiplicar por \(\mathbf B\), los milímetros se convierten a metros:

\[
\mathbf u_e=
\begin{bmatrix}
0\\0\\0\\0\\
-2.8471324\times10^{-5}\\
-3.8550447\times10^{-5}\\
-3.8253503\times10^{-5}\\
-6.2918377\times10^{-5}
\end{bmatrix}\ \text{m}.
\]

### Paso 2: calcular la deformación normal x

La primera fila de \(\mathbf B\) solo multiplica los desplazamientos
horizontales:

\[
\begin{aligned}
\varepsilon_x={}&
(0.4889848)(-2.8471324\times10^{-5})\\
&+(-0.4889848)(-3.8253503\times10^{-5})\\
={}&4.78334\times10^{-6}.
\end{aligned}
\]

En microdeformación:

\[
\boxed{\varepsilon_x=+4.783\ \mu\varepsilon}.
\]

### Paso 3: calcular la deformación normal z

La segunda fila usa los desplazamientos verticales:

\[
\begin{aligned}
\varepsilon_z={}&
(0.4565521)(-3.8550447\times10^{-5})\\
&+(1.6863050)(-6.2918377\times10^{-5})\\
={}&-1.2369986\times10^{-4}.
\end{aligned}
\]

Por tanto:

\[
\boxed{\varepsilon_z=-123.700\ \mu\varepsilon}.
\]

### Paso 4: calcular la deformación cortante

La tercera fila de \(\mathbf B\) produce:

\[
\begin{aligned}
\gamma_{xz}={}&
(0.4565521)(-2.8471324\times10^{-5})\\
&+(0.4889848)(-3.8550447\times10^{-5})\\
&+(1.6863050)(-3.8253503\times10^{-5})\\
&+(-0.4889848)(-6.2918377\times10^{-5})\\
={}&-6.5590171\times10^{-5}.
\end{aligned}
\]

Así:

\[
\boxed{\gamma_{xz}=-65.590\ \mu\varepsilon}.
\]

El vector completo es:

\[
\boxed{
\boldsymbol\varepsilon=
\begin{bmatrix}
4.78334\\-123.69986\\-65.59017
\end{bmatrix}\times10^{-6}}.
\]

### Paso 5: convertir las deformaciones en esfuerzos

La ley constitutiva es:

\[
\boldsymbol\sigma=\mathbf D\boldsymbol\varepsilon.
\]

Para \(\sigma_x\):

\[
\begin{aligned}
\sigma_x
&=25\,640.1002(4.78334\times10^{-6})\\
&\quad+5\,128.0200(-123.69986\times10^{-6})\\
&=0.122645-0.634335\\
&=\boxed{-0.511690\ \text{MPa}}.
\end{aligned}
\]

Para \(\sigma_z\):

\[
\begin{aligned}
\sigma_z
&=5\,128.0200(4.78334\times10^{-6})\\
&\quad+25\,640.1002(-123.69986\times10^{-6})\\
&=0.024529-3.171677\\
&=\boxed{-3.147148\ \text{MPa}}.
\end{aligned}
\]

Para el cortante:

\[
\tau_{xz}
=10\,256.0401(-65.59017\times10^{-6})
=\boxed{-0.672695\ \text{MPa}}.
\]

### Paso 6: calcular los esfuerzos principales

El centro del círculo de Mohr es:

\[
\sigma_{prom}=\frac{\sigma_x+\sigma_z}{2}
=\frac{-0.511690-3.147148}{2}
=-1.829419\ \text{MPa}.
\]

El radio es:

\[
\begin{aligned}
R&=\sqrt{\left(\frac{\sigma_x-\sigma_z}{2}\right)^2+\tau_{xz}^2}\\
&=1.479503\ \text{MPa}.
\end{aligned}
\]

Entonces:

\[
\boxed{\sigma_1=\sigma_{prom}+R=-0.349916\ \text{MPa}},
\]

\[
\boxed{\sigma_2=\sigma_{prom}-R=-3.308922\ \text{MPa}}.
\]

Aquí \(\sigma_1\) es el esfuerzo principal **mayor algebraicamente**, aunque
sea negativo. Ambos esfuerzos principales son de compresión en este punto.

### Paso 7: calcular la orientación principal

El programa emplea:

\[
\theta_1=\frac12\operatorname{atan2}
\left(2\tau_{xz},\sigma_x-\sigma_z\right).
\]

Sustituyendo:

\[
\theta_1
=\frac12\operatorname{atan2}
\left(2(-0.672695),-0.511690-(-3.147148)\right)
=\boxed{-13.5221^\circ}.
\]

El signo negativo indica un giro horario desde el eje \(+x\), de acuerdo con
la convención matemática utilizada por `atan2`.

### Comparación con el JSON

| Resultado | Manual | JSON |
|---|---:|---:|
| \(\varepsilon_x\) | \(+4.78334\times10^{-6}\) | no se almacena |
| \(\varepsilon_z\) | \(-1.2369986\times10^{-4}\) | no se almacena |
| \(\gamma_{xz}\) | \(-6.5590171\times10^{-5}\) | no se almacena |
| \(\sigma_x\) | -0.511690 MPa | -0.511690 MPa |
| \(\sigma_z\) | -3.147148 MPa | -3.147148 MPa |
| \(\tau_{xz}\) | -0.672695 MPa | -0.672695 MPa |
| \(\sigma_1\) | -0.349916 MPa | -0.349916 MPa |
| \(\sigma_2\) | -3.308922 MPa | -3.308922 MPa |
| \(\theta_1\) | -13.5221° | -13.5221° |

Esta cadena reproduce `_esfuerzos_gauss(...)` en el script de análisis.

## 2. Lectura estructural del resultado

- Cerca de la unión con la zapata, este punto particular está en compresión
  biaxial; no debe confundirse con las zonas positivas de \(\sigma_1\) que
  orientan la trayectoria del tirante.
- El valor \(\sigma_2=-3.309\ \text{MPa}\) identifica la compresión principal
  más intensa del punto.
- Un mapa llamado `sigma1` no implica que todos sus valores sean tracciones:
  \(\sigma_1\) puede ser negativo si los dos principales son compresivos.
- Los esfuerzos se calculan en cuatro puntos de Gauss por elemento; no en los
  nodos.
- Los picos próximos a cargas nodales y empotramientos dependen de la malla. El
  programa reporta también percentiles para evitar interpretar un único pico
  como una demanda global de diseño.

## 3. Errores frecuentes

1. Introducir desplazamientos en milímetros mientras \(\mathbf B\) está en
   \(\text{m}^{-1}\). Deben convertirse a metros.
2. Usar una matriz de deformación plana. El script adopta esfuerzo plano.
3. Colocar \(N_{i,x}\) y \(N_{i,z}\) en columnas equivocadas de \(\mathbf B\).
4. Usar \(2G\) en la tercera diagonal de \(\mathbf D\). Con
   \(\gamma_{xz}\) de ingeniería corresponde \(G\).
5. Ordenar los desplazamientos por número global en lugar del orden local
   `[0, 1, 16, 15]`.
6. Interpretar siempre \(\sigma_1\) como tracción. Es el principal mayor, no
   necesariamente positivo.
7. Confundir \(\theta\) con el ángulo de la biela STM. Este ángulo describe la
   dirección principal local del campo elástico FEM.

## 4. Autoevaluación

1. ¿Qué información aporta \(\mathbf B\) y qué información aporta
   \(\mathbf D\)?
2. ¿Por qué los cuatro primeros términos de \(\mathbf u_e\) son cero?
3. ¿Qué ocurriría con los esfuerzos si todos los desplazamientos se
   multiplicaran por dos en este análisis lineal?
4. ¿Puede \(\sigma_1\) ser negativo? ¿Qué significa?

Respuestas esperadas:

1. \(\mathbf B\) representa la geometría y los gradientes; \(\mathbf D\), la
   relación constitutiva del material;
2. porque los nodos 0 y 1 pertenecen al borde basal empotrado;
3. las deformaciones y los esfuerzos también se duplicarían;
4. sí; significa que incluso el esfuerzo principal algebraicamente mayor es
   compresivo.

## 5. Puente hacia la sesión 4

Hasta ahora hemos partido de desplazamientos ya resueltos. La siguiente sesión
explicará cómo se obtiene la matriz de rigidez elemental:

\[
\mathbf k_e=\sum_{p=1}^{4}
\mathbf B_p^T\mathbf D\mathbf B_p\,t\,\det(\mathbf J_p),
\]

cómo se ensambla en la matriz global, cómo se aplican las restricciones de la
base y cómo se verifica el equilibrio entre cargas y reacciones.

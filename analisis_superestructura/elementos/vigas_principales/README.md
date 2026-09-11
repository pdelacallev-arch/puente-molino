# Vigas principales compuestas - MTC 2018

Sistema reproducible para analizar y verificar vigas I de placas soldadas, rectas y simplemente apoyadas, con tablero de concreto. Sigue la secuencia de Bartra (pp. impresas 113-165), actualizada al Manual de Puentes MTC 2018.

Consulte el [manual de uso](../../documentos/vigas_principales/MANUAL_USO.md) para la instalación, preparación del YAML, ejecución e interpretación de resultados.

## Alcance

Incluye propiedades no compuestas y compuestas, ancho efectivo, cargas por etapa, HL-93, distribución lateral, combinaciones LRFD, flexión positiva, corte, servicio, fatiga, estabilidad durante construcción, deflexiones, contraflecha y búsqueda discreta por peso.

No diseña conectores, rigidizadores ni diafragmas. Si sus validaciones externas están pendientes, el resultado no puede ser `CUMPLE`; se reporta `CONDICIONAL` o `NO_CUMPLE`.

## Unidades de entrada

El YAML declara `proyecto.sistema_unidades`:

- `SI`: geometría global en m, placas en mm, fuerzas en kN, cargas lineales en kN/m, pesos unitarios en kN/m3 y esfuerzos en MPa.
- `MKS`: geometría global en m, placas en mm, fuerzas en tf, cargas lineales en tf/m, pesos unitarios en tf/m3 y esfuerzos en kgf/cm2.

El cálculo interno usa N-mm-MPa. No se admiten unidades mezcladas dentro de un archivo.
Active `analisis.reportar_mks: true` para añadir equivalencias en tf, tf.m y kgf/cm2 al JSON y la memoria.

## Uso

Desde la raíz del repositorio:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_superestructura.elementos.vigas_principales validate analisis_superestructura/casos/bartra/R00/entrada.yaml
uv run python -m analisis_superestructura.elementos.vigas_principales analyze analisis_superestructura/casos/bartra/R00/entrada.yaml
uv run python -m analisis_superestructura.elementos.vigas_principales design analisis_superestructura/casos/bartra/R00/entrada.yaml
```

Los productos se escriben dentro de la carpeta del caso, junto a `entrada.yaml`,
en `casos/<caso>/<revision>/ejecuciones/<id>/elementos/vigas_principales/<calculo>/`:

- `entrada.json`: configuración resuelta e identificadores de la ejecución.
- `resultado.json`: contrato con estado, resultados y huellas de archivos.
- `reporte.md`: memoria automática del cálculo.
- `envolventes.csv`: resultados por estación, para análisis y diseño.
- `figuras/*.png`: diagramas de acciones, envolventes, combinaciones y DCR.
- `busqueda.json`, `diseno_optimo.json` y `memoria_optima.md`: cuando la búsqueda está habilitada.

Si el YAML está fuera de `casos/`, se conserva la salida histórica en
`outputs/vigas_principales/<proyecto>/<revision>/`.

## Búsqueda

Para habilitarla, complete las seis listas de dimensiones y, opcionalmente, los grupos de segmentos. Los índices son base cero. Los segmentos de un mismo grupo reciben la misma combinación, permitiendo imponer simetría.

```yaml
busqueda:
  habilitada: true
  peraltes_alma: [1800, 1900, 2000]
  espesores_alma: [14, 16]
  anchos_ala_superior: [400, 450]
  espesores_ala_superior: [25, 32]
  anchos_ala_inferior: [450, 500]
  espesores_ala_inferior: [25, 38, 50]
  grupos:
    - segmentos: [0, 4]
    - segmentos: [1, 3]
    - segmentos: [2]
  maximo_candidatos: 20000
  mejores_alternativas: 10
```

## Limitaciones técnicas

- Los factores MTC aproximados se marcan con advertencia fuera de sus rangos; en esos casos se requiere contraste con análisis refinado.
- La estabilidad lateral durante construcción es un cribado elástico conservador con `Cb=1.0`, no reemplaza un modelo de montaje.
- La fatiga se verifica contra el umbral de amplitud constante de la categoría suministrada; la categoría debe corresponder al detalle fabricado.
- La capacidad de corte se calcula sin acción de campo de tensión. Los rigidizadores permanecen fuera de alcance.
- El ejemplo Molinohuayco es preliminar porque el expediente contiene geometrías y cargas contradictorias.

Todo resultado requiere revisión y aprobación del ingeniero estructural responsable.

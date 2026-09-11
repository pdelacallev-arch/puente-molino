# Análisis de estabilidad por elementos estructurales

Subsistema autocontenido para el análisis y diseño del estribo del Puente
Molinohuayco. Los parámetros se conservan en un YAML maestro y los elementos
se comunican mediante contratos JSON verificables.

Para una explicación progresiva, ejemplos completos y solución de errores,
consulte la [guía de uso para estudiantes](GUIA_USO_ESTUDIANTE.md).

## Organización

| Elemento | Cálculos |
|---|---|
| Estribo | estabilidad global e interfaces de contacto |
| Pantalla | shell 3D, transferencia a contrafuertes y diseño E.060/MTC |
| Contrafuertes | FEM 2D y diseño STM |
| Zapata | diseño longitudinal y transversal |
| Dentellón | diseño E.060 y presiones |
| Cajuela | verificación del voladizo y cargas |

`nucleo/` sólo contiene configuración, contratos, rutas y orquestación. Los
motores y representaciones permanecen dentro de la carpeta de su elemento.

## Fuente de entrada

La configuración vigente está en:

```text
casos/molinohuayco/R02/entrada.yaml
```

Puede añadirse un ajuste particular en:

```text
casos/molinohuayco/R02/entradas/<elemento>/<calculo>.override.json
```

El override JSON tiene prioridad sobre la sección correspondiente del YAML.
La entrada resuelta e inmutable de cada cálculo queda registrada junto a su
resultado.

## Uso

Desde la raíz del proyecto:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_estabilidad validar --caso molinohuayco --revision R02
uv run python -m analisis_estabilidad ejecutar zapata.longitudinal --caso molinohuayco --revision R02
uv run python -m analisis_estabilidad ejecutar contrafuertes.diseno --caso molinohuayco --revision R02
uv run python -m analisis_estabilidad ejecutar todo --caso molinohuayco --revision R02
uv run python -m analisis_estabilidad consolidar --caso molinohuayco --revision R02
```

El orquestador ejecuta automáticamente las dependencias técnicas. Una misma
huella de configuración y código continúa la ejecución compatible; cualquier
cambio crea otra carpeta fechada.

El modelo shell factoriza una sola vez la matriz restringida y reutiliza esa
factorización en todos los casos de carga. El objetivo
`pantalla.reacciones_contrafuertes` deriva sus datos del resultado
`pantalla.analisis_shell_3d`, por lo que no repite el FEM ni sus figuras.

## Ejecución independiente

Cada paquete estructural admite una entrada y salida explícitas:

```powershell
uv run python -m analisis_estabilidad.elementos.zapata `
  diseno_longitudinal_e060 `
  --entrada analisis_estabilidad/casos/molinohuayco/R02/ejecuciones/<id>/elementos/zapata/diseno_longitudinal_e060/entrada.json `
  --salida analisis_estabilidad/.tmp/zapata_independiente
```

El módulo sólo consume su `entrada.json` y los `resultado.json` declarados en
ella. Verifica identidad, esquema y SHA-256 antes de calcular.

## Contrato de archivos

Cada cálculo produce:

```text
elementos/<elemento>/<calculo>/
├── entrada.json
├── resultado.json
├── reporte.md
└── figuras/
    ├── *.png
    └── *.svg  # cuando el módulo dispone de salida vectorial
```

Las figuras son un posprocesamiento del mismo resultado estructural; no repiten
el análisis. Sus rutas quedan registradas en `resultado.json`, dentro de
`archivos_generados`.

No se admiten entradas ni salidas fuera de `analisis_estabilidad/`. Los
resultados históricos anteriores a este sistema se conservan en `historico/`.

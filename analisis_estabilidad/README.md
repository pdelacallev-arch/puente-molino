# Análisis de estabilidad por elementos estructurales

Subsistema autocontenido para el análisis y diseño del estribo del Puente
Molinohuayco. Los parámetros se conservan en un YAML maestro y los elementos
se comunican mediante contratos JSON verificables.

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
casos/molinohuayco/R00/entrada.yaml
```

Puede añadirse un ajuste particular en:

```text
casos/molinohuayco/R00/entradas/<elemento>/<calculo>.override.json
```

El override JSON tiene prioridad sobre la sección correspondiente del YAML.
La entrada resuelta e inmutable de cada cálculo queda registrada junto a su
resultado.

## Uso

Desde la raíz del proyecto:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_estabilidad validar --caso molinohuayco --revision R00
uv run python -m analisis_estabilidad ejecutar zapata.longitudinal --caso molinohuayco --revision R00
uv run python -m analisis_estabilidad ejecutar contrafuertes.diseno --caso molinohuayco --revision R00
uv run python -m analisis_estabilidad ejecutar todo --caso molinohuayco --revision R00
uv run python -m analisis_estabilidad consolidar --caso molinohuayco --revision R00
```

El orquestador ejecuta automáticamente las dependencias técnicas. Una misma
huella de configuración y código continúa la ejecución compatible; cualquier
cambio crea otra carpeta fechada.

## Ejecución independiente

Cada paquete estructural admite una entrada y salida explícitas:

```powershell
uv run python -m analisis_estabilidad.elementos.zapata `
  diseno_longitudinal_e060 `
  --entrada analisis_estabilidad/casos/molinohuayco/R00/ejecuciones/<id>/elementos/zapata/diseno_longitudinal_e060/entrada.json `
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
└── reporte.md
```

No se admiten entradas ni salidas fuera de `analisis_estabilidad/`. Los
resultados históricos anteriores a este sistema se conservan en `historico/`.


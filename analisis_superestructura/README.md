# Análisis de superestructura por elementos

Subsistema modular para analizar y diseñar los elementos de la superestructura
del Puente Molinohuayco. La organización replica el criterio de
`analisis_estabilidad`: el núcleo sólo resuelve rutas y despacha cálculos; cada
elemento conserva su formulación, modelos, verificaciones y reportes.

## Organización

```text
analisis_superestructura/
├── nucleo/                         # registro, rutas y orquestación común
├── elementos/
│   └── vigas_principales/          # motor técnico actualmente disponible
├── casos/
│   ├── bartra/R00/entrada.yaml
│   └── molinohuayco/<revision>/entrada.yaml
├── pruebas/                        # pruebas del subsistema
├── documentos/                     # manuales, metrados y notebooks
└── historico/                      # resultados anteriores, sin uso operativo
```

Los elementos futuros deben añadirse en `elementos/<elemento>/` y registrarse
en `nucleo/motores.py`. No deben incorporar lógica técnica en `nucleo/` ni usar
archivos de otro elemento sin una interfaz explícita.

## Uso general

Desde la raíz del repositorio:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run python -m analisis_superestructura objetivos
uv run python -m analisis_superestructura validar --elemento vigas_principales --caso bartra --revision R00
uv run python -m analisis_superestructura ejecutar vigas_principales.analisis --caso bartra --revision R00
uv run python -m analisis_superestructura ejecutar vigas_principales.diseno --caso molinohuayco --revision PRELIMINAR-R00
uv run python -m analisis_superestructura ejecutar todo --caso molinohuayco --revision PRELIMINAR-R00
uv run python -m analisis_superestructura consolidar --caso molinohuayco --revision PRELIMINAR-R00
uv run python -m analisis_superestructura estado --caso molinohuayco --revision PRELIMINAR-R00
```

Una misma huella de configuración y de código reutiliza la carpeta de ejecución
compatible; cualquier cambio crea otra carpeta fechada. `ejecutar todo` recorre
todos los objetivos aplicables y omite los que la configuración no habilita,
como `vigas_principales.busqueda` cuando `busqueda.habilitada` es `false`.

## Resultados

Los resultados se guardan dentro de la carpeta del caso, junto a `entrada.yaml`,
replicando la organización de `analisis_estabilidad`:

```text
casos/<caso>/<revision>/ejecuciones/<id>/
├── configuracion_resuelta.yaml
├── manifiesto.json
├── consolidado.json               # tras `consolidar`
├── indice.json                    # en ejecuciones/
└── elementos/<elemento>/<calculo>/
    ├── entrada.json
    ├── resultado.json
    ├── reporte.md
    ├── envolventes.csv            # solo cálculos de viga
    └── figuras/
        └── *.png
```

La carpeta `ejecuciones/indice.json` relaciona cada huella con su ejecución. El
manifiesto registra estado, entradas, resultados y huellas SHA-256 de cada
módulo. El comando histórico `analisis_superestructura.elementos.vigas_principales`
sigue disponible y, cuando el YAML pertenece a un caso, escribe en la misma
carpeta de ejecución.

## Elemento disponible

Las capacidades, hipótesis y limitaciones de las vigas principales están en su
[README técnico](elementos/vigas_principales/README.md). La guía detallada está
en [documentos/vigas_principales/MANUAL_USO.md](documentos/vigas_principales/MANUAL_USO.md).


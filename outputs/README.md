# Índice de resultados externos a estabilidad

Los resultados del subsistema de estabilidad fueron trasladados a
`analisis_estabilidad/casos/` y su histórico a
`analisis_estabilidad/historico/`.

Los resultados de la superestructura (vigas principales) se guardan ahora
dentro de la carpeta del caso, junto a `entrada.yaml`:

```text
analisis_superestructura/casos/<caso>/<revision>/ejecuciones/<id>/elementos/vigas_principales/<calculo>/
```

Esta carpeta conserva únicamente comparaciones y reportes sueltos de apoyo.

## Estructura

| Archivo | Contenido |
|---|---|
| `reporte_comparativo_vigas_molinohuayco.md` | Comparación de alternativas de sección de vigas |
| `comparacion_secciones_vigas.png` | Figura de apoyo del reporte comparativo |

## Convenciones

- `*.md`: informes legibles y trazabilidad del cálculo.
- `*.json`: resultados estructurados para reprocesamiento.
- `*.png` y `*.svg`: figuras y láminas generadas.
- `*.xlsx`: hoja de apoyo del recálculo de falsa zapata.

Los programas de `analisis_estabilidad` no deben leer ni escribir aquí.

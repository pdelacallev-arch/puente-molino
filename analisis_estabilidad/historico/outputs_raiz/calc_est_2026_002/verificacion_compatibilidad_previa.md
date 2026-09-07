# Verificación de compatibilidad previa — CALC-EST-2026-002-R00

**Fecha:** 31/07/2026  
**Estado:** apto para ejecución con salvedades documentadas

| Comprobación | Desarrollo | Resultado |
|---|---|---|
| Altura total | `H = hp + hz = 13.15 + 1.50 = 14.65 m` | Compatible |
| Ancho de zapata | `B = B2 + tp2 + B1 = 5.10 + 0.75 + 6.10 = 11.95 m` | Compatible |
| Falsa zapata en planta | `B_fz = 11.95 m = B` | Compatible con el modelo rígido sin vuelo |
| Profundidad del dentellón | `h_d = 1.50 m < h_fz = 3.74 m` | Cabe dentro de la altura modelada de falsa zapata |
| Espesor útil del dentellón | `t_d = 0.70 m`; con recubrimiento de 75 mm y barra de control de 25.4 mm, `d > 0` | Compatible |
| Sistema de unidades | `tf`, `m`, `tf·m`, `kgf/cm²`, `cm²/m` | Compatible con todos los módulos |
| Encadenamiento | Zapata y dentellón importan `GEOM`, `MAT`, `LOADS`, `SEISMIC` y `FALSE_FOOTING` del agente | Consistente |

## Salvedades previas

- La altura `H = 14.65 m` es un dato proporcionado para el caso alternativo. Se adopta `hp = 13.15 m` porque la zapata mantiene `hz = 1.50 m`.
- La geometría horizontal restante, los materiales, las cargas, la falsa zapata y los factores se mantienen iguales a la memoria anterior.
- La falsa zapata está documentada como concreto `f'c = 140 kg/cm² + 50 % P.G.`. El módulo del dentellón calcula una ley pasiva de Rankine para medio granular; por tanto, el medio pasivo no se marcará como confirmado.
- No se ha acreditado una abertura previa ni un sistema de anclaje postinstalado. El cálculo se ejecutará como conexión postinstalada no confirmada y la transferencia en la junta quedará pendiente.
- Como el modelo anterior ya cerraba el deslizamiento sin aporte del dentellón, su resistencia pasiva no se necesita para declarar la estabilidad global del caso analizado.
- La capacidad portante factorizada, el comportamiento estructural tridimensional de la falsa zapata y la representación de contrafuertes permanecen fuera del alcance.

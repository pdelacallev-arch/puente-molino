---
name: subestructura-puentes
description: Analisis paso a paso de subestructura de puentes aplicado al Puente Molinohuaico
license: MIT
compatibility: opencode
metadata:
  project: puente-molinohuaico
---

Activa al agente `ingeniero-subestructura` para aplicar, paso a paso, la metodología de `analisis_subestructura.md` al análisis de la subestructura del Puente Molinohuaico/Molinohuaycco.

## Cuándo usar

Usa esta skill cuando el usuario pida:

- Adoptar la metodología de análisis de subestructura de la referencia.
- Desarrollar la memoria de cálculo de estribos, aletas o cimentación.
- Calcular empujes de Coulomb o Mononobe-Okabe.
- Revisar estabilidad al volteo, deslizamiento o capacidad portante.
- Coordinar una secuencia de cálculo en Markdown.
- Generar scripts Python para apoyar el cálculo.

## Archivos

- Agente: `.opencode/agents/ingeniero-subestructura.md`
- Referencia: `analisis_subestructura.md`
- Memoria viva: `memoria_subestructura_molinohuaico.md`
- Script auxiliar: `agente_subestructura.py`
- Figuras: `referencias/figuras_analisis_subestructura/`

## Flujo de trabajo

1. Leer `analisis_subestructura.md` para reconocer la secuencia.
2. Leer o crear `memoria_subestructura_molinohuaico.md`.
3. Detectar el primer paso no cerrado.
4. Ejecutar solo ese paso con datos confirmados o supuestos marcados.
5. Actualizar la memoria Markdown.
6. Generar o actualizar scripts Python solo si ayudan a verificar o automatizar el paso.
7. Pedir confirmación del usuario antes de cerrar datos críticos.

## Secuencia base

1. Alcance y datos disponibles.
2. Cajuela.
3. Geometría del estribo.
4. Cargas verticales estabilizadoras.
5. Reacciones de superestructura.
6. Parámetros sísmicos.
7. Empujes de tierra estáticos.
8. Empujes de tierra sísmicos.
9. Servicio I.
10. Resistencia I-a.
11. Resistencia I-b.
12. Evento Extremo I.
13. Capacidad de carga.
14. Conclusiones y pendientes.

## Reglas

- La memoria Markdown es la fuente de coordinación.
- El script Python es auxiliar, no sustituye la memoria.
- Todo supuesto debe quedar marcado como `asumido preliminar`.
- Todo dato tomado de una memoria, plano o PDF debe citar archivo y, si es posible, página o sección.
- No se declara cumplimiento definitivo mientras haya datos críticos pendientes.
- Mantener unidades MKS salvo instrucción contraria: t, m, t-m, kg/cm2.

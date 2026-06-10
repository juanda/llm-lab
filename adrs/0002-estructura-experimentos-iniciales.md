# ADR-0002

Estado: reemplazada por ADR-0005.

## Decisión

Organizar los primeros experimentos como carpetas numeradas en `experiments/` y guardar las ejecuciones como JSONL en `results/`.

## Contexto

El módulo 0 necesita experimentos reproducibles que puedan ejecutarse con modelos locales en Ollama y compararse entre repeticiones.

## Justificación

Las carpetas numeradas mantienen el orden del plan de laboratorio. JSONL permite registrar una muestra por línea, anexar ejecuciones nuevas y analizar los resultados con herramientas simples de consola o Python.

## Consecuencias

Cada experimento debe documentar hipótesis, variables, ejecución, observaciones y conclusiones. Los scripts deben incluir metadatos suficientes para reproducir las condiciones básicas de ejecución.

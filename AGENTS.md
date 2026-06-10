# AGENTS

Este repositorio es un curso-laboratorio práctico para entender LLMs mediante experimentación local con Ollama. El objetivo no es producir documentación teórica aislada, sino módulos didácticos que conecten conceptos, hipótesis, experimentos reproducibles, observaciones y conclusiones.

## Principios

1. Toda afirmación técnica debe poder verificarse experimentalmente o quedar marcada como hipótesis, inferencia o limitación.
2. Cada módulo debe incluir `## Conceptos`, `## Hipótesis`, `## Experimentos`, `## Observaciones` y `## Conclusiones`.
3. Los experimentos se documentan dentro de la sección `## Experimentos` del módulo correspondiente. No recrear el directorio `experiments/`.
4. Los resultados generados se guardan como JSONL en `results/<id-experimento>/`.
5. Registrar decisiones estructurales o metodológicas relevantes en `adrs/`.
6. Priorizar modelos locales ejecutables con Ollama y scripts basados en la biblioteca estándar de Python.

## Enfoque Didáctico

- Mantener el hilo conductor: un LLM predice el siguiente token a partir de una secuencia de tokens.
- Distinguir siempre modelo, runtime, template, system prompt, stop tokens, parámetros y hardware.
- Evitar antropomorfismos y explicaciones que sugieran memoria humana, búsqueda interna o razonamiento simbólico si el experimento no lo demuestra.
- Separar explícitamente lo observado de lo inferido.
- Introducir conceptos en el orden del plan: no usar RAG, agentes, tool calling, fine tuning o interpretabilidad avanzada antes de que el módulo los haya preparado.

## Estructura

- `docs/00-plan-estudios.md`: mapa del curso.
- `docs/modules/`: módulos del curso.
- `scripts/`: utilidades reproducibles para Ollama.
- `results/`: datos experimentales JSONL.
- `references/`: bibliografía, Modelfiles e información de modelos.
- `adrs/`: decisiones de arquitectura y metodología.
- `.codex/skills/`: skills locales para trabajar en este repo.

## Reglas Para Experimentos

Al añadir o modificar un experimento, documentar:

- pregunta experimental;
- hipótesis;
- variables independientes, controladas y observadas;
- modelo o modelos usados;
- prompt visible;
- prompt real inferido cuando aplique;
- template, system prompt, stop tokens y modo `raw` cuando sean relevantes;
- parámetros de generación (`temperature`, `num_predict`, `num_ctx`, etc.);
- ruta de resultados en `results/<id-experimento>/`;
- criterios de observación y límites de interpretación.

Los scripts deben escribir registros JSONL con metadatos suficientes para reproducir las condiciones básicas. No sobrescribir resultados existentes salvo petición explícita.

## Reglas Para Módulos

Al desarrollar un módulo:

- empezar por el objetivo y el alcance;
- declarar qué temas quedan fuera del módulo;
- avanzar de conceptos simples a conceptos dependientes;
- incluir experimentos ejecutables con Ollama cuando sea posible;
- añadir tablas de registro cuando ayuden a observar sin inventar datos;
- terminar con conclusiones que no excedan lo observado.

## Validación

Antes de cerrar cambios:

- revisar referencias rotas con `rg`;
- ejecutar `git diff --check`;
- si se modifican scripts, ejecutar al menos una validación local del script o explicar por qué no se pudo;
- si se crean skills, validarlas con `quick_validate.py`.

# 001-anatomia-llm

## Pregunta

¿Qué hay realmente dentro de un LLM y cómo transforma texto en predicciones de tokens?

## Hipótesis

1. El texto visible se transforma en tokens antes de llegar al modelo.
2. Modelos distintos pueden tokenizar y procesar de forma distinta el mismo texto.
3. Propiedades como arquitectura, parámetros, context length, embedding length y cuantización son observables con Ollama.
4. Modelos de distinto tamaño pueden producir diferencias observables en respuesta, latencia y métricas de generación.
5. La generación autoregresiva se observa como una secuencia incremental de tokens o fragmentos, no como una frase completa producida de una vez.
6. Cambios en sampling pueden cambiar la salida aunque el modelo y el prompt visible sean los mismos.
7. `raw=true` modifica la secuencia de entrada construida por el runtime, no el mecanismo interno del Transformer.

## Experimento 001A - Tokenización comparada

Objetivo: observar que distintos textos se dividen en tokens de forma no intuitiva.

Textos:

```text
El cielo es azul.
LearningML
inteligencia artificial
def fibonacci(n):
¡Hola! ¿Qué tal?
```

Registro:

| Texto | Modelo | `prompt_eval_count` | Tokens aproximados | Observaciones |
| --- | --- | --- | --- | --- |
| El cielo es azul. | | | | |
| LearningML | | | | |
| inteligencia artificial | | | | |
| def fibonacci(n): | | | | |
| ¡Hola! ¿Qué tal? | | | | |

Limitación: Ollama no expone necesariamente la lista exacta de tokens en la API usada por este laboratorio. Si solo se dispone de `prompt_eval_count`, registrar el conteo y no inventar tokens. La inspección exacta puede hacerse más adelante con tokenizers de Hugging Face específicos para cada modelo.

## Experimento 001B - Parámetros del modelo

Objetivo: extraer información observable del modelo.

Comandos directos:

```bash
ollama show qwen2.5-coder:0.5b
ollama show qwen2.5-coder:3b
ollama show llama3.2:3b
```

Script:

```bash
python3 scripts/model_inventory.py \
  --models qwen2.5-coder:0.5b qwen2.5-coder:3b llama3.2:3b
```

Registrar:

| Modelo | Arquitectura | Parámetros | Context length | Embedding length | Cuantización | Capacidades |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | | | | | | |
| qwen2.5-coder:3b | | | | | | |
| llama3.2:3b | | | | | | |

## Experimento 001C - Mismo prompt, modelos de distinto tamaño

Objetivo: comparar cómo cambia la salida entre modelos pequeños y algo mayores.

Prompt base:

```text
Explica en una frase qué es un token en un LLM.
```

Modelos:

- `qwen2.5-coder:0.5b`;
- `qwen2.5-coder:3b`;
- `llama3.2:3b`.

Script:

```bash
python3 scripts/compare_models.py \
  --models qwen2.5-coder:0.5b qwen2.5-coder:3b llama3.2:3b \
  --prompt "Explica en una frase qué es un token en un LLM."
```

Registrar:

| Modelo | Respuesta | Longitud | Claridad observada | Tiempo | `eval_count` |
| --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:0.5b | | | | | |
| qwen2.5-coder:3b | | | | | |
| llama3.2:3b | | | | | |

La claridad es una observación cualitativa. Debe justificarse con criterios concretos: exactitud, concisión, ausencia de contradicciones y adecuación al prompt.

## Experimento 001D - Autoregresión observada

Objetivo: reutilizar `000-next-token` para observar cómo la respuesta se construye paso a paso.

Prompt:

```text
El cielo es
```

Modo chat/template:

```bash
python3 scripts/run_next_token.py \
  --model qwen2.5-coder:3b \
  --prompt "El cielo es" \
  --num-predict 16 \
  --temperature 0.2
```

Modo raw:

```bash
python3 scripts/run_next_token.py \
  --model qwen2.5-coder:3b \
  --prompt "El cielo es" \
  --num-predict 16 \
  --temperature 0.2 \
  --raw
```

Registrar:

- fragmentos de streaming;
- respuesta final;
- `prompt_eval_count`;
- `eval_count`;
- diferencias entre modo chat/template y raw;
- inferencia sobre la secuencia real de entrada.
- diferencia entre una predicción local de token y la respuesta completa acumulada.

Nota metodológica:

```text
raw ≠ modo interno diferente
```

Cuando se usa `raw=true`, Ollama construye una secuencia de entrada más directa. El modelo sigue haciendo lo mismo: recibe tokens y predice el siguiente token.

## Resultados

Los scripts guardan resultados en:

```text
results/001-anatomia-llm/
```

Archivos esperados:

- inventario de modelos en JSONL;
- comparación de respuestas en JSONL;
- notas manuales sobre tokenización si se usan herramientas externas.

## Observaciones

Anotar:

- métricas ausentes o `null`;
- modelos no disponibles localmente;
- diferencias de tokenizer inferidas por conteos;
- diferencias de latencia entre primera ejecución y ejecuciones posteriores;
- diferencias que podrían deberse a template o system prompt.
- diferencias que podrían deberse a sampling;
- errores conceptuales evitados durante la interpretación.

## Conclusiones

Completar después de ejecutar los experimentos. La conclusión debe distinguir entre:

- información observable directamente con Ollama;
- comportamiento observado en respuestas;
- inferencias razonables;
- limitaciones del método.

Lección central:

```text
Un LLM transforma secuencias de tokens en predicciones del siguiente token.
```

Lecciones adicionales:

- una respuesta completa emerge por repetición de muchas predicciones locales;
- un embedding es un vector aprendido, no una definición simbólica;
- el runtime no siempre elige el token más probable;
- el comportamiento depende tanto de los pesos como de la secuencia de entrada construida por el sistema.

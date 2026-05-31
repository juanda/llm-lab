# 000-template-vs-raw

## Pregunta

¿Por qué dos modelos generan respuestas radicalmente distintas para el mismo prompt visible?

## Hipótesis

Dos modelos pueden producir respuestas distintas ante el mismo prompt visible porque el prompt real recibido por cada modelo puede incluir chat templates, system prompts, tokens especiales, stop tokens y parámetros diferentes.

## Conceptos

Este experimento compara dos modos de entrada en Ollama:

- `template_chat`: Ollama aplica la plantilla normal del modelo.
- `raw`: el script envía `"raw": true` para omitir la plantilla de chat.

El prompt visible se mantiene fijo:

```text
El cielo es
```

La diferencia observada no se atribuye automáticamente al modelo. La conclusión debe considerar:

- modelo;
- template;
- system prompt;
- stop tokens;
- runtime;
- parámetros de generación.

## Variables

- Variable independiente: modo de generación (`template_chat` o `raw`).
- Variables controladas: prompt, `temperature`, `num_predict`, runtime local.
- Variables comparadas: modelo (`qwen2.5-coder:3b`, `llama3.2:3b`).
- Variables observadas: tokens generados reportados por Ollama, respuesta final, latencia y diferencias cualitativas.

## Ejecución

Desde la raíz del repositorio:

```bash
python3 scripts/run_template_vs_raw.py
```

Ejecución explícita:

```bash
python3 scripts/run_template_vs_raw.py \
  --models qwen2.5-coder:3b llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 24 \
  --temperature 0.2
```

El script crea resultados en:

```text
results/000-template-vs-raw/
```

Cada registro JSONL incluye:

- `model`;
- `variant`;
- `raw`;
- `prompt`;
- `options`;
- `eval_count`;
- `response`;
- métricas de duración reportadas por Ollama.

## Inspección previa

Antes de interpretar los resultados, exportar la información de los modelos:

```bash
python3 scripts/show_model_info.py qwen2.5-coder:3b llama3.2:3b
python3 scripts/export_modelfile.py qwen2.5-coder:3b llama3.2:3b
```

Los archivos se guardan en:

```text
references/models/
```

## Registro

| Modelo | Modo | Tokens generados (`eval_count`) | Respuesta final | Diferencias observadas |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:3b | template_chat | | | |
| qwen2.5-coder:3b | raw | | | |
| llama3.2:3b | template_chat | | | |
| llama3.2:3b | raw | | | |

## Observaciones

Anotar:

- si la salida parece una continuación textual o una respuesta de asistente;
- si el idioma cambia;
- si la respuesta se detiene por un stop token;
- si `eval_count` difiere entre modo chat y modo raw;
- qué diferencias aparecen en los Modelfiles.

## Conclusiones

La conclusión debe separar observación e interpretación. Una respuesta distinta no demuestra por sí sola que un modelo sea mejor o peor: muestra que, bajo estas condiciones, el sistema completo generó una salida distinta.

Principio recurrente:

```text
No estamos observando únicamente el modelo.

Estamos observando:

Modelo
+
Chat Template
+
System Prompt
+
Stop Tokens
+
Runtime
+
Parámetros
```

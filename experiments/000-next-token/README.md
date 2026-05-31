# 000-next-token

## Pregunta

¿Qué se observa cuando un LLM genera una respuesta corta paso a paso?

¿Por qué dos modelos generan continuaciones radicalmente distintas para el mismo prompt visible?

## Hipótesis

Un LLM genera texto prediciendo sucesivamente el siguiente token. El texto final emerge de una cadena de decisiones locales de generación.

Dos modelos pueden generar secuencias completamente distintas ante el mismo prompt visible porque el prompt real recibido por el modelo no es idéntico.

## Conceptos

Este experimento es deliberadamente mínimo. No intenta explicar todavía la tokenización interna ni la atención. Solo observa que la generación no aparece como un bloque conceptual completo, sino como una secuencia incremental producida por el runtime.

Ollama devuelve fragmentos en streaming. Esos fragmentos permiten observar la construcción progresiva de la respuesta, aunque no siempre equivalen a tokens visibles completos ni exponen los IDs reales de token.

### Prompt visible vs Prompt real

El prompt visible es el texto que escribe el usuario, por ejemplo:

```text
El cielo es
```

El prompt real es la entrada efectiva que llega al modelo después de que Ollama prepara la petición:

```text
Prompt real =
Prompt visible
+ System Prompt
+ Template
+ Tokens especiales
+ Parámetros de generación
```

Por eso este experimento no debe interpretarse como una observación aislada del modelo. Observamos:

```text
Modelo
+
Template
+
System Prompt
+
Runtime
+
Parámetros
```

### Chat Template

Una plantilla de chat transforma mensajes con roles en una secuencia que el modelo puede continuar. Ollama obtiene esa plantilla de la definición o metadatos del modelo local y la aplica en modo normal.

Ejemplo conceptual:

```text
system: ...
user: El cielo es
assistant:
```

El formato real depende del modelo. No todos usan esas palabras, esos separadores ni los mismos tokens especiales.

### Modo raw de Ollama

Ollama permite omitir la plantilla de chat en `/api/generate` usando:

```json
{
  "raw": true
}
```

En modo raw, el prompt se envía como texto directo para estudiar la continuación textual sin template de chat. Siguen influyendo el tokenizer, el runtime, los parámetros, la cuantización y el comportamiento aprendido del modelo.

## Variables

- Variable independiente: prompt simple.
- Variables controladas: modelo, `temperature`, `num_predict`, modo de generación.
- Variables observadas: fragmentos generados, texto final, métricas de Ollama, tiempo de pared, diferencia entre modo normal y modo raw.

## Variantes

### Experimento A: modo normal

Objetivo: observar la generación cuando Ollama aplica la plantilla del modelo.

En esta variante, Ollama prepara el prompt real usando la configuración normal del modelo. Esto puede incluir template de chat, system prompt y tokens especiales.

### Experimento B: modo raw

Objetivo: observar la continuación textual sin plantilla de chat.

En esta variante, el script envía `"raw": true` a Ollama para evitar que se aplique el template de chat del modelo.

## Ejecución

Desde la raíz del repositorio:

```bash
python3 scripts/run_next_token.py --model llama3.2:3b
```

Experimento A, modo normal:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 12 \
  --temperature 0.2
```

Experimento B, modo raw:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 12 \
  --temperature 0.2 \
  --raw
```

Opciones útiles:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 12 \
  --temperature 0.2
```

El script crea resultados en:

```text
results/000-next-token/
```

Cada registro JSONL incluye:

- `variant`: `template_chat` o `raw`;
- `raw`: `false` o `true`;
- `chunks`: fragmentos textuales recibidos en streaming;
- `eval_count`: tokens generados reportados por Ollama, si está disponible;
- `response`: respuesta final reconstruida.

## Actividad práctica

Comparar el prompt:

```text
El cielo es
```

en:

- Qwen2.5-Coder;
- Llama 3.2.

Para cada modelo ejecutar:

- modo normal;
- modo raw.

Tabla de registro:

| Modelo | Modo | Tokens generados (`eval_count`) | Respuesta final | Diferencias observadas |
| --- | --- | --- | --- | --- |
| Qwen2.5-Coder | normal | | | |
| Qwen2.5-Coder | raw | | | |
| Llama 3.2 | normal | | | |
| Llama 3.2 | raw | | | |

Durante el análisis investigar:

- system prompts;
- templates;
- modo raw;
- alineamiento;
- comportamiento instruct.

## Observaciones

Anotar aquí observaciones después de ejecutar el experimento:

- Modelo usado:
- Prompt:
- Modo usado: normal / raw
- ¿La respuesta apareció en fragmentos sucesivos?
- ¿Los fragmentos coincidieron con palabras completas?
- ¿Cuántos tokens generados reportó Ollama?
- ¿La respuesta parece una continuación textual o una respuesta de asistente?
- ¿Qué cambia al comparar el mismo modelo en modo normal y raw?
- ¿Qué cambia al comparar Qwen2.5-Coder y Llama 3.2?

## Conclusiones

Completar después de revisar el JSONL. La conclusión debe distinguir entre lo observado directamente, fragmentos de streaming y texto final, y lo inferido a partir de métricas de token.

Conclusión importante del laboratorio:

```text
No estamos observando únicamente el modelo.

Estamos observando:

Modelo
+
Template
+
System Prompt
+
Runtime
+
Parámetros
```

Esta idea debe reutilizarse al interpretar resultados en módulos posteriores.

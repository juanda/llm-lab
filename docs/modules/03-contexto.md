# 03-contexto

## Objetivo

Estudiar qué significa "contexto" en un LLM y cómo afecta a la generación. El módulo parte de los módulos anteriores: el modelo recibe una secuencia de tokens, genera token a token y el runtime controla parámetros como `num_ctx`, `num_predict` y `temperature`.

El objetivo no es construir memoria persistente ni RAG. En este módulo toda la información relevante se incluye directamente dentro del prompt. Si el modelo responde usando un dato, ese dato debe estar en la secuencia de entrada del experimento.

Este módulo no introduce embeddings, bases de datos vectoriales, recuperación documental, tool calling ni agentes. Esos mecanismos aparecen después. Aquí se estudia la ventana de contexto como límite operativo de la secuencia que el modelo puede usar durante inferencia.

## Conceptos

### Contexto

En este laboratorio, contexto significa la secuencia de tokens disponible para el modelo en un paso de generación.

Conceptualmente:

```text
Contexto =
prompt real
+
tokens generados hasta ahora
```

El prompt real puede incluir más que el texto visible:

```text
Prompt visible
+
System Prompt
+
Chat Template
+
Tokens especiales
+
Stop tokens
+
Parámetros del runtime
```

Por eso dos experimentos con el mismo prompt visible pueden tener contextos reales distintos si cambian modelo, template, modo `raw`, system prompt o runtime.

### Ventana de contexto

La ventana de contexto es el límite máximo de tokens que el runtime intenta mantener disponibles para el modelo. En Ollama se puede controlar con opciones como `num_ctx`, aunque el límite efectivo depende del modelo, su configuración, la memoria disponible y el backend.

Una ventana de contexto mayor permite incluir más tokens en la entrada, pero no garantiza que el modelo use todos los detalles igual de bien. También puede aumentar coste de cómputo y memoria.

### Contexto no es memoria persistente

Un LLM no recuerda entre ejecuciones por el mero hecho de haber respondido antes. Si una información no está en el contexto actual, en los pesos del modelo o en una herramienta externa que la inserte en el prompt, el modelo no puede consultarla durante esa inferencia.

En una conversación, la "memoria" visible suele ser una reconstrucción del historial incluida en el prompt real:

```text
Mensajes anteriores
+
Mensaje actual
↓
Prompt real de esta petición
```

Si el historial se recorta, resume o transforma, cambia el contexto real.

### Atención

La atención es un mecanismo del Transformer que permite que las representaciones de los tokens se calculen teniendo en cuenta otros tokens de la secuencia. Para este módulo basta con una idea operativa: el modelo procesa relaciones dentro de la secuencia disponible.

No se observarán matrices de atención ni pesos internos. Se observarán efectos externos: si el modelo puede recuperar un dato incluido en el prompt y cómo cambia esa recuperación cuando aumenta la cantidad de información irrelevante.

### Posición y distancia

Los tokens tienen posición dentro de la secuencia. En muchos modelos, la capacidad para usar información puede depender de dónde aparece el dato dentro del contexto y de cuánta información lo rodea.

Este módulo no demostrará mecanismos internos de posición. Solo prepara la pregunta experimental: aunque un dato esté dentro del prompt, puede ser más o menos fácil de recuperar según longitud, ubicación, formato y ruido.

### Ruido contextual

Ruido contextual es información presente en el prompt que no es necesaria para responder la pregunta. No es ruido para el tokenizer: son tokens reales que consumen ventana de contexto y pueden competir con el dato relevante.

Ejemplo:

```text
Hecho 001: ...
Hecho 002: ...
...
Hecho 096: el código de la muestra 096 es clave-096-azul.
```

Si la pregunta pide un identificador concreto, todos los demás hechos son distractores para esa tarea.

### Recuperación dentro del prompt

Recuperar información dentro del prompt significa responder usando un dato que está explícitamente incluido en la secuencia de entrada.

No es RAG:

```text
Prompt largo con hechos
↓
Modelo
↓
Respuesta
```

RAG implicaría una etapa externa de recuperación antes de construir el prompt:

```text
Consulta
↓
Buscador o base vectorial
↓
Documentos recuperados
↓
Prompt aumentado
↓
Modelo
```

Este módulo solo estudia el primer caso.

### `num_ctx`

`num_ctx` es una opción del runtime que solicita un tamaño de contexto. Debe registrarse porque afecta al experimento, pero no debe interpretarse aisladamente como garantía de que todo el prompt se usó de forma perfecta.

Si el prompt se aproxima o supera la ventana efectiva, pueden aparecer truncamientos, pérdida de información o errores. El script registra `prompt_eval_count` cuando Ollama lo informa para ayudar a estimar cuántos tokens de entrada se procesaron.

### `prompt_eval_count`

`prompt_eval_count` es una métrica reportada por Ollama en algunas respuestas. Indica tokens evaluados del prompt según el runtime. Es una observación útil para comparar tamaños de entrada.

Limitaciones:

- puede faltar o aparecer como `null`;
- no muestra la lista exacta de tokens;
- no explica por sí sola por qué el modelo acierta o falla;
- depende del prompt real, no solo del texto visible.

### KV cache

Durante generación, el runtime puede guardar estados intermedios de tokens ya procesados para no recalcular todo desde cero en cada paso. Esto suele llamarse KV cache.

Para este módulo basta con saber que la generación larga y los contextos grandes tienen coste de memoria y tiempo. No se analizará la implementación interna de la cache.

### Evaluación exacta y evaluación cualitativa

El experimento del módulo usa códigos sintéticos como `clave-064-verde`. Esto permite una evaluación automática simple:

- `exact_match`: la respuesta es exactamente el código esperado;
- `contains_expected`: la respuesta contiene el código esperado, aunque añada texto extra.

La evaluación exacta es útil, pero limitada. Si `exact_match=false` y `contains_expected=true`, el modelo recuperó el dato pero no siguió el formato pedido. Esa diferencia importa.

## Hipótesis

1. Si el dato relevante está explícitamente dentro del contexto y el prompt es claro, el modelo podrá recuperarlo en algunos casos bajo condiciones controladas.
2. Al aumentar el número de hechos irrelevantes, puede aumentar la probabilidad de errores, respuestas incompletas o texto extra.
3. `exact_match` y `contains_expected` pueden divergir: una respuesta puede contener el dato correcto y aun así incumplir el formato.
4. Aumentar `num_ctx` permite solicitar una ventana mayor, pero no garantiza recuperación perfecta.
5. Una respuesta incorrecta no demuestra por sí sola que el dato estuviera fuera del contexto; puede deberse a formato, atención, sampling, truncamiento, template o límites del experimento.
6. Para interpretar resultados de contexto hay que registrar modelo, prompt real inferido, `num_ctx`, `prompt_eval_count`, `eval_count`, runtime y parámetros.

## Experimentos

### 003A - Recuperación de hechos dentro del prompt

Pregunta: ¿puede el modelo recuperar información incluida explícitamente dentro de un prompt largo?

Hipótesis: si la información relevante está dentro del contexto y el prompt es claro, el modelo debería poder recuperarla. Al aumentar la cantidad de hechos irrelevantes, pueden aparecer errores de recuperación o respuestas incompletas.

Restricción: este experimento no usa RAG, embeddings, bases de datos vectoriales ni agentes. Toda la información se incluye directamente en el prompt.

Script:

```bash
python3 scripts/run_context.py --model llama3.2:3b
```

Opciones útiles:

```bash
python3 scripts/run_context.py \
  --model llama3.2:3b \
  --fact-counts 8 32 96 \
  --num-ctx 4096 \
  --num-predict 40 \
  --temperature 0.0
```

El script genera hechos sintéticos:

```text
Hecho 001: el código de la muestra 001 es clave-001-azul.
Hecho 002: el código de la muestra 002 es clave-002-azul.
...
```

Una muestra objetivo recibe un código diferente:

```text
clave-064-verde
```

El prompt pide responder únicamente con el código exacto asociado a esa muestra.

Variables:

- variable independiente: número de hechos sintéticos incluidos en el prompt;
- variables controladas: modelo, formato de hechos, pregunta, `num_predict`, `num_ctx` y `temperature`;
- variables observadas: respuesta del modelo, valor esperado, `exact_match`, `contains_expected`, `prompt_eval_count`, `eval_count`, `done_reason` y métricas de duración.

Resultados:

```text
results/003-context/
```

Cada registro JSONL incluye:

- `experiment`: `003-context`;
- `fact_count`;
- `target_label`;
- `expected_code`;
- `answer`;
- `exact_match`;
- `contains_expected`;
- `model`;
- `prompt`;
- `options`;
- métricas de Ollama como `prompt_eval_count`, `eval_count`, duraciones y `done_reason`.

Registro:

| Hechos | Muestra objetivo | Código esperado | Respuesta | `exact_match` | `contains_expected` | `prompt_eval_count` | Observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | | | | | | | |
| 32 | | | | | | | |
| 96 | | | | | | | |

Interpretación:

- si `exact_match=true`, el modelo devolvió exactamente el código esperado;
- si `exact_match=false` y `contains_expected=true`, recuperó el dato pero incumplió la instrucción de responder solo con el código;
- si ambos son `false`, revisar manualmente si respondió otro código, explicó demasiado, truncó la respuesta o no siguió el formato.

### 003B - Tamaño de contexto solicitado

Pregunta: ¿cambia el resultado observable al modificar `num_ctx` manteniendo el mismo número de hechos?

Hipótesis: si el prompt cabe con holgura en ambas configuraciones, puede no observarse diferencia. Si el prompt se aproxima al límite efectivo, una configuración de contexto menor puede empeorar la recuperación o alterar métricas.

Ejecuciones sugeridas:

```bash
python3 scripts/run_context.py \
  --model llama3.2:3b \
  --fact-counts 96 \
  --num-ctx 1024 \
  --temperature 0.0
```

```bash
python3 scripts/run_context.py \
  --model llama3.2:3b \
  --fact-counts 96 \
  --num-ctx 4096 \
  --temperature 0.0
```

Variables:

- variable independiente: `num_ctx`;
- variables controladas: modelo, hechos, target, formato, `temperature` y `num_predict`;
- variables observadas: `prompt_eval_count`, respuesta, `exact_match`, `contains_expected`, duración y `done_reason`.

Registro:

| `num_ctx` | Hechos | `prompt_eval_count` | Respuesta | `exact_match` | `contains_expected` | Interpretación |
| --- | --- | --- | --- | --- | --- | --- |
| 1024 | 96 | | | | | |
| 4096 | 96 | | | | | |

Limitación: si el script genera el mismo target para el mismo `fact_count`, la comparación es más limpia. Si se modifica el script o el prompt entre ejecuciones, registrar el cambio.

### 003C - Posición y distractores

Pregunta: ¿basta con que el dato esté dentro del prompt para que se recupere siempre igual?

Hipótesis: no. La posición del dato, el número de distractores y el formato pueden afectar a la recuperación observable.

Actividad manual con el script actual:

1. Ejecutar `003A`.
2. Revisar el campo `prompt` en el JSONL.
3. Localizar dónde aparece `expected_code`.
4. Comparar si los fallos aparecen con más frecuencia en prompts más largos.

Actividad opcional de extensión:

- modificar temporalmente el generador de hechos para colocar el dato objetivo al principio, en el centro y al final;
- mantener constantes modelo, `fact_count`, `num_ctx`, `temperature` y `num_predict`;
- registrar la modificación como nuevo experimento si se conserva en el repo.

Registro:

| Posición del dato | Hechos | Respuesta | `exact_match` | Observaciones |
| --- | --- | --- | --- | --- |
| inicio | | | | |
| centro | | | | |
| final | | | | |

No sacar conclusiones fuertes sin ejecutar repeticiones y mantener constantes las demás variables.

### 003D - Contexto frente a RAG

Pregunta: ¿qué diferencia hay entre incluir datos directamente en el prompt y recuperarlos externamente?

Hipótesis: incluir datos directamente en el prompt demuestra uso de contexto, no RAG. Para hablar de RAG haría falta una etapa adicional de recuperación documental o vectorial antes de llamar al modelo.

Actividad conceptual:

Comparar estos dos flujos:

```text
Flujo de este módulo:
hechos escritos en el prompt
↓
modelo
↓
respuesta
```

```text
Flujo RAG futuro:
pregunta
↓
recuperador externo
↓
documentos seleccionados
↓
prompt aumentado
↓
modelo
↓
respuesta
```

Registrar en las observaciones por qué `003-context` no evalúa embeddings, búsqueda semántica ni calidad de recuperación externa.

## Observaciones

Anotar después de ejecutar:

- modelo usado;
- `num_ctx`, `num_predict` y `temperature`;
- tamaños de contexto probados;
- número de hechos (`fact_count`);
- `prompt_eval_count`, si Ollama lo informa;
- muestra objetivo y código esperado;
- si el modelo devolvió exactamente el identificador pedido;
- si la respuesta contiene el identificador pero añade explicación extra;
- si aparecieron respuestas con otro código;
- si `done_reason` sugiere truncamiento;
- si faltan métricas o aparecen valores `null`;
- si la evaluación automática coincide con una inspección manual.

Separar siempre:

- observación directa: respuesta, métricas y flags del JSONL;
- inferencia: posible efecto de longitud, ruido o ventana;
- limitación: falta de tokens exactos, logits o trazas de atención;
- siguiente paso: qué variable conviene aislar.

Plantilla de observación:

| Campo | Registro |
| --- | --- |
| Modelo | |
| `fact_count` | |
| `num_ctx` | |
| `prompt_eval_count` | |
| Muestra objetivo | |
| Código esperado | |
| Respuesta | |
| `exact_match` | |
| `contains_expected` | |
| `done_reason` | |
| Observación directa | |
| Inferencia razonable | |
| Limitación | |

Comando de inspección línea a línea:

```bash
python3 -c 'import json,sys; [print(json.dumps(json.loads(line), ensure_ascii=False, indent=2)) for line in open(sys.argv[1], encoding="utf-8")]' results/003-context/<archivo>.jsonl
```

JSONL contiene un objeto JSON por línea. No tratar el archivo completo como un único documento JSON.

## Conclusiones

El contexto es la secuencia de tokens disponible para el modelo durante una petición. No es memoria persistente, no es una base de datos y no es RAG. El modelo solo puede condicionar su generación con lo que está en la secuencia de entrada, en sus pesos o en información que una herramienta externa inserte antes de la llamada.

Conclusiones que el módulo debe comprobar experimentalmente:

- un dato explícito dentro del prompt puede recuperarse bajo condiciones controladas;
- aumentar la cantidad de hechos irrelevantes puede dificultar la recuperación o el cumplimiento exacto del formato;
- `exact_match` y `contains_expected` miden cosas distintas;
- `num_ctx` solicita una ventana de contexto, pero no garantiza uso perfecto de cada detalle;
- `prompt_eval_count` ayuda a observar tamaño de entrada, pero no reemplaza una inspección conceptual del prompt real;
- un fallo de recuperación no demuestra por sí solo que el modelo no tenga capacidad: hay que revisar prompt, formato, parámetros, template, truncamiento y métricas.

Antes de avanzar al módulo 4, el estudiante debe poder:

- explicar la diferencia entre prompt visible, prompt real y contexto;
- distinguir contexto de memoria persistente;
- distinguir recuperación dentro del prompt de RAG;
- interpretar `fact_count`, `expected_code`, `exact_match` y `contains_expected`;
- usar `prompt_eval_count` como señal observable sin sobreinterpretarla;
- diseñar una comparación donde solo cambie `num_ctx` o la cantidad de hechos.

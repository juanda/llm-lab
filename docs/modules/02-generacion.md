# 02-generacion

## Objetivo

Estudiar cómo aparece una respuesta completa durante la generación autoregresiva y qué papel juegan los parámetros de decodificación del runtime. El módulo conecta la anatomía interna estudiada en el módulo 1 con controles observables de salida: longitud, sampling, parada y repetición.

El objetivo no es aprender a escribir mejores prompts todavía. Prompt engineering se tratará en el módulo 4. Aquí el prompt se usa como variable controlada para observar cómo el runtime convierte distribuciones de probabilidad en texto.

Este módulo no introduce RAG, agentes, tool calling, entrenamiento, RLHF ni memoria conversacional. Tampoco intenta acceder a logits internos: se trabaja con señales observables en Ollama, como respuesta final, `eval_count`, `done_reason`, métricas de duración y diferencias entre variantes.

## Conceptos

### Generar no es responder de golpe

Un LLM autoregresivo genera una respuesta repitiendo un ciclo:

```text
Secuencia actual
↓
Prediccion del siguiente token
↓
Seleccion de un token
↓
Secuencia actual + token seleccionado
↓
Nueva prediccion
```

La respuesta final que leemos es el resultado acumulado de muchas selecciones locales. El modelo no imprime internamente una respuesta completa ya escrita. En cada paso produce información numérica que el runtime usa para seleccionar el siguiente token.

### Logits, probabilidades y sampling

La salida inmediata del modelo para el siguiente token se puede describir como una puntuación para cada token del vocabulario. Esas puntuaciones suelen llamarse logits.

El runtime transforma esas puntuaciones en una distribución de probabilidad y decide qué token añadir a la secuencia. Esa decisión puede ser más determinista o más aleatoria según los parámetros de generación.

En este laboratorio no observamos directamente los logits con los scripts actuales. Observamos sus efectos indirectos:

- texto final;
- variación entre repeticiones;
- longitud de respuesta;
- `eval_count`;
- `done_reason`;
- tiempo de generación;
- cumplimiento o incumplimiento del formato pedido.

### Decodificación

Decodificar, en este módulo, significa elegir tokens a partir de la distribución producida por el modelo y los controles del runtime. No debe confundirse con detokenizar. Detokenizar convierte tokens en texto visible; decodificar decide qué token se añade.

Flujo simplificado:

```text
Logits
↓
Ajustes de sampling
↓
Seleccion del siguiente token
↓
Detokenizacion parcial o final
↓
Texto visible
```

### `temperature`

`temperature` controla cuánto se suaviza o concentra la distribución antes de seleccionar tokens.

Con `temperature` baja, el runtime tiende a elegir tokens de alta probabilidad con más frecuencia. En condiciones similares, las respuestas suelen ser más parecidas entre repeticiones.

Con `temperature` alta, aumenta la probabilidad de elegir tokens menos dominantes. Esto puede aumentar diversidad, pero también puede producir respuestas menos estables, cambios de estructura o errores de formato.

Observación importante: una temperatura alta no hace que el modelo "sea creativo" como una propiedad interna estable. Cambia el proceso de selección de tokens bajo unas condiciones concretas.

### `top_p`

`top_p`, también llamado nucleus sampling, limita la selección a un subconjunto dinámico de tokens cuya probabilidad acumulada alcanza un umbral. Un `top_p` bajo restringe más el conjunto candidato; un `top_p` alto permite considerar más alternativas.

`temperature` y `top_p` interactúan. No se debe atribuir un cambio de salida a un único parámetro si ambos han cambiado.

### `top_k`

`top_k` limita la selección a los `k` tokens candidatos más probables. Es otro mecanismo para restringir el espacio de selección. En Ollama puede estar disponible como opción del runtime según modelo y backend.

En este módulo se menciona como concepto, pero el experimento principal usa `top_p` porque permite una comparación simple sin introducir demasiadas variantes.

### `num_predict`

`num_predict` limita el número máximo de tokens que el runtime intentará generar. No equivale a longitud en palabras ni caracteres.

Si `num_predict` es demasiado bajo, una respuesta puede cortarse antes de completar el formato pedido. Si es suficiente, la respuesta puede terminar por stop token, fin de turno u otra condición reportada por el runtime.

### Stop sequences

Una stop sequence es una secuencia textual que el runtime usa como señal para detener la generación. No es una conclusión conceptual del modelo: es una regla externa aplicada por el sistema.

Si se configura `stop: ["FIN"]`, el runtime puede parar cuando aparece esa secuencia. Según la implementación, la secuencia de parada puede no aparecer en la respuesta final visible, aunque haya causado la detención.

### Penalización de repetición

La penalización de repetición modifica la probabilidad de tokens que ya han aparecido. Puede reducir bucles o repeticiones superficiales, pero también puede cambiar estilo, longitud o precisión.

No debe interpretarse como una comprensión interna de que "repetir está mal". Es un ajuste numérico aplicado durante la selección.

### Semilla y reproducibilidad

Algunos runtimes permiten fijar una semilla para hacer más reproducible el muestreo. Aun así, la reproducibilidad completa depende de modelo, versión del runtime, hardware, cuantización, parámetros y backend.

Si no se fija semilla, comparar varias repeticiones es parte del experimento. Si se fija, se debe registrar.

### Condiciones de parada

Una generación puede detenerse por varias razones:

- alcanzar `num_predict`;
- generar una stop sequence;
- generar un token de fin esperado por la plantilla;
- completar una respuesta bajo reglas internas del runtime;
- error o interrupción externa.

Por eso `done_reason` y `eval_count` son observaciones importantes. Una respuesta corta no significa necesariamente que el modelo "no supiera más"; puede haber terminado por una regla de parada.

### Formato visible y cumplimiento

Cuando se pide una lista, un JSON o una frase exacta, el resultado observable combina:

```text
Modelo
+
Prompt visible
+
Prompt real
+
Template
+
System Prompt
+
Runtime
+
Parametros de generacion
```

El incumplimiento de formato no debe atribuirse automáticamente a falta de capacidad del modelo. Puede deberse a longitud insuficiente, sampling, stop sequences, template, prompt ambiguo o límites del runtime.

## Hipótesis

1. Si se mantiene fijo el prompt y aumenta `temperature`, aumentará la variabilidad observable entre repeticiones.
2. Si `num_predict` es demasiado bajo, aumentará la probabilidad de respuestas truncadas o incompletas.
3. Si se configura una stop sequence alineada con el prompt, la generación puede detenerse antes de alcanzar `num_predict`.
4. Si se reduce `top_p`, la salida tenderá a usar un conjunto de continuaciones más restringido bajo las mismas condiciones.
5. Si se aumenta `repeat_penalty`, pueden reducirse repeticiones superficiales, aunque también puede cambiar el estilo o la completitud.
6. Las diferencias de salida solo son interpretables si se registran modelo, prompt, template, system prompt, runtime y parámetros.

## Experimentos

### 002A - Temperatura y variabilidad

Pregunta: ¿cómo cambia la variabilidad de las respuestas al modificar `temperature` manteniendo fijo el prompt?

Hipótesis: con temperaturas bajas, las respuestas serán más parecidas entre repeticiones; con temperaturas altas, aumentarán diferencias de vocabulario, estructura y contenido.

Este experimento reutiliza el script ya introducido en el módulo 0:

```bash
python3 scripts/run_temperature.py \
  --model llama3.2:3b \
  --temperatures 0.0 0.3 0.7 1.0 \
  --repeat 3 \
  --num-predict 160
```

Variables:

- variable independiente: `temperature`;
- variables controladas: modelo, prompt, `num_predict`, número de repeticiones y runtime;
- variables observadas: respuesta, longitud, `eval_count`, `done_reason`, tiempo y diferencias cualitativas.

Resultados:

```text
results/001-temperature/
```

Registro:

| Temperatura | Repetición | `eval_count` | `done_reason` | Resumen de respuesta | Diferencias observadas |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 1 | | | | |
| 0.0 | 2 | | | | |
| 0.7 | 1 | | | | |
| 1.0 | 1 | | | | |

Limitación: si también cambian modelo, prompt, `num_predict` o template, el experimento ya no aísla el efecto de `temperature`.

### 002B - Controles de generación

Pregunta: ¿qué cambios observables aparecen al modificar controles de generación manteniendo fijo el prompt visible?

Hipótesis: las variantes con longitud corta, sampling más abierto, nucleus sampling más restrictivo, penalización de repetición o stop sequence producirán diferencias observables en longitud, formato, `done_reason` o contenido.

Script:

```bash
python3 scripts/run_generation_controls.py --model llama3.2:3b
```

Opciones útiles:

```bash
python3 scripts/run_generation_controls.py \
  --model llama3.2:3b \
  --repeat 2
```

Prompt por defecto:

```text
Escribe exactamente una lista numerada de tres recomendaciones para evaluar una respuesta de un modelo de lenguaje. Termina con la palabra FIN.
```

Variantes:

| Variante | Cambio principal | Qué observar |
| --- | --- | --- |
| `baseline` | `temperature=0.2`, longitud suficiente | formato esperado y estabilidad |
| `short_length` | `num_predict=24` | truncamiento o respuesta incompleta |
| `high_temperature` | `temperature=1.0` | variabilidad y cambios de formato |
| `low_top_p` | `top_p=0.4` | vocabulario o estructura más restringidos |
| `repeat_penalty` | `repeat_penalty=1.3` | cambios en repetición y estilo |
| `stop_sequence` | `stop=["FIN"]` | parada por secuencia de stop |

Variables:

- variables independientes: variante de opciones de generación;
- variables controladas: modelo, prompt visible, número de repeticiones y runtime;
- variables observadas: respuesta final, longitud, `eval_count`, `done_reason`, cumplimiento del formato, aparición visible o no de `FIN` y métricas de duración.

Resultados:

```text
results/002-generation-controls/
```

Cada registro JSONL incluye:

- `experiment`: `002-generation-controls`;
- `variant`;
- `variant_description`;
- `repetition`;
- `model`;
- `prompt`;
- `options`;
- `response`;
- `response_length_chars`;
- métricas de Ollama como `eval_count`, `prompt_eval_count`, duraciones, `tokens_per_second`, `done` y `done_reason`.

Registro:

| Variante | Repetición | `eval_count` | `done_reason` | ¿Cumple lista de 3? | ¿Aparece `FIN`? | Observaciones |
| --- | --- | --- | --- | --- | --- | --- |
| `baseline` | 1 | | | | | |
| `short_length` | 1 | | | | | |
| `high_temperature` | 1 | | | | | |
| `low_top_p` | 1 | | | | | |
| `repeat_penalty` | 1 | | | | | |
| `stop_sequence` | 1 | | | | | |

Interpretación esperada: si `short_length` queda incompleta, la causa observable puede ser el límite de generación, no una incapacidad del modelo. Si `stop_sequence` no muestra `FIN`, puede ser porque el runtime la usó para detener y la excluyó del texto visible. Si `high_temperature` cambia el formato, eso muestra sensibilidad al proceso de selección, no un cambio en los pesos.

### 002C - Parada y longitud

Pregunta: ¿la longitud visible de la respuesta basta para saber por qué se detuvo la generación?

Hipótesis: no. Hay que revisar `done_reason`, `eval_count`, `num_predict` y stop sequences para interpretar la parada.

Actividad:

1. Ejecutar `002B`.
2. Comparar `short_length`, `baseline` y `stop_sequence`.
3. Leer los campos `options`, `eval_count` y `done_reason` en el JSONL.
4. Anotar si la respuesta terminó por longitud, por stop sequence o por otra causa reportada.

Comando de inspección línea a línea:

```bash
python3 -c 'import json,sys; [print(json.dumps(json.loads(line), ensure_ascii=False, indent=2)) for line in open(sys.argv[1], encoding="utf-8")]' results/002-generation-controls/<archivo>.jsonl
```

JSONL contiene un objeto JSON por línea, no un único documento JSON. Por eso se debe procesar línea a línea.

Registro:

| Variante | `num_predict` | Stop configurado | `eval_count` | `done_reason` | Interpretación de la parada |
| --- | --- | --- | --- | --- | --- |
| `baseline` | | | | | |
| `short_length` | | | | | |
| `stop_sequence` | | | | | |

## Observaciones

Durante este módulo se deben anotar observaciones como:

- si una variante produce respuestas más largas o más cortas;
- si `eval_count` se aproxima a `num_predict`;
- si `done_reason` indica longitud, stop u otra condición;
- si una respuesta queda truncada;
- si el formato pedido se conserva o se rompe;
- si respuestas con temperatura alta varían entre repeticiones;
- si `top_p` bajo reduce diversidad observable;
- si `repeat_penalty` cambia repeticiones, estilo o completitud;
- si la secuencia `FIN` aparece en el texto visible o solo parece actuar como condición de parada;
- si faltan métricas en los registros de Ollama.

Separar:

- dato observado: valores JSONL y texto generado;
- inferencia: posible efecto de un parámetro;
- limitación: falta de logits, tokens exactos o control completo sobre template;
- siguiente experimento: qué parámetro conviene aislar mejor.

Plantilla de observación:

| Campo | Registro |
| --- | --- |
| Modelo | |
| Prompt visible | |
| Variante | |
| Parámetros | |
| `eval_count` | |
| `done_reason` | |
| Respuesta final | |
| Observación directa | |
| Inferencia razonable | |
| Limitación | |

## Conclusiones

La generación de texto es un proceso autoregresivo controlado por el modelo y por el runtime. El modelo produce información para el siguiente token; el runtime aplica parámetros de decodificación, selecciona tokens, detiene la generación y reconstruye texto visible.

Conclusiones que el módulo debe comprobar experimentalmente:

- una respuesta completa emerge por acumulación de tokens seleccionados;
- `temperature`, `top_p`, `repeat_penalty`, `num_predict` y stop sequences son controles externos al Transformer;
- cambiar esos controles puede cambiar la salida sin modificar los pesos del modelo;
- una respuesta incompleta puede deberse a límites de generación o reglas de parada;
- una diferencia entre respuestas no demuestra por sí sola que un modelo sea mejor, peor, más inteligente o menos capaz;
- para interpretar generación hay que registrar modelo, prompt visible, prompt real inferido, template, system prompt, runtime y parámetros.

Antes de avanzar al módulo 3, el estudiante debe poder:

- explicar la diferencia entre logits, sampling, token seleccionado y texto detokenizado;
- distinguir `temperature`, `top_p`, `num_predict`, stop sequence y penalización de repetición;
- leer un JSONL de resultados y localizar `options`, `eval_count` y `done_reason`;
- separar una observación directa de una inferencia sobre el efecto de un parámetro;
- evitar atribuir al modelo lo que pertenece al runtime o a la configuración de generación.

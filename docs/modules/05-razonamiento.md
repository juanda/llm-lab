# 05-razonamiento

## Objetivo

Estudiar el razonamiento como comportamiento observable en tareas que requieren varios pasos, restricciones o inferencias simples. El módulo no intenta demostrar que el modelo razona como una persona ni que podamos ver su proceso interno. Estudia qué respuestas produce bajo prompts controlados y cómo cambian al pedir respuesta directa, verificación breve, descomposición o formato JSON.

El objetivo es convertir "parece razonar" en preguntas verificables:

- ¿llega a la respuesta esperada?
- ¿mantiene restricciones?
- ¿el formato permite evaluar?
- ¿cambia la respuesta al pedir pasos?
- ¿la explicación coincide con la respuesta final?

Este módulo no introduce agentes, herramientas, búsqueda, ejecución de código ni verificación externa automática más allá de reglas simples sobre texto y JSON. Esos mecanismos aparecerán más adelante.

## Conceptos

### Razonamiento observable

En este laboratorio, razonamiento observable significa comportamiento en tareas donde la respuesta no parece una simple continuación superficial del prompt.

Ejemplos:

- resolver una operación aritmética sencilla;
- ordenar relaciones transitivas;
- cumplir restricciones;
- comparar alternativas;
- detectar una contradicción;
- producir una respuesta final consistente con una verificación breve.

No observamos directamente el razonamiento interno. Observamos texto generado y métricas.

### Razonamiento interno frente a traza textual

Una explicación generada por el modelo no es una ventana directa a su estado interno. Es otra secuencia de tokens generada.

Por tanto:

```text
explicacion generada != proceso interno demostrado
```

Una traza textual puede ser útil para depurar, enseñar o evaluar consistencia, pero no debe confundirse con evidencia completa de cómo se calculó la respuesta.

### Respuesta final

La respuesta final es el dato que se evalúa contra un criterio esperado.

Ejemplo:

```text
Pregunta: Marta es más alta que Luis. Luis es más alto que Ana. ¿Quién es la persona más baja?
Respuesta final esperada: Ana
```

Si la explicación es larga pero la respuesta final es incorrecta, el resultado debe contarse como fallo para la tarea.

### Verificación breve

Una verificación breve es una comprobación textual de la respuesta.

Ejemplo:

```text
Verificacion: si Marta > Luis y Luis > Ana, entonces Ana es la más baja.
Respuesta: Ana
```

La verificación puede ayudar a detectar contradicciones entre explicación y respuesta, pero sigue siendo salida generada. No sustituye a una evaluación externa.

### Descomposición

Descomponer un problema consiste en dividirlo en pasos intermedios.

Puede ayudar cuando:

- hay varias operaciones;
- hay restricciones;
- hay relaciones que combinar;
- el formato final necesita comprobarse.

También puede perjudicar si:

- aumenta demasiado la longitud;
- introduce errores intermedios;
- el modelo se desvía;
- el prompt favorece explicaciones plausibles pero incorrectas.

### Chain-of-thought y límites metodológicos

Muchos prompts piden "piensa paso a paso". En este curso no se usará esa frase como prueba de razonamiento interno. Si se pide una descomposición, se evaluará como texto observable.

Para tareas del laboratorio, preferimos formatos como:

```text
Verificacion: una comprobacion corta.
Respuesta: la respuesta final.
```

Esto permite observar consistencia sin depender de trazas largas o difíciles de evaluar.

### Problemas con respuesta esperada

Un experimento de razonamiento necesita respuestas esperadas claras. Si la respuesta admite muchas interpretaciones, la evaluación automática simple será débil.

Buenas tareas iniciales:

- aritmética pequeña;
- relaciones de orden;
- selección con restricciones;
- clasificación con criterio cerrado.

Malas tareas iniciales:

- preguntas filosóficas abiertas;
- escritura creativa;
- decisiones con preferencias no definidas;
- problemas ambiguos sin respuesta esperada.

### Evaluación automática simple

El script de este módulo usa una comprobación básica:

- `contains_expected_answer`: la respuesta contiene la respuesta esperada;
- `json_parseable`: la respuesta puede parsearse como JSON.

Esto no equivale a una evaluación completa. Una respuesta puede contener el valor esperado y aun así estar mal explicada. También puede ser correcta con una forma textual no prevista. Por eso la inspección manual sigue siendo necesaria.

### Consistencia

La consistencia observable compara partes de la salida:

- ¿la verificación apoya la respuesta final?
- ¿el JSON contiene una respuesta compatible con el texto?
- ¿la respuesta cambia entre repeticiones?
- ¿una variante acierta unas tareas y falla otras?

La consistencia no demuestra verdad. Solo reduce ciertos tipos de error visible.

### Razonamiento y sampling

Los parámetros de generación siguen importando. Una tarea "de razonamiento" no deja de ser generación autoregresiva. Cambiar `temperature`, `num_predict`, template o system prompt puede cambiar la respuesta.

Por eso los experimentos de este módulo deben registrar:

- modelo;
- prompt;
- variante;
- `temperature`;
- `num_predict`;
- `eval_count`;
- `done_reason`;
- respuesta final;
- respuesta esperada.

## Hipótesis

1. Pedir una respuesta estructurada puede facilitar la evaluación frente a una respuesta libre.
2. Pedir una verificación breve puede revelar contradicciones entre explicación y respuesta final.
3. Pedir descomposición puede mejorar algunas tareas y empeorar otras bajo las mismas condiciones.
4. Una salida JSON puede facilitar evaluación automática, pero puede fallar por formato aunque contenga una respuesta correcta.
5. La presencia de una explicación plausible no garantiza que la respuesta final sea correcta.
6. Las diferencias observadas deben atribuirse al sistema completo: modelo, prompt, template, runtime y parámetros.

## Experimentos

### 005A - Patrones de prompt en tareas con respuesta esperada

Pregunta: ¿cómo cambia el resultado observable al resolver tareas pequeñas con distintos patrones de prompt?

Hipótesis: las variantes con estructura explícita permitirán evaluar mejor la respuesta que una respuesta directa libre, pero no garantizan más aciertos.

Script:

```bash
python3 scripts/run_reasoning_tasks.py --model llama3.2:3b
```

Opciones útiles:

```bash
python3 scripts/run_reasoning_tasks.py \
  --model llama3.2:3b \
  --repeat 2 \
  --temperature 0.2
```

Tareas incluidas:

| `task_id` | Tipo | Respuesta esperada |
| --- | --- | --- |
| `arithmetic` | aritmética | `8` |
| `ordering` | lógica relacional | `Ana` |
| `constraint` | restricción | `4,9` |

Variantes:

| Variante | Prompt | Qué observar |
| --- | --- | --- |
| `direct` | pide solo respuesta final | concisión y acierto |
| `structured` | pide verificación breve y respuesta | consistencia visible |
| `decompose` | pide pasos breves y respuesta final | errores intermedios o mejora |
| `json` | pide JSON válido | parseo y respuesta estructurada |

Variables:

- variables independientes: tarea y variante de prompt;
- variables controladas: modelo, `temperature`, `num_predict`, repeticiones y runtime;
- variables observadas: `contains_expected_answer`, `json_parseable`, respuesta, `eval_count`, `done_reason`, longitud y métricas de duración.

Resultados:

```text
results/005-reasoning-tasks/
```

Cada registro JSONL incluye:

- `experiment`: `005-reasoning-tasks`;
- `task_id`;
- `task_type`;
- `question`;
- `expected_answer`;
- `variant`;
- `contains_expected_answer`;
- `json_parseable`;
- `parsed_json`;
- `model`, `prompt`, `options`, `response` y métricas de Ollama.

Registro:

| Tarea | Variante | Repetición | ¿Contiene respuesta esperada? | ¿JSON parseable? | `done_reason` | Observaciones |
| --- | --- | --- | --- | --- | --- | --- |
| `arithmetic` | `direct` | 1 | | | | |
| `arithmetic` | `structured` | 1 | | | | |
| `ordering` | `decompose` | 1 | | | | |
| `constraint` | `json` | 1 | | | | |

Interpretación:

- si `contains_expected_answer=true`, la respuesta contiene el valor esperado, pero revisar si hay contradicciones;
- si `json_parseable=false` en la variante `json`, el formato falló aunque el contenido pueda ser útil;
- si `decompose` falla donde `direct` acierta, la descomposición no ayudó en esa condición;
- si una tarea falla en todas las variantes, revisar ambigüedad, prompt, modelo y parámetros antes de sacar conclusiones.

### 005B - Respuesta directa frente a verificación breve

Pregunta: ¿pedir una verificación breve cambia la respuesta final o solo añade texto?

Hipótesis: la verificación breve puede ayudar a detectar inconsistencias visibles, pero no garantiza acierto.

Actividad:

1. Ejecutar `005A`.
2. Comparar `direct` y `structured` para cada tarea.
3. Revisar si ambas contienen la respuesta esperada.
4. Inspeccionar si la verificación contradice la respuesta.

Registro:

| Tarea | Direct acierta | Structured acierta | ¿Verificación consistente? | Observación |
| --- | --- | --- | --- | --- |
| `arithmetic` | | | | |
| `ordering` | | | | |
| `constraint` | | | | |

Conclusión esperada: una verificación breve puede ser útil como superficie de inspección, pero no es una prueba del proceso interno.

### 005C - Descomposición y errores intermedios

Pregunta: ¿descomponer siempre mejora el resultado?

Hipótesis: no. La descomposición puede ayudar en algunas tareas y crear errores en otras.

Actividad:

1. Ejecutar `005A` con `--repeat 3`.
2. Comparar `direct` y `decompose`.
3. Revisar si los pasos intermedios son compatibles con la respuesta final.
4. Registrar casos donde una explicación plausible termine en respuesta incorrecta.

Comando:

```bash
python3 scripts/run_reasoning_tasks.py \
  --model llama3.2:3b \
  --repeat 3 \
  --temperature 0.2
```

Registro:

| Tarea | Variante | Respuesta final | Error intermedio observado | Observación |
| --- | --- | --- | --- | --- |
| `arithmetic` | `decompose` | | | |
| `ordering` | `decompose` | | | |
| `constraint` | `decompose` | | | |

No concluir que "pensar paso a paso" es mejor sin datos de varias tareas y repeticiones.

### 005D - JSON como superficie de evaluación

Pregunta: ¿pedir JSON facilita evaluar tareas de razonamiento?

Hipótesis: JSON facilita parseo y extracción, pero puede fallar por formato o contener una respuesta incorrecta.

Actividad:

1. Ejecutar `005A`.
2. Filtrar registros con `variant=json`.
3. Revisar `json_parseable`, `parsed_json` y `contains_expected_answer`.
4. Separar fallos de formato de fallos de contenido.

Registro:

| Tarea | JSON parseable | Contiene esperada | Tipo de fallo | Observación |
| --- | --- | --- | --- | --- |
| `arithmetic` | | | | |
| `ordering` | | | | |
| `constraint` | | | | |

Tipos de fallo sugeridos:

- formato inválido;
- respuesta incorrecta;
- respuesta correcta con texto extra;
- clave inesperada;
- valor ambiguo.

### 005E - Sensibilidad a temperatura

Pregunta: ¿las tareas con respuesta esperada son sensibles al sampling?

Hipótesis: aumentar `temperature` puede aumentar variabilidad y errores, especialmente en tareas donde el formato importa.

Ejecuciones sugeridas:

```bash
python3 scripts/run_reasoning_tasks.py \
  --model llama3.2:3b \
  --repeat 3 \
  --temperature 0.0
```

```bash
python3 scripts/run_reasoning_tasks.py \
  --model llama3.2:3b \
  --repeat 3 \
  --temperature 0.8
```

Registro:

| Temperatura | Tarea | Variante | Aciertos observados | Fallos observados | Comentario |
| --- | --- | --- | --- | --- | --- |
| 0.0 | | | | | |
| 0.8 | | | | | |

Limitación: comparar temperaturas requiere mantener fijo modelo, tareas, variantes y `num_predict`.

## Observaciones

Durante este módulo se deben anotar observaciones como:

- si la respuesta contiene la respuesta esperada;
- si la respuesta final contradice la verificación;
- si una explicación plausible termina en error;
- si `json_parseable` falla aunque el contenido sea comprensible;
- si `eval_count` aumenta al pedir descomposición;
- si `done_reason` sugiere truncamiento;
- si una variante mejora una tarea pero empeora otra;
- si hay variabilidad entre repeticiones con los mismos parámetros;
- si el modelo responde con texto adicional pese a restricciones.

Separar:

- observación directa: respuesta, flags y métricas del JSONL;
- evaluación: comparación con la respuesta esperada;
- inferencia: posible efecto del patrón de prompt;
- limitación: evaluación automática simple, pocas tareas, ausencia de verificador externo;
- siguiente experimento: más tareas, más modelos o validación programática.

Plantilla de observación:

| Campo | Registro |
| --- | --- |
| Modelo | |
| Tarea | |
| Variante | |
| Respuesta esperada | |
| Respuesta generada | |
| `contains_expected_answer` | |
| `json_parseable` | |
| `eval_count` | |
| `done_reason` | |
| Observación directa | |
| Evaluación | |
| Inferencia razonable | |
| Limitación | |

Comando de inspección línea a línea:

```bash
python3 -c 'import json,sys; [print(json.dumps(json.loads(line), ensure_ascii=False, indent=2)) for line in open(sys.argv[1], encoding="utf-8")]' results/005-reasoning-tasks/<archivo>.jsonl
```

JSONL contiene un objeto JSON por línea. No tratar el archivo completo como un único documento JSON.

## Conclusiones

El razonamiento, en este módulo, se estudia como comportamiento observable en tareas con respuesta esperada. No se demuestra acceso al proceso interno del modelo. Una explicación generada es texto generado; puede ayudar a inspeccionar consistencia, pero no prueba por sí sola cómo se obtuvo la respuesta.

Conclusiones que el módulo debe comprobar experimentalmente:

- una respuesta correcta debe evaluarse contra una respuesta esperada o un criterio explícito;
- pedir pasos, verificación o JSON cambia el contexto y puede cambiar la salida;
- descomponer no garantiza acierto;
- una explicación plausible puede acompañar una respuesta incorrecta;
- JSON facilita evaluación automática, pero introduce fallos de formato;
- las tareas de razonamiento siguen dependiendo de modelo, prompt, template, runtime y parámetros.

Antes de avanzar al módulo 6, el estudiante debe poder:

- distinguir razonamiento observable de razonamiento interno;
- diseñar tareas pequeñas con respuesta esperada;
- comparar variantes de prompt sin cambiar varias variables a la vez;
- leer `contains_expected_answer` y `json_parseable` sin sobreinterpretarlos;
- detectar contradicciones entre verificación y respuesta final;
- explicar por qué un patrón de prompt no es universal aunque funcione en una tarea.

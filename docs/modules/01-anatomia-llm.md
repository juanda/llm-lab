# 01-anatomia-llm

## Objetivo

Estudiar qué hay realmente dentro de un LLM y cómo transforma texto en predicciones de tokens. Este módulo continúa el principio fijado en el módulo 0: para el modelo no existen modos internos como chat, raw, RAG o agente. Solo existen secuencias de tokens.

El objetivo no es memorizar una descripción teórica del Transformer, sino conectar cada concepto con una observación reproducible usando Ollama y modelos locales.

Este módulo no introduce RAG, agentes, RLHF, DPO, fine tuning, interpretabilidad mecanicista avanzada ni entrenamiento desde cero. Esos temas requieren entender antes tokenización, embeddings, parámetros, atención y salida probabilística.

## Conceptos

### ¿Qué es realmente un LLM?

Un LLM es una red neuronal entrenada para modelar secuencias de texto. En los modelos modernos usados en este laboratorio, normalmente hablamos de redes basadas en arquitectura Transformer.

En inferencia, el modelo recibe una secuencia de tokens y calcula una distribución de probabilidad para el siguiente token.

Un LLM no debe confundirse con:

```text
LLM ≠ base de datos
LLM ≠ buscador
LLM ≠ programa simbólico clásico
LLM ≠ memoria humana
```

Esto no significa que un LLM no pueda producir información útil. Significa que el mecanismo observado no es una consulta directa a una tabla de hechos, sino una predicción condicionada por una secuencia de entrada y por los patrones aprendidos durante entrenamiento.

Observación asociada: comparar respuestas de modelos distintos ante el mismo prompt muestra comportamiento lingüístico y capacidad de generalización, pero no demuestra que el modelo esté buscando en una base de datos interna.

Experimento asociado: `001C - Mismo prompt, modelos de distinto tamaño`.

### Modelo autoregresivo

Un modelo autoregresivo genera texto reutilizando su propia salida como parte de la siguiente entrada.

Flujo conceptual:

```text
Prompt
↓
Token 1
↓
Prompt + Token 1
↓
Token 2
↓
Prompt + Token 1 + Token 2
↓
Token 3
```

La frase completa no aparece de golpe como una unidad semántica indivisible. Emerge al repetir muchas veces la predicción del siguiente token.

Observación asociada: el experimento `000-next-token` registra fragmentos de streaming y métricas como `eval_count`, lo que permite observar la generación incremental aunque Ollama no exponga necesariamente los IDs exactos de cada token.

Experimento asociado: `001D - Autoregresión observada`.

### Una inferencia frente a una respuesta completa

Conviene distinguir una inferencia elemental de una respuesta completa.

Una inferencia, en el sentido mínimo que nos interesa aquí, predice el siguiente token a partir de la secuencia disponible:

```text
Prompt
↓
Predicción de Token 1
```

Una respuesta completa aparece cuando el runtime repite el mismo proceso muchas veces:

```text
Prompt
↓
Token 1
↓
Prompt + Token 1
↓
Token 2
↓
Prompt + Token 1 + Token 2
↓
...
↓
Respuesta completa
```

El Transformer no genera internamente una respuesta completa y después la imprime. En cada paso calcula una distribución para el siguiente token. La respuesta que leemos emerge por repetición del mismo proceso autoregresivo, selección de tokens y detokenización final.

No existe una representación interna única y legible de la respuesta completa antes de generarla. Lo que existe son estados internos numéricos que permiten calcular el siguiente token probable bajo el contexto actual.

Experimento asociado: `001D - Autoregresión observada`.

### Tokens

Un token es una unidad discreta usada por el modelo para representar texto. No equivale necesariamente a una palabra.

Un token puede ser:

- una palabra completa;
- una subpalabra;
- una parte de una palabra;
- un espacio junto con texto;
- un signo de puntuación;
- un carácter especial;
- un token especial usado por una plantilla de chat.

Ejemplos conceptuales:

```text
El cielo es azul.
```

podría dividirse en unidades similares a:

```text
El | cielo | es | azul | .
```

Pero otra palabra puede partirse:

```text
inteligencia artificial
```

en unidades similares a:

```text
int | elig | encia | artificial
```

En inglés, un identificador técnico puede partirse de forma distinta:

```text
LearningML
```

podría quedar como:

```text
Learning | ML
```

Estos ejemplos son aproximaciones pedagógicas. La partición real depende del tokenizer concreto del modelo.

Observación asociada: si dos modelos tienen tokenizers distintos, pueden contar diferente el mismo texto. En Ollama se puede observar indirectamente mediante `prompt_eval_count`, aunque no siempre se obtienen los tokens exactos.

Experimento asociado: `001A - Tokenización comparada`.

### Tokenización

Antes de entrar al modelo, el texto se transforma en IDs numéricos.

```text
Texto
↓
Tokenizer
↓
IDs de tokens
↓
Modelo
```

El modelo no recibe caracteres Unicode como los vemos en pantalla. Recibe IDs que indexan elementos de su vocabulario. El tokenizer es una pieza crítica del sistema: si cambia el tokenizer, cambia la secuencia de IDs.

Observación asociada: Ollama informa `prompt_eval_count` en las respuestas de `/api/generate`. Esa métrica permite medir cuántos tokens de prompt procesó el runtime, pero no muestra necesariamente la lista exacta de tokens.

Limitación experimental: si se necesita inspeccionar tokens exactos, este laboratorio deberá incorporar más adelante tokenizers específicos, por ejemplo desde Hugging Face. En este módulo basta con registrar la limitación y medir conteos observables.

### Vocabulario

El vocabulario de un modelo es el conjunto de tokens que su tokenizer puede producir y que el modelo puede representar.

Cada modelo puede tener:

- su propio tokenizer;
- su propio tamaño de vocabulario;
- sus propios tokens especiales;
- distintas reglas para espacios, símbolos, subpalabras o código.

Por eso dos modelos pueden convertir el mismo texto visible en secuencias de IDs distintas.

Observación asociada: modelos como `qwen2.5-coder:3b` y `llama3.2:3b` pueden reportar distinto `prompt_eval_count` para el mismo prompt, especialmente cuando intervienen templates de chat.

Experimentos asociados: `001A` y `000-template-vs-raw`.

### Embeddings

Los IDs de token no entran al Transformer como números ordinales con significado aritmético directo. El ID selecciona un vector aprendido en una tabla de embeddings.

```text
Token ID
↓
Vector de embedding
```

Ese vector tiene una dimensión fija. Ollama permite observar esta propiedad con:

```bash
ollama show <modelo>
```

En la salida aparece como `embedding length`.

Ejemplo de interpretación:

```text
embedding length 2048
```

significa que cada token se representa internamente como un vector de 2048 componentes antes de pasar por las capas del modelo.

Observación asociada: `qwen2.5-coder:3b` y `llama3.2:3b` pueden tener dimensiones de embedding distintas. Eso es una propiedad arquitectónica observable con `ollama show`.

Experimento asociado: `001B - Parámetros del modelo`.

#### Qué NO es un embedding

Un embedding no es una definición del token.

Un embedding no es un significado simbólico escrito en una estructura que podamos leer directamente.

Un embedding no es una explicación humana del concepto representado por el token.

La relación correcta es:

```text
Token
↓
Vector numérico aprendido
```

El vector existe dentro de un espacio vectorial: una región matemática donde cada token queda representado por muchas coordenadas numéricas. La utilidad semántica no vive en una coordenada aislada ni en una etiqueta legible, sino en relaciones matemáticas entre vectores aprendidas durante entrenamiento.

Por ejemplo, si dos tokens aparecen en contextos parecidos durante entrenamiento, sus vectores pueden acabar ocupando posiciones relacionadas en ese espacio. Esa relación puede ayudar al modelo a generalizar, pero no equivale a que el embedding contenga una definición explícita.

En este módulo no estudiaremos álgebra lineal avanzada. Solo fijamos la idea: los embeddings son vectores aprendidos que permiten al Transformer operar sobre tokens.

### Parámetros

Los parámetros son valores numéricos aprendidos durante entrenamiento. Incluyen matrices de embeddings, pesos de atención, pesos de redes feed-forward y otros valores internos.

Cuando se dice que un modelo tiene `0.5B`, `3B` o más parámetros, se está hablando de cientos o miles de millones de valores numéricos.

Distinción importante:

- arquitectura: la forma del sistema, por ejemplo capas, dimensiones, atención y redes internas;
- pesos: los valores concretos aprendidos dentro de esa arquitectura.

Dos modelos pueden compartir una familia arquitectónica y comportarse distinto porque sus pesos, tokenizer, datos de entrenamiento, template o parámetros de ejecución son distintos.

Relación experimental:

- más parámetros suelen implicar más memoria y coste de inferencia;
- más parámetros no garantizan mejor respuesta en todo caso;
- la cuantización puede reducir memoria a costa de precisión numérica.

Experimentos asociados: `001B` y `001C`.

### Transformer

Un Transformer es una arquitectura neuronal diseñada para procesar secuencias. En este módulo solo necesitamos su mapa básico:

```text
IDs de tokens
↓
Embeddings
↓
Capas Transformer
  - atención
  - feed-forward
  - normalizaciones y conexiones residuales
↓
Logits
↓
Probabilidades
↓
Siguiente token
```

Cada capa transforma la representación de los tokens. La salida final permite calcular una puntuación para cada token del vocabulario.

No estudiaremos todavía la matemática de matrices, queries, keys y values. En este módulo basta con entender que el Transformer convierte una secuencia de vectores en una distribución para continuar la secuencia.

### Atención

La atención permite que el modelo combine información de posiciones anteriores de la secuencia al calcular la representación de cada token.

Intuición:

- algunos tokens anteriores serán más relevantes que otros para predecir el siguiente;
- el mecanismo de atención calcula relaciones internas entre posiciones;
- esa relación es matemática, no comprensión humana.

Ejemplo:

```text
El cielo es
```

Para continuar la secuencia, el modelo puede usar patrones aprendidos donde `cielo` se relaciona frecuentemente con `azul`, pero esa relación aparece como cálculo sobre vectores y pesos, no como una regla simbólica escrita a mano.

Observación asociada: cambiar el contexto anterior puede cambiar radicalmente el siguiente token probable. Esto conecta con el principio del módulo 0: cambiar la secuencia de tokens de entrada cambia el comportamiento.

### Logits y probabilidades

El modelo no produce directamente una frase completa. Para cada paso de generación produce puntuaciones sobre el vocabulario. Esas puntuaciones se llaman logits.

Flujo conceptual:

```text
Estado interno del modelo
↓
Logits sobre el vocabulario
↓
Softmax
↓
Distribución de probabilidad
↓
Selección del siguiente token
```

`softmax` convierte puntuaciones en una distribución de probabilidad. Después el runtime selecciona el siguiente token usando parámetros como `temperature`, límites de generación y otros mecanismos de muestreo.

Ollama no expone por defecto todos los logits en los scripts de este laboratorio. Por tanto, en este módulo trataremos logits y probabilidades como mecanismo conceptual inferido a partir del comportamiento observable.

Experimento asociado: comparar salidas con distintos modelos y parámetros permite observar los efectos de esa selección, aunque no veamos la distribución completa.

### Del logit al token seleccionado

El token generado no tiene por qué ser siempre el token con mayor probabilidad. Después de calcular logits y probabilidades, el runtime aplica una estrategia de selección.

Flujo:

```text
Logits
↓
Softmax
↓
Distribución de probabilidad
↓
Sampling
↓
Token generado
```

Estrategias y parámetros importantes:

- greedy decoding: selecciona el token más probable en cada paso;
- `temperature`: modifica cuánta variabilidad permite el muestreo;
- top-k: restringe la selección a los `k` tokens más probables;
- top-p: restringe la selección al conjunto mínimo de tokens cuya probabilidad acumulada supera un umbral.

El objetivo de estos mecanismos es controlar cómo se pasa de una distribución de probabilidad a un token concreto. Con baja variabilidad, la salida tiende a ser más estable. Con más variabilidad, pueden aparecer respuestas más diversas y también más errores.

Experimento asociado: los experimentos del módulo 0 sobre temperatura muestran que el comportamiento observable cambia aunque el prompt y el modelo se mantengan constantes. Lo que cambia es el proceso de selección del siguiente token.

### Salida del modelo

La salida observable de Ollama es texto, pero ese texto es el resultado de varios pasos:

```text
Distribución del siguiente token
↓
Token seleccionado
↓
Nueva secuencia
↓
Nueva predicción
↓
Texto final detokenizado
```

La respuesta final es una reconstrucción textual realizada por el runtime a partir de tokens generados.

Conclusión conceptual: cuando leemos una respuesta completa, estamos viendo el resultado acumulado de muchas decisiones locales de generación.

### Nota metodológica: uso de `raw=true`

Cuando el objetivo experimental es estudiar continuación textual, puede ser conveniente usar:

```json
{
  "raw": true
}
```

Esto reduce la influencia de:

- templates;
- system prompts;
- formatos de conversación.

Pero `raw` no significa comportamiento interno distinto del modelo.

```text
raw ≠ modo interno diferente
```

`raw=true` solo cambia la forma en que el runtime construye la secuencia de entrada. El Transformer sigue recibiendo tokens y prediciendo el siguiente token. Esta nota conecta directamente con el principio del módulo 0:

```text
No existen modos internos.
Solo secuencias de tokens.
```

Experimentos asociados: `000-next-token`, `000-template-vs-raw` y `001D - Autoregresión observada`.

### Errores frecuentes al aprender LLM

Estos errores conceptuales son comunes y deben evitarse desde este módulo:

- pensar que un token equivale siempre a una palabra;
- pensar que el modelo genera una respuesta completa de una sola vez;
- pensar que un embedding es una definición simbólica;
- pensar que el modelo siempre elige el token más probable;
- pensar que chat y raw son modos internos del modelo;
- pensar que los parámetros son conocimiento explícito almacenado como frases o hechos legibles;
- pensar que una respuesta correcta demuestra que el modelo consultó una base de datos interna;
- pensar que una diferencia de salida se explica solo por los pesos sin revisar template, system prompt, runtime y parámetros.

### Tabla de conceptos fundamentales

| Concepto | Definición breve |
| --- | --- |
| Token | Unidad discreta de texto usada por el tokenizer y el modelo; no equivale necesariamente a una palabra. |
| Tokenizer | Componente que transforma texto en IDs de tokens y permite detokenizar la salida. |
| Vocabulario | Conjunto de tokens que un modelo puede representar mediante su tokenizer. |
| Embedding | Vector numérico aprendido asociado a un token. |
| Parámetro | Valor numérico aprendido durante entrenamiento, como pesos de embeddings, atención o redes internas. |
| Transformer | Arquitectura neuronal que procesa secuencias mediante capas, atención y transformaciones vectoriales. |
| Atención | Mecanismo matemático que relaciona posiciones de la secuencia para calcular representaciones útiles. |
| Logit | Puntuación no normalizada que el modelo asigna a un token candidato del vocabulario. |
| Sampling | Proceso por el que el runtime selecciona un token a partir de probabilidades. |
| Autoregresión | Generación en la que cada token producido se añade al contexto para predecir el siguiente. |

## Hipótesis

1. Un LLM no almacena texto como una base de datos consultable; modela patrones de secuencias de tokens aprendidos durante entrenamiento.
2. El mismo texto visible puede producir conteos de tokens distintos según el modelo, el tokenizer y la plantilla aplicada por el runtime.
3. Modelos de distinto tamaño o arquitectura pueden producir respuestas con diferencias observables en claridad, longitud, latencia y métricas de generación.
4. `embedding length`, `context length`, cuantización y número de parámetros son propiedades observables del modelo local mediante Ollama.
5. La generación autoregresiva puede observarse indirectamente mediante streaming, `eval_count` y respuestas parciales, aunque no se expongan logits ni tokens exactos.
6. Cambios en sampling, como `temperature`, pueden cambiar el token seleccionado aunque los pesos, el prompt visible y el modelo no cambien.
7. Usar `raw=true` puede aproximar mejor una continuación textual directa, pero no activa un modo interno distinto del Transformer.

## Experimentos

### 001A - Tokenización comparada

Objetivo: observar que distintos textos se dividen en tokens de forma no intuitiva y que Ollama no siempre permite ver la lista exacta de tokens.

Textos sugeridos:

```text
El cielo es azul.
LearningML
inteligencia artificial
def fibonacci(n):
¡Hola! ¿Qué tal?
```

Registro mínimo:

- texto original;
- modelo usado;
- modo usado, si aplica;
- `prompt_eval_count`, si Ollama lo informa;
- tokens aproximados, solo si se dispone de una herramienta externa fiable;
- diferencias observadas.

Limitación: los scripts actuales de Ollama registran conteos (`prompt_eval_count`), pero no tokens exactos. La inspección exacta se deja para una actividad posterior con tokenizers específicos.

### 001B - Parámetros del modelo

Objetivo: extraer información observable del modelo usando Ollama.

Comandos:

```bash
ollama show qwen2.5-coder:0.5b
ollama show qwen2.5-coder:3b
ollama show llama3.2:3b
```

Script recomendado:

```bash
python3 scripts/model_inventory.py \
  --models qwen2.5-coder:0.5b qwen2.5-coder:3b llama3.2:3b
```

Registrar:

- arquitectura;
- número de parámetros;
- context length;
- embedding length;
- cuantización;
- capacidades.

### 001C - Mismo prompt, modelos de distinto tamaño

Objetivo: comparar cómo cambia la salida entre modelos pequeños y algo mayores.

Prompt base:

```text
Explica en una frase qué es un token en un LLM.
```

Modelos:

- `qwen2.5-coder:0.5b`;
- `qwen2.5-coder:3b`;
- `llama3.2:3b`.

Script recomendado:

```bash
python3 scripts/compare_models.py \
  --models qwen2.5-coder:0.5b qwen2.5-coder:3b llama3.2:3b \
  --prompt "Explica en una frase qué es un token en un LLM."
```

Registrar:

- respuesta;
- longitud;
- claridad observada;
- tiempo de pared;
- `eval_count`, si Ollama lo informa;
- `tokens_per_second`, si puede calcularse.

### 001D - Autoregresión observada

Objetivo: reutilizar el experimento `000-next-token` para mostrar cómo la respuesta se genera paso a paso.

Prompt:

```text
El cielo es
```

Comparar:

- modo raw;
- modo chat/template.

Comandos:

```bash
python3 scripts/run_next_token.py \
  --model qwen2.5-coder:3b \
  --prompt "El cielo es" \
  --num-predict 16 \
  --temperature 0.2
```

```bash
python3 scripts/run_next_token.py \
  --model qwen2.5-coder:3b \
  --prompt "El cielo es" \
  --num-predict 16 \
  --temperature 0.2 \
  --raw
```

Registro mínimo:

- fragmentos de streaming;
- respuesta final;
- `prompt_eval_count`;
- `eval_count`;
- diferencia entre prompt visible y prompt real inferido.

## Observaciones

Durante este módulo se deben registrar observaciones como:

- si un texto corto produce más tokens de los esperados;
- si un modelo reporta distinta arquitectura, dimensión de embedding o cuantización;
- si un modelo pequeño produce una respuesta más corta, menos precisa o más lenta que otro bajo las mismas condiciones;
- si la primera ejecución es más lenta por carga inicial;
- si faltan métricas en la respuesta de Ollama;
- si una salida se explica mejor por template o system prompt que por pesos del modelo.
- si una diferencia entre repeticiones puede explicarse por sampling;
- si usar `raw=true` cambia la salida al reducir la plantilla conversacional.

Separar siempre:

- lo que sabemos: por ejemplo, la salida de `ollama show`;
- lo que observamos: por ejemplo, `prompt_eval_count=29`;
- lo que inferimos: por ejemplo, que el template añadió tokens;
- lo que queda pendiente: por ejemplo, inspeccionar tokens exactos con un tokenizer externo.

## Conclusiones

Un LLM es una red neuronal autoregresiva que transforma secuencias de tokens en distribuciones para el siguiente token. La respuesta textual final emerge al repetir ese proceso y detokenizar los tokens generados.

El módulo 1 debe dejar claras estas conclusiones:

- el texto visible no entra directamente al Transformer como caracteres;
- el tokenizer convierte texto en IDs;
- los IDs seleccionan embeddings;
- un embedding es un vector aprendido, no una definición simbólica;
- el Transformer procesa vectores mediante capas, atención y feed-forward;
- la salida inmediata del modelo son logits sobre el vocabulario;
- el runtime convierte logits en probabilidades, aplica sampling, selecciona tokens y finalmente reconstruye texto;
- una respuesta de un LLM es el resultado acumulado de muchas predicciones locales de tokens;
- la secuencia de entrada influye tanto en el comportamiento observable como los propios pesos del modelo;
- propiedades como parámetros, contexto, embeddings y cuantización son observables con Ollama;
- no se debe atribuir una diferencia de comportamiento a una sola causa sin registrar modelo, tokenizer, template, system prompt, runtime y parámetros.

Antes de avanzar, el estudiante debe ser capaz de explicar el siguiente flujo:

```text
Texto visible
↓
Runtime + template
↓
Tokenizer
↓
IDs de tokens
↓
Embeddings
↓
Transformer
↓
Logits
↓
Probabilidades
↓
Token generado
↓
Texto detokenizado
```

## Referencias iniciales

- Attention Is All You Need: paper fundacional de la arquitectura Transformer.
- Hugging Face, causal language modeling: referencia práctica para entender entrenamiento autoregresivo.
- Hugging Face, tokenizers: referencia práctica para entender tokenización, vocabularios y subpalabras.
- The Illustrated Transformer: explicación visual útil para conectar embeddings, atención y capas Transformer.

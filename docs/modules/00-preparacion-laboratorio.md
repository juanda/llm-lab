# 00-preparacion-laboratorio

## Objetivo

Preparar un laboratorio local para estudiar LLMs mediante experimentos reproducibles con Ollama. Este módulo no intenta construir una aplicación de IA: establece el entorno, el vocabulario mínimo, las primeras hipótesis y los protocolos básicos de observación.

Este módulo no implementa RAG, embeddings, agentes ni fine tuning. Esos temas se tratarán cuando el curso haya introducido tokenización, contexto, atención, entrenamiento y evaluación.

## Conceptos

### ¿Qué hace realmente un LLM?

La idea central del laboratorio es esta:

Un LLM predice el siguiente token.

De esta idea se derivan varias consecuencias que se comprobarán durante el curso:

- un LLM no busca respuestas como lo haría un buscador;
- un LLM no consulta una base de conocimiento interna durante la inferencia;
- un LLM recibe una secuencia de tokens y produce una distribución probable para el siguiente token;
- el texto final emerge al repetir ese proceso muchas veces.

Flujo conceptual de generación:

```text
Prompt
  ↓
Tokenizer
  ↓
Tokens
  ↓
Modelo
  ↓
Tokens
  ↓
Detokenizer
  ↓
Texto
```

En este módulo aún no estudiaremos la tokenización en detalle. La usaremos como una caja negra observable: el prompt entra como texto, el runtime lo convierte en tokens, el modelo genera nuevos tokens y el runtime los convierte de nuevo en texto.

### Modelo y runtime

Modelo no es lo mismo que runtime.

Un modelo es el artefacto aprendido durante entrenamiento. Contiene parámetros numéricos que codifican patrones estadísticos del lenguaje. Por sí solo no es una aplicación ejecutable: necesita software que cargue sus pesos, prepare entradas, ejecute inferencia y convierta resultados en texto.

Un runtime es el software que ejecuta el modelo. Gestiona memoria, tokenización, cuantización, planificación de inferencia, uso de CPU/GPU, parámetros de generación y exposición de una interfaz de uso.

Ollama es una herramienta que facilita descargar, gestionar y ejecutar modelos locales mediante una API HTTP y una interfaz de línea de comandos.

llama.cpp es un runtime de inferencia para modelos tipo LLaMA y compatibles. Está optimizado para ejecutar modelos localmente, especialmente en formatos cuantizados.

GGUF es un formato de archivo usado para distribuir modelos compatibles con llama.cpp. Normalmente contiene pesos del modelo, metadatos y datos necesarios para la tokenización.

Relación conceptual:

```text
Modelo
  ↓
GGUF
  ↓
llama.cpp
  ↓
Ollama
  ↓
API HTTP
```

Esta cadena simplifica la realidad, pero sirve como mapa inicial: el modelo es lo que se ejecuta; llama.cpp es una pieza de runtime; Ollama empaqueta esa ejecución y la expone de forma cómoda.

### Prompt

El prompt es la entrada textual entregada al sistema. En este módulo se usará como variable controlada: si cambia el prompt, cambia el experimento.

### Parámetros de generación

Los parámetros principales para los primeros experimentos son:

- `temperature`: controla cómo se muestrea el siguiente token desde la distribución del modelo. Valores bajos reducen variación; valores altos aumentan diversidad y riesgo de respuestas inesperadas.
- `num_predict`: limita cuántos tokens nuevos puede generar el modelo.
- `seed`: cuando el runtime y el modelo lo soportan, ayuda a repetir muestreos bajo las mismas condiciones.

`num_ctx` no se usa como variable experimental en este módulo. La ventana de contexto se estudiará en el módulo 3.

### Métricas observables

Los scripts registran métricas verificables:

- `wall_time_seconds`: tiempo medido por el script entre petición y respuesta.
- `total_duration_ns`: duración total reportada por Ollama.
- `load_duration_ns`: tiempo de carga reportado por Ollama.
- `prompt_eval_count`: tokens de prompt procesados, si Ollama los informa.
- `eval_count`: tokens generados, si Ollama los informa.
- `tokens_per_second`: tokens generados por segundo, calculados a partir de `eval_count` y `eval_duration_ns`.
- `response_length_chars`: longitud de la respuesta en caracteres.

No todas las métricas están disponibles para todos los modelos o versiones de Ollama. Cuando falte una métrica, el resultado debe conservar `null` en vez de inventar valores.

### Reproducibilidad

Un experimento reproducible debe declarar:

- modelo usado;
- runtime usado;
- versión de Ollama, si se registra manualmente;
- prompt;
- parámetros de generación;
- número de repeticiones;
- fecha de ejecución;
- máquina o entorno, si se comparan rendimientos.

## Hipótesis

1. Un LLM genera texto mediante una secuencia de pasos de predicción del siguiente token.
2. Si se mantiene fijo el prompt y aumenta `temperature`, aumentará la diversidad textual entre repeticiones.
3. Si se mantiene fijo el modelo y aumenta `num_predict`, aumentará el tiempo total de generación.
4. Las métricas de rendimiento solo son comparables cuando modelo, runtime, hardware, parámetros y carga del sistema son equivalentes.

## Experimentos

### 000-next-token

Observa el comportamiento básico de generación como proceso iterativo.

Ruta:

```text
experiments/000-next-token/
```

Script:

```bash
python3 scripts/run_next_token.py --model llama3.2:3b
```

Resultado esperado:

- un archivo JSONL en `results/000-next-token/`;
- fragmentos de texto recibidos durante la generación;
- métricas finales reportadas por Ollama;
- una primera intuición experimental de que el texto se construye paso a paso.

Nota: Ollama permite observar la generación en streaming, pero no expone necesariamente los IDs exactos de cada token en la API usada aquí. Por eso este experimento registra pasos incrementales de salida textual y métricas de token cuando el runtime las informa.

### 001-temperature

Evalúa cómo cambia la variabilidad de las respuestas al modificar `temperature`.

Ruta:

```text
experiments/001-temperature/
```

Script:

```bash
python3 scripts/run_temperature.py --model llama3.2:3b
```

Resultado esperado:

- un archivo JSONL en `results/001-temperature/`;
- varias respuestas para el mismo prompt;
- metadatos con modelo, temperatura, repetición y métricas de Ollama.

### 002-performance

Mide latencia y throughput de generación con un conjunto pequeño de prompts controlados.

Ruta:

```text
experiments/002-performance/
```

Script:

```bash
python3 scripts/run_performance.py --model llama3.2:3b
```

Resultado esperado:

- un archivo JSONL en `results/002-performance/`;
- mediciones por prompt y repetición;
- `tokens_per_second` cuando Ollama informe `eval_count` y `eval_duration`.

### Experimento aplazado: 003-context

El experimento `003-context` queda reservado para el módulo 3, Contexto y Memoria.

Justificación: todavía no se han explicado tokenización, contexto, atención ni ventana de contexto. Ejecutarlo ahora mezclaría preparación del laboratorio con conceptos que necesitan una base previa.

## Observaciones

Durante la ejecución se deben anotar observaciones como:

- si el modelo no sigue el formato solicitado;
- si cambia el idioma de respuesta;
- si aparecen respuestas no deterministas con la misma configuración;
- si una primera ejecución es más lenta por carga inicial del modelo;
- si el sistema estaba ejecutando otras tareas pesadas;
- si la salida en streaming llega en fragmentos que no coinciden visualmente con palabras completas.

Las observaciones deben quedar en los `README.md` de cada experimento o junto a los archivos generados en `results/`.

## Conclusiones

Este módulo deja el laboratorio listo para experimentar con LLMs locales de forma verificable. La conclusión principal no debe ser que un modelo es mejor o peor en abstracto, sino que bajo unas condiciones concretas se observaron determinados comportamientos medibles.

Antes de avanzar a módulos posteriores, el estudiante debe ser capaz de:

- distinguir modelo y runtime;
- explicar que un LLM genera texto prediciendo el siguiente token;
- ejecutar Ollama localmente;
- descargar y seleccionar un modelo;
- lanzar los experimentos iniciales del módulo 0;
- leer archivos JSONL de resultados;
- distinguir entre hipótesis, medición, observación y conclusión;
- evitar extrapolar resultados fuera de las condiciones experimentales.

## Preguntas fundamentales del laboratorio

Estas preguntas se responderán progresivamente durante el curso:

- ¿Qué es un token?
- ¿Cómo representa significado un LLM?
- ¿Dónde está la memoria?
- ¿Qué es un embedding?
- ¿Cómo aparece el razonamiento?
- ¿Qué aporta RLHF?
- ¿Qué diferencia hay entre un LLM y un agente?
- ¿Qué es realmente una alucinación?
- ¿Cómo funciona RAG?
- ¿Cómo se entrenan los modelos?

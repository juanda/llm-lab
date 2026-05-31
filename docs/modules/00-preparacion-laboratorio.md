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

### Prompt visible vs Prompt real

El modelo no recibe necesariamente solo el texto que introduce el usuario. Ese texto es el prompt visible: la parte que vemos y controlamos directamente en el experimento.

El prompt real es la entrada efectiva que llega al modelo después de que el runtime prepara la petición. Conceptualmente:

```text
Prompt real =
Prompt visible
+ System Prompt
+ Chat Template
+ Tokens especiales
+ Parámetros de generación
```

Esta fórmula no significa que todos los runtimes concatenen literalmente esos elementos del mismo modo. Sirve para recordar que la entrada experimental observada puede ser mayor que el texto visible.

Dos modelos distintos pueden producir resultados diferentes ante el mismo prompt visible porque el prompt real no tiene por qué ser idéntico. Las diferencias pueden venir de:

- plantilla de chat;
- system prompt;
- alineamiento;
- entrenamiento instruct;
- tokens especiales esperados por cada familia de modelo;
- parámetros de generación aplicados por el runtime.

Principio recurrente del laboratorio:

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

Este principio debe revisarse al interpretar resultados en módulos posteriores, especialmente en prompt engineering, comparativa de modelos, alineamiento, RAG, tool calling y agentes.

Diagrama experimental:

```text
Prompt visible: "El cielo es"
        │
        ▼
Ollama prepara la petición
        │
        ├── system prompt
        ├── chat template
        ├── tokens especiales
        ├── stop tokens
        └── parámetros
        │
        ▼
Prompt real evaluado por el modelo
        │
        ▼
Tokens generados
```

### Chat Template

Una plantilla de chat es una regla de serialización que transforma una conversación estructurada en una secuencia textual y de tokens especiales compatible con un modelo concreto.

En una interfaz de chat, el usuario ve mensajes separados por rol. El modelo, en cambio, recibe una secuencia preparada por el runtime. Ollama obtiene la plantilla desde los metadatos o la definición del modelo disponible localmente y la aplica cuando se usa la API en modo normal.

Sirve para convertir una conversación en una forma similar a la que el modelo vio durante entrenamiento instruct. Por eso dos modelos pueden responder de forma diferente al mismo prompt visible: no solo cambia el modelo, también puede cambiar la forma exacta de representar roles, turnos, inicio de respuesta y final de mensaje.

Ejemplo conceptual:

```text
system
  ...
user
  El cielo es
assistant
  ...
```

Este ejemplo no debe interpretarse como formato universal. Un modelo puede usar etiquetas distintas, separadores específicos, tokens de inicio o fin de turno, o convenciones propias de su entrenamiento instruct.

Hipótesis asociada: si dos modelos usan templates distintos, el mismo prompt visible puede convertirse en prompts reales distintos.

Experimento asociado: `experiments/000-template-vs-raw/`.

Observación esperada: en modo normal, una respuesta puede parecer conversación de asistente; en modo raw, puede parecer más una continuación textual.

### System Prompt

El system prompt es una instrucción de alto nivel que condiciona el comportamiento del asistente antes del mensaje del usuario. Puede definir identidad, estilo, restricciones o capacidades esperadas.

En Ollama, el system prompt puede venir de:

- la definición del modelo;
- un `Modelfile`;
- el campo `system` enviado a la API;
- una aplicación que envuelve a Ollama.

Se puede inspeccionar con:

```bash
ollama show <modelo>
```

Ejemplos reales observados localmente:

```text
ollama show qwen2.5-coder:3b
```

mostró una sección `System` con una instrucción de identidad y asistencia para Qwen.

```text
ollama show llama3.2:3b
```

mostró parámetros `stop`, capacidades y metadatos del modelo; el system prompt base aparece dentro del `TEMPLATE` exportado en el Modelfile.

Conclusión experimental: antes de comparar respuestas entre modelos, hay que inspeccionar si uno de ellos recibe instrucciones de sistema explícitas o diferentes.

### Modelfile

Un `Modelfile` describe cómo Ollama construye o ejecuta una variante local de un modelo. No contiene necesariamente los pesos completos, pero sí instrucciones de configuración importantes para la inferencia.

Se puede visualizar con:

```bash
ollama show --modelfile qwen2.5-coder:3b
```

```bash
ollama show --modelfile llama3.2:3b
```

También puede exportarse al repositorio con:

```bash
python3 scripts/export_modelfile.py qwen2.5-coder:3b llama3.2:3b
```

Los archivos se guardan en:

```text
references/models/
```

Bloques relevantes:

- `FROM`: identifica el modelo base o blob local usado por Ollama.
- `TEMPLATE`: define cómo se serializa una conversación antes de entrar al modelo.
- `SYSTEM`: define una instrucción de sistema por defecto, si existe.
- `PARAMETER`: define parámetros de ejecución, por ejemplo stop tokens.

Ejemplos reales observados localmente:

```text
qwen2.5-coder:3b
SYSTEM You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
```

```text
llama3.2:3b
PARAMETER stop <|start_header_id|>
PARAMETER stop <|end_header_id|>
PARAMETER stop <|eot_id|>
```

Estos fragmentos son evidencia verificable: deben regenerarse en cada máquina si se usan como base para una conclusión.

### Stop Tokens

Los stop tokens son secuencias que indican al runtime cuándo detener la generación. Pueden ser tokens especiales del modelo o cadenas configuradas como parámetros.

En un Modelfile aparecen como:

```text
PARAMETER stop ...
```

Su función es evitar que el modelo continúe generando más allá del final esperado de un turno de chat. Están relacionados con:

- `EOS`: token de fin de secuencia aprendido o definido por la familia de modelos;
- finalización de respuestas;
- separación entre turnos de usuario y asistente;
- comportamiento de chat.

Hipótesis asociada: si dos modelos usan stop tokens distintos, pueden cortar respuestas en puntos distintos aunque reciban prompts visibles iguales.

Observación asociada: si una respuesta termina de forma brusca o justo antes de una marca de turno, revisar los `PARAMETER stop` del Modelfile.

### Modo raw de Ollama

Ollama permite solicitar generación sin aplicar la plantilla de chat del modelo mediante el campo:

```json
{
  "raw": true
}
```

En modo raw, el prompt enviado a `/api/generate` se trata como texto de entrada directo. Esto permite estudiar la continuación textual de una secuencia sin que Ollama añada la plantilla de chat normal del modelo.

El modo raw no elimina todos los factores experimentales: siguen existiendo tokenizer, runtime, parámetros de generación, cuantización y comportamiento aprendido del modelo. Su utilidad en este módulo es aislar la diferencia entre generación con template y generación sin template de chat.

Comparación:

```text
Modo Chat
Prompt visible -> Ollama aplica chat template -> Prompt real -> Modelo
```

```text
Modo Raw
Prompt visible -> Ollama lo envía como prompt directo -> Modelo
```

Cuándo usar modo raw:

- para estudiar continuaciones textuales;
- para comparar el efecto de una plantilla de chat;
- para reducir variables cuando se investiga generación autoregresiva.

Cuándo no usar modo raw como sustituto de chat:

- cuando se evalúa comportamiento de asistente;
- cuando el modelo fue entrenado principalmente para seguir formatos instruct;
- cuando se necesitan roles, herramientas o turnos estructurados.

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
5. Dos modelos pueden generar secuencias completamente distintas ante el mismo prompt visible porque el prompt real recibido por el modelo no es idéntico.

## Experimentos

### 000-next-token

Observa el comportamiento básico de generación como proceso iterativo y compara dos variantes de entrada: modo normal con plantilla de chat y modo raw sin plantilla de chat.

Ruta:

```text
experiments/000-next-token/
```

Script:

```bash
python3 scripts/run_next_token.py --model llama3.2:3b
```

Experimento A, modo normal:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es"
```

Objetivo: observar la generación cuando Ollama aplica la plantilla del modelo.

Experimento B, modo raw:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es" \
  --raw
```

Objetivo: observar la continuación textual sin plantilla de chat. El script envía `"raw": true` a la API de Ollama.

Resultado esperado:

- un archivo JSONL en `results/000-next-token/`;
- fragmentos de texto recibidos durante la generación;
- métricas finales reportadas por Ollama;
- una primera intuición experimental de que el texto se construye paso a paso.
- la variante usada (`template_chat` o `raw`) registrada en cada JSONL.

Nota: Ollama permite observar la generación en streaming, pero no expone necesariamente los IDs exactos de cada token en la API usada aquí. Por eso este experimento registra pasos incrementales de salida textual y métricas de token cuando el runtime las informa.

Actividad práctica:

Comparar el prompt:

```text
El cielo es
```

en estos modelos:

- Qwen2.5-Coder;
- Llama 3.2.

Para cada modelo ejecutar:

- modo normal;
- modo raw.

Registrar:

- tokens generados reportados por Ollama;
- respuesta final;
- diferencias observadas entre modelos;
- diferencias observadas entre modo normal y modo raw.

### 000-template-vs-raw

Compara explícitamente el efecto de la plantilla de chat frente al modo raw en dos modelos locales.

Ruta:

```text
experiments/000-template-vs-raw/
```

Script:

```bash
python3 scripts/run_template_vs_raw.py
```

Modelos por defecto:

- `qwen2.5-coder:3b`;
- `llama3.2:3b`.

Prompt base:

```text
El cielo es
```

Resultado esperado:

- un archivo JSONL en `results/000-template-vs-raw/`;
- un registro por modelo y variante;
- `eval_count` cuando Ollama lo informe;
- respuesta final;
- comparación entre `template_chat` y `raw`.

Antes de interpretar los resultados, inspeccionar la configuración de los modelos:

```bash
python3 scripts/show_model_info.py qwen2.5-coder:3b llama3.2:3b
python3 scripts/export_modelfile.py qwen2.5-coder:3b llama3.2:3b
```

Hipótesis: si el modo normal y el modo raw producen salidas distintas para el mismo modelo, parte del comportamiento observado procede del template, system prompt, stop tokens o parámetros aplicados por Ollama.

Conclusión esperada: el experimento no decide qué modelo es mejor. Delimita qué parte de la observación pertenece al sistema completo de inferencia.

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
- si una diferencia parece explicarse por template, system prompt, modo raw, alineamiento o comportamiento instruct.

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
- explicar por qué el prompt visible no siempre coincide con el prompt real.

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
- ¿Por qué dos modelos generan continuaciones radicalmente distintas para el mismo prompt?

Para responder a esta última pregunta se investigarán system prompts, templates, modo raw, alineamiento y comportamiento instruct.

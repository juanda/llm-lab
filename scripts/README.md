# Scripts

Utilidades para ejecutar experimentos locales con Ollama.

## Requisitos

1. Instalar Ollama.
2. Arrancar el servicio local si no está ya activo:

```bash
ollama serve
```

3. Descargar un modelo pequeño para empezar:

```bash
ollama pull llama3.2:3b
```

4. Ejecutar los scripts desde la raíz del repositorio.

Los scripts usan solo la biblioteca estándar de Python y llaman a:

```text
http://localhost:11434/api/generate
```

Las utilidades de inspección llaman al binario local `ollama`.

## Cliente común

`ollama_client.py` contiene funciones compartidas para:

- invocar `/api/generate` con `stream=false`;
- medir tiempo de pared;
- calcular tokens por segundo cuando Ollama informa las métricas necesarias;
- escribir resultados JSONL.

## Experimentos del módulo 0

### 000-next-token

```bash
python3 scripts/run_next_token.py --model llama3.2:3b
```

Opciones principales:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 12 \
  --temperature 0.2
```

Modo raw:

```bash
python3 scripts/run_next_token.py \
  --model llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 12 \
  --temperature 0.2 \
  --raw
```

Este experimento usa streaming para observar la generación incremental. Los fragmentos observados no tienen por qué coincidir visualmente con tokens completos. Sin `--raw`, Ollama aplica la plantilla normal del modelo; con `--raw`, el script envía `"raw": true` para estudiar la continuación textual sin template de chat.

### 000-template-vs-raw

```bash
python3 scripts/run_template_vs_raw.py
```

Opciones principales:

```bash
python3 scripts/run_template_vs_raw.py \
  --models qwen2.5-coder:3b llama3.2:3b \
  --prompt "El cielo es" \
  --num-predict 24 \
  --temperature 0.2
```

Este experimento ejecuta cada modelo en modo normal y en modo raw, y registra `variant`, `raw`, `eval_count`, respuesta final y métricas de Ollama.

### 001-temperature

```bash
python3 scripts/run_temperature.py --model llama3.2:3b
```

Opciones principales:

```bash
python3 scripts/run_temperature.py \
  --model llama3.2:3b \
  --temperatures 0.0 0.3 0.7 1.0 \
  --repeat 3 \
  --num-predict 160
```

### 002-performance

```bash
python3 scripts/run_performance.py --model llama3.2:3b
```

Opciones principales:

```bash
python3 scripts/run_performance.py \
  --model llama3.2:3b \
  --repeat 5 \
  --num-predict 200
```

## Experimentos de módulos posteriores

### 003-context

Este experimento pertenece al módulo 3, Contexto y Memoria. Se documenta aquí porque ya existe un script asociado, pero no debe tratarse como parte del módulo 0.

```bash
python3 scripts/run_context.py --model llama3.2:3b
```

Opciones principales:

```bash
python3 scripts/run_context.py \
  --model llama3.2:3b \
  --fact-counts 8 32 96 \
  --num-ctx 4096
```

Este experimento no implementa RAG, embeddings ni agentes: solo incluye hechos dentro del prompt.

## Inspección de modelos

Guardar información de `ollama show <modelo>`:

```bash
python3 scripts/show_model_info.py qwen2.5-coder:3b llama3.2:3b
```

Exportar Modelfiles:

```bash
python3 scripts/export_modelfile.py qwen2.5-coder:3b llama3.2:3b
```

Las salidas se guardan en:

```text
references/models/
```

## Salidas

Cada ejecución crea un archivo `.jsonl` en `results/<id-experimento>/`. Cada línea es una muestra independiente con prompt, respuesta, parámetros y métricas.

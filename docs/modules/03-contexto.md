# 03-contexto

## Conceptos

## Hipótesis

## Experimentos

### 003-context

Este experimento se retoma en este módulo porque requiere haber introducido tokenización, atención, contexto y ventana de contexto.

Pregunta: ¿puede el modelo recuperar información incluida explícitamente dentro de un prompt largo?

Hipótesis: si la información relevante está dentro del contexto y el prompt es claro, el modelo debería poder recuperarla. Al aumentar la cantidad de hechos irrelevantes, pueden aparecer errores de recuperación o respuestas incompletas.

Restricción: este experimento no usa RAG, embeddings, bases de datos vectoriales ni agentes. Toda la información se incluye directamente en el prompt.

Variables:

- variable independiente: número de hechos sintéticos incluidos en el prompt;
- variables controladas: modelo, formato de hechos, pregunta, `num_predict` y `num_ctx`;
- variables observadas: respuesta del modelo, valor esperado, acierto local por coincidencia de texto y métricas de Ollama.

Ejecución desde la raíz del repositorio:

```bash
python3 scripts/run_context.py --model llama3.2:3b
```

Opciones útiles:

```bash
python3 scripts/run_context.py \
  --model llama3.2:3b \
  --fact-counts 8 32 96 \
  --num-ctx 4096
```

El script crea resultados en:

```text
results/003-context/
```

## Observaciones

Anotar después de ejecutar:

- modelo usado;
- tamaños de contexto probados;
- si el modelo devolvió exactamente el identificador pedido;
- si aparecieron respuestas con explicación extra;
- si la evaluación automática por coincidencia de texto coincide con una inspección manual;
- métricas ausentes o valores `null` reportados por Ollama.

## Conclusiones

Completar después de revisar los resultados. La evaluación por coincidencia de texto es deliberadamente simple; si falla, inspeccionar manualmente antes de sacar conclusiones fuertes.

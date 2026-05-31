# 003-context

## Módulo

Este experimento pertenece al módulo 3, Contexto y Memoria. No forma parte del módulo 0 porque requiere conceptos todavía no introducidos allí: tokenización, contexto, atención y ventana de contexto.

## Pregunta

¿Puede el modelo recuperar información incluida explícitamente dentro de un prompt largo?

## Hipótesis

Si la información relevante está dentro del contexto y el prompt es claro, el modelo debería poder recuperarla. Al aumentar la cantidad de hechos irrelevantes, pueden aparecer errores de recuperación o respuestas incompletas.

## Restricción

Este experimento no usa RAG, embeddings, bases de datos vectoriales ni agentes. Toda la información se incluye directamente en el prompt.

## Variables

- Variable independiente: número de hechos sintéticos incluidos en el prompt.
- Variables controladas: modelo, formato de hechos, pregunta, `num_predict`, `num_ctx`.
- Variables observadas: respuesta del modelo, valor esperado, acierto local por coincidencia de texto, métricas de Ollama.

## Ejecución

Desde la raíz del repositorio:

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

Anotar aquí observaciones después de ejecutar el experimento:

- Modelo usado:
- Tamaños de contexto probados:
- ¿El modelo devolvió exactamente el identificador pedido?
- ¿Aparecieron respuestas con explicación extra?

## Conclusiones

Completar después de revisar los resultados. La evaluación por coincidencia de texto es deliberadamente simple; si falla, inspeccionar manualmente antes de sacar conclusiones fuertes.

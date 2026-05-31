# 000-next-token

## Pregunta

¿Qué se observa cuando un LLM genera una respuesta corta paso a paso?

## Hipótesis

Un LLM genera texto prediciendo sucesivamente el siguiente token. El texto final emerge de una cadena de decisiones locales de generación.

## Conceptos

Este experimento es deliberadamente mínimo. No intenta explicar todavía la tokenización interna ni la atención. Solo observa que la generación no aparece como un bloque conceptual completo, sino como una secuencia incremental producida por el runtime.

Ollama devuelve fragmentos en streaming. Esos fragmentos permiten observar la construcción progresiva de la respuesta, aunque no siempre equivalen a tokens visibles completos ni exponen los IDs reales de token.

## Variables

- Variable independiente: prompt simple.
- Variables controladas: modelo, `temperature`, `num_predict`.
- Variables observadas: fragmentos generados, texto final, métricas de Ollama, tiempo de pared.

## Ejecución

Desde la raíz del repositorio:

```bash
python3 scripts/run_next_token.py --model llama3.2:3b
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

## Observaciones

Anotar aquí observaciones después de ejecutar el experimento:

- Modelo usado:
- Prompt:
- ¿La respuesta apareció en fragmentos sucesivos?
- ¿Los fragmentos coincidieron con palabras completas?
- ¿Cuántos tokens generados reportó Ollama?

## Conclusiones

Completar después de revisar el JSONL. La conclusión debe distinguir entre lo observado directamente, fragmentos de streaming y texto final, y lo inferido a partir de métricas de token.

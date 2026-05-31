# 002-performance

## Pregunta

¿Qué latencia y throughput se observan al generar texto con un modelo local en Ollama?

## Hipótesis

La primera petición puede ser más lenta por carga del modelo. Para un mismo modelo y hardware, respuestas más largas tenderán a requerir más tiempo total.

## Variables

- Variables independientes: prompt, `num_predict`, repetición.
- Variables controladas: modelo, runtime, máquina local.
- Variables observadas: `wall_time_seconds`, `total_duration_ns`, `eval_count`, `eval_duration_ns`, `tokens_per_second`.

## Ejecución

Desde la raíz del repositorio:

```bash
python3 scripts/run_performance.py --model llama3.2:3b
```

Opciones útiles:

```bash
python3 scripts/run_performance.py \
  --model llama3.2:3b \
  --repeat 5 \
  --num-predict 200
```

El script crea resultados en:

```text
results/002-performance/
```

## Observaciones

Anotar aquí observaciones después de ejecutar el experimento:

- Modelo usado:
- Hardware:
- ¿La primera ejecución fue más lenta?
- ¿Hubo variación fuerte entre repeticiones?

## Conclusiones

Completar después de revisar los resultados. No comparar contra otros equipos salvo que se hayan igualado modelo, parámetros y condiciones de ejecución.

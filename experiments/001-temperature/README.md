# 001-temperature

## Pregunta

¿Cómo cambia la variabilidad de las respuestas cuando se modifica `temperature` manteniendo fijo el prompt?

## Hipótesis

Con temperaturas bajas, las respuestas serán más parecidas entre repeticiones. Con temperaturas altas, aumentarán las diferencias de vocabulario, estructura y contenido.

## Variables

- Variable independiente: `temperature`.
- Variables controladas: modelo, prompt, `num_predict`, número de repeticiones.
- Variables observadas: texto generado, longitud de respuesta, tiempo de generación y métricas reportadas por Ollama.

## Ejecución

Desde la raíz del repositorio:

```bash
python3 scripts/run_temperature.py --model llama3.2:3b
```

Opciones útiles:

```bash
python3 scripts/run_temperature.py \
  --model llama3.2:3b \
  --temperatures 0.0 0.3 0.7 1.0 \
  --repeat 3 \
  --num-predict 160
```

El script crea resultados en:

```text
results/001-temperature/
```

## Observaciones

Anotar aquí observaciones después de ejecutar el experimento:

- Temperatura usada:
- Modelo usado:
- ¿Se observó más diversidad con temperaturas altas?
- ¿Hubo respuestas fuera de formato?

## Conclusiones

Completar después de comparar los resultados JSONL. La conclusión debe mencionar solo lo observado con el modelo, prompt y parámetros usados.

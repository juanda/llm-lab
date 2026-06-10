# ADR-0005

## Decisión

Documentar los experimentos dentro de la sección `## Experimentos` de cada módulo y eliminar el directorio `experiments/`.

## Contexto

La documentación de algunos experimentos existía en dos lugares: el módulo didáctico y un `README.md` dentro de `experiments/`. Esa duplicación obligaba a mantener preguntas, hipótesis, variables, comandos y conclusiones en paralelo.

## Justificación

Cada módulo debe contener conceptos, hipótesis, experimentos y conclusiones. Mantener el protocolo experimental dentro del módulo reduce redundancia y hace que la lectura siga el orden pedagógico completo.

Los resultados generados siguen guardándose como JSONL en `results/`, porque esos archivos son datos experimentales y no documentación duplicada.

## Consecuencias

Los scripts siguen identificando experimentos por nombre y escribiendo en `results/<experimento>/`.

Cuando se añada o modifique un experimento, el protocolo debe actualizarse en el módulo correspondiente. Si hay observaciones manuales, deben quedar en el módulo o junto a los resultados generados.

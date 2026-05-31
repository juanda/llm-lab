# ADR-0004

## Decisión

Ampliar el experimento `000-next-token` para comparar dos variantes: generación normal con la plantilla del modelo aplicada por Ollama y generación en modo raw mediante `"raw": true`.

## Contexto

El prompt visible `El cielo es` produjo comportamientos radicalmente distintos en modelos instruct diferentes. La observación mostró que el experimento no estaba aislando únicamente la predicción del siguiente token a partir del texto escrito por el usuario.

La entrada efectiva del modelo puede incluir system prompt, plantilla de chat, tokens especiales y parámetros de generación, además del prompt visible.

## Justificación

El laboratorio debe mantener una separación verificable entre lo que se controla directamente y lo que el runtime construye antes de ejecutar inferencia. Comparar modo normal y modo raw permite observar cuándo el comportamiento procede de la continuación textual y cuándo está mediado por la interfaz de chat del modelo.

## Consecuencias

El módulo 0 introduce el principio recurrente de que una respuesta observada es resultado de modelo, template, system prompt, runtime y parámetros. Los resultados de `000-next-token` deben registrar la variante ejecutada y si se usó `raw`.

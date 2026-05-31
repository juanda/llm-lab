# ADR-0003

## Decisión

Limitar el módulo 0 a preparación del laboratorio, distinción entre modelo y runtime, y observación básica de generación autoregresiva.

## Contexto

El experimento de contexto requiere explicar tokenización, atención, contexto y ventana de contexto. Incluirlo en el módulo 0 adelanta conceptos que todavía no tienen base experimental en el curso.

## Justificación

El primer módulo debe fijar la idea recurrente del laboratorio: un LLM genera texto prediciendo sucesivamente el siguiente token. Los experimentos iniciales deben observar ese comportamiento, variabilidad por temperatura y métricas de rendimiento local.

## Consecuencias

`003-context` queda asignado al módulo 3, Contexto y Memoria. El módulo 0 incorpora `000-next-token` como experimento previo a temperatura y rendimiento.

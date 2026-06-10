# LLM Lab

Laboratorio experimental para comprender los LLM mediante experimentación práctica.

## Objetivos
- Comprender la arquitectura de los LLM.
- Experimentar con Ollama, llama.cpp y modelos abiertos.
- Reproducir resultados clásicos de papers.
- Construir RAG, agentes y herramientas.
- Analizar alineamiento e interpretabilidad.

## Principios del laboratorio

- Un LLM predice el siguiente token a partir de una secuencia de tokens.
- Para el Transformer no existen modos internos como chat, raw, RAG, tool calling o agentes.
- Esos nombres describen formas de construir el contexto de entrada alrededor del modelo.
- Todo experimento debe documentar modelo, prompt visible, prompt real inferido, template, system prompt, runtime y parámetros.

## Estructura
- docs/
- notebooks/
- datasets/
- results/
- adrs/
- scripts/
- references/

## Módulos disponibles

- [00 - Preparación del laboratorio](docs/modules/00-preparacion-laboratorio.md)
- [01 - Anatomía de un LLM](docs/modules/01-anatomia-llm.md)
- [02 - Generación de texto](docs/modules/02-generacion.md)
- [03 - Contexto y memoria](docs/modules/03-contexto.md)

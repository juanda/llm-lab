---
name: llm-results-analyst
description: Analyze LLM Lab JSONL experiment outputs under results/ and convert them into careful observations, summaries, tables, and module conclusions. Use when reviewing experiment runs, comparing Ollama models or parameters, interpreting metrics, updating Observaciones or Conclusiones sections, or checking whether claims are supported by recorded data.
---

# LLM Results Analyst

## Workflow

1. Identify the relevant `results/<id-experimento>/` directory and matching module section.
2. Read JSONL records with a structured parser, not ad hoc string matching.
3. Summarize only fields present in the data.
4. Separate observation from interpretation.
5. Update module `## Observaciones` or `## Conclusiones` only when the result supports the claim.

## Analysis Checklist

For each run, inspect:

- `experiment`, `run_id`, `model`;
- `prompt` and `options`;
- `variant` and `raw`, if present;
- `temperature`, `num_predict`, `num_ctx`, repetitions, or prompt index;
- `prompt_eval_count`, `eval_count`, durations, `tokens_per_second`;
- `done` and `done_reason`;
- `response` and qualitative behavior.

When comparing records, verify that controlled variables really stayed fixed.

## Interpretation Rules

- Say "observed" for values directly present in JSONL.
- Say "inferred" for explanations such as template effects or prompt-real differences.
- Do not generalize from one model, one prompt, or one run to LLMs in general.
- Do not rank models as better unless the metric and task define better.
- Treat missing or `null` metrics as missing data, not zero.
- Watch for first-run load effects in latency and throughput analysis.

## Useful Local Commands

Inspect available results:

```bash
find results -name "*.jsonl" | sort
```

Preview records:

```bash
python3 -m json.tool results/<id-experimento>/<run>.jsonl
```

For multi-line JSONL analysis, prefer short Python one-liners or small temporary scripts that parse each line with `json.loads`.

## Reporting

A useful result summary usually includes:

- experiment and run files analyzed;
- model and parameters;
- number of records;
- table of key metrics;
- observed behavior;
- cautious interpretation;
- limitations and next experiment.

When updating course prose, write conclusions in the same style as the modules: concrete, operational, and tied to the recorded conditions.

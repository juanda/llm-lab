---
name: ollama-experiment-designer
description: Design, implement, and document reproducible Ollama experiments for the LLM Lab repository. Use when creating or modifying Python scripts under scripts/, adding experiment protocols to module sections, choosing local models and generation parameters, recording JSONL metadata, or checking that an LLM experiment separates observation from interpretation.
---

# Ollama Experiment Designer

## Workflow

1. Read `AGENTS.md`, `scripts/README.md`, `scripts/ollama_client.py`, and the target module.
2. Reuse `scripts/ollama_client.py` unless the experiment needs streaming or a different API shape.
3. Document the experiment in the module's `## Experimentos` section.
4. Write results to `results/<id-experimento>/` as JSONL.
5. Keep scripts runnable from the repository root with only Python standard library dependencies unless a new dependency is explicitly justified.

## Experiment Contract

Every experiment must declare:

- question;
- hypothesis;
- independent variables;
- controlled variables;
- observed variables;
- model names;
- prompt visible;
- prompt real inferred, when relevant;
- template/system prompt/raw mode considerations;
- generation parameters such as `temperature`, `num_predict`, `num_ctx`;
- output schema and result directory;
- interpretation limits.

## Script Patterns

Use argparse options for:

- `--model` or `--models`;
- prompt text or a clearly documented default prompt;
- generation parameters;
- repetitions when measuring variability;
- `--output-dir` defaulting to `results/<id-experimento>`.

Each JSONL record should include enough metadata to reproduce the run:

- `experiment`;
- `model`;
- `prompt`;
- `options`;
- `response`;
- `response_length_chars`;
- `wall_time_seconds`;
- Ollama metrics such as `prompt_eval_count`, `eval_count`, durations, `done`, `done_reason`;
- experiment-specific fields such as `variant`, `raw`, `temperature`, `repetition`, expected answer, or correctness flag.

## Ollama Discipline

- Prefer local, small models first: `llama3.2:3b`, `qwen2.5-coder:3b`, or `qwen2.5-coder:0.5b`.
- If comparing models, keep prompt and generation options fixed.
- If comparing templates, record `raw` and `variant`.
- If measuring performance, control for first-run load effects and current machine load.
- If testing context, avoid calling it RAG unless retrieval, external documents, or vector search are actually implemented.

## Validation

If Ollama is available, run a small smoke test with low `num_predict`. If not available, validate syntax and argument parsing where possible.

Always run:

```bash
python3 -m py_compile scripts/*.py
git diff --check
```

Report whether real model execution was performed.

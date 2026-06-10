---
name: llm-lab-module-writer
description: Develop and revise LLM Lab course modules in docs/modules for a practical Ollama-based course. Use when adding a new module, expanding an existing module, restructuring module content, aligning a module with the study plan, or improving didactic explanations that must include concepts, hypotheses, experiments, observations, and conclusions.
---

# LLM Lab Module Writer

## Workflow

1. Read `AGENTS.md`, `README.md`, `docs/00-plan-estudios.md`, and the target module before editing.
2. Check adjacent modules when sequencing matters.
3. Preserve the course thread: an LLM predicts the next token from a token sequence.
4. Keep experiments inside the module section `## Experimentos`; do not recreate `experiments/`.
5. Add or update an ADR when the change alters repository structure, experiment methodology, naming conventions, or course scope.

## Module Shape

Every module must include these headings:

```markdown
## Objetivo
## Conceptos
## Hipótesis
## Experimentos
## Observaciones
## Conclusiones
```

If the module is still a placeholder, add `## Objetivo` before `## Conceptos`. Keep existing valid content and fill gaps conservatively.

## Didactic Rules

- Start with the module's purpose and explicit non-goals.
- Introduce dependencies before dependent concepts.
- Mark claims as observation, hypothesis, inference, limitation, or conclusion.
- Avoid anthropomorphic explanations unless contrasting them with the actual mechanism.
- Avoid using RAG, agents, tool calling, fine tuning, RLHF, DPO, or interpretability details before their module has introduced the required base.
- Prefer concrete prompts, tables, and measurable criteria over broad prose.

## Experiment Sections

For each experiment, include:

- question;
- hypothesis;
- variables: independent, controlled, observed;
- command or script from `scripts/`;
- result path under `results/<id-experimento>/`;
- table or checklist for observations;
- limits on interpretation.

Use local models that are practical with Ollama, especially `llama3.2:3b`, `qwen2.5-coder:3b`, or smaller variants already referenced by the repo.

## Interpretation Discipline

When explaining behavior, distinguish:

- model weights;
- tokenizer;
- prompt visible;
- prompt real inferred;
- chat template;
- system prompt;
- stop tokens;
- runtime;
- generation parameters;
- hardware and current system load.

Do not claim a model "knows", "remembers", "searches", or "reasons" unless the module defines that term operationally and the experiment supports the statement.

## Validation

Before finishing:

- run `rg -n "experiments/|TODO|FIXME" docs/modules README.md AGENTS.md` when relevant;
- run `git diff --check`;
- mention if experiments were not executed because Ollama or models were unavailable.

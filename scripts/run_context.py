"""Run experiment 003-context against a local Ollama model."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from ollama_client import append_jsonl, generate, result_record


def build_facts(count: int) -> tuple[str, str, str]:
    target_index = max(1, count * 2 // 3)
    expected_code = f"clave-{target_index:03d}-verde"
    facts = []
    for index in range(1, count + 1):
        code = expected_code if index == target_index else f"clave-{index:03d}-azul"
        facts.append(f"Hecho {index:03d}: el código de la muestra {index:03d} es {code}.")
    return "\n".join(facts), f"muestra {target_index:03d}", expected_code


def build_prompt(facts: str, target_label: str) -> str:
    return (
        "Lee los hechos siguientes y responde únicamente con el código exacto "
        f"asociado a {target_label}.\n\n"
        f"{facts}\n\n"
        f"Pregunta: ¿Cuál es el código de la {target_label}?\n"
        "Respuesta:"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--fact-counts", nargs="+", type=int, default=[8, 32, 96])
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--num-predict", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--output-dir", default="results/003-context")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}.jsonl")

    records = []
    for fact_count in args.fact_counts:
        facts, target_label, expected_code = build_facts(fact_count)
        prompt = build_prompt(facts, target_label)
        options = {
            "temperature": args.temperature,
            "num_predict": args.num_predict,
            "num_ctx": args.num_ctx,
        }
        result = generate(
            model=args.model,
            prompt=prompt,
            options=options,
            ollama_url=args.ollama_url,
        )
        answer = result.response.strip()
        exact_match = answer == expected_code
        contains_expected = expected_code in answer
        records.append(
            result_record(
                experiment="003-context",
                model=args.model,
                prompt=prompt,
                options=options,
                result=result,
                extra={
                    "run_id": run_id,
                    "fact_count": fact_count,
                    "target_label": target_label,
                    "expected_code": expected_code,
                    "answer": answer,
                    "exact_match": exact_match,
                    "contains_expected": contains_expected,
                },
            )
        )
        print(
            f"fact_count={fact_count} expected={expected_code} "
            f"exact_match={exact_match} contains_expected={contains_expected}"
        )

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

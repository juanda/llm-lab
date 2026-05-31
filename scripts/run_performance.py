"""Run experiment 002-performance against a local Ollama model."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from ollama_client import append_jsonl, generate, result_record


DEFAULT_PROMPTS = [
    "Resume en español qué es un modelo de lenguaje en tres frases.",
    "Enumera cinco riesgos de evaluar un LLM solo con impresiones subjetivas.",
    "Escribe una explicación breve sobre la diferencia entre prompt y contexto.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--num-predict", type=int, default=180)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--output-dir", default="results/002-performance")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}.jsonl")
    options = {
        "temperature": args.temperature,
        "num_predict": args.num_predict,
    }

    records = []
    for prompt_index, prompt in enumerate(DEFAULT_PROMPTS, start=1):
        for repetition in range(1, args.repeat + 1):
            result = generate(
                model=args.model,
                prompt=prompt,
                options=options,
                ollama_url=args.ollama_url,
            )
            record = result_record(
                experiment="002-performance",
                model=args.model,
                prompt=prompt,
                options=options,
                result=result,
                extra={
                    "run_id": run_id,
                    "prompt_index": prompt_index,
                    "repetition": repetition,
                },
            )
            records.append(record)
            print(
                "prompt="
                f"{prompt_index} repetition={repetition} "
                f"wall_time={record['wall_time_seconds']:.3f}s "
                f"tokens_per_second={record['tokens_per_second']}"
            )

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

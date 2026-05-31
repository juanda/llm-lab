"""Run experiment 001-temperature against a local Ollama model."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from ollama_client import append_jsonl, generate, result_record


DEFAULT_PROMPT = (
    "Explica en español, en un solo párrafo breve, por qué los modelos de "
    "lenguaje pueden producir respuestas distintas ante el mismo prompt."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--temperatures", nargs="+", type=float, default=[0.0, 0.3, 0.7, 1.0])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--num-predict", type=int, default=160)
    parser.add_argument("--output-dir", default="results/001-temperature")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}.jsonl")

    records = []
    for temperature in args.temperatures:
        options = {
            "temperature": temperature,
            "num_predict": args.num_predict,
        }
        for repetition in range(1, args.repeat + 1):
            result = generate(
                model=args.model,
                prompt=args.prompt,
                options=options,
                ollama_url=args.ollama_url,
            )
            records.append(
                result_record(
                    experiment="001-temperature",
                    model=args.model,
                    prompt=args.prompt,
                    options=options,
                    result=result,
                    extra={
                        "run_id": run_id,
                        "repetition": repetition,
                        "temperature": temperature,
                    },
                )
            )
            print(f"temperature={temperature} repetition={repetition} chars={len(result.response)}")

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

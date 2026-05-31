"""Run experiment 000-template-vs-raw against local Ollama models."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from ollama_client import append_jsonl, generate, result_record


DEFAULT_MODELS = ["qwen2.5-coder:3b", "llama3.2:3b"]
DEFAULT_PROMPT = "El cielo es"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--num-predict", type=int, default=24)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--output-dir", default="results/000-template-vs-raw")
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
    for model in args.models:
        for raw in (False, True):
            variant = "raw" if raw else "template_chat"
            result = generate(
                model=model,
                prompt=args.prompt,
                options=options,
                raw=raw,
                ollama_url=args.ollama_url,
            )
            records.append(
                result_record(
                    experiment="000-template-vs-raw",
                    model=model,
                    prompt=args.prompt,
                    options=options,
                    result=result,
                    extra={
                        "run_id": run_id,
                        "variant": variant,
                        "raw": raw,
                    },
                )
            )
            print(f"model={model} variant={variant} eval_count={result.raw.get('eval_count')}")
            print(result.response)

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

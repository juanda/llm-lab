"""Compare multiple Ollama models on the same prompt."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from ollama_client import DEFAULT_OLLAMA_URL, append_jsonl, generate, result_record


DEFAULT_MODELS = ["qwen2.5-coder:0.5b", "qwen2.5-coder:3b", "llama3.2:3b"]
DEFAULT_PROMPT = "Explica en una frase qué es un token en un LLM."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--num-predict", type=int, default=96)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--output-dir", default="results/001-anatomia-llm")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}-compare-models.jsonl")
    options = {
        "temperature": args.temperature,
        "num_predict": args.num_predict,
    }

    records = []
    for model in args.models:
        result = generate(
            model=model,
            prompt=args.prompt,
            options=options,
            raw=args.raw,
            ollama_url=args.ollama_url,
        )
        record = result_record(
            experiment="001-anatomia-llm",
            model=model,
            prompt=args.prompt,
            options=options,
            result=result,
            extra={
                "variant": "compare_models",
                "run_id": run_id,
                "raw": args.raw,
            },
        )
        records.append(record)
        print(
            f"model={model} chars={record['response_length_chars']} "
            f"eval_count={record['eval_count']} wall_time={record['wall_time_seconds']:.3f}s"
        )
        print(result.response)

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

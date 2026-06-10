"""Run experiment 002-generation-controls against a local Ollama model."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from typing import Any

from ollama_client import append_jsonl, generate, result_record


DEFAULT_PROMPT = (
    "Escribe exactamente una lista numerada de tres recomendaciones para evaluar "
    "una respuesta de un modelo de lenguaje. Termina con la palabra FIN."
)

VARIANTS: list[dict[str, Any]] = [
    {
        "variant": "baseline",
        "description": "temperature baja y longitud suficiente",
        "options": {"temperature": 0.2, "num_predict": 120},
    },
    {
        "variant": "short_length",
        "description": "limite de generacion corto",
        "options": {"temperature": 0.2, "num_predict": 24},
    },
    {
        "variant": "high_temperature",
        "description": "mayor variabilidad por sampling",
        "options": {"temperature": 1.0, "num_predict": 120},
    },
    {
        "variant": "low_top_p",
        "description": "nucleus sampling mas restrictivo",
        "options": {"temperature": 0.8, "top_p": 0.4, "num_predict": 120},
    },
    {
        "variant": "repeat_penalty",
        "description": "penalizacion de repeticion mas alta",
        "options": {"temperature": 0.2, "repeat_penalty": 1.3, "num_predict": 120},
    },
    {
        "variant": "stop_sequence",
        "description": "parada al generar FIN",
        "options": {"temperature": 0.2, "num_predict": 120, "stop": ["FIN"]},
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--output-dir", default="results/002-generation-controls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}.jsonl")

    records = []
    for variant in VARIANTS:
        options = dict(variant["options"])
        for repetition in range(1, args.repeat + 1):
            result = generate(
                model=args.model,
                prompt=args.prompt,
                options=options,
                ollama_url=args.ollama_url,
            )
            records.append(
                result_record(
                    experiment="002-generation-controls",
                    model=args.model,
                    prompt=args.prompt,
                    options=options,
                    result=result,
                    extra={
                        "run_id": run_id,
                        "variant": variant["variant"],
                        "variant_description": variant["description"],
                        "repetition": repetition,
                    },
                )
            )
            print(
                f"variant={variant['variant']} repetition={repetition} "
                f"done_reason={result.raw.get('done_reason')} chars={len(result.response)}"
            )

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

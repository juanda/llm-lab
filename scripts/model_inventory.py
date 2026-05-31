"""Collect observable Ollama model metadata for module 001."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from ollama_client import DEFAULT_OLLAMA_URL, append_jsonl


DEFAULT_MODELS = ["qwen2.5-coder:0.5b", "qwen2.5-coder:3b", "llama3.2:3b"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--output-dir", default="results/001-anatomia-llm")
    return parser.parse_args()


def show_model(*, model: str, ollama_url: str) -> tuple[dict[str, Any], float]:
    payload = {"model": model}
    request = urllib.request.Request(
        f"{ollama_url.rstrip('/')}/api/show",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Check that `ollama serve` is running "
            f"and that the model `{model}` is available."
        ) from exc
    return data, time.perf_counter() - started


def model_record(*, run_id: str, model: str, raw: dict[str, Any], wall_time_seconds: float) -> dict[str, Any]:
    details = raw.get("details") or {}
    model_info = raw.get("model_info") or {}
    return {
        "experiment": "001-anatomia-llm",
        "variant": "model_inventory",
        "run_id": run_id,
        "model": model,
        "architecture": details.get("family") or model_info.get("general.architecture"),
        "parameter_size": details.get("parameter_size"),
        "context_length": model_info.get("llama.context_length") or model_info.get("qwen2.context_length"),
        "embedding_length": model_info.get("llama.embedding_length") or model_info.get("qwen2.embedding_length"),
        "quantization": details.get("quantization_level"),
        "capabilities": raw.get("capabilities"),
        "families": details.get("families"),
        "format": details.get("format"),
        "wall_time_seconds": wall_time_seconds,
        "raw": raw,
    }


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}-model-inventory.jsonl")

    records = []
    for model in args.models:
        raw, wall_time_seconds = show_model(model=model, ollama_url=args.ollama_url)
        record = model_record(
            run_id=run_id,
            model=model,
            raw=raw,
            wall_time_seconds=wall_time_seconds,
        )
        records.append(record)
        print(
            f"model={model} architecture={record['architecture']} "
            f"parameters={record['parameter_size']} embedding={record['embedding_length']}"
        )

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

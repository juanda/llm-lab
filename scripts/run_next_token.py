"""Run experiment 000-next-token with Ollama streaming output."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from ollama_client import append_jsonl, tokens_per_second


DEFAULT_PROMPT = "El cielo es"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--num-predict", type=int, default=16)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Send raw=true to Ollama so the model receives the prompt without the model chat template.",
    )
    parser.add_argument("--output-dir", default="results/000-next-token")
    return parser.parse_args()


def stream_generate(
    *,
    model: str,
    prompt: str,
    options: dict[str, Any],
    ollama_url: str,
    raw: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any], float]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": options,
    }
    if raw:
        payload["raw"] = True
    request = urllib.request.Request(
        f"{ollama_url.rstrip('/')}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    chunks: list[dict[str, Any]] = []
    final: dict[str, Any] = {}
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            for index, line in enumerate(response, start=1):
                if not line.strip():
                    continue
                event = json.loads(line.decode("utf-8"))
                text = event.get("response", "")
                if text:
                    chunks.append({"index": index, "text": text})
                    print(f"{index:03d}: {text!r}")
                if event.get("done"):
                    final = event
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Check that `ollama serve` is running "
            f"and that the model `{model}` is available."
        ) from exc

    return chunks, final, time.perf_counter() - started


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.output_dir, f"{run_id}.jsonl")
    options = {
        "temperature": args.temperature,
        "num_predict": args.num_predict,
    }

    chunks, final, wall_time_seconds = stream_generate(
        model=args.model,
        prompt=args.prompt,
        options=options,
        ollama_url=args.ollama_url,
        raw=args.raw,
    )
    response_text = "".join(chunk["text"] for chunk in chunks)
    variant = "raw" if args.raw else "template_chat"
    record = {
        "experiment": "000-next-token",
        "variant": variant,
        "raw": args.raw,
        "run_id": run_id,
        "model": args.model,
        "prompt": args.prompt,
        "options": options,
        "chunks": chunks,
        "chunk_count": len(chunks),
        "response": response_text,
        "response_length_chars": len(response_text),
        "wall_time_seconds": wall_time_seconds,
        "total_duration_ns": final.get("total_duration"),
        "load_duration_ns": final.get("load_duration"),
        "prompt_eval_count": final.get("prompt_eval_count"),
        "prompt_eval_duration_ns": final.get("prompt_eval_duration"),
        "eval_count": final.get("eval_count"),
        "eval_duration_ns": final.get("eval_duration"),
        "tokens_per_second": tokens_per_second(final),
        "done": final.get("done"),
        "done_reason": final.get("done_reason"),
    }
    append_jsonl(output_path, [record])
    print(f"Final response: {response_text!r}")
    print(f"Wrote 1 record to {output_path}")


if __name__ == "__main__":
    main()

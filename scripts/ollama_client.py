"""Minimal Ollama HTTP client used by the lab experiments."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_OLLAMA_URL = "http://localhost:11434"


@dataclass(frozen=True)
class OllamaResult:
    response: str
    raw: dict[str, Any]
    wall_time_seconds: float


def generate(
    *,
    model: str,
    prompt: str,
    options: dict[str, Any] | None = None,
    system: str | None = None,
    raw: bool = False,
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> OllamaResult:
    """Call Ollama /api/generate with stream disabled."""
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if options:
        payload["options"] = options
    if system:
        payload["system"] = system
    if raw:
        payload["raw"] = True

    request = urllib.request.Request(
        f"{ollama_url.rstrip('/')}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Check that `ollama serve` is running "
            f"and that the model `{model}` is available."
        ) from exc

    return OllamaResult(
        response=data.get("response", ""),
        raw=data,
        wall_time_seconds=time.perf_counter() - started,
    )


def tokens_per_second(raw: dict[str, Any]) -> float | None:
    eval_count = raw.get("eval_count")
    eval_duration_ns = raw.get("eval_duration")
    if not eval_count or not eval_duration_ns:
        return None
    return eval_count / (eval_duration_ns / 1_000_000_000)


def result_record(
    *,
    experiment: str,
    model: str,
    prompt: str,
    options: dict[str, Any],
    result: OllamaResult,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw = result.raw
    record: dict[str, Any] = {
        "experiment": experiment,
        "model": model,
        "prompt": prompt,
        "options": options,
        "response": result.response,
        "response_length_chars": len(result.response),
        "wall_time_seconds": result.wall_time_seconds,
        "total_duration_ns": raw.get("total_duration"),
        "load_duration_ns": raw.get("load_duration"),
        "prompt_eval_count": raw.get("prompt_eval_count"),
        "prompt_eval_duration_ns": raw.get("prompt_eval_duration"),
        "eval_count": raw.get("eval_count"),
        "eval_duration_ns": raw.get("eval_duration"),
        "tokens_per_second": tokens_per_second(raw),
        "done": raw.get("done"),
        "done_reason": raw.get("done_reason"),
    }
    if extra:
        record.update(extra)
    return record


def append_jsonl(path: str, records: list[dict[str, Any]]) -> None:
    with open(path, "a", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            file.write("\n")

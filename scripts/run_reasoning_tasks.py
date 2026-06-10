"""Run experiment 005-reasoning-tasks against a local Ollama model."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from typing import Any

from ollama_client import append_jsonl, generate, result_record


TASKS: list[dict[str, str]] = [
    {
        "task_id": "arithmetic",
        "task_type": "arithmetic",
        "question": (
            "Un cuaderno cuesta 3 euros. Ana compra 4 cuadernos y paga con 20 euros. "
            "Cuanto dinero le devuelven?"
        ),
        "expected_answer": "8",
    },
    {
        "task_id": "ordering",
        "task_type": "logic",
        "question": (
            "Marta es mas alta que Luis. Luis es mas alto que Ana. "
            "Quien es la persona mas baja?"
        ),
        "expected_answer": "Ana",
    },
    {
        "task_id": "constraint",
        "task_type": "constraint",
        "question": (
            "Elige dos numeros distintos de la lista 2, 4, 6, 9 que sumen 13. "
            "Responde con los dos numeros separados por coma."
        ),
        "expected_answer": "4,9",
    },
]


def build_prompt(task: dict[str, str], variant: str) -> str:
    question = task["question"]
    if variant == "direct":
        return f"Responde solo con la respuesta final.\n\nPregunta: {question}\nRespuesta:"
    if variant == "structured":
        return (
            "Resuelve la tarea de forma breve. Devuelve exactamente dos lineas:\n"
            "Verificacion: una comprobacion corta.\n"
            "Respuesta: la respuesta final.\n\n"
            f"Pregunta: {question}"
        )
    if variant == "decompose":
        return (
            "Descompón el problema en pasos breves y termina con una linea "
            "'Respuesta: ...'. No añadas texto despues de la respuesta.\n\n"
            f"Pregunta: {question}"
        )
    if variant == "json":
        return (
            "Resuelve la tarea y devuelve solo JSON valido con las claves "
            '"respuesta" y "verificacion_breve".\n\n'
            f"Pregunta: {question}"
        )
    raise ValueError(f"Unknown variant: {variant}")


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.strip().lower())


def response_contains_expected(response: str, expected: str) -> bool:
    if expected == "4,9":
        normalized = normalize(response)
        return ("4,9" in normalized) or ("9,4" in normalized)
    return normalize(expected) in normalize(response)


def parse_json_response(response: str) -> tuple[bool, Any | None]:
    try:
        return True, json.loads(response.strip())
    except json.JSONDecodeError:
        return False, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--variants", nargs="+", default=["direct", "structured", "decompose", "json"])
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--num-predict", type=int, default=220)
    parser.add_argument("--output-dir", default="results/005-reasoning-tasks")
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
    for task in TASKS:
        for variant in args.variants:
            prompt = build_prompt(task, variant)
            for repetition in range(1, args.repeat + 1):
                result = generate(
                    model=args.model,
                    prompt=prompt,
                    options=options,
                    ollama_url=args.ollama_url,
                )
                json_parseable, parsed_json = parse_json_response(result.response)
                contains_expected = response_contains_expected(result.response, task["expected_answer"])
                records.append(
                    result_record(
                        experiment="005-reasoning-tasks",
                        model=args.model,
                        prompt=prompt,
                        options=options,
                        result=result,
                        extra={
                            "run_id": run_id,
                            "task_id": task["task_id"],
                            "task_type": task["task_type"],
                            "question": task["question"],
                            "expected_answer": task["expected_answer"],
                            "variant": variant,
                            "repetition": repetition,
                            "contains_expected_answer": contains_expected,
                            "json_parseable": json_parseable,
                            "parsed_json": parsed_json,
                        },
                    )
                )
                print(
                    f"task={task['task_id']} variant={variant} repetition={repetition} "
                    f"contains_expected={contains_expected} json_parseable={json_parseable}"
                )

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

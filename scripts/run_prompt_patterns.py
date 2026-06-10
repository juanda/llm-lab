"""Run experiment 004-prompt-patterns against a local Ollama model."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any

from ollama_client import append_jsonl, generate, result_record


DEFAULT_MESSAGE = (
    "Me han cobrado dos veces la suscripcion mensual y necesito que alguien "
    "lo revise hoy. El recibo aparece duplicado en mi banco."
)

EXPECTED_CATEGORY = "facturacion"
EXPECTED_PRIORITY = "alta"


def build_variants(message: str) -> list[dict[str, Any]]:
    return [
        {
            "variant": "vague",
            "description": "instruccion abierta sin formato esperado",
            "prompt": f"Analiza este mensaje de soporte:\n\n{message}",
            "system": None,
        },
        {
            "variant": "explicit_fields",
            "description": "campos pedidos explicitamente en texto",
            "prompt": (
                "Clasifica el mensaje de soporte. Responde con categoria, prioridad "
                "y una justificacion breve.\n\n"
                f"Mensaje: {message}"
            ),
            "system": None,
        },
        {
            "variant": "json_schema",
            "description": "salida JSON con claves especificas",
            "prompt": (
                "Clasifica el mensaje de soporte. Devuelve solo JSON valido con estas claves: "
                '"categoria", "prioridad", "justificacion_breve". '
                'Usa categoria="facturacion" si el problema es de cobros o recibos. '
                'Usa prioridad="alta" si requiere revision hoy.\n\n'
                f"Mensaje: {message}"
            ),
            "system": None,
        },
        {
            "variant": "few_shot_json",
            "description": "ejemplos antes del caso objetivo",
            "prompt": (
                "Clasifica mensajes de soporte y devuelve solo JSON valido.\n\n"
                "Ejemplo 1\n"
                "Mensaje: No puedo cambiar mi contrasena.\n"
                'Respuesta: {"categoria":"acceso","prioridad":"media","justificacion_breve":"problema de acceso sin urgencia explicita"}\n\n'
                "Ejemplo 2\n"
                "Mensaje: Me cobraron dos veces y necesito resolverlo hoy.\n"
                'Respuesta: {"categoria":"facturacion","prioridad":"alta","justificacion_breve":"cobro duplicado con urgencia"}\n\n'
                "Caso objetivo\n"
                f"Mensaje: {message}\n"
                "Respuesta:"
            ),
            "system": None,
        },
        {
            "variant": "system_json",
            "description": "restriccion de formato en system prompt",
            "prompt": f"Mensaje: {message}",
            "system": (
                "Eres un clasificador de soporte. Responde solo JSON valido con las claves "
                '"categoria", "prioridad" y "justificacion_breve".'
            ),
        },
    ]


def parse_json_response(response: str) -> tuple[bool, Any | None]:
    try:
        return True, json.loads(response.strip())
    except json.JSONDecodeError:
        return False, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--message", default=DEFAULT_MESSAGE)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--num-predict", type=int, default=160)
    parser.add_argument("--output-dir", default="results/004-prompt-patterns")
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
    for variant in build_variants(args.message):
        for repetition in range(1, args.repeat + 1):
            result = generate(
                model=args.model,
                prompt=variant["prompt"],
                system=variant["system"],
                options=options,
                ollama_url=args.ollama_url,
            )
            json_parseable, parsed_json = parse_json_response(result.response)
            normalized_response = result.response.lower()
            records.append(
                result_record(
                    experiment="004-prompt-patterns",
                    model=args.model,
                    prompt=variant["prompt"],
                    options=options,
                    result=result,
                    extra={
                        "run_id": run_id,
                        "variant": variant["variant"],
                        "variant_description": variant["description"],
                        "system": variant["system"],
                        "message": args.message,
                        "repetition": repetition,
                        "expected_category": EXPECTED_CATEGORY,
                        "expected_priority": EXPECTED_PRIORITY,
                        "json_parseable": json_parseable,
                        "parsed_json": parsed_json,
                        "contains_expected_category": EXPECTED_CATEGORY in normalized_response,
                        "contains_expected_priority": EXPECTED_PRIORITY in normalized_response,
                    },
                )
            )
            print(
                f"variant={variant['variant']} repetition={repetition} "
                f"json_parseable={json_parseable} chars={len(result.response)}"
            )

    append_jsonl(output_path, records)
    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()

"""Save `ollama show <model>` output for later inspection."""

from __future__ import annotations

import argparse
import os
import subprocess


DEFAULT_MODELS = ["qwen2.5-coder:3b", "llama3.2:3b"]
DEFAULT_OUTPUT_DIR = "references/models"


def safe_model_name(model: str) -> str:
    return model.replace("/", "-").replace(":", "-")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="*", default=DEFAULT_MODELS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def ollama_show(model: str) -> str:
    completed = subprocess.run(
        ["ollama", "show", model],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    for model in args.models:
        output = ollama_show(model)
        path = os.path.join(args.output_dir, f"{safe_model_name(model)}.show.txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write(output)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .assistant import ManufacturingAssistant
from .loader import load_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manufacturing Personal Assistant POC CLI"
    )
    parser.add_argument(
        "--data",
        default="data/unstructured",
        help="Path to unstructured text files (default: data/unstructured)",
    )
    parser.add_argument(
        "--question",
        help="Single question to ask the assistant. If omitted, starts interactive mode.",
    )
    parser.add_argument(
        "--as-of",
        help="Optional YYYY-MM-DD date for deterministic risk calculations.",
    )
    return parser


def parse_as_of(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def run(data_dir: str, question: str | None, as_of: date | None = None) -> int:
    dataset = load_dataset(Path(data_dir))
    assistant = ManufacturingAssistant(dataset, as_of=as_of)

    if question:
        print(assistant.ask(question))
        return 0

    print(assistant.overview())
    print()
    print("Type a question. Use 'exit' or 'quit' to end.")
    while True:
        try:
            prompt = input("mfg-pa> ").strip()
        except EOFError:
            print()
            break
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break
        print(assistant.ask(prompt))
        print()
    return 0


def main() -> int:
    args = build_parser().parse_args()
    as_of = parse_as_of(args.as_of)
    return run(args.data, args.question, as_of)


if __name__ == "__main__":
    raise SystemExit(main())


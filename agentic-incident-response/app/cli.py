import argparse
import json
from pathlib import Path

from app.core.pipeline import review_logs


def main() -> None:
    parser = argparse.ArgumentParser(description="Review JSONL logs and generate incident reports.")
    parser.add_argument("log_file", type=Path, help="Path to a JSONL log file.")
    parser.add_argument("--pretty", action="store_true", help="Print indented JSON output.")
    args = parser.parse_args()

    raw_logs = args.log_file.read_text(encoding="utf-8")
    response = review_logs(raw_logs)
    print(response.model_dump_json(indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

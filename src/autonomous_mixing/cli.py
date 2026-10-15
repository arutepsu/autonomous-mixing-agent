import argparse
import json
import sys
from pathlib import Path

from .audio.analysis import analyze_pair


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="autonomous-mixing")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Run deterministic descriptive kick/bass analysis")
    analyze.add_argument("kick")
    analyze.add_argument("bass")
    analyze.add_argument("--output", default="results/analysis.json")
    args = parser.parse_args(argv)
    if args.command == "analyze":
        try:
            result = analyze_pair(args.kick, args.bass)
        except ValueError as exc:
            # Input validation failures are user errors: report them without a traceback.
            print(f"error: {exc}", file=sys.stderr)
            return 2
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

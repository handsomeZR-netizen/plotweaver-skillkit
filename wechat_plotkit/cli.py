from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import analyze_links, build_style_index, generate_example, validate_capture


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="wechat-plotkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze-links", help="Fetch and analyze a Markdown link list.")
    analyze_parser.add_argument("--input", required=True, help="Markdown file containing WeChat article links.")
    analyze_parser.add_argument("--out", required=True, help="Output run directory.")
    analyze_parser.add_argument("--validate", action="store_true", help="Run sampled browser validation after analysis.")
    analyze_parser.add_argument("--sample-mode", default="risk_based", choices=["risk_based", "all", "manual_only"])
    analyze_parser.add_argument("--sample-limit", type=int, default=3)

    index_parser = subparsers.add_parser("build-style-index", help="Rebuild master style index from an existing run.")
    index_parser.add_argument("--run", required=True, help="Run directory.")

    validate_parser = subparsers.add_parser("validate-capture", help="Run browser screenshot validation on a batch.")
    validate_parser.add_argument("--run", required=True, help="Run directory.")
    validate_parser.add_argument("--sample-mode", default="risk_based", choices=["risk_based", "all", "manual_only"])
    validate_parser.add_argument("--sample-limit", type=int, default=3)

    example_parser = subparsers.add_parser("generate-example", help="Copy a starter example template to an output directory.")
    example_parser.add_argument("--style-source", required=True, help="Article JSON or master style index path.")
    example_parser.add_argument(
        "--template",
        required=True,
        choices=["line", "bar", "scatter", "heatmap", "distribution", "multi_panel"],
    )
    example_parser.add_argument("--output", required=True, help="Directory to receive the generated example script.")

    args = parser.parse_args()

    if args.command == "analyze-links":
        result = analyze_links(
            input_path=args.input,
            out_dir=args.out,
            validate=args.validate,
            sample_mode=args.sample_mode,
            sample_limit=args.sample_limit,
        )
    elif args.command == "build-style-index":
        result = build_style_index(args.run)
    elif args.command == "validate-capture":
        result = validate_capture(args.run, sample_mode=args.sample_mode, sample_limit=args.sample_limit)
    else:
        generated = generate_example(args.style_source, template=args.template, output=args.output)
        result = {"generated": Path(generated).resolve().as_posix()}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

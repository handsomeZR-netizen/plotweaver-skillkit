from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

REPO_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPO_ROOT
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from select_template import select_template_for_source
from wechat_plotkit.pipeline import generate_example


def generate_plot_example(
    style_source: str | Path,
    output: str | Path,
    template: str | None = None,
    registry_path: str | Path | None = None,
) -> dict:
    selection = select_template_for_source(style_source, registry_path=registry_path, requested_template=template)
    output_path = Path(output)
    generated = generate_example(style_source, template=selection["chosen_template"], output=output_path)
    style_marker = output_path / "style_source.txt"

    return {
        "ok": True,
        "style_source_path": Path(style_source).resolve().as_posix(),
        "output_dir": output_path.resolve().as_posix(),
        "chosen_template": selection["chosen_template"],
        "generated_script_path": Path(generated).resolve().as_posix(),
        "style_source_marker_path": style_marker.resolve().as_posix(),
        "template_entry": selection["template_entry"],
        "rationale": selection["rationale"],
        "warnings": selection["warnings"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a publication-style starter script from an extracted style source.")
    parser.add_argument("--style-source", required=True, help="master_style_index.json, style_profile.json, or article.json")
    parser.add_argument("--output", required=True, help="Directory to receive the generated starter script.")
    parser.add_argument("--registry", help="Optional explicit template_registry.json path")
    parser.add_argument("--template", help="Optional explicit template override")
    args = parser.parse_args()

    result = generate_plot_example(
        args.style_source,
        args.output,
        template=args.template,
        registry_path=args.registry,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

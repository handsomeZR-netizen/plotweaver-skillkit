from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from preflight_check import PACKAGE_ROOT, REPO_ROOT, run_preflight

package_path = str(PACKAGE_ROOT)
if package_path not in sys.path:
    sys.path.insert(0, package_path)

from wechat_plotkit.pipeline import analyze_links


def _manual_review_articles(manifest: dict) -> list[dict]:
    output = []
    for item in manifest.get("articles", []):
        if item.get("manual_review_required"):
            output.append(
                {
                    "slug": item.get("slug"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "recommended_template": item.get("recommended_template"),
                }
            )
    return output


def _failed_articles(manifest: dict) -> list[dict]:
    output = []
    for item in manifest.get("articles", []):
        if item.get("fetch_status") == "failed":
            output.append(
                {
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "error": item.get("error"),
                }
            )
    return output


def _validation_summary(records: list[dict]) -> dict:
    counts = {"validated": 0, "failed": 0, "skipped": 0}
    for record in records:
        status = record.get("status", "")
        if status in counts:
            counts[status] += 1
    counts["record_count"] = len(records)
    return counts


def run_analysis(
    input_path: str | Path,
    out_dir: str | Path,
    validate: bool = False,
    sample_mode: str = "risk_based",
    sample_limit: int = 3,
) -> dict:
    preflight = run_preflight(input_path, out_dir, validate=validate)
    out_dir = Path(out_dir)
    if not preflight["ok"]:
        return {
            "ok": False,
            "error": "Preflight checks failed.",
            "preflight": preflight,
            "run_dir": out_dir.resolve().as_posix(),
        }

    result = analyze_links(
        input_path=input_path,
        out_dir=out_dir,
        validate=validate,
        sample_mode=sample_mode,
        sample_limit=sample_limit,
    )
    manifest = result.get("manifest", {})
    validation_records = result.get("validation", [])
    manifest_path = out_dir / "batch_manifest.json"
    style_index_path = out_dir / "master_style_index.json"
    template_registry_path = out_dir / "template_registry.json"
    reuse_playbook_path = out_dir / "reuse_playbook.md"

    return {
        "ok": True,
        "preflight": preflight,
        "repo_root": REPO_ROOT.resolve().as_posix(),
        "package_root": PACKAGE_ROOT.resolve().as_posix(),
        "run_dir": out_dir.resolve().as_posix(),
        "manifest_path": manifest_path.resolve().as_posix(),
        "master_style_index_path": style_index_path.resolve().as_posix() if style_index_path.exists() else None,
        "template_registry_path": template_registry_path.resolve().as_posix() if template_registry_path.exists() else None,
        "reuse_playbook_path": reuse_playbook_path.resolve().as_posix() if reuse_playbook_path.exists() else None,
        "processed_count": manifest.get("processed_count", 0),
        "failed_count": manifest.get("failed_count", 0),
        "manual_review_articles": _manual_review_articles(manifest),
        "failed_articles": _failed_articles(manifest),
        "validation_requested": validate,
        "validation_summary": _validation_summary(validation_records),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the wechat-analysis skill wrapper.")
    parser.add_argument("--input", required=True, help="Markdown file containing WeChat article links.")
    parser.add_argument("--out", required=True, help="Output run directory.")
    parser.add_argument("--validate", action="store_true", help="Run browser validation after extraction.")
    parser.add_argument("--sample-mode", default="risk_based", choices=["risk_based", "all", "manual_only"])
    parser.add_argument("--sample-limit", default=3, type=int)
    args = parser.parse_args()

    result = run_analysis(
        args.input,
        args.out,
        validate=args.validate,
        sample_mode=args.sample_mode,
        sample_limit=args.sample_limit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

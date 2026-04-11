from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPO_ROOT

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from wechat_plotkit.extract import recommend_template


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_registry_path(style_source: Path) -> Path | None:
    for parent in [style_source.parent, *style_source.parents]:
        candidate = parent / "template_registry.json"
        if candidate.exists():
            return candidate
    return None


def _style_summary_from_master_index(payload: dict, style_source: Path) -> dict:
    articles = payload.get("articles", [])
    recommended = None
    if articles:
        ranked = sorted(
            articles,
            key=lambda item: (
                item.get("manual_review_required", False),
                -float(item.get("confidence", 0.0)),
            ),
        )
        recommended = ranked[0].get("recommended_template")

    plot_counter = Counter()
    layout_counter = Counter()
    for article in articles:
        plot_counter.update(article.get("plot_types", []))
        layout_counter.update([article.get("layout_pattern", "single_panel")])

    return {
        "source_type": "master_style_index",
        "style_source_path": style_source.resolve().as_posix(),
        "recommended_template": recommended or payload.get("aggregate", {}).get("dominant_template"),
        "dominant_template": payload.get("aggregate", {}).get("dominant_template"),
        "plot_types": [name for name, _ in plot_counter.most_common()],
        "palette_hex": payload.get("aggregate", {}).get("palette_hex_top", []),
        "layout_pattern": layout_counter.most_common(1)[0][0] if layout_counter else "single_panel",
        "manual_review_required": any(article.get("manual_review_required") for article in articles),
        "article_count": payload.get("article_count", len(articles)),
    }


def _style_summary_from_style_profile(payload: dict, style_source: Path) -> dict:
    return {
        "source_type": "style_profile",
        "style_source_path": style_source.resolve().as_posix(),
        "recommended_template": payload.get("recommended_template"),
        "dominant_template": payload.get("recommended_template"),
        "plot_types": payload.get("plot_types", []),
        "palette_hex": payload.get("palette_hex", []),
        "layout_pattern": payload.get("layout_pattern", "single_panel"),
        "manual_review_required": payload.get("manual_review_required", False),
        "article_count": 1,
    }


def _style_summary_from_article_json(payload: dict, style_source: Path) -> dict:
    style_profile = payload.get("style_profile", {})
    return _style_summary_from_style_profile(style_profile, style_source)


def load_style_summary(style_source: str | Path) -> dict:
    style_source = Path(style_source)
    payload = _read_json(style_source)

    if style_source.name == "master_style_index.json":
        return _style_summary_from_master_index(payload, style_source)
    if style_source.name == "style_profile.json":
        return _style_summary_from_style_profile(payload, style_source)
    if style_source.name == "article.json":
        return _style_summary_from_article_json(payload, style_source)
    if "style_profile" in payload:
        return _style_summary_from_article_json(payload, style_source)
    return _style_summary_from_style_profile(payload, style_source)


def _infer_template(style_summary: dict) -> tuple[str, str]:
    if style_summary.get("layout_pattern") == "multi_panel":
        return "multi_panel", "Used multi_panel because the layout pattern is multi_panel."

    inferred = recommend_template(style_summary.get("plot_types", []))
    return inferred, f"Inferred {inferred} from plot_types={style_summary.get('plot_types', [])}."


def select_template_for_source(
    style_source: str | Path,
    registry_path: str | Path | None = None,
    requested_template: str | None = None,
) -> dict:
    style_source = Path(style_source)
    style_summary = load_style_summary(style_source)
    resolved_registry = Path(registry_path) if registry_path else _find_registry_path(style_source)

    registry_map: dict[str, dict] = {}
    if resolved_registry and resolved_registry.exists():
        registry_map = {
            item["template"]: item
            for item in _read_json(resolved_registry).get("templates", [])
        }

    rationale: list[str] = []
    warnings: list[str] = []

    if requested_template:
        chosen_template = requested_template
        rationale.append(f"Used explicit template override '{requested_template}'.")
    else:
        recommended = style_summary.get("recommended_template")
        if recommended and (not registry_map or recommended in registry_map):
            chosen_template = recommended
            rationale.append(f"Used recommended_template '{recommended}' from the style source.")
        else:
            inferred_template, reason = _infer_template(style_summary)
            chosen_template = inferred_template
            rationale.append(reason)
            if recommended and registry_map and recommended not in registry_map:
                warnings.append(f"recommended_template '{recommended}' was not present in the registry.")

    if registry_map and chosen_template not in registry_map:
        fallback = style_summary.get("dominant_template") or "line"
        if fallback not in registry_map:
            fallback = next(iter(registry_map), "line")
        warnings.append(f"Template '{chosen_template}' was not in the registry; fell back to '{fallback}'.")
        chosen_template = fallback

    if style_summary.get("manual_review_required"):
        warnings.append("Source requires manual review; reuse style cues before trusting extracted code.")

    template_entry = registry_map.get(
        chosen_template,
        {"template": chosen_template, "path": None, "annotated_path": None, "fits": []},
    )

    return {
        "style_source_path": style_source.resolve().as_posix(),
        "registry_path": resolved_registry.resolve().as_posix() if resolved_registry and resolved_registry.exists() else None,
        "source_type": style_summary["source_type"],
        "chosen_template": chosen_template,
        "template_entry": template_entry,
        "style_summary": style_summary,
        "rationale": rationale,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Choose a starter template from an extracted style source.")
    parser.add_argument("--style-source", required=True, help="master_style_index.json, style_profile.json, or article.json")
    parser.add_argument("--registry", help="Optional explicit template_registry.json path")
    parser.add_argument("--template", help="Optional explicit template override")
    args = parser.parse_args()

    result = select_template_for_source(args.style_source, registry_path=args.registry, requested_template=args.template)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

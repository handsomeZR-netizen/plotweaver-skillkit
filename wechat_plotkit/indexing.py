from __future__ import annotations

from collections import Counter
from pathlib import Path

from .models import ArticleRecord, dataclass_to_dict
from .utils import read_json, write_json, write_text

TEMPLATE_DEFINITIONS = [
    {
        "template": "line",
        "path": "templates/line_template.py",
        "annotated_path": "templates/line_template.py",
        "fits": ["line", "trend", "time_series"],
    },
    {
        "template": "bar",
        "path": "templates/bar_template.py",
        "annotated_path": "templates/bar_template.py",
        "fits": ["bar", "grouped_comparison"],
    },
    {
        "template": "scatter",
        "path": "templates/scatter_template.py",
        "annotated_path": "templates/scatter_template.py",
        "fits": ["scatter", "correlation"],
    },
    {
        "template": "heatmap",
        "path": "templates/heatmap_template.py",
        "annotated_path": "templates/heatmap_template.py",
        "fits": ["heatmap", "matrix"],
    },
    {
        "template": "distribution",
        "path": "templates/distribution_template.py",
        "annotated_path": "templates/distribution_template.py",
        "fits": ["distribution", "histogram", "density", "violin", "boxplot"],
    },
    {
        "template": "multi_panel",
        "path": "templates/multi_panel_template.py",
        "annotated_path": "templates/multi_panel_template.py",
        "fits": ["multi_panel", "subplot"],
    },
]


def build_master_style_index(run_dir: Path, articles: list[ArticleRecord]) -> dict:
    validation_map = _load_validation_map(run_dir)
    plot_type_counts = Counter()
    library_counts = Counter()
    template_counts = Counter()
    palette_hits = Counter()

    for article in articles:
        plot_type_counts.update(article.style_profile.plot_types)
        library_counts.update(article.style_profile.libraries_detected)
        template_counts.update([article.style_profile.recommended_template])
        palette_hits.update(article.style_profile.palette_hex)

    payload = {
        "article_count": len(articles),
        "articles": [
            {
                "slug": article.slug,
                "title": article.title,
                "url": article.url,
                "plot_types": article.style_profile.plot_types,
                "libraries_detected": article.style_profile.libraries_detected,
                "palette_hex": article.style_profile.palette_hex,
                "layout_pattern": article.style_profile.layout_pattern,
                "annotation_style": article.style_profile.annotation_style,
                "confidence": article.style_profile.confidence,
                "manual_review_required": article.style_profile.manual_review_required,
                "validation_status": validation_map.get(article.slug, "not_validated"),
                "recommended_template": article.style_profile.recommended_template,
            }
            for article in articles
        ],
        "aggregate": {
            "plot_type_counts": dict(plot_type_counts),
            "library_counts": dict(library_counts),
            "template_counts": dict(template_counts),
            "palette_hex_top": [color for color, _ in palette_hits.most_common(10)],
            "dominant_template": template_counts.most_common(1)[0][0] if template_counts else "line",
            "validated_count": sum(1 for article in articles if validation_map.get(article.slug) == "validated"),
        },
    }
    write_json(run_dir / "master_style_index.json", payload)
    return payload


def write_template_registry(run_dir: Path) -> dict:
    payload = {
        "theme_entrypoint": "style_kit/theme.py",
        "templates": TEMPLATE_DEFINITIONS,
    }
    write_json(run_dir / "template_registry.json", payload)
    return payload


def write_reuse_playbook(run_dir: Path, master_index: dict) -> Path:
    dominant_template = master_index["aggregate"].get("dominant_template", "line")
    top_palette = ", ".join(master_index["aggregate"].get("palette_hex_top", [])[:5]) or "No stable palette detected"
    lines = [
        "# Reuse Playbook",
        "",
        "## How Codex Should Use This Pack",
        "",
        "1. Read `master_style_index.json` to identify dominant plot families and palette choices.",
        "2. Read `template_registry.json` to map target data in project B to the nearest template.",
        "3. Apply `style_kit/theme.py` before drawing any final figure.",
        "4. If an article is marked `manual_review_required`, prefer a confirmed template over OCR-derived code.",
        "",
        "## Current Batch Summary",
        "",
        f"- Dominant template: `{dominant_template}`",
        f"- Top palette colors: `{top_palette}`",
        "",
        "## Reuse Rules",
        "",
        "- Keep serif typography, restrained colors, light grid, and high-resolution export.",
        "- Treat extracted snippets as reference logic; convert them into reusable plotting functions in project B.",
        "- Preserve figure spacing, annotation density, and line-weight hierarchy from the closest matched article.",
        "- For unsupported chart forms, reuse theme and palette first, then adapt the nearest template.",
    ]
    output = run_dir / "reuse_playbook.md"
    write_text(output, "\n".join(lines) + "\n")
    return output


def write_article_json(article_dir: Path, article: ArticleRecord) -> None:
    write_json(article_dir / "article.json", dataclass_to_dict(article))
    write_json(article_dir / "style_profile.json", dataclass_to_dict(article.style_profile))


def _load_validation_map(run_dir: Path) -> dict[str, str]:
    manifest_path = run_dir / "validation" / "validation_manifest.json"
    if not manifest_path.exists():
        return {}
    payload = read_json(manifest_path)
    return {item["slug"]: item["status"] for item in payload.get("records", [])}

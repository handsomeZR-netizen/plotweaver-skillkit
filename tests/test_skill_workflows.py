import importlib.util
import json
from pathlib import Path

from wechat_plotkit.indexing import write_template_registry
from wechat_plotkit.pipeline import generate_example


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generate_example_uses_real_template_files(tmp_path: Path) -> None:
    expectations = {
        "line": "Publication line template",
        "bar": "Publication bar template",
        "scatter": "Publication scatter template",
        "heatmap": "Publication heatmap template",
        "distribution": "Publication distribution template",
        "multi_panel": "Publication multi-panel template",
    }

    for template, marker in expectations.items():
        output_dir = tmp_path / template
        generated_path = generate_example(tmp_path / "style_source.json", template=template, output=output_dir)
        generated_text = generated_path.read_text(encoding="utf-8")
        assert marker in generated_text
        style_marker = (output_dir / "style_source.txt").read_text(encoding="utf-8")
        assert f"template={template}" in style_marker
        assert f"template_source={(PROJECT_ROOT / 'templates' / f'{template}_template.py').resolve().as_posix()}" in style_marker


def test_template_registry_points_to_concrete_templates(tmp_path: Path) -> None:
    payload = write_template_registry(tmp_path)

    assert payload["theme_entrypoint"] == "style_kit/theme.py"
    template_names = {item["template"] for item in payload["templates"]}
    assert template_names == {"line", "bar", "scatter", "heatmap", "distribution", "multi_panel"}

    for item in payload["templates"]:
        assert (PROJECT_ROOT / item["path"]).exists()
        assert (PROJECT_ROOT / item["annotated_path"]).exists()


def test_analysis_preflight_reports_missing_input(tmp_path: Path) -> None:
    module = _load_module(
        "wechat_analysis_preflight",
        REPO_ROOT / ".agents" / "skills" / "wechat-analysis" / "scripts" / "preflight_check.py",
    )

    result = module.run_preflight(tmp_path / "missing.md", tmp_path / "out", validate=False)

    assert result["ok"] is False
    assert result["status"] == "failed"
    input_check = next(item for item in result["checks"] if item["name"] == "input_file")
    assert input_check["ok"] is False


def test_analysis_preflight_fails_when_validation_browser_is_unavailable(tmp_path: Path, monkeypatch) -> None:
    module = _load_module(
        "wechat_analysis_preflight_browser",
        REPO_ROOT / ".agents" / "skills" / "wechat-analysis" / "scripts" / "preflight_check.py",
    )
    input_path = tmp_path / "links.md"
    input_path.write_text("https://mp.weixin.qq.com/s/example\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "_check_chromium_available",
        lambda: {"name": "playwright_chromium", "ok": False, "detail": "Chromium missing"},
    )

    result = module.run_preflight(input_path, tmp_path / "out", validate=True)

    assert result["ok"] is False
    chromium_check = next(item for item in result["checks"] if item["name"] == "playwright_chromium")
    assert chromium_check["detail"] == "Chromium missing"


def test_run_analysis_returns_wrapper_summary(tmp_path: Path, monkeypatch) -> None:
    module = _load_module(
        "wechat_analysis_runner",
        REPO_ROOT / ".agents" / "skills" / "wechat-analysis" / "scripts" / "run_analysis.py",
    )

    def fake_analyze_links(input_path, out_dir, validate, sample_mode, sample_limit):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "processed_count": 2,
            "failed_count": 1,
            "articles": [
                {
                    "slug": "article-a",
                    "title": "Article A",
                    "url": "https://example.com/a",
                    "fetch_status": "success",
                    "manual_review_required": True,
                    "recommended_template": "scatter",
                },
                {
                    "slug": "article-b",
                    "title": "Article B",
                    "url": "https://example.com/b",
                    "fetch_status": "failed",
                    "error": "timeout",
                },
            ],
            "validation": [{"slug": "article-a", "status": "validated"}],
        }
        (out_dir / "batch_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (out_dir / "master_style_index.json").write_text(json.dumps({"aggregate": {"dominant_template": "scatter"}}), encoding="utf-8")
        (out_dir / "template_registry.json").write_text(json.dumps({"templates": []}), encoding="utf-8")
        (out_dir / "reuse_playbook.md").write_text("# Playbook\n", encoding="utf-8")
        return {"manifest": manifest, "master_style_index": {"aggregate": {"dominant_template": "scatter"}}, "validation": manifest["validation"]}

    monkeypatch.setattr(module, "run_preflight", lambda *args, **kwargs: {"ok": True, "status": "ready", "checks": []})
    monkeypatch.setattr(module, "analyze_links", fake_analyze_links)

    result = module.run_analysis(tmp_path / "links.md", tmp_path / "run", validate=True)

    assert result["ok"] is True
    assert result["processed_count"] == 2
    assert result["failed_count"] == 1
    assert len(result["manual_review_articles"]) == 1
    assert len(result["failed_articles"]) == 1
    assert result["validation_summary"]["validated"] == 1
    assert result["master_style_index_path"].endswith("master_style_index.json")


def test_plot_style_reuse_prefers_recommended_template(tmp_path: Path) -> None:
    module = _load_module(
        "plot_style_selector",
        REPO_ROOT / ".agents" / "skills" / "plot-style-reuse" / "scripts" / "select_template.py",
    )
    style_source = tmp_path / "master_style_index.json"
    style_source.write_text(
        json.dumps(
            {
                "article_count": 1,
                "articles": [
                    {
                        "slug": "article-a",
                        "title": "Article A",
                        "recommended_template": "heatmap",
                        "plot_types": ["heatmap"],
                        "palette_hex": ["#123456"],
                        "layout_pattern": "single_panel",
                        "manual_review_required": False,
                        "confidence": 0.9,
                    }
                ],
                "aggregate": {
                    "dominant_template": "line",
                    "plot_type_counts": {"heatmap": 1},
                    "palette_hex_top": ["#123456"],
                },
            }
        ),
        encoding="utf-8",
    )
    registry_path = tmp_path / "template_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "templates": [
                    {"template": "line", "path": "templates/line_template.py", "annotated_path": "templates/line_template.py", "fits": ["line"]},
                    {"template": "heatmap", "path": "templates/heatmap_template.py", "annotated_path": "templates/heatmap_template.py", "fits": ["heatmap"]},
                ]
            }
        ),
        encoding="utf-8",
    )

    selection = module.select_template_for_source(style_source, registry_path=registry_path)

    assert selection["chosen_template"] == "heatmap"
    assert any("recommended_template" in reason for reason in selection["rationale"])

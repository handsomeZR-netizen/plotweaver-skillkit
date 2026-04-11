from __future__ import annotations

import shutil
from pathlib import Path

from .extract import build_style_profile, extract_code_snippets, maybe_run_ocr_for_code, write_manual_review_note
from .fetch import (
    build_session,
    build_slug_from_title,
    extract_images_from_body,
    fetch_article_html,
    parse_article_content,
    write_body_text,
)
from .indexing import build_master_style_index, write_article_json, write_reuse_playbook, write_template_registry
from .input_loader import load_links_from_markdown
from .models import ArticleRecord, BatchManifest, dataclass_to_dict
from .utils import compact_text, ensure_dir, stable_hash, write_json
from .validate import load_articles_from_run, validate_articles


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_SOURCES = {
    "line": PROJECT_ROOT / "templates" / "line_template.py",
    "bar": PROJECT_ROOT / "templates" / "bar_template.py",
    "scatter": PROJECT_ROOT / "templates" / "scatter_template.py",
    "heatmap": PROJECT_ROOT / "templates" / "heatmap_template.py",
    "distribution": PROJECT_ROOT / "templates" / "distribution_template.py",
    "multi_panel": PROJECT_ROOT / "templates" / "multi_panel_template.py",
}


def analyze_links(
    input_path: str | Path,
    out_dir: str | Path,
    validate: bool = False,
    sample_mode: str = "risk_based",
    sample_limit: int = 3,
) -> dict:
    input_path = Path(input_path)
    out_dir = ensure_dir(Path(out_dir))
    links = load_links_from_markdown(input_path)
    session = build_session()

    manifest = BatchManifest(
        input_path=input_path.resolve().as_posix(),
        output_path=out_dir.resolve().as_posix(),
        link_count=len(links),
    )
    articles: list[ArticleRecord] = []

    ensure_dir(out_dir / "articles")
    for url in links:
        try:
            provisional_slug = f"article-{stable_hash(url, 8)}"
            article_dir = ensure_dir(out_dir / "articles" / provisional_slug)
            html_text, html_path = fetch_article_html(session, url, article_dir)
            title, body_html, body_text, author = parse_article_content(html_text)
            final_slug = _resolve_unique_slug(out_dir / "articles", build_slug_from_title(title, url), provisional_slug)
            if final_slug != provisional_slug:
                target_dir = out_dir / "articles" / final_slug
                article_dir.rename(target_dir)
                article_dir = target_dir
                html_path = article_dir / "raw" / "article.html"
            text_path, body_html_path = write_body_text(article_dir, body_text, body_html)
            images = extract_images_from_body(body_html, session, article_dir)
            image_paths = [Path(asset.local_path) for asset in images if asset.local_path]
            code_snippets = extract_code_snippets(body_html, body_text, article_dir)
            ocr_snippets = maybe_run_ocr_for_code(image_paths, article_dir, code_snippets)
            all_snippets = code_snippets + ocr_snippets
            style_profile = build_style_profile(body_text, all_snippets, image_paths)

            if style_profile.manual_review_required:
                write_manual_review_note(
                    article_dir,
                    reason="No high-confidence text code was detected from the article DOM.",
                    ocr_snippets=ocr_snippets,
                )

            record = ArticleRecord(
                slug=final_slug,
                url=url,
                title=title,
                fetch_status="success",
                body_text_excerpt=compact_text(body_text),
                html_path=html_path.as_posix(),
                text_path=text_path.as_posix(),
                body_html_path=body_html_path.as_posix(),
                author=author,
                images=images,
                code_snippets=all_snippets,
                style_profile=style_profile,
            )
            write_article_json(article_dir, record)
            articles.append(record)
            manifest.processed_count += 1
            manifest.articles.append(
                {
                    "slug": record.slug,
                    "title": record.title,
                    "url": record.url,
                    "fetch_status": record.fetch_status,
                    "manual_review_required": record.style_profile.manual_review_required,
                    "recommended_template": record.style_profile.recommended_template,
                }
            )
        except Exception as exc:
            manifest.failed_count += 1
            manifest.articles.append({"url": url, "fetch_status": "failed", "error": str(exc)})

    master_index = build_master_style_index(out_dir, articles)
    write_template_registry(out_dir)
    write_reuse_playbook(out_dir, master_index)

    validation_records = []
    if validate:
        validation_records = validate_articles(out_dir, articles, sample_mode=sample_mode, sample_limit=sample_limit)
        manifest.validated_count = len(validation_records)
        manifest.validation = [dataclass_to_dict(item) for item in validation_records]
        master_index = build_master_style_index(out_dir, articles)
        write_reuse_playbook(out_dir, master_index)

    write_json(out_dir / "batch_manifest.json", manifest.to_dict())
    return {
        "manifest": manifest.to_dict(),
        "master_style_index": master_index,
        "validation": [dataclass_to_dict(item) for item in validation_records],
    }


def build_style_index(run_dir: str | Path) -> dict:
    run_dir = Path(run_dir)
    articles = load_articles_from_run(run_dir)
    master_index = build_master_style_index(run_dir, articles)
    write_template_registry(run_dir)
    write_reuse_playbook(run_dir, master_index)
    return master_index


def validate_capture(run_dir: str | Path, sample_mode: str = "risk_based", sample_limit: int = 3) -> dict:
    run_dir = Path(run_dir)
    articles = load_articles_from_run(run_dir)
    records = validate_articles(run_dir, articles, sample_mode=sample_mode, sample_limit=sample_limit)
    return {"records": [dataclass_to_dict(item) for item in records]}


def generate_example(style_source: str | Path, template: str, output: str | Path) -> Path:
    output = ensure_dir(Path(output))
    try:
        template_source = TEMPLATE_SOURCES[template]
    except KeyError as exc:
        available = ", ".join(sorted(TEMPLATE_SOURCES))
        raise ValueError(f"Unsupported template '{template}'. Available templates: {available}") from exc
    if not template_source.exists():
        raise FileNotFoundError(f"Template file not found: {template_source}")
    destination = output / f"{template}_example.py"
    shutil.copy2(template_source, destination)
    (output / "style_source.txt").write_text(
        (
            f"style_source={Path(style_source).resolve().as_posix()}\n"
            f"template={template}\n"
            f"template_source={template_source.resolve().as_posix()}\n"
        ),
        encoding="utf-8",
    )
    return destination


def _resolve_unique_slug(article_root: Path, candidate: str, provisional_slug: str) -> str:
    if candidate == provisional_slug:
        return candidate
    if not (article_root / candidate).exists():
        return candidate
    suffix = 2
    while (article_root / f"{candidate}-{suffix}").exists():
        suffix += 1
    return f"{candidate}-{suffix}"

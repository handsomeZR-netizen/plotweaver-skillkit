from __future__ import annotations

from pathlib import Path

from .models import ArticleAsset, ArticleRecord, CodeSnippet, StyleProfile, ValidationRecord, dataclass_to_dict
from .utils import ensure_dir, read_json, write_json, write_text


def select_validation_targets(articles: list[ArticleRecord], sample_mode: str, sample_limit: int) -> list[ArticleRecord]:
    if sample_mode == "all":
        return articles
    if sample_mode == "manual_only":
        selected = [article for article in articles if article.style_profile.manual_review_required]
        return selected[:sample_limit]

    ranked = sorted(
        articles,
        key=lambda article: (
            not article.style_profile.manual_review_required,
            len(article.code_snippets) > 0,
            -len(article.images),
            article.style_profile.confidence,
        ),
    )
    return ranked[:sample_limit]


def validate_articles(run_dir: Path, articles: list[ArticleRecord], sample_mode: str, sample_limit: int) -> list[ValidationRecord]:
    selected = select_validation_targets(articles, sample_mode=sample_mode, sample_limit=sample_limit)
    records = [validate_single_article(run_dir, article, sampled_reason=sample_mode) for article in selected]
    write_json(run_dir / "validation" / "validation_manifest.json", {"records": [dataclass_to_dict(record) for record in records]})
    return records


def validate_single_article(run_dir: Path, article: ArticleRecord, sampled_reason: str) -> ValidationRecord:
    validation_dir = ensure_dir(run_dir / "validation" / article.slug)
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        record = ValidationRecord(
            slug=article.slug,
            url=article.url,
            status="skipped",
            sampled_reason=sampled_reason,
            extracted_image_count=len(article.images),
            extracted_code_count=len(article.code_snippets),
            notes=["Playwright is not installed; browser validation skipped."],
        )
        _write_validation_report(validation_dir, record)
        return record

    dom_image_count = 0
    dom_code_candidates = 0
    screenshot_paths: list[str] = []
    missing_items: list[str] = []
    notes: list[str] = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 540, "height": 1280},
                device_scale_factor=2,
                is_mobile=True,
                has_touch=True,
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
                ),
            )
            page = context.new_page()
            page.goto(article.url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(2500)
            page.locator("#js_content").wait_for(timeout=15000)
            page.evaluate(
                """
                () => {
                  const node = document.querySelector('#js_content');
                  if (node) {
                    node.style.visibility = 'visible';
                    node.style.opacity = '1';
                  }
                  window.scrollTo(0, 0);
                }
                """
            )
            dom_image_count = page.evaluate(
                """
                () => {
                  const urls = [...document.querySelectorAll('#js_content img')]
                    .map((img) => img.getAttribute('data-src') || img.getAttribute('src') || '')
                    .map((value) => value.trim())
                    .filter((value) => value && !value.startsWith('data:image'));
                  return [...new Set(urls)].length;
                }
                """
            )
            dom_code_candidates = page.evaluate(
                """
                () => {
                  const blocks = [...document.querySelectorAll('#js_content pre, #js_content code')]
                    .map((node) => (node.innerText || '').replace(/\\s+/g, ' ').trim())
                    .filter((text) => text.length >= 40)
                    .filter((text) => text.length >= 80 || text.split(';').length >= 3)
                    .filter((text) => /(import\\s+|plt\\.|sns\\.|ax\\.|np\\.|pd\\.|def\\s+|for\\s+.+:|if\\s+.+:)/i.test(text));
                  return [...new Set(blocks)].length;
                }
                """
            )
            full_path = validation_dir / "page_full.png"
            try:
                page.screenshot(path=str(full_path), full_page=True)
                screenshot_paths.append(full_path.as_posix())
            except Exception:
                screenshot_paths.extend(_capture_tiled_screenshots(page, validation_dir))
            browser.close()
    except Exception as exc:
        notes.append(f"Browser validation failed: {exc}")

    if dom_image_count > len(article.images):
        missing_items.append(f"DOM shows {dom_image_count} images but extracted {len(article.images)}.")
    if dom_code_candidates > len(article.code_snippets):
        missing_items.append(
            f"DOM exposes {dom_code_candidates} pre/code nodes but extracted {len(article.code_snippets)} snippets."
        )
    if article.style_profile.manual_review_required:
        missing_items.append("Article requires manual review because no high-confidence text code was found.")

    status = "validated" if screenshot_paths else "failed"
    if status == "validated" and not missing_items:
        notes.append("No obvious mismatch detected in this sampled browser validation.")

    record = ValidationRecord(
        slug=article.slug,
        url=article.url,
        status=status,
        sampled_reason=sampled_reason,
        screenshot_paths=screenshot_paths,
        dom_image_count=dom_image_count,
        extracted_image_count=len(article.images),
        dom_code_candidates=dom_code_candidates,
        extracted_code_count=len(article.code_snippets),
        missing_items=missing_items,
        notes=notes,
    )
    _write_validation_report(validation_dir, record)
    return record


def load_articles_from_run(run_dir: Path) -> list[ArticleRecord]:
    articles: list[ArticleRecord] = []
    for article_json in sorted((run_dir / "articles").glob("*/article.json")):
        payload = read_json(article_json)
        article = ArticleRecord(
            slug=payload["slug"],
            url=payload["url"],
            title=payload["title"],
            fetch_status=payload["fetch_status"],
            body_text_excerpt=payload.get("body_text_excerpt", ""),
            html_path=payload.get("html_path"),
            text_path=payload.get("text_path"),
            body_html_path=payload.get("body_html_path"),
            author=payload.get("author"),
        )
        article.images = [ArticleAsset(**item) for item in payload.get("images", [])]
        article.code_snippets = [CodeSnippet(**item) for item in payload.get("code_snippets", [])]
        article.style_profile = StyleProfile(**payload.get("style_profile", {}))
        article.errors = payload.get("errors", [])
        articles.append(article)
    return articles


def _capture_tiled_screenshots(page, validation_dir: Path) -> list[str]:
    paths: list[str] = []
    height = page.evaluate("() => document.body.scrollHeight")
    viewport_height = page.viewport_size["height"]
    tile = 1
    for top in range(0, height, viewport_height):
        page.evaluate("(y) => window.scrollTo(0, y)", top)
        page.wait_for_timeout(400)
        path = validation_dir / f"page_{tile:03d}.png"
        page.screenshot(path=str(path))
        paths.append(path.as_posix())
        tile += 1
    return paths


def _write_validation_report(validation_dir: Path, record: ValidationRecord) -> None:
    write_json(validation_dir / "validation.json", dataclass_to_dict(record))
    lines = [
        "# Validation Report",
        "",
        f"- Status: `{record.status}`",
        f"- Sample reason: `{record.sampled_reason}`",
        f"- DOM images: `{record.dom_image_count}`",
        f"- Extracted images: `{record.extracted_image_count}`",
        f"- DOM code candidates: `{record.dom_code_candidates}`",
        f"- Extracted code snippets: `{record.extracted_code_count}`",
        "",
        "## Missing Or Risk Items",
    ]
    if record.missing_items:
        lines.extend(f"- {item}" for item in record.missing_items)
    else:
        lines.append("- No obvious gap detected in this sampled validation.")
    lines.extend(["", "## Notes"])
    if record.notes:
        lines.extend(f"- {note}" for note in record.notes)
    else:
        lines.append("- None.")
    lines.extend(["", "## Screenshots"])
    if record.screenshot_paths:
        lines.extend(f"- {path}" for path in record.screenshot_paths)
    else:
        lines.append("- No screenshot generated.")
    write_text(validation_dir / "missing_report.md", "\n".join(lines) + "\n")

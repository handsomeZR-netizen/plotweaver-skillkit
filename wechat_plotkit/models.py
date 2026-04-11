from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ArticleAsset:
    name: str
    url: str
    kind: str
    local_path: str | None = None
    width: int | None = None
    height: int | None = None
    sha1: str | None = None


@dataclass
class CodeSnippet:
    snippet_id: str
    source: str
    text: str
    language: str = "python"
    confidence: float = 0.0
    local_path: str | None = None


@dataclass
class StyleProfile:
    plot_types: list[str] = field(default_factory=list)
    libraries_detected: list[str] = field(default_factory=list)
    palette_hex: list[str] = field(default_factory=list)
    layout_pattern: str = "single_panel"
    annotation_style: str = "light"
    typography: str = "serif"
    confidence: float = 0.0
    recommended_template: str = "line"
    manual_review_required: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class ArticleRecord:
    slug: str
    url: str
    title: str
    fetch_status: str
    body_text_excerpt: str = ""
    html_path: str | None = None
    text_path: str | None = None
    body_html_path: str | None = None
    author: str | None = None
    images: list[ArticleAsset] = field(default_factory=list)
    code_snippets: list[CodeSnippet] = field(default_factory=list)
    style_profile: StyleProfile = field(default_factory=StyleProfile)
    errors: list[str] = field(default_factory=list)


@dataclass
class ValidationRecord:
    slug: str
    url: str
    status: str
    sampled_reason: str
    screenshot_paths: list[str] = field(default_factory=list)
    dom_image_count: int = 0
    extracted_image_count: int = 0
    dom_code_candidates: int = 0
    extracted_code_count: int = 0
    missing_items: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class BatchManifest:
    input_path: str
    output_path: str
    link_count: int
    processed_count: int = 0
    failed_count: int = 0
    validated_count: int = 0
    articles: list[dict[str, Any]] = field(default_factory=list)
    validation: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def dataclass_to_dict(obj: Any) -> dict[str, Any]:
    return asdict(obj)


def relativize_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()

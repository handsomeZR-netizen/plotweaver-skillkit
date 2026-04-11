from __future__ import annotations

from pathlib import Path

from .utils import extract_urls


def load_links_from_markdown(path: str | Path) -> list[str]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    return extract_urls(text)

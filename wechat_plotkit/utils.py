from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Iterable


URL_RE = re.compile(r"https?://[^\s\])>]+")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(value: str, fallback: str = "article") -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"https?://", "", lowered)
    lowered = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered[:80] or fallback


def stable_hash(value: str, length: int = 10) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def write_json(path: Path, payload: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def extract_urls(text: str) -> list[str]:
    seen: set[str] = set()
    links: list[str] = []
    for match in URL_RE.findall(text):
        cleaned = normalize_url(match)
        if cleaned not in seen:
            seen.add(cleaned)
            links.append(cleaned)
    return links


def normalize_url(url: str) -> str:
    cleaned = html.unescape(url.strip().strip('"').strip("'"))
    cleaned = cleaned.replace("\\x26amp;", "&")
    cleaned = cleaned.replace("&amp;", "&")
    cleaned = cleaned.split("\\x3c")[0]
    cleaned = cleaned.split("\\")[0]
    cleaned = cleaned.rstrip('",>')
    return cleaned


def sha1_file(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_text(text: str, limit: int = 320) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized[:limit]


def chunked(iterable: Iterable[str], size: int) -> list[list[str]]:
    bucket: list[str] = []
    output: list[list[str]] = []
    for item in iterable:
        bucket.append(item)
        if len(bucket) == size:
            output.append(bucket)
            bucket = []
    if bucket:
        output.append(bucket)
    return output

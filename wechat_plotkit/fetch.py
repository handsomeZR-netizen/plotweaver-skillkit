from __future__ import annotations

from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .models import ArticleAsset
from .utils import ensure_dir, normalize_url, sha1_file, slugify, stable_hash, write_text


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://mp.weixin.qq.com/",
        }
    )
    return session


def fetch_article_html(session: requests.Session, url: str, article_dir: Path) -> tuple[str, Path]:
    response = session.get(url, timeout=40)
    response.raise_for_status()
    html_text = response.text
    html_path = ensure_dir(article_dir / "raw") / "article.html"
    write_text(html_path, html_text)
    return html_text, html_path


def parse_article_content(html_text: str) -> tuple[str, str, str, str | None]:
    soup = BeautifulSoup(html_text, "html.parser")
    title = (
        _meta_content(soup, "og:title")
        or _meta_content(soup, "twitter:title")
        or _extract_with_regex(html_text, r'var\s+msg_title\s*=\s*"([^"]+)"')
        or _get_text(soup.select_one("#activity-name"))
        or _get_text(soup.title)
        or "untitled"
    )
    author = (
        _get_text(soup.select_one("#js_name"))
        or _extract_with_regex(html_text, r'var\s+nickname\s*=\s*"([^"]+)"')
    )
    content_node = soup.select_one("#js_content")
    body_html = str(content_node) if content_node else ""
    body_text = content_node.get_text("\n", strip=True) if content_node else soup.get_text("\n", strip=True)
    return title.strip(), body_html, body_text, author


def extract_images_from_body(body_html: str, session: requests.Session, article_dir: Path) -> list[ArticleAsset]:
    soup = BeautifulSoup(body_html, "html.parser")
    image_dir = ensure_dir(article_dir / "assets" / "images")
    images: list[ArticleAsset] = []
    seen: set[str] = set()
    for index, tag in enumerate(soup.select("img"), start=1):
        raw_url = tag.get("data-src") or tag.get("src") or tag.get("data-croporisrc")
        if not raw_url:
            continue
        url = normalize_url(raw_url)
        if not url.startswith("http") or url in seen:
            continue
        seen.add(url)
        suffix = _guess_suffix(url)
        filename = f"image_{index:03d}{suffix}"
        local_path = image_dir / filename
        width, height = _download_image(session, url, local_path)
        images.append(
            ArticleAsset(
                name=filename,
                url=url,
                kind="image",
                local_path=local_path.as_posix(),
                width=width,
                height=height,
                sha1=sha1_file(local_path),
            )
        )
    return images


def write_body_text(article_dir: Path, body_text: str, body_html: str) -> tuple[Path, Path]:
    text_path = ensure_dir(article_dir / "raw") / "article.txt"
    html_path = ensure_dir(article_dir / "raw") / "body.html"
    write_text(text_path, body_text)
    write_text(html_path, body_html)
    return text_path, html_path


def build_slug_from_title(title: str, url: str) -> str:
    cleaned = slugify(title, fallback="article")
    return f"{cleaned[:48] or 'article'}-{stable_hash(url, 8)}"


def _download_image(session: requests.Session, url: str, path: Path) -> tuple[int | None, int | None]:
    response = session.get(url, timeout=40)
    response.raise_for_status()
    path.write_bytes(response.content)
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.width, image.height
    except Exception:
        return None, None


def _guess_suffix(url: str) -> str:
    lower = url.lower()
    if "wx_fmt=png" in lower or lower.endswith(".png"):
        return ".png"
    if "wx_fmt=gif" in lower or lower.endswith(".gif"):
        return ".gif"
    return ".jpg"


def _meta_content(soup: BeautifulSoup, property_name: str) -> str | None:
    node = soup.find("meta", attrs={"property": property_name}) or soup.find(
        "meta", attrs={"name": property_name}
    )
    return node.get("content") if node else None


def _extract_with_regex(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1) if match else None


def _get_text(node) -> str | None:
    return node.get_text(strip=True) if node else None

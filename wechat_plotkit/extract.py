from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

from .models import CodeSnippet, StyleProfile
from .ocr import run_optional_ocr
from .utils import ensure_dir, write_text


LIBRARY_PATTERNS = {
    "matplotlib": r"\bmatplotlib\b|\bplt\.",
    "seaborn": r"\bseaborn\b|\bsns\.",
    "pandas": r"\bpandas\b|\bpd\.",
    "numpy": r"\bnumpy\b|\bnp\.",
    "plotly": r"\bplotly\b|\bpx\.",
    "scipy": r"\bscipy\b",
    "sklearn": r"\bsklearn\b",
}

PLOT_KEYWORDS = {
    "line": [r"lineplot", r"折线", r"trend", r"\bplot\("],
    "bar": [r"barplot", r"柱状", r"\bbar\("],
    "scatter": [r"scatter", r"散点", r"\bscatter\("],
    "heatmap": [r"heatmap", r"热图", r"imshow"],
    "distribution": [r"hist", r"kde", r"violin", r"boxplot", r"distribution", r"密度"],
    "multi_panel": [r"subplot", r"gridspec", r"subplots", r"panel"],
}

ANNOTATION_KEYWORDS = {
    "heavy": [r"annotate", r"text\(", r"arrow", r"label"],
    "light": [r"legend", r"title", r"xlabel", r"ylabel"],
}


def extract_code_snippets(body_html: str, body_text: str, article_dir: Path) -> list[CodeSnippet]:
    snippets: list[CodeSnippet] = []
    snippet_dir = ensure_dir(article_dir / "assets" / "code")
    soup = BeautifulSoup(body_html, "html.parser")
    seen: set[str] = set()

    for node in soup.select("pre, code"):
        text = node.get_text("\n", strip=True)
        if len(text) < 20 or text in seen:
            continue
        if not _looks_like_python(text):
            continue
        snippets.append(_build_snippet(text, "html_code_block", snippet_dir, len(snippets) + 1))
        seen.add(text)

    for block in _extract_code_blocks_from_text(body_text):
        if block in seen:
            continue
        snippets.append(_build_snippet(block, "text_heuristic", snippet_dir, len(snippets) + 1))
        seen.add(block)

    return snippets


def maybe_run_ocr_for_code(
    image_paths: list[Path], article_dir: Path, existing_snippets: list[CodeSnippet]
) -> list[CodeSnippet]:
    if existing_snippets:
        return []

    ocr_dir = ensure_dir(article_dir / "assets" / "ocr")
    ocr_snippets: list[CodeSnippet] = []
    for index, image_path in enumerate(image_paths[:5], start=1):
        text, engine = run_optional_ocr(image_path)
        if not text or not _looks_like_python(text):
            continue
        snippet = _build_snippet(text, f"ocr:{engine or 'unknown'}", ocr_dir, index, confidence=0.35)
        ocr_snippets.append(snippet)
    return ocr_snippets


def build_style_profile(body_text: str, code_snippets: list[CodeSnippet], image_paths: list[Path]) -> StyleProfile:
    combined_text = "\n".join([body_text, *(snippet.text for snippet in code_snippets)])
    libraries = detect_libraries(combined_text)
    plot_types = infer_plot_types(combined_text)
    palette = extract_palette_from_images(image_paths)
    annotation_style = infer_annotation_style(combined_text)
    layout_pattern = infer_layout_pattern(combined_text, len(image_paths))
    recommended = recommend_template(plot_types)
    notes: list[str] = []
    manual_review_required = False

    if not code_snippets:
        notes.append("No high-confidence text code extracted; rely on OCR/manual review.")
        manual_review_required = True
    if not palette:
        notes.append("Palette extraction low confidence; images may be photos or screenshots.")
    if len(image_paths) >= 4:
        notes.append("Article contains multiple images; preserve ordering during reuse.")

    confidence = 0.45
    if code_snippets:
        confidence += 0.25
    if palette:
        confidence += 0.2
    if libraries:
        confidence += 0.1

    return StyleProfile(
        plot_types=plot_types or ["line"],
        libraries_detected=libraries,
        palette_hex=palette,
        layout_pattern=layout_pattern,
        annotation_style=annotation_style,
        typography="serif",
        confidence=min(confidence, 0.95),
        recommended_template=recommended,
        manual_review_required=manual_review_required,
        notes=notes,
    )


def detect_libraries(text: str) -> list[str]:
    return [name for name, pattern in LIBRARY_PATTERNS.items() if re.search(pattern, text, flags=re.I)]


def infer_plot_types(text: str) -> list[str]:
    return [name for name, patterns in PLOT_KEYWORDS.items() if any(re.search(p, text, flags=re.I) for p in patterns)]


def infer_annotation_style(text: str) -> str:
    for style, patterns in ANNOTATION_KEYWORDS.items():
        if any(re.search(p, text, flags=re.I) for p in patterns):
            return style
    return "light"


def infer_layout_pattern(text: str, image_count: int) -> str:
    if re.search(r"subplot|subplots|gridspec|panel|facet", text, flags=re.I) or image_count >= 3:
        return "multi_panel"
    return "single_panel"


def recommend_template(plot_types: list[str]) -> str:
    priority = ["multi_panel", "scatter", "heatmap", "distribution", "bar", "line"]
    for name in priority:
        if name in plot_types:
            return name
    return "line"


def extract_palette_from_images(image_paths: list[Path], max_colors: int = 6) -> list[str]:
    try:
        from PIL import Image
    except Exception:
        return []

    palette_counter: Counter[str] = Counter()
    for image_path in image_paths[:4]:
        try:
            with Image.open(image_path) as image:
                rgb = image.convert("RGB")
                rgb.thumbnail((320, 320))
                quantized = rgb.quantize(colors=10)
                colors = quantized.getcolors() or []
                for count, color_index in colors:
                    palette = quantized.getpalette()
                    base = color_index * 3
                    color = tuple(palette[base : base + 3])
                    if _is_background_like(color):
                        continue
                    palette_counter[_rgb_to_hex(color)] += count
        except Exception:
            continue

    return [color for color, _ in palette_counter.most_common(max_colors)]


def write_manual_review_note(article_dir: Path, reason: str, ocr_snippets: list[CodeSnippet]) -> Path:
    lines = [
        "# Manual Review Required",
        "",
        reason,
        "",
        "## OCR Hints",
    ]
    if not ocr_snippets:
        lines.append("- No OCR code candidate detected.")
    else:
        for snippet in ocr_snippets:
            lines.append(f"- {snippet.snippet_id} from {snippet.source}, confidence={snippet.confidence:.2f}")
            lines.append("")
            lines.append("```python")
            lines.append(snippet.text)
            lines.append("```")
    note_path = article_dir / "manual_review.md"
    write_text(note_path, "\n".join(lines) + "\n")
    return note_path


def _extract_code_blocks_from_text(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        if _looks_like_python(line):
            current.append(line)
            continue
        if current and (not line.strip() or line.startswith("    ")):
            current.append(line)
            continue
        if current:
            if sum(1 for candidate in current if _looks_like_python(candidate)) >= 2:
                blocks.append(current)
            current = []
    if current and sum(1 for candidate in current if _looks_like_python(candidate)) >= 2:
        blocks.append(current)
    cleaned = ["\n".join(block).strip() for block in blocks]
    return [block for block in cleaned if len(block) >= 24]


def _looks_like_python(text: str) -> bool:
    if not text or len(text.strip()) < 6:
        return False
    tokens = [
        r"\bimport\b",
        r"\bfrom\b.+\bimport\b",
        r"\bdef\b",
        r"\bfor\b.+:",
        r"\bif\b.+:",
        r"plt\.",
        r"sns\.",
        r"ax\.",
        r"fig\s*=",
        r"pd\.",
        r"np\.",
    ]
    return any(re.search(pattern, text, flags=re.I) for pattern in tokens)


def _build_snippet(
    text: str,
    source: str,
    target_dir: Path,
    index: int,
    confidence: float = 0.7,
) -> CodeSnippet:
    snippet_id = f"snippet_{index:03d}"
    path = target_dir / f"{snippet_id}.py"
    write_text(path, text.strip() + "\n")
    return CodeSnippet(
        snippet_id=snippet_id,
        source=source,
        text=text.strip(),
        confidence=confidence,
        local_path=path.as_posix(),
    )


def _is_background_like(color: tuple[int, int, int]) -> bool:
    return max(color) <= 20 or min(color) >= 245 or (max(color) - min(color) < 10 and max(color) > 220)


def _rgb_to_hex(color: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*color)

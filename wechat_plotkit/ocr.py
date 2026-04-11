from __future__ import annotations

from pathlib import Path


def run_optional_ocr(image_path: Path) -> tuple[str | None, str | None]:
    try:
        import pytesseract
        from PIL import Image

        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image)
        return text.strip() or None, "pytesseract"
    except Exception:
        return None, None

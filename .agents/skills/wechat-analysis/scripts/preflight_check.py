from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPO_ROOT
ARTIFACT_ROOT = PACKAGE_ROOT


def _prepare_import_path() -> None:
    package_path = str(PACKAGE_ROOT)
    if package_path not in sys.path:
        sys.path.insert(0, package_path)


def _check_input_file(input_path: Path) -> dict:
    if input_path.exists() and input_path.is_file():
        return {"name": "input_file", "ok": True, "detail": input_path.resolve().as_posix()}
    return {"name": "input_file", "ok": False, "detail": f"Input file not found: {input_path}"}


def _check_wechat_plotkit_import() -> dict:
    _prepare_import_path()
    try:
        importlib.import_module("wechat_plotkit")
    except Exception as exc:
        return {"name": "wechat_plotkit_import", "ok": False, "detail": str(exc)}
    return {"name": "wechat_plotkit_import", "ok": True, "detail": str(PACKAGE_ROOT)}


def _check_output_dir(output_dir: Path) -> dict:
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".codex_preflight_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except Exception as exc:
        return {"name": "output_dir", "ok": False, "detail": str(exc)}
    return {"name": "output_dir", "ok": True, "detail": output_dir.resolve().as_posix()}


def _check_chromium_available() -> dict:
    _prepare_import_path()
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {"name": "playwright_chromium", "ok": False, "detail": f"Playwright import failed: {exc}"}

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            browser.close()
    except Exception as exc:
        return {"name": "playwright_chromium", "ok": False, "detail": f"Chromium launch failed: {exc}"}
    return {"name": "playwright_chromium", "ok": True, "detail": "Chromium launch succeeded."}


def run_preflight(input_path: str | Path, output_dir: str | Path, validate: bool = False) -> dict:
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    checks = [
        _check_input_file(input_path),
        _check_wechat_plotkit_import(),
        _check_output_dir(output_dir),
    ]
    if validate:
        checks.append(_check_chromium_available())

    ok = all(item["ok"] for item in checks)
    return {
        "ok": ok,
        "status": "ready" if ok else "failed",
        "repo_root": REPO_ROOT.resolve().as_posix(),
        "package_root": PACKAGE_ROOT.resolve().as_posix(),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight checks for the wechat-analysis skill.")
    parser.add_argument("--input", required=True, help="Markdown file containing WeChat article links.")
    parser.add_argument("--out", required=True, help="Output run directory.")
    parser.add_argument("--validate", action="store_true", help="Require Chromium validation support.")
    args = parser.parse_args()

    result = run_preflight(args.input, args.out, validate=args.validate)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()

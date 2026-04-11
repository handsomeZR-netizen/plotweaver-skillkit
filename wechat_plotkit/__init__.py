"""Reusable toolkit for extracting plotting assets from WeChat articles."""

from .pipeline import analyze_links, build_style_index, generate_example, validate_capture

__all__ = [
    "analyze_links",
    "build_style_index",
    "generate_example",
    "validate_capture",
]

# Reuse Playbook

## How Codex Should Use This Pack

1. Read `master_style_index.json` to identify dominant plot families and palette choices.
2. Read `template_registry.json` to map target data in project B to the nearest template.
3. Apply `style_kit/theme.py` before drawing any final figure.
4. If an article is marked `manual_review_required`, prefer a confirmed template over OCR-derived code.

## Current Batch Summary

- Dominant template: `scatter`
- Top palette colors: `#ADB4DD, #FFFAF4, #BACBEA, #E2F4FD, #DFF5E1`

## Reuse Rules

- Keep serif typography, restrained colors, light grid, and high-resolution export.
- Treat extracted snippets as reference logic; convert them into reusable plotting functions in project B.
- Preserve figure spacing, annotation density, and line-weight hierarchy from the closest matched article.
- For unsupported chart forms, reuse theme and palette first, then adapt the nearest template.

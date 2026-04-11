---
name: plot-style-reuse
description: "Reuse extracted plotting styles in downstream projects. Use when Codex already has a `master_style_index.json`, `style_profile.json`, or `article.json` from this repo and needs to choose a starter template, explain the style rationale, or generate publication-style plotting code that applies `style_kit/theme.py` first. Do not use to fetch WeChat articles or rebuild a batch from raw links."
---

# Plot Style Reuse

Use this skill after analysis has already produced a stable style source. Read `references/downstream_integration.md` for the reuse order, `references/style_decision_rules.md` for visual constraints, and `references/template_mapping.md` for concrete template files.

## Workflow

1. Accept one style source:
   - `master_style_index.json`
   - `style_profile.json`
   - `article.json`
2. Resolve `template_registry.json` from the same run when possible.
3. Run `scripts/select_template.py` to choose a starter template.
4. Prefer `recommended_template` from the style source when that template exists in the registry.
5. If no direct recommendation exists, infer from `plot_types`, `layout_pattern`, and palette summary.
6. Run `scripts/generate_plot_example.py` when the user wants an actual starter script.

## Required Behavior

- Always apply `style_kit/theme.py` before custom plot logic.
- Treat low-confidence OCR snippets as reference material, not final production code.
- Return:
  - chosen template
  - rationale
  - template file path
  - generated script path when code generation was requested
  - any fallback assumptions

## Commands

Select a template from a completed run:

```powershell
python .agents/skills/plot-style-reuse/scripts/select_template.py --style-source .\examples\demo_pack\master_style_index.json
```

Generate a starter script in an export directory:

```powershell
python .agents/skills/plot-style-reuse/scripts/generate_plot_example.py --style-source .\examples\demo_pack\master_style_index.json --output .\exports
```

## Fallbacks

- If the style source lacks a registry, infer the template from the style source and explain that the selection is registry-free.
- If the source recommends a template that is absent from the registry, fall back to inference and record the mismatch.
- If the source came from an article marked `manual_review_required`, emphasize style reuse over direct code reuse.

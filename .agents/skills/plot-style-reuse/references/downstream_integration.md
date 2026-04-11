# Downstream Integration

Place this repository, or a curated exported style pack from it, inside the downstream project when the project needs direct access to extracted run artifacts and template files.

Recommended read order for Codex:

1. `master_style_index.json`
2. `template_registry.json`
3. `reuse_playbook.md`
4. `style_kit/theme.py`

Template selection priority:

1. `recommended_template`
2. `plot_types` plus `layout_pattern`
3. palette and typography cues
4. high-confidence extracted snippets from the closest article

Do not:

- promote low-confidence OCR snippets into final code without review
- bypass `style_kit/theme.py` and hand-roll conflicting rcParams
- replace the restrained palette with unrelated saturated defaults

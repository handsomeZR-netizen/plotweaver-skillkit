# Template Mapping

The registry produced by `PlotWeaver SkillKit` points to concrete starter templates:

- `line` -> `templates/line_template.py`
- `bar` -> `templates/bar_template.py`
- `scatter` -> `templates/scatter_template.py`
- `heatmap` -> `templates/heatmap_template.py`
- `distribution` -> `templates/distribution_template.py`
- `multi_panel` -> `templates/multi_panel_template.py`

Selection rules:

- Use `recommended_template` first when it exists in `template_registry.json`.
- If the source says `layout_pattern=multi_panel`, prefer `multi_panel`.
- Otherwise infer from `plot_types` using the package recommendation logic.
- Fall back to the registry's available dominant template only when the preferred template is missing.

Every generated starter script should call `style_kit/theme.py` before custom plot code.

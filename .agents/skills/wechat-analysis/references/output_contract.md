# WeChat Analysis Output Contract

Every successful analysis run should create these run-level artifacts:

- `batch_manifest.json`: batch counts, per-article status, validation summary.
- `master_style_index.json`: aggregated plot-type, palette, and template summary.
- `template_registry.json`: concrete starter template files and their fit labels.
- `reuse_playbook.md`: downstream reuse guidance for later plot generation.

Article-level outputs live under `articles/<slug>/`:

- `raw/article.html`: original article HTML.
- `raw/body.html`: parsed article body HTML.
- `raw/article.txt`: extracted body text.
- `assets/images/`: downloaded article images.
- `assets/code/`: high-confidence extracted code snippets.
- `assets/ocr/`: OCR fallback snippets when text code was not extracted.
- `article.json`: full article record.
- `style_profile.json`: compact style profile.
- `manual_review.md`: only present when manual review is required.

Validation outputs live under `validation/<slug>/`:

- `page_full.png` or tiled `page_*.png`: captured screenshots.
- `validation.json`: structured validation record.
- `missing_report.md`: human-readable gap report.

The skill response should always return the run directory, manifest path, style index path when present, and explicit lists of failed or manual-review articles.

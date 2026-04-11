# WeChat Analysis Failure Modes

## Input and environment

- Missing Markdown file: stop before running extraction.
- `wechat_plotkit` cannot be imported: stop and report the repo or environment issue.
- Validation requested but Chromium cannot launch: stop and explain that browser validation cannot run.

## Per-article extraction

- Fetch failures: continue the batch, mark the article as failed, and list the URL in the final summary.
- No high-confidence DOM code found: write `manual_review.md` and treat OCR snippets only as hints.
- Palette extraction weak or absent: keep the article, but report that reuse should lean on typography, spacing, and template shape instead of color.

## Validation

- Browser validation can fail even when extraction succeeded. Report it as a validation failure, not as a full batch failure.
- DOM image or code counts can exceed extracted assets. Surface that mismatch in `missing_report.md` and the final summary.

## Existing output directories

- Reusing an existing run directory can mix old and new artifacts. Prefer a fresh output path unless the user explicitly wants to rebuild or revalidate an existing run.

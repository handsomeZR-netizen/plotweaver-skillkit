# Manual Review Protocol

Use this only when an article was marked `manual_review_required`.

Trigger conditions:

- the article body does not expose usable text code blocks
- code appears to exist only in screenshots
- downloaded image count does not match the browser DOM
- browser validation shows missing sections or ordering problems

Recommended sequence:

1. Open `validation/<slug>/page_full.png` or tiled page screenshots.
2. Read `validation/<slug>/missing_report.md`.
3. Compare that result with `articles/<slug>/manual_review.md`.
4. If code can be recovered manually, place confirmed snippets into `articles/<slug>/assets/code/`.
5. Record what was added and where it came from in `manual_review.md`.

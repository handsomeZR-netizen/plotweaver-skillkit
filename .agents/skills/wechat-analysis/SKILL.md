---
name: wechat-analysis
description: "Analyze a Markdown file of WeChat public-article links into a reusable plotting-style dataset. Use when Codex needs to fetch WeChat articles, extract text, images, code snippets, and OCR fallbacks, build batch manifests and style indexes, or run sampled browser validation for a fresh batch. Do not use for downstream plot generation from an existing style index or for reviewing an already completed run without re-analysis."
---

# WeChat Analysis

Run the repo-local wrappers in this skill when the task starts from raw WeChat article links and needs a fresh analysis run under `runs/` or another chosen output directory.

Read `references/usage.md` for concrete CLI examples, `references/output_contract.md` for the run layout, and `references/failure_modes.md` only when a run fails or validation cannot proceed.

## Workflow

1. Require two inputs:
   - a Markdown file containing WeChat article links
   - an output directory for the run
2. Run `scripts/preflight_check.py` before any heavy operation.
3. Stop immediately if the input file is missing, `wechat_plotkit` cannot be imported, or browser validation was requested but Chromium cannot launch.
4. Run `scripts/run_analysis.py` to execute the batch.
5. Report the stable artifacts:
   - `batch_manifest.json`
   - `master_style_index.json` if generated
   - `template_registry.json`
   - `reuse_playbook.md`
6. Summarize:
   - processed count
   - failed count
   - articles marked `manual_review_required`
   - validation status counts if validation ran

## Required Behavior

- Prefer the wrapper scripts in this skill over rebuilding the command flow by hand.
- Pass `--validate` only when the user asked for browser-backed capture checks or when validation is necessary to explain extraction gaps.
- Continue through per-article fetch failures and report failed URLs instead of aborting the whole batch.
- Point the user to article-level `manual_review.md` when high-confidence text code was not extracted.
- Treat OCR snippets as hints for review, not as final trusted plotting code.

## Commands

Use these wrappers from the repo root:

```powershell
python .agents/skills/wechat-analysis/scripts/preflight_check.py --input .\links.md --out .\runs\demo
python .agents/skills/wechat-analysis/scripts/run_analysis.py --input .\links.md --out .\runs\demo --validate --sample-mode risk_based --sample-limit 3
```

## Failure Handling

- If validation was requested and preflight reports Chromium is unavailable, stop and explain the missing dependency instead of silently skipping validation.
- If analysis succeeds with partial failures, return the run directory and list the failed articles separately.
- If the user only wants to inspect an existing run, switch to `$plot-style-reuse` or read the review artifacts directly instead of rerunning analysis.

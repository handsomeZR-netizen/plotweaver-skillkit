# PlotWeaver SkillKit

[简体中文](README.md)

<p align="center">
  <img src="docs/assets/hero.svg" alt="PlotWeaver SkillKit hero banner" width="100%">
</p>

<p align="center">
  <a href="https://github.com/handsomeZR-netizen/plotweaver-skillkit"><img src="https://img.shields.io/badge/Codex-SkillKit-111827?style=flat-square" alt="Codex SkillKit"></a>
  <a href="https://github.com/handsomeZR-netizen/plotweaver-skillkit"><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/Playwright-Validation-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright validation"></a>
  <a href="https://github.com/garrettj403/SciencePlots"><img src="https://img.shields.io/badge/SciencePlots-Ready-1F6FEB?style=flat-square" alt="SciencePlots ready"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/handsomeZR-netizen/plotweaver-skillkit?style=flat-square" alt="MIT license"></a>
  <a href="https://github.com/handsomeZR-netizen/plotweaver-skillkit/stargazers"><img src="https://img.shields.io/github/stars/handsomeZR-netizen/plotweaver-skillkit?style=flat-square" alt="GitHub stars"></a>
</p>

> A Codex-ready skill + toolkit for turning WeChat article plots into reusable paper-figure style assets.

`PlotWeaver SkillKit` packages two things into one repository:

- a `wechat-plotkit` Python toolkit that fetches article content, extracts plotting cues, builds style indexes, and validates capture quality
- a pair of Codex skills that turn raw article links into reusable assets, then turn those assets into starter plotting code for downstream paper projects

This repository is designed for a very specific workflow: build a style pack once, then let Codex read that pack together with project B and reuse the visual language with much less prompt friction and much higher consistency.

## Why PlotWeaver

Most alternatives stop at one of these layers:

- a crawler that saves article HTML but does not surface plot style decisions
- a screenshot scrapbook that shows inspiration but does not produce reusable code paths
- a one-shot prompt workflow that can imitate a look once, but cannot keep a stable style memory across projects

`PlotWeaver SkillKit` focuses on the handoff layer between inspiration and implementation.

- `Signal Harvester`: fetch article HTML, images, text, high-confidence code snippets, and OCR fallbacks
- `Style Loom`: distill each article into `style_profile.json`, then aggregate a batch into `master_style_index.json`, `template_registry.json`, and `reuse_playbook.md`
- `Proof Capture`: sample browser screenshots and generate missing reports so extraction quality is not a blind guess
- `Project-B Handoff`: generate starter plotting scripts and explicit reuse rules that Codex can apply inside a downstream paper repository

## What Makes It Different

| Typical approach | PlotWeaver SkillKit |
| --- | --- |
| Saves pages and images | Builds a reusable style dataset with explicit plot types, palettes, confidence, layout patterns, and template suggestions |
| Relies on raw snippets | Separates trusted code, OCR hints, and manual-review paths so low-confidence extraction does not silently become production code |
| Good for one batch | Designed to become a portable style pack that can be dropped into project B and read by Codex later |
| Focuses on scraping | Focuses on reuse: template registry, starter code generation, theme entrypoint, and downstream playbook |
| Trusts extraction blindly | Adds browser-backed validation and missing reports to surface gaps before reuse |

## What You Actually Get

`PlotWeaver SkillKit` does not stop at downloaded article content. It gives you a reusable style asset layer that can keep working across projects:

- `master_style_index.json`: a batch-level style map that turns many inspirations into one reusable reference point
- `style_profile.json`: article-level summaries for palette, layout, annotation density, and plot family
- `template_registry.json`: an explicit bridge from extracted style signals to starter plotting templates
- `reuse_playbook.md`: practical reuse guidance that Codex can follow inside a downstream project
- starter plotting scripts: runnable code seeds that convert inspiration into action quickly

In other words, the output is not just a scrape. It is a reusable memory of style.

## Who This Is For

- researchers who want a stable Codex-assisted plotting workflow
- users who regularly study WeChat plotting articles and want to operationalize the inspiration
- teams that want to carry a visual language from one paper project to the next
- skill builders who want a stronger plotting foundation than one-off prompts

## Typical Use Cases

- turn a batch of WeChat plotting articles into a private style pack
- drop that style pack into a new paper project and let Codex reuse the same visual language
- choose the closest starter template for a new figure automatically
- build a long-lived plotting reference base for a broader skill ecosystem

## Quick Start

### 1. Install

```powershell
python -m pip install -e .[dev,style]
python -m playwright install chromium
```

Optional OCR support:

```powershell
python -m pip install -e .[ocr]
```

### 2. Analyze a Markdown link list

```powershell
wechat-plotkit analyze-links --input .\links.md --out .\runs\demo --validate --sample-mode risk_based --sample-limit 3
```

### 3. Rebuild an index or rerun validation

```powershell
wechat-plotkit build-style-index --run .\runs\demo
wechat-plotkit validate-capture --run .\runs\demo --sample-mode manual_only --sample-limit 5
```

### 4. Generate a starter plotting script from a style source

```powershell
wechat-plotkit generate-example --style-source .\examples\demo_pack\master_style_index.json --template scatter --output .\exports
```

## Codex Skill Entry Points

The repository also ships two repo-local skills:

- `wechat-analysis`: starts from raw WeChat links and produces a fresh reusable style dataset
- `plot-style-reuse`: starts from an existing style source and selects or generates the best starter template

Example invocations:

```powershell
python .agents/skills/wechat-analysis/scripts/preflight_check.py --input .\links.md --out .\runs\demo --validate
python .agents/skills/wechat-analysis/scripts/run_analysis.py --input .\links.md --out .\runs\demo --validate
python .agents/skills/plot-style-reuse/scripts/select_template.py --style-source .\examples\demo_pack\master_style_index.json
python .agents/skills/plot-style-reuse/scripts/generate_plot_example.py --style-source .\examples\demo_pack\master_style_index.json --output .\exports
```

## Curated Demo Pack

The repository includes a lightweight demo pack that is ready for exploration and showcase use:

- [`examples/demo_pack/master_style_index.json`](examples/demo_pack/master_style_index.json)
- [`examples/demo_pack/template_registry.json`](examples/demo_pack/template_registry.json)
- [`examples/demo_pack/reuse_playbook.md`](examples/demo_pack/reuse_playbook.md)
- [`examples/demo_pack/style_profile_radar.json`](examples/demo_pack/style_profile_radar.json)
- [`examples/demo_pack/article_radar.json`](examples/demo_pack/article_radar.json)

It keeps the public repository lightweight while still showing the exact artifact shapes that Codex and downstream projects will use.

## Preview

![Annotated template preview](docs/assets/annotated-template.png)

## How To Plug It Into Your Project

Recommended downstream layout:

```text
project-b/
  vendor/
    plotweaver-skillkit/
  src/
  data/
```

Recommended Codex read order:

1. `master_style_index.json`
2. `template_registry.json`
3. `reuse_playbook.md`
4. matched `article.json` or `style_profile.json`
5. `style_kit/theme.py`

## Repository Layout

```text
.agents/                 Codex skills and wrapper scripts
docs/                    Usage notes, integration guidance, visual assets
examples/demo_pack/      Lightweight public example artifacts
style_kit/               Theme entrypoint and palette assets
templates/               Starter plotting templates
tests/                   Package and skill workflow tests
wechat_plotkit/          Core toolkit package
```

## Why It Belongs In Your Skill Stack

- it combines `Skill + Toolkit + Template + Style Pack` instead of shipping just one script
- it is designed to compound value over time as your style assets grow
- it helps Codex do more than imitate a look once; it helps Codex keep that look across projects
- it works well as a foundation repository for a larger scientific plotting workflow

## Tagline

> PlotWeaver SkillKit turns plotting inspiration from WeChat articles into long-lived style assets you can keep reusing.

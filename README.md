# PlotWeaver SkillKit

[English](README.en.md)

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

> 面向 Codex 的公众号绘图风格提取与论文复用工具链。
>
> A Codex-ready skill + toolkit for turning WeChat article plots into reusable paper-figure style assets.

`PlotWeaver SkillKit` 把两类能力打包进了同一个仓库：

- 一个 `wechat-plotkit` Python 工具包，负责抓取文章内容、抽取绘图信号、构建风格索引，并做浏览器校验
- 两个面向 Codex 的 repo-local skills，负责把原始公众号链接变成可复用风格资产，再把这些资产变成下游论文项目可直接接手的 starter plotting code

这个仓库不是为了“一次性抓完一批文章”而设计的，而是为了构建一套可持续复用的 style pack。你可以先分析一批公众号绘图文章，再让 Codex 在项目 B 里同时读取这份风格包和项目代码，从而更稳定地复用配色、布局、注释密度和整体图形语言。

## 这个仓库解决什么问题

市面上很多相近方案通常只做到其中一层：

- 只做爬取，保存 HTML 和图片，但不显式总结绘图风格决策
- 只做截图收藏，能看灵感，但不能转成稳定的复用代码路径
- 只靠一次 prompt 模仿风格，能临时出图，但很难跨项目保持一致的风格记忆

`PlotWeaver SkillKit` 重点做的是“从灵感到复用”的交接层。

- `Signal Harvester`：抓取 HTML、正文、图片、高置信代码片段，以及 OCR 回退候选
- `Style Loom`：把每篇文章沉淀为 `style_profile.json`，再把整批文章汇总为 `master_style_index.json`、`template_registry.json` 和 `reuse_playbook.md`
- `Proof Capture`：用浏览器抽样截图和缺失报告去验证抽取结果，而不是盲信抓取
- `Project-B Handoff`：生成 starter plotting script 和明确的复用规则，方便 Codex 在下游论文项目里直接接手

## 和同类方案的差异点

| 常见做法 | PlotWeaver SkillKit |
| --- | --- |
| 只保存页面和图片 | 直接产出可复用的风格数据集，包含 plot types、palette、confidence、layout pattern 和模板建议 |
| 直接相信抓到的代码片段 | 区分高置信代码、OCR 提示和人工复核路径，避免低质量抽取直接进入生产图 |
| 只适合单次批处理 | 目标是形成一个可移植的 style pack，后续可以放进项目 B 继续复用 |
| 重心在爬取 | 重心在复用，提供 template registry、starter code generation、theme entrypoint 和 reuse playbook |
| 没有校验层 | 加入浏览器抽样验证和 missing report，能更早暴露漏抓与抽取缺口 |

## 核心产物

每次成功分析都会生成一套稳定的产物契约，方便 Codex 和下游项目直接读取：

- `batch_manifest.json`：本批次处理了什么、失败了什么、哪些需要人工复核
- `articles/<slug>/article.json`：文章级抽取快照
- `articles/<slug>/style_profile.json`：文章级风格总结
- `master_style_index.json`：批次级 plot family、library、palette 和推荐模板汇总
- `template_registry.json`：模板映射注册表
- `reuse_playbook.md`：项目 B 里的复用规则说明
- `validation/validation_manifest.json`：启用浏览器校验时生成的验证记录

## 快速开始

### 1. 安装

```powershell
python -m pip install -e .[dev,style]
python -m playwright install chromium
```

如果你本地还准备启用 OCR：

```powershell
python -m pip install -e .[ocr]
```

### 2. 分析 Markdown 链接清单

```powershell
wechat-plotkit analyze-links --input .\links.md --out .\runs\demo --validate --sample-mode risk_based --sample-limit 3
```

### 3. 重建索引或重新执行校验

```powershell
wechat-plotkit build-style-index --run .\runs\demo
wechat-plotkit validate-capture --run .\runs\demo --sample-mode manual_only --sample-limit 5
```

### 4. 从风格源生成 starter plotting script

```powershell
wechat-plotkit generate-example --style-source .\examples\demo_pack\master_style_index.json --template scatter --output .\exports
```

## Codex Skill 入口

这个仓库同时提供两个 repo-local skills：

- `wechat-analysis`：从原始公众号链接出发，生成一份新的可复用风格数据集
- `plot-style-reuse`：从现有 style source 出发，自动选择最合适的 starter template，并生成示例脚本

调用示例：

```powershell
python .agents/skills/wechat-analysis/scripts/preflight_check.py --input .\links.md --out .\runs\demo --validate
python .agents/skills/wechat-analysis/scripts/run_analysis.py --input .\links.md --out .\runs\demo --validate
python .agents/skills/plot-style-reuse/scripts/select_template.py --style-source .\examples\demo_pack\master_style_index.json
python .agents/skills/plot-style-reuse/scripts/generate_plot_example.py --style-source .\examples\demo_pack\master_style_index.json --output .\exports
```

## 精简演示包

为了让公开仓库足够轻量，这里没有直接上传全量本地抓取结果，而是保留了一套可展示数据结构的精简 demo：

- [`examples/demo_pack/master_style_index.json`](examples/demo_pack/master_style_index.json)
- [`examples/demo_pack/template_registry.json`](examples/demo_pack/template_registry.json)
- [`examples/demo_pack/reuse_playbook.md`](examples/demo_pack/reuse_playbook.md)
- [`examples/demo_pack/style_profile_radar.json`](examples/demo_pack/style_profile_radar.json)
- [`examples/demo_pack/article_radar.json`](examples/demo_pack/article_radar.json)

这套 demo 足够展示下游项目和 Codex 真正会消费的文件形状，同时避免公开仓库过大。

## 预览

![Annotated template preview](docs/assets/annotated-template.png)

## 如何接入项目 B

推荐的下游目录结构：

```text
project-b/
  vendor/
    plotweaver-skillkit/
  src/
  data/
```

推荐的 Codex 读取顺序：

1. `master_style_index.json`
2. `template_registry.json`
3. `reuse_playbook.md`
4. 与目标图最接近的 `article.json` 或 `style_profile.json`
5. `style_kit/theme.py`

## 仓库结构

```text
.agents/                 Codex skills 和 wrapper scripts
docs/                    使用说明、集成文档、展示素材
examples/demo_pack/      轻量级公开演示产物
style_kit/               主题入口和调色板资产
templates/               starter plotting templates
tests/                   包级测试和 skill workflow 测试
wechat_plotkit/          核心工具包
```

## 边界与限制

- 微信公众号页面结构可能变化，也可能出现额外反爬限制，所以这套流程应该被视为 best-effort extraction，而不是法律意义上的归档器
- OCR 片段只是提示，不应该被直接当作最终可信绘图代码
- 如果版权边界或仓库体积不清晰，不建议把完整原始抓取全集直接公开上传

## 一句话定位

如果你要把这个项目写进 GitHub About、演示文档或者对外介绍，可以直接用这句：

> PlotWeaver SkillKit 是一套面向 Codex 的风格资产化系统，用来从公众号绘图文章中提取 plotting signals，把它们沉淀为可复用的 style pack，并在下游论文项目中重放这些风格。

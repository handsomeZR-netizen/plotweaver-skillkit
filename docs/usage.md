# Usage

## 1. 安装

```powershell
python -m pip install -e .[dev,style]
python -m playwright install chromium
```

如果本地已有 `tesseract` 和 `pytesseract`，还可以安装：

```powershell
python -m pip install -e .[ocr]
```

## 2. 分析公众号链接清单

```powershell
wechat-plotkit analyze-links --input .\links.md --out .\runs\demo --validate --sample-mode risk_based --sample-limit 3
```

## 3. 重新构建风格索引

```powershell
wechat-plotkit build-style-index --run .\runs\demo
```

## 4. 重新执行浏览器校验

```powershell
wechat-plotkit validate-capture --run .\runs\demo --sample-mode manual_only --sample-limit 5
```

## 5. 生成示例脚本

```powershell
wechat-plotkit generate-example --style-source .\examples\demo_pack\master_style_index.json --template line --output .\exports
```

## 6. 输出目录说明

- `articles/<slug>/raw/article.html`: 原始 HTML
- `articles/<slug>/raw/body.html`: 解析后的正文节点
- `articles/<slug>/assets/images/`: 下载的正文图片
- `articles/<slug>/assets/code/`: 抽取的高置信代码片段
- `articles/<slug>/assets/ocr/`: OCR 候选代码片段
- `articles/<slug>/manual_review.md`: 需要人工补录时生成
- `validation/<slug>/page_full.png`: 浏览器整页截图
- `validation/<slug>/missing_report.md`: 缺失报告和截图索引

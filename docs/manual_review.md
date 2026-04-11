# Manual Review Protocol

以下情况会触发人工补录：

- 页面正文没有可解析的文本代码块
- 代码疑似以截图形式存在
- 下载图片数量与浏览器 DOM 数量不一致
- 浏览器截图显示有遗漏段落或顺序错误

人工补录时建议：

1. 先看 `validation/<slug>/page_full.png`
2. 对照 `missing_report.md`
3. 将确认后的代码补入 `articles/<slug>/assets/code/`
4. 在 `manual_review.md` 中追加说明补录来源和修改日期

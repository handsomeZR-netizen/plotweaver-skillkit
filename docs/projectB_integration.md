# Project B Integration

## 接入方式

推荐把整个仓库作为一个 vendored 工具包放入项目 B，或把需要的 style pack 目录单独拷入 `vendor/plotweaver-skillkit/`。

```text
project-b/
  vendor/
    plotweaver-skillkit/
  src/
  data/
```

## Codex 使用顺序

1. 读 `runs/<batch>/master_style_index.json`，或一份已导出的 demo/style pack
2. 读 `runs/<batch>/template_registry.json`
3. 读 `runs/<batch>/reuse_playbook.md`
4. 按数据结构匹配模板，再补读最接近的 `article.json` 或 `style_profile.json`
5. 在新图代码中先调用 `style_kit/theme.py`

## 复用优先级

- 第一优先级：`recommended_template`
- 第二优先级：`palette_hex` + `layout_pattern`
- 第三优先级：同类文章的高置信代码片段

## 禁止的捷径

- 不要直接把低置信 OCR 代码当最终产图代码。
- 不要绕过主题系统单独改默认 rcParams。
- 不要混用与索引风格明显冲突的高饱和颜色。

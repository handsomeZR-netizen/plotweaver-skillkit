# WeChat Analysis Usage

Run the skill wrappers from the repository root.

## Preflight

```powershell
python .agents/skills/wechat-analysis/scripts/preflight_check.py --input .\links.md --out .\runs\demo
```

Add `--validate` when the run must prove browser validation is available before analysis starts.

## Execute a batch

```powershell
python .agents/skills/wechat-analysis/scripts/run_analysis.py --input .\links.md --out .\runs\demo --validate --sample-mode risk_based --sample-limit 3
```

The wrapper delegates to the package CLI behavior:

```powershell
wechat-plotkit analyze-links --input .\links.md --out .\runs\demo --validate --sample-mode risk_based --sample-limit 3
```

## Related package commands

Rebuild a style index from an existing run:

```powershell
wechat-plotkit build-style-index --run .\runs\demo
```

Re-run validation for an existing batch:

```powershell
wechat-plotkit validate-capture --run .\runs\demo --sample-mode manual_only --sample-limit 5
```

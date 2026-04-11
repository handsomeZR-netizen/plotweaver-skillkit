from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


STYLE_ROOT = Path(__file__).resolve().parent


def get_palette(name: str = "atlas") -> list[str]:
    palettes = json.loads((STYLE_ROOT / "palettes.json").read_text(encoding="utf-8"))
    return palettes.get(name, palettes["atlas"])


def apply_publication_theme(palette_name: str = "atlas", use_chinese: bool = False) -> list[str]:
    try:
        import scienceplots  # noqa: F401

        plt.style.use(["science", "nature", "no-latex"])
    except Exception:
        plt.style.use("default")

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "STSong", "SimSun", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.color": "#D9DDE3",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.6,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "savefig.dpi": 600,
            "figure.dpi": 150,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    if use_chinese:
        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
    return get_palette(palette_name)


def export_figure(fig, output_stem: str | Path) -> None:
    output_stem = Path(output_stem)
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    for suffix in [".png", ".pdf", ".svg"]:
        fig.savefig(output_stem.with_suffix(suffix), bbox_inches="tight", dpi=600)

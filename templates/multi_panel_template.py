from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from style_kit.theme import apply_publication_theme, export_figure


def main() -> None:
    palette = apply_publication_theme("atlas")
    rng = np.random.default_rng(21)
    x = np.linspace(0, 12, 90)
    y = 0.25 * x + np.sin(x * 0.8) + rng.normal(0, 0.15, size=len(x))
    categories = ["Q1", "Q2", "Q3", "Q4"]
    values = np.array([3.1, 4.0, 4.6, 5.2])

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2), gridspec_kw={"width_ratios": [1.4, 1.0]})

    axes[0].plot(x, y, color=palette[0], linewidth=2.2)
    axes[0].fill_between(x, y - 0.18, y + 0.18, color=palette[2], alpha=0.20, linewidth=0)
    axes[0].set_title("Trend")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Signal")

    axes[1].bar(categories, values, color=[palette[4], palette[2], palette[0], palette[5]], alpha=0.92)
    axes[1].set_title("Summary")
    axes[1].set_ylabel("Score")

    fig.suptitle("Publication multi-panel template", y=1.02)
    fig.tight_layout()
    export_figure(fig, "outputs/multi_panel_template")


if __name__ == "__main__":
    main()

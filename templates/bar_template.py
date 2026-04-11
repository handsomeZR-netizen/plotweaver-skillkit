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
    categories = ["A", "B", "C", "D", "E"]
    control = np.array([3.8, 4.2, 5.1, 4.6, 5.4])
    treated = np.array([4.4, 4.9, 5.6, 5.0, 5.9])
    x = np.arange(len(categories))
    width = 0.34

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.bar(x - width / 2, control, width=width, color=palette[0], alpha=0.92, label="Control")
    ax.bar(x + width / 2, treated, width=width, color=palette[2], alpha=0.92, label="Treatment")
    ax.set_xticks(x, categories)
    ax.set_ylabel("Normalized signal")
    ax.set_title("Publication bar template")
    ax.legend(loc="upper left")

    for index, value in enumerate(treated):
        ax.text(index + width / 2, value + 0.06, f"{value:.1f}", ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    export_figure(fig, "outputs/bar_template")


if __name__ == "__main__":
    main()

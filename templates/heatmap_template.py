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
    apply_publication_theme("atlas")
    grid = np.array(
        [
            [0.81, 0.42, 0.26, 0.18],
            [0.55, 0.73, 0.39, 0.22],
            [0.31, 0.44, 0.78, 0.47],
            [0.16, 0.28, 0.53, 0.86],
        ]
    )

    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    image = ax.imshow(grid, cmap="Blues", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(4), ["T1", "T2", "T3", "T4"])
    ax.set_yticks(range(4), ["G1", "G2", "G3", "G4"])
    ax.set_title("Publication heatmap template")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Similarity")

    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            ax.text(col, row, f"{grid[row, col]:.2f}", ha="center", va="center", fontsize=8)

    fig.tight_layout()
    export_figure(fig, "outputs/heatmap_template")


if __name__ == "__main__":
    main()

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from style_kit.theme import apply_publication_theme, export_figure


def main() -> None:
    palette = apply_publication_theme("atlas")
    x = np.linspace(0, 10, 80)
    y = np.sin(x) + 0.15 * np.cos(3 * x)

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot(x, y, color=palette[0], linewidth=2.2, label="Signal")
    ax.fill_between(x, y - 0.12, y + 0.12, color=palette[2], alpha=0.22)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc="upper right")
    export_figure(fig, "outputs/minimal_template")


if __name__ == "__main__":
    main()

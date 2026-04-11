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
    rng = np.random.default_rng(9)
    group_a = rng.normal(0.0, 0.85, size=240)
    group_b = rng.normal(0.55, 0.65, size=240)
    bins = np.linspace(-2.8, 3.0, 22)

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.hist(group_a, bins=bins, density=True, color=palette[0], alpha=0.55, label="Group A")
    ax.hist(group_b, bins=bins, density=True, color=palette[2], alpha=0.55, label="Group B")
    ax.axvline(group_a.mean(), color=palette[4], linewidth=1.2, linestyle="--")
    ax.axvline(group_b.mean(), color=palette[5], linewidth=1.2, linestyle="--")
    ax.set_xlabel("Standardized measurement")
    ax.set_ylabel("Density")
    ax.set_title("Publication distribution template")
    ax.legend(loc="upper right")
    fig.tight_layout()
    export_figure(fig, "outputs/distribution_template")


if __name__ == "__main__":
    main()

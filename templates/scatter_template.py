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
    rng = np.random.default_rng(5)
    x = rng.normal(5.0, 1.2, size=80)
    y = 1.35 * x + rng.normal(0, 1.1, size=80)
    fit = np.polyfit(x, y, deg=1)
    x_fit = np.linspace(x.min(), x.max(), 80)
    y_fit = np.polyval(fit, x_fit)

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.scatter(x, y, s=34, color=palette[0], alpha=0.82, edgecolor="white", linewidth=0.5)
    ax.plot(x_fit, y_fit, color=palette[4], linewidth=2.0, label="Trend line")
    ax.set_xlabel("Predictor")
    ax.set_ylabel("Outcome")
    ax.set_title("Publication scatter template")
    ax.legend(loc="upper left")
    fig.tight_layout()
    export_figure(fig, "outputs/scatter_template")


if __name__ == "__main__":
    main()

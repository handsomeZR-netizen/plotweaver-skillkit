from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from style_kit.theme import apply_publication_theme, export_figure


def build_demo_series(seed: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 12, 120)
    baseline = 0.3 * x + np.sin(x * 0.9)
    signal = baseline + rng.normal(0, 0.18, size=len(x))
    band = 0.25 + 0.05 * np.cos(x)
    return x, signal, band


def main() -> None:
    # Theme first: keep palette, typography, and export behavior stable across projects.
    palette = apply_publication_theme("atlas")
    x, signal, band = build_demo_series()

    fig, ax = plt.subplots(figsize=(6.8, 4.3))

    # Use a restrained hierarchy: one dominant line, one support ribbon, limited annotation.
    ax.plot(x, signal, color=palette[0], linewidth=2.4, label="Primary trend")
    ax.fill_between(x, signal - band, signal + band, color=palette[2], alpha=0.20, linewidth=0)

    highlight_mask = (x >= 4.5) & (x <= 7.5)
    ax.plot(x[highlight_mask], signal[highlight_mask], color=palette[4], linewidth=2.8)
    ax.axvspan(4.5, 7.5, color=palette[5], alpha=0.25)
    ax.annotate(
        "Key interval",
        xy=(6.0, signal[highlight_mask].max()),
        xytext=(7.7, signal[highlight_mask].max() + 0.8),
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": palette[4]},
        fontsize=9,
        color=palette[4],
    )

    ax.set_xlabel("Time")
    ax.set_ylabel("Measured response")
    ax.set_title("Reusable publication-style template")
    ax.legend(loc="upper left")
    export_figure(fig, "outputs/annotated_template")


if __name__ == "__main__":
    main()

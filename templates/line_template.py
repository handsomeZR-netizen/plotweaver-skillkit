from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from style_kit.theme import apply_publication_theme, export_figure


def build_series(seed: int = 11) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 18, 160)
    baseline = 0.18 * x + 0.55 * np.sin(x * 0.65)
    signal = baseline + rng.normal(0, 0.12, size=len(x))
    band = 0.18 + 0.04 * np.cos(x)
    return x, signal, band


def main() -> None:
    palette = apply_publication_theme("atlas")
    x, signal, band = build_series()

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(x, signal, color=palette[0], linewidth=2.4, label="Observed series")
    ax.fill_between(x, signal - band, signal + band, color=palette[2], alpha=0.22, linewidth=0)
    ax.axhline(signal.mean(), color=palette[4], linewidth=1.0, linestyle="--", label="Mean level")
    ax.set_title("Publication line template")
    ax.set_xlabel("Time")
    ax.set_ylabel("Response")
    ax.legend(loc="upper left")
    fig.tight_layout()
    export_figure(fig, "outputs/line_template")


if __name__ == "__main__":
    main()

"""Minimal end-to-end example: run a small threshold sweep and save plots.

Run with:
    python examples/quick_threshold.py

Outputs are written to ``outputs/`` (gitignored).
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from surfacecode import run_threshold_sweep
from surfacecode.viz import plot_logical_vs_distance, plot_threshold_sweep


def main() -> None:
    os.makedirs("outputs", exist_ok=True)

    result = run_threshold_sweep(
        distances=[3, 5, 7],
        error_rates=[0.005, 0.008, 0.01, 0.012, 0.015],
        shots=20_000,
        seed=2026,
    )

    ax = plot_threshold_sweep(result)
    ax.figure.tight_layout()
    ax.figure.savefig("outputs/threshold_sweep.png", dpi=150)
    plt.close(ax.figure)

    ax = plot_logical_vs_distance(result, p=0.008)
    ax.figure.tight_layout()
    ax.figure.savefig("outputs/logical_vs_distance.png", dpi=150)
    plt.close(ax.figure)

    print(f"threshold estimate: {result.threshold_estimate}")
    print("saved outputs/threshold_sweep.png and outputs/logical_vs_distance.png")


if __name__ == "__main__":
    main()

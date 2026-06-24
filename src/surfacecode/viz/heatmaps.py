"""Syndrome heatmap rendering.

A surface-code memory experiment produces ``rounds`` layers of detectors. We
reshape the flat per-detector firing frequencies into a ``rounds x checks``
grid so the spatial-temporal structure of where errors are detected is visible
at a glance.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from ..sampling import SyndromeSample, syndrome_density


def plot_syndrome_heatmap(
    sample: SyndromeSample,
    *,
    rounds: int,
    ax: Axes | None = None,
    title: str = "Detector firing frequency",
) -> Axes:
    """Render per-detector firing frequencies as a ``rounds x checks`` heatmap.

    Falls back to a single-row layout when the detector count is not divisible
    by ``rounds`` (which can happen for boundary rounds in some codes).
    """
    if rounds < 1:
        raise ValueError("rounds must be >= 1")

    density = syndrome_density(sample)
    num_detectors = density.shape[0]
    if num_detectors % rounds == 0:
        grid = density.reshape(rounds, num_detectors // rounds)
        ylabel = "Measurement round"
    else:
        grid = density.reshape(1, num_detectors)
        ylabel = ""

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 4))
    image = ax.imshow(grid, aspect="auto", cmap="magma", vmin=0.0, vmax=float(density.max() or 1.0))
    ax.set_title(title)
    ax.set_xlabel("Detector (stabilizer check)")
    ax.set_ylabel(ylabel)
    plt.colorbar(image, ax=ax, label="Firing probability")
    return ax

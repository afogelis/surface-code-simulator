"""Threshold and scaling plots."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ..types import ThresholdPoint, ThresholdResult


def _group_by_distance(points: Sequence[ThresholdPoint]) -> dict[int, list[ThresholdPoint]]:
    grouped: dict[int, list[ThresholdPoint]] = {}
    for point in points:
        grouped.setdefault(point.distance, []).append(point)
    for series in grouped.values():
        series.sort(key=lambda pt: pt.p)
    return grouped


def plot_threshold_sweep(result: ThresholdResult, *, ax: Axes | None = None) -> Axes:
    """Plot logical error rate vs physical error rate, one curve per distance.

    Curves for different distances crossing at a common point is the visual
    signature of the threshold; the estimated crossing is marked when present.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    for distance, series in sorted(_group_by_distance(result.points).items()):
        ps = [pt.p for pt in series]
        lers = [pt.logical_error_rate for pt in series]
        lows = [pt.logical_error_rate - pt.ci_low for pt in series]
        highs = [pt.ci_high - pt.logical_error_rate for pt in series]
        ax.errorbar(ps, lers, yerr=[lows, highs], marker="o", capsize=3, label=f"d = {distance}")

    if result.threshold_estimate is not None:
        ax.axvline(result.threshold_estimate, linestyle="--", color="gray",
                   label=f"p_th ~ {result.threshold_estimate:.4f}")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Logical error rate (per shot)")
    ax.set_title("Surface-code threshold sweep")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    return ax


def plot_logical_vs_distance(result: ThresholdResult, *, p: float, ax: Axes | None = None) -> Axes:
    """Plot logical error rate vs code distance at a fixed physical error rate.

    Below threshold this curve falls (often exponentially) with distance; above
    threshold it rises. The nearest available physical rate to ``p`` is used.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    available = sorted({pt.p for pt in result.points})
    nearest = min(available, key=lambda candidate: abs(candidate - p))
    selected = sorted((pt for pt in result.points if pt.p == nearest), key=lambda pt: pt.distance)

    distances = [pt.distance for pt in selected]
    lers = [pt.logical_error_rate for pt in selected]
    ax.semilogy(distances, lers, marker="s")
    ax.set_xlabel("Code distance d")
    ax.set_ylabel("Logical error rate (per shot)")
    ax.set_title(f"Logical error rate vs distance at p = {nearest:.4f}")
    ax.grid(True, which="both", alpha=0.3)
    return ax

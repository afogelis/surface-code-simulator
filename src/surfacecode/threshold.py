"""Threshold sweeps over code distance and physical error rate.

A code is *below threshold* at physical rate ``p`` when increasing the code
distance lowers the logical error rate. The threshold ``p_th`` is the crossing
point where curves for different distances intersect. We provide a direct
sweep (looping over our own experiment driver) and a convenience crossing
estimate; for large-scale sweeps the ``sinter`` package is the production tool
and is listed as a dependency for that purpose.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .experiment import run_memory_experiment
from .types import ExperimentConfig, ThresholdPoint, ThresholdResult


def run_threshold_sweep(
    *,
    distances: Sequence[int],
    error_rates: Sequence[float],
    rounds: int | None = None,
    shots: int = 20_000,
    basis: str = "Z",
    rotated: bool = True,
    seed: int | None = None,
) -> ThresholdResult:
    """Sweep ``distances`` x ``error_rates`` and return logical error rates.

    When ``rounds`` is ``None`` we set ``rounds = distance`` for each distance,
    matching the common convention of running ``d`` rounds for a distance-``d``
    memory experiment.
    """
    if not distances:
        raise ValueError("distances must be non-empty")
    if not error_rates:
        raise ValueError("error_rates must be non-empty")

    points: list[ThresholdPoint] = []
    for distance in distances:
        for p in error_rates:
            config = ExperimentConfig(
                distance=distance,
                rounds=rounds if rounds is not None else distance,
                p=p,
                shots=shots,
                basis=basis,  # type: ignore[arg-type]
                rotated=rotated,
                seed=seed,
            )
            result = run_memory_experiment(config)
            points.append(
                ThresholdPoint(
                    distance=distance,
                    p=p,
                    logical_error_rate=result.logical_error_rate,
                    ci_low=result.ci_low,
                    ci_high=result.ci_high,
                    num_shots=result.num_shots,
                    num_failures=result.num_failures,
                )
            )

    return ThresholdResult(points=points, threshold_estimate=estimate_threshold(points))


def estimate_threshold(points: Sequence[ThresholdPoint]) -> float | None:
    """Estimate ``p_th`` as the error rate where adjacent-distance curves cross.

    This is a deliberately simple estimator: for each pair of neighbouring
    distances we find where their logical-error-rate-vs-p curves intersect by
    linear interpolation, then average the crossings. A rigorous estimate would
    fit the finite-size scaling ansatz; that refinement lives in the paper
    reproduction repository.
    """
    by_distance: dict[int, list[ThresholdPoint]] = {}
    for point in points:
        by_distance.setdefault(point.distance, []).append(point)
    distances = sorted(by_distance)
    if len(distances) < 2:
        return None

    crossings: list[float] = []
    for d_low, d_high in zip(distances, distances[1:]):
        low = sorted(by_distance[d_low], key=lambda pt: pt.p)
        high = sorted(by_distance[d_high], key=lambda pt: pt.p)
        ps = sorted({pt.p for pt in low} & {pt.p for pt in high})
        if len(ps) < 2:
            continue
        low_map = {pt.p: pt.logical_error_rate for pt in low}
        high_map = {pt.p: pt.logical_error_rate for pt in high}
        diff = np.array([high_map[p] - low_map[p] for p in ps])
        for i in range(len(ps) - 1):
            if diff[i] == 0.0:
                crossings.append(ps[i])
            elif diff[i] * diff[i + 1] < 0.0:
                frac = diff[i] / (diff[i] - diff[i + 1])
                crossings.append(ps[i] + frac * (ps[i + 1] - ps[i]))

    return float(np.mean(crossings)) if crossings else None

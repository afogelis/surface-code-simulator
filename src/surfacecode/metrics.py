"""Statistical estimators for logical error rates.

Logical error rates are Bernoulli proportions, so we report Wilson score
intervals rather than naive normal-approximation intervals: the Wilson
interval is well behaved when the number of observed failures is small, which
is exactly the regime of interest below threshold.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class LerEstimate:
    """A logical error-rate point estimate with a confidence interval."""

    logical_error_rate: float
    ci_low: float
    ci_high: float
    num_shots: int
    num_failures: int


def wilson_interval(num_failures: int, num_shots: int, *, confidence: float = 0.95) -> LerEstimate:
    """Return the Wilson score interval for a Bernoulli proportion.

    Guard clauses handle the degenerate ``num_shots == 0`` case up front so the
    happy path stays linear.
    """
    if num_shots < 0 or num_failures < 0:
        raise ValueError("counts must be non-negative")
    if num_failures > num_shots:
        raise ValueError("num_failures cannot exceed num_shots")
    if num_shots == 0:
        return LerEstimate(float("nan"), float("nan"), float("nan"), 0, 0)

    z = float(norm.ppf(1.0 - (1.0 - confidence) / 2.0))
    p_hat = num_failures / num_shots
    denom = 1.0 + z**2 / num_shots
    center = (p_hat + z**2 / (2 * num_shots)) / denom
    half = (z / denom) * np.sqrt(p_hat * (1 - p_hat) / num_shots + z**2 / (4 * num_shots**2))
    return LerEstimate(
        logical_error_rate=p_hat,
        ci_low=max(0.0, center - half),
        ci_high=min(1.0, center + half),
        num_shots=num_shots,
        num_failures=num_failures,
    )


def per_round_error_rate(logical_error_rate: float, rounds: int) -> float:
    """Convert a per-shot logical error probability into a per-round rate.

    Uses the standard relation ``epsilon = (1 - (1 - 2 p_L)^(1/rounds)) / 2``,
    which inverts the accumulation of independent per-round flips over a memory
    experiment of ``rounds`` cycles.
    """
    if rounds < 1:
        raise ValueError("rounds must be >= 1")
    p_l = min(max(logical_error_rate, 0.0), 0.5)
    return 0.5 * (1.0 - (1.0 - 2.0 * p_l) ** (1.0 / rounds))

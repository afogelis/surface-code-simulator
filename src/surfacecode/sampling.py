"""Syndrome and observable sampling helpers.

These functions isolate the ``stim`` sampling API behind small, typed helpers
so that downstream code (decoders, dashboards, ML feature builders) never has
to touch the simulator directly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import stim


@dataclass(frozen=True)
class SyndromeSample:
    """A batch of sampled detection events and the true logical observable flips.

    Attributes
    ----------
    detection_events:
        Boolean array of shape ``(shots, num_detectors)``. Each column is a
        detector (a parity check whose value changed unexpectedly).
    observable_flips:
        Boolean array of shape ``(shots, num_observables)`` giving the true
        logical flips. A decoder is judged correct when its prediction matches
        this array.
    """

    detection_events: np.ndarray
    observable_flips: np.ndarray

    @property
    def num_shots(self) -> int:
        return int(self.detection_events.shape[0])

    @property
    def num_detectors(self) -> int:
        return int(self.detection_events.shape[1])

    @property
    def num_observables(self) -> int:
        return int(self.observable_flips.shape[1])


def sample_syndromes(
    circuit: stim.Circuit, *, shots: int, seed: int | None = None
) -> SyndromeSample:
    """Sample ``shots`` detector/observable batches from ``circuit``.

    Parameters
    ----------
    circuit:
        A ``stim`` circuit containing ``DETECTOR`` and ``OBSERVABLE_INCLUDE``
        annotations (as produced by :mod:`surfacecode.circuits`).
    shots:
        Number of Monte Carlo shots to draw.
    seed:
        Optional seed forwarded to ``stim`` for reproducible sampling.
    """
    if shots < 1:
        raise ValueError("shots must be >= 1")

    sampler = circuit.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(shots, separate_observables=True)
    return SyndromeSample(
        detection_events=np.asarray(detection_events, dtype=bool),
        observable_flips=np.asarray(observable_flips, dtype=bool),
    )


def syndrome_density(sample: SyndromeSample) -> np.ndarray:
    """Return the per-detector firing frequency across all shots."""
    if sample.num_shots == 0:
        return np.zeros(sample.num_detectors, dtype=float)
    return sample.detection_events.mean(axis=0)

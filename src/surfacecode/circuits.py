"""Surface-code circuit builders built on top of ``stim``.

We deliberately wrap :func:`stim.Circuit.generated` rather than hand-rolling
the stabilizer layout. The generated circuits are the de-facto reference used
across the QEC community and keep the noise model well defined, which matters
when comparing against published thresholds.
"""

from __future__ import annotations

import stim

from .types import ExperimentConfig


def build_surface_code_circuit(config: ExperimentConfig) -> stim.Circuit:
    """Return a noisy surface-code memory circuit for ``config``.

    The depolarizing rate ``config.p`` is mapped onto every circuit-level noise
    channel exposed by ``stim`` (data depolarization, measurement flips, reset
    and idle errors) so that a single knob controls the physical error rate.
    """
    return stim.Circuit.generated(
        config.code_task(),
        distance=config.distance,
        rounds=config.rounds,
        after_clifford_depolarization=config.p,
        after_reset_flip_probability=config.p,
        before_measure_flip_probability=config.p,
        before_round_data_depolarization=config.p,
    )


def build_repetition_code_circuit(*, distance: int, rounds: int, p: float) -> stim.Circuit:
    """Return a noisy repetition-code circuit, used as a decoder sanity check.

    The repetition code is a 1D code with a well-understood threshold and is a
    fast smoke test that the sampling and decoding pipeline behaves correctly
    before moving on to the full 2D surface code.
    """
    if distance < 2:
        raise ValueError("repetition-code distance must be >= 2")
    if rounds < 1:
        raise ValueError("rounds must be >= 1")
    return stim.Circuit.generated(
        "repetition_code:memory",
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=p,
        after_reset_flip_probability=p,
        before_measure_flip_probability=p,
        before_round_data_depolarization=p,
    )

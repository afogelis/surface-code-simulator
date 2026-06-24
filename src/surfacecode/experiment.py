"""Top-level memory-experiment driver (the RORO entry point)."""

from __future__ import annotations

from .circuits import build_surface_code_circuit
from .decoding import count_logical_failures
from .metrics import per_round_error_rate, wilson_interval
from .sampling import sample_syndromes
from .types import ExperimentConfig, ExperimentResult


def run_memory_experiment(config: ExperimentConfig) -> ExperimentResult:
    """Run one surface-code memory experiment end to end.

    Pipeline: build a noisy circuit, sample syndromes, decode with MWPM, and
    summarise the logical failure rate with a Wilson interval and a per-round
    rate. Returns a fully populated :class:`ExperimentResult`.
    """
    circuit = build_surface_code_circuit(config)
    sample = sample_syndromes(circuit, shots=config.shots, seed=config.seed)
    num_failures = count_logical_failures(circuit, sample)

    estimate = wilson_interval(num_failures, config.shots)
    return ExperimentResult(
        config=config,
        num_shots=config.shots,
        num_failures=num_failures,
        logical_error_rate=estimate.logical_error_rate,
        ci_low=estimate.ci_low,
        ci_high=estimate.ci_high,
        per_round_error_rate=per_round_error_rate(estimate.logical_error_rate, config.rounds),
        num_detectors=sample.num_detectors,
        num_observables=sample.num_observables,
    )

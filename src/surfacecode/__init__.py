"""Circuit-level surface-code Monte Carlo simulation and threshold analysis."""

from .circuits import build_repetition_code_circuit, build_surface_code_circuit
from .decoding import count_logical_failures, matching_from_circuit
from .experiment import run_memory_experiment
from .metrics import LerEstimate, per_round_error_rate, wilson_interval
from .sampling import SyndromeSample, sample_syndromes, syndrome_density
from .threshold import estimate_threshold, run_threshold_sweep
from .types import (
    ExperimentConfig,
    ExperimentResult,
    ThresholdPoint,
    ThresholdResult,
)

__version__ = "0.1.0"

__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "LerEstimate",
    "SyndromeSample",
    "ThresholdPoint",
    "ThresholdResult",
    "build_repetition_code_circuit",
    "build_surface_code_circuit",
    "count_logical_failures",
    "estimate_threshold",
    "matching_from_circuit",
    "per_round_error_rate",
    "run_memory_experiment",
    "run_threshold_sweep",
    "sample_syndromes",
    "syndrome_density",
    "wilson_interval",
]

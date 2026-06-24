"""End-to-end pipeline tests.

These exercise the real stim/pymatching stack on small circuits, so they
double as integration tests for the whole simulate -> sample -> decode loop.
"""

import numpy as np

from surfacecode.circuits import build_repetition_code_circuit, build_surface_code_circuit
from surfacecode.decoding import count_logical_failures
from surfacecode.experiment import run_memory_experiment
from surfacecode.sampling import sample_syndromes
from surfacecode.threshold import run_threshold_sweep
from surfacecode.types import ExperimentConfig


def test_surface_code_circuit_has_detectors_and_observable():
    config = ExperimentConfig(distance=3, rounds=3, p=0.001, shots=10, seed=1)
    circuit = build_surface_code_circuit(config)
    assert circuit.num_detectors > 0
    assert circuit.num_observables == 1


def test_sampling_shapes_match_circuit():
    config = ExperimentConfig(distance=3, rounds=3, p=0.01, shots=128, seed=2)
    circuit = build_surface_code_circuit(config)
    sample = sample_syndromes(circuit, shots=config.shots, seed=config.seed)
    assert sample.detection_events.shape == (128, circuit.num_detectors)
    assert sample.observable_flips.shape == (128, 1)
    assert sample.detection_events.dtype == bool


def test_noiseless_circuit_has_no_logical_failures():
    config = ExperimentConfig(distance=3, rounds=3, p=0.0, shots=256, seed=3)
    circuit = build_surface_code_circuit(config)
    sample = sample_syndromes(circuit, shots=config.shots, seed=config.seed)
    assert count_logical_failures(circuit, sample) == 0


def test_memory_experiment_returns_consistent_result():
    config = ExperimentConfig(distance=3, rounds=3, p=0.01, shots=2000, seed=7)
    result = run_memory_experiment(config)
    assert 0 <= result.num_failures <= result.num_shots
    assert 0.0 <= result.logical_error_rate <= 1.0
    assert result.num_observables == 1


def test_larger_distance_helps_below_threshold():
    # Deep below threshold, distance 5 should not be worse than distance 3.
    sweep = run_threshold_sweep(distances=[3, 5], error_rates=[0.003], shots=20000, seed=11)
    by_distance = {pt.distance: pt.logical_error_rate for pt in sweep.points}
    assert by_distance[5] <= by_distance[3] + 0.01


def test_repetition_code_smoke():
    circuit = build_repetition_code_circuit(distance=5, rounds=5, p=0.05)
    sample = sample_syndromes(circuit, shots=500, seed=5)
    failures = count_logical_failures(circuit, sample)
    assert 0 <= failures <= 500
    assert np.any(sample.detection_events)

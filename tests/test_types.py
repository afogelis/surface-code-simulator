import pytest
from pydantic import ValidationError

from surfacecode.types import ExperimentConfig


def test_code_task_string_matches_layout_and_basis():
    config = ExperimentConfig(distance=5, rounds=5, p=0.001, shots=100, basis="X", rotated=True)
    assert config.code_task() == "surface_code:rotated_memory_x"

    unrotated = ExperimentConfig(distance=3, rounds=3, p=0.001, shots=100, basis="Z", rotated=False)
    assert unrotated.code_task() == "surface_code:unrotated_memory_z"


def test_even_distance_is_rejected():
    with pytest.raises(ValidationError):
        ExperimentConfig(distance=4, rounds=4, p=0.001, shots=100)


def test_error_rate_bounds_are_enforced():
    with pytest.raises(ValidationError):
        ExperimentConfig(distance=3, rounds=3, p=0.9, shots=100)

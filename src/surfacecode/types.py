"""Typed configuration and result models for surface-code experiments.

All public functions follow the Receive-an-Object / Return-an-Object (RORO)
pattern: callers pass an :class:`ExperimentConfig` and receive an
:class:`ExperimentResult`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Basis = Literal["X", "Z"]
CodeTask = Literal[
    "surface_code:rotated_memory_x",
    "surface_code:rotated_memory_z",
    "surface_code:unrotated_memory_x",
    "surface_code:unrotated_memory_z",
    "repetition_code:memory",
]


class ExperimentConfig(BaseModel):
    """Inputs for a single memory experiment.

    The depolarizing rate ``p`` is applied uniformly as the circuit-level noise
    strength understood by ``stim``'s generated circuits (gate, reset,
    measurement and idle error all scale with ``p``).
    """

    model_config = {"frozen": True}

    distance: int = Field(..., ge=2, description="Code distance (odd >= 3 for surface codes).")
    rounds: int = Field(..., ge=1, description="Number of measurement rounds.")
    p: float = Field(..., ge=0.0, le=0.5, description="Physical depolarizing error rate.")
    shots: int = Field(..., ge=1, description="Number of Monte Carlo shots.")
    basis: Basis = Field(default="Z", description="Logical observable basis.")
    rotated: bool = Field(default=True, description="Use the rotated surface code layout.")
    seed: int | None = Field(default=None, description="Optional RNG seed for reproducibility.")

    @field_validator("distance")
    @classmethod
    def _odd_distance(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError("surface-code distance must be odd")
        return value

    def code_task(self) -> CodeTask:
        layout = "rotated" if self.rotated else "unrotated"
        return f"surface_code:{layout}_memory_{self.basis.lower()}"  # type: ignore[return-value]


class ExperimentResult(BaseModel):
    """Outputs from a single memory experiment."""

    model_config = {"frozen": True}

    config: ExperimentConfig
    num_shots: int
    num_failures: int
    logical_error_rate: float = Field(..., description="Per-shot logical error probability.")
    ci_low: float = Field(..., description="Lower bound of the Wilson 95% interval.")
    ci_high: float = Field(..., description="Upper bound of the Wilson 95% interval.")
    per_round_error_rate: float = Field(
        ..., description="Logical error per round, derived from the per-shot rate."
    )
    num_detectors: int
    num_observables: int


class ThresholdPoint(BaseModel):
    """A single (distance, p) measurement in a threshold sweep."""

    model_config = {"frozen": True}

    distance: int
    p: float
    logical_error_rate: float
    ci_low: float
    ci_high: float
    num_shots: int
    num_failures: int


class ThresholdResult(BaseModel):
    """Collection of :class:`ThresholdPoint` measurements plus a threshold estimate."""

    points: list[ThresholdPoint]
    threshold_estimate: float | None = Field(
        default=None, description="Crude crossing estimate of the physical threshold p_th."
    )

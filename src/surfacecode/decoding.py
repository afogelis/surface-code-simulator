"""Minimal MWPM decoding used to score logical failures.

The full decoder zoo (union-find, belief propagation, ML) lives in the
``decoder-benchmark`` repository. Here we only need a reference decoder to turn
sampled syndromes into a logical error rate, so we use PyMatching's
minimum-weight perfect matching decoder built directly from the circuit's
detector error model.
"""

from __future__ import annotations

import numpy as np
import pymatching
import stim

from .sampling import SyndromeSample


def matching_from_circuit(circuit: stim.Circuit) -> pymatching.Matching:
    """Build a PyMatching MWPM decoder from a circuit's detector error model."""
    dem = circuit.detector_error_model(decompose_errors=True)
    return pymatching.Matching.from_detector_error_model(dem)


def count_logical_failures(circuit: stim.Circuit, sample: SyndromeSample) -> int:
    """Decode ``sample`` with MWPM and count shots whose observable was mispredicted."""
    matcher = matching_from_circuit(circuit)
    predictions = matcher.decode_batch(sample.detection_events)
    predictions = np.asarray(predictions, dtype=bool)
    mismatches = np.any(predictions != sample.observable_flips, axis=1)
    return int(np.count_nonzero(mismatches))

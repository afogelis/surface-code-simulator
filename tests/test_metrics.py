import math

import pytest

from surfacecode.metrics import per_round_error_rate, wilson_interval


def test_wilson_interval_brackets_point_estimate():
    est = wilson_interval(50, 1000)
    assert est.logical_error_rate == pytest.approx(0.05)
    assert est.ci_low < est.logical_error_rate < est.ci_high
    assert 0.0 <= est.ci_low <= est.ci_high <= 1.0


def test_wilson_interval_zero_failures_has_zero_lower_bound():
    est = wilson_interval(0, 500)
    assert est.logical_error_rate == 0.0
    assert est.ci_low == pytest.approx(0.0, abs=1e-12)
    assert est.ci_high > 0.0


def test_wilson_interval_zero_shots_is_nan():
    est = wilson_interval(0, 0)
    assert math.isnan(est.logical_error_rate)


def test_wilson_interval_rejects_impossible_counts():
    with pytest.raises(ValueError):
        wilson_interval(10, 5)


def test_per_round_rate_is_smaller_than_per_shot_rate():
    per_shot = 0.1
    rounds = 5
    per_round = per_round_error_rate(per_shot, rounds)
    assert 0.0 < per_round < per_shot


def test_per_round_rate_single_round_matches_per_shot():
    assert per_round_error_rate(0.2, 1) == pytest.approx(0.2)

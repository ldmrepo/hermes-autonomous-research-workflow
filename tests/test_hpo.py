"""Tests for pipelines.hpo — Optuna study wrapper."""

from pathlib import Path

import pytest

from pipelines.hpo import run_hpo_study


def _quadratic_objective(trial):
    """f(x) = (x - 3)^2, optimum at x=3 (value=0). Used to verify HPO 진동."""
    x = trial.suggest_float("x", -10.0, 10.0)
    return (x - 3.0) ** 2


class TestRunHpoStudy:
    def test_returns_required_keys(self, tmp_path):
        result = run_hpo_study(
            objective=_quadratic_objective,
            n_trials=5,
            study_name="test_returns_keys",
            storage=f"sqlite:///{tmp_path / 'optuna.db'}",
            sampler_seed=42,
        )
        assert "best_params" in result
        assert "best_value" in result
        assert "n_trials_completed" in result
        assert "study_name" in result
        assert result["n_trials_completed"] == 5
        assert result["study_name"] == "test_returns_keys"

    def test_deterministic_with_same_seed(self, tmp_path):
        r1 = run_hpo_study(
            objective=_quadratic_objective,
            n_trials=5,
            study_name="det_1",
            storage=f"sqlite:///{tmp_path / 'a.db'}",
            sampler_seed=42,
        )
        r2 = run_hpo_study(
            objective=_quadratic_objective,
            n_trials=5,
            study_name="det_2",
            storage=f"sqlite:///{tmp_path / 'b.db'}",
            sampler_seed=42,
        )
        # Same seed + same objective → same trajectory
        assert r1["best_value"] == r2["best_value"]
        assert r1["best_params"] == r2["best_params"]

    def test_study_resume_accumulates_trials(self, tmp_path):
        storage = f"sqlite:///{tmp_path / 'resume.db'}"
        r1 = run_hpo_study(
            objective=_quadratic_objective,
            n_trials=3,
            study_name="resume_test",
            storage=storage,
            sampler_seed=42,
        )
        assert r1["n_trials_completed"] == 3

        # Resume same study, expect 6 cumulative trials
        r2 = run_hpo_study(
            objective=_quadratic_objective,
            n_trials=3,
            study_name="resume_test",
            storage=storage,
            sampler_seed=42,
        )
        assert r2["n_trials_completed"] == 6

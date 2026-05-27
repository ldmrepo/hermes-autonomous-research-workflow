"""Optuna study wrapper with MLflow nested run integration.

Reusable across M4 (LightGBM) and M5 (KLUE-RoBERTa) hyperparameter search.
"""

from __future__ import annotations

from typing import Any, Callable

import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler


def run_hpo_study(
    objective: Callable[[optuna.Trial], float],
    n_trials: int,
    study_name: str,
    storage: str,
    sampler_seed: int = 42,
    direction: str = "minimize",
) -> dict[str, Any]:
    """Create or resume an Optuna study and run n_trials trials.

    Returns dict with: best_params, best_value, n_trials_completed, study_name.
    """
    sampler = TPESampler(seed=sampler_seed)
    pruner = MedianPruner(n_startup_trials=5)

    study = optuna.create_study(
        study_name=study_name,
        storage=storage,
        sampler=sampler,
        pruner=pruner,
        direction=direction,
        load_if_exists=True,
    )

    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    return {
        "best_params": dict(study.best_params),
        "best_value": float(study.best_value),
        "n_trials_completed": len(study.trials),
        "study_name": study_name,
    }

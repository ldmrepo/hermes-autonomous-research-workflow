"""Tests for pipelines.train CLI extensions (--model, --hpo-trials, --cycle-id str, M5/M6 dispatch)."""

import pytest

from pipelines.train import MODEL_SPECS, parse_args


class TestCliArgs:
    def test_accepts_model_arg(self, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["train.py", "--models", "M5", "--model", "klue/roberta-small", "--cycle-id", "M1"],
        )
        args = parse_args()
        assert args.model == "klue/roberta-small"

    def test_accepts_hpo_trials_arg(self, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["train.py", "--models", "M5", "--hpo-trials", "30", "--cycle-id", "M1"],
        )
        args = parse_args()
        assert args.hpo_trials == 30

    def test_cycle_id_accepts_string(self, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["train.py", "--models", "M5", "--cycle-id", "M2"],
        )
        args = parse_args()
        assert args.cycle_id == "M2"


class TestModelSpecs:
    def test_m5_klue_roberta_in_specs(self):
        assert "M5" in MODEL_SPECS
        spec = MODEL_SPECS["M5"]
        assert spec["model_type"] == "KLUE-RoBERTa"
        assert spec["feature_set"] == "raw_text"
        assert "assumption" in spec

    def test_m6_ensemble_in_specs(self):
        assert "M6" in MODEL_SPECS
        spec = MODEL_SPECS["M6"]
        assert spec["model_type"] == "RidgeStackingEnsemble"
        assert "M4" in spec["depends_on"]
        assert "M5" in spec["depends_on"]

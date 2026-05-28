"""Phase 3 M5 multi-task transformer tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipelines.train_transformer import (
    PHASE3_LOSS_FORMULA,
    PHASE3_TARGET_COLUMNS,
    PHASE3_WEIGHT_COLUMNS,
    train_transformer,
    weighted_multitask_mse_loss,
)


def _phase3_df(n: int = 12) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    data = {
        "text": [f"sample essay text {idx}" for idx in range(n)],
        "target_exp": rng.uniform(0.0, 3.0, size=n),
        "target_org": rng.uniform(0.0, 3.0, size=n),
        "target_cont": rng.uniform(0.0, 3.0, size=n),
        "target_overall_norm": rng.uniform(0.0, 3.0, size=n),
        "w_exp": np.full(n, 3.0),
        "w_org": np.full(n, 3.0),
        "w_cont": np.full(n, 4.0),
        "w_overall": np.full(n, 0.5),
    }
    return pd.DataFrame(data)


def _tiny_multitask_model_init():
    from transformers import AutoTokenizer, RobertaConfig, RobertaForSequenceClassification

    tok = AutoTokenizer.from_pretrained("klue/bert-base")
    config = RobertaConfig(
        vocab_size=tok.vocab_size,
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=64,
        pad_token_id=tok.pad_token_id,
        type_vocab_size=2,
        num_labels=4,
        problem_type="regression",
    )
    return RobertaForSequenceClassification(config)


def test_weighted_multitask_loss_matches_phase3_contract():
    import torch

    preds = torch.tensor([[1.0, 2.0, 3.0, 1.5], [0.5, 1.0, 2.5, 3.0]])
    labels = torch.tensor([[0.0, 2.0, 1.0, 1.0], [1.5, 1.0, 2.0, 2.0]])
    weights = torch.tensor([[3.0, 3.0, 4.0, 0.5], [3.0, 3.0, 4.0, 0.5]])

    actual = weighted_multitask_mse_loss(preds, labels, weights)
    expected = ((preds - labels) ** 2 * weights).sum(dim=1).mean()

    assert PHASE3_LOSS_FORMULA == "((preds - labels) ** 2 * macro_weights).sum(dim=1).mean()"
    assert actual.item() == pytest.approx(expected.item())


def test_phase3_rejects_scalar_score_path_before_training(tmp_path):
    df = pd.DataFrame({"text": ["a", "b", "c", "d"], "score": [1.0, 2.0, 3.0, 4.0]})

    with pytest.raises(ValueError, match="scalar score/essay_scoreT_avg is forbidden"):
        train_transformer(
            train_df=df.iloc[:2],
            valid_df=df.iloc[2:],
            hparams={"num_train_epochs": 1},
            output_dir=str(tmp_path / "blocked"),
            phase=3,
        )


def test_multitask_smoke_returns_four_dimensional_predictions(tmp_path):
    df = _phase3_df()

    result = train_transformer(
        train_df=df.iloc[:8],
        valid_df=df.iloc[8:],
        hparams={
            "learning_rate": 1e-4,
            "per_device_train_batch_size": 2,
            "num_train_epochs": 1,
            "weight_decay": 0.01,
            "warmup_ratio": 0.0,
        },
        model_name=None,
        model_init=_tiny_multitask_model_init,
        tokenizer_name="klue/bert-base",
        output_dir=str(tmp_path / "tf_multitask"),
        max_length=32,
        text_col="text",
        label_cols=PHASE3_TARGET_COLUMNS,
        macro_weight_cols=PHASE3_WEIGHT_COLUMNS,
        phase=3,
        save_model=False,
    )

    assert result["task_type"] == "phase3_multitask"
    assert result["num_labels"] == 4
    assert result["valid_predictions"].shape == (4, 4)
    assert result["target_columns"] == list(PHASE3_TARGET_COLUMNS)
    assert result["macro_weight_columns"] == list(PHASE3_WEIGHT_COLUMNS)
    assert result["model_path"] is None

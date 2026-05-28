"""KLUE-RoBERTa fine-tune helper (M5).

Built on HuggingFace Trainer for stability. The function accepts either a
pretrained `model_name` (HF Hub or local cache) or a `model_init` callable
(for synthetic tiny-model unit tests).

Phase 3 M5 uses a four-output multi-task regression head:
`[exp, org, cont, overall_norm]`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional, Sequence

import numpy as np


PHASE3_TARGET_COLUMNS = (
    "target_exp",
    "target_org",
    "target_cont",
    "target_overall_norm",
)
PHASE3_WEIGHT_COLUMNS = ("w_exp", "w_org", "w_cont", "w_overall")
PHASE3_OUTPUT_NAMES = ("exp", "org", "cont", "overall_norm")
W_OVERALL_DEFAULT = 0.5
PHASE3_LOSS_FORMULA = "((preds - labels) ** 2 * macro_weights).sum(dim=1).mean()"


def is_phase3(phase: Any) -> bool:
    if phase is None:
        return False
    return str(phase).strip().lower() in {"3", "phase3", "phase_3", "mid_multitask"}


def weighted_multitask_mse_loss(preds, labels, macro_weights):
    """Phase 3 weighted MSE: row-wise weighted sum, then batch mean."""
    return ((preds - labels) ** 2 * macro_weights).sum(dim=1).mean()


def _as_float_matrix(df, columns: Sequence[str], df_name: str) -> np.ndarray:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(
            f"{df_name} missing required Phase 3 columns {missing}. "
            "Phase 3 M5 requires labels shape (N,4) and macro_weights shape (N,4); "
            "scalar score/essay_scoreT_avg is forbidden."
        )
    arr = df.loc[:, list(columns)].to_numpy(dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != len(columns):
        raise ValueError(
            f"{df_name} columns {list(columns)} produced shape {arr.shape}, "
            f"expected (N,{len(columns)})."
        )
    if not np.isfinite(arr).all():
        raise ValueError(f"{df_name} columns {list(columns)} contain non-finite values")
    return arr


def _validate_macro_weights(weights: np.ndarray, df_name: str) -> None:
    if np.any(weights < 0):
        raise ValueError(f"{df_name} macro_weights contain negative values")
    if np.any(weights.sum(axis=1) <= 0):
        raise ValueError(f"{df_name} macro_weights contain zero-sum rows")


def _validate_phase3_frames(
    train_df,
    valid_df,
    label_cols: Sequence[str],
    macro_weight_cols: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train_labels = _as_float_matrix(train_df, label_cols, "train_df")
    valid_labels = _as_float_matrix(valid_df, label_cols, "valid_df")
    train_weights = _as_float_matrix(train_df, macro_weight_cols, "train_df")
    valid_weights = _as_float_matrix(valid_df, macro_weight_cols, "valid_df")
    _validate_macro_weights(train_weights, "train_df")
    _validate_macro_weights(valid_weights, "valid_df")
    return train_labels, valid_labels, train_weights, valid_weights


def _as_scalar_labels(df, label_col: str, df_name: str) -> np.ndarray:
    if label_col not in df.columns:
        raise ValueError(f"{df_name} missing scalar label column '{label_col}'")
    labels = df[label_col].to_numpy(dtype=np.float32)
    if not np.isfinite(labels).all():
        raise ValueError(f"{df_name}.{label_col} contains non-finite values")
    return labels


def _prediction_array(raw_predictions: Any, expected_dim: int) -> np.ndarray:
    if isinstance(raw_predictions, tuple):
        raw_predictions = raw_predictions[0]
    arr = np.asarray(raw_predictions, dtype=float)
    if expected_dim == 1:
        return arr.reshape(-1)
    return arr.reshape((-1, expected_dim))


def _weighted_loss_np(
    predictions: np.ndarray, labels: np.ndarray, macro_weights: np.ndarray
) -> float:
    return float(np.mean(np.sum((predictions - labels) ** 2 * macro_weights, axis=1)))


def _per_target_metrics(labels: np.ndarray, predictions: np.ndarray) -> dict[str, dict[str, float]]:
    metrics: dict[str, dict[str, float]] = {}
    for idx, name in enumerate(PHASE3_OUTPUT_NAMES):
        diff = predictions[:, idx] - labels[:, idx]
        metrics[name] = {
            "mae": float(np.mean(np.abs(diff))),
            "rmse": float(np.sqrt(np.mean(diff ** 2))),
            "mse": float(np.mean(diff ** 2)),
        }
    return metrics


def train_transformer(
    train_df,
    valid_df,
    hparams: dict[str, Any],
    output_dir: str,
    text_col: str = "text",
    label_col: str = "score",
    label_cols: Optional[Sequence[str]] = None,
    macro_weight_cols: Optional[Sequence[str]] = None,
    phase: Any = None,
    model_name: Optional[str] = None,
    model_init: Optional[Callable] = None,
    tokenizer_name: Optional[str] = None,
    max_length: int = 256,
    seed: int = 42,
    save_model: bool = True,
    rubric_json_col: Optional[str] = None,
) -> dict[str, Any]:
    """Fine-tune a transformer regression model.

    Scalar mode remains available for archived Phase 2 use. When `phase=3` or
    multi-task target columns are supplied, the function requires labels and
    macro weights shaped `(N,4)` and uses the Phase 3 weighted loss.

    Phase 3 multi-task wire-up (P3-W3): `rubric_json_col`이 지정되고 dataframe에 해당 컬럼이
    있으면 학습 진입 직전 `validate_rubric_for_phase3` 사전 검증. drift essay 발견 시 `RuntimeError`.
    Phase 2 호환을 위해 기본은 비활성 (rubric_json_col=None).
    """
    label_cols = tuple(label_cols or ())
    macro_weight_cols = tuple(macro_weight_cols or ())
    multitask = bool(label_cols or macro_weight_cols or is_phase3(phase))
    if is_phase3(phase):
        label_cols = label_cols or PHASE3_TARGET_COLUMNS
        macro_weight_cols = macro_weight_cols or PHASE3_WEIGHT_COLUMNS
    if multitask and not label_cols:
        label_cols = PHASE3_TARGET_COLUMNS
    if multitask and not macro_weight_cols:
        macro_weight_cols = PHASE3_WEIGHT_COLUMNS

    if multitask:
        (
            train_label_matrix,
            valid_label_matrix,
            train_weight_matrix,
            valid_weight_matrix,
        ) = _validate_phase3_frames(train_df, valid_df, label_cols, macro_weight_cols)
        num_labels = len(label_cols)
        if num_labels != 4:
            raise ValueError(f"Phase 3 M5 expects exactly 4 labels, got {num_labels}")
    else:
        train_label_vector = _as_scalar_labels(train_df, label_col, "train_df")
        valid_label_vector = _as_scalar_labels(valid_df, label_col, "valid_df")
        num_labels = 1

    # P3-W3 fix (R1-NNF1 + R1-REG-H1 운영 보강): Phase 3 학습 직전 사전 검증
    if rubric_json_col is not None:
        from pipelines.extract_5k import validate_rubric_for_phase3
        for df_name, df in (("train_df", train_df), ("valid_df", valid_df)):
            if rubric_json_col not in df.columns:
                raise ValueError(
                    f"train_transformer: rubric_json_col='{rubric_json_col}' not in {df_name}. "
                    "Phase 3 multi-task 학습 시 rubric JSON dict 컬럼 필수."
                )
            drift = []
            for idx, rubric_doc in enumerate(df[rubric_json_col]):
                ok, reason = validate_rubric_for_phase3(rubric_doc)
                if not ok:
                    drift.append((idx, reason))
                    if len(drift) >= 3:
                        break
            if drift:
                drift_msg = "; ".join(f"row {i}: {r}" for i, r in drift[:3])
                raise RuntimeError(
                    f"train_transformer: rubric spec drift in {df_name} — {drift_msg}. "
                    "extract_5k --validate-rubric로 사전 skip 필수 (Hard Rule #15)."
                )
    import torch
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    if model_name is None and model_init is None:
        raise ValueError("Provide either model_name or model_init.")

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name or model_name)

    def _to_features(df):
        encs = tokenizer(
            df[text_col].tolist(),
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors=None,
        )
        if multitask:
            label_matrix = df.loc[:, list(label_cols)].to_numpy(dtype=np.float32)
            weight_matrix = df.loc[:, list(macro_weight_cols)].to_numpy(dtype=np.float32)
            encs["labels"] = label_matrix.tolist()
            encs["macro_weights"] = weight_matrix.tolist()
        else:
            encs["labels"] = [float(x) for x in df[label_col].tolist()]
        return encs

    class _DictDataset(torch.utils.data.Dataset):
        def __init__(self, encs):
            self.encs = encs
            self.n = len(encs["labels"])

        def __len__(self):
            return self.n

        def __getitem__(self, i):
            return {
                k: (
                    torch.tensor(v[i])
                    if k != "labels"
                    else torch.tensor(v[i], dtype=torch.float32)
                )
                for k, v in self.encs.items()
            }

    train_ds = _DictDataset(_to_features(train_df))
    valid_ds = _DictDataset(_to_features(valid_df))

    if model_init is None:
        def model_init():
            return AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=num_labels, problem_type="regression"
            )
    else:
        original_model_init = model_init

        def model_init():
            model = original_model_init()
            configured = getattr(getattr(model, "config", None), "num_labels", None)
            if multitask and configured != num_labels:
                raise ValueError(
                    f"Phase 3 M5 requires num_labels={num_labels}; "
                    f"model_init returned num_labels={configured}."
                )
            return model

    class WeightedMSEMultiTaskTrainer(Trainer):
        """Trainer with Phase 3 row-wise weighted multi-task MSE."""

        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            labels = inputs.pop("labels")
            macro_weights = inputs.pop("macro_weights")
            outputs = model(**inputs)
            logits = outputs.logits
            if logits.shape != labels.shape:
                raise ValueError(
                    f"Phase 3 logits shape {tuple(logits.shape)} must match "
                    f"labels shape {tuple(labels.shape)}"
                )
            if macro_weights.shape != labels.shape:
                raise ValueError(
                    f"Phase 3 macro_weights shape {tuple(macro_weights.shape)} must match "
                    f"labels shape {tuple(labels.shape)}"
                )
            loss = weighted_multitask_mse_loss(logits, labels, macro_weights)
            return (loss, outputs) if return_outputs else loss

    output_dir_p = Path(output_dir)
    output_dir_p.mkdir(parents=True, exist_ok=True)

    args = TrainingArguments(
        output_dir=str(output_dir_p),
        per_device_train_batch_size=int(hparams.get("per_device_train_batch_size", 16)),
        per_device_eval_batch_size=int(hparams.get("per_device_train_batch_size", 16)),
        learning_rate=float(hparams.get("learning_rate", 2e-5)),
        num_train_epochs=int(hparams.get("num_train_epochs", 3)),
        weight_decay=float(hparams.get("weight_decay", 0.01)),
        warmup_ratio=float(hparams.get("warmup_ratio", 0.0)),
        seed=seed,
        report_to=[],
        logging_steps=10,
        save_strategy="no",
        eval_strategy="no",
        disable_tqdm=True,
        remove_unused_columns=False,
    )

    trainer_cls = WeightedMSEMultiTaskTrainer if multitask else Trainer
    trainer = Trainer(
        model_init=model_init,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
    ) if not multitask else trainer_cls(
        model_init=model_init,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
    )
    trainer.train()

    # Predict on train/valid for the same train-vs-valid diagnostics used by
    # the CPU baselines.
    train_output = trainer.predict(train_ds)
    train_predictions = _prediction_array(train_output.predictions, num_labels)

    valid_output = trainer.predict(valid_ds)
    valid_predictions = _prediction_array(valid_output.predictions, num_labels)

    if multitask:
        train_labels = train_label_matrix
        valid_labels = valid_label_matrix
        train_loss = _weighted_loss_np(train_predictions, train_labels, train_weight_matrix)
        valid_loss = _weighted_loss_np(valid_predictions, valid_labels, valid_weight_matrix)
        train_mae = float(np.mean(np.abs(train_predictions - train_labels)))
        train_rmse = float(np.sqrt(np.mean((train_predictions - train_labels) ** 2)))
        valid_mae = float(np.mean(np.abs(valid_predictions - valid_labels)))
        valid_rmse = float(np.sqrt(np.mean((valid_predictions - valid_labels) ** 2)))
        train_per_target = _per_target_metrics(train_labels, train_predictions)
        valid_per_target = _per_target_metrics(valid_labels, valid_predictions)
    else:
        train_labels = train_label_vector
        valid_labels = valid_label_vector
        train_mae = float(mean_absolute_error(train_labels, train_predictions))
        train_rmse = float(np.sqrt(mean_squared_error(train_labels, train_predictions)))
        train_loss = float(np.mean((train_predictions - train_labels) ** 2))
        valid_mae = float(mean_absolute_error(valid_labels, valid_predictions))
        valid_rmse = float(np.sqrt(mean_squared_error(valid_labels, valid_predictions)))
        valid_loss = float(np.mean((valid_predictions - valid_labels) ** 2))
        train_per_target = None
        valid_per_target = None

    model_path = output_dir_p / "model"
    if save_model:
        trainer.save_model(str(model_path))

    result = {
        "train_loss": train_loss,
        "train_mae": train_mae,
        "train_rmse": train_rmse,
        "train_predictions": train_predictions,
        "valid_loss": valid_loss,
        "valid_mae": valid_mae,
        "valid_rmse": valid_rmse,
        "valid_predictions": valid_predictions,
        "model_path": str(model_path) if save_model else None,
        "hparams": hparams,
        "task_type": "phase3_multitask" if multitask else "scalar_regression",
        "num_labels": num_labels,
    }
    if multitask:
        result.update(
            {
                "target_columns": list(label_cols),
                "macro_weight_columns": list(macro_weight_cols),
                "output_names": list(PHASE3_OUTPUT_NAMES),
                "loss_formula": PHASE3_LOSS_FORMULA,
                "train_per_target": train_per_target,
                "valid_per_target": valid_per_target,
            }
        )
    return result

#!/usr/bin/env python3
"""Create leakage-checked location-grouped folds for the toy sample.

The split artifacts intentionally contain only essay identifiers and relative
paths. Raw essay text, target scores, rater scores, and label-side features are
not copied into fold JSON files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sklearn.model_selection import StratifiedGroupKFold


GROUP_KEY = "student.location"
STRATIFY_KEY = "essay_type__student_grade_group"
SEED = 42


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create k-fold splits grouped by student.location."
    )
    parser.add_argument("--input", default="dataset/sample", help="Sample dataset root.")
    parser.add_argument("--k", type=int, default=5, help="Number of folds.")
    parser.add_argument("--output", default="workspace/cycle_2/splits")
    parser.add_argument("--cycle-id", type=int, default=2)
    parser.add_argument("--kanban-task-id", default="t_68c5fd8a")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--audit-table",
        default=None,
        help=(
            "Existing audit table to reuse when present. Defaults to "
            "workspace/cycle_<cycle-id>/audit/audit_table_no_raw_text.csv."
        ),
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_payload(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def json_paths(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*.json"))
        if path.is_file()
    }


def build_split_table(input_root: Path) -> pd.DataFrame:
    source_root = input_root / "원천데이터"
    label_root = input_root / "라벨링데이터"
    source_paths = json_paths(source_root)
    label_paths = json_paths(label_root)
    rows: list[dict[str, Any]] = []

    for relative_path in sorted(set(source_paths) & set(label_paths)):
        source = load_json(source_paths[relative_path])
        label = load_json(label_paths[relative_path])
        essay_id_source = source.get("essay_id")
        essay_id_label = label.get("info", {}).get("essay_id")
        if essay_id_source != essay_id_label:
            raise ValueError(
                f"essay_id mismatch for {relative_path}: "
                f"source={essay_id_source} label={essay_id_label}"
            )
        student = label.get("student", {})
        rows.append(
            {
                "relative_path": relative_path,
                "essay_id_source": essay_id_source,
                "essay_id_label": essay_id_label,
                "essay_type": label.get("info", {}).get("essay_type")
                or label.get("rubric", {}).get("essay_type"),
                "student_grade_group": student.get("student_grade_group"),
                "student_location": student.get("location"),
            }
        )

    return pd.DataFrame(rows)


def load_split_table(args: argparse.Namespace) -> tuple[pd.DataFrame, str, str]:
    audit_table = Path(args.audit_table) if args.audit_table else Path(
        f"workspace/cycle_{args.cycle_id}/audit/audit_table_no_raw_text.csv"
    )
    if audit_table.exists():
        df = pd.read_csv(audit_table, dtype={"student_location": "string"})
        return df, str(audit_table), sha256_file(audit_table)

    df = build_split_table(Path(args.input))
    return df, "built_from_dataset_json", sha256_payload(df.to_dict(orient="records"))


def require_columns(df: pd.DataFrame) -> None:
    required = [
        "relative_path",
        "essay_id_source",
        "essay_id_label",
        "essay_type",
        "student_grade_group",
        "student_location",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"split input is missing required columns: {missing}")
    null_columns = [
        column
        for column in ["relative_path", "essay_id_source", "essay_type", "student_location"]
        if df[column].isna().any()
    ]
    if null_columns:
        raise ValueError(f"split input has null values in required columns: {null_columns}")


def item_rows(df: pd.DataFrame) -> list[dict[str, str]]:
    rows = df.sort_values("relative_path")
    return [
        {
            "essay_id": str(row["essay_id_source"]),
            "relative_path": str(row["relative_path"]),
        }
        for _, row in rows.iterrows()
    ]


def count_dict(series: pd.Series) -> dict[str, int]:
    counts = series.fillna("<MISSING>").astype(str).value_counts().sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def stratify_labels(df: pd.DataFrame) -> pd.Series:
    essay_type = df["essay_type"].fillna("<MISSING>").astype(str)
    grade_group = df["student_grade_group"].fillna("<MISSING>").astype(str)
    return essay_type + "|" + grade_group


def build_folds(df: pd.DataFrame, k: int, seed: int) -> list[dict[str, Any]]:
    groups = df["student_location"].fillna("<MISSING>").astype(str)
    labels = stratify_labels(df)
    splitter = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
    folds: list[dict[str, Any]] = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(df, labels, groups)):
        train_df = df.iloc[train_idx].copy()
        valid_df = df.iloc[valid_idx].copy()
        train_groups = sorted(train_df["student_location"].fillna("<MISSING>").astype(str).unique())
        valid_groups = sorted(valid_df["student_location"].fillna("<MISSING>").astype(str).unique())
        overlap = sorted(set(train_groups) & set(valid_groups))
        warnings = []
        if len(valid_df) < 30:
            warnings.append("valid_n < 30")
        if overlap:
            warnings.append("group overlap detected")

        folds.append(
            {
                "fold": fold,
                "train_df": train_df,
                "valid_df": valid_df,
                "train_groups": train_groups,
                "valid_groups": valid_groups,
                "group_overlap": overlap,
                "warnings": warnings,
            }
        )

    return folds


def fold_doc(args: argparse.Namespace, fold: dict[str, Any]) -> dict[str, Any]:
    return {
        "cycle_id": args.cycle_id,
        "kanban_task_id": args.kanban_task_id,
        "fold": int(fold["fold"]),
        "seed": int(args.seed),
        "split_method": "sklearn.model_selection.StratifiedGroupKFold",
        "k": int(args.k),
        "group_key": GROUP_KEY,
        "stratify_key": STRATIFY_KEY,
        "model_feature_policy": {
            "student_location": "split-only; exclude from model inputs",
            "raw_text": "not copied into split artifacts",
            "label_side_features": "not copied into split artifacts",
        },
        "train_n": int(len(fold["train_df"])),
        "valid_n": int(len(fold["valid_df"])),
        "train_groups": fold["train_groups"],
        "valid_groups": fold["valid_groups"],
        "group_overlap": fold["group_overlap"],
        "warnings": fold["warnings"],
        "train": item_rows(fold["train_df"]),
        "valid": item_rows(fold["valid_df"]),
    }


def write_folds(args: argparse.Namespace, output_dir: Path, folds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    docs = []
    for fold in folds:
        doc = fold_doc(args, fold)
        write_json(output_dir / f"fold_{fold['fold']}.json", doc)
        docs.append(doc)
    return docs


def manifest(
    args: argparse.Namespace,
    output_dir: Path,
    df: pd.DataFrame,
    source_audit_table: str,
    source_audit_table_sha: str,
    folds: list[dict[str, Any]],
    fold_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    config_payload = {
        "cycle_id": args.cycle_id,
        "kanban_task_id": args.kanban_task_id,
        "k": args.k,
        "seed": args.seed,
        "group_key": GROUP_KEY,
        "stratify_key": STRATIFY_KEY,
        "split_method": "StratifiedGroupKFold",
        "source_audit_table_sha256": source_audit_table_sha,
    }
    split_hash = sha256_payload(
        [
            {
                "fold": doc["fold"],
                "train": doc["train"],
                "valid": doc["valid"],
                "valid_groups": doc["valid_groups"],
            }
            for doc in fold_docs
        ]
    )

    fold_summaries = []
    for fold in folds:
        valid_df = fold["valid_df"]
        fold_summaries.append(
            {
                "fold": int(fold["fold"]),
                "train_n": int(len(fold["train_df"])),
                "valid_n": int(len(valid_df)),
                "train_groups": fold["train_groups"],
                "valid_groups": fold["valid_groups"],
                "group_overlap_count": int(len(fold["group_overlap"])),
                "valid_essay_type_counts": count_dict(valid_df["essay_type"]),
                "valid_student_grade_group_counts": count_dict(valid_df["student_grade_group"]),
                "valid_stratify_counts": count_dict(stratify_labels(valid_df)),
                "warnings": fold["warnings"],
            }
        )

    all_valid_paths = [
        item["relative_path"]
        for doc in fold_docs
        for item in doc["valid"]
    ]
    stratify_counts = count_dict(stratify_labels(df))
    sparse_stratify_classes = {
        key: value for key, value in stratify_counts.items() if value < args.k
    }
    warnings = []
    if sparse_stratify_classes:
        warnings.append(
            "exact stratification infeasible for classes with count < k: "
            f"{sparse_stratify_classes}"
        )
    for summary in fold_summaries:
        if summary["valid_n"] < 30:
            warnings.append(
                f"fold_{summary['fold']} valid_n={summary['valid_n']} < 30; "
                f"unavoidable under k={args.k} with "
                f"{df['student_location'].nunique(dropna=True)} uneven location groups"
            )

    return {
        "cycle_id": int(args.cycle_id),
        "kanban_task_id": args.kanban_task_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_audit_table": source_audit_table,
        "source_audit_table_sha256": source_audit_table_sha,
        "split_method": "sklearn.model_selection.StratifiedGroupKFold",
        "k": int(args.k),
        "seed": int(args.seed),
        "group_key": GROUP_KEY,
        "stratify_key": STRATIFY_KEY,
        "stratify_note": "essay_type x student_grade_group; target scores were not used for splitting",
        "split_hash_algorithm": "sha256",
        "split_hash": split_hash,
        "config_hash_algorithm": "sha256",
        "config_hash": sha256_payload(config_payload),
        "location_groups": count_dict(df["student_location"]),
        "total_rows": int(len(df)),
        "unique_locations": int(df["student_location"].nunique(dropna=True)),
        "stratify_feasibility": {
            "stratify_class_counts": stratify_counts,
            "classes_with_count_below_k": sparse_stratify_classes,
            "exact_stratification_feasible": not bool(sparse_stratify_classes),
        },
        "folds": fold_summaries,
        "leakage_checks": {
            "group_overlap_count_all_folds": int(
                sum(summary["group_overlap_count"] for summary in fold_summaries)
            ),
            "all_rows_appear_once_as_valid": sorted(all_valid_paths)
            == sorted(df["relative_path"].astype(str).tolist()),
            "raw_text_copied": False,
            "target_scores_used_for_split": False,
            "student_location_policy": "split-only; excluded from model feature artifacts",
        },
        "warnings": warnings,
        "outputs": {
            "fold_json_glob": str(output_dir / f"fold_{{0..{args.k - 1}}}.json"),
            "split_manifest": str(output_dir / "split_manifest.yaml"),
            "split_leakage_check": str(output_dir / "split_leakage_check.md"),
        },
        "verification_command": (
            f"python3 pipelines/make_splits.py --input {args.input} --k {args.k} "
            f"--output {args.output} --cycle-id {args.cycle_id} "
            f"--kanban-task-id {args.kanban_task_id}"
        ),
    }


def leakage_report(manifest_doc: dict[str, Any]) -> str:
    fold_rows = []
    for summary in manifest_doc["folds"]:
        fold_rows.append(
            "| {fold} | {train_n} | {valid_n} | {valid_groups} | {group_overlap_count} | {warnings} |".format(
                fold=summary["fold"],
                train_n=summary["train_n"],
                valid_n=summary["valid_n"],
                valid_groups=", ".join(summary["valid_groups"]),
                group_overlap_count=summary["group_overlap_count"],
                warnings=", ".join(summary["warnings"]),
            )
        )
    warnings = manifest_doc["warnings"] or ["None"]
    warning_lines = "\n".join(f"- WARN: {item}" for item in warnings)
    type_lines = "\n".join(
        f"- fold_{summary['fold']}: {summary['valid_essay_type_counts']}"
        for summary in manifest_doc["folds"]
    )
    grade_lines = "\n".join(
        f"- fold_{summary['fold']}: {summary['valid_student_grade_group_counts']}"
        for summary in manifest_doc["folds"]
    )
    return f"""# Cycle {manifest_doc['cycle_id']} Split Leakage Check

## Verdict
PASS. Every validation fold has zero `student.location` overlap with its training fold. Raw essay text, target scores, rater scores, and label-side features were not copied into fold JSON artifacts.

## Split Method
- Method: `StratifiedGroupKFold(n_splits={manifest_doc['k']}, shuffle=True, random_state={manifest_doc['seed']})`
- Group key: `student.location`
- Stratify key: `essay_type__student_grade_group` (`essay_type x student_grade_group`)
- Target scores were not used for splitting.
- `student.location` is retained only in split metadata for leakage verification and must not be used as a model input.

## Fold Leakage Summary
| fold | train_n | valid_n | valid_groups | group_overlap_count | warnings |
|---:|---:|---:|:---|---:|:---|
{chr(10).join(fold_rows)}

## Valid Essay Type Counts
{type_lines}

## Valid Grade Group Counts
{grade_lines}

## Warnings
{warning_lines}
- Rationale: location groups are highly imbalanced (`041`=149, `032`=91, `051`=71, remaining four groups sum to 31), so five location-disjoint folds cannot all reach `valid_n >= 30`.

## Reproducibility
- Split hash: `{manifest_doc['split_hash']}`
- Config hash: `{manifest_doc['config_hash']}`
- Verification command:
```bash
{manifest_doc['verification_command']}
```
"""


def validate_manifest(manifest_doc: dict[str, Any]) -> None:
    checks = manifest_doc["leakage_checks"]
    if checks["group_overlap_count_all_folds"] != 0:
        raise RuntimeError("group leakage detected in split manifest")
    if checks["all_rows_appear_once_as_valid"] is not True:
        raise RuntimeError("not every row appears exactly once as validation")
    if checks["raw_text_copied"] or checks["target_scores_used_for_split"]:
        raise RuntimeError("split artifact leakage policy violated")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output)
    df, source_audit_table, source_audit_table_sha = load_split_table(args)
    require_columns(df)
    df = df.sort_values("relative_path").reset_index(drop=True)

    folds = build_folds(df, args.k, args.seed)
    fold_docs = write_folds(args, output_dir, folds)
    manifest_doc = manifest(
        args=args,
        output_dir=output_dir,
        df=df,
        source_audit_table=source_audit_table,
        source_audit_table_sha=source_audit_table_sha,
        folds=folds,
        fold_docs=fold_docs,
    )
    validate_manifest(manifest_doc)
    write_yaml(output_dir / "split_manifest.yaml", manifest_doc)
    (output_dir / "split_leakage_check.md").write_text(
        leakage_report(manifest_doc), encoding="utf-8"
    )

    print(
        f"wrote {args.k} folds to {output_dir}; "
        f"split_hash={manifest_doc['split_hash']}; "
        f"warnings={len(manifest_doc['warnings'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

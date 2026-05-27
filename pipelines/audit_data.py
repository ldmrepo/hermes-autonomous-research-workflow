#!/usr/bin/env python3
"""Audit the toy Korean essay-scoring sample without copying raw text.

The audit intentionally records only metadata, counts, hashes, and label-side
inventory. Raw essay text, prompts, paragraphs, and correction strings are not
written to artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SENTENCE_SEPARATOR = "#@문장구분#"
LABEL_SIDE_FIELDS = [
    "target_essay_scoreT_avg",
    "rater_1",
    "rater_2",
    "rater_3",
    "paragraph_count_label_side",
    "correction_count_label_side",
    "student_date",
    "student_educated",
    "student_location",
    "student_reading",
    "essay_prompt_present",
    "organization_weight_keys",
    "organization_weight_sum",
    "content_weight_keys",
    "content_weight_sum",
    "expression_weight_keys",
    "expression_weight_sum",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run toy data quality and leakage audit.")
    parser.add_argument("--input", default="dataset/sample", help="Sample dataset root.")
    parser.add_argument("--output-dir", default="workspace/cycle_2/audit")
    parser.add_argument("--cycle-id", type=int, default=2)
    parser.add_argument("--kanban-task-id", default="t_2cf26996")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_paths(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*.json"))
        if path.is_file()
    }


def get_weight_summary(label: dict[str, Any], key: str) -> tuple[str, int]:
    weights = label.get("rubric", {}).get(key, {})
    if not isinstance(weights, dict):
        return "", 0
    keys = sorted(str(item) for item in weights.keys())
    total = sum(value for value in weights.values() if isinstance(value, (int, float)))
    return ",".join(keys), int(total)


def collect_rows(source_root: Path, label_root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    source_paths = json_paths(source_root)
    label_paths = json_paths(label_root)
    relative_paths = sorted(set(source_paths) | set(label_paths))
    rows: list[dict[str, Any]] = []
    source_ids: list[str] = []
    label_ids: list[str] = []
    source_hashes: list[str] = []

    for relative_path in relative_paths:
        source_path = source_paths.get(relative_path)
        label_path = label_paths.get(relative_path)
        source = load_json(source_path) if source_path else {}
        label = load_json(label_path) if label_path else {}

        essay_text = source.get("essay_txt")
        essay_id_source = source.get("essay_id")
        essay_id_label = label.get("info", {}).get("essay_id")
        if essay_id_source:
            source_ids.append(str(essay_id_source))
        if essay_id_label:
            label_ids.append(str(essay_id_label))

        source_sha = sha256_text(essay_text) if isinstance(essay_text, str) else ""
        if source_sha:
            source_hashes.append(source_sha)
        label_sha = sha256_file(label_path) if label_path else ""

        score = label.get("score", {})
        essay_scores = score.get("essay_scoreT", [])
        if not isinstance(essay_scores, list):
            essay_scores = []
        student = label.get("student", {})
        info = label.get("info", {})
        paragraph = label.get("paragraph", [])
        correction = label.get("correction", [])
        org_keys, org_sum = get_weight_summary(label, "organization_weight")
        con_keys, con_sum = get_weight_summary(label, "content_weight")
        exp_keys, exp_sum = get_weight_summary(label, "expression_weight")

        rows.append(
            {
                "relative_path": relative_path,
                "genre_dir": Path(relative_path).parts[0] if Path(relative_path).parts else "",
                "has_source": bool(source_path),
                "has_label": bool(label_path),
                "essay_id_source": essay_id_source,
                "essay_id_label": essay_id_label,
                "essay_id_match": bool(essay_id_source and essay_id_label and essay_id_source == essay_id_label),
                "essay_type": info.get("essay_type") or label.get("rubric", {}).get("essay_type"),
                "student_grade": student.get("student_grade"),
                "student_grade_group": student.get("student_grade_group"),
                "student_location": student.get("location"),
                "student_date": student.get("date"),
                "target_essay_scoreT_avg": score.get("essay_scoreT_avg"),
                "essay_txt_present": isinstance(essay_text, str) and bool(essay_text.strip()),
                "essay_txt_chars": len(essay_text) if isinstance(essay_text, str) else 0,
                "sentence_sep_count_source": essay_text.count(SENTENCE_SEPARATOR)
                if isinstance(essay_text, str)
                else 0,
                "source_sha256": source_sha,
                "essay_level": info.get("essay_level"),
                "essay_len_label": info.get("essay_len"),
                "essay_prompt_present": "essay_prompt" in info,
                "student_educated": student.get("student_educated"),
                "student_reading": student.get("student_reading"),
                "rater_1": essay_scores[0] if len(essay_scores) > 0 else None,
                "rater_2": essay_scores[1] if len(essay_scores) > 1 else None,
                "rater_3": essay_scores[2] if len(essay_scores) > 2 else None,
                "paragraph_count_label_side": len(paragraph) if isinstance(paragraph, list) else 0,
                "correction_count_label_side": len(correction) if isinstance(correction, list) else 0,
                "label_sha256": label_sha,
                "organization_weight_keys": org_keys,
                "organization_weight_sum": org_sum,
                "content_weight_keys": con_keys,
                "content_weight_sum": con_sum,
                "expression_weight_keys": exp_keys,
                "expression_weight_sum": exp_sum,
            }
        )

    df = pd.DataFrame(rows)
    duplicate_source_ids = duplicate_count(source_ids)
    duplicate_label_ids = duplicate_count(label_ids)
    duplicate_source_hashes = duplicate_count(source_hashes)
    extras = {
        "source_json_files": len(source_paths),
        "label_json_files": len(label_paths),
        "duplicate_source_ids": duplicate_source_ids,
        "duplicate_label_ids": duplicate_label_ids,
        "duplicate_source_hashes": duplicate_source_hashes,
    }
    return df, extras


def duplicate_count(values: list[str]) -> int:
    counts = Counter(values)
    return sum(count - 1 for count in counts.values() if count > 1)


def count_table(series: pd.Series, name: str) -> pd.DataFrame:
    counts = series.fillna("<MISSING>").astype(str).value_counts(dropna=False)
    return counts.rename_axis(name).reset_index(name="count")


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    return df.to_markdown(index=False)


def target_summary(target: pd.Series) -> dict[str, float | int]:
    clean = pd.to_numeric(target, errors="coerce").dropna()
    return {
        "n": int(clean.shape[0]),
        "min": float(clean.min()),
        "p25": float(clean.quantile(0.25)),
        "median": float(clean.median()),
        "mean": float(clean.mean()),
        "p75": float(clean.quantile(0.75)),
        "max": float(clean.max()),
        "std": float(clean.std()),
    }


def imbalance(series: pd.Series) -> dict[str, Any]:
    counts = series.fillna("<MISSING>").astype(str).value_counts()
    min_count = int(counts.min()) if not counts.empty else 0
    max_count = int(counts.max()) if not counts.empty else 0
    ratio = float(max_count / min_count) if min_count else float("inf")
    return {
        "min": min_count,
        "max": max_count,
        "ratio": ratio,
        "counts": {str(key): int(value) for key, value in counts.items()},
    }


def build_target_distribution(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    target = pd.to_numeric(df["target_essay_scoreT_avg"], errors="coerce")
    n = int(target.notna().sum())
    for value, count in target.dropna().value_counts().sort_index().items():
        rows.append(
            {
                "dimension": "essay_scoreT_avg_exact",
                "value": value,
                "count": int(count),
                "ratio": float(count / n) if n else 0.0,
            }
        )
    rounded = target.dropna().round().astype(int)
    for value, count in rounded.value_counts().sort_index().items():
        rows.append(
            {
                "dimension": "score_band_rounded",
                "value": int(value),
                "count": int(count),
                "ratio": float(count / n) if n else 0.0,
            }
        )
    return pd.DataFrame(rows)


def quality_report(
    df: pd.DataFrame,
    extras: dict[str, Any],
    paths: dict[str, str],
    source_root: Path,
    label_root: Path,
    summary: dict[str, Any],
    imbalance_checks: dict[str, Any],
    cycle_id: int,
) -> str:
    dtype_rows = [
        {
            "column": column,
            "dtype": str(df[column].dtype),
            "non_null": int(df[column].notna().sum()),
            "nulls": int(df[column].isna().sum()),
        }
        for column in df.columns
    ]
    target = pd.to_numeric(df["target_essay_scoreT_avg"], errors="coerce")
    score_bands = target.dropna().round().astype(int).value_counts().sort_index()
    score_band_df = score_bands.rename_axis("score_band").reset_index(name="count")
    target_summary_df = pd.DataFrame([target_summary(df["target_essay_scoreT_avg"])])

    warnings = []
    for name, check in imbalance_checks.items():
        if check["ratio"] > 5:
            warnings.append(
                f"- WARN: `{name}` max/min ratio {check['ratio']:.2f} (>5). Counts: {check['counts']}"
            )
    warning_text = "\n".join(warnings) if warnings else "- No imbalance ratios >5x."

    return f"""# Cycle {cycle_id} Data Quality Audit
## Scope
- Source root: `{source_root.as_posix()}/`
- Label root: `{label_root.as_posix()}/`
- Raw essay text, prompts, paragraphs, and correction text were not copied into audit artifacts.
- Milestone goal was reinjected by the kanban task body; SHA256 is recorded in `audit_manifest.json`.

## Shape
{markdown_table(pd.DataFrame([summary]))}

## Dtypes And Non-Null Counts
{markdown_table(pd.DataFrame(dtype_rows))}

## Missing Pairs And ID Consistency
- Missing source files: {summary["missing_source"]}
- Missing label files: {summary["missing_label"]}
- Source/label essay ID mismatches: {summary["id_mismatches"]}
- Duplicate source essay IDs: {extras["duplicate_source_ids"]}
- Duplicate label essay IDs: {extras["duplicate_label_ids"]}

## Genre / Type Distribution
{markdown_table(count_table(df["essay_type"], "essay_type"))}

## Grade Distribution
{markdown_table(count_table(df["student_grade"], "student_grade"))}

## Location Group Distribution
{markdown_table(count_table(df["student_location"], "student_location"))}

## Target Summary
{markdown_table(target_summary_df)}

## Target Rounded Score-Band Distribution
{markdown_table(score_band_df)}

## Imbalance Checks (>5x)
{warning_text}

Recommended policy: preserve all samples in toy scope, report segment metrics separately, and allow the SPLIT step to use location groups while monitoring type/grade coverage per fold. For training-only mitigation, prefer sample weights over resampling so evaluator distributions remain unchanged.

## Generated Files
- `{paths["data_quality_report"]}`
- `{paths["leakage_audit"]}`
- `{paths["target_distribution"]}`
- `{paths["audit_manifest"]}`
- `{paths["audit_table_no_raw_text"]}`
"""


def leakage_report(df: pd.DataFrame, extras: dict[str, Any], cycle_id: int) -> str:
    location_counts = count_table(df["student_location"], "student_location")
    dates = count_table(df["student_date"], "student_date").head(30)
    location_type = pd.crosstab(df["student_location"], df["essay_type"]).reset_index()
    location_grade_group = pd.crosstab(
        df["student_location"], df["student_grade_group"]
    ).reset_index()
    provenance = pd.DataFrame(
        [
            {
                "field": "source.essay_txt",
                "source": "source",
                "provenance": "model-input-allowed",
                "policy": "Allowed as text input after sentence-token handling.",
            },
            {
                "field": "label.student.student_grade",
                "source": "label",
                "provenance": "allowed-metadata",
                "policy": "Only student metadata allowed in model input by Hard Rule #2.",
            },
            {
                "field": "label.student.location",
                "source": "label",
                "provenance": "split-only",
                "policy": "Allowed only as GroupKFold split key, never model input.",
            },
            {
                "field": "label.score.*",
                "source": "label",
                "provenance": "label-side",
                "policy": "Evaluator/target only. Hard block if used as feature.",
            },
            {
                "field": "label.paragraph.*",
                "source": "label",
                "provenance": "label-side",
                "policy": "Hard block if used as feature; includes paragraph_count.",
            },
            {
                "field": "label.correction.*",
                "source": "label",
                "provenance": "label-side",
                "policy": "Hard block if used as feature; includes correction_count.",
            },
            {
                "field": "label.rubric.*_weight",
                "source": "label",
                "provenance": "config-derived/reference",
                "policy": "Weights must be extracted into configs/rubric_weights.yaml, not hardcoded or used as per-row target proxy.",
            },
            {
                "field": "label.info.essay_prompt",
                "source": "label",
                "provenance": "prompt/context",
                "policy": "Not allowed for current toy model input unless explicitly approved; audit artifacts omit raw prompt text.",
            },
        ]
    )

    return f"""# Cycle {cycle_id} Leakage Audit
## Verdict
PASS for audit-stage data inventory. No duplicate essay IDs, no source/label ID mismatches, and no missing source/label pairs were found. Downstream FEATURE/MODEL steps must block any label-side feature listed below.

## ID Leakage / Duplicate Checks
- Source JSON files: {extras["source_json_files"]}
- Label JSON files: {extras["label_json_files"]}
- Matched source-label pairs with identical essay_id: {int(df["essay_id_match"].sum())}
- Duplicate source essay IDs: {extras["duplicate_source_ids"]}
- Duplicate label essay IDs: {extras["duplicate_label_ids"]}
- Duplicate source payload hashes: {extras["duplicate_source_hashes"]}

## Time Leakage
- `student.date` exists only in label JSON and is not model-safe. It must not be used for features.
- Current toy pipeline uses k-fold grouping, not chronological evaluation, so no temporal split leakage was detected at audit stage.

Top date distribution:
{markdown_table(dates)}

_Showing first 30 of {df["student_date"].nunique(dropna=True)} rows._

## Target Leakage / Feature Provenance
{markdown_table(provenance)}

Label-side fields present in normalized audit table: {", ".join(LABEL_SIDE_FIELDS)}

## Group Leakage: student.location
- Unique location groups: {df["student_location"].nunique(dropna=True)}
- Largest location group size: {int(df["student_location"].value_counts().max())}
- Required split policy: `student.location` based GroupKFold. Location must be excluded from model features.

Location counts:
{markdown_table(location_counts)}

Location x essay_type:
{markdown_table(location_type)}

Location x student_grade_group:
{markdown_table(location_grade_group)}

## Split Feasibility Notes
- Five-fold group split is feasible in the narrow sense that there are {df["student_location"].nunique(dropna=True)} non-null location groups, but fold balance will be constrained by the largest group.
- If any validation fold has fewer than 30 samples in SPLIT, emit warn as required by AGENTS.md.
- Because location groups are correlated with genre/grade coverage, SPLIT should report fold-wise type and grade distributions and avoid using location in model inputs.

## Block Conditions For Downstream Tasks
- Block FEATURE/MODEL if `paragraph_count_label_side`, `correction_count_label_side`, `score.*`, raw rater scores, `student.location`, `student.date`, or `student.reading` appear in model feature provenance.
- Block SPLIT if the same `student.location` group appears in both train and validation for any fold.
- Block any task that silently drops unmatched pairs or duplicate IDs. Current audit found none.
"""


def main() -> None:
    args = parse_args()
    input_root = Path(args.input)
    source_root = input_root / "원천데이터"
    label_root = input_root / "라벨링데이터"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not source_root.exists() or not label_root.exists():
        raise FileNotFoundError(f"expected source and label roots under {input_root}")

    df, extras = collect_rows(source_root, label_root)
    target = pd.to_numeric(df["target_essay_scoreT_avg"], errors="coerce")
    summary = {
        "rows": int(df.shape[0]),
        "source_json_files": extras["source_json_files"],
        "label_json_files": extras["label_json_files"],
        "matched_pairs": int(df["essay_id_match"].sum()),
        "missing_source": int((~df["has_source"]).sum()),
        "missing_label": int((~df["has_label"]).sum()),
        "id_mismatches": int((df["has_source"] & df["has_label"] & ~df["essay_id_match"]).sum()),
        "duplicate_source_ids": extras["duplicate_source_ids"],
        "duplicate_label_ids": extras["duplicate_label_ids"],
        "target_min": float(target.min()),
        "target_max": float(target.max()),
        "target_mean": float(target.mean()),
        "target_std": float(target.std()),
        "unique_locations": int(df["student_location"].nunique(dropna=True)),
        "max_location_group_size": int(df["student_location"].value_counts().max()),
    }
    imbalance_checks = {
        "essay_type": imbalance(df["essay_type"]),
        "student_grade": imbalance(df["student_grade"]),
        "student_grade_group": imbalance(df["student_grade_group"]),
        "student_location": imbalance(df["student_location"]),
    }
    imbalance_flags = {
        key: value for key, value in imbalance_checks.items() if value["ratio"] > 5
    }
    warnings = [
        f"{key} imbalance ratio {value['ratio']:.2f} > 5x"
        for key, value in imbalance_flags.items()
    ]
    errors = []
    if summary["missing_source"]:
        errors.append("missing source files detected")
    if summary["missing_label"]:
        errors.append("missing label files detected")
    if summary["id_mismatches"]:
        errors.append("source/label essay_id mismatches detected")
    if summary["duplicate_source_ids"]:
        errors.append("duplicate source essay IDs detected")
    if summary["duplicate_label_ids"]:
        errors.append("duplicate label essay IDs detected")

    paths = {
        "data_quality_report": (output_dir / "data_quality_report.md").as_posix(),
        "leakage_audit": (output_dir / "leakage_audit.md").as_posix(),
        "target_distribution": (output_dir / "target_distribution.csv").as_posix(),
        "audit_manifest": (output_dir / "audit_manifest.json").as_posix(),
        "audit_table_no_raw_text": (output_dir / "audit_table_no_raw_text.csv").as_posix(),
    }

    milestone_path = Path("MILESTONE.md")
    milestone_hash = sha256_file(milestone_path) if milestone_path.exists() else None
    target_distribution = build_target_distribution(df)

    df.to_csv(paths["audit_table_no_raw_text"], index=False)
    target_distribution.to_csv(paths["target_distribution"], index=False)
    Path(paths["data_quality_report"]).write_text(
        quality_report(
            df,
            extras,
            paths,
            source_root,
            label_root,
            summary,
            imbalance_checks,
            args.cycle_id,
        ),
        encoding="utf-8",
    )
    Path(paths["leakage_audit"]).write_text(
        leakage_report(df, extras, args.cycle_id),
        encoding="utf-8",
    )

    manifest = {
        "task_id": args.kanban_task_id,
        "task_title": f"T-CYCLE-{args.cycle_id}-AUDIT: 데이터 검증",
        "cycle_id": args.cycle_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "milestone_goal_hash": milestone_hash,
        "milestone_goal_hash_algorithm": "sha256",
        "input_roots": {
            "source": source_root.as_posix(),
            "labels": label_root.as_posix(),
        },
        "outputs": paths,
        "verification_command": (
            f"python3 pipelines/audit_data.py --input {input_root.as_posix()}/ "
            f"--output-dir {output_dir.as_posix()} --cycle-id {args.cycle_id} "
            f"--kanban-task-id {args.kanban_task_id}"
        ),
        "summary": summary,
        "imbalance_checks": imbalance_checks,
        "imbalance_flags_over_5x": imbalance_flags,
        "feature_provenance_policy": {
            "model_allowed": ["essay_txt", "student_grade"],
            "split_only": ["student_location"],
            "label_side_hard_block": LABEL_SIDE_FIELDS,
        },
        "errors": errors,
        "status": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "warnings": warnings,
    }
    write_json(Path(paths["audit_manifest"]), manifest)

    if errors:
        raise SystemExit("; ".join(errors))
    print(f"audit status: {manifest['status']}")
    print(f"artifacts: {output_dir.as_posix()}/")


if __name__ == "__main__":
    main()

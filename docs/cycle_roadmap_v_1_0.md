# Cycle Roadmap

Task: `t_1840027a`  
Date: 2026-05-27  
Scope: Phase B infrastructure plan for Hermes self-improving Korean essay auto-scoring cycles

## 1. Purpose

This roadmap defines the phase model, Cycle 1 execution chain, acceptance posture, and handoff boundaries for the toy Korean K-12 essay auto-scoring workflow.

The immediate objective is not model performance. The objective is to prove that Hermes can repeatedly run an audit -> split -> feature -> model -> eval -> review -> synth cycle, preserve evidence in files and MLflow, stop on hard safety failures, and create a DECIDE task for the next bounded cycle.

Cycle 1 must directly address the prior T7 blocking finding: label-side `paragraph` and `correction` annotations were used as validation features. Any recurrence of label-side feature use is a hard block.

## 2. Non-Negotiable Boundaries

Cycle work remains under the locked rules in `AGENTS.md`.

| Boundary | Cycle 1 handling |
| --- | --- |
| Test leakage | `student.location` group split only; validation labels accessed only by evaluator. |
| Student PII | `student_grade` may be used; `student.location` is split-only and not a model feature. |
| Feature provenance | Every feature must be tagged `source`, `derived`, or `label-side`; `label-side` use blocks acceptance. |
| MLflow evidence | All model runs must log seed, config hash, artifact path, `cycle_id`, `kanban_task_id`, and `feature_provenance`. |
| Rubric weights | Extract from `configs/rubric_weights.yaml`; hardcoding is not allowed. |
| Ceiling comparison | Compare model QWK against the same target unit as the human ceiling, with bootstrap CI. |
| Toy-only warnings | Baseline monotonicity and ceiling excess are warnings except where `AGENTS.md` explicitly keeps a toy hard sanity gate. |
| Phase-up | DECIDE can recommend phase-up, but implementation cannot start without human approval. |

## 3. Phase 1: Toy Workflow Validation

| Field | Plan |
| --- | --- |
| Goal | Prove leakage-free toy pipeline execution and Hermes autonomous cycle behavior on the 342-row sample. |
| Data | `dataset/sample/` only; no full 50K data loading. |
| Sub-task sequence | AUDIT -> SPLIT -> FEATURE -> MODEL -> EVAL and REVIEW in parallel -> SYNTH -> DECIDE. |
| Priority fix | Remove label-side feature reads found by T7; feature construction must use fold records and source text only. |
| AGENTS.md changes | None in Cycle 1. `AGENTS.md` is locked for this task. |
| MLflow changes | Require `cycle_id=cycle_1`, task id tags, config hash, feature provenance tag, and artifacts for predictions, metrics, segment metrics, and manifests. |
| Exit criteria | `ACCEPTANCE_CRITERIA.yaml` toy stage returns `PASS_CANDIDATE` or a documented fail judgement with block metadata and repro commands. |

Cycle 1 should also carry a small isolated cron/event-trigger validation recommendation into SYNTH, but it should not make cron validation a modeling acceptance dependency.

## 4. Phase 2: Mid-Scale Robustness

| Field | Plan |
| --- | --- |
| Goal | Stress the procedure beyond the 342-row toy sample while staying below production scope and preserving the same safety rules. |
| Data | A human-approved mid-scale subset only; no autonomous full-data load. |
| Sub-task sequence | AUDIT -> SPLIT -> FEATURE -> MODEL -> EVAL -> REVIEW -> SYNTH -> DECIDE, with an added stability task for repeated split seeds if approved. |
| AGENTS.md changes | Propose only mutable routing/reporting refinements; do not change hard rules. |
| MLflow changes | Add run groups for repeated seeds, CI artifacts, and per-segment trend artifacts across cycles. |
| Exit criteria | Repeated leakage checks pass; segment metrics have enough support to interpret; no cost circuit breaker breach; DECIDE recommends full phase only with evidence package. |

Mid phase should introduce stronger reproducibility diagnostics before increasing model complexity.

## 5. Phase 3: Full Dataset Research

| Field | Plan |
| --- | --- |
| Goal | Run the validated pipeline on the full dataset after human phase-up approval. |
| Data | Full dataset only after explicit Phase-up DECIDE approval. |
| Sub-task sequence | AUDIT -> SPLIT -> FEATURE -> MODEL -> EVAL -> REVIEW -> SYNTH, with separate data ingestion and resource planning tasks. |
| AGENTS.md changes | Remove toy relaxations through a separate reviewed change; all monotonic and ceiling gates become hard-block where specified. |
| MLflow changes | Add dataset versioning, full split versioning, bootstrap CI by fold, and model registry candidate records. |
| Exit criteria | Strict leakage, monotonicity, ceiling, reproducibility, and segment gates pass with CI; model remains candidate-only unless production approval is granted. |

Full phase must use the same metric unit for model and human ceiling comparison and must not block on point estimates alone.

## 6. Phase 4: Production Readiness

| Field | Plan |
| --- | --- |
| Goal | Prepare an accepted full-phase model for controlled registration and downstream evaluation. |
| Data | Human-approved production training and validation surfaces only. |
| Sub-task sequence | Registry planning -> final review -> model registration request -> external deployment planning -> canary plan. |
| AGENTS.md changes | Production-specific approval rules may be proposed, but locked safety policy remains human-owned. |
| MLflow changes | Use Model Registry only after approval; record aliases, lineage, and rollback metadata. |
| Exit criteria | Human approves registry/deployment; canary and rollback evidence exists; external release remains gated. |

Production phase is outside the current milestone and must not be entered automatically.

## 7. Cycle 1 Execution Plan

| Step | Profile | Parent | Required output |
| --- | --- | --- | --- |
| T-CYCLE-1-AUDIT | `tukey` | none | Data audit, leakage audit, target distribution, milestone goal anchor evidence. |
| T-CYCLE-1-SPLIT | `gauss` | AUDIT | Group split files, split manifest YAML, leakage recheck, fold size warnings. |
| T-CYCLE-1-FEATURE | `gauss` | SPLIT | Leakage-free feature builder/config, feature provenance manifest, no label-side features. |
| T-CYCLE-1-MODEL | `gauss` | FEATURE | M1-M4 baseline runs, MLflow records, manifests, prediction artifacts. |
| T-CYCLE-1-EVAL | `spearman` | MODEL | Overall, segment, acceptance, ceiling, bootstrap CI, and monotonic diagnostics. |
| T-CYCLE-1-REVIEW | `turing` | MODEL | WRONG/FRAGILE/STYLE review, split leakage and feature provenance audit. |
| T-CYCLE-1-SYNTH | `aristotle` | EVAL and REVIEW | Cycle report, acceptance judgement, next-cycle recommendation, skill candidates. |
| DECIDE-1 | human | SYNTH | Continue, Phase-up, or Stop decision. |

The dependency graph is acyclic: all edges point forward from audit to decision, with only one fork at MODEL and one join at SYNTH.

## 8. Acceptance Model

Acceptance is defined in `ACCEPTANCE_CRITERIA.yaml`.

Judgement values follow the MLflow guide Section 15:

```text
PASS_FINAL
PASS_CANDIDATE
FAIL_RETRY_HPO
FAIL_REBUILD_FEATURES
FAIL_REVIEW_LABELS
FAIL_CHANGE_MODEL
FAIL_NEED_MORE_DATA
FAIL_STOP_NO_GAIN
```

Toy Cycle 1 should normally produce `PASS_CANDIDATE` only if hard safety gates pass. It should not produce `PASS_FINAL`, because final model registration is forbidden in the toy phase.

## 9. MLflow and Artifact Requirements

Every modeling run must log:

| Category | Required fields |
| --- | --- |
| Params | model id, feature set, target, split version, seed, config hash. |
| Metrics | QWK, MAE, RMSE, train/valid gap, segment summary metrics. |
| Tags | `cycle_id`, `kanban_task_id`, `feature_provenance`, dataset version, split version, rubric version. |
| Artifacts | predictions, metrics JSON, segment metrics CSV, feature provenance manifest, reproducibility manifest. |

The SYNTH task must cite artifact paths and verification commands in its metadata so later cycles can consume full trace context.

## 10. Escalation and Timeout Handling

Cycle 1 inherits `configs/board_config.yaml`:

| Control | Policy |
| --- | --- |
| Max concurrent cycles | 1 |
| Max tasks per cycle | 12 |
| Max consecutive failures | 3 |
| DECIDE grace | 6h grace, then Pause |
| Phase-up timeout | Always Pause |
| Cost breaker | Pause and notify on token/USD/velocity breach |

Any hard safety failure must block with reason, artifact paths, policy reference, and a reproducible command. Silent failure is not allowed.

## 11. Skill Library Plan

Cycle 1 may identify skill candidates, but only `acceptance_pass` outputs are eligible for `skills/`.

Initial categories:

| Category | Candidate |
| --- | --- |
| `text_preprocessing/` | `sentence_separator_token.md` for `#@문장구분#` handling. |
| `feature_engineering/` | `feature_provenance_contract.md` after label-side checks pass. |
| `error_analysis_patterns/` | `toy_segment_eval_template.md` after evaluator/reviewer agreement. |

Cycle 2 may create placeholder `skills/index.json`; Cycle 3+ can introduce semantic retrieval.

## 12. Verification

This roadmap is verified by:

```bash
test -f docs/cycle_roadmap_v_1_0.md
python3 -c "import pathlib; p=pathlib.Path('docs/cycle_roadmap_v_1_0.md'); assert p.read_text().count('\n## ') >= 8"
python3 -c "import yaml; yaml.safe_load(open('ACCEPTANCE_CRITERIA.yaml'))"
```

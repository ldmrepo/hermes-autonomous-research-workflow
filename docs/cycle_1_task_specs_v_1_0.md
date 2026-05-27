# Cycle 1 Kanban Task Specs

Task: `t_1840027a`  
Date: 2026-05-27  
Board: `essay-auto-scoring-research-v2`

## 1. Purpose

This document specifies the seven Cycle 1 sub-tasks plus `DECIDE-1` in `hermes kanban create` command form.

The commands are intentionally specs, not executed by this task. They keep implementation in later tasks and preserve the dependency graph required by `AGENTS.md`.

## 2. Dependency Graph

```text
T-CYCLE-1-AUDIT
  -> T-CYCLE-1-SPLIT
    -> T-CYCLE-1-FEATURE
      -> T-CYCLE-1-MODEL
        -> T-CYCLE-1-EVAL
        -> T-CYCLE-1-REVIEW
          [EVAL + REVIEW] -> T-CYCLE-1-SYNTH
            -> DECIDE-1
```

No edge points back to an ancestor. EVAL and REVIEW are siblings with the same parent, MODEL.

## 3. Shared Command Defaults

All tasks use the project directory workspace:

```bash
--workspace dir:/home/dev/work/essay-auto-scoring-research
```

Every body must include artifact paths and verification commands in completion metadata. Failed tasks must block with a reason, policy reference, artifact paths, and a reproducible command.

## 4. T-CYCLE-1-AUDIT

Goal anchor, verbatim from `MILESTONE.md`:

```text
Hermes Multi-Agent Kanban Board로 한국어 K-12 에세이 자동채점 워크플로우의
**24시간 자가발전 long-running cycle** 가능성을 toy 데이터(342건) + 라이트 모델로 검증한다.

본 milestone의 1차 목표는 모델 성능이 아니라 **자가발전 워크플로우의 동작 입증**이다.
매 Cycle N의 첫 sub-task(AUDIT)는 이 문서를 verbatim으로 컨텍스트에 재주입한다 (Hard Rule #10).
```

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-AUDIT: data and leakage audit" \
  --assignee tukey \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-audit \
  --body "## Goal
Run Cycle 1 AUDIT for the toy Korean essay-scoring pipeline.

## Goal Anchor
Hermes Multi-Agent Kanban Board로 한국어 K-12 에세이 자동채점 워크플로우의
**24시간 자가발전 long-running cycle** 가능성을 toy 데이터(342건) + 라이트 모델로 검증한다.

본 milestone의 1차 목표는 모델 성능이 아니라 **자가발전 워크플로우의 동작 입증**이다.
매 Cycle N의 첫 sub-task(AUDIT)는 이 문서를 verbatim으로 컨텍스트에 재주입한다 (Hard Rule #10).

## Input Context
- MILESTONE.md
- AGENTS.md
- ACCEPTANCE_CRITERIA.yaml
- docs/cycle_roadmap_v_1_0.md
- docs/final_report_v_1_0.md
- docs/hermes_validation_v_1_0.md

## Work
- Inspect dataset/sample/ only.
- Run shape, dtype, NaN, duplicate, and target distribution checks.
- Run leakage checks for ID duplicate, time leakage, target leakage, and group leakage using student.location as split key.
- Report label imbalance >5x and propose weighting/resampling policy.

## Outputs
- reports/cycle_1/audit/data_quality_report.md
- reports/cycle_1/audit/leakage_audit.md
- reports/cycle_1/audit/audit_manifest.json

## Verification
python pipelines/audit_data.py --input dataset/sample/"
```

## 5. T-CYCLE-1-SPLIT

Parent: output id of `T-CYCLE-1-AUDIT`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-SPLIT: group stratified folds" \
  --assignee gauss \
  --parent <T-CYCLE-1-AUDIT_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-split \
  --body "## Goal
Create leakage-safe Cycle 1 splits.

## Input Context
- Parent AUDIT artifact paths and full output trace.
- AGENTS.md Hard Rule #1 and split conventions.
- ACCEPTANCE_CRITERIA.yaml toy stage.

## Work
- Use student.location as GroupKFold group key.
- Stratify by Type x grade band where possible.
- Generate k=5 folds under dataset/splits/.
- Recheck split leakage after writing files.
- Write fold valid sizes and warn when valid_n < 30.
- Save split manifest YAML and hash.

## Outputs
- dataset/splits/
- reports/cycle_1/split/split_manifest.yaml
- reports/cycle_1/split/split_leakage_check.md

## Verification
python pipelines/make_splits.py --input dataset/sample/ --k 5 --output dataset/splits/"
```

## 6. T-CYCLE-1-FEATURE

Parent: output id of `T-CYCLE-1-SPLIT`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-FEATURE: leakage-free feature contract" \
  --assignee gauss \
  --parent <T-CYCLE-1-SPLIT_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-feature \
  --body "## Goal
Build Cycle 1 features without label-side leakage.

## Input Context
- Parent SPLIT artifact paths and full output trace.
- T7 blocking lesson from docs/final_report_v_1_0.md.
- AGENTS.md Hard Rule #9.
- ACCEPTANCE_CRITERIA.yaml global_hard_gates.feature_provenance_label_side_count.

## Work
- Fix the label-side feature boundary found in prior T7.
- Build model features from fold records and source text only.
- Do not read label JSON for paragraph_count, correction_count, or any model input.
- Mark every feature as source, derived, or label-side in a provenance manifest.
- Automatically block if any label-side feature is selected.

## Outputs
- reports/cycle_1/features/feature_config.yaml
- reports/cycle_1/features/feature_provenance_manifest.yaml
- reports/cycle_1/features/feature_leakage_check.md
- feature matrices under the accepted project convention.

## Verification
python pipelines/train.py --config configs/<model>.yaml --split dataset/splits/ --dry-run-features"
```

## 7. T-CYCLE-1-MODEL

Parent: output id of `T-CYCLE-1-FEATURE`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-MODEL: M1-M4 toy baselines" \
  --assignee gauss \
  --parent <T-CYCLE-1-FEATURE_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-model \
  --body "## Goal
Train and log the four toy baselines.

## Input Context
- Parent FEATURE artifact paths and full output trace.
- ACCEPTANCE_CRITERIA.yaml mlflow_recording and toy stage.
- configs/rubric_weights.yaml.

## Work
- Train M1 dummy, M2 length, M3 TF-IDF+Ridge, M4 LightGBM.
- Log every run to MLflow with cycle_id=cycle_1, kanban_task_id, config_hash, seed, artifact paths, and feature_provenance.
- Report assumptions, training time, validation metrics, prediction distribution, and train/valid gap.
- Do not register a final model.

## Outputs
- reports/cycle_1/model/baseline_summary.json
- reports/cycle_1/model/reproducibility_manifest.json
- mlruns/
- model and prediction artifacts under the accepted project convention.

## Verification
python pipelines/train.py --config configs/<model>.yaml --split dataset/splits/"
```

## 8. T-CYCLE-1-EVAL

Parent: output id of `T-CYCLE-1-MODEL`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-EVAL: metrics, segments, and ceiling CI" \
  --assignee spearman \
  --parent <T-CYCLE-1-MODEL_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-eval \
  --body "## Goal
Evaluate Cycle 1 model outputs.

## Input Context
- Parent MODEL artifact paths and full output trace.
- ACCEPTANCE_CRITERIA.yaml toy stage.
- AGENTS.md Hard Rule #8.

## Work
- Report overall, per-segment, and acceptance-comparison metrics.
- Segment by type, grade band, and score band.
- Compute or attach bootstrap CI.
- Compare model metric to human ceiling using the same metric unit.
- Run toy monotonic diagnostics and record warn-only vs hard-block status.

## Outputs
- reports/cycle_1/eval/eval_report.md
- reports/cycle_1/eval/segment_metrics.csv
- reports/cycle_1/eval/ceiling_comparison.json
- reports/cycle_1/eval/eval_manifest.json

## Verification
python pipelines/evaluate.py --run-id <mlflow_run_id>"
```

## 9. T-CYCLE-1-REVIEW

Parent: output id of `T-CYCLE-1-MODEL`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-REVIEW: leakage and reproducibility gate" \
  --assignee turing \
  --parent <T-CYCLE-1-MODEL_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-review \
  --body "## Goal
Review Cycle 1 for hard-rule violations.

## Input Context
- Parent MODEL artifact paths and full output trace.
- Prior T7 leakage block from docs/final_report_v_1_0.md.
- ACCEPTANCE_CRITERIA.yaml global hard gates.

## Work
- Classify findings as WRONG, FRAGILE, or STYLE.
- Recheck split leakage.
- Audit feature provenance and confirm label-side feature count is zero.
- Confirm reproducibility manifests and MLflow tags.
- Do not approve if failing tests or hard-rule violations exist.

## Outputs
- reports/cycle_1/review/review_report.md
- reports/cycle_1/review/leakage_reverification.md
- reports/cycle_1/review/feature_provenance_audit.md

## Verification
python3 -c \"import yaml; yaml.safe_load(open('ACCEPTANCE_CRITERIA.yaml'))\""
```

## 10. T-CYCLE-1-SYNTH

Parents: output ids of `T-CYCLE-1-EVAL` and `T-CYCLE-1-REVIEW`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "T-CYCLE-1-SYNTH: acceptance synthesis and next decision" \
  --assignee aristotle \
  --parent <T-CYCLE-1-EVAL_ID> \
  --parent <T-CYCLE-1-REVIEW_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-synth \
  --body "## Goal
Synthesize Cycle 1 outputs into an acceptance judgement and DECIDE-1 recommendation.

## Input Context
- Full parent EVAL and REVIEW artifact paths and output trace.
- ACCEPTANCE_CRITERIA.yaml.
- docs/cycle_roadmap_v_1_0.md.

## Work
- Combine the seven sub-task outputs into reports/cycle_1/cycle_1_report.md.
- Compare evidence against ACCEPTANCE_CRITERIA.yaml and record the judgement enum.
- Extract skill library candidates only from acceptance-passing outputs.
- Prepare DECIDE-1 body with Continue, Phase-up, Stop options.
- Keep cron validation separate from modeling acceptance.

## Outputs
- reports/cycle_1/cycle_1_report.md
- reports/cycle_1/decision_summary.md
- reports/cycle_1/skill_candidates.md

## Verification
python3 -c \"import yaml; yaml.safe_load(open('ACCEPTANCE_CRITERIA.yaml'))\""
```

## 11. DECIDE-1

Parent: output id of `T-CYCLE-1-SYNTH`. This task is assigned to the human gate by leaving the assignee as `user`.

```bash
hermes kanban --board essay-auto-scoring-research-v2 create "DECIDE-1: continue, phase-up, or stop" \
  --assignee user \
  --parent <T-CYCLE-1-SYNTH_ID> \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --idempotency-key cycle-1-decide \
  --initial-status blocked \
  --body "## Decision Required
[Continue] -> Cycle 2 automatic spawn inside toy scope if acceptance is not final and no hard safety block prevents continuation.
[Phase-up] -> Create T-PHASE-MIGRATE planning task and pause for human approval.
[Stop] -> End the autonomous cycle and create a summary/archive task.

## Cycle 1 Summary
- Acceptance vs ACCEPTANCE_CRITERIA.yaml: <PASS/FAIL>
- Top model QWK: <value>
- Leakage findings: <count>
- Diff vs previous cycle: <text>

## Timeout Policy
- 6h grace -> default Continue only for same-phase toy continuation.
- 6h~24h -> Pause according to configs/board_config.yaml decide_n_after_grace.
- Phase-up DECIDE ignores timeout and always pauses.

## Allowed Enum
- Continue
- Phase-up
- Stop"
```

## 12. Verification

Self-check the graph with:

```bash
python3 - <<'PY'
edges = [
    ("AUDIT", "SPLIT"),
    ("SPLIT", "FEATURE"),
    ("FEATURE", "MODEL"),
    ("MODEL", "EVAL"),
    ("MODEL", "REVIEW"),
    ("EVAL", "SYNTH"),
    ("REVIEW", "SYNTH"),
    ("SYNTH", "DECIDE"),
]
nodes = {n for edge in edges for n in edge}
visiting, visited = set(), set()
graph = {n: [] for n in nodes}
for a, b in edges:
    graph[a].append(b)

def dfs(node):
    if node in visiting:
        raise SystemExit("cycle found")
    if node in visited:
        return
    visiting.add(node)
    for child in graph[node]:
        dfs(child)
    visiting.remove(node)
    visited.add(node)

for node in nodes:
    dfs(node)
print("acyclic")
PY
```

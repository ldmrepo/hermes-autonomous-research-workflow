# MLflow Required Tag Audit

Source cycle: `cycle_3`
Acceptance evidence: `workspace/cycle_3/review/mlflow_tag_audit.md`, `workspace/cycle_3/review/review_manifest.json`

## Purpose

Check that all training runs for a cycle are registered in MLflow with required reproducibility and provenance tags.

## Required Tags

- `cycle_id`
- `kanban_task_id`
- `feature_provenance`

## Required Scope

- Check all M1-M4 x 5 fold runs for the target cycle.
- Confirm each run is associated with the expected cycle.
- Report missing tags as a hard gate issue for model/review remediation.

## Verification

```bash
python3 -c "import json; m=json.load(open('workspace/cycle_3/review/review_manifest.json')); assert m['verification_summary']['mlflow_runs_checked']==20; assert m['verification_summary']['mlflow_bad_required_tags']==0"
```

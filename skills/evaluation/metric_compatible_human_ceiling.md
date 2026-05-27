# Metric-Compatible Human Ceiling Comparison

Source cycle: `cycle_3`
Acceptance evidence: `workspace/cycle_3/eval/ceiling_comparison.md`, `workspace/cycle_3/eval/eval_manifest.json`

## Purpose

Compare model performance to human agreement without metric mismatch.

## Required Contract

- Model metric must be `QWK(model_pred, 3-rater-average)`.
- Human ceiling must use a compatible unit: `ICC(2,k)` or `mean_QWK(rater_i, 3-rater-average)`.
- Simple pairwise `QWK(rater_i, rater_j)` is not valid ceiling evidence.
- Report bootstrap CI, not only point estimates.
- In toy phase, ceiling excess is warn-only. The warning condition is `model_lower95 > ceiling_upper95`.

## Verification

```bash
python3 -c "import json; m=json.load(open('workspace/cycle_3/eval/eval_manifest.json')); assert m['bootstrap_ci']['model_metric']=='QWK(model_pred, 3-rater-average)'; assert '3-rater-average' in m['bootstrap_ci']['ceiling_metric']; assert m['human_ceiling']['b'] >= 1000"
```

# Location-Group Split Reverification

Source cycle: `cycle_3`
Acceptance evidence: `workspace/cycle_3/splits/split_manifest.yaml`, `workspace/cycle_3/review/leakage_reverification.md`

## Purpose

Verify toy-sample folds are isolated by `student.location` while preserving Type x grade-band stratification as far as the imbalanced sample permits.

## Required Contract

- Use `student.location` only as a grouping key.
- Do not use target scores to form folds.
- Confirm every row appears exactly once as validation across k folds.
- Confirm train and validation groups have zero overlap in every fold.
- Warn when `valid_n < 30`; do not relax group isolation to improve fold balance.

## Known Toy Constraint

The sample has 7 location groups with a max group size of 149 and rare Type x grade cells such as `글짓기|고등` with 2 rows. Exact stratification is not feasible for k=5, so segment metrics are descriptive.

## Verification

```bash
python3 -c "import yaml; m=yaml.safe_load(open('workspace/cycle_3/splits/split_manifest.yaml')); assert m['leakage_checks']['group_overlap_count_all_folds']==0; assert m['leakage_checks']['all_rows_appear_once_as_valid'] is True"
```

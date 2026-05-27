# Leakage-Free Text Feature Provenance

Source cycle: `cycle_3`
Acceptance evidence: `workspace/cycle_3/features/feature_provenance_manifest.json`, `workspace/cycle_3/review/feature_provenance_audit.md`

## Purpose

Build and review Korean essay-scoring features without using label-side fields or split-only student metadata.

## Required Contract

- Every feature entry must include `name`, `source`, `derived`, and `label_side`.
- `label_side` must be `false` for every model feature.
- Allowed feature sources are source essay text and allowed grade context only.
- `student.location` is split-only and must never appear in model features.
- Raw essay text may be used in memory for fit/transform but must not be copied into artifacts.

## Forbidden Inputs

- `essay_scoreT`, `essay_scoreT_avg`, rater scores, target columns
- paragraph annotations or paragraph counts from labels
- correction annotations or correction counts from labels
- rubric weights as model features
- prompt text, student date, student education, student reading, and `student.location`

## Verification

```bash
python3 -c "import json; m=json.load(open('workspace/cycle_3/features/feature_provenance_manifest.json')); assert m['label_side_feature_count']==0; assert all(f.get('label_side') is False for f in m['features']); assert all('source' in f and 'derived' in f for f in m['features'])"
```

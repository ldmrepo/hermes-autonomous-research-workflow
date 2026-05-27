# Escalation Matrix

Task: `t_7aa8b610`  
Date: 2026-05-27  
Scope: Cycle 2+ failure handling, resource control, and forbidden escalation boundaries

## 1. Purpose

This document defines how Hermes should respond when autonomous research tasks fail, stall, or approach policy boundaries.

The matrix protects two goals at the same time:

1. Keep routine research work moving without requiring a human for every transient failure.
2. Ensure safety-critical changes, leakage findings, privacy decisions, phase transitions, and production actions stop at an explicit human gate.

Cycle 1 showed the need for this distinction. T5 recovered after dependency and toy-policy clarification, while T7 correctly blocked the pipeline on a real leakage issue.

## 2. Failure Levels

Consecutive failures are counted per task or per logical task family when a task is decomposed into retries.

| Consecutive failures | Action | Owner | Notes |
| ---: | --- | --- | --- |
| 1 | Automatic retry | Same assignee | Suitable for transient environment, timeout, or command failure. Metadata must include the failed command and error summary. |
| 2 | Reassign or sub-decompose | Research Master / Project Planner | Reassign to a better profile or split the task into smaller implementation, verification, and report tasks. |
| 3 | Create Layer 3 human-gate task | Research Master | Mark the blocked task and create a decision task asking whether to change mutable policy, narrow scope, or stop. |

No failure level permits automatic edits to locked rules or automatic phase transition.

## 3. Failure-Type Routing

| Failure type | Example from Cycle 1 | Default response |
| --- | --- | --- |
| Missing dependency | T5 initially blocked when MLflow was unavailable. | Block with install/verification command; retry after dependency availability. |
| Schema mismatch | T1 found `student_school` absent and used human-approved `student.location` proxy after clarification. | Block for policy/schema decision when the rule and data disagree. |
| Policy ambiguity | T5 initially treated toy monotonic/ceiling warnings as hard blocks. | Block or ask for clarification; do not silently downgrade a hard rule. |
| Review finding | T7 found label-side feature leakage. | Hard block acceptance and require a fix cycle. |
| Small-sample instability | Toy fold sizes and ceiling CI are noisy. | Warn in toy phase; full phase requires CI-based hard gates. |
| Cron gap | T8 found cron trigger not observed. | Add a narrow Layer 2 validation task, separate from model acceptance. |

## 4. Resource Limits

The board must bound autonomous expansion so self-improvement cannot create uncontrolled work.

Recommended defaults:

| Setting | Draft value | Rationale |
| --- | ---: | --- |
| `max_concurrent_cycles` | 1 | Prevent overlapping research cycles from mixing artifacts or decisions. |
| `max_tasks_per_cycle` | 12 | Enough for audit, implementation, evaluation, review, reporting, and one follow-up decomposition. |
| `max_consecutive_failures` | 3 | Matches the escalation threshold for a human-gated policy decision. |
| `max_active_modeling_tasks` | 1 | Avoid concurrent writes to shared model artifacts in the current non-worktree setup. |
| `max_active_review_tasks` | 1 | Preserve a clear acceptance gate. |

If a cycle would exceed `max_tasks_per_cycle`, the Research Master should create a planning summary instead of spawning more tasks.

## 5. DECIDE Timeout Handling

DECIDE tasks must carry an explicit timeout block.

| Field | Allowed values | Recommended Cycle 2 value |
| --- | --- | --- |
| `human_decision_timeout` | Duration string such as `24h`, `72h`, `7d` | `72h` |
| `default_on_timeout` | `Continue` or `Stop` | `Stop` |
| `timeout_comment_required` | `true` or `false` | `true` |

Defaulting to `Continue` is allowed only for a maintenance-only cycle where every follow-up task is already within locked toy scope. It is not appropriate for phase-up, privacy, production, or acceptance-criteria decisions.

## 6. Layer 3 Gate

Layer 3 means the board wants to change its own mutable operating policy. It is not permission to edit locked rules.

A Layer 3 human-gate task must include:

1. The failed task id and failure count.
2. The current policy that caused the block or repeated failure.
3. The proposed mutable-policy change.
4. The risk of making the change.
5. A rollback path.
6. A verification command.

Allowed Layer 3 proposals:

| Proposal | Allowed? | Reason |
| --- | --- | --- |
| Lower `max_tasks_per_cycle` after overload | Yes | Operational safety default. |
| Reassign repeated feature tasks from `gauss` to `ada-lovelace` | Yes | Routing policy only. |
| Add a stale-task report cadence | Yes | Ops policy only. |
| Treat toy ceiling warnings as report-only | Only if already allowed by locked policy | Cannot contradict hard rules. |

## 7. Layer 3 and Layer 4 Forbidden Cases

The following cases must not be handled by autonomous mutable-policy edits.

| Case | Required handling |
| --- | --- |
| Champion alias replacement | Human approval and release/registry task only. |
| Student PII policy change | Human approval; security/privacy review required. |
| Hard Rule text modification | Human approval; never automatic. |
| Full dataset loading | Human phase-up approval first. |
| Transformer training | Human phase-up approval first. |
| External deployment | Human approval; deployment plan and canary verification required. |
| Final model registration | Human approval; forbidden in toy phase. |
| Acceptance criteria change | Human approval with decision log. |
| Leakage hard-block downgrade | Human approval; reviewer must sign off. |

Layer 4 auto-phase-transition remains forbidden. The board may prepare a phase-up recommendation, but it may not execute phase-up.

## 8. Block Metadata Requirements

Every blocked task must include enough metadata for a later agent or human to reproduce the issue.

Required fields:

| Field | Description |
| --- | --- |
| `reason` | Short human-readable block reason. |
| `failed_command` | Exact command that reproduced the failure, if applicable. |
| `artifact_paths` | Paths to reports, logs, manifests, or partial outputs. |
| `policy_reference` | Rule or document section that required blocking. |
| `next_action` | The smallest action that would unblock the task. |

Silent failure is not allowed. If the task cannot produce an artifact, it must still record a reason and command or evidence path.

## 9. Cycle 2 Escalation Defaults

Cycle 2 should start with these defaults:

| Policy | Value |
| --- | --- |
| Max concurrent cycles | 1 |
| Max tasks per cycle | 12 |
| Max consecutive failures | 3 |
| Human decision timeout | `72h` |
| Default on DECIDE timeout | `Stop` |
| Cron validation | Isolated Layer 2 task only |
| Phase-up | Human gated |

These defaults can be represented in `configs/board_config.yaml`.

## 10. Verification

This escalation matrix is verified by:

```bash
test -f docs/escalation_matrix_v_1_0.md
python3 -c "import pathlib; p=pathlib.Path('docs/escalation_matrix_v_1_0.md'); assert p.read_text().count('\\n## ') >= 6"
```

The matrix explicitly covers 1, 2, and 3 consecutive failures; resource limits; DECIDE timeout behavior; and forbidden Layer 3-4 cases.

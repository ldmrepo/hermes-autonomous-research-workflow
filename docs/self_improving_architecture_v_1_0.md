# Self-Improving Research Architecture

Task: `t_7aa8b610`  
Date: 2026-05-27  
Scope: Cycle 2+ architecture foundation for the Korean K-12 essay auto-scoring research board

## 1. Purpose

This document defines the bounded self-improving architecture for Cycle 2 and later Hermes Kanban research cycles.

The target operating model is:

1. Humans make one explicit cycle-level decision.
2. Hermes decomposes, schedules, runs, reviews, and reports the work between human decisions.
3. The board may improve task routing, retry strategy, and mutable operating policy within a constrained area.
4. The board must not silently change hard safety rules, phase gates, student privacy policy, model registry state, or deployment state.

This task combines the Research Master and Project Planner concerns from the full 30-role team plan while keeping the current six-profile system: `aristotle`, `tukey`, `spearman`, `gauss`, `ada-lovelace`, and `turing`.

## 2. Cycle 1 Evidence Baseline

Cycle 1 provides the evidence used to design Cycle 2+.

| Evidence | Observed behavior | Architecture implication |
| --- | --- | --- |
| T3 -> T3a | T3 split-policy work created child implementation task `t_07d2d658` for Gauss. | Layer 1 auto-decompose is already validated and may be reused. |
| T5 retry and unblock | T5 blocked on missing MLflow, then resumed after dependency availability and toy warn-only policy clarification. | Retry and block/unblock are valid operational controls, but dependency failures need clearer escalation rules. |
| T7 BLOCK | T7 found feature leakage from label-side `paragraph` and `correction` fields and blocked acceptance. | Review tasks must remain hard gates for acceptance, even when the workflow itself succeeds. |
| T8 validation | Hermes workflow validation passed 8/9; cron trigger was not observed. | Cycle 2 should introduce a small cron/event-triggered task without coupling it to model acceptance. |

The final Cycle 1 state is deliberately two-axis:

| Axis | Result | Source |
| --- | --- | --- |
| Pipeline acceptance | `BLOCK` | `workspace/final/final_report.md`, `workspace/review/review_report.md` |
| Hermes workflow validation | `PASS` | `workspace/final/hermes_validation.md`, `docs/hermes_validation_v_1_0.md` |

## 3. Layer Model

The architecture has four layers. Higher layers require stricter boundaries because they can change the behavior of future work.

| Layer | Name | Status | Autonomous scope | Human gate boundary |
| --- | --- | --- | --- | --- |
| Layer 1 | Auto-decompose | Validated | Decompose approved goals into role-specific child tasks, assign current profiles, link dependencies, and carry artifact requirements forward. | Cannot create tasks that change project hard rules, privacy policy, phase, production state, or model registry state. |
| Layer 2 | Cron/Event trigger | Not yet validated | Create recurring maintenance, stale-task, blocked-task, or report-refresh tasks from an approved template. | New cron classes, external notifications, and any task touching private data or external systems require human approval first. |
| Layer 3 | Self-modifying policy | Restricted future capability | Propose edits only to an explicit mutable policy surface, tentatively named `AGENTS_MUTABLE`, such as retry limits, default routing, or reporting cadence. | All policy changes are reviewable and cannot alter locked hard rules, PII policy, leakage gates, acceptance criteria, or phase gates. |
| Layer 4 | Auto-phase-transition | Forbidden | None. The board may prepare evidence and a decision task, but it may not move from toy to full phase by itself. | Human approval is mandatory for phase-up, production registration, full dataset loading, transformer training, deployment, and acceptance criteria changes. |

Layer 1 may run inside the current project rules. Layer 2 may be introduced in Cycle 2 only as a narrow validation task. Layer 3 is design-only until `AGENTS_LOCKED` and `AGENTS_MUTABLE` are physically separated and reviewed. Layer 4 remains disallowed.

## 4. Autonomy Boundaries

The board may do the following without a new human decision after a cycle goal is approved:

| Area | Allowed autonomous action |
| --- | --- |
| Task planning | Break a goal into audit, implementation, evaluation, review, and report tasks. |
| Role routing | Assign tasks to the existing six profiles according to current responsibilities. |
| Retry | Retry transient failures within configured consecutive-failure limits. |
| Sub-decompose | Split a failed implementation task into smaller bounded tasks after repeated failure. |
| Reporting | Write reports, manifests, decision summaries, and evidence commands. |
| Review enforcement | Block acceptance on leakage, missing MLflow, missing artifacts, or silent failure. |

The board must stop at a human gate for:

| Area | Required human decision |
| --- | --- |
| Phase transition | Toy -> full production-scale work. |
| Privacy | Any change to student PII handling or external LLM data policy. |
| Hard rules | Any edit to locked rules, leakage policy, or acceptance criteria. |
| Model registry | Final model registration, champion alias changes, or production release. |
| Data scale | Loading the full 50K dataset. |
| External systems | Deployment, public publishing, or new external integrations. |

## 5. DECIDE-N Task Pattern

Every cycle ends in a DECIDE task. The suffix `N` is the cycle number, for example `DECIDE-2`.

### Body Schema

```yaml
task_type: DECIDE-N
cycle_id: <string>
decision_owner: Human Approver
context:
  summary_report: <path>
  validation_report: <path>
  review_report: <path>
  mlflow_summary: <path optional>
options:
  - Continue
  - Phase-up
  - Stop
recommendation:
  selected_option: <Continue|Phase-up|Stop>
  rationale: <short text>
timeout:
  duration: <duration>
  default_on_timeout: <Continue|Stop>
post_decision_dispatch:
  Continue: <task-template-or-plan>
  Phase-up: <human-gated expansion plan>
  Stop: <archive/report-only plan>
```

### Option Semantics

| Option | Meaning | Allowed automatic follow-up |
| --- | --- | --- |
| Continue | Stay in the current phase and run the next improvement cycle. | Spawn pre-approved Cycle N+1 tasks from templates. |
| Phase-up | Move to a broader phase such as full dataset work. | Do not auto-run implementation; create a gated phase-up planning task. |
| Stop | Stop autonomous improvement for this project phase. | Archive or summarize; no new modeling tasks. |

The enum is exactly `Continue`, `Phase-up`, and `Stop`. Other labels should be rejected by the DECIDE task validator once implemented.

## 6. Dispatch Chain

The intended chain is:

1. Reporter builds cumulative evidence for the completed cycle.
2. Research Master creates `DECIDE-N` with the three-option enum and a recommendation.
3. Human Approver selects one option or lets the timeout policy apply.
4. If `Continue`, Research Master spawns the next bounded task graph.
5. If `Phase-up`, Research Master creates a human-gated planning package and stops short of implementation.
6. If `Stop`, Reporter writes final status and Ops may archive stale work.

The chain must preserve parent-child links so the board can prove which decision authorized each subsequent task.

## 7. Timeout Policy

Timeout behavior is a board-level policy, not a hard rule.

Recommended Cycle 2 draft:

| Field | Default | Rationale |
| --- | --- | --- |
| `human_decision_timeout` | `72h` | Long enough for a human cycle-level decision. |
| `default_on_timeout` | `Stop` | Safer when the decision may expand phase, data scope, or policy. |
| `Continue` timeout use | Allowed only for maintenance cycles | Use only when all follow-up tasks are already within the same phase and locked rules. |

For this project, `Stop` is the safer default because the blocked T7 leakage finding means automatic continuation should be explicit unless the next-cycle task graph is narrowly pre-approved.

## 8. AGENTS_LOCKED and AGENTS_MUTABLE

Long term, the current `AGENTS.md` should be split conceptually into two surfaces:

| Surface | Contents | Edit authority |
| --- | --- | --- |
| `AGENTS_LOCKED` | Hard rules, student privacy policy, leakage gates, toy/full phase boundaries, forbidden work, human approval requirements. | Human only. Board may cite but not modify. |
| `AGENTS_MUTABLE` | Routing preferences, retry thresholds, report cadence, task template refinements, non-safety defaults. | Board may propose; reviewer must approve before use. |

Until that split exists, `AGENTS.md` is treated as locked. This task does not modify it.

## 9. Cycle 2 Entry Criteria

Cycle 2 may start only if its task graph stays in toy scope and directly addresses the T7 leakage block.

Minimum entry checks:

1. No full dataset loading.
2. No transformer training.
3. No student PII policy change.
4. No model registration.
5. First implementation target fixes label-side feature leakage.
6. Review task re-verifies split and feature leakage before any acceptance report.
7. Cron/event trigger validation is isolated from modeling acceptance.

## 10. Verification

This architecture artifact is verified by:

```bash
test -f docs/self_improving_architecture_v_1_0.md
python3 -c "import pathlib; p=pathlib.Path('docs/self_improving_architecture_v_1_0.md'); assert p.read_text().count('\\n## ') >= 6"
```

Required evidence references included: T3 -> T3a, T5 retry/unblock, T7 BLOCK, and T8 8/9 Hermes validation.

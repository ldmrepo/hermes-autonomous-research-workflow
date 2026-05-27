# Cycle 1 작업체인 요약

> 문서 버전: v1.0 · 작성일: 2026-05-27 · 보드: `essay-auto-scoring-research-v2`
> 본 문서는 Cycle 1에 등록된 8개 task의 책임·의존성·산출·자가발전 메커니즘을 한 번에 요약한다.

---

## 1. 의존성 그래프

```
                    ┌─────────────────────┐
                    │ T-CYCLE-1-AUDIT     │  ready (자동 spawn)
                    │ tukey               │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ T-CYCLE-1-SPLIT     │
                    │ gauss               │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ T-CYCLE-1-FEATURE   │  ★ Hard Rule #9 강조
                    │ gauss               │  (label-side feature 0건)
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ T-CYCLE-1-MODEL     │
                    │ gauss               │  (M1~M4 × 5 fold)
                    └─────┬─────────┬─────┘
                          │ 병렬 fan-out
                ┌─────────▼──┐  ┌──▼──────────┐
                │ EVAL       │  │ REVIEW      │
                │ spearman   │  │ turing      │
                └─────────┬──┘  └──┬──────────┘
                          │ join  │
                          ▼       ▼
                    ┌─────────────────────┐
                    │ T-CYCLE-1-SYNTH     │  ★ 자가발전 핵심
                    │ aristotle           │  (다음 cycle 자체 등록)
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ DECIDE-1            │  ★ 인간 게이트
                    │ (unassigned=human)  │  ([Continue]/[Phase-up]/[Stop])
                    └──────────┬──────────┘
                               ▼
                    Cycle 2 chain (SYNTH-1이 자체 등록)
```

---

## 2. Task 목록 + ID 매핑

| Step | Task ID | 제목 | 담당 | Parent |
|---|---|---|---|---|
| 1 | `t_d731286c` | T-CYCLE-1-AUDIT | tukey | — |
| 2 | `t_769d2c8a` | T-CYCLE-1-SPLIT | gauss | AUDIT |
| 3 | `t_17813ef2` | T-CYCLE-1-FEATURE | gauss | SPLIT |
| 4 | `t_fe88cfdb` | T-CYCLE-1-MODEL | gauss | FEATURE |
| 5a | `t_221295da` | T-CYCLE-1-EVAL | spearman | MODEL |
| 5b | `t_53282c07` | T-CYCLE-1-REVIEW | turing | MODEL |
| 6 | `t_020af195` | T-CYCLE-1-SYNTH | aristotle | EVAL + REVIEW |
| 7 | `t_8756c008` | DECIDE-1 | (human) | SYNTH |

각 task `max-runtime`: AUDIT/SPLIT/FEATURE/EVAL/REVIEW = 20분, MODEL = 30분, SYNTH = 25분, DECIDE = (timeout는 board_config의 decide_timeout_policy 참조).
각 task `max-retries`: 1 (DECIDE는 default 2, 인간 task라 무관).

---

## 3. 각 Task 핵심 책임

| Step | 핵심 책임 | 주요 산출 (workspace/cycle_1/) | 핵심 룰 |
|---|---|---|---|
| AUDIT | Toy 342건 audit + leakage 사전 검사 | `audit/data_quality_report.md`, `leakage_audit.md`, `audit_manifest.json` (milestone hash 포함) | Hard Rule #10 (MILESTONE.md verbatim 재주입) |
| SPLIT | `student.location` GroupKFold(k=5) | `splits/fold_{0..4}.json`, `split_manifest.yaml`, `split_leakage_check.md` | Hard Rule #1 (leakage 금지) |
| FEATURE | **Leakage-free 피처** (1차 T7 재발 방지) | `features/X_{0..4}.npz`, `feature_config.yaml`, **`feature_provenance_manifest.json`** | **Hard Rule #9 (label-side 0건 강제)** |
| MODEL | M1~M4 × 5 fold = 20 MLflow run | `models/M{1..4}/`, `mlruns/` (tags: cycle_id, kanban_task_id, feature_provenance) | Hard Rule #3 (MLflow 등록), #11 (cost cap) |
| EVAL | Multi-axis + bootstrap CI ceiling 비교 | `eval/eval_report.md`, `segment_metrics.csv`, **`ceiling_comparison.md`** | Hard Rule #8 (metric 단위 일치 + CI) |
| REVIEW | 코드+leakage 재검증 | `review/review_report.md`, `leakage_reverification.md`, **`feature_provenance_audit.md`** | WRONG/FRAGILE/STYLE 분류 |
| SYNTH | 종합 + **다음 cycle 자체 등록** | `final/cycle_1_report.md`, `hermes_validation_cycle_1.md` | **자가발전 핵심 책임** |
| DECIDE-1 | 인간 결정 (board native) | (코멘트로 [Continue]/[Phase-up]/[Stop]) | board_config decide_timeout_policy |

---

## 4. 자가발전 메커니즘 (SYNTH의 책임)

```
SYNTH (Cycle 1) 실행 시 분기:

┌─ judgement != PASS_FINAL && acceptance_pass = false ─┐
│                                                       │
│  hermes kanban create로 Cycle 2 sub-task 7 + DECIDE-2 │
│  등록 (모두 todo, parent chain):                       │
│                                                       │
│    T-CYCLE-2-AUDIT  parent = DECIDE-1 ◀━ 핵심         │
│    T-CYCLE-2-SPLIT  parent = AUDIT-2                  │
│    T-CYCLE-2-FEATURE parent = SPLIT-2                 │
│    T-CYCLE-2-MODEL  parent = FEATURE-2                │
│    T-CYCLE-2-EVAL   parent = MODEL-2                  │
│    T-CYCLE-2-REVIEW parent = MODEL-2                  │
│    T-CYCLE-2-SYNTH  parent = EVAL-2 + REVIEW-2        │
│    DECIDE-2         parent = SYNTH-2                  │
│                                                       │
│  → DECIDE-1 done 시 AUDIT-2 auto-promote → chain 시작 │
└───────────────────────────────────────────────────────┘

┌─ judgement == PASS_FINAL/PASS_CANDIDATE ─┐
│                                           │
│  Cycle 2 task 등록 X                      │
│  → 사용자가 DECIDE-1에서                  │
│     [Phase-up] 또는 [Stop] 결정 대기       │
└───────────────────────────────────────────┘

공통:
- DECIDE-1 (t_8756c008)은 이미 등록되어 있음. SYNTH는 재등록 X
- DECIDE-1 코멘트로 cycle 1 결과 요약 첨부:
  - judgement enum
  - top model QWK
  - acceptance vs ACCEPTANCE_CRITERIA.yaml
  - leakage findings count
  - diff vs prior
  - skill candidates
- 외부 script 호출 0건 — hermes kanban create CLI inline만
```

---

## 5. 사용자 Action Point

전체 cycle에서 사용자 개입은 **DECIDE-1 1회**만:

```
1. 보드 UI 접속 → DECIDE-1 카드 클릭 (ready 상태)
2. SYNTH가 첨부한 요약 코멘트 확인
3. 코멘트 영역에 결정 명시:
   [Continue]   → Cycle 2 자동 진행
   [Phase-up]   → Phase 전환 (별도 결정)
   [Stop]       → 종결
4. 카드 상태 "완료"로 변경
```

→ Cycle 2 이후는 동일 패턴 (DECIDE-N 1클릭 / cycle).

---

## 6. 검증 룰 적용 (AGENTS.md v2)

| Hard Rule | 적용 위치 | 강제 강도 |
|---|---|---|
| #1 Leakage 금지 | SPLIT, REVIEW | hard-block |
| #2 PII 비전송 | 모든 task | hard-block |
| #3 MLflow 등록 | MODEL | hard-block |
| #4 Rubric 외부화 | FEATURE | hard-block |
| #5 단조성 | EVAL | toy=warn / full=block |
| #6 산출물 경로 + repro | 모든 task | hard-block |
| #7 silent fail 금지 | 모든 task | hard-block |
| #8 Ceiling 비교 | EVAL | toy=warn / full=block |
| **#9 Feature provenance** | **FEATURE, REVIEW** | **hard-block** (1차 T7 재발 방지) |
| **#10 Goal anchor** | **AUDIT** | **hard-block** (milestone hash) |
| **#11 Cost circuit breaker** | **MODEL** (특히) | **hard-block** (board_config 임계) |

---

## 7. 진행 상황 (작성 시점: 2026-05-27 18:10)

```
✓ T-CYCLE-1-AUDIT     done       산출 5개
✓ T-CYCLE-1-SPLIT     done       산출 7개
● T-CYCLE-1-FEATURE   running    Hard Rule #9 핵심 검증 중
◻ T-CYCLE-1-MODEL     todo
◻ T-CYCLE-1-EVAL      todo
◻ T-CYCLE-1-REVIEW    todo
◻ T-CYCLE-1-SYNTH     todo       (정정 코멘트 2개 첨부)
◻ DECIDE-1            todo
```

→ 사용자 개입 0회, gateway dispatcher 자동 spawn으로 chain 정상 진행 중.

---

## 8. 참고 문서

- `MILESTONE.md` — Hard Rule #10 source (AUDIT body에 verbatim 주입)
- `AGENTS.md` — 11 Hard Rules, When-X 섹션, DECIDE Task Pattern, Cycle Sub-task Pattern
- `configs/board_config.yaml` — 3-tier timeout, cost cap, terminal conditions
- `ACCEPTANCE_CRITERIA.yaml` — toy/mid/full 3단계 acceptance schema
- `docs/cycle_roadmap_v_1_0.md` — Phase 1-4 maturity model
- `docs/self_improving_architecture_v_1_0.md` — Layer 1-4
- `docs/escalation_matrix_v_1_0.md` — 실패 행동 매트릭스
- `docs/research/self_improving_long_running_research_v_1_0.md` — 외부 evidence

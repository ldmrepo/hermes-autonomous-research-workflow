# Cycle Task Chain v1.1 (자가발전 lifecycle)

> 문서 버전: v1.1 · 갱신일: 2026-05-27 · 보드: `essay-auto-scoring-research-v2`
> v1.0 (cycle_1_task_chain_v_1_0.md) 후속. Cycle 1 완료 + Cycle 2 진행 + Cycle 3+ 자율 패턴 확정.

---

## 1. 변경 사항 (v1.0 → v1.1)

| 항목 | v1.0 | v1.1 |
|---|---|---|
| Task 명명 | 영어만 (T-CYCLE-1-AUDIT) | **Mixed** (T-CYCLE-1-AUDIT: 데이터 검증) |
| AGENTS.md "When Synthesizing" | PASS_CANDIDATE 미등록 (결함) | **PASS_CANDIDATE도 Cycle N+1 등록** (옵션 #1) |
| Cycle 1 결과 | (진행 중) | **PASS_CANDIDATE, leakage 0건, M4 QWK 0.2402** |
| Cycle 1 → 2 bridge | — | **BOOTSTRAP-2** 1회성 helper (v2→v3 정책 차이) |
| Cycle 2 | (미시작) | **자동 시작 (AUDIT-2 running)** |
| 자가발전 검증 | 가설 | **실증 (사용자 [Continue] 1클릭으로 Cycle 2 자동 시작)** |

---

## 2. 보드 현황 (Cycle 1 + Cycle 2)

```
✓ Cycle 1 (8 task, 모두 done)
   ├ T-CYCLE-1-AUDIT: 데이터 검증              tukey       t_d731286c
   ├ T-CYCLE-1-SPLIT: 분할 정책                gauss       t_769d2c8a
   ├ T-CYCLE-1-FEATURE: 피처 엔지니어링        gauss       t_17813ef2
   ├ T-CYCLE-1-MODEL: 베이스라인 학습          gauss       t_fe88cfdb
   ├ T-CYCLE-1-EVAL: 다축 평가                 spearman    t_221295da
   ├ T-CYCLE-1-REVIEW: 코드/누수 리뷰          turing      t_53282c07
   ├ T-CYCLE-1-SYNTH: 종합 + 다음 cycle 등록   aristotle   t_020af195
   └ DECIDE-1: 인간 결정 (Cycle 1)             human       t_8756c008

✓ Bridge (v2→v3 1회성)
   └ T-CYCLE-BOOTSTRAP-2: Cycle 2 sub-task 등록  aristotle  t_dad19a09

▶ Cycle 2 (8 task, 진행 중)
   ├ T-CYCLE-2-AUDIT: 데이터 검증              tukey       t_2cf26996  ◀ running
   ├ T-CYCLE-2-SPLIT: 분할 정책                gauss       t_68c5fd8a
   ├ T-CYCLE-2-FEATURE: 피처 엔지니어링        gauss       t_0312fd2c
   ├ T-CYCLE-2-MODEL: 베이스라인 학습          gauss       t_07fdb5e7
   ├ T-CYCLE-2-EVAL: 다축 평가                 spearman    t_21aadeeb
   ├ T-CYCLE-2-REVIEW: 코드/누수 리뷰          turing      t_10323bd7
   ├ T-CYCLE-2-SYNTH: 종합 + 다음 cycle 등록   aristotle   t_896e4353
   └ DECIDE-2: 인간 결정 (Cycle 2)             human       t_1fa8e935
```

---

## 3. 의존성 그래프 (cycle 간 연결)

```
Cycle 1                                  Cycle 2                            Cycle 3+
─────────                                ─────────                          ─────────
AUDIT → SPLIT → FEATURE → MODEL          AUDIT → SPLIT → FEATURE → MODEL    동일 패턴
                       ↓ fan-out                                ↓ fan-out
                  EVAL || REVIEW                          EVAL || REVIEW
                       ↓ join                                  ↓ join
                  SYNTH                                   SYNTH
                    ↓                                       ↓
                  DECIDE-1 ─[Continue]─▶ BOOTSTRAP-2  ▶  DECIDE-2 ─[Continue]─▶ Cycle 3 AUDIT
                                          (1회성)              ▲
                                            │                 │
                                            ▼                 │
                                       Cycle 2 AUDIT          │
                                          (parent=DECIDE-1)   │
                                                              │
                                       SYNTH-2가 Cycle 3 자체 등록 (BOOTSTRAP 없음)
                                                              │
                                                       Cycle 3 AUDIT (parent=DECIDE-2)
```

**핵심**: Cycle 1 → 2는 BOOTSTRAP 경유 (예외), Cycle 2 → 3부터는 SYNTH 직접 (정상).

---

## 4. Cycle 1 검증 결과 (PASS_CANDIDATE)

| 항목 | 값 |
|---|---|
| judgement | PASS_CANDIDATE |
| acceptance_pass | true |
| top model | M4 LightGBM QWK 0.2402 (95% CI 0.1611-0.3139) |
| **Leakage findings** | **0** (Hard Rule #9 통과, 1차 사이클 T7 재발 방지 성공) |
| label-side feature | 0 |
| Human ceiling | QWK 0.5985 (95% CI 0.5462-0.6465) — 모델이 ceiling 아래, 정상 |
| diff vs 1차 사이클 | label-side leakage 해소 + CI-aligned ceiling 비교 추가 |
| skill candidates | 3개 (text_only_dense_features, feature_provenance_audit, bootstrap_ceiling_comparison) |
| MLflow runs | 40 |

---

## 5. 자가발전 메커니즘 (v3)

### AGENTS.md "When Synthesizing" 분기

```
judgement                  Cycle N+1 등록    DECIDE-N 옵션
─────────                  ────────────    ──────────────
PASS_FINAL                 X                Phase-up 또는 Stop만 (production 게이트)
PASS_CANDIDATE             ✓ 등록           Continue / Phase-up / Stop 모두 가능 ← 옵션 #1
FAIL_RETRY_HPO             ✓ 등록           Continue 권장 (개선 cycle)
FAIL_REBUILD_FEATURES      ✓ 등록           Continue
FAIL_REVIEW_LABELS         ✓ 등록           Continue
FAIL_CHANGE_MODEL          ✓ 등록           Continue
FAIL_NEED_MORE_DATA        ✓ 등록           Continue 또는 Phase-up
FAIL_STOP_NO_GAIN          X                Stop 권장
```

### Cycle N+1 등록 사양 (SYNTH 책임)

```python
# pseudo-code (SYNTH가 hermes kanban create로 인라인 호출)
for step in ["AUDIT: 데이터 검증", "SPLIT: 분할 정책", ...]:
    hermes kanban create f"T-CYCLE-{N+1}-{step}" \
        --assignee <profile> \
        --workspace dir:... \
        --parent <prev_step_or_DECIDE_N> \
        --body <input_context + MILESTONE.md verbatim if AUDIT>

# 핵심 의존성
T-CYCLE-(N+1)-AUDIT: parent = DECIDE-N
```

---

## 6. 사용자 부담 (cycle별)

| Cycle | 인간 액션 | 자동 |
|---|---|---|
| Setup (1회) | AGENTS.md, MILESTONE.md, board_config.yaml, Cycle 1 task 8개 등록 | — |
| Cycle 1 진행 | 0 | chain 자동 |
| Cycle 1 종료 → 2 시작 | **DECIDE-1 [Continue] 1클릭** | BOOTSTRAP-2 → Cycle 2 8개 등록 |
| Cycle 2 진행 | 0 | chain 자동 |
| Cycle 2 종료 → 3 시작 | **DECIDE-2 1클릭** | SYNTH-2가 Cycle 3 자체 등록 |
| Cycle 3+ | **DECIDE-N 1클릭/cycle** | 동일 |

→ 24시간 운영 시 cycle당 1클릭, 그 외 시스템 자율.

---

## 7. 검증된 자가발전 동작 8가지

| # | 항목 | Cycle 1 evidence | Cycle 2+ |
|---|---|---|---|
| 1 | Board native chain auto-promote | ✓ AUDIT→SYNTH 자동 spawn | ✓ AUDIT-2 spawn 확인 |
| 2 | Profile 자동 routing | ✓ 6 profile 분배 | ✓ |
| 3 | Full-trace propagation | ✓ workspace 산출 input context | ✓ |
| 4 | Hard Rule #9 (Feature provenance) | ✓ leakage 0 | (검증 예정) |
| 5 | Hard Rule #10 (Goal anchor) | ✓ MILESTONE hash 기록 | (검증 예정) |
| 6 | SYNTH 자체 분기 | ✓ PASS_CANDIDATE 정확 분기 | (Cycle 2 SYNTH 검증) |
| 7 | DECIDE 코멘트 자동 첨부 | ✓ cycle 결과 + 추천 | (Cycle 2 검증) |
| 8 | Cycle 간 자동 bridge | ✓ DECIDE-1→BOOTSTRAP-2→Cycle 2 | ✓ DECIDE-2→Cycle 3 SYNTH 직접 |

---

## 8. 종료 조건 (board_config.yaml `terminal_conditions`)

| 조건 | 동작 |
|---|---|
| `acceptance_pass` | 최종 acceptance 충족 시 → 종료 + T-TERMINAL 인간 알림 |
| `max_cycles_reached` (30) | 누적 cycle 한도 도달 |
| `explicit_stop_decided` | 사용자 [Stop] 선택 |
| `max_consecutive_failures_reached` (3) | 연속 cycle fail 한도 |

종료 시 docs/ + workspace/ + mlruns/ + DB 모두 보존. 보드는 archive 가능.

---

## 9. 보드 가독성 정책 (향후 적용 권고)

Cycle N 누적 시 done task 폭증 → 가독성 ↓. 권장 정책 (AGENTS.md 추가 필요):

```
SYNTH-(N) 완료 시 → Cycle (N-2) 이전 모든 done task를
hermes kanban archive로 자동 정리.
(MLflow run, workspace artifact, docs는 보존 — board view만 정리)
```

→ 보드에 항상 최근 2 cycle만 표시.

---

## 10. 참고 문서

- `MILESTONE.md` — Hard Rule #10 goal anchor source
- `AGENTS.md` — v3 (PASS_CANDIDATE 등록 + mixed naming)
- `configs/board_config.yaml` — 3-tier timeout, cost cap, terminal conditions
- `ACCEPTANCE_CRITERIA.yaml` — toy/mid/full 3단계 acceptance
- `docs/cycle_roadmap_v_1_0.md` — Phase 1-4 maturity model
- `docs/self_improving_architecture_v_1_0.md` — Layer 1-4
- `docs/escalation_matrix_v_1_0.md` — 실패 행동 매트릭스
- `docs/research/self_improving_long_running_research_v_1_0.md` — 외부 evidence
- `docs/cycle_1_task_chain_v_1_0.md` — 본 문서의 v1.0 (Cycle 1 초기 등록 기준)

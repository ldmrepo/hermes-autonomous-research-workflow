# PPT 슬라이드 원고 v1.1 (자가발전 architecture 확장본)

> **사용 방법**: `ppt_slides_v_1_0.md` (Part 1-6, 38 slides + 부록 4) 뒤에 본 문서 (Part 7-9, +17 slides + 부록 1)를 **append**. 총 55 slides + 5 부록 = 60 slides. 1.5시간 강의 또는 60분 + Q&A.
> **변경 사유**: 1차 검증(workflow 9/9 중 8) + 자가발전 architecture 실증(Cycle 1+2 자율 chain) + 외부 evidence 차용으로 본 확장.
> **테마**: v1.0 동일 (다크 네이비 #0E1525 + 시안 #22D3EE + 라임 #A3E635, Pretendard + JetBrains Mono, minimal flat isometric).

---

## 변경 요약 표 (발표자 cheat sheet)

| Part | v1.0 → v1.1 |
|---|---|
| 1-5 | 변경 없음 (1차 사이클 evidence) |
| 6 (BEYOND) | **Part 9로 이동 + 확장 (3→5 slides)** |
| **신규 Part 7** | **Self-Improving Architecture (8 slides)** |
| **신규 Part 8** | **Cycle 2+ Autonomous Loop (6 slides)** |
| Part 9 | Production Readiness (확장) |
| 부록 | A5 추가 (자가발전 패턴 카드) |

---

# Part 7. Self-Improving Architecture (8 slides)

## Slide 39 — 1차 사이클의 미해결 과제

### 슬라이드 내용
**1차 검증 후 남은 격차 3가지**

1. **Cron trigger 미검증** — 9-Point 중 1개 NOT_OBSERVED
2. **인간 trigger 과다** — 매 task마다 사람이 dispatch 또는 검토
3. **Cycle 반복 메커니즘 부재** — 1 cycle만 검증, 자동 반복 X

→ 진정한 long-running 검증은 **N cycle 자율 반복**

### 페이지 디자인 프롬프트
```
3 row layout, each row showing a "gap" with red strikethrough icon.
Row 1: clock with X mark (cron not observed)
Row 2: many human-hand icons across the timeline (manual triggers)
Row 3: single cycle loop with question mark (no auto-repeat)
Bottom callout in lime: "→ 진정한 long-running = N cycle 자율 반복"
Dark navy background.
```

---

## Slide 40 — 자가발전 4-Layer 모델

### 슬라이드 내용

```
Layer 4 ─ Auto-phase-transition       ❌ 금지 (인간 게이트 필수)
Layer 3 ─ Self-modifying policy       △ 제한적 (MUTABLE만)
Layer 2 ─ Cron/Event trigger          ✓ 자동 (parent→child auto-promote)
Layer 1 ─ Auto-decompose               ✓ 자동 (T3a 등 자율 생성)
```

**원칙**: 위로 갈수록 자동화 위험 증가. 24h 운영은 Layer 1+2까지만.

### 페이지 디자인 프롬프트
```
Vertical pyramid/ladder with 4 layers stacked.
Layer 1 (bottom) = lime (safe), Layer 4 (top) = red (forbidden).
Each layer has icon: gear (1), clock (2), wrench (3), warning sign (4).
Right side: "24h auto = L1+L2 only" annotation.
Dark navy background.
```

---

## Slide 41 — DECIDE-N 패턴 (인간 결정 게이트)

### 슬라이드 내용

```
T-CYCLE-N-SYNTH done
   ↓
DECIDE-N (ready, unassigned=human)
   ├─ 사용자가 코멘트로 결정: [Continue] / [Phase-up] / [Stop]
   └─ 카드 "완료" → child auto-promote
        ↓
   Cycle N+1 첫 sub-task auto-spawn
```

**핵심**: assignee 없는 ready task = **board-native 인간 게이트**. dispatcher가 spawn 안 함.

### 페이지 디자인 프롬프트
```
Vertical sequence with 4 boxes.
Middle box (DECIDE-N) highlighted with golden border + person icon + 3 button preview.
Arrows showing "human comment + complete → child auto-promote".
Right side annotation: "assignee 없음 = human-only gate".
Dark navy background.
```

---

## Slide 42 — SYNTH 자체 등록 책임 (옵션 #1)

### 슬라이드 내용
**Cycle N의 SYNTH가 직접 Cycle N+1 sub-task 등록 (script 없음)**

```
judgement           Cycle N+1 등록    DECIDE 가능 옵션
─────────           ────────────    ──────────────
PASS_FINAL          X                Phase-up / Stop
PASS_CANDIDATE      ✓               Continue / Phase-up / Stop  ★ 옵션 #1
FAIL_*              ✓               Continue / (Stop)
```

→ SYNTH의 책임: 평가 + 다음 cycle 8 task `hermes kanban create` × 8

### 페이지 디자인 프롬프트
```
3-row table with judgement enum, registration, options.
PASS_CANDIDATE row highlighted with gold star + "옵션 #1" badge.
Below table: terminal mockup showing 8 hermes kanban create commands.
Caption: "Script-free, board-native dependency only".
Dark navy background.
```

---

## Slide 43 — Cycle 간 의존성 chain (board native)

### 슬라이드 내용

```
Cycle N                          Cycle N+1
─────────                        ─────────
... SYNTH ─→ DECIDE-N ─→ AUDIT-(N+1) ─→ SPLIT-(N+1) ...
              ▲ (사용자 1클릭)    ▲ (parent=DECIDE-N)
              │                  │
              human gate         auto-promote on DECIDE done
```

cron 없음. 사용자 trigger 없음. 오직 **parent done → child auto-promote**.

### 페이지 디자인 프롬프트
```
Horizontal flow diagram spanning the slide.
DECIDE-N highlighted as the only human-gate point (person icon).
All other transitions labeled "auto-promote".
Bottom callout: "Zero script, zero cron, board-native only".
Dark navy background.
```

---

## Slide 44 — 외부 evidence (Voyager / AutoGPT / Cognition)

### 슬라이드 내용

| 프로젝트 | 패턴 | 우리 적용 |
|---|---|---|
| **Voyager** (NeurIPS 2023) | Verified skill library + semantic retrieve | Cycle 3+ skill_candidates 누적 (예정) |
| **AutoGPT** | Infinite verification loop (실패) | 회피: max-retries + identical-action detection |
| **Cognition Devin** | "Don't Build Multi-Agents" + checkpoint commit | 6 profile 유지 + git worktree per task |
| **Anthropic Multi-Agent** | Lead → sub-agent + full-trace propagation | SYNTH가 sub-task body에 부모 산출 명시 |
| **Replit Agent 3** | Verifier role + max-autonomy 200분 | turing profile + cost circuit breaker |

### 페이지 디자인 프롬프트
```
5-row comparison table on dark navy.
Each row has small project logo, pattern, and "우리 적용" column with our profile icons.
Cyan highlights on adopted patterns.
Bottom URL strip with arxiv/blog links in monospace.
```

---

## Slide 45 — Cost circuit breaker + Goal anchor

### 슬라이드 내용
**2개 외부 권고 차용 (Layer 0 안전)**

```yaml
# board_config.yaml
cost_circuit_breaker:                          # sanj.dev 권고
  max_tokens_per_cycle: 500000
  max_token_velocity_per_min: 10000
  max_usd_per_cycle: 20.0
  on_breach: pause_and_notify

goal_anchor:                                   # arXiv 2505.02709 권고
  enabled: true
  inject_into_first_subtask: true
  source: MILESTONE.md
```

→ **silent cost runaway 방지 + goal drift 방지**

### 페이지 디자인 프롬프트
```
Split layout. Left: yaml code block highlighted with cost_circuit_breaker.
Right: yaml code block highlighted with goal_anchor.
Below: 2 icons (dollar shield + anchor compass) with captions.
Dark navy background, code in monospace.
```

---

## Slide 46 — AGENTS.md v3 (Hard Rule 9-11 신설)

### 슬라이드 내용

| 신설 Rule | 내용 | 1차 evidence 활용 |
|---|---|---|
| **#9 Feature provenance** | 모든 feature에 source/derived/label-side 표시, label-side 사용 시 자동 block | T7이 발견한 leakage 재발 방지 |
| **#10 Goal anchor 재주입** | 매 cycle 첫 sub-task에 MILESTONE.md verbatim 주입 | Goal drift 방지 |
| **#11 Cost circuit breaker** | board_config 임계 도달 시 cycle pause + 인간 알림 | silent runaway 방지 |

기존 Rule 5/8은 처음부터 toy=warn / full=block 분기.

### 페이지 디자인 프롬프트
```
3 stacked rule cards, each with rule number badge (#9 #10 #11) in cyan.
Each card: rule title (bold), one-line description, "→ 1차 evidence" link.
Background dark navy, cards have subtle borders.
```

---

# Part 8. Cycle 2+ Autonomous Loop (6 slides)

## Slide 47 — v2 보드 setup (한글 mixed naming)

### 슬라이드 내용

```
Board: essay-auto-scoring-research-v2 (신규)
   ├ AGENTS.md v3 (11 Hard Rules, mixed naming 규칙)
   ├ MILESTONE.md (goal anchor source)
   ├ configs/board_config.yaml (cost + timeout + terminal)
   └ docs/research/ (외부 evidence)

Task 명명:
   T-CYCLE-1-AUDIT: 데이터 검증     ◀ mixed: 영어 prefix + 한글 설명
   T-CYCLE-1-SPLIT: 분할 정책
   ...
   DECIDE-1: 인간 결정 (Cycle 1)
```

### 페이지 디자인 프롬프트
```
Folder tree mockup on left showing setup files.
Right side: kanban card mockup with mixed Korean+English title.
Top label: "Board v2 = 자가발전 사이클 신규 시작".
Dark navy background.
```

---

## Slide 48 — Cycle 1 자율 chain 실행

### 슬라이드 내용

```
[17:56] AUDIT spawn (gateway dispatcher 자동)
[17:58] AUDIT done → SPLIT auto-promote
[18:01] SPLIT done → FEATURE auto-promote
[18:05] FEATURE done → MODEL auto-promote
[18:18] MODEL done → EVAL + REVIEW 병렬 spawn
[18:24] EVAL + REVIEW done → SYNTH auto-promote
[18:25] SYNTH start
[18:29] SYNTH done → DECIDE-1 ready
```

→ **34분 동안 사용자 개입 0회**

### 페이지 디자인 프롬프트
```
Vertical timeline with timestamps + cards transitioning.
All transitions marked "auto" in cyan.
At top: "Human action: 0".
Final card (DECIDE-1) marked with golden border + "사용자 대기 시작".
Dark navy background.
```

---

## Slide 49 — Cycle 1 결과 (PASS_CANDIDATE, leakage 0)

### 슬라이드 내용

| 항목 | 값 | 변화 (vs 1차) |
|---|---|---|
| judgement | **PASS_CANDIDATE** | (신규 평가) |
| top model QWK | **0.2402** (95% CI 0.16~0.31) | bootstrap CI 첫 적용 |
| **Leakage findings** | **0** | T7 발견 0 (1차 재발 방지 성공) |
| label-side feature | 0 | Hard Rule #9 통과 |
| Human ceiling | 0.5985 (95% CI 0.55~0.65) | metric 단위 일치 (Hard Rule #8) |
| MLflow runs | 40 | cycle_id tag 적용 |
| skill candidates | 3개 | Voyager-style 첫 후보 |

### 페이지 디자인 프롬프트
```
Result card with PASS_CANDIDATE stamp in lime.
Below: 7-row metrics table.
Key rows highlighted: "Leakage findings = 0" (lime), "label-side = 0" (lime).
Right side: small Cycle 1 vs 1차 사이클 diff badges.
Dark navy background.
```

---

## Slide 50 — BOOTSTRAP-2 bridge (v2→v3 1회성)

### 슬라이드 내용
**왜 BOOTSTRAP이 필요했나**

```
Cycle 1 SYNTH 실행 시: AGENTS.md v2 (PASS_CANDIDATE 미등록)
   ↓ SYNTH done
사용자가 AGENTS.md를 v3으로 보강 (PASS_CANDIDATE 등록)
   ↓
그러나 본 SYNTH는 이미 done → 새 정책 적용 못 함
   ↓ 해결
T-CYCLE-BOOTSTRAP-2 (aristotle) 등록 → DECIDE-1 done 후 spawn
   ↓ BOOTSTRAP-2가 Cycle 2 sub-task 8개 등록
Cycle 2 chain 자동 시작
```

→ **본 1회성, Cycle 3+는 SYNTH 직접 등록**

### 페이지 디자인 프롬프트
```
Vertical flow diagram showing the v2→v3 policy gap and BOOTSTRAP-2 as a bridge.
BOOTSTRAP-2 box marked "1회성 (one-shot)" with bridge icon.
Caption: "Cycle 3+ 부터 BOOTSTRAP 없음".
Dark navy background.
```

---

## Slide 51 — DECIDE-1 [Continue] → Cycle 2 자동 시작

### 슬라이드 내용
**사용자 단일 action**

```
사용자 UI action:
1. DECIDE-1 카드 클릭
2. 코멘트: [Continue] - PASS_CANDIDATE 상태에서 Cycle 2 진행
3. "완료" 버튼 클릭

자동 후속 (0 사용자 액션):
4. DECIDE-1 done
5. BOOTSTRAP-2 auto-promote → spawn (~3분)
6. BOOTSTRAP-2 done → Cycle 2 8 task 등록 완료
7. T-CYCLE-2-AUDIT auto-promote (parent=DECIDE-1, 이미 done) → spawn
8. Cycle 2 chain 자동 진행
```

→ **사용자 1클릭 = 24시간 chain trigger**

### 페이지 디자인 프롬프트
```
Split layout. Left: 3 steps (human, with person icon).
Right: 5 steps (auto, with gear icons + arrows).
Top callout: "1 click → 24h chain".
Dark navy background, lime for human steps, cyan for auto.
```

---

## Slide 52 — Cycle 3+ 완전 자율 (BOOTSTRAP 없음)

### 슬라이드 내용

| Cycle | BOOTSTRAP | 사용자 action |
|---|---|---|
| 1 | — (수동 setup) | DECIDE-1 1클릭 |
| 2 | ✓ (v2→v3 1회성) | DECIDE-2 1클릭 |
| **3+** | **❌ (SYNTH 직접 등록)** | **DECIDE-N 1클릭/cycle** |

```
Cycle 3 자동 흐름:
  SYNTH-2 (옵션 #1) → Cycle 3 sub-task 8개 자체 등록
       ↓
  DECIDE-2 [Continue]
       ↓ done
  AUDIT-3 (parent=DECIDE-2) auto-promote → spawn
       ↓
  Cycle 3 chain 자동 진행
       ↓
  DECIDE-3 → 사용자 1클릭 → Cycle 4 ...
```

### 페이지 디자인 프롬프트
```
3-row table at top.
Cycle 3+ row highlighted with infinity icon.
Below: small DAG showing Cycle 2 → 3 → 4 → ... with single human gate per cycle.
Dark navy background.
```

---

# Part 9. Production Readiness (5 slides, 기존 Part 6 확장)

## Slide 53 — 한계 (24h 운영 진입 전 보완 필요)

### 슬라이드 내용

| # | 한계 | Mitigation |
|---|---|---|
| 1 | Verifier(turing)가 generator와 동일 모델 → self-refine 한계 | 이질적 critic (예: 작은 fast model로 sanity) |
| 2 | Identical-action detection 부재 (VS Code Copilot 2080회 재편집 류) | Cycle 2+ SYNTH 책임 추가 |
| 3 | DB 손상 시 자동 복구 X | systemd hook으로 REINDEX 자동화 |
| 4 | Skill library semantic index 미구현 (Cycle 3+ 예정) | Voyager 패턴 구현 |
| 5 | DECIDE timeout 처리 미실제 작동 검증 | Cycle 2-3에서 6h+ 무응답 시나리오 검증 |

### 페이지 디자인 프롬프트
```
5-row limit cards with amber warning icon.
Right column shows mitigation in cyan with checkmark.
Title: "24h 진입 전 최종 점검 5".
Dark navy background.
```

---

## Slide 54 — Production 진입 게이트 (Phase 2/3/4 maturity)

### 슬라이드 내용

```
Phase 1 (Toy, 현재) ── 검증 완료
   ├ Sample 342건, light models
   ├ Hard Rule 5/8 toy=warn
   └ Cycle 1+2 acceptance PASS_CANDIDATE

Phase 2 (Mid-scale) ── 다음 milestone
   ├ Sample 5K, k=10
   ├ KLUE-RoBERTa 추가
   └ Hard Rule 모두 hard-block 격상

Phase 3 (Full)
   ├ Sample 50K
   └ Ensemble + bias audit

Phase 4 (Production)
   └ Champion alias + 외부 배포 (인간+법무 게이트)
```

### 페이지 디자인 프롬프트
```
Vertical 4-step staircase ascending right.
Phase 1 (lime check), Phase 2 (cyan target), Phase 3-4 (white outline).
Each step has "exit criteria" annotation.
Dark navy background.
```

---

## Slide 55 — 24h 무인 운영 운용 패턴

### 슬라이드 내용

```
새벽 (사람 자는 동안):
   Cycle N spawn → 자율 chain 30-40분
   → DECIDE-N ready
   → board_config.yaml decide_n_grace_period (6h) 시작

아침:
   사용자가 DECIDE-N 확인 → 1클릭

오후/저녁:
   Cycle N+1 spawn → 자율 chain
   → DECIDE-(N+1) ready → 사용자 1클릭

비상:
   cost_circuit_breaker 초과 → cycle 자동 pause
   → T-TERMINAL 자동 생성 → 사용자 알림
```

→ **하루 사용자 부담: DECIDE 1-2클릭 + 비상 알림 대응**

### 페이지 디자인 프롬프트
```
24-hour clock face with annotations at key hours.
Person icons marked only at 9am (DECIDE click) and 6pm (DECIDE click).
All other hours marked "auto" with gear icons.
Center: "1-2 clicks / day".
Dark navy background.
```

---

## Slide 56 — 다음 milestone (Mid-scale 5K 진입)

### 슬라이드 내용

```
Cycle 1-N 토이 완료 (Cycle 1 PASS_CANDIDATE 달성)
   ↓
사용자 DECIDE-N [Phase-up] 선택
   ↓
T-PHASE-MIGRATE-MID 자동 생성 (인간 게이트 카드)
   ↓
인간 승인 → mid-scale 설정 전환:
   ├ AGENTS.md Toy Scope 섹션 삭제
   ├ Hard Rule 모두 hard-block 격상
   ├ Sample 5K (50K 中 stratified subsample)
   ├ KLUE-RoBERTa profile (transformer-modeler) 추가
   └ DVC + Optuna 도입
   ↓
Cycle (N+1)부터 mid-scale 자율 진행
```

### 페이지 디자인 프롬프트
```
Migration flow diagram. Toy phase (light) → Phase-up gate (golden) → Mid-scale (cyan).
Configuration delta panel showing AGENTS.md/profile/data changes.
Dark navy background.
```

---

## Slide 57 — Q&A / 참고자료 (확장)

### 슬라이드 내용
**산출물**
- `docs/cycle_task_chain_v_1_1.md` — Cycle 1+2 lifecycle
- `docs/self_improving_architecture_v_1_0.md` — Layer 1-4
- `docs/escalation_matrix_v_1_0.md` — 실패 행동
- `docs/research/self_improving_long_running_research_v_1_0.md` — 외부 evidence
- `MILESTONE.md` — Hard Rule #10 source
- `configs/board_config.yaml` — terminal + cost cap

**1차 사이클 evidence (v1.0 PPT 참조)**
- `docs/hermes_validation_v_1_0.md`
- `docs/final_report_v_1_0.md`
- `docs/ppt_slides_v_1_0.md`

**참고**
- Hermes 공식 docs: hermes-agent.nousresearch.com
- 외부 리서치 URL 20+ (research/ 보고서 내)

**감사합니다 — 질문 환영**

### 페이지 디자인 프롬프트
```
Closing slide with large "감사합니다" in cyan.
3-column layout of links/paths.
Subtle Hermes logo watermark.
Dark navy background.
```

---

# 부록 A5 — 자가발전 패턴 카드 (요약)

### 슬라이드 내용

```
┌─────────────────────────────────────────────────────┐
│  Hermes Self-Improving Loop Pattern (한 장 요약)    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Setup (1회)                                        │
│   ├ AGENTS.md (Hard Rule 11)                        │
│   ├ MILESTONE.md (goal anchor)                      │
│   ├ board_config.yaml (cost + timeout + terminal)   │
│   └ Cycle 1 sub-task 8개 등록                       │
│                                                     │
│  Cycle N (자율)                                     │
│   ├ chain: AUDIT→SPLIT→FEATURE→MODEL                │
│   │         → (EVAL || REVIEW) → SYNTH              │
│   └ SYNTH가 Cycle N+1 sub-task 자체 등록            │
│                                                     │
│  DECIDE-N (인간, cycle당 1클릭)                     │
│   ├ [Continue] → Cycle N+1 chain 시작              │
│   ├ [Phase-up] → Phase 진입 인간 게이트            │
│   └ [Stop] → 종결                                  │
│                                                     │
│  Terminal (자동 종료)                               │
│   ├ acceptance_pass                                 │
│   ├ max_cycles_reached                              │
│   ├ explicit_stop_decided                           │
│   └ max_consecutive_failures_reached                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 페이지 디자인 프롬프트
```
Single large boxed diagram covering full slide.
4 sections: Setup (top), Cycle (middle, with 2 sub-rows), DECIDE (bottom-left), Terminal (bottom-right).
Each section bordered, with icons (gear/cycle/person/stop).
Title at top: "자가발전 Loop 한 장 요약".
Dark navy background, sections have subtle different tints.
```

---

## 사용 가이드 (v1.1 발표용)

| 슬라이드 영역 | 시간 배분 (90분 기준) |
|---|---|
| Part 1-2 WHY/WHAT (v1.0) | 12분 |
| Part 3 SETUP (v1.0) | 12분 |
| Part 4 CYCLE 1 RUN (v1.0) | 18분 (live evidence) |
| Part 5 FINDINGS (v1.0) | 8분 |
| **Part 7 SELF-IMPROVING** (v1.1) | **12분 ★** |
| **Part 8 CYCLE 2+ LOOP** (v1.1) | **10분 ★** |
| Part 9 PRODUCTION (v1.1 확장) | 8분 |
| Q&A + 부록 | 10분 |

**핵심 강조 슬라이드 (v1.1)**: #41 (DECIDE pattern), #42 (옵션 #1), #51 (사용자 1클릭 = 24h chain)

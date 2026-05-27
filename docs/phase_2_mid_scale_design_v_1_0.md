# Phase 2 (Mid-scale) 진입 설계 문서

> 문서 버전: v1.0 · 작성일: 2026-05-27
> 범위: Phase 1 (Toy 342건, PASS_CANDIDATE) → Phase 2 (Mid-scale 5K + transformer + HPO) 진입 설계
> 본 문서는 Phase 2 milestone 시작 전 인프라/데이터/모델/architecture 변경 사항을 정리하고 사용자가 진입 시점·방식·리스크를 결정할 수 있도록 한다.

---

## 0. 문서 목적

Phase 1 자가발전 lifecycle 검증 완료 (Cycle 1-3, PASS_CANDIDATE 8/9 PASS) → 다음 단계 = **진짜 모델 품질 향상**.

본 문서는:
- Phase 1과 Phase 2의 차이 정의
- 진입 전 필요한 인프라/문서 변경 사항
- 첫 cycle 설계
- 리스크 식별 및 mitigation
- 일정/비용 추정
- 진입 시점 결정 가이드

---

## 1. Phase 1 vs Phase 2 비교

| 차원 | Phase 1 Toy (완료) | Phase 2 Mid-scale |
|---|---|---|
| Sample 크기 | 342건 | **5,000건** (full 50K 中 stratified 추출) |
| Fold | k=5 (valid_n 16~91) | k=10 (valid_n ~500) |
| Group key | `student.location` (school 부재) | **`student_school`** (5K에 존재 예상) |
| Baseline | M1 dummy ~ M4 LightGBM | + **M5 KLUE-RoBERTa + M6 ensemble** |
| HPO | 없음 | **Optuna 50+ trial** |
| Data versioning | 없음 | **DVC stage 관리** |
| MLflow backend | SQLite (전환됨) | SQLite → PostgreSQL (Cycle 5+) |
| Gate 정책 | Rule 5/8 = warn-only | **모두 hard-block 격상** |
| Skill library | placeholder | **Voyager-style 실 활용** |
| Acceptance 목표 | PASS_CANDIDATE | **PASS_FINAL 후보** |
| Cost circuit breaker | cycle당 $20 | **cycle당 $50** (velocity tighter) |
| Cycle 소요 | ~40분 (toy chain) | **~4-8시간** (CPU) / 1-2시간 (GPU) |
| 사용자 부담 | DECIDE 1클릭/cycle | 동일 (자가발전 유지) |

---

## 2. 인프라 변경 사항

### 2.1 신규 도입 (인간 setup 영역)

| 도구 | 역할 | 도입 절차 |
|---|---|---|
| **DVC** | dataset / split / feature artifact version | `pip install dvc` + `.dvc/` init + 5K 데이터 stage |
| **Optuna** | HPO trial 관리 | `pip install optuna` + study DB (`optuna.db`) |
| **KLUE-RoBERTa** | transformer baseline | HuggingFace pre-download → local cache `HF_HOME` |
| **GPU 환경** (선택) | RoBERTa 학습 가속 | WSL2 CUDA setup 또는 CPU-only fp16 |
| **MLflow PostgreSQL** (Cycle 5+) | 안정성 (현 SQLite도 보드 손상 빈발) | Local Postgres or Docker container |

### 2.2 변경 (문서 + 정책)

#### AGENTS.md v4 변경 diff

- **삭제**: `# Toy Scope (정상 절차 + gate 완화)` 섹션 전체 (warn-only 정책 해제)
- **변경**: Hard Rule #5 → strict "M1 ≤ M2 ≤ M3 ≤ M4 ≤ M5" with bootstrap CI hard-block
- **변경**: Hard Rule #8 → metric 단위 일치 + CI hard-block (warn 옵션 제거)
- **신설 Hard Rule #12**: HPO trial 50+ 필수 (Optuna study 등록)
- **신설 Hard Rule #13**: Transformer 학습 시 PII 토큰 단위 audit (학생 PII 외부 LLM 전송 0건 보장)
- **신설 섹션 `# Mid-scale Scope`**:
  - Sample 5K (50K 중 stratified subsample)
  - k=10 fold
  - M1~M6 baseline
  - DVC + Optuna 활성
  - Forbidden 유지: production 등록, champion alias, 외부 배포
- **변경 `# When Modeling`**:
  - transformer-modeler profile 활용
  - GPU/CPU 분기 명시
  - HuggingFace cache 위치 (`HF_HOME=/home/dev/.cache/huggingface`)
- **신설 `# When HPO (gauss + transformer-modeler)`**: Optuna trial 설계, search space

#### MILESTONE.md v2

```markdown
# Milestone Goal v2 (Mid-scale)

Hermes Multi-Agent Kanban Board로 한국어 K-12 에세이 자동채점 모델의
**5K mid-scale 학습 + transformer 도입 + Voyager-style skill library 활성**.

## Success Criteria
1. KLUE-RoBERTa M5 valid QWK >= 0.40 (95% CI lower bound)
2. M5 > M4 LightGBM (transformer 효과 입증)
3. 모든 fold valid_n >= 300 (small-fold 한계 해소)
4. Optuna HPO 50+ trial 완료
5. Skill library 5+ verified skill 누적 (Cycle 2+)
6. PASS_CANDIDATE 또는 PASS_FINAL 달성

## Out of Scope
- 풀데이터 50K (Phase 3)
- Production 모델 등록 (Phase 4)
- 외부 배포
```

### 2.3 새 Profile 추가 (선택)

| 옵션 | 방식 |
|---|---|
| **A. 6 profile 유지 + gauss 확장** | AGENTS.md "When Modeling"에 transformer 책임 추가 |
| **B. transformer-modeler 신규** | `hermes profile create transformer-modeler --description "..."` |

권장: **A** (profile 수 증가 최소화, 본 검증 6-profile 시스템 유지). gauss가 sklearn/lightgbm + KLUE-RoBERTa 모두 담당.

### 2.4 보드 분리 결정

| 옵션 | 장점 | 단점 |
|---|---|---|
| **A. 새 보드 `essay-auto-scoring-research-v3`** | Phase 2 evidence 격리, v2 toy evidence 보존 | 보드 전환 부담 |
| **B. 본 v2 보드 유지** | 연속성, leaderboard 통합 | toy/mid evidence 혼탁 |

권장: **A** (새 보드). toy evidence를 별도 archive 가능 + Phase 2가 깔끔하게 시작.

---

## 3. 새 milestone 첫 cycle 설계

### Cycle M1 sub-task chain (9개, HPO 추가)

| Step | Task | 담당 | Parent | Output |
|---|---|---|---|---|
| 1 | `T-CYCLE-M1-AUDIT: 5K 데이터 검증` | tukey | — | 5K 표본 audit + `student_school` 검증 |
| 2 | `T-CYCLE-M1-SPLIT: k=10 분할` | gauss | AUDIT | StratifiedGroupKFold k=10 |
| 3 | `T-CYCLE-M1-FEATURE: 피처 + RoBERTa embedding` | gauss | SPLIT | dense + RoBERTa CLS embedding |
| 4 | `T-CYCLE-M1-MODEL: M1~M5 baseline` | gauss | FEATURE | sklearn/lightgbm + KLUE-RoBERTa fine-tune |
| 5 | `T-CYCLE-M1-HPO: Optuna 30 trial` | gauss | MODEL | M4/M5 hyperparam 탐색 + best model |
| 6 | `T-CYCLE-M1-EVAL: 다축 평가 + bootstrap CI` | spearman | HPO | per-fold + per-segment + ceiling |
| 7 | `T-CYCLE-M1-REVIEW: 코드 + leakage + PII audit` | turing | HPO | review_report + leakage_reverification + pii_audit |
| 8 | `T-CYCLE-M1-SYNTH: 종합 + skill library 갱신` | aristotle | EVAL + REVIEW | cycle_M1_report + skill candidates 5+ |
| 9 | `DECIDE-M1: 인간 결정 (Cycle M1)` | human | SYNTH | [Continue]/[Phase-up to full]/[Stop] |

### 의존성 그래프

```
AUDIT → SPLIT → FEATURE → MODEL → HPO → (EVAL || REVIEW) → SYNTH → DECIDE-M1
                                                             ↓
                                                          Cycle M2 자체 등록
```

---

## 4. 리스크 및 mitigation

| # | 리스크 | 영향 | Mitigation |
|---|---|---|---|
| 1 | **HuggingFace 모델 다운로드 (sandbox network=false)** | 학습 불가 | 사전 다운로드 후 local cache (`HF_HOME=/home/dev/.cache/huggingface`), AGENTS.md "When Modeling"에 명시 |
| 2 | **GPU 없으면 RoBERTa 학습 너무 느림** | cycle당 5-10시간 | CPU-only fp16 또는 `klue/roberta-small` (110M params), 또는 GPU setup 우선 |
| 3 | **5K subsample stratification 잘못** | bias | tukey가 type×grade-band stratify 강제 + AUDIT manifest에 분포 기록 |
| 4 | **DVC + git LFS 인프라 부담** | 운영 복잡 | toy data는 git만, mid부터 DVC만 적용. 5K는 LFS 불필요 (~10MB) |
| 5 | **Cost circuit breaker 초과** | cycle pause | cycle당 $50로 상향, M5 trial을 4 batch로 분할 |
| 6 | **kanban DB 손상 재발** (1차 사이클에 3회 발생) | chain 중단 | PostgreSQL 전환 검토 (Cycle M5+) 또는 SQLite WAL mode + 주기적 backup cron |
| 7 | **MLflow tracking 부하** | 느린 UI | 현 SQLite → Cycle M5+ PostgreSQL 전환 (Tracking Server 별도) |
| 8 | **Transformer PII leakage 위험** | 법적 | Hard Rule #13 신설 (토큰 단위 audit), `student_name`/`student_id` 완전 제거 |
| 9 | **Skill library quality (Voyager-style)** | misuse | acceptance_pass된 산출만 add, REVIEW가 검증 |
| 10 | **첫 cycle 실패 시 인프라 vs 모델 진단 어려움** | debug 시간 | T-PHASE-MIGRATE-2를 인프라 검증 task로 먼저 실행 (별 cycle) |

---

## 5. 일정/비용 추정

### Setup (인간 작업, 1회만)

| 작업 | 시간 |
|---|---|
| DVC + Optuna pip install | 5분 |
| KLUE-RoBERTa HuggingFace pre-download | 10-30분 (네트워크) |
| AGENTS.md v4 작성 | 30분 |
| MILESTONE.md v2 작성 | 15분 |
| 새 보드 `essay-auto-scoring-research-v3` 생성 + setup | 10분 |
| Cycle M1 task 9개 등록 | 20분 |
| **합계** | **1.5-2시간** |

### 첫 cycle 실행 (자율)

| 환경 | 시간 |
|---|---|
| CPU-only (klue/roberta-small + fp16) | 4-8시간 |
| GPU (klue/roberta-base + Optuna 30 trial) | 1-2시간 |

### 이후 cycle (자율 반복)

- Cycle당 사용자 부담: DECIDE 1클릭
- Cycle당 자동 실행: 첫 cycle과 유사
- 종료 조건: ACCEPTANCE_CRITERIA.yaml mid-scale 기준 충족 시 자동 PASS_FINAL

### 총 milestone 예상 (CPU 기준)

- Setup ~2시간 + 5-10 cycle × 6시간 = **30-60시간** (사용자 클릭 5-10번)

---

## 6. 진입 시점 결정 옵션

| 옵션 | 적합 시점 | 권장 |
|---|---|---|
| **A. 즉시 [Phase-up] + setup 시작** | 시간/GPU 확보, 본 세션 연장 진행 | 단발 검증 시 |
| **B. 현 milestone [Stop] + 별도 시점에 Phase 2 시작** | 인프라 준비 필요, 검증 깔끔 마무리 | **★ 권장** |
| **C. 단계적: SQLite + Optuna 먼저 (RoBERTa는 Cycle M3+)** | 점진적 진입, 리스크 분산 | RoBERTa 인프라 부담 시 |

### 권장 이유 (B)

1. 현 milestone 목적(자가발전 lifecycle 검증) **100% 달성**
2. Phase 2는 별 scope, 별 인프라 → 별 milestone이 깔끔
3. 한 세션에 toy + mid 섞으면 evidence 혼탁
4. Phase 2 인프라(GPU/DVC/RoBERTa)는 사용자가 준비할 시간 필요
5. 토이 검증 → 발표 자료 정리 → mid 시작이 자연 흐름

---

## 7. Phase 2 진입 Setup Checklist (실행 시)

### Pre-setup (인간)

```
□ GPU 가용 확인 (선택)
□ HuggingFace pre-download:
  HF_HOME=/home/dev/.cache/huggingface
  python3 -c "from transformers import AutoModel; AutoModel.from_pretrained('klue/roberta-small')"
□ 5K subsample 추출 도구 준비 (Phase 1 dataset에서 stratified)
□ DVC + Optuna pip install
□ docs/phase_2_mid_scale_design_v_1_0.md 재검토
```

### Document setup

```
□ docs/MILESTONE_v2.md 작성 (mid-scale)
□ AGENTS.md v4 (Toy Scope 삭제, Hard Rule 5/8/12/13 보강, Mid-scale Scope 신설)
□ configs/board_config_mid.yaml (cost cap $50, max_cycles 20)
□ ACCEPTANCE_CRITERIA.yaml mid 섹션 활성
```

### Board setup

```
□ hermes kanban boards create essay-auto-scoring-research-v3 \
    --name "서술형 자동채점 mid-scale" --icon "🚀"
□ hermes kanban boards switch essay-auto-scoring-research-v3
□ AGENTS.md/MILESTONE.md/configs/ 위치 확인 (대상 디렉터리)
□ Cycle M1 task 9개 등록 (mixed 한글 명명)
```

### 첫 실행

```
□ "디스패처 깨우기" 또는 60초 대기
□ T-CYCLE-M1-AUDIT spawn 확인
□ chain 자율 진행 (4-8시간)
□ DECIDE-M1 ready 대기 → 사용자 1클릭
```

---

## 8. 종료 후 (Phase 2 → Phase 3)

Phase 2 acceptance_pass + 5K로 PASS_FINAL 후보 도달 시:
- DECIDE-N에서 `[Phase-up]` 선택
- T-PHASE-MIGRATE-FULL 인간 게이트 task 자동 생성
- 인간 승인 후 Phase 3 (full 50K + bias audit + ensemble) 진입

---

## 9. 참고 문서

- `docs/cycle_roadmap_v_1_0.md` — Phase 1-4 maturity model 원문
- `docs/self_improving_architecture_v_1_0.md` — Layer 1-4 정책
- `docs/escalation_matrix_v_1_0.md` — 실패 행동 매트릭스
- `docs/mlflow_기반_..._v_1_0.md` — MLflow 운영 가이드 (mid-scale 적용)
- `docs/research/mlflow_tracing_2026_research_v_1_0.md` — LLM Judge 도입 검토 (Cycle M3+ 후보)
- `docs/research/self_improving_long_running_research_v_1_0.md` — 외부 evidence (Voyager skill, cost circuit breaker)
- `docs/cycle_task_chain_v_1_1.md` — Phase 1 evidence (참조)

---

## 10. 1줄 결론

> Phase 2 진입은 **인프라 부담 큰 별 milestone**. 현 Phase 1 [Stop]으로 깔끔 종결 후, 별도 시점에 본 문서 §7 checklist로 진행 권장.

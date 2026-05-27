# Phase 2 (Mid-scale) 진입 설계 문서 v1.1

> 문서 버전: v1.1 · 갱신일: 2026-05-28 (v1.0 → v1.1: Phase 1 종료 반영, 5K 데이터 확보 사실 + audit 결과 반영, P0 5건 정정)
> 범위: Phase 1 (Toy 342건, [Stop] 종료) → Phase 2 (Mid-scale 5K + KLUE-RoBERTa + Optuna HPO) 진입 설계
> 본 문서는 진행 중인 Phase 2 milestone의 인프라/데이터/모델/architecture 의사결정 + 위험 분석을 기록한다.

---

## 0. 문서 목적 + 상태

Phase 1 자가발전 lifecycle 검증 완료 → Phase 1 [Stop] 결정 (2026-05-27) → Phase 2 진입 준비.

본 문서가 다루는 것:
- Phase 1과 Phase 2의 차이 정의
- 진입을 위해 필요한 인프라 / 정책 변경
- 첫 cycle (M1) 설계
- 리스크 식별 및 mitigation
- 일정 / 비용 추정 (vast.ai 원격 GPU 포함)
- 차단점 (P2-A~F) 진행 트래킹

### 현 상태 (2026-05-28 기준)

- ✓ **P2-B**: `pipelines/extract_5k.py` (18 tests) 완성
- ✓ **P2-C**: `dataset/sample_5k/` 5,003건 추출 + audit 완료 (manifest 검증, school 38건 surface)
- ✓ **P2-D**: AGENTS.md v4 + MILESTONE_v2.md + 본 문서 v1.1 (현 commit)
- ⌛ P2-A: vast.ai API 키 rotate (사용자 액션)
- ⌛ P2-E: `pipelines/train.py` Phase 2 확장 (KLUE-RoBERTa + Optuna)
- ⌛ P2-F: 새 보드 setup + Cycle M1 등록 + dispatcher 가동

---

## 1. Phase 1 vs Phase 2 비교 (정정)

| 차원 | Phase 1 Toy (종료) | Phase 2 Mid-scale (현재) |
|---|---|---|
| Sample 크기 | 342건 | **5,003건** (AI Hub Training stratified seed=42) |
| Fold | k=5 (valid_n 16~91) | k=10 (valid_n ~500 보장, hard-block ≥300) |
| Group key | `student.location` | `student.location` (Phase 3에서 `student_school` 검토) |
| Baseline | M1 dummy ~ M4 LightGBM | + **M5 KLUE-RoBERTa + M6 M4+M5 ensemble** |
| HPO | 없음 | **Optuna 30 trial+ (Cycle M2+ 누적 50+)** |
| Data versioning | 없음 | DVC 미사용 (Phase 3 50K부터 검토 — `~10MB`에 over-engineering) |
| MLflow backend | SQLite | SQLite 유지 (성능 임계 도달 시 PostgreSQL 검토 — trigger: `mlflow.db > 1GB` 또는 UI > 5s) |
| Gate 정책 | Rule 5/8 = warn-only | **모두 hard-block 격상** (#1~#13) |
| Skill library | placeholder | Voyager-style 활성 (Cycle M3 종료 시 5+ verified) |
| Acceptance 목표 | PASS_CANDIDATE | **M5 valid QWK ≥ 0.40 (95% CI lower)** + PASS_CANDIDATE/FINAL |
| Cost circuit breaker | $20/cycle | **$20/cycle 유지**, 대형 모델 적용 시 $50 상향 검토 (board_config.yaml) |
| Cycle 소요 (CPU only) | ~40분 | ~4-8h (M1~M4 only) |
| Cycle 소요 (원격 8GB GPU) | — | **~1~1.5h** (M5 roberta-small + HPO 30) ★ 권장 |
| Cycle 소요 (원격 12GB+ GPU) | — | ~2h (M5 roberta-base fp16 + HPO 30) |
| 사용자 부담 | DECIDE 1클릭/cycle | 동일 (자가발전 유지) |

---

## 2. 인프라 변경 사항

### 2.1 신규 도입

| 도구 | 역할 | 진입 시점 | 도입 절차 |
|---|---|---|---|
| **Optuna** | HPO trial 관리 | Cycle M1 | `pip install optuna` + study DB `sqlite:///optuna.db` |
| **KLUE-RoBERTa** | transformer baseline | Cycle M1 | HuggingFace pre-download → local cache `HF_HOME=/home/dev/.cache/huggingface` |
| **원격 8GB GPU (vast.ai)** | M5 학습 가속 | Cycle M1 | `VAST_GPU_GUIDE.md` 절차 — RTX 3060 8GB, $0.04~0.08/hr |
| `pipelines/audit_pii.py --fail-on-hit` | PII 외부 송신 게이트 | Cycle M1 (의무) | Hard Rule #13 |
| DVC | dataset/feature version | **Phase 3로 후순위** | 5K(~10MB)에 over-engineering. 50K Full부터 검토 |
| MLflow PostgreSQL | tracking 안정성 | **trigger 도달 시** | `mlflow.db > 1GB` 또는 UI 응답 > 5s |

### 2.2 변경 (문서 + 정책) — 완료

| 산출물 | 변경 내용 | commit |
|---|---|---|
| `AGENTS.md` v4 | Hard Rule #5/#8 strict, #12/#13 신설, Mid-scale Scope, 9 sub-task pattern, When HPO, Forbidden 갱신 | (이전 commit) |
| `MILESTONE_v2.md` 신설 | Phase 2 goal anchor (Hard Rule #10 source), 7 success criteria | (이전 commit) |
| `VAST_GPU_GUIDE.md` v2 | Essay/RoBERTa 도메인, .env 키 로드, PII gate 의무화, trap destroy | (Phase 2 hardening plan) |
| `pipelines/audit_pii.py` | PII regex 4종 + essay_id hash + CLI + `--fail-on-hit` | (Phase 2 hardening plan) |
| `pipelines/extract_5k.py` | 비례 stratified 5K 추출 + manifest + CLI | (P2-B) |
| `dataset/sample_5k/` | 5,003건, 21 strata, seed=42 (gitignored) | (P2-C 실행) |

### 2.3 Profile 정책

| 옵션 | 방식 |
|---|---|
| **A. 6 profile 유지 + gauss 확장 (채택)** | AGENTS.md "When Modeling" + "When HPO" 섹션에 transformer/HPO 책임 추가. gauss가 sklearn+lightgbm+KLUE-RoBERTa+Optuna 모두 담당 |
| B. transformer-modeler 신규 | 6 → 7 profile, profile 수 증가 |

**채택: A** — 6-profile 시스템 안정성 유지, 책임 확장만.

### 2.4 보드 분리 (P2-F에서 적용)

| 옵션 | 결정 |
|---|---|
| **A. 새 보드 `essay-auto-scoring-research-phase2` (채택)** | Phase 1 toy evidence 격리, Phase 2 깨끗한 시작 |
| B. 본 v2 보드(Phase 1) 유지 | toy/mid evidence 혼재 |

---

## 3. 새 milestone 첫 cycle (M1) 설계

### Cycle M1 sub-task chain (9개, AGENTS.md v4와 일치)

| Step | Task 명명 (mixed) | 담당 | Parent | 핵심 Output |
|---|---|---|---|---|
| 1 | `T-CYCLE-M1-AUDIT: 데이터 검증` | tukey | (시작) | 5K 표본 audit + manifest 검증 + PII gate commit hash 기록 |
| 2 | `T-CYCLE-M1-SPLIT: 분할 정책` | gauss | AUDIT | StratifiedGroupKFold k=10, valid_n≥300 확인 |
| 3 | `T-CYCLE-M1-FEATURE: 피처 + RoBERTa embedding` | gauss | SPLIT | TF-IDF + RoBERTa CLS embedding cache |
| 4 | `T-CYCLE-M1-MODEL: M1~M5 baseline` | gauss | FEATURE | M1~M4 로컬 + M5 vast.ai 원격 (한 trial best) |
| 5 | `T-CYCLE-M1-HPO: Optuna 30 trial+` | gauss | MODEL | M4/M5 hyperparam study → best_params, study summary |
| 6 | `T-CYCLE-M1-EVAL: 다축 평가 + bootstrap CI` | spearman | HPO | per-fold + per-segment + ceiling 비교 |
| 7 | `T-CYCLE-M1-REVIEW: 코드 + leakage + PII audit` | turing | HPO | review_report + leakage_reverification + PII gate hash 검증 |
| 8 | `T-CYCLE-M1-SYNTH: 종합 + 다음 cycle 등록` | aristotle | EVAL + REVIEW | cycle_M1_report.md + skill candidates + Cycle M2 9 sub-task 자동 등록 |
| 9 | `DECIDE-M1: 인간 결정 (Cycle M1)` | human | SYNTH | [Continue]/[Pause-redesign]/[Stop] |

### 의존성 그래프

```
AUDIT → SPLIT → FEATURE → MODEL → HPO → (EVAL || REVIEW) → SYNTH → DECIDE-M1
                                                                     ↓
                                                                  Cycle M2 9-task 자체 등록
```

### DECIDE 옵션 (Phase 1 패턴 통일)

| 옵션 | 의미 |
|---|---|
| `[Continue]` | Cycle M(N+1) chain 자동 시작 |
| `[Pause-redesign]` | 현 cycle evidence를 인간 검토, redesign 후 cycle 재실행 (Phase 1의 [Phase-up]을 좁힘 — Phase 전환은 acceptance 충족 누적 시에만 별도 결정) |
| `[Stop]` | 종결, `explicit_stop_decided` terminal |

`[Phase-up to full]` 은 Phase 2 acceptance criteria 1~5 누적 충족 시점에만 별도 사용자 결정 — Cycle M1에서 바로 점프 금지.

---

## 4. 리스크 및 mitigation

| # | 리스크 | 영향 | Mitigation | 상태 |
|---|---|---|---|---|
| 1 | HuggingFace 모델 sandbox network=false 환경에서 다운로드 불가 | 학습 차단 | `HF_HOME=/home/dev/.cache/huggingface` 사전 다운로드 (vast.ai 인스턴스도 동일 경로 mount 또는 onstart-cmd로 pip+model 동시 설치) | 절차 명시 |
| 2 | 모델별 VRAM mismatch | OOM | klue/roberta-small(68M, ~4GB) → roberta-base(110M fp16, ~7GB) → roberta-large(337M, 24GB, **Forbidden in Phase 2**). 본 phase는 small 진입 권장 | AGENTS.md v4 Forbidden |
| 3 | 5K stratification 잘못 (지역 편중) | bias | tukey가 manifest 분포를 PDF 기준 ±3%p로 검증 강제. 본 추출(P2-C) 결과: essay_type ±0.5%, grade ±2%p — 정상 | ✓ 통과 |
| 4 | 외부 compute(vast.ai) 학생 PII 송신 | 컴플라이언스 위반 | Hard Rule #13 게이트: `audit_pii --fail-on-hit` 통과 commit hash 강제. 본 P2-C에서 6 진짜 school + 1 placeholder + 44 false positive person_name surface — gate가 정상 차단 | ✓ 게이트 동작 |
| 5 | Cost circuit breaker 초과 | cycle pause | board_config `max_usd_per_cycle: 20.0` 유지. vast.ai 8GB GPU cycle당 $0.075~0.15 (RTX 3060) → 충분 여유. 대형 모델 사용 시 $50 상향 검토 | 충분 |
| 6 | kanban.db SQLite 손상 재발 (Phase 1에서 3회) | chain 중단 | WAL mode + 주기적 backup cron (Phase 2 setup 시 추가). Hermes Gateway 자체 issue, 회복 절차 정착됨 | 회복 절차 보유 |
| 7 | MLflow tracking 부하 | UI slow | SQLite 유지. 임계(`mlflow.db > 1GB` 또는 UI > 5s) 도달 시 PostgreSQL 전환 | trigger 정의 |
| 8 | KLUE-RoBERTa fine-tune false positive PII 누출 | 법적 | Hard Rule #13 + tokenizer 통과 후 essay 본문 회귀 audit | ✓ 게이트 정착 |
| 9 | Skill library 품질 (Voyager-style) | misuse | acceptance_pass된 산출만 add, REVIEW가 검증, semantic search index Cycle M2+ 활성 | 정책 명시 |
| 10 | 첫 cycle 인프라 vs 모델 진단 어려움 | debug 시간 | P2-E 단계에서 train.py 확장을 작은 TDD plan으로 분리 (별 plan), Cycle M1 진입 전 dry-run 가능 | 분리 예정 |
| **11** | **AI Hub 데이터 사용 약관 / 상업적 이용 시 별 협의** | 라이선스 | 본 프로젝트는 연구/내부용 가정. 상업 전환 시 티맥스에이아이(sanghyo_lee@tmax.co.kr) 별도 협의. PDF 설명서 §메타테이블 참조 | 명시 |
| **12** | **AGENTS.md Hard Rules LOCKED 변경 게이트** | 정책 위반 | 변경 시 사용자 명시적 동의 + commit message에 게이트 통과 사유 기록. 본 v4는 2026-05-28 사용자 "진행" 결정 통과 | ✓ 정착 |

---

## 5. 일정 / 비용 추정 (vast.ai 8GB GPU 기준)

### Setup (인간 + 협업, 1회만)

| 작업 | 누가 | 시간 |
|---|---|---|
| vast.ai API 키 rotate (P2-A) | 사용자 | 5분 |
| HuggingFace KLUE-RoBERTa pre-download (`klue/roberta-small`) | 사용자 또는 onstart-cmd | 5-15분 |
| pipelines/train.py Phase 2 확장 (P2-E) | 협업 plan + TDD | 2-3h |
| 새 보드 setup + Cycle M1 9 task 등록 + dispatcher 가동 (P2-F) | 협업 | 30분 |
| **합계** | | **3-4h** (병렬 가능) |

### 첫 cycle (M1) 실행 (자율 chain)

| 환경 | Cycle 시간 | 비용 (vast.ai) |
|---|---|---|
| 로컬 CPU only (M1~M4) | ~4h | $0 |
| **vast.ai RTX 3060 8GB (M5 small + HPO 30)** | **~1.5h** | **$0.06~0.15** |
| vast.ai RTX 3060 12GB (M5 base fp16 + HPO 30) | ~2h | $0.10~0.30 |

### 이후 cycle (자율 반복)

- Cycle당 사용자 부담: DECIDE-MN 1클릭
- Cycle당 자동 실행: M1 유사 시간
- 종료: ACCEPTANCE_CRITERIA.yaml mid 섹션 충족 시 PASS_FINAL 자동 또는 사용자 [Stop]

### 총 milestone 예상

- Setup ~3h + 5-10 cycle × 1.5h(GPU) = **10-18h 자율 chain**
- 사용자 클릭: setup 1회 (vast.ai 키) + cycle당 DECIDE 1회 × 5-10회 = 6-11회
- 총 vast.ai 비용 (small + HPO 30, 10 cycle): **~$0.75~1.50**

---

## 6. 진입 진행 트래킹 (P2-A ~ P2-F)

| # | 작업 | 상태 | 비고 |
|---|---|---|---|
| **P2-A** | vast.ai API 키 rotate | ⌛ | 사용자 콘솔, 5분 |
| **P2-B** | `pipelines/extract_5k.py` plan + TDD (18 tests) | ✓ | 5 commits |
| **P2-C** | 5K 추출 + audit 검증 | ✓ | 5,003건, school 38건 surface, gate 정상 차단 |
| **P2-D** | AGENTS.md v4 + MILESTONE_v2.md + 본 문서 v1.1 | 🔄 | 본 commit |
| **P2-E** | `pipelines/train.py` Phase 2 확장 | ⌛ | 별 plan, TDD |
| **P2-F** | 새 보드 + Cycle M1 등록 + dispatcher | ⌛ | P2-A~E 의존 |

---

## 7. Phase 2 진입 Setup Checklist

### Pre-setup (인간 액션)

```
□ vast.ai 콘솔에서 기존 API 키 revoke + 신규 발급 (P2-A)
□ .env에 신규 키 저장, `vastai show user` 인증 확인
□ HuggingFace KLUE-RoBERTa pre-download:
  HF_HOME=/home/dev/.cache/huggingface
  python3 -c "from transformers import AutoModel; AutoModel.from_pretrained('klue/roberta-small')"
□ 본 문서 v1.1 재검토 (의사결정 확인)
```

### Document setup (완료)

```
✓ MILESTONE_v2.md 작성 (Phase 2 goal anchor)
✓ AGENTS.md v4 (Hard Rule strict 격상, #12/#13 신설, 9 sub-task pattern)
✓ docs/phase_2_mid_scale_design_v_1_1.md 본 문서
✓ configs/board_config.yaml (Phase 1과 동일, $20/cycle cap 유지)
✓ ACCEPTANCE_CRITERIA.yaml (mid 섹션 활성 — Cycle M1 SYNTH 참조)
```

### Code setup (P2-E)

```
□ pipelines/train.py에 KLUE-RoBERTa fine-tune + Optuna study 추가 (별 plan)
□ --model klue/roberta-small, --hpo-trials 30, --cycle-id M1 인자
□ MLflow nested run + study summary 등록
□ TDD: synthetic dataset으로 학습 cycle 검증
```

### Board setup (P2-F)

```
□ hermes kanban boards create essay-auto-scoring-research-phase2 \
    --name "서술형 자동채점 mid-scale" --icon "🚀"
□ hermes kanban boards switch essay-auto-scoring-research-phase2
□ Cycle M1 task 9개 등록 (mixed 한글, AGENTS.md v4 §Cycle Sub-task Pattern)
□ dispatcher 가동 (gateway tick)
```

### 첫 실행 (M1)

```
□ "디스패처 깨우기" 또는 60초 대기
□ T-CYCLE-M1-AUDIT spawn 확인 (tukey)
□ chain 자율 진행 (~1.5h, vast.ai GPU 사용 시)
□ DECIDE-M1 ready 대기 → 사용자 1클릭
```

---

## 8. 종료 후 (Phase 2 → Phase 3)

Phase 2 acceptance criteria 1~5 누적 충족 + M5 vs M4 strict 진화 입증 시:
- DECIDE-MN에서 사용자가 별도로 [Phase-up to full] 선택 (Cycle M1에서 점프 금지)
- T-PHASE-MIGRATE-FULL 인간 게이트 task 자동 생성
- 인간 승인 후 Phase 3 (full 50K + DVC + bias audit + ensemble + Validation set holdout) 진입
- AGENTS.md v5 신설 (LOCKED 게이트)

---

## 9. 참고 문서

- `MILESTONE_v2.md` — Phase 2 goal anchor (본 문서가 인용)
- `AGENTS.md` v4 — Hard Rules + 9-step Cycle Pattern + When HPO
- `VAST_GPU_GUIDE.md` — vast.ai 작업 절차
- `docs/research/vast_ai_essay_workflow_v_1_0.md` — vast.ai 운영 evidence (위험, 비용, 데이터 흐름)
- `docs/research/self_improving_long_running_research_v_1_0.md` — 외부 사례 (Voyager, AutoGPT, Devin)
- `docs/research/mlflow_tracing_2026_research_v_1_0.md` — LLM Judge 도입 검토 (Cycle M3+ 후보)
- `docs/cycle_roadmap_v_1_0.md` — Phase 1-4 maturity model
- `docs/self_improving_architecture_v_1_0.md` — Layer 1-4 정책
- `dataset/sample_5k/manifest.json` — 본 milestone primary 5K 추출 spec

---

## 10. 1줄 결론

> Phase 1 [Stop] 종결, P2-B/C/D 완료. **남은 차단점 P2-A (사용자, 5분), P2-E (협업 plan, 2-3h), P2-F (협업 setup, 30분)** 처리 후 dispatcher tick으로 Cycle M1 자가발전 chain 시작.

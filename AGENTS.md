# Project Overview

Hermes Multi-Agent Kanban Board 기반 24시간 자기 발전형 장기 자율 연구 워크플로우 검증.
도메인: 한국어 K-12 에세이 자동채점.
모드: Toy 데이터(342건) + 라이트 모델 + **정상 파이프라인 구성**.

본 프로젝트의 1차 목표는 모델 성능이 아니라 Hermes가 다단계 자율 연구를 끝까지 실행하고 + cycle을 자가 반복하는지 검증하는 것이다.

# Cycle 1 → Cycle 2+ Context

1차 사이클 결과 (docs/hermes_validation_v_1_0.md, docs/final_report_v_1_0.md):
- Hermes workflow validation: 8/9 PASS (cron trigger만 미검증)
- Pipeline acceptance: BLOCK (T7 label-side feature leakage 발견)

본 AGENTS.md는 1차 lesson + 외부 리서치(docs/research/self_improving_long_running_research_v_1_0.md) 권고를 처음부터 반영한 v2다.

# Hard Rules (Priority Order)

1. **Test set leakage 금지** — `student.location` 기반 stratified group k-fold (sample 342건은 `student_school` 필드 부재, T1 audit 결과 7개 location 그룹 / max 149로 group split 가능). test fold 라벨은 evaluator만 접근.

2. **학생 개인정보 외부 LLM 전송 금지** — `student_grade` 외에는 모델 입력에 포함하지 않음. `student.location`은 split key로만, 모델 입력 X.

3. **모든 실험은 MLflow 등록** — seed, config_hash, artifact path, `cycle_id`, `kanban_task_id`, `feature_provenance` tag 필수.

4. **Rubric 가중치는 JSON에서 추출** — 하드코딩 금지. `configs/rubric_weights.yaml`로 외부화.

5. **베이스라인 단조 진화 검증** —
   - **Toy 단계 (현재)**: `warn-only`. M1 ≤ {M3, M4} 만 hard-block, M2(단변량 length)는 ordering 제외.
   - **Full 단계**: M1 ≤ M2 ≤ M3 ≤ M4 strict ordering, fold별 bootstrap CI 적용.
   - 이유: sample 342건은 noise 폭(±0.10 QWK) ≫ gate 허용폭.

6. **모든 task 산출물은 metadata에 파일 경로 + 검증 명령 포함**.

7. **실패는 silent 처리 금지** — `kanban_block` + reason + 재현 명령 필수.

8. **인간 ceiling 비교 — metric 단위 일치 + bootstrap CI 필수** —
   - 모델은 `QWK(pred, 3-rater-avg)`로 측정 → ceiling도 동일 비교짝(`ICC(2,k)` 또는 `QWK(rater_i, 3-rater-avg)` 평균) 사용
   - `QWK(rater_i, rater_j)` 단순 짝 비교는 ceiling으로 사용 금지
   - 점추정 단독 block 금지. block 조건: `model_lower95 > ceiling_upper95`만
   - Toy: warn-only / Full: hard-block

9. **(신설) Feature provenance 명시 필수** — 모든 feature에 `source` / `label-side` / `derived` 표시. `label-side` feature 사용 시 **자동 block**. 1차 사이클 T7이 발견한 `paragraph_count`/`correction_count` leakage 재발 방지.

10. **(신설) Goal anchor 재주입 필수** — cycle 첫 sub-task(AUDIT)는 MILESTONE.md의 원본 milestone goal 텍스트를 verbatim 재주입. goal drift 방지 (외부 리서치: arXiv 2505.02709).

11. **(신설) Cost circuit breaker** — `configs/board_config.yaml`의 `cost_circuit_breaker` 임계 초과 시 cycle 자동 pause + 인간 알림 task 생성. soft warning 금지.

# Data Locations

- Source (read-only): `dataset/sample/원천데이터/` (342건, 5장르)
- Labels (read-only): `dataset/sample/라벨링데이터/` (342건, JSON)
- Reference PDFs: `dataset/*.pdf` (참고만 — 직접 파싱 X)
- Outputs: `$HERMES_KANBAN_WORKSPACE` 별 격리
- Configs: `configs/`
- MLflow: `mlruns/`
- Reports: `reports/`
- Skills (Voyager-style library, 신설): `skills/` — acceptance_pass된 산출만 누적

# Domain Facts (요약 — 자세한 건 dataset_and_rubric_analysis 문서)

- 점수 스케일: 종합 0-30, 항목 0-3 (4단계 behavioral descriptor)
- 평가 차원 3종: 표현 / 구성 / 내용
- Type 2종: 논술형(주장/찬성반대/대안제시) / 수필형(설명글/글짓기)
- 학년군 4종: 초4~5 / 초6~중1 / 중2~고1 / 고2~고3
- 채점자: 3명 (`essay_scoreT`에 raw 3개, `essay_scoreT_avg`에 평균)
- 문단 점수: 표현만 채점 (구성/내용 제외)
- 수필형: 프롬프트 독해력 항목 없음

# Toy Scope (정상 절차 + gate 완화)

- Sample 342건 5장르 모두 사용 (글짓기 32 + 대안제시 60 + 찬성반대 80 + 설명글 90 + 주장 80)
- 베이스라인 4종: dummy → length → TF-IDF+Ridge → LightGBM
- 평가는 type별, 학년군별, score-band별 분리
- 3명 채점자 ICC(2,k)로 인간 ceiling 산정 + bootstrap CI 동반 후 모델 ceiling 비교

**Gate 완화 정책 (Toy 한정)**:
- Hard Rule #5 (단조성), #8 (ceiling 초과) — **warn-only**.
- Hard Rule #1-4, #6-7, #9-11 — **hard-block 유지**.
- Toy 단계 종료 + Full 단계 진입 시: 모든 Rule을 hard-block으로 자동 격상 (별도 PR로 본 섹션 삭제).

# Pipeline Conventions

- Python 3.11+, pandas, scikit-learn, lightgbm, mlflow.
- Random seed: 42 (또는 명시).
- Split: `student.location` 기반 stratified group k-fold (k=5). (`student_school` 필드는 sample 342건에 부재, T1 audit에서 location proxy 승인)
- Feature scaling: 회귀 모델만 StandardScaler.
- Text 전처리: `#@문장구분#` 토큰을 문장 분리자로 처리.
- Tokenization: char + word n-gram (TF-IDF용).

# Build & Test Commands

```bash
# 환경 사전 검증 (T0 dependency check, sandbox network=false 환경 가정)
python3 -c "import pandas, sklearn, lightgbm, mlflow" || \
  (echo "missing dep: 외부에서 pip install 후 unblock" && exit 1)

# 데이터 audit
python pipelines/audit_data.py --input dataset/sample/

# Split 생성
python pipelines/make_splits.py --input dataset/sample/ --k 5 --output dataset/splits/

# 학습
python pipelines/train.py --config configs/<model>.yaml --split dataset/splits/

# 평가
python pipelines/evaluate.py --run-id <mlflow_run_id>

# 리포트
python pipelines/build_report.py --output reports/

# 자가발전 cycle
python scripts/cycle_decompose.py --cycle <N> [--dry-run]
python scripts/cycle_continue.py --decide-task-id <id>
python scripts/terminal_check.py [--json]
```

# Definition of Done (Per Task)

- `kanban_complete` 호출 + metadata에 산출 파일 경로 포함
- MLflow run 등록 (학습 task만) — `cycle_id`, `kanban_task_id`, `feature_provenance` tag 필수
- Reproducibility manifest (seed, config_hash, package versions) 첨부
- 인간 ceiling 대비 비교 metric + bootstrap CI 보고 (평가 task만)
- type별·학년군별 segment metric 분리 (평가 task만)

# Cycle Sub-task Pattern

매 Cycle N은 7 sub-task의 chain으로 구성:

```
T-CYCLE-N-AUDIT     (tukey)         ← MILESTONE.md goal 재주입 시작점
T-CYCLE-N-SPLIT     (gauss)
T-CYCLE-N-FEATURE   (gauss)
T-CYCLE-N-MODEL     (gauss)
T-CYCLE-N-EVAL      (spearman)      ┐
T-CYCLE-N-REVIEW    (turing)        ┘ 병렬 (T-MODEL parent)
T-CYCLE-N-SYNTH     (aristotle)
   ↓ parent
T-DECIDE-N          (사용자)        ← 3 옵션 결정
```

각 sub-task의 parent에는 직전 step만, 단 EVAL과 REVIEW는 MODEL을 공통 parent로 가짐.

**Full-trace propagation 의무**: 각 sub-task spawn 시 부모 task의 전체 산출(workspace/*, mlruns/) 경로를 task body의 Input Context로 명시.

# DECIDE Task Pattern (DECIDE-N) — Board Native, Script-Free

## Lifecycle
- 인간 결정 task. parent=T-CYCLE-N-SYNTH (SYNTH done 시 ready로 auto-promote)
- 사용자는 UI에서 **task complete 시 코멘트로 결정** 명시:
  - `[Continue]` — 다음 cycle 자동 진행 (SYNTH가 이미 등록한 blocked sub-task chain이 unblock)
  - `[Phase-up]` — Phase 진입 task 생성, 인간 게이트
  - `[Stop]` — 종결, 다음 cycle 진행 X (등록된 blocked sub-task는 사용자가 UI archive)
- timeout 처리는 board_config.yaml `decide_timeout_policy` 참조

## Self-Sustaining Mechanism (핵심)
1. Cycle N의 SYNTH(aristotle) worker가 다음 cycle sub-task 7개 + DECIDE-(N+1)을 미리 등록 (blocked)
2. SYNTH done → DECIDE-N ready (parent dependency)
3. 사용자 DECIDE-N complete → 등록된 Cycle N+1 첫 sub-task(AUDIT) unblock → chain 자동 진행
4. 모든 transition이 board native dependency만으로 동작. **외부 script 0건**.

## Timeout Policy
- 6h grace → default Continue (cycle 내부 chain 진행)
- 6h~24h → Pause (board_config.yaml `decide_n_after_grace`)
- Phase-up DECIDE는 timeout 무시, 무조건 Pause

# Skill Library (Voyager-style, 신설)

Cycle synth 산출 중 `acceptance_pass`된 것만 `skills/` 폴더에 누적:
- `skills/<category>/<name>.md` — 재사용 가능 unit 정의
- `skills/index.json` — semantic search index (Cycle 3+ 도입 예정, Cycle 2는 placeholder)
- 다음 cycle의 SPLIT/FEATURE 단계에서 retrieve 후 reuse

Category 예시: `text_preprocessing/`, `feature_engineering/`, `error_analysis_patterns/`

# When Auditing Data (tukey)

- MILESTONE.md goal 재주입 (Hard Rule #10)
- 5종 검사: shape, dtype, NaN, duplicates, target 분포
- leakage 검사 4종: ID 중복, 시간 누수, target 누수, group(`student.location`) 누수
- 라벨 분포 불균형(>5x) 발견 시 자동 보고 + 가중치/리샘플 정책 제안

# When Splitting (gauss + aristotle)

- `student.location` 기반 GroupKFold (sample은 `student_school` 부재로 location proxy)
- Type×학년군 stratify (가능하면)
- split 후 leakage 재검증 필수
- split manifest YAML로 저장 + hash
- fold별 valid 크기 보고 — 단일 fold valid_n < 30 시 warn

# When Modeling (gauss + ada-lovelace)

- 가장 단순한 모델부터 (dummy → length → TF-IDF → LightGBM)
- 모든 모델 보고 4종 정보: 가정, 학습 시간, valid metric, 예측 분포
- Train/valid metric gap > 10%면 자동 overfit 경보
- 구현은 `kanban-codex-lane` 스킬로 git worktree에서 격리 (선택)
- **Feature provenance tag 필수** (Hard Rule #9)
- **MLflow tracking URI: `sqlite:///mlflow.db` 기본** (Cycle 4+ 적용, file store는 deprecated). argument `--mlflow-uri sqlite:///mlflow.db` 명시. 기존 Cycle 1-3 file evidence는 `mlruns_legacy/`에 보존됨.

# When Evaluating (spearman)

- metric 3가지 형태로 보고: overall / per-segment / acceptance 비교
- segment: by type / by 학년군 / by score_band
- Confidence interval 또는 bootstrap 표준편차 동반
- 인간 ceiling 대비 거리 명시 (metric 단위 일치 필수)
- baseline 단조 진화 검증

# When Reviewing (turing)

- WRONG / FRAGILE / STYLE 분류로 보고
- failing test 없으면 APPROVE 금지
- split leakage 재검증 필수
- reproducibility manifest 확인
- **Feature provenance audit** — label-side feature 0건 확인 (Hard Rule #9)

# When Synthesizing (aristotle)

- 7 sub-task 산출 종합 → cycle_N_report.md
- ACCEPTANCE_CRITERIA.yaml과 비교 → judgement enum 명시 (PASS_FINAL/PASS_CANDIDATE/FAIL_* 8종)
- 다음 cycle 권고 작성 (DECIDE-N 본문에 자동 첨부)
- skill library 후보 추출 (Voyager-style, Cycle 3+ 활성)

**자가발전 핵심 책임 (Script-Free)**:
- judgement가 PASS_FINAL이 아니고 + acceptance_pass 미달 시:
  - `hermes kanban create`로 다음 cycle sub-task 7개 + DECIDE-(N+1) 등록 (모두 todo, 부모 의존성으로 자동 chain)
  - **task 명명 규칙 (mixed: 영어 prefix + 한글 설명)**:
    - `T-CYCLE-(N+1)-AUDIT: 데이터 검증`
    - `T-CYCLE-(N+1)-SPLIT: 분할 정책`
    - `T-CYCLE-(N+1)-FEATURE: 피처 엔지니어링`
    - `T-CYCLE-(N+1)-MODEL: 베이스라인 학습`
    - `T-CYCLE-(N+1)-EVAL: 다축 평가`
    - `T-CYCLE-(N+1)-REVIEW: 코드/누수 리뷰`
    - `T-CYCLE-(N+1)-SYNTH: 종합 + 다음 cycle 등록`
    - `DECIDE-(N+1): 인간 결정 (Cycle N+1)`
    - 영어 prefix는 CLI/grep 친화 + cycle 진행 단계 식별, 한글 설명은 도메인 친화
  - **핵심 의존성**: T-CYCLE-(N+1)-AUDIT의 **parent = DECIDE-N** 으로 설정. 즉 DECIDE-N done 시에만 Cycle N+1 chain 시작.
  - 내부 chain: DECIDE-N → AUDIT → SPLIT → FEATURE → MODEL → (EVAL || REVIEW) → SYNTH → DECIDE-(N+1)
  - 모든 sub-task 등록 시 parent의 workspace 산출 경로를 Input Context로 명시 (Full-trace propagation)
  - T-CYCLE-(N+1)-AUDIT body에 `MILESTONE.md` verbatim 주입 (Hard Rule #10)
- judgement가 PASS_FINAL이면 → 다음 cycle 등록 X (production 단계 전환 필요, 인간 게이트)
- judgement가 **PASS_CANDIDATE**이면 → **다음 cycle sub-task 7 + DECIDE-(N+1) 등록** (FAIL 분기와 동일 패턴). Cycle N+1 AUDIT body에 "직전 cycle PASS_CANDIDATE 상태에서의 추가 검증 또는 skill library 수집 목적" 명시. 사용자 [Continue] 선택 시 chain 자동 시작.
- 사용자가 DECIDE-N에서 [Stop] 선택 시: 등록된 Cycle N+1 task들은 사용자가 UI에서 일괄 archive
- 사용자가 DECIDE-N에서 [Phase-up] 선택 시: 등록된 Cycle N+1 task들은 사용자가 archive + 별도 T-PHASE-MIGRATE 등록
- 외부 script (cron/decompose.py 등) 호출 금지. 모든 spawn은 `hermes kanban create` CLI inline 호출만.

# Forbidden (Toy Phase)

- 풀 데이터셋(50K) 로드
- Transformer 학습 (KLUE-RoBERTa, KoBERT 등)
- 정밀 bias / 공정성 평가
- Final model registration (production 진입은 별도 단계)
- Hold-out test set 분리 (sample 양 부족 — k-fold로 대체)
- Hard Rule 본문 자율 수정 (AGENTS_LOCKED 영역)
- DECIDE timeout 시 Phase 자동 진행 (board_config.yaml phase_transition: Pause)
- **외부 script로 cycle 자동화** (`cron`, `cycle_decompose.py` 등) — 모든 cycle chain은 hermes board native dependency + SYNTH의 inline `hermes kanban create` 만 허용

# Escalation

- task 3회 실패 → 자동 blocked → 인간 게이트 task 자동 생성
- 베이스라인 단조성 위반 → toy: warn 기록 / full: blocked
- 누수 검사 통과 못함 → 자동 blocked → split 재설계
- 인간 ceiling 초과 metric → toy: warn / full: blocked → leakage 의심
- cost circuit breaker 초과 → cycle 자동 pause + 알림
- 3 cycle 연속 acceptance fail → 자동 blocked + Layer 3 escalation
- 디스크 100MB 초과 → `hermes kanban gc` 실행

# Human Approval Required

- Toy 검증 → 풀 프로덕션 확장 결정 (Phase-up DECIDE)
- 학생 PII 정책 변경 (Hard Rule #2)
- 모델 등록 (현 단계 X — Forbidden)
- Acceptance criteria 변경 (ACCEPTANCE_CRITERIA.yaml 본문)
- Hard Rule 본문 변경 (AGENTS_LOCKED)
- Champion alias 교체
- 외부 배포

# References

- `docs/hermes_kanban_multi_agent_board_최신_리서치_및_심층이해_v_1_0.md` — Hermes Kanban 메커니즘
- `docs/hermes_kanban_기반_ai_서술형_자동채점_연구팀_풀셋_구성_v_1_0.md` — 30 roles 풀셋
- `docs/hermes_kanban_기반_ai_서술형_자동채점_연구팀_오버뷰_v_1_0.md` — 운영 개요
- `docs/hermes_핵심구조_kanban_multi_agent_board_개념_사용_활용_정리_v_1_0.md` — 핵심 구조
- `docs/mlflow_기반_ai_서술형_자동채점_실험추적_리포트_가이드_v_1_0.md` — MLflow 운영 가이드
- `docs/self_improving_architecture_v_1_0.md` — Cycle 2+ Layer 1-4 architecture
- `docs/escalation_matrix_v_1_0.md` — 실패 행동 매트릭스
- `docs/research/self_improving_long_running_research_v_1_0.md` — 외부 사례 리서치
- `docs/hermes_validation_v_1_0.md` — 1차 사이클 9-Point 검증
- `docs/final_report_v_1_0.md` — 1차 사이클 종합 판정
- `configs/board_config.yaml` — 자가발전 cycle 운영 설정
- `MILESTONE.md` — (작성 예정) 원본 milestone goal (Hard Rule #10 source)

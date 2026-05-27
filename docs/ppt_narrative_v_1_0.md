# PPT 발표 narrative v1.0

> **목적**: `ppt_slides_v_1_0.md`의 슬라이드별 발표 narrative + 강의 운영 가이드.
> 발표자가 슬라이드를 보면서 어떤 흐름으로 말할지, 무엇을 강조할지, 어떤 질문이 나올지 정리.

---

## 청중 가정

- 1차 청중: AI/ML 엔지니어, 연구 팀 리드
- 2차 청중: 자동화 도구 도입 결정자, 데이터 사이언티스트
- 사전 지식: ML 파이프라인 경험 있음, LLM agent는 기본 개념만, kanban은 일반 협업 도구로 알고 있음
- 청취 시간: 60분 (45분 발표 + 15분 Q&A) 또는 90분 (워크숍 포맷)

---

## 전체 흐름 설계

```
도입 (Part 1: 5분)         "왜 지금 자율 워크플로우인가"로 청중 hook
                            ↓
이해 (Part 2-3: 20분)      Hermes의 구조와 설정 — 기술적 토대
                            ↓
사건 (Part 4: 20분)        실제 lifecycle을 narrative로 — 가장 강렬한 파트
                            ↓
교훈 (Part 5: 10분)         검증 결과를 일반화된 lesson으로
                            ↓
미래 (Part 6: 5분)          한계와 다음 단계, Q&A
```

발표 전 강조: **Part 4가 핵심 evidence**다. 시간이 부족하면 Part 2-3을 압축하더라도 Part 4는 반드시 풀로.

---

## 시간 배분 (60분 표준)

| Part | 슬라이드 | 시간 | 슬라이드당 |
|---|---|---|---|
| 1. WHY | 1-5 | 6분 | 1.2분 |
| 2. WHAT | 6-11 | 8분 | 1.3분 |
| 3. SETUP | 12-19 | 12분 | 1.5분 |
| 4. RUN | 20-29 | 20분 | 2분 |
| 5. FINDINGS | 30-35 | 8분 | 1.3분 |
| 6. BEYOND + Q&A | 36-38 | 6분 + 15 | — |

---

# Slide-by-Slide Narrative

## Slide 1 (표지)

> 안녕하세요. 오늘 발표는 "장기 AI 연구를 자동화한다"입니다.
> 부제가 길지만 핵심은 한 줄입니다 — **Hermes Multi-Agent Kanban이 진짜 long-running 연구 워크플로우로 쓸만한가**, 이것을 실제 한국어 에세이 채점 파이프라인으로 검증했습니다.
> 결론부터 말씀드리면: **워크플로우 검증은 PASS**, 모델 파이프라인은 BLOCK이지만 — 이게 가장 의미 있는 결과라는 점을 마지막에 설명드리겠습니다.

**발표 팁**: 결론을 먼저 던지는 게 청중 집중도를 높인다. "BLOCK인데 성공"이라는 모순으로 호기심 유발.

---

## Slide 2 (문제 정의)

> 우리가 LLM agent로 ML 연구를 한다고 할 때 부딪히는 5가지 비효율을 봅시다. 직렬화, 컨텍스트 손실, 인간 개입점 모호, 재현성 결여, escalation 부재.
> 특히 **5번 escalation 부재**는 LLM agent의 고질병입니다. 실패가 silent하게 처리되거나 token 노이즈에 묻혀서 사람이 못 봅니다.

**Q&A 대비**: "그냥 GitHub Actions로 하면 안 되나요?" → "Actions는 인간 개입점이 PR review로 분리됩니다. 한 워크플로우 안에서 block-resume이 불가능해요."

---

## Slide 3 (이상적 워크플로우)

> 우리가 원하는 건 단순합니다. 단계마다 전문 역할이 자동 routing, 위험 신호 자동 escalation, **인간은 정책 결정만**.
> 마지막 문장이 중요합니다 — 자동화의 목표는 인간 제거가 아니라 **인간 시간의 재배치**입니다.

**강조**: 발표자가 손짓으로 이 한 줄을 짚는다.

---

## Slide 4 (도구 비교)

> 후보는 4가지였습니다. LangGraph는 in-memory가 강점이지만 long-running엔 약합니다. CrewAI는 multi-agent에 좋지만 durable state가 약합니다. AutoGen은 conversation 중심이라 task gate가 약하고요.
> 우리가 Hermes를 고른 이유는 **SQLite + artifact 디렉터리로 모든 상태가 durable**하다는 점, 그리고 **명시적 block/unblock**이 first-class 명령이라는 점입니다.

**Q&A 대비**: "Temporal/Airflow는?" → "워크플로우 엔진은 맞지만 LLM-agent 통합이 별도 구현 필요. Hermes는 profile system으로 LLM agent가 native primitive."

---

## Slide 5 (목적)

> 가장 중요한 슬라이드 중 하나입니다.
> 오늘 우리가 검증한 것은 **모델 성능이 아닙니다**. Toy 데이터 342건, 라이트 모델로 한 거니까요.
> 검증한 것은 **Hermes의 9가지 메커니즘이 long-running cycle에서 동작하는가**입니다.
> 모델 점수가 낮아도, 심지어 leakage가 발견돼서 pipeline이 BLOCK 돼도 — **워크플로우가 끝까지 그 사실을 인지하고 escalation 한다면 워크플로우 검증은 성공**입니다.

**강조**: 청중이 "검증=품질"로 헷갈리지 않도록 명확히 분리.

---

## Slide 6 (핵심 메커니즘)

> Hermes의 핵심은 네 개의 primitive입니다.
> 보드는 SQLite로 영속화된 task queue. 태스크는 atomic하게 claim/run/complete 되고요. 프로파일은 역할 페르소나이고, 워커는 그 프로파일이 spawn한 격리된 실행자입니다.

**Q&A 대비**: "Profile과 worker 차이?" → "Profile은 설정/페르소나, worker는 실제 process. 같은 profile이 동시에 여러 worker로 spawn 가능."

---

## Slide 7 (Task 상태 전이)

> State machine은 6개 상태입니다. **blocked → unblock으로 ready로 돌아온다**는 점이 핵심입니다. 다른 워크플로우 도구의 'failed → 재실행'과 다르게, blocked는 **명시적 인간 결정 게이트**입니다.

**시간 짧으면**: 슬라이드를 빠르게 넘기되 "blocked는 실패가 아니라 게이트"라는 한 줄만 강조.

---

## Slide 8 (9-Point Validation)

> 이 9개 체크는 마지막 검증 보고에서 다시 돌아옵니다. 지금은 "Hermes가 통과해야 할 9개 항목이 있다"는 정도만 인지하시면 됩니다.
> Part 5에서 이 표를 다시 띄우고 "8/9 PASS, 1 NOT OBSERVED"로 결론 내립니다.

---

## Slide 9 (3-layer)

> 설정은 layer로 분리되어 있다는 게 중요합니다.
> 글로벌은 `~/.hermes/`에, 보드와 프로젝트 룰은 보드 디렉터리에, 프로파일과 페르소나는 `profiles/<name>/`에 분리.
> **분리 원칙은 다음 슬라이드(13번)에서 강조하는 핵심 원칙으로 이어집니다.**

---

## Slide 10 (Worker 실행 모델)

> 워커는 codex_app_server 런타임으로 동작합니다. 이건 OpenAI Codex CLI를 long-lived subprocess로 띄우는 모드인데요, **sandbox network_access=false** — 외부 네트워크 차단입니다.
> 이게 우리 세션에서 mlflow 미설치 block을 만들었습니다. 외부 의존성은 **반드시 사전 설치**가 원칙.

**Q&A 대비**: "왜 network=false?" → "보안과 재현성. agent가 임의 URL fetch 못 하게."

---

## Slide 11 (인간 개입)

> swim-lane으로 보시면: 워커가 block, 보드가 알림, 인간이 진단, 코멘트나 AGENTS.md 수정, unblock, 워커가 다시 claim, resume.
> **포인트는 "Block ≠ Failure"**입니다. 다른 워크플로우에서 block은 실패지만, Hermes에선 **체크포인트**입니다.

**강조**: 슬라이드 하단의 callout을 손가락으로 짚는다.

---

## Slide 12 (환경 셋업)

> WSL2 환경에서 5분 셋업입니다.
> 한 가지 함정: WSL2의 시스템 openssl.cnf가 SQL Server 2012 호환 블록으로 깨진 경우가 있어서, `OPENSSL_CONF=/dev/null`로 우회합니다. 이거 모르면 한 시간 디버깅합니다.

**실제 일화**: "저도 처음 30분을 SSL 에러로 날렸어요." (청중 웃음 유도)

---

## Slide 13 (★ 프로파일 vs 프로젝트)

> 이 슬라이드가 **오늘 강의 통틀어 3대 핵심 중 하나**입니다.
> 흔한 실수: 새 프로젝트마다 `essay-tukey`, `recommend-tukey`처럼 프로젝트 prefix를 붙인 프로파일을 만드는 것.
> 이러면 프로파일이 재사용 안 됩니다.
> 올바른 분리: **프로파일은 역할 (재사용 가능한 페르소나), 프로젝트별 룰은 AGENTS.md (격리된 도메인 지식)**.
> 이 원칙을 어기면 6개월 후 profile 30개가 쌓이고 SOUL.md가 도메인 dump가 됩니다.

**강조**: 슬라이드를 멈추고 청중에게 "여러분 회사에서 비슷한 실수 있으신가요?" 한 박자 쉬기.

---

## Slide 14 (6명 프로파일)

> 우리는 6명을 만들었습니다. aristotle은 오케스트레이터, tukey는 데이터 감사관(통계학자 John Tukey 이름), spearman은 평가 통계 분석가, gauss는 모델 엔지니어, ada-lovelace는 코드 작성자, turing은 코드 리뷰어.
> 이름이 사람 이름이지만 **모두 역할만 정의**되어 있습니다. 프로젝트 이야기는 한 줄도 없어요.

---

## Slide 15 (SOUL.md 구조)

> SOUL.md는 4 section입니다. Identity는 영어로, Style/Avoid/Defaults는 한국어로 했습니다. 언어 mix는 허용됩니다 — 단 **각 section은 일관**해야 LLM이 헷갈리지 않습니다.

---

## Slide 16 (AGENTS.md 골격)

> AGENTS.md는 168 lines, 13 section입니다. 두 섹션이 가장 중요한데, **Hard Rules**와 **Toy Scope**입니다. Hard Rules는 워크플로우 gate이고, Toy Scope는 단계별 gate 완화 정책을 명시합니다.

---

## Slide 17 (Hard Rule 8개)

> 8개 룰에 우선순위가 있습니다. Leakage가 1번, PII가 2번. Rule 5와 8은 toy 단계에서 warn-only, full 단계에서 hard-block으로 단계 분리한 게 우리 케이스의 핵심 변경입니다.
> 일반적으로 룰을 만들 때 "strict가 최선"이라 생각하지만, **sample size가 작을 땐 strict gate가 noise에 trip**합니다. 단계별 완화가 필수입니다.

---

## Slide 18 (DAG)

> 8 task를 DAG로 그렸습니다. 주목: **T3a는 사람이 만든 게 아니라 aristotle이 자율로 만든 task**입니다. T3에서 정책 결정 후 "구현은 gauss에 위임"이라 판단해서 child task를 만들었어요. 이게 검증 항목 2번 "decompose 동작"입니다.

**강조**: T3a 노드에 "자율 생성" 배지가 있다는 점.

---

## Slide 19 (CLI)

> CLI 예시는 후속 활용을 위해 슬라이드에 넣었습니다. 발표 중에는 빠르게 넘기되 부록 A4에 cheatsheet 있다고 안내.

---

## Slide 20 (T1 첫 block)

> 이제 실제 사건을 봅니다.
> T1이 시작하자마자 block입니다. AGENTS.md는 `student_school` 필드를 split key로 쓴다고 했는데, sample 342건엔 그 필드가 없었어요. tukey가 즉시 block + 이유 보고.
> 인간이 진단해서 "location을 proxy로 쓰자"고 결정, AGENTS.md를 수정, unblock. T1 정상 done.
> **여기가 첫 번째 block-resume 사이클**입니다.

---

## Slide 21 (T3a 자율 decompose)

> 두 번째 흥미로운 사건: T3가 "분할 정책 결정" task였는데, aristotle이 정책만 결정하고 구현은 **자동으로 T3a라는 child task를 만들어 gauss에 위임**했습니다.
> 이게 우리가 사전에 설계 안 한 동작입니다. **워커가 워크플로우를 자율 확장**한 거예요.

**Q&A 대비**: "이게 위험하지 않나? 무한 분기?" → "max-retries와 dispatch --max로 cap. 또 새 task도 같은 룰 적용."

---

## Slide 22 (auto promotion)

> 흔한 워크플로우 동작이지만 evidence가 강합니다. SQLite의 task_events 테이블에 promoted 이벤트가 영구 기록됩니다. **재현 명령**도 명시했어요 — sqlite3로 query 가능.

---

## Slide 23 (T5 첫 block - 환경)

> T5는 4 model × 5 fold = 20 MLflow run을 돌려야 하는 가장 무거운 task였습니다.
> 첫 시도에서 mlflow 미설치로 block. 중요한 건 **gauss가 train.py와 4개 config을 이미 작성한 채로** block 했다는 점입니다. 부분 산출물 보존, repro 명령 자동 첨부.
> 이게 "silent fail 금지" Hard Rule #7의 실제 작동입니다.

---

## Slide 24 (T5 두 번째 block - gate)

> mlflow 설치 후 retry. 학습은 성공했는데 결과가 이상합니다.
> M1 dummy는 -0.10 — 정상. **M2 length 단변량이 0.19, M3 TF-IDF가 0.03**. 단순한 모델이 복잡한 모델보다 높습니다 (단조성 위반).
> 게다가 M2와 M4가 human ceiling 0.179를 초과 — Rule #8 위반.
> gauss는 자동으로 block. **gate가 학습 결과를 받아들이지 않은 것**입니다.

---

## Slide 25 (★ AGENTS.md 수정)

> **두 번째 핵심 슬라이드**입니다.
> 우리가 진단합니다: M3는 sample 251에 feature 337K — 극심한 overfit, valid에서 noise. Ceiling 0.179는 sample 342건 ICC라 표준오차가 ±0.10. **즉 strict gate가 toy 단계엔 부적합**.
> AGENTS.md를 5곳 수정했습니다:
> 1. Rule 5: strict → toy=warn / full=block
> 2. Rule 8: metric 단위 일치 + bootstrap CI
> 3. student_school → student.location (3곳)
> 4. Toy Scope 섹션 신설
> **여기가 인간 개입의 정수**입니다 — 코드 수정이 아니라 **정책 수정**.

**강조**: 슬라이드 멈추고 "정책 수정과 코드 수정의 차이가 무엇일까요?" 청중에게 던지기.

---

## Slide 26 (T5 → done)

> unblock 후 retry 3분 21초 만에 done. gauss는 **AGENTS.md 변경을 자동으로 reload**해서 warn-only 정책 인지, warning만 task body에 기록한 채 다음 단계로 진행 허용.

---

## Slide 27 (T6 + T7 병렬)

> T5 done → T6/T7 자동 promote → **병렬 spawn**. spearman과 turing이 동시에 같은 T5 산출물을 read.
> DAG fan-out이 정상 작동 검증.

---

## Slide 28 (★ T7 leakage 발견)

> **세 번째 핵심 슬라이드**입니다.
> turing이 코드를 검토하다가 발견했습니다: `build_features.py`가 label JSON을 다시 열어서 **paragraph_count와 correction_count를 feature로 사용**.
> correction_count는 채점자가 단 빨간 줄 개수입니다. 즉 모델은 "쓰기 품질"이 아니라 "채점자가 얼마나 표시했나"를 학습한 거예요.
> M2/M4가 ceiling 위로 나온 진짜 원인이 **noise가 아니라 실제 leakage**였습니다. **우리도 못 본 걸 turing이 찾았어요.**
> Review task는 multi-agent 시스템의 **가장 강한 안전망**입니다.

**강조**: 슬라이드를 멈추고 "여러분 코드 리뷰가 이 정도 했었나요?" 청중 자기성찰 유도.

---

## Slide 29 (T8 종합)

> aristotle은 T6 평가 + T7 리뷰 + 우리가 단 코멘트(다음 사이클 권고)를 모두 컨텍스트로 받아 종합 보고를 만듭니다.
> 산출은 final_report.md와 hermes_validation.md 둘.
> **판정 2-axis**: Pipeline = BLOCK, Hermes workflow = PASS.

---

## Slide 30 (2-axis 매트릭스)

> 4 사분면입니다. 우리는 좌하단 "Pipeline BLOCK + Workflow PASS".
> 이게 **가장 의미 있는 결과**라는 게 오늘의 핵심 메시지입니다.
> 워크플로우가 잘 작동했기 때문에 leakage를 잡아냈고, 잡아냈기 때문에 pipeline을 BLOCK으로 보호한 거예요.
> Pipeline PASS + Workflow PASS면 좋은 모델일 수는 있지만, leakage가 있어도 못 잡았다는 의미일 수도 있습니다. 즉 **이번 결과가 다음 사이클의 fix 방향을 명확히 알려줍니다**.

**강조**: "BLOCK이 성공"의 모순을 청중이 이해하도록 충분히 시간을 둔다.

---

## Slide 31 (9-Point 결과표)

> 결과표입니다. 8/9 PASS, 1 cron만 NOT OBSERVED.
> 우리 워크플로우엔 cron task가 없었으니까 합리적이지만, 다음 사이클에 한 개 추가하면 9/9가 됩니다.

---

## Slide 32 (timeline)

> 3번의 block-resume을 timeline으로 봅니다.
> T1 한 번, T5 두 번, T7가 conclusion-block. 각 사이클이 깔끔하게 진단 → 정책수정/외부조치 → resume.
> 시간으로는 1차 사이클 14:56 시작, 15:49 종결 — **53분 동안 8 task + 1 자율 task가 자동 실행**.

---

## Slide 33 (5 패턴)

> 검증된 패턴 5가지를 아이콘으로 압축. 자동 승격, 자율 decompose, 정책 인지, 산출물 누적, escalation.
> 이 5가지가 다른 워크플로우 도구에선 부분적으로만 지원합니다. Hermes는 모두 first-class.

---

## Slide 34 (Lessons 4)

> 일반화된 lesson 4가지입니다.
> 1번 "gate는 단계별": strict로만 만들면 토이 단계에서 매번 trip.
> 2번 "sample size가 gate 폭 결정": bootstrap CI 필수.
> 3번 "외부 의존은 사전 검증 task": 우리도 mlflow에서 한 번 당했음.
> 4번 "review task는 가장 강한 안전망": 우리가 못 본 leakage를 잡음.

---

## Slide 35 (Anti-pattern)

> 하지 말 것 4가지. 특히 첫 번째 "프로파일에 도메인 룰"이 가장 흔한 실수입니다. Slide 13의 원칙과 짝.

---

## Slide 36 (한계)

> 솔직하게 한계도 말씀드립니다. Toy 342건은 fold valid_n이 16, 11처럼 작아서 단일 sample 변동이 큽니다. Cron 미검증, sandbox network=false 인지의 어려움, 단일 워크스페이스(per-task worktree 미사용) 등.

---

## Slide 37 (다음 사이클)

> 다음 사이클 권고 3가지: leakage fix, cron 검증, 풀단계 진입 시 Toy Scope 섹션 삭제.
> **풀단계 진입은 별도 결정 task**로 만들어야 합니다. 자동 격상하면 위험.

---

## Slide 38 (Q&A)

> 산출물은 모두 docs/ 폴더 + workspace/에 보존. GitHub issue 두 개도 발생했어요 — #5736과 #30908. 직접 시도하시는 분은 참고하시면 좋습니다.
> 감사합니다. 질문 받겠습니다.

---

# 강의 운영 팁

## 사전 준비

- 시연 demo 환경: `essay-auto-scoring-research` 보드를 백업해두고 강의 직전 복원
- 백업 영상: live demo가 실패할 경우를 대비해 핵심 lifecycle 1분 녹화본 준비
- 청중에게 미리 안내: "코드 실습은 없고, 결과 해석과 워크플로우 패턴이 핵심"

## 흐름 조절

- **Part 4가 길어진다면** Part 3의 슬라이드 12, 15, 17은 빠르게 넘긴다
- **시간이 남으면** Slide 25, 28, 30에 시간 더 투자 — 가장 강력한 evidence
- **시간이 모자라면** Slide 35 (anti-pattern) 생략

## 청중 인터랙션 포인트

| 슬라이드 | 인터랙션 |
|---|---|
| 5 | "검증 목적이 모델 성능이 아니라 워크플로우인 게 왜 중요할까요?" |
| 13 | "여러분 회사에서 비슷한 실수 있으신가요?" |
| 25 | "정책 수정과 코드 수정의 차이가 무엇일까요?" |
| 28 | "여러분 코드 리뷰가 이 정도 했었나요?" |
| 30 | "BLOCK이 성공이라는 게 무슨 뜻일까요?" |

## 예상 Q&A

**Q1. Hermes를 production에서 써본 사례가 있나?**
A. 본 검증은 toy 단계입니다. Nous Research 공식 사례와 finance 워크플로우 사례가 있고 (Binance trading 자동화 등), 본격 production 적용은 별도 데이터로 추가 검증 후 결정해야 합니다.

**Q2. cost는 어떻게 되나?**
A. Codex CLI 기반이라 OpenAI ChatGPT subscription 또는 API 종량제. 우리 53분 세션은 medium 모델 기준 대략 X USD 예상 (정확한 값은 mlflow logs 참조). LangGraph 등 대비 비싸지 않음.

**Q3. 다른 LLM provider도 되나?**
A. Anthropic Claude 가능. 우리 세션에서도 처음엔 mix하려 했으나 third-party usage 제한에 걸려서 Codex로 통일했습니다. 안정성 위해 single provider 권장.

**Q4. 코드 결과의 reproducibility?**
A. seed 고정 + config_hash + package_versions + MLflow run ID로 4중 기록. T8 final_report에 모든 run ID 명시.

**Q5. 인간 개입 빈도가 너무 잦지 않나?**
A. 본 세션은 검증 목적상 일부러 작은 정책 변경으로 cycle을 만들었습니다. 실제 production에선 AGENTS.md를 안정화 후엔 block 빈도 급감.

**Q6. 보드를 여러 팀이 공유 가능?**
A. SQLite + filesystem 기반이라 동일 머신/마운트면 가능. 멀티 호스트는 별도 sync 필요 (gateway dispatcher가 SQL I/O 이슈 있음, GitHub #30908 참조).

---

# 90분 워크숍 포맷 (확장)

60분 발표 + 30분 hands-on lab

| 시간 | 활동 |
|---|---|
| 0-45 | Part 1-5 발표 |
| 45-60 | live demo (T5 unblock + retry 재현, 또는 새 작은 task 1개 생성) |
| 60-75 | hands-on: 청중이 자기 노트북에서 `hermes kanban create` 한 개 시도 |
| 75-90 | Q&A + 다음 단계 (Part 6) |

---

# 발표 자료 사용 라이선스 / 출처

본 narrative와 슬라이드 원고는 본 세션의 실측 데이터를 기반으로 작성됨.
- 데이터: AIHub K-12 서술형 답안 (sample 342건)
- 시스템: Nous Research Hermes Agent v0.14.0
- 모델: OpenAI Codex (gpt-5.5, codex_app_server runtime)
- 실측 보고서: `docs/final_report_v_1_0.md`, `docs/hermes_validation_v_1_0.md`

— 끝 —

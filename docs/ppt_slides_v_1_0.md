# PPT 슬라이드 원고 v1.0

> **목적**: PowerPoint/Keynote/Google Slides 등에 옮겨 적을 슬라이드 내용 + 각 페이지의 디자인 프롬프트(이미지 생성 AI 또는 디자이너용).
> **분량**: 38 본문 + 4 부록 = 42 슬라이드.
> **테마 통일**:
> - 색상 팔레트: 다크 네이비 배경 (#0E1525) + 시안 (#22D3EE) + 라임 (#A3E635) + 화이트 텍스트 (#F8FAFC)
> - 폰트: 제목 = Pretendard Bold / 본문 = Pretendard Regular / 코드 = JetBrains Mono
> - 좌상단 footer: "Hermes Kanban 검증 세션 · 2026-05-27"
> - 우상단 페이지 번호
> - 시각 스타일: minimal flat + isometric illustrations + soft glow

---

## Slide 1 — 표지

### 슬라이드 내용
- 메인 타이틀: **장기 AI 연구를 자동화한다**
- 서브 타이틀: Hermes Multi-Agent Kanban으로 검증한 8단계 한국어 채점 파이프라인
- 일시: 2026-05-27
- 발표자: (이름)
- 하단 캡션: "Toy 데이터 + 라이트 모델로 검증한 워크플로우 도입 가이드"

### 페이지 디자인 프롬프트
```
Dark navy background (#0E1525) with subtle starfield texture.
Large cyan glowing title text centered slightly above the middle.
Bottom-right: isometric illustration of a translucent kanban board floating,
with 8 small task cards arranged in swim lanes moving through stages
(todo → ready → running → done). Cards emit soft cyan glow.
Minimal, no clutter, premium tech keynote feel.
```

---

## Slide 2 — 문제 정의

### 슬라이드 내용
**LLM 시대 ML 연구의 5가지 비효율**

| # | 문제 | 증상 |
|---|---|---|
| 1 | 작업 직렬화 | 모델/평가/리뷰가 한 사람·한 채팅 안에서 순차 |
| 2 | 컨텍스트 손실 | 긴 세션 끝에서 초기 결정 사라짐 |
| 3 | 인간 개입점 모호 | 어디서 멈추고 어디서 자동 진행할지 불명확 |
| 4 | 재현성 결여 | seed/config/artifact 흩어짐 |
| 5 | Escalation 부재 | 실패가 silent 처리되거나 noise에 묻힘 |

### 페이지 디자인 프롬프트
```
5-column flat icon grid on dark navy background.
Each column has a minimal monochrome line icon in cyan
(serial timeline, fading bubbles, question mark, broken puzzle, silent bell with X).
Below each icon, one-line label in white sans-serif.
Title at top in large white bold.
```

---

## Slide 3 — 이상적 워크플로우

### 슬라이드 내용
**우리가 원하는 것**

- 각 단계 → 전문 역할에 **자동 라우팅**
- 위험 신호 → 자동 **escalation + block**
- 인간은 **정책 결정만**, 실행은 위임
- 산출물은 **durable + 재현 가능**

### 페이지 디자인 프롬프트
```
Horizontal flow diagram with 4 stages connected by glowing cyan arrows:
[Input] → [Auto-Routing 5 worker icons] → [Block ⛔ + Human icon 🧑] → [Resume → Done ✓].
Each stage is an isometric card with subtle drop shadow.
Background dark navy with diagonal grid lines, very subtle.
Bottom: caption "자동화의 목표는 인간 제거가 아니라 인간 시간의 재배치"
```

---

## Slide 4 — 검증 대상 후보 비교

### 슬라이드 내용

| 도구 | Long-running | 인간 개입점 | Durable state | 본 세션 사용 |
|---|---|---|---|---|
| LangGraph | △ in-memory | 코드 수정 필요 | △ (외부 store) | |
| CrewAI | △ | weak | X | |
| AutoGen | ○ | weak | △ | |
| **Hermes Multi-Agent Kanban** | **○** | **명시적 block/unblock** | **○ SQLite + artifacts** | **✓** |

### 페이지 디자인 프롬프트
```
4-row comparison table on dark navy.
Last row (Hermes) highlighted with cyan glow border and bold text.
Table cells use simple ✓/△/X symbols colored green/amber/red.
Right side: small isometric icon of SQLite database + kanban board badge.
```

---

## Slide 5 — 이 세션의 목적

### 슬라이드 내용
**검증 ≠ 모델 성능 / 검증 = 워크플로우 동작**

- 데이터: 한국어 K-12 에세이 **toy 342건** (전체 50K 中)
- 모델: dummy → length → TF-IDF+Ridge → LightGBM (라이트)
- 검증 대상: **Hermes의 9가지 메커니즘이 long-running cycle에서 동작하는가**
- 모델 점수가 낮아도 OK, **워크플로우가 끝까지 돌면 성공**

### 페이지 디자인 프롬프트
```
Split screen. Left half: small/light icon (mini brain, small dataset chip) — labeled "Toy".
Right half: large gear-and-pipeline icon glowing cyan — labeled "Workflow ⭐".
Big arrow between them with text "검증 대상은 → 오른쪽".
Top title bold white. Bottom callout box highlighting the key sentence in lime.
```

---

## Slide 6 — Hermes Kanban 핵심 메커니즘

### 슬라이드 내용
**SQLite-backed durable task queue + profile-based worker spawn**

- 보드(board) = 하나의 프로젝트/워크스트림 — 자체 DB + workspace
- 태스크(task) = 원자적으로 claim/run/complete되는 작업 단위
- 프로파일(profile) = 역할 페르소나 (모델·SOUL.md·tools 묶음)
- 워커(worker) = 프로파일이 claim한 task를 격리 환경에서 실행

### 페이지 디자인 프롬프트
```
4-component isometric diagram:
[Board cylinder with kanban grid on top] — [Task cards stack] — [Profile avatar with mask icon] — [Worker robot in glass box].
Arrows show: board contains tasks → profile claims task → spawns worker.
Dark navy background, components glow cyan. Annotations in small white text.
```

---

## Slide 7 — Task 상태 전이

### 슬라이드 내용
**Task 생명주기 state machine**

```
   created
      │
      ▼
   ┌──todo──┐                 ┌──→ done
   │        ▼                 │
   │     ready ─claim→ running┤
   │        ▲                 │
   │        │                 ├──→ blocked ──unblock─┐
   │        │                 │                       │
   │        └─────promote─────┴──→ failed             │
   │                                                  │
   └──────────────────────────────────────────────────┘
```

전이 트리거: parent done → child promote / claim → spawn / `kanban_block` / `kanban_complete` / 인간 `unblock`

### 페이지 디자인 프롬프트
```
Large clean state-machine diagram centered on slide.
Nodes are rounded rectangles with subtle gradient fills.
Transition arrows labeled with small badges (auto / human / system).
Dark navy background, lines in cyan, nodes in lighter navy.
Bottom note in monospace explaining the key triggers.
```

---

## Slide 8 — 9-Point Validation 항목

### 슬라이드 내용
**Hermes가 통과해야 할 9가지 체크**

1. Task 자동 승격 (parent done → child ready)
2. Decompose 동작 (큰 task → 작은 task 자율 생성)
3. Profile 자동 라우팅
4. Handoff metadata 전달
5. Workspace 격리
6. Circuit breaker (실패 N회 → 자동 block)
7. 인간 개입점 (block/comment/unblock)
8. 메모리 누적 (durable artifacts)
9. Cron trigger (스케줄 기반 자동 실행)

### 페이지 디자인 프롬프트
```
3x3 checklist grid on dark navy.
Each cell: number badge + short label in white + small icon (auto-promote arrow, fork, route, package, isolation box, breaker, human-hand, archive, clock).
Cells have subtle borders. Slight glow on each.
Title bar at top in cyan.
```

---

## Slide 9 — 핵심 3-layer 구조

### 슬라이드 내용
**설정은 3개 layer로 분리된다**

| Layer | 위치 | 책임 |
|---|---|---|
| 1. 글로벌 | `~/.hermes/config.yaml`, `.env` | model provider, dispatcher 주기, secrets |
| 2. 보드 + 프로젝트 룰 | `board.json`, `AGENTS.md` | 워크플로우 gate, 도메인 룰 |
| 3. 프로파일 + 페르소나 | `~/.hermes/profiles/<name>/` | 역할별 모델 선택, SOUL.md |

→ **분리 원칙**: 도메인 룰은 AGENTS.md, 역할 페르소나는 SOUL.md

### 페이지 디자인 프롬프트
```
3-layer stacked transparent isometric panels (like a glass cake).
Top: profile masks. Middle: kanban board + AGENTS scroll. Bottom: gear icon + key icon.
Side annotations point to each layer with its file path in monospace.
Dark navy backdrop, panels emit faint cyan glow.
```

---

## Slide 10 — Worker 실행 모델

### 슬라이드 내용
**Profile → Codex CLI subprocess**

- Runtime: `codex_app_server` (로컬 Codex CLI를 long-lived subprocess로 실행)
- Sandbox: `workspace-write`, **`network_access=false`**
- 환경 dependency는 **외부에서 사전 설치 필수**
- 실행: `hermes -p <profile> work kanban task <id>`

### 페이지 디자인 프롬프트
```
Sequence diagram (vertical).
Actors left-to-right: Dispatcher → Profile → Codex CLI subprocess → Sandbox box.
Messages: "claim task", "spawn", "run with sandbox network=false", "complete/block".
Sandbox box has a "no-network" wifi-strikethrough icon.
Dark navy, lines cyan, actor heads as small avatar circles.
```

---

## Slide 11 — 인간 개입 지점

### 슬라이드 내용
**Block은 실패가 아니라 체크포인트**

```
Worker        Board         Human
   │            │             │
   │── block ──▶│             │
   │            │── notify ──▶│
   │            │             │── 진단
   │            │             │── AGENTS.md edit
   │            │◀── comment ─│
   │            │◀── unblock ─│
   │◀── claim ──│             │
   │── resume                 │
```

### 페이지 디자인 프롬프트
```
Swim-lane diagram with 3 columns labeled Worker / Board / Human.
Steps shown as numbered boxes with arrows crossing lanes.
Human column has a person icon at top, worker has robot icon, board has kanban icon.
Highlight: "Block ≠ Failure" callout in lime at the bottom.
```

---

## Slide 12 — 환경 셋업 (WSL2 + Codex OAuth)

### 슬라이드 내용
**5분 셋업**

```bash
pip install hermes-agent
hermes setup                    # 설정 마법사
hermes login codex              # OAuth
# ~/.hermes/.env 에 추가:
OPENSSL_CONF=/dev/null          # WSL2 SSL config 충돌 회피
TELEGRAM_BOT_TOKEN=...
```

⚠️ 주의: WSL2의 시스템 openssl.cnf가 깨진 환경에서 `[SSL] error in system default config` 발생 시 위 변수로 우회.

### 페이지 디자인 프롬프트
```
Terminal mockup at center on dark navy.
Terminal has neon green prompt, cyan command text, white output.
Top-right: WSL2 + Codex logos in small badges.
Bottom: warning box in amber with the SSL workaround tip.
```

---

## Slide 13 — ★ 프로파일 vs 프로젝트 원칙

### 슬라이드 내용
**"프로파일은 역할로, 프로젝트는 AGENTS.md로"**

| 잘못된 분리 | 올바른 분리 |
|---|---|
| `essay-tukey` 프로파일 | `tukey` 프로파일 (역할: 데이터 감사관) |
| SOUL.md에 "이 프로젝트의 라벨 형식은…" | AGENTS.md에 "라벨 형식은…" |
| 새 프로젝트마다 프로파일 추가 | 새 프로젝트마다 AGENTS.md만 |

→ 프로파일은 **재사용**, AGENTS.md는 **프로젝트별 격리**

### 페이지 디자인 프롬프트
```
Side-by-side comparison cards.
Left card (red tinted border): "Wrong" — profile names with project prefix.
Right card (cyan border): "Right" — generic role names.
Below: large lime callout box with the rule sentence in bold.
Icons: left has stacked redundant masks, right has 6 distinct role masks.
```

---

## Slide 14 — 6명 프로파일 (역할 기반)

### 슬라이드 내용

| 프로파일 | 역할 | 모티프 |
|---|---|---|
| **aristotle** | 연구 오케스트레이터 | 종합 판단, 정책 |
| **tukey** | 데이터 감사관 (EDA) | 분포, leakage 검사 |
| **spearman** | 평가 통계 분석가 | metric, ceiling, segment |
| **gauss** | 모델·실험 엔지니어 | baseline, MLflow |
| **ada-lovelace** | 코드·파이프라인 작성 | 알고리즘 구현 |
| **turing** | 코드 리뷰 + leakage 검증 | WRONG/FRAGILE/STYLE 분류 |

### 페이지 디자인 프롬프트
```
6 hexagonal portrait tiles arranged in 2 rows of 3.
Each tile: stylized monochrome portrait (philosopher/scientist silhouette) +
name in cyan + role in white below.
Hexes have thin cyan borders, dark navy background, soft glow.
Style reminiscent of card game character roster.
```

---

## Slide 15 — SOUL.md 4-section 구조

### 슬라이드 내용

```markdown
# Identity (English)
You are Aristotle, a research orchestrator…

# Style (Korean)
- 결정은 근거와 함께 명시
- 불확실하면 명시적으로 표시

# Avoid (Korean)
- silent fail
- 과도한 도메인 가정

# Defaults (Korean)
- 답변은 한국어
- 코드 주석은 영어
```

→ **언어 mix 허용**, 단 각 섹션은 일관

### 페이지 디자인 프롬프트
```
Code editor mockup showing markdown with syntax highlighting (Identity/Style/Avoid/Defaults).
Cyan header lines, white body, language tags shown as small chips next to headers.
Right side: small icon strip representing "identity / tone / restrictions / fallbacks".
```

---

## Slide 16 — AGENTS.md 골격 (168 lines)

### 슬라이드 내용
**섹션 목차**

1. Project Overview
2. Hard Rules (Priority Order) ← gate
3. Data Locations
4. Domain Facts
5. **Toy Scope** ← 단계별 gate 완화
6. Pipeline Conventions
7. Build & Test Commands
8. Definition of Done
9. When Auditing / Splitting / Modeling / Evaluating / Reviewing
10. Forbidden
11. Escalation
12. Human Approval Required
13. References

### 페이지 디자인 프롬프트
```
Vertical TOC list on left side of slide as elegant numbered scroll.
Right side: stylized open scroll/parchment with markdown headings visible.
Highlight Hard Rules and Toy Scope sections with cyan glow.
Dark navy background, parchment in warm off-white.
```

---

## Slide 17 — Hard Rule 8개 우선순위

### 슬라이드 내용

| 우선 | 룰 | 위반 시 |
|---|---|---|
| 1 | Test set leakage 금지 | hard-block |
| 2 | 학생 PII 외부 LLM 금지 | hard-block |
| 3 | 모든 실험 MLflow 등록 | hard-block |
| 4 | Rubric 가중치 JSON 외부화 | hard-block |
| 5 | 베이스라인 단조 진화 | **toy: warn / full: block** |
| 6 | task 산출물 경로 + 검증 명령 | hard-block |
| 7 | silent 실패 금지 | hard-block |
| 8 | 인간 ceiling 초과 leakage 의심 | **toy: warn / full: block** |

### 페이지 디자인 프롬프트
```
Vertical ladder/staircase visualization with 8 steps.
Each step shows rule number + short text + traffic-light icon (red hard-block, amber warn).
Steps 5 and 8 highlighted with amber color to show toy-policy difference.
Dark navy background, ladder rendered with isometric perspective.
```

---

## Slide 18 — 8 task 그래프 (T1~T8 + T3a)

### 슬라이드 내용

```
            T1 (tukey: 데이터 audit)
              │
              ▼
            T2 (spearman: 인간 ceiling)
              │
              ▼
            T3 (aristotle: 분할 정책)
              │
              ▼
         T3a (gauss: split 구현)     ← 자율 생성
              │
              ▼
            T4 (gauss: 피처)
              │
              ▼
            T5 (gauss: 베이스라인 4종)
              │
        ┌─────┴─────┐
        ▼           ▼
       T6          T7
   (spearman)   (turing)
   평가         리뷰
        │           │
        └─────┬─────┘
              ▼
            T8 (aristotle: 종합)
```

### 페이지 디자인 프롬프트
```
DAG diagram centered. Nodes are pill-shaped with profile icon + task name.
Edges are glowing cyan lines.
Node T3a has a small "自" badge indicating "autonomously created".
T6 and T7 shown side-by-side at same vertical level (parallel).
Dark navy background. Slight depth shading on each node.
```

---

## Slide 19 — 보드 + 태스크 생성 CLI

### 슬라이드 내용

```bash
# 보드 생성
hermes kanban boards create essay-auto-scoring-research \
  --name "서술형 자동채점 연구" --icon "🧪"
hermes kanban boards set-default-workdir \
  essay-auto-scoring-research /home/dev/work/essay-auto-scoring-research

# 태스크 생성 (예: T5)
hermes kanban create "T5: 베이스라인 모델 4종" \
  --assignee gauss \
  --workspace dir:/home/dev/work/essay-auto-scoring-research \
  --max-runtime 30m --max-retries 1 \
  --parent t_2c34c9dc \
  --body "$(cat T5_body.md)"
```

### 페이지 디자인 프롬프트
```
Two terminal mockup blocks vertically stacked.
Top block: board creation commands.
Bottom block: task creation command with each flag annotated by floating cyan callouts.
Background dark navy, terminals slightly translucent.
```

---

## Slide 20 — T1: 첫 block (스키마 불일치)

### 슬라이드 내용
**상황**: T1 audit 중 AGENTS.md가 명시한 `student_school` 필드가 sample 342건에 부재

**워크플로우 반응**:
- tukey가 즉시 `kanban_block`
- reason: "schema mismatch: student_school absent (7 location groups instead)"
- 인간 진단 → `student.location`을 group proxy로 승인 + AGENTS.md 수정
- `unblock` → T1 정상 done

→ **silent fail 없이 인간 결정으로 escalate**

### 페이지 디자인 프롬프트
```
Card mockup of a kanban task in "blocked" state with red border and ⛔ icon.
Below card: comment thread showing tukey's block reason and a human reply approving location proxy.
Right side: small "AGENTS.md edit" diff snippet showing the rule change.
Dark navy background, sequence arrow connecting block → approve → unblock.
```

---

## Slide 21 — T3 자율 decompose (T3a 생성)

### 슬라이드 내용
**T3 (aristotle: 분할 정책 결정)**
- aristotle이 정책만 결정 후 — "구현은 gauss에 위임" 판단
- **자율로 T3a 생성**: "stratified location group split implementation"
- assignee = gauss, parent = T3
- T3 done → T3a auto-promote → gauss 실행 → done

→ **사람이 미리 분해하지 않은 작업도 worker가 만든다**

### 페이지 디자인 프롬프트
```
DAG diagram showing T3 node spawning a child T3a node with a glowing "auto" badge.
Animation hint: cyan particle trail from T3 to T3a.
Annotation arrow points to T3a: "Created by aristotle, not human".
Right side: hermes_kanban_create tool call mockup in monospace.
```

---

## Slide 22 — T4 → T5 자동 promotion

### 슬라이드 내용
**Parent done이 child를 자동 ready로**

```
event id 47: T4 completed
event id 48: T5 promoted (todo → ready)
event id 49: T5 claimed by gauss
```

- 인간 dispatch 명령 없이 dispatcher tick에서 자동 실행
- Event log는 **kanban.db `task_events` 테이블에 영구 기록**
- 재현 명령: `sqlite3 kanban.db "select * from task_events where task_id='t_130be2fe'"`

### 페이지 디자인 프롬프트
```
Three-card timeline horizontally arranged:
[T4 done ✓] → [auto-promote 🔄] → [T5 ready ▶ claimed by gauss].
Below: SQL query mockup showing the task_events rows with cyan column highlights.
Dark navy background. Glow effect on the auto-promote arrow.
```

---

## Slide 23 — T5 첫 block (환경 미비)

### 슬라이드 내용
**상황**: T5 worker가 `import mlflow` 실패

**Hermes 반응**:
- gauss가 train.py + 4개 config 초안 작성한 채로 `kanban_block`
- reason: "MLflow is required by Hard Rule #3, but pip install network=false rejected"
- **repro 명령 자동 첨부**: `python3 pipelines/train.py --config all`

→ **부분 산출물 보존 + 정확한 진단 메시지**

### 페이지 디자인 프롬프트
```
Two-panel layout:
Left: Blocked card with the error reason in monospace amber text.
Right: tree view of partial artifacts (train.py, 4 yaml configs) shown as file icons.
Caption: "Even on block, work is preserved."
Dark navy background, amber highlights for warning.
```

---

## Slide 24 — T5 두 번째 block (gate violation)

### 슬라이드 내용
**상황**: 외부에서 mlflow 설치 → unblock → run #11 학습은 성공

| 모델 | QWK | 비고 |
|---|---|---|
| M1 dummy | -0.10 | 정상 |
| **M2 length** | **0.19** | ceiling 초과 |
| M3 TF-IDF | 0.03 | M2보다 낮음 (단조성 위반) |
| **M4 LightGBM** | **0.31** | ceiling 초과 |

**자동 감지된 위반**:
- Hard Rule #5: M2 > M3 (단조성 깨짐)
- Hard Rule #8: M2/M4 > human ceiling 0.179

→ **학습 자체는 성공했지만 gate가 결과 수용 거부**

### 페이지 디자인 프롬프트
```
Bar chart of QWK values for M1-M4.
M2 and M4 bars colored amber with warning triangle icons.
Horizontal dashed line at 0.179 labeled "Human ceiling".
M3 bar tagged "monotonic break".
Title bar at top in cyan. Subcaption: "Auto-detected by Hard Rules #5 + #8".
```

---

## Slide 25 — ★ 인간 진단 → AGENTS.md 수정

### 슬라이드 내용
**진단**:
- M3 untuned Ridge가 p=337K ≫ n=251 overfit
- Human ceiling 0.179는 단일 점추정 — sample 342건 noise 폭 ±0.10
- → strict gate가 **toy 단계엔 부적합**

**수정 (AGENTS.md, 5곳)**:
1. Rule #5: strict → toy=warn / full=block + bootstrap CI
2. Rule #8: metric 단위 일치 + CI block 조건
3. Pipeline Conventions: `student_school` → `student.location`
4. When Splitting: 동일 + small-fold warning 추가
5. Toy Scope: gate 완화 정책 섹션 신설

### 페이지 디자인 프롬프트
```
Split layout.
Left: diagnostic notes on a clipboard with checkmarks/x marks next to findings.
Right: AGENTS.md before/after diff mockup with red strikethroughs and green additions.
Connecting arrow labeled "Policy edit".
Dark navy background, paper tones for clipboard, code editor tones for diff.
```

---

## Slide 26 — T5 unblock + retry → done

### 슬라이드 내용
**Run #12**: 201s, gate 완화 정책 인지하여 warning만 기록한 채 done

```
[15:30:52] running  log=181B  mlruns=4  models=4
[15:31:43] running  log=181B  mlruns=4  models=4
[15:32:32] running  log=181B  mlruns=7  models=4    ← retry runs
[15:33:24] running  log=181B  mlruns=8  models=4
[15:34:13] done     log=8748B mlruns=8  models=4    ✓
```

→ **AGENTS.md 변경을 worker가 자동 reload**

### 페이지 디자인 프롬프트
```
Monitor-style log mockup with timestamped lines in monospace.
Final "done ✓" line highlighted in lime green with checkmark.
Above the log: T5 card flipping from blocked → done state animation hint.
Dark navy background, terminal-style block.
```

---

## Slide 27 — T6 + T7 병렬 실행

### 슬라이드 내용
**Parent T5 done → T6 + T7 자동 promote, 병렬 spawn**

- T6 (spearman, multi-axis 평가) — 261s
- T7 (turing, 코드+leakage 리뷰) — 308s
- 두 task가 같은 T5 산출물(`workspace/models/`, `mlruns/`) 동시 read

→ **DAG fan-out 처리 검증**

### 페이지 디자인 프롬프트
```
Y-shaped fan-out diagram.
T5 node at top, splits into two parallel lanes for T6 (left) and T7 (right).
Each lane has its own profile avatar + progress bar.
Shared resource pile in middle (folder icon labeled "T5 outputs") with arrows from both lanes.
Dark navy background, cyan + lime lane colors.
```

---

## Slide 28 — ★ T7가 실제 leakage 발견

### 슬라이드 내용
**turing의 conclusion: BLOCK**

> "feature generation reopens label JSON and uses label-side `paragraph` and `correction` annotations for validation features"

| 발견 등급 | 위치 | 내용 |
|---|---|---|
| **WRONG** | `build_features.py:248,296` | `paragraph_count`, `correction_count`가 label-side |
| FRAGILE | `train.py:446` | human_ceiling 0.179 하드코딩 |
| FRAGILE | `make_splits.py:278` | small-fold warning 누락 |
| FRAGILE | `build_features.py:371` | disallowed-key contract 불일치 |

→ **M2/M4가 ceiling 초과한 진짜 원인 = leakage**. 우리가 "noise"라 추측한 것 중 일부는 실제 버그였다.

### 페이지 디자인 프롬프트
```
Bold "BLOCK" stamp in red at top-right corner, slightly tilted.
Below: 4-row finding table with severity badges (WRONG=red, FRAGILE=amber).
Bottom callout in cyan: "Review task is the strongest safety net".
Dark navy background, slight glow on the WRONG row.
```

---

## Slide 29 — T8 종합 (aristotle)

### 슬라이드 내용
**aristotle 입력**: T6 eval + T7 review + 인간 코멘트(다음 사이클 권고 포함)
**aristotle 출력**: 2개 산출물

| 산출물 | 내용 |
|---|---|
| `final_report.md` | Pipeline acceptance 판정 (BLOCK) |
| `hermes_validation.md` | 9-Point 검증 결과 (8/9 PASS) |

**판정 2-axis**:
- Pipeline: **BLOCK** (leakage)
- Hermes workflow: **PASS** (8/9)

### 페이지 디자인 프롬프트
```
Two-document spread layout.
Left doc: "final_report.md" with BLOCK stamp in red corner.
Right doc: "hermes_validation.md" with PASS stamp in lime corner.
Below documents: 2x2 matrix labeled (Pipeline / Hermes Workflow) × (PASS / BLOCK) with results placed.
Dark navy background, document mockups in warm parchment tone.
```

---

## Slide 30 — 최종 판정 2-axis

### 슬라이드 내용

```
                    Hermes workflow
                    PASS       BLOCK
                  ┌───────────┬──────────┐
   Pipeline PASS  │           │          │
                  ├───────────┼──────────┤
   Pipeline BLOCK │ ★ 우리    │          │
                  │ (검증 성공) │          │
                  └───────────┴──────────┘
```

**우리 결과 = "Pipeline BLOCK + Workflow PASS"가 가장 의미 있는 결과**
- 워크플로우가 잘 작동했기 때문에 leakage를 잡아냄
- 잡아냈기 때문에 pipeline을 BLOCK으로 보호

### 페이지 디자인 프롬프트
```
Large 2x2 matrix occupying center of slide.
Our cell highlighted with gold border and star icon.
Each cell has a 1-line interpretation below in small text.
Top-left and bottom-right cells dimmed to draw eye to our cell.
Dark navy background.
```

---

## Slide 31 — 9-Point 검증 결과표

### 슬라이드 내용

| # | 항목 | 결과 | Evidence |
|---|---|---|---|
| 1 | Task 자동 승격 | ✅ | event id 20,21,33,47,63,64,71 |
| 2 | Decompose 동작 | ✅ | T3 → T3a 자율 생성 |
| 3 | Profile 자동 라우팅 | ✅ | 5 profiles 분배 |
| 4 | Handoff metadata | ✅ | T6/T7가 T5 산출물 컨텍스트 인지 |
| 5 | Workspace 격리 | ✅ | T1/splits/features/models/eval/review/final 분리 |
| 6 | Circuit breaker | ✅ | T1, T5×2, T7 자동 block |
| 7 | 인간 개입점 | ✅ | T1·T5 unblock + AGENTS.md 수정 인지 |
| 8 | 메모리 누적 | ✅ | 8 task 산출물 durable 보존 |
| 9 | Cron trigger | ⚠️ | 본 세션 미검증 |

### 페이지 디자인 프롬프트
```
Clean 9-row checklist on dark navy.
Rows 1-8 have lime checkmarks, row 9 has amber warning triangle.
Right column shows tiny evidence snippets in monospace.
Title bar in cyan. Bottom note: "8/9 directly observed".
```

---

## Slide 32 — Block→Resume 사이클 3회 timeline

### 슬라이드 내용

```
14:56 ─ T1 created
        │
        ▼
15:00 ─ T1 BLOCK (student_school 부재)         #1
        │       ↑ 인간: location proxy 승인
15:02 ─ T1 RESUME → done

15:04 ─ T5 BLOCK #1 (mlflow 미설치)            #2
        │       ↑ 인간: pip install
15:13 ─ T5 BLOCK #2 (gate violation)
        │       ↑ 인간: AGENTS.md 수정
15:30 ─ T5 RESUME → done

15:39 ─ T7 BLOCK conclusion (실제 leakage)     #3
        │       ↑ aristotle이 종합 보고로 반영
15:49 ─ T8 done (Pipeline BLOCK + Workflow PASS)
```

### 페이지 디자인 프롬프트
```
Vertical timeline on the left with timestamps.
Three "block-resume" arcs branching to the right side showing diagnosis → fix → resume.
Each arc colored differently (amber for #1, orange for #2, red for #3).
Final node at bottom: "Workflow PASS" with star.
Dark navy background.
```

---

## Slide 33 — 검증된 워크플로우 패턴

### 슬라이드 내용
**다섯 가지 핵심 패턴이 모두 작동**

1. 🔄 **자동 승격** — parent done → child ready
2. 🌱 **자율 decompose** — worker가 child task 생성
3. 📖 **정책 인지** — AGENTS.md 변경을 worker가 자동 반영
4. 📦 **산출물 누적** — durable artifacts + MLflow + DB events
5. 🚨 **Escalation** — block + repro 명령 + 인간 개입점

### 페이지 디자인 프롬프트
```
5-icon grid on dark navy (pentagon arrangement).
Each icon is a stylized minimal flat illustration in cyan.
Labels below each icon in white.
Center: small "Hermes" logo or symbol.
Soft radial glow from center outward.
```

---

## Slide 34 — Lessons (4)

### 슬라이드 내용
1. **Gate는 strict가 아니라 단계별** — toy(warn) → full(block) 전환
2. **Sample size가 gate 폭을 결정** — bootstrap CI 필수
3. **외부 dependency는 사전 검증 task로** — T0 dependency check 추가 필요
4. **Review task가 가장 강한 안전망** — turing이 우리도 못 본 leakage 발견

### 페이지 디자인 프롬프트
```
2x2 quadrant card layout.
Each card has a large number, bold lesson title in cyan, and 1-line elaboration in white.
Subtle iconography: ladder (1), measuring tape (2), filter (3), magnifying glass over code (4).
Dark navy background.
```

---

## Slide 35 — Anti-pattern 회피

### 슬라이드 내용
**하지 말 것**

- ❌ 프로파일에 도메인 룰 (재사용성 파괴)
- ❌ AGENTS.md에 환경 setup 명령 (책임 혼선)
- ❌ 점추정으로 strict block (noise 1σ에 trip)
- ❌ 큰 task를 분할 안 하고 그대로 dispatch (Codex timeout 위험)

### 페이지 디자인 프롬프트
```
4 horizontal rows, each starting with a large red ❌ symbol.
After X: the anti-pattern in white, followed by ":" and the consequence in amber italics.
Dark navy background. Subtle red glow underneath each row.
```

---

## Slide 36 — 한계 (this session)

### 슬라이드 내용
**짚어야 할 한계**

- Toy 342건 → fold valid_n=16,11 (단일 sample 변동 큼)
- Cron trigger 미검증 → 9/9 미완
- Codex sandbox network=false → 외부 의존 인지 어려움
- 단일 워크스페이스 (per-task git worktree 미사용)

### 페이지 디자인 프롬프트
```
4 limitation cards in a horizontal row.
Each card has a small warning icon, the limitation, and an "Impact" mini-tag below.
Cards have amber accent borders.
Dark navy background.
```

---

## Slide 37 — 다음 사이클 권고

### 슬라이드 내용
**3 step**

1. **Leakage fix**: `pipelines/build_features.py:248,296` 수정 → T4→T5→T6→T7 재dispatch
2. **Cron 검증**: 짧은 scheduled task 1개 추가 → 9/9 완성
3. **풀단계 진입**: 50K 데이터 + Transformer 진입 시 AGENTS.md `Toy Scope` 섹션 삭제 (모든 gate hard-block 격상)

### 페이지 디자인 프롬프트
```
3 numbered cards in a horizontal sequence with arrows between.
Each card title in cyan, body in white.
Cards have slight 3D depth.
At the end: small target/finish-line icon labeled "Production".
Dark navy background.
```

---

## Slide 38 — Q&A / 참고자료

### 슬라이드 내용
**산출물**
- `docs/hermes_validation_v_1_0.md`
- `docs/final_report_v_1_0.md`
- `docs/hermes_kanban_토이_검증_파이프라인_구조_v_1_0.md`
- `workspace/` 전체 + `mlruns/`

**관련 GitHub issues**
- #5736: openai-codex `NoneType` agent loop bug
- #30908: gateway dispatcher SQL I/O error

**참고**
- Hermes 공식 docs: hermes-agent.nousresearch.com
- 본 세션 보드 슬러그: `essay-auto-scoring-research`

**감사합니다 — 질문 환영**

### 페이지 디자인 프롬프트
```
Closing slide with large "감사합니다" in cyan center.
Below: 3-column layout of links/paths in monospace.
Subtle Hermes logo watermark in background, low opacity.
Dark navy background. Premium keynote closing feel.
```

---

## 부록 A1 — ~/.hermes/.env + config.yaml

### 슬라이드 내용

```yaml
# ~/.hermes/config.yaml
model:
  provider: openai-codex
  default: gpt-5.5
  openai_runtime: codex_app_server
kanban:
  failure_limit: 2

# ~/.hermes/.env
OPENSSL_CONF=/dev/null
TELEGRAM_BOT_TOKEN=...
TELEGRAM_ALLOWED_USERS=...
```

### 페이지 디자인 프롬프트
```
Two side-by-side terminal blocks showing the yaml and env files.
Syntax highlighting in cyan/white/amber for keys/values/comments.
Title: "Appendix A1 — Global Config".
Dark navy background.
```

---

## 부록 A2 — AGENTS.md 최종본 TOC

### 슬라이드 내용
- 168 lines, 13 sections
- 핵심 변화: Toy Scope 섹션 신설, Hard Rule #5/#8 toy=warn-only, student_school→student.location 3곳
- 전체 파일: `/home/dev/work/essay-auto-scoring-research/AGENTS.md`

### 페이지 디자인 프롬프트
```
Single tall code/markdown panel showing the TOC of AGENTS.md.
Highlighted (cyan glow) the new/modified sections.
Right side: small diff badges showing "+1 section, ~5 lines modified".
Dark navy background.
```

---

## 부록 A3 — 8 task body 요약 표

### 슬라이드 내용

| Task | 담당 | Goal 1줄 |
|---|---|---|
| T1 | tukey | sample 342건 audit + leakage 사전 검사 |
| T2 | spearman | 3-rater ICC로 human ceiling 산정 |
| T3 | aristotle | 분할 정책 결정 |
| T3a | gauss | StratifiedGroupKFold(k=5) 구현 |
| T4 | gauss | 피처 엔지니어링 (per-fold train-only TF-IDF) |
| T5 | gauss | 4 baseline × 5 fold = 20 MLflow runs |
| T6 | spearman | multi-axis 평가 (overall / per-segment / ceiling) |
| T7 | turing | 코드 + leakage 리뷰 (WRONG/FRAGILE/STYLE) |
| T8 | aristotle | 종합 판정 + Hermes 검증 보고 |

### 페이지 디자인 프롬프트
```
Single 9-row table on dark navy.
Profile icons in left column, monospace IDs in middle, descriptions in right.
Even rows have slight cyan tint for readability.
Title: "Appendix A3 — Task Roster".
```

---

## 부록 A4 — CLI 치트시트

### 슬라이드 내용

```bash
# 보드
hermes kanban boards create <slug>
hermes kanban boards switch <slug>

# 태스크
hermes kanban create "<title>" --assignee <profile> --workspace dir:<path>
hermes kanban link <parent> <child>
hermes kanban show <task_id>
hermes kanban ls

# 실행
hermes kanban dispatch --max 1            # 한 번 깨우기
hermes kanban daemon --interval 60        # 데몬

# 인간 개입
hermes kanban comment <task_id> "..."
hermes kanban unblock <task_id>
hermes kanban reclaim <task_id>
hermes kanban reassign <task_id> <profile>

# 정리
hermes kanban archive <task_id>
hermes kanban gc
```

### 페이지 디자인 프롬프트
```
Single large monospace terminal block organized by section comments.
Section headers in cyan (보드/태스크/실행/인간 개입/정리).
Commands in white. Flags in amber.
Title at top in white: "Appendix A4 — CLI Cheatsheet".
Dark navy background, terminal style.
```

---

## 사용 가이드

1. **PPT 임포트**: 각 슬라이드 섹션의 "슬라이드 내용"을 PPT 페이지에 그대로 옮긴다.
2. **디자인 적용**: "페이지 디자인 프롬프트"는
   - 디자이너에게 전달, 또는
   - Midjourney/DALL-E/Figma AI 등 이미지 생성 도구에 그대로 입력
3. **본 문서의 발표자 노트 + narrative는 `docs/ppt_narrative_v_1_0.md` 참조**

— 끝 —

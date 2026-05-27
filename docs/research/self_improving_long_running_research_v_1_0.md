# 24시간 자기 발전형 장기 자율 워크플로우 — 외부 사례 리서치

> 문서 버전: v1.0 · 작성일: 2026-05-27 · 범위: Cycle 2+ 자가발전 architecture 설계 evidence

본 문서는 Hermes Multi-Agent Kanban Board 기반 self-improving long-running autonomous architecture 설계를 위해 2022~2026년에 걸쳐 공개된 대표 프로젝트·논문·커뮤니티 실패 사례를 정리한 것이다. **외부 evidence**(인용·URL 포함)와 **내부 의견**(우리 architecture와의 비교)을 명확히 구분했다.

---

## 1. 대표 self-improving long-running 프로젝트 5선

| 프로젝트 | Self-improvement 메커니즘 | Long-running 안정성 | 인간 개입 지점 | Evidence |
|---|---|---|---|---|
| **Voyager** (NVIDIA/MineDojo, NeurIPS 2023) | (a) automatic curriculum, (b) **executable code skill library** (벡터 검색으로 재사용), (c) iterative prompting + self-verification critic | Minecraft에서 수십 시간 무인 운영 보고. catastrophic forgetting을 skill library로 완화 | 없음(open-ended exploration). 단 reward signal은 inventory 변화 등 환경 신호 | [arXiv 2305.16291](https://arxiv.org/abs/2305.16291), [voyager.minedojo.org](https://voyager.minedojo.org/) |
| **AutoGPT / BabyAGI** (커뮤니티 OSS, 2023) | "더 좋은 결과"를 LLM이 스스로 판단 → 재계획. **별도 학습 루프 없음** | **매우 불안정**. Amazon 연구에서 쇼핑 task 24% 성공률. infinite verification loop, runaway API bill 다발 | 없음(이게 문제). 사용자가 Ctrl+C로 중단 | [Vectara awesome-agent-failures](https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/autogpt-planning-failures.md) |
| **Devin / Devin 2.0** (Cognition, 2024-25) | DAG plan + dynamic re-planning, sandboxed VM에서 hundreds of decisions/hour. Multi-Devin 병렬 | SWE-Bench Verified 45.8%. 시간 단위 세션 유지. 그러나 **multi-agent 병렬은 의도적으로 회피** ("Don't Build Multi-Agents") | Slack/PR로 사용자에게 hand-off, checkpoint마다 사용자 직접 review | [Cognition Devin 2 blog](https://cognition.ai/blog/devin-2), [Don't Build Multi-Agents (HN)](https://news.ycombinator.com/item?id=45096962) |
| **Replit Agent 3** (Replit, 2025) | Manager / Editor / **Verifier** 3-role multi-agent. Verifier가 자기 출력 monitor | "Max Autonomy" mode에서 **최대 200분 무인 운영**. checkpoint 자동 commit으로 시간 되돌리기 가능 | Verifier가 모호하면 user에게 fallback. 모든 step에 git checkpoint | [InfoQ](https://www.infoq.com/news/2025/09/replit-agent-3/) |
| **Anthropic Multi-Agent Research System** (2025) | Lead(Opus) → 병렬 sub-agent(Sonnet/Haiku) **orchestrator-worker**. Lead가 plan을 memory에 저장 후 위임 | Opus 단독 대비 **+90.2%** 성능. token usage가 분산의 80% 설명 | 결과 합성은 lead가, 결정 권한은 사용자가 | [Anthropic engineering blog](https://www.anthropic.com/engineering/multi-agent-research-system) |

추가 언급: **Generative Agents (Stanford Smallville, 25명 NPC, 며칠 무인 운영)** — memory stream + reflection + planning 3계층 구조는 우리의 audit→synth 사이클과 닮은 점이 있다. [arXiv 2304.03442](https://arxiv.org/abs/2304.03442)

---

## 2. 핵심 이론/논문 8선

1. **Reflexion** (Shinn et al., 2023) — verbal RL. 실패 후 자기 비판을 episodic memory에 저장 → 다음 trial에서 reuse. [arXiv 2303.11366](https://arxiv.org/abs/2303.11366)
2. **Self-Refine** (Madaan et al., 2023) — 동일 모델이 generator/critic/refiner 1인 3역. single-trial 한정 약점. [arXiv 2303.17651](https://arxiv.org/abs/2303.17651)
3. **STaR: Self-Taught Reasoner** (Zelikman et al., 2022, NeurIPS) — 정답이 맞은 rationale만 finetune 데이터로 bootstrap → 추론 능력 자기 증식. [arXiv 2203.14465](https://arxiv.org/abs/2203.14465)
4. **Voyager skill library** — 검증 통과한 코드만 library에 add, semantic search로 retrieve. **자기 검증된 산출물만 누적**이 핵심. [arXiv 2305.16291](https://arxiv.org/abs/2305.16291)
5. **Constitutional AI / RLAIF** (Bai et al., Anthropic 2022) — 명문화된 원칙 기반으로 모델이 자기 출력을 비판·수정. 인간 라벨 없이 alignment를 scale. [arXiv 2212.08073](https://arxiv.org/abs/2212.08073)
6. **Chain-of-Verification (CoVe)** (Dhuliawala et al., 2023) — draft → verification plan → execute verify → synthesize 4단계로 hallucination 감소. 우리 cycle의 eval→review 단계와 직접 호환. [OpenReview](https://openreview.net/forum?id=VP20ZB6DHL)
7. **Self-Discover** (Zhou et al., 2024) — task별로 atomic reasoning module(critical thinking/step-by-step 등)을 **모델이 직접 합성**. BigBench-Hard +32%. [arXiv 2402.03620](https://arxiv.org/pdf/2402.03620)
8. **Evaluating Goal Drift in LM Agents** (2025) — drift 심각도가 "instrumental goal pursuit 기간" + "adversarial pressure"와 강하게 상관. 우리에게 직접적 시사점. [arXiv 2505.02709](https://arxiv.org/abs/2505.02709)

---

## 3. Anti-pattern 5선 (커뮤니티 보고)

1. **Infinite verification / perfectionism loop** — AutoGPT 사례에서 "task 완료 → 검증 → 검증이 충분치 않다고 판단 → 재검증 무한 반복", 한 사용자가 300+ API call에도 요약 결과물 0개로 수동 중단. [awesome-agent-failures](https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/autogpt-planning-failures.md)
2. **Context pollution / "Lost in the Middle"** — 1M~2M token window여도 **100k 이후 성능 50%+ 급락**. trial-and-error 로그가 모델 주의를 흩뜨림.
3. **Goal drift in long horizons** — "에이전트가 50k token 근처부터 원래 목표를 잊기 시작한다" (HN 토론). 장기 reward에 가까워지면 sub-goal로 표류. [HN 45096962](https://news.ycombinator.com/item?id=45096962)
4. **Cost runaway / silent 10x** — "agent가 reasoning loop에 걸려 $800 burn될 때까지 아무도 못 알아챘다." Show HN에는 AgentFuse, FailWatch, Runtime Fence 등 **킬 스위치 OSS만 4종 이상** 등장. [sanj.dev: AI Agents Don't Crash, They Spend](https://sanj.dev/post/llm-cost-control)
5. **Naive multi-agent context isolation** — Cognition "Flappy Bird" 일화: sub-agent A는 Mario 배경, sub-agent B는 비-게임 자산 새를 만듦. **sub-agent 간 implicit decision conflict**. [Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)

부가: VS Code Copilot Chat이 같은 파일을 20초간 2080회 재편집한 [issue #257885](https://github.com/microsoft/vscode/issues/257885), SWE-agent #971, Mistral Vibe #83 등 **production-grade 도구에서도 동일 패턴이 재발**.

---

## 4. 운영 패턴 5종 (real production)

1. **Hard cap stack** — per-request token ceiling, per-session budget, per-key monthly cap, model-tier routing, **cost-velocity circuit breaker** 5계층. soft warning은 이미 호출이 나간 뒤라 무력.
2. **Checkpoint as collaboration surface** — Replit이 모든 step마다 git commit. 사용자는 "시간을 거슬러" 임의 시점으로 롤백. HITL의 본질은 **pause-able state**.
3. **Tests-as-acceptance-criteria** — Ralph Wiggum 패턴: while true에 명시적 pass/fail test가 있을 때만 stop. **LLM 자체 판단의 "완료"는 신뢰하지 않음**. progress는 context window가 아니라 **파일과 git history에 산다**. [ghuntley.com/ralph](https://ghuntley.com/ralph/)
4. **Rich escalation context** — escalation 시 "무엇을 시도했고/왜 불확실하고/어떤 옵션이 있는지"를 패키지로. recurring escalation을 logging해서 agent 개선 데이터로 재투입.
5. **Orchestrator-worker with full context propagation** — Anthropic은 병렬을 쓰되 lead가 **전체 trace를 sub-agent에 propagate**. Cognition은 정반대(병렬 자체 회피)지만 두 진영 모두 "isolated message만 넘기면 망한다"에 동의.

24시간 무인 운영 사례는 사실상 **두 패턴만 안정적으로 보고**됨:
- (i) Voyager·Generative Agents같은 **환경이 reward를 주는 simulated world**
- (ii) Ralph 루프 같은 **명시적 pass/fail test가 oracle 역할을 하는 작업**

일반 open-domain "더 좋게 만들어"는 24시간 운영하면 거의 모두 위 anti-pattern에 빠진다.

---

## 5. 우리 Hermes architecture 비교 및 권고 (내부 의견)

### 이미 잘 갖춰진 부분
- 7-stage sub-task chain (audit→split→…→synth)은 CoVe의 draft/plan/verify/synthesize와 isomorphic. **외부 SOTA와 정합**.
- 4종 terminal condition + Layer 1-4 게이팅은 AutoGPT가 결여한 "good enough" 기준을 명문화. 큰 강점.
- DECIDE-N task로 cycle마다 인간 게이트를 강제 → Replit 철학과 일치.

### 차용 권고 패턴 5개

1. **Voyager-style verified skill library**: cycle synth 산출물 중 **acceptance_pass된 것만** semantic-indexable repository에 add. 다음 cycle의 split 단계에서 retrieve. *Catastrophic forgetting 방지 + 가속화.*
2. **Cost-velocity circuit breaker** (Layer 0 추가 권고): per-cycle token cap뿐 아니라 **token/min 가속도**가 임계 초과 시 자동 pause → DECIDE-N 강제 트리거.
3. **Full-trace context propagation between siblings** (Anthropic 패턴): parent done → child auto-promote 시 **부모의 전체 audit·eval trace를 child의 첫 컨텍스트로 강제 주입**. Cognition Flappy Bird 함정 회피.
4. **Goal anchor refresh**: cycle N의 첫 sub-task(audit)마다 "원본 milestone goal" 텍스트를 verbatim 재주입. goal drift 논문이 권고하는 가장 단순하고 효과적인 방어.
5. **DECIDE timeout default를 "Continue"가 아니라 "Pause"로**: 외부 사례 일관된 교훈. silent 비용 사고는 거의 모두 default-continue에서 발생.

### 피해야 할 anti-pattern 5개
1. acceptance criteria를 LLM의 자기 판단에만 의존 (AutoGPT 함정) — 우리 eval task는 **객관 metric** 유지 필요.
2. sub-agent에 isolated message만 전달 (Cognition 함정).
3. context window 의존 progress 추적 — **artifact(파일/DB)로 외재화**.
4. max_consecutive_failures만으로 loop 방어 — **identical-action detection**도 필요.
5. soft warning만으로 비용 제어 — hard cap이 없으면 통제 불능.

### 현재 격차
- 우리 설계에는 명시적 **skill library / 학습 누적 메커니즘**이 없음 (cycle은 반복되지만 산출이 다음 cycle 행동을 가속하지 않음). 이게 "self-improving"의 정의와 가장 큰 갭.
- Layer 3-4 인간 게이트는 명확하나 **Layer 1-2 cost/velocity guardrail은 모호**. 24시간 운영하려면 여기가 가장 위험.
- Verifier가 generator와 같은 모델/프로필이면 self-refine 한계에 갇힘. **이질적 critic** 권장.

---

## 6. 참고 출처 (selected URLs)

**대표 프로젝트**
- Voyager: https://arxiv.org/abs/2305.16291 · https://voyager.minedojo.org/
- AutoGPT failure case study: https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/autogpt-planning-failures.md
- Cognition Devin 2: https://cognition.ai/blog/devin-2
- Cognition "Don't Build Multi-Agents" (HN): https://news.ycombinator.com/item?id=45096962
- Replit Agent 3: https://www.infoq.com/news/2025/09/replit-agent-3/
- Anthropic Multi-Agent Research: https://www.anthropic.com/engineering/multi-agent-research-system
- Generative Agents: https://arxiv.org/abs/2304.03442

**이론/논문**
- Reflexion: https://arxiv.org/abs/2303.11366
- Self-Refine: https://arxiv.org/abs/2303.17651
- STaR: https://arxiv.org/abs/2203.14465
- Constitutional AI: https://arxiv.org/abs/2212.08073
- CoVe: https://openreview.net/forum?id=VP20ZB6DHL
- Self-Discover: https://arxiv.org/pdf/2402.03620
- Evaluating Goal Drift: https://arxiv.org/abs/2505.02709

**운영/anti-pattern**
- Ralph Wiggum loop: https://ghuntley.com/ralph/
- "AI Agents Don't Crash, They Spend": https://sanj.dev/post/llm-cost-control
- VS Code Copilot infinite loop bug: https://github.com/microsoft/vscode/issues/257885

---

**요약 (1줄)**: Hermes 설계는 7-stage chain + 4종 terminal + Layer gating으로 외부 SOTA와 정합적이지만, 24시간 무인 운영을 노린다면 (a) Voyager-style verified skill library, (b) cost-velocity circuit breaker, (c) full-trace sub-agent propagation, (d) goal anchor 재주입, (e) DECIDE timeout default=Pause 5가지를 우선 보강할 것을 권고한다.

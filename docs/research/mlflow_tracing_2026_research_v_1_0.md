# MLflow Tracing 2026 현황 보고서 — Hermes Multi-Agent Kanban 적용 검토

> 문서 버전: v1.0 · 작성일: 2026-05-27 · 범위: MLflow Tracing 2026 최신 + 본 워크플로우 적용 검토
> Agent research 산출 (WebSearch + 공식 docs 기반)

본 문서는 Hermes Multi-Agent Kanban 기반 한국어 에세이 자동채점 워크플로우의 MLflow Tracing 도입 여부와 시점을 결정하기 위해 2026년 5월 시점의 외부 사례·공식 문서·도구 비교를 정리한 것이다. **외부 evidence**(URL)와 **내부 의견**(우리 setup 결론) 명확 구분.

---

## 1. 도입 버전 / 안정성

MLflow Tracing은 **2.14 (2024 중반)** 부터 도입됐고, **MLflow 3.0 (2025)** 에서 GenAI/Agent observability 전용 1급 시민으로 승격됨. 2026년 5월 기준 안정 버전은 **3.12.0** (귀하 환경과 일치). 최근 3.7~3.9 릴리스는 token tracking 자동 캡처, AI 어시스턴트, judge builder UI, **distributed tracing**, continuous monitoring with LLM judges를 추가. MLflow 3는 "20+ GenAI 라이브러리 자동 tracing"을 핵심 기능으로 마케팅 중이며 대규모 프로덕션 배포에 충분한 성숙도.

**SQL backend 필수 이유** — file store (`./mlruns`)는 backward compat으로만 유지되며, Model Registry, Workspaces, job execution, **그리고 Trace UI의 인덱스 검색/필터/dashboard가 사실상 동작 불가**. 프로덕션 운영 권고는 SQLite (소규모) → PostgreSQL/MySQL (스케일).

---

## 2. 지원 SDK

- **Python 자동 instrumentation (one-line autolog)**: OpenAI, Anthropic, LangChain, LangGraph, LlamaIndex, DSPy, Hugging Face, PydanticAI, smolagents, Mastra, Google Gemini, Bedrock + OpenAI-compatible 게이트웨이 전부.
- **TypeScript/Node.js SDK**: 3.6에서 추가, 현재 `@mlflow/core`, `@mlflow/openai`, `@mlflow/anthropic`, `@mlflow/gemini` 패키지 (v0.2.0). Vercel AI SDK, LangChain.js, LangGraph.js 자동 trace.
- **수동 instrumentation**: `@mlflow.trace` 데코레이터 + `mlflow.start_span` context manager. span name/type/attributes 커스터마이즈, 예외 자동 캡처, generator/iterator 지원 (2.20.2+).
- **OpenTelemetry 호환**: MLflow Tracing은 OTel GenAI Semantic Conventions를 native로 지원 — 즉 **non-Python 환경에서도 OTel exporter만 있으면 ingest 가능**. 다만 **Codex CLI (Rust binary, subprocess)** 자체는 trace를 emit 하지 않음. 우리 케이스에는 두 가지 전략이 가능: (a) Python wrapper에서 `@mlflow.trace` 데코레이터로 subprocess 호출을 감싸고 stdout에서 token usage를 파싱해 span attribute로 주입, (b) Codex가 사용하는 OpenAI/Anthropic API 호출 자체를 별도 Python 프로세스/sidecar에서 proxy/replay하는 것은 비현실적.

---

## 3. Trace 데이터 구조

- **Trace = TraceInfo (metadata) + TraceData (Span 트리)**
- 각 Span: input, output, latency, attributes, events, exceptions, parent-child 관계
- **자동 token usage / cost**: LangChain, LangGraph, OpenAI 등은 prompt/completion token + 비용까지 자동 집계
- Metadata: user_id, session_id, request_id, custom tags
- UI에서 trace 단위 search / filter / dashboard / replay 지원 (단, SQL backend 필수)

---

## 4. Production 패턴

- 기본 retention 무한 → `delete_traces(max_timestamp_millis=...)` 또는 `TraceArchivalConfig(location, retention="30d")`로 lifecycle 관리 필수
- **Lightweight Production Tracing SDK** (`mlflow-tracing` PyPI 패키지) — full MLflow 의존성 없이 trace만 emit, 저지연 OTel exporter 사용
- LLM Judge (`mlflow.genai.scorers`) + continuous monitoring으로 production 트래픽에 hallucination/PII/frustration 스코어 자동 부착

---

## 5. Hermes 워크플로우 적용 시나리오

| 시나리오 | 가능성 | 구현 비용 |
|---|---|---|
| **Codex CLI subprocess trace** | 부분 가능 — Python wrapper에서 `@mlflow.trace`로 감싸고 stdout 파싱해 token/latency를 span attribute 주입 | 중 (worker당 30-60줄) |
| **LLM Judge (rubric-aware 보조평가)** | 즉시 가능 — Judge Builder UI 또는 `@scorer` 데코레이터, 기존 rubric을 prompt로 변환 | 낮음 (Judge 정의 + 자동 평가 hook) |
| **Voyager-style skill retrieval (embedding 호출)** | 자동 — OpenAI embedding API autolog 적용, retrieval span + similarity score를 attribute로 | 매우 낮음 |
| **Worker reasoning chain** | Codex 내부 reasoning은 캡처 불가 (Codex가 trace emit 안 함). worker-level decision/action만 manual span으로 기록 가능 | 중 |
| **cost_circuit_breaker 연계** | 가능 — trace의 token/cost attribute를 polling해 임계치 초과 시 break. 단 file store에서는 query 성능 한계 → **SQLite 전환 필요** | 낮음 (SQLite 전환 후) |

**핵심 한계**: Codex CLI 자체가 black box subprocess라 내부 LLM 호출의 prompt/completion 원문을 MLflow trace로 직접 캡처 불가. 워커 입출력 경계에서의 "outer span"만 기록 가능. Voyager skill library / LLM Judge 도입 시는 Python 영역이므로 풍부한 trace 확보 가능.

---

## 6. 대안 비교

| 도구 | 강점 | 약점 | Hermes 적합도 |
|---|---|---|---|
| **MLflow Tracing** | 이미 MLflow 사용 중, self-host, 데이터 소유, evaluation/registry 통합 | file store에서 trace UI 제약, judge UI는 Databricks 편향 | ★★★★★ (current stack) |
| **LangSmith** | LangChain 통합 최강, 셋업 5분 | self-host 불가, $39/user/월부터, vendor lock-in | ★★ (LangChain 안 쓰면 무가치) |
| **Arize Phoenix** | OSS, 50+ 평가 metric, trace 품질 우수 | self-host 운영부담, MLflow와 중복 | ★★★ (MLflow 대체 시) |
| **Helicone** | gateway + 캐싱, 2분 셋업, cost tracking 즉시 | trace 깊이 낮음, replay/chain 시각화 없음 | ★★ (cost만 필요할 때) |
| **Langfuse** | OSS, balanced, prompt management 우수 | 별도 stack 추가 부담 | ★★★ |

**결론**: 이미 MLflow 3.12 사용 중이고 sklearn/lightgbm metric도 같은 곳에 모이는데 굳이 trace만 별도 도구로 분리할 이유 없음. **MLflow Tracing 유지가 최적**.

---

## 7. 도입 권고 시점 + 결론

| 단계 | 권고 |
|---|---|
| **현재 (Cycle 1/2, sklearn/lightgbm only)** | **도입 무가치**. LLM 호출 자체가 없어 trace할 대상이 없음. file store 유지해도 무방. |
| **LLM Judge 도입 시점** | **즉시 도입**. 가장 ROI 높은 진입점. Judge 호출이 자동 trace되고 rubric score가 평가 result에 부착됨. 이때 **SQLite backend 전환 필수** (Trace UI/dashboard/judge builder 사용 위해). |
| **Voyager-style skill library 도입 시** | embedding/retrieval trace로 skill hit rate, retrieval latency 측정 가능. 동시 도입 권장. |
| **Codex worker LLM trace가 critical할 때** | Python wrapper로 outer span만 + stdout 파싱해 token usage 주입. 완벽한 inner trace는 Codex가 OTel exporter를 native 지원하지 않는 한 불가. 대안: Codex 대신 직접 Anthropic/OpenAI SDK 호출하는 worker profile 추가 시 자동 instrumentation 100% 활용. |
| **cost_circuit_breaker 통합** | SQLite 전환 후 `mlflow.search_traces(filter_string="attributes.usage.total_tokens > X")`로 polling. 또는 trace 생성 hook에서 직접 누계 카운터 업데이트. |

**최종 권고**:
1. **지금은 도입 보류**, 그러나 SQLite 전환을 다음 인프라 작업에 포함 (file store는 trace 시대에 막다른 길).
2. **LLM Judge가 첫 진입 trigger** — Judge가 들어오는 순간 trace가 의미를 가지므로 그때 한 번에 SQLite 전환 + autolog 활성화 + Judge 정의.
3. 도입 시 Hermes worker는 `mlflow.openai.autolog()` 또는 wrapper의 `@mlflow.trace` 정도로 충분. Codex CLI는 outer-span only로 시작하고, full inner trace가 필요해지면 worker를 Python SDK 기반으로 전환 검토.
4. cost 추적은 trace의 자동 token attribute + `cost_circuit_breaker`에서 SQL query 방식이 가장 깔끔 (별도 Helicone 도입 불필요).

---

## 8. 본 워크플로우 추가 결정 사항

- **SQLite 전환 시점**: DECIDE-N에서 `[Phase-up]` 선택 시 또는 DECIDE-N의 SYNTH done 직후 idle 구간
- **Worker tracking URI 변경 절차**: 환경변수 `MLFLOW_TRACKING_URI=sqlite:///mlflow.db` 또는 AGENTS.md "When Modeling" 섹션에 명시
- **기존 80+ runs 보존**: `mlruns_legacy/` 디렉터리로 이동 후 신규 SQLite 시작 (또는 별도 마이그레이션 도구 사용)
- **LLM Judge 도입 후보 task**: Cycle 4+ 에서 spearman EVAL 단계에 통합 또는 별도 LLM Judge Designer profile 추가

---

## 9. 참고 출처

**공식 문서**
- [LLM Tracing and Agent Observability | MLflow](https://mlflow.org/docs/latest/genai/tracing/)
- [MLflow 3.0 Blog (Databricks)](https://www.databricks.com/blog/mlflow-30-unified-ai-experimentation-observability-and-governance)
- [MLflow Releases](https://mlflow.github.io/mlflow-website/releases/)
- [MLflow Tracing Integrations](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/)
- [Tracing Anthropic | MLflow](https://mlflow.org/docs/3.0.0rc2/tracing/integrations/anthropic)
- [Tracing LangChain | MLflow](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/langchain/)
- [Manual Tracing - Decorators & Context Managers](https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/manual-tracing/fluent-apis)
- [OpenTelemetry Integration | MLflow](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/)
- [Lightweight Production Tracing SDK](https://mlflow.org/docs/latest/genai/tracing/lightweight-sdk/)
- [Backend Stores | MLflow](https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/)
- [Issue #2857 - File-based backend limitations](https://github.com/mlflow/mlflow/issues/2857)
- [Production Tracing and Monitoring](https://mlflow.org/docs/latest/genai/tracing/prod-tracing/)
- [Tracing FAQ - retention/deletion](https://mlflow.org/docs/latest/genai/tracing/faq/)
- [LLM-as-a-Judge | MLflow](https://mlflow.org/llm-as-a-judge)
- [Automatic Evaluation | MLflow](https://mlflow.org/docs/latest/genai/eval-monitor/automatic-evaluations/)
- [MLflow Meets TypeScript](https://mlflow.org/blog/mlflow-typescript)
- [TypeScript SDK | MLflow](https://www.mlflow.org/docs/latest/genai/tracing/app-instrumentation/typescript-sdk/)

**도구 비교**
- [Top 5 LLM and Agent Observability Tools in 2026 | MLflow](https://mlflow.org/top-5-agent-observability-tools/)
- [Best LLM Observability Tools in 2026 - Firecrawl](https://www.firecrawl.dev/blog/best-llm-observability-tools)
- [Best LLM tracing tools for multi-agent systems 2026 - Braintrust](https://www.braintrust.dev/articles/best-llm-tracing-tools-2026)

---

## 10. 요약 (한 줄)

> 지금 도입 무가치, LLM Judge 도입 시점이 trigger, 그때 SQLite + autolog 한 번에. 별도 도구 도입 X — MLflow Tracing 유지.

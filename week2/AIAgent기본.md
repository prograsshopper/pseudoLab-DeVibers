# AI Agent
- 목표를 달성하기 위해 스스로 판단하고 행동하는 시스템
- LLM이라는 두뇌가 도구(Tools)와 메모리(Memory)를 활용해 목표(Goal)를 달성할 때까지 스스로 루프(Loop)를 도는 시스템

# AI Agent 핵심 요소
__1. Brain (LLM & Reasoning)__
- 역할: 상황 파악, 계획 수립, 의사 결정.

__2. Planning & Loop (The Strategy)__
- 역할: 목표(Goal)를 잘게 쪼개고, 실행 결과(Observation)를 보고 다음 행동을 수정하는 반복 과정.

__3. Memory (Context & State)__
- 역할: 이전 단계에서 무엇을 했는지, 사용자 취향은 무엇인지 기억하는 저장소.

__4. Tools / Action (The Hands & Feet)__
- 역할: 외부 세계와 상호작용 (웹 검색, API 호출, DB 조회, 코드 실행).


# AI Agent 디자인 패턴
## 1. 핵심 디자인 패턴 요약

| 패턴명 | 작동 방식 (Workflow) | 주요 특징 | 적합한 상황 |
| :--- | :--- | :--- | :--- |
| **ReAct** | `Thought` → `Action` → `Observation` 반복 | 생각과 행동을 결합한 가장 표준적인 루프 | 일반적인 문제 해결, 단계적 추론 필요 시 |
| **Plan & Execute** | `Plan` 생성 → `Steps` 순차 실행 → `Re-plan` | 전체 경로를 먼저 그린 후 실행 | 목표가 명확하고 긴 호흡의 작업 |
| **Reflection** | `Draft` → `Critique` → `Revise` | 결과물을 스스로 검토하고 수정 | 코드 생성, 글쓰기 등 고품질 결과물 필요 시 |
| **Multi-Agent** | 역할 분담 (Planner, Coder, Reviewer 등) | 에이전트 간 협업 및 조율(Orchestration) | 복잡한 도메인 분리, 대규모 프로젝트 |
| **Tool-Use** | `LLM` ↔ `External Tools (API/DB/Code)` | 외부 환경과의 상호작용에 집중 | 실계 시스템 연동, 데이터 조작 |

---

## 2. 패턴별 상세 분석

### 🔹 1. ReAct (Reasoning + Acting)
가장 기본이 되는 패턴으로, LLM이 '왜 이 행동을 하는지' 기록하며 진행합니다.
* **장점:** 중간 과정이 투명하여 디버깅이 쉽고, 예상치 못한 도구 결과에 유연하게 대응합니다.
* **단점:** 루프가 길어질수록 컨텍스트 비용이 증가하며, 가끔 무한 루프에 빠질 위험이 있습니다.

### 🔹 2. Plan & Execute
문제를 하위 작업(Sub-tasks)으로 쪼개고 순차적으로 처리합니다.
* **장점:** 전체 맥락을 유지하며 일관성 있게 작업합니다.
* **단점:** 초기 계획이 잘못되면 이후 모든 단계가 틀어질 수 있습니다. (최근에는 실행 중 계획을 수정하는 *Adaptive Plan* 방식이 선호됨)

### 🔹 3. Reflection (Self-Correction)
생성(Actor)과 비판(Critic) 역할을 나누어 품질을 높이는 패턴입니다.
* **Workflow:** `초안 작성` → `자가 피드백` → `수정본 작성` → `최종 검수`
* **핵심:** 단순히 "다시 해봐"가 아니라, 구체적인 체크리스트(Linter 결과, 유닛 테스트 통과 여부 등)를 피드백으로 주는 것이 중요합니다.

### 🔹 4. Multi-Agent Systems (MAS)
하나의 거대한 프롬프트 대신, 전문화된 작은 에이전트들을 활용합니다.
* **구조:** * **Hierarchical (계층형):** 관리자 에이전트가 하위 에이전트에게 일을 시킴.
    * **Joint (협업형):** 공유된 워크스페이스(Shared Memory)에서 자유롭게 소통.
* **장점:** 관심사 분리(SoC)가 명확해져서 유지보수가 용이합니다.

---

## 3. 💡 실무자를 위한 추가 정리 (Architecture Insight)

에이전트 패턴을 실제 서비스에 이식할 때 놓치기 쉬운 **Backend 관점**의 요소입니다.

### 🏗️ 에이전트의 4대 구성 요소
1.  **Memory (상태 관리):**
    * **Short-term:** 현재 세션의 대화 기록 (Chat History).
    * **Long-term:** 과거 사용자 선호도나 지식을 벡터 DB(RAG)에 저장.
2.  **Planning (전략):**
    * Chain of Thought(CoT), Step-back Prompting 등을 통해 추론 능력 극대화.
3.  **Tools (역량):**
    * 에이전트가 실행 가능한 Python 함수, API 명세서, DB 스키마 등.
4.  **Guardrails (통제):**
    * 출력 형식 강제 (JSON/Pydantic), 실행 시간 제한(Timeout), 비용 제한(Max Loops).

### 🛠️ 구현 시 고려할 점
* **State Management:** 에이전트의 루프 상태를 어디에 저장할 것인가? (Redis, Postgres 등) 특히 멀티 에이전트 환경에서는 상태 동기화가 핵심입니다.
* **Error Handling:** 도구 호출 실패나 LLM의 잘못된 형식 응답 시 `Retry` 로직 및 `Fallback` 전략이 필수적입니다.
* **Streaming:** 에이전트의 `Thought` 과정을 사용자에게 실시간으로 보여줄지 여부에 따라 UX 체감이 크게 달라집니다.

---

## 4. 패턴 선택 가이드라인



| 우선순위 | 권장 패턴 | 이유 |
| :--- | :--- | :--- |
| **빠른 개발** | **Tool-use (Function Calling)** | 대부분의 프레임워크(LangChain, LangGraph)에서 기본 지원함. |
| **안정성/정확도** | **Reflection + RAG** | 검증 단계를 추가하여 할루시네이션(환각) 최소화. |
| **복잡한 비즈니스 로직** | **Multi-Agent** | 로직을 모듈화하여 개별 에이전트 단위로 테스트 가능. |

---

# Open Code 디자인 패턴 분석

## AI Agent 핵심 디자인 패턴

### 패턴 간 관계 요약

```
ReAct Loop (while true)
  └── 매 스텝마다 Tool Use
        ├── BashTool     → Human-in-the-Loop (permission ask)
        ├── TaskTool     → Multi-Agent (새 ReAct 루프 재귀 생성)
        └── (any tool)   → Structured Output (JSON schema 강제)
  └── 토큰 초과 감지   → Context Compaction → 루프 재개
  └── Doom Loop 감지  → Human-in-the-Loop 강제 개입
  └── 모든 툴 호출    → Plugin Hook (before/after)
```

---

### 1. ReAct (Reasoning + Acting)

**파일**: `session/prompt.ts:1337`

`while(true)` 루프가 본체. LLM이 텍스트(Reasoning)와 툴 호출(Acting)을 반복하다가 `finish` reason이 `tool-calls`가 아닐 때 스스로 루프를 탈출한다.

```
LLM 호출 → 텍스트 생성(Reasoning) + 툴 호출(Acting)
         → 툴 결과를 컨텍스트에 추가
         → 반복
         → finish != "tool-calls" → 루프 종료
```

---

### 2. Tool Use / Function Calling

**파일**: `session/processor.ts:170`

Vercel AI SDK 스트리밍 이벤트를 타입으로 분기 처리:

```
tool-input-start → tool-call → tool-result
                            └→ tool-error
```

툴 실행 결과는 자동으로 다음 LLM 호출의 컨텍스트에 포함된다.

---

### 3. Multi-Agent Orchestration

두 가지 방식이 공존한다.

**방식 A — Task Tool** (`tool/task.ts`)
LLM이 직접 `task` 툴을 호출 → 새 자식 Session 생성 → `loop()` 재귀 호출. 완전한 Agent 루프가 중첩 실행된다.

**방식 B — Subtask Part** (`session/prompt.ts:1379`)
메시지에 `subtask` 파트가 있으면 루프가 `handleSubtask()`로 분기. 선언적·구조화된 방식으로 서브에이전트를 실행한다.

---

### 4. Context Window Management (Compaction)

**파일**: `session/compaction.ts`

컨텍스트가 넘치면 세 가지 전략을 순서대로 적용:

| 전략 | 설명 |
|------|------|
| **Compaction** | `compaction` 에이전트가 전체 대화를 LLM으로 요약 → 요약본으로 대체 후 루프 재개 |
| **Prune** | 오래된 tool 결과의 output만 지워서 토큰 절약 (메시지 구조는 유지) |
| **Overflow replay** | 컨텍스트 초과 시 직전 사용자 메시지를 새 컨텍스트에 replay |

루프 내에서 `compact` 시그널이 오면 자동 실행 후 루프가 재개된다. Compaction은 단순 truncation이 아니라 **별도 LLM 호출로 요약을 생성**하고 그 결과가 다시 루프로 돌아오는 구조다.

---

### 5. Human-in-the-Loop (Permission / Approval)

**파일**: `permission/index.ts`

툴 실행 전 `ask(permission)` 호출. 가능한 응답:

| 응답 | 동작 |
|------|------|
| `allow` | 한 번만 허용 |
| `allow-all` | 이 패턴 항상 허용 (룰셋에 저장) |
| `deny` | 거절 → `Permission.RejectedError` → loop stop |

**Doom Loop 감지**: 같은 툴·같은 입력이 3번 연속 실행되면 자동으로 `permission.ask()` 발동 (`session/processor.ts:184`)

---

### 6. Structured Output

**파일**: `session/prompt.ts:1454`

JSON 응답이 필요할 때 `StructuredOutput` 툴을 동적으로 주입한다. LLM이 이 툴을 반드시 마지막에 호출하도록 시스템 프롬프트로 강제하여 스키마 검증된 JSON을 보장한다.

---

### 7. Prompt Caching

**파일**: `provider/transform.ts:192`

Anthropic/Bedrock 모델에 대해 system prompt 앞 2개 + 대화 마지막 2개 메시지에 `cache_control: ephemeral` 자동 삽입. ReAct 루프의 반복 호출에서 캐시 히트율을 극대화한다.

---

### 8. Plugin Hook System

**파일**: `plugin/index.ts`

모든 주요 실행 지점에 훅이 있어 외부 플러그인이 동작을 끼어들 수 있다:

| 훅 | 시점 |
|----|------|
| `tool.execute.before` / `after` | 툴 실행 전후 |
| `chat.message` | 메시지 저장 전 |
| `shell.env` | 쉘 실행 환경변수 주입 |
| `experimental.text.complete` | LLM 텍스트 후처리 |

---
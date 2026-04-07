# OpenCode 레포지토리 분석

## 분석 진행 상황

| 단계 | 내용 | 상태 |
|------|------|------|
| 1단계 | 진입점 (index.ts, run.ts) | ✅ 완료 |
| 2단계 | Agent 루프 (prompt.ts, processor.ts, llm.ts) | ✅ 완료 |
| 3단계 | Tool 시스템 (tool.ts, bash.ts, edit.ts, task.ts, registry.ts) | ✅ 완료 |
| 4단계 | Provider (provider.ts, transform.ts) | ✅ 완료 |
| 5단계 | Server (server.ts, routes/) | ✅ 완료 |
| 6단계 | 저장소 & 설정 (storage/, config/) | ✅ 완료 |
| 7단계 | 확장 시스템 (mcp/, lsp/, plugin/) | ✅ 완료 |

---

## 한 줄 요약

오픈소스 AI 코딩 에이전트 (Claude Code와 유사). TypeScript 모노레포.

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| 런타임 | Bun + TypeScript |
| AI 추상화 | Vercel AI SDK (Claude/OpenAI/Google 등 20+ 프로바이더) |
| 함수형 패턴 | Effect (4.0 beta) - 에러 처리, 비동기 전반 |
| 서버 | Hono (경량 웹 프레임워크) |
| 로컬 DB | SQLite + Drizzle ORM |
| 빌드 | Turbo 모노레포 |
| 데스크톱 | Tauri v2 |
| 프론트엔드 | SolidJS + TailwindCSS |


---
## 전체 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                   사용자 인터페이스                     │
│   TUI (CLI)  │  Web (SolidJS)  │  Desktop (Tauri)   │
└─────────────────────┬───────────────────────────────┘
                      │
               ┌──────▼──────┐
               │ Server (Hono)│
               └──────┬──────┘
          ┌───────────┼───────────┐
     ┌────▼────┐  ┌───▼────┐  ┌──▼──────┐
     │  Agent  │  │ Tools  │  │Provider │
     │(AI Loop)│  │bash/   │  │Claude/  │
     └─────────┘  │read/   │  │OpenAI   │
                  │edit... │  └─────────┘
                  └────────┘
```

---


## 패키지별 기능

| 패키지 | 역할 |
|--------|------|
| `packages/opencode` | **핵심 CLI** - Agent, Tools, Server, Provider 전부 여기 |
| `packages/app` | 웹 UI (SolidJS) |
| `packages/desktop` | 데스크톱 앱 (Tauri) |
| `packages/sdk/js` | 클라이언트/서버 SDK |
| `packages/ui` | 공유 UI 컴포넌트 |
| `packages/console/*` | 관리 콘솔 + 백엔드 (Stripe, DB) |
| `packages/plugin` | 플러그인 시스템 API |


---

## 핵심 흐름 분석 순서

### 1단계 - 진입점과 전체 흐름
```
packages/opencode/src/index.ts         # CLI 엔트리포인트
packages/opencode/src/cli/cmd/run.ts   # 메인 실행 커맨드
```

### 2단계 - Agent 루프 (핵심)
```
packages/opencode/src/agent/agent.ts         # Agent 레지스트리 (build/plan/general/explore 등 정의)
packages/opencode/src/session/prompt.ts      # ReAct Loop 구현체 (loop() 메서드)
packages/opencode/src/session/processor.ts   # LLM 스트림 이벤트 처리기
packages/opencode/src/session/llm.ts         # Vercel AI SDK 호출 레이어
```

### 3단계 - Tools (Agent의 손발)
```
packages/opencode/src/tool/tool.ts     # Tool 인터페이스 정의
packages/opencode/src/tool/           # bash, read, edit, write, glob, grep 등
```

### 4단계 - Provider (AI 두뇌 연결)
```
packages/opencode/src/provider/provider.ts  # Claude, OpenAI 등 추상화
```

### 5단계 - Server (통신 레이어)
```
packages/opencode/src/server/server.ts
packages/opencode/src/server/routes/
```

### 6단계 - 저장소 & 설정
```
packages/opencode/src/storage/         # SQLite (Drizzle ORM)
packages/opencode/src/config/          # 설정 관리
```

### 7단계 - 확장 시스템 (선택)
```
packages/opencode/src/mcp/             # Model Context Protocol
packages/opencode/src/lsp/             # Language Server Protocol
packages/opencode/src/plugin/          # 플러그인
```

---

## 실제 코드 흐름 (추적 완료)

### 전체 흐름 다이어그램

```
[사용자] opencode run "메시지"
    │
    ▼
[index.ts] yargs CLI 파서
    │  - 전역 옵션 처리 (log-level, pure 등)
    │  - 최초 실행시 SQLite DB 마이그레이션
    ▼
[cli/cmd/run.ts] RunCommand.handler()
    │  - 메시지/파일 파싱
    │  - 로컬 Server 시작 또는 원격 attach
    │  - sdk.session.create() → sessionID 획득
    │  - sdk.event.subscribe() → 이벤트 루프 시작
    │  - sdk.session.prompt() → 메시지 전송
    ▼
[session/prompt.ts] SessionPrompt.prompt()
    │  - Agent 선택 (build/plan/...)
    │  - Model 선택 (Claude/GPT 등)
    │  - Tool 레지스트리 로드
    │  - System Prompt 구성
    │  - SessionProcessor.create() 호출
    ▼
[session/prompt.ts] loop() ← ReAct 루프
    │  ┌─────────────────────────────┐
    │  │ processor.process() 호출    │
    │  │   → LLM.stream() 호출       │
    │  │   → 스트림 이벤트 처리       │
    │  │     - tool-call: 툴 실행    │
    │  │     - text-delta: 텍스트    │
    │  │     - finish-step: 완료     │
    │  │   → "continue"/"stop"/"compact" 반환
    │  │                             │
    │  │ result === "continue" → 반복 │
    │  │ result === "stop"    → 종료  │
    │  │ result === "compact" → 압축후 반복
    │  └─────────────────────────────┘
    ▼
[session/llm.ts] LLM.stream()
    │  - Vercel AI SDK streamText() 호출
    │  - 시스템 프롬프트 + 메시지 + 툴 전달
    │  - Provider별 옵션 처리
    ▼
[Vercel AI SDK] → Claude / OpenAI / Google API
```

### 핵심 파일별 역할 요약

| 파일 | 역할 | 핵심 패턴 |
|------|------|----------|
| `index.ts` | CLI 진입, 커맨드 등록 | yargs |
| `cli/cmd/run.ts` | run 커맨드, 이벤트 루프 | SDK 클라이언트, SSE 스트림 |
| `agent/agent.ts` | Agent 정의 레지스트리 | Effect Service |
| `session/prompt.ts` | **ReAct 루프** | loop() → continue/stop |
| `session/processor.ts` | 스트림 이벤트 처리 | switch(event.type) |
| `session/llm.ts` | LLM API 호출 | Vercel AI SDK streamText |
| `tool/tool.ts` | Tool 인터페이스 | execute(args, ctx) |

### 내장 Agent 목록

| Agent | mode | 설명 |
|-------|------|------|
| `build` | primary | 기본 에이전트, 전체 권한 |
| `plan` | primary | 읽기 전용, 계획 작성만 |
| `general` | subagent | 복잡한 멀티스텝 작업 |
| `explore` | subagent | 빠른 코드베이스 탐색 |
| `compaction` | primary (hidden) | 컨텍스트 압축 |
| `title` | primary (hidden) | 세션 제목 생성 |
| `summary` | primary (hidden) | 세션 요약 |

---

## 기능별 핵심 파일 지도

> 경로 기준: `packages/opencode/src/`

### 🔁 Agent 루프 (ReAct 이해하려면 이것만)

| 우선순위 | 파일 | 이유 |
|---------|------|------|
| ★★★ | `session/prompt.ts` | **루프 본체** - `loop()`, `prompt()` |
| ★★★ | `session/processor.ts` | **이벤트 처리** - tool 실행/에러/텍스트 |
| ★★☆ | `session/llm.ts` | LLM API 호출 (Vercel AI SDK 래퍼) |
| ★☆☆ | `agent/agent.ts` | 에이전트 설정 레지스트리 |

### 🛠 Tool 시스템

| 우선순위 | 파일 | 이유 |
|---------|------|------|
| ★★★ | `tool/tool.ts` | **Tool 인터페이스 정의** - 모든 툴의 기반 |
| ★★★ | `tool/bash.ts` | 가장 복잡한 툴, 권한/PTY 처리 |
| ★★☆ | `tool/edit.ts` | 파일 편집, diff 생성 |
| ★★☆ | `tool/task.ts` | SubAgent 생성 (Multi-Agent 패턴) |
| ★☆☆ | `tool/registry.ts` | 툴 등록/조합 관리 |

### 🤖 Provider (AI 모델 연결)

| 우선순위 | 파일 | 이유 |
|---------|------|------|
| ★★★ | `provider/provider.ts` | **Provider 추상화** - 모델 선택/로드 |
| ★★☆ | `provider/transform.ts` | Provider별 파라미터 변환 |
| ★☆☆ | `provider/schema.ts` | 모델/Provider ID 타입 정의 |

### 🌐 Server & API

| 우선순위 | 파일 | 이유 |
|---------|------|------|
| ★★★ | `server/server.ts` | **서버 초기화** - 라우트 조합 |
| ★★☆ | `server/routes/` (디렉토리) | REST API 엔드포인트들 |

### 💾 저장소

| 우선순위 | 파일 | 이유 |
|---------|------|------|
| ★★★ | `storage/db.ts` | SQLite 연결, Drizzle 설정 |
| ★★☆ | `session/session.sql.ts` | 세션 테이블 스키마 |
| ★★☆ | `session/message-v2.ts` | 메시지 구조 정의 |

### 🔐 권한 시스템

| 우선순위 | 파일 | 이유 |
|---------|------|------|
| ★★★ | `permission/index.ts` | **권한 룰셋** - allow/deny/ask |

### 🔌 확장 시스템 (나중에 봐도 됨)

| 파일 | 이유 |
|------|------|
| `mcp/index.ts` | MCP 서버 연결 |
| `lsp/index.ts` | 언어 서버 연결 |
| `plugin/index.ts` | 플러그인 훅 |

---

## 최소 필수 독해 10개 (전체 흐름의 80%)

```
1.  session/prompt.ts       ← 루프 본체
2.  session/processor.ts    ← 이벤트 처리
3.  session/llm.ts          ← API 호출
4.  tool/tool.ts            ← 툴 인터페이스
5.  tool/bash.ts            ← 툴 구현 예시 (가장 복잡)
6.  tool/task.ts            ← Multi-Agent 진입점
7.  provider/provider.ts    ← 모델 추상화
8.  permission/index.ts     ← 권한 시스템
9.  server/server.ts        ← 서버 구조
10. session/message-v2.ts   ← 데이터 모델
```

---

## 3단계: Tool 시스템 분석

### Tool 인터페이스 구조 (`tool/tool.ts`)

```typescript
// 모든 툴이 따르는 인터페이스
Tool.Info = {
  id: string
  init(ctx?: InitContext) => Promise<Tool.Def>
}

Tool.Def = {
  description: string          // LLM에게 전달되는 툴 설명
  parameters: z.ZodType        // Zod 스키마로 입력 검증
  execute(args, ctx) => Promise<{ title, metadata, output }>
}

// execute에 주입되는 컨텍스트
Tool.Context = {
  sessionID, messageID, agent
  abort: AbortSignal           // 취소 신호
  ask(permission)              // 권한 요청 (allow/deny/ask)
  metadata(info)               // 실시간 UI 업데이트
}
```

**공통 처리**: 모든 툴의 output은 자동으로 truncate 처리 (툴이 직접 처리하지 않는 경우)

---

### 핵심 툴 상세 분석

#### 1. BashTool (`tool/bash.ts`) - 가장 복잡

```
명령어 입력
  → tree-sitter로 bash/powershell AST 파싱
  → 파일 경로 정적 분석 (rm, cp, mv 등 파일 조작 커맨드 감지)
  → 외부 디렉토리 접근 여부 확인 → 권한 요청(ask)
  → bash 권한 요청(ask)
  → child_process.spawn() 실행
  → stdout/stderr 실시간 스트리밍
  → timeout (기본 2분) 초과 시 프로세스 킬
  → abort 신호 수신 시 킬
```

- **tree-sitter**: bash + PowerShell 문법 파서로 커맨드 AST 분석
- **외부 디렉토리 감지**: 프로젝트 밖 경로 접근 시 별도 권한 요청
- **플랫폼 지원**: Unix/Windows/PowerShell 모두 처리

#### 2. EditTool (`tool/edit.ts`) - 9단계 폴백 매칭

`oldString`을 찾지 못하면 다음 순서로 폴백:

| 순서 | Replacer | 설명 |
|------|----------|------|
| 1 | SimpleReplacer | 완전 일치 |
| 2 | LineTrimmedReplacer | 각 줄 앞뒤 공백 무시 |
| 3 | BlockAnchorReplacer | 첫/마지막 줄 앵커 + Levenshtein 유사도 |
| 4 | WhitespaceNormalizedReplacer | 연속 공백 정규화 |
| 5 | IndentationFlexibleReplacer | 들여쓰기 무시 |
| 6 | EscapeNormalizedReplacer | 이스케이프 문자 정규화 |
| 7 | TrimmedBoundaryReplacer | 앞뒤 trim 후 매칭 |
| 8 | ContextAwareReplacer | 첫/마지막 줄 앵커 + 중간 50% 유사도 |
| 9 | MultiOccurrenceReplacer | 전체 치환 |

- 편집 후 **LSP 진단** 실행 → 에러 있으면 LLM에 반환
- **FileTime** 으로 동시 편집 충돌 감지

#### 3. TaskTool (`tool/task.ts`) - Multi-Agent 구현체

```
LLM이 task 툴 호출
  → 새 자식 Session 생성 (parentID = 현재 sessionID)
  → SessionPrompt.prompt() 재귀 호출 (완전한 새 루프)
  → 자식 세션 완료 후 결과 텍스트 반환
  → task_id 반환 (나중에 이어서 실행 가능)
```

**핵심**: TaskTool이 Multi-Agent 패턴의 실제 구현. 툴 하나가 완전한 Agent 루프를 새로 시작한다.

---

### ToolRegistry (`tool/registry.ts`)

전체 툴 목록 관리 및 조합:

```
내장 툴 (하드코딩)
  + 커스텀 툴 ({config_dir}/tool/*.{js,ts} 파일 로드)
  + 플러그인 툴
  → 모델별 필터링 (GPT-4 계열은 edit/write 대신 apply_patch 사용)
  → 에이전트 컨텍스트로 init()
  → LLM에 전달될 툴 목록 완성
```

**모델별 툴 분기**:
- GPT-4 계열 → `apply_patch` 툴 사용
- 나머지 → `edit` + `write` 툴 사용

---

## 4단계: Provider 시스템 분석

### Provider 아키텍처 (`provider/provider.ts`)

```
ModelsDev API (외부 모델 DB)
    │  - 모든 Provider/Model 메타데이터 제공
    ▼
Provider.Service.layer (Effect Service 초기화)
    │  - 환경변수에서 API Key 감지 → 자동 로드
    │  - opencode.json config에서 커스텀 Provider 병합
    │  - CUSTOM_LOADERS 실행 (Provider별 특수 설정)
    │  - 모델 whitelist/blacklist/disabled 필터링
    ▼
BUNDLED_PROVIDERS (20+ Provider 내장)
    │  - @ai-sdk/anthropic, @ai-sdk/openai, @ai-sdk/google 등
    │  - 없으면 BunProc.install()로 npm 패키지 동적 설치
    ▼
resolveSDK(model, state)
    │  - SSE 청크 타임아웃 래핑 (wrapSSE)
    │  - fetch 인터셉터로 openai itemId 제거
    ▼
getLanguage(model)
    │  - CUSTOM_LOADERS[providerID].getModel() 또는 sdk.languageModel()
    │  - 결과를 Map 캐시에 저장
```

#### Provider별 특수 처리

| Provider | 특이사항 |
|---------|---------|
| `anthropic` | `anthropic-beta` 헤더 자동 추가 (interleaved-thinking, fine-grained-tool-streaming) |
| `openai` | `sdk.responses(modelID)` 사용 (chat API 대신) |
| `github-copilot` | gpt-5 이상이면 Responses API, 미만이면 Chat API |
| `amazon-bedrock` | 리전별 cross-region prefix 자동 추가 (us./eu./ap. 등) |
| `google-vertex` | GoogleAuth로 Bearer token 자동 갱신 |
| `gitlab` | `discoverWorkflowModels()`로 동적 모델 디스커버리 |
| `opencode` | API Key 없으면 무료 모델만 노출 |

#### Model 타입 구조

```typescript
Provider.Model = {
  id: ModelID                 // "claude-sonnet-4-6"
  providerID: ProviderID      // "anthropic"
  api: { id, url, npm }       // SDK 연결 정보
  capabilities: {
    temperature, reasoning, attachment, toolcall
    input: { text, audio, image, video, pdf }
    output: { text, audio, image, video, pdf }
    interleaved: boolean | { field: "reasoning_content" | "reasoning_details" }
  }
  cost: { input, output, cache: { read, write } }
  limit: { context, input, output }
  variants: Record<string, Record<string, any>>  // reasoning effort 변형
}
```

---

### ProviderTransform (`provider/transform.ts`)

LLM에 메시지를 보내기 전 변환하는 파이프라인:

```
ProviderTransform.message(msgs, model, options)
    ├── unsupportedParts()   모델이 지원 안 하는 미디어 → 에러 텍스트로 대체
    ├── normalizeMessages()  Provider별 메시지 형식 정규화
    │     - Anthropic/Bedrock: 빈 content 필터링
    │     - Claude: tool-call ID 특수문자 → '_' 치환
    │     - Mistral: tool → user 사이에 더미 assistant 삽입
    │     - interleaved 모델: reasoning 파트를 providerOptions.field로 이동
    └── applyCaching()       Anthropic/Bedrock에 prompt cache 마킹
          - system 메시지 앞 2개 + 대화 마지막 2개에 ephemeral 캐시 태그
```

**온도/샘플링 파라미터**:
- `temperature()`: Claude=undefined, Gemini=1.0, Qwen=0.55, Kimi-k2=0.6/1.0
- `topP()`: Qwen=1, Gemini/MiniMax=0.95
- `topK()`: MiniMax=20/40, Gemini=64

**variants (reasoning effort)**:
- Claude Opus/Sonnet 4.6: `low/medium/high/max`
- OpenAI o시리즈: `low/medium/high/xhigh`
- Grok-3-mini: `low/high`

---

## 5단계: Server 시스템 분석

### 서버 구조 (`server/server.ts` + `server/instance.ts`)

```
Server.listen() → Bun.serve() 시작 (기본 4096 포트)
    │
    ▼
ControlPlaneRoutes (server.ts) - 글로벌 라우트
    ├── CORS 미들웨어 (localhost/tauri/opencode.ai 허용)
    ├── basicAuth 미들웨어 (OPENCODE_SERVER_PASSWORD 있을 때)
    ├── gzip 압축 (SSE/스트리밍 엔드포인트 제외)
    ├── GET  /global/*           → GlobalRoutes (프로바이더/인증)
    ├── PUT  /auth/:providerID   → Auth.set()
    ├── DELETE /auth/:providerID → Auth.remove()
    ├── GET  /doc                → OpenAPI 스펙
    └── WorkspaceRouterMiddleware → directory/workspace 쿼리로 인스턴스 라우팅
            │
            ▼
        InstanceRoutes (instance.ts) - 프로젝트별 라우트
            ├── /session/*      → 세션 CRUD + prompt 실행
            ├── /project/*      → 프로젝트 정보
            ├── /provider/*     → 모델 목록
            ├── /permission/*   → 권한 승인/거절
            ├── /question/*     → 사용자 질문 처리
            ├── /config/*       → 설정 읽기/쓰기
            ├── /pty/*          → 터미널 세션
            ├── /mcp/*          → MCP 서버 관리
            ├── /event          → SSE 이벤트 스트림
            ├── /tui            → TUI 전용 엔드포인트
            └── /*              → 내장 웹 UI 서빙 (없으면 app.opencode.ai 프록시)
```

#### 핵심 라우트 패턴

| 엔드포인트 | 역할 |
|-----------|------|
| `POST /session/:id/prompt` | 메시지 전송 → SessionPrompt.prompt() 호출 |
| `GET /event` | SSE 스트림 - 모든 실시간 이벤트 구독 |
| `GET /provider` | 사용 가능한 Provider/Model 목록 |
| `PUT /permission/:id` | 툴 실행 권한 승인 |
| `POST /session/:id/abort` | 진행 중인 루프 중단 |

#### 웹 UI 서빙 전략
- **빌드시 내장**: `opencode-web-ui.gen.ts`에 파일 경로 맵으로 번들
- **개발/폴백**: `app.opencode.ai`로 리버스 프록시
- **CSP 설정**: inline script의 SHA-256 해시를 동적 계산하여 허용

---

## 6단계: 저장소 시스템 분석

### 이중 저장소 구조

opencode는 **두 가지 저장소**를 병행 사용:

| 저장소 | 파일 | 용도 |
|-------|------|------|
| SQLite (Drizzle ORM) | `storage/db.ts` | 세션/메시지 구조화 데이터 |
| JSON 파일 저장소 | `storage/storage.ts` | 범용 key-value (설정, 파트 등) |

### SQLite (`storage/db.ts`)

```
Database.Path  →  ~/.local/share/opencode/opencode.db
                  (채널별 분리: opencode-nightly.db 등)

초기화:
  WAL 모드, 동기화=NORMAL, busy_timeout=5s, cache=64MB
  → 마이그레이션 자동 적용 (migration/ 디렉토리 또는 번들된 SQL)

사용 패턴:
  Database.use(callback)         일반 읽기/쓰기
  Database.transaction(callback) 트랜잭션 (중첩 지원 - Context 활용)
  Database.effect(fn)            트랜잭션 커밋 후 사이드이펙트 실행
```

### JSON 파일 저장소 (`storage/storage.ts`)

```
~/.local/share/opencode/storage/
  ├── project/          프로젝트 메타데이터
  ├── session/          세션 정보 (project별 서브디렉토리)
  ├── message/          메시지 데이터
  ├── part/             메시지 파트 (스트리밍 청크)
  └── session_diff/     세션 diff 통계

특징:
  - RcMap으로 파일별 TxReentrantLock (읽기/쓰기 잠금)
  - Effect 기반 비동기 처리
  - 2단계 마이그레이션 시스템 (기존 project-based → projectID-based)
```

---

## 7단계: 확장 시스템 분석

### MCP (Model Context Protocol) — `mcp/index.ts`

외부 MCP 서버를 연결해 LLM이 사용할 수 있는 툴/프롬프트/리소스를 동적으로 확장한다.

#### 연결 방식

| 타입 | 설명 |
|------|------|
| `local` | `command` 배열로 서브프로세스 실행 → stdio 통신 (StdioClientTransport) |
| `remote` | HTTP URL로 연결 → StreamableHTTP 먼저 시도, 실패 시 SSE 폴백 |

#### 인증 흐름 (OAuth 2.0)

```
opencode mcp auth <name>
    │
    ▼
McpOAuthProvider 생성
    │  - Dynamic Client Registration 시도
    │  - 브라우저로 인증 URL 열기
    ▼
McpOAuthCallback 로컬 서버
    │  - 리다이렉트 수신 → authorization code 캡처
    ▼
transport.finishAuth(code)
    │  - 토큰 교환 및 저장
    ▼
연결 재시도 → connected
```

상태: `connected` / `disabled` / `failed` / `needs_auth` / `needs_client_registration`

#### 핵심 동작
- 툴 목록 변경 알림(`ToolListChangedNotification`) 수신 시 실시간 갱신
- 툴 이름 충돌 방지: `{clientName}_{toolName}` 형식으로 자동 prefix
- 종료 시 자식 프로세스 및 모든 자손 프로세스 `SIGTERM` 전송

---

### LSP (Language Server Protocol) — `lsp/index.ts`

에디터 수준의 코드 인텔리전스를 Agent에 제공한다. EditTool이 파일 수정 후 LSP 진단을 실행해 에러를 LLM에게 피드백하는 것이 핵심 용도다.

#### 내장 LSP 서버 목록 (`lsp/server.ts`)

| 서버 | 언어 | 자동 설치 |
|------|------|---------|
| TypeScript (`tsserver`) | `.ts .tsx .js .jsx` | bun으로 설치 |
| Python (`pyright`) | `.py` | pip/bun |
| Rust (`rust-analyzer`) | `.rs` | 바이너리 다운로드 |
| Go (`gopls`) | `.go` | `go install` |
| Ruby (`ruby-lsp`) | `.rb` | `gem install` |
| 기타 | Java, PHP, C#, Swift, Kotlin 등 | 각각 다름 |

#### 파일별 동적 클라이언트 생성

```
파일 접근 (touchFile / diagnostics 등)
    │
    ▼
확장자로 해당하는 서버 목록 추출
    │
    ▼
NearestRoot() → 파일에서 위쪽으로 탐색
    │  - package.json, tsconfig.json 등으로 프로젝트 루트 결정
    ▼
(root + serverID) 키로 클라이언트 캐시 확인
    │  없으면 → server.spawn(root) → LSPClient.create()
    ▼
JSON-RPC로 요청 전송
```

#### 제공하는 기능

| 메서드 | LSP 요청 |
|-------|---------|
| `diagnostics()` | 모든 열린 파일의 에러/경고 수집 |
| `hover()` | `textDocument/hover` |
| `definition()` | `textDocument/definition` |
| `documentSymbol()` | `textDocument/documentSymbol` |
| `workspaceSymbol()` | `workspace/symbol` |
| `incomingCalls()` | `callHierarchy/incomingCalls` |

---

### Plugin 시스템 — `plugin/index.ts`

npm 패키지 또는 로컬 파일로 배포되는 플러그인을 로드해 훅을 등록한다.

#### 내장(Internal) 플러그인

| 플러그인 | 역할 |
|---------|------|
| `CodexAuthPlugin` | OpenAI Codex 인증 처리 |
| `CopilotAuthPlugin` | GitHub Copilot OAuth 처리 |
| `GitlabAuthPlugin` | GitLab 인증 처리 |
| `PoeAuthPlugin` | Poe 인증 처리 |

#### 플러그인 로딩 파이프라인

```
opencode.json의 plugin[] 항목
    │
    ▼
PluginLoader.plan()   스펙 파싱 (npm 패키지명 or file:// 경로)
    │
    ▼
PluginLoader.resolve()
    │  - npm 패키지: BunProc.install() → 버전 호환성 체크
    │  - 로컬 파일: 직접 경로 확인
    ▼
PluginLoader.load()   import()로 모듈 로드
    │
    ▼
applyPlugin()         hooks[] 배열에 등록
    │  - v1 플러그인: plugin.server(input) 호출
    │  - 레거시: export된 함수들을 순서대로 실행
    ▼
Bus 이벤트 구독       모든 이벤트를 플러그인에 전달 (hook["event"]?.())
```

#### Hook 트리거 방식

```typescript
// 모든 훅은 동일한 패턴: (input, output) => Promise<void>
// output 객체를 직접 변경해 동작을 수정
plugin.trigger("tool.execute.after", { tool, sessionID }, result)
```

훅 목록: `tool.execute.before/after`, `chat.message`, `shell.env`, `experimental.text.complete`, `config`, `event`

#### PluginMeta (`plugin/meta.ts`)
플러그인 설치 이력을 `~/.local/state/opencode/plugin-meta.json`에 기록:
- 최초 설치 시각, 마지막 로드 시각, 변경 감지(fingerprint), 로드 횟수
- 파일 플러그인: mtime으로 변경 감지 / npm 플러그인: 버전으로 감지

---

## 주요 도구 목록

| 도구 | 파일 | 특이사항 |
|------|------|---------|
| Bash | `tool/bash.ts` | tree-sitter AST 파싱, 권한 체크 |
| Read | `tool/read.ts` | 파일 읽기 |
| Edit | `tool/edit.ts` | 9단계 폴백 매칭, LSP 진단 |
| Write | `tool/write.ts` | 파일 쓰기 |
| Glob | `tool/glob.ts` | 파일 패턴 검색 |
| Grep | `tool/grep.ts` | 정규식 검색 |
| WebFetch | `tool/webfetch.ts` | 웹 페칭 |
| WebSearch | `tool/websearch.ts` | Exa 검색 엔진 |
| Task | `tool/task.ts` | **Multi-Agent 진입점** |
| Skill | `tool/skill.ts` | 스킬 호출 |
| ApplyPatch | `tool/apply_patch.ts` | GPT-4 전용 편집 툴 |
| TodoWrite | `tool/todo.ts` | 태스크 목록 관리 |

---

## 에이전트 모드

- **Build Agent**: 전체 권한, 파일 수정 가능
- **Plan Agent**: 읽기 전용, 분석 및 탐색용
- **General SubAgent**: 복잡한 검색 및 다단계 작업
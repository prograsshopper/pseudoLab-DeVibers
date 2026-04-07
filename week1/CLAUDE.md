# Week 1 — React + Apollo Client + Apollo Server + GraphQL Hello World

## 목적

### Basic Mission 1.
아래의 스펙으로 Hello World 페이지를 구현한다.
- React / Apollo Client / Apollo Server / GraphQL

## 프로젝트 구조

```
week1/
├── server/                   # Apollo Server (GraphQL API)
│   ├── src/
│   │   └── index.ts          # 스키마, 리졸버, 서버 실행 진입점
│   ├── package.json
│   └── tsconfig.json
└── client/                   # React 앱 (Apollo Client)
    ├── src/
    │   ├── main.tsx          # 앱 진입점, ApolloProvider 래핑
    │   ├── App.tsx           # UI 컴포넌트
    │   └── lib/
    │       ├── apolloClient.ts   # Apollo Client 인스턴스
    │       └── queries.ts        # GQL 쿼리 정의
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## 기술 스택

| 역할 | 라이브러리 |
|------|-----------|
| UI | React 18 |
| 번들러 | Vite 5 |
| GraphQL 클라이언트 | Apollo Client 3 |
| GraphQL 서버 | Apollo Server 4 |
| 언어 | TypeScript 5 |

## 실행 방법

서버와 클라이언트를 **각각 별도의 터미널**에서 실행한다.

### 서버

```bash
cd week1/server
npm install      # 최초 1회
npm run dev      # ts-node-dev로 핫리로드 실행
```

- 실행 포트: `http://localhost:4000`
- Apollo Sandbox(GraphQL IDE): 브라우저에서 `http://localhost:4000` 접속

### 클라이언트

```bash
cd week1/client
npm install      # 최초 1회
npm run dev      # Vite dev server 실행
```

- 실행 포트: `http://localhost:3000`

## GraphQL 스키마

```graphql
type Query {
  hello: String!
  helloWithName(name: String!): String!
}
```

## 구현된 기능

- `hello` 쿼리: 페이지 로드 시 자동 실행 → `"Hello, World!"` 출력
- `helloWithName(name)` 쿼리: 이름 입력 후 버튼 클릭 → `"Hello, {name}!"` 출력

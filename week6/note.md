# 빌더(Builder) 패턴
## 정의
- 복잡한 객체를 한 번에 생성하지 않고, 여러 단계로 나누어 조립하도록 객체 생성 과정을 캡슐화하며, 클라이언트가 그 과정을 간결하고 명확한 API로 사용할 수 있게 해주는 생성 패턴

## 해결하려는 문제
- 복잡한 객체를 생성자 하나로 만들면:
    - 생성자가 매우 커짐
    - optional parameter 증가
    - 객체 생성 로직이 복잡해짐

-> 이 문제들을 해결하기 위해 사용

## 핵심 구성 요소
- __Product__: 최종적으로 생성되는 객체
- __Builder__: 객체를 생성하는 인터페이스/추상 클래스
- __Concrete Builder__: 실제 생성 로직 구현
- __Director__ (선택적): 생성 순서를 관리

## 장단점
### 장점
1. 복잡한 객체 생성 과정을 캡슐화할 수 있다
- 객체 생성 로직을 Builder 내부로 숨겨서 클라이언트 코드가 단순해진다.
2. 객체를 단계별로 유연하게 생성할 수 있다
- 객체를 여러 단계에 걸쳐 생성할 수 있으며:
    - 생성 순서를 제어할 수 있고
    - 필요한 단계만 선택 가능하며
    - 생성 시점을 늦출 수도 있다.
- 즉, 복잡한 객체 조립 과정을 세밀하게 제어할 수 있다.
3. 같은 생성 과정을 재사용해 다양한 객체 표현을 만들 수 있다
- 동일한 생성 절차를 사용하더라도 서로 다른 결과물을 생성할 수 있다.
4. 제품의 내부 구조를 클라이언트로부터 숨길 수 있다
- 클라이언트는 Builder의 추상 API만 사용하므로, 객체 내부 구현이나 생성 방식 변경의 영향을 덜 받는다. 즉, 생성 로직과 구현 세부사항을 은닉할 수 있다.
5. 생성 코드와 비즈니스 로직을 분리할 수 있다 (SRP)
- 복잡한 객체 생성 책임을 Builder로 분리하여, 원래 객체(Product)는 자신의 핵심 비즈니스 로직에만 집중할 수 있다.

### 단점
1. 클래스 수와 구조 복잡성이 증가한다
- Builder, ConcreteBuilder, Director 등의 클래스가 추가되면서 전체 코드 구조가 복잡해질 수 있다. 특히 단순한 객체에는 오히려 과한 설계가 될 수 있다.

2. 객체 생성 과정에 대한 이해가 필요하다
- 클라이언트가 Builder의 사용 순서나 생성 과정을 어느 정도 이해해야 한다. 즉, 어떤 단계가 필요한지 어떤 순서로 조립해야 하는지 를 알아야 제대로 사용할 수 있다.
- 팩토리 패턴처럼 “한 번에 생성”하는 방식보다 사용 난이도가 조금 더 높을 수 있다.

## 실제 예제 - 랭그래프(LangGraph)
- [랭그래프 깃허브](https://github.com/langchain-ai/langgraph)
- AI 워크플로우를 단계적으로 조립하는 구조라서 Builder 패턴 느낌이 아주 강하다.
- 고전적인 빌더 패턴은 단순히 "필드가 많아서" 쓰기도 하지만, 더 중요한 목적은 "복잡한 객체를 안전하게 단계별로 만들기 위함"인데, LangGraph의 StateGraph가 이 메커니즘을 정확히 따르고 있다.
```
from langgraph.graph import StateGraph

workflow = StateGraph(State)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge("agent", "tools")
workflow.add_edge("tools", "agent")

workflow.set_entry_point("agent")

graph = workflow.compile()
```
### Builder 패턴 느낌인 이유
1. 빈 workflow 생성
2. node 추가
3. edge 추가
4. entry 설정
5. compile()로 최종 graph 생성

-> 복잡한 객체(Graph)”를 단계별로 조립하고 있다.

### 대응 관계

| Builder Pattern 개념 | LangGraph              |
| ------------------ | ---------------------- |
| Product            | 최종 compiled graph      |
| Builder            | StateGraph             |
| build step         | add_node(), add_edge() |
| Final build        | compile()              |

-> 복잡한 객체를 한 번에 생성하지 않고 단계별로 조립한 뒤 마지막에 완성(build/compile)한다

## 유사한 다른 디자인패턴과 비교
| 패턴        | 비유              |
| --------- | --------------- |
| Builder   | 레고를 하나씩 조립      |
| Factory   | 완성품을 공장에서 바로 생산 |
| Prototype | 기존 제품을 복사해서 사용  |


| 패턴            | 공통점      | 핵심 차이점           | 초점             | 대표 방식                             |
| ------------- | -------- | ---------------- | -------------- | --------------------------------- |
| **Builder**   | 객체 생성 패턴 | 객체를 단계별로 조립해서 생성 | “어떻게 조립할까?”    | `builder.step1().step2().build()` |
| **Factory**   | 객체 생성 패턴 | 객체를 한 번에 생성하고 반환 | “무슨 객체를 만들까?”  | `UserFactory.create("admin")`     |
| **Prototype** | 객체 생성 패턴 | 기존 객체를 복제해서 생성   | “기존 객체를 복사할까?” | `existing.clone()`                |


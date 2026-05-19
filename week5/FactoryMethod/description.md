# Factory Method Pattern 핵심 정리

> 참고 자료: Head First Design Patterns, refactoring.guru

---

## 1. 정의 & 의도

> "객체를 생성할 인터페이스는 부모(Creator) 클래스에서 정의하되, **어떤 클래스의 인스턴스를 만들지는 서브클래스(ConcreteCreator)가 결정**한다."

- 별칭: **가상 생성자 (Virtual Constructor)**
- 생성 패턴(Creational Pattern) 중 하나
- `new` 연산자를 직접 호출하는 대신, **팩토리 메서드를 호출하는 것으로 대체**

---

## 2. 문제 상황 (왜 쓰는가)

```
[Before]
물류 앱에 Truck만 있을 때
→ 코드 전체가 Truck 클래스에 강하게 결합

[After - Ship 추가 요구]
→ 전체 코드베이스 수정 + 수많은 if/else 조건문 폭발
```

**핵심 원인:** 객체 생성 코드(`new Truck()`)가 비즈니스 로직과 뒤섞여 있음 → **결합도(coupling) 문제**

---

## 3. 핵심 구성 요소

```
       «abstract»
        Creator
    ─────────────────
    + someOperation()           ← 비즈니스 로직 (여기에 핵심 로직이 있음)
    + createProduct(): Product  ← 팩토리 메서드 (추상 or 디폴트 구현)
         △
         │
  ┌──────┴──────┐
  ConcreteCreatorA   ConcreteCreatorB
  + createProduct()  + createProduct()
     return new A()     return new B()
                              │
                   «interface» Product
                   ─────────────────
                   + doStuff()
                         △
                    ┌────┴────┐
               ConcreteProductA  ConcreteProductB
```

| 구성요소 | 역할 |
|---------|------|
| **Product** | 모든 제품이 구현해야 할 공통 인터페이스 |
| **ConcreteProduct** | Product 인터페이스의 구체적 구현체 |
| **Creator** | 팩토리 메서드를 선언하는 클래스. **주 책임은 비즈니스 로직이지, 객체 생성이 아님** |
| **ConcreteCreator** | 팩토리 메서드를 오버라이드해 특정 제품을 반환 |

> **[보완]** Creator의 주 책임이 "제품 생산"인 것처럼 오해하기 쉽지만, Creator의 핵심은 비즈니스 로직이고, 팩토리 메서드는 그 로직을 구상 클래스로부터 분리(디커플링)하는 수단이다.

---

## 4. 동작 원리 (핵심 메커니즘)

```python
# Creator (추상 클래스)
class Dialog:
    def create_button(self) -> Button:  # 팩토리 메서드
        raise NotImplementedError

    def render(self):                   # 비즈니스 로직
        btn = self.create_button()      # 팩토리 메서드 호출
        btn.on_click(self.close_dialog)
        btn.render()

# ConcreteCreator
class WindowsDialog(Dialog):
    def create_button(self) -> Button:
        return WindowsButton()          # 구체 타입을 여기서 결정

class WebDialog(Dialog):
    def create_button(self) -> Button:
        return HTMLButton()
```

**클라이언트 코드는 `Button` 인터페이스만 알면 된다** → 구상 타입으로부터 독립

---

## 5. 제약 조건 (중요)

- 자식 클래스들이 반환할 수 있는 제품은 **반드시 공통 인터페이스 또는 공통 기초 클래스를 가져야 한다**
- 팩토리 메서드의 반환 타입은 Product 인터페이스로 선언되어야 함

---

## 6. 팩토리 메서드의 두 가지 형태

> 팩토리 메서드가 항상 `abstract`(추상)이어야 하는 것은 아니다. 실제로는 두 가지 형태가 가능하다:

| 형태 | 설명 |
|------|------|
| **추상 팩토리 메서드** | 모든 서브클래스가 반드시 구현하도록 강제 |
| **디폴트 구현이 있는 팩토리 메서드** | 기본 제품 타입을 반환하고, 서브클래스에서 선택적 오버라이드 |

---

## 7. 팩토리 메서드 ≠ 항상 `new`

> 팩토리 메서드는 반드시 새 객체를 생성할 필요가 없다.

```
팩토리 메서드가 반환 가능한 것:
- new로 새로 생성한 객체
- 캐시(Cache)에서 꺼낸 기존 객체
- 객체 풀(Object Pool)에서 가져온 객체
```

→ DB 연결, 파일 시스템, 네트워크처럼 **생성 비용이 큰 객체 재사용**에 유용

---

## 8. 적용 시점

1. 함께 작동할 객체의 **정확한 유형과 의존관계를 미리 알 수 없을 때**
2. 라이브러리/프레임워크 사용자에게 **내부 컴포넌트 확장 방법을 제공**하고 싶을 때
3. 기존 객체 재사용으로 **시스템 리소스를 절약**하고 싶을 때

---

## 9. 장단점

| 장점 | 단점 |
|------|------|
| Creator와 ConcreteProduct 간 **결합도 제거** | 새 제품마다 ConcreteCreator 서브클래스가 필요 → **클래스 수 증가** |
| **단일 책임 원칙(SRP)**: 객체 생성 코드를 한 곳으로 집중 | 간단한 경우에는 오히려 과설계(over-engineering)가 될 수 있음 |
| **개방/폐쇄 원칙(OCP)**: 기존 코드 수정 없이 새 제품 추가 가능 | |

> **[첨언]** 이 패턴은 SRP/OCP 외에도 **DIP(의존성 역전 원칙)**도 실현한다. Creator가 ConcreteProduct에 직접 의존하지 않고 Product 인터페이스(추상)에 의존하기 때문이다.

---

## 10. Simple Factory vs Factory Method (혼동 주의)

| | Simple Factory | Factory Method Pattern |
|--|----------------|------------------------|
| **형태** | 단순 클래스/메서드 | 상속 기반 패턴 |
| **확장** | 팩토리 클래스 수정 필요 | 서브클래스 추가로 확장 (OCP 만족) |
| **GoF 패턴 여부** | 아님 (관용구) | 공식 GoF 패턴 |

---

## 11. 다른 패턴과의 관계

```
Factory Method
    │
    ├─ 여러 개 모으면 → Abstract Factory
    │
    ├─ 알고리즘 뼈대 관점에서 → Template Method의 특수화
    │   (Template Method가 알고리즘 단계를 서브클래스에 위임하듯,
    │    Factory Method는 객체 생성을 서브클래스에 위임)
    │
    └─ 더 복잡해지면 → Prototype, Builder 패턴으로 발전
```

> 패턴의 진화 방향: 디자인은 보통 Factory Method처럼 단순한 것에서 시작해, 요구가 복잡해지면 Abstract Factory나 Builder로 발전한다. 처음부터 복잡한 패턴을 선택할 필요는 없다.
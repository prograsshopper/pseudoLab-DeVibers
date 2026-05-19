# Factory Method Pattern 실습 예제 (Simple)
## 쇼핑몰 주문 완료 알림 시스템

---

## 시나리오

쇼핑몰 **"ShopNow"** 에서는 주문이 완료되면 사용자에게 알림을 보낸다.
현재 지원하는 채널은 **Email**, **SMS**, **Kakao** 3가지이며,
채널마다 메시지 형식이 다르다.

```
Email  →  "[주문 완료] 주문번호: ORD-001 | 상품: MacBook Pro"  (일반 텍스트)
SMS    →  "[ShopNow] 주문(ORD-001) 완료. MacBook Pro"          (단문)
Kakao  →  "template=ORDER_01 | order_id=ORD-001, item=MacBook Pro"  (템플릿 기반)
```

처음에는 Email만 있었는데, SMS와 Kakao가 순서대로 추가되면서
아래처럼 조건문이 쌓이기 시작했다:

```python
if channel == "email":
    message = f"[주문 완료] 주문번호: {order_id} | 상품: {item_name}"
    send_email(to, message)
elif channel == "sms":
    message = f"[ShopNow] 주문({order_id}) 완료. {item_name}"
    send_sms(to, message)
elif channel == "kakao":
    ...
```

**새 채널이 추가될 때마다 이 조건문을 수정해야 한다.**
Factory Method 패턴을 적용해서 새 채널을 추가해도 기존 코드를 수정하지 않도록 개선하라.

---

## 요구사항

1. **채널별 메시지 형식이 다르다** — Email / SMS / Kakao 각각 `format_message()` 구현
2. **발송 인터페이스는 동일하다** — 어떤 채널이든 `send(to, message)` 로 발송
3. **어떤 채널 인스턴스를 만들지는 서브클래스가 결정한다** — 팩토리 메서드 적용
4. **새 채널(예: Push) 추가 시 기존 코드는 수정하지 않는다** — OCP 만족 여부 확인

---

## 클래스 구조 힌트

```
«interface»
Notifier                        ← Product
────────────────────
+ format_message(order_id, item_name) -> str
+ send(to, message) -> None
        △
        │
┌───────┼───────┐
Email  SMS   Kakao
Notifier    Notifier  Notifier  ← ConcreteProduct


«abstract»
NotificationFactory             ← Creator
────────────────────
+ create_notifier() -> Notifier     ← 팩토리 메서드 (추상)
+ notify(to, order_id, item_name)   ← 비즈니스 로직 (공통)
        △
        │
┌───────┼───────┐
Email  SMS   Kakao
NotificationFactory              ← ConcreteCreator
```

---

## 구현 과제

- [ ] `Notifier` 인터페이스 정의
- [ ] `EmailNotifier`, `SMSNotifier`, `KakaoNotifier` 구현
- [ ] `NotificationFactory` 추상 클래스 + `notify()` 구현
- [ ] `EmailNotificationFactory`, `SMSNotificationFactory`, `KakaoNotificationFactory` 구현
- [ ] `main.py` 에서 3가지 채널로 알림 발송 확인
- [ ] `PushNotifier` + `PushNotificationFactory` 추가 시 기존 코드 변경 없이 동작하는지 확인

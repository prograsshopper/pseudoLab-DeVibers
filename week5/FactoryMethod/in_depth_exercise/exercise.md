# Factory Method Pattern 실습 예제
## 멀티채널 알림 시스템 (Multi-Channel Notification System)

---

## 배경 시나리오

당신은 중규모 이커머스 플랫폼 **"ShopNow"** 의 백엔드 개발자다.
ShopNow는 하루 주문 건수 약 10만 건, 회원 수 50만 명을 보유하고 있으며
현재 다음과 같은 알림을 사용자에게 발송한다:

- 주문 접수 / 결제 완료
- 배송 시작 / 배송 완료
- 재입고 알림
- 마케팅 프로모션

초기에는 **이메일(Email)** 알림만 있었다. 그러다 사용자 요청으로 **SMS**, **카카오톡(Kakao)**, **앱 푸시(Push)** 가 순차적으로 추가되었고,
알림을 보낼 때마다 아래와 같은 코드가 반복되었다:

```python
if channel == "email":
    send_email(user.email, subject, body)
elif channel == "sms":
    send_sms(user.phone, message)
elif channel == "kakao":
    send_kakao(user.kakao_id, message)
elif channel == "push":
    send_push(user.device_token, title, body)
```

이 코드는 새로운 채널이 추가될 때마다 여러 곳을 함께 수정해야 해서
버그가 자주 발생하고, 채널별 로직이 뒤섞여 테스트가 어렵다.

**당신의 임무**: Factory Method 패턴을 적용해 이 시스템을 재설계하라.

---

## 도메인 이해

### 알림 채널 (Notification Channel)

| 채널 | 특징 | 제한 |
|------|------|------|
| **Email** | HTML 본문 지원, 첨부파일 가능 | 발송 후 도달까지 최대 수 분 소요 |
| **SMS** | 90바이트 이내 단문, 한국어 약 45자 | 건당 비용 발생, 광고 문자 수신거부 대상 |
| **Kakao** | 템플릿 기반, 버튼 추가 가능 | 카카오 채널 친구 추가 사용자만 수신 |
| **Push** | 앱 설치 사용자 대상, 즉시 도달 | 기기 토큰 만료 가능성 있음 |

### 알림 유형 (Notification Type)

| 유형 | 우선순위 | 기본 채널 | 폴백 채널 |
|------|---------|---------|---------|
| `ORDER_CONFIRMED` | 높음 | Kakao | SMS → Email |
| `SHIPPING_STARTED` | 높음 | Push | Kakao → SMS |
| `SHIPPING_COMPLETED` | 중간 | Push | Kakao |
| `RESTOCK_ALERT` | 낮음 | Email | Push |
| `PROMOTION` | 낮음 | Email | - (수신 동의자만) |

---

## 요구사항

### 기능 요구사항

**[FR-1] 채널별 독립적인 메시지 포맷**
- 채널마다 메시지를 다르게 구성해야 한다
- Email: HTML 템플릿 렌더링
- SMS: 90바이트 이내 단문으로 자동 절삭
- Kakao: 정해진 템플릿 코드 + 변수 바인딩
- Push: title / body 분리

**[FR-2] 사용자 수신 설정 반영**
- 사용자는 채널별로 수신 여부를 설정할 수 있다 (opt-in / opt-out)
- 마케팅 알림은 명시적 수신 동의자에게만 발송
- 수신 설정이 없는 채널로는 발송하지 않는다

**[FR-3] 폴백(Fallback) 메커니즘**
- 우선순위가 높은 알림은 기본 채널 발송 실패 시 폴백 채널로 재시도한다
- 모든 채널이 실패하면 실패 로그를 남기고 알림팀에 내부 슬랙 메시지를 보낸다

**[FR-4] 발송 결과 로깅**
- 모든 발송 시도에 대해 아래 정보를 기록한다:
  - 수신자 ID, 알림 유형, 채널, 발송 시각, 성공 여부, 실패 사유

**[FR-5] 채널별 발송 제한 (Rate Limiting)**
- SMS: 동일 사용자에게 1분에 최대 3건
- Push: 동일 사용자에게 1시간에 최대 10건
- 제한 초과 시 해당 채널을 건너뛰고 폴백 채널로 이동

**[FR-6] 새로운 채널 추가 시 기존 코드 무수정**
- 향후 `Slack`, `Line`, `Discord` 채널이 추가될 수 있다
- 새 채널 추가 시 기존 발송 로직을 수정하지 않아야 한다 (OCP)

---

### 비기능 요구사항

- 채널별 클래스는 단독으로 테스트 가능해야 한다 (SRP)
- 알림 발송 핵심 로직은 구체적인 채널 클래스를 직접 참조해선 안 된다 (DIP)
- 채널 추가 시 `NotificationService` 내부 코드는 변경되지 않아야 한다 (OCP)

---

## 설계 가이드

### 등장인물 (역할과 책임)

```
«interface»
Notifier                          ← Product
─────────────────────────────
+ send(recipient, message) -> NotificationResult
+ validate(recipient) -> bool
+ format_message(template, context) -> str


EmailNotifier                     ← ConcreteProduct
SMSNotifier                       ← ConcreteProduct
KakaoNotifier                     ← ConcreteProduct
PushNotifier                      ← ConcreteProduct


«abstract»
NotificationFactory               ← Creator
─────────────────────────────
+ create_notifier() -> Notifier   ← 팩토리 메서드 (추상)
+ notify(event) -> bool           ← 핵심 비즈니스 로직
  (수신 설정 확인 → rate limit 확인 → 발송 → 로깅 → 폴백)


EmailNotificationFactory          ← ConcreteCreator
SMSNotificationFactory            ← ConcreteCreator
KakaoNotificationFactory          ← ConcreteCreator
PushNotificationFactory           ← ConcreteCreator
```

### 핵심 흐름 (notify 메서드 내부)

```
notify(event) 호출
    │
    ├─ 1. 사용자 수신 설정 확인 (opt-in/out)
    │       └─ 수신 거부 → 종료
    │
    ├─ 2. Rate Limit 확인
    │       └─ 초과 → 폴백 채널로 전환
    │
    ├─ 3. create_notifier() 호출  ← 팩토리 메서드
    │       └─ 구체적인 Notifier 생성
    │
    ├─ 4. notifier.validate(recipient)
    │       └─ 유효하지 않음 → 폴백 채널로 전환
    │
    ├─ 5. notifier.format_message(template, context)
    │
    ├─ 6. notifier.send(recipient, message)
    │       └─ 실패 → 폴백 채널로 전환
    │
    └─ 7. 결과 로깅
```

### 데이터 구조 참고

```python
# 알림 이벤트 (입력)
@dataclass
class NotificationEvent:
    event_type: str          # "ORDER_CONFIRMED", "SHIPPING_STARTED", ...
    user_id: int
    context: dict            # 메시지 본문에 쓸 변수들
                             # e.g. {"order_id": 123, "item_name": "맥북"}

# 발송 결과 (출력)
@dataclass
class NotificationResult:
    success: bool
    channel: str
    sent_at: datetime
    error_message: str | None
```

---

## 구현 과제

### Phase 1 — 기본 구조 구현
- [ ] `Notifier` 인터페이스 정의 (`send`, `validate`, `format_message`)
- [ ] `EmailNotifier`, `SMSNotifier` 구현
- [ ] `NotificationFactory` 추상 클래스 + `notify()` 비즈니스 로직 구현
- [ ] `EmailNotificationFactory`, `SMSNotificationFactory` 구현
- [ ] `NotificationEvent`, `NotificationResult` 데이터 클래스 정의

### Phase 2 — 채널 확장
- [ ] `KakaoNotifier` / `KakaoNotificationFactory` 추가
- [ ] `PushNotifier` / `PushNotificationFactory` 추가
- [ ] **Phase 1에서 작성한 `notify()` 코드를 수정하지 않고 추가되는지 확인**

### Phase 3 — 실전 기능 추가
- [ ] 폴백(Fallback) 메커니즘: 실패 시 다음 채널로 자동 전환
- [ ] Rate Limiting: 채널별 발송 횟수 제한 로직
- [ ] 발송 결과 로깅

### Phase 4 — 검증
- [ ] 각 `Notifier` 를 단독으로 단위 테스트 작성
- [ ] `NotificationFactory.notify()` 는 Mock Notifier로 테스트
- [ ] 새 채널(`SlackNotifier`) 추가 시 기존 테스트가 모두 통과하는지 확인

---

## 토론 포인트

1. `NotificationFactory`가 추상 클래스가 아니라 `NotificationService` 하나에 `channel` 파라미터를 받도록 구현하면 어떤 문제가 생길까?

2. 폴백 채널도 Factory Method로 처리하려면 구조를 어떻게 바꿔야 할까?

3. 채널 선택 로직(어떤 이벤트에 어떤 채널을 쓸지)을 Factory 안에 두는 게 맞을까, 아니면 별도 클래스로 분리하는 게 맞을까?

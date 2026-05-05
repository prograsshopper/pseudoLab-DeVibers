# ============================================================
# CREATOR (추상 클래스) + CONCRETE CREATORS
# ─────────────────────────────────────────────────────────────
#
#  ★ create_notifier() : 팩토리 메서드
#                        "무엇을 만들지"는 서브클래스가 결정한다.
#
#  ★ notify()          : 비즈니스 로직
#                        create_notifier()를 호출하지만
#                        반환된 것이 Email인지 SMS인지 알지 못한다.
#                        오직 Notifier 인터페이스를 통해서만 사용한다.
# ============================================================

# ── Creator ───────────────────────────────────────────────────
ABSTRACT CLASS NotificationFactory:

    ABSTRACT METHOD create_notifier() -> Notifier:
        # 서브클래스(ConcreteCreator)에서만 구현한다.
        MUST BE OVERRIDDEN

    METHOD notify(to, order_id, item_name):
        notifier = self.create_notifier()          # ← 팩토리 메서드 호출
                                                   #   구체 타입을 모른 채 사용
        message  = notifier.format_message(order_id, item_name)
        notifier.send(to, message)


# ── Concrete Creators ─────────────────────────────────────────
# create_notifier() 하나만 구현하면 된다.
# notify()의 비즈니스 로직은 부모 클래스에서 그대로 상속받는다.

CLASS EmailNotificationFactory EXTENDS NotificationFactory:
    METHOD create_notifier() -> Notifier:
        RETURN new EmailNotifier()

CLASS SMSNotificationFactory EXTENDS NotificationFactory:
    METHOD create_notifier() -> Notifier:
        RETURN new SMSNotifier()

CLASS KakaoNotificationFactory EXTENDS NotificationFactory:
    METHOD create_notifier() -> Notifier:
        RETURN new KakaoNotifier()

# 새 채널 추가: 이 클래스 하나만 추가하면 된다.
CLASS PushNotificationFactory EXTENDS NotificationFactory:
    METHOD create_notifier() -> Notifier:
        RETURN new PushNotifier()

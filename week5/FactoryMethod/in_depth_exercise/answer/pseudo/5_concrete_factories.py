# ============================================================
# CONCRETE CREATOR — 채널별 팩토리 구현체
# ─────────────────────────────────────────────────────────────
# 각 클래스는 create_notifier() 하나만 구현한다.
# 나머지 비즈니스 로직(notify, _try_fallback 등)은
# 모두 부모 클래스(NotificationFactory)에서 상속받는다.
#
# 이것이 Factory Method 패턴의 핵심:
# "무엇을 만들지(create_notifier)는 서브클래스가 결정하고,
#  만든 것으로 무엇을 할지(notify)는 부모 클래스가 처리한다."
# ============================================================

CLASS EmailNotificationFactory EXTENDS NotificationFactory:

    METHOD create_notifier() -> Notifier:
        RETURN new EmailNotifier()          # Email 채널 생성


CLASS SMSNotificationFactory EXTENDS NotificationFactory:

    METHOD create_notifier() -> Notifier:
        RETURN new SMSNotifier()            # SMS 채널 생성


CLASS KakaoNotificationFactory EXTENDS NotificationFactory:

    METHOD create_notifier() -> Notifier:
        RETURN new KakaoNotifier()          # Kakao 채널 생성


CLASS PushNotificationFactory EXTENDS NotificationFactory:

    METHOD create_notifier() -> Notifier:
        RETURN new PushNotifier()           # Push 채널 생성


# ─────────────────────────────────────────────────────────────
# 새 채널 추가 예시: Slack
# 기존 코드(factory.py, email/sms/kakao/push 파일들)는 전혀 수정하지 않는다.
# ─────────────────────────────────────────────────────────────

CLASS SlackNotifier IMPLEMENTS Notifier:
    channel_name = "slack"
    validate     = Slack 웹훅 URL이 존재하는지 확인
    format_message = Slack Block Kit 형식으로 변환
    send         = Slack Incoming Webhook API 호출

CLASS SlackNotificationFactory EXTENDS NotificationFactory:

    METHOD create_notifier() -> Notifier:
        RETURN new SlackNotifier()          # Slack 채널 생성

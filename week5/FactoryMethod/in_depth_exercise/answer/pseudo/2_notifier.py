# ============================================================
# PRODUCT (인터페이스)
# ─────────────────────────────────────────────────────────────
# 모든 알림 채널이 구현해야 하는 공통 계약.
# Creator(NotificationFactory)는 이 인터페이스에만 의존하므로
# 새 채널이 추가되어도 Creator 코드는 변경되지 않는다.
# ============================================================

INTERFACE Notifier:

    PROPERTY channel_name -> 문자열:
        # 채널 식별자를 반환한다. ("email", "sms", "kakao", "push")
        ABSTRACT

    METHOD validate(recipient: UserPreference) -> 불리언:
        # 수신자 정보가 이 채널로 발송 가능한 상태인지 확인한다.
        # e.g. 이메일 주소 형식, 전화번호 형식, 기기 토큰 존재 여부
        ABSTRACT

    METHOD format_message(event_type: 문자열, context: 딕셔너리) -> 문자열:
        # 채널에 맞는 포맷으로 메시지를 변환한다.
        # e.g. Email → HTML, SMS → 90바이트 단문, Kakao → 템플릿 코드
        ABSTRACT

    METHOD send(recipient: UserPreference, message: 문자열) -> NotificationResult:
        # 외부 API를 호출해 실제로 메시지를 발송한다.
        ABSTRACT

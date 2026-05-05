# ============================================================
# MODELS — 시스템에서 사용하는 데이터 구조
# ============================================================

# 사용자 수신 설정
DATA UserPreference:
    user_id          : 정수
    email            : 문자열 or NULL
    phone            : 문자열 or NULL
    kakao_id         : 문자열 or NULL
    device_token     : 문자열 or NULL          # 앱 푸시용 기기 토큰
    opted_in_channels: 문자열 목록             # ["email", "sms", "kakao", "push"]
    marketing_consent: 불리언 (기본값 = False)


# 알림 발송 요청 (입력)
DATA NotificationEvent:
    event_type  : 문자열        # "ORDER_CONFIRMED", "SHIPPING_STARTED", ...
    user        : UserPreference
    context     : 딕셔너리      # 메시지 템플릿에 바인딩할 변수
                                # e.g. {"order_id": "ORD-001", "item_name": "MacBook"}
    is_marketing: 불리언 (기본값 = False)


# 발송 결과 (출력)
DATA NotificationResult:
    success      : 불리언
    channel      : 문자열        # 실제로 발송된 채널 이름
    sent_at      : 시각
    error_message: 문자열 or NULL

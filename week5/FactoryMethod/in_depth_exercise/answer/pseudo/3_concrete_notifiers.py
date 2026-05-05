# ============================================================
# CONCRETE PRODUCT — 채널별 구체 구현체
# 모두 Notifier 인터페이스를 구현한다.
# 각 클래스는 오직 자신의 채널에 대한 책임만 진다. (SRP)
# ============================================================


# ── Email ────────────────────────────────────────────────────
CLASS EmailNotifier IMPLEMENTS Notifier:

    PROPERTY channel_name:
        RETURN "email"

    METHOD validate(recipient):
        RETURN recipient.email 이 존재하고 "@" 포함

    METHOD format_message(event_type, context):
        template = HTML_TEMPLATES에서 event_type에 해당하는 HTML 가져오기
        RETURN template에 context 변수 바인딩한 결과
        # e.g. "<h1>주문 확인</h1><p>주문번호: ORD-001 | 상품: MacBook</p>"

    METHOD send(recipient, message):
        AWS SES 또는 SMTP 클라이언트로 recipient.email에 message 발송
        RETURN NotificationResult(success=True, channel="email")


# ── SMS ──────────────────────────────────────────────────────
CLASS SMSNotifier IMPLEMENTS Notifier:

    PROPERTY channel_name:
        RETURN "sms"

    METHOD validate(recipient):
        RETURN recipient.phone 이 "010"으로 시작하는지 확인

    METHOD format_message(event_type, context):
        template = SMS_TEMPLATES에서 event_type에 해당하는 단문 가져오기
        message  = template에 context 변수 바인딩
        IF message의 바이트 길이 > 90 THEN
            message = 90바이트에서 잘라내기 + "..."
        RETURN message

    METHOD send(recipient, message):
        네이버 클라우드 SMS API 또는 Twilio로 recipient.phone에 message 발송
        RETURN NotificationResult(success=True, channel="sms")


# ── Kakao ─────────────────────────────────────────────────────
CLASS KakaoNotifier IMPLEMENTS Notifier:

    PROPERTY channel_name:
        RETURN "kakao"

    METHOD validate(recipient):
        RETURN recipient.kakao_id 가 존재하는지 확인
        # 카카오 채널 친구 추가 사용자에게만 발송 가능

    METHOD format_message(event_type, context):
        template_code = KAKAO_TEMPLATE_CODES에서 event_type에 해당하는 코드 가져오기
        # 카카오 알림톡은 사전 심사를 통과한 템플릿 코드를 사용한다.
        RETURN template_code와 context를 API 페이로드 형태로 묶기

    METHOD send(recipient, message):
        카카오 비즈메시지 API로 recipient.kakao_id에 message 발송
        RETURN NotificationResult(success=True, channel="kakao")


# ── Push ──────────────────────────────────────────────────────
CLASS PushNotifier IMPLEMENTS Notifier:

    PROPERTY channel_name:
        RETURN "push"

    METHOD validate(recipient):
        RETURN recipient.device_token 이 존재하는지 확인
        # 토큰이 만료된 경우에도 False를 반환해야 하지만 여기선 존재 여부만 확인

    METHOD format_message(event_type, context):
        (title_template, body_template) = PUSH_TEMPLATES에서 event_type에 해당 가져오기
        title = title_template에 context 바인딩
        body  = body_template에 context 바인딩
        RETURN title과 body를 묶은 페이로드

    METHOD send(recipient, message):
        FCM(Android) 또는 APNs(iOS)로 recipient.device_token에 message 발송
        RETURN NotificationResult(success=True, channel="push")

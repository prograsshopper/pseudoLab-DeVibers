# ============================================================
# PRODUCT (인터페이스) + CONCRETE PRODUCTS
# ============================================================

# ── Product ──────────────────────────────────────────────────
INTERFACE Notifier:

    METHOD format_message(order_id, item_name) -> 문자열:
        # 채널에 맞는 형식으로 메시지를 만들어 반환한다.
        ABSTRACT

    METHOD send(to, message) -> 없음:
        # 외부 API를 호출해 메시지를 발송한다.
        ABSTRACT


# ── Concrete Products ─────────────────────────────────────────
CLASS EmailNotifier IMPLEMENTS Notifier:

    METHOD format_message(order_id, item_name):
        RETURN "[주문 완료] 주문번호: {order_id} | 상품: {item_name}"

    METHOD send(to, message):
        AWS SES 또는 SMTP로 to에 message 발송


CLASS SMSNotifier IMPLEMENTS Notifier:

    METHOD format_message(order_id, item_name):
        RETURN "[ShopNow] 주문({order_id}) 완료. {item_name}"

    METHOD send(to, message):
        SMS API로 to(전화번호)에 message 발송


CLASS KakaoNotifier IMPLEMENTS Notifier:

    METHOD format_message(order_id, item_name):
        RETURN "template=ORDER_01 | order_id={order_id}, item={item_name}"

    METHOD send(to, message):
        카카오 비즈메시지 API로 to(카카오 ID)에 message 발송


# 새 채널 추가 시 이 파일에 클래스 하나만 추가하면 된다.
# 아래 Creator 코드는 전혀 수정하지 않는다. (OCP)
CLASS PushNotifier IMPLEMENTS Notifier:
    format_message → "title='주문 완료' | body='주문({order_id}) {item_name}'"
    send           → FCM / APNs로 to(기기 토큰)에 message 발송

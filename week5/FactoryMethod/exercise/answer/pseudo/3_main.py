# ============================================================
# MAIN — 조립 및 실행
# ─────────────────────────────────────────────────────────────
# 클라이언트는 ConcreteFactory만 교체하면 된다.
# notify() 내부 로직은 건드리지 않는다.
# ============================================================

# ── 기본 발송 ─────────────────────────────────────────────────
factories = [
    new EmailNotificationFactory(),
    new SMSNotificationFactory(),
    new KakaoNotificationFactory(),
]

FOR factory IN factories:
    factory.notify(to=사용자_주소, order_id="ORD-001", item_name="MacBook Pro")

# 실행 결과:
# [EMAIL] → alice@example.com  /  [주문 완료] 주문번호: ORD-001 | 상품: MacBook Pro
# [SMS]   → 010-1234-5678      /  [ShopNow] 주문(ORD-001) 완료. MacBook Pro
# [KAKAO] → kakao_alice        /  template=ORDER_01 | order_id=ORD-001, item=MacBook Pro


# ── OCP 확인: Push 채널 추가 ─────────────────────────────────
# push_notifier.py + PushNotificationFactory 정의만 추가.
# 위 코드와 factory.py, notifier.py 등 기존 파일은 변경 없음.

new PushNotificationFactory().notify("device_token_xyz", "ORD-001", "MacBook Pro")

# 실행 결과:
# [PUSH]  → token=device_token_xyz  /  title='주문 완료' | body='주문(ORD-001) MacBook Pro'

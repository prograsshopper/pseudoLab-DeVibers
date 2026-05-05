"""
멀티채널 알림 시스템 — Factory Method 패턴 데모
실행: python main.py  (python/ 디렉토리에서)
"""

from email_factory import EmailNotificationFactory
from kakao_factory import KakaoNotificationFactory
from models import NotificationEvent, UserPreference
from notification_logger import NotificationLogger
from push_factory import PushNotificationFactory
from rate_limiter import RateLimiter
from sms_factory import SMSNotificationFactory


# ── 폴백 체인을 포함한 팩토리 조립 ──────────────────────────────────────────
def build_factories(
    rate_limiter: RateLimiter,
    logger: NotificationLogger,
) -> dict:
    """
    알림 유형별 팩토리와 폴백 체인을 조립한다.

    폴백 체인:
      Push → Kakao → SMS → Email → (실패)

    각 팩토리는 create_notifier()만 다르고,
    notify()의 비즈니스 로직(수신 설정 확인, Rate Limit, 로깅 등)은
    NotificationFactory 부모 클래스가 공통으로 처리한다.
    """
    email  = EmailNotificationFactory(rate_limiter, logger)
    sms    = SMSNotificationFactory(rate_limiter, logger, fallback=email)
    kakao  = KakaoNotificationFactory(rate_limiter, logger, fallback=sms)
    push   = PushNotificationFactory(rate_limiter, logger, fallback=kakao)

    return {
        "ORDER_CONFIRMED":    kakao,   # Kakao → SMS → Email
        "SHIPPING_STARTED":   push,    # Push  → Kakao → SMS → Email
        "SHIPPING_COMPLETED": push,
        "RESTOCK_ALERT":      email,
        "PROMOTION":          EmailNotificationFactory(rate_limiter, logger),  # 폴백 없음
    }


def divider(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("="*60)


# ── 시나리오용 유저 픽스처 ────────────────────────────────────────────────────
def make_user(
    user_id: int,
    *,
    email: str | None = None,
    phone: str | None = None,
    kakao_id: str | None = None,
    device_token: str | None = None,
    opted_in_channels: list[str] | None = None,
    marketing_consent: bool = False,
) -> UserPreference:
    return UserPreference(
        user_id=user_id,
        email=email,
        phone=phone,
        kakao_id=kakao_id,
        device_token=device_token,
        opted_in_channels=opted_in_channels or [],
        marketing_consent=marketing_consent,
    )


def main() -> None:
    rate_limiter = RateLimiter()
    logger = NotificationLogger()
    factories = build_factories(rate_limiter, logger)

    # ── 시나리오 1: 정상 발송 (주문 확인 → Kakao) ───────────────────────────
    divider("시나리오 1: 정상 발송 (ORDER_CONFIRMED → Kakao)")
    user1 = make_user(
        1001,
        email="alice@example.com",
        phone="010-1234-5678",
        kakao_id="kakao_alice",
        device_token="fcm_token_alice_abcdef1234567890",
        opted_in_channels=["email", "sms", "kakao", "push"],
    )
    factories["ORDER_CONFIRMED"].notify(NotificationEvent(
        event_type="ORDER_CONFIRMED",
        user=user1,
        context={"order_id": "ORD-9001", "item_name": "MacBook Pro 14"},
    ))

    # ── 시나리오 2: Kakao 미연동 → SMS 폴백 ─────────────────────────────────
    divider("시나리오 2: Kakao 미연동 → SMS 폴백")
    user2 = make_user(
        1002,
        email="bob@example.com",
        phone="010-9999-0000",
        kakao_id=None,          # 카카오 미연동 → validate() 실패
        opted_in_channels=["email", "sms", "kakao"],  # 수신은 동의했지만 연동 안 됨
    )
    factories["ORDER_CONFIRMED"].notify(NotificationEvent(
        event_type="ORDER_CONFIRMED",
        user=user2,
        context={"order_id": "ORD-9002", "item_name": "iPad Air"},
    ))

    # ── 시나리오 3: Kakao 수신 거부 → SMS 폴백 ──────────────────────────────
    divider("시나리오 3: Kakao 수신 거부(opt-out) → SMS 폴백")
    user3 = make_user(
        1003,
        email="carol@example.com",
        phone="010-5555-4444",
        kakao_id="kakao_carol",
        device_token="fcm_token_carol_xyz7890123456789",
        opted_in_channels=["email", "sms"],  # kakao는 opt-out
    )
    factories["ORDER_CONFIRMED"].notify(NotificationEvent(
        event_type="ORDER_CONFIRMED",
        user=user3,
        context={"order_id": "ORD-9003", "item_name": "AirPods Pro"},
    ))

    # ── 시나리오 4: SMS Rate Limit 초과 → Email 폴백 ────────────────────────
    divider("시나리오 4: SMS Rate Limit(1분 3건) 초과 → Email 폴백")
    user4 = make_user(
        1004,
        email="david@example.com",
        phone="010-3333-2222",
        kakao_id=None,          # 카카오 미연동
        opted_in_channels=["email", "sms"],
    )
    # SMS Rate Limit 3건 소진
    for _ in range(3):
        rate_limiter.record(user4.user_id, "sms")
    print("  (SMS 발송 한도 3건 선소진 처리)")

    factories["ORDER_CONFIRMED"].notify(NotificationEvent(
        event_type="ORDER_CONFIRMED",
        user=user4,
        context={"order_id": "ORD-9004", "item_name": "Magic Keyboard"},
    ))

    # ── 시나리오 5: 마케팅 수신 미동의 → 전체 건너뜀 ───────────────────────
    divider("시나리오 5: 마케팅 프로모션 — 수신 미동의 → 발송 안 함")
    user5 = make_user(
        1005,
        email="eve@example.com",
        phone="010-7777-8888",
        kakao_id="kakao_eve",
        opted_in_channels=["email", "kakao"],
        marketing_consent=False,    # 마케팅 미동의
    )
    factories["PROMOTION"].notify(NotificationEvent(
        event_type="PROMOTION",
        user=user5,
        context={"promo_title": "봄맞이 특가", "promo_detail": "전 품목 20% 할인"},
        is_marketing=True,
    ))

    # ── 시나리오 6: 배송 시작 → Push 정상 발송 ──────────────────────────────
    divider("시나리오 6: 배송 시작 알림 → Push")
    factories["SHIPPING_STARTED"].notify(NotificationEvent(
        event_type="SHIPPING_STARTED",
        user=user1,
        context={"order_id": "ORD-9001", "tracking_number": "1234567890"},
    ))

    # ── 발송 로그 전체 요약 ────────────────────────────────────────────────
    divider("발송 로그 요약")
    for log in logger.get_logs():
        status = "성공" if log["success"] else "실패"
        err = f" ({log['error']})" if log["error"] else ""
        print(f"  user={log['user_id']} | {log['event_type']:<20} | {log['channel']:<6} | {status}{err}")


if __name__ == "__main__":
    main()
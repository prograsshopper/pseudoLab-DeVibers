from email_factory import EmailNotificationFactory
from kakao_factory import KakaoNotificationFactory
from sms_factory import SMSNotificationFactory

ORDER_ID  = "ORD-001"
ITEM_NAME = "MacBook Pro 14"

# 채널마다 ConcreteFactory를 교체하는 것만으로 발송 채널이 바뀐다.
# notify() 내부 로직은 전혀 변경되지 않는다.

factories = [
    EmailNotificationFactory(),
    SMSNotificationFactory(),
    KakaoNotificationFactory(),
]

for factory in factories:
    factory.notify(
        to=f"user_{factory.__class__.__name__}",
        order_id=ORDER_ID,
        item_name=ITEM_NAME,
    )
    print()

# ── OCP 확인: Push 채널 추가 ────────────────────────────────
# push_notifier.py + push_factory.py 파일만 추가하면 된다.
# 이 아래 코드 외에 기존 파일은 한 줄도 수정하지 않는다.

print("── Push 채널 추가 (기존 코드 수정 없음) ──")

from push_notifier import PushNotifier        # noqa: E402
from factory import NotificationFactory       # noqa: E402
from notifier import Notifier                 # noqa: E402

class PushNotificationFactory(NotificationFactory):
    def create_notifier(self) -> Notifier:
        return PushNotifier()

PushNotificationFactory().notify("device_token_xyz", ORDER_ID, ITEM_NAME)

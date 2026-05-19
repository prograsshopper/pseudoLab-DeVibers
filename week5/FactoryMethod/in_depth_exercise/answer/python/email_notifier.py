from models import NotificationResult, UserPreference
from notifier import Notifier

_TEMPLATES: dict[str, str] = {
    "ORDER_CONFIRMED":    "<h1>주문이 확인되었습니다</h1><p>주문번호: {order_id} | 상품: {item_name}</p>",
    "SHIPPING_STARTED":   "<h1>배송이 시작되었습니다</h1><p>주문번호: {order_id} | 송장번호: {tracking_number}</p>",
    "SHIPPING_COMPLETED": "<h1>배송이 완료되었습니다</h1><p>주문번호: {order_id}</p>",
    "RESTOCK_ALERT":      "<h1>재입고 알림</h1><p>{item_name}이(가) 재입고되었습니다.</p>",
    "PROMOTION":          "<h1>특별 프로모션</h1><p>{promo_title}: {promo_detail}</p>",
}


class EmailNotifier(Notifier):
    @property
    def channel_name(self) -> str:
        return "email"

    def validate(self, recipient: UserPreference) -> bool:
        return bool(recipient.email and "@" in recipient.email)

    def format_message(self, event_type: str, context: dict) -> str:
        template = _TEMPLATES.get(event_type, "<p>{message}</p>")
        try:
            return template.format(**context)
        except KeyError:
            return template

    def send(self, recipient: UserPreference, message: str) -> NotificationResult:
        # 실제 환경: AWS SES / SMTP 클라이언트 호출
        print(f"    [EMAIL] → {recipient.email}")
        print(f"             {message[:80]}...")
        return NotificationResult(success=True, channel=self.channel_name)
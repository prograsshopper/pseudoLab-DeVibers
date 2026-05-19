from models import NotificationResult, UserPreference
from notifier import Notifier

_MAX_BYTES = 90

_TEMPLATES: dict[str, str] = {
    "ORDER_CONFIRMED":    "[ShopNow] 주문({order_id}) 결제완료. {item_name}",
    "SHIPPING_STARTED":   "[ShopNow] 주문({order_id}) 배송출발. 송장:{tracking_number}",
    "SHIPPING_COMPLETED": "[ShopNow] 주문({order_id}) 배송완료.",
    "RESTOCK_ALERT":      "[ShopNow] {item_name} 재입고!",
    "PROMOTION":          "[ShopNow] {promo_title} - {promo_detail}",
}


class SMSNotifier(Notifier):
    @property
    def channel_name(self) -> str:
        return "sms"

    def validate(self, recipient: UserPreference) -> bool:
        return bool(recipient.phone and recipient.phone.replace("-", "").startswith("010"))

    def format_message(self, event_type: str, context: dict) -> str:
        template = _TEMPLATES.get(event_type, "{message}")
        try:
            message = template.format(**context)
        except KeyError:
            message = template

        # 90바이트 초과 시 절삭
        encoded = message.encode("utf-8")
        if len(encoded) > _MAX_BYTES:
            message = encoded[:_MAX_BYTES].decode("utf-8", errors="ignore") + "..."
        return message

    def send(self, recipient: UserPreference, message: str) -> NotificationResult:
        # 실제 환경: 네이버 클라우드 SMS / Twilio API 호출
        print(f"    [SMS]   → {recipient.phone}")
        print(f"             {message}")
        return NotificationResult(success=True, channel=self.channel_name)
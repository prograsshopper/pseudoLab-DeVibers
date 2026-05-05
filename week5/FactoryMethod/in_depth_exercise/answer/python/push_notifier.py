from models import NotificationResult, UserPreference
from notifier import Notifier

# (제목 템플릿, 본문 템플릿)
_TEMPLATES: dict[str, tuple[str, str]] = {
    "ORDER_CONFIRMED":    ("주문 완료 ✓",   "{item_name} 주문이 확인되었습니다."),
    "SHIPPING_STARTED":   ("배송 출발 🚚",  "주문({order_id}) 배송이 출발했어요!"),
    "SHIPPING_COMPLETED": ("배송 완료 📦",  "주문({order_id})이 도착했습니다."),
    "RESTOCK_ALERT":      ("재입고 알림 🔔", "{item_name}이(가) 돌아왔어요!"),
    "PROMOTION":          ("특별 혜택 🎁",  "{promo_title}"),
}


class PushNotifier(Notifier):
    @property
    def channel_name(self) -> str:
        return "push"

    def validate(self, recipient: UserPreference) -> bool:
        # 기기 토큰이 없거나 만료된 경우 발송 불가
        return bool(recipient.device_token)

    def format_message(self, event_type: str, context: dict) -> str:
        title_tpl, body_tpl = _TEMPLATES.get(event_type, ("알림", "{message}"))
        try:
            title = title_tpl.format(**context)
            body = body_tpl.format(**context)
        except KeyError:
            title, body = title_tpl, body_tpl
        return f"title={title!r} | body={body!r}"

    def send(self, recipient: UserPreference, message: str) -> NotificationResult:
        # 실제 환경: FCM(Android) / APNs(iOS) 호출
        token_preview = recipient.device_token[:16] + "..."
        print(f"    [PUSH]  → token={token_preview}")
        print(f"             {message}")
        return NotificationResult(success=True, channel=self.channel_name)
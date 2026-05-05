from models import NotificationResult, UserPreference
from notifier import Notifier

# 카카오 알림톡은 사전 승인된 템플릿 코드를 사용한다.
# 실제 환경에서는 카카오 비즈니스 채널에서 템플릿을 등록하고 심사를 받아야 한다.
_TEMPLATE_CODES: dict[str, str] = {
    "ORDER_CONFIRMED":    "ORDER_01",
    "SHIPPING_STARTED":   "SHIP_01",
    "SHIPPING_COMPLETED": "SHIP_02",
    "RESTOCK_ALERT":      "RESTOCK_01",
    "PROMOTION":          "PROMO_01",
}


class KakaoNotifier(Notifier):
    @property
    def channel_name(self) -> str:
        return "kakao"

    def validate(self, recipient: UserPreference) -> bool:
        # 카카오 채널 친구 추가 사용자에게만 발송 가능
        return bool(recipient.kakao_id)

    def format_message(self, event_type: str, context: dict) -> str:
        template_code = _TEMPLATE_CODES.get(event_type, "DEFAULT_01")
        variables = ", ".join(f"{k}={v}" for k, v in context.items())
        # 실제 환경: {"template_code": ..., "template_args": context} 형태로 API 호출
        return f"template_code={template_code} | params=[{variables}]"

    def send(self, recipient: UserPreference, message: str) -> NotificationResult:
        # 실제 환경: 카카오 비즈메시지 API 호출
        print(f"    [KAKAO] → {recipient.kakao_id}")
        print(f"             {message}")
        return NotificationResult(success=True, channel=self.channel_name)
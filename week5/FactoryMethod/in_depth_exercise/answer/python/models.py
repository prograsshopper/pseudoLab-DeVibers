from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserPreference:
    user_id: int
    email: str | None
    phone: str | None
    kakao_id: str | None
    device_token: str | None
    opted_in_channels: list[str]   # 수신 동의 채널 목록 ["email", "sms", "kakao", "push"]
    marketing_consent: bool = False


@dataclass
class NotificationEvent:
    event_type: str                # "ORDER_CONFIRMED", "SHIPPING_STARTED", ...
    user: UserPreference
    context: dict[str, Any]        # 메시지 템플릿에 바인딩할 변수
    is_marketing: bool = False


@dataclass
class NotificationResult:
    success: bool
    channel: str
    sent_at: datetime = field(default_factory=datetime.now)
    error_message: str | None = None
from abc import ABC, abstractmethod

from models import NotificationResult, UserPreference


class Notifier(ABC):
    """
    Product (인터페이스)
    모든 알림 채널이 구현해야 하는 공통 인터페이스.
    Creator(NotificationFactory)는 이 타입에만 의존하므로
    구체적인 채널 클래스가 추가되어도 Creator 코드는 변경되지 않는다.
    """

    @property
    @abstractmethod
    def channel_name(self) -> str:
        """채널 식별자 (e.g. "email", "sms", "kakao", "push")"""
        ...

    @abstractmethod
    def validate(self, recipient: UserPreference) -> bool:
        """수신자 정보가 발송 가능한 상태인지 확인"""
        ...

    @abstractmethod
    def format_message(self, event_type: str, context: dict) -> str:
        """채널에 맞는 포맷으로 메시지 변환"""
        ...

    @abstractmethod
    def send(self, recipient: UserPreference, message: str) -> NotificationResult:
        """실제 발송 처리 (외부 API 호출 등)"""
        ...
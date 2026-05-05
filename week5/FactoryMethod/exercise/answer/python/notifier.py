from abc import ABC, abstractmethod


class Notifier(ABC):
    """Product (인터페이스) — 모든 채널이 구현해야 하는 공통 계약"""

    @abstractmethod
    def format_message(self, order_id: str, item_name: str) -> str:
        ...

    @abstractmethod
    def send(self, to: str, message: str) -> None:
        ...

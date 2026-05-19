from abc import ABC, abstractmethod

from notifier import Notifier


class NotificationFactory(ABC):
    """
    Creator (추상 클래스)

    create_notifier() : 팩토리 메서드 — 서브클래스가 구현
    notify()          : 비즈니스 로직 — create_notifier()를 사용하지만
                        반환된 것이 Email인지 SMS인지 알지 못한다.
    """

    @abstractmethod
    def create_notifier(self) -> Notifier:
        ...

    def notify(self, to: str, order_id: str, item_name: str) -> None:
        notifier = self.create_notifier()               # 팩토리 메서드 호출
        message  = notifier.format_message(order_id, item_name)
        notifier.send(to, message)

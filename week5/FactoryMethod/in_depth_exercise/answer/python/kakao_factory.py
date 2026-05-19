from factory import NotificationFactory
from kakao_notifier import KakaoNotifier
from notifier import Notifier


class KakaoNotificationFactory(NotificationFactory):
    def create_notifier(self) -> Notifier:
        return KakaoNotifier()
from factory import NotificationFactory
from notifier import Notifier
from push_notifier import PushNotifier


class PushNotificationFactory(NotificationFactory):
    def create_notifier(self) -> Notifier:
        return PushNotifier()
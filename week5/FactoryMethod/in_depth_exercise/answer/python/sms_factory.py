from factory import NotificationFactory
from notifier import Notifier
from sms_notifier import SMSNotifier


class SMSNotificationFactory(NotificationFactory):
    def create_notifier(self) -> Notifier:
        return SMSNotifier()
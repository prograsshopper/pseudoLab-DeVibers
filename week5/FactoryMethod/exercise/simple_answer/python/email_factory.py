from email_notifier import EmailNotifier
from factory import NotificationFactory
from notifier import Notifier


class EmailNotificationFactory(NotificationFactory):
    def create_notifier(self) -> Notifier:
        return EmailNotifier()

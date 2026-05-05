from models import NotificationEvent, NotificationResult


class NotificationLogger:
    def __init__(self) -> None:
        self._logs: list[dict] = []

    def log(self, event: NotificationEvent, result: NotificationResult) -> None:
        entry = {
            "user_id":    event.user.user_id,
            "event_type": event.event_type,
            "channel":    result.channel,
            "success":    result.success,
            "sent_at":    result.sent_at.isoformat(),
            "error":      result.error_message,
        }
        self._logs.append(entry)

        icon = "✓" if result.success else "✗"
        err = f" | error={result.error_message}" if result.error_message else ""
        print(f"    [LOG {icon}] user={event.user.user_id} | {event.event_type} | {result.channel}{err}")

    def get_logs(self) -> list[dict]:
        return list(self._logs)
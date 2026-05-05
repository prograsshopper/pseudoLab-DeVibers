from notifier import Notifier


class PushNotifier(Notifier):
    def format_message(self, order_id: str, item_name: str) -> str:
        return f"title='주문 완료' | body='주문({order_id}) {item_name}'"

    def send(self, to: str, message: str) -> None:
        print(f"[PUSH]  → token={to}")
        print(f"         {message}")

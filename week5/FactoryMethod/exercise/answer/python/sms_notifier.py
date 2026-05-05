from notifier import Notifier


class SMSNotifier(Notifier):
    def format_message(self, order_id: str, item_name: str) -> str:
        return f"[ShopNow] 주문({order_id}) 완료. {item_name}"

    def send(self, to: str, message: str) -> None:
        print(f"[SMS]   → {to}")
        print(f"         {message}")

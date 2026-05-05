from notifier import Notifier


class EmailNotifier(Notifier):
    def format_message(self, order_id: str, item_name: str) -> str:
        return f"[주문 완료] 주문번호: {order_id} | 상품: {item_name}"

    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] → {to}")
        print(f"         {message}")

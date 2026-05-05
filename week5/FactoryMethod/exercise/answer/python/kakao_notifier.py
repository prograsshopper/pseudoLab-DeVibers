from notifier import Notifier


class KakaoNotifier(Notifier):
    def format_message(self, order_id: str, item_name: str) -> str:
        return f"template=ORDER_01 | order_id={order_id}, item={item_name}"

    def send(self, to: str, message: str) -> None:
        print(f"[KAKAO] → {to}")
        print(f"         {message}")

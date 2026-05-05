from collections import defaultdict
from datetime import datetime, timedelta

# 채널별 발송 제한 정책: {channel: (최대 건수, 윈도우 초)}
_LIMITS: dict[str, tuple[int, int]] = {
    "sms":  (3, 60),      # 1분에 최대 3건
    "push": (10, 3600),   # 1시간에 최대 10건
}


class RateLimiter:
    def __init__(self) -> None:
        # {(user_id, channel): [발송 시각, ...]}
        self._history: dict[tuple[int, str], list[datetime]] = defaultdict(list)

    def is_allowed(self, user_id: int, channel: str) -> bool:
        if channel not in _LIMITS:
            return True

        max_count, window_sec = _LIMITS[channel]
        key = (user_id, channel)
        cutoff = datetime.now() - timedelta(seconds=window_sec)

        # 윈도우 밖의 기록 제거
        self._history[key] = [t for t in self._history[key] if t > cutoff]
        return len(self._history[key]) < max_count

    def record(self, user_id: int, channel: str) -> None:
        if channel in _LIMITS:
            self._history[(user_id, channel)].append(datetime.now())
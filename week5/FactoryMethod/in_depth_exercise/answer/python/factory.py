from __future__ import annotations

from abc import ABC, abstractmethod

from models import NotificationEvent, NotificationResult
from notification_logger import NotificationLogger
from notifier import Notifier
from rate_limiter import RateLimiter


class NotificationFactory(ABC):
    """
    Creator (추상 클래스) — Factory Method 패턴의 핵심
    ─────────────────────────────────────────────────────────────────────
    ★ create_notifier() : 팩토리 메서드 (서브클래스에서 반드시 구현)
    ★ notify()          : 비즈니스 로직 (공통 템플릿, 여기서 팩토리 메서드를 사용)

    주의: Creator의 주 책임은 Notifier를 '생성'하는 것이 아니라
         '알림 발송'이라는 비즈니스 로직을 실행하는 것이다.
         팩토리 메서드는 그 로직을 구상 Notifier 클래스로부터 분리하는 수단일 뿐이다.

    폴백 체인: EmailFactory → (없음)
               SMSFactory  → fallback=EmailFactory
               KakaoFactory→ fallback=SMSFactory
               PushFactory → fallback=KakaoFactory
    """

    def __init__(
        self,
        rate_limiter: RateLimiter,
        logger: NotificationLogger,
        fallback: NotificationFactory | None = None,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._logger = logger
        self._fallback = fallback

    # ── 팩토리 메서드 ────────────────────────────────────────────────
    @abstractmethod
    def create_notifier(self) -> Notifier:
        """서브클래스가 생성할 구체적인 Notifier를 결정한다."""
        ...

    # ── 핵심 비즈니스 로직 ───────────────────────────────────────────
    def notify(self, event: NotificationEvent) -> bool:
        """
        알림 발송 공통 템플릿:
        수신 동의 확인 → Rate Limit → 유효성 검사 → 포맷팅 → 발송 → 로깅
        실패 시 폴백 채널로 자동 전환.
        """
        notifier = self.create_notifier()   # ← 팩토리 메서드 호출
        channel = notifier.channel_name
        user = event.user

        # 1. 마케팅 수신 동의 확인
        if event.is_marketing and not user.marketing_consent:
            print(f"  [SKIP] {channel} — 마케팅 수신 미동의")
            return self._try_fallback(event)

        # 2. 채널별 수신 설정(opt-in) 확인
        if channel not in user.opted_in_channels:
            print(f"  [SKIP] {channel} — 수신 거부")
            return self._try_fallback(event)

        # 3. Rate Limit 확인
        if not self._rate_limiter.is_allowed(user.user_id, channel):
            print(f"  [RATE LIMIT] {channel} — 발송 한도 초과")
            return self._try_fallback(event)

        # 4. 수신자 유효성 확인 (이메일 형식, 전화번호 등)
        if not notifier.validate(user):
            result = NotificationResult(
                success=False,
                channel=channel,
                error_message="수신자 정보 유효하지 않음",
            )
            self._logger.log(event, result)
            return self._try_fallback(event)

        # 5. 채널에 맞는 메시지 포맷팅
        message = notifier.format_message(event.event_type, event.context)

        # 6. 발송
        try:
            result = notifier.send(user, message)
            if result.success:
                self._rate_limiter.record(user.user_id, channel)
        except Exception as exc:
            result = NotificationResult(
                success=False,
                channel=channel,
                error_message=str(exc),
            )

        # 7. 발송 결과 로깅
        self._logger.log(event, result)

        if not result.success:
            return self._try_fallback(event)

        return True

    def _try_fallback(self, event: NotificationEvent) -> bool:
        if self._fallback:
            fallback_channel = self._fallback.create_notifier().channel_name
            print(f"  ↳ [FALLBACK] → {fallback_channel}")
            return self._fallback.notify(event)
        print(f"  [FAILED] user={event.user.user_id} — 모든 채널 실패")
        return False
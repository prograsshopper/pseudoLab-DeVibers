# ============================================================
# CREATOR (추상 클래스) — Factory Method 패턴의 핵심
# ─────────────────────────────────────────────────────────────
#
#  ★ create_notifier()  : 팩토리 메서드 (ABSTRACT)
#                         서브클래스가 어떤 Notifier를 만들지 결정한다.
#
#  ★ notify()           : 비즈니스 로직 (CONCRETE, 공통)
#                         create_notifier()를 호출하지만,
#                         반환된 것이 Email인지 SMS인지 알지 못한다.
#                         오직 Notifier 인터페이스를 통해서만 사용한다.
#
#  핵심 원칙:
#  Creator의 주 책임은 Notifier를 '생성'하는 것이 아니라
#  '알림 발송'이라는 비즈니스 로직을 실행하는 것이다.
#  팩토리 메서드는 그 로직을 구상 클래스와 분리하는 수단일 뿐이다.
# ============================================================

ABSTRACT CLASS NotificationFactory:

    CONSTRUCTOR(rate_limiter, logger, fallback=NULL):
        self.rate_limiter = rate_limiter
        self.logger       = logger
        self.fallback     = fallback    # 실패 시 시도할 다음 채널의 Factory

    # ── 팩토리 메서드 ─────────────────────────────────────────
    ABSTRACT METHOD create_notifier() -> Notifier:
        # 서브클래스(ConcreteCreator)에서 구현.
        # 어떤 Notifier 인스턴스를 반환할지는 서브클래스만 안다.
        MUST BE OVERRIDDEN

    # ── 핵심 비즈니스 로직 ────────────────────────────────────
    METHOD notify(event: NotificationEvent) -> 불리언:

        notifier = self.create_notifier()   # ← 팩토리 메서드 호출
                                            #   반환 타입은 Notifier 인터페이스.
                                            #   구체적으로 Email인지 SMS인지 모른다.
        channel  = notifier.channel_name
        user     = event.user

        # STEP 1. 마케팅 수신 동의 확인
        IF event.is_marketing AND NOT user.marketing_consent THEN
            SKIP "마케팅 수신 미동의"
            RETURN self._try_fallback(event)

        # STEP 2. 채널별 수신 설정(opt-in) 확인
        IF channel NOT IN user.opted_in_channels THEN
            SKIP "수신 거부"
            RETURN self._try_fallback(event)

        # STEP 3. Rate Limit 확인
        IF self.rate_limiter.is_allowed(user.user_id, channel) == False THEN
            SKIP "발송 한도 초과"
            RETURN self._try_fallback(event)

        # STEP 4. 수신자 유효성 확인 (이메일 형식, 전화번호 등)
        IF notifier.validate(user) == False THEN
            result = NotificationResult(success=False, error="수신자 정보 유효하지 않음")
            self.logger.log(event, result)
            RETURN self._try_fallback(event)

        # STEP 5. 채널에 맞는 메시지 포맷팅
        message = notifier.format_message(event.event_type, event.context)

        # STEP 6. 발송
        TRY:
            result = notifier.send(user, message)
            IF result.success THEN
                self.rate_limiter.record(user.user_id, channel)
        CATCH exception:
            result = NotificationResult(success=False, error=exception.message)

        # STEP 7. 결과 로깅
        self.logger.log(event, result)

        IF NOT result.success THEN
            RETURN self._try_fallback(event)

        RETURN True

    # ── 폴백 처리 ─────────────────────────────────────────────
    METHOD _try_fallback(event) -> 불리언:
        IF self.fallback 존재 THEN
            LOG "다음 채널로 재시도"
            RETURN self.fallback.notify(event)  # 폴백 Factory의 notify() 호출
        ELSE
            LOG "모든 채널 실패"
            RETURN False

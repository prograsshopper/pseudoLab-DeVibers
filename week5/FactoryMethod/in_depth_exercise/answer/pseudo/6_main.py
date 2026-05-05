# ============================================================
# MAIN — 폴백 체인 조립 및 시나리오 실행
# ─────────────────────────────────────────────────────────────
# 클라이언트 코드(main)는 ConcreteCreator 이름만 알면 된다.
# 각 Factory 내부에서 어떤 Notifier를 쓰는지는 알 필요가 없다.
# ============================================================

# ── 공유 인프라 초기화 ────────────────────────────────────────
rate_limiter = new RateLimiter()
logger       = new NotificationLogger()


# ── 폴백 체인 조립 ────────────────────────────────────────────
#
# 체인 구조 (오른쪽이 폴백):
#   Push → Kakao → SMS → Email → (실패)
#
# 생성자에 fallback을 주입함으로써 체인을 구성한다.
# 각 Factory는 자신의 다음 채널이 무엇인지 신경 쓰지 않는다.

email = new EmailNotificationFactory(rate_limiter, logger, fallback=NULL)
sms   = new SMSNotificationFactory  (rate_limiter, logger, fallback=email)
kakao = new KakaoNotificationFactory(rate_limiter, logger, fallback=sms)
push  = new PushNotificationFactory (rate_limiter, logger, fallback=kakao)


# ── 이벤트 유형별 진입 팩토리 매핑 ───────────────────────────
factories = {
    "ORDER_CONFIRMED"   : kakao,    # Kakao → SMS → Email
    "SHIPPING_STARTED"  : push,     # Push  → Kakao → SMS → Email
    "SHIPPING_COMPLETED": push,
    "RESTOCK_ALERT"     : email,
    "PROMOTION"         : new EmailNotificationFactory(rate_limiter, logger),  # 폴백 없음
}


# ============================================================
# 시나리오 실행
# ============================================================

# ── 시나리오 1: 정상 발송 ─────────────────────────────────────
#
# 흐름: Kakao Factory
#       → create_notifier() → KakaoNotifier 생성
#       → validate() 통과 (kakao_id 존재)
#       → format_message() → 템플릿 코드 페이로드
#       → send() → 카카오 API 호출
#       → 로그: 성공

user1  = UserPreference(kakao_id="kakao_alice", opted_in=["kakao", "sms", "email"])
event1 = NotificationEvent("ORDER_CONFIRMED", user1, {order_id, item_name})

factories["ORDER_CONFIRMED"].notify(event1)


# ── 시나리오 2: 채널 미연동 → 폴백 ───────────────────────────
#
# 흐름: Kakao Factory
#       → create_notifier() → KakaoNotifier
#       → validate() 실패 (kakao_id = NULL)
#       → _try_fallback() → SMS Factory로 위임
#       → SMSNotifier.send() 성공

user2  = UserPreference(kakao_id=NULL, phone="010-...", opted_in=["sms", "kakao"])
event2 = NotificationEvent("ORDER_CONFIRMED", user2, {order_id, item_name})

factories["ORDER_CONFIRMED"].notify(event2)


# ── 시나리오 3: 수신 거부(opt-out) → 폴백 ────────────────────
#
# 흐름: Kakao Factory
#       → channel "kakao" NOT IN user.opted_in_channels
#       → _try_fallback() → SMS Factory로 위임
#       → SMSNotifier.send() 성공

user3  = UserPreference(kakao_id="kakao_carol", opted_in=["email", "sms"])  # kakao opt-out
event3 = NotificationEvent("ORDER_CONFIRMED", user3, {order_id, item_name})

factories["ORDER_CONFIRMED"].notify(event3)


# ── 시나리오 4: Rate Limit 초과 → 폴백 연쇄 ─────────────────
#
# 흐름: Kakao Factory → opt-out → SMS Factory
#       → rate_limiter.is_allowed("sms") == False (한도 초과)
#       → _try_fallback() → Email Factory로 위임
#       → EmailNotifier.send() 성공

rate_limiter.미리_3건_소진(user4.user_id, "sms")
user4  = UserPreference(kakao_id=NULL, opted_in=["email", "sms"])
event4 = NotificationEvent("ORDER_CONFIRMED", user4, {order_id, item_name})

factories["ORDER_CONFIRMED"].notify(event4)


# ── 시나리오 5: 마케팅 수신 미동의 → 전체 중단 ───────────────
#
# 흐름: Email Factory
#       → event.is_marketing == True AND user.marketing_consent == False
#       → SKIP, _try_fallback() → fallback == NULL → FAILED

user5  = UserPreference(marketing_consent=False, opted_in=["email"])
event5 = NotificationEvent("PROMOTION", user5, {promo_title, promo_detail}, is_marketing=True)

factories["PROMOTION"].notify(event5)


# ── 시나리오 6: OCP 검증 — 새 채널 추가 ─────────────────────
#
# SlackNotifier + SlackNotificationFactory를 추가해도
# factories["ORDER_CONFIRMED"].notify() 코드는 한 줄도 변경되지 않는다.
# ConcreteFactory를 교체하는 것만으로 충분하다.

slack = new SlackNotificationFactory(rate_limiter, logger, fallback=email)
factories["ORDER_CONFIRMED"] = new KakaoNotificationFactory(
    rate_limiter, logger, fallback=slack  # 폴백 체인에 Slack 삽입
)

# Python으로 구현하는 커맨드 패턴

## 2. 구성 요소 (Python 관점)

| 역할 | Python 구현 | 설명 |
|------|-------------|------|
| Command Interface | `ABC` + `@abstractmethod` | 모든 커맨드가 상속해야 하는 추상 클래스 |
| ConcreteCommand | `Command`를 상속한 클래스 | `execute()`, `undo()` 구현체 |
| Receiver | 일반 클래스 | 실제 작업 로직 보유 |
| Invoker | 일반 클래스 | 커맨드를 저장하고 실행 요청 |
| Client | `if __name__ == "__main__"` | 객체 조립 및 의존성 주입 |

---

## 3. 예시: 스마트홈 리모컨

> 리모컨(Invoker)이 전등(Receiver)을 직접 제어하지 않고,
> 커맨드 객체를 통해 간접 제어하는 예시. Undo도 지원한다.

```python
from abc import ABC, abstractmethod
from typing import List


# ── Command Interface ──────────────────────────────────────────
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


# ── Receiver ───────────────────────────────────────────────────
class Light:
    def __init__(self, location: str):
        self.location = location
        self.is_on = False

    def turn_on(self):
        self.is_on = True
        print(f"[{self.location}] 전등 켜짐")

    def turn_off(self):
        self.is_on = False
        print(f"[{self.location}] 전등 꺼짐")


class Fan:
    def __init__(self, location: str):
        self.location = location
        self.speed = 0  # 0=off, 1=low, 2=high

    def set_speed(self, speed: int):
        self.speed = speed
        label = {0: "꺼짐", 1: "약풍", 2: "강풍"}
        print(f"[{self.location}] 선풍기 {label[speed]}")


# ── ConcreteCommand ────────────────────────────────────────────
class LightOnCommand(Command):
    def __init__(self, light: Light):
        self._light = light

    def execute(self):
        self._light.turn_on()

    def undo(self):
        self._light.turn_off()


class LightOffCommand(Command):
    def __init__(self, light: Light):
        self._light = light

    def execute(self):
        self._light.turn_off()

    def undo(self):
        self._light.turn_on()


class FanSpeedCommand(Command):
    def __init__(self, fan: Fan, speed: int):
        self._fan = fan
        self._speed = speed
        self._prev_speed = 0  # undo를 위해 이전 상태 저장

    def execute(self):
        self._prev_speed = self._fan.speed
        self._fan.set_speed(self._speed)

    def undo(self):
        self._fan.set_speed(self._prev_speed)


# ── Null Object: NoCommand ─────────────────────────────────────
class NoCommand(Command):
    """슬롯에 커맨드가 없을 때 사용하는 기본 커맨드 (null 체크 불필요)"""
    def execute(self):
        pass

    def undo(self):
        pass


# ── Invoker ────────────────────────────────────────────────────
class RemoteControl:
    def __init__(self, slots: int = 3):
        self._on_commands: List[Command] = [NoCommand()] * slots
        self._off_commands: List[Command] = [NoCommand()] * slots
        self._last_command: Command = NoCommand()

    def set_command(self, slot: int, on_cmd: Command, off_cmd: Command):
        self._on_commands[slot] = on_cmd
        self._off_commands[slot] = off_cmd

    def press_on(self, slot: int):
        self._on_commands[slot].execute()
        self._last_command = self._on_commands[slot]

    def press_off(self, slot: int):
        self._off_commands[slot].execute()
        self._last_command = self._off_commands[slot]

    def press_undo(self):
        print("[UNDO]", end=" ")
        self._last_command.undo()


# ── Client ─────────────────────────────────────────────────────
if __name__ == "__main__":
    remote = RemoteControl(slots=3)

    living_light = Light("거실")
    bedroom_light = Light("침실")
    living_fan = Fan("거실")

    # 슬롯에 커맨드 등록
    remote.set_command(0, LightOnCommand(living_light),  LightOffCommand(living_light))
    remote.set_command(1, LightOnCommand(bedroom_light), LightOffCommand(bedroom_light))
    remote.set_command(2, FanSpeedCommand(living_fan, speed=2), FanSpeedCommand(living_fan, speed=0))

    print("=== 리모컨 조작 ===")
    remote.press_on(0)   # 거실 전등 켜짐
    remote.press_on(1)   # 침실 전등 켜짐
    remote.press_on(2)   # 거실 선풍기 강풍
    remote.press_off(1)  # 침실 전등 꺼짐

    print("\n=== Undo ===")
    remote.press_undo()  # 침실 전등 켜짐 (마지막 off 취소)
    remote.press_undo()  # (undo의 undo는 없으므로 동일 동작)
```

### 실행 결과
```
=== 리모컨 조작 ===
[거실] 전등 켜짐
[침실] 전등 켜짐
[거실] 선풍기 강풍
[침실] 전등 꺼짐

=== Undo ===
[UNDO] [침실] 전등 켜짐
[UNDO] [침실] 전등 꺼짐
```

---

## 4. 핵심 포인트 정리

| 포인트 | 설명 |
|--------|------|
| **분리** | `RemoteControl`은 `Light`, `Fan`을 전혀 모름. 오직 `Command.execute()`만 호출 |
| **Undo** | `FanSpeedCommand`처럼 이전 상태를 필드에 저장해두면 쉽게 구현 가능 |
| **NoCommand** | 빈 슬롯에 `None` 대신 사용 → `if command is not None` 체크 코드 제거 |
| **확장** | 새 기기(TV, 에어컨)를 추가해도 `RemoteControl` 코드는 수정하지 않아도 됨 (OCP) |

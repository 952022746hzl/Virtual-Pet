"""行为状态机。纯逻辑，不依赖 Qt / win32；随机源可注入以便测试。"""
import enum
import random

SLEEP_AFTER = 120.0  # 秒，无互动后入睡


class State(enum.Enum):
    IDLE = "idle"
    WALK = "walk"
    DRAGGED = "dragged"
    FALL = "fall"
    LAND = "land"
    SLEEP = "sleep"
    BOW = "bow"
    COFFEE = "coffee"
    SPECIAL = "special"
    CHASE = "chase"


ONESHOT = {State.BOW: 1.5, State.LAND: 1.2, State.SPECIAL: 2.5}


class PetBrain:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.state = State.IDLE
        self.facing = 1                # 1 右 / -1 左
        self.chase_enabled = False
        self._idle_clock = 0.0         # 距上次互动秒数
        self._state_clock = 0.0
        self._next_decision = self._roll_gap()
        self._events = []

    # ---- 内部 ----
    def _roll_gap(self):
        return self.rng.uniform(2.0, 5.0)

    def _enter(self, state):
        self.state = state
        self._state_clock = 0.0

    def _emit(self, kind, payload):
        self._events.append((kind, payload))

    def _touch(self):
        self._idle_clock = 0.0

    # ---- 主循环 ----
    def update(self, dt):
        self._state_clock += dt
        if self.state in (State.IDLE, State.WALK):
            self._idle_clock += dt
            if self._idle_clock >= SLEEP_AFTER:
                self._enter(State.SLEEP)
                return
            self._next_decision -= dt
            if self._next_decision <= 0:
                self._next_decision = self._roll_gap()
                if self.rng.random() < 0.5:
                    self._enter(State.WALK if self.state is State.IDLE else State.IDLE)
                if self.rng.random() < 0.3:
                    self.facing = -self.facing
        elif self.state in ONESHOT and self._state_clock >= ONESHOT[self.state]:
            self._enter(State.IDLE)

    def pop_events(self):
        events, self._events = self._events, []
        return events

    # ---- 用户互动 ----
    def on_click(self):
        self._touch()
        if self.state is State.SLEEP:
            self._enter(State.IDLE)
            self._emit("say", "wake")
        elif self.state in (State.IDLE, State.WALK, State.CHASE):
            self._enter(State.BOW)
            self._emit("say", "click")

    def on_drag_start(self):
        self._touch()
        self._enter(State.DRAGGED)

    def on_drag_end(self):
        self._touch()
        self._enter(State.FALL)

    # ---- 物理回调 ----
    def on_ground_lost(self):
        if self.state is not State.DRAGGED:
            self._enter(State.FALL)

    def on_land(self, hard):
        if hard:
            self._enter(State.LAND)
            self._emit("say", "land_hard")
        else:
            self._enter(State.IDLE)

    # ---- 菜单命令 ----
    def command_coffee(self):
        self._touch()
        self._enter(State.COFFEE)

    def on_coffee_arrived(self):
        self._enter(State.BOW)
        self._emit("say", "coffee")

    def command_special(self, scene):
        self._touch()
        self._enter(State.SPECIAL)
        self._emit("say", scene)

    # ---- 跟随鼠标 ----
    def set_chase(self, enabled):
        self.chase_enabled = enabled
        if not enabled and self.state is State.CHASE:
            self._enter(State.IDLE)

    def set_chasing(self, active):
        """由窗口层根据光标距离调用：进入/退出追逐状态。"""
        if not self.chase_enabled:
            return
        if active and self.state in (State.IDLE, State.WALK):
            self._enter(State.CHASE)
        elif not active and self.state is State.CHASE:
            self._enter(State.IDLE)

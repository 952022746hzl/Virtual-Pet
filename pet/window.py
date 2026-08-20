"""桌宠主窗口：动画渲染、拖拽点击、物理与状态机的接线。"""
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QCursor, QGuiApplication, QPainter, QTransform
from PySide6.QtWidgets import QWidget

from pet.physics import (
    HARD_LANDING_SPEED, Body, Platform, step_fall, supporting_platform,
)
from pet.quotes import pick
from pet.sprite import FPS, FRAME_SIZE
from pet.state_machine import PetBrain, State
from pet.win_platforms import enumerate_platforms

TICK = 0.033
SPEED = {State.WALK: 90.0, State.COFFEE: 140.0, State.CHASE: 220.0}
DRAG_THRESHOLD = 4
PLATFORM_REFRESH = 1.0
CHASE_STOP_DIST = 60
COFFEE_ARRIVE_DIST = 10

# 状态 → 动作素材名（缺项即用 state.value）
ACTION_OVERRIDES = {State.FALL: "dragged", State.CHASE: "walk"}


class PetWindow(QWidget):
    def __init__(self, brain: PetBrain, sprites, quotes, bubble):
        super().__init__()
        self.brain = brain
        self.sprites = sprites
        self.quotes = quotes
        self.bubble = bubble

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(FRAME_SIZE, FRAME_SIZE)

        geo = QGuiApplication.primaryScreen().availableGeometry()
        self.work_area = (geo.left(), geo.top(), geo.right(), geo.bottom())
        self.ground = Platform(left=geo.left(), right=geo.right(), top=geo.bottom())
        self.platforms = [self.ground]
        self._platform_clock = 0.0

        self.x_pos = float(geo.center().x())
        self.y_pos = float(geo.bottom() - FRAME_SIZE)
        self.vy = 0.0
        self._coffee_target_x = None
        self._anim_clock = 0.0
        self._last_state = self.brain.state

        self._dragging = False
        self._press_pos = QPoint()
        self._press_offset = QPoint()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(int(TICK * 1000))
        self._sync_pos()

    # ---- 菜单命令入口（由 main.py 接到托盘） ----
    def command_coffee(self):
        self._coffee_target_x = float(QCursor.pos().x())
        self.brain.command_coffee()

    # ---- 主循环 ----
    def _tick(self):
        state = self.brain.state
        self._refresh_platforms()

        if state in (State.IDLE, State.WALK, State.COFFEE, State.CHASE):
            self._tick_grounded(state)
        elif state is State.FALL:
            self._tick_fall()
        elif state is State.DRAGGED:
            self.vy = 0.0

        self.brain.update(TICK)
        if self.brain.state is not self._last_state:
            self._anim_clock = 0.0
            self._last_state = self.brain.state
        else:
            self._anim_clock += TICK

        for kind, scene in self.brain.pop_events():
            if kind == "say":
                line = pick(self.quotes, scene)
                if line:
                    self.bubble.say(line)

        self._sync_pos()
        self.update()

    def _tick_grounded(self, state):
        body = self._body()
        support = supporting_platform(body, self.platforms)
        if support is None:
            self.vy = 0.0
            self.brain.on_ground_lost()
            return

        if state is State.CHASE or (self.brain.chase_enabled and state in (State.IDLE, State.WALK)):
            dist = QCursor.pos().x() - body.center_x
            self.brain.set_chasing(abs(dist) > CHASE_STOP_DIST)
            state = self.brain.state

        dx = 0.0
        if state is State.WALK:
            dx = SPEED[state] * self.brain.facing * TICK
        elif state is State.CHASE:
            dist = QCursor.pos().x() - body.center_x
            self.brain.facing = 1 if dist > 0 else -1
            dx = SPEED[state] * self.brain.facing * TICK
        elif state is State.COFFEE and self._coffee_target_x is not None:
            dist = self._coffee_target_x - body.center_x
            if abs(dist) < COFFEE_ARRIVE_DIST:
                self._coffee_target_x = None
                self.brain.on_coffee_arrived()
            else:
                self.brain.facing = 1 if dist > 0 else -1
                dx = SPEED[state] * self.brain.facing * TICK

        new_x = self.x_pos + dx
        if new_x + FRAME_SIZE / 2 > support.right or new_x + FRAME_SIZE / 2 < support.left:
            self.brain.facing = -self.brain.facing  # 撞到平台边缘掉头
        else:
            self.x_pos = new_x

    def _tick_fall(self):
        body = self._body()
        landing_vy = body.vy
        after, landed = step_fall(body, self.platforms, TICK)
        self.x_pos, self.y_pos, self.vy = after.x, after.y, after.vy
        if landed:
            self.vy = 0.0
            self.brain.on_land(hard=landing_vy >= HARD_LANDING_SPEED)

    def _refresh_platforms(self):
        self._platform_clock += TICK
        if self._platform_clock >= PLATFORM_REFRESH:
            self._platform_clock = 0.0
            hwnd = int(self.winId())
            wins = enumerate_platforms({hwnd}, self.work_area)
            self.platforms = [self.ground] + wins

    def _body(self):
        return Body(x=self.x_pos, y=self.y_pos, vy=self.vy)

    def _sync_pos(self):
        self.move(int(self.x_pos), int(self.y_pos))
        self.bubble.follow(int(self.x_pos), int(self.y_pos))

    # ---- 渲染 ----
    def paintEvent(self, _event):
        action = ACTION_OVERRIDES.get(self.brain.state, self.brain.state.value)
        frames = self.sprites.frames_for(action)
        frame = frames[int(self._anim_clock * FPS) % len(frames)]
        if self.brain.facing == -1:
            frame = frame.transformed(QTransform().scale(-1, 1))
        p = QPainter(self)
        p.drawPixmap(0, 0, frame)
        p.end()

    # ---- 鼠标 ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._press_offset = self._press_pos - self.pos()
            self._dragging = False

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        pos = event.globalPosition().toPoint()
        if not self._dragging and (pos - self._press_pos).manhattanLength() > DRAG_THRESHOLD:
            self._dragging = True
            self.brain.on_drag_start()
        if self._dragging:
            new_pos = pos - self._press_offset
            self.x_pos, self.y_pos = float(new_pos.x()), float(new_pos.y())
            self._sync_pos()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self._dragging:
            self._dragging = False
            self.vy = 0.0
            self.brain.on_drag_end()
        else:
            self.brain.on_click()

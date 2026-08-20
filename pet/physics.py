"""重力与平台判定。纯逻辑，不依赖 Qt / win32。坐标系：y 向下为正。"""
from dataclasses import dataclass, replace

GRAVITY = 2400.0          # px/s^2
MAX_FALL_SPEED = 1800.0   # px/s
HARD_LANDING_SPEED = 900.0  # 落地瞬间 vy 超过它算"重摔"


@dataclass(frozen=True)
class Platform:
    left: int
    right: int
    top: int


@dataclass(frozen=True)
class Body:
    x: float
    y: float
    vy: float = 0.0
    width: int = 128
    height: int = 128

    @property
    def foot_y(self):
        return self.y + self.height

    @property
    def center_x(self):
        return self.x + self.width / 2


def supporting_platform(body, platforms, tolerance=2.0):
    """返回当前正踩着的平台；悬空返回 None。"""
    for p in platforms:
        if p.left <= body.center_x <= p.right and abs(body.foot_y - p.top) <= tolerance:
            return p
    return None


def step_fall(body, platforms, dt):
    """推进一个下落 tick。返回 (新 Body, 落到的平台或 None)。

    本 tick 内脚底扫过 [foot_y, new_foot] 区间；命中区间内最高的平台则吸附其顶。
    """
    vy = min(body.vy + GRAVITY * dt, MAX_FALL_SPEED)
    new_foot = body.foot_y + vy * dt
    crossed = [
        p for p in platforms
        if p.left <= body.center_x <= p.right and body.foot_y <= p.top <= new_foot
    ]
    if crossed:
        p = min(crossed, key=lambda q: q.top)
        return replace(body, y=p.top - body.height, vy=vy), p
    return replace(body, y=body.y + vy * dt, vy=vy), None

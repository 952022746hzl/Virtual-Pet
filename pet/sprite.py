"""精灵帧发现与加载。discover_frames 为纯函数；SpriteSet 需要 QApplication。"""
import re
from pathlib import Path

ACTIONS = ["idle", "walk", "bow", "sleep", "dragged", "land", "coffee", "special"]
FRAME_SIZE = 128
FPS = 8

_FRAME_RE = re.compile(r"^([a-z_]+?)_(\d+)\.png$")

# 占位图各动作的衣服颜色（深浅区分状态，便于没素材时肉眼调试）
_PLACEHOLDER_TINTS = {
    "idle": "#37474f", "walk": "#455a64", "bow": "#6a1b9a", "sleep": "#263238",
    "dragged": "#b71c1c", "land": "#e65100", "coffee": "#4e342e", "special": "#1b5e20",
}


def discover_frames(directory):
    """扫描目录，返回 {动作名: [按帧号排序的 Path]}。目录不存在返回 {}。"""
    directory = Path(directory)
    if not directory.is_dir():
        return {}
    groups = {}
    for f in directory.iterdir():
        m = _FRAME_RE.match(f.name)
        if m:
            groups.setdefault(m.group(1), []).append((int(m.group(2)), f))
    return {action: [p for _, p in sorted(pairs)] for action, pairs in groups.items()}


class SpriteSet:
    """按动作提供 QPixmap 帧列表；素材缺失的动作回退到代码绘制的占位小人。"""

    def __init__(self, directory):
        self._frames = {}
        discovered = discover_frames(directory)
        for action in ACTIONS:
            paths = discovered.get(action)
            if paths:
                self._frames[action] = self._load(paths)
            else:
                self._frames[action] = self._placeholders(action)

    def frames_for(self, action):
        return self._frames.get(action) or self._frames["idle"]

    @staticmethod
    def _load(paths):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap
        out = []
        for p in paths:
            pm = QPixmap(str(p))
            if pm.width() != FRAME_SIZE or pm.height() != FRAME_SIZE:
                pm = pm.scaled(FRAME_SIZE, FRAME_SIZE,
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
            out.append(pm)
        return out

    @staticmethod
    def _placeholders(action):
        from PySide6.QtCore import Qt, QRect
        from PySide6.QtGui import QColor, QPainter, QPixmap

        frames = []
        for i in range(2):  # 2 帧交替，形成简单动感
            pm = QPixmap(FRAME_SIZE, FRAME_SIZE)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing)
            bounce = 4 * i  # 第二帧整体下沉 4px
            # 头
            p.setBrush(QColor("#ffcc80")); p.setPen(Qt.NoPen)
            p.drawEllipse(44, 16 + bounce, 40, 40)
            # 发型（标志性短发）
            p.setBrush(QColor("#3e2723"))
            p.drawChord(QRect(44, 12 + bounce, 40, 30), 0, 180 * 16)
            # 身体（黑 T 恤）
            p.setBrush(QColor(_PLACEHOLDER_TINTS[action]))
            p.drawRoundedRect(40, 56 + bounce, 48, 44, 8, 8)
            # 腿
            p.drawRect(48, 100 + bounce, 10, 24 - bounce)
            p.drawRect(70, 100 + bounce, 10, 24 - bounce)
            # 动作标签
            p.setPen(QColor("#ffffff"))
            p.drawText(QRect(0, 60 + bounce, FRAME_SIZE, 20), Qt.AlignCenter, action)
            p.end()
            frames.append(pm)
        return frames

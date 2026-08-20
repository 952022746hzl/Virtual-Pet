"""对话气泡：无边框半透明小窗，显示台词后自动淡出。"""
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget

PAD_X, PAD_Y = 12, 8
MAX_WIDTH = 260


class Bubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            | Qt.Tool | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._text = ""
        self._font = QFont("Microsoft YaHei", 10)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def say(self, text, ms=3000):
        self._text = text
        metrics = QFontMetrics(self._font)
        rect = metrics.boundingRect(0, 0, MAX_WIDTH, 1000,
                                    Qt.TextWordWrap, text)
        self.resize(rect.width() + PAD_X * 2, rect.height() + PAD_Y * 2 + 8)
        self.show()
        self.update()
        self._hide_timer.start(ms)

    def follow(self, pet_x, pet_y):
        """pet_x/pet_y 为桌宠窗口左上角；气泡放头顶上方居中。"""
        self.move(int(pet_x + 64 - self.width() / 2), int(pet_y - self.height() - 4))

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        body = QRectF(0, 0, self.width(), self.height() - 8)
        path = QPainterPath()
        path.addRoundedRect(body, 10, 10)
        # 底部小三角指向桌宠
        cx = self.width() / 2
        path.moveTo(cx - 6, body.bottom())
        path.lineTo(cx, body.bottom() + 8)
        path.lineTo(cx + 6, body.bottom())
        p.fillPath(path, QColor(255, 255, 255, 235))
        p.setPen(QColor("#333333"))
        p.setFont(self._font)
        p.drawText(body.adjusted(PAD_X, PAD_Y, -PAD_X, -PAD_Y),
                   Qt.TextWordWrap | Qt.AlignCenter, self._text)
        p.end()

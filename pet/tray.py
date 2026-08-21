"""系统托盘：菜单命令入口，也是唯一的退出方式。"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def _make_icon():
    pm = QPixmap(32, 32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#ffcc80"))
    p.drawEllipse(6, 4, 20, 20)          # 头
    p.setBrush(QColor("#3e2723"))
    p.drawChord(2, 2, 28, 14, 0, 180 * 16)  # 头发
    p.setBrush(QColor("#37474f"))
    p.drawRoundedRect(8, 22, 16, 9, 3, 3)   # 衣服
    p.end()
    return QIcon(pm)


def build_tray(app, on_coffee, on_cancel_overtime, on_refund_salary,
               on_chase_toggled, on_toggle_visible, on_quit):
    tray = QSystemTrayIcon(_make_icon(), app)
    tray.setToolTip("老板桌宠")
    menu = QMenu()

    for label, handler in [("要杯咖啡", on_coffee),
                           ("取消加班", on_cancel_overtime),
                           ("返还扣薪", on_refund_salary)]:
        action = QAction(label, menu)
        action.triggered.connect(handler)
        menu.addAction(action)

    menu.addSeparator()
    chase = QAction("跟随鼠标", menu)
    chase.setCheckable(True)
    chase.toggled.connect(on_chase_toggled)
    menu.addAction(chase)

    menu.addSeparator()
    toggle = QAction("显示/隐藏", menu)
    toggle.triggered.connect(on_toggle_visible)
    menu.addAction(toggle)
    quit_action = QAction("退出", menu)
    quit_action.triggered.connect(on_quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray._menu = menu  # 保留引用，防止 Python GC 回收菜单
    tray.show()
    return tray

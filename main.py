"""老板桌宠 —— 入口。"""
import signal
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from pet.bubble import Bubble
from pet.quotes import load_quotes
from pet.sprite import SpriteSet
from pet.state_machine import PetBrain
from pet.tray import build_tray
from pet.window import PetWindow

ROOT = Path(__file__).resolve().parent


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关窗口不退出，托盘退出
    # 终端 Ctrl+C 干净退出：默认处理器只会在 Qt 循环里抛 KeyboardInterrupt
    # 且不终止事件循环；主循环 33ms 一次的 Python 回调保证信号被及时处理。
    signal.signal(signal.SIGINT, lambda *_: app.quit())

    quotes = load_quotes(ROOT / "quotes.json")
    sprites = SpriteSet(ROOT / "assets" / "musk")
    brain = PetBrain()
    bubble = Bubble()
    window = PetWindow(brain, sprites, quotes, bubble)

    def toggle_visible():
        window.setVisible(not window.isVisible())
        if not window.isVisible():
            bubble.hide()

    tray = build_tray(
        app,
        on_coffee=window.command_coffee,
        on_cancel_overtime=lambda: brain.command_special("cancel_overtime"),
        on_refund_salary=lambda: brain.command_special("refund_salary"),
        on_chase_toggled=brain.set_chase,
        on_toggle_visible=toggle_visible,
        on_quit=app.quit,
    )
    window.set_context_menu(tray.contextMenu())

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

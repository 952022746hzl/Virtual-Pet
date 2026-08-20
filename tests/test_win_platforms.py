from pet.physics import Platform
from pet.win_platforms import platform_from_window

WORK = (0, 0, 1920, 1040)  # left, top, right, bottom


def test_normal_window_becomes_platform():
    p = platform_from_window("记事本", True, False, (100, 300, 900, 800), WORK)
    assert p == Platform(left=100, right=900, top=300)


def test_rejects_invisible_minimized_untitled():
    assert platform_from_window("x", False, False, (100, 300, 900, 800), WORK) is None
    assert platform_from_window("x", True, True, (100, 300, 900, 800), WORK) is None
    assert platform_from_window("", True, False, (100, 300, 900, 800), WORK) is None


def test_rejects_narrow_window():
    assert platform_from_window("x", True, False, (100, 300, 250, 800), WORK) is None


def test_rejects_maximized_and_offscreen():
    assert platform_from_window("x", True, False, (0, 10, 1920, 1040), WORK) is None      # 贴顶
    assert platform_from_window("x", True, False, (100, 1030, 900, 1400), WORK) is None   # 掉出底部

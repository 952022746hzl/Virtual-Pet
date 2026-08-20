from pet.physics import Platform
from pet.win_platforms import platform_from_window, scale_rect

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


def test_scale_rect_divides_physical_pixels_to_dip():
    # 150% 缩放下，物理像素矩形应换算回设备无关像素（Qt 坐标系）
    assert scale_rect((150, 300, 1350, 1200), 1.5) == (100, 200, 900, 800)


def test_scale_rect_rounds_to_int():
    assert scale_rect((100, 200, 900, 800), 1.25) == (80, 160, 720, 640)


def test_scale_rect_defaults_to_identity_for_invalid_scale():
    assert scale_rect((100, 200, 900, 800), 1.0) == (100, 200, 900, 800)
    assert scale_rect((100, 200, 900, 800), 0) == (100, 200, 900, 800)
    assert scale_rect((100, 200, 900, 800), None) == (100, 200, 900, 800)


def test_scaled_rect_feeds_platform_from_window_in_dip_space():
    # 125% 缩放：win32 物理像素矩形换算后应与未缩放时的 DIP 判定结果一致
    physical = (125, 375, 1125, 1000)  # 对应 DIP (100, 300, 900, 800)
    dip_rect = scale_rect(physical, 1.25)
    assert platform_from_window("记事本", True, False, dip_rect, WORK) == Platform(
        left=100, right=900, top=300
    )

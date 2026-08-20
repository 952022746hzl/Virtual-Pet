"""把其他软件的可见窗口顶边转成可站立平台。

platform_from_window 是纯函数；enumerate_platforms 才碰 win32 API。
"""
from pet.physics import Platform

MIN_WIDTH = 200
TOP_MARGIN = 40


def platform_from_window(title, visible, minimized, rect, work_area):
    left, top, right, _bottom = rect
    wa_left, wa_top, wa_right, wa_bottom = work_area
    if not visible or minimized or not title:
        return None
    if right - left < MIN_WIDTH:
        return None
    if top <= wa_top + TOP_MARGIN or top >= wa_bottom - TOP_MARGIN:
        return None
    return Platform(left=max(left, wa_left), right=min(right, wa_right), top=top)


def scale_rect(rect, scale):
    """把物理像素矩形 (win32 GetWindowRect) 换算成设备无关像素 (Qt) 坐标。

    scale 为 devicePixelRatio；scale<=0 视为 1.0 兜底。
    """
    if not scale or scale <= 0:
        scale = 1.0
    left, top, right, bottom = rect
    return (
        round(left / scale),
        round(top / scale),
        round(right / scale),
        round(bottom / scale),
    )


def enumerate_platforms(exclude_hwnds, work_area, scale=1.0):
    """枚举所有顶层窗口，返回平台列表。exclude_hwnds 排除桌宠自身窗口。

    scale：devicePixelRatio，用于把 win32 物理像素坐标换算到 Qt 的 DIP 坐标系
    （work_area 与 platform_from_window 均在 DIP 空间）。
    """
    import win32gui

    platforms = []

    def _on_window(hwnd, _):
        if hwnd in exclude_hwnds:
            return True
        try:
            p = platform_from_window(
                title=win32gui.GetWindowText(hwnd),
                visible=bool(win32gui.IsWindowVisible(hwnd)),
                minimized=bool(win32gui.IsIconic(hwnd)),
                rect=scale_rect(win32gui.GetWindowRect(hwnd), scale),
                work_area=work_area,
            )
            if p:
                platforms.append(p)
        except win32gui.error:
            pass
        return True

    win32gui.EnumWindows(_on_window, None)
    return platforms

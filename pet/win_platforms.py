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


def enumerate_platforms(exclude_hwnds, work_area):
    """枚举所有顶层窗口，返回平台列表。exclude_hwnds 排除桌宠自身窗口。"""
    import win32gui

    platforms = []

    def _on_window(hwnd, _):
        if hwnd in exclude_hwnds:
            return
        p = platform_from_window(
            title=win32gui.GetWindowText(hwnd),
            visible=bool(win32gui.IsWindowVisible(hwnd)),
            minimized=bool(win32gui.IsIconic(hwnd)),
            rect=win32gui.GetWindowRect(hwnd),
            work_area=work_area,
        )
        if p:
            platforms.append(p)

    win32gui.EnumWindows(_on_window, None)
    return platforms

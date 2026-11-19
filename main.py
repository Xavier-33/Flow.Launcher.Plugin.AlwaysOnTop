# -*- coding: utf-8 -*-
"""
Always On Top - Flow Launcher Plugin
Only lists windows that appear on the Windows taskbar.
Pin / unpin like PowerToys Always On Top.

Safety notes:
- Only uses SetWindowPos with SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE
  (z-order only, no move/resize/focus steal)
- No hooks, no injection, no global keyboard hooks
- Never touches taskbar / desktop / system shell windows
- Validates HWND with IsWindow before any change
"""

import sys
import os
import ctypes
from ctypes import wintypes

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from flowlauncher import FlowLauncher, FlowLauncherAPI

# ---------- Win32 constants ----------
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
GW_OWNER = 4

user32 = ctypes.WinDLL("user32", use_last_error=True)

user32.EnumWindows.argtypes = [
    ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM),
    wintypes.LPARAM,
]
user32.EnumWindows.restype = wintypes.BOOL
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetWindow.restype = wintypes.HWND
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.SetWindowPos.restype = wintypes.BOOL
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int


def get_window_title(hwnd):
    try:
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def get_class_name(hwnd):
    try:
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        return buf.value
    except Exception:
        return ""


def is_topmost(hwnd):
    try:
        if not user32.IsWindow(hwnd):
            return False
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        return bool(style & WS_EX_TOPMOST)
    except Exception:
        return False


def is_taskbar_window(hwnd):
    """Only windows that normally appear on the Windows taskbar."""
    try:
        if not user32.IsWindow(hwnd):
            return False
        if not user32.IsWindowVisible(hwnd):
            return False

        title = get_window_title(hwnd)
        if not title or not title.strip():
            return False

        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        # Tool windows do not appear on the taskbar
        if ex_style & WS_EX_TOOLWINDOW:
            return False

        # Owned windows normally stay off the taskbar unless APPWINDOW is set
        owner = user32.GetWindow(hwnd, GW_OWNER)
        if owner and not (ex_style & WS_EX_APPWINDOW):
            return False

        cls = get_class_name(hwnd)
        # Never touch shell / desktop / taskbar system windows
        skip_classes = {
            "Shell_TrayWnd",
            "Shell_SecondaryTrayWnd",
            "Progman",
            "WorkerW",
            "DV2ControlHost",
            "Windows.UI.Core.CoreWindow",
            "ForegroundStaging",
            "ApplicationManager_ImmersiveShellWindow",
            "NotifyIconOverflowWindow",
            "Windows.UI.Input.InputSite.WindowClass",
        }
        if cls in skip_classes:
            return False

        return True
    except Exception:
        return False


def enum_taskbar_windows():
    result = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd, lParam):
        try:
            if is_taskbar_window(hwnd):
                title = get_window_title(hwnd)
                result.append((int(hwnd), title, is_topmost(hwnd)))
        except Exception:
            pass
        return True  # always continue enumeration

    try:
        user32.EnumWindows(callback, 0)
    except Exception:
        return []

    result.sort(key=lambda x: (not x[2], x[1].lower()))
    return result


def set_topmost(hwnd, enable: bool) -> bool:
    """
    Toggle always-on-top.
    Only changes z-order; does not move, resize, or activate the window.
    Returns True on success.
    """
    try:
        hwnd = int(hwnd)
        if not user32.IsWindow(hwnd):
            return False
        # Extra safety: refuse system classes even if somehow passed in
        if not is_taskbar_window(hwnd) and not is_topmost(hwnd):
            # Allow unpin of a window that was pinned earlier but filter changed
            # only when we are turning TOPMOST off; when enabling, must be taskbar window
            if enable:
                return False
        flag = HWND_TOPMOST if enable else HWND_NOTOPMOST
        ok = user32.SetWindowPos(
            hwnd,
            wintypes.HWND(flag),
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
        )
        return bool(ok)
    except Exception:
        return False


def refresh_query(search: str = ""):
    """Re-run the plugin query so list / pin status update immediately."""
    q = "aot"
    if search:
        q = f"aot {search}"
    try:
        FlowLauncherAPI.change_query(q, True)
    except Exception:
        try:
            FlowLauncherAPI.change_query(q, requery=True)
        except Exception:
            pass


class AlwaysOnTop(FlowLauncher):

    def query(self, query: str):
        query = (query or "").strip()
        query_lower = query.lower()
        windows = enum_taskbar_windows()
        pinned_windows = [(h, t) for h, t, p in windows if p]

        results = []

        # Always first item: cancel always-on-top
        if pinned_windows:
            if len(pinned_windows) == 1:
                _, t = pinned_windows[0]
                sub = f"取消当前唯一置顶窗口：{t}"
            else:
                sub = f"取消全部 {len(pinned_windows)} 个已置顶窗口"
        else:
            sub = "当前没有已置顶的窗口"

        results.append(
            {
                "Title": "取消置顶",
                "SubTitle": sub,
                "IcoPath": "Images/app.png",
                "Score": 10000,
                "JsonRPCAction": {
                    "method": "unpin_all",
                    "parameters": [query],
                    "dontHideAfterAction": True,
                },
            }
        )

        for hwnd, title, pinned in windows:
            if query_lower and query_lower not in title.lower():
                continue

            if pinned:
                results.append(
                    {
                        "Title": f"📌 {title}",
                        "SubTitle": "已置顶 · 点击取消置顶",
                        "IcoPath": "Images/app.png",
                        "Score": 200,
                        "JsonRPCAction": {
                            "method": "toggle_window",
                            "parameters": [str(hwnd), query],
                            "dontHideAfterAction": True,
                        },
                    }
                )
            else:
                results.append(
                    {
                        "Title": title,
                        "SubTitle": "点击置顶（Always On Top）",
                        "IcoPath": "Images/app.png",
                        "Score": 50,
                        "JsonRPCAction": {
                            "method": "toggle_window",
                            "parameters": [str(hwnd), query],
                            "dontHideAfterAction": True,
                        },
                    }
                )

        if len(results) == 1 and query_lower:
            results.append(
                {
                    "Title": "没有匹配的任务栏窗口",
                    "SubTitle": "请换个关键词，或确认目标窗口已出现在任务栏",
                    "IcoPath": "Images/app.png",
                    "Score": 0,
                }
            )

        return results

    def toggle_window(self, hwnd_str: str, search: str = ""):
        try:
            hwnd = int(hwnd_str)
        except (ValueError, TypeError):
            refresh_query(search)
            return
        if not user32.IsWindow(hwnd):
            refresh_query(search)
            return
        currently = is_topmost(hwnd)
        set_topmost(hwnd, not currently)
        refresh_query(search)

    def unpin_all(self, search: str = ""):
        # Only unpin windows we currently classify as taskbar windows and that are topmost
        for hwnd, _title, pinned in enum_taskbar_windows():
            if pinned:
                set_topmost(hwnd, False)
        refresh_query(search)

    def context_menu(self, data):
        return []


if __name__ == "__main__":
    AlwaysOnTop()

import win32con
import win32api
import win32gui
import ctypes
import cv2
import numpy as np
import time
from functools import wraps
from DTOnmyoji_captureclient import capture_client_area

# Cờ để ngăn sleep và tắt màn hình (chỉ dùng cho Windows)
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ngăn hệ thống tắt màn hình hoặc sleep
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        try:
            return func(*args, **kwargs)
        finally:
            # Khôi phục lại trạng thái bình thường
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    return wrapper

def click_down(hwnd, x, y):
    lParam = win32api.MAKELONG(int(x), int(y))
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam)

def click_move(hwnd, x, y):
    lParam = win32api.MAKELONG(int(x), int(y))
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam)

def click_up(hwnd, x, y):
    lParam = win32api.MAKELONG(int(x), int(y))
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    
@prevent_sleep
def click(hwnd, x, y, wheel=None):
    """
    Giả lập cuộn chuột bằng cách kéo chuột (drag) thay vì sử dụng mouse wheel.
    """
    lParam = win32api.MAKELONG(x, y)

    # Nếu wheel = "up" hoặc "down", thực hiện hành động kéo chuột
    if wheel == "up" or wheel == "down":
        # Khoảng cách di chuyển chuột khi cuộn
        delta = 30 if wheel == "up" else -30
        
        # Tính toán vị trí bắt đầu và kết thúc của drag
        start_x = x
        start_y = y
        end_x = x  # Giữ x không thay đổi (cuộn theo chiều dọc)
        end_y = y + delta  # Di chuyển dọc theo chiều y

        # Gửi sự kiện WM_LBUTTONDOWN (nhấn chuột trái)
        lParam_start = win32api.MAKELONG(start_x, start_y)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam_start)
        time.sleep(0.01)

        # Giả lập di chuyển chuột (drag)
        lParam_end = win32api.MAKELONG(end_x, end_y)
        win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam_end)

        # Gửi sự kiện WM_LBUTTONUP (thả chuột trái)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam_end)
    else:
        # Click chuột trái thông thường nếu không có wheel
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.01)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)


def get_onmyoji_hwnd_list(title="陰陽師Onmyoji"):
    hwnd_list = []
    def enum_windows(hwnd, _):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title.startswith(title) and win32gui.IsWindowVisible(hwnd):
            hwnd_list.append(hwnd)
    win32gui.EnumWindows(enum_windows, None)
    return hwnd_list

def sync_click_all(hwnd_list, main_hwnd, click_x, click_y, log_func=None):
    """
    Click tại đúng vị trí (click_x, click_y) trên tất cả các client (tọa độ client).
    """
    hwnd_list = get_onmyoji_hwnd_list() if hwnd_list is None else hwnd_list
    for hwnd in hwnd_list:
        if hwnd == main_hwnd:
            continue  # bỏ qua client chính
        click(hwnd, click_x, click_y)
        if log_func:
            log_func(f"✅ Đã click tại ({click_x}, {click_y}) trên hwnd={hwnd}")
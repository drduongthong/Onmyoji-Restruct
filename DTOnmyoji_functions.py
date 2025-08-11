import os
import sys
import win32gui
import json
import pyautogui
import asyncio

#setup icon
def resource_path(relative_path):
    """Trả về đường dẫn thật cho file khi đóng gói bằng PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def is_window_valid(hwnd):
        return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)

DATA_FILE = "data.json"

def set_soul_value(handle, value):
    """Ghi giá trị vào data.json dưới section Soul theo handle"""
    data = {}

    # Đọc nếu file đã tồn tại
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass  # file trống hoặc lỗi, bỏ qua

    # Đảm bảo section "Soul" tồn tại
    if "Soul" not in data:
        data["Soul"] = {}

    # Ghi giá trị
    data["Soul"][str(handle)] = value

    # Ghi trở lại file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_soul_value(handle):
    """Trả về giá trị đã lưu trong Soul theo handle, nếu có"""
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("Soul", {}).get(str(handle), None)
        except json.JSONDecodeError:
            return None

DATA_FILE = "data.json"
# Ghi và đọc giá trị từ data.json
def set_quest_value(handle, value):
    """Ghi giá trị vào data.json dưới section Quest theo handle"""
    data = {}

    # Đọc nếu file đã tồn tại
    if os.path.exists(DATA_FILE): 
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass  # file trống hoặc lỗi, bỏ qua

    # Đảm bảo section "Quest" tồn tại
    if "Quest" not in data:
        data["Quest"] = {}

    # Ghi giá trị
    data["Quest"][str(handle)] = value

    # Ghi trở lại file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_quest_value(handle):
    """Trả về giá trị đã lưu trong Quest theo handle, nếu có"""
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("Quest", {}).get(str(handle), None)
        except json.JSONDecodeError:
            return None

def set_function_value(handle, value):
    """Ghi giá trị vào data.json dưới section Function theo handle"""
    data = {}

    # Đọc nếu file đã tồn tại
    if os.path.exists(DATA_FILE): 
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass  # file trống hoặc lỗi, bỏ qua

    # Đảm bảo section "Function" tồn tại
    if "Function" not in data:
        data["Function"] = {}

    # Ghi giá trị
    data["Function"][str(handle)] = value

    # Ghi trở lại file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_function_value(handle):
    """Trả về giá trị đã lưu trong Function theo handle, nếu có"""
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("Function", {}).get(str(handle), None)
        except json.JSONDecodeError:
            return None

def get_mouse_position_relative_to_foreground_window():
    # Lấy handle của cửa sổ đang ở foreground
    handle = win32gui.GetForegroundWindow()
    
    # Lấy tọa độ của cửa sổ client
    rect = win32gui.GetWindowRect(handle)
    x_window, y_window, x_window_right, y_window_bottom = rect

    # Lấy vị trí của chuột trên màn hình
    mouse_x, mouse_y = pyautogui.position()

    # Tính toán vị trí chuột tương đối với cửa sổ
    relative_x = mouse_x - x_window
    relative_y = mouse_y - y_window

    # Trả về vị trí chuột trong cửa sổ client
    return relative_x, relative_y

#function onmyoji
def resize_window(hwnd, width, height):
    # Lấy vị trí hiện tại của cửa sổ (x, y)
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]

    # Di chuyển và thay đổi kích thước
    win32gui.MoveWindow(hwnd, x, y, width, height, True)

def change_title(new_title):
    # Get the handle of the current window
    hwnd = win32gui.GetForegroundWindow()
    
    # Set the new title for the window
    win32gui.SetWindowText(hwnd, new_title)

def get_client_size(hwnd):
    # Lấy rect client (tọa độ tương đối bên trong cửa sổ)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top
    return width, height

async def ensure_client_size(hwnd, target_width=800, target_height=481):
    while True:
        w, h = get_client_size(hwnd)
        if w == 784 and h == 442:
            print("✔ Đã đạt kích thước chuẩn")
            break
        print(f"🔁 Kích thước hiện tại: {w}x{h} → Resize...")
        resize_window(hwnd, target_width, target_height)
        await asyncio.sleep(0.1)  # đợi một chút để hệ thống cập nhật

#data.json
data_json_key = ["Soul"]
def ensure_data_key(file_path="data.json", required_keys=data_json_key):
    # Nếu chưa có file thì tạo file trống với các key cần
    if not os.path.exists(file_path):
        data = {k: {} for k in required_keys}
    else:
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

        # Đảm bảo mỗi key cần thiết đều có mặt
        for k in required_keys:
            if k not in data:
                data[k] = {}

    # Ghi đè lại nếu có thay đổi hoặc file mới
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        
ensure_data_key()
#functions
def find_window(title_keyword):
    def enum_handler(hwnd, result):
        if title_keyword.lower() in win32gui.GetWindowText(hwnd).lower():
            result.append(hwnd)
    results = []
    win32gui.EnumWindows(enum_handler, results)
    return results[0] if results else None

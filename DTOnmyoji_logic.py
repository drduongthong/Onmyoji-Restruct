# logic.py
import win32gui
import time
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Lock

from DTOnmyoji_captureclient import capture_client_area, save_debug_image, find_image
from DTOnmyoji_clicker import click
from DTOnmyoji_functions import *
from DTOnmyoji_quest import *
from DTOnmyoji_realmraid import *
from DTOnmyoji_duel import *
from DTOnmyoji_helper import *
from DTOnmyoji_soul import *

file_lock = Lock()
exit_flag = False
current_data = {}

# Các dict lưu trạng thái theo hwnd (khai báo ở đây hoặc import từ module khác)
task_state = {}
hwnd_to_info = {}

TITLE_BASE = "陰陽師Onmyoji"

def get_title(type=None):
    if type:
        return f"{TITLE_BASE} {type}"
    return TITLE_BASE

class DataJsonHandler(FileSystemEventHandler):
    def __init__(self, filepath, log_func):
        super().__init__()
        self.filepath = filepath
        self.log_func = log_func

    def on_modified(self, event):
        if event.src_path.endswith(self.filepath):
            self.log_func(f"🔄 {self.filepath} vừa bị thay đổi, đọc lại file...")
            read_data_json(self.filepath, self.log_func)

def filter_hwnd_by_title(state_dict):
    """Chỉ giữ lại các hwnd có title đúng với get_title() trong dict trạng thái."""
    for hwnd in list(state_dict.keys()):
        try:
            title = win32gui.GetWindowText(hwnd)
            if get_title() not in title:
                del state_dict[hwnd]
        except Exception:
            del state_dict[hwnd]

def read_data_json(filepath, log_func):
    global current_data
    try:
        with file_lock:
            with open(filepath, "r") as f:
                data = json.load(f)
        current_data = data
        log_func("✅ Đã đọc data.json thành công")
        # Lọc lại các dict trạng thái sau khi reload data.json
        filter_hwnd_by_title(task_state)
        filter_hwnd_by_title(hwnd_to_info)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_func(f"Lỗi khi đọc {filepath}: {e}")

def start_watchdog(log_func):
    filepath = os.path.abspath("data.json")
    event_handler = DataJsonHandler(filepath, log_func)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(filepath) or '.', recursive=False)
    observer.start()
    log_func("👁️ Watchdog đã khởi động để theo dõi data.json")
    read_data_json(filepath, log_func)
    reload_template_cache()
    return observer

def auto_add(type, log_func, hwnd=None):
    title = "陰陽師Onmyoji"
    if hwnd is None:
        hwnd = str(win32gui.GetForegroundWindow())
    else:
        hwnd = str(hwnd)

    current_title = win32gui.GetWindowText(int(hwnd))
    if not current_title.startswith(title):
        log_func(f"⚠️ Cửa sổ {hwnd} KHÔNG phải {title}")
        return

    with file_lock:
        if not os.path.exists("data.json"):
            data = {}
        else:
            with open("data.json", "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    log_func("⚠️ data.json lỗi định dạng")
                    data = {}

        data.setdefault("Soul", {})
        data.setdefault("Quest", {})

        current_type = data["Soul"].get(hwnd)

        if current_type == type:
            # Xóa hwnd khỏi Soul
            del data["Soul"][hwnd]
            log_func(f"🗑️ Đã gỡ {hwnd} khỏi {type}")
            win32gui.SetWindowText(int(hwnd), title)
        else:
            # ✅ MỖI KHI ĐỔI TYPE → XÓA hwnd TRONG QUEST (NẾU CÓ)
            if hwnd in data["Quest"]:
                del data["Quest"][hwnd]
                log_func(f"🗑️ Đã xoá {hwnd} khỏi Quest do đổi type")
            
            # Thêm/đổi trong Soul
            data["Soul"][hwnd] = type
            log_func(f"✅ Đã thêm/đổi {hwnd} thành {type}")
            win32gui.SetWindowText(int(hwnd), title + f" {type}")

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def task(log_func):
    global current_data, exit_flag
    while not exit_flag:
        hwnds = current_data.get("Soul", {})
        for hwnd, value in hwnds.items():
            try:
                if value == "Soul":
                    Auto_soul(hwnd, value)
                elif value == "Key":
                    Auto_soul(hwnd, value)
                elif value == "ReamlRaid":
                    Auto_reamlraid(hwnd, value)
                elif value == "Duel":
                    Auto_duel(hwnd, value)
            except Exception as e:
                log_func(f"Lỗi khi xử lý {hwnd}: {e}")
        time.sleep(0.25)

def task_slow(log_func):
    global current_data, exit_flag
    while not exit_flag:
        hwnds = current_data.get("Soul", {})
        for hwnd, value in hwnds.items():
            try:
                if value == "Quest":
                    Auto_quest(hwnd, value)
            except Exception as e:
                log_func(f"[task_slow] Lỗi {hwnd}: {e}")
        time.sleep(0.5)

def task_helper(log_func):
    global current_data, exit_flag
    while not exit_flag:
        hwnds = current_data.get("Soul", {})
        for hwnd, value in hwnds.items():
            try:
                handle_soul_helper(hwnd, value)
            except Exception as e:
                log_func(f"[task_helper] Lỗi {hwnd}: {e}")
        time.sleep(0.25)

def cleanup(log_func):
    log_func("🧹 Đang cleanup...")
    if not os.path.exists("data.json"):
        log_func("⚠️ Không tìm thấy data.json")
        return

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        log_func("⚠️ data.json lỗi định dạng")
        return

    for hwnd in list(data.get("Soul", {}).keys()):
        try:
            hwnd_int = int(hwnd)
            if win32gui.IsWindow(hwnd_int):
                win32gui.SetWindowText(hwnd_int, "陰陽師Onmyoji")
                log_func(f"🔁 Đã đặt lại title {hwnd}")
        except Exception as e:
            log_func(f"❌ Lỗi đặt title {hwnd}: {e}")

    for section in ["Soul", "Quest"]:
        if section in data:
            data[section].clear()
            log_func(f"🗑️ Đã xoá {section}")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    log_func("✅ Cleanup xong")

def set_exit_flag():
    global exit_flag
    exit_flag = True
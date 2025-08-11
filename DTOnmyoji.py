# main.py
import sys
import os
import threading
import time
import keyboard
import asyncio
import win32gui
import cv2
import mouse
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from DTOnmyoji_killprocess import kill_process_by_name
from DTOnmyoji_logic import start_watchdog, auto_add, task, task_slow, task_helper, cleanup, set_exit_flag, capture_client_area
from DTOnmyoji_functions import ensure_client_size, resource_path
from DTOnmyoji_logic import get_title

class MainWindow(QWidget):
    log_signal = pyqtSignal(str)  # signal để log từ thread

    def __init__(self):
        super().__init__()
        self.initUI()
        self.log_signal.connect(self.log)  # connect signal → slot

        self.observer = None
        self.threads = []
        self.exit_flag = False
        self.sync_click_enabled = False  # trạng thái sync click
        self.sync_click_main_hwnd = None
        self.mouse_left_down = False
        self.last_drag_pos = None
        
        # Capture mode variables
        self.capture_mode = False
        self.capture_event_index = 0  # 1-12 cho F1-F12

    def initUI(self):
        self.setWindowTitle("DTOnmyoji PyQt5")
        icon_path = resource_path("assets/icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        width = 350
        height = 200

        # center màn hình
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        center_x = screen_geometry.x() + (screen_geometry.width() - width) // 2
        center_y = screen_geometry.y() + (screen_geometry.height() - height) // 2
        self.setGeometry(center_x, center_y, width, height)

        layout = QVBoxLayout()

        # chỉ có log box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.setLayout(layout)

    def log(self, text):
        self.log_box.append(text)

    def start(self):
        # truyền signal.emit thay vì self.log → thread-safe
        self.observer = start_watchdog(self.log_signal.emit)

        t1 = threading.Thread(target=task, args=(self.log_signal.emit,), daemon=True)
        t2 = threading.Thread(target=task_slow, args=(self.log_signal.emit,), daemon=True)
        t3 = threading.Thread(target=task_helper, args=(self.log_signal.emit,), daemon=True)

        t1.start()
        t2.start()
        t3.start()

        self.threads.extend([t1, t2, t3])
        self.log("✅ Các thread đã khởi động")

        keyboard.on_press(lambda event: self.handle_key(event))
        
        # Hook chuột trực tiếp như cũ
        mouse.hook(self.handle_mouse_event)

    def capture_and_crop_at_click(self, hwnd, click_x, click_y):
        """Capture client area và crop vùng 35x35 pixel tại vị trí click"""
        try:
            # Capture client area
            screenshot, (w, h) = capture_client_area(hwnd)
            if screenshot is None or w == 0 or h == 0:
                self.log_signal.emit("❌ Không thể capture client area")
                return False

            # Tính toán vùng crop 35x35 pixel quanh vị trí click
            crop_size = 35
            half_size = crop_size // 2

            # Đảm bảo vùng crop không vượt quá boundaries của screenshot
            y1 = max(0, click_y - half_size)
            y2 = min(screenshot.shape[0], click_y + half_size)
            x1 = max(0, click_x - half_size)
            x2 = min(screenshot.shape[1], click_x + half_size)

            # Crop vùng 35x35
            cropped_image = screenshot[y1:y2, x1:x2]

            # Resize về đúng 35x35 nếu crop bị cắt do boundary
            if cropped_image.shape[:2] != (crop_size, crop_size):
                cropped_image = cv2.resize(cropped_image, (crop_size, crop_size), interpolation=cv2.INTER_AREA)

            # Lưu file với tên event tương ứng
            filename = f"event_{self.capture_event_index}.png"
            filepath = resource_path(f"assets/{filename}")

            # Tạo thư mục assets nếu chưa có
            assets_dir = os.path.dirname(filepath)
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)

            success = cv2.imwrite(filepath, cropped_image)
            if success:
                self.log_signal.emit(f"✅ Đã lưu {filename} (35x35px) tại vị trí ({click_x}, {click_y})")

                # Reload cache cho template event vừa lưu
                try:
                    from DTOnmyoji_assets import TEMPLATE_CACHE, SCALE_DEFAULT
                    from DTOnmyoji_captureclient import load_cache, save_cache

                    # Xóa cache trong TEMPLATE_CACHE
                    if filepath in TEMPLATE_CACHE:
                        del TEMPLATE_CACHE[filepath]
                        self.log_signal.emit(f"🗑️ Đã xóa TEMPLATE_CACHE cũ của {filename}")

                    # Xóa cache trong cache.json
                    try:
                        cache_data = load_cache()
                        cache_key = filename  # key trong cache.json là filename
                        if cache_key in cache_data:
                            del cache_data[cache_key]
                            save_cache(cache_data)
                            self.log_signal.emit(f"🗑️ Đã xóa cache.json entry của {filename}")
                    except Exception as json_error:
                        self.log_signal.emit(f"⚠️ Lỗi xóa cache.json: {json_error}")

                    # Load lại template mới
                    img = cv2.imread(filepath, cv2.IMREAD_COLOR)
                    if img is not None:
                        resized = cv2.resize(
                            img,
                            (max(1, int(img.shape[1] * SCALE_DEFAULT)), max(1, int(img.shape[0] * SCALE_DEFAULT))),
                            interpolation=cv2.INTER_AREA,
                        )
                        TEMPLATE_CACHE[filepath] = {
                            "original": img,
                            "resized": resized,
                            "lab": cv2.cvtColor(resized, cv2.COLOR_BGR2LAB),
                            "hls": cv2.cvtColor(resized, cv2.COLOR_BGR2HLS),
                        }
                        self.log_signal.emit(f"🔄 Đã reload TEMPLATE_CACHE cho {filename}")
                    else:
                        self.log_signal.emit(f"⚠️ Không thể đọc lại file {filename}")

                except Exception as cache_error:
                    self.log_signal.emit(f"⚠️ Lỗi reload cache: {cache_error}")

                return True
            else:
                self.log_signal.emit(f"❌ Lỗi lưu file {filename}")
                return False

        except Exception as e:
            self.log_signal.emit(f"❌ Lỗi capture_and_crop: {e}")
            return False
    
    def handle_mouse_event(self, mouse_event):
        """Mouse hook - xử lý trực tiếp"""
        
        # Xử lý capture mode trước
        if self.capture_mode and type(mouse_event).__name__ == "ButtonEvent":
            if mouse_event.event_type == "down" and mouse_event.button == "left":
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)
                
                if get_title() in window_title:
                    try:
                        x, y = mouse.get_position()
                        client_origin_x, client_origin_y = win32gui.ClientToScreen(hwnd, (0, 0))
                        rel_x = x - client_origin_x
                        rel_y = y - client_origin_y
                        
                        # Kiểm tra click có trong client area không
                        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                        client_w = right - left
                        client_h = bottom - top
                        
                        if 0 <= rel_x < client_w and 0 <= rel_y < client_h:
                            self.log_signal.emit(f"📸 Capture mode: Click tại ({rel_x}, {rel_y})")
                            success = self.capture_and_crop_at_click(hwnd, rel_x, rel_y)
                            if success:
                                self.capture_mode = False
                                self.log_signal.emit(f"🔚 Capture mode OFF - Hoàn tất event_{self.capture_event_index}")
                            return
                        else:
                            self.log_signal.emit("⚠️ Click ngoài vùng client area")
                            return
                    except Exception as e:
                        self.log_signal.emit(f"❌ Lỗi xử lý capture click: {e}")
                        return
        
        # Xử lý sync click như cũ
        if not getattr(self, "sync_click_enabled", False):
            return
        
        main_hwnd = self.sync_click_main_hwnd
        if not main_hwnd:
            return
            
        try:
            window_title = win32gui.GetWindowText(main_hwnd)
            if get_title() not in window_title:
                return

            event_type = type(mouse_event).__name__
            x, y = mouse.get_position()
            client_origin_x, client_origin_y = win32gui.ClientToScreen(main_hwnd, (0, 0))
            rel_x = x - client_origin_x
            rel_y = y - client_origin_y
            
            from DTOnmyoji_clicker import get_onmyoji_hwnd_list, click_down, click_move, click_up
            hwnd_list = get_onmyoji_hwnd_list()
            hwnd_list = [hwnd for hwnd in hwnd_list if hwnd != main_hwnd]

            left, top, right, bottom = win32gui.GetWindowRect(main_hwnd)
            client_w = right - left
            client_h = bottom - top
            in_client = (client_origin_x <= x < client_origin_x + client_w and client_origin_y <= y < client_origin_y + client_h)

            if event_type == "ButtonEvent":
                # Xử lý cả "down" và "double" events như nhau - đều là mouse down
                if (mouse_event.event_type == "down" or mouse_event.event_type == "double") and mouse_event.button == "left":
                    if in_client:
                        self.mouse_left_down = True
                        self.last_drag_pos = (rel_x, rel_y)
                        
                        # Gửi click down đến tất cả clients
                        for hwnd in hwnd_list:
                            click_down(hwnd, rel_x, rel_y)
                        
                        self.log_signal.emit(f"🖱️ DOWN tại ({rel_x}, {rel_y})")
                        
                elif mouse_event.event_type == "up" and mouse_event.button == "left":
                    if self.mouse_left_down and in_client:
                        self.mouse_left_down = False
                        for hwnd in hwnd_list:
                            click_up(hwnd, rel_x, rel_y)
                        self.log_signal.emit(f"🖱️ UP tại ({rel_x}, {rel_y})")
                        
            elif event_type == "MoveEvent":
                if self.mouse_left_down and in_client:
                    if self.last_drag_pos != (rel_x, rel_y):
                        for hwnd in hwnd_list:
                            click_move(hwnd, rel_x, rel_y)
                        self.last_drag_pos = (rel_x, rel_y)
                        self.log_signal.emit(f"🖱️ Drag tới ({rel_x}, {rel_y})")
                        
        except Exception as e:
            self.log_signal.emit(f"❌ Lỗi handle_mouse_event: {e}")

    
    def handle_key(self, event):
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        
        # Xử lý Alt + F1 đến F12 cho xóa event files
        if event.name in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']:
            if keyboard.is_pressed('alt'):
                # Map F-key to event index
                f_key_map = {
                    'f1': 1, 'f2': 2, 'f3': 3, 'f4': 4, 'f5': 5, 'f6': 6,
                    'f7': 7, 'f8': 8, 'f9': 9, 'f10': 10, 'f11': 11, 'f12': 12
                }
                
                event_index = f_key_map[event.name]
                filename = f"event_{event_index}.png"
                filepath = resource_path(f"assets/{filename}")
                
                try:
                    # Kiểm tra file có tồn tại không
                    if os.path.exists(filepath):
                        # Xóa file
                        os.remove(filepath)
                        self.log_signal.emit(f"🗑️ Đã xóa file {filename}")
                        
                        # Xóa cache trong TEMPLATE_CACHE
                        try:
                            from DTOnmyoji_assets import TEMPLATE_CACHE
                            if filepath in TEMPLATE_CACHE:
                                del TEMPLATE_CACHE[filepath]
                                self.log_signal.emit(f"🗑️ Đã xóa TEMPLATE_CACHE của {filename}")
                        except Exception as cache_error:
                            self.log_signal.emit(f"⚠️ Lỗi xóa TEMPLATE_CACHE: {cache_error}")
                        
                        # Xóa cache trong cache.json
                        try:
                            from DTOnmyoji_captureclient import load_cache, save_cache
                            cache_data = load_cache()
                            if filename in cache_data:
                                del cache_data[filename]
                                save_cache(cache_data)
                                self.log_signal.emit(f"🗑️ Đã xóa cache.json entry của {filename}")
                        except Exception as json_error:
                            self.log_signal.emit(f"⚠️ Lỗi xóa cache.json: {json_error}")
                        
                        self.log_signal.emit(f"✅ Hoàn tất xóa Alt+{event.name.upper()} -> {filename}")
                    else:
                        self.log_signal.emit(f"⚠️ File {filename} không tồn tại")
                        
                except Exception as e:
                    self.log_signal.emit(f"❌ Lỗi xóa {filename}: {e}")
                
                return
        
        # Xử lý Ctrl + F1 đến F12 cho capture mode
        if event.name in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']:
            if keyboard.is_pressed('ctrl'):
                if get_title() not in window_title:
                    self.log_signal.emit(f"⚠️ Không phải cửa sổ Onmyoji: {window_title}")
                    return
                
                # Map F-key to event index
                f_key_map = {
                    'f1': 1, 'f2': 2, 'f3': 3, 'f4': 4, 'f5': 5, 'f6': 6,
                    'f7': 7, 'f8': 8, 'f9': 9, 'f10': 10, 'f11': 11, 'f12': 12
                }
                
                self.capture_event_index = f_key_map[event.name]
                self.capture_mode = True
                self.log_signal.emit(f"📸 Capture mode ON - Ctrl+{event.name.upper()} -> event_{self.capture_event_index}")
                self.log_signal.emit("🖱️ Click vào vị trí cần capture...")
                return
        
        # Xử lý các phím tắt thường
        if get_title() not in window_title and not event.name == 'f9':
            self.log_signal.emit(f"⚠️ Không phải cửa sổ Onmyoji: {window_title}")
            return
        
        if event.name == 'f1':
            self.log_signal.emit("🔍 F1: Đang đảm bảo kích thước cửa sổ...")
            try:
                asyncio.run(ensure_client_size(hwnd))
                self.log_signal.emit("✅ Đã đảm bảo kích thước cửa sổ")
            except Exception as e:
                self.log_signal.emit(f"❌ Lỗi F1: {e}")
        if event.name == 'f2':
            auto_add("Soul", self.log_signal.emit)
        elif event.name == 'f3':
            auto_add("Key", self.log_signal.emit)
        elif event.name == 'f4':
            auto_add("ReamlRaid", self.log_signal.emit)
        elif event.name == 'f5':
            auto_add("Duel", self.log_signal.emit)
        elif event.name == 'f6':
            auto_add("Quest", self.log_signal.emit)
        elif event.name == 'f7':
            self.sync_click_enabled = not self.sync_click_enabled
            if self.sync_click_enabled:
                self.sync_click_main_hwnd = hwnd  # Lưu hwnd chuẩn khi bật
                self.log_signal.emit(f"🖱️ Đã bật Sync Click (F7). hwnd chuẩn: {hwnd}")
            else:
                self.sync_click_main_hwnd = None
                self.log_signal.emit("🛑 Đã tắt Sync Click (F7).")
        elif event.name == 'f9':
            kill_process_by_name()
            self.log_signal.emit("🛑 Đã kill process")
        elif event.name == 'f12':
            self.log_signal.emit("📸 F12: Đang chụp screenshot...")
            img, _ = capture_client_area(hwnd)
            if img is not None:
                cv2.imwrite("f12_debug.png", img)
                self.log_signal.emit("✅ Đã lưu f12_debug.png")
            else:
                self.log_signal.emit("⚠️ Không chụp được ảnh (img is None)")

    def closeEvent(self, event):
        self.log("⏳ Đang cleanup...")
        self.exit_flag = True
        
        set_exit_flag()
        cleanup(self.log_signal.emit)

        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.log("👁️ Watchdog đã dừng")

        self.log("✅ Đã cleanup xong, thoát app.")
        event.accept()

def create_desktop_shortcut():
    try:
        from win32com.client import Dispatch
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shortcut_path = os.path.join(desktop, "DTOnmyoji PyQt5.lnk")
        target = sys.executable  # đường dẫn file pythonw.exe hoặc exe
        script_path = os.path.abspath(sys.argv[0])
        # Nếu bạn đã đóng gói thành exe thì target sẽ là file exe luôn.
        if target.lower().endswith('python.exe') or target.lower().endswith('pythonw.exe'):
            arguments = f'"{script_path}"'
        else:
            arguments = ""
            target = script_path

        icon_path = resource_path("assets/icon.ico")

        if not os.path.exists(shortcut_path):
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = icon_path
            shortcut.save()
    except Exception as e:
        print(f"Lỗi tạo shortcut: {e}")

if __name__ == '__main__':
    create_desktop_shortcut()  # Thêm dòng này trước khi tạo QApplication
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.start()
    sys.exit(app.exec_())
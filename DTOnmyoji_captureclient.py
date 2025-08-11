import win32gui
import win32ui
import win32con
import numpy as np
import cv2
import os
from DTOnmyoji_functions import is_window_valid
from DTOnmyoji_assets import *

# def capture_client_area(hwnd): 
#     # Kích thước vùng client
#     if not is_window_valid(hwnd):
#         print("⚠️ Handle cửa sổ không hợp lệ!")
#         return
#     left, top, right, bottom = win32gui.GetClientRect(hwnd)
#     w, h = right - left, bottom - top

#     # Tọa độ client trên màn hình
#     client_origin = win32gui.ClientToScreen(hwnd, (0, 0))
#     window_origin = win32gui.GetWindowRect(hwnd)[:2]

#     # Tọa độ client so với cửa sổ (tức là điểm bắt đầu để BitBlt)
#     offset_x = client_origin[0] - window_origin[0]
#     offset_y = client_origin[1] - window_origin[1]

#     # Chụp từ vùng client
#     hwndDC = win32gui.GetWindowDC(hwnd)
#     mfcDC = win32ui.CreateDCFromHandle(hwndDC)
#     saveDC = mfcDC.CreateCompatibleDC()
#     saveBitmap = win32ui.CreateBitmap()
#     saveBitmap.CreateCompatibleBitmap(mfcDC, w, h)
#     saveDC.SelectObject(saveBitmap)
#     saveDC.BitBlt((0, 0), (w, h), mfcDC, (offset_x, offset_y), win32con.SRCCOPY)

#     # Chuyển ảnh sang numpy
#     bmpstr = saveBitmap.GetBitmapBits(True)
#     img = np.frombuffer(bmpstr, dtype='uint8').reshape((h, w, 4))

#     # Dọn tài nguyên
#     win32gui.DeleteObject(saveBitmap.GetHandle())
#     saveDC.DeleteDC()
#     mfcDC.DeleteDC()
#     win32gui.ReleaseDC(hwnd, hwndDC)

#     return img[..., :3], (w, h)

# def capture_client_area(hwnd):
#     if not is_window_valid(hwnd):
#         print("⚠️ Handle cửa sổ không hợp lệ!")
#         return None, (0, 0)

#     # Lấy kích thước vùng client
#     left, top, right, bottom = win32gui.GetClientRect(hwnd)
#     w, h = right - left, bottom - top
#     if w == 0 or h == 0:
#         return None, (0, 0)

#     # Lấy device context chỉ của vùng client (nhẹ hơn)
#     hwndDC = win32gui.GetDC(hwnd)
#     srcDC = win32ui.CreateDCFromHandle(hwndDC)
#     memDC = srcDC.CreateCompatibleDC()

#     bmp = win32ui.CreateBitmap()
#     bmp.CreateCompatibleBitmap(srcDC, w, h)
#     memDC.SelectObject(bmp)

#     memDC.BitBlt((0, 0), (w, h), srcDC, (0, 0), win32con.SRCCOPY)

#     # Chuyển bitmap sang numpy
#     bmpstr = bmp.GetBitmapBits(True)
#     img = np.frombuffer(bmpstr, dtype='uint8').reshape((h, w, 4))

#     # Cleanup
#     win32gui.DeleteObject(bmp.GetHandle())
#     memDC.DeleteDC()
#     srcDC.DeleteDC()
#     win32gui.ReleaseDC(hwnd, hwndDC)

#     return img[..., :3], (w, h)

# # thêm ở 1 file global
# from threading import Lock

# hwnd_locks = {}

# def get_hwnd_lock(hwnd):
#     if hwnd not in hwnd_locks:
#         hwnd_locks[hwnd] = Lock()
#     return hwnd_locks[hwnd]

# def capture_client_area_threadsafe(hwnd):
#     lock = get_hwnd_lock(hwnd)
#     with lock:
#         return capture_client_area(hwnd)

from threading import Lock

# hwnd_locks = {}

# def get_hwnd_lock(hwnd):
#     if hwnd not in hwnd_locks:
#         hwnd_locks[hwnd] = Lock()
#     return hwnd_locks[hwnd]

# def capture_client_area(hwnd):
#     lock = get_hwnd_lock(hwnd)
#     with lock:
#         if not is_window_valid(hwnd):
#             print("⚠️ Handle cửa sổ không hợp lệ!")
#             return None, (0, 0)

#         # Lấy kích thước vùng client
#         left, top, right, bottom = win32gui.GetClientRect(hwnd)
#         w, h = right - left, bottom - top
#         if w == 0 or h == 0:
#             return None, (0, 0)

#         hwndDC = win32gui.GetDC(hwnd)
#         srcDC = win32ui.CreateDCFromHandle(hwndDC)
#         memDC = srcDC.CreateCompatibleDC()

#         bmp = win32ui.CreateBitmap()
#         bmp.CreateCompatibleBitmap(srcDC, w, h)
#         memDC.SelectObject(bmp)

#         memDC.BitBlt((0, 0), (w, h), srcDC, (0, 0), win32con.SRCCOPY)

#         bmpstr = bmp.GetBitmapBits(True)
#         img = np.frombuffer(bmpstr, dtype='uint8').reshape((h, w, 4))

#         win32gui.DeleteObject(bmp.GetHandle())
#         memDC.DeleteDC()
#         srcDC.DeleteDC()
#         win32gui.ReleaseDC(hwnd, hwndDC)

#         return img[..., :3], (w, h)

import win32gui
import win32ui
import win32con
import numpy as np
from threading import Lock
from DTOnmyoji_functions import is_window_valid

hwnd_locks = {}

def get_hwnd_lock(hwnd):
    if hwnd not in hwnd_locks:
        hwnd_locks[hwnd] = Lock()
    return hwnd_locks[hwnd]

def capture_client_area(hwnd):
    """
    Chụp vùng client của cửa sổ hwnd, trả về ảnh numpy (BGR) và kích thước (w, h).
    Thread-safe cho từng hwnd.
    """
    lock = get_hwnd_lock(hwnd)
    with lock:
        if not is_window_valid(hwnd):
            print("⚠️ Handle cửa sổ không hợp lệ!")
            return None, (0, 0)

        # Lấy kích thước vùng client
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        w, h = right - left, bottom - top
        if w == 0 or h == 0:
            return None, (0, 0)

        hwndDC = win32gui.GetDC(hwnd)
        srcDC = win32ui.CreateDCFromHandle(hwndDC)
        memDC = srcDC.CreateCompatibleDC()

        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcDC, w, h)
        memDC.SelectObject(bmp)

        memDC.BitBlt((0, 0), (w, h), srcDC, (0, 0), win32con.SRCCOPY)

        bmpstr = bmp.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8').reshape((h, w, 4))

        win32gui.DeleteObject(bmp.GetHandle())
        memDC.DeleteDC()
        srcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return img[..., :3], (w, h)

def save_debug_image(img, pos):
    img_debug = img.copy()
    if pos:
        cv2.circle(img_debug, pos, 10, (0, 255, 0), 2)
    cv2.imwrite("debug_result.png", img_debug)

def color_distance_lab(patch1, patch2):
    # Chuyển sang màu Lab để so sánh màu sắc thật
    lab1 = cv2.cvtColor(patch1, cv2.COLOR_BGR2LAB)
    lab2 = cv2.cvtColor(patch2, cv2.COLOR_BGR2LAB)
    diff = cv2.absdiff(lab1, lab2)
    dist = np.mean(diff)
    return dist

# Tạo mask trắng-đen từ ảnh template có nền trắng
def create_mask_from_template(template_path, mask_output_path='mask_from_template.png', threshold=250):
    """
    Tạo mask trắng-đen từ ảnh template có nền trắng.
    
    Args:
        template_path (str): Đường dẫn tới file ảnh template.
        mask_output_path (str): Đường dẫn để lưu mask đầu ra.
        threshold (int): Ngưỡng để xác định nền trắng (mặc định 250).
        
    Returns:
        mask (np.ndarray): Ảnh mask dạng numpy array.
    """
    # Đọc ảnh
    template = cv2.imread(template_path)
    if template is None:
        raise FileNotFoundError(f"Không tìm thấy file: {template_path}")

    # Chuyển sang grayscale
    gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Tạo mask: vùng sáng hơn threshold sẽ bị loại (mặc định là nền trắng)
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    return mask

#
ORIGINAL_SIZE = (784, 442)  # width, height chuẩn gốc
     
def find_image_autoscale(
    hwnd,
    screenshot,
    template_path,
    threshold=0.8,
    mask_path=None,
    y_min=0,
    y_max=None,
    x_min=0,
    x_max=None,
    prefer_topmost=False,
    preloaded_template=None
):
    # Lấy kích thước client hiện tại để debug
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_w, client_h = right - left, bottom - top

    if client_w == 0 or client_h == 0:
        print("⚠️ Không lấy được kích thước client hợp lệ.")
        return None, None

    h_img, w_img = screenshot.shape[:2]
    orig_w, orig_h = ORIGINAL_SIZE

    # Tính tỷ lệ scale thực tế dựa trên kích thước screenshot
    scale_x = w_img / orig_w
    scale_y = h_img / orig_h

    print(f"[DEBUG] Client hiện tại: {client_w}x{client_h}, Screenshot: {w_img}x{h_img}")
    print(f"[DEBUG] Tỷ lệ scale: width={scale_x:.3f}, height={scale_y:.3f}")

    # Xác định vùng tìm kiếm
    y_max = orig_h if y_max is None else y_max
    x_max = orig_w if x_max is None else x_max

    y_min_s = max(0, int(y_min * scale_y))
    y_max_s = min(h_img, int(y_max * scale_y))
    x_min_s = max(0, int(x_min * scale_x))
    x_max_s = min(w_img, int(x_max * scale_x))

    search_area = screenshot[y_min_s:y_max_s, x_min_s:x_max_s]

    # Load hoặc sử dụng template preload
    if preloaded_template is not None:
        template_orig = preloaded_template
    else:
        template_orig = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template_orig is None:
            print(f"⚠️ Không đọc được template: {template_path}")
            return None, None

    # Resize template theo scale
    new_w = max(1, int(template_orig.shape[1] * scale_x))
    new_h = max(1, int(template_orig.shape[0] * scale_y))
    template = cv2.resize(template_orig, (new_w, new_h), interpolation=cv2.INTER_AREA)

    print(f"[DEBUG] Template sau scale: {template.shape[1]}x{template.shape[0]}")

    # Load & resize mask nếu có
    mask = None
    if mask_path:
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            mask = cv2.resize(mask, (template.shape[1], template.shape[0]), interpolation=cv2.INTER_AREA)
            if mask.shape != template.shape[:2]:
                print("⚠️ Mask không đúng kích thước với template")
                mask = None

    # Thực hiện match template
    result = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED, mask=mask)

    if prefer_topmost:
        match_locations = np.where(result >= threshold)
        h_temp, w_temp = template.shape[:2]
        matches = []
        for pt in zip(*match_locations[::-1]):
            center_x = int(pt[0] + w_temp / 2 + x_min_s)
            center_y = int(pt[1] + h_temp / 2 + y_min_s)
            score = result[pt[1], pt[0]]
            matches.append(((center_x, center_y), score))
        if matches:
            matches.sort(key=lambda x: x[0][1])
            print(f"[DEBUG] Match tại (scaled): {matches[0][0]}, val={matches[0][1]:.2f}")
            return matches[0]
        else:
            print("[DEBUG] Không tìm thấy match (prefer_topmost)")
            return None, None
    else:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h_temp, w_temp = template.shape[:2]
            center_x = int(max_loc[0] + w_temp / 2 + x_min_s)
            center_y = int(max_loc[1] + h_temp / 2 + y_min_s)
            print(f"[DEBUG] Match tại (scaled): ({center_x}, {center_y}), val={max_val:.2f}")
            return (center_x, center_y), max_val
        else:
            print("[DEBUG] Không tìm thấy match.")
            return None, None

# 14/5
REGION_CACHE = {}

from DTOnmyoji_cache import load_cache, save_cache

def find_image(
    screenshot,
    template_path,
    hwnd,
    mode="normal",
    threshold=0.8,  # Giảm từ 0.8 xuống 0.75 để tăng độ nhạy
    mask_path=None,
    y_min=0,
    y_max=None,
    x_min=0,
    x_max=None,
    prefer_topmost=False,
    brightness_threshold=10,  # Tăng từ 10 lên 15 để tolerant hơn
    color_dist_threshold=15,  # Tăng từ 15 lên 20 để tolerant hơn
    preloaded_template=None,
    use_scaled_template=False,
    original_size=(784, 442),
    debug=False,
    skip_cache=False,
):
    def color_distance_lab(patch1, patch2):
        lab1 = cv2.cvtColor(patch1, cv2.COLOR_BGR2LAB)
        lab2 = cv2.cvtColor(patch2, cv2.COLOR_BGR2LAB)
        diff = cv2.absdiff(lab1, lab2)
        return np.mean(diff)

    h_img, w_img = screenshot.shape[:2]
    orig_w, orig_h = original_size

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_w = right - left
    client_h = bottom - top

    if preloaded_template is not None:
        if isinstance(preloaded_template, dict):
            template_resized = preloaded_template["scaled"] if use_scaled_template else preloaded_template["original"]
        else:
            template_resized = preloaded_template
    else:
        template_resized = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template_resized is None:
            if debug:
                print(f"⚠️ Không đọc được template: {template_path}")
            return None, None

    h_temp, w_temp = template_resized.shape[:2]

    if use_scaled_template:
        scale_down = 0.75
        screenshot = cv2.resize(
            screenshot,
            (int(screenshot.shape[1] * scale_down), int(screenshot.shape[0] * scale_down)),
            interpolation=cv2.INTER_AREA
        )
    else:
        scale_down = 1.0

    h_img_scaled, w_img_scaled = screenshot.shape[:2]

    # 🔄 Đọc cache và tự động khoanh vùng nếu có cache (trừ khi skip_cache=True)
    cache_data = load_cache()
    template_key = os.path.basename(template_path)
    if not skip_cache and template_key in cache_data:
        cached_x, cached_y = cache_data[template_key]
        if debug:
            print(f"[DEBUG] Sử dụng cache để thu hẹp vùng tìm kiếm quanh ({cached_x}, {cached_y}) với kích thước template ({w_temp}, {h_temp})")
        x_min = max(0, cached_x - w_temp)
        x_max = min(orig_w, cached_x + w_temp)
        y_min = max(0, cached_y - h_temp *1.5)
        y_max = min(orig_h, cached_y + h_temp *1.5)
    elif skip_cache and debug:
        print("[DEBUG] Bỏ qua cache, tìm kiếm toàn bộ vùng.")

    y_max = orig_h if y_max is None else y_max
    x_max = orig_w if x_max is None else x_max
    y_min_s = max(0, int(y_min * scale_down))
    y_max_s = min(h_img_scaled, int(y_max * scale_down))
    x_min_s = max(0, int(x_min * scale_down))
    x_max_s = min(w_img_scaled, int(x_max * scale_down))
    search_area = screenshot[y_min_s:y_max_s, x_min_s:x_max_s]

    if search_area.shape[0] < h_temp or search_area.shape[1] < w_temp:
        if debug:
            print(f"⚠️ Vùng tìm kiếm ({search_area.shape[1]}x{search_area.shape[0]}) nhỏ hơn template ({w_temp}x{h_temp}), bỏ qua.")
        return None, None

    mask = None
    if mask_path:
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            if mask.shape != (h_temp, w_temp):
                if debug:
                    print("⚠️ Mask không khớp template, bỏ qua mask.")
                mask = None

    def scale_to_client(center_img):
        scaled_x = int(center_img[0] * client_w / orig_w)
        scaled_y = int(center_img[1] * client_h / orig_h)
        if debug:
            print(f"[DEBUG] Tọa độ sau khi scale sang client: ({scaled_x}, {scaled_y})")
        return (scaled_x, scaled_y)

    def log_cache(center):
        cache_data[template_key] = center
        save_cache(cache_data)
        if debug:
            print(f"[DEBUG] Đã cập nhật cache: {template_key} => {center}")

    def process_matches(matches, prefer_topmost=False):
        if prefer_topmost:
            matches.sort(key=lambda x: x[0][1])  # Ưu tiên tọa độ Y nhỏ nhất
        else:
            matches.sort(key=lambda x: -x[1])    # Ưu tiên confidence cao nhất
        best_center = matches[0][0]
        if debug:
            print(f"[DEBUG] Match tại {best_center}, val={matches[0][1]:.2f}")
        log_cache(best_center)
        return scale_to_client(best_center), matches[0][1]

    if mode == "brightness":
        if debug:
            print(f"[DEBUG] Vùng tìm kiếm brightness: {search_area.shape}, Template: {template_resized.shape}")

        template_hls = cv2.cvtColor(template_resized, cv2.COLOR_BGR2HLS)
        search_area_hls = cv2.cvtColor(search_area, cv2.COLOR_BGR2HLS)
        avg_lightness_template = np.mean(template_hls[:, :, 1])

        result = cv2.matchTemplate(search_area, template_resized, cv2.TM_CCOEFF_NORMED, mask=mask)
        match_locations = np.where(result >= threshold)
        matches = []

        for pt in zip(*match_locations[::-1]):
            y1, y2 = pt[1], pt[1] + h_temp
            x1, x2 = pt[0], pt[0] + w_temp

            if y2 > search_area_hls.shape[0] or x2 > search_area_hls.shape[1]:
                if debug:
                    print(f"[DEBUG] Bỏ qua match tại {pt} do out-of-bounds (crop)")
                continue

            matched_patch_hls = search_area_hls[y1:y2, x1:x2]

            if matched_patch_hls.shape[:2] != (h_temp, w_temp):
                if debug:
                    print(f"[DEBUG] Bỏ qua match tại {pt} do size không khớp: {matched_patch_hls.shape}")
                continue

            avg_lightness_patch = np.mean(matched_patch_hls[:, :, 1])
            diff = abs(avg_lightness_template - avg_lightness_patch)

            if debug:
                print(f"[DEBUG] Brightness diff tại {pt}: {diff:.2f}")

            if diff > brightness_threshold:
                continue

            center = (pt[0] + w_temp // 2 + x_min_s, pt[1] + h_temp // 2 + y_min_s)
            score = result[pt[1], pt[0]]
            matches.append((center, score))

        if matches:
            return process_matches(matches, prefer_topmost)
        else:
            if debug:
                print("[DEBUG] Không tìm thấy match (brightness)")
            return None, None

    elif mode == "color":
        result = cv2.matchTemplate(search_area, template_resized, cv2.TM_CCOEFF_NORMED, mask=mask)
        match_locations = np.where(result >= threshold)
        matches = []
        for pt in zip(*match_locations[::-1]):
            matched_patch = search_area[pt[1]:pt[1]+h_temp, pt[0]:pt[0]+w_temp]
            if matched_patch.shape[0] < 5 or matched_patch.shape[1] < 5:
                continue
            dist = color_distance_lab(matched_patch, template_resized)
            if debug:
                print(f"[DEBUG] Color distance tại {pt}: {dist:.2f}")
            if dist > color_dist_threshold:
                continue
            center = (pt[0] + w_temp // 2 + x_min_s, pt[1] + h_temp // 2 + y_min_s)
            score = result[pt[1], pt[0]]
            matches.append((center, score))
        if matches:
            return process_matches(matches, prefer_topmost)
        else:
            if debug:
                print("[DEBUG] Không tìm thấy match (color-strict)")
            return None, None

    else:
        result = cv2.matchTemplate(search_area, template_resized, cv2.TM_CCOEFF_NORMED, mask=mask)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            center = (max_loc[0] + w_temp // 2 + x_min_s, max_loc[1] + h_temp // 2 + y_min_s)
            if debug:
                print(f"[DEBUG] Match (normal) tại {center}, val={max_val:.2f}")
            log_cache(center)
            return scale_to_client(center), max_val
        else:
            if debug:
                print("[DEBUG] Không tìm thấy match (normal)")
            return None, None

#
def find_image_relative(
    screenshot,
    template_main_path,
    template_target_path,
    hwnd,
    threshold=0.8,
    y_range_min=0,
    y_range_max=0,
    x_range_min=0,
    x_range_max=0,
    mode="normal",  # hỗ trợ: normal, color (strict), brightness
    brightness_threshold=15,
    color_dist_threshold=15,
    preloaded_main=None,
    preloaded_target=None,
    original_size=(784, 442),
    prefer_topmost=False,
    debug=False
):
    def color_distance_lab(patch1, patch2):
        lab1 = cv2.cvtColor(patch1, cv2.COLOR_BGR2LAB)
        lab2 = cv2.cvtColor(patch2, cv2.COLOR_BGR2LAB)
        diff = cv2.absdiff(lab1, lab2)
        return np.mean(diff)

    def extract_image(preloaded):
        if isinstance(preloaded, dict):
            return preloaded.get("original")
        return preloaded

    h_img, w_img = screenshot.shape[:2]
    orig_w, orig_h = original_size

    # Lấy kích thước client thật sự
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_w = right - left
    client_h = bottom - top

    # ==== 1️⃣ Tìm vị trí Template Main ====
    if preloaded_main is not None:
        template_main = extract_image(preloaded_main)
    else:
        template_main = cv2.imread(template_main_path, cv2.IMREAD_COLOR)
    if template_main is None:
        if debug:
            print(f"⚠️ Không load được template main: {template_main_path}")
        return None, None

    main_w, main_h = template_main.shape[1], template_main.shape[0]

    result_main = cv2.matchTemplate(screenshot, template_main, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_main)

    if max_val < threshold:
        if debug:
            print("[DEBUG] Không tìm thấy Template Main.")
        return None, None

    main_center_x = max_loc[0] + main_w // 2
    main_center_y = max_loc[1] + main_h // 2
    if debug:
        print(f"[DEBUG] Template Main tại ({main_center_x}, {main_center_y}), val={max_val:.2f}")

    # ==== 2️⃣ Vùng dò cho Target ====
    y_min_s = max(0, main_center_y - y_range_min)
    y_max_s = min(h_img, main_center_y + y_range_max)
    x_min_s = max(0, main_center_x - x_range_min)
    x_max_s = min(w_img, main_center_x + x_range_max)
    search_area = screenshot[y_min_s:y_max_s, x_min_s:x_max_s]

    # ==== 3️⃣ Tìm Template Target ====
    if preloaded_target is not None:
        template_target = extract_image(preloaded_target)
    else:
        template_target = cv2.imread(template_target_path, cv2.IMREAD_COLOR)
    if template_target is None:
        if debug:
            print(f"⚠️ Không load được template target: {template_target_path}")
        return None, None

    w_temp, h_temp = template_target.shape[1], template_target.shape[0]

    # === Function scale ra tọa độ client thật ===
    def scale_to_client(center_img):
        scaled_x = int(center_img[0] * client_w / orig_w)
        scaled_y = int(center_img[1] * client_h / orig_h)
        if debug:
            print(f"[DEBUG] Tọa độ sau khi scale sang client: ({scaled_x}, {scaled_y})")
        return (scaled_x, scaled_y)

    # ==== Xử lý các mode ====

    if mode == "color":
        result = cv2.matchTemplate(search_area, template_target, cv2.TM_CCOEFF_NORMED)
        match_locations = np.where(result >= threshold)
        matches = []
        for pt in zip(*match_locations[::-1]):
            matched_patch = search_area[pt[1]:pt[1]+h_temp, pt[0]:pt[0]+w_temp]
            if matched_patch.shape[:2] != (h_temp, w_temp):
                continue

            dist = color_distance_lab(matched_patch, template_target)
            if debug:
                print(f"[DEBUG] Color distance tại {pt}: {dist:.2f}")

            if dist > color_dist_threshold:
                continue

            center = (pt[0] + w_temp // 2 + x_min_s, pt[1] + h_temp // 2 + y_min_s)
            score = result[pt[1], pt[0]]
            matches.append((center, score))

        if matches:
            if prefer_topmost:
                matches.sort(key=lambda x: x[0][1])  # ưu tiên trên cùng
            else:
                matches.sort(key=lambda x: -x[1])  # ưu tiên điểm cao nhất
            best_center = matches[0][0]
            if debug:
                print(f"[DEBUG] Match (color-strict) tại {best_center}, val={matches[0][1]:.2f}")
            return scale_to_client(best_center), matches[0][1]
        else:
            if debug:
                print("[DEBUG] Không tìm thấy match (color-strict)")
            return None, None

    elif mode == "brightness":
        # Log debug thông tin vùng tìm kiếm + template
        if debug:
            print(f"[DEBUG] Vùng tìm kiếm brightness: {search_area.shape}, Template: {template_target.shape}")

        # Convert sang HLS để xử lý độ sáng
        template_hls = cv2.cvtColor(template_target, cv2.COLOR_BGR2HLS)
        search_area_hls = cv2.cvtColor(search_area, cv2.COLOR_BGR2HLS)
        avg_lightness_template = np.mean(template_hls[:, :, 1])

        result = cv2.matchTemplate(search_area, template_target, cv2.TM_CCOEFF_NORMED)
        match_locations = np.where(result >= threshold)
        matches = []

        for pt in zip(*match_locations[::-1]):
            y1, y2 = pt[1], pt[1] + h_temp
            x1, x2 = pt[0], pt[0] + w_temp

            # ✅ Check tránh out-of-bounds khi crop
            if y2 > search_area_hls.shape[0] or x2 > search_area_hls.shape[1]:
                if debug:
                    print(f"[DEBUG] Bỏ qua match tại {pt} do out-of-bounds (crop)")
                continue

            matched_patch_hls = search_area_hls[y1:y2, x1:x2]

            # ✅ Check kích thước đúng (height, width)
            if matched_patch_hls.shape[:2] != (h_temp, w_temp):
                if debug:
                    print(f"[DEBUG] Bỏ qua match tại {pt} do size không khớp: {matched_patch_hls.shape}")
                continue

            avg_lightness_patch = np.mean(matched_patch_hls[:, :, 1])
            diff = abs(avg_lightness_template - avg_lightness_patch)

            if debug:
                print(f"[DEBUG] Brightness diff tại {pt}: {diff:.2f}")

            if diff > brightness_threshold:
                continue

            center = (pt[0] + w_temp // 2 + x_min_s, pt[1] + h_temp // 2 + y_min_s)
            score = result[pt[1], pt[0]]
            matches.append((center, score))

        if matches:
            if prefer_topmost:
                matches.sort(key=lambda x: x[0][1])  # ưu tiên trên cùng
            else:
                matches.sort(key=lambda x: -x[1])  # ưu tiên điểm cao nhất
            best_center = matches[0][0]
            if debug:
                print(f"[DEBUG] Match (brightness) tại {best_center}, val={matches[0][1]:.2f}")
            return scale_to_client(best_center), matches[0][1]
        else:
            if debug:
                print("[DEBUG] Không tìm thấy match (brightness)")
            return None, None

    else:  # normal
        result = cv2.matchTemplate(search_area, template_target, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            center = (max_loc[0] + w_temp // 2 + x_min_s, max_loc[1] + h_temp // 2 + y_min_s)
            if debug:
                print(f"[DEBUG] Target (normal) tại {center}, val={max_val:.2f}")
            return scale_to_client(center), max_val
        else:
            if debug:
                print("[DEBUG] Không tìm thấy Target (normal)")
            return None, None
from DTOnmyoji_functions import *
from DTOnmyoji_captureclient import *
from DTOnmyoji_clicker import *
from DTOnmyoji_assets import *
import time
import json
import os

def count_fight_click(hwnd):
    """Tăng count fight cho hwnd, chỉ tăng nếu cách lần trước >= 3s, lưu vào data.json section 'fight_count'."""
    DATA_FILE = "data.json"
    hwnd_str = str(hwnd)
    now = time.time()
    # Đọc file
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    if "fight_count" not in data:
        data["fight_count"] = {}
    if "fight_timestamp" not in data:
        data["fight_timestamp"] = {}

    last_ts = data["fight_timestamp"].get(hwnd_str, 0)
    if now - last_ts >= 3.0:
        # Đủ điều kiện tăng count
        count = data["fight_count"].get(hwnd_str, 0) + 1
        data["fight_count"][hwnd_str] = count
        data["fight_timestamp"][hwnd_str] = now
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Đã count fight cho hwnd {hwnd_str}: {count}")
        return count
    else:
        # Không tăng count nếu chưa đủ 3s
        print(f"⏳ Chưa đủ 3s cho hwnd {hwnd_str} (còn {3.0 - (now - last_ts):.1f}s)")
        return data["fight_count"].get(hwnd_str, 0)

def Auto_soul(hwnd, type="Soul"):
    if not is_window_valid(hwnd):
        return

    screenshot, (w, h) = capture_client_area(hwnd)
    if w == 0 or h == 0:
        print("⚠️ Kích thước vùng client là 0x0 — có thể cửa sổ bị thu nhỏ hoặc không khả dụng.")
        return None, None

    if type == "Soul":
        # Nhóm Soul: fight + assembly challenge
        soul_templates = [
            (img_fight, "fight", "color"),
            (img_assembly_challenge, "assembly challenge", "normal"),
        ]
        for tpl, label, mode in soul_templates:
            pos, conf = find_image(
                screenshot,
                tpl,
                hwnd,
                preloaded_template=TEMPLATE_CACHE.get(tpl),
                mode=mode
            )
            if pos:
                if label == "fight":
                    count = count_fight_click(hwnd)
                    print(f"[COUNT] Fight count for hwnd {hwnd}: {count}")
                click(hwnd, *pos)

    elif type == "Key":
        # Nhóm addteam + fight
        pos_addteam, conf_addteam = find_image(
            screenshot, img_addteam, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_addteam), skip_cache=True
        )
        if pos_addteam:
            return
        else:
            pos_fight, conf_fight = find_image(
                screenshot, img_fight, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_fight), mode="color"
            )
            if pos_fight:
                count = count_fight_click(hwnd)
                print(f"[COUNT] Fight count for hwnd {hwnd}: {count}")
                click(hwnd, *pos_fight)

        # Nhóm invite + default invite + ok
        pos_invite, conf_invite = find_image(
            screenshot, img_invite, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_invite), skip_cache=True
        )
        if pos_invite:
            # Khi đã thấy invite, kiểm tra default invite trước
            pos_default, conf_default = find_image(
                screenshot, img_default_invite, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_default_invite), skip_cache=True
            )
            print(f"[DEBUG] Default invite confidence: {conf_default}")
            if pos_default:
                click(hwnd, *pos_default)
                print("Đã click vào default invite")
            else:
                pos_ok, conf_ok = find_image(
                    screenshot, img_ok, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_ok), skip_cache=True
                )
                if pos_ok:
                    click(hwnd, *pos_ok)
                    print("Đã click vào ok")
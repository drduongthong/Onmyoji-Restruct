from DTOnmyoji_captureclient import *
from DTOnmyoji_functions import *
from DTOnmyoji_clicker import *
from DTOnmyoji_assets import *

skip_cache = True

def Auto_reamlraid(hwnd, type):
    if is_window_valid(hwnd) == False:
        return
    screenshot, (w, h) = capture_client_area(hwnd)
    if w == 0 or h == 0:
        print("⚠️ Kích thước vùng client là 0x0 — có thể cửa sổ bị thu nhỏ hoặc không khả dụng.")
        return None, None

    if type == "ReamlRaid":
        # raid attack
        pos, confidence = find_image(
            screenshot, img_raid_attack, hwnd,
            preloaded_template=TEMPLATE_CACHE.get(img_raid_attack),
            mode="color", skip_cache=skip_cache
        )
        if pos:
            click(hwnd, *pos)
        else:
            # raid opponent, frog
            raid_targets = [
                (img_raid_opponent, "opponent"),
                (img_raid_frog, "frog")
            ]

            for tpl, label in raid_targets:
                pos, confidence = find_image(
                    screenshot, tpl, hwnd,
                    preloaded_template=TEMPLATE_CACHE.get(tpl),
                    mode="brightness", skip_cache=True
                )
                if pos:
                    click(hwnd, *pos)
                    print(f"🟢 Đã click vào {label}")
                    break
            else:
                # raid fail
                pos_fail, confidence_fail = find_image(
                    screenshot, img_raid_fail, hwnd,
                    preloaded_template=TEMPLATE_CACHE.get(img_raid_fail),
                    mode="color", skip_cache=skip_cache
                )
                if pos_fail:
                    click(hwnd, *pos_fail)

        # raid attack out
        pos, confidence = find_image(
            screenshot, img_raid_attack_out, hwnd,
            preloaded_template=TEMPLATE_CACHE.get(img_raid_attack_out),
            mode="color", skip_cache=skip_cache
        )
        if pos:
            x, y = pos
            pos = x + 100, y
            click(hwnd, *pos)
            print(f"🚫 Đã click img_raid_attack_out cho hwnd {hwnd}")

        # Kiểm tra img_raid_ko
        pos_ko, confidence_ko = find_image(
            screenshot, img_raid_ko, hwnd,
            preloaded_template=TEMPLATE_CACHE.get(img_raid_ko),
            skip_cache=skip_cache
        )
        if pos_ko:
            print("🔄 Tìm thấy img_raid_ko – thực hiện scroll lên")
            click(hwnd, *pos_ko, wheel="up")

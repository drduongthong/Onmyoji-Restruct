from DTOnmyoji_captureclient import *
from DTOnmyoji_functions import *
from DTOnmyoji_clicker import *
from DTOnmyoji_assets import *

def Auto_duel(hwnd, type):
    if not is_window_valid(hwnd):
        return

    screenshot, (w, h) = capture_client_area(hwnd)
    if w == 0 or h == 0:
        print("⚠️ Kích thước vùng client là 0x0 — có thể cửa sổ bị thu nhỏ hoặc không khả dụng.")
        return None, None

    if type == "Duel":
        print("Đang ở chế độ Duel")

        # Duel Fight
        pos, confidence = find_image(
            screenshot,
            img_duel_fight,
            hwnd,
            preloaded_template=TEMPLATE_CACHE.get(img_duel_fight)
        )
        if pos:
            click(hwnd, *pos)

        # Auto Deploy
        pos, confidence = find_image(
            screenshot,
            img_duel_auto_deploy,
            hwnd,
            preloaded_template=TEMPLATE_CACHE.get(img_duel_auto_deploy)
        )
        if pos:
            click(hwnd, *pos)

        # Mode Manual
        pos, confidence = find_image(
            screenshot,
            img_mode_manual,
            hwnd,
            threshold=0.7,
            preloaded_template=TEMPLATE_CACHE.get(img_mode_manual)
        )
        if pos:
            click(hwnd, *pos)

        # Duel Victory
        pos, confidence = find_image(
            screenshot,
            img_duel_victory_topduel,
            hwnd,
            preloaded_template=TEMPLATE_CACHE.get(img_duel_victory_topduel)
        )
        if pos:
            click(hwnd, *pos)

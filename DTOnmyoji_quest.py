from DTOnmyoji_functions import *
from DTOnmyoji_captureclient import *
from DTOnmyoji_clicker import *
from DTOnmyoji_assets import *
import pyautogui


def mouse_move(x, y, duration=0.5):
    pyautogui.moveTo(x, y, duration=duration)

handle_counters = {}
topmost = False

def Auto_quest(hwnd, type):
    if is_window_valid(hwnd) == False:
        return
    screenshot, (w, h) = capture_client_area(hwnd)
    if w == 0 or h == 0:
        print("⚠️ Kích thước vùng client là 0x0 — có thể cửa sổ bị thu nhỏ hoặc không khả dụng.")
        return None, None

    if type == "Quest":
        print("Đang ở chế độ Quest")
        
        # quest board
        pos, confidence = find_image(screenshot, img_quest_board, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_board))
        if pos:
            # quest trackall
            pos, confidence = find_image(screenshot, img_quest_trackall, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_trackall))
            if pos:
                click(hwnd, *pos)
            else:
                # quest tracked
                quest_value = get_quest_value(hwnd)
                if quest_value != "Navigating":
                    # quest undone
                    pos, confidence = find_image(
                        screenshot, img_quest_undone, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_undone), mode='strict', skip_cache=True
                    )
                    if pos:
                        click(hwnd, *pos)
        else:
            # không phải quest board => explore zone
            pos, confidence = find_image(screenshot, img_quest_location, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_location))
            if not pos:
                counter = handle_counters.get(hwnd, 0)
                # quest unshown
                if counter % 7 == 0:
                    pos, confidence = find_image(
                        screenshot, img_quest_unshown, hwnd, prefer_topmost=True,
                        preloaded_template=TEMPLATE_CACHE.get(img_quest_unshown), skip_cache=True
                    )
                    if pos:
                        click(hwnd, *pos, wheel="down")
                    else:
                        # quest done
                        pos, confidence = find_image(
                            screenshot, img_quest_done, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_done), skip_cache=True
                        )
                        if pos:
                            click(hwnd, *pos, wheel="down")
                if counter % 3 == 0:
                    global topmost
                    topmost = not topmost
                    pos, confidence = find_image(
                        screenshot, img_quest_board_tracked_undone, hwnd,
                        prefer_topmost=topmost, preloaded_template=TEMPLATE_CACHE.get(img_quest_board_tracked_undone), mode="brightness", skip_cache=True
                    )
                    if pos:
                        click(hwnd, *pos)

                handle_counters[hwnd] = counter + 1

        # quest location
        pos, confidence = find_image(screenshot, img_quest_location, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_location))
        if pos:
            print("Đã tìm thấy quest location")
            pos_unshown_quit, confidence = find_image(
                screenshot, img_quest_unshown_quit, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_unshown_quit)
            )
            if pos_unshown_quit:
                x, y = pos_unshown_quit
                pos_unshown_quit = (x, y - 150)
                click(hwnd, *pos_unshown_quit)

            # --- Đặt phạm vi tìm kiếm ---
            y_range_min = 25
            y_range_max = 25
            x_range_min = 0
            x_range_max = 500  # Quét 500px sang phải

            # Tìm go_topchoice dựa trên challenge
            pos, confidence = find_image_relative(
                screenshot,
                img_quest_location_challenge,          # template chính
                img_quest_location_go_topchoice,       # template target
                hwnd,
                y_range_min=y_range_min,
                y_range_max=y_range_max,
                x_range_min=x_range_min,
                x_range_max=x_range_max,
                prefer_topmost=True,
                preloaded_main=TEMPLATE_CACHE.get(img_quest_location_challenge),
                preloaded_target=TEMPLATE_CACHE.get(img_quest_location_go_topchoice),
                mode="color"
            )
            if pos:
                click(hwnd, *pos)
            else:
                # Nếu ko tìm thấy topchoice, tìm go bình thường
                pos, confidence = find_image_relative(
                    screenshot,
                    img_quest_location_challenge,
                    img_quest_location_go,
                    hwnd,
                    y_range_min=y_range_min,
                    y_range_max=y_range_max,
                    x_range_min=x_range_min,
                    x_range_max=x_range_max,
                    prefer_topmost=True,
                    preloaded_main=TEMPLATE_CACHE.get(img_quest_location_challenge),
                    preloaded_target=TEMPLATE_CACHE.get(img_quest_location_go),
                    mode="color"
                )
                if pos:
                    click(hwnd, *pos)

            # Nếu không tìm thấy challenge, fallback sang secret
            if not pos:
                pos, confidence = find_image_relative(
                    screenshot,
                    img_quest_location_secret,
                    img_quest_location_go_topchoice,
                    hwnd,
                    y_range_min=y_range_min,
                    y_range_max=y_range_max,
                    x_range_min=x_range_min,
                    x_range_max=x_range_max,
                    prefer_topmost=True,
                    preloaded_main=TEMPLATE_CACHE.get(img_quest_location_secret),
                    preloaded_target=TEMPLATE_CACHE.get(img_quest_location_go_topchoice),
                    mode="color"
                )
                if pos:
                    click(hwnd, *pos)
                else:
                    pos, confidence = find_image_relative(
                        screenshot,
                        img_quest_location_secret,
                        img_quest_location_go,
                        hwnd,
                        y_range_min=y_range_min,
                        y_range_max=y_range_max,
                        x_range_min=x_range_min,
                        x_range_max=x_range_max,
                        prefer_topmost=True,
                        preloaded_main=TEMPLATE_CACHE.get(img_quest_location_secret),
                        preloaded_target=TEMPLATE_CACHE.get(img_quest_location_go),
                        mode="color"
                    )
                    if pos:
                        click(hwnd, *pos)
                        print(*pos)


        # Challenge & secret
        quest_value = get_quest_value(hwnd)
        if quest_value != "Done":
            pos, confidence = find_image(
                screenshot, img_quest_challenge, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_challenge)
            )
            if pos:
                click(hwnd, *pos)
                set_quest_value(hwnd, "Processing")
            pos, confidence = find_image(
                screenshot, img_quest_secret_challenge,
                hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_secret_challenge)
            )
            if pos:
                click(hwnd, *pos)
                set_quest_value(hwnd, "Processing")
            pos, confidence = find_image(
                screenshot, img_quest_secret_explore,
                hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_secret_explore)
            )
            if pos:
                click(hwnd, *pos)
                set_quest_value(hwnd, "Processing")
            pos, confidence = find_image(
                screenshot, img_quest_story,
                hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_story)
            ) 
            if pos:
                click(hwnd, *pos)
        else:
            pos, confidence = find_image(
                screenshot, img_exploration_zone,
                hwnd, preloaded_template=TEMPLATE_CACHE.get(img_exploration_zone)
            )
            if pos:
                set_quest_value(hwnd, "Processing")
            else:
                pos, confidence = find_image(
                    screenshot, img_quest_secret_quit,
                    hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_secret_quit),
                    skip_cache=True
                )
                if pos:
                    click(hwnd, *pos)
                pos, confidence = find_image(
                    screenshot, img_quest_secret_exit,
                    hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_secret_exit)
                )
                if pos:
                    click(hwnd, *pos)
                pos, confidence = find_image(
                    screenshot, img_quest_challenge_exit,
                    hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_challenge_exit)
                )
                if pos:
                    click(hwnd, *pos)

        pos, confidence = find_image(
            screenshot, img_quest_claim,
            hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_claim)
        )
        if pos:
            x, y = pos
            pos = (x, y - 100)
            click(hwnd, *pos)

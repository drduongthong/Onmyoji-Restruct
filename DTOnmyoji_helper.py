from DTOnmyoji_functions import *
from DTOnmyoji_captureclient import *
from DTOnmyoji_clicker import *
from DTOnmyoji_assets import *
import pyautogui

# Counter riêng cho Rift
# Đếm số vòng lặp cho từng cửa sổ (hwnd)
rift_loop_counters = {}
encounter_loop_counters = {}
# Thêm biến toàn cục hoặc ngoài vòng lặp chính
fail_end_counters = {}        # dict lưu counter cho từng hwnd
force_check_fail_ends = {}    # dict lưu force_check cho từng hwnd
can_check_claim = {}
claim_loop_counters = {}

def handle_soul_helper(hwnd, value):
    if not is_window_valid(hwnd):
        return

    screenshot, (w, h) = capture_client_area(hwnd)
    if w == 0 or h == 0:
        print("⚠️ Kích thước vùng client là 0x0 — có thể cửa sổ bị thu nhỏ hoặc không khả dụng.")
        return None, None

    # Nhóm Encounter: chạy mỗi 3 vòng
    encounter_count = encounter_loop_counters.get(hwnd, 0)
    if encounter_count % 3 == 0:
        pos_encounter_door, _ = find_image(screenshot, img_encounter_door, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_encounter_door), skip_cache=True)
        if pos_encounter_door:
            pos_daruma, _ = find_image(screenshot, img_encounter_daruma, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_encounter_daruma), skip_cache=True)
            if pos_daruma:
                click(hwnd, *pos_encounter_door)
                print("Đã click vào encounter door")
    else:
        print(f"[DEBUG] Encounter skip ở vòng {encounter_count}")

    encounter_loop_counters[hwnd] = encounter_count + 1

    # Nhóm Ready
    pos_ready, conf_ready = find_image(screenshot, img_ready, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_ready), skip_cache=True)
    if pos_ready:
        click(hwnd, *pos_ready)
        print("Đã click vào ready")

    # Trong vòng lặp chính (ví dụ while True:)
        # Khởi tạo counter nếu chưa có
    if hwnd not in fail_end_counters:
        fail_end_counters[hwnd] = 0
    if hwnd not in force_check_fail_ends:
        force_check_fail_ends[hwnd] = 0

    # --- Nhóm Victory ---
    victory_templates = [
        (img_soul_victory, "soul victory"),
        (img_victory_general, "general victory"),
        (img_raid_victory, "raid victory"),
        (img_victory_tabtocon, "victory tab to continue"),
        (img_secret_weekly_victory, "secret weekly victory"),
    ]

    for tpl, label in victory_templates:
        pos, confidence = find_image(screenshot, tpl, hwnd, preloaded_template=TEMPLATE_CACHE.get(tpl))
        if pos:
            if label == "general victory":
                x, y = pos
                pos = (x, y + 20)
            click(hwnd, *pos)
            print(f"Đã click vào {label}")

            can_check_claim[hwnd] = True       # ✅ Cho phép check claim
            claim_loop_counters[hwnd] = 5       # ✅ Giới hạn 5 lần quét claim

            soul_value = get_soul_value(hwnd)
            if soul_value in ["Quest", "Soul", "Key"]:
                set_quest_value(hwnd, "Done")
            force_check_fail_ends[hwnd] = 5
            fail_end_counters[hwnd] = 0
            break

    # --- Xác định quét fail_end ---
    if force_check_fail_ends[hwnd] > 0:
        should_check_fail_end = True
        force_check_fail_ends[hwnd] -= 1
    else:
        fail_end_counters[hwnd] += 1
        if fail_end_counters[hwnd] >= 5:
            should_check_fail_end = True
            fail_end_counters[hwnd] = 0
        else:
            should_check_fail_end = False

    # --- Nhóm Fail & End ---
    if should_check_fail_end:
        fail_end_templates = [
            (img_raid_result_fail, "raid result fail"),
            (img_end, "end"),
        ]
        if can_check_claim.get(hwnd, False):
            fail_end_templates.append((img_victory_claim, "victory claim"))  # ✅ thêm claim chỉ khi được phép

        for tpl, label in fail_end_templates:
            pos, confidence = find_image(screenshot, tpl, hwnd, preloaded_template=TEMPLATE_CACHE.get(tpl))
            if pos:
                if label == "victory claim":
                    x, y = pos
                    pos = (x, y - 50)  # ✅ click lệch vị trí claim

                click(hwnd, *pos)
                print(f"Đã click vào {label}")

                if label == "end":
                    soul_value = get_soul_value(hwnd)
                    if soul_value in ["Quest", "Soul", "Key"]:
                        set_quest_value(hwnd, "Done")
                break
        # ✅ Giảm counter claim sau mỗi loop fail_end
        if can_check_claim.get(hwnd, False):
            claim_loop_counters[hwnd] -= 1
            if claim_loop_counters[hwnd] <= 0:
                can_check_claim[hwnd] = False

    # Tìm first_accept trước
    pos_first, confidence_first = find_image(screenshot, img_first_accept, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_first_accept))
    if pos_first:
        # Nếu thấy first_accept → tìm tiếp default_accept
        pos_default, confidence_default = find_image(screenshot, img_default_accept, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_default_accept))
        
        if pos_default:
            click(hwnd, *pos_default)
            print("✅ Đã click vào default accept")
        else:
            click(hwnd, *pos_first)
            print("✅ Không thấy default → đã click vào first accept")


    # Request accept (nằm riêng)
    pos_request_accept, conf_request = find_image(screenshot, img_request_accept, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_request_accept), skip_cache=True)
    if pos_request_accept:
        click(hwnd, *pos_request_accept)
        print("Đã click vào request accept")

    # Nhóm Rift: chạy mỗi 3 vòng
    rift_count = rift_loop_counters.get(hwnd, 0)
    if rift_count % 3 == 0:
        rift_templates = [
            (img_rift_challenge, "rift challenge"),
            (img_rift_go, "rift go")
        ]
        for tpl, label in rift_templates:
            pos, confidence = find_image(screenshot, tpl, hwnd, preloaded_template=TEMPLATE_CACHE.get(tpl), skip_cache=True)
            if pos:
                click(hwnd, *pos)
                print(f"Đã click vào {label}")
    else:
        print(f"[DEBUG] Rift skip ở vòng {rift_count}")

    rift_loop_counters[hwnd] = rift_count + 1

    # Challenge
    pos_challenge, conf_challenge = find_image(screenshot, img_quest_secret_challenge, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_quest_secret_challenge))
    if pos_challenge:
        if get_soul_value(hwnd) != "Quest":
            click(hwnd, *pos_challenge)
            print("Đã click vào secret challenge")
    pos_weekly, conf_weekly = find_image(screenshot, img_secret_weekly_challenge, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_secret_weekly_challenge))
    if pos_weekly:
        pos_notcleared, conf_notcleared = find_image(screenshot, img_secret_weekly_notcleared, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_secret_weekly_notcleared), skip_cache=True)
        if pos_notcleared:
            click(hwnd, *pos_weekly)
            print("Đã click vào secret weekly challenge (not cleared)")

    # Event - tìm kiếm trong tổ hợp 12 hình ảnh (chỉ chạy với template có sẵn)
    event_templates = [
        (img_event_1, "event 1"),
        (img_event_2, "event 2"),
        (img_event_3, "event 3"),
        (img_event_4, "event 4"),
        (img_event_5, "event 5"),
        (img_event_6, "event 6"),
        (img_event_7, "event 7"),
        (img_event_8, "event 8"),
        (img_event_9, "event 9"),
        (img_event_10, "event 10"),
        (img_event_11, "event 11"),
        (img_event_12, "event 12"),
    ]
    
    print(f"[DEBUG] Đang tìm kiếm events... Total templates: {len([t for t, _ in event_templates if t in TEMPLATE_CACHE])}")
    
    for tpl, label in event_templates:
        if tpl not in TEMPLATE_CACHE:
            print(f"[DEBUG] {label}: Template không có trong cache - {tpl}")
            continue
    
        print(f"[DEBUG] {label}: Đang tìm kiếm...")
        try:
            pos_event, conf_event = find_image(
                screenshot, tpl, hwnd,
                preloaded_template=TEMPLATE_CACHE.get(tpl),
                threshold=0.8,
                debug=True
            )
            print(f"[DEBUG] {label}: pos={pos_event}, confidence={conf_event}")
    
            # Chỉ click nếu confidence >= threshold
            if pos_event and conf_event is not None and conf_event >= 0.8:
                click(hwnd, *pos_event)
                print(f"✅ Đã click vào {label} tại ({pos_event[0]}, {pos_event[1]}) với confidence {conf_event:.3f}")
                break
            else:
                print(f"[DEBUG] {label}: Không tìm thấy (confidence: {conf_event}) hoặc dưới ngưỡng")
        except Exception as e:
            print(f"❌ [DEBUG] Lỗi khi tìm {label}: {e}")
            continue

    # Max soul
    pos_maxsoul_announce, _ = find_image(screenshot, img_maxsoul_announce, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_maxsoul_announce))
    if pos_maxsoul_announce:
        pos_maxsoul_confirm, _ = find_image(screenshot, img_maxsoul_confirm, hwnd, preloaded_template=TEMPLATE_CACHE.get(img_maxsoul_confirm))
        if pos_maxsoul_confirm:
            click(hwnd, *pos_maxsoul_confirm)
            print("Đã click vào max soul confirm")

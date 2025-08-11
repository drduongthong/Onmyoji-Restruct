import cv2
import os
from DTOnmyoji_functions import resource_path

# 🎯 Common
onmyoji_icon = resource_path("assets/icon.ico")
img_fight = resource_path("assets/fight.png")
img_ready = resource_path("assets/ready.png")
img_soul_victory = resource_path("assets/soul_victory.png")
img_soul_victory_mask = resource_path("assets/soul_victory_mask.png")
img_invite = resource_path("assets/invite.png")
img_default_invite = resource_path("assets/default_invite.png")
img_ok = resource_path("assets/ok.png")
img_addteam = resource_path("assets/addteam.png")
img_default_accept = resource_path("assets/default_accept.png")
img_end = resource_path("assets/end.png")
img_request_accept = resource_path("assets/request_accept.png")
img_request_reject = resource_path("assets/request_reject.png")
img_first_accept = resource_path("assets/first_accept.png")
img_first_reject = resource_path("assets/first_reject.png")
img_team = resource_path("assets/team.png")
img_raid_victory = resource_path("assets/raid_victory.png")
img_raid_victory_2 = resource_path("assets/raid_victory_2.png")
img_assembly_challenge = resource_path("assets/assembly_challenge.png")
img_victory_general = resource_path("assets/victory_general.png")
img_event = resource_path("assets/event.png")
img_victory_tabtocon = resource_path("assets/victory_tabtocon.png")
img_victory_claim = resource_path("assets/victory_claim.png")

# 🎪 Events (12 variants)
img_event_1 = resource_path("assets/event_1.png")
img_event_2 = resource_path("assets/event_2.png")
img_event_3 = resource_path("assets/event_3.png")
img_event_4 = resource_path("assets/event_4.png")
img_event_5 = resource_path("assets/event_5.png")
img_event_6 = resource_path("assets/event_6.png")
img_event_7 = resource_path("assets/event_7.png")
img_event_8 = resource_path("assets/event_8.png")
img_event_9 = resource_path("assets/event_9.png")
img_event_10 = resource_path("assets/event_10.png")
img_event_11 = resource_path("assets/event_11.png")
img_event_12 = resource_path("assets/event_12.png")

# 🌀 Encounter
img_encounter_door = resource_path("assets/encounter_door.png")
img_encounter_daruma = resource_path("assets/encounter_daruma.png")

# ⚔️ Raid
img_raid_opponent = resource_path("assets/raid_opponent.png")
img_raid_fail = resource_path("assets/raid_fail.png")
img_raid_attack = resource_path("assets/raid_attack.png")
img_raid_result_fail = resource_path("assets/raid_result_fail.png")
img_raid_attack_out = resource_path("assets/raid_attack_out.png")
img_raid_ko = resource_path("assets/raid_ko.png")
img_raid_frog = resource_path("assets/raid_frog.png")

# 🚩 Rift
img_rift_challenge = resource_path("assets/rift_challenge.png")
img_rift_go = resource_path("assets/rift_go.png")

# 📜 Quest
img_exploration_zone = resource_path("assets/exploration_zone.png")
img_quest_board = resource_path("assets/quest_board.png")
img_quest_trackall = resource_path("assets/quest_trackall.png")
img_quest_undone = resource_path("assets/quest_undone.png")
img_quest_done = resource_path("assets/quest_done.png")
img_quest_unshown = resource_path("assets/quest_unshown.png")
img_quest_unshown_mask = resource_path("assets/quest_unshown_mask.png")
img_quest_location = resource_path("assets/quest_location.png")
img_quest_location_challenge = resource_path("assets/quest_location_challenge.png")
img_quest_location_secret = resource_path("assets/quest_location_secret.png")
img_quest_location_go_topchoice = resource_path("assets/quest_location_go_topchoice.png")
img_quest_location_go = resource_path("assets/quest_location_go.png")
img_quest_challenge = resource_path("assets/quest_challenge.png")
img_quest_secret_challenge = resource_path("assets/quest_secret_challenge.png")
img_quest_secret_explore = resource_path("assets/quest_secret_explore.png")
img_quest_secret_quit = resource_path("assets/quest_secret_quit.png")
img_quest_secret_exit = resource_path("assets/quest_secret_exit.png")
img_quest_secret_story = resource_path("assets/quest_secret_story.png")
img_quest_board_tracked_undone = resource_path("assets/quest_board_tracked_undone.png")
img_quest_board_tracked_undone_mask = resource_path("assets/quest_board_tracked_undone_mask.png")
img_quest_unshown_quit = resource_path("assets/quest_unshown_quit.png")
img_quest_claim = resource_path("assets/quest_claim.png")
img_quest_story = resource_path("assets/quest_story.png")
img_quest_challenge_exit = resource_path("assets/quest_challenge_exit.png")
img_quest_challenge_ticket = resource_path("assets/quest_challenge_ticket.png")

# 🗓️ Weekly Challenge
img_secret_weekly_challenge = resource_path("assets/secret_weekly_challenge.png")
img_secret_weekly_notcleared = resource_path("assets/secret_weekly_notcleared.png")
img_secret_weekly_victory = resource_path("assets/secret_weekly_victory.png")

# 🎉 MaxSoul
img_maxsoul_announce = resource_path("assets/maxsoul_announce.png")
img_maxsoul_confirm = resource_path("assets/maxsoul_confirm.png")

# 🛡️ Duel
img_duel_fight = resource_path("assets/duel_fight.png")
img_duel_auto_deploy = resource_path("assets/duel_auto_deploy.png")
img_duel_victory_topduel = resource_path("assets/duel_victory_topduel.png")
img_duel_victory_topduel_mask = resource_path("assets/duel_victory_topduel_mask.png")

# ⚙️ Mode Auto
img_mode_manual = resource_path("assets/mode_manual.png")
img_mode_manual_mask = resource_path("assets/mode_manual_mask.png")

# 🔄 All template paths (including optional ones)
ALL_TEMPLATE_PATHS = [
    # Common
    img_fight, img_ready, img_soul_victory, img_soul_victory_mask, img_invite,
    img_default_invite, img_ok, img_addteam, img_default_accept, img_end,
    img_request_accept, img_first_accept, img_team, img_raid_victory, img_raid_victory_2,
    img_assembly_challenge, img_victory_general, img_event, img_request_reject, img_first_reject, 
    img_victory_tabtocon, img_victory_claim,

    # Events (12 variants) - optional
    img_event_1, img_event_2, img_event_3, img_event_4, img_event_5, img_event_6,
    img_event_7, img_event_8, img_event_9, img_event_10, img_event_11, img_event_12,

    # Encounter
    img_encounter_door, img_encounter_daruma,

    # Raid
    img_raid_opponent, img_raid_fail, img_raid_attack, img_raid_result_fail, img_raid_attack_out, img_raid_ko, img_raid_frog,

    # Rift
    img_rift_challenge, img_rift_go,

    # Quest
    img_exploration_zone, img_quest_board, img_quest_trackall, img_quest_undone, img_quest_done,
    img_quest_unshown, img_quest_unshown_mask, img_quest_location, img_quest_location_challenge,
    img_quest_location_secret, img_quest_location_go_topchoice, img_quest_location_go,
    img_quest_challenge, img_quest_secret_challenge, img_quest_secret_explore, img_quest_secret_quit,
    img_quest_secret_exit, img_quest_secret_story, img_quest_board_tracked_undone,
    img_quest_board_tracked_undone_mask, img_quest_unshown_quit, img_quest_claim, img_quest_story,
    img_quest_challenge_exit, img_quest_challenge_ticket,

    # Weekly Challenge
    img_secret_weekly_challenge, img_secret_weekly_notcleared, img_secret_weekly_victory,

    # MaxSoul
    img_maxsoul_announce, img_maxsoul_confirm,

    # Duel
    img_duel_fight, img_duel_auto_deploy, img_duel_victory_topduel, img_duel_victory_topduel_mask,

    # Mode Auto
    img_mode_manual, img_mode_manual_mask,
]

# 🚀 Template cache
TEMPLATE_CACHE = {}
SCALE_DEFAULT = 0.75

def load_template_cache():
    """Load tất cả templates, bỏ qua những file không tồn tại"""
    global TEMPLATE_CACHE
    TEMPLATE_CACHE.clear()
    
    loaded_count = 0
    skipped_count = 0
    
    for path in ALL_TEMPLATE_PATHS:
        # Kiểm tra file có tồn tại không
        if not os.path.exists(path):
            skipped_count += 1
            continue
            
        try:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is not None:
                resized = cv2.resize(
                    img,
                    (max(1, int(img.shape[1] * SCALE_DEFAULT)), max(1, int(img.shape[0] * SCALE_DEFAULT))),
                    interpolation=cv2.INTER_AREA,
                )
                TEMPLATE_CACHE[path] = {
                    "original": img,
                    "resized": resized,
                    "lab": cv2.cvtColor(resized, cv2.COLOR_BGR2LAB),
                    "hls": cv2.cvtColor(resized, cv2.COLOR_BGR2HLS),
                }
                loaded_count += 1
            else:
                print(f"⚠️ Không đọc được file: {path}")
                skipped_count += 1
        except Exception as e:
            print(f"⚠️ Lỗi load template {path}: {e}")
            skipped_count += 1
    
    print(f"✅ Loaded {loaded_count} templates, skipped {skipped_count} files")

def reload_template_cache():
    """Reload template cache - được gọi từ watchdog"""
    print("🔄 Reloading template cache...")
    load_template_cache()

# Load templates lần đầu
load_template_cache()
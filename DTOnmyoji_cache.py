import json
import os
import numpy as np
from filelock import FileLock

CACHE_FILE = "cache.json"
LOCK_FILE = CACHE_FILE + ".lock"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("⚠️ cache.json rỗng – sẽ tạo mới.")
                return {}  # Trả về dict rỗng để cho phép cập nhật lại cache
            return json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ cache.json bị lỗi JSON – sẽ tạo mới.")
        return {}
    except Exception as e:
        print(f"⚠️ Lỗi không mong muốn khi đọc cache.json: {e}")
        return {}

def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type {type(obj)} not serializable")

def save_cache(cache):
    if not cache:
        print("⚠️ Không lưu cache vì dữ liệu rỗng hoặc không hợp lệ.")
        return

    tmp_file = CACHE_FILE + ".tmp"
    lock = FileLock(LOCK_FILE)
    with lock:
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, default=convert_numpy)
            os.replace(tmp_file, CACHE_FILE)
        except Exception as e:
            print(f"⚠️ Lỗi khi ghi cache.json: {e}")

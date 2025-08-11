import psutil

def kill_process_by_name(process_name="steam.exe"):
    """Tìm và kết thúc tất cả tiến trình có tên nhất định (vd: steam.exe)"""
    killed = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return killed

import os
import shutil
import stat
import subprocess
import sys

# ====== Hàm kiểm tra và cài đặt PyInstaller ======
def check_and_install_pyinstaller():
    try:
        # Kiểm tra xem PyInstaller đã được cài đặt chưa
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                      check=True, capture_output=True, text=True)
        print("✅ PyInstaller đã được cài đặt")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ PyInstaller chưa được cài đặt, đang cài đặt...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True)
            print("✅ Đã cài đặt PyInstaller thành công")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Không thể cài đặt PyInstaller: {e}")
            return False

# ====== Cấu hình ======
script_name = "DTOnmyoji.py"
build_name = "DTOnmyoji"
current_dir = os.path.dirname(os.path.abspath(__file__))  # Thư mục hiện tại của build.py
icon_path = os.path.join(current_dir, "assets", "icon.ico")  # Icon trong assets
cache_file = os.path.join(current_dir, "cache.json")  # File cache.json cùng cấp DTOnmyoji.py
data_file = os.path.join(current_dir, "data.json")  # File data.json cùng cấp DTOnmyoji.py

dist_folder = os.path.join(current_dir, "dist")
build_folder = os.path.join(dist_folder, build_name)

# ====== Kiểm tra PyInstaller ======
if not check_and_install_pyinstaller():
    print("❌ Không thể tiếp tục build do không cài được PyInstaller")
    exit(1)

# ====== Hàm xóa readonly ======
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# ====== Xoá build cũ ======
if os.path.exists(build_folder):
    try:
        print(f"🗑️ Đang xoá thư mục build cũ: {build_folder}")
        shutil.rmtree(build_folder, onerror=remove_readonly)
    except Exception as e:
        print(f"⚠️ Không thể xoá thư mục {build_folder}: {e}")
else:
    print(f"ℹ️ Không tìm thấy thư mục build cũ: {build_folder}")

# ====== Build command với Python module ======
assets_path = os.path.join(current_dir, "assets")
script_path = os.path.join(current_dir, script_name)

print(f"🏗️ Đang build từ: {current_dir}")

# Chuyển về thư mục chứa script để build
original_cwd = os.getcwd()
os.chdir(current_dir)

try:
    # Sử dụng subprocess để gọi PyInstaller
    cmd_args = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        f"--name={build_name}",
        f"--icon={icon_path}",
        "--noconsole",
        f"--add-data={assets_path};assets",
        script_path
    ]
    
    print(f"🏗️ Command: {' '.join(cmd_args)}")
    
    result = subprocess.run(cmd_args, check=True)
    print("✅ Build thành công!")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Build thất bại: {e}")
    os.chdir(original_cwd)
    exit(1)
except Exception as e:
    print(f"❌ Lỗi không xác định: {e}")
    os.chdir(original_cwd)
    exit(1)

# Trở lại thư mục gốc
os.chdir(original_cwd)

# ====== Copy cache.json ======
built_cache_path = os.path.join(build_folder, "cache.json")
if os.path.exists(cache_file):
    try:
        shutil.copy2(cache_file, built_cache_path)
        print(f"✅ Đã copy cache.json vào {built_cache_path}")
    except Exception as e:
        print(f"⚠️ Không thể copy cache.json: {e}")
else:
    print(f"⚠️ Không tìm thấy cache.json, không copy được!")

# ====== Copy data.json ======
built_data_path = os.path.join(build_folder, "data.json")
if os.path.exists(data_file):
    try:
        shutil.copy2(data_file, built_data_path)
        print(f"✅ Đã copy data.json vào {built_data_path}")
    except Exception as e:
        print(f"⚠️ Không thể copy data.json: {e}")
else:
    print(f"⚠️ Không tìm thấy data.json, không copy được!")

print("🎉 ✅ Build hoàn tất!")
print(f"📁 File build tại: {build_folder}")
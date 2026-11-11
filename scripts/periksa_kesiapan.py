import sys
import subprocess

print("=== DAFTAR PERIKSA KESIAPAN MLOPS ===")

# 1. Python Version
print(f"[1] Python Version: {sys.version.split()[0]}")

# 2. Virtual Environment
in_venv = sys.prefix != sys.base_prefix
print(f"[2] Virtual Environment Active: {in_venv} ({sys.prefix})")

# 3. Git Config
try:
    user_name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
    user_email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
    print(f"[3] Git User: {user_name} <{user_email}>")
except Exception:
    print("[3] Git User: Belum terkonfigurasi")

# 4. Git Remote
try:
    remotes = subprocess.check_output(["git", "remote", "-v"]).decode().strip()
    print(f"[4] Git Remotes:\n{remotes}")
except Exception:
    print("[4] Git Remotes: Tidak ditemukan")

print("\nSemua pemeriksaan dasar selesai!")

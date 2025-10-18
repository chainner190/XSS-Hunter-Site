import os
import subprocess

# Ganti URL di bawah dengan URL repository GitHub kamu
GITHUB_URL = "https://github.com/chainner190/xss.git"
REPO_NAME = GITHUB_URL.split("/")[-1].replace(".git", "")

def run_command(command):
    """Jalankan perintah shell dan tampilkan outputnya."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Terjadi kesalahan saat menjalankan perintah:", command)
        print(e.stderr)

def update_tool():
    if not os.path.exists(REPO_NAME):
        print(f"📦 Repository belum ada. Meng-clone dari {GITHUB_URL} ...")
        run_command(f"git clone {GITHUB_URL}")
    else:
        print(f"🔄 Repository sudah ada. Melakukan update (git pull)...")
        os.chdir(REPO_NAME)
        run_command("git pull")
        os.chdir("..")

if __name__ == "__main__":
    update_tool()

import os
import sys
import subprocess


def get_base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def main():
    base_dir = get_base_dir()
    app_path = os.path.join(base_dir, "app.py")

    if not os.path.exists(app_path):
        print(f"未找到 app.py: {app_path}")
        sys.exit(1)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--browser.serverAddress=localhost",
        "--server.port=8501"
    ]

    try:
        subprocess.run(cmd, check=True, cwd=base_dir)
    except Exception as e:
        print("启动失败：", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

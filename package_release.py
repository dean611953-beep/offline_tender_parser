import os
import shutil
import zipfile


PROJECT_NAME = "offline_tender_parser"
RELEASE_DIR = "release"
PACKAGE_DIR = os.path.join(RELEASE_DIR, PROJECT_NAME)

INCLUDE_FILES = [
    "app.py",
    "start.py",
    "start.bat",
    "requirements.txt",
    "README.md",
    "TenderParser.spec"
]

INCLUDE_DIRS = [
    "parser",
    "extractors",
    "rules",
    "exporters",
    "models",
    "utils",
    ".streamlit"
]


def ensure_clean_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def copy_files():
    ensure_clean_dir(RELEASE_DIR)
    os.makedirs(PACKAGE_DIR, exist_ok=True)

    for file_name in INCLUDE_FILES:
        if os.path.exists(file_name):
            shutil.copy2(file_name, os.path.join(PACKAGE_DIR, file_name))

    for dir_name in INCLUDE_DIRS:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(PACKAGE_DIR, dir_name))

    os.makedirs(os.path.join(PACKAGE_DIR, "data", "uploads"), exist_ok=True)
    os.makedirs(os.path.join(PACKAGE_DIR, "data", "outputs"), exist_ok=True)


def make_zip():
    zip_path = os.path.join(RELEASE_DIR, f"{PROJECT_NAME}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PACKAGE_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, RELEASE_DIR)
                zf.write(full_path, rel_path)
    print(f"Created package: {zip_path}")


if __name__ == "__main__":
    copy_files()
    make_zip()

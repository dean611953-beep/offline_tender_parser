import os
from datetime import datetime


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def save_uploaded_file(uploaded_file, save_dir="data/uploads"):
    ensure_dir(save_dir)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(save_dir, f"{timestamp}_{uploaded_file.name}")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

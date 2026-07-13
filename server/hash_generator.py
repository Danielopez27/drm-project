import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
path = (BASE_DIR / ".." / "game" / "scripts" / "critical.gd").resolve()

def calculateHash():
    with open(path, "rb") as file:
        content = file.read()

    file_hash = hashlib.sha256(content).hexdigest()
    print(f"HASH: {file_hash}")

    return file_hash
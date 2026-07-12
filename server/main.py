from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from hash_generator import calculateHash

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
ASSET_KEY_PATH = BASE_DIR / "asset_key.txt"

EXPECTED_HASH = calculateHash()

class VerifyRequest(BaseModel):
    file_hash: str


def load_asset_key():
    with open(ASSET_KEY_PATH, "r") as file:
        return file.read().strip()


@app.get("/")
def home():
    return {"message": "Servidor DRM funcionando"}


@app.post("/verify")
def verify_code(data: VerifyRequest):
    if data.file_hash == EXPECTED_HASH:
        asset_key = load_asset_key()

        return {
            "status": "ok",
            "key": asset_key
        }

    return {
        "status": "denied",
        "message": "Integridad fallida"
    }
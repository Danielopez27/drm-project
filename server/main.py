from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import json
from hash_generator import calculateHash

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
SCENE_KEYS_PATH = BASE_DIR / "scene_keys.json"

EXPECTED_HASH = calculateHash()

class VerifyRequest(BaseModel):
    file_hash: str
    scene_name: str


def load_scene_keys():
    with open(SCENE_KEYS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {"message": "Servidor DRM funcionando"}


@app.post("/verify")
def verify_code(data: VerifyRequest):
    if data.file_hash != EXPECTED_HASH:
        return {
            "status": "denied",
            "message": "Integridad fallida"
        }

    scene_keys = load_scene_keys()
    scene_key = scene_keys.get(data.scene_name)

    if scene_key is None:
        return {
            "status": "denied",
            "message": f"No existe llave registrada para la escena '{data.scene_name}'"
        }

    return {
        "status": "ok",
        "key": scene_key
    }
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

EXPECTED_HASH = "e7c7f8f5a2b80479d771c81ed1400d3e9316852318186d95211c6c65f71a4f59"


class VerifyRequest(BaseModel):
    file_hash: str


def load_asset_key():
    with open("asset_key.txt", "r") as file:
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
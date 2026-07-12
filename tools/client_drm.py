import hashlib
import base64
import requests
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SERVER_URL = "http://127.0.0.1:8000/verify"

BASE_DIR = Path(__file__).resolve().parent
CRITICAL_FILE_PATH = (BASE_DIR / ".." / "game" / "scripts" / "critical.gd").resolve()
ENCRYPTED_ASSET_PATH = (BASE_DIR / ".." / "game" / "assets" / "mensaje_secreto.enc").resolve()


def calculate_sha256(path):
    with open(path, "rb") as file:
        content = file.read()

    return hashlib.sha256(content).hexdigest()


def request_key(file_hash):
    response = requests.post(
        SERVER_URL,
        json={"file_hash": file_hash}
    )

    return response.json()


def decrypt_asset(encrypted_path, key_base64):
    key = base64.b64decode(key_base64)

    with open(encrypted_path, "rb") as file:
        encrypted_package = file.read()

    nonce = encrypted_package[:12]
    ciphertext = encrypted_package[12:]

    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode("utf-8")


def main():
    file_hash = calculate_sha256(CRITICAL_FILE_PATH)

    print("Hash calculado:", file_hash)

    server_response = request_key(file_hash)

    print("Respuesta del servidor:", server_response)

    if server_response["status"] != "ok":
        print("Acceso denegado. No se puede descifrar el asset.")
        return

    key = server_response["key"]

    decrypted_content = decrypt_asset(
        ENCRYPTED_ASSET_PATH,
        key
    )

    print("Contenido descifrado:")
    print(decrypted_content)


if __name__ == "__main__":
    main()

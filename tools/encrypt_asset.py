from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from pathlib import Path


KEY = AESGCM.generate_key(bit_length=256)

BASE_DIR = Path(__file__).resolve().parent
input_path = (BASE_DIR / ".." / "game" / "assets" / "mensaje_secreto.txt").resolve()
output_path = (BASE_DIR / ".." / "game" / "assets" / "mensaje_secreto.enc").resolve()
key_output_path = (BASE_DIR / ".." / "server" / "asset_key.txt").resolve()


with open(input_path, "rb") as file:
    plaintext = file.read()

aesgcm = AESGCM(KEY)

nonce = os.urandom(12)

ciphertext = aesgcm.encrypt(
    nonce,
    plaintext,
    None
)

encrypted_package = nonce + ciphertext

with open(output_path, "wb") as file:
    file.write(encrypted_package)

with open(key_output_path, "w") as file:
    file.write(base64.b64encode(KEY).decode("utf-8"))

print("Asset cifrado correctamente.")
print("Archivo cifrado:", output_path)
print("Llave guardada en:", key_output_path)
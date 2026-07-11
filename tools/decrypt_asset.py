from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64


encrypted_path = "../game/assets/mensaje_secreto.enc"
key_path = "../server/asset_key.txt"


with open(key_path, "r") as file:
    key_base64 = file.read()

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

print(plaintext.decode("utf-8"))
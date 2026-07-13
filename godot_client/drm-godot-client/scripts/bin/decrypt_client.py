"""
Cliente DRM en CLI, pensado para ser compilado a .exe (PyInstaller) e
incluido dentro del proyecto Godot exportado.

Uso:
    decrypt_client.exe <ruta_critical_gd> <ruta_escena_enc> <nombre_escena> <ruta_salida_tscn> <server_url>

Ejemplo real (llamado desde GDScript):
    decrypt_client.exe "res://scripts/critical.gd" "res://scenes/level1.tscn.enc" \
        "level1.tscn" "user://cache/level1.tscn" "http://127.0.0.1:8000/verify"

Comportamiento:
- Calcula SHA-256 de critical.gd
- Pide al servidor la llave de la escena indicada, mandando el hash
- Si el servidor responde "ok": descifra la escena a la ruta de salida y
  termina con código 0
- Si el servidor responde "denied" o hay cualquier error: NO escribe nada
  y termina con código distinto de 0

Este script NUNCA contiene una llave embebida. Si el servidor no está
disponible o el hash no es válido, no hay forma de obtener el contenido
descifrado.
"""

import sys
import hashlib
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def calculate_sha256(path):
    with open(path, "rb") as file:
        content = file.read()
    return hashlib.sha256(content).hexdigest()


def request_key(server_url, file_hash, scene_name):
    payload = json.dumps({
        "file_hash": file_hash,
        "scene_name": scene_name
    }).encode("utf-8")

    request = urllib.request.Request(
        server_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def decrypt_scene(encrypted_path, key_hex):
    key = bytes.fromhex(key_hex)

    with open(encrypted_path, "rb") as file:
        encrypted_package = file.read()

    nonce = encrypted_package[:12]
    ciphertext = encrypted_package[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return plaintext


def fail(message, code=1):
    print(f"[DENEGADO] {message}", file=sys.stderr)
    sys.exit(code)


def main():
    if len(sys.argv) != 6:
        fail(
            "Uso: decrypt_client.exe <critical_gd_path> <escena_enc_path> "
            "<scene_name> <salida_tscn_path> <server_url>"
        )

    critical_gd_path = sys.argv[1]
    encrypted_scene_path = sys.argv[2]
    scene_name = sys.argv[3]
    output_path = sys.argv[4]
    server_url = sys.argv[5]

    try:
        file_hash = calculate_sha256(critical_gd_path)
    except OSError as error:
        fail(f"No se pudo leer critical.gd: {error}")

    try:
        server_response = request_key(server_url, file_hash, scene_name)
    except (urllib.error.URLError, TimeoutError) as error:
        fail(f"No se pudo contactar al servidor DRM: {error}")

    if server_response.get("status") != "ok":
        fail(server_response.get("message", "Verificación fallida"))

    key_hex = server_response["key"]

    try:
        with open(encrypted_scene_path, "rb") as f:
            encrypted_package = f.read()

        nonce = encrypted_package[:12]
        ciphertext = encrypted_package[12:]
        aesgcm = AESGCM(bytes.fromhex(key_hex))
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as error:
        fail(f"No se pudo descifrar la escena: {error}")

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path_obj, "wb") as file:
        file.write(plaintext)

    print(f"Escena descifrada correctamente en: {output_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
"""
Cliente CLI para descifrado de escenas Godot.

Soporta DOS modos:

1. Modo completo (pide la llave al servidor él mismo):
   decrypt_client.exe <critical_gd_path> <escena_enc_path> <scene_name> \
       <salida_tscn_path> <server_url>

2. Modo --decrypt-only (Godot ya llamó al servidor vía HTTPRequest y ya
   tiene la llave; este modo solo descifra, sin hacer ninguna petición
   de red):
   decrypt_client.exe --decrypt-only <escena_enc_path> <key_hex> <salida_tscn_path>

Este script NUNCA contiene una llave embebida. En modo --decrypt-only,
la llave se recibe como argumento en cada ejecución (viene de la
respuesta HTTP que Godot ya validó), nunca se guarda en el binario.
"""

import sys
import hashlib
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


def decrypt_to_file(encrypted_path, key_hex, output_path):
    key = bytes.fromhex(key_hex)

    with open(encrypted_path, "rb") as file:
        encrypted_package = file.read()

    nonce = encrypted_package[:12]
    ciphertext = encrypted_package[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path_obj, "wb") as file:
        file.write(plaintext)


def fail(message, code=1):
    print(f"[DENEGADO] {message}", file=sys.stderr)
    sys.exit(code)


def run_decrypt_only_mode():
    # sys.argv: [prog, "--decrypt-only", encrypted_path, key_hex, output_path]
    if len(sys.argv) != 5:
        fail(
            "Uso: decrypt_client.exe --decrypt-only <escena_enc_path> "
            "<key_hex> <salida_tscn_path>"
        )

    encrypted_path = sys.argv[2]
    key_hex = sys.argv[3]
    output_path = sys.argv[4]

    try:
        decrypt_to_file(encrypted_path, key_hex, output_path)
    except Exception as error:
        fail(f"No se pudo descifrar la escena: {error}")

    print(f"Escena descifrada correctamente en: {output_path}")
    sys.exit(0)


def run_full_mode():
    # sys.argv: [prog, critical_gd_path, escena_enc_path, scene_name, salida_path, server_url]
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
        decrypt_to_file(encrypted_scene_path, key_hex, output_path)
    except Exception as error:
        fail(f"No se pudo descifrar la escena: {error}")

    print(f"Escena descifrada correctamente en: {output_path}")
    sys.exit(0)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--decrypt-only":
        run_decrypt_only_mode()
    else:
        run_full_mode()


if __name__ == "__main__":
    main()
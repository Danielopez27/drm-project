"""
Cifra las escenas .tscn listadas en scenes_to_encrypt.txt.

- Genera una llave AES-GCM de 256 bits POR CADA escena.
- Escribe el archivo cifrado como <escena>.tscn.enc junto al original.
- Guarda todas las llaves en scene_keys.json (indexado por nombre de archivo),
  que main.py usa para responder al cliente cuando la verificación es válida.

IMPORTANTE: después de correr este script, el .tscn en texto plano NO debe
exportarse con el juego. Solo el .tscn.enc debe quedar en el proyecto Godot
al momento de exportar (ver instrucciones en README).
"""

import json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

BASE_DIR = Path(__file__).resolve().parent
GODOT_PROJECT_DIR = (BASE_DIR / ".." / "godot_client" / "drm-godot-client").resolve()
SCENES_LIST_PATH = BASE_DIR / "scenes_to_encrypt.txt"
KEYS_OUTPUT_PATH = BASE_DIR / "scene_keys.json"


def read_scene_list(path):
    scenes = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            scenes.append(line)
    return scenes


def encrypt_scene(scene_relative_path):
    scene_path = (GODOT_PROJECT_DIR / scene_relative_path).resolve()

    if not scene_path.exists():
        print(f"[AVISO] No encontrada, se omite: {scene_path}")
        return None

    with open(scene_path, "rb") as file:
        plaintext = file.read()

    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    encrypted_package = nonce + ciphertext

    encrypted_path = scene_path.with_suffix(scene_path.suffix + ".enc")

    with open(encrypted_path, "wb") as file:
        file.write(encrypted_package)

    print(f"Cifrada: {scene_relative_path} -> {encrypted_path.name}")

    scene_filename = Path(scene_relative_path).name
    return scene_filename, key


def main():
    scenes = read_scene_list(SCENES_LIST_PATH)

    if not scenes:
        print("No hay escenas listadas en scenes_to_encrypt.txt")
        return

    keys_by_scene = {}

    if KEYS_OUTPUT_PATH.exists():
        with open(KEYS_OUTPUT_PATH, "r", encoding="utf-8") as file:
            keys_by_scene = json.load(file)

    for scene_relative_path in scenes:
        result = encrypt_scene(scene_relative_path)
        if result is None:
            continue
        scene_filename, key = result
        keys_by_scene[scene_filename] = key.hex()

    with open(KEYS_OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(keys_by_scene, file, indent=2)

    print(f"\nLlaves guardadas en: {KEYS_OUTPUT_PATH}")
    print("Escenas cifradas:", list(keys_by_scene.keys()))
    print("\nRecuerda: NO incluyas los .tscn en texto plano al exportar el juego,")
    print("solo los .tscn.enc deben viajar con el build exportado.")


if __name__ == "__main__":
    main()
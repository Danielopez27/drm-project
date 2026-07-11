import hashlib

path = "../game/scripts/critical.gd"

with open(path, "rb") as file:
    content = file.read()

file_hash = hashlib.sha256(content).hexdigest()

print(file_hash)
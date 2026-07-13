extends Node
## Autoload (Singleton) responsable de:
## 1. Pedir al servidor DRM la llave de una escena específica (mandando el
##    hash de critical.gd para verificación de integridad).
## 2. Invocar decrypt_client.exe para descifrar esa escena a un archivo
##    temporal en user:// (NUNCA en res://, que es de solo lectura en un
##    build exportado).
## 3. Cargar la escena descifrada y borrar el temporal INMEDIATAMENTE
##    después, exista o no error.
##
## No contiene ninguna llave embebida: todo depende de la respuesta del
## servidor en cada llamada.

signal verification_started(scene_name: String)
signal verification_failed(scene_name: String, reason: String)
signal scene_ready(scene_name: String)

const SERVER_URL := "http://127.0.0.1:8000/verify"
const CRITICAL_GD_PATH := "res://scripts/critical.gd"
const DECRYPT_CLIENT_EXE := "res://scripts/bin/decrypt_client.exe"
const CACHE_DIR := "user://cache/"

var UNLOCK_CONTENT_KEY

var _http_request: HTTPRequest
var _pending_scene_name := ""


func _ready() -> void:
	_http_request = HTTPRequest.new()
	add_child(_http_request)
	_http_request.request_completed.connect(_on_verify_request_completed)

	var dir := DirAccess.open("user://")
	if dir and not dir.dir_exists("cache"):
		dir.make_dir("cache")


func query_scene_change(new_scene_name: String) -> void:
	_pending_scene_name = new_scene_name

	emit_signal("verification_started", new_scene_name)

	var critical_file := FileAccess.open(CRITICAL_GD_PATH, FileAccess.READ)

	if critical_file == null:
		_fail(new_scene_name, "No se pudo leer critical.gd")
		return

	var content := critical_file.get_as_text()
	critical_file.close()

	var file_hash := content.sha256_text()

	var payload := {
		"file_hash": file_hash,
		"scene_name": new_scene_name + ".tscn"
	}

	var json_body := JSON.stringify(payload)

	var headers := PackedStringArray([
		"Content-Type: application/json"
	])

	var error := _http_request.request(
		SERVER_URL,
		headers,
		HTTPClient.METHOD_POST,
		json_body
	)

	if error != OK:
		_fail(new_scene_name, "Error al enviar petición HTTP: %s" % error)


func _on_verify_request_completed(
	result: int,
	response_code: int,
	headers: PackedStringArray,
	body: PackedByteArray
) -> void:
	var scene_name := _pending_scene_name

	if response_code != 200:
		_fail(scene_name, "Error del servidor (código %s)" % response_code)
		return

	var response_text := body.get_string_from_utf8()

	var json := JSON.new()
	var parse_error := json.parse(response_text)

	if parse_error != OK:
		_fail(scene_name, "Respuesta del servidor inválida")
		return

	var response = json.data

	if not (response.has("status") and response["status"] == "ok"):
		var reason: String = response.get("message", "Acceso denegado")
		_fail(scene_name, reason)
		return

	var scene_key := str(response.get("key", ""))

	if scene_key == "":
		_fail(scene_name, "Acceso concedido, pero no llegó la llave")
		return

	UNLOCK_CONTENT_KEY = scene_key

	_decrypt_and_load_scene(scene_name, scene_key)


func _decrypt_and_load_scene(scene_name: String, scene_key: String) -> void:
	var encrypted_res_path := "res://assets/%s.tscn.enc" % scene_name
	var output_path := CACHE_DIR + scene_name + ".tscn"

	var critical_gd_abs := ProjectSettings.globalize_path(CRITICAL_GD_PATH)
	var encrypted_scene_abs := ProjectSettings.globalize_path(encrypted_res_path)
	var output_abs := ProjectSettings.globalize_path(output_path)
	var exe_abs := ProjectSettings.globalize_path(DECRYPT_CLIENT_EXE)

	var args := [
		"--decrypt-only",
		encrypted_scene_abs,
		scene_key,
		output_abs
	]

	var output := []
	var exit_code := OS.execute(exe_abs, args, output, true)

	if exit_code != 0:
		_fail(scene_name, "No se pudo descifrar la escena: %s" % str(output))
		return

	if not FileAccess.file_exists(output_path):
		_fail(scene_name, "El proceso terminó bien pero no se generó el archivo esperado")
		return

	if ResourceLoader.load_threaded_request(output_path) != OK:
		_delete_temp_file(output_path)
		_fail(scene_name, "No se pudo iniciar la carga de la escena")
		return

	var packed_scene: PackedScene = ResourceLoader.load_threaded_get(output_path)

	_delete_temp_file(output_path)

	if packed_scene == null:
		_fail(scene_name, "No se pudo cargar la escena descifrada")
		return

	emit_signal("scene_ready", scene_name)
	get_tree().change_scene_to_packed(packed_scene)


func _delete_temp_file(path: String) -> void:
	if FileAccess.file_exists(path):
		var dir := DirAccess.open(CACHE_DIR)
		if dir:
			dir.remove(path.get_file())


func _fail(scene_name: String, reason: String) -> void:
	UNLOCK_CONTENT_KEY = null
	print("[DRM] Acceso denegado para '%s': %s" % [scene_name, reason])
	emit_signal("verification_failed", scene_name, reason)
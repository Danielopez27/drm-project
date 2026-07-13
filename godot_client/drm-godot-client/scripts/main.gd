extends Control

@onready var validate_button: Button = $VBoxContainer/ValidateButton
@onready var status_label: Label = $VBoxContainer/StatusLabel
@onready var protected_content_label: Label = $VBoxContainer/ProtectedContentLabel
@onready var license_request: HTTPRequest = $LicenseRequest


var critical_file_path := "res://scripts/critical.gd"
var protected_asset_path := "res://assets/mensaje_secreto.txt"
var server_url := "http://127.0.0.1:8000/verify"
var received_key := ""


func _ready():
	validate_button.pressed.connect(_on_validate_button_pressed)
	license_request.request_completed.connect(_on_license_request_completed)

	ContentManager.verification_started.connect(_on_scene_verification_started)
	ContentManager.verification_failed.connect(_on_scene_verification_failed)
	ContentManager.scene_ready.connect(_on_scene_ready)

	protected_content_label.text = "Contenido protegido: bloqueado"


func _on_validate_button_pressed():
	status_label.text = "Estado: leyendo critical.gd..."
	protected_content_label.text = "Contenido protegido: bloqueado"

	var file := FileAccess.open(critical_file_path, FileAccess.READ)

	if file == null:
		status_label.text = "Estado: no se pudo leer critical.gd"
		print("Error: no se encontró el archivo en ", critical_file_path)
		return

	var content := file.get_as_text()
	file.close()

	var file_hash := content.sha256_text()

	print("Hash SHA-256 enviado:")
	print(file_hash)

	status_label.text = "Estado: enviando hash al servidor..."

	var data := {
		"file_hash": file_hash
	}

	var json_body := JSON.stringify(data)

	var headers := PackedStringArray([
		"Content-Type: application/json"
	])

	var error := license_request.request(
		server_url,
		headers,
		HTTPClient.METHOD_POST,
		json_body
	)

	if error != OK:
		status_label.text = "Estado: error al enviar petición"
		print("Error HTTPRequest:", error)


func _on_license_request_completed(
	result: int,
	response_code: int,
	headers: PackedStringArray,
	body: PackedByteArray
):
	var response_text := body.get_string_from_utf8()

	print("Resultado de la petición:", result)
	print("Código HTTP:", response_code)
	print("Respuesta del servidor:")
	print(response_text)

	if response_code != 200:
		status_label.text = "Estado: error del servidor"
		protected_content_label.text = "Contenido protegido: bloqueado"
		return

	var json := JSON.new()
	var parse_error := json.parse(response_text)

	if parse_error != OK:
		status_label.text = "Estado: respuesta inválida"
		protected_content_label.text = "Contenido protegido: bloqueado"
		return

	var response = json.data

	if response.has("status") and response["status"] == "ok":
		received_key = str(response.get("key", ""))

		if received_key == "":
			status_label.text = "Estado: acceso concedido, pero no llegó key"
			protected_content_label.text = "Contenido protegido: bloqueado"
			return

		status_label.text = "Estado: acceso concedido"

		print("Llave recibida:")
		print(received_key)

		unlock_protected_content()

	else:
		received_key = ""
		status_label.text = "Estado: acceso denegado"
		protected_content_label.text = "Contenido protegido: bloqueado"


func unlock_protected_content():
	if received_key == "":
		protected_content_label.text = "Contenido protegido: bloqueado"
		return

	var file := FileAccess.open(protected_asset_path, FileAccess.READ)

	if file == null:
		protected_content_label.text = "Contenido protegido: no se encontró el asset"
		print("Error: no se encontró el archivo en ", protected_asset_path)
		return

	var protected_content := file.get_as_text()
	file.close()

	protected_content_label.text = "Contenido desbloqueado: " + protected_content
	ContentManager.UNLOCK_CONTENT_KEY = received_key


func _on_validate_button_2_pressed() -> void:
	validate_button.disabled = true
	ContentManager.query_scene_change("first_level")


func _on_scene_verification_started(scene_name: String) -> void:
	status_label.text = "Estado: verificando '%s'..." % scene_name


func _on_scene_verification_failed(scene_name: String, reason: String) -> void:
	status_label.text = "Estado: acceso denegado (%s)" % reason
	validate_button.disabled = false


func _on_scene_ready(scene_name: String) -> void:
	status_label.text = "Estado: acceso concedido, cargando '%s'..." % scene_name
	# El propio ContentManager ya hace get_tree().change_scene_to_packed(),
	# así que esta escena (main.gd) será reemplazada justo después de esto.

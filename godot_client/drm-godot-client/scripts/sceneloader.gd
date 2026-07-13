extends Node
## Si el proceso termina con código 0, carga la escena desde user://cache/
## Borra el archivo temporal INMEDIATAMENTE tras el load(), sin importar
## si el load fue exitoso o no.

const SERVER_URL := "http://127.0.0.1:8000/verify"
const CRITICAL_GD_PATH := "res://scripts/critical.gd"
const DECRYPT_CLIENT_EXE := "res://scripts/bin/decrypt_client.exe"
const CACHE_DIR := "user://cache/"

func load_encrypted_scene(scene_filename: String) -> Node:
	var encrypted_res_path := "res://scenes/%s.enc" % scene_filename
	var output_path := CACHE_DIR + scene_filename

	var dir := DirAccess.open("user://")
	if dir and not dir.dir_exists("cache"):
		dir.make_dir("cache")

	var critical_gd_abs := ProjectSettings.globalize_path(CRITICAL_GD_PATH)
	var encrypted_scene_abs := ProjectSettings.globalize_path(encrypted_res_path)
	var output_abs := ProjectSettings.globalize_path(output_path)
	var exe_abs := ProjectSettings.globalize_path(DECRYPT_CLIENT_EXE)

	var args := [
		critical_gd_abs,
		encrypted_scene_abs,
		scene_filename,
		output_abs,
		SERVER_URL
	]

	var output := []
	var exit_code := OS.execute(exe_abs, args, output, true)

	if exit_code != 0:
		push_error("Acceso denegado por el servidor DRM para la escena '%s'." % scene_filename)
		push_error("Detalle: %s" % str(output))
		return null

	if not FileAccess.file_exists(output_path):
		push_error("El proceso de desencriptado terminó bien pero no se encontró el archivo de salida.")
		return null

	var packed_scene: PackedScene = load(output_path)

	_delete_temp_file(output_path)

	if packed_scene == null:
		push_error("No se pudo cargar la escena descifrada '%s'." % scene_filename)
		return null

	return packed_scene.instantiate()


func _delete_temp_file(path: String) -> void:
	if FileAccess.file_exists(path):
		var dir := DirAccess.open(CACHE_DIR)
		if dir:
			dir.remove(path.get_file())


## Ejemplo de uso desde otra escena/nodo:
##
##   var loader := preload("res://scripts/SceneLoader.gd").new()
##   var level_node = loader.load_encrypted_scene("level1.tscn")
##   if level_node:
##       get_tree().current_scene.add_child(level_node)
##   else:
##       get_tree().change_scene_to_file("res://scenes/access_denied.tscn")
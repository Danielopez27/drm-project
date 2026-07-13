extends Node

var UNLOCK_CONTENT_KEY

func query_scene_change(new_scene_name : String) -> void:
	var path : String = "res://assets/" + new_scene_name + ".tscn"
	
	### Copy target scene
	var raw_encrypted_scene : PackedByteArray = FileAccess.get_file_as_bytes(path)
	print("Copy")
	
	### Save a copy to decrypt
	var path_copy : String = "res://assets/" + new_scene_name + "_temp.tscn"
	var copy : FileAccess = FileAccess.open(path_copy, FileAccess.WRITE)
	copy.store_buffer(raw_encrypted_scene)
	copy.close()
	print("Clone")
	
	### Decrypt the copy
	# TODO OS.execute("") 
	
	### Load the decrypted scene 
	if ResourceLoader.load_threaded_request(path_copy) != OK:
		printerr("Fatal: couldn't load decrypted scene" + new_scene_name)
	var scene_to_load : PackedScene = ResourceLoader.load_threaded_get(path_copy)
	print("Load")
	
	### Delete the copy ASAP
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path_copy))
	print("Clean")
	
	### Change current scene
	get_tree().change_scene_to_packed(scene_to_load)
	print("Change")

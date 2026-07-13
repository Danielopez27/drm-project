extends CharacterBody2D

const SPEED = 300.0
const JUMP_VELOCITY = -400.0

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta):
	if not is_on_floor():
		velocity.y += gravity * delta

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	var direction = Input.get_axis("left", "right")
	if direction:
		velocity.x = direction * SPEED
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)

	move_and_slide()
	
#@export var debug_run_now: bool = false:
	#set(value):
		#debug_run_now = false
		#_change_to_unencrypted_resource()
		#
#func _change_to_unencrypted_resource():
	## Get the path of the appropiate texture
	#var base_dir = "res://" if OS.has_feature("editor") else OS.get_executable_path().get_base_dir()
	#print(base_dir)
	#var asset_path : String = "C:/Users/Emilio/Documents/GitHub/drm-project/godot_client/pikachu.png" 
	#var err : Error = ResourceLoader.load_threaded_request(asset_path)
	#if err != OK:
		#printerr(name + " couldn't load asset at " + asset_path)
	#
	#var correct_image : CompressedTexture2D = ResourceLoader.load_threaded_get(asset_path)
	#$Icon.texture = correct_image

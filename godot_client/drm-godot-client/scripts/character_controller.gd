extends CharacterBody2D

const SPEED = 300.0
const MAX_SPEED = 1000.0
const JUMP_VELOCITY = 800.0

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta):
	var direction = Input.get_axis("left", "right")
	if direction:
		if up_direction.y:
			velocity.x = direction * SPEED * (- up_direction.y) 
		elif up_direction.x:
			velocity.y = direction * SPEED * (up_direction.x) 
	else:
		if up_direction.y:
			velocity.x = move_toward(velocity.x, 0, SPEED)
		elif up_direction.x:
			velocity.y = move_toward(velocity.y, 0, SPEED)
	
	if not is_on_floor():
		velocity.y += gravity * delta * up_direction.dot(Vector2.UP)
		velocity.x += gravity * delta * up_direction.dot(Vector2.LEFT)
		
	if Input.is_action_just_pressed("ui_accept"):
		rotate_1()
		
	if Input.is_action_just_pressed("ui_cancel"):
		rotate_2()

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY * up_direction.dot(Vector2.DOWN) 
		velocity.x = JUMP_VELOCITY * up_direction.dot(Vector2.RIGHT)

	

	move_and_slide()
	
func rotate_1() -> void:
	$AnimationPlayer.play("rotation_1")
	up_direction = Vector2(0, 1)
	
func rotate_2() -> void:
	$AnimationPlayer.play("rotation_2")
	up_direction = Vector2(1, 0)

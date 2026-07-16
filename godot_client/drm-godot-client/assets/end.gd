extends Area2D

func _ready() -> void:
	$AnimationPlayer.play("hover")

func _on_body_entered(body: CharacterBody2D) -> void:
	$AnimationPlayer.play("attained")
	await get_tree().create_timer(3).timeout
	if (body.has_method("rotate_1")):
		body.rotate_1()

extends Area2D

func _ready() -> void:
	$AnimationPlayer.play("hover")

func _on_body_entered(_body: Node2D) -> void:
	$AnimationPlayer.play("attained")

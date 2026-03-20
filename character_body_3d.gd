extends CharacterBody3D

const MOUSE_SENSITIVITY = 0.003

@onready var camera = $Camera3D
@onready var raycast = $Camera3D/RayCast3D

# This creates a box in the Inspector so we can tell the script exactly WHICH object is the target
@export var target_node: Node3D

# Your exact, hardcoded coordinate list! 
# You can change these numbers anytime to make them closer, further, higher, or lower.
var target_positions: Array[Vector3] = [
	Vector3(0, 1.5, -5),   # Center, close
	Vector3(-3, 2, -8),    # Left, a bit higher, further away
	Vector3(3, 1, -6),     # Right, lower
	Vector3(0, 3, -10),    # Center, high up, far away
	Vector3(-4, 0.5, -4)   # Far left, very low, close
]

var current_target_index = 0

func _ready() -> void:
	# Locks the mouse to the game window
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
	# 1. Look around
	if event is InputEventMouseMotion:
		rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
		camera.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-90), deg_to_rad(90))

	# 2. Shoot
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			shoot()

func shoot():
	if raycast.is_colliding():
		var hit_object = raycast.get_collider()
		
		# If the object our laser hit is our assigned target...
		if hit_object == target_node:
			# Move to the next coordinate in our list
			current_target_index += 1
			
			# If we reach the end of the list, loop back to the first coordinate
			if current_target_index >= target_positions.size():
				current_target_index = 0
				
			# Instantly teleport the target to the new exact coordinate
			target_node.global_position = target_positions[current_target_index]
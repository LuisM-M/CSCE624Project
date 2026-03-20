extends CharacterBody3D

const MOUSE_SENSITIVITY = 0.003

# These let the script easily find your camera and laser
@onready var camera = $Camera3D
@onready var raycast = $Camera3D/RayCast3D

func _ready() -> void:
	# Locks the mouse to the game window and hides the default cursor
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
	# 1. Handle looking around
	if event is InputEventMouseMotion:
		# Look left/right (rotates the body)
		rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
		# Look up/down (rotates the camera)
		camera.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
		# Prevents the camera from doing a full backflip
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-90), deg_to_rad(90))

	# 2. Handle Shooting (Left Mouse Click)
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			shoot()

func shoot():
	# Check if our invisible laser is touching anything solid
	if raycast.is_colliding():
		var hit_object = raycast.get_collider()
		
		# If the object we hit is our target (the RigidBody3D), make it disappear!
		if hit_object is RigidBody3D:
			hit_object.queue_free()
extends CharacterBody3D

const MOUSE_SENSITIVITY = 0.003

@onready var camera = $Camera3D
@onready var raycast = $Camera3D/RayCast3D
@export var target_node: Node3D

var target_positions: Array[Vector3] = [
	Vector3(0, 1.5, -5),
	Vector3(-3, 2, -8),
	Vector3(3, 1, -6),
	Vector3(0, 3, -10),
	Vector3(-4, 0.5, -4)
]
var current_target_index = 0

# --- DATA LOGGING VARIABLES ---
var start_time: int = 0
var total_shots: int = 0
var tracking_data: Array = [] # This holds our rows of data

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	start_time = Time.get_ticks_msec()
	
	# Create the CSV Header
	tracking_data.append("Timestamp_ms,Event_Type,Cam_Rot_X,Player_Rot_Y,Hit_Target_Index")

func _input(event: InputEvent) -> void:
	# Pressing Escape saves the data to a file and closes the game
	if event is InputEventKey and event.keycode == KEY_ESCAPE and event.pressed:
		save_data_to_csv()
		get_tree().quit()

	# 1. Look around & Log Mouse Movement
	if event is InputEventMouseMotion:
		rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
		camera.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-90), deg_to_rad(90))
		
		# Log continuous movement
		var timestamp = Time.get_ticks_msec() - start_time
		var log_string = "%d,MouseMove,%f,%f,-1" % [timestamp, camera.rotation.x, rotation.y]
		tracking_data.append(log_string)

	# 2. Shoot & Log Shot Data
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			shoot()

func shoot():
	total_shots += 1
	var timestamp = Time.get_ticks_msec() - start_time
	var hit_index = -1 # Default to -1 (meaning a miss)

	if raycast.is_colliding():
		var hit_object = raycast.get_collider()
		
		if hit_object == target_node:
			hit_index = current_target_index # Record which target we successfully hit
			current_target_index += 1
			if current_target_index >= target_positions.size():
				current_target_index = 0
			target_node.global_position = target_positions[current_target_index]
	
	# Log the shot event
	var log_string = "%d,ShotFired,%f,%f,%d" % [timestamp, camera.rotation.x, rotation.y, hit_index]
	tracking_data.append(log_string)

func save_data_to_csv():
	# user:// points to Godot's safe data folder on your local computer
	var file = FileAccess.open("user://aim_trial_data.csv", FileAccess.WRITE)
	for line in tracking_data:
		file.store_line(line)
	
	# This prints the exact folder path in your Godot output console so you can find the file!
	print("Trial Saved! File located at: ", ProjectSettings.globalize_path("user://aim_trial_data.csv"))
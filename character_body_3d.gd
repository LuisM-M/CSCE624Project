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
	Vector3(-4, 1.25, -4)
]
var current_target_index = 0

# --- DATA LOGGING VARIABLES ---
var start_time: int = 0
var total_shots: int = 0
var tracking_data: Array = []

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	start_time = Time.get_ticks_msec()

	# Put the target at the initial position explicitly.
	target_node.global_position = target_positions[current_target_index]

	# Create CSV header
	tracking_data.append(
		"Timestamp_ms,Event_Type,Cam_Rot_X,Player_Rot_Y,Target_Index,Target_Pos_X,Target_Pos_Y,Target_Pos_Z"
	)

	# Log the very first target spawn
	log_target_spawned()

func _input(event: InputEvent) -> void:
	# Press Escape to save and quit
	if event is InputEventKey and event.keycode == KEY_ESCAPE and event.pressed:
		save_data_to_csv()
		get_tree().quit()

	# Mouse look
	if event is InputEventMouseMotion:
		rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
		camera.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-90), deg_to_rad(90))

		log_mouse_move()

	# Mouse click shoot
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			shoot()

func current_timestamp() -> int:
	return Time.get_ticks_msec() - start_time

func current_target_position() -> Vector3:
	return target_positions[current_target_index]

func log_target_spawned() -> void:
	var timestamp = current_timestamp()
	var target_pos = current_target_position()

	var log_string = "%d,TargetSpawned,%f,%f,%d,%f,%f,%f" % [
		timestamp,
		camera.rotation.x,
		rotation.y,
		current_target_index,
		target_pos.x,
		target_pos.y,
		target_pos.z
	]

	tracking_data.append(log_string)

func log_mouse_move() -> void:
	var timestamp = current_timestamp()
	var target_pos = current_target_position()

	var log_string = "%d,MouseMove,%f,%f,%d,%f,%f,%f" % [
		timestamp,
		camera.rotation.x,
		rotation.y,
		current_target_index,
		target_pos.x,
		target_pos.y,
		target_pos.z
	]

	tracking_data.append(log_string)

func shoot() -> void:
	total_shots += 1
	var timestamp = current_timestamp()
	var hit_index = -1
	var target_pos = current_target_position()

	raycast.force_raycast_update()

	if raycast.is_colliding():
		var hit_object = raycast.get_collider()

		if hit_object == target_node:
			hit_index = current_target_index

			# Log the successful shot before advancing target
			var hit_log = "%d,ShotFired,%f,%f,%d,%f,%f,%f" % [
				timestamp,
				camera.rotation.x,
				rotation.y,
				hit_index,
				target_pos.x,
				target_pos.y,
				target_pos.z
			]
			tracking_data.append(hit_log)

			# Advance target
			current_target_index += 1
			if current_target_index >= target_positions.size():
				current_target_index = 0

			target_node.global_position = target_positions[current_target_index]

			# Log the next target spawn
			log_target_spawned()
			return

	# Miss case
	var miss_log = "%d,ShotFired,%f,%f,%d,%f,%f,%f" % [
		timestamp,
		camera.rotation.x,
		rotation.y,
		hit_index,
		target_pos.x,
		target_pos.y,
		target_pos.z
	]
	tracking_data.append(miss_log)

func save_data_to_csv() -> void:
	var filename = "user://aim_trial_data_%d.csv" % Time.get_unix_time_from_system()
	var file = FileAccess.open(filename, FileAccess.WRITE)

	if file == null:
		push_error("Failed to open file for writing: " + filename)
		return

	for line in tracking_data:
		file.store_line(line)

	file.close()
	print("Trial Saved! File located at: ", ProjectSettings.globalize_path(filename))
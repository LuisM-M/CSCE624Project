extends CharacterBody3D

const MOUSE_SENSITIVITY = 0.003
const TRIALS_PER_DIFFICULTY = 24


@onready var camera = $Camera3D
@onready var raycast = $Camera3D/RayCast3D
@export var target_node: Node3D
@export var participant_id: String = "unknown"

# Easy / Medium / Hard target sets
# Same general directional structure, larger offsets for higher difficulty.
var easy_targets: Array[Vector3] = [
	Vector3(-10.6, 3.4, -8.0), # left
	Vector3(-3.4, 3.4, -8.0),  # right

	Vector3(-7.0, 6.0, -8.0),  # up
	Vector3(-7.0, 2.1, -8.0),  # down

	Vector3(-9.6, 4.4, -8.0),  # up-left
	Vector3(-4.4, 4.4, -8.0),  # up-right

	Vector3(-9.6, 2.4, -8.0),  # down-left
	Vector3(-4.4, 2.4, -8.0)   # down-right
]


var hard_targets: Array[Vector3] = [
	Vector3(-12.8, 3.4, -8.0), # left
	Vector3(-1.2, 3.4, -8.0),  # right

	Vector3(-7.0, 7.0, -8.0),  # up
	Vector3(-7.0, 1.4, -8.0),  # down

	Vector3(-11.4, 4.8, -8.0), # up-left
	Vector3(-2.6, 4.8, -8.0),  # up-right

	Vector3(-11.4, 2.0, -8.0), # down-left
	Vector3(-2.6, 2.0, -8.0)   # down-right
]

# Each trial will be a dictionary like:
# {
#   "difficulty": "easy",
#   "target_index": 3,
#   "target_position": Vector3(...)
# }
var trial_sequence: Array = []
var current_trial_index: int = 0

# --- DATA LOGGING VARIABLES ---
var start_time: int = 0
var total_shots: int = 0
var tracking_data: Array = []

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	start_time = Time.get_ticks_msec()

	build_trial_sequence()

	# Create CSV header
	tracking_data.append(
		"Timestamp_ms,Event_Type,Difficulty,Trial_Index,Cam_Rot_X,Player_Rot_Y,Target_Index,Target_Pos_X,Target_Pos_Y,Target_Pos_Z"
	)

	if trial_sequence.is_empty():
		push_error("Trial sequence is empty.")
		return

	start_current_trial()

func _input(event: InputEvent) -> void:
	# Press Escape to save and quit early
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

func build_trial_sequence() -> void:
	trial_sequence.clear()

	append_trials_for_difficulty("easy", easy_targets)
	append_trials_for_difficulty("hard", hard_targets)

func append_trials_for_difficulty(difficulty_name: String, target_array: Array[Vector3]) -> void:
	var target_count = target_array.size()
	if target_count == 0:
		return

	for i in range(TRIALS_PER_DIFFICULTY):
		var target_index = i % target_count
		trial_sequence.append({
			"difficulty": difficulty_name,
			"target_index": target_index,
			"target_position": target_array[target_index]
		})

func start_current_trial() -> void:
	if current_trial_index >= trial_sequence.size():
		print("All trials complete.")
		save_data_to_csv()
		get_tree().quit()
		return

	reset_aim_to_center()

	var target_pos = current_target_position()
	target_node.global_position = target_pos

	log_target_spawned()

func reset_aim_to_center() -> void:
	rotation.y = 0.0
	camera.rotation.x = 0.3

func current_timestamp() -> int:
	return Time.get_ticks_msec() - start_time

func current_trial_data() -> Dictionary:
	return trial_sequence[current_trial_index]

func current_difficulty() -> String:
	return str(current_trial_data().get("difficulty", "unknown"))

func current_target_index() -> int:
	return int(current_trial_data().get("target_index", -1))

func current_target_position() -> Vector3:
	return current_trial_data().get("target_position", Vector3.ZERO)

func log_target_spawned() -> void:
	var timestamp = current_timestamp()
	var target_pos = current_target_position()

	var log_string = "%d,TargetSpawned,%s,%d,%f,%f,%d,%f,%f,%f" % [
		timestamp,
		current_difficulty(),
		current_trial_index,
		camera.rotation.x,
		rotation.y,
		current_target_index(),
		target_pos.x,
		target_pos.y,
		target_pos.z
	]

	tracking_data.append(log_string)

func log_mouse_move() -> void:
	if current_trial_index >= trial_sequence.size():
		return

	var timestamp = current_timestamp()
	var target_pos = current_target_position()

	var log_string = "%d,MouseMove,%s,%d,%f,%f,%d,%f,%f,%f" % [
		timestamp,
		current_difficulty(),
		current_trial_index,
		camera.rotation.x,
		rotation.y,
		current_target_index(),
		target_pos.x,
		target_pos.y,
		target_pos.z
	]

	tracking_data.append(log_string)

func shoot() -> void:
	if current_trial_index >= trial_sequence.size():
		return

	total_shots += 1
	var timestamp = current_timestamp()
	var hit_index = -1
	var target_pos = current_target_position()

	raycast.force_raycast_update()

	if raycast.is_colliding():
		var hit_object = raycast.get_collider()

		if hit_object == target_node:
			hit_index = current_target_index()

			var hit_log = "%d,ShotFired,%s,%d,%f,%f,%d,%f,%f,%f" % [
				timestamp,
				current_difficulty(),
				current_trial_index,
				camera.rotation.x,
				rotation.y,
				hit_index,
				target_pos.x,
				target_pos.y,
				target_pos.z
			]
			tracking_data.append(hit_log)

			current_trial_index += 1
			start_current_trial()
			return

	# Miss case
	var miss_log = "%d,ShotFired,%s,%d,%f,%f,%d,%f,%f,%f" % [
		timestamp,
		current_difficulty(),
		current_trial_index,
		camera.rotation.x,
		rotation.y,
		hit_index,
		target_pos.x,
		target_pos.y,
		target_pos.z
	]
	tracking_data.append(miss_log)

func save_data_to_csv() -> void:
	var filename = "user://%s_aim_trial_data_%d.csv" % [
		participant_id,
		Time.get_unix_time_from_system()
	]
	var file = FileAccess.open(filename, FileAccess.WRITE)

	if file == null:
		push_error("Failed to open file for writing: " + filename)
		return

	for line in tracking_data:
		file.store_line(line)

	file.close()
	print("Trial Saved! File located at: ", ProjectSettings.globalize_path(filename))

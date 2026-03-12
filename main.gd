extends Node2D

const TARGET_RADIUS: float = 30.0
const TARGET_COLOR: Color = Color(1, 0, 0) # Red

var target_center: Vector2 = Vector2.ZERO
var rng: RandomNumberGenerator
var targets_clicked: int = 0
var tracking_data: Array = []
var current_stroke_data: Array = []


func _ready() -> void:
	rng = RandomNumberGenerator.new()
	rng.randomize()
	_spawn_new_target()


func _draw() -> void:
	# Draw the circular target at the current center position.
	if target_center != Vector2.ZERO:
		draw_circle(target_center, TARGET_RADIUS, TARGET_COLOR)


func _process(delta: float) -> void:
	# Continuously record mouse trajectory for the current stroke.
	var mouse_pos: Vector2 = get_viewport().get_mouse_position()
	var t_ms: int = Time.get_ticks_msec()
	current_stroke_data.append({
		"time_ms": t_ms,
		"position": mouse_pos,
	})


func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton \
			and event.button_index == MOUSE_BUTTON_LEFT \
			and event.pressed:
		var mouse_pos: Vector2 = event.position
		# Check if the click is inside the target circle.
		if mouse_pos.distance_to(target_center) <= TARGET_RADIUS:
			# Record this successful hit with its full mouse trajectory.
			tracking_data.append({
				"target_id": targets_clicked + 1,
				"target_position": target_center,
				"click_position": mouse_pos,
				"stroke": current_stroke_data.duplicate(true),
			})

			# Reset stroke buffer for the next target.
			current_stroke_data.clear()

			targets_clicked += 1

			# If we've reached exactly 5 successful hits, print and quit.
			if targets_clicked == 5:
				_export_to_csv()
				get_tree().quit()
			else:
				# Instantly "remove" the current circle and spawn a new one.
				_spawn_new_target()


func _spawn_new_target() -> void:
	var viewport_rect: Rect2 = get_viewport_rect()
	var size: Vector2 = viewport_rect.size

	# Ensure the target stays fully inside the window bounds.
	var min_x: float = TARGET_RADIUS
	var max_x: float = max(TARGET_RADIUS, size.x - TARGET_RADIUS)
	var min_y: float = TARGET_RADIUS
	var max_y: float = max(TARGET_RADIUS, size.y - TARGET_RADIUS)

	target_center.x = rng.randf_range(min_x, max_x)
	target_center.y = rng.randf_range(min_y, max_y)

	queue_redraw() 


func _export_to_csv() -> void:
	var file_path = "user://trajectory_data.csv"
	var file = FileAccess.open(file_path, FileAccess.WRITE)
	if file == null:
		push_error("Failed to open CSV file for writing: " + file_path)
		return

	# Header row
	file.store_line("Target_ID,Timestamp_ms,X_Pos,Y_Pos")

	# Each entry in tracking_data is a dictionary
	for entry in tracking_data:
		var target_id: int = entry.get("target_id", 0)
		var stroke: Array = entry.get("stroke", [])

		for sample in stroke:
			var t_ms: int = sample.get("time_ms", 0)
			var pos: Vector2 = sample.get("position", Vector2.ZERO)
			var line = "%s,%s,%s,%s" % [target_id, t_ms, pos.x, pos.y]
			file.store_line(line)

	file.close()
	print("Data successfully exported to: ", file_path)

import csv
import math
import os
import statistics
import sys


def distance_xy(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def parse_filename_metadata(path):
    """
    Expected filename format:
    <participant>_<session>_raw.csv

    Examples:
    richard_s1_raw.csv
    alex_s2_raw.csv

    Returns:
    (participant_id, session_id)
    """
    base = os.path.basename(path)
    name_without_ext = os.path.splitext(base)[0]
    parts = name_without_ext.split("_")

    if len(parts) < 3:
        raise ValueError(
            f"Filename '{base}' does not match expected format "
            f"'<participant>_<session>_raw.csv'"
        )

    participant_id = parts[0]
    session_id = parts[1]

    return participant_id, session_id


def process_csv(input_path):
    trials = []
    current_trial = None
    participant_id, session_id = parse_filename_metadata(input_path)

    with open(input_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            event = row["Event_Type"]

            timestamp = float(row["Timestamp_ms"])
            cam_x = float(row["Cam_Rot_X"])
            player_y = float(row["Player_Rot_Y"])
            target_index = int(row["Target_Index"])
            difficulty = row.get("Difficulty", "unknown")
            trial_index = int(row.get("Trial_Index", -1))
            target_pos_x = float(row["Target_Pos_X"])
            target_pos_y = float(row["Target_Pos_Y"])
            target_pos_z = float(row["Target_Pos_Z"])

            if event == "TargetSpawned":
                current_trial = {
                    "participant_id": participant_id,
                    "session_id": session_id,
                    "difficulty": difficulty,
                    "trial_index": trial_index,
                    "spawn_time": timestamp,
                    "target_index": target_index,
                    "target_position": (target_pos_x, target_pos_y, target_pos_z),
                    "points": [],
                    "misses": 0,
                }

            elif event == "MouseMove" and current_trial is not None:
                # Store points as (x, y, t), where x=player_y and y=cam_x
                current_trial["points"].append((player_y, cam_x, timestamp))

            elif event == "ShotFired" and current_trial is not None:
                hit_index = int(row["Target_Index"])

                if hit_index == -1:
                    current_trial["misses"] += 1
                    continue

                current_trial["hit_time"] = timestamp
                trials.append(current_trial)
                current_trial = None

    return trials


def safe_divide(a, b):
    return a / b if abs(b) > 1e-12 else 0.0


def compute_path_length(points):
    total = 0.0
    for i in range(1, len(points)):
        x1, y1, _ = points[i - 1]
        x2, y2, _ = points[i]
        total += distance_xy(x1, y1, x2, y2)
    return total


def compute_segment_velocities(points):
    velocities = []
    for i in range(1, len(points)):
        x1, y1, t1 = points[i - 1]
        x2, y2, t2 = points[i]
        dt = t2 - t1
        if dt <= 0:
            continue
        dist = distance_xy(x1, y1, x2, y2)
        velocities.append(dist / dt)
    return velocities


def compute_direction_changes(points):
    if len(points) < 4:
        return 0

    turn_signs = []

    for i in range(2, len(points)):
        x0, y0, _ = points[i - 2]
        x1, y1, _ = points[i - 1]
        x2, y2, _ = points[i]

        dx1 = x1 - x0
        dy1 = y1 - y0
        dx2 = x2 - x1
        dy2 = y2 - y1

        cross = dx1 * dy2 - dy1 * dx2

        if cross > 1e-12:
            turn_signs.append(1)
        elif cross < -1e-12:
            turn_signs.append(-1)

    changes = 0
    for i in range(1, len(turn_signs)):
        if turn_signs[i] != turn_signs[i - 1]:
            changes += 1

    return changes


def compute_bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    return xmin, xmax, ymin, ymax


def compute_initial_angle_features(points):
    eps = 1e-12
    x0, y0, _ = points[0]

    for i in range(1, len(points)):
        xi, yi, _ = points[i]
        dist = distance_xy(x0, y0, xi, yi)
        if dist > eps:
            dx = xi - x0
            dy = yi - y0
            return dx / dist, dy / dist

    return 0.0, 0.0


def compute_rubine_rotation_features(points):
    if len(points) < 3:
        return 0.0, 0.0, 0.0

    total_rel = 0.0
    total_abs = 0.0
    total_sq = 0.0

    for i in range(2, len(points)):
        x0, y0, _ = points[i - 2]
        x1, y1, _ = points[i - 1]
        x2, y2, _ = points[i]

        dx_prev = x1 - x0
        dy_prev = y1 - y0
        dx_curr = x2 - x1
        dy_curr = y2 - y1

        if (abs(dx_prev) < 1e-12 and abs(dy_prev) < 1e-12) or (
            abs(dx_curr) < 1e-12 and abs(dy_curr) < 1e-12
        ):
            continue

        cross = dx_curr * dy_prev - dx_prev * dy_curr
        dot = dx_curr * dx_prev + dy_curr * dy_prev

        theta = math.atan2(cross, dot)

        total_rel += theta
        total_abs += abs(theta)
        total_sq += theta * theta

    return total_rel, total_abs, total_sq


def compute_rubine_features(points):
    eps = 1e-12

    f1, f2 = compute_initial_angle_features(points)

    xmin, xmax, ymin, ymax = compute_bbox(points)
    width = xmax - xmin
    height = ymax - ymin

    f3 = math.sqrt(width * width + height * height)
    f4 = math.atan2(height, width)

    x_start, y_start, _ = points[0]
    x_end, y_end, _ = points[-1]
    f5 = distance_xy(x_start, y_start, x_end, y_end)

    if f5 > eps:
        f6 = (x_end - x_start) / f5
        f7 = (y_end - y_start) / f5
    else:
        f6 = 0.0
        f7 = 0.0

    f8 = compute_path_length(points)

    f9, f10, f11 = compute_rubine_rotation_features(points)

    velocities = compute_segment_velocities(points)
    f12 = 0.0
    if velocities:
        f12 = max(v * v for v in velocities)

    f13 = points[-1][2] - points[0][2]

    return {
        "rubine_f1_initial_cos": f1,
        "rubine_f2_initial_sin": f2,
        "rubine_f3_bbox_diag": f3,
        "rubine_f4_bbox_angle": f4,
        "rubine_f5_endpoint_dist": f5,
        "rubine_f6_overall_cos": f6,
        "rubine_f7_overall_sin": f7,
        "rubine_f8_stroke_length": f8,
        "rubine_f9_total_rotation": f9,
        "rubine_f10_total_abs_rotation": f10,
        "rubine_f11_total_sq_rotation": f11,
        "rubine_f12_max_speed_sq": f12,
        "rubine_f13_duration": f13,
    }


def extract_features(trials):
    feature_rows = []

    for trial in trials:
        points = trial["points"]

        if len(points) < 2:
            continue

        path_length = compute_path_length(points)
        start_time = trial["spawn_time"]
        end_time = trial["hit_time"]
        duration = end_time - start_time
        mean_velocity = safe_divide(path_length, duration)

        x_start, y_start, _ = points[0]
        x_end, y_end, _ = points[-1]
        straight_line_distance = distance_xy(x_start, y_start, x_end, y_end)
        efficiency_ratio = safe_divide(straight_line_distance, path_length)

        velocities = compute_segment_velocities(points)
        max_velocity = max(velocities) if velocities else 0.0
        velocity_std = statistics.pstdev(velocities) if len(velocities) >= 2 else 0.0

        direction_changes = compute_direction_changes(points)

        xmin, xmax, ymin, ymax = compute_bbox(points)
        bbox_width = xmax - xmin
        bbox_height = ymax - ymin

        rubine = compute_rubine_features(points)

        row = {
            "participant_id": trial["participant_id"],
            "session_id": trial["session_id"],
            "difficulty": trial["difficulty"],
            "trial_index": trial["trial_index"],
            "target_index": trial["target_index"],
            "mean_velocity": mean_velocity,
            "num_points": len(points),
            "misses": trial["misses"],
            "efficiency_ratio": efficiency_ratio,
            "max_velocity": max_velocity,
            "velocity_std": velocity_std,
            "direction_changes": direction_changes,
            "bbox_width": bbox_width,
            "bbox_height": bbox_height,
        }

        row.update(rubine)
        feature_rows.append(row)

    return feature_rows


def write_output(rows, output_path):
    if len(rows) == 0:
        print("No trials found.")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analysis/segment_trials.py <input_csv_path>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    participant_id, session_id = parse_filename_metadata(input_path)

    output_filename = f"{participant_id}_{session_id}_segmented_trials.csv"

    repo_processed_dir = os.path.join(
        os.path.dirname(__file__),
        "data",
        "processed"
    )

    output_path = os.path.join(repo_processed_dir, output_filename)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    trials = process_csv(input_path)
    print(f"Segmented {len(trials)} trials")

    features = extract_features(trials)
    write_output(features, output_path)

    print(f"Saved features to {output_path}")


if __name__ == "__main__":
    main()
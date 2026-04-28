# CSCE 624 Aim Trajectory User Identification Project

This project collects mouse aiming trajectories from a Godot 3D target acquisition task and uses them for user identification experiments inspired by sketch-recognition stroke analysis methods.

Each trial produces a trajectory:

TargetSpawned → MouseMove events → ShotFired

These trajectories are converted into feature datasets for classification experiments.

---

## Requirements

- Godot Engine (standard version, not .NET)
- Python 3

Python dependencies:
pip install pandas numpy scikit-learn matplotlib

---

## Running the Experiment (Godot)

1. Install Godot
2. Open Godot
3. Import this repository using `project.godot`
4. Open the scene: 3d_test_arena.tscn

5. Run the scene

The experiment presents aiming targets and automatically logs mouse trajectory data.

Press Escape to save and exit early if needed.

After completion, a CSV telemetry file is generated automatically.

---

## Running Without Godot (Executable Export)

Godot can export a standalone executable so participants do not need the engine installed.

To export:

1. Open project in Godot
2. Go to Project → Export
3. Add a target platform
4. Export executable

Participants can run the executable and send back generated CSV files.

---

## Locating Generated CSV Files

Godot stores telemetry in its user data directory.

On Windows:

Press Win + R and run: %appdata%\Godot\app_userdata\

Open the project folder and retrieve: trajectory_data_*.csv

Move these into: analysis/data/raw/

---

## Data Pipeline

The analysis workflow is:
raw telemetry CSV
↓
segment_trials.py
↓
segmented trajectory dataset

---

## Segmenting Trajectories

Place raw CSV files in: analysis/data/raw/

Run: python analysis/segment_trials.py

This converts event-level telemetry into one row per trajectory.

Example output features:
target_index
duration_ms
path_length
mean_velocity
num_points
misses

Saved to:
analysis/data/segmented_trials.csv

---

## Project Structure
CSCE624Project/
├── analysis/
│ ├── data/
│ │ └── raw/
│ └── segment_trials.py
├── resultsDisplay/
├── 3d_test_arena.tscn
├── character_body_3d.gd
├── main.gd
├── main.tscn
└── project.godot

---

## Notes

- Generated CSV telemetry files should not be committed
- Raw data belongs in `analysis/data/raw/`
- The main experiment logic is implemented in: character_body_3d.gd

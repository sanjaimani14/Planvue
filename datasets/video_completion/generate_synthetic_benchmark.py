"""
Generator for Controlled Synthetic Video Completion Dataset.
Generates scene_001, scene_002, and scene_003 with exact CAD ground truth,
simulated camera trajectories, observed surfaces, and ground truth hidden surfaces.
"""
from pathlib import Path
import json
import math

DATASETS_DIR = Path(__file__).resolve().parent

def create_synthetic_completion_dataset():
    scenes = [
        {
            "id": "scene_001",
            "name": "Rectangular Studio with Occluded Wardrobe Wall",
            "bounds": {"min": [-2.5, 0.0, -2.0], "max": [2.5, 2.8, 2.0]},
            "ground_truth_walls": [
                {"id": "gt_south", "start": [-2.5, 0.0, -2.0], "end": [2.5, 0.0, -2.0], "normal": [0, 0, -1], "observed": True},
                {"id": "gt_east", "start": [2.5, 0.0, -2.0], "end": [2.5, 0.0, 2.0], "normal": [1, 0, 0], "observed": True},
                {"id": "gt_west", "start": [-2.5, 0.0, -2.0], "end": [-2.5, 0.0, 2.0], "normal": [-1, 0, 0], "observed": True},
                {"id": "gt_north", "start": [-2.5, 0.0, 2.0], "end": [2.5, 0.0, 2.0], "normal": [0, 0, 1], "observed": False}  # Occluded!
            ],
            "camera_trajectory": [
                {"frame": 0, "pos": [-1.2, 1.4, -0.8], "dir": [0.3, -0.1, 0.9]},
                {"frame": 10, "pos": [-0.6, 1.4, -0.9], "dir": [0.4, -0.1, 0.8]},
                {"frame": 20, "pos": [0.0, 1.4, -1.0], "dir": [0.2, -0.1, 0.9]},
                {"frame": 30, "pos": [0.8, 1.4, -0.8], "dir": [-0.3, -0.1, 0.8]},
                {"frame": 40, "pos": [1.2, 1.4, -0.4], "dir": [-0.6, -0.1, 0.7]}
            ],
            "unseen_sector": {
                "id": "UNSEEN_NORTH",
                "bounds": {"min": [-2.5, 0.0, 1.2], "max": [2.5, 2.8, 2.0]},
                "reason": "Occluded behind interior wardrobe partition.",
                "gt_wall_id": "gt_north"
            }
        },
        {
            "id": "scene_002",
            "name": "L-Shaped Alcove Room",
            "bounds": {"min": [-3.0, 0.0, -2.5], "max": [3.0, 2.8, 2.5]},
            "ground_truth_walls": [
                {"id": "gt_w1", "start": [-3.0, 0.0, -2.5], "end": [3.0, 0.0, -2.5], "normal": [0, 0, -1], "observed": True},
                {"id": "gt_w2", "start": [3.0, 0.0, -2.5], "end": [3.0, 0.0, 1.0], "normal": [1, 0, 0], "observed": True},
                {"id": "gt_w3", "start": [-3.0, 0.0, -2.5], "end": [-3.0, 0.0, 2.5], "normal": [-1, 0, 0], "observed": True},
                {"id": "gt_w4", "start": [-3.0, 0.0, 2.5], "end": [1.0, 0.0, 2.5], "normal": [0, 0, 1], "observed": True},
                {"id": "gt_w5_hidden", "start": [1.0, 0.0, 1.0], "end": [1.0, 0.0, 2.5], "normal": [-1, 0, 0], "observed": False},
                {"id": "gt_w6_hidden", "start": [1.0, 0.0, 1.0], "end": [3.0, 0.0, 1.0], "normal": [0, 0, 1], "observed": False}
            ],
            "camera_trajectory": [
                {"frame": 0, "pos": [-2.0, 1.4, -1.5], "dir": [0.6, -0.1, 0.8]},
                {"frame": 15, "pos": [-1.0, 1.4, -1.0], "dir": [0.5, -0.1, 0.8]},
                {"frame": 30, "pos": [0.0, 1.4, -0.5], "dir": [0.4, -0.1, 0.8]}
            ],
            "unseen_sector": {
                "id": "UNSEEN_ALCOVE",
                "bounds": {"min": [1.0, 0.0, 1.0], "max": [3.0, 2.8, 2.5]},
                "reason": "Recessed alcove hidden around orthogonal blind corner.",
                "gt_wall_id": "gt_w5_hidden"
            }
        },
        {
            "id": "scene_003",
            "name": "Executive Meeting Room",
            "bounds": {"min": [-3.5, 0.0, -2.5], "max": [3.5, 3.0, 2.5]},
            "ground_truth_walls": [
                {"id": "gt_entry", "start": [-3.5, 0.0, -2.5], "end": [3.5, 0.0, -2.5], "normal": [0, 0, -1], "observed": True},
                {"id": "gt_glass_side", "start": [3.5, 0.0, -2.5], "end": [3.5, 0.0, 2.5], "normal": [1, 0, 0], "observed": True},
                {"id": "gt_hall_side", "start": [-3.5, 0.0, -2.5], "end": [-3.5, 0.0, 2.5], "normal": [-1, 0, 0], "observed": True},
                {"id": "gt_screen_wall", "start": [-3.5, 0.0, 2.5], "end": [3.5, 0.0, 2.5], "normal": [0, 0, 1], "observed": False}
            ],
            "camera_trajectory": [
                {"frame": 0, "pos": [-2.0, 1.4, -1.8], "dir": [0.3, -0.1, 0.9]},
                {"frame": 20, "pos": [0.0, 1.4, -1.6], "dir": [0.1, -0.1, 0.9]},
                {"frame": 40, "pos": [2.0, 1.4, -1.8], "dir": [-0.2, -0.1, 0.9]}
            ],
            "unseen_sector": {
                "id": "UNSEEN_DISPLAY",
                "bounds": {"min": [-3.5, 0.0, 1.5], "max": [3.5, 3.0, 2.5]},
                "reason": "Presentation wall outside camera turning radius.",
                "gt_wall_id": "gt_screen_wall"
            }
        }
    ]

    for s in scenes:
        sc_dir = DATASETS_DIR / s["id"]
        sc_dir.mkdir(parents=True, exist_ok=True)

        with open(sc_dir / "ground_truth_scene.json", "w") as f:
            json.dump({
                "scene_id": s["id"],
                "name": s["name"],
                "bounds": s["bounds"],
                "walls": s["ground_truth_walls"],
                "total_walls": len(s["ground_truth_walls"])
            }, f, indent=2)

        with open(sc_dir / "camera_path.json", "w") as f:
            json.dump(s["camera_trajectory"], f, indent=2)

        with open(sc_dir / "observed_region.json", "w") as f:
            json.dump([w for w in s["ground_truth_walls"] if w["observed"]], f, indent=2)

        with open(sc_dir / "unseen_region.json", "w") as f:
            json.dump(s["unseen_sector"], f, indent=2)

    print(f"Generated {len(scenes)} controlled synthetic completion benchmark datasets.")

if __name__ == "__main__":
    create_synthetic_completion_dataset()

import pytest
import os
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon

from ai.metric_calibration import calibrate_metric_scale
from reconstruction.geometry_constraints import (
    apply_geometry_constraints_and_repair,
    point_to_segment_projection
)
from reconstruction.scene_builder_3d import build_3d_building_scene
from reconstruction.spatial_coverage import compute_camera_spatial_coverage
from reconstruction.unseen_completion import generate_unseen_region_completion, export_mode_b_glb

def test_scale_calculation_door_heuristic():
    """Test metric scale calibration based on standard door widths."""
    mock_doors = [{"width_px": 45.0}, {"width_px": 45.0}]
    scale = calibrate_metric_scale([], mock_doors, [], (800, 1000))
    # 45 px / 0.90 m = 50 px/m
    assert scale["pixels_per_meter"] == 50.0
    assert scale["confidence"] in ["MEDIUM", "HIGH"]
    assert scale["meters_per_pixel"] == 0.02

def test_point_to_segment_projection():
    """Test projection of floating point onto line segment."""
    # Segment from (0, 0) to (10, 0), point at (5, 3)
    proj_x, proj_y, dist = point_to_segment_projection(5.0, 3.0, 0.0, 0.0, 10.0, 0.0)
    assert abs(proj_x - 5.0) < 1e-3
    assert abs(proj_y - 0.0) < 1e-3
    assert abs(dist - 3.0) < 1e-3

def test_duplicate_wall_elimination():
    """Test geometry constraints engine pruning duplicate walls."""
    walls = [
        {"id": "w1", "start": {"x": 100.0, "y": 100.0}, "end": {"x": 500.0, "y": 100.0}, "thickness_px": 10.0},
        {"id": "w2", "start": {"x": 102.0, "y": 101.0}, "end": {"x": 498.0, "y": 99.0}, "thickness_px": 10.0}, # duplicate
    ]
    repaired_w, _, _, _, logs = apply_geometry_constraints_and_repair(walls, [], [], [], ppm=50.0)
    assert len(repaired_w) == 1
    assert any(log["rule"] == "DUPLICATE_WALL_ELIMINATION" for log in logs)

def test_floating_door_snapping():
    """Test floating door snapped onto wall segment."""
    walls = [
        {"id": "w1", "start": {"x": 0.0, "y": 100.0}, "end": {"x": 500.0, "y": 100.0}, "thickness_px": 10.0}
    ]
    doors = [
        {"id": "d1", "position": {"x": 200.0, "y": 108.0}, "width_px": 45.0, "status": "OBSERVED"} # 8px away
    ]
    _, repaired_d, _, _, logs = apply_geometry_constraints_and_repair(walls, doors, [], [], ppm=50.0)
    assert len(repaired_d) == 1
    assert repaired_d[0]["position"]["y"] == 100.0
    assert repaired_d[0]["status"] == "CORRECTED"
    assert any(log["rule"] == "FLOATING_DOOR_WALL_ATTACHMENT" for log in logs)

def test_room_polygon_validity():
    """Test self-intersecting polygon repair via buffer(0)."""
    # Figure-8 bowtie self-intersecting polygon
    bow_tie = [
        {"x": 0.0, "y": 0.0},
        {"x": 100.0, "y": 100.0},
        {"x": 100.0, "y": 0.0},
        {"x": 0.0, "y": 100.0}
    ]
    rooms = [{"id": "r1", "name": "Test Room", "vertices": bow_tie, "status": "OBSERVED"}]
    _, _, _, repaired_rooms, logs = apply_geometry_constraints_and_repair([], [], [], rooms, ppm=50.0)
    assert len(repaired_rooms) >= 1
    for r in repaired_rooms:
        poly = Polygon([(p["x"], p["y"]) for p in r["vertices"]])
        assert poly.is_valid

def test_glb_scene_generation(tmp_path):
    """Test 3D scene construction and binary GLB export."""
    walls = [
        {"id": "w1", "start": {"x": 0.0, "y": 0.0}, "end": {"x": 200.0, "y": 0.0}, "thickness_m": 0.18, "status": "OBSERVED"}
    ]
    doors = [
        {"id": "d1", "position": {"x": 100.0, "y": 0.0}, "wall_id": "w1", "status": "OBSERVED"}
    ]
    glb_out = tmp_path / "test_building.glb"
    meta = build_3d_building_scene(walls, doors, [], [], ppm=50.0, wall_height=3.0, output_glb_path=str(glb_out))
    assert os.path.exists(glb_out)
    assert os.path.getsize(glb_out) > 500
    assert meta["mesh_count"] > 0

def test_spatial_coverage_computation():
    """Test camera visibility raycasting and coverage classification."""
    cam_poses = [
        {"position": [0.0, 1.4, 0.0], "rotation": np.eye(3).tolist(), "num_inliers": 100},
        {"position": [0.2, 1.4, 0.4], "rotation": np.eye(3).tolist(), "num_inliers": 100},
        {"position": [0.4, 1.4, 0.8], "rotation": np.eye(3).tolist(), "num_inliers": 100},
    ]
    points = [{"x": 0.0, "y": 1.4, "z": 2.0, "r": 200, "g": 200, "b": 200}]
    cov = compute_camera_spatial_coverage(cam_poses, points, grid_resolution=6)
    assert cov["total_voxels"] > 0
    assert cov["observed_pct"] >= 0.0
    assert cov["unseen_pct"] >= 0.0
    assert cov["total_space_volume_m3"] > 0.0

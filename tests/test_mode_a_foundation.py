import pytest
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.geometry.schema import Wall, Door, Window, Room, Scale
from backend.app.geometry.scale import (
    compute_metric_scale, calibrate_manual_scale, apply_metric_scale_to_scene
)
from backend.app.geometry.constraints import (
    validate_and_repair_geometry, point_to_segment_projection
)

client = TestClient(app)

def test_api_health():
    """Section 4 & 31: Test GET /api/health endpoint returns {'status': 'ok', 'service': 'plane-vue'}."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "plane-vue"}

def test_scale_calculation_priorities():
    """Section 17 & 31: Test scale calculation priority hierarchy."""
    # Priority 1: Explicit dimension annotation
    mock_dims = [{"value": 5.0, "start": [100.0, 100.0], "end": [350.0, 100.0], "raw_text": "5.0m"}]
    scale_dim = compute_metric_scale(mock_dims, [], [], (800, 1000))
    # 250 px / 5.0 m = 50.0 px/m -> 0.02 m/px
    assert scale_dim["confidence"] == "HIGH"
    assert scale_dim["source"] == "dimension_annotation"
    assert scale_dim["pixels_per_meter"] == 50.0
    assert scale_dim["meters_per_pixel"] == 0.02

    # Priority 3: Architectural door leaf heuristic (0.90m)
    mock_doors = [{"width_px": 45.0}]
    scale_door = compute_metric_scale([], mock_doors, [], (800, 1000))
    assert scale_door["confidence"] == "MEDIUM"
    assert scale_door["source"] == "architectural_reference"
    assert scale_door["pixels_per_meter"] == 50.0

    # Priority 5: Fallback when no evidence exists
    scale_fallback = compute_metric_scale([], [], [], (800, 1000))
    assert scale_fallback["confidence"] == "LOW"
    assert scale_fallback["meters_per_pixel"] is None
    assert scale_fallback["confidence_score"] == 0.0

def test_manual_scale_calibration():
    """Section 18 & 31: Test user manual scale calibration fallback."""
    pt1 = [100.0, 200.0]
    pt2 = [300.0, 200.0] # 200 px span
    calibrated = calibrate_manual_scale(pt1, pt2, known_distance=4.0, unit="m")
    assert calibrated["pixels_per_meter"] == 50.0
    assert calibrated["meters_per_pixel"] == 0.02
    assert calibrated["source"] == "manual_calibration"
    assert calibrated["confidence"] == "HIGH"

def test_coordinate_conversion():
    """Section 19 & 31: Test pixel -> metric conversion without destroying pixel coords."""
    walls = [{
        "id": "W001", "start": [100.0, 100.0], "end": [300.0, 100.0],
        "thickness_px": 10.0, "status": "OBSERVED"
    }]
    doors = [{"id": "D001", "position": [150.0, 100.0], "width_px": 45.0, "status": "OBSERVED"}]
    rooms = [{"id": "R001", "polygon": [[0.0, 0.0], [200.0, 0.0], [200.0, 200.0], [0.0, 200.0]], "area_px2": 40000.0}]

    scale_info = {"meters_per_pixel": 0.02, "pixels_per_meter": 50.0}
    apply_metric_scale_to_scene(walls, doors, [], rooms, scale_info, wall_height_m=3.0)

    # Pixel coords intact
    assert walls[0]["start"] == [100.0, 100.0]
    # Metric coords computed: 100 * 0.02 = 2.0m, 300 * 0.02 = 6.0m
    assert walls[0]["metric_start"] == [2.0, 2.0]
    assert walls[0]["metric_end"] == [6.0, 2.0]
    assert walls[0]["length_m"] == 4.0
    assert walls[0]["height_m"] == 3.0

    # Door converted
    assert doors[0]["metric_position"] == [3.0, 2.0]
    assert doors[0]["width_m"] == 0.90

    # Room area converted: 40000 * 0.0004 = 16.0 m2
    assert rooms[0]["area_m2"] == 16.0

def test_wall_representation():
    """Section 11 & 31: Test structured Wall schema representation."""
    wall = Wall(
        id="W001",
        start=[10.0, 20.0],
        end=[100.0, 20.0],
        thickness_px=12.0,
        confidence=0.91,
        status="OBSERVED"
    )
    assert wall.id == "W001"
    assert wall.start == [10.0, 20.0]
    assert wall.height_m == 3.0 # Default 3.0m

def test_duplicate_wall_removal():
    """Section 21, 22 & 31: Test duplicate wall removal in geometry constraints."""
    walls = [
        {"id": "W001", "start": [50.0, 50.0], "end": [250.0, 50.0], "thickness_px": 12.0, "status": "OBSERVED"},
        {"id": "W002", "start": [51.0, 50.0], "end": [249.0, 51.0], "thickness_px": 12.0, "status": "OBSERVED"}, # Duplicate
    ]
    repaired_w, _, _, _, report = validate_and_repair_geometry(walls, [], [], [], {})
    assert len(repaired_w) == 1
    assert any(c["action"] == "PRUNED_DUPLICATE_WALL" for c in report["corrections"])

def test_door_wall_snapping():
    """Section 21, 22 & 31: Test floating door snapped to wall normal and logged."""
    walls = [
        {"id": "W001", "start": [0.0, 100.0], "end": [400.0, 100.0], "thickness_px": 12.0, "status": "OBSERVED"}
    ]
    doors = [
        {"id": "D001", "position": [150.0, 106.0], "width_px": 40.0, "status": "OBSERVED"} # 6px offset
    ]
    _, repaired_d, _, _, report = validate_and_repair_geometry(walls, doors, [], [], {"pixels_per_meter": 50.0})
    assert len(repaired_d) == 1
    assert repaired_d[0]["position"][1] == 100.0 # Snapped to Y=100
    assert repaired_d[0]["status"] == "CORRECTED"
    assert any(c["action"] == "SNAPPED_TO_WALL" for c in report["corrections"])

def test_window_wall_snapping():
    """Section 21, 22 & 31: Test floating window snapped to wall normal and logged."""
    walls = [
        {"id": "W001", "start": [100.0, 0.0], "end": [100.0, 300.0], "thickness_px": 12.0, "status": "OBSERVED"}
    ]
    windows = [
        {"id": "WIN001", "position": [105.0, 150.0], "width_px": 60.0, "status": "OBSERVED"} # 5px offset
    ]
    _, _, repaired_win, _, report = validate_and_repair_geometry(walls, [], windows, [], {"pixels_per_meter": 50.0})
    assert len(repaired_win) == 1
    assert repaired_win[0]["position"][0] == 100.0 # Snapped to X=100
    assert repaired_win[0]["status"] == "CORRECTED"
    assert any(c["action"] == "SNAPPED_TO_WALL" for c in report["corrections"])

def test_room_polygon_validation():
    """Section 21, 22 & 31: Test self-intersecting polygon repair via buffer(0)."""
    # Self-intersecting bowtie polygon
    bowtie = [[0.0, 0.0], [100.0, 100.0], [100.0, 0.0], [0.0, 100.0]]
    rooms = [{"id": "R001", "polygon": bowtie, "area_px2": 5000.0, "status": "OBSERVED"}]
    _, _, _, repaired_rooms, report = validate_and_repair_geometry([], [], [], rooms, {})
    assert len(repaired_rooms) >= 1
    for r in repaired_rooms:
        p = Polygon(r["polygon"])
        assert p.is_valid
    assert any(c["action"] == "REPAIRED_POLYGON_TOPOLOGY" for c in report["corrections"])

def test_upload_validation(tmp_path):
    """Section 7 & 31: Test upload validation for valid and invalid file formats."""
    # Test invalid format rejection
    invalid_file = tmp_path / "bad_file.txt"
    invalid_file.write_text("not a floorplan")
    with open(invalid_file, "rb") as f:
        resp = client.post("/api/upload", files={"file": ("bad_file.txt", f, "text/plain")})
    assert resp.status_code == 400
    assert "Unsupported file format" in resp.json()["detail"]

    # Test valid image format acceptance
    valid_file = Path("data/demo/simple_plan.png")
    if valid_file.exists():
        with open(valid_file, "rb") as f:
            resp = client.post("/api/upload", files={"file": ("simple_plan.png", f, "image/png")})
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert resp.json()["file_id"].startswith("upload_")

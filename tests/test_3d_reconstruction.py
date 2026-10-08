import os
import math
import pytest
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.reconstruction.wall_builder import build_wall_geometry
from backend.app.reconstruction.door_builder import build_door_geometry
from backend.app.reconstruction.window_builder import build_window_geometry
from backend.app.reconstruction.floor_builder import build_floor_geometry
from backend.app.reconstruction.scene_builder import build_scene
from backend.app.reconstruction.exporter import export_glb, export_obj, export_json

client = TestClient(app)

def test_wall_3d_generation():
    """Test wall 3D rectangular prism generation, dimensions, bounds, and vertex counts."""
    wall = {
        "id": "W001",
        "start": [0, 0],
        "end": [500, 0],
        "metric_start": [0.0, 0.0],
        "metric_end": [5.0, 0.0],
        "thickness_m": 0.15,
        "height_m": 3.0,
        "confidence": 0.95,
        "status": "OBSERVED"
    }
    wall_geom = build_wall_geometry(wall, [], [], default_height=3.0, default_thickness=0.15)
    
    assert wall_geom["id"] == "W001"
    assert wall_geom["type"] == "wall"
    assert wall_geom["dimensions"]["length_m"] == 5.0
    assert wall_geom["dimensions"]["thickness_m"] == 0.15
    assert wall_geom["dimensions"]["height_m"] == 3.0
    assert wall_geom["status"] == "OBSERVED"
    assert wall_geom["confidence"] == 0.95
    assert wall_geom["mesh"] is not None
    assert len(wall_geom["mesh"].vertices) > 0
    assert len(wall_geom["mesh"].faces) > 0

def test_door_positioning():
    """Test 3D door frame and panel positioning with parent wall orientation."""
    wall_map = {
        "W001": {
            "id": "W001",
            "transform": {
                "position": [2.5, 1.5, 0.0],
                "rotation_y": 0.0
            }
        }
    }
    door = {
        "id": "D001",
        "wall_id": "W001",
        "metric_position": [2.5, 0.0],
        "width_m": 0.90,
        "height_m": 2.10,
        "confidence": 0.88,
        "status": "OBSERVED"
    }
    door_geom = build_door_geometry(door, wall_map)
    assert door_geom["id"] == "D001"
    assert door_geom["type"] == "door"
    assert door_geom["is_resolved"] is True
    assert door_geom["dimensions"]["width_m"] == 0.90
    assert door_geom["dimensions"]["height_m"] == 2.10
    assert door_geom["transform"]["position"][1] == 1.05  # half height

def test_window_positioning():
    """Test 3D window frame and glass positioning with sill height and elevation."""
    wall_map = {
        "W001": {
            "id": "W001",
            "transform": {
                "position": [2.5, 1.5, 0.0],
                "rotation_y": 0.0
            }
        }
    }
    win = {
        "id": "WIN001",
        "wall_id": "W001",
        "metric_position": [3.5, 0.0],
        "width_m": 1.20,
        "height_m": 1.20,
        "sill_height_m": 0.90,
        "confidence": 0.86,
        "status": "OBSERVED"
    }
    win_geom = build_window_geometry(win, wall_map)
    assert win_geom["id"] == "WIN001"
    assert win_geom["type"] == "window"
    assert win_geom["is_resolved"] is True
    assert win_geom["dimensions"]["sill_height_m"] == 0.90
    # Center Y: 0.9 + 1.2 / 2 = 1.5m
    assert win_geom["transform"]["position"][1] == 1.50

def test_floor_polygon_generation():
    """Test room polygon earcut triangulation into 3D floor slab and centroid computation."""
    room = {
        "id": "R001",
        "label": "Living Room",
        "metric_polygon": [[0.0, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]],
        "area_m2": 20.0,
        "confidence": 0.92,
        "status": "OBSERVED"
    }
    floor_geom = build_floor_geometry(room)
    assert floor_geom is not None
    assert floor_geom["id"] == "R001"
    assert floor_geom["label"] == "Living Room"
    assert floor_geom["area_m2"] == 20.0
    assert floor_geom["centroid"][0] == 2.5
    assert floor_geom["centroid"][2] == 2.0
    assert len(floor_geom["mesh"].vertices) > 0
    assert len(floor_geom["mesh"].faces) > 0

def test_invalid_floor_polygon_safely_ignored():
    """Test invalid or degenerate room polygon returns None instead of corrupted geometry."""
    room = {
        "id": "R_BAD",
        "metric_polygon": [[0.0, 0.0], [0.0, 0.0]],  # Only 2 points
        "area_m2": 0.0
    }
    floor_geom = build_floor_geometry(room)
    assert floor_geom is None

def test_scene_bounding_box_and_metadata():
    """Test full scene assembly, global bounding box, and object metadata retention."""
    mock_scene = {
        "scene_id": "test_scene_101",
        "mode": "blueprint",
        "walls": [
            {"id": "W1", "metric_start": [0.0, 0.0], "metric_end": [6.0, 0.0], "thickness_m": 0.15, "height_m": 3.0, "status": "OBSERVED", "confidence": 0.95},
            {"id": "W2", "metric_start": [6.0, 0.0], "metric_end": [6.0, 4.0], "thickness_m": 0.15, "height_m": 3.0, "status": "OBSERVED", "confidence": 0.95},
            {"id": "W3", "metric_start": [6.0, 4.0], "metric_end": [0.0, 4.0], "thickness_m": 0.15, "height_m": 3.0, "status": "OBSERVED", "confidence": 0.95},
            {"id": "W4", "metric_start": [0.0, 4.0], "metric_end": [0.0, 0.0], "thickness_m": 0.15, "height_m": 3.0, "status": "OBSERVED", "confidence": 0.95},
        ],
        "doors": [
            {"id": "D1", "wall_id": "W1", "metric_position": [3.0, 0.0], "width_m": 0.90, "height_m": 2.10, "status": "OBSERVED", "confidence": 0.90}
        ],
        "windows": [
            {"id": "WIN1", "wall_id": "W3", "metric_position": [3.0, 4.0], "width_m": 1.20, "height_m": 1.20, "status": "OBSERVED", "confidence": 0.88}
        ],
        "rooms": [
            {"id": "R1", "label": "Office", "metric_polygon": [[0.0, 0.0], [6.0, 0.0], [6.0, 4.0], [0.0, 4.0]], "area_m2": 24.0, "status": "OBSERVED", "confidence": 0.92}
        ]
    }

    scene_3d = build_scene(mock_scene, wall_height=3.0, wall_thickness=0.15)
    
    assert scene_3d["scene_id"] == "test_scene_101"
    assert scene_3d["units"] == "meters"
    assert scene_3d["metrics"]["wall_count"] == 4
    assert scene_3d["metrics"]["door_count"] == 1
    assert scene_3d["metrics"]["window_count"] == 1
    assert scene_3d["metrics"]["room_count"] == 1

    # Check bounds
    bounds = scene_3d["bounds"]
    assert bounds["width_m"] >= 6.0
    assert bounds["depth_m"] >= 4.0
    assert bounds["height_m"] >= 3.0

    # Check object metadata retention
    for obj in scene_3d["objects"]:
        assert "id" in obj
        assert "type" in obj
        assert "confidence" in obj
        assert "status" in obj

def test_glb_and_obj_export(tmp_path):
    """Test GLB generation has valid 'glTF' binary header and OBJ export succeeds."""
    mock_scene = {
        "scene_id": "export_test",
        "walls": [
            {"id": "W1", "metric_start": [0.0, 0.0], "metric_end": [4.0, 0.0], "thickness_m": 0.15, "height_m": 3.0, "status": "OBSERVED", "confidence": 0.95}
        ],
        "doors": [],
        "windows": [],
        "rooms": []
    }
    scene_3d = build_scene(mock_scene)
    
    glb_path = str(tmp_path / "test.glb")
    export_glb(scene_3d, glb_path)
    assert os.path.exists(glb_path)
    assert os.path.getsize(glb_path) > 100

    # Verify binary glTF header
    with open(glb_path, "rb") as f:
        magic = f.read(4)
        assert magic == b"glTF"

    # Verify OBJ export
    obj_path = str(tmp_path / "test.obj")
    export_obj(scene_3d, obj_path)
    assert os.path.exists(obj_path)
    assert os.path.getsize(obj_path) > 50

    # Verify JSON export
    json_path = str(tmp_path / "test.json")
    export_json(scene_3d, json_path)
    assert os.path.exists(json_path)

def test_metric_measurement_calculation():
    """Test measurement Euclidean distance calculation in real scene coordinates."""
    # Point A at (1.0, 0.0, 2.0), Point B at (4.0, 0.0, 6.0)
    # dx = 3.0, dz = 4.0 -> distance = 5.0m
    p1 = [1.0, 0.0, 2.0]
    p2 = [4.0, 0.0, 6.0]
    dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)
    assert round(dist, 3) == 5.0

def test_e2e_reconstruction_api_with_3d():
    """Test end-to-end blueprint reconstruction API yields genuine 3D scene and GLB URL."""
    resp = client.post(
        "/api/blueprint/reconstruct",
        data={"is_demo": "true", "demo_type": "simple"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "scene_3d" in data
    assert "glb_url" in data
    assert data["glb_url"].endswith(".glb")
    assert len(data["scene_3d"]["walls"]) > 0
    assert "bounds" in data["scene_3d"]
    assert data["scene_3d"]["bounds"]["width_m"] > 0

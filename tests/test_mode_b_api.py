import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_video_upload_demo_api():
    res = client.post("/api/video/upload", data={"is_demo": "true"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["video_id"] == "sample_room_demo"
    assert data["metadata"]["width"] == 640
    assert data["metadata"]["height"] == 480

def test_video_analyze_quality_api():
    res = client.post("/api/video/analyze", data={"video_id": "sample_room_demo"})
    assert res.status_code == 200
    data = res.json()
    assert data["video_id"] == "sample_room_demo"
    assert "quality_report" in data
    assert data["quality_report"]["sharpness_score"] > 0.0

def test_video_frames_api():
    res = client.post("/api/video/frames", data={"video_id": "sample_room_demo", "target_keyframes": 6})
    assert res.status_code == 200
    data = res.json()
    assert data["keyframes_count"] >= 4
    assert len(data["keyframes"]) == data["keyframes_count"]

def test_video_reconstruct_sync_api():
    res = client.post("/api/video/reconstruct", data={
        "video_id": "sample_room_demo",
        "target_keyframes": 6,
        "is_async": "false"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert "scene" in data
    scene = data["scene"]
    assert scene["source_mode"] == "VIDEO"
    assert len(scene["camera_poses"]) >= 4
    assert len(scene["point_cloud"]) > 0
    assert len(scene["unseen_regions"]) > 0
    assert len(scene["completion_regions"]) > 0

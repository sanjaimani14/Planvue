import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.reconstruction.mesh_audit import validate_glb_file

client = TestClient(app)
DEMO_VIDEO = Path(__file__).resolve().parent.parent / "data" / "demo" / "sample_room.mp4"

def test_full_mode_b_pipeline_integration():
    """
    Section 44: Complete Mode B End-to-End Integration Test.
    Upload -> Analyze -> Keyframes -> Reconstruction -> Coverage -> Unseen -> Completion -> GLB.
    """
    assert DEMO_VIDEO.exists()

    # 1. Upload
    res_up = client.post("/api/video/upload", data={"is_demo": "true"})
    assert res_up.status_code == 200
    video_id = res_up.json()["video_id"]
    assert video_id == "sample_room_demo"

    # 2. Analyze
    res_an = client.post("/api/video/analyze", data={"video_id": video_id})
    assert res_an.status_code == 200
    quality = res_an.json()["quality_report"]
    assert quality["sharpness_score"] > 0

    # 3. Keyframes
    res_kf = client.post("/api/video/frames", data={"video_id": video_id, "target_keyframes": 8})
    assert res_kf.status_code == 200
    assert len(res_kf.json()["keyframes"]) >= 4

    # 4. Reconstruction
    res_rec = client.post("/api/video/reconstruct", data={
        "video_id": video_id,
        "target_keyframes": 8,
        "is_async": "false"
    })
    assert res_rec.status_code == 200
    scene = res_rec.json()["scene"]
    assert scene["source_mode"] == "VIDEO"
    assert len(scene["camera_poses"]) >= 4
    assert len(scene["point_cloud"]) > 0
    assert len(scene["unseen_regions"]) > 0
    assert len(scene["completion_regions"]) > 0
    assert "coverage" in scene
    assert scene["coverage"]["observed_percentage"] > 0

    # 5. Scene retrieval endpoint
    res_sc = client.get(f"/api/video/{video_id}/scene")
    assert res_sc.status_code == 200
    assert res_sc.json()["scene_id"] == scene["scene_id"]

    # 6. GLB Export and Deep Validation
    res_exp = client.post(f"/api/video/{video_id}/export", data={"format": "glb"})
    assert res_exp.status_code == 200
    glb_bytes = res_exp.content
    assert len(glb_bytes) > 1000

    validation = validate_glb_file(glb_bytes)
    assert validation["is_valid"] is True
    assert validation["total_vertices"] > 0
    assert validation["total_faces"] > 0
    assert validation["mesh_count"] > 0

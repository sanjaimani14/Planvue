import pytest
from pathlib import Path
import trimesh
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_glb_completion_export_binary(tmp_path):
    res = client.post("/api/video/sample_room_demo/export", data={"format": "glb"})
    assert res.status_code == 200
    assert len(res.content) > 1000

    # Save and parse via trimesh
    glb_file = tmp_path / "test_comp.glb"
    glb_file.write_bytes(res.content)

    loaded = trimesh.load(str(glb_file), file_type="glb")
    assert isinstance(loaded, trimesh.Scene)
    assert len(loaded.geometry) >= 4

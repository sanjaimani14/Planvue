import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_completion_endpoints():
    # 1. Run completion on demo video
    res_run = client.post("/api/video/completion/run", data={"video_id": "sample_room_demo"})
    assert res_run.status_code == 200
    data = res_run.json()
    job_id = data["job_id"]
    assert data["status"] == "COMPLETED"

    # 2. Get completion job
    res_job = client.get(f"/api/video/completion/{job_id}")
    assert res_job.status_code == 200

    # 3. Get coverage
    res_cov = client.get(f"/api/video/completion/{job_id}/coverage")
    assert res_cov.status_code == 200

    # 4. Get regions
    res_reg = client.get(f"/api/video/completion/{job_id}/regions")
    assert res_reg.status_code == 200

    # 5. Validate completion
    res_val = client.post(f"/api/video/completion/{job_id}/validate")
    assert res_val.status_code == 200

    # 6. Get report
    res_rep = client.get(f"/api/video/completion/{job_id}/report")
    assert res_rep.status_code == 200
    assert "research_contribution" in res_rep.json()

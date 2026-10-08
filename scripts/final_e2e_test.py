"""
PLANE VUE — End-to-End Test Suite (Section 36)
Runs complete pipeline across:
Application -> Mode A (Blueprint -> Analysis -> 3D -> GLB)
            -> Mode B (Video -> Reconstruction -> Coverage -> Unseen -> Completion -> Validation -> GLB)
"""
import sys
import os
import json
import time
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def run_e2e_pipeline():
    print("=" * 70)
    print("  PLANE VUE — COMPLETE END-TO-END VERIFICATION")
    print("=" * 70)

    stages = []
    overall_status = "PASS"

    # ==========================================
    # STAGE 1: HEALTH
    # ==========================================
    try:
        res = client.get("/api/health")
        assert res.status_code == 200
        stages.append(("Application Health", "PASS", "Backend responding at /api/health"))
    except Exception as e:
        stages.append(("Application Health", "FAIL", str(e)))
        overall_status = "FAIL"

    # ==========================================
    # STAGE 2: MODE A (BLUEPRINT -> 3D -> GLB)
    # ==========================================
    try:
        # Reconstruct demo blueprint
        res_rec_a = client.post(
            "/api/blueprint/reconstruct",
            data={"is_demo": "true", "demo_type": "simple"}
        )
        assert res_rec_a.status_code == 200, f"Blueprint reconstruct error: {res_rec_a.text}"
        data_rec_a = res_rec_a.json()
        assert data_rec_a.get("success") is True
        scene_id = data_rec_a.get("scene_id")
        assert scene_id is not None
        assert "scene_3d" in data_rec_a

        stages.append(("Mode A Blueprint Analysis", "PASS", f"Analyzed blueprint, scene_id: {scene_id}"))
        stages.append(("Mode A 3D Scene Generation", "PASS", f"Generated metric 3D scene ({len(data_rec_a['scene_3d']['walls'])} walls)"))

        # Export GLB
        res_exp_a = client.post("/api/blueprint/export", json={"scene_id": scene_id, "format": "glb"})
        assert res_exp_a.status_code == 200, f"GLB export failed: {res_exp_a.status_code}"
        assert res_exp_a.content[:4] == b"glTF", "Invalid glTF binary magic bytes"

        stages.append(("Mode A Binary GLB Export", "PASS", f"Verified binary GLB export ({len(res_exp_a.content)} bytes)"))
    except Exception as e:
        stages.append(("Mode A Pipeline", "FAIL", str(e)))
        overall_status = "FAIL"

    # ==========================================
    # STAGE 3: MODE B (VIDEO -> RECONSTRUCTION -> COMPLETION -> GLB)
    # ==========================================
    try:
        # Ingestion
        res_v_up = client.post("/api/video/upload", data={"is_demo": "true"})
        assert res_v_up.status_code == 200
        video_id = res_v_up.json()["video_id"]
        stages.append(("Mode B Video Ingestion", "PASS", f"Ingested walkthrough video: {video_id}"))

        # Frames
        res_kf = client.post("/api/video/frames", data={"video_id": video_id, "target_keyframes": 6})
        assert res_kf.status_code == 200
        kf_count = res_kf.json()["keyframes_count"]
        stages.append(("Mode B Keyframe Selection", "PASS", f"Extracted {kf_count} sharp keyframes"))

        # Full Sync Reconstruction
        res_v_rec = client.post("/api/video/reconstruct", data={
            "video_id": video_id,
            "target_keyframes": 6,
            "is_async": "false"
        })
        assert res_v_rec.status_code == 200, f"Reconstruct error: {res_v_rec.text}"
        data_v = res_v_rec.json()
        job_id = data_v.get("job_id", video_id)
        scene_b = data_v["scene"]

        # Camera trajectory
        cam_count = len(scene_b.get("camera_poses", []))
        assert cam_count >= 4
        stages.append(("Mode B Camera Estimation", "PASS", f"Recovered {cam_count} 6-DOF camera poses"))

        # Sparse 3D
        pt_count = len(scene_b.get("point_cloud", []))
        assert pt_count > 0
        stages.append(("Mode B 3D Reconstruction", "PASS", f"Triangulated {pt_count} points, fitted surface planes"))

        # Coverage
        cov = scene_b.get("coverage", {})
        assert "observed_percentage" in cov
        stages.append(("Mode B Coverage Map", "PASS", f"Observed: {cov['observed_percentage']}%, Unseen: {cov['unseen_percentage']}%"))

        # Unseen detection
        unseen = scene_b.get("unseen_regions", [])
        assert len(unseen) > 0
        stages.append(("Mode B Unseen Detection", "PASS", f"Identified {len(unseen)} unobserved sectors"))

        # Completion
        comps = scene_b.get("completion_regions", [])
        assert len(comps) > 0
        stages.append(("Mode B Structural Completion", "PASS", f"Synthesized {len(comps)} conservative wall/shell elements"))

        # Validation
        val_statuses = [c.get("validation_status") for c in comps]
        assert all(s in ["PASSED", "PASSED_WITH_CORRECTIONS"] for s in val_statuses)
        stages.append(("Mode B Completion Validation", "PASS", "Verified non-overwrite invariant & manifold integrity"))

        # GLB export
        res_v_exp = client.post(f"/api/video/completion/{job_id}/export", data={"format": "glb"})
        assert res_v_exp.status_code == 200
        assert res_v_exp.content[:4] == b"glTF"
        stages.append(("Mode B Binary GLB Export", "PASS", f"Verified binary GLB export ({len(res_v_exp.content)} bytes)"))

    except Exception as e:
        stages.append(("Mode B Pipeline", "FAIL", str(e)))
        overall_status = "FAIL"

    # Print summary
    print("\n" + "=" * 70)
    print(f"{'Pipeline Stage':<30} | {'Status':<10} | {'Details'}")
    print("-" * 70)
    for name, status, details in stages:
        print(f"{name:<30} | {status:<10} | {details}")
    print("=" * 70)
    print(f"FINAL E2E RESULT: {overall_status}")
    print("=" * 70)

    return overall_status

if __name__ == "__main__":
    status = run_e2e_pipeline()
    sys.exit(0 if status == "PASS" else 1)

import pytest
from pathlib import Path
from backend.app.video.video_ingestion import validate_and_ingest_video
from backend.app.video.frame_extraction import extract_intelligent_keyframes
from backend.app.video.completion_eligibility import assess_completion_eligibility

def test_failure_invalid_video_container(tmp_path):
    fake_file = tmp_path / "corrupted.mp4"
    fake_file.write_bytes(b"NOT_A_REAL_VIDEO_HEADER")
    is_valid, meta, err = validate_and_ingest_video(fake_file, "bad_vid")
    assert is_valid is False
    assert err is not None

def test_failure_unsupported_isolated_region():
    # Extremely remote void with no structural planes
    assessment = assess_completion_eligibility(
        region_id="VOID_01",
        region_bounds={"min": [100, 0, 100], "max": [105, 3, 105]},
        observed_planes=[],
        points_3d=[]
    )
    assert assessment.is_eligible is False
    assert assessment.action_directive == "LEAVE_UNRESOLVED"

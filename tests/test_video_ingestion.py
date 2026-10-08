import pytest
from pathlib import Path
from backend.app.video.video_ingestion import validate_and_ingest_video

DEMO_VIDEO = Path(__file__).resolve().parent.parent / "data" / "demo" / "sample_room.mp4"

def test_video_ingestion_valid():
    assert DEMO_VIDEO.exists(), "sample_room.mp4 must exist for ingestion tests"
    is_valid, meta, err = validate_and_ingest_video(DEMO_VIDEO, video_id="test_ingest")
    assert is_valid is True
    assert err is None
    assert meta is not None
    assert meta.video_id == "test_ingest"
    assert meta.width == 640
    assert meta.height == 480
    assert meta.fps == 30.0
    assert meta.total_frames > 100
    assert meta.duration_seconds > 2.0
    assert meta.size_bytes > 0

def test_video_ingestion_nonexistent_file():
    is_valid, meta, err = validate_and_ingest_video("nonexistent_video.mp4")
    assert is_valid is False
    assert meta is None
    assert "not found" in err.lower()

def test_video_ingestion_invalid_extension(tmp_path):
    fake_txt = tmp_path / "fake.txt"
    fake_txt.write_text("not a video")
    is_valid, meta, err = validate_and_ingest_video(fake_txt)
    assert is_valid is False
    assert "unsupported" in err.lower()

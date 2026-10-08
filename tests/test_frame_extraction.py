import pytest
from pathlib import Path
from backend.app.video.frame_extraction import extract_intelligent_keyframes
from backend.app.video.frame_quality import analyze_video_stream_quality, assess_frame_quality

DEMO_VIDEO = Path(__file__).resolve().parent.parent / "data" / "demo" / "sample_room.mp4"

def test_frame_quality_analysis():
    quality = analyze_video_stream_quality(str(DEMO_VIDEO))
    assert quality.sharpness_score > 0.0
    assert quality.exposure_status in ["OPTIMAL", "UNDEREXPOSED", "OVEREXPOSED"]
    assert quality.quality_grade in ["GOOD", "WARNING", "POOR"]
    assert quality.sharp_frames_count + quality.blurred_frames_count > 0

def test_keyframe_extraction():
    kf_items, kf_matrices = extract_intelligent_keyframes(
        str(DEMO_VIDEO), video_id="test_kf", target_keyframes=6
    )
    assert len(kf_items) >= 4
    assert len(kf_matrices) == len(kf_items)
    for kf in kf_items:
        assert kf.sharpness > 0.0
        assert kf.timestamp_s >= 0.0
        assert kf.image_url.startswith("/data/video/frames/")

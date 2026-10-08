import pytest
from backend.app.video.schemas import VideoSceneObject

def test_provenance_schema_strict():
    obj = VideoSceneObject(
        id="wall_001",
        type="wall",
        status="OBSERVED",
        confidence=0.94,
        source_frames=[12, 18, 25],
        evidence=["multi_view_observation", "feature_tracks"],
        geometry={"start": [0,0,0], "end": [2,0,0]}
    )
    d = obj.model_dump()
    assert d["status"] in ["OBSERVED", "INFERRED", "GENERATED", "CORRECTED"]
    assert d["confidence"] == 0.94
    assert len(d["source_frames"]) == 3
    assert "multi_view_observation" in d["evidence"]

import pytest
from backend.app.video.schemas import CompletionRegion, VideoSceneObject
from backend.app.video.completion.completion_validator import validate_completion_candidate

def test_validation_non_overwrite_trimming():
    # Candidate wall overlaps an observed wall
    candidate = CompletionRegion(
        region_id="CMP_01",
        element_type="WALL_CONTINUATION",
        status="INFERRED",
        completion_level="LEVEL_1_CONTINUATION",
        geometry={
            "start": [-2.0, 0.0, 2.0],
            "end": [2.0, 0.0, 2.0],
            "height": 2.80,
            "thickness": 0.18,
            "length": 4.0,
            "orientation": "HORIZONTAL_X"
        },
        reason="Test",
        evidence_category="GEOMETRIC_CONTINUATION",
        confidence_level="HIGH"
    )

    observed_objs = [
        VideoSceneObject(
            id="OBS_WALL_01",
            type="wall",
            status="OBSERVED",
            provenance_note="Direct observation",
            confidence=0.98,
            source_frames=[1, 2],
            evidence=["multi_view_observation"],
            geometry={
                "start": [-2.0, 0.0, 2.0],
                "end": [0.0, 0.0, 2.0],
                "height": 2.80,
                "thickness": 0.18,
                "length": 2.0
            }
        )
    ]

    val_res = validate_completion_candidate(
        candidate=candidate,
        observed_objects=observed_objs,
        scene_bounds={"min": [-5, 0, -5], "max": [5, 3, 5]}
    )

    assert val_res.is_valid is True
    assert val_res.status == "PASSED_WITH_CORRECTIONS"
    assert len(val_res.corrections_applied) > 0
    # Candidate should be trimmed so it doesn't overwrite observed segment
    assert val_res.corrected_geometry is not None
    assert val_res.corrected_geometry["start"][0] >= 0.0

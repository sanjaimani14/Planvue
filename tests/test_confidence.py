import pytest
from backend.app.video.confidence_model import compute_completion_confidence

def test_confidence_decomposition():
    decomp = compute_completion_confidence(
        completion_level="LEVEL_1_CONTINUATION",
        distance_to_observed_m=1.0,
        rule_score=1.0,
        validation_passed=True,
        blueprint_aligned=False,
        supporting_frames_count=3
    )
    assert 0.70 <= decomp.confidence_score <= 1.0
    assert decomp.confidence_level == "HIGH"
    assert "multi_view_support" in decomp.components
    assert "distance_penalty" in decomp.components
    assert decomp.components["distance_penalty"] == 0.0  # Under 1.5m, no penalty

import pytest
from backend.app.video.schemas import UnseenRegion
from backend.app.video.completion_ablation import run_mode_b_ablation_study

def test_ablation_study_configurations():
    unseen = [
        UnseenRegion(
            region_id="REG_01", label="North sector", reason="Unobserved",
            evidence="No rays", boundary_min=[-2.0, 0, 1.5], boundary_max=[2.0, 2.8, 2.0]
        )
    ]
    runs = run_mode_b_ablation_study(unseen, [], has_blueprint=False)
    assert len(runs) >= 5
    config_ids = [r.config_id for r in runs]
    assert "A0" in config_ids
    assert "A1" in config_ids
    assert "A2" in config_ids
    assert "A3" in config_ids
    assert "A5" in config_ids
    # Full system (A5) should have 0 defects and 1.0 closure
    a5 = [r for r in runs if r.config_id == "A5"][0]
    assert a5.defects_count == 0
    assert a5.closure_rate == 1.0

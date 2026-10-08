import pytest
from datasets.video_completion.evaluate_synthetic_completion import evaluate_scene_completion

def test_synthetic_completion_metrics():
    res = evaluate_scene_completion("scene_001")
    assert "baseline" in res
    assert "proposed" in res
    assert res["proposed"]["room_closure_rate"] == 1.0
    assert res["proposed"]["topology_defects"] == 0
    assert res["proposed"]["chamfer_distance_m"] <= res["baseline"]["chamfer_distance_m"]

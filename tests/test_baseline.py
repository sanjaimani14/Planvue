import pytest
from backend.app.video.schemas import UnseenRegion, PlaneSurface
from backend.app.video.completion_baseline import run_naive_baseline_completion, evaluate_baseline_vs_proposed

def test_baseline_completion():
    unseen = [
        UnseenRegion(
            region_id="REG_01", label="North sector", reason="Unobserved",
            evidence="No rays", boundary_min=[-2.0, 0, 1.5], boundary_max=[2.0, 2.8, 2.0]
        )
    ]
    naive_walls, defects, closure, t_ms = run_naive_baseline_completion(unseen, [])
    assert len(naive_walls) == 1
    assert defects > 0
    assert closure < 1.0

def test_baseline_vs_proposed_comparison():
    unseen = [
        UnseenRegion(
            region_id="REG_01", label="North sector", reason="Unobserved",
            evidence="No rays", boundary_min=[-2.0, 0, 1.5], boundary_max=[2.0, 2.8, 2.0]
        )
    ]
    comp_rep = evaluate_baseline_vs_proposed(unseen, [], [], proposed_runtime_ms=25.0)
    assert comp_rep.baseline_topology_defects > comp_rep.proposed_topology_defects
    assert comp_rep.proposed_room_closure_rate >= comp_rep.baseline_room_closure_rate

import pytest
from backend.app.video.completion.constraints import (
    WallContinuityConstraint, ParallelWallConstraint, PerpendicularCornerConstraint, FloorIntersectionConstraint
)
from backend.app.video.completion.structural_rules import evaluate_structural_rules

def test_constraints_math():
    c_cont = WallContinuityConstraint(constraint_id="c1", target_element_id="w1")
    err = c_cont.check([0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.1, 0.0, 1.0])
    assert c_cont.is_satisfied is True

    c_par = ParallelWallConstraint(constraint_id="c2", target_element_id="w2")
    c_par.check([0, 0, 1], [0, 0, -1])  # opposite parallel
    assert c_par.is_satisfied is True

    c_perp = PerpendicularCornerConstraint(constraint_id="c3", target_element_id="w3")
    c_perp.check([1, 0, 0], [0, 0, 1])  # 90 degrees
    assert c_perp.is_satisfied is True

def test_evaluate_structural_rules():
    geom = {
        "start": [0.0, 0.0, 0.0],
        "end": [3.0, 0.0, 0.0],
        "height": 2.80,
        "thickness": 0.18,
        "length": 3.0,
        "orientation": "HORIZONTAL_X"
    }
    res = evaluate_structural_rules(geom, [], nominal_wall_thickness=0.18, nominal_wall_height=2.80)
    assert res.all_rules_passed is True
    assert res.score == 1.0

import pytest
from backend.app.video.schemas import PlaneSurface, Point3D
from backend.app.video.completion_eligibility import assess_completion_eligibility

def test_completion_eligibility_grounded():
    # Region adjacent to an observed wall plane should be eligible
    region_bounds = {"min": [-2.5, 0.0, 1.8], "max": [2.5, 2.8, 2.2]}
    observed_planes = [
        PlaneSurface(
            plane_id="wall_east",
            surface_type="WALL",
            normal=[1.0, 0.0, 0.0],
            offset=2.5,
            inlier_count=50,
            confidence=0.95,
            bounds={"min": [2.3, 0.0, -2.0], "max": [2.5, 2.8, 2.0]}
        ),
        PlaneSurface(
            plane_id="floor_main",
            surface_type="FLOOR",
            normal=[0.0, 1.0, 0.0],
            offset=0.0,
            inlier_count=120,
            confidence=0.98,
            bounds={"min": [-2.5, 0.0, -2.5], "max": [2.5, 0.0, 2.5]}
        )
    ]
    points = [Point3D(id="p1", position=[2.4, 1.2, 1.9])]

    assessment = assess_completion_eligibility(
        region_id="REG_NORTH",
        region_bounds=region_bounds,
        observed_planes=observed_planes,
        points_3d=points
    )
    assert assessment.is_eligible is True
    assert assessment.action_directive == "PROCEED_COMPLETION"
    assert assessment.primary_rule in ["ROOM_SHELL_CONTINUATION", "CORNER_CONSTRAINT", "WALL_ALIGNMENT"]

def test_completion_eligibility_unsupported():
    # Region far away from any observed plane with no floor or walls
    region_bounds = {"min": [50.0, 0.0, 50.0], "max": [55.0, 2.8, 55.0]}
    assessment = assess_completion_eligibility(
        region_id="REG_ISOLATED_VOID",
        region_bounds=region_bounds,
        observed_planes=[],
        points_3d=[]
    )
    assert assessment.is_eligible is False
    assert assessment.action_directive == "LEAVE_UNRESOLVED"
    assert assessment.primary_rule == "INSUFFICIENT_EVIDENCE"

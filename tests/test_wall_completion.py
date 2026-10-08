import pytest
from backend.app.video.schemas import UnseenRegion, PlaneSurface
from backend.app.video.completion.wall_completion import complete_unseen_wall_segment

def test_wall_completion_continuation():
    unseen_reg = UnseenRegion(
        region_id="UNSEEN_01",
        label="North wall gap",
        reason="Blocked by furniture",
        evidence="No camera rays",
        boundary_min=[-2.5, 0.0, 1.8],
        boundary_max=[2.5, 2.8, 2.2],
        evidence_frames=[1, 2]
    )
    observed_planes = [
        PlaneSurface(
            plane_id="wall_north_adj",
            surface_type="WALL",
            normal=[0.0, 0.0, 1.0],
            offset=2.0,
            inlier_count=35,
            confidence=0.9,
            bounds={}
        )
    ]
    res = complete_unseen_wall_segment(unseen_reg, observed_planes)
    assert res is not None
    assert res.status == "INFERRED"
    assert res.completion_level == "LEVEL_1_CONTINUATION"
    assert res.geometry["orientation"] == "HORIZONTAL_X"

def test_wall_completion_room_shell_fallback():
    unseen_reg = UnseenRegion(
        region_id="UNSEEN_02",
        label="Isolated side wall",
        reason="Out of camera view",
        evidence="No camera rays",
        boundary_min=[-2.5, 0.0, -1.0],
        boundary_max=[-2.1, 2.8, 1.0],
        evidence_frames=[]
    )
    res = complete_unseen_wall_segment(unseen_reg, observed_planes=[])
    assert res is not None
    assert res.status == "GENERATED"
    assert res.completion_level == "LEVEL_4_ROOM_SHELL"

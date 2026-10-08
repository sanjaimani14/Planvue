import pytest
from backend.app.video.schemas import CameraPose, Point3D, PlaneSurface, CoverageReport
from backend.app.video.unseen_detection import detect_unseen_regions
from backend.app.video.completion import complete_unseen_regions

def test_unseen_detection_and_conservative_completion():
    cam_poses = [
        CameraPose(
            frame_index=0,
            timestamp_s=0.0,
            position=[0.0, 1.4, 0.0],
            rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        )
    ]
    # Points only on South and West side
    points = [
        Point3D(id="p1", position=[-2.0, 0.0, 1.0], color=[100, 100, 100]),
        Point3D(id="p2", position=[-2.0, 1.5, 1.0], color=[100, 100, 100])
    ]
    planes = [
        PlaneSurface(
            plane_id="PLN_WAL_01",
            surface_type="WALL",
            normal=[-1.0, 0.0, 0.0],
            offset=2.0,
            inlier_count=20,
            confidence=0.85,
            bounds={"min": [-2.1, 0, 0.5], "max": [-1.9, 2.5, 3.0]}
        )
    ]
    coverage = CoverageReport(
        observed_percentage=30.0,
        weakly_observed_percentage=20.0,
        unseen_percentage=50.0,
        total_scene_volume_m3=45.0,
        observed_bounding_box={"min": [-3.0, 0.0, -1.0], "max": [3.0, 2.8, 5.0]},
        camera_visibility_rays_count=64
    )

    unseen_regs = detect_unseen_regions(cam_poses, points, planes, coverage)
    assert len(unseen_regs) > 0
    for reg in unseen_regs:
        assert reg.status == "UNSEEN"
        assert len(reg.reason) > 5
        assert len(reg.evidence) > 5

    completions = complete_unseen_regions(unseen_regs, planes, coverage)
    assert len(completions) > 0
    for comp in completions:
        assert comp.status in ["INFERRED", "GENERATED"]
        assert comp.completion_level in ["LEVEL_1_CONTINUATION", "LEVEL_2_SYMMETRY", "LEVEL_3_ROOM_SHELL"]
        assert len(comp.reason) > 5
        assert comp.confidence_level in ["HIGH", "MEDIUM", "CONSERVATIVE"]

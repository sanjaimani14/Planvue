import pytest
from backend.app.video.schemas import CameraPose, Point3D, PlaneSurface, CoverageReport
from backend.app.video.unseen_detection import detect_unseen_regions

def test_detect_unseen_regions():
    cams = [
        CameraPose(frame_index=0, timestamp_s=0.0, position=[0, 1.4, -1.0], rotation=[[1,0,0],[0,1,0],[0,0,1]]),
        CameraPose(frame_index=1, timestamp_s=0.5, position=[0.5, 1.4, -0.8], rotation=[[1,0,0],[0,1,0],[0,0,1]]),
    ]
    # Provide points in South, East, West, but NONE in North
    points = [
        Point3D(id="pt_s1", position=[0.0, 1.0, -2.5]),
        Point3D(id="pt_e1", position=[2.5, 1.0, 0.0]),
        Point3D(id="pt_w1", position=[-2.5, 1.0, 0.0]),
    ]
    planes = [
        PlaneSurface(
            plane_id="p_south", surface_type="WALL", normal=[0,0,-1], offset=2.5, inlier_count=20, confidence=0.9, bounds={}
        )
    ]
    coverage = CoverageReport(
        observed_percentage=70.0, weakly_observed_percentage=15.0, unseen_percentage=15.0,
        total_scene_volume_m3=36.0, observed_bounding_box={"min": [-2.5, 0, -2.5], "max": [2.5, 2.8, 2.5]},
        camera_visibility_rays_count=120
    )

    unseen = detect_unseen_regions(cams, points, planes, coverage)
    assert len(unseen) > 0
    # North perimeter should be detected as unobserved
    north_unseen = [u for u in unseen if "North" in u.label]
    assert len(north_unseen) >= 1
    assert north_unseen[0].status == "UNSEEN"
    assert north_unseen[0].classification in ["UNSEEN", "OCCLUDED", "OUT_OF_VIEW"]
    assert "completion_eligibility" in north_unseen[0].model_dump()

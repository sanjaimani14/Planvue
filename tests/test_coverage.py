import pytest
import numpy as np
from backend.app.video.schemas import CameraPose, Point3D
from backend.app.video.coverage import compute_spatial_coverage, is_point_in_frustum

def test_point_in_frustum():
    cam_pos = np.array([0.0, 1.4, 0.0])
    cam_dir = np.array([0.0, 0.0, 1.0])  # Looking along Z
    
    # Point directly in front
    pt_front = np.array([0.0, 1.4, 2.5])
    assert is_point_in_frustum(pt_front, cam_pos, cam_dir) is True

    # Point behind camera
    pt_behind = np.array([0.0, 1.4, -2.5])
    assert is_point_in_frustum(pt_behind, cam_pos, cam_dir) is False

def test_spatial_coverage_computation():
    cam_poses = [
        CameraPose(
            frame_index=0,
            timestamp_s=0.0,
            position=[0.0, 1.4, 0.0],
            rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        ),
        CameraPose(
            frame_index=1,
            timestamp_s=0.5,
            position=[0.3, 1.4, 0.2],
            rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        )
    ]
    points = [
        Point3D(id="p1", position=[0.0, 0.0, 2.0], color=[100, 100, 100]),
        Point3D(id="p2", position=[0.5, 0.0, 2.5], color=[100, 100, 100])
    ]

    coverage, grid = compute_spatial_coverage(cam_poses, points, grid_res=1.0)
    assert coverage.total_scene_volume_m3 > 0.0
    assert coverage.observed_percentage + coverage.weakly_observed_percentage + coverage.unseen_percentage == pytest.approx(100.0, abs=0.5)
    assert coverage.camera_visibility_rays_count > 0

import pytest
import numpy as np
from backend.app.video.schemas import CameraPose, Point3D, PlaneSurface
from backend.app.video.visibility.ray_visibility import cast_frustum_rays, is_point_in_camera_frustum, compute_ray_plane_intersection
from backend.app.video.visibility.coverage_grid import VoxelCoverageGrid, compute_dense_coverage_grid
from backend.app.video.visibility.surface_visibility import evaluate_surface_visibility
from backend.app.video.visibility.visibility_map import build_visibility_map

def test_ray_visibility_frustum():
    cam_pos = np.array([0.0, 1.4, 0.0])
    cam_rot = [[1,0,0],[0,1,0],[0,0,1]]  # Identity: looks forward +Z
    
    # Point directly in front
    pt_front = np.array([0.0, 1.4, 2.0])
    in_f, dist, cos_a = is_point_in_camera_frustum(pt_front, cam_pos, cam_rot)
    assert in_f is True
    assert abs(dist - 2.0) < 1e-4

    # Point directly behind camera
    pt_behind = np.array([0.0, 1.4, -2.0])
    in_b, _, _ = is_point_in_camera_frustum(pt_behind, cam_pos, cam_rot)
    assert in_b is False

def test_voxel_coverage_grid():
    cams = [
        CameraPose(frame_index=0, timestamp_s=0.0, position=[0, 1.4, 0], rotation=[[1,0,0],[0,1,0],[0,0,1]]),
        CameraPose(frame_index=1, timestamp_s=0.5, position=[0.2, 1.4, 0], rotation=[[1,0,0],[0,1,0],[0,0,1]]),
    ]
    grid, stats, heatmap = compute_dense_coverage_grid(cams, [], resolution=0.50)
    assert stats["total_voxels"] > 0
    assert stats["total_volume_m3"] > 0
    assert "cells" in heatmap

def test_surface_and_visibility_map():
    cams = [
        CameraPose(frame_index=0, timestamp_s=0.0, position=[0, 1.4, 0], rotation=[[1,0,0],[0,1,0],[0,0,1]]),
        CameraPose(frame_index=1, timestamp_s=0.5, position=[0.2, 1.4, 0], rotation=[[1,0,0],[0,1,0],[0,0,1]]),
    ]
    planes = [
        PlaneSurface(
            plane_id="p_wall_north",
            surface_type="WALL",
            normal=[0, 0, -1],  # Facing towards camera at Z=2.5
            offset=-2.5,
            inlier_count=45,
            confidence=0.92,
            bounds={"min": [-2, 0, 2.4], "max": [2, 2.8, 2.6]}
        )
    ]
    vis_rep = build_visibility_map(cams, [], planes)
    assert vis_rep.total_volume_m3 > 0
    assert len(vis_rep.regions) >= 4
    assert len(vis_rep.surface_visibilities) == 1

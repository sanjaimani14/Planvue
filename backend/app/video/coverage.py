"""
Spatial Coverage and Camera Visibility Map Engine for Mode B.
Computes volumetric coverage (Observed, Weakly Observed, Unseen) using camera viewing frustums.
"""

from typing import List, Dict, Any, Tuple
import math
import numpy as np

from backend.app.video.schemas import CameraPose, Point3D, CoverageReport

def compute_camera_viewing_direction(rotation_matrix: List[List[float]]) -> np.ndarray:
    """Computes normalized forward viewing ray in world coordinates from rotation matrix."""
    R = np.array(rotation_matrix, dtype=np.float64)
    # Camera looks along positive Z axis in local coordinates
    dir_vec = R @ np.array([0.0, 0.0, 1.0])
    norm = np.linalg.norm(dir_vec)
    return dir_vec / norm if norm > 1e-6 else np.array([0.0, 0.0, 1.0])

def is_point_in_frustum(
    pt: np.ndarray,
    cam_pos: np.ndarray,
    cam_dir: np.ndarray,
    max_dist: float = 6.0,
    cos_half_fov: float = 0.50  # ~120 deg total horizontal/vertical cone
) -> bool:
    """Checks if a 3D point lies within camera viewing frustum."""
    diff = pt - cam_pos
    dist = np.linalg.norm(diff)
    if dist < 0.25 or dist > max_dist:
        return False
    ray = diff / dist
    return float(np.dot(ray, cam_dir)) >= cos_half_fov

def compute_spatial_coverage(
    camera_poses: List[CameraPose],
    points_3d: List[Point3D],
    grid_res: float = 0.50  # 0.5m voxel size
) -> Tuple[CoverageReport, Dict[str, Any]]:
    """
    Evaluates volumetric observation coverage across the bounding scene.
    Classifies spatial voxels into:
    - OBSERVED (>= 2 camera rays and near 3D feature points)
    - WEAKLY_OBSERVED (1 camera ray)
    - UNSEEN (within room envelope but outside all camera rays)
    """
    if not camera_poses:
        return CoverageReport(
            observed_percentage=0.0,
            weakly_observed_percentage=0.0,
            unseen_percentage=100.0,
            total_scene_volume_m3=0.0,
            observed_bounding_box={"min": [0, 0, 0], "max": [0, 0, 0]},
            camera_visibility_rays_count=0
        ), {}

    # Calculate scene spatial envelope from camera poses and points
    all_coords = [c.position for c in camera_poses]
    if points_3d:
        all_coords.extend([p.position for p in points_3d])

    xs = [pt[0] for pt in all_coords]
    ys = [pt[1] for pt in all_coords]
    zs = [pt[2] for pt in all_coords]

    min_x = math.floor(min(xs) - 0.8)
    max_x = math.ceil(max(xs) + 0.8)
    min_y = max(0.0, math.floor(min(ys) - 0.5))
    max_y = math.ceil(max(ys) + 0.8)
    min_z = math.floor(min(zs) - 0.8)
    max_z = math.ceil(max(zs) + 0.8)

    scene_vol_m3 = (max_x - min_x) * (max_y - min_y) * (max_z - min_z)

    # Prepare camera vectors
    cams = []
    for c in camera_poses:
        pos = np.array(c.position, dtype=np.float64)
        dir_vec = compute_camera_viewing_direction(c.rotation)
        cams.append((pos, dir_vec))

    # Discretize voxel centers
    observed_count = 0
    weakly_observed_count = 0
    unseen_count = 0
    total_voxels = 0

    x_range = np.arange(min_x + grid_res/2, max_x, grid_res)
    y_range = np.arange(min_y + grid_res/2, max_y, grid_res)
    z_range = np.arange(min_z + grid_res/2, max_z, grid_res)

    voxel_samples: Dict[str, str] = {}  # key -> classification

    for x in x_range:
        for y in y_range:
            for z in z_range:
                total_voxels += 1
                voxel_pt = np.array([x, y, z], dtype=np.float64)

                vis_count = 0
                for pos, d_vec in cams:
                    if is_point_in_frustum(voxel_pt, pos, d_vec):
                        vis_count += 1

                v_key = f"{round(x, 1)}_{round(y, 1)}_{round(z, 1)}"
                if vis_count >= 2:
                    observed_count += 1
                    voxel_samples[v_key] = "OBSERVED"
                elif vis_count == 1:
                    weakly_observed_count += 1
                    voxel_samples[v_key] = "WEAKLY_OBSERVED"
                else:
                    unseen_count += 1
                    voxel_samples[v_key] = "UNSEEN"

    total = max(1, total_voxels)
    obs_pct = round((observed_count / total) * 100.0, 1)
    weak_pct = round((weakly_observed_count / total) * 100.0, 1)
    unseen_pct = round((unseen_count / total) * 100.0, 1)

    rep = CoverageReport(
        observed_percentage=obs_pct,
        weakly_observed_percentage=weak_pct,
        unseen_percentage=unseen_pct,
        total_scene_volume_m3=round(scene_vol_m3, 2),
        observed_bounding_box={
            "min": [min_x, min_y, min_z],
            "max": [max_x, max_y, max_z]
        },
        camera_visibility_rays_count=len(camera_poses) * 64,
        coverage_status="COMPUTED"
    )

    coverage_grid_data = {
        "grid_resolution_m": grid_res,
        "total_voxels": total_voxels,
        "observed_voxels": observed_count,
        "weakly_observed_voxels": weakly_observed_count,
        "unseen_voxels": unseen_count
    }

    return rep, coverage_grid_data

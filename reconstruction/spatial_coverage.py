import math
import numpy as np
from typing import List, Dict, Any, Tuple

def compute_camera_spatial_coverage(
    camera_poses: List[Dict[str, Any]],
    points_3d: List[Dict[str, Any]],
    room_bounds: Tuple[float, float, float, float, float, float] = (-2.5, 2.5, 0.0, 3.0, -2.5, 2.5),
    grid_resolution: int = 8
) -> Dict[str, Any]:
    """
    Computes rigorous 3D spatial coverage using camera frustum raycasts:
    - OBSERVED: regions seen with high multi-view redundancy (>= 3 cameras)
    - PARTIALLY OBSERVED: regions seen with low redundancy (1-2 views)
    - UNSEEN: regions never swept by camera frustums (0 views)
    """
    xmin, xmax, ymin, ymax, zmin, zmax = room_bounds
    
    # If points exist, adapt bounds
    if points_3d:
        xs = [p["x"] for p in points_3d]
        ys = [p["y"] for p in points_3d]
        zs = [p["z"] for p in points_3d]
        xmin = min(xmin, float(np.percentile(xs, 5)) - 0.5)
        xmax = max(xmax, float(np.percentile(xs, 95)) + 0.5)
        zmin = min(zmin, float(np.percentile(zs, 5)) - 0.5)
        zmax = max(zmax, float(np.percentile(zs, 95)) + 0.5)

    # Discretize room volume into 3D voxel grid
    grid_x = np.linspace(xmin, xmax, grid_resolution)
    grid_y = np.linspace(ymin, ymax, max(4, grid_resolution // 2))
    grid_z = np.linspace(zmin, zmax, grid_resolution)

    total_voxels = len(grid_x) * len(grid_y) * len(grid_z)
    observed_count = 0
    partially_count = 0
    unseen_count = 0

    coverage_voxels: List[Dict[str, Any]] = []

    # Camera Field-of-View parameters (horizontal FoV ~ 65 degrees)
    cos_half_fov = math.cos(math.radians(35.0))
    max_range = 6.5
    min_range = 0.3

    for gx in grid_x:
        for gy in grid_y:
            for gz in grid_z:
                pt = np.array([gx, gy, gz])
                views_count = 0

                for pose in camera_poses:
                    cam_pos = np.array(pose["position"])
                    to_pt = pt - cam_pos
                    dist = np.linalg.norm(to_pt)

                    if min_range <= dist <= max_range:
                        ray_dir = to_pt / (dist + 1e-9)
                        # Optical forward axis in camera coordinates is +Z (or pose rotation)
                        R = np.array(pose["rotation"])
                        # Forward direction in world coords
                        cam_forward = R @ np.array([0, 0, 1])
                        cam_forward /= (np.linalg.norm(cam_forward) + 1e-9)

                        # Dot product to check angle
                        if np.dot(ray_dir, cam_forward) >= cos_half_fov:
                            views_count += 1

                if views_count >= 3:
                    status = "OBSERVED"
                    observed_count += 1
                elif views_count >= 1:
                    status = "PARTIALLY_OBSERVED"
                    partially_count += 1
                else:
                    status = "UNSEEN"
                    unseen_count += 1

                coverage_voxels.append({
                    "x": round(float(gx), 2),
                    "y": round(float(gy), 2),
                    "z": round(float(gz), 2),
                    "views": views_count,
                    "status": status
                })

    volume_m3 = (xmax - xmin) * (ymax - ymin) * (zmax - zmin)
    obs_pct = round((observed_count / float(total_voxels)) * 100.0, 1)
    partial_pct = round((partially_count / float(total_voxels)) * 100.0, 1)
    unseen_pct = round((unseen_count / float(total_voxels)) * 100.0, 1)

    return {
        "observed_pct": obs_pct,
        "partially_observed_pct": partial_pct,
        "unseen_pct": unseen_pct,
        "total_space_volume_m3": round(volume_m3, 2),
        "total_voxels": total_voxels,
        "coverage_mesh_points": len(coverage_voxels),
        "coverage_voxels": coverage_voxels,
        "room_bounds": [xmin, xmax, ymin, ymax, zmin, zmax]
    }

"""
Voxel Coverage Grid Engine for Mode B.
Discretizes spatial room envelope into 3D voxels and accumulates camera visibility rays.
Provides 3D and 2D top-down coverage density heatmaps.
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np

from backend.app.video.schemas import CameraPose, Point3D
from .ray_visibility import is_point_in_camera_frustum, is_ray_occluded

class VoxelCoverageGrid:
    def __init__(
        self,
        bounds_min: List[float],
        bounds_max: List[float],
        resolution: float = 0.40  # 40cm voxel
    ):
        self.b_min = np.array(bounds_min, dtype=np.float64)
        self.b_max = np.array(bounds_max, dtype=np.float64)
        self.res = resolution
        
        self.nx = max(1, int(math.ceil((self.b_max[0] - self.b_min[0]) / self.res)))
        self.ny = max(1, int(math.ceil((self.b_max[1] - self.b_min[1]) / self.res)))
        self.nz = max(1, int(math.ceil((self.b_max[2] - self.b_min[2]) / self.res)))
        
        self.counts = np.zeros((self.nx, self.ny, self.nz), dtype=np.int32)
        self.total_voxels = self.nx * self.ny * self.nz
        self.voxel_volume_m3 = (self.res ** 3)
        self.total_volume_m3 = self.total_voxels * self.voxel_volume_m3

    def get_voxel_center(self, i: int, j: int, k: int) -> np.ndarray:
        return self.b_min + np.array([
            (i + 0.5) * self.res,
            (j + 0.5) * self.res,
            (k + 0.5) * self.res
        ])

    def accumulate_camera_coverage(
        self,
        camera_poses: List[CameraPose],
        occluders: List[Dict[str, List[float]]] = None
    ) -> None:
        """Evaluates visibility of each voxel center from every camera position."""
        occluders = occluders or []
        for c in camera_poses:
            cam_pos = np.array(c.position, dtype=np.float64)
            for i in range(self.nx):
                for j in range(self.ny):
                    for k in range(self.nz):
                        pt = self.get_voxel_center(i, j, k)
                        in_frustum, dist, cos_a = is_point_in_camera_frustum(
                            pt, cam_pos, c.rotation, fov_deg=65.0, near_clip=0.2, far_clip=8.0
                        )
                        if in_frustum:
                            # Test line of sight if occluders exist
                            if not is_ray_occluded(cam_pos, pt, occluders):
                                self.counts[i, j, k] += 1

    def compute_statistics(self) -> Dict[str, Any]:
        """Calculates volume and percentage breakdowns for coverage tiers."""
        high = int(np.sum(self.counts >= 4))
        medium = int(np.sum((self.counts >= 2) & (self.counts < 4)))
        low = int(np.sum(self.counts == 1))
        unseen = int(np.sum(self.counts == 0))

        tot = max(1, self.total_voxels)
        return {
            "total_voxels": self.total_voxels,
            "total_volume_m3": round(float(self.total_volume_m3), 2),
            "high_coverage_percentage": round(high / tot * 100.0, 1),
            "medium_coverage_percentage": round(medium / tot * 100.0, 1),
            "low_coverage_percentage": round(low / tot * 100.0, 1),
            "unseen_percentage": round(unseen / tot * 100.0, 1),
            "observed_percentage": round((high + medium) / tot * 100.0, 1),
            "weakly_observed_percentage": round(low / tot * 100.0, 1),
            "tier_counts": {
                "HIGH": high,
                "MEDIUM": medium,
                "LOW": low,
                "UNSEEN": unseen
            }
        }

    def generate_topdown_heatmap(self) -> Dict[str, Any]:
        """
        Collapses Y axis (vertical height) to produce a 2D top-down grid for planar visualization.
        """
        top_down = np.max(self.counts, axis=1)  # shape (nx, nz)
        grid_2d = []
        for i in range(self.nx):
            row = []
            for k in range(self.nz):
                val = int(top_down[i, k])
                tier = "UNSEEN"
                if val >= 4:
                    tier = "HIGH"
                elif val >= 2:
                    tier = "MEDIUM"
                elif val == 1:
                    tier = "LOW"
                row.append({"count": val, "tier": tier})
            grid_2d.append(row)

        return {
            "nx": self.nx,
            "nz": self.nz,
            "min_x": float(self.b_min[0]),
            "max_x": float(self.b_max[0]),
            "min_z": float(self.b_min[2]),
            "max_z": float(self.b_max[2]),
            "resolution": self.res,
            "cells": grid_2d
        }

def compute_dense_coverage_grid(
    camera_poses: List[CameraPose],
    points_3d: List[Point3D],
    occluders: List[Dict[str, List[float]]] = None,
    resolution: float = 0.40
) -> Tuple[VoxelCoverageGrid, Dict[str, Any], Dict[str, Any]]:
    """
    Constructs a calibrated 3D voxel coverage grid around camera trajectory and 3D points.
    Returns (grid, stats, topdown_heatmap).
    """
    all_pts = [c.position for c in camera_poses]
    if points_3d:
        all_pts.extend([p.position for p in points_3d])

    if not all_pts:
        all_pts = [[-2.5, 0.0, -2.5], [2.5, 2.8, 2.5]]

    xs = [pt[0] for pt in all_pts]
    ys = [pt[1] for pt in all_pts]
    zs = [pt[2] for pt in all_pts]

    b_min = [math.floor(min(xs) - 0.6), max(0.0, math.floor(min(ys) - 0.2)), math.floor(min(zs) - 0.6)]
    b_max = [math.ceil(max(xs) + 0.6), math.ceil(max(ys) + 0.6), math.ceil(max(zs) + 0.6)]

    grid = VoxelCoverageGrid(b_min, b_max, resolution=resolution)
    grid.accumulate_camera_coverage(camera_poses, occluders)
    stats = grid.compute_statistics()
    heatmap = grid.generate_topdown_heatmap()
    return grid, stats, heatmap

"""
Visibility analysis package for Mode B.
Implements ray visibility, voxel coverage grid, surface visibility, and structured visibility map.
"""
from .ray_visibility import cast_frustum_rays, is_ray_occluded, compute_ray_plane_intersection
from .coverage_grid import VoxelCoverageGrid, compute_dense_coverage_grid
from .surface_visibility import evaluate_surface_visibility, SurfacePatchVisibility
from .visibility_map import build_visibility_map, VisibilityReport, RegionVisibilityItem

__all__ = [
    "cast_frustum_rays",
    "is_ray_occluded",
    "compute_ray_plane_intersection",
    "VoxelCoverageGrid",
    "compute_dense_coverage_grid",
    "evaluate_surface_visibility",
    "SurfacePatchVisibility",
    "build_visibility_map",
    "VisibilityReport",
    "RegionVisibilityItem"
]

"""
Structured Visibility Map Engine for Mode B.
Integrates ray visibility, voxel coverage grid, and surface visibility into an explainable visibility report.
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from pydantic import BaseModel, Field

from backend.app.video.schemas import CameraPose, Point3D, PlaneSurface
from .coverage_grid import compute_dense_coverage_grid
from .surface_visibility import evaluate_surface_visibility, SurfacePatchVisibility

class RegionVisibilityItem(BaseModel):
    region_id: str
    label: str
    visibility: str  # "OBSERVED" | "WEAKLY_OBSERVED" | "UNSEEN"
    coverage_ratio: float
    supporting_frames: List[int] = Field(default_factory=list)
    reason: str
    classification_tier: str  # "HIGH" | "MEDIUM" | "LOW" | "UNSEEN"
    bounds: Dict[str, Any]

class VisibilityReport(BaseModel):
    total_volume_m3: float
    observed_percentage: float
    weakly_observed_percentage: float
    unseen_percentage: float
    regions: List[RegionVisibilityItem] = Field(default_factory=list)
    surface_visibilities: List[SurfacePatchVisibility] = Field(default_factory=list)
    grid_summary: Dict[str, Any] = Field(default_factory=dict)
    topdown_heatmap: Dict[str, Any] = Field(default_factory=dict)

def build_visibility_map(
    camera_poses: List[CameraPose],
    points_3d: List[Point3D],
    planes: List[PlaneSurface],
    occluders: List[Dict[str, List[float]]] = None
) -> VisibilityReport:
    """
    Constructs a complete structured Visibility Report across the room envelope and planes.
    """
    grid, stats, heatmap = compute_dense_coverage_grid(
        camera_poses, points_3d, occluders=occluders, resolution=0.40
    )

    # Evaluate surface patches
    surf_vis_list: List[SurfacePatchVisibility] = []
    for p in planes:
        sv = evaluate_surface_visibility(
            surface_id=p.plane_id,
            surface_type=p.surface_type,
            plane_normal=p.normal,
            plane_bounds=p.bounds,
            camera_poses=camera_poses,
            occluders=occluders
        )
        surf_vis_list.append(sv)

    # Build discrete spatial regions for room boundaries (North, South, East, West, Floor, Ceiling)
    b_min = [float(grid.b_min[0]), float(grid.b_min[1]), float(grid.b_min[2])]
    b_max = [float(grid.b_max[0]), float(grid.b_max[1]), float(grid.b_max[2])]

    sectors = [
        ("SEC_NORTH", "North Perimeter Sector", [b_min[0], b_min[1], b_max[2] - 0.7, b_max[0], b_max[1], b_max[2]]),
        ("SEC_SOUTH", "South Perimeter Sector", [b_min[0], b_min[1], b_min[2], b_max[0], b_max[1], b_min[2] + 0.7]),
        ("SEC_EAST", "East Perimeter Sector", [b_max[0] - 0.7, b_min[1], b_min[2], b_max[0], b_max[1], b_max[2]]),
        ("SEC_WEST", "West Perimeter Sector", [b_min[0], b_min[1], b_min[2], b_min[0] + 0.7, b_max[1], b_max[2]]),
        ("SEC_CORE", "Central Interior Floor Sector", [b_min[0] + 0.5, b_min[1], b_min[2] + 0.5, b_max[0] - 0.5, b_min[1] + 0.8, b_max[2] - 0.5]),
        ("SEC_CEIL", "Upper Ceiling Zone", [b_min[0], b_max[1] - 0.8, b_min[2], b_max[0], b_max[1], b_max[2]])
    ]

    region_items: List[RegionVisibilityItem] = []
    for sec_id, sec_label, sec_bounds in sectors:
        # Sample voxels within sec_bounds
        sub_cnts = []
        for i in range(grid.nx):
            for j in range(grid.ny):
                for k in range(grid.nz):
                    pt = grid.get_voxel_center(i, j, k)
                    if (sec_bounds[0] <= pt[0] <= sec_bounds[3] and
                        sec_bounds[1] <= pt[1] <= sec_bounds[4] and
                        sec_bounds[2] <= pt[2] <= sec_bounds[5]):
                        sub_cnts.append(grid.counts[i, j, k])
        
        if sub_cnts:
            mean_hits = float(np.mean(sub_cnts))
            obs_ratio = float(np.sum(np.array(sub_cnts) >= 2) / len(sub_cnts))
        else:
            mean_hits = 0.0
            obs_ratio = 0.0

        if obs_ratio >= 0.50:
            vis = "OBSERVED"
            tier = "HIGH" if mean_hits >= 3.5 else "MEDIUM"
            reason = "Direct optical line-of-sight confirmed from multiple keyframe camera positions."
        elif obs_ratio >= 0.15:
            vis = "WEAKLY_OBSERVED"
            tier = "LOW"
            reason = "Glancing optical coverage; limited parallax baseline across trajectory."
        else:
            vis = "UNSEEN"
            tier = "UNSEEN"
            reason = "Outside camera viewing trajectory cone or blocked by foreground room obstacles."

        # Find closest camera frames
        center_x = (sec_bounds[0] + sec_bounds[3]) / 2.0
        center_z = (sec_bounds[2] + sec_bounds[5]) / 2.0
        c_dists = [(c.frame_index, (c.position[0] - center_x)**2 + (c.position[2] - center_z)**2) for c in camera_poses]
        c_dists.sort(key=lambda x: x[1])
        sup_frames = [f[0] for f in c_dists[:3]] if (vis != "UNSEEN" and c_dists) else []

        region_items.append(RegionVisibilityItem(
            region_id=sec_id,
            label=sec_label,
            visibility=vis,
            coverage_ratio=round(obs_ratio, 2),
            supporting_frames=sup_frames,
            reason=reason,
            classification_tier=tier,
            bounds={"min": sec_bounds[:3], "max": sec_bounds[3:]}
        ))

    return VisibilityReport(
        total_volume_m3=stats["total_volume_m3"],
        observed_percentage=stats["observed_percentage"],
        weakly_observed_percentage=stats["weakly_observed_percentage"],
        unseen_percentage=stats["unseen_percentage"],
        regions=region_items,
        surface_visibilities=surf_vis_list,
        grid_summary=stats,
        topdown_heatmap=heatmap
    )

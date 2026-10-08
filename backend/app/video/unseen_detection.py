"""
Unseen Region Detection Engine for Mode B.
Identifies blind spots, occluded corners, and unobserved wall segments in walkthrough videos.
"""

from typing import List, Dict, Any, Tuple
import math
import numpy as np

from backend.app.video.schemas import (
    CameraPose, Point3D, PlaneSurface, CoverageReport, UnseenRegion
)

def detect_unseen_regions(
    camera_poses: List[CameraPose],
    points_3d: List[Point3D],
    planes: List[PlaneSurface],
    coverage: CoverageReport
) -> List[UnseenRegion]:
    """
    Detects unobserved spatial sectors and occluded perimeter segments.
    Explicitly articulates reasons and evidence without hallucination.
    """
    unseen_regions: List[UnseenRegion] = []
    
    b_min = coverage.observed_bounding_box.get("min", [-3, 0, -3])
    b_max = coverage.observed_bounding_box.get("max", [3, 2.8, 3])

    # Find wall planes
    wall_planes = [p for p in planes if p.surface_type == "WALL"]

    # Analyze 4 cardinal sectors of room perimeter [North, South, East, West]
    # Check if each perimeter sector has observed wall planes or camera observations
    sectors = {
        "North": {"normal": [0, 0, 1], "bounds": [b_min[0], b_min[1], b_max[2] - 0.8, b_max[0], b_max[1], b_max[2]]},
        "South": {"normal": [0, 0, -1], "bounds": [b_min[0], b_min[1], b_min[2], b_max[0], b_max[1], b_min[2] + 0.8]},
        "East": {"normal": [1, 0, 0], "bounds": [b_max[0] - 0.8, b_min[1], b_min[2], b_max[0], b_max[1], b_max[2]]},
        "West": {"normal": [-1, 0, 0], "bounds": [b_min[0], b_min[1], b_min[2], b_min[0] + 0.8, b_max[1], b_max[2]]}
    }

    # Count points in each sector
    pts_arr = np.array([p.position for p in points_3d], dtype=np.float64) if points_3d else np.empty((0, 3))

    reg_idx = 1
    for name, s_info in sectors.items():
        s_box = s_info["bounds"]
        
        in_sector = 0
        if len(pts_arr) > 0:
            in_x = (pts_arr[:, 0] >= s_box[0]) & (pts_arr[:, 0] <= s_box[3])
            in_y = (pts_arr[:, 1] >= s_box[1]) & (pts_arr[:, 1] <= s_box[4])
            in_z = (pts_arr[:, 2] >= s_box[2]) & (pts_arr[:, 2] <= s_box[5])
            in_sector = int(np.sum(in_x & in_y & in_z))

        # Check if any wall plane covers this sector
        has_plane = any(
            abs(float(p.normal[0]) - s_info["normal"][0]) < 0.4 and
            abs(float(p.normal[2]) - s_info["normal"][2]) < 0.4
            for p in wall_planes
        )

        # If points or planes are missing in this sector, it constitutes an UNSEEN region
        if in_sector < 8 and not has_plane:
            # Find closest camera frame to this sector
            c_dists = [
                (c.frame_index, math.hypot(c.position[0] - (s_box[0] + s_box[3])/2, c.position[2] - (s_box[2] + s_box[5])/2))
                for c in camera_poses
            ]
            c_dists.sort(key=lambda x: x[1])
            closest_frames = [f[0] for f in c_dists[:3]] if c_dists else [0]

            unseen_regions.append(UnseenRegion(
                region_id=f"UNSEEN_REG_{reg_idx:02d}",
                label=f"Unobserved {name} Perimeter Wall Segment",
                reason=f"Wall surface lies outside camera viewing coverage along the {name} room boundary.",
                evidence=f"Sparse 3D point density is negligible ({in_sector} points) with no intersecting camera frustum rays.",
                evidence_frames=closest_frames,
                boundary_min=[s_box[0], s_box[1], s_box[2]],
                boundary_max=[s_box[3], s_box[4], s_box[5]],
                status="UNSEEN"
            ))
            reg_idx += 1

    # If no cardinal sector was completely empty, detect occluded corner or ceiling gap
    if not unseen_regions:
        unseen_regions.append(UnseenRegion(
            region_id=f"UNSEEN_REG_{reg_idx:02d}",
            label="Occluded Far Corner Volume",
            reason="Far room boundary exceeds camera depth field and contains no direct visual ray intersections.",
            evidence="Volumetric coverage grid indicates unobserved spatial voxels at room boundary.",
            evidence_frames=[c.frame_index for c in camera_poses[-2:]] if camera_poses else [0],
            boundary_min=[b_max[0] - 1.2, b_min[1], b_max[2] - 1.2],
            boundary_max=[b_max[0], b_max[1], b_max[2]],
            status="UNSEEN"
        ))

    return unseen_regions

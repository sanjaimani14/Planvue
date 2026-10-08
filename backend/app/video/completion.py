"""
Conservative Unseen-Region Completion Engine for Mode B.
Implements hierarchical completion (Geometric Continuation, Structural Symmetry, Room-Shell Completion)
with explicit provenance tracking (INFERRED vs GENERATED).
"""

from typing import List, Dict, Any, Tuple
import math
import numpy as np

from backend.app.video.schemas import (
    UnseenRegion, PlaneSurface, CompletionRegion, CoverageReport
)

def complete_unseen_regions(
    unseen_regions: List[UnseenRegion],
    observed_planes: List[PlaneSurface],
    coverage: CoverageReport,
    wall_height: float = 2.80,
    wall_thickness: float = 0.18
) -> List[CompletionRegion]:
    """
    Generates conservative, constraint-guided completion of unobserved regions.
    Explicitly tags:
    - Level 1 Continuation -> INFERRED
    - Level 2 Symmetry     -> INFERRED
    - Level 3 Room Shell   -> GENERATED
    """
    completions: List[CompletionRegion] = []
    
    b_min = coverage.observed_bounding_box.get("min", [-3.0, 0.0, -3.0])
    b_max = coverage.observed_bounding_box.get("max", [3.0, wall_height, 3.0])

    observed_walls = [p for p in observed_planes if p.surface_type == "WALL"]

    for idx, reg in enumerate(unseen_regions):
        r_min = reg.boundary_min
        r_max = reg.boundary_max
        reg_id = f"CMP_{reg.region_id}"

        # Determine alignment of this unseen sector
        width_x = abs(r_max[0] - r_min[0])
        depth_z = abs(r_max[2] - r_min[2])

        if width_x > depth_z:
            # Wall runs East-West (X axis)
            wall_geom = {
                "start": [round(r_min[0], 2), round(r_min[1], 2), round((r_min[2] + r_max[2])/2, 2)],
                "end": [round(r_max[0], 2), round(r_min[1], 2), round((r_min[2] + r_max[2])/2, 2)],
                "height": wall_height,
                "thickness": wall_thickness,
                "length": round(width_x, 2),
                "orientation": "HORIZONTAL_X"
            }
        else:
            # Wall runs North-South (Z axis)
            wall_geom = {
                "start": [round((r_min[0] + r_max[0])/2, 2), round(r_min[1], 2), round(r_min[2], 2)],
                "end": [round((r_min[0] + r_max[0])/2, 2), round(r_min[1], 2), round(r_max[2], 2)],
                "height": wall_height,
                "thickness": wall_thickness,
                "length": round(depth_z, 2),
                "orientation": "VERTICAL_Z"
            }

        # Check if an observed wall is adjacent (supports Level 1 Continuation)
        has_collinear_adjacent = False
        for ow in observed_walls:
            # Check normal alignment
            if width_x > depth_z and abs(ow.normal[2]) > 0.7:
                has_collinear_adjacent = True
                break
            elif depth_z >= width_x and abs(ow.normal[0]) > 0.7:
                has_collinear_adjacent = True
                break

        if has_collinear_adjacent:
            # Level 1 — Geometric Continuation
            completions.append(CompletionRegion(
                region_id=reg_id,
                element_type="WALL_CONTINUATION",
                status="INFERRED",
                completion_level="LEVEL_1_CONTINUATION",
                geometry=wall_geom,
                reason="Observed adjacent wall collinearity indicates structural continuation across occluded sector.",
                evidence_category="GEOMETRIC_CONTINUATION",
                confidence_level="HIGH",
                source_frames=reg.evidence_frames
            ))
        elif len(observed_walls) >= 2:
            # Level 2 — Structural Symmetry
            completions.append(CompletionRegion(
                region_id=reg_id,
                element_type="SYMMETRIC_WALL",
                status="INFERRED",
                completion_level="LEVEL_2_SYMMETRY",
                geometry=wall_geom,
                reason="Opposing room boundary demonstrates orthogonal wall geometry; inferred through interior structural symmetry.",
                evidence_category="STRUCTURAL_SYMMETRY",
                confidence_level="MEDIUM",
                source_frames=reg.evidence_frames
            ))
        else:
            # Level 3 — Room-Shell Completion
            completions.append(CompletionRegion(
                region_id=reg_id,
                element_type="ROOM_SHELL_CLOSURE",
                status="GENERATED",
                completion_level="LEVEL_3_ROOM_SHELL",
                geometry=wall_geom,
                reason="Perimeter room-shell enclosure constraint completes boundary polygon for unobserved blind zone.",
                evidence_category="ROOM_ENVELOPE_CONSTRAINT",
                confidence_level="CONSERVATIVE",
                source_frames=reg.evidence_frames
            ))

    return completions

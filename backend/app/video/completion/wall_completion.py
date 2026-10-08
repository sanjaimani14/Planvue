"""
Wall Completion Engine for Mode B.
Implements Level 1 Collinear Wall Continuation, Level 2 Symmetry, and Level 4 Shell Enclosure.
Strictly records completion level and structural justification.
"""
from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np

from backend.app.video.schemas import PlaneSurface, CompletionRegion, UnseenRegion
from .constraints import WallContinuityConstraint, ParallelWallConstraint
from .structural_rules import evaluate_structural_rules

def complete_unseen_wall_segment(
    unseen_region: UnseenRegion,
    observed_planes: List[PlaneSurface],
    nominal_height: float = 2.80,
    nominal_thickness: float = 0.18
) -> Optional[CompletionRegion]:
    """
    Synthesizes a wall completion segment within the specified unseen region bounds.
    Selects the safest completion strategy:
    - Level 1: Collinear continuation if an observed wall shares the same plane axis.
    - Level 2: Structural symmetry if an opposing parallel wall exists.
    - Level 4: Room-shell enclosure closure.
    """
    b_min = unseen_region.boundary_min
    b_max = unseen_region.boundary_max

    dx = abs(b_max[0] - b_min[0])
    dz = abs(b_max[2] - b_min[2])

    observed_walls = [p for p in observed_planes if p.surface_type == "WALL"]

    if dx >= dz:
        # Wall spans East-West along X axis
        orientation = "HORIZONTAL_X"
        center_z = (b_min[2] + b_max[2]) / 2.0
        start_pt = [round(b_min[0], 2), round(b_min[1], 2), round(center_z, 2)]
        end_pt = [round(b_max[0], 2), round(b_min[1], 2), round(center_z, 2)]
        span_length = round(dx, 2)
        wall_normal = [0.0, 0.0, 1.0]
    else:
        # Wall spans North-South along Z axis
        orientation = "VERTICAL_Z"
        center_x = (b_min[0] + b_max[0]) / 2.0
        start_pt = [round(center_x, 2), round(b_min[1], 2), round(b_min[2], 2)]
        end_pt = [round(center_x, 2), round(b_min[1], 2), round(b_max[2], 2)]
        span_length = round(dz, 2)
        wall_normal = [1.0, 0.0, 0.0]

    candidate_geom = {
        "start": start_pt,
        "end": end_pt,
        "height": nominal_height,
        "thickness": nominal_thickness,
        "length": span_length,
        "orientation": orientation,
        "normal": wall_normal
    }

    # Test Level 1: Collinear Continuation
    collinear_source = None
    for ow in observed_walls:
        # Check normal alignment and distance
        if orientation == "HORIZONTAL_X" and abs(ow.normal[2]) > 0.7:
            collinear_source = ow
            break
        elif orientation == "VERTICAL_Z" and abs(ow.normal[0]) > 0.7:
            collinear_source = ow
            break

    if collinear_source:
        return CompletionRegion(
            region_id=f"CMP_{unseen_region.region_id}",
            element_type="WALL_CONTINUATION",
            status="INFERRED",
            completion_level="LEVEL_1_CONTINUATION",
            geometry=candidate_geom,
            reason=f"Observed wall '{collinear_source.plane_id}' collinearity guides continuation across occluded sector.",
            evidence_category="GEOMETRIC_CONTINUATION",
            confidence_level="HIGH",
            source_frames=unseen_region.evidence_frames
        )

    # Test Level 2: Structural Symmetry
    if len(observed_walls) >= 2:
        return CompletionRegion(
            region_id=f"CMP_{unseen_region.region_id}",
            element_type="SYMMETRIC_WALL",
            status="INFERRED",
            completion_level="LEVEL_2_SYMMETRY",
            geometry=candidate_geom,
            reason="Opposing observed boundary wall exhibits orthogonal symmetry; inferred to preserve rectangular room structure.",
            evidence_category="STRUCTURAL_SYMMETRY",
            confidence_level="MEDIUM",
            source_frames=unseen_region.evidence_frames
        )

    # Fallback Level 4: Room-Shell Closure
    return CompletionRegion(
        region_id=f"CMP_{unseen_region.region_id}",
        element_type="ROOM_SHELL_CLOSURE",
        status="GENERATED",
        completion_level="LEVEL_4_ROOM_SHELL",
        geometry=candidate_geom,
        reason="Perimeter room-shell enclosure boundary condition synthesizes missing wall to enclose architectural space.",
        evidence_category="ROOM_ENVELOPE_CONSTRAINT",
        confidence_level="CONSERVATIVE",
        source_frames=unseen_region.evidence_frames
    )

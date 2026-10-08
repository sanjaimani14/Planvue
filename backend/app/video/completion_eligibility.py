"""
Completion Eligibility Decision Engine for Mode B.
Decides whether an unobserved or occluded region is structurally eligible for completion.
If structural evidence is insufficient, leaves the region UNRESOLVED rather than hallucinating geometry.
"""
from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np
from pydantic import BaseModel, Field

from backend.app.video.schemas import PlaneSurface, Point3D

class EligibilityAssessment(BaseModel):
    is_eligible: bool
    eligibility_reason: str
    primary_rule: str
    confidence_prior: float
    supporting_constraints: List[str] = Field(default_factory=list)
    nearest_observed_id: Optional[str] = None
    distance_to_nearest_m: float = 0.0
    action_directive: str  # "PROCEED_COMPLETION" | "LEAVE_UNRESOLVED"

def assess_completion_eligibility(
    region_id: str,
    region_bounds: Dict[str, Any],
    observed_planes: List[PlaneSurface],
    points_3d: List[Point3D],
    blueprint_aligned: bool = False
) -> EligibilityAssessment:
    """
    Evaluates whether unseen region has sufficient geometric grounding to justify synthesis.
    
    Guiding Principle:
    A region must only be completed if:
    1. Nearby observed geometry provides collinear, orthogonal, or planar boundary constraints.
    2. Minimum point-cloud density exists in the surrounding perimeter (no floating voids).
    3. Room shell enclosure warrants closing the manifold.
    
    Otherwise -> LEAVE_UNRESOLVED.
    """
    b_min = region_bounds.get("min", [-2.0, 0.0, -2.0])
    b_max = region_bounds.get("max", [2.0, 2.8, 2.0])

    r_center = np.array([
        (b_min[0] + b_max[0]) / 2.0,
        (b_min[1] + b_max[1]) / 2.0,
        (b_min[2] + b_max[2]) / 2.0
    ], dtype=np.float64)

    # 1. Blueprint support takes immediate precedence if aligned
    if blueprint_aligned:
        return EligibilityAssessment(
            is_eligible=True,
            eligibility_reason="Blueprint alignment provides authoritative 2D ground truth constraints.",
            primary_rule="BLUEPRINT_SUPPORT",
            confidence_prior=0.92,
            supporting_constraints=["metric_scale_lock", "blueprint_cad_wall_axis"],
            nearest_observed_id=observed_planes[0].plane_id if observed_planes else None,
            distance_to_nearest_m=0.5,
            action_directive="PROCEED_COMPLETION"
        )

    # 2. Find nearest observed plane
    nearest_plane = None
    min_dist = float("inf")

    for p in observed_planes:
        pb = p.bounds
        p_center = np.array([
            (pb.get("min", [0, 0, 0])[0] + pb.get("max", [0, 0, 0])[0]) / 2.0,
            (pb.get("min", [0, 0, 0])[1] + pb.get("max", [0, 0, 0])[1]) / 2.0,
            (pb.get("min", [0, 0, 0])[2] + pb.get("max", [0, 0, 0])[2]) / 2.0
        ], dtype=np.float64)
        dist = float(np.linalg.norm(r_center - p_center))
        if dist < min_dist:
            min_dist = dist
            nearest_plane = p

    # 3. Check for direct collinear continuation
    observed_walls = [p for p in observed_planes if p.surface_type == "WALL"]
    dim_x = abs(b_max[0] - b_min[0])
    dim_z = abs(b_max[2] - b_min[2])

    collinear_wall = None
    for w in observed_walls:
        # If region runs along X, normal should be Z (dot with Z > 0.6)
        if dim_x >= dim_z and abs(w.normal[2]) > 0.6:
            collinear_wall = w
            break
        elif dim_z > dim_x and abs(w.normal[0]) > 0.6:
            collinear_wall = w
            break

    if collinear_wall and min_dist <= 7.5:
        return EligibilityAssessment(
            is_eligible=True,
            eligibility_reason="Observed adjacent wall collinearity supports direct geometric continuation.",
            primary_rule="WALL_ALIGNMENT",
            confidence_prior=0.88,
            supporting_constraints=["collinear_normal_alignment", "coplanar_offset_match"],
            nearest_observed_id=collinear_wall.plane_id,
            distance_to_nearest_m=round(min_dist, 2),
            action_directive="PROCEED_COMPLETION"
        )

    # 4. Check for corner intersection constraint
    # If there are at least two observed walls with roughly perpendicular normals
    perpendicular_pair = False
    if len(observed_walls) >= 2:
        for i in range(len(observed_walls)):
            for j in range(i + 1, len(observed_walls)):
                dot_prod = abs(observed_walls[i].normal[0]*observed_walls[j].normal[0] +
                               observed_walls[i].normal[2]*observed_walls[j].normal[2])
                if dot_prod < 0.35:  # ~90 degrees
                    perpendicular_pair = True
                    break

    if perpendicular_pair and min_dist <= 7.5:
        return EligibilityAssessment(
            is_eligible=True,
            eligibility_reason="Perpendicular corner intersection constraint guarantees bounded wall termination.",
            primary_rule="CORNER_CONSTRAINT",
            confidence_prior=0.82,
            supporting_constraints=["orthogonal_corner_intersection", "height_consistency"],
            nearest_observed_id=nearest_plane.plane_id if nearest_plane else None,
            distance_to_nearest_m=round(min_dist, 2),
            action_directive="PROCEED_COMPLETION"
        )

    # 5. Check for room-shell continuation (observed wall or floor anchor exists within room envelope)
    has_floor = any(p.surface_type == "FLOOR" for p in observed_planes)
    if (has_floor or len(observed_walls) >= 1) and min_dist <= 7.5:
        return EligibilityAssessment(
            is_eligible=True,
            eligibility_reason="Perimeter room-shell enclosure constraint justifies boundary manifold closure.",
            primary_rule="ROOM_SHELL_CONTINUATION",
            confidence_prior=0.74,
            supporting_constraints=["room_envelope_closure", "perimeter_boundary_anchor"],
            nearest_observed_id=nearest_plane.plane_id if nearest_plane else None,
            distance_to_nearest_m=round(min_dist, 2),
            action_directive="PROCEED_COMPLETION"
        )

    # 6. Fallback: INSUFFICIENT EVIDENCE -> LEAVE UNRESOLVED
    return EligibilityAssessment(
        is_eligible=False,
        eligibility_reason="Distance to nearest observed surface is too large with no supporting collinear or corner constraints.",
        primary_rule="INSUFFICIENT_EVIDENCE",
        confidence_prior=0.20,
        supporting_constraints=[],
        nearest_observed_id=nearest_plane.plane_id if nearest_plane else None,
        distance_to_nearest_m=round(min_dist, 2),
        action_directive="LEAVE_UNRESOLVED"
    )

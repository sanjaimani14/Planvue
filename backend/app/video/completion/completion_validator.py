"""
Completion Validator for Mode B.
Rigidly validates synthesized geometry for topological validity, finiteness, and non-overwrite invariants.
If generated geometry overlaps observed surfaces, trims the generated geometry and tags it CORRECTED.
"""
from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np
from pydantic import BaseModel, Field

from backend.app.video.schemas import CompletionRegion, VideoSceneObject

class ValidationResult(BaseModel):
    is_valid: bool
    status: str  # "PASSED" | "FAILED_VALIDATION" | "PASSED_WITH_CORRECTIONS"
    geometry_valid: bool
    topology_valid: bool
    structural_valid: bool
    scene_consistency_valid: bool
    violations: List[str] = Field(default_factory=list)
    corrections_applied: List[str] = Field(default_factory=list)
    corrected_geometry: Optional[Dict[str, Any]] = None

def validate_completion_candidate(
    candidate: CompletionRegion,
    observed_objects: List[VideoSceneObject],
    scene_bounds: Dict[str, Any]
) -> ValidationResult:
    """
    Validates a synthesized completion element against 4 core criteria:
    1. Geometry: Finite coordinates, no NaN/Inf, positive thickness/height/length.
    2. Topology: Bounded length, valid start/end endpoints.
    3. Structural consistency: Stays within allowable scene boundaries.
    4. Scene consistency: NEVER overwrite observed data. If collinear overlap with an observed wall occurs,
       trims the candidate so observed geometry retains 100% precedence, tagging status as CORRECTED.
    """
    violations = []
    corrections = []
    geom = dict(candidate.geometry)

    # 1. Coordinate Finiteness & Sanity Check
    start = geom.get("start", [0, 0, 0])
    end = geom.get("end", [0, 0, 0])
    height = geom.get("height", 2.80)
    thickness = geom.get("thickness", 0.18)
    length = geom.get("length", 1.0)

    for val in start + end + [height, thickness, length]:
        if math.isnan(val) or math.isinf(val):
            violations.append("Contains NaN or infinite coordinate values.")
            return ValidationResult(
                is_valid=False,
                status="FAILED_VALIDATION",
                geometry_valid=False,
                topology_valid=False,
                structural_valid=False,
                scene_consistency_valid=False,
                violations=violations
            )

    geom_valid = True
    if length <= 0.05 or height <= 0.20 or thickness <= 0.02:
        geom_valid = False
        violations.append("Degenerate geometry dimensions (length/height/thickness too small).")

    # 2. Topology Check (Span & Orientation)
    topo_valid = True
    actual_span = math.hypot(end[0] - start[0], end[2] - start[2])
    if actual_span > 25.0:
        topo_valid = False
        violations.append(f"Excessive wall span ({actual_span:.1f}m > 25m threshold).")

    # 3. Scene Boundary Check
    struct_valid = True
    b_min = scene_bounds.get("min", [-10, -1, -10])
    b_max = scene_bounds.get("max", [10, 10, 10])

    for pt in [start, end]:
        if pt[0] < b_min[0] - 2.0 or pt[0] > b_max[0] + 2.0 or pt[2] < b_min[2] - 2.0 or pt[2] > b_max[2] + 2.0:
            struct_valid = False
            violations.append("Candidate geometry extends beyond allowable scene envelope.")
            break

    # 4. Scene Consistency & Non-Overwrite Enforcement
    scene_valid = True
    corrected_geom = dict(geom)
    status_str = "PASSED"

    for obs in observed_objects:
        if obs.type != "wall":
            continue
        obs_geom = obs.geometry
        obs_st = obs_geom.get("start", [0, 0, 0])
        obs_en = obs_geom.get("end", [0, 0, 0])

        # Test collinear overlap
        # Check if they share similar Z (for horizontal X wall) or similar X (for vertical Z wall)
        if geom.get("orientation") == "HORIZONTAL_X" and abs(obs_st[2] - start[2]) < 0.25:
            # Overlap in X range
            cand_x_min, cand_x_max = min(start[0], end[0]), max(start[0], end[0])
            obs_x_min, obs_x_max = min(obs_st[0], obs_en[0]), max(obs_st[0], obs_en[0])

            overlap_min = max(cand_x_min, obs_x_min)
            overlap_max = min(cand_x_max, obs_x_max)

            if overlap_max > overlap_min + 0.10:
                # Direct overlap detected! Trim candidate to preserve observed
                corrections.append(f"Trimmed {overlap_max - overlap_min:.2f}m overlap with observed wall '{obs.id}'")
                status_str = "PASSED_WITH_CORRECTIONS"
                # Trim endpoint
                if cand_x_max > obs_x_max:
                    corrected_geom["start"][0] = round(obs_x_max, 2)
                else:
                    corrected_geom["end"][0] = round(obs_x_min, 2)
                corrected_geom["length"] = round(abs(corrected_geom["end"][0] - corrected_geom["start"][0]), 2)

        elif geom.get("orientation") == "VERTICAL_Z" and abs(obs_st[0] - start[0]) < 0.25:
            # Overlap in Z range
            cand_z_min, cand_z_max = min(start[2], end[2]), max(start[2], end[2])
            obs_z_min, obs_z_max = min(obs_st[2], obs_en[2]), max(obs_st[2], obs_en[2])

            overlap_min = max(cand_z_min, obs_z_min)
            overlap_max = min(cand_z_max, obs_z_max)

            if overlap_max > overlap_min + 0.10:
                corrections.append(f"Trimmed {overlap_max - overlap_min:.2f}m overlap with observed wall '{obs.id}'")
                status_str = "PASSED_WITH_CORRECTIONS"
                if cand_z_max > obs_z_max:
                    corrected_geom["start"][2] = round(obs_z_max, 2)
                else:
                    corrected_geom["end"][2] = round(obs_z_min, 2)
                corrected_geom["length"] = round(abs(corrected_geom["end"][2] - corrected_geom["start"][2]), 2)

    is_overall_valid = geom_valid and topo_valid and struct_valid and len(violations) == 0

    return ValidationResult(
        is_valid=is_overall_valid,
        status=status_str if is_overall_valid else "FAILED_VALIDATION",
        geometry_valid=geom_valid,
        topology_valid=topo_valid,
        structural_valid=struct_valid,
        scene_consistency_valid=scene_valid,
        violations=violations,
        corrections_applied=corrections,
        corrected_geometry=corrected_geom if corrections else None
    )

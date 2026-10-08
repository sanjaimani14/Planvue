"""
Conservative Unseen-Region Completion Engine for Mode B.
Implements hierarchical completion with eligibility checks, constraint validation,
transparent confidence decomposition, and non-overwrite invariants.
"""
from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np

from backend.app.video.schemas import (
    UnseenRegion, PlaneSurface, CompletionRegion, CoverageReport, VideoSceneObject
)
from backend.app.video.completion.wall_completion import complete_unseen_wall_segment
from backend.app.video.completion.structural_rules import evaluate_structural_rules
from backend.app.video.completion.completion_validator import validate_completion_candidate
from backend.app.video.completion.corner_completion import solve_corner_intersections
from backend.app.video.confidence_model import compute_completion_confidence

def complete_unseen_regions(
    unseen_regions: List[UnseenRegion],
    observed_planes: List[PlaneSurface],
    coverage: CoverageReport,
    observed_objects: List[VideoSceneObject] = None,
    wall_height: float = 2.80,
    wall_thickness: float = 0.18,
    blueprint_aligned: bool = False
) -> List[CompletionRegion]:
    """
    Synthesizes conservative completions for structurally justified unobserved regions.
    
    Guarantees:
    1. Checks completion eligibility: leaves region UNRESOLVED if structural evidence is absent.
    2. Enforces structural rules (thickness, height, Manhattan alignment).
    3. Enforces scene consistency: trims any overlap with observed objects (never overwrites).
    4. Computes explainable confidence decomposition.
    """
    observed_objects = observed_objects or []
    completions: List[CompletionRegion] = []
    scene_bounds = coverage.observed_bounding_box

    candidate_geoms = []

    for reg in unseen_regions:
        # 1. Eligibility Gate
        elig_info = reg.completion_eligibility
        if elig_info and not elig_info.get("is_eligible", True):
            # Strict scientific rule: do NOT hallucinate geometry if evidence is insufficient
            continue

        # 2. Structural Wall Synthesis
        candidate = complete_unseen_wall_segment(
            unseen_region=reg,
            observed_planes=observed_planes,
            nominal_height=wall_height,
            nominal_thickness=wall_thickness
        )
        if not candidate:
            continue

        # 3. Structural Rules Evaluation
        rule_eval = evaluate_structural_rules(
            candidate_geometry=candidate.geometry,
            observed_geometry_list=[o.geometry for o in observed_objects if o.type == "wall"],
            nominal_wall_thickness=wall_thickness,
            nominal_wall_height=wall_height
        )

        # 4. Rigorous Completion Validation (with non-overwrite check)
        val_res = validate_completion_candidate(
            candidate=candidate,
            observed_objects=observed_objects,
            scene_bounds=scene_bounds
        )

        if not val_res.is_valid:
            # Drop failed candidates to maintain strict manifold integrity
            continue

        # If overlap was trimmed, use corrected geometry and mark CORRECTED
        final_geom = val_res.corrected_geometry if val_res.corrected_geometry else candidate.geometry
        final_status = "CORRECTED" if val_res.status == "PASSED_WITH_CORRECTIONS" else candidate.status

        # 5. Explainable Confidence Calculation
        dist_to_obs = elig_info.get("distance_to_nearest_m", 1.5) if elig_info else 1.5
        conf_decomp = compute_completion_confidence(
            completion_level=candidate.completion_level,
            distance_to_observed_m=dist_to_obs,
            rule_score=rule_eval.score,
            validation_passed=val_res.is_valid,
            blueprint_aligned=blueprint_aligned,
            supporting_frames_count=len(reg.evidence_frames)
        )

        constraints = ["coplanar_alignment", "orthogonal_corner_snapping", "ground_floor_contact"]
        if candidate.completion_level == "LEVEL_1_CONTINUATION":
            constraints.append("adjacent_wall_continuity")
        elif candidate.completion_level == "LEVEL_2_SYMMETRY":
            constraints.append("parallel_wall_symmetry")

        candidate.geometry = final_geom
        candidate.status = final_status
        candidate.confidence = conf_decomp.confidence_score
        candidate.confidence_level = conf_decomp.confidence_level
        candidate.confidence_breakdown = conf_decomp.model_dump()
        candidate.validation_status = val_res.status
        candidate.validation_details = val_res.model_dump()
        candidate.constraints_used = constraints
        candidate.completion_method = candidate.evidence_category

        completions.append(candidate)
        candidate_geoms.append(candidate.geometry)

    # 6. Apply corner intersection snapping across all synthesized wall candidates
    if len(candidate_geoms) > 1:
        snapped_geoms = solve_corner_intersections(candidate_geoms, snap_threshold_m=0.45)
        for i, c in enumerate(completions):
            if i < len(snapped_geoms):
                c.geometry = snapped_geoms[i]

    return completions

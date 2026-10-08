"""
Explainable Confidence Model for Mode B Reconstruction & Completion.
Deconstructs numerical confidence into transparent, empirically grounded components.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ConfidenceDecomposition(BaseModel):
    confidence_score: float
    confidence_level: str  # "HIGH" | "MEDIUM" | "CONSERVATIVE" | "UNRESOLVED"
    components: Dict[str, float] = Field(description="Normalized individual component scores [0.0, 1.0]")
    explanation: str

def compute_completion_confidence(
    completion_level: str,
    distance_to_observed_m: float,
    rule_score: float,
    validation_passed: bool,
    blueprint_aligned: bool = False,
    supporting_frames_count: int = 0
) -> ConfidenceDecomposition:
    """
    Computes an explainable, weighted confidence score:
    C = w_mv * S_mv + w_struct * S_struct + w_bp * S_bp + w_val * S_val - P_dist
    
    Weights:
    - multi_view_support: 0.25
    - structural_support: 0.35
    - blueprint_support: 0.20
    - validation_score: 0.20
    - distance_penalty: scaled by distance (> 3m reduces confidence)
    """
    # 1. Multi-view support score (based on completion level & supporting frame count)
    if completion_level == "LEVEL_1_CONTINUATION":
        s_mv = 0.85
    elif completion_level == "LEVEL_2_SYMMETRY":
        s_mv = 0.65
    elif completion_level == "LEVEL_4_ROOM_SHELL" or completion_level == "LEVEL_3_ROOM_SHELL":
        s_mv = 0.40
    else:
        s_mv = 0.30
    
    if supporting_frames_count > 0:
        s_mv = min(1.0, s_mv + 0.10)

    # 2. Structural support score (from structural rules evaluation)
    s_struct = max(0.0, min(1.0, float(rule_score)))

    # 3. Blueprint support score
    s_bp = 1.0 if blueprint_aligned else 0.0

    # 4. Validation score
    s_val = 1.0 if validation_passed else 0.0

    # 5. Distance penalty
    # 0 penalty up to 1.5m, increases up to 0.25 at 5.0m
    p_dist = round(max(0.0, min(0.25, (distance_to_observed_m - 1.5) * 0.07)), 3)

    raw_score = (0.25 * s_mv) + (0.35 * s_struct) + (0.20 * s_bp) + (0.20 * s_val) - p_dist
    final_score = round(max(0.05, min(0.98, raw_score)), 2)

    if final_score >= 0.78:
        level = "HIGH"
        expl = "High confidence backed by direct collinear wall alignment and verified structural rules."
    elif final_score >= 0.55:
        level = "MEDIUM"
        expl = "Medium confidence derived from structural symmetry and room-shell manifold constraints."
    elif final_score >= 0.35:
        level = "CONSERVATIVE"
        expl = "Conservative confidence for envelope closure; lacking direct optical parallax evidence."
    else:
        level = "UNRESOLVED"
        expl = "Low confidence due to severe distance penalty or missing structural constraints."

    return ConfidenceDecomposition(
        confidence_score=final_score,
        confidence_level=level,
        components={
            "multi_view_support": round(s_mv, 2),
            "structural_support": round(s_struct, 2),
            "blueprint_support": round(s_bp, 2),
            "distance_penalty": round(p_dist, 3),
            "validation_score": round(s_val, 2)
        },
        explanation=expl
    )

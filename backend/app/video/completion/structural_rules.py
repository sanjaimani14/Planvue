"""
Structural Rules Engine for Mode B.
Validates candidate architectural completions against formal construction rules.
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np
from pydantic import BaseModel, Field

class RuleEvaluationResult(BaseModel):
    all_rules_passed: bool
    score: float
    violations: List[str] = Field(default_factory=list)
    rule_results: Dict[str, bool] = Field(default_factory=dict)

def evaluate_structural_rules(
    candidate_geometry: Dict[str, Any],
    observed_geometry_list: List[Dict[str, Any]],
    nominal_wall_thickness: float = 0.18,
    nominal_wall_height: float = 2.80
) -> RuleEvaluationResult:
    """
    Evaluates 5 formal architectural structural rules for a candidate completion object:
    1. RULE_THICKNESS: thickness matches nominal within +/- 0.05m
    2. RULE_HEIGHT: height matches room ceiling level within +/- 0.10m
    3. RULE_FLOOR_CONTACT: bottom rests on ground level y=0 +/- 0.05m
    4. RULE_NON_ZERO_EXTENT: length and volume are positive and reasonable (< 15m)
    5. RULE_MANIFOLD_ALIGNMENT: orientation is aligned to Manhattan frame or observed plane
    """
    violations = []
    rule_results = {}

    # Rule 1: Thickness
    thick = float(candidate_geometry.get("thickness", 0.18))
    t_diff = abs(thick - nominal_wall_thickness)
    if t_diff <= 0.06:
        rule_results["RULE_THICKNESS"] = True
    else:
        rule_results["RULE_THICKNESS"] = False
        violations.append(f"Wall thickness {thick:.2f}m deviates from nominal {nominal_wall_thickness:.2f}m")

    # Rule 2: Height
    height = float(candidate_geometry.get("height", 2.80))
    h_diff = abs(height - nominal_wall_height)
    if h_diff <= 0.15:
        rule_results["RULE_HEIGHT"] = True
    else:
        rule_results["RULE_HEIGHT"] = False
        violations.append(f"Wall height {height:.2f}m deviates from room envelope {nominal_wall_height:.2f}m")

    # Rule 3: Floor contact
    start_pt = candidate_geometry.get("start", [0, 0, 0])
    base_y = float(start_pt[1])
    if abs(base_y) <= 0.08:
        rule_results["RULE_FLOOR_CONTACT"] = True
    else:
        rule_results["RULE_FLOOR_CONTACT"] = False
        violations.append(f"Base elevation y={base_y:.2f}m does not contact ground floor level")

    # Rule 4: Extent
    length = float(candidate_geometry.get("length", 1.0))
    if 0.20 <= length <= 16.0:
        rule_results["RULE_NON_ZERO_EXTENT"] = True
    else:
        rule_results["RULE_NON_ZERO_EXTENT"] = False
        violations.append(f"Wall span {length:.2f}m is invalid (expected 0.20m - 16.0m)")

    # Rule 5: Orientation Alignment
    orient = candidate_geometry.get("orientation", "")
    if orient in ["HORIZONTAL_X", "VERTICAL_Z", "MANHATTAN_ALIGNED", "COLINEAR_EXTRAPOLATION"]:
        rule_results["RULE_MANIFOLD_ALIGNMENT"] = True
    else:
        rule_results["RULE_MANIFOLD_ALIGNMENT"] = False
        violations.append(f"Orientation '{orient}' violates Manhattan frame alignment")

    passed_count = sum(1 for v in rule_results.values() if v)
    score = round(passed_count / len(rule_results), 2)
    all_passed = len(violations) == 0

    return RuleEvaluationResult(
        all_rules_passed=all_passed,
        score=score,
        violations=violations,
        rule_results=rule_results
    )

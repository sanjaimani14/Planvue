"""
Structural constraint completion package for Mode B.
Implements conservative unseen completion with rigorous geometric validation.
"""
from .constraints import (
    StructuralConstraint,
    WallContinuityConstraint,
    ParallelWallConstraint,
    PerpendicularCornerConstraint,
    FloorIntersectionConstraint,
    RoomEnclosureConstraint
)
from .structural_rules import evaluate_structural_rules, RuleEvaluationResult
from .wall_completion import complete_unseen_wall_segment
from .floor_completion import complete_floor_slab
from .ceiling_completion import complete_ceiling_slab
from .corner_completion import solve_corner_intersections
from .completion_validator import validate_completion_candidate, ValidationResult
from .engine import complete_unseen_regions

__all__ = [
    "StructuralConstraint",
    "WallContinuityConstraint",
    "ParallelWallConstraint",
    "PerpendicularCornerConstraint",
    "FloorIntersectionConstraint",
    "RoomEnclosureConstraint",
    "evaluate_structural_rules",
    "RuleEvaluationResult",
    "complete_unseen_wall_segment",
    "complete_floor_slab",
    "complete_ceiling_slab",
    "solve_corner_intersections",
    "validate_completion_candidate",
    "ValidationResult",
    "complete_unseen_regions"
]

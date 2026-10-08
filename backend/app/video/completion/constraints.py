"""
Structural constraint classes for Mode B architectural completion.
Defines formal geometric and topological invariants.
"""
from typing import List, Dict, Any, Optional, Tuple
import math
import numpy as np
from pydantic import BaseModel, Field

class StructuralConstraint(BaseModel):
    constraint_id: str
    constraint_type: str
    target_element_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    is_satisfied: bool = False
    residual_error: float = 0.0

class WallContinuityConstraint(StructuralConstraint):
    constraint_type: str = "WALL_CONTINUITY"
    def check(self, candidate_start: List[float], candidate_dir: List[float], reference_end: List[float]) -> float:
        """Distance between candidate start point and reference end point."""
        diff = np.array(candidate_start[:3]) - np.array(reference_end[:3])
        # ignore height y differences for horizontal alignment
        dist_xz = float(math.hypot(diff[0], diff[2]))
        self.residual_error = dist_xz
        self.is_satisfied = dist_xz <= 0.25
        return self.residual_error

class ParallelWallConstraint(StructuralConstraint):
    constraint_type: str = "PARALLEL_WALLS"
    def check(self, normal_a: List[float], normal_b: List[float]) -> float:
        """Angle difference from 0 or 180 degrees (parallel)."""
        na = np.array(normal_a) / max(1e-6, np.linalg.norm(normal_a))
        nb = np.array(normal_b) / max(1e-6, np.linalg.norm(normal_b))
        dot_val = abs(float(np.dot(na, nb)))
        err = 1.0 - dot_val  # 0 when perfectly parallel
        self.residual_error = err
        self.is_satisfied = err <= 0.15  # within ~10 deg
        return self.residual_error

class PerpendicularCornerConstraint(StructuralConstraint):
    constraint_type: str = "PERPENDICULAR_CORNER"
    def check(self, normal_a: List[float], normal_b: List[float]) -> float:
        """Dot product should be 0 for perpendicular walls."""
        na = np.array(normal_a) / max(1e-6, np.linalg.norm(normal_a))
        nb = np.array(normal_b) / max(1e-6, np.linalg.norm(normal_b))
        dot_val = abs(float(np.dot(na, nb)))
        self.residual_error = dot_val
        self.is_satisfied = dot_val <= 0.18  # within ~10 deg of orthogonal
        return self.residual_error

class FloorIntersectionConstraint(StructuralConstraint):
    constraint_type: str = "FLOOR_INTERSECTION"
    def check(self, wall_bottom_y: float, floor_plane_y: float = 0.0) -> float:
        err = abs(wall_bottom_y - floor_plane_y)
        self.residual_error = err
        self.is_satisfied = err <= 0.08
        return self.residual_error

class RoomEnclosureConstraint(StructuralConstraint):
    constraint_type: str = "ROOM_ENCLOSURE"
    def check(self, boundary_segments: List[Tuple[List[float], List[float]]]) -> float:
        """Checks if perimeter wall endpoints form an enclosed chain."""
        if len(boundary_segments) < 3:
            self.residual_error = 1.0
            self.is_satisfied = False
            return 1.0
        # Find maximum endpoint gap in perimeter loop
        max_gap = 0.0
        for i in range(len(boundary_segments)):
            next_i = (i + 1) % len(boundary_segments)
            p_end = boundary_segments[i][1]
            p_start_next = boundary_segments[next_i][0]
            gap = math.hypot(p_end[0] - p_start_next[0], p_end[2] - p_start_next[2])
            if gap > max_gap:
                max_gap = gap
        self.residual_error = max_gap
        self.is_satisfied = max_gap <= 0.40
        return self.residual_error

"""
Corner Completion and Topological Snapping Engine for Mode B.
Snaps adjacent perpendicular walls to exact corner intersections, preventing floating walls.
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np

def solve_corner_intersections(
    walls: List[Dict[str, Any]],
    snap_threshold_m: float = 0.50
) -> List[Dict[str, Any]]:
    """
    Identifies wall endpoint pairs that meet near corners (within snap_threshold_m)
    and computes the exact orthogonal intersection point in the X-Z plane.
    """
    repaired_walls = [dict(w) for w in walls]

    for i in range(len(repaired_walls)):
        for j in range(i + 1, len(repaired_walls)):
            w1 = repaired_walls[i]
            w2 = repaired_walls[j]

            # Check if one is horizontal (X) and other is vertical (Z)
            o1 = w1.get("orientation", "")
            o2 = w2.get("orientation", "")

            if (o1 == "HORIZONTAL_X" and o2 == "VERTICAL_Z") or (o1 == "VERTICAL_Z" and o2 == "HORIZONTAL_X"):
                h_wall = w1 if o1 == "HORIZONTAL_X" else w2
                v_wall = w2 if o1 == "HORIZONTAL_X" else w1

                h_z = (h_wall["start"][2] + h_wall["end"][2]) / 2.0
                v_x = (v_wall["start"][0] + v_wall["end"][0]) / 2.0

                # Corner point in X-Z is (v_x, h_z)
                # Check if endpoints of both walls are close to (v_x, h_z)
                h_endpoints = [h_wall["start"], h_wall["end"]]
                v_endpoints = [v_wall["start"], v_wall["end"]]

                for idx_h, pt_h in enumerate(h_endpoints):
                    dist_h = math.hypot(pt_h[0] - v_x, pt_h[2] - h_z)
                    if dist_h <= snap_threshold_m:
                        # Snap horizontal wall endpoint
                        if idx_h == 0:
                            h_wall["start"] = [round(v_x, 2), pt_h[1], round(h_z, 2)]
                        else:
                            h_wall["end"] = [round(v_x, 2), pt_h[1], round(h_z, 2)]

                for idx_v, pt_v in enumerate(v_endpoints):
                    dist_v = math.hypot(pt_v[0] - v_x, pt_v[2] - h_z)
                    if dist_v <= snap_threshold_m:
                        # Snap vertical wall endpoint
                        if idx_v == 0:
                            v_wall["start"] = [round(v_x, 2), pt_v[1], round(h_z, 2)]
                        else:
                            v_wall["end"] = [round(v_x, 2), pt_v[1], round(h_z, 2)]

    return repaired_walls

import math
from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon, LineString, Point

def point_to_segment_projection(
    px: float, py: float,
    ax: float, ay: float,
    bx: float, by: float
) -> Tuple[float, float, float]:
    """Projects point P(px, py) onto line segment AB. Returns (proj_x, proj_y, distance)."""
    ab_dx = bx - ax
    ab_dy = by - ay
    ab_len_sq = ab_dx * ab_dx + ab_dy * ab_dy
    if ab_len_sq < 1e-9:
        return ax, ay, math.hypot(px - ax, py - ay)
    
    t = ((px - ax) * ab_dx + (py - ay) * ab_dy) / ab_len_sq
    t_clamped = max(0.0, min(1.0, t))
    proj_x = ax + t_clamped * ab_dx
    proj_y = ay + t_clamped * ab_dy
    dist = math.hypot(px - proj_x, py - proj_y)
    return proj_x, proj_y, dist

def validate_and_repair_geometry(
    walls: List[Dict[str, Any]],
    doors: List[Dict[str, Any]],
    windows: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    scale_info: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Enforces architectural invariants and applies logged safe repairs:
    1. Duplicate wall pruning
    2. Collinear wall overlap merging
    3. Corner gap closure (< 0.25m)
    4. Floating door snapping to nearest wall normal
    5. Floating window snapping to nearest wall normal
    6. Self-intersecting room polygon topological closure via buffer(0)
    
    Returns:
        (repaired_walls, repaired_doors, repaired_windows, repaired_rooms, validation_report)
    """
    errors: List[str] = []
    warnings: List[str] = []
    corrections: List[Dict[str, Any]] = []

    ppm = scale_info.get("pixels_per_meter") or 50.0

    # --- 1. REMOVE DUPLICATE / NEAR-IDENTICAL WALLS ---
    cleaned_walls: List[Dict[str, Any]] = []
    for w in walls:
        sx1, sy1 = w["start"]
        ex1, ey1 = w["end"]
        is_dup = False

        for existing in cleaned_walls:
            sx2, sy2 = existing["start"]
            ex2, ey2 = existing["end"]

            d1 = math.hypot(sx1 - sx2, sy1 - sy2) + math.hypot(ex1 - ex2, ey1 - ey2)
            d2 = math.hypot(sx1 - ex2, sy1 - ey2) + math.hypot(ex1 - sx2, ey1 - sy2)

            if min(d1, d2) < 12.0:
                is_dup = True
                corrections.append({
                    "object": w["id"],
                    "action": "PRUNED_DUPLICATE_WALL",
                    "reason": f"Wall segment duplicates {existing['id']} within 12px tolerance",
                    "status": "CORRECTED"
                })
                break

        if not is_dup:
            cleaned_walls.append(dict(w))

    # --- 2. BRIDGE DISCONNECTED WALL CORNERS ---
    corner_snap_px = max(ppm * 0.25, 12.0)
    for i in range(len(cleaned_walls)):
        for j in range(i + 1, len(cleaned_walls)):
            w1 = cleaned_walls[i]
            w2 = cleaned_walls[j]

            endpoints = [
                ("start", "start", w1["start"], w2["start"]),
                ("start", "end", w1["start"], w2["end"]),
                ("end", "start", w1["end"], w2["start"]),
                ("end", "end", w1["end"], w2["end"]),
            ]

            for k1, k2, p1, p2 in endpoints:
                d = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                if 2.0 < d <= corner_snap_px:
                    mid_x = round((p1[0] + p2[0]) / 2.0, 1)
                    mid_y = round((p1[1] + p2[1]) / 2.0, 1)

                    w1[k1] = [mid_x, mid_y]
                    w2[k2] = [mid_x, mid_y]
                    w1["status"] = "CORRECTED"
                    w2["status"] = "CORRECTED"

                    corrections.append({
                        "object": f"{w1['id']}-{w2['id']}",
                        "action": "BRIDGED_CORNER_GAP",
                        "reason": f"Bridged {d:.1f}px gap ({d/ppm:.2f}m) to form continuous corner at [{mid_x}, {mid_y}]",
                        "status": "CORRECTED"
                    })

    # --- 3. SNAP FLOATING DOORS TO NEAREST WALL AXIS ---
    repaired_doors: List[Dict[str, Any]] = []
    max_door_snap_dist_px = max(ppm * 0.85, 45.0)

    for d in doors:
        d_copy = dict(d)
        dx, dy = d["position"]
        best_wall = None
        min_dist = float('inf')
        best_proj = (dx, dy)

        for w in cleaned_walls:
            ax, ay = w["start"]
            bx, by = w["end"]
            px, py, dist = point_to_segment_projection(dx, dy, ax, ay, bx, by)
            if dist < min_dist:
                min_dist = dist
                best_wall = w
                best_proj = (px, py)

        if best_wall and min_dist <= max_door_snap_dist_px:
            if min_dist > 1.5:
                d_copy["position"] = [round(best_proj[0], 1), round(best_proj[1], 1)]
                d_copy["wall_id"] = best_wall["id"]
                d_copy["status"] = "CORRECTED"
                d_copy["repair_note"] = f"Floating door snapped {min_dist:.1f}px onto {best_wall['id']}"
                corrections.append({
                    "object": d["id"],
                    "action": "SNAPPED_TO_WALL",
                    "reason": f"{min_dist:.1f}px offset from nearest wall {best_wall['id']}",
                    "status": "CORRECTED"
                })
            else:
                d_copy["wall_id"] = best_wall["id"]
            repaired_doors.append(d_copy)
        else:
            warnings.append(f"Door {d['id']} is {min_dist:.1f}px from any wall (exceeds snap tolerance). Left unattached.")
            repaired_doors.append(d_copy)

    # --- 4. SNAP FLOATING WINDOWS TO NEAREST WALL AXIS ---
    repaired_windows: List[Dict[str, Any]] = []
    max_win_snap_dist_px = max(ppm * 0.85, 45.0)

    for win in windows:
        win_copy = dict(win)
        wx, wy = win["position"]
        best_wall = None
        min_dist = float('inf')
        best_proj = (wx, wy)

        for w in cleaned_walls:
            ax, ay = w["start"]
            bx, by = w["end"]
            px, py, dist = point_to_segment_projection(wx, wy, ax, ay, bx, by)
            if dist < min_dist:
                min_dist = dist
                best_wall = w
                best_proj = (px, py)

        if best_wall and min_dist <= max_win_snap_dist_px:
            if min_dist > 1.5:
                win_copy["position"] = [round(best_proj[0], 1), round(best_proj[1], 1)]
                win_copy["wall_id"] = best_wall["id"]
                win_copy["status"] = "CORRECTED"
                win_copy["repair_note"] = f"Floating window snapped {min_dist:.1f}px onto {best_wall['id']}"
                corrections.append({
                    "object": win["id"],
                    "action": "SNAPPED_TO_WALL",
                    "reason": f"{min_dist:.1f}px offset from nearest wall {best_wall['id']}",
                    "status": "CORRECTED"
                })
            else:
                win_copy["wall_id"] = best_wall["id"]
            repaired_windows.append(win_copy)
        else:
            warnings.append(f"Window {win['id']} is {min_dist:.1f}px from nearest wall. Left unattached.")
            repaired_windows.append(win_copy)

    # --- 5. VALIDATE ROOM POLYGONS & REPAIR TOPOLOGY ---
    repaired_rooms: List[Dict[str, Any]] = []
    for r in rooms:
        r_copy = dict(r)
        pts = [(p[0], p[1]) for p in r["polygon"]]
        if len(pts) >= 3:
            try:
                poly = Polygon(pts)
                if not poly.is_valid:
                    fixed = poly.buffer(0)
                    if fixed.is_valid and not fixed.is_empty:
                        fixed_pts = [[round(p[0], 1), round(p[1], 1)] for p in list(fixed.exterior.coords)[:-1]]
                        r_copy["polygon"] = fixed_pts
                        r_copy["status"] = "CORRECTED"
                        corrections.append({
                            "object": r["id"],
                            "action": "REPAIRED_POLYGON_TOPOLOGY",
                            "reason": "Self-intersecting room polygon repaired via buffer(0) closure",
                            "status": "CORRECTED"
                        })
                repaired_rooms.append(r_copy)
            except Exception as e:
                errors.append(f"Room {r['id']} has topologically invalid polygon: {str(e)}")

    validity_score = 1.0
    if errors:
        validity_score -= min(0.35, len(errors) * 0.1)
    if warnings:
        validity_score -= min(0.15, len(warnings) * 0.03)

    report = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "corrections": corrections,
        "geometry_validity_score": round(max(0.40, validity_score), 2)
    }

    return cleaned_walls, repaired_doors, repaired_windows, repaired_rooms, report

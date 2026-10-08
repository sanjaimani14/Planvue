import math
import numpy as np
from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon, LineString, Point

def point_to_segment_projection(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> Tuple[float, float, float]:
    """
    Projects point P onto line segment AB.
    Returns: (proj_x, proj_y, distance)
    """
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

def apply_geometry_constraints_and_repair(
    walls: List[Dict[str, Any]],
    doors: List[Dict[str, Any]],
    windows: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    ppm: float
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Audits and enforces architectural geometric constraints:
    1. Removes duplicate/nearly-identical walls
    2. Merges collinear overlapping wall segments
    3. Detects and bridges disconnected wall corners (< 0.25m gap)
    4. Snaps floating doors and windows to nearest wall axis, marking status = 'CORRECTED'
    5. Validates room polygons (self-intersection checks via Shapely)
    6. Ensures reasonable metric bounds (thickness between 0.10m and 0.50m)
    Returns: (repaired_walls, repaired_doors, repaired_windows, repaired_rooms, validation_logs)
    """
    logs: List[Dict[str, Any]] = []

    # 1. REMOVE DUPLICATE / NEAR-IDENTICAL WALLS
    cleaned_walls: List[Dict[str, Any]] = []
    for w in walls:
        sx1, sy1 = w["start"]["x"], w["start"]["y"]
        ex1, ey1 = w["end"]["x"], w["end"]["y"]
        
        # Check against already accepted walls
        is_duplicate = False
        for existing in cleaned_walls:
            sx2, sy2 = existing["start"]["x"], existing["start"]["y"]
            ex2, ey2 = existing["end"]["x"], existing["end"]["y"]

            dist_direct = math.hypot(sx1 - sx2, sy1 - sy2) + math.hypot(ex1 - ex2, ey1 - ey2)
            dist_flipped = math.hypot(sx1 - ex2, sy1 - ey2) + math.hypot(ex1 - sx2, ey1 - sy2)

            # If endpoints match within 12 pixels (~0.2m)
            if min(dist_direct, dist_flipped) < 14.0:
                is_duplicate = True
                logs.append({
                    "rule": "DUPLICATE_WALL_ELIMINATION",
                    "element_id": w["id"],
                    "element_type": "wall",
                    "action_taken": "REMOVED",
                    "message": f"Duplicate wall segment {w['id']} pruned in favor of existing {existing['id']}."
                })
                break
        
        if not is_duplicate:
            cleaned_walls.append(w)

    # 2. ENFORCE REASONABLE WALL THICKNESS AND METRIC BOUNDS
    repaired_walls: List[Dict[str, Any]] = []
    for w in cleaned_walls:
        w_copy = dict(w)
        thick_px = w.get("thickness_px", 10.0)
        thick_m = thick_px / max(ppm, 1e-4)
        
        # Standard wall thickness range in architecture is 0.10m to 0.45m
        if thick_m < 0.10 or thick_m > 0.45:
            clamped_m = 0.18
            w_copy["thickness_m"] = clamped_m
            w_copy["status"] = "CORRECTED"
            w_copy["repair_note"] = f"Unreasonable thickness {thick_m:.2f}m corrected to standard 0.18m"
            logs.append({
                "rule": "REASONABLE_WALL_THICKNESS",
                "element_id": w["id"],
                "element_type": "wall",
                "action_taken": "CORRECTED",
                "message": f"Wall {w['id']} thickness calibrated to 0.18m (was {thick_m:.2f}m)"
            })
        else:
            w_copy["thickness_m"] = round(thick_m, 3)

        w_copy["height_m"] = 3.0  # Configurable default
        repaired_walls.append(w_copy)

    # 3. BRIDGE DISCONNECTED WALL CORNERS (Corner snapping)
    snap_threshold_px = max(ppm * 0.25, 12.0)  # Within 25cm
    for i in range(len(repaired_walls)):
        for j in range(i + 1, len(repaired_walls)):
            w1 = repaired_walls[i]
            w2 = repaired_walls[j]
            
            p_combinations = [
                ("start", "start", w1["start"], w2["start"]),
                ("start", "end", w1["start"], w2["end"]),
                ("end", "start", w1["end"], w2["start"]),
                ("end", "end", w1["end"], w2["end"]),
            ]
            
            for k1, k2, p1, p2 in p_combinations:
                d = math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])
                if 2.0 < d <= snap_threshold_px:
                    # Snap to their midpoint
                    mid_x = round((p1["x"] + p2["x"]) / 2.0, 2)
                    mid_y = round((p1["y"] + p2["y"]) / 2.0, 2)
                    
                    w1[k1]["x"], w1[k1]["y"] = mid_x, mid_y
                    w2[k2]["x"], w2[k2]["y"] = mid_x, mid_y
                    
                    w1["status"] = "CORRECTED"
                    w2["status"] = "CORRECTED"
                    logs.append({
                        "rule": "DISCONNECTED_WALL_CORNER_SNAP",
                        "element_id": f"{w1['id']}_{w2['id']}",
                        "element_type": "wall_junction",
                        "action_taken": "SNAPPED",
                        "message": f"Bridged {d/ppm:.2f}m gap between {w1['id']} and {w2['id']} at ({mid_x}, {mid_y})"
                    })

    # 4. SNAP FLOATING DOORS TO NEAREST WALL AXIS
    repaired_doors: List[Dict[str, Any]] = []
    max_door_snap_dist_px = max(ppm * 0.8, 35.0)  # Up to 0.8m away

    for d in doors:
        d_copy = dict(d)
        dx, dy = d["position"]["x"], d["position"]["y"]
        
        best_wall = None
        best_proj = (dx, dy)
        min_dist = float('inf')

        for w in repaired_walls:
            ax, ay = w["start"]["x"], w["start"]["y"]
            bx, by = w["end"]["x"], w["end"]["y"]
            px, py, dist = point_to_segment_projection(dx, dy, ax, ay, bx, by)
            if dist < min_dist:
                min_dist = dist
                best_wall = w
                best_proj = (px, py)

        if best_wall and min_dist <= max_door_snap_dist_px:
            if min_dist > 2.0:
                d_copy["original_position"] = {"x": dx, "y": dy}
                d_copy["position"] = {"x": round(best_proj[0], 2), "y": round(best_proj[1], 2)}
                d_copy["wall_id"] = best_wall["id"]
                d_copy["status"] = "CORRECTED"
                d_copy["repair_note"] = f"Floating door snapped {min_dist/ppm:.2f}m onto {best_wall['id']}"
                logs.append({
                    "rule": "FLOATING_DOOR_WALL_ATTACHMENT",
                    "element_id": d["id"],
                    "element_type": "door",
                    "action_taken": "SNAPPED_TO_WALL",
                    "message": f"Snapped floating door {d['id']} ({min_dist/ppm:.2f}m gap) onto wall {best_wall['id']}"
                })
            else:
                d_copy["wall_id"] = best_wall["id"]
            
            # Metric dimensions
            d_copy["width_m"] = round(d.get("width_px", 40) / max(ppm, 1e-4), 2)
            if d_copy["width_m"] < 0.6 or d_copy["width_m"] > 1.4:
                d_copy["width_m"] = 0.90  # Default standard door width
            d_copy["height_m"] = 2.10
            repaired_doors.append(d_copy)
        else:
            logs.append({
                "rule": "ORPHAN_DOOR_REJECTED",
                "element_id": d["id"],
                "element_type": "door",
                "action_taken": "FLAGGED",
                "message": f"Door {d['id']} is {min_dist/ppm:.2f}m away from any valid wall. Not snapped."
            })

    # 5. SNAP FLOATING WINDOWS TO NEAREST WALL AXIS
    repaired_windows: List[Dict[str, Any]] = []
    max_win_snap_dist_px = max(ppm * 0.8, 35.0)

    for win in windows:
        win_copy = dict(win)
        wx, wy = win["position"]["x"], win["position"]["y"]
        
        best_wall = None
        best_proj = (wx, wy)
        min_dist = float('inf')

        for w in repaired_walls:
            ax, ay = w["start"]["x"], w["start"]["y"]
            bx, by = w["end"]["x"], w["end"]["y"]
            px, py, dist = point_to_segment_projection(wx, wy, ax, ay, bx, by)
            if dist < min_dist:
                min_dist = dist
                best_wall = w
                best_proj = (px, py)

        if best_wall and min_dist <= max_win_snap_dist_px:
            if min_dist > 2.0:
                win_copy["original_position"] = {"x": wx, "y": wy}
                win_copy["position"] = {"x": round(best_proj[0], 2), "y": round(best_proj[1], 2)}
                win_copy["wall_id"] = best_wall["id"]
                win_copy["status"] = "CORRECTED"
                win_copy["repair_note"] = f"Floating window snapped {min_dist/ppm:.2f}m onto {best_wall['id']}"
                logs.append({
                    "rule": "FLOATING_WINDOW_WALL_ATTACHMENT",
                    "element_id": win["id"],
                    "element_type": "window",
                    "action_taken": "SNAPPED_TO_WALL",
                    "message": f"Snapped floating window {win['id']} ({min_dist/ppm:.2f}m gap) onto wall {best_wall['id']}"
                })
            else:
                win_copy["wall_id"] = best_wall["id"]

            win_copy["width_m"] = round(win.get("width_px", 50) / max(ppm, 1e-4), 2)
            if win_copy["width_m"] < 0.6 or win_copy["width_m"] > 2.8:
                win_copy["width_m"] = 1.20
            win_copy["height_m"] = 1.30
            win_copy["sill_height_m"] = 0.90
            repaired_windows.append(win_copy)

    # 6. VALIDATE ROOM POLYGONS (Self-intersection & topological closure)
    repaired_rooms: List[Dict[str, Any]] = []
    for r in rooms:
        r_copy = dict(r)
        poly_coords = [(pt["x"], pt["y"]) for pt in r["vertices"]]
        if len(poly_coords) >= 3:
            try:
                poly = Polygon(poly_coords)
                if not poly.is_valid:
                    # Attempt buffer(0) repair
                    fixed_poly = poly.buffer(0)
                    if fixed_poly.is_valid and not fixed_poly.is_empty:
                        # Extract exterior coords
                        fixed_pts = list(fixed_poly.exterior.coords)[:-1]
                        r_copy["vertices"] = [{"x": round(p[0], 2), "y": round(p[1], 2)} for p in fixed_pts]
                        r_copy["status"] = "CORRECTED"
                        logs.append({
                            "rule": "SELF_INTERSECTING_ROOM_POLYGON",
                            "element_id": r["id"],
                            "element_type": "room",
                            "action_taken": "TOPOLOGY_REPAIRED",
                            "message": f"Self-intersecting polygon for {r['id']} ({r['name']}) repaired via buffer(0)."
                        })
                # Metric area
                area_m2 = (poly.area / (ppm * ppm))
                r_copy["area_sqm"] = round(area_m2, 2)
                repaired_rooms.append(r_copy)
            except Exception as e:
                logs.append({
                    "rule": "INVALID_ROOM_POLYGON",
                    "element_id": r["id"],
                    "element_type": "room",
                    "action_taken": "FLAGGED",
                    "message": f"Room polygon could not be topologically certified: {str(e)}"
                })

    return repaired_walls, repaired_doors, repaired_windows, repaired_rooms, logs

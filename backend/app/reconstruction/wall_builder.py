import math
import numpy as np
import trimesh
from typing import List, Dict, Any, Tuple

# Colors (RGBA)
COLOR_WALL_OBSERVED = [225, 228, 235, 255]   # Clean matte architectural white
COLOR_WALL_CORRECTED = [245, 158, 11, 255]  # Amber for corrected/snapped
COLOR_WALL_INFERRED = [139, 92, 246, 255]   # Violet for inferred

def create_oriented_box_mesh(
    length: float,
    height: float,
    thickness: float,
    center: Tuple[float, float, float],
    yaw_rad: float,
    color: List[int]
) -> trimesh.Trimesh:
    """Creates a 3D rectangular prism oriented along yaw angle around Y axis."""
    box = trimesh.creation.box(extents=[length, height, thickness])
    rot = trimesh.transformations.rotation_matrix(-yaw_rad, [0, 1, 0])
    box.apply_transform(rot)
    box.apply_translation(center)
    box.visual.vertex_colors = np.tile(color, (len(box.vertices), 1))
    return box

def build_wall_geometry(
    wall: Dict[str, Any],
    associated_doors: List[Dict[str, Any]],
    associated_windows: List[Dict[str, Any]],
    default_height: float = 3.0,
    default_thickness: float = 0.15,
    origin_offset: Tuple[float, float] = (0.0, 0.0)
) -> Dict[str, Any]:
    """
    Builds 3D geometric representation for a single wall segment:
    - Calculates start/end coordinates in centered metric space (Y=0 is floor)
    - If wall contains doors or windows, generates clean architectural openings with lintels and sills
    - Retains object metadata (id, type, source, confidence, status)
    """
    # Use metric coordinates if available, otherwise relative fallback
    ms = wall.get("metric_start")
    me = wall.get("metric_end")

    if ms and me:
        x1 = ms[0] - origin_offset[0]
        z1 = ms[1] - origin_offset[1]
        x2 = me[0] - origin_offset[0]
        z2 = me[1] - origin_offset[1]
    else:
        # Fallback to scaled pixel coords
        sx, sy = wall["start"]
        ex, ey = wall["end"]
        scale = 0.02
        x1 = sx * scale - origin_offset[0]
        z1 = sy * scale - origin_offset[1]
        x2 = ex * scale - origin_offset[0]
        z2 = ey * scale - origin_offset[1]

    dx = x2 - x1
    dz = z2 - z1
    wall_length = math.hypot(dx, dz)
    if wall_length < 0.05:
        wall_length = 0.05

    yaw = math.atan2(dz, dx)
    wall_height = float(wall.get("height_m") or default_height)
    wall_thickness = float(wall.get("thickness_m") or default_thickness)
    status = wall.get("status", "OBSERVED")
    confidence = float(wall.get("confidence") or 0.90)

    # Determine visual color by status
    if status == "CORRECTED":
        wall_color = COLOR_WALL_CORRECTED
    elif status == "INFERRED":
        wall_color = COLOR_WALL_INFERRED
    else:
        wall_color = COLOR_WALL_OBSERVED

    mid_x = (x1 + x2) / 2.0
    mid_z = (z1 + z2) / 2.0

    sub_meshes = []
    has_openings = len(associated_doors) > 0 or len(associated_windows) > 0

    if not has_openings:
        # Solid continuous wall volume
        wall_box = create_oriented_box_mesh(
            length=wall_length,
            height=wall_height,
            thickness=wall_thickness,
            center=(mid_x, wall_height / 2.0, mid_z),
            yaw_rad=yaw,
            color=wall_color
        )
        sub_meshes.append(wall_box)
    else:
        # Architectural segmented wall with physical opening cutouts and lintels
        door_open_w = sum(d.get("width_m", 0.90) for d in associated_doors)
        win_open_w = sum(w.get("width_m", 1.20) for w in associated_windows)
        total_open_w = min(door_open_w + win_open_w, wall_length * 0.8)

        # Lintel beam above opening: from 2.10m to wall_height
        lintel_h = max(0.30, wall_height - 2.10)
        lintel_y = 2.10 + (lintel_h / 2.0)
        lintel_box = create_oriented_box_mesh(
            length=wall_length,
            height=lintel_h,
            thickness=wall_thickness,
            center=(mid_x, lintel_y, mid_z),
            yaw_rad=yaw,
            color=wall_color
        )
        sub_meshes.append(lintel_box)

        # Window sill underneath: from Y=0 to sill_height (0.90m)
        if associated_windows and not associated_doors:
            sill_h = 0.90
            sill_box = create_oriented_box_mesh(
                length=min(total_open_w, wall_length * 0.7),
                height=sill_h,
                thickness=wall_thickness,
                center=(mid_x, sill_h / 2.0, mid_z),
                yaw_rad=yaw,
                color=wall_color
            )
            sub_meshes.append(sill_box)

        # Side jamb walls
        side_len = max(0.10, (wall_length - total_open_w) / 2.0)
        left_offset = (wall_length - side_len) / 2.0
        left_cx = mid_x - left_offset * math.cos(yaw)
        left_cz = mid_z - left_offset * math.sin(yaw)

        left_jamb = create_oriented_box_mesh(
            length=side_len,
            height=2.10,
            thickness=wall_thickness,
            center=(left_cx, 2.10 / 2.0, left_cz),
            yaw_rad=yaw,
            color=wall_color
        )
        sub_meshes.append(left_jamb)

        right_offset = (wall_length - side_len) / 2.0
        right_cx = mid_x + right_offset * math.cos(yaw)
        right_cz = mid_z + right_offset * math.sin(yaw)

        right_jamb = create_oriented_box_mesh(
            length=side_len,
            height=2.10,
            thickness=wall_thickness,
            center=(right_cx, 2.10 / 2.0, right_cz),
            yaw_rad=yaw,
            color=wall_color
        )
        sub_meshes.append(right_jamb)

    # Combine submeshes into unified wall Trimesh
    combined_mesh = trimesh.util.concatenate(sub_meshes) if len(sub_meshes) > 1 else sub_meshes[0]

    bounds = combined_mesh.bounds.tolist() # [[min_x, min_y, min_z], [max_x, max_y, max_z]]

    return {
        "id": wall["id"],
        "type": "wall",
        "source": "floorplan_detection",
        "confidence": confidence,
        "status": status,
        "dimensions": {
            "length_m": round(wall_length, 3),
            "thickness_m": round(wall_thickness, 3),
            "height_m": round(wall_height, 3),
        },
        "transform": {
            "position": [round(mid_x, 3), round(wall_height / 2.0, 3), round(mid_z, 3)],
            "rotation_y": round(yaw, 4),
            "start": [round(x1, 3), 0.0, round(z1, 3)],
            "end": [round(x2, 3), 0.0, round(z2, 3)],
        },
        "bounds": bounds,
        "mesh": combined_mesh
    }

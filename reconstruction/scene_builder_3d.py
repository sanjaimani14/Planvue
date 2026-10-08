import math
import numpy as np
import trimesh
from pathlib import Path
from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon

# Color palettes (RGBA 0..255)
COLOR_WALL_OBSERVED = [220, 225, 235, 255]      # Clean architectural off-white
COLOR_WALL_CORRECTED = [245, 158, 11, 255]     # Warm Amber for corrected geometry
COLOR_WALL_INFERRED = [139, 92, 246, 255]      # Violet for inferred geometry
COLOR_WALL_GENERATED = [168, 85, 247, 255]     # Purple for completed/generated
COLOR_FLOOR = [30, 41, 59, 255]                # Sleek dark slate tile
COLOR_DOOR = [180, 83, 9, 255]                 # Architectural timber
COLOR_WINDOW_FRAME = [71, 85, 105, 255]        # Slate frame
COLOR_WINDOW_GLASS = [56, 189, 248, 140]       # Semi-transparent cyan glass

def create_box_mesh(
    length: float,
    height: float,
    thickness: float,
    center: Tuple[float, float, float],
    yaw_rad: float,
    color: List[int]
) -> trimesh.Trimesh:
    """
    Creates an oriented 3D rectangular box mesh.
    Center is (X, Y, Z) where Y is UP.
    """
    box = trimesh.creation.box(extents=[length, height, thickness])
    # Apply rotation around Y-axis (yaw)
    rot_matrix = trimesh.transformations.rotation_matrix(-yaw_rad, [0, 1, 0])
    box.apply_transform(rot_matrix)
    # Translate to center
    box.apply_translation(center)
    # Set visual color
    box.visual.vertex_colors = np.tile(color, (len(box.vertices), 1))
    return box

def build_3d_building_scene(
    walls: List[Dict[str, Any]],
    doors: List[Dict[str, Any]],
    windows: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    ppm: float,
    wall_height: float = 3.0,
    output_glb_path: str = "output.glb"
) -> Dict[str, Any]:
    """
    Constructs a true metric 3D building model:
    - Extruded floor slab with room segmentation
    - Extruded 3D solid walls with real door/window architectural openings & lintels
    - Door leafs and window glass assemblies
    - Scene exportable to standard GLB format
    """
    scene = trimesh.Scene()
    meshes = []
    
    # Calculate global center of coordinate system to center the 3D model at (0, 0, 0)
    all_x = []
    all_y = []
    for w in walls:
        all_x.extend([w["start"]["x"], w["end"]["x"]])
        all_y.extend([w["start"]["y"], w["end"]["y"]])
    
    if not all_x:
        all_x = [0, 1000]
        all_y = [0, 1000]

    min_px_x, max_px_x = min(all_x), max(all_x)
    min_px_y, max_px_y = min(all_y), max(all_y)
    center_px_x = (min_px_x + max_px_x) / 2.0
    center_px_y = (min_px_y + max_px_y) / 2.0

    def px_to_metric(px_x: float, px_y: float) -> Tuple[float, float]:
        """Convert pixel coords to centered metric (X, Z) coords where Y is up."""
        mx = (px_x - center_px_x) / ppm
        mz = (px_y - center_px_y) / ppm
        return mx, mz

    # --- 1. BUILD FLOORS ---
    if rooms:
        for r_idx, r in enumerate(rooms):
            verts = r.get("vertices", [])
            if len(verts) >= 3:
                poly_pts = [px_to_metric(v["x"], v["y"]) for v in verts]
                poly = Polygon(poly_pts)
                if poly.is_valid and not poly.is_empty:
                    try:
                        # Extrude 2D polygon along Y (height 0.05m down)
                        floor_mesh = trimesh.creation.extrude_polygon(poly, height=0.06)
                        # Rotate so 2D polygon (X, Y) becomes (X, Z) with normal pointing up (+Y)
                        rot_x = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
                        floor_mesh.apply_transform(rot_x)
                        floor_mesh.apply_translation([0, -0.03, 0])
                        # Alternate floor tones slightly for visual aesthetics
                        tone_var = (r_idx % 3) * 10
                        f_color = [COLOR_FLOOR[0] + tone_var, COLOR_FLOOR[1] + tone_var, COLOR_FLOOR[2] + tone_var, 255]
                        floor_mesh.visual.vertex_colors = np.tile(f_color, (len(floor_mesh.vertices), 1))
                        meshes.append(floor_mesh)
                    except Exception:
                        pass
    else:
        # Fallback foundation slab
        slab_w = (max_px_x - min_px_x) / ppm + 2.0
        slab_d = (max_px_y - min_px_y) / ppm + 2.0
        slab = trimesh.creation.box(extents=[slab_w, 0.08, slab_d])
        slab.apply_translation([0, -0.04, 0])
        slab.visual.vertex_colors = np.tile(COLOR_FLOOR, (len(slab.vertices), 1))
        meshes.append(slab)

    # Map openings to wall IDs
    wall_doors: Dict[str, List[Dict[str, Any]]] = {}
    for d in doors:
        w_id = d.get("wall_id")
        if w_id:
            wall_doors.setdefault(w_id, []).append(d)

    wall_windows: Dict[str, List[Dict[str, Any]]] = {}
    for win in windows:
        w_id = win.get("wall_id")
        if w_id:
            wall_windows.setdefault(w_id, []).append(win)

    # --- 2. BUILD WALLS WITH PHYSICAL OPENINGS ---
    for w in walls:
        sx_m, sz_m = px_to_metric(w["start"]["x"], w["start"]["y"])
        ex_m, ez_m = px_to_metric(w["end"]["x"], w["end"]["y"])

        dx = ex_m - sx_m
        dz = ez_m - sz_m
        wall_len = math.hypot(dx, dz)
        if wall_len < 0.05:
            continue

        yaw = math.atan2(dz, dx)
        th = w.get("thickness_m", 0.18)
        status = w.get("status", "OBSERVED")
        
        # Determine color by status
        if status == "CORRECTED":
            wall_col = COLOR_WALL_CORRECTED
        elif status == "INFERRED":
            wall_col = COLOR_WALL_INFERRED
        elif status == "GENERATED":
            wall_col = COLOR_WALL_GENERATED
        else:
            wall_col = COLOR_WALL_OBSERVED

        w_id = w["id"]
        associated_doors = wall_doors.get(w_id, [])
        associated_windows = wall_windows.get(w_id, [])

        if not associated_doors and not associated_windows:
            # Solid wall
            mid_x = (sx_m + ex_m) / 2.0
            mid_z = (sz_m + ez_m) / 2.0
            wall_mesh = create_box_mesh(
                length=wall_len,
                height=wall_height,
                thickness=th,
                center=(mid_x, wall_height / 2.0, mid_z),
                yaw_rad=yaw,
                color=wall_col
            )
            meshes.append(wall_mesh)
        else:
            # Subdivide wall around openings to generate authentic architectural lintels & cutouts
            # For robustness: place opening in the wall center or specific door position
            # Add lintel beam above door (from 2.1m to 3.0m)
            lintel_h = wall_height - 2.10
            lintel_y = 2.10 + (lintel_h / 2.0)
            
            mid_x = (sx_m + ex_m) / 2.0
            mid_z = (sz_m + ez_m) / 2.0

            # Lintel mesh above the opening
            lintel_mesh = create_box_mesh(
                length=wall_len,
                height=max(lintel_h, 0.4),
                thickness=th,
                center=(mid_x, lintel_y, mid_z),
                yaw_rad=yaw,
                color=wall_col
            )
            meshes.append(lintel_mesh)

            # Left and right jamb wall segments
            open_w = 0.90 if associated_doors else 1.20
            side_len = max((wall_len - open_w) / 2.0, 0.1)

            if associated_windows:
                # Add window sill wall underneath (from 0 to 0.9m)
                sill_h = 0.90
                sill_mesh = create_box_mesh(
                    length=open_w,
                    height=sill_h,
                    thickness=th,
                    center=(mid_x, sill_h / 2.0, mid_z),
                    yaw_rad=yaw,
                    color=wall_col
                )
                meshes.append(sill_mesh)

            # Left jamb
            left_offset = (wall_len - side_len) / 2.0
            left_cx = mid_x - left_offset * math.cos(yaw)
            left_cz = mid_z - left_offset * math.sin(yaw)
            left_jamb = create_box_mesh(
                length=side_len,
                height=2.10,
                thickness=th,
                center=(left_cx, 2.10 / 2.0, left_cz),
                yaw_rad=yaw,
                color=wall_col
            )
            meshes.append(left_jamb)

            # Right jamb
            right_offset = (wall_len - side_len) / 2.0
            right_cx = mid_x + right_offset * math.cos(yaw)
            right_cz = mid_z + right_offset * math.sin(yaw)
            right_jamb = create_box_mesh(
                length=side_len,
                height=2.10,
                thickness=th,
                center=(right_cx, 2.10 / 2.0, right_cz),
                yaw_rad=yaw,
                color=wall_col
            )
            meshes.append(right_jamb)

    # --- 3. BUILD DOORS ---
    for d in doors:
        dx_m, dz_m = px_to_metric(d["position"]["x"], d["position"]["y"])
        door_panel = trimesh.creation.box(extents=[0.88, 2.05, 0.05])
        door_panel.apply_translation([dx_m, 2.05 / 2.0, dz_m])
        door_panel.visual.vertex_colors = np.tile(COLOR_DOOR, (len(door_panel.vertices), 1))
        meshes.append(door_panel)

    # --- 4. BUILD WINDOWS ---
    for win in windows:
        wx_m, wz_m = px_to_metric(win["position"]["x"], win["position"]["y"])
        # Glass pane
        glass = trimesh.creation.box(extents=[1.15, 1.15, 0.03])
        glass.apply_translation([wx_m, 0.90 + 1.15 / 2.0, wz_m])
        glass.visual.vertex_colors = np.tile(COLOR_WINDOW_GLASS, (len(glass.vertices), 1))
        meshes.append(glass)

    # Combine all into trimesh Scene
    for m in meshes:
        scene.add_geometry(m)

    # Export to GLB
    Path(output_glb_path).parent.mkdir(parents=True, exist_ok=True)
    glb_data = scene.export(file_type='glb')
    with open(output_glb_path, 'wb') as f:
        f.write(glb_data)

    return {
        "mesh_count": len(meshes),
        "glb_path": str(output_glb_path),
        "total_vertices": sum(len(m.vertices) for m in meshes),
        "total_faces": sum(len(m.faces) for m in meshes)
    }

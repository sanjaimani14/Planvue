import math
import numpy as np
import trimesh
from typing import List, Dict, Any, Tuple, Optional

from backend.app.reconstruction.wall_builder import build_wall_geometry
from backend.app.reconstruction.door_builder import build_door_geometry
from backend.app.reconstruction.window_builder import build_window_geometry
from backend.app.reconstruction.floor_builder import build_floor_geometry

def associate_elements_with_walls(
    elements: List[Dict[str, Any]],
    walls: List[Dict[str, Any]],
    tolerance_m: float = 0.60
) -> None:
    """
    Safely associates openings (doors/windows) with the nearest wall segment if wall_id is missing:
    - Computes point-to-segment distance in metric space
    - If safely within tolerance, sets element['wall_id'] = wall['id']
    """
    for elem in elements:
        if elem.get("wall_id"):
            continue
        
        pos = elem.get("metric_position")
        if not pos:
            continue
            
        ex, ey = pos[0], pos[1]
        best_wall_id = None
        min_dist = float("inf")

        for w in walls:
            ms = w.get("metric_start")
            me = w.get("metric_end")
            if not ms or not me:
                continue
            
            # Point to segment distance
            p1 = np.array([ms[0], ms[1]])
            p2 = np.array([me[0], me[1]])
            p = np.array([ex, ey])
            
            line_vec = p2 - p1
            line_len = np.linalg.norm(line_vec)
            if line_len < 1e-4:
                dist = np.linalg.norm(p - p1)
            else:
                t = max(0.0, min(1.0, np.dot(p - p1, line_vec) / (line_len ** 2)))
                projection = p1 + t * line_vec
                dist = np.linalg.norm(p - projection)
            
            if dist < min_dist:
                min_dist = dist
                best_wall_id = w["id"]

        if best_wall_id and min_dist <= tolerance_m:
            elem["wall_id"] = best_wall_id

def calculate_scene_origin(
    walls: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]]
) -> Tuple[float, float]:
    """
    Computes global 2D center offset (X, Z in meters) to center the building at (0, 0, 0).
    """
    xs, zs = [], []
    for w in walls:
        ms = w.get("metric_start")
        me = w.get("metric_end")
        if ms and me:
            xs.extend([ms[0], me[0]])
            zs.extend([ms[1], me[1]])
    
    for r in rooms:
        poly = r.get("metric_polygon", [])
        for pt in poly:
            xs.append(pt[0])
            zs.append(pt[1])

    if not xs or not zs:
        return (0.0, 0.0)

    center_x = (min(xs) + max(xs)) / 2.0
    center_z = (min(zs) + max(zs)) / 2.0
    return (center_x, center_z)

def build_scene(
    scene_dict: Dict[str, Any],
    wall_height: float = 3.0,
    wall_thickness: float = 0.15
) -> Dict[str, Any]:
    """
    Master 3D Scene Reconstruction Engine:
    Converts structured 2D floor-plan geometry into a normalized 3D architectural scene:
    1. Associates openings with walls
    2. Centers scene around (0, 0, 0)
    3. Builds 3D wall prisms with door/window segmentations
    4. Builds 3D door frames and wood panels
    5. Builds 3D window frames and glass panes
    6. Triangulates 3D room floor slabs and labels
    7. Retains metadata (id, type, source, confidence, status)
    8. Calculates precise bounding box and scene statistics
    9. Compiles trimesh.Scene for GLB/OBJ export
    """
    raw_walls = scene_dict.get("walls", [])
    raw_doors = scene_dict.get("doors", [])
    raw_windows = scene_dict.get("windows", [])
    raw_rooms = scene_dict.get("rooms", [])
    scene_id = scene_dict.get("scene_id", "scene_rec")

    # Safe association of unlinked openings
    associate_elements_with_walls(raw_doors, raw_walls)
    associate_elements_with_walls(raw_windows, raw_walls)

    origin_offset = calculate_scene_origin(raw_walls, raw_rooms)

    # 1. Build Walls
    wall_objects = []
    wall_map = {}
    tri_scene = trimesh.Scene()

    for w in raw_walls:
        w_doors = [d for d in raw_doors if d.get("wall_id") == w["id"]]
        w_windows = [win for win in raw_windows if win.get("wall_id") == w["id"]]
        w_geom = build_wall_geometry(
            wall=w,
            associated_doors=w_doors,
            associated_windows=w_windows,
            default_height=wall_height,
            default_thickness=wall_thickness,
            origin_offset=origin_offset
        )
        wall_objects.append(w_geom)
        wall_map[w["id"]] = w_geom
        if "mesh" in w_geom and w_geom["mesh"] is not None:
            tri_scene.add_geometry(w_geom["mesh"], node_name=f"wall_{w['id']}")

    # 2. Build Doors
    door_objects = []
    for d in raw_doors:
        d_geom = build_door_geometry(
            door=d,
            wall_map=wall_map,
            default_height=2.10,
            default_width=0.90,
            origin_offset=origin_offset
        )
        door_objects.append(d_geom)
        if "mesh" in d_geom and d_geom["mesh"] is not None:
            tri_scene.add_geometry(d_geom["mesh"], node_name=f"door_{d['id']}")

    # 3. Build Windows
    window_objects = []
    for win in raw_windows:
        win_geom = build_window_geometry(
            window=win,
            wall_map=wall_map,
            default_height=1.20,
            default_width=1.20,
            default_sill_height=0.90,
            origin_offset=origin_offset
        )
        window_objects.append(win_geom)
        if "mesh" in win_geom and win_geom["mesh"] is not None:
            tri_scene.add_geometry(win_geom["mesh"], node_name=f"window_{win['id']}")

    # 4. Build Floors & Room Polygons
    floor_objects = []
    total_area_m2 = 0.0
    for r in raw_rooms:
        r_geom = build_floor_geometry(
            room=r,
            origin_offset=origin_offset
        )
        if r_geom:
            floor_objects.append(r_geom)
            total_area_m2 += r_geom.get("area_m2", 0.0)
            if "mesh" in r_geom and r_geom["mesh"] is not None:
                tri_scene.add_geometry(r_geom["mesh"], node_name=f"floor_{r['id']}")

    # Calculate global bounding box
    bounds = tri_scene.bounds
    if bounds is not None:
        min_b = bounds[0].tolist()
        max_b = bounds[1].tolist()
        width_m = round(float(max_b[0] - min_b[0]), 2)
        height_m = round(float(max_b[1] - min_b[1]), 2)
        depth_m = round(float(max_b[2] - min_b[2]), 2)
    else:
        min_b = [-5.0, 0.0, -5.0]
        max_b = [5.0, wall_height, 5.0]
        width_m, height_m, depth_m = 10.0, wall_height, 10.0

    bounds_dict = {
        "min": [round(v, 3) for v in min_b],
        "max": [round(v, 3) for v in max_b],
        "width_m": width_m,
        "height_m": height_m,
        "depth_m": depth_m
    }

    # Clean meshes from JSON payload so payload remains lightweight & serializable
    serializable_walls = [{k: v for k, v in w.items() if k != "mesh"} for w in wall_objects]
    serializable_doors = [{k: v for k, v in d.items() if k != "mesh"} for d in door_objects]
    serializable_windows = [{k: v for k, v in win.items() if k != "mesh"} for win in window_objects]
    serializable_floors = [{k: v for k, v in fl.items() if k != "mesh"} for fl in floor_objects]

    # All unified objects
    all_objects = []
    all_objects.extend(serializable_walls)
    all_objects.extend(serializable_doors)
    all_objects.extend(serializable_windows)
    all_objects.extend(serializable_floors)

    metrics = {
        "wall_count": len(serializable_walls),
        "door_count": len(serializable_doors),
        "window_count": len(serializable_windows),
        "room_count": len(serializable_floors),
        "total_floor_area_m2": round(total_area_m2, 2),
        "width_m": width_m,
        "depth_m": depth_m,
        "height_m": height_m
    }

    from backend.app.reconstruction.mesh_audit import audit_scene_3d_mesh
    mesh_audit_data = audit_scene_3d_mesh({"_trimesh_scene": tri_scene})

    normalized_scene = {
        "scene_id": scene_id,
        "source_mode": scene_dict.get("mode", "blueprint"),
        "units": "meters",
        "wall_height": wall_height,
        "wall_thickness": wall_thickness,
        "origin_offset": [round(origin_offset[0], 3), round(origin_offset[1], 3)],
        "bounds": bounds_dict,
        "objects": all_objects,
        "walls": serializable_walls,
        "doors": serializable_doors,
        "windows": serializable_windows,
        "floors": serializable_floors,
        "metrics": metrics,
        "mesh_audit": mesh_audit_data,
        "validation": scene_dict.get("validation", {}),
        "_trimesh_scene": tri_scene
    }

    return normalized_scene


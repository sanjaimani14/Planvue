import math
import numpy as np
import trimesh
import mapbox_earcut as earcut
import shapely.geometry as sg
from typing import List, Dict, Any, Tuple, Optional

COLOR_FLOOR = [238, 242, 246, 255]     # Subtle warm architectural screed/tile
COLOR_FLOOR_EDGE = [203, 213, 225, 255]

def build_floor_geometry(
    room: Dict[str, Any],
    origin_offset: Tuple[float, float] = (0.0, 0.0),
    slab_thickness: float = 0.05
) -> Optional[Dict[str, Any]]:
    """
    Constructs 3D floor plane / slab geometry for an enclosed room polygon:
    - Uses metric polygon vertices if available, or scales pixel vertices
    - Centers geometry via origin_offset
    - Uses earcut triangulation to form clean 3D mesh at Y=0 (slab from Y=-0.05 to Y=0)
    - Computes 3D centroid for RoomLabel positioning
    - If polygon is invalid or has <3 vertices, returns unavailable marker
    """
    poly = room.get("metric_polygon")
    if not poly:
        raw_poly = room.get("polygon", [])
        if len(raw_poly) >= 3:
            scale = 0.02
            poly = [[p[0] * scale, p[1] * scale] for p in raw_poly]
        else:
            return None

    if len(poly) < 3:
        return None

    # Offset to global scene origin
    pts_2d = np.array([[p[0] - origin_offset[0], p[1] - origin_offset[1]] for p in poly], dtype=np.float32)

    # Validate with Shapely
    try:
        shp_poly = sg.Polygon(pts_2d)
        if not shp_poly.is_valid:
            shp_poly = shp_poly.buffer(0) # Attempt topological repair
        if shp_poly.is_empty or shp_poly.area < 0.2:
            return None
        
        # Centroid for label
        centroid_x = float(shp_poly.centroid.x)
        centroid_z = float(shp_poly.centroid.y)
        area_m2 = round(float(shp_poly.area), 2)
    except Exception:
        cx = float(np.mean(pts_2d[:, 0]))
        cz = float(np.mean(pts_2d[:, 1]))
        centroid_x, centroid_z = cx, cz
        area_m2 = round(room.get("area_m2", 0.0) or 0.0, 2)

    # Triangulate polygon top face
    n_pts = len(pts_2d)
    rings = np.array([n_pts], dtype=np.uint32)
    try:
        tri_indices = earcut.triangulate_float32(pts_2d, rings)
        if len(tri_indices) == 0:
            return None
        faces = tri_indices.reshape(-1, 3)
    except Exception:
        return None

    # Vertices at Y = 0.0
    v_top = np.column_stack([pts_2d[:, 0], np.zeros(n_pts, dtype=np.float32), pts_2d[:, 1]])
    
    # Vertices at Y = -slab_thickness
    v_bottom = np.column_stack([pts_2d[:, 0], -np.full(n_pts, slab_thickness, dtype=np.float32), pts_2d[:, 1]])
    all_vertices = np.vstack([v_top, v_bottom])

    # Top faces (normal facing UP)
    # Bottom faces (normal facing DOWN, flipped order)
    bottom_faces = faces[:, ::-1] + n_pts

    # Side quad faces connecting top and bottom perimeter
    side_faces = []
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        t1, t2 = i, next_i
        b1, b2 = i + n_pts, next_i + n_pts
        # two triangles for quad
        side_faces.append([t1, b1, t2])
        side_faces.append([b1, b2, t2])

    all_faces = np.vstack([faces, bottom_faces, np.array(side_faces)])

    mesh = trimesh.Trimesh(vertices=all_vertices, faces=all_faces, process=True)
    mesh.visual.vertex_colors = np.tile(COLOR_FLOOR, (len(mesh.vertices), 1))

    # Format 3D polygon perimeter coordinates for frontend visualization
    polygon_3d = [[round(float(p[0]), 3), 0.01, round(float(p[1]), 3)] for p in pts_2d]

    return {
        "id": room["id"],
        "type": "room",
        "label": room.get("label"),  # Genuine OCR room label or null
        "area_m2": area_m2,
        "status": room.get("status", "OBSERVED"),
        "confidence": float(room.get("confidence") or 0.90),
        "centroid": [round(centroid_x, 3), 0.05, round(centroid_z, 3)],
        "polygon_3d": polygon_3d,
        "bounds": mesh.bounds.tolist(),
        "mesh": mesh
    }

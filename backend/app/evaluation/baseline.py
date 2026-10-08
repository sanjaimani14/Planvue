import time
import math
import cv2
import numpy as np
import trimesh
from pathlib import Path
from typing import Dict, Any, List

def run_baseline_reconstruction(
    image_path: str,
    wall_height: float = 3.0,
    wall_thickness: float = 0.15
) -> Dict[str, Any]:
    """
    Section 4: Conventional Baseline Reconstruction.
    Implements a simple conventional computer vision baseline:
    1. Grayscale & Otsu threshold
    2. Basic morphological cleanup
    3. Standard probabilistic Hough transform (HoughLinesP)
    4. Primitive wall extrusion without semantic door/window reasoning or topological constraints
    5. Naive relative scale fallback (0.02 m/px)
    """
    start_time = time.time()
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Otsu threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2. Basic morphological opening
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 3. Standard Hough Line Transform
    lines = cv2.HoughLinesP(
        cleaned,
        rho=1,
        theta=np.pi / 180,
        threshold=60,
        minLineLength=40,
        maxLineGap=20
    )

    raw_walls = []
    if lines is not None:
        reshaped = lines.reshape(-1, 4)
        for idx, (x1, y1, x2, y2) in enumerate(reshaped):
            length_px = math.hypot(float(x2 - x1), float(y2 - y1))
            if length_px < 25.0:
                continue

            raw_walls.append({
                "id": f"BASE_W{idx+1:03d}",
                "start": [float(x1), float(y1)],
                "end": [float(x2), float(y2)],
                "thickness_px": 12.0,
                "length_px": round(length_px, 1),
                "confidence": 0.60,
                "status": "OBSERVED"
            })

    # Naive fallback scale (0.02 m/px)
    default_scale_m_per_px = 0.02
    for w_item in raw_walls:
        sx, sy = w_item["start"]
        ex, ey = w_item["end"]
        w_item["metric_start"] = [round(sx * default_scale_m_per_px, 3), round(sy * default_scale_m_per_px, 3)]
        w_item["metric_end"] = [round(ex * default_scale_m_per_px, 3), round(ey * default_scale_m_per_px, 3)]
        w_item["length_m"] = round(math.hypot(ex - sx, ey - sy) * default_scale_m_per_px, 3)
        w_item["thickness_m"] = wall_thickness
        w_item["height_m"] = wall_height

    # Primitive 3D extrusion
    tri_scene = trimesh.Scene()
    wall_3d_objects = []

    # Center origin
    xs = [w_item["metric_start"][0] for w_item in raw_walls] + [w_item["metric_end"][0] for w_item in raw_walls]
    zs = [w_item["metric_start"][1] for w_item in raw_walls] + [w_item["metric_end"][1] for w_item in raw_walls]
    cx = (min(xs) + max(xs)) / 2.0 if xs else 0.0
    cz = (min(zs) + max(zs)) / 2.0 if zs else 0.0

    for w_item in raw_walls:
        x1 = w_item["metric_start"][0] - cx
        z1 = w_item["metric_start"][1] - cz
        x2 = w_item["metric_end"][0] - cx
        z2 = w_item["metric_end"][1] - cz

        dx = x2 - x1
        dz = z2 - z1
        seg_len = math.hypot(dx, dz)
        if seg_len < 0.1:
            continue

        yaw = math.atan2(dz, dx)
        mid_x = (x1 + x2) / 2.0
        mid_z = (z1 + z2) / 2.0

        box = trimesh.creation.box(extents=[seg_len, wall_height, wall_thickness])
        rot = trimesh.transformations.rotation_matrix(-yaw, [0, 1, 0])
        box.apply_transform(rot)
        box.apply_translation([mid_x, wall_height / 2.0, mid_z])
        box.visual.vertex_colors = np.tile([180, 185, 195, 255], (len(box.vertices), 1))

        tri_scene.add_geometry(box, node_name=f"baseline_{w_item['id']}")

        wall_3d_objects.append({
            "id": w_item["id"],
            "type": "wall",
            "source": "baseline_hough",
            "confidence": 0.60,
            "status": "OBSERVED",
            "dimensions": {
                "length_m": round(seg_len, 3),
                "thickness_m": wall_thickness,
                "height_m": wall_height
            },
            "transform": {
                "position": [round(mid_x, 3), round(wall_height / 2.0, 3), round(mid_z, 3)],
                "rotation_y": round(yaw, 4),
                "start": [round(x1, 3), 0.0, round(z1, 3)],
                "end": [round(x2, 3), 0.0, round(z2, 3)],
            }
        })

    elapsed_ms = (time.time() - start_time) * 1000.0

    # Bounding box
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

    return {
        "scene_id": "baseline_scene",
        "method": "BASELINE",
        "source_file": Path(image_path).name,
        "image_width": w,
        "image_height": h,
        "scale": {
            "meters_per_pixel": default_scale_m_per_px,
            "pixels_per_meter": 50.0,
            "source": "naive_relative_fallback",
            "confidence": "LOW",
            "confidence_score": 0.30
        },
        "walls": raw_walls,
        "doors": [],       # Baseline does not perform door detection
        "windows": [],     # Baseline does not perform window detection
        "rooms": [],       # Baseline does not perform topological room cycle extraction
        "summary": {
            "wall_count": len(raw_walls),
            "door_count": 0,
            "window_count": 0,
            "room_count": 0,
            "processing_time_ms": round(elapsed_ms, 1)
        },
        "bounds": {
            "min": min_b,
            "max": max_b,
            "width_m": width_m,
            "depth_m": depth_m,
            "height_m": height_m
        },
        "objects": wall_3d_objects,
        "metrics": {
            "processing_time_ms": round(elapsed_ms, 1)
        },
        "_trimesh_scene": tri_scene
    }

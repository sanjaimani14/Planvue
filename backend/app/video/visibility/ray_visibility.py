"""
Ray visibility and frustum intersection engine for Mode B.
Computes geometric line-of-sight and frustum ray tests.
"""
from typing import List, Tuple, Optional, Dict, Any
import math
import numpy as np

def compute_camera_viewing_direction(rotation_matrix: List[List[float]]) -> np.ndarray:
    """Computes normalized forward viewing vector in world space from rotation matrix R."""
    R = np.array(rotation_matrix, dtype=np.float64)
    dir_vec = R @ np.array([0.0, 0.0, 1.0])
    norm = np.linalg.norm(dir_vec)
    return dir_vec / norm if norm > 1e-6 else np.array([0.0, 0.0, 1.0])

def is_point_in_camera_frustum(
    pt: np.ndarray,
    cam_pos: np.ndarray,
    cam_rot: List[List[float]],
    fov_deg: float = 65.0,
    near_clip: float = 0.20,
    far_clip: float = 8.00
) -> Tuple[bool, float, float]:
    """
    Checks if a 3D point is within the camera's viewing frustum.
    Returns: (in_frustum, distance, cos_angle)
    """
    diff = pt - cam_pos
    dist = float(np.linalg.norm(diff))
    if dist < near_clip or dist > far_clip:
        return False, dist, 0.0

    cam_dir = compute_camera_viewing_direction(cam_rot)
    ray = diff / dist
    cos_angle = float(np.dot(ray, cam_dir))
    half_fov_rad = math.radians(fov_deg / 2.0)
    cos_threshold = math.cos(half_fov_rad)

    in_frustum = cos_angle >= cos_threshold
    return in_frustum, dist, cos_angle

def compute_ray_plane_intersection(
    ray_origin: np.ndarray,
    ray_dir: np.ndarray,
    plane_normal: np.ndarray,
    plane_offset: float
) -> Optional[Tuple[np.ndarray, float]]:
    """
    Computes ray-plane intersection: n . P + d = 0
    t = -(n . O + d) / (n . D)
    Returns (hit_point, t) if t > 0, else None.
    """
    denom = float(np.dot(plane_normal, ray_dir))
    if abs(denom) < 1e-6:
        return None  # Parallel
    
    t = -(float(np.dot(plane_normal, ray_origin)) + plane_offset) / denom
    if t <= 0.001:
        return None
    
    hit_pt = ray_origin + t * ray_dir
    return hit_pt, t

def is_ray_occluded(
    origin: np.ndarray,
    target: np.ndarray,
    occluder_boxes: List[Dict[str, List[float]]]
) -> bool:
    """
    Tests if line segment between origin and target intersects any occluder bounding box.
    occluder_box: {"min": [x,y,z], "max": [x,y,z]}
    """
    direction = target - origin
    dist = float(np.linalg.norm(direction))
    if dist < 1e-4:
        return False
    d = direction / dist

    for box in occluder_boxes:
        b_min = np.array(box["min"], dtype=np.float64)
        b_max = np.array(box["max"], dtype=np.float64)

        # Slab method for AABB ray intersection
        tmin = 0.001
        tmax = dist - 0.001

        intersected = True
        for i in range(3):
            if abs(d[i]) < 1e-7:
                if origin[i] < b_min[i] or origin[i] > b_max[i]:
                    intersected = False
                    break
            else:
                inv_d = 1.0 / d[i]
                t1 = (b_min[i] - origin[i]) * inv_d
                t2 = (b_max[i] - origin[i]) * inv_d
                if t1 > t2:
                    t1, t2 = t2, t1
                tmin = max(tmin, t1)
                tmax = min(tmax, t2)
                if tmin > tmax:
                    intersected = False
                    break
        
        if intersected and tmin < tmax and tmin < dist:
            return True

    return False

def cast_frustum_rays(
    cam_pos: np.ndarray,
    cam_rot: List[List[float]],
    num_horizontal: int = 7,
    num_vertical: int = 5,
    fov_h_deg: float = 65.0,
    fov_v_deg: float = 48.0
) -> List[np.ndarray]:
    """Generates a bundle of discrete rays spanning the camera viewing frustum."""
    R = np.array(cam_rot, dtype=np.float64)
    # Camera local: X=right, Y=down, Z=forward
    rays = []
    h_angles = np.linspace(-math.radians(fov_h_deg/2), math.radians(fov_h_deg/2), num_horizontal)
    v_angles = np.linspace(-math.radians(fov_v_deg/2), math.radians(fov_v_deg/2), num_vertical)

    for v in v_angles:
        for h in h_angles:
            # local ray
            local_ray = np.array([math.sin(h), math.sin(v), math.cos(h) * math.cos(v)], dtype=np.float64)
            local_ray /= np.linalg.norm(local_ray)
            world_ray = R @ local_ray
            world_ray /= np.linalg.norm(world_ray)
            rays.append(world_ray)
            
    return rays

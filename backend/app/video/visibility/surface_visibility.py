"""
Surface Visibility Evaluator for Mode B.
Computes camera viewing angles, occlusions, and sample point visibility across planar architectural surfaces.
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np
from pydantic import BaseModel, Field

from backend.app.video.schemas import CameraPose, PlaneSurface
from .ray_visibility import compute_camera_viewing_direction, is_point_in_camera_frustum, is_ray_occluded

class SurfacePatchVisibility(BaseModel):
    surface_id: str
    surface_type: str  # "WALL" | "FLOOR" | "CEILING"
    sample_points_count: int
    observed_samples: int
    weak_samples: int
    unseen_samples: int
    coverage_ratio: float
    visibility_status: str  # "OBSERVED" | "WEAKLY_OBSERVED" | "UNSEEN"
    supporting_frames: List[int] = Field(default_factory=list)
    reason: str = ""

def evaluate_surface_visibility(
    surface_id: str,
    surface_type: str,
    plane_normal: List[float],
    plane_bounds: Dict[str, Any],
    camera_poses: List[CameraPose],
    occluders: List[Dict[str, List[float]]] = None,
    num_samples_u: int = 6,
    num_samples_v: int = 4
) -> SurfacePatchVisibility:
    """
    Evaluates multi-view camera visibility for an architectural surface patch.
    Samples a regular 2D grid across surface bounds and tests frustum visibility & occlusions.
    """
    occluders = occluders or []
    n = np.array(plane_normal, dtype=np.float64)
    norm_n = np.linalg.norm(n)
    if norm_n > 1e-6:
        n /= norm_n
    else:
        n = np.array([0.0, 1.0, 0.0])

    p_min = plane_bounds.get("min", [-2.0, 0.0, -2.0])
    p_max = plane_bounds.get("max", [2.0, 2.8, 2.0])

    # Sample grid of 3D points
    samples = []
    if surface_type == "FLOOR" or surface_type == "CEILING":
        # Sample in X-Z
        xs = np.linspace(p_min[0], p_max[0], num_samples_u)
        zs = np.linspace(p_min[2], p_max[2], num_samples_v)
        y = p_min[1] if surface_type == "FLOOR" else p_max[1]
        for x in xs:
            for z in zs:
                samples.append(np.array([x, y, z], dtype=np.float64))
    else:
        # Wall: determine primary axis
        dx = abs(p_max[0] - p_min[0])
        dz = abs(p_max[2] - p_min[2])
        ys = np.linspace(p_min[1], p_max[1], num_samples_v)
        if dx >= dz:
            xs = np.linspace(p_min[0], p_max[0], num_samples_u)
            z = (p_min[2] + p_max[2]) / 2.0
            for x in xs:
                for y in ys:
                    samples.append(np.array([x, y, z], dtype=np.float64))
        else:
            zs = np.linspace(p_min[2], p_max[2], num_samples_u)
            x = (p_min[0] + p_max[0]) / 2.0
            for z in zs:
                for y in ys:
                    samples.append(np.array([x, y, z], dtype=np.float64))

    tot_samples = max(1, len(samples))
    observed_cnt = 0
    weak_cnt = 0
    unseen_cnt = 0
    frames_hit: Dict[int, int] = {}

    for pt in samples:
        hit_cameras = 0
        for c in camera_poses:
            cam_pos = np.array(c.position, dtype=np.float64)
            in_frustum, dist, cos_a = is_point_in_camera_frustum(
                pt, cam_pos, c.rotation, fov_deg=65.0, near_clip=0.2, far_clip=8.0
            )
            if in_frustum:
                # Check normal facing camera: camera-to-point ray dot normal < 0 (facing)
                ray_dir = (pt - cam_pos) / max(1e-4, dist)
                face_dot = float(np.dot(ray_dir, n))
                # If absolute dot > 0.05 (not completely edge-on)
                if abs(face_dot) > 0.05:
                    if not is_ray_occluded(cam_pos, pt, occluders):
                        hit_cameras += 1
                        frames_hit[c.frame_index] = frames_hit.get(c.frame_index, 0) + 1

        if hit_cameras >= 2:
            observed_cnt += 1
        elif hit_cameras == 1:
            weak_cnt += 1
        else:
            unseen_cnt += 1

    cov_ratio = round((observed_cnt + 0.5 * weak_cnt) / tot_samples, 2)
    cov_ratio = min(1.0, max(0.0, cov_ratio))

    if cov_ratio >= 0.55:
        vis_status = "OBSERVED"
        reason = "Surface received direct multi-view optical coverage from camera trajectory."
    elif cov_ratio >= 0.20:
        vis_status = "WEAKLY_OBSERVED"
        reason = "Surface partially intersected camera frustum, but lacks multi-view redundancy."
    else:
        vis_status = "UNSEEN"
        reason = "Surface lies outside camera field of view or is blocked by occluding structures."

    # Top supporting frames
    sorted_frames = sorted(frames_hit.items(), key=lambda kv: kv[1], reverse=True)
    top_frames = [f[0] for f in sorted_frames[:4]]

    return SurfacePatchVisibility(
        surface_id=surface_id,
        surface_type=surface_type,
        sample_points_count=tot_samples,
        observed_samples=observed_cnt,
        weak_samples=weak_cnt,
        unseen_samples=unseen_cnt,
        coverage_ratio=cov_ratio,
        visibility_status=vis_status,
        supporting_frames=top_frames,
        reason=reason
    )

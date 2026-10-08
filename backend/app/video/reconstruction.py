"""
Sparse 3D Reconstruction and Planar Surface Estimation Engine for Mode B.
Triangulates multi-view point correspondences, filters outliers, and fits structural planes via RANSAC.
"""

from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

from backend.app.video.schemas import Point3D, PlaneSurface

def triangulate_pairwise_points(
    P1: np.ndarray,
    P2: np.ndarray,
    pts1: np.ndarray,
    pts2: np.ndarray,
    frame_idx1: int,
    frame_idx2: int,
    img1: np.ndarray,
    max_reproj_err: float = 8.0
) -> List[Point3D]:
    """
    Triangulates 2D matched correspondences into 3D world coordinates.
    Filters out invalid depth and points with high reprojection error.
    """
    if len(pts1) == 0 or len(pts2) == 0:
        return []

    # Triangulate homogeneous coordinates (4xN)
    pts4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
    w_coords = pts4d[3]
    
    # Avoid division by zero
    valid_w = np.abs(w_coords) > 1e-6
    pts3d = pts4d[:3, valid_w] / w_coords[valid_w]
    pts3d = pts3d.T  # (N, 3)

    valid_pts1 = pts1[valid_w]
    h, w = img1.shape[:2]

    points: List[Point3D] = []
    for idx, (X, pt2d) in enumerate(zip(pts3d, valid_pts1)):
        x, y, z = float(X[0]), float(X[1]), float(X[2])

        # Depth check: point must be in front of camera and within indoor room bounds
        if z <= 0.1 or z > 15.0 or abs(x) > 12.0 or abs(y) > 10.0:
            continue

        # Check reprojection error on camera 1
        X_homo = np.array([x, y, z, 1.0], dtype=np.float64)
        proj1 = P1 @ X_homo
        if proj1[2] <= 0:
            continue
        u_p1 = proj1[0] / proj1[2]
        v_p1 = proj1[1] / proj1[2]
        reproj_err = float(np.hypot(u_p1 - pt2d[0], v_p1 - pt2d[1]))
        if reproj_err > max_reproj_err:
            continue

        # Sample RGB color from image
        px = int(np.clip(pt2d[0], 0, w - 1))
        py = int(np.clip(pt2d[1], 0, h - 1))
        b, g, r = img1[py, px]

        pt_id = f"pt_{frame_idx1}_{frame_idx2}_{idx:04d}"
        points.append(Point3D(
            id=pt_id,
            position=[round(x, 3), round(y, 3), round(z, 3)],
            color=[int(r), int(g), int(b)],
            observation_count=2,
            source_frames=[frame_idx1, frame_idx2],
            reprojection_error=round(reproj_err, 2),
            status="OBSERVED"
        ))

    return points

def fit_planes_ransac(
    points: List[Point3D],
    max_planes: int = 5,
    dist_threshold: float = 0.18,
    min_inliers: int = 15
) -> List[PlaneSurface]:
    """
    Fits dominant architectural planes (floor, walls, ceiling) to sparse 3D point cloud using RANSAC.
    """
    if len(points) < min_inliers:
        return []

    pts_array = np.array([p.position for p in points], dtype=np.float64)
    remaining_indices = set(range(len(pts_array)))
    planes: List[PlaneSurface] = []

    for plane_idx in range(max_planes):
        if len(remaining_indices) < min_inliers:
            break

        current_pts = pts_array[list(remaining_indices)]
        curr_map = list(remaining_indices)

        best_inliers = []
        best_normal = None
        best_d = 0.0

        # RANSAC iterations
        n_iters = min(200, max(50, len(current_pts) * 2))
        for _ in range(n_iters):
            sample_idx = np.random.choice(len(current_pts), 3, replace=False)
            p1, p2, p3 = current_pts[sample_idx]

            v1 = p2 - p1
            v2 = p3 - p1
            norm = np.cross(v1, v2)
            norm_len = np.linalg.norm(norm)
            if norm_len < 1e-6:
                continue

            normal = norm / norm_len
            d = -np.dot(normal, p1)

            # Distance of all current points to plane: |ax + by + cz + d|
            dists = np.abs(np.dot(current_pts, normal) + d)
            inliers = np.where(dists < dist_threshold)[0]

            if len(inliers) > len(best_inliers):
                best_inliers = inliers
                best_normal = normal
                best_d = d

        if len(best_inliers) < min_inliers:
            break

        inlier_global_indices = [curr_map[idx] for idx in best_inliers]
        inlier_pts = pts_array[inlier_global_indices]

        # Classify surface based on normal direction
        # Y is up-axis
        ny = abs(best_normal[1])
        mean_y = float(np.mean(inlier_pts[:, 1]))

        if ny > 0.70:
            if mean_y < 0.8:
                surface_type = "FLOOR"
            else:
                surface_type = "CEILING"
        else:
            surface_type = "WALL"

        bounds = {
            "min": [float(np.min(inlier_pts[:, 0])), float(np.min(inlier_pts[:, 1])), float(np.min(inlier_pts[:, 2]))],
            "max": [float(np.max(inlier_pts[:, 0])), float(np.max(inlier_pts[:, 1])), float(np.max(inlier_pts[:, 2]))]
        }

        confidence = round(min(0.95, len(best_inliers) / 100.0 + 0.40), 2)
        plane_id = f"PLN_{surface_type[:3]}_{plane_idx+1:02d}"

        planes.append(PlaneSurface(
            plane_id=plane_id,
            surface_type=surface_type,
            normal=[round(float(best_normal[0]), 4), round(float(best_normal[1]), 4), round(float(best_normal[2]), 4)],
            offset=round(float(best_d), 4),
            inlier_count=len(best_inliers),
            confidence=confidence,
            bounds=bounds,
            status="OBSERVED"
        ))

        # Remove inliers so subsequent planes fit remaining points
        for g_idx in inlier_global_indices:
            remaining_indices.discard(g_idx)

    return planes

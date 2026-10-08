"""
Camera Motion Estimation and Trajectory Reconstruction Engine for Mode B.
Computes relative rotation R and translation t using Essential Matrix decomposition and RANSAC.
"""

from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

from backend.app.video.schemas import CameraPose

def build_camera_intrinsics(width: int, height: int, f_factor: float = 1.0) -> np.ndarray:
    """
    Constructs pinhole camera intrinsic matrix K.
    Focal length approximated from typical 70-80 deg field-of-view phone cameras.
    """
    f = float(max(width, height)) * f_factor
    cx = float(width) / 2.0
    cy = float(height) / 2.0
    return np.array([
        [f, 0.0, cx],
        [0.0, f, cy],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

def estimate_camera_trajectory(
    pts_pairs: List[Tuple[np.ndarray, np.ndarray]],
    keyframe_timestamps: List[float],
    width: int,
    height: int,
    step_scale_relative: float = 0.35,
    camera_height_offset: float = 1.40
) -> Tuple[List[CameraPose], np.ndarray, List[np.ndarray]]:
    """
    Recovers sequential camera rotation and translation trajectory.
    Returns:
    - List of CameraPose objects
    - Intrinsic matrix K
    - Projection matrices P for each frame [P0, P1, ...]
    """
    K = build_camera_intrinsics(width, height)
    num_frames = len(pts_pairs) + 1 if pts_pairs else 1

    # First camera is at identity pose [I | 0]
    cur_R = np.eye(3, dtype=np.float64)
    cur_t = np.zeros((3, 1), dtype=np.float64)

    poses: List[CameraPose] = []
    projection_matrices: List[np.ndarray] = []

    # Frame 0 projection matrix
    P0 = K @ np.hstack([cur_R, cur_t])
    projection_matrices.append(P0)

    # Eye height is placed along Y axis
    poses.append(CameraPose(
        frame_index=0,
        timestamp_s=keyframe_timestamps[0] if keyframe_timestamps else 0.0,
        position=[0.0, camera_height_offset, 0.0],
        rotation=cur_R.tolist(),
        inliers_count=0,
        focal_length_px=float(K[0, 0])
    ))

    for i, (pts1, pts2) in enumerate(pts_pairs):
        t_stamp = keyframe_timestamps[i + 1] if i + 1 < len(keyframe_timestamps) else (i + 1) * 0.5
        
        if len(pts1) < 8 or len(pts2) < 8:
            # Fallback for degenerate motion or insufficient features: small linear forward drift
            forward_vec = cur_R @ np.array([[0.0], [0.0], [step_scale_relative]])
            cur_t = cur_t + forward_vec
            P_i = K @ np.hstack([cur_R, cur_t])
            projection_matrices.append(P_i)
            poses.append(CameraPose(
                frame_index=i + 1,
                timestamp_s=t_stamp,
                position=[float(cur_t[0, 0]), float(cur_t[1, 0]) + camera_height_offset, float(cur_t[2, 0])],
                rotation=cur_R.tolist(),
                inliers_count=0,
                focal_length_px=float(K[0, 0])
            ))
            continue

        # Essential Matrix estimation
        E, mask = cv2.findEssentialMat(
            pts1, pts2, K,
            method=cv2.RANSAC,
            prob=0.999,
            threshold=1.5
        )

        if E is None or mask is None:
            forward_vec = cur_R @ np.array([[0.0], [0.0], [step_scale_relative]])
            cur_t = cur_t + forward_vec
            P_i = K @ np.hstack([cur_R, cur_t])
            projection_matrices.append(P_i)
            poses.append(CameraPose(
                frame_index=i + 1,
                timestamp_s=t_stamp,
                position=[float(cur_t[0, 0]), float(cur_t[1, 0]) + camera_height_offset, float(cur_t[2, 0])],
                rotation=cur_R.tolist(),
                inliers_count=0,
                focal_length_px=float(K[0, 0])
            ))
            continue

        inliers = mask.ravel() == 1
        num_inliers = int(np.sum(inliers))

        # Recover relative pose
        _, R_rel, t_rel, _ = cv2.recoverPose(E, pts1[inliers], pts2[inliers], K)

        # Accumulate world pose: R_world = R_prev * R_rel, t_world = t_prev + R_prev * (t_rel * step)
        t_world = cur_t + cur_R @ (t_rel * step_scale_relative)
        R_world = cur_R @ R_rel

        cur_R = R_world
        cur_t = t_world

        P_i = K @ np.hstack([cur_R, cur_t])
        projection_matrices.append(P_i)

        poses.append(CameraPose(
            frame_index=i + 1,
            timestamp_s=t_stamp,
            position=[
                round(float(cur_t[0, 0]), 3),
                round(float(cur_t[1, 0]) + camera_height_offset, 3),
                round(float(cur_t[2, 0]), 3)
            ],
            rotation=[[round(float(v), 4) for v in row] for row in cur_R.tolist()],
            inliers_count=num_inliers,
            focal_length_px=float(K[0, 0])
        ))

    return poses, K, projection_matrices

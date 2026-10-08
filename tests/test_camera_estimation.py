import pytest
import numpy as np
from backend.app.video.camera_estimation import build_camera_intrinsics, estimate_camera_trajectory

def test_camera_intrinsics_matrix():
    K = build_camera_intrinsics(640, 480)
    assert K.shape == (3, 3)
    assert K[0, 0] > 0.0  # focal x
    assert K[1, 1] > 0.0  # focal y
    assert K[0, 2] == 320.0  # cx
    assert K[1, 2] == 240.0  # cy
    assert K[2, 2] == 1.0

def test_camera_trajectory_solver():
    # Synthetic point pairs simulating smooth rightward camera pan
    pts1 = np.array([[100, 100], [200, 100], [300, 150], [400, 200],
                     [150, 300], [250, 300], [350, 350], [450, 400]], dtype=np.float32)
    pts2 = pts1 - np.array([15.0, 0.0], dtype=np.float32)  # 15px shift
    pts_pairs = [(pts1, pts2)]
    timestamps = [0.0, 0.5]

    poses, K, proj_mats = estimate_camera_trajectory(pts_pairs, timestamps, 640, 480)
    assert len(poses) == 2
    assert poses[0].frame_index == 0
    assert poses[1].frame_index == 1
    assert len(proj_mats) == 2
    assert proj_mats[0].shape == (3, 4)
    # Check that position has 3 components
    assert len(poses[0].position) == 3
    assert len(poses[1].position) == 3

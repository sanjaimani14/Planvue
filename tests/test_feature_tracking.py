import pytest
import numpy as np
import cv2
from backend.app.video.feature_tracking import FeatureTracker

def test_feature_tracker_extraction_and_matching():
    tracker = FeatureTracker(n_features=500, ratio_thresh=0.80)
    
    # Create two synthetic frames with textured patterns
    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
    for x in range(50, 600, 40):
        for y in range(50, 450, 40):
            cv2.circle(frame1, (x, y), 8, (255, 255, 255), -1)

    # Frame 2 shifted slightly
    M = np.float32([[1, 0, -10], [0, 1, 2]])
    frame2 = cv2.warpAffine(frame1, M, (640, 480))

    kps, des = tracker.extract_features([frame1, frame2])
    assert len(kps) == 2
    assert len(des) == 2
    assert des[0] is not None
    assert des[1] is not None
    assert len(kps[0]) > 20
    assert len(kps[1]) > 20

    pts1, pts2, matches = tracker.match_pair(kps[0], des[0], kps[1], des[1])
    assert len(pts1) >= 8
    assert len(pts2) == len(pts1)
    assert len(matches) == len(pts1)

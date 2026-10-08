"""
Feature Detection, Matching, and Track Extraction Engine for Mode B.
Uses robust ORB keypoints, Lowe's ratio filtering, and RANSAC epipolar constraints.
"""

from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

class FeatureTracker:
    def __init__(self, n_features: int = 1500, ratio_thresh: float = 0.75):
        self.orb = cv2.ORB_create(
            nfeatures=n_features,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31,
            fastThreshold=20
        )
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        self.ratio_thresh = ratio_thresh

    def extract_features(self, frames: List[np.ndarray]) -> Tuple[List[Any], List[Optional[np.ndarray]]]:
        """Extracts 2D keypoints and binary descriptors across all keyframes."""
        all_kps = []
        all_des = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kps, des = self.orb.detectAndCompute(gray, None)
            all_kps.append(kps)
            all_des.append(des)
        return all_kps, all_des

    def match_pair(
        self,
        kps1: List[cv2.KeyPoint],
        des1: Optional[np.ndarray],
        kps2: List[cv2.KeyPoint],
        des2: Optional[np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Matches descriptors between a pair of frames with Lowe's ratio test and Fundamental matrix RANSAC.
        Returns (pts1, pts2, match_info).
        """
        if des1 is None or des2 is None or len(des1) < 8 or len(des2) < 8:
            return np.empty((0, 2), dtype=np.float32), np.empty((0, 2), dtype=np.float32), []

        raw_matches = self.matcher.knnMatch(des1, des2, k=2)
        good_matches = []
        for match in raw_matches:
            if len(match) == 2:
                m, n = match
                if m.distance < self.ratio_thresh * n.distance:
                    good_matches.append(m)

        if len(good_matches) < 8:
            return np.empty((0, 2), dtype=np.float32), np.empty((0, 2), dtype=np.float32), []

        pts1 = np.float32([kps1[m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([kps2[m.trainIdx].pt for m in good_matches])

        # RANSAC filtering with Fundamental matrix
        F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 2.5, 0.99)
        if F is None or mask is None:
            return np.empty((0, 2), dtype=np.float32), np.empty((0, 2), dtype=np.float32), []

        inliers = mask.ravel() == 1
        filtered_pts1 = pts1[inliers]
        filtered_pts2 = pts2[inliers]

        match_records = []
        idx = 0
        for i, is_inlier in enumerate(inliers):
            if is_inlier:
                m = good_matches[i]
                match_records.append({
                    "query_idx": m.queryIdx,
                    "train_idx": m.trainIdx,
                    "distance": float(m.distance),
                    "pt1": [float(filtered_pts1[idx][0]), float(filtered_pts1[idx][1])],
                    "pt2": [float(filtered_pts2[idx][0]), float(filtered_pts2[idx][1])]
                })
                idx += 1

        return filtered_pts1, filtered_pts2, match_records

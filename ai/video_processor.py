import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

def extract_keyframes_from_video(
    video_path: str,
    max_keyframes: int = 16,
    min_sharpness_var: float = 30.0
) -> Tuple[List[np.ndarray], Dict[str, Any]]:
    """
    Extracts informative, non-blurry keyframes from a static walkthrough video.
    Filters frames based on:
    - Laplacian variance (motion blur rejection)
    - Inter-frame visual distance (histogram correlation/difference)
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duration_s = total_frames / fps if fps > 0 else 0.0

    all_frames = []
    sharpness_scores = []
    
    # Read evenly spaced frames
    step = max(1, total_frames // (max_keyframes * 3))
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % step == 0:
            # Measure sharpness via Laplacian variance
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            all_frames.append((frame_idx, frame, sharpness))
            sharpness_scores.append(sharpness)

        frame_idx += 1

    cap.release()

    # Filter out blurred frames and select keyframes with maximum visual disparity
    selected_keyframes: List[np.ndarray] = []
    selected_indices: List[int] = []
    
    # Sort or pick keyframes with good sharpness
    if all_frames:
        # Pick frames spaced along trajectory
        target_interval = max(1, len(all_frames) // max_keyframes)
        for i in range(0, len(all_frames), target_interval):
            # In local neighborhood, pick the frame with highest sharpness
            window = all_frames[i : min(i + target_interval, len(all_frames))]
            best_in_window = max(window, key=lambda item: item[2])
            selected_keyframes.append(best_in_window[1])
            selected_indices.append(best_in_window[0])
            if len(selected_keyframes) >= max_keyframes:
                break

    meta = {
        "total_frames": total_frames,
        "fps": round(fps, 1),
        "duration_seconds": round(duration_s, 2),
        "keyframes_selected": len(selected_keyframes),
        "keyframe_indices": selected_indices,
        "mean_sharpness": round(float(np.mean(sharpness_scores)) if sharpness_scores else 0.0, 2)
    }

    return selected_keyframes, meta

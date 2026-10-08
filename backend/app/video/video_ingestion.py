"""
Video Ingestion and Format Validation Engine for Mode B.
Validates video containers, streams, and physical metadata without external cloud dependencies.
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import cv2

from backend.app.video.schemas import VideoMetadata

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
MAX_FILE_SIZE_BYTES = 120 * 1024 * 1024  # 120 MB
MAX_DURATION_SECONDS = 180.0
MIN_DURATION_SECONDS = 1.0

from typing import Tuple, Dict, Any, Optional, Union

def validate_and_ingest_video(
    video_path: Union[str, Path],
    video_id: str = "vid_sample"
) -> Tuple[bool, Optional[VideoMetadata], Optional[str]]:
    """
    Validates container, checks dimensions, FPS, frame counts, and duration.
    Returns (is_valid, metadata, error_message).
    """
    path = Path(video_path)
    if not path.exists():
        return False, None, f"Video file not found at path: {video_path}"

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, None, f"Unsupported format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"

    file_size = path.stat().st_size
    if file_size == 0:
        return False, None, "Video file is empty (0 bytes)"
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, None, f"Video exceeds size limit ({file_size / (1024*1024):.1f}MB > 120MB)"

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return False, None, "Failed to decode video stream. Container may be corrupted or codec unsupported."

    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0

        if width <= 0 or height <= 0 or total_frames <= 0:
            return False, None, "Video contains invalid spatial or temporal dimensions (0 frames or 0x0 resolution)"

        duration_s = total_frames / fps if fps > 0 else 0.0

        if duration_s < MIN_DURATION_SECONDS:
            return False, None, f"Video is too short ({duration_s:.1f}s). Walkthroughs must be at least {MIN_DURATION_SECONDS}s"

        # Read fourcc codec
        fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)]) if fourcc_int > 0 else "mp4v"

        meta = VideoMetadata(
            video_id=video_id,
            filename=path.name,
            duration_seconds=round(duration_s, 2),
            fps=round(fps, 2),
            total_frames=total_frames,
            width=width,
            height=height,
            codec=codec,
            size_bytes=file_size,
            file_url=f"/data/video/{path.name}"
        )
        return True, meta, None

    except Exception as e:
        return False, None, f"Metadata extraction failed: {str(e)}"
    finally:
        cap.release()

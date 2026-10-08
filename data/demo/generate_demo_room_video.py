"""
Generates a realistic synthetic indoor room walkthrough video for Mode B testing and demo.
Simulates a handheld walkthrough where 3 walls are observed while 1 perimeter wall is occluded.
"""

from pathlib import Path
import math
import cv2
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = OUTPUT_DIR / "sample_room.mp4"

def generate_sample_room_walkthrough_video(
    output_path: str = str(VIDEO_PATH),
    width: int = 640,
    height: int = 480,
    fps: int = 30,
    duration_s: float = 8.0
):
    """
    Renders an 8-second 640x480 room walkthrough video with perspective projection:
    - 4 walls (South, East, West visible; North occluded by an interior divider/wardrobe)
    - Floor grid pattern providing strong ORB feature track points
    - Wall paintings/posters providing planar feature points
    - Handheld camera trajectory panning smoothly from South-West towards East
    """
    total_frames = int(fps * duration_s)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    # Room bounds: X in [-3, 3], Y in [0, 2.8], Z in [0.5, 6.0]
    # Camera path: moving from x=-1.2 to x=+1.2, z=1.0 to z=2.2, y=1.4m
    for i in range(total_frames):
        t = i / float(total_frames)
        
        # Camera position
        cam_x = -1.2 + 2.4 * t + 0.02 * math.sin(i * 0.4)  # Small handheld wobble
        cam_y = 1.40 + 0.015 * math.cos(i * 0.5)
        cam_z = 1.0 + 1.2 * t

        # Camera yaw angle (panning from slightly left to right)
        yaw = -0.15 + 0.30 * t

        frame = np.full((height, width, 3), (220, 220, 225), dtype=np.uint8)

        # Draw perspective floor
        # Floor points from z=1.0 to 6.0, x from -3.0 to 3.0
        focal = 400.0
        cx = width / 2.0
        cy = height / 2.0

        def project(wx, wy, wz):
            # Translate relative to camera
            rx = wx - cam_x
            ry = wy - cam_y
            rz = wz - cam_z
            # Rotate yaw around Y
            cos_y = math.cos(-yaw)
            sin_y = math.sin(-yaw)
            px = rx * cos_y - rz * sin_y
            py = ry
            pz = rx * sin_y + rz * cos_y
            if pz <= 0.2:
                return None
            sx = int(cx + (px / pz) * focal)
            sy = int(cy - (py / pz) * focal)  # Y is up
            return (sx, sy)

        # Draw floor grid lines
        for gz in np.linspace(1.5, 6.0, 10):
            p_left = project(-3.0, 0.0, gz)
            p_right = project(3.0, 0.0, gz)
            if p_left and p_right:
                cv2.line(frame, p_left, p_right, (180, 180, 190), 1)

        for gx in np.linspace(-3.0, 3.0, 11):
            p_near = project(gx, 0.0, 1.2)
            p_far = project(gx, 0.0, 6.0)
            if p_near and p_far:
                cv2.line(frame, p_near, p_far, (180, 180, 190), 1)

        # Draw West wall (x = -3.0)
        w_bot1 = project(-3.0, 0.0, 1.2)
        w_bot2 = project(-3.0, 0.0, 6.0)
        w_top1 = project(-3.0, 2.6, 1.2)
        w_top2 = project(-3.0, 2.6, 6.0)
        if w_bot1 and w_bot2 and w_top1 and w_top2:
            pts = np.array([w_bot1, w_bot2, w_top2, w_top1], np.int32)
            cv2.fillPoly(frame, [pts], (200, 205, 210))
            cv2.polylines(frame, [pts], True, (130, 135, 140), 2)

        # Draw East wall (x = 3.0)
        e_bot1 = project(3.0, 0.0, 1.2)
        e_bot2 = project(3.0, 0.0, 6.0)
        e_top1 = project(3.0, 2.6, 1.2)
        e_top2 = project(3.0, 2.6, 6.0)
        if e_bot1 and e_bot2 and e_top1 and e_top2:
            pts = np.array([e_bot1, e_bot2, e_top2, e_top1], np.int32)
            cv2.fillPoly(frame, [pts], (195, 200, 205))
            cv2.polylines(frame, [pts], True, (130, 135, 140), 2)

        # Draw high-contrast feature posters on East wall to ensure robust ORB keypoints
        for poster_z in [2.5, 4.2]:
            p1 = project(2.98, 1.2, poster_z - 0.4)
            p2 = project(2.98, 1.2, poster_z + 0.4)
            p3 = project(2.98, 2.0, poster_z + 0.4)
            p4 = project(2.98, 2.0, poster_z - 0.4)
            if p1 and p2 and p3 and p4:
                pts = np.array([p1, p2, p3, p4], np.int32)
                cv2.fillPoly(frame, [pts], (70, 90, 140))
                cv2.polylines(frame, [pts], True, (40, 50, 80), 2)
                # Inner contrast pattern
                m_pt = project(2.98, 1.6, poster_z)
                if m_pt:
                    cv2.circle(frame, m_pt, 6, (240, 220, 100), -1)

        # Draw Occluding Wardrobe / Partition Divider (x in [-0.8, 0.8], z=3.8, height=2.4)
        # This occludes the North wall behind it!
        div_bl = project(-0.8, 0.0, 3.8)
        div_br = project(0.8, 0.0, 3.8)
        div_tr = project(0.8, 2.2, 3.8)
        div_tl = project(-0.8, 2.2, 3.8)
        if div_bl and div_br and div_tr and div_tl:
            pts = np.array([div_bl, div_br, div_tr, div_tl], np.int32)
            cv2.fillPoly(frame, [pts], (110, 80, 60))
            cv2.polylines(frame, [pts], True, (60, 40, 30), 2)
            # Wardrobe door handles
            h1 = project(-0.1, 1.1, 3.79)
            h2 = project(0.1, 1.1, 3.79)
            if h1:
                cv2.circle(frame, h1, 3, (220, 220, 230), -1)
            if h2:
                cv2.circle(frame, h2, 3, (220, 220, 230), -1)

        # Add slight natural Gaussian noise
        noise = np.random.normal(0, 2, frame.shape).astype(np.int16)
        noisy_frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Write frame
        out.write(noisy_frame)

    out.release()
    print(f"Generated sample room walkthrough video: {output_path} ({total_frames} frames, {width}x{height})")

if __name__ == "__main__":
    generate_sample_room_walkthrough_video()

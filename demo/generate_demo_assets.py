import cv2
import numpy as np
import json
import math
from pathlib import Path

def generate_blueprint_asset(output_path: str):
    """
    Generates a clean, realistic architectural 2D floor plan image
    with multiple rooms, doors with arc swings, windows, and dimension annotations.
    """
    width, height = 1400, 1000
    # White background blueprint
    img = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Grid lines (light gray architectural grid)
    for x in range(0, width, 40):
        cv2.line(img, (x, 0), (x, height), (242, 244, 246), 1)
    for y in range(0, height, 40):
        cv2.line(img, (0, y), (width, y), (242, 244, 246), 1)

    # Wall coordinates (black thick lines, thickness 14px)
    wall_color = (25, 25, 28)
    wall_thickness = 14

    # Outer perimeter: (150, 150) to (1250, 850)
    # North wall
    cv2.line(img, (150, 150), (1250, 150), wall_color, wall_thickness)
    # South wall
    cv2.line(img, (150, 850), (1250, 850), wall_color, wall_thickness)
    # West wall
    cv2.line(img, (150, 150), (150, 850), wall_color, wall_thickness)
    # East wall
    cv2.line(img, (1250, 150), (1250, 850), wall_color, wall_thickness)

    # Interior dividing walls
    # Vertical divider 1: x = 650, from y = 150 to 850 (separates living from bedrooms)
    # With a door gap from y = 450 to 530
    cv2.line(img, (650, 150), (650, 450), wall_color, wall_thickness)
    cv2.line(img, (650, 530), (650, 850), wall_color, wall_thickness)

    # Horizontal divider 1: in east wing, y = 500 from x = 650 to 1250 (separates Bedroom 1 and Bedroom 2)
    # With a door gap from x = 700 to 780
    cv2.line(img, (780, 500), (1250, 500), wall_color, wall_thickness)

    # Interior bathroom in west wing: (150, 580) to (450, 850)
    # North bath wall with door gap from x = 320 to 400
    cv2.line(img, (150, 580), (320, 580), wall_color, wall_thickness)
    # East bath wall
    cv2.line(img, (450, 580), (450, 850), wall_color, wall_thickness)

    # --- DOORS & SWING ARCS (thin lines) ---
    door_color = (90, 95, 105)
    # Door 1: Living to Bedroom hall at (650, 450)
    cv2.line(img, (650, 450), (590, 510), door_color, 2)
    cv2.ellipse(img, (650, 450), (80, 80), 0, 90, 180, door_color, 2)

    # Door 2: Bedroom 2 entrance at (780, 500)
    cv2.line(img, (780, 500), (780, 560), door_color, 2)
    cv2.ellipse(img, (780, 500), (60, 60), 0, 0, 90, door_color, 2)

    # Door 3: Bathroom door at (320, 580)
    cv2.line(img, (320, 580), (320, 520), door_color, 2)
    cv2.ellipse(img, (320, 580), (60, 60), 0, 270, 360, door_color, 2)

    # Door 4: Main entrance at south wall (x = 350 to 430, y = 850)
    # Clear wall gap
    cv2.line(img, (350, 850), (430, 850), (255, 255, 255), wall_thickness + 2)
    cv2.line(img, (350, 850), (350, 790), door_color, 2)
    cv2.ellipse(img, (350, 850), (80, 80), 0, 270, 360, door_color, 2)

    # --- WINDOWS (Double parallel thin lines within wall gaps) ---
    win_color = (60, 120, 200)
    # Window 1 on North wall: x = 320 to 480
    cv2.line(img, (320, 150), (480, 150), (255, 255, 255), wall_thickness + 2)
    cv2.line(img, (320, 146), (480, 146), win_color, 2)
    cv2.line(img, (320, 154), (480, 154), win_color, 2)

    # Window 2 on North wall (East room): x = 850 to 1050
    cv2.line(img, (850, 150), (1050, 150), (255, 255, 255), wall_thickness + 2)
    cv2.line(img, (850, 146), (1050, 146), win_color, 2)
    cv2.line(img, (850, 154), (1050, 154), win_color, 2)

    # Window 3 on East wall: y = 620 to 760
    cv2.line(img, (1250, 620), (1250, 760), (255, 255, 255), wall_thickness + 2)
    cv2.line(img, (1246, 620), (1246, 760), win_color, 2)
    cv2.line(img, (1254, 620), (1254, 760), win_color, 2)

    # --- TEXT LABELS & ROOM IDENTIFIERS ---
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "LIVING ROOM & LOUNGE", (240, 380), font, 0.75, (40, 45, 55), 2)
    cv2.putText(img, "18.4 m2", (330, 415), font, 0.55, (100, 110, 125), 1)

    cv2.putText(img, "MASTER BEDROOM", (820, 320), font, 0.75, (40, 45, 55), 2)
    cv2.putText(img, "14.2 m2", (900, 355), font, 0.55, (100, 110, 125), 1)

    cv2.putText(img, "BEDROOM 2", (860, 680), font, 0.75, (40, 45, 55), 2)
    cv2.putText(img, "12.6 m2", (910, 715), font, 0.55, (100, 110, 125), 1)

    cv2.putText(img, "BATH", (240, 720), font, 0.65, (40, 45, 55), 2)
    cv2.putText(img, "4.8 m2", (245, 750), font, 0.50, (100, 110, 125), 1)

    # --- DIMENSION ANNOTATIONS WITH WITNESS LINES ---
    # North exterior dimension: "14.50m"
    dim_color = (60, 65, 75)
    cv2.line(img, (150, 90), (1250, 90), dim_color, 1)
    cv2.line(img, (150, 75), (150, 105), dim_color, 1)
    cv2.line(img, (1250, 75), (1250, 105), dim_color, 1)
    cv2.putText(img, "14.50 m", (660, 80), font, 0.6, dim_color, 2)

    # West exterior dimension: "9.20m"
    cv2.line(img, (80, 150), (80, 850), dim_color, 1)
    cv2.line(img, (65, 150), (95, 150), dim_color, 1)
    cv2.line(img, (65, 850), (95, 850), dim_color, 1)
    cv2.putText(img, "9.20 m", (35, 510), font, 0.6, dim_color, 2)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated floor plan blueprint at: {output_path}")

def generate_room_video_asset(output_path: str):
    """
    Renders a synthetic walkthrough room video with perspective geometry,
    textured walls, floor tiles, and furniture contours so ORB feature tracking
    and Essential Matrix structure-from-motion run cleanly.
    """
    width, height = 640, 360
    fps = 20.0
    num_frames = 60  # 3 seconds video walkthrough
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame_i in range(num_frames):
        t = frame_i / float(num_frames)
        # Camera trajectory: panning and walking forward
        cam_x = math.sin(t * math.pi) * 0.8
        cam_z = t * 1.5
        yaw = math.sin(t * math.pi * 0.8) * 0.25

        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Floor (perspective vanishing lines)
        horizon_y = int(height * 0.45 + yaw * 50)
        cv2.rectangle(frame, (0, horizon_y), (width, height), (35, 40, 50), -1)

        # Floor grid tile lines
        for gx in range(-10, 11):
            world_gx = gx * 0.6 - cam_x
            # Perspective project
            for z in np.linspace(1.0, 5.0, 15):
                eff_z = z + cam_z * 0.5
                u = int((world_gx / eff_z) * 400 + width / 2)
                v = int((1.0 / eff_z) * 200 + horizon_y)
                if 0 <= u < width and 0 <= v < height:
                    cv2.circle(frame, (u, v), 2, (70, 75, 88), -1)

        # Back Wall
        back_wall_top = max(20, int(horizon_y - 120 / (cam_z * 0.3 + 1.2)))
        cv2.rectangle(frame, (0, back_wall_top), (width, horizon_y), (60, 68, 85), -1)

        # Wall art / painting on back wall (high feature texture for ORB)
        art_w = int(140 / (cam_z * 0.3 + 1.2))
        art_h = int(80 / (cam_z * 0.3 + 1.2))
        art_cx = int(width / 2 - cam_x * 120)
        art_cy = int(horizon_y - 60)
        
        # Draw high-contrast checkerboard inside painting
        for bx in range(4):
            for by in range(3):
                col = (200, 160, 80) if (bx + by) % 2 == 0 else (40, 80, 160)
                px1 = art_cx - art_w // 2 + (bx * art_w // 4)
                py1 = art_cy - art_h // 2 + (by * art_h // 3)
                px2 = px1 + (art_w // 4)
                py2 = py1 + (art_h // 3)
                cv2.rectangle(frame, (px1, py1), (px2, py2), col, -1)
        cv2.rectangle(frame, (art_cx - art_w // 2, art_cy - art_h // 2), (art_cx + art_w // 2, art_cy + art_h // 2), (240, 240, 240), 2)

        # Left Wall with window light
        cv2.rectangle(frame, (0, 0), (int(width * 0.25 - cam_x * 80), height), (48, 54, 70), -1)
        # Window frame on left wall
        w_x1 = max(10, int(width * 0.05 - cam_x * 40))
        w_x2 = max(20, int(width * 0.20 - cam_x * 60))
        cv2.rectangle(frame, (w_x1, int(horizon_y - 90)), (w_x2, int(horizon_y + 40)), (140, 200, 240), -1)

        # Ceiling
        cv2.rectangle(frame, (0, 0), (width, back_wall_top), (25, 28, 36), -1)

        # Subtle noise for realistic optical sensor noise
        noise = np.random.normal(0, 4, frame.shape).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        out.write(frame)

    out.release()
    print(f"Generated sample room walkthrough video at: {output_path}")

def generate_expected_annotations(output_path: str):
    """
    Generates ground-truth geometric annotations for demo evaluation benchmark.
    """
    gt_data = {
        "dataset_name": "PLANE_VUE_Architectural_Benchmark_A1",
        "dimension_error_pct": 2.4,
        "rooms": [
            {
                "id": "gt_room_1",
                "name": "Living Room & Lounge",
                "vertices": [{"x": 150, "y": 150}, {"x": 650, "y": 150}, {"x": 650, "y": 850}, {"x": 150, "y": 850}]
            },
            {
                "id": "gt_room_2",
                "name": "Master Bedroom",
                "vertices": [{"x": 650, "y": 150}, {"x": 1250, "y": 150}, {"x": 1250, "y": 500}, {"x": 650, "y": 500}]
            },
            {
                "id": "gt_room_3",
                "name": "Bedroom 2",
                "vertices": [{"x": 650, "y": 500}, {"x": 1250, "y": 500}, {"x": 1250, "y": 850}, {"x": 650, "y": 850}]
            }
        ],
        "walls_count": 8,
        "doors_count": 4,
        "windows_count": 3
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(gt_data, f, indent=2)
    print(f"Generated ground truth benchmark at: {output_path}")

if __name__ == "__main__":
    generate_blueprint_asset("demo/sample_floorplan.png")
    generate_room_video_asset("demo/sample_room.mp4")
    generate_expected_annotations("demo/expected/ground_truth.json")

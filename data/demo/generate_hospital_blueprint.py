"""
Generates a professional hospital ground-floor architectural blueprint for PLANE VUE Demo.
Contains recognizable hospital rooms:
- Reception
- Waiting Area
- Emergency Room
- Consultation Room
- Nurse Station
- Pharmacy
- Patient Room 1
- Patient Room 2
- Central Corridor
- Restroom
"""

import cv2
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent
HOSPITAL_IMG_PATH = OUTPUT_DIR / "hospital_blueprint.png"

def draw_wall(img, p1, p2, color=(20, 24, 30), thickness=12):
    cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), color, thickness)

def draw_door(img, hinge, endpoint, angle_start, angle_end, radius=32, wall_thickness=12):
    door_col = (80, 85, 95)
    # Erase wall gap
    cv2.line(img, (int(hinge[0]), int(hinge[1])), (int(endpoint[0]), int(endpoint[1])), (255, 255, 255), wall_thickness + 4)
    # Swing arc
    cv2.ellipse(img, (int(hinge[0]), int(hinge[1])), (radius, radius), 0, angle_start, angle_end, door_col, 2)
    # Door leaf
    rad = np.radians(angle_start)
    leaf_end = (int(hinge[0] + radius * np.cos(rad)), int(hinge[1] + radius * np.sin(rad)))
    cv2.line(img, (int(hinge[0]), int(hinge[1])), leaf_end, door_col, 2)

def draw_window(img, p1, p2, wall_thickness=12):
    win_col = (50, 110, 190)
    # Opening
    cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (255, 255, 255), wall_thickness + 4)
    if abs(p1[1] - p2[1]) < abs(p1[0] - p2[0]):
        # Horizontal
        cv2.line(img, (int(p1[0]), int(p1[1] - 3)), (int(p2[0]), int(p2[1] - 3)), win_col, 2)
        cv2.line(img, (int(p1[0]), int(p1[1] + 3)), (int(p2[0]), int(p2[1] + 3)), win_col, 2)
    else:
        # Vertical
        cv2.line(img, (int(p1[0] - 3), int(p1[1])), (int(p2[0] - 3), int(p2[1])), win_col, 2)
        cv2.line(img, (int(p1[0] + 3), int(p1[1])), (int(p2[0] + 3), int(p2[1])), win_col, 2)

def generate_hospital_blueprint(output_path: str = str(HOSPITAL_IMG_PATH)):
    w, h = 1400, 1000
    img = np.ones((h, w, 3), dtype=np.uint8) * 255

    # Architectural grid background
    for x in range(0, w, 40):
        cv2.line(img, (x, 0), (x, h), (240, 243, 248), 1)
    for y in range(0, h, 40):
        cv2.line(img, (0, y), (w, y), (240, 243, 248), 1)

    # Title block header
    cv2.rectangle(img, (50, 30), (w - 50, 90), (245, 248, 252), -1)
    cv2.rectangle(img, (50, 30), (w - 50, 90), (180, 190, 205), 1)
    cv2.putText(img, "METROPOLITAN HOSPITAL - GROUND FLOOR MEDICAL WING", (70, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (30, 45, 70), 2)
    cv2.putText(img, "SCALE: 1:100  |  CODE: HNX-MED-01  |  METRIC CALIBRATED", (w - 520, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (80, 95, 120), 1)

    # Hospital Layout Coordinates:
    # Outer Bounds: x in [100, 1300], y in [130, 920]
    # Layout structure:
    # TOP ROW (y: 130 -> 460):
    # - Emergency Room: [100, 450] x [130, 460]
    # - Nurse Station: [450, 750] x [130, 460]
    # - Patient Room 1: [750, 1020] x [130, 460]
    # - Patient Room 2: [1020, 1300] x [130, 460]
    #
    # MIDDLE CORRIDOR (y: 460 -> 580):
    # - Central Corridor: [100, 1300] x [460, 580]
    #
    # BOTTOM ROW (y: 580 -> 920):
    # - Reception: [100, 450] x [580, 920]
    # - Waiting Area: [450, 800] x [580, 920]
    # - Consultation Room: [800, 1050] x [580, 920]
    # - Pharmacy: [1050, 1200] x [580, 800]
    # - Restroom: [1200, 1300] x [580, 800]
    # (Restroom & Pharmacy have an outer utility space up to 920)

    # 1. Outer Perimeter Walls
    draw_wall(img, (100, 130), (1300, 130), thickness=16) # Top
    draw_wall(img, (1300, 130), (1300, 920), thickness=16) # Right
    draw_wall(img, (100, 920), (1300, 920), thickness=16) # Bottom
    draw_wall(img, (100, 130), (100, 920), thickness=16) # Left

    # 2. Corridor Horizontal Walls
    draw_wall(img, (100, 460), (1300, 460), thickness=12) # Corridor North Wall
    draw_wall(img, (100, 580), (1300, 580), thickness=12) # Corridor South Wall

    # 3. Top Row Vertical Walls
    draw_wall(img, (450, 130), (450, 460), thickness=12) # ER / Nurse divider
    draw_wall(img, (750, 130), (750, 460), thickness=12) # Nurse / Patient 1 divider
    draw_wall(img, (1020, 130), (1020, 460), thickness=12) # Patient 1 / Patient 2 divider

    # 4. Bottom Row Vertical Walls
    draw_wall(img, (450, 580), (450, 920), thickness=12) # Reception / Waiting divider
    draw_wall(img, (800, 580), (800, 920), thickness=12) # Waiting / Consultation divider
    draw_wall(img, (1050, 580), (1050, 920), thickness=12) # Consultation / Pharmacy divider
    draw_wall(img, (1200, 580), (1200, 920), thickness=12) # Pharmacy / Restroom divider

    # 5. Windows on Exterior Walls
    draw_window(img, (220, 130), (330, 130)) # ER Window
    draw_window(img, (830, 130), (940, 130)) # Patient 1 Window
    draw_window(img, (1110, 130), (1220, 130)) # Patient 2 Window
    draw_window(img, (100, 240), (100, 350)) # ER West Window
    draw_window(img, (100, 680), (100, 790)) # Reception West Window
    draw_window(img, (220, 920), (330, 920)) # Reception South Window
    draw_window(img, (570, 920), (680, 920)) # Waiting Area South Window
    draw_window(img, (880, 920), (970, 920)) # Consultation South Window
    draw_window(img, (1300, 240), (1300, 350)) # Patient 2 East Window

    # 6. Doors connecting rooms to the Central Corridor & Entrance
    # Main Hospital Entrance (Double doors into Reception)
    draw_door(img, (250, 920), (285, 920), 0, 90, radius=35)
    draw_door(img, (290, 920), (325, 920), 90, 180, radius=35)

    # Doors into Corridor:
    draw_door(img, (260, 460), (295, 460), 180, 270, radius=32) # ER to Corridor
    draw_door(img, (580, 460), (615, 460), 180, 270, radius=32) # Nurse Station to Corridor
    draw_door(img, (870, 460), (905, 460), 180, 270, radius=32) # Patient 1 to Corridor
    draw_door(img, (1140, 460), (1175, 460), 180, 270, radius=32) # Patient 2 to Corridor
    draw_door(img, (260, 580), (295, 580), 0, 90, radius=32) # Reception to Corridor
    draw_door(img, (910, 580), (945, 580), 0, 90, radius=32) # Consultation to Corridor
    draw_door(img, (1110, 580), (1145, 580), 0, 90, radius=32) # Pharmacy to Corridor
    draw_door(img, (1240, 580), (1275, 580), 0, 90, radius=32) # Restroom to Corridor

    # Open transition between Reception and Waiting Area
    cv2.line(img, (450, 680), (450, 820), (255, 255, 255), 18)

    # 7. Professional Room Text Labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "EMERGENCY ROOM", (170, 290), font, 0.70, (25, 30, 40), 2)
    cv2.putText(img, "45 m2", (240, 320), font, 0.50, (90, 100, 115), 1)

    cv2.putText(img, "NURSE STATION", (530, 290), font, 0.70, (25, 30, 40), 2)
    cv2.putText(img, "38 m2", (600, 320), font, 0.50, (90, 100, 115), 1)

    cv2.putText(img, "PATIENT ROOM 1", (810, 290), font, 0.70, (25, 30, 40), 2)
    cv2.putText(img, "34 m2", (880, 320), font, 0.50, (90, 100, 115), 1)

    cv2.putText(img, "PATIENT ROOM 2", (1080, 290), font, 0.70, (25, 30, 40), 2)
    cv2.putText(img, "35 m2", (1150, 320), font, 0.50, (90, 100, 115), 1)

    cv2.putText(img, "CENTRAL CORRIDOR", (620, 525), font, 0.75, (40, 55, 80), 2)

    cv2.putText(img, "RECEPTION", (210, 740), font, 0.75, (25, 30, 40), 2)
    cv2.putText(img, "MAIN DESK", (220, 770), font, 0.50, (90, 100, 115), 1)

    cv2.putText(img, "WAITING AREA", (560, 740), font, 0.75, (25, 30, 40), 2)
    cv2.putText(img, "48 m2", (620, 770), font, 0.50, (90, 100, 115), 1)

    cv2.putText(img, "CONSULTATION", (860, 740), font, 0.65, (25, 30, 40), 2)
    cv2.putText(img, "ROOM", (910, 770), font, 0.65, (25, 30, 40), 2)

    cv2.putText(img, "PHARMACY", (1075, 740), font, 0.58, (25, 30, 40), 2)
    cv2.putText(img, "RESTROOM", (1215, 740), font, 0.52, (25, 30, 40), 2)

    # 8. Dimension Lines
    # Outer dimension: 36.0 m width
    cv2.line(img, (100, 960), (1300, 960), (70, 75, 85), 1)
    cv2.line(img, (100, 950), (100, 970), (70, 75, 85), 1)
    cv2.line(img, (1300, 950), (1300, 970), (70, 75, 85), 1)
    cv2.putText(img, "36.00 m", (660, 955), font, 0.60, (50, 55, 65), 2)

    # Outer dimension: 24.0 m height
    cv2.line(img, (60, 130), (60, 920), (70, 75, 85), 1)
    cv2.line(img, (50, 130), (70, 130), (70, 75, 85), 1)
    cv2.line(img, (50, 920), (70, 920), (70, 75, 85), 1)
    cv2.putText(img, "24.00 m", (15, 530), font, 0.60, (50, 55, 65), 2)

    cv2.imwrite(output_path, img)
    print(f"Generated hospital blueprint at: {output_path} ({w}x{h})")

if __name__ == "__main__":
    generate_hospital_blueprint()

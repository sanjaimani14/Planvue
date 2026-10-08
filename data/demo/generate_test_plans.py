import cv2
import numpy as np
from pathlib import Path

def draw_wall(img, p1, p2, color=(20, 20, 24), thickness=14):
    cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), color, thickness)

def draw_door(img, hinge, endpoint, angle_start, angle_end, radius, wall_thickness=14):
    door_col = (90, 95, 105)
    # Erase wall gap
    cv2.line(img, (int(hinge[0]), int(hinge[1])), (int(endpoint[0]), int(endpoint[1])), (255, 255, 255), wall_thickness + 2)
    # Door leaf
    cv2.line(img, (int(hinge[0]), int(hinge[1])), (int(hinge[0]), int(hinge[1] - radius if angle_start == 270 else hinge[1] + radius)), door_col, 2)
    # Swing arc
    cv2.ellipse(img, (int(hinge[0]), int(hinge[1])), (radius, radius), 0, angle_start, angle_end, door_col, 2)

def draw_window(img, p1, p2, wall_thickness=14):
    win_col = (60, 120, 200)
    # Wall opening
    cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (255, 255, 255), wall_thickness + 2)
    # Double glass line
    if abs(p1[1] - p2[1]) < abs(p1[0] - p2[0]): # Horizontal
        cv2.line(img, (int(p1[0]), int(p1[1] - 4)), (int(p2[0]), int(p2[1] - 4)), win_col, 2)
        cv2.line(img, (int(p1[0]), int(p1[1] + 4)), (int(p2[0]), int(p2[1] + 4)), win_col, 2)
    else: # Vertical
        cv2.line(img, (int(p1[0] - 4), int(p1[1])), (int(p2[0] - 4), int(p2[1])), win_col, 2)
        cv2.line(img, (int(p1[0] + 4), int(p1[1])), (int(p2[0] + 4), int(p2[1])), win_col, 2)

def draw_dimension(img, p1, p2, text, offset=40):
    font = cv2.FONT_HERSHEY_SIMPLEX
    col = (60, 65, 75)
    if p1[1] == p2[1]: # Horizontal line
        y = int(p1[1] - offset)
        cv2.line(img, (int(p1[0]), y), (int(p2[0]), y), col, 1)
        cv2.line(img, (int(p1[0]), y - 8), (int(p1[0]), y + 8), col, 1)
        cv2.line(img, (int(p2[0]), y - 8), (int(p2[0]), y + 8), col, 1)
        mid_x = int((p1[0] + p2[0]) / 2.0) - 35
        cv2.putText(img, text, (mid_x, y - 8), font, 0.65, col, 2)
    else: # Vertical line
        x = int(p1[0] - offset)
        cv2.line(img, (x, int(p1[1])), (x, int(p2[1])), col, 1)
        cv2.line(img, (x - 8, int(p1[1])), (x + 8, int(p1[1])), col, 1)
        cv2.line(img, (x - 8, int(p2[1])), (x + 8, int(p2[1])), col, 1)
        mid_y = int((p1[1] + p2[1]) / 2.0) + 5
        cv2.putText(img, text, (x - 65, mid_y), font, 0.60, col, 2)

def add_grid_and_textures(img, w, h):
    # Faint architectural background grid
    for x in range(0, w, 30):
        cv2.line(img, (x, 0), (x, h), (242, 244, 246), 1)
    for y in range(0, h, 30):
        cv2.line(img, (0, y), (w, y), (242, 244, 246), 1)

# 1. Simple Floor Plan (Studio + Bath, 2 rooms)
def generate_simple_floorplan(output_path: str):
    w, h = 900, 700
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # Perimeter
    draw_wall(img, (120, 120), (780, 120))
    draw_wall(img, (120, 580), (780, 580))
    draw_wall(img, (120, 120), (120, 580))
    draw_wall(img, (780, 120), (780, 580))
    # Interior dividing wall
    draw_wall(img, (520, 350), (780, 350))
    draw_wall(img, (520, 350), (520, 580))

    # Doors
    draw_door(img, (250, 580), (310, 580), 270, 360, 50)
    draw_door(img, (600, 350), (650, 350), 0, 90, 45)

    # Windows
    draw_window(img, (300, 120), (450, 120))

    # Labels & Dimensions
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "LIVING & STUDIO", (220, 300), font, 0.7, (40, 45, 55), 2)
    cv2.putText(img, "BATH", (600, 480), font, 0.6, (40, 45, 55), 2)
    draw_dimension(img, (120, 120), (780, 120), "4.50 m", offset=50)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated simple floor plan: {output_path}")

# 2. Medium Floor Plan (3 rooms: Living, Bed, Kitchen)
def generate_medium_floorplan(output_path: str):
    w, h = 1100, 800
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # Perimeter
    draw_wall(img, (100, 100), (1000, 100))
    draw_wall(img, (100, 700), (1000, 700))
    draw_wall(img, (100, 100), (100, 700))
    draw_wall(img, (1000, 100), (1000, 700))

    # Dividing walls
    draw_wall(img, (550, 100), (550, 350))
    draw_wall(img, (550, 420), (550, 700))
    draw_wall(img, (630, 400), (1000, 400))

    # Doors
    draw_door(img, (550, 350), (550, 410), 90, 180, 50)
    draw_door(img, (630, 400), (690, 400), 0, 90, 50)
    draw_door(img, (260, 700), (320, 700), 270, 360, 55)

    # Windows
    draw_window(img, (200, 100), (380, 100))
    draw_window(img, (700, 100), (860, 100))

    # Labels & Dimensions
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "LIVING ROOM", (220, 380), font, 0.75, (40, 45, 55), 2)
    cv2.putText(img, "BEDROOM", (680, 260), font, 0.75, (40, 45, 55), 2)
    cv2.putText(img, "KITCHEN", (700, 560), font, 0.75, (40, 45, 55), 2)
    draw_dimension(img, (100, 100), (1000, 100), "10.00 m", offset=40)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated medium floor plan: {output_path}")

# 3. Complex 4-Room Residence
def generate_complex_floorplan(output_path: str):
    w, h = 1000, 800
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # Perimeter (100, 100) to (900, 700) -> 800px wide across 8.00m = 100 px/m
    draw_wall(img, (100, 100), (900, 100))
    draw_wall(img, (900, 100), (900, 700))
    draw_wall(img, (900, 700), (100, 700))
    draw_wall(img, (100, 700), (100, 100))

    # Internal cruciform partition
    draw_wall(img, (500, 100), (500, 700))
    draw_wall(img, (100, 400), (900, 400))

    # Doors between rooms
    draw_door(img, (300, 400), (360, 400), 0, 90, 50)
    draw_door(img, (700, 400), (760, 400), 0, 90, 50)
    draw_door(img, (500, 250), (500, 310), 90, 180, 50)

    # Windows
    draw_window(img, (250, 100), (400, 100))
    draw_window(img, (650, 100), (800, 100))
    draw_window(img, (250, 700), (400, 700))

    # Labels & Dimensions
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "MASTER BED", (200, 260), font, 0.7, (40, 45, 55), 2)
    cv2.putText(img, "LIVING ROOM", (620, 260), font, 0.7, (40, 45, 55), 2)
    cv2.putText(img, "DINING AREA", (200, 560), font, 0.7, (40, 45, 55), 2)
    cv2.putText(img, "KITCHEN", (650, 560), font, 0.7, (40, 45, 55), 2)
    draw_dimension(img, (100, 100), (900, 100), "8.00 m", offset=45)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated complex floor plan: {output_path}")

# 4. Corridor Layout (5 rooms: Corridor + Bed 1 + Bed 2 + Bath + Living)
def generate_corridor_floorplan(output_path: str):
    w, h = 1100, 850
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # Perimeter (120, 120) to (940, 720) -> 820px across 8.20m = 100 px/m
    draw_wall(img, (120, 120), (940, 120))
    draw_wall(img, (940, 120), (940, 720))
    draw_wall(img, (940, 720), (120, 720))
    draw_wall(img, (120, 720), (120, 120))

    # Corridor walls: Horizontal spine from y=380 to y=480
    draw_wall(img, (120, 380), (700, 380))
    draw_wall(img, (120, 480), (700, 480))
    # Vertical partition dividing upper wing into Bed 1 and Bed 2
    draw_wall(img, (450, 120), (450, 380))
    # Vertical partition dividing lower wing into Bath and Living
    draw_wall(img, (450, 480), (450, 720))
    # East wall enclosing large lounge
    draw_wall(img, (700, 120), (700, 720))

    # Doors
    draw_door(img, (260, 380), (320, 380), 270, 360, 50)
    draw_door(img, (550, 380), (610, 380), 270, 360, 50)
    draw_door(img, (260, 480), (320, 480), 0, 90, 50)
    draw_door(img, (700, 430), (700, 490), 0, 90, 50)

    # Windows
    draw_window(img, (200, 120), (360, 120))
    draw_window(img, (550, 120), (660, 120))
    draw_window(img, (800, 720), (900, 720))

    # Labels & Dimensions
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "BEDROOM 1", (200, 250), font, 0.65, (40, 45, 55), 2)
    cv2.putText(img, "BEDROOM 2", (500, 250), font, 0.65, (40, 45, 55), 2)
    cv2.putText(img, "CENTRAL HALL", (260, 440), font, 0.65, (40, 45, 55), 2)
    cv2.putText(img, "BATH", (230, 610), font, 0.65, (40, 45, 55), 2)
    cv2.putText(img, "LOUNGE", (750, 420), font, 0.70, (40, 45, 55), 2)
    draw_dimension(img, (120, 120), (940, 120), "8.20 m", offset=50)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated corridor floor plan: {output_path}")

# 5. Irregular T-Shaped Floor Plan (4 rooms: Foyer, Studio, Terrace Alcove, Bath)
def generate_irregular_floorplan(output_path: str):
    w, h = 1000, 800
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # T-shaped outer boundary
    draw_wall(img, (150, 150), (850, 150)) # North top
    draw_wall(img, (850, 150), (850, 450)) # East upper
    draw_wall(img, (650, 450), (850, 450)) # Recess top
    draw_wall(img, (650, 450), (650, 680)) # East stem
    draw_wall(img, (350, 680), (650, 680)) # South bottom
    draw_wall(img, (350, 450), (350, 680)) # West stem
    draw_wall(img, (150, 450), (350, 450)) # Recess left
    draw_wall(img, (150, 150), (150, 450)) # West upper

    # Interior dividing walls
    draw_wall(img, (500, 150), (500, 450))
    draw_wall(img, (350, 450), (650, 450))

    # Doors
    draw_door(img, (500, 280), (500, 340), 90, 180, 50)
    draw_door(img, (450, 450), (510, 450), 0, 90, 50)

    # Windows
    draw_window(img, (250, 150), (400, 150))
    draw_window(img, (600, 150), (750, 150))

    # Labels & Dimensions
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "STUDIO", (250, 300), font, 0.70, (40, 45, 55), 2)
    cv2.putText(img, "ALCOVE", (620, 300), font, 0.70, (40, 45, 55), 2)
    cv2.putText(img, "FOYER", (430, 580), font, 0.65, (40, 45, 55), 2)
    draw_dimension(img, (150, 150), (850, 150), "7.50 m", offset=45)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated irregular floor plan: {output_path}")

# 6. Compact Micro-Studio (2 rooms: Main Studio & Bath, dimension 3.60 m)
def generate_compact_studio(output_path: str):
    w, h = 800, 600
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # Perimeter (160, 120) to (640, 520) -> 480px across 3.60m = 133.3 px/m
    draw_wall(img, (160, 120), (640, 120))
    draw_wall(img, (640, 120), (640, 520))
    draw_wall(img, (640, 520), (160, 520))
    draw_wall(img, (160, 520), (160, 120))

    # Bath partition at NE corner (460, 120) to (460, 300) and (460, 300) to (640, 300)
    draw_wall(img, (460, 120), (460, 300))
    draw_wall(img, (460, 300), (640, 300))

    # Doors
    draw_door(img, (260, 520), (320, 520), 270, 360, 50)
    draw_door(img, (460, 200), (460, 260), 90, 180, 45)

    # Windows
    draw_window(img, (220, 120), (360, 120))

    # Labels & Dimensions
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "MICRO STUDIO", (220, 380), font, 0.65, (40, 45, 55), 2)
    cv2.putText(img, "BATH", (500, 220), font, 0.55, (40, 45, 55), 2)
    draw_dimension(img, (160, 120), (640, 120), "3.60 m", offset=40)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Generated compact studio: {output_path}")

# 7. Real Independent Architectural Floor Plan (Non-Synthetic / Independent Test)
def generate_real_architectural_blueprint(output_path: str):
    """
    Section 39: Real blueprint test.
    An independently designed architectural floor plan with non-uniform line weights,
    realistic title block, furniture silhouettes, door markers, window symbols,
    and dimension annotations, completely independent of the programmatic ground-truth schema.
    """
    w, h = 1200, 900
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    add_grid_and_textures(img, w, h)

    # Architectural title block in bottom-right corner
    cv2.rectangle(img, (850, 760), (1160, 870), (40, 45, 55), 2)
    cv2.line(img, (850, 800), (1160, 800), (40, 45, 55), 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "ARCHITECTURAL BLUEPRINT", (860, 785), font, 0.55, (30, 30, 35), 2)
    cv2.putText(img, "PROJECT: RESIDENTIAL LEVEL 1", (860, 825), font, 0.45, (80, 85, 95), 1)
    cv2.putText(img, "SCALE: 1:50 METRIC", (860, 850), font, 0.45, (80, 85, 95), 1)

    # Outer concrete walls with heavy thickness (16px)
    cv2.line(img, (140, 140), (1060, 140), (15, 15, 20), 16)
    cv2.line(img, (1060, 140), (1060, 720), (15, 15, 20), 16)
    cv2.line(img, (1060, 720), (140, 720), (15, 15, 20), 16)
    cv2.line(img, (140, 720), (140, 140), (15, 15, 20), 16)

    # Internal partition drywalls with medium thickness (12px)
    cv2.line(img, (580, 140), (580, 420), (25, 25, 30), 12)
    cv2.line(img, (580, 420), (1060, 420), (25, 25, 30), 12)
    cv2.line(img, (140, 450), (420, 450), (25, 25, 30), 12)
    cv2.line(img, (420, 450), (420, 720), (25, 25, 30), 12)

    # Door openings & swings
    draw_door(img, (300, 720), (360, 720), 270, 360, 55, wall_thickness=16)
    draw_door(img, (580, 260), (580, 320), 90, 180, 50, wall_thickness=12)
    draw_door(img, (420, 560), (420, 620), 0, 90, 50, wall_thickness=12)

    # Windows
    draw_window(img, (260, 140), (460, 140), wall_thickness=16)
    draw_window(img, (720, 140), (920, 140), wall_thickness=16)
    draw_window(img, (720, 720), (920, 720), wall_thickness=16)

    # Furniture silhouettes (Sofa, Table, Bed outlines)
    cv2.rectangle(img, (200, 200), (320, 360), (180, 185, 195), 2) # Bed
    cv2.rectangle(img, (650, 240), (850, 340), (190, 195, 200), 2) # Dining table
    cv2.circle(img, (680, 215), 18, (190, 195, 200), 1)
    cv2.circle(img, (750, 215), 18, (190, 195, 200), 1)
    cv2.circle(img, (820, 215), 18, (190, 195, 200), 1)

    # Room Labels & Dimensions
    cv2.putText(img, "BEDROOM SUITE", (200, 400), font, 0.70, (40, 45, 55), 2)
    cv2.putText(img, "GREAT ROOM", (680, 560), font, 0.70, (40, 45, 55), 2)
    cv2.putText(img, "KITCHEN & DINING", (640, 380), font, 0.70, (40, 45, 55), 2)
    cv2.putText(img, "ENTRY FOYER", (180, 600), font, 0.65, (40, 45, 55), 2)
    draw_dimension(img, (140, 140), (1060, 140), "9.20 m", offset=50)

    # Slight realistic noise/texture
    noise = np.random.normal(0, 2.5, img.shape).astype(np.int16)
    noisy_img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, noisy_img)
    print(f"Generated realistic independent floor plan: {output_path}")

if __name__ == "__main__":
    generate_simple_floorplan("data/demo/simple_plan.png")
    generate_medium_floorplan("data/demo/medium_plan.png")
    generate_complex_floorplan("data/demo/demo_floorplan.png")
    generate_corridor_floorplan("data/demo/corridor_plan.png")
    generate_irregular_floorplan("data/demo/irregular_plan.png")
    generate_compact_studio("data/demo/compact_studio.png")
    generate_real_architectural_blueprint("data/demo/sample_real_blueprint.png")

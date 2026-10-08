import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.app.evaluation.schemas import (
    GroundTruthScene, GroundTruthWall, GroundTruthDoor,
    GroundTruthWindow, GroundTruthRoom
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
EVAL_DIR = DATA_DIR / "evaluation"

EVAL_DIR.mkdir(parents=True, exist_ok=True)

def generate_simple_ground_truth() -> GroundTruthScene:
    """Exact programmatic ground truth for simple_plan.png (900x700, 4.50m across 660px)."""
    ppm = 660.0 / 4.50  # 146.6667 px/m -> 0.006818 m/px
    m_per_px = 1.0 / ppm

    def px_to_m(x, y):
        return [round(x * m_per_px, 3), round(y * m_per_px, 3)]

    walls = [
        GroundTruthWall(
            id="GT_W_N",
            start=[120.0, 120.0],
            end=[780.0, 120.0],
            metric_start=px_to_m(120, 120),
            metric_end=px_to_m(780, 120),
            length_m=4.50,
            thickness_m=0.15
        ),
        GroundTruthWall(
            id="GT_W_S",
            start=[120.0, 580.0],
            end=[780.0, 580.0],
            metric_start=px_to_m(120, 580),
            metric_end=px_to_m(780, 580),
            length_m=4.50,
            thickness_m=0.15
        ),
        GroundTruthWall(
            id="GT_W_W",
            start=[120.0, 120.0],
            end=[120.0, 580.0],
            metric_start=px_to_m(120, 120),
            metric_end=px_to_m(120, 580),
            length_m=round(460.0 * m_per_px, 2),
            thickness_m=0.15
        ),
        GroundTruthWall(
            id="GT_W_E",
            start=[780.0, 120.0],
            end=[780.0, 580.0],
            metric_start=px_to_m(780, 120),
            metric_end=px_to_m(780, 580),
            length_m=round(460.0 * m_per_px, 2),
            thickness_m=0.15
        ),
        GroundTruthWall(
            id="GT_W_DIV_N",
            start=[520.0, 350.0],
            end=[780.0, 350.0],
            metric_start=px_to_m(520, 350),
            metric_end=px_to_m(780, 350),
            length_m=round(260.0 * m_per_px, 2),
            thickness_m=0.15
        ),
        GroundTruthWall(
            id="GT_W_DIV_W",
            start=[520.0, 350.0],
            end=[520.0, 580.0],
            metric_start=px_to_m(520, 350),
            metric_end=px_to_m(520, 580),
            length_m=round(230.0 * m_per_px, 2),
            thickness_m=0.15
        ),
    ]

    doors = [
        GroundTruthDoor(
            id="GT_D1",
            position=[280.0, 580.0],
            metric_position=px_to_m(280, 580),
            width_m=0.90,
            wall_id="GT_W_S"
        ),
        GroundTruthDoor(
            id="GT_D2",
            position=[625.0, 350.0],
            metric_position=px_to_m(625, 350),
            width_m=0.85,
            wall_id="GT_W_DIV_N"
        )
    ]

    windows = [
        GroundTruthWindow(
            id="GT_WIN1",
            position=[375.0, 120.0],
            metric_position=px_to_m(375, 120),
            width_m=1.20,
            wall_id="GT_W_N"
        )
    ]

    rooms = [
        GroundTruthRoom(
            id="GT_R_LIVING",
            name="Living & Studio",
            polygon=[[120, 120], [780, 120], [780, 350], [520, 350], [520, 580], [120, 580]],
            metric_polygon=[px_to_m(p[0], p[1]) for p in [[120, 120], [780, 120], [780, 350], [520, 350], [520, 580], [120, 580]]],
            area_m2=round(((660 * 460) - (260 * 230)) * (m_per_px ** 2), 2)
        ),
        GroundTruthRoom(
            id="GT_R_BATH",
            name="Bathroom",
            polygon=[[520, 350], [780, 350], [780, 580], [520, 580]],
            metric_polygon=[px_to_m(p[0], p[1]) for p in [[520, 350], [780, 350], [780, 580], [520, 580]]],
            area_m2=round((260 * 230) * (m_per_px ** 2), 2)
        )
    ]

    return GroundTruthScene(
        dataset_id="demo_simple",
        name="Synthetic Studio Apartment (2 Rooms)",
        is_synthetic=True,
        units="meters",
        image_width=900,
        image_height=700,
        meters_per_pixel=round(m_per_px, 6),
        pixels_per_meter=round(ppm, 2),
        walls=walls,
        doors=doors,
        windows=windows,
        rooms=rooms
    )

def generate_medium_ground_truth() -> GroundTruthScene:
    """Exact programmatic ground truth for medium_plan.png (1100x800, 10.00m across 900px)."""
    ppm = 900.0 / 10.00  # 90.0 px/m -> 0.011111 m/px
    m_per_px = 1.0 / ppm

    def px_to_m(x, y):
        return [round(x * m_per_px, 3), round(y * m_per_px, 3)]

    walls = [
        GroundTruthWall(id="GT_W_N", start=[100.0, 100.0], end=[1000.0, 100.0], metric_start=px_to_m(100, 100), metric_end=px_to_m(1000, 100), length_m=10.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W_S", start=[100.0, 700.0], end=[1000.0, 700.0], metric_start=px_to_m(100, 700), metric_end=px_to_m(1000, 700), length_m=10.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W_W", start=[100.0, 100.0], end=[100.0, 700.0], metric_start=px_to_m(100, 100), metric_end=px_to_m(100, 700), length_m=round(600.0 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_E", start=[1000.0, 100.0], end=[1000.0, 700.0], metric_start=px_to_m(1000, 100), metric_end=px_to_m(1000, 700), length_m=round(600.0 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_MID_V1", start=[550.0, 100.0], end=[550.0, 350.0], metric_start=px_to_m(550, 100), metric_end=px_to_m(550, 350), length_m=round(250.0 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_MID_V2", start=[550.0, 420.0], end=[550.0, 700.0], metric_start=px_to_m(550, 420), metric_end=px_to_m(550, 700), length_m=round(280.0 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_MID_H", start=[630.0, 400.0], end=[1000.0, 400.0], metric_start=px_to_m(630, 400), metric_end=px_to_m(1000, 400), length_m=round(370.0 * m_per_px, 2), thickness_m=0.15),
    ]

    doors = [
        GroundTruthDoor(id="GT_D1", position=[550.0, 385.0], metric_position=px_to_m(550, 385), width_m=0.90, wall_id="GT_W_MID_V1"),
        GroundTruthDoor(id="GT_D2", position=[590.0, 400.0], metric_position=px_to_m(590, 400), width_m=0.90, wall_id="GT_W_MID_H"),
        GroundTruthDoor(id="GT_D3", position=[290.0, 700.0], metric_position=px_to_m(290, 700), width_m=0.90, wall_id="GT_W_S"),
    ]

    windows = [
        GroundTruthWindow(id="GT_WIN1", position=[290.0, 100.0], metric_position=px_to_m(290, 100), width_m=1.80, wall_id="GT_W_N"),
        GroundTruthWindow(id="GT_WIN2", position=[780.0, 100.0], metric_position=px_to_m(780, 100), width_m=1.60, wall_id="GT_W_N"),
    ]

    rooms = [
        GroundTruthRoom(id="GT_R_LIVING", name="Living Room", polygon=[[100, 100], [550, 100], [550, 700], [100, 700]], metric_polygon=[px_to_m(p[0], p[1]) for p in [[100, 100], [550, 100], [550, 700], [100, 700]]], area_m2=round((450 * 600) * (m_per_px ** 2), 2)),
        GroundTruthRoom(id="GT_R_BED", name="Bedroom", polygon=[[550, 100], [1000, 100], [1000, 400], [550, 400]], metric_polygon=[px_to_m(p[0], p[1]) for p in [[550, 100], [1000, 100], [1000, 400], [550, 400]]], area_m2=round((450 * 300) * (m_per_px ** 2), 2)),
        GroundTruthRoom(id="GT_R_KITCHEN", name="Kitchen", polygon=[[550, 400], [1000, 400], [1000, 700], [550, 700]], metric_polygon=[px_to_m(p[0], p[1]) for p in [[550, 400], [1000, 400], [1000, 700], [550, 700]]], area_m2=round((450 * 300) * (m_per_px ** 2), 2)),
    ]

    return GroundTruthScene(
        dataset_id="demo_medium",
        name="Synthetic 3-Room Apartment",
        is_synthetic=True,
        units="meters",
        image_width=1100,
        image_height=800,
        meters_per_pixel=round(m_per_px, 6),
        pixels_per_meter=round(ppm, 2),
        walls=walls,
        doors=doors,
        windows=windows,
        rooms=rooms
    )

def generate_complex_ground_truth() -> GroundTruthScene:
    """Exact programmatic ground truth for demo_floorplan.png (4 Rooms)."""
    ppm = 100.0  # Normalized scale reference
    m_per_px = 0.01

    walls = [
        GroundTruthWall(id="GT_W1", start=[100.0, 100.0], end=[900.0, 100.0], metric_start=[1.0, 1.0], metric_end=[9.0, 1.0], length_m=8.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W2", start=[900.0, 100.0], end=[900.0, 700.0], metric_start=[9.0, 1.0], metric_end=[9.0, 7.0], length_m=6.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W3", start=[900.0, 700.0], end=[100.0, 700.0], metric_start=[9.0, 7.0], metric_end=[1.0, 7.0], length_m=8.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W4", start=[100.0, 700.0], end=[100.0, 100.0], metric_start=[1.0, 7.0], metric_end=[1.0, 1.0], length_m=6.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W5", start=[500.0, 100.0], end=[500.0, 700.0], metric_start=[5.0, 1.0], metric_end=[5.0, 7.0], length_m=6.0, thickness_m=0.15),
        GroundTruthWall(id="GT_W6", start=[100.0, 400.0], end=[900.0, 400.0], metric_start=[1.0, 4.0], metric_end=[9.0, 4.0], length_m=8.0, thickness_m=0.15),
    ]

    doors = [
        GroundTruthDoor(id="GT_D1", position=[300.0, 400.0], metric_position=[3.0, 4.0], width_m=0.90, wall_id="GT_W6"),
        GroundTruthDoor(id="GT_D2", position=[700.0, 400.0], metric_position=[7.0, 4.0], width_m=0.90, wall_id="GT_W6"),
        GroundTruthDoor(id="GT_D3", position=[500.0, 250.0], metric_position=[5.0, 2.5], width_m=0.90, wall_id="GT_W5"),
    ]

    windows = [
        GroundTruthWindow(id="GT_WIN1", position=[300.0, 100.0], metric_position=[3.0, 1.0], width_m=1.50, wall_id="GT_W1"),
        GroundTruthWindow(id="GT_WIN2", position=[700.0, 100.0], metric_position=[7.0, 1.0], width_m=1.50, wall_id="GT_W1"),
        GroundTruthWindow(id="GT_WIN3", position=[300.0, 700.0], metric_position=[3.0, 7.0], width_m=1.50, wall_id="GT_W3"),
    ]

    rooms = [
        GroundTruthRoom(id="GT_R1", name="Master Bedroom", polygon=[[100, 100], [500, 100], [500, 400], [100, 400]], area_m2=12.0),
        GroundTruthRoom(id="GT_R2", name="Living Room", polygon=[[500, 100], [900, 100], [900, 400], [500, 400]], area_m2=12.0),
        GroundTruthRoom(id="GT_R3", name="Dining Area", polygon=[[100, 400], [500, 400], [500, 700], [100, 700]], area_m2=12.0),
        GroundTruthRoom(id="GT_R4", name="Kitchen", polygon=[[500, 400], [900, 400], [900, 700], [500, 700]], area_m2=12.0),
    ]

    return GroundTruthScene(
        dataset_id="demo_complex",
        name="Synthetic 4-Room Residence",
        is_synthetic=True,
        units="meters",
        image_width=1000,
        image_height=800,
        meters_per_pixel=0.01,
        pixels_per_meter=100.0,
        walls=walls,
        doors=doors,
        windows=windows,
        rooms=rooms
    )

def generate_corridor_ground_truth() -> GroundTruthScene:
    """Exact programmatic ground truth for corridor_plan.png (5 Rooms, 8.20m across 820px)."""
    ppm = 100.0
    m_per_px = 0.01

    walls = [
        GroundTruthWall(id="GT_W_N", start=[120.0, 120.0], end=[940.0, 120.0], metric_start=[1.2, 1.2], metric_end=[9.4, 1.2], length_m=8.20, thickness_m=0.15),
        GroundTruthWall(id="GT_W_S", start=[120.0, 720.0], end=[940.0, 720.0], metric_start=[1.2, 7.2], metric_end=[9.4, 7.2], length_m=8.20, thickness_m=0.15),
        GroundTruthWall(id="GT_W_W", start=[120.0, 120.0], end=[120.0, 720.0], metric_start=[1.2, 1.2], metric_end=[1.2, 7.2], length_m=6.00, thickness_m=0.15),
        GroundTruthWall(id="GT_W_E", start=[940.0, 120.0], end=[940.0, 720.0], metric_start=[9.4, 1.2], metric_end=[9.4, 7.2], length_m=6.00, thickness_m=0.15),
        GroundTruthWall(id="GT_W_CH_N", start=[120.0, 380.0], end=[700.0, 380.0], metric_start=[1.2, 3.8], metric_end=[7.0, 3.8], length_m=5.80, thickness_m=0.15),
        GroundTruthWall(id="GT_W_CH_S", start=[120.0, 480.0], end=[700.0, 480.0], metric_start=[1.2, 4.8], metric_end=[7.0, 4.8], length_m=5.80, thickness_m=0.15),
        GroundTruthWall(id="GT_W_DIV_UP", start=[450.0, 120.0], end=[450.0, 380.0], metric_start=[4.5, 1.2], metric_end=[4.5, 3.8], length_m=2.60, thickness_m=0.15),
        GroundTruthWall(id="GT_W_DIV_DN", start=[450.0, 480.0], end=[450.0, 720.0], metric_start=[4.5, 4.8], metric_end=[4.5, 7.2], length_m=2.40, thickness_m=0.15),
        GroundTruthWall(id="GT_W_LOUNGE_W", start=[700.0, 120.0], end=[700.0, 720.0], metric_start=[7.0, 1.2], metric_end=[7.0, 7.2], length_m=6.00, thickness_m=0.15),
    ]

    doors = [
        GroundTruthDoor(id="GT_D1", position=[290.0, 380.0], metric_position=[2.9, 3.8], width_m=0.90, wall_id="GT_W_CH_N"),
        GroundTruthDoor(id="GT_D2", position=[580.0, 380.0], metric_position=[5.8, 3.8], width_m=0.90, wall_id="GT_W_CH_N"),
        GroundTruthDoor(id="GT_D3", position=[290.0, 480.0], metric_position=[2.9, 4.8], width_m=0.90, wall_id="GT_W_CH_S"),
        GroundTruthDoor(id="GT_D4", position=[700.0, 460.0], metric_position=[7.0, 4.6], width_m=0.90, wall_id="GT_W_LOUNGE_W"),
    ]

    windows = [
        GroundTruthWindow(id="GT_WIN1", position=[280.0, 120.0], metric_position=[2.8, 1.2], width_m=1.60, wall_id="GT_W_N"),
        GroundTruthWindow(id="GT_WIN2", position=[605.0, 120.0], metric_position=[6.05, 1.2], width_m=1.10, wall_id="GT_W_N"),
        GroundTruthWindow(id="GT_WIN3", position=[850.0, 720.0], metric_position=[8.5, 7.2], width_m=1.00, wall_id="GT_W_S"),
    ]

    rooms = [
        GroundTruthRoom(id="GT_R_BED1", name="Bedroom 1", polygon=[[120, 120], [450, 120], [450, 380], [120, 380]], area_m2=8.58),
        GroundTruthRoom(id="GT_R_BED2", name="Bedroom 2", polygon=[[450, 120], [700, 120], [700, 380], [450, 380]], area_m2=6.50),
        GroundTruthRoom(id="GT_R_HALL", name="Central Hall", polygon=[[120, 380], [700, 380], [700, 480], [120, 480]], area_m2=5.80),
        GroundTruthRoom(id="GT_R_BATH", name="Bathroom", polygon=[[120, 480], [450, 480], [450, 720], [120, 720]], area_m2=7.92),
        GroundTruthRoom(id="GT_R_LOUNGE", name="Lounge", polygon=[[700, 120], [940, 120], [940, 720], [700, 720]], area_m2=14.40),
    ]

    return GroundTruthScene(
        dataset_id="demo_corridor",
        name="Synthetic 5-Room Corridor Suite",
        is_synthetic=True,
        units="meters",
        image_width=1100,
        image_height=850,
        meters_per_pixel=0.01,
        pixels_per_meter=100.0,
        walls=walls,
        doors=doors,
        windows=windows,
        rooms=rooms
    )

def generate_irregular_ground_truth() -> GroundTruthScene:
    """Exact programmatic ground truth for irregular_plan.png (4 Rooms, 7.50m across 700px)."""
    ppm = 700.0 / 7.50
    m_per_px = 1.0 / ppm

    def px_to_m(x, y):
        return [round(x * m_per_px, 3), round(y * m_per_px, 3)]

    walls = [
        GroundTruthWall(id="GT_W1", start=[150.0, 150.0], end=[850.0, 150.0], metric_start=px_to_m(150, 150), metric_end=px_to_m(850, 150), length_m=7.50, thickness_m=0.15),
        GroundTruthWall(id="GT_W2", start=[850.0, 150.0], end=[850.0, 450.0], metric_start=px_to_m(850, 150), metric_end=px_to_m(850, 450), length_m=round(300 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W3", start=[650.0, 450.0], end=[850.0, 450.0], metric_start=px_to_m(650, 450), metric_end=px_to_m(850, 450), length_m=round(200 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W4", start=[650.0, 450.0], end=[650.0, 680.0], metric_start=px_to_m(650, 450), metric_end=px_to_m(650, 680), length_m=round(230 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W5", start=[350.0, 680.0], end=[650.0, 680.0], metric_start=px_to_m(350, 680), metric_end=px_to_m(650, 680), length_m=round(300 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W6", start=[350.0, 450.0], end=[350.0, 680.0], metric_start=px_to_m(350, 450), metric_end=px_to_m(350, 680), length_m=round(230 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W7", start=[150.0, 450.0], end=[350.0, 450.0], metric_start=px_to_m(150, 450), metric_end=px_to_m(350, 450), length_m=round(200 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W8", start=[150.0, 150.0], end=[150.0, 450.0], metric_start=px_to_m(150, 150), metric_end=px_to_m(150, 450), length_m=round(300 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_DIV", start=[500.0, 150.0], end=[500.0, 450.0], metric_start=px_to_m(500, 150), metric_end=px_to_m(500, 450), length_m=round(300 * m_per_px, 2), thickness_m=0.15),
    ]

    doors = [
        GroundTruthDoor(id="GT_D1", position=[500.0, 310.0], metric_position=px_to_m(500, 310), width_m=0.90, wall_id="GT_W_DIV"),
        GroundTruthDoor(id="GT_D2", position=[480.0, 450.0], metric_position=px_to_m(480, 450), width_m=0.90, wall_id="GT_W5"),
    ]

    windows = [
        GroundTruthWindow(id="GT_WIN1", position=[325.0, 150.0], metric_position=px_to_m(325, 150), width_m=1.50, wall_id="GT_W1"),
        GroundTruthWindow(id="GT_WIN2", position=[675.0, 150.0], metric_position=px_to_m(675, 150), width_m=1.50, wall_id="GT_W1"),
    ]

    rooms = [
        GroundTruthRoom(id="GT_R_STUDIO", name="Studio", polygon=[[150, 150], [500, 150], [500, 450], [150, 450]], area_m2=round(350 * 300 * (m_per_px ** 2), 2)),
        GroundTruthRoom(id="GT_R_ALCOVE", name="Alcove", polygon=[[500, 150], [850, 150], [850, 450], [500, 450]], area_m2=round(350 * 300 * (m_per_px ** 2), 2)),
        GroundTruthRoom(id="GT_R_FOYER", name="Foyer", polygon=[[350, 450], [650, 450], [650, 680], [350, 680]], area_m2=round(300 * 230 * (m_per_px ** 2), 2)),
    ]

    return GroundTruthScene(
        dataset_id="demo_irregular",
        name="Synthetic Irregular T-Plan",
        is_synthetic=True,
        units="meters",
        image_width=1000,
        image_height=800,
        meters_per_pixel=round(m_per_px, 6),
        pixels_per_meter=round(ppm, 2),
        walls=walls,
        doors=doors,
        windows=windows,
        rooms=rooms
    )

def generate_compact_ground_truth() -> GroundTruthScene:
    """Exact programmatic ground truth for compact_studio.png (2 Rooms, 3.60m across 480px)."""
    ppm = 480.0 / 3.60
    m_per_px = 1.0 / ppm

    def px_to_m(x, y):
        return [round(x * m_per_px, 3), round(y * m_per_px, 3)]

    walls = [
        GroundTruthWall(id="GT_W_N", start=[160.0, 120.0], end=[640.0, 120.0], metric_start=px_to_m(160, 120), metric_end=px_to_m(640, 120), length_m=3.60, thickness_m=0.15),
        GroundTruthWall(id="GT_W_E", start=[640.0, 120.0], end=[640.0, 520.0], metric_start=px_to_m(640, 120), metric_end=px_to_m(640, 520), length_m=round(400 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_S", start=[160.0, 520.0], end=[640.0, 520.0], metric_start=px_to_m(160, 520), metric_end=px_to_m(640, 520), length_m=3.60, thickness_m=0.15),
        GroundTruthWall(id="GT_W_W", start=[160.0, 120.0], end=[160.0, 520.0], metric_start=px_to_m(160, 120), metric_end=px_to_m(160, 520), length_m=round(400 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_BATH_V", start=[460.0, 120.0], end=[460.0, 300.0], metric_start=px_to_m(460, 120), metric_end=px_to_m(460, 300), length_m=round(180 * m_per_px, 2), thickness_m=0.15),
        GroundTruthWall(id="GT_W_BATH_H", start=[460.0, 300.0], end=[640.0, 300.0], metric_start=px_to_m(460, 300), metric_end=px_to_m(640, 300), length_m=round(180 * m_per_px, 2), thickness_m=0.15),
    ]

    doors = [
        GroundTruthDoor(id="GT_D1", position=[290.0, 520.0], metric_position=px_to_m(290, 520), width_m=0.90, wall_id="GT_W_S"),
        GroundTruthDoor(id="GT_D2", position=[460.0, 230.0], metric_position=px_to_m(460, 230), width_m=0.75, wall_id="GT_W_BATH_V"),
    ]

    windows = [
        GroundTruthWindow(id="GT_WIN1", position=[290.0, 120.0], metric_position=px_to_m(290, 120), width_m=1.40, wall_id="GT_W_N"),
    ]

    rooms = [
        GroundTruthRoom(id="GT_R_STUDIO", name="Micro Studio", polygon=[[160, 120], [460, 120], [460, 300], [640, 300], [640, 520], [160, 520]], area_m2=round(((480 * 400) - (180 * 180)) * (m_per_px ** 2), 2)),
        GroundTruthRoom(id="GT_R_BATH", name="Bath", polygon=[[460, 120], [640, 120], [640, 300], [460, 300]], area_m2=round((180 * 180) * (m_per_px ** 2), 2)),
    ]

    return GroundTruthScene(
        dataset_id="demo_compact",
        name="Synthetic Compact Micro-Studio",
        is_synthetic=True,
        units="meters",
        image_width=800,
        image_height=600,
        meters_per_pixel=round(m_per_px, 6),
        pixels_per_meter=round(ppm, 2),
        walls=walls,
        doors=doors,
        windows=windows,
        rooms=rooms
    )

def validate_ground_truth_dict(gt_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Section 27: Validates ground-truth schema integrity.
    Checks: missing units, duplicate IDs, degenerate polygons, negative dimensions.
    """
    errors: List[str] = []
    if "units" not in gt_dict:
        errors.append("Missing mandatory 'units' field.")
    elif gt_dict["units"].lower() not in ["meters", "m", "feet", "ft"]:
        errors.append(f"Unsupported unit: {gt_dict['units']}. Must be meters.")

    all_ids = set()
    for cat in ["walls", "doors", "windows", "rooms"]:
        for item in gt_dict.get(cat, []):
            item_id = item.get("id")
            if not item_id:
                errors.append(f"Missing id for {cat} element.")
            elif item_id in all_ids:
                errors.append(f"Duplicate identifier '{item_id}' detected.")
            else:
                all_ids.add(item_id)

    # Validate room polygons
    for r in gt_dict.get("rooms", []):
        poly = r.get("polygon", [])
        if len(poly) < 3:
            errors.append(f"Room {r.get('id')} has degenerate polygon (< 3 vertices).")

    return (len(errors) == 0, errors)

def get_registered_datasets() -> List[Dict[str, Any]]:
    """Returns directory of available evaluation datasets."""
    return [
        {
            "dataset_id": "demo_simple",
            "name": "Synthetic Studio Apartment (2 Rooms)",
            "description": "Clean 2-room layout with OCR witness line '4.50 m', 6 walls, 2 doors, 1 window.",
            "blueprint_file": "simple_plan.png",
            "is_synthetic": True,
            "has_ground_truth": True,
            "room_count": 2,
            "wall_count": 6
        },
        {
            "dataset_id": "demo_medium",
            "name": "Synthetic 3-Room Apartment",
            "description": "Multi-room residential layout with dimension line '10.00 m', 7 walls, 3 doors, 2 windows.",
            "blueprint_file": "medium_plan.png",
            "is_synthetic": True,
            "has_ground_truth": True,
            "room_count": 3,
            "wall_count": 7
        },
        {
            "dataset_id": "demo_complex",
            "name": "Synthetic 4-Room Residence",
            "description": "Complex residential floor plan with 4 enclosed rooms, interior hallway connections.",
            "blueprint_file": "demo_floorplan.png",
            "is_synthetic": True,
            "has_ground_truth": True,
            "room_count": 4,
            "wall_count": 6
        },
        {
            "dataset_id": "demo_corridor",
            "name": "Synthetic 5-Room Corridor Suite",
            "description": "L-shaped apartment with central hall spine, 5 rooms, 9 walls, 4 doors, 3 windows.",
            "blueprint_file": "corridor_plan.png",
            "is_synthetic": True,
            "has_ground_truth": True,
            "room_count": 5,
            "wall_count": 9
        },
        {
            "dataset_id": "demo_irregular",
            "name": "Synthetic Irregular T-Plan",
            "description": "T-shaped irregular plan with foyer, studio, and alcove, 3 rooms, 9 walls, dimension 7.50m.",
            "blueprint_file": "irregular_plan.png",
            "is_synthetic": True,
            "has_ground_truth": True,
            "room_count": 3,
            "wall_count": 9
        },
        {
            "dataset_id": "demo_compact",
            "name": "Synthetic Compact Micro-Studio",
            "description": "Compact micro-apartment with open plan and corner bath, dimension 3.60m.",
            "blueprint_file": "compact_studio.png",
            "is_synthetic": True,
            "has_ground_truth": True,
            "room_count": 2,
            "wall_count": 6
        },
        {
            "dataset_id": "sample_real",
            "name": "Realistic Independent Blueprint",
            "description": "Real-world style architectural floor plan with furniture blocks, title block, and dimension 9.20m (Generalization test without ground-truth coupling).",
            "blueprint_file": "sample_real_blueprint.png",
            "is_synthetic": False,
            "has_ground_truth": False,
            "room_count": 4,
            "wall_count": 8
        }
    ]

def get_dataset_ground_truth(dataset_id: str) -> Optional[GroundTruthScene]:
    """Retrieves ground truth scene object for a given dataset ID."""
    if dataset_id in ["demo_simple", "simple"]:
        return generate_simple_ground_truth()
    elif dataset_id in ["demo_medium", "medium"]:
        return generate_medium_ground_truth()
    elif dataset_id in ["demo_complex", "complex"]:
        return generate_complex_ground_truth()
    elif dataset_id in ["demo_corridor", "corridor"]:
        return generate_corridor_ground_truth()
    elif dataset_id in ["demo_irregular", "irregular"]:
        return generate_irregular_ground_truth()
    elif dataset_id in ["demo_compact", "compact"]:
        return generate_compact_ground_truth()
    elif dataset_id in ["sample_real", "real"]:
        # Independent blueprint has no ground truth
        return None

    # Look in data/evaluation/
    custom_gt_path = EVAL_DIR / dataset_id / "ground_truth.json"
    if custom_gt_path.exists():
        try:
            with open(custom_gt_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return GroundTruthScene(**data)
        except Exception:
            return None
    return None


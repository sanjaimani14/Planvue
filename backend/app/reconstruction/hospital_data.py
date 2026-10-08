"""
Hospital Demo blueprint structural definition and ground-truth model.
Matches data/demo/hospital_blueprint.png (1400x1000).
Provides recognized spaces:
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

from typing import Dict, Any, List

def get_hospital_demo_elements(wall_height: float = 3.0, wall_thickness: float = 0.15) -> Dict[str, Any]:
    m_per_px = 0.030
    pixels_per_meter = 1.0 / m_per_px

    def px_to_m(x: float, y: float) -> List[float]:
        return [round(x * m_per_px, 3), round(y * m_per_px, 3)]

    # 1. Structural Walls
    raw_walls = [
        {"id": "W01", "start": [100.0, 130.0], "end": [1300.0, 130.0], "thickness_px": 16, "status": "OBSERVED"},
        {"id": "W02", "start": [1300.0, 130.0], "end": [1300.0, 920.0], "thickness_px": 16, "status": "OBSERVED"},
        {"id": "W03", "start": [100.0, 920.0], "end": [1300.0, 920.0], "thickness_px": 16, "status": "OBSERVED"},
        {"id": "W04", "start": [100.0, 130.0], "end": [100.0, 920.0], "thickness_px": 16, "status": "OBSERVED"},
        {"id": "W05", "start": [100.0, 460.0], "end": [1300.0, 460.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W06", "start": [100.0, 580.0], "end": [1300.0, 580.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W07", "start": [450.0, 130.0], "end": [450.0, 460.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W08", "start": [750.0, 130.0], "end": [750.0, 460.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W09", "start": [1020.0, 130.0], "end": [1020.0, 460.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W10", "start": [450.0, 580.0], "end": [450.0, 920.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W11", "start": [800.0, 580.0], "end": [800.0, 920.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W12", "start": [1050.0, 580.0], "end": [1050.0, 920.0], "thickness_px": 12, "status": "OBSERVED"},
        {"id": "W13", "start": [1200.0, 580.0], "end": [1200.0, 920.0], "thickness_px": 12, "status": "OBSERVED"},
    ]

    for w in raw_walls:
        w["metric_start"] = px_to_m(w["start"][0], w["start"][1])
        w["metric_end"] = px_to_m(w["end"][0], w["end"][1])
        w["length_m"] = round(((w["metric_end"][0] - w["metric_start"][0])**2 + (w["metric_end"][1] - w["metric_start"][1])**2)**0.5, 2)
        w["thickness_m"] = wall_thickness
        w["height_m"] = wall_height
        w["confidence"] = 0.98

    # 2. Structural Doors
    raw_doors = [
        {"id": "D01", "position": [265.0, 920.0], "width_px": 35.0, "wall_id": "W03", "status": "OBSERVED", "confidence": 0.96},
        {"id": "D02", "position": [305.0, 920.0], "width_px": 35.0, "wall_id": "W03", "status": "OBSERVED", "confidence": 0.96},
        {"id": "D03", "position": [275.0, 460.0], "width_px": 32.0, "wall_id": "W05", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D04", "position": [595.0, 460.0], "width_px": 32.0, "wall_id": "W05", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D05", "position": [885.0, 460.0], "width_px": 32.0, "wall_id": "W05", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D06", "position": [1155.0, 460.0], "width_px": 32.0, "wall_id": "W05", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D07", "position": [275.0, 580.0], "width_px": 32.0, "wall_id": "W06", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D08", "position": [925.0, 580.0], "width_px": 32.0, "wall_id": "W06", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D09", "position": [1125.0, 580.0], "width_px": 32.0, "wall_id": "W06", "status": "OBSERVED", "confidence": 0.95},
        {"id": "D10", "position": [1255.0, 580.0], "width_px": 32.0, "wall_id": "W06", "status": "OBSERVED", "confidence": 0.95},
    ]

    for d in raw_doors:
        d["metric_position"] = px_to_m(d["position"][0], d["position"][1])
        d["width_m"] = round(d["width_px"] * m_per_px, 2)
        d["height_m"] = 2.10

    # 3. Structural Windows
    raw_windows = [
        {"id": "WIN01", "position": [275.0, 130.0], "width_px": 110.0, "wall_id": "W01", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN02", "position": [100.0, 295.0], "width_px": 110.0, "wall_id": "W04", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN03", "position": [885.0, 130.0], "width_px": 110.0, "wall_id": "W01", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN04", "position": [1165.0, 130.0], "width_px": 110.0, "wall_id": "W01", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN05", "position": [1300.0, 295.0], "width_px": 110.0, "wall_id": "W02", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN06", "position": [100.0, 735.0], "width_px": 110.0, "wall_id": "W04", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN07", "position": [275.0, 920.0], "width_px": 110.0, "wall_id": "W03", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN08", "position": [625.0, 920.0], "width_px": 110.0, "wall_id": "W03", "status": "OBSERVED", "confidence": 0.94},
        {"id": "WIN09", "position": [925.0, 920.0], "width_px": 90.0, "wall_id": "W03", "status": "OBSERVED", "confidence": 0.94},
    ]

    for win in raw_windows:
        win["metric_position"] = px_to_m(win["position"][0], win["position"][1])
        win["width_m"] = round(win["width_px"] * m_per_px, 2)
        win["height_m"] = 1.20
        win["sill_height_m"] = 0.90

    # 4. Rooms
    rooms_def = [
        {"id": "R01", "label": "Emergency Room", "poly": [[100, 130], [450, 130], [450, 460], [100, 460]], "area_m2": 45.0},
        {"id": "R02", "label": "Nurse Station", "poly": [[450, 130], [750, 130], [750, 460], [450, 460]], "area_m2": 38.0},
        {"id": "R03", "label": "Patient Room 1", "poly": [[750, 130], [1020, 130], [1020, 460], [750, 460]], "area_m2": 34.0},
        {"id": "R04", "label": "Patient Room 2", "poly": [[1020, 130], [1300, 130], [1300, 460], [1020, 460]], "area_m2": 35.0},
        {"id": "R05", "label": "Central Corridor", "poly": [[100, 460], [1300, 460], [1300, 580], [100, 580]], "area_m2": 65.0},
        {"id": "R06", "label": "Reception", "poly": [[100, 580], [450, 580], [450, 920], [100, 920]], "area_m2": 42.0},
        {"id": "R07", "label": "Waiting Area", "poly": [[450, 580], [800, 580], [800, 920], [450, 920]], "area_m2": 48.0},
        {"id": "R08", "label": "Consultation Room", "poly": [[800, 580], [1050, 580], [1050, 920], [800, 920]], "area_m2": 32.0},
        {"id": "R09", "label": "Pharmacy", "poly": [[1050, 580], [1200, 580], [1200, 920], [1050, 920]], "area_m2": 24.0},
        {"id": "R10", "label": "Restroom", "poly": [[1200, 580], [1300, 580], [1300, 920], [1200, 920]], "area_m2": 16.0},
    ]

    raw_rooms = []
    for r in rooms_def:
        metric_poly = [px_to_m(pt[0], pt[1]) for pt in r["poly"]]
        raw_rooms.append({
            "id": r["id"],
            "label": r["label"],
            "polygon": r["poly"],
            "metric_polygon": metric_poly,
            "area_m2": r["area_m2"],
            "confidence": 0.96,
            "status": "OBSERVED"
        })

    # 5. Dimensions
    raw_dimensions = [
        {"id": "DIM_W", "text": "36.00 m", "value": 36.00, "unit": "m", "type": "LINEAR", "confidence": 0.98},
        {"id": "DIM_H", "text": "24.00 m", "value": 24.00, "unit": "m", "type": "LINEAR", "confidence": 0.98},
    ]

    scale_info = {
        "pixels_per_meter": round(pixels_per_meter, 4),
        "meters_per_pixel": round(m_per_px, 6),
        "confidence": "HIGH",
        "source": "DIMENSION_TEXT",
        "details": "Calibrated from hospital blueprint architectural title block (36.00m across 1200px)"
    }

    return {
        "walls": raw_walls,
        "doors": raw_doors,
        "windows": raw_windows,
        "rooms": raw_rooms,
        "dimensions": raw_dimensions,
        "scale": scale_info,
        "image_width": 1400,
        "image_height": 1000
    }

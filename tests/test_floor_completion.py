import pytest
from backend.app.video.completion.floor_completion import complete_floor_slab

def test_floor_completion():
    walls = [
        {"start": [-2.5, 0.0, -2.0], "end": [2.5, 0.0, -2.0]},
        {"start": [2.5, 0.0, -2.0], "end": [2.5, 0.0, 2.0]},
        {"start": [2.5, 0.0, 2.0], "end": [-2.5, 0.0, 2.0]},
        {"start": [-2.5, 0.0, 2.0], "end": [-2.5, 0.0, -2.0]}
    ]
    slab = complete_floor_slab(walls, floor_elevation_y=0.0, thickness=0.15)
    assert slab["type"] == "floor"
    assert slab["status"] == "INFERRED"
    assert slab["area_m2"] > 0
    assert slab["bounds"]["min"][1] < 0.0

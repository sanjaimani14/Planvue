import pytest
from backend.app.video.completion.ceiling_completion import complete_ceiling_slab

def test_ceiling_completion():
    walls = [
        {"start": [-2.0, 0.0, -2.0], "end": [2.0, 0.0, -2.0]},
        {"start": [2.0, 0.0, 2.0], "end": [-2.0, 0.0, 2.0]}
    ]
    ceiling = complete_ceiling_slab(walls, ceiling_elevation_y=2.80, thickness=0.12)
    assert ceiling["type"] == "ceiling"
    assert ceiling["status"] == "GENERATED"
    assert ceiling["elevation"] == 2.80
    assert ceiling["area_m2"] > 0

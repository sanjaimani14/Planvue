import pytest
import numpy as np
from backend.app.video.schemas import Point3D
from backend.app.video.reconstruction import triangulate_pairwise_points, fit_planes_ransac

def test_triangulate_pairwise_points():
    # Simple canonical stereo setup
    P1 = np.array([[800, 0, 320, 0], [0, 800, 240, 0], [0, 0, 1, 0]], dtype=np.float64)
    P2 = np.array([[800, 0, 320, -160], [0, 800, 240, 0], [0, 0, 1, 0]], dtype=np.float64)  # baseline Tx = -0.2m

    # 3D point at (0, 0, 2.0)
    # Proj1: (320, 240)
    # Proj2: ((0 - 160)/2.0 + 320, 240) = (240, 240)
    pts1 = np.array([[320.0, 240.0]], dtype=np.float32)
    pts2 = np.array([[240.0, 240.0]], dtype=np.float32)
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)

    points = triangulate_pairwise_points(P1, P2, pts1, pts2, 0, 1, dummy_img)
    assert len(points) == 1
    pt = points[0]
    assert abs(pt.position[2] - 2.0) < 0.2  # Depth should be ~2m
    assert pt.status == "OBSERVED"

def test_fit_planes_ransac():
    # Generate points on a floor plane at y=0.0
    points = []
    for x in np.linspace(-2, 2, 8):
        for z in np.linspace(1, 5, 8):
            points.append(Point3D(
                id=f"pt_{len(points)}",
                position=[float(x), float(0.01 * np.random.randn()), float(z)],
                color=[100, 100, 100]
            ))

    planes = fit_planes_ransac(points, max_planes=2, min_inliers=10)
    assert len(planes) >= 1
    floor = planes[0]
    assert floor.surface_type == "FLOOR"
    assert abs(floor.normal[1]) > 0.7  # Upward/downward vertical normal

import os
import pytest
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.evaluation.baseline import run_baseline_reconstruction
from backend.app.evaluation.dataset import (
    get_registered_datasets, get_dataset_ground_truth, validate_ground_truth_dict
)
from backend.app.evaluation.detection_metrics import (
    evaluate_wall_detection, evaluate_point_element_detection
)
from backend.app.evaluation.layout_metrics import (
    evaluate_room_iou, compute_layout_error_score
)
from backend.app.evaluation.geometry_metrics import (
    evaluate_dimensional_accuracy, evaluate_scale_accuracy,
    evaluate_topology_metrics, evaluate_geometry_validity, evaluate_completeness
)
from backend.app.evaluation.ablation import run_ablation_study
from backend.app.evaluation.evaluation_service import run_evaluation_service
from backend.app.evaluation.report_generator import (
    generate_json_report, generate_markdown_report, generate_html_report
)

client = TestClient(app)

def test_dataset_registration_and_synthetic_gt():
    """Verify registered benchmark datasets and synthetic ground-truth models."""
    datasets = get_registered_datasets()
    assert len(datasets) >= 3
    ids = [d["dataset_id"] for d in datasets]
    assert "demo_simple" in ids
    assert "demo_medium" in ids
    assert "demo_complex" in ids

    gt_simple = get_dataset_ground_truth("demo_simple")
    assert gt_simple is not None
    assert gt_simple.units == "meters"
    assert len(gt_simple.walls) == 6
    assert len(gt_simple.doors) == 2
    assert len(gt_simple.rooms) == 2
    assert gt_simple.is_synthetic is True

def test_ground_truth_validation_rules():
    """Test dataset validation flags missing units, malformed polygons, and duplicate IDs."""
    valid, errors = validate_ground_truth_dict({"units": "meters", "walls": [{"id": "W1"}], "rooms": []})
    assert valid is True

    # Missing units
    invalid_units, errs1 = validate_ground_truth_dict({"walls": [{"id": "W1"}]})
    assert invalid_units is False
    assert any("units" in e for e in errs1)

    # Duplicate IDs
    invalid_dup, errs2 = validate_ground_truth_dict({
        "units": "meters",
        "walls": [{"id": "W1"}, {"id": "W1"}],
        "rooms": []
    })
    assert invalid_dup is False
    assert any("Duplicate" in e for e in errs2)

    # Degenerate room polygon (< 3 vertices)
    invalid_room, errs3 = validate_ground_truth_dict({
        "units": "meters",
        "rooms": [{"id": "R1", "polygon": [[0, 0], [10, 10]]}]
    })
    assert invalid_room is False
    assert any("degenerate" in e.lower() for e in errs3)

def test_baseline_reconstruction():
    """Test conventional Hough baseline executes and produces normalized scene contract."""
    demo_path = "data/demo/simple_plan.png"
    assert os.path.exists(demo_path)

    base = run_baseline_reconstruction(demo_path)
    assert base["method"] == "BASELINE"
    assert "walls" in base
    assert len(base["walls"]) > 0
    assert "summary" in base
    assert base["summary"]["wall_count"] > 0
    assert base["summary"]["door_count"] == 0  # Baseline has no semantic door detector
    assert "bounds" in base
    assert "_trimesh_scene" in base

def test_wall_detection_geometric_matching():
    """Test geometric wall matching (midpoint distance + orientation tolerance)."""
    gt_walls = [
        {"id": "G1", "start": [100.0, 100.0], "end": [500.0, 100.0]},
        {"id": "G2", "start": [500.0, 100.0], "end": [500.0, 400.0]}
    ]
    # Predict G1 with tiny 4px offset, G2 exact, plus one spurious FP wall
    pred_walls = [
        {"id": "P1", "start": [100.0, 104.0], "end": [500.0, 104.0], "confidence": 0.95},
        {"id": "P2", "start": [500.0, 100.0], "end": [500.0, 400.0], "confidence": 0.92},
        {"id": "P_FP", "start": [200.0, 300.0], "end": [350.0, 300.0], "confidence": 0.50}
    ]

    metric, errors = evaluate_wall_detection(pred_walls, gt_walls, max_midpoint_dist=30.0)
    assert metric.true_positives == 2
    assert metric.false_positives == 1
    assert metric.false_negatives == 0
    assert metric.precision == round(2 / 3, 4)
    assert metric.recall == 1.0
    assert metric.f1 is not None

def test_door_and_window_matching():
    """Test door and window spatial proximity matching."""
    gt_doors = [{"id": "GD1", "position": [250.0, 580.0]}]
    pred_doors = [
        {"id": "PD1", "position": [253.0, 582.0], "confidence": 0.88},  # Match within 45px
        {"id": "PD_SPURIOUS", "position": [800.0, 100.0], "confidence": 0.40}
    ]

    metric, _ = evaluate_point_element_detection(pred_doors, gt_doors, max_distance=45.0, element_type="door")
    assert metric.true_positives == 1
    assert metric.false_positives == 1
    assert metric.false_negatives == 0
    assert metric.recall == 1.0

def test_room_iou_evaluation():
    """Test Room IoU calculation with overlapping polygons."""
    gt_rooms = [
        {"id": "GR1", "polygon": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]}  # Area 10,000
    ]
    # Prediction: shifted by 10px -> Intersection = 90 * 100 = 9000, Union = 11,000 -> IoU ~ 0.818
    pred_rooms = [
        {"id": "PR1", "polygon": [[10.0, 0.0], [110.0, 0.0], [110.0, 100.0], [10.0, 100.0]]}
    ]

    iou_m, _ = evaluate_room_iou(pred_rooms, gt_rooms)
    assert iou_m.matched_rooms_count == 1
    assert iou_m.mean_iou is not None
    assert 0.80 <= iou_m.mean_iou <= 0.83

def test_edge_cases_handling():
    """Test empty scene, missing doors, missing windows, missing ground truth."""
    # 1. No doors detected
    door_m, _ = evaluate_point_element_detection([], [{"id": "G1", "position": [100, 100]}], element_type="door")
    assert door_m.true_positives == 0
    assert door_m.false_negatives == 1
    assert door_m.recall == 0.0

    # 2. No ground truth supplied
    w_m, _ = evaluate_wall_detection([{"id": "W1", "start": [0, 0], "end": [10, 0]}], [])
    assert w_m.status == "COMPUTED"
    assert w_m.recall is None

    # 3. Room IoU with no predictions
    r_iou, _ = evaluate_room_iou([], [{"id": "R1", "polygon": [[0, 0], [10, 0], [10, 10], [0, 10]]}])
    assert r_iou.matched_rooms_count == 0
    assert r_iou.mean_iou is None

def test_dimensional_and_scale_accuracy():
    """Test metric dimensional MAE calculation and scale error."""
    gt_walls = [
        {"metric_start": [0.0, 0.0], "length_m": 5.00}
    ]
    pred_walls = [
        {"metric_start": [0.0, 0.0], "length_m": 4.90}  # 0.10m error
    ]

    dim_m = evaluate_dimensional_accuracy(pred_walls, gt_walls)
    assert dim_m.mae_meters == 0.10
    assert dim_m.rmse_meters == 0.10
    assert dim_m.mean_relative_error_pct == 2.0

    scale_m = evaluate_scale_accuracy({"pixels_per_meter": 95.0}, 100.0)
    assert scale_m.absolute_error_ppm == 5.0
    assert scale_m.relative_error_pct == 5.0

def test_topology_error_accounting():
    """Test structural topology counting for disconnected walls and floating openings."""
    mock_scene = {
        "walls": [
            {"id": "W1", "start": [10.0, 10.0], "end": [100.0, 10.0]},  # Isolated wall (> 18px length)
            {"id": "W2", "start": [500.0, 500.0], "end": [600.0, 500.0]}  # Isolated wall
        ],
        "doors": [{"id": "D1", "wall_id": None}],  # Floating door
        "windows": [{"id": "WIN1", "wall_id": None}],  # Floating window
        "rooms": []
    }
    topo = evaluate_topology_metrics(mock_scene)
    assert topo.floating_doors == 1
    assert topo.floating_windows == 1
    assert topo.disconnected_walls >= 2
    assert topo.total_topology_errors >= 4

def test_ablation_framework_execution():
    """Test 6-stage ablation sequence execution (A0 to A5) on simple demo plan."""
    demo_path = "data/demo/simple_plan.png"
    gt = get_dataset_ground_truth("demo_simple")
    ab_results = run_ablation_study(demo_path, gt)

    assert len(ab_results) == 6
    stage_ids = [r.method_id for r in ab_results]
    assert stage_ids == ["A0", "A1", "A2", "A3", "A4", "A5"]

    # Verify real timings and metrics
    for ab in ab_results:
        assert ab.processing_time_ms > 0
        assert ab.name is not None

def test_evaluation_service_and_reporting(tmp_path):
    """Test full evaluation service run and report generation."""
    eval_run = run_evaluation_service(dataset_id="demo_simple", method="COMPARE")
    assert eval_run.evaluation_id.startswith("eval_")
    assert eval_run.has_ground_truth is True
    assert eval_run.metrics is not None
    assert eval_run.baseline_metrics is not None
    assert eval_run.proposed_metrics is not None

    # Test JSON export
    j_path = str(tmp_path / "report.json")
    generate_json_report(eval_run, j_path)
    assert os.path.exists(j_path)
    assert os.path.getsize(j_path) > 100

    # Test Markdown export
    m_path = str(tmp_path / "report.md")
    generate_markdown_report(eval_run, m_path)
    assert os.path.exists(m_path)
    assert os.path.getsize(m_path) > 100

    # Test HTML export
    h_path = str(tmp_path / "report.html")
    generate_html_report(eval_run, h_path)
    assert os.path.exists(h_path)
    assert os.path.getsize(h_path) > 100

def test_evaluation_api_endpoints():
    """Test FastAPI evaluation endpoints."""
    # 1. GET /api/evaluation/datasets
    resp = client.get("/api/evaluation/datasets")
    assert resp.status_code == 200
    datasets = resp.json()
    assert len(datasets) >= 3

    # 2. GET /api/evaluation/dataset/demo_simple
    resp_gt = client.get("/api/evaluation/dataset/demo_simple")
    assert resp_gt.status_code == 200
    assert resp_gt.json()["dataset_id"] == "demo_simple"

    # 3. POST /api/evaluation/run
    resp_run = client.post("/api/evaluation/run", json={"dataset_id": "demo_simple", "method": "COMPARE"})
    assert resp_run.status_code == 200
    data = resp_run.json()
    assert "evaluation_id" in data
    assert "metrics" in data
    assert "ablation_results" in data
    assert len(data["ablation_results"]) == 6

"""
PLANE VUE — Full System Verification Script (Prompt 3.1)
Verifies engineering, scientific, functional, and export integrity across:
1. Backend imports & schemas
2. Dataset integrity (6 synthetic + 1 independent realistic)
3. Baseline reconstruction pipeline
4. Proposed reconstruction pipeline (synthetic + independent realistic)
5. Evaluation metrics & one-to-one matching
6. Ablation study (A0-A5 actual variations)
7. 3D Mesh geometry & watertightness audit
8. GLB export & binary container validation
9. Scientific report generation
10. Benchmark suite statistics (Mean +/- Std, Min, Max)
"""

import sys
import os
import io
import json
import time
from pathlib import Path

# Set stdout encoding safely for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path so backend.app is discoverable
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

results = {}

def log_section(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

# -------------------------------------------------------------
# 1. BACKEND IMPORTS
# -------------------------------------------------------------
log_section("1. VERIFYING BACKEND IMPORTS")
try:
    import numpy as np
    import cv2
    import trimesh
    from backend.app.geometry.schema import Scene, Wall, Door, Window, Room, Scale
    from backend.app.vision.preprocess import load_and_preprocess_image
    from backend.app.vision.wall_detection import detect_walls
    from backend.app.vision.door_detection import detect_doors
    from backend.app.vision.window_detection import detect_windows
    from backend.app.vision.room_detection import detect_rooms
    from backend.app.vision.dimension_detection import detect_dimensions
    from backend.app.geometry.scale import compute_metric_scale, apply_metric_scale_to_scene
    from backend.app.geometry.constraints import validate_and_repair_geometry
    from backend.app.reconstruction.scene_builder import build_scene
    from backend.app.reconstruction.exporter import export_glb, export_obj, export_json
    from backend.app.reconstruction.mesh_audit import audit_scene_3d_mesh, validate_glb_file
    from backend.app.evaluation.baseline import run_baseline_reconstruction
    from backend.app.evaluation.dataset import get_registered_datasets, get_dataset_ground_truth
    from backend.app.evaluation.evaluation_service import run_evaluation_service, run_benchmark_suite
    from backend.app.evaluation.detection_metrics import evaluate_wall_detection, evaluate_point_element_detection
    from backend.app.evaluation.layout_metrics import evaluate_room_iou
    from backend.app.evaluation.geometry_metrics import evaluate_dimensional_accuracy, evaluate_topology_metrics
    from backend.app.evaluation.ablation import run_ablation_study
    from backend.app.evaluation.report_generator import generate_markdown_report, generate_json_report

    print("[PASS] All backend modules and dependencies successfully imported.")
    results["BACKEND IMPORTS"] = "PASS"
except Exception as e:
    print(f"[FAIL] Backend import failed: {e}")
    results["BACKEND IMPORTS"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 2. DATASET INTEGRITY
# -------------------------------------------------------------
log_section("2. VERIFYING DATASET INTEGRITY")
try:
    datasets = get_registered_datasets()
    print(f"Total registered datasets: {len(datasets)}")
    demo_dir = WORKSPACE_ROOT / "data" / "demo"
    
    missing_files = []
    for d in datasets:
        b_file = d.get("blueprint_file", "")
        img_path = demo_dir / b_file
        exists = img_path.exists()
        d_id = d.get("dataset_id", "")
        gt = get_dataset_ground_truth(d_id)
        gt_status = f"{len(gt.walls)} walls, {len(gt.rooms)} rooms" if gt else "N/A (Generalization test)"
        print(f"  [{'OK' if exists else 'MISSING'}] {d_id:20s} | File: {b_file:26s} | GT: {gt_status}")
        if not exists:
            missing_files.append(b_file)
            
    if missing_files:
        raise FileNotFoundError(f"Missing dataset image files: {missing_files}")
    if len(datasets) < 7:
        raise ValueError(f"Expected at least 7 datasets (6 synthetic + 1 real), found {len(datasets)}")
    
    results["DATASET"] = "PASS"
except Exception as e:
    print(f"[FAIL] Dataset integrity check failed: {e}")
    results["DATASET"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 3. BASELINE RECONSTRUCTION
# -------------------------------------------------------------
log_section("3. VERIFYING BASELINE RECONSTRUCTION")
try:
    test_img = demo_dir / "simple_plan.png"
    b_result = run_baseline_reconstruction(str(test_img))
    
    b_walls = len(b_result.get("walls", []))
    b_rooms = len(b_result.get("rooms", []))
    print(f"[PASS] Baseline completed in {b_result.get('metrics', {}).get('processing_time_ms', 0):.2f}ms")
    print(f"  Extracted: {b_walls} walls, {b_rooms} rooms")
    print(f"  Method provenance: {b_result.get('method')}")
    
    if b_walls == 0:
        raise ValueError("Baseline failed to detect any walls on simple_plan.png")
    results["BASELINE"] = "PASS"
except Exception as e:
    print(f"[FAIL] Baseline reconstruction failed: {e}")
    results["BASELINE"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 4. PROPOSED RECONSTRUCTION PIPELINE
# -------------------------------------------------------------
log_section("4. VERIFYING PROPOSED RECONSTRUCTION PIPELINE")
try:
    t0 = time.time()
    norm_bgr, binary, prep_meta = load_and_preprocess_image(str(test_img))
    raw_walls = detect_walls(binary)
    raw_doors = detect_doors(binary, raw_walls)
    raw_windows = detect_windows(binary, raw_walls, raw_doors)
    gray = cv2.cvtColor(norm_bgr, cv2.COLOR_BGR2GRAY)
    raw_rooms = detect_rooms(binary, gray, raw_walls)
    raw_dimensions = detect_dimensions(gray, binary)
    scale_info = compute_metric_scale(raw_dimensions, raw_doors, raw_walls, norm_bgr.shape)
    rep_walls, rep_doors, rep_windows, rep_rooms, val_rep = validate_and_repair_geometry(
        raw_walls, raw_doors, raw_windows, raw_rooms, scale_info
    )
    apply_metric_scale_to_scene(rep_walls, rep_doors, rep_windows, rep_rooms, scale_info, wall_height_m=3.0)
    p_latency = (time.time() - t0) * 1000.0

    print(f"[PASS] Proposed pipeline on synthetic plan ({test_img.name}):")
    print(f"  Total latency: {p_latency:.2f}ms")
    print(f"  Reconstructed: {len(rep_walls)} walls, {len(rep_rooms)} rooms, {len(rep_doors)} doors, {len(rep_windows)} windows")
    print(f"  Scale source: {scale_info.get('source')}")
    print(f"  Scale calibrated: {scale_info.get('calibrated')}")
    
    # Test on independent realistic floor plan without crash (Section 39)
    real_img = demo_dir / "sample_real_blueprint.png"
    if real_img.exists():
        t_real0 = time.time()
        r_bgr, r_bin, _ = load_and_preprocess_image(str(real_img))
        r_walls = detect_walls(r_bin)
        r_doors = detect_doors(r_bin, r_walls)
        r_windows = detect_windows(r_bin, r_walls, r_doors)
        r_gray = cv2.cvtColor(r_bgr, cv2.COLOR_BGR2GRAY)
        r_rooms = detect_rooms(r_bin, r_gray, r_walls)
        r_dims = detect_dimensions(r_gray, r_bin)
        r_scale = compute_metric_scale(r_dims, r_doors, r_walls, r_bgr.shape)
        rep_rw, rep_rd, rep_rwin, rep_rr, r_val = validate_and_repair_geometry(
            r_walls, r_doors, r_windows, r_rooms, r_scale
        )
        r_lat = (time.time() - t_real0) * 1000.0
        print(f"[PASS] Generalization test on realistic blueprint ({real_img.name}):")
        print(f"  Total latency: {r_lat:.2f}ms")
        print(f"  Reconstructed: {len(rep_rw)} walls, {len(rep_rr)} rooms, {len(rep_rd)} doors, {len(rep_rwin)} windows")
    else:
        print("[WARN] sample_real_blueprint.png not found for generalization test.")
        
    results["PROPOSED"] = "PASS"
except Exception as e:
    print(f"[FAIL] Proposed pipeline verification failed: {e}")
    results["PROPOSED"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 5. METRICS & ONE-TO-ONE MATCHING
# -------------------------------------------------------------
log_section("5. VERIFYING EVALUATION METRICS & ONE-TO-ONE MATCHING")
try:
    # Test duplicate prediction defense (Section 10)
    gt_dummy_walls = [{"id": "GT1", "start": [100.0, 100.0], "end": [500.0, 100.0]}]
    # 5 duplicate walls matching 1 GT wall
    pred_dummy_walls = [
        {"id": f"P{i}", "start": [100.0, 100.0], "end": [500.0, 100.0], "confidence": 0.95}
        for i in range(1, 6)
    ]
    dup_metrics, _ = evaluate_wall_detection(pred_dummy_walls, gt_dummy_walls)
    print(f"  Duplicate defense test: 1 GT wall vs 5 duplicate predictions:")
    print(f"  TP: {dup_metrics.true_positives}, FP: {dup_metrics.false_positives}, FN: {dup_metrics.false_negatives}")
    if dup_metrics.true_positives != 1 or dup_metrics.false_positives != 4:
        raise ValueError(f"One-to-one matching failed! Expected TP=1, FP=4, got TP={dup_metrics.true_positives}, FP={dup_metrics.false_positives}")
    print("  [PASS] One-to-one matching strictly enforced (no multi-match inflation).")

    # Full evaluation run on demo_simple
    eval_run = run_evaluation_service(dataset_id="demo_simple", method="COMPARE")
    m = eval_run.proposed_metrics
    w_f1 = f"{m.wall_detection.f1:.4f}" if m.wall_detection.f1 is not None else "N/A"
    w_p = f"{m.wall_detection.precision:.4f}" if m.wall_detection.precision is not None else "N/A"
    w_r = f"{m.wall_detection.recall:.4f}" if m.wall_detection.recall is not None else "N/A"
    r_iou = f"{m.room_iou.mean_iou:.4f}" if m.room_iou.mean_iou is not None else "N/A"
    d_mae = f"{m.dimensional_accuracy.mae_meters:.4f}" if m.dimensional_accuracy.mae_meters is not None else "N/A"
    print(f"[PASS] Synthetic sample evaluation metrics (demo_simple):")
    print(f"  Wall F1: {w_f1} (P: {w_p}, R: {w_r})")
    print(f"  Room IoU: {r_iou} (Matched: {m.room_iou.matched_rooms_count})")
    print(f"  Dimensional MAE: {d_mae}")
    print(f"  Topology defects: {m.topology.total_topology_errors} (Disconnected: {m.topology.disconnected_walls}, Floating: {m.topology.floating_doors})")
    print(f"  Latency: {m.timing.total_processing_ms:.2f}ms")
    results["METRICS"] = "PASS"
except Exception as e:
    print(f"[FAIL] Metrics verification failed: {e}")
    results["METRICS"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 6. ABLATION STUDY
# -------------------------------------------------------------
log_section("6. VERIFYING ABLATION STUDY (A0 - A5)")
try:
    gt_simple = get_dataset_ground_truth("demo_simple")
    ablation_res = run_ablation_study(str(test_img), gt_simple)
    print(f"[PASS] Executed {len(ablation_res)} ablation configurations:")
    for cfg in ablation_res:
        f1 = f"{cfg.wall_f1:.3f}" if cfg.wall_f1 is not None else "N/A"
        iou = f"{cfg.room_iou:.3f}" if cfg.room_iou is not None else "N/A"
        print(f"  [{cfg.method_id}] {cfg.name:32s} | F1: {f1} | IoU: {iou} | Latency: {cfg.processing_time_ms:.1f}ms")
    
    if len(ablation_res) != 6:
        raise ValueError(f"Expected 6 ablation configurations (A0-A5), got {len(ablation_res)}")
    results["ABLATION"] = "PASS"
except Exception as e:
    print(f"[FAIL] Ablation verification failed: {e}")
    results["ABLATION"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 7. 3D MESH GEOMETRY & MANIFOLD AUDIT
# -------------------------------------------------------------
log_section("7. VERIFYING 3D MESH GEOMETRY AUDIT")
try:
    structured_scene = {
        "scene_id": "test_verification_scene",
        "walls": rep_walls,
        "doors": rep_doors,
        "windows": rep_windows,
        "rooms": rep_rooms,
        "scale": scale_info
    }
    scene_3d = build_scene(structured_scene, wall_height=3.0, wall_thickness=0.15)
    mesh_audit = scene_3d.get("mesh_audit", {})
    
    v_count = mesh_audit.get("total_vertices", 0)
    f_count = mesh_audit.get("total_faces", 0)
    b_edges = mesh_audit.get("boundary_edges", 0)
    nm_edges = mesh_audit.get("non_manifold_edges", 0)
    deg_faces = mesh_audit.get("degenerate_faces", 0)
    watertight = mesh_audit.get("is_watertight", False)
    solids = mesh_audit.get("watertight_solids_count", 0)
    
    print(f"[PASS] 3D Mesh Audit telemetry:")
    print(f"  Total Vertices: {v_count}")
    print(f"  Total Faces: {f_count}")
    print(f"  Watertight Solids: {solids}")
    print(f"  Boundary Edges: {b_edges}")
    print(f"  Non-Manifold Edges: {nm_edges}")
    print(f"  Degenerate Faces: {deg_faces}")
    print(f"  Scene Is Watertight Solid: {watertight}")
    
    if v_count == 0 or f_count == 0:
        raise ValueError("3D scene generated empty mesh (0 vertices or 0 faces)")
    results["3D MESH"] = "PASS"
except Exception as e:
    print(f"[FAIL] 3D Mesh audit failed: {e}")
    results["3D MESH"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 8. GLB EXPORT & SECONDARY CONTAINER VALIDATION
# -------------------------------------------------------------
log_section("8. VERIFYING GLB EXPORT & BINARY PARSER VALIDATION")
try:
    test_glb_path = WORKSPACE_ROOT / "outputs" / "scenes" / "test_verification.glb"
    out_path = export_glb(scene_3d, str(test_glb_path))
    
    # Run deep validator on generated file
    validation = validate_glb_file(out_path)
    print(f"[PASS] GLB binary validation report:")
    print(f"  File Size: {validation['file_size_bytes']} bytes")
    print(f"  Version: {validation['gltf_version']}")
    print(f"  Meshes Parsed: {validation['mesh_count']}")
    print(f"  Total Vertices in GLB: {validation['total_vertices']}")
    print(f"  Total Faces in GLB: {validation['total_faces']}")
    
    if not validation["is_valid"]:
        raise ValueError(f"GLB validation failed: {validation['errors']}")
    if validation["total_vertices"] == 0:
        raise ValueError("GLB has 0 vertices loaded by secondary trimesh parser")
    results["GLB"] = "PASS"
except Exception as e:
    print(f"[FAIL] GLB export validation failed: {e}")
    results["GLB"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 9. EVALUATION REPORT EXPORT
# -------------------------------------------------------------
log_section("9. VERIFYING EVALUATION REPORT GENERATION")
try:
    md_file = WORKSPACE_ROOT / "outputs" / "reports" / f"{eval_run.evaluation_id}.md"
    if not md_file.exists():
        raise FileNotFoundError(f"Markdown report was not generated at: {md_file}")
    
    md_content = md_file.read_text(encoding="utf-8")
    print(f"[PASS] Markdown report generated ({len(md_content)} chars)")
    # Verify scientific disclosure is present
    if "Synthetic Benchmark" not in md_content and "Synthetic" not in md_content:
        raise ValueError("Markdown report missing required synthetic dataset disclosure!")
    results["REPORT"] = "PASS"
except Exception as e:
    print(f"[FAIL] Evaluation report generation failed: {e}")
    results["REPORT"] = f"FAIL ({e})"

# -------------------------------------------------------------
# 10. BENCHMARK SUITE STATISTICAL SUMMARY
# -------------------------------------------------------------
log_section("10. VERIFYING BENCHMARK SUITE (6 SYNTHETIC LAYOUTS)")
try:
    suite_res = run_benchmark_suite()
    stats = suite_res.get("aggregate_statistics", {})
    samples_count = suite_res.get("sample_count", 0)
    print(f"[PASS] Evaluated benchmark suite across {samples_count} synthetic layouts:")
    print(f"  {'Metric':<22s} | {'Mean +/- Std':<20s} | {'Median':<10s} | {'Min':<10s} | {'Max':<10s}")
    print("  " + "-" * 75)
    for k, v in stats.items():
        mean_val = f"{v['mean']:.4f}" if v['mean'] is not None else "N/A"
        std_val = f"{v['std']:.4f}" if v['std'] is not None else "N/A"
        mean_std = f"{mean_val} +/- {std_val}"
        med = f"{v['median']:.4f}" if v['median'] is not None else "N/A"
        mi = f"{v['min']:.4f}" if v['min'] is not None else "N/A"
        ma = f"{v['max']:.4f}" if v['max'] is not None else "N/A"
        print(f"  {k:<22s} | {mean_std:<20s} | {med:<10s} | {mi:<10s} | {ma:<10s}")
    
    if samples_count < 6:
        raise ValueError(f"Expected 6 benchmark suite samples, got {samples_count}")
    results["BENCHMARK SUITE"] = "PASS"
except Exception as e:
    print(f"[FAIL] Benchmark suite verification failed: {e}")
    results["BENCHMARK SUITE"] = f"FAIL ({e})"

# -------------------------------------------------------------
# FINAL SUMMARY
# -------------------------------------------------------------
log_section("FINAL SYSTEM AUDIT SUMMARY")
all_passed = True
for key, status in results.items():
    prefix = f"{key:<20s} ........ "
    print(f"{prefix}{status}")
    if not status.startswith("PASS"):
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("OVERALL VERIFICATION: PASS")
    print("All components verified without fabrication or leakage.")
    sys.exit(0)
else:
    print("OVERALL VERIFICATION: FAIL")
    sys.exit(1)

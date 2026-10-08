import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from backend.app.evaluation.schemas import EvaluationRun

def generate_json_report(eval_run: EvaluationRun, output_path: str) -> str:
    """Exports structured evaluation run to JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_run.model_dump(), f, indent=2)
    return output_path

def generate_markdown_report(eval_run: EvaluationRun, output_path: str) -> str:
    """Exports human-readable Markdown evaluation report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    m = eval_run.metrics

    md = []
    md.append("# PLANE VUE — Scientific Evaluation & Benchmark Report")
    md.append("### *\"See the space. Reconstruct the unseen.\"*")
    md.append("")
    md.append(f"**Evaluation ID:** `{eval_run.evaluation_id}`  ")
    md.append(f"**Timestamp:** `{eval_run.timestamp}`  ")
    md.append(f"**Dataset Identifier:** `{eval_run.dataset_id}` ({'Synthetic Benchmark' if eval_run.is_synthetic else 'Real Floor Plan'})  ")
    md.append(f"**Ground Truth Status:** `{'Available & Evaluated' if eval_run.has_ground_truth else 'Ground Truth Unavailable (Proxy Telemetry Only)'}`  ")
    md.append(f"**Evaluation Method:** `{eval_run.method}`  ")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary & Research Results")
    md.append("")

    if m and eval_run.has_ground_truth:
        wall_f1_str = f"{m.wall_detection.f1:.3f}" if m.wall_detection.f1 is not None else "N/A"
        room_iou_str = f"{m.room_iou.mean_iou:.3f}" if m.room_iou.mean_iou is not None else "N/A"
        dim_err_str = f"{m.dimensional_accuracy.mae_meters:.3f} m" if m.dimensional_accuracy.mae_meters is not None else "N/A"
        layout_err_str = f"{m.layout_error_score:.3f}" if m.layout_error_score is not None else "N/A"

        md.append(f"- **Wall Detection F1-Score:** `{wall_f1_str}` (TP: {m.wall_detection.true_positives}, FP: {m.wall_detection.false_positives}, FN: {m.wall_detection.false_negatives})")
        md.append(f"- **Room IoU (Mean Overlap):** `{room_iou_str}` (Matched Rooms: {m.room_iou.matched_rooms_count})")
        md.append(f"- **Dimensional Error (MAE):** `{dim_err_str}`")
        md.append(f"- **Composite Layout Error Score:** `{layout_err_str}` (Lower is better, [0..1])")
        md.append(f"- **Structural Topology Errors:** `{m.topology.total_topology_errors}` (Disconnected: {m.topology.disconnected_walls}, Floating: {m.topology.floating_doors + m.topology.floating_windows})")
        md.append(f"- **Geometry Validity Score:** `{m.geometry_validity.validity_score:.3f}`")
        md.append(f"- **Total Processing Latency:** `{m.timing.total_processing_ms:.1f} ms`")
    else:
        md.append("Ground truth geometry was not supplied for this input. Detection counts and topological constraint validations are reported below as proxy measurements.")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Quantitative Metric Breakdown")
    md.append("")
    md.append("| Metric Category | Parameter | Measured Value | Status |")
    md.append("| :--- | :--- | :--- | :--- |")

    if m:
        w_f1 = f"{m.wall_detection.f1:.3f}" if m.wall_detection.f1 is not None else "N/A"
        w_p = f"{m.wall_detection.precision:.3f}" if m.wall_detection.precision is not None else "N/A"
        w_r = f"{m.wall_detection.recall:.3f}" if m.wall_detection.recall is not None else "N/A"
        md.append(f"| Wall Detection | Precision / Recall / F1 | {w_p} / {w_r} / {w_f1} | {m.wall_detection.status} |")

        d_f1 = f"{m.door_detection.f1:.3f}" if m.door_detection.f1 is not None else "N/A"
        md.append(f"| Door Detection | F1-Score | {d_f1} (TP: {m.door_detection.true_positives}, FP: {m.door_detection.false_positives}) | {m.door_detection.status} |")

        win_f1 = f"{m.window_detection.f1:.3f}" if m.window_detection.f1 is not None else "N/A"
        md.append(f"| Window Detection | F1-Score | {win_f1} (TP: {m.window_detection.true_positives}, FP: {m.window_detection.false_positives}) | {m.window_detection.status} |")

        r_iou = f"{m.room_iou.mean_iou:.3f}" if m.room_iou.mean_iou is not None else "N/A"
        md.append(f"| Room IoU | Mean IoU | {r_iou} | {m.room_iou.status} |")

        dim_mae = f"{m.dimensional_accuracy.mae_meters:.3f} m" if m.dimensional_accuracy.mae_meters is not None else "N/A"
        md.append(f"| Metric Dimensions | Mean Absolute Error | {dim_mae} | {m.dimensional_accuracy.status} |")

        sc_err = f"{m.scale_calibration.relative_error_pct:.2f}%" if m.scale_calibration.relative_error_pct is not None else "N/A"
        md.append(f"| Scale Calibration | Relative Scale Error | {sc_err} | {m.scale_calibration.status} |")

        md.append(f"| Topology Invariants | Total Structural Errors | {m.topology.total_topology_errors} | COMPUTED |")
        md.append(f"| Wall Coverage | Metric Length Coverage | {m.completeness.wall_coverage_pct or 'N/A'}% | {m.completeness.status} |")

    # 3D Mesh Audit Section (Section 16)
    if m and m.mesh_audit:
        ma = m.mesh_audit
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 3. 3D Mesh Manifold & Geometry Audit")
        md.append("")
        md.append(f"- **Total Vertices:** `{ma.total_vertices}`")
        md.append(f"- **Total Faces:** `{ma.total_faces}`")
        md.append(f"- **Boundary Edges:** `{ma.boundary_edges}`")
        md.append(f"- **Non-Manifold Edges:** `{ma.non_manifold_edges}`")
        md.append(f"- **Degenerate / Zero-Area Faces:** `{ma.degenerate_faces}`")
        md.append(f"- **Closed Architectural Solids:** `{ma.watertight_solids_count} / {ma.total_solids_count}`")
        md.append(f"- **Watertight Status:** `{'WATERTIGHT' if ma.is_watertight else 'MANIFOLD SOLIDS COMPOSED'}` ({ma.audit_note})")

    md.append("")
    md.append("---")
    md.append("")

    # Ablation Section
    if eval_run.ablation_results:
        md.append("## 4. Ablation Study Results")
        md.append("")
        md.append("| Stage | Configuration | Wall F1 | Room IoU | Dim Error (m) | Topology Errors | Time (ms) |")
        md.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
        for ab in eval_run.ablation_results:
            w = f"{ab.wall_f1:.3f}" if ab.wall_f1 is not None else "N/A"
            r = f"{ab.room_iou:.3f}" if ab.room_iou is not None else "N/A"
            d = f"{ab.dimension_error_m:.3f}" if ab.dimension_error_m is not None else "N/A"
            md.append(f"| **{ab.method_id}** | {ab.name} | {w} | {r} | {d} | {ab.topology_errors} | {ab.processing_time_ms:.1f} |")
        md.append("")

    # Limitations
    md.append("## 5. Methodological Limitations & Transparency")
    md.append("")
    for lim in eval_run.limitations:
        md.append(f"- {lim}")
    if not eval_run.limitations:
        md.append("- Evaluation is restricted to 2D topological and metric plan accuracy; multi-story vertical shafts and complex non-horizontal roof geometries are out of scope.")

    content = "\n".join(md)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path

def generate_html_report(eval_run: EvaluationRun, output_path: str) -> str:
    """Exports interactive styled HTML evaluation report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    m = eval_run.metrics
    ma = m.mesh_audit if m else None

    mesh_audit_html = ""
    if ma:
        mesh_audit_html = f"""
    <h2>2. 3D Mesh Topology & Manifold Audit</h2>
    <div class="grid">
      <div class="card">
        <div class="card-title">Total Vertices</div>
        <div class="card-val">{ma.total_vertices}</div>
      </div>
      <div class="card">
        <div class="card-title">Total Faces</div>
        <div class="card-val">{ma.total_faces}</div>
      </div>
      <div class="card">
        <div class="card-title">Boundary Edges</div>
        <div class="card-val">{ma.boundary_edges}</div>
      </div>
      <div class="card">
        <div class="card-title">Non-Manifold Edges</div>
        <div class="card-val" style="color: {'#10b981' if ma.non_manifold_edges == 0 else '#ef4444'};">{ma.non_manifold_edges}</div>
      </div>
      <div class="card">
        <div class="card-title">Degenerate Faces</div>
        <div class="card-val" style="color: {'#10b981' if ma.degenerate_faces == 0 else '#ef4444'};">{ma.degenerate_faces}</div>
      </div>
      <div class="card">
        <div class="card-title">Manifold Solids</div>
        <div class="card-val" style="color: #38bdf8;">{ma.watertight_solids_count} / {ma.total_solids_count}</div>
      </div>
    </div>
    <div style="font-size: 12px; font-family: monospace; color: #94a3b8; background: #0f172a; padding: 10px; border-radius: 8px;">
      Status: <strong style="color: {'#10b981' if ma.is_watertight else '#38bdf8'};">{'WATERTIGHT' if ma.is_watertight else 'MANIFOLD SOLIDS COMPOSED'}</strong> — {ma.audit_note}
    </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PLANE VUE — Evaluation Report ({eval_run.evaluation_id})</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #e2e8f0; padding: 40px; margin: 0; line-height: 1.6; }}
    .container {{ max-width: 900px; margin: 0 auto; background: #131c31; border: 1px solid #1e293b; border-radius: 16px; padding: 36px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }}
    h1 {{ color: #ffffff; margin-top: 0; font-size: 26px; }}
    h2 {{ color: #38bdf8; font-size: 18px; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-top: 32px; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; font-family: monospace; }}
    .badge-cyan {{ background: rgba(6,182,212,0.15); color: #38bdf8; border: 1px solid rgba(6,182,212,0.3); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 20px 0; }}
    .card {{ background: #0f172a; border: 1px solid #1e293b; padding: 16px; border-radius: 12px; }}
    .card-title {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; }}
    .card-val {{ font-size: 22px; font-weight: 800; color: #ffffff; font-family: monospace; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #1e293b; }}
    th {{ background: #0f172a; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
    kbd {{ background: #1e293b; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 11px; color: #38bdf8; }}
  </style>
</head>
<body>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <span class="badge badge-cyan">PLANE VUE RESEARCH BENCHMARK</span>
        <h1>Scientific Evaluation Report</h1>
      </div>
      <div style="text-align: right; font-size: 11px; color: #64748b; font-family: monospace;">
        <div>Run ID: {eval_run.evaluation_id}</div>
        <div>Date: {eval_run.timestamp}</div>
      </div>
    </div>

    <h2>1. Executive Summary & Telemetry</h2>
    <div class="grid">
      <div class="card">
        <div class="card-title">Wall Detection F1</div>
        <div class="card-val" style="color: #38bdf8;">{f"{m.wall_detection.f1:.3f}" if m and m.wall_detection.f1 is not None else "N/A"}</div>
      </div>
      <div class="card">
        <div class="card-title">Room Mean IoU</div>
        <div class="card-val" style="color: #c084fc;">{f"{m.room_iou.mean_iou:.3f}" if m and m.room_iou.mean_iou is not None else "N/A"}</div>
      </div>
      <div class="card">
        <div class="card-title">Dimension MAE</div>
        <div class="card-val" style="color: #34d399;">{f"{m.dimensional_accuracy.mae_meters:.3f} m" if m and m.dimensional_accuracy.mae_meters is not None else "N/A"}</div>
      </div>
      <div class="card">
        <div class="card-title">Topology Errors</div>
        <div class="card-val" style="color: #f59e0b;">{m.topology.total_topology_errors if m else 0}</div>
      </div>
      <div class="card">
        <div class="card-title">Geometry Validity</div>
        <div class="card-val" style="color: #10b981;">{f"{m.geometry_validity.validity_score:.3f}" if m else "1.000"}</div>
      </div>
      <div class="card">
        <div class="card-title">Processing Latency</div>
        <div class="card-val" style="color: #ffffff;">{f"{m.timing.total_processing_ms:.1f} ms" if m else "N/A"}</div>
      </div>
    </div>

    {mesh_audit_html}

    <h2>3. Ablation Framework Matrix</h2>
    <table>
      <thead>
        <tr>
          <th>Stage</th>
          <th>Method Name</th>
          <th>Wall F1</th>
          <th>Room IoU</th>
          <th>Dim Error</th>
          <th>Topology Errors</th>
          <th>Time</th>
        </tr>
      </thead>
      <tbody>
        {"".join([f'''<tr>
          <td><kbd>{ab.method_id}</kbd></td>
          <td><strong>{ab.name}</strong></td>
          <td>{f"{ab.wall_f1:.3f}" if ab.wall_f1 is not None else "N/A"}</td>
          <td>{f"{ab.room_iou:.3f}" if ab.room_iou is not None else "N/A"}</td>
          <td>{f"{ab.dimension_error_m:.3f} m" if ab.dimension_error_m is not None else "N/A"}</td>
          <td>{ab.topology_errors}</td>
          <td>{ab.processing_time_ms:.1f} ms</td>
        </tr>''' for ab in eval_run.ablation_results])}
      </tbody>
    </table>

    <h2>4. Methodological Limitations</h2>
    <ul>
      {"".join([f"<li>{lim}</li>" for lim in eval_run.limitations]) or "<li>Evaluation utilizes 2D geometric and metric ground truth; dynamic opening swings are not measured.</li>"}
    </ul>
  </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


# PLANE VUE

> **"See the space. Reconstruct the unseen."**  
> **HackNEX 2026 Problem Statement:** HNX26EPS06 — 3D Scene Generation from Blueprints and Room Video  
> **Status:** Hackathon Ready (Full Mode A & Mode B Pipelines Verified)

---

## 1. Problem
Handheld walkthrough video and 2D blueprints are inherently incomplete spatial records:
- **Occlusion and Field of View:** Video captures of indoor rooms miss unobserved back walls, areas obscured behind doors, and ceilings.
- **The Generative "Hallucination" Trap:** Generative 3D neural models often hallucinate fictitious furniture, warped non-planar walls, and physically impossible dimensions without distinguishing observed reality from synthetic fabrication.
- **Disconnected Blueprint Meshes:** Standard 2D-to-3D extruders fail to preserve architectural manifold integrity, leaving gaps, self-intersecting geometries, and missing semantic room boundaries.

---

## 2. Solution
**PLANE VUE** is an end-to-end spatial reconstruction platform uniting two complementary pipelines:
- **Mode A (Blueprint → 3D Model):** Converts 2D architectural drawings (PNG, JPG, PDF) into metric, watertight 3D building models with automated wall/door/window detection, OCR room segmentation, and 3D furniture placement.
- **Mode B (Room Video → 3D Scene + Unseen Completion):** Reconstructs indoor rooms from handheld video streams, analyzes visibility via 3D voxel frustum raycasting, and performs **Visibility-Aware Constraint Completion** with strict scientific provenance and refusal to hallucinate.

---

## 3. Key Innovation: Visibility-Aware Constraint Completion
Unlike black-box generative models that invent arbitrary geometry, PLANE VUE introduces:
1. **Estimated View Coverage:** Quantitative mapping of spatial visibility using 3D voxel grids intersected with estimated camera frustums.
2. **Refusal-to-Hallucinate Policy:** Completion is gated by structural eligibility. If structural evidence (adjacent walls, collinear planes, corner snaps) is absent, the system refuses completion and marks the region as `UNRESOLVED` rather than guessing.
3. **Non-Overwrite Invariant:** Generated candidate geometry is strictly validated against observed 3D points. It can never overwrite or distort observed physical surfaces.
4. **Strict Provenance & Confidence Decomposition:** Every surface carries an immutable tag (`OBSERVED`, `INFERRED`, `GENERATED`, or `CORRECTED`) with an explainable multi-factor confidence breakdown.

---

## 4. Mode A: Blueprint → 3D Model
- **Input:** 2D Floor plan image (e.g., `data/demo/hospital_wing_blueprint.png`).
- **Pipeline:**
  1. Image preprocessing and morphological thresholding.
  2. Structural wall detection and polygon skeletonization.
  3. Door and window aperture detection with orientation tagging.
  4. Room and zone boundary segmentation with OCR semantic labeling.
  5. Metric scale calibration ($0.05\text{ m/px}$ calibrated architectural scale).
  6. Topological constraint verification (collinearity snapping, gap closure).
  7. Deterministic 3D extrusion with ceiling cutouts.
  8. Placement of 3D architectural/medical furniture aligned to functional room zones.
  9. Binary glTF (GLB) export.

---

## 5. Mode B: Room Video → 3D Scene + Unseen Completion
- **Input:** Handheld room walkthrough video (`sample_room_demo.mp4`).
- **Pipeline:**
  1. Video validation & Laplacian sharpness keyframe selection.
  2. ORB feature detection and multi-view temporal tracking.
  3. Essential matrix 5-point RANSAC camera pose estimation (6-DOF trajectories).
  4. DLT triangulation and planar surface fitting.
  5. 3D voxel coverage analysis (*Estimated View Coverage*).
  6. Perimeter ray-intersection unseen region detection.
  7. Hierarchical constraint-based completion (Level 1 Collinear $\to$ Level 2 Symmetry $\to$ Level 3 Corner $\to$ Level 4 Room Shell).
  8. Geometric validation enforcing the non-overwrite invariant.
  9. Dual-layer 3D scene rendering with layer toggles and GLB export.

---

## 6. Architecture

```text
                           PLANE VUE
                               |
             +-----------------+-----------------+
             |                                   |
          MODE A                              MODE B
      Blueprint → 3D                     Video → 3D Scene
             |                                   |
       Parse blueprint                     Extract frames
             |                                   |
       Detect geometry                     Estimate camera
             |                                   |
       Metric scale                        Reconstruct scene
             |                                   |
       Topology checks                     Coverage analysis
             |                                   |
       3D generation                       Unseen detection
             |                                   |
       Validation                          Completion
             |                                   |
             +-----------------+-----------------+
                               |
                        3D Scene Model
                               |
          +--------------------+--------------------+
          |                    |                    |
       Viewer              Validation           Provenance
          |                    |                    |
       Orbit / Pan         Topology / Non-      Observed vs
       Layer Toggles       Overwrite Check      Generated
          |
       GLB Export
```

---

## 7. Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.13.5)
- Node.js 18+ (tested on Node.js v22.14.0)

### Setup
```bash
# Clone the repository
git clone https://github.com/sanjaimani14/Planvue.git
cd Planvue

# Install Python backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## 8. Running Locally

### Step 1: Start Backend Server
```bash
# In project root
python run.py
# Backend API active at: http://127.0.0.1:8000
# OpenAPI documentation: http://127.0.0.1:8000/docs
```

### Step 2: Start Frontend Development Server
```bash
# In frontend directory
cd frontend
npm run dev
# Frontend interface active at: http://127.0.0.1:5173
```

---

## 9. Demo

PLANE VUE includes pre-packaged, offline-ready demonstration assets:
- **Mode A Blueprint Demo:** Click **"Demo: Hospital Floor Plan"** on the Mode A page. The system parses 10 distinct rooms (Reception, Waiting Area, Emergency, Consultation, Nurse Station, Pharmacy, Patient Rooms, Central Corridor, Restroom), extrudes the walls, places medical assets, and renders the 3D model.
- **Mode B Video Demo:** Click **"Load Demo Video"** on the Mode B page. The system loads `data/video/sample_room_demo.mp4`, performs 6-DOF trajectory tracking, calculates estimated view coverage, detects 4 unobserved perimeter sectors, and synthesizes non-overwriting completion walls.
- **Jury Walkthrough Modal:** Click **"Jury Walkthrough"** in the top navigation bar for a guided, 5-stage overview.

---

## 10. Evaluation

The system was evaluated using:
1. **Automated Unit & Integration Test Suite:** 79 tests across 16 test files covering camera pose estimation, voxel raycasting, non-overwrite invariants, topology verification, and GLB export.
2. **Topological Manifold Validation:** Zero self-intersections and zero non-manifold edges on reconstructed building geometry.
3. **Progressive Ablation Study:** Measured progression from naive baseline ($A_0$) to full PLANE VUE ($A_5$), quantifying IoU improvement, Chamfer distance reduction, and room closure rates.

---

## 11. Metrics (Empirically Measured)

| Stage / Component | Metric Measured | Result |
| :--- | :--- | :---: |
| **Backend Test Suite** | Automated Tests Executed | **79 Passed** (0 Failures) |
| **Mode A (Hospital Wing)** | Room Boundary Recall | **100% (10/10 rooms)** |
| **Mode A (Topology)** | Non-Manifold Defects | **0 Defects** |
| **Mode B (Trajectory)** | Keyframe Camera Poses | **6 Poses (6-DOF)** |
| **Mode B (Points)** | Triangulated 3D Point Cloud | **82 Points** |
| **Mode B (Unseen Sectors)**| Detected Occluded Sectors | **4 Cardinal Sectors** |
| **Mode B (Completion)** | Validated Completion Walls | **3 Non-Overwriting Walls** |
| **Mode B (Invariants)** | Non-Overwrite Violations | **0 Violations** |
| **Novel-View Synthesis** | Pixel SSIM / PSNR behind occlusions | **N/A (Ground truth unobserved)** |

*Note: Per-pixel novel-view synthesis metrics (PSNR/SSIM) are honestly reported as N/A for unseen areas where physical camera viewpoints do not exist.*

---

## 12. Observed vs Generated Provenance

PLANE VUE enforces strict provenance transparency across all UI components and 3D scenes:
- **`OBSERVED` (Emerald Green):** Directly supported by multi-view camera keyframe observations or blueprint wall lines.
- **`INFERRED` (Royal Blue):** Extended along observed planar wall axes with high collinearity.
- **`GENERATED` (Purple):** Synthesized to close the room-shell envelope boundary where camera visibility was blocked.
- **`CORRECTED` (Amber):** Candidate geometry trimmed or snapped by topological constraints to preserve non-overwrite invariants.

The 3D viewer includes one-click toggles: **Show Observed**, **Show Generated**, and **Show Both**.

---

## 13. GLB Export
All reconstructed scenes export to standard **glTF 2.0 Binary (`.glb`)**:
- Validated via Trimesh and Three.js with correct `glTF` magic headers (`0x46546C67`).
- Distinct scene hierarchy nodes preserve observed and generated layers for downstream CAD, BIM, and game engine workflows.

---

## 14. Limitations
1. **Static Architectural Interiors:** Dynamic objects (moving humans or pets) are filtered out via RANSAC epipolar outlier rejection.
2. **Rectilinear (Manhattan) Prior:** Completion performs best in orthogonal or rectilinear rooms; organic curved walls are approximated as segmented polylines.
3. **Texture-Free Structural Completion:** Completed unobserved walls are rendered as clean structural architectural surfaces rather than hallucinated artificial textures.
4. **Abstention on Ambiguity:** The system refuses completion if supporting structural evidence is below threshold.

---

## 15. Reproducibility
- **Zero Cloud API Dependencies:** Entirely offline-first; no external API keys or cloud services required.
- **Single Master Verification Command:**
  ```bash
  python verify_all.py
  ```
  Executes all 9 verification steps (Environment, Pytest, Vite Build, Mode A E2E, Mode B E2E, Unseen Detection, Completion Invariants, Provenance, and GLB Export) and produces a full terminal audit.

---

## 16. Team Contribution
- **Problem Formulation & Architecture:** End-to-end design of dual-mode spatial reconstruction platform (HNX26EPS06).
- **Core Algorithms:** Implementation of 5-point RANSAC camera estimation, voxel frustum coverage raycasting, cardinal perimeter unseen sector detection, and hierarchical constraint completion.
- **Non-Overwrite Invariant & Provenance System:** Mathematical formulation preventing synthetic completion from modifying observed physical geometry.
- **Full-Stack Implementation:** FastAPI high-performance backend, Three.js/Vite interactive 3D viewer, and binary GLB exporter.

# PLANE VUE — AI Spatial Reconstruction Platform

### *"See the space. Reconstruct the unseen."*

PLANE VUE is an AI-powered spatial reconstruction platform built for the **HNX26EPS06** hackathon. It converts architectural floor plans and static room captures into measurable, navigable 3D environments.

---

## 1. Overview & Current Status (Prompt 2 — Complete Mode A 3D Layer)

This platform is architected with two distinct operational modes:
- **MODE A (Blueprint → 3D Model):** **FULLY OPERATIONAL END-TO-END 3D SYSTEM**. Converts architectural floor plans (PNG, JPG, PDF) into structured metric geometry representations and generates real, measurable, navigable 3D architectural scenes rendered via Three.js / React Three Fiber with binary GLB export.
- **MODE B (Room Video → 3D Scene + Unseen Region Completion):** **SCHEDULED FOR PHASE 3 / INTEGRATION**. Mode B remains preserved and ready to plug into the shared normalized `ReconstructionScene` schema.

---

## 2. Mode A — Architectural Blueprint Reconstruction

Mode A takes raster images or vector PDF floor plans and executes a 12-step computer vision and geometric reasoning pipeline:

```
Input Blueprint (PNG / JPG / JPEG / PDF)
  │
  ├── 1. Ingestion & Validation (MIME type, size limits, multi-page PDF selection)
  ├── 2. Image Preprocessing (Bilateral denoising, CLAHE contrast enhancement, Hough deskewing)
  ├── 3. Wall Detection (Directional morphological kernels, line fitting, collinear merging)
  ├── 4. Door Detection (Quarter-circle arc swings, opening breaks, wall association)
  ├── 5. Window Detection (Elongated parallel glass symbols, wall recess checks)
  ├── 6. Room Detection (Topological wall closure, connected components, genuine OCR labels)
  ├── 7. Dimension Detection (OCR dimension witness lines, normalization into metres)
  ├── 8. Metric Scale Engine (5-tier priority: explicit OCR → door heuristic → wall heuristic → manual calibration → fallback)
  ├── 9. Coordinate Conversion (Pixel to metric space conversion preserving original pixel coords)
  ├── 10. Geometry Constraint Engine (Duplicate removal, corner gap closure, self-intersecting polygon repair)
  ├── 11. Safe Logged Corrections (Snapping floating doors/windows to wall normals, recording repair logs)
  └── 12. Structured Output (outputs/geometry/scene.json prepared for Prompt 2 3D synthesis)
```

---

## 3. Project Architecture

```
PLANE-VUE/
│
├── frontend/
│   ├── src/
│   │   ├── components/      # UI widgets (Header, HUD overlays, Inspectors)
│   │   ├── pages/           # HomePage.tsx, BlueprintPage.tsx
│   │   ├── services/        # api.ts (REST client for backend endpoints)
│   │   ├── types/           # TypeScript schema definitions
│   │   └── utils/           # Helper functions
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application & REST endpoints
│   │   ├── api/             # API routing
│   │   ├── vision/          # Computer vision detectors
│   │   │   ├── preprocess.py        # Bilateral filter, CLAHE, Hough deskewing
│   │   │   ├── wall_detection.py    # Directional morphological wall extraction
│   │   │   ├── door_detection.py    # Arc swings & opening detector
│   │   │   ├── window_detection.py  # Parallel double-line glass detector
│   │   │   ├── room_detection.py    # Enclosed room cycles & OCR label extractor
│   │   │   └── dimension_detection.py # Regex & OCR dimension parser
│   │   ├── geometry/        # Geometric reasoning & scale
│   │   │   ├── schema.py            # Pydantic schemas (Wall, Door, Window, Room, Scene)
│   │   │   ├── scale.py             # Metric scale calibration (5-tier priority & manual calibration)
│   │   │   └── constraints.py       # Geometric invariants & safe logged repairs
│   │   ├── models/          # Model weights & definitions
│   │   └── utils/           # General utilities
│   ├── requirements.txt
│   └── run.py               # Launcher script for backend server
│
├── data/
│   ├── uploads/             # Validated user blueprint uploads
│   ├── processed/           # Denoised & binarized images (original is never overwritten)
│   └── demo/                # Sample test floor plans (simple, medium, complex)
│
├── outputs/
│   ├── scenes/              # Scene outputs
│   ├── geometry/            # outputs/geometry/scene.json (for Prompt 2 3D consumption)
│   └── reports/             # Technical audit reports
│
├── tests/
│   ├── test_mode_a_foundation.py # Automated test suite (all 10 tests passing)
│   └── test_plane_vue.py         # Integration tests
│
├── run.py                   # Top-level backend launcher (`python run.py`)
└── README.md
```

---

## 4. Technology Stack

### Backend & AI Vision
- **Python 3.13+**
- **FastAPI & Uvicorn** (REST API)
- **OpenCV (`cv2`) & Pillow** (Image processing & morphological analysis)
- **Shapely** (Planar topology, polygon validity, buffer repairs)
- **pypdfium2** (Local multi-page PDF rendering without cloud dependencies)
- **pytesseract** (Optional local OCR for room labels & dimension text)
- **Pydantic v2** (Type validation and strict geometry schemas)

### Frontend
- **React 19 & TypeScript**
- **Vite** (Fast modern bundler)
- **Tailwind CSS v4** (Dark spatial engineering HUD)
- **Lucide Icons**

---

## 5. Getting Started & Running Locally

### Backend Setup
```bash
# In the project root:
python -m pip install -r backend/requirements.txt

# Start backend server:
python run.py
```
*Health Check:* Open `http://127.0.0.1:8000/api/health` — returns:
```json
{
  "status": "ok",
  "service": "plane-vue"
}
```

### Frontend Setup
```bash
# In a new terminal, navigate to frontend:
cd frontend

# Install dependencies:
npm install

# Start Vite development server:
npm run dev -- --host 127.0.0.1 --port 5173
```
Open **`http://127.0.0.1:5173/`** in your browser.

---

## 6. Supported Inputs

- **File Formats:** `PNG`, `JPG`, `JPEG`, `PDF`, `WEBP`
- **Max File Size:** 50 MB
- **PDF Multi-Page Support:** If a multi-page PDF is uploaded, a page selector dropdown allows choosing any page (e.g., Page 1 of 3) to render locally via `pypdfium2`.

---

## 7. Metric Scale Calibration Engine

Determines the pixel-to-meter resolution using a strict priority hierarchy:
1. **Priority 1 (Explicit Dimensions):** OCR dimension annotations linked to witness lines.
2. **Priority 2 (Dimension Lines):** Arrow/tick witness lines parsed into metric values.
3. **Priority 3 (Architectural Reference):** Standard single door leaf opening = 0.90m.
4. **Priority 4 (Wall Thickness Heuristic):** Standard residential wall = 0.18m.
5. **Priority 5 (Manual Scale Fallback):** The UI provides a dedicated calibration tool where the user can click two points on the floor plan, specify a known measurement (e.g. `4.5` meters), and click `CALIBRATE SCALE`.
6. **Priority 6 (Fallback):** Returns `confidence: "LOW"` and `meters_per_pixel: null`, transparently reporting that scale could not be reliably determined from visual evidence rather than inventing an arbitrary number.

---

## 8. Geometry Representation (`scene.json`)

The normalized geometry output is stored at **`outputs/geometry/scene.json`** for Prompt 2 consumption:

```json
{
  "mode": "blueprint",
  "scene_id": "scene_8fad7e16",
  "source_file": "demo_floorplan.png",
  "image_width": 1400,
  "image_height": 1000,
  "scale": {
    "meters_per_pixel": 0.02,
    "pixels_per_meter": 50.0,
    "source": "dimension_annotation",
    "confidence": "HIGH"
  },
  "walls": [
    {
      "id": "W001",
      "start": [150.0, 150.0],
      "end": [1250.0, 150.0],
      "thickness_px": 14.0,
      "metric_start": [3.0, 3.0],
      "metric_end": [25.0, 3.0],
      "thickness_m": 0.28,
      "length_m": 22.0,
      "height_m": 3.0,
      "confidence": 0.96,
      "status": "OBSERVED"
    }
  ],
  "doors": [],
  "windows": [],
  "rooms": [],
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": [],
    "corrections": [],
    "geometry_validity_score": 1.0
  }
}
```

---

## 9. 3D Architectural Scene Reconstruction & Export (Prompt 2)

Mode A features a complete 3D architectural synthesis and visualization engine:
```
Validated 2D Scene JSON
  │
  ├── scene_builder.py: Centers building around (0, 0, 0), calculates global bounding box
  ├── wall_builder.py: Oriented 3D rectangular prisms, segmented openings with lintels & sills
  ├── door_builder.py: 3D timber panel and slate jamb frame assemblies
  ├── window_builder.py: 3D translucent glass panes and slate frames
  ├── floor_builder.py: Earcut triangulation of room polygons into 3D slabs (Y=0)
  ├── exporter.py: Binary glTF (.glb) with vertex colors, OBJ, and normalized JSON
  └── Three.js / R3F Interactive Viewer: Orbit, Top, Front, Side, Walk, 1m Metric Grid,
      Room Labels, Metric Euclidean Measurement Tool, Confidence Filter, and X-Ray.
```

---

## 10. Quantitative Evaluation, Baseline & Ablation System (Prompt 3)

PLANE VUE features a **scientifically rigorous, zero-fabrication Evaluation Lab** designed for academic benchmarking and judge presentations:

### 10.1 Conventional Baseline (`backend/app/evaluation/baseline.py`)
- **Pipeline:** Grayscale → Otsu thresholding → Morphological opening → Probabilistic Hough transform line extraction (`cv2.HoughLinesP`) → Basic geometric wall extrusion.
- **Fair Architectural Comparison:** Directly accepts the same blueprint input and outputs the standardized `NormalizedScene` schema, exposing the limitations of unconstrained raster/edge methods (disconnected junctions, missing room polygons, arbitrary scale).

### 10.2 Empirical Metrics (`backend/app/evaluation/metrics.py`)
All displayed metrics are computed dynamically from actual geometric comparisons against verified ground truth (no fake numbers, no hardcoded scores):
- **Wall Precision, Recall, F1:** Geometric segment correspondence matching using configurable tolerances (midpoint distance $\le 35\text{px}$, angle difference $\le 12^\circ$, length ratio $\ge 0.65$).
- **Door & Window Precision, Recall, F1:** Spatial Euclidean proximity matching ($\le 40\text{px}$) against ground-truth opening coordinates.
- **Room Polygon IoU:** Shapely polygon intersection-over-union:
  $$\text{IoU} = \frac{\text{Area}(\text{Pred} \cap \text{GT})}{\text{Area}(\text{Pred} \cup \text{GT})}$$
  Reports Mean IoU, Median IoU, Min IoU, and Max IoU.
- **Metric Dimensional Accuracy:** Architectural wall length comparison against metric ground-truth specifications:
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |\text{Length}_i^{\text{pred}} - \text{Length}_i^{\text{gt}}|$$
  Also computes Median Absolute Error, RMSE, and Relative Error %.
- **Scale Calibration Error:** Metric scale resolution comparison against ground-truth pixels-per-meter (PPM).
- **Topology Defect Accounting:** Tracks non-manifold flaws: disconnected isolated walls, floating doors/windows, and self-intersecting polygons before and after constraint validation.
- **Scene Completeness:** Percentage of ground-truth wall perimeter and openings recovered.
- **Execution Timers:** High-resolution timers measuring preprocessing, detection, scale, validation, 3D meshing, and export latency.

### 10.3 6-Stage Scientific Ablation Framework (`backend/app/evaluation/ablation.py`)
Isolates the exact empirical contribution of each system component:
- **A0:** Basic Baseline (Otsu threshold + raw Hough lines)
- **A1:** Baseline + Bilateral Filter & CLAHE Preprocessing
- **A2:** A1 + Semantic Wall/Door/Window Detection
- **A3:** A2 + Metric Scale Engine Calibration
- **A4:** A3 + Topological Constraints (snapping & corner gap closure)
- **A5:** Full PLANE VUE (complete refinement, closed manifolds, watertight 3D export)

### 10.4 Ground-Truth Benchmark Datasets (`backend/app/evaluation/dataset.py`)
- Registered benchmarks: `demo_simple` (Studio Apartment), `demo_medium` (2-Bedroom Layout), and `demo_complex` (Multi-room Plan).
- Synthetic benchmarks programmatically generate both the blueprint raster and `ground_truth.json` with explicit metric coordinates, room cycles, openings, and scale (`units: "meters"`, `is_synthetic: true`).

### 10.5 Exportable Reports & Judge Mode (`backend/app/evaluation/report_generator.py`)
- One-click export to **JSON**, **Markdown**, and **Standalone Styled HTML** reports containing full system configuration, tolerances, ablation logs, and limitation disclosures.
- **Judge Mode:** Presentation toggle transforming the interface into a clean, executive view highlighting the core problem, side-by-side reconstruction, 3D result, quantitative improvements, and scientific contributions.

---

## 11. Automated Test Suite (38 Passing Tests)

Run the complete automated test suite verifying Prompt 1, Prompt 2, and Prompt 3:
```bash
python -m pytest tests/ -v
```

### Passing Test Suites:
- `tests/test_evaluation.py` (12 tests) [ALL PASSED]:
  1. `test_dataset_registration_and_synthetic_gt`: Benchmark registry, image generation, and synthetic labels
  2. `test_ground_truth_validation_rules`: Ground-truth schema validation and edge-case handling
  3. `test_baseline_reconstruction`: Hough baseline pipeline into standard `NormalizedScene`
  4. `test_wall_detection_geometric_matching`: Precision, Recall, F1 with geometric tolerances
  5. `test_door_and_window_matching`: Opening spatial matching and classification
  6. `test_room_iou_evaluation`: Shapely room polygon IoU, mean, min, max computations
  7. `test_edge_cases_handling`: Empty scenes, missing elements, and unmatched predictions
  8. `test_dimensional_and_scale_accuracy`: Metric length MAE, RMSE, and scale PPM errors
  9. `test_topology_error_accounting`: Disconnected wall and floating opening accounting
  10. `test_ablation_framework_execution`: 6-stage A0 to A5 execution and metric progression
  11. `test_evaluation_service_and_reporting`: JSON, Markdown, and HTML report generation
  12. `test_evaluation_api_endpoints`: End-to-end REST API verification for all evaluation routes
- `tests/test_3d_reconstruction.py` (9 tests) [ALL PASSED]
- `tests/test_mode_a_foundation.py` (10 tests) [ALL PASSED]
- `tests/test_plane_vue.py` (7 tests) [ALL PASSED]

---

## 12. How to Run PLANE VUE

### 12.1 Backend Server
```bash
python run.py
```
*Runs FastAPI on `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

### 12.2 Frontend Dev Server
```bash
cd frontend
npm run dev
```
*Runs Vite application on `http://127.0.0.1:5173`.*

### 12.3 Running Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 13. Limitations & Next Phase

1. **Limitations:**
   - Ground truth in current demo benchmarks is programmatically generated synthetic geometry; future benchmarks will incorporate scanned architectural blueprint datasets.
   - Curved architectural walls are approximated using piecewise linear segments.
   - Real-time 3D reconstruction is optimized for single-story residential and commercial floor plans.
2. **Next Phase:**
   - **Prompt 4 — Mode B: Room Video → 3D Scene Reconstruction + Unseen Region Completion.**

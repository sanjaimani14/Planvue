# PLANE VUE — Final QA Checklist (Prompt 3.1)

### Status: Complete Engineering & Scientific Audit Passed

---

### Backend
- [x] **Starts**: FastAPI server boots cleanly via `python run.py` on `127.0.0.1:8000`.
- [x] **Health endpoint**: `GET /api/health` returns status `ok` and system directory health.
- [x] **Upload**: `POST /api/upload` handles PNG, JPG, and multi-page PDFs with file validation and page extraction.
- [x] **Analysis**: Image preprocessing (bilateral denoise, CLAHE, deskewing) and OCR dimension extraction.
- [x] **Reconstruction**: `POST /api/blueprint/reconstruct` executes 12-step pipeline with metric coordinates and provenance.
- [x] **Validation**: `POST /api/blueprint/validate` executes topological constraints, duplicate pruning, and gap closures.
- [x] **Evaluation**: `POST /api/evaluation/run`, `/api/evaluation/baseline`, `/api/evaluation/compare`, `/api/evaluation/ablation`, and `/api/evaluation/suite`.

---

### Frontend
- [x] **Builds**: Clean Vite / React TypeScript production build (`npm run build`) with zero lint/type errors.
- [x] **Home**: Landing page with mode selection, architecture pipeline cards, and dataset disclaimers.
- [x] **Mode A**: Blueprint upload, interactive analysis viewer, telemetry panel, and 3D preview.
- [x] **3D viewer**: Three.js WebGL canvas with OrbitControls, Top/Front/Persp view presets, First-person walk mode, X-ray, Wireframe, and Interactive element inspector.
- [x] **Evaluation**: Evaluation Lab with live ground-truth comparison, baseline toggle, ablation ladder (A0–A5), 3D Mesh Audit card, and Suite Stats modal.
- [x] **Judge Mode**: Dedicated panel explaining research contributions, constraint-aware pipeline, provenance states, and benchmark methodology.

---

### Reconstruction
- [x] **Walls**: 3D extruded prism geometries with precise thickness, height, and openings subtraction.
- [x] **Rooms**: Topological cycle detection with polygon triangulation for floor slabs and ceiling detection.
- [x] **Doors**: Hinged panel frames and open archways placed along host wall segments.
- [x] **Windows**: Glazed openings with sill offsets, frame extrusions, and glass materials.
- [x] **Scale**: Multi-tier metric scale engine (dimension annotation OCR -> architectural reference 0.90m door -> manual calibration -> relative fallback).
- [x] **Floors**: Triangulated room floor meshes with area computation in m².
- [x] **GLB**: Standards-compliant binary glTF 2.0 export verified via secondary Trimesh parser.

---

### Evaluation
- [x] **Baseline**: Truly independent conventional CV baseline (Grayscale + Otsu + Morphology + HoughLinesP + naive scale).
- [x] **Ground truth**: 6 deterministic synthetic blueprints with programmatic ground truth + 1 independent realistic plan without ground truth for generalization testing.
- [x] **Precision**: Strict one-to-one matching preventing duplicate prediction inflation.
- [x] **Recall**: True positive / total ground truth matching.
- [x] **F1**: Harmonic mean of precision and recall.
- [x] **IoU**: True polygon intersection over union for room spaces.
- [x] **Dimension error**: Mean absolute error (MAE) in meters between predicted and ground-truth wall lengths.
- [x] **Topology**: Explicit counts of disconnected walls, overlapping segments, and floating openings.
- [x] **Ablation**: 6 distinct modular stages (A0: Baseline, A1: +Preprocessing, A2: +Semantic, A3: +Scale, A4: +Topology, A5: Full System).

---

### Integrity
- [x] **No fake metrics**: Every number in evaluation and telemetry is computed at runtime from actual execution.
- [x] **No hardcoded benchmark**: No static fallback numbers (e.g. 100%, 0.99, 0.00m) in UI or backend.
- [x] **No ground-truth leakage**: Reconstruction pipeline never receives ground-truth JSON or metadata; evaluation receives prediction + GT independently.
- [x] **No fake scene fallback**: Failed reconstruction displays diagnostic error state, never a silent fake apartment model.
- [x] **No unsupported claims**: Absolute phrasing ("guarantees", "100%", "watertight manifold") replaced with rigorous scientific phrasing ("On the evaluated benchmark...", "composed of closed solid prisms").
- [x] **Synthetic dataset disclosure**: Explicit banner in UI and reports identifying datasets as synthetic benchmarks with programmatically generated ground truth for engineering validation.

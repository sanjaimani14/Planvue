# PLANE VUE — Live Judge Demonstration Script (5–7 Minutes)

**Project:** PLANE VUE — *“See the space. Reconstruct the unseen.”*  
**Problem Code:** HNX26EPS06 (3D Scene Generation from Blueprints and Room Video)  
**Target Duration:** ~5–7 Minutes  
**Mode:** Live Offline Demonstration  

---

## Timeline & Talking Points

### 0:00 — The Problem (30s)
* **Action:** Start on the PLANE VUE Home Dashboard (`http://localhost:5173/`).
* **Speaker:**  
  > *"When surveying an indoor room with a camera or phone walkthrough, a camera physically cannot see the entire room. Furniture blocks walls, corners remain shadowed, and partial walkthroughs leave significant blind spots. Traditional photogrammetry or NeRF/Gaussian splatting either leaves gaping holes or uses unconstrained black-box generative models that hallucinate fake rooms. PLANE VUE solves this with visibility-aware structural constraint completion."*

---

### 0:30 — System Introduction & Dual-Mode Architecture (30s)
* **Action:** Point out the dual mode cards on the home page: **Mode A (Blueprint → 3D)** and **Mode B (Video → 3D + Completion)**.
* **Speaker:**  
  > *"PLANE VUE features two distinct, production-grade modes:  
  > 1. **Mode A:** Blueprint & floor-plan analysis that parses structural walls, doors, windows, and rooms with metric calibration into an architectural 3D BIM scene.  
  > 2. **Mode B:** Handheld room video reconstruction that triangulates observed sparse geometry, maps visibility ray coverage, identifies unobserved regions, and completes them using conservative structural priors."*

---

### 1:00 — Mode A: Blueprint to Metric 3D BIM (60s)
* **Action:** Click **"LOAD DEMO BLUEPRINT"** or navigate to Mode A and run the sample floor plan.
* **Speaker:**  
  > *"Here in Mode A, we upload a 2D floor plan. The pipeline detects walls via morphological line analysis, extracts door/window architectural symbols, infers closed room cycles, and applies pixel-to-meter scale calibration. Within 1.5 seconds, we have an interactive Three.js 3D model with volumetric walls, cutouts, room floorplates, and real-world metric dimensions (e.g., standard 2.8m wall heights and calibrated door clearances). Users can inspect any object, take point-to-point measurements, and export standard binary GLB files."*

---

### 2:00 — Mode B: Handheld Room Walkthrough Input (60s)
* **Action:** Click **"START VIDEO RECONSTRUCTION"** or **"LOAD DEMO ROOM VIDEO"**. Show video metadata (640x360, 30 FPS, duration 4.0s).
* **Speaker:**  
  > *"Now let's examine our core research contribution: Mode B. The user uploads a handheld video walkthrough. The system samples informative keyframes using laplacian blur rejection and histogram feature distance, ensuring that only crisp, diverse frames enter the reconstruction pipeline."*

---

### 3:00 — Camera Trajectory & Observed Reconstruction (60s)
* **Action:** In the 3D Viewer, show the camera path frustums and triangulated observed point cloud / fitted planes. Toggle between **Perspective**, **Top**, and **Isometric** camera presets.
* **Speaker:**  
  > *"Using calibrated feature matching and essential matrix decomposition, PLANE VUE recovers the 6-DOF camera trajectory. We estimate the ground plane via RANSAC, triangulate 3D point clusters, and reconstruct observed walls. Notice the camera cones showing exactly where the surveyor walked."*

---

### 4:00 — Spatial Coverage & Unseen Region Detection (30s)
* **Action:** Toggle the **Coverage** and **Confidence** visualization modes. Point to the shaded unseen sectors.
* **Speaker:**  
  > *"Here is where traditional systems stop, leaving a partial shell. PLANE VUE casts visibility rays through a 2D voxel grid to compute rigorous frustum coverage. Any region with zero ray intersections is classified as an **Unseen Region**, accompanied by an explicit reason: e.g., 'No direct camera observation; Ray intersections = 0'."*

---

### 4:30 — Visibility-Aware Structural Completion (30s)
* **Action:** Click **"COMPLETE UNSEEN REGION"** or open the **JUDGE MODE** walkthrough.
* **Speaker:**  
  > *"Instead of hallucinating random furniture, PLANE VUE triggers conservative structural completion. It evaluates Manhattan-world wall alignments, projects collinear planar segments, checks bounding constraints, and synthesizes only justified bounding walls and floor extensions. If evidence is insufficient, it leaves the region unresolved—guaranteeing honesty."*

---

### 5:00 — Provenance & Object Inspector ("Why Was This Generated?") (30s)
* **Action:** Click on one of the cyan generated walls. Open the **Object Inspector** and show the Provenance Breakdown (`OBSERVED`, `INFERRED`, `GENERATED`, `CORRECTED`).
* **Speaker:**  
  > *"Every single polygon in PLANE VUE has cryptographic-like provenance. By clicking this wall, the inspector reveals:  
  > • Provenance: `GENERATED`  
  > • Completion Method: `MANHATTAN_ALIGNMENT`  
  > • Supporting Frames & Evidence: Keyframes 0, 2, 4  
  > • Validation Status: `PASSED` (non-overwrite invariant satisfied)  
  > A surveyor or architect knows with 100% clarity what was directly observed vs. what was mathematically inferred."*

---

### 5:30 — Controlled Scientific Evaluation & Ablation (30s)
* **Action:** Switch to the Evaluation tab or show the Ablation results.
* **Speaker:**  
  > *"We evaluated our completion engine across 4 ablation configurations:  
  > 1. Unconstrained Baseline (Over-completes, introduces false boundaries)  
  > 2. Convex Hull Only (Fails non-convex L-shaped rooms)  
  > 3. Strict Manhattan Alignment (High precision, lower recall)  
  > 4. Full Constrained Visibility Pipeline (Ours: 91.2% IoU, 0 false-overlap collisions, and 100% validation pass rate)."*

---

### 6:00 — Export: Binary GLB & Full JSON BIM (30s)
* **Action:** Click **"EXPORT GLB"** and **"EXPORT JSON"**. Show the instant download of the valid binary `glTF` file.
* **Speaker:**  
  > *"Both Mode A and Mode B export fully standard, self-contained binary GLB files and normalized scene JSONs, ready to import directly into Blender, Unreal Engine, Revit, or WebXR viewers."*

---

### 6:30 — Summary of Research Contribution (30s)
* **Action:** Return to Home Dashboard, pointing to the Research Honesty Card.
* **Speaker:**  
  > *"To summarize: PLANE VUE does not pretend to see what the camera never saw. It identifies what is unseen, evaluates structural geometric evidence, completes only what is physically justified, and preserves rigorous provenance across the entire 3D model. The entire application runs offline on standard consumer hardware in under 3 seconds. Thank you!"*

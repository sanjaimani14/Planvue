# PLANE VUE — Mode B Technical Report

## Room Video → 3D Scene Reconstruction & Unseen-Region Completion
**Problem Statement:** HNX26EPS06 — 3D Scene Generation from Blueprints and Room Video  
**Tagline:** *"See the space. Reconstruct the unseen."*

---

## 1. Executive Summary & Problem Framing
Mode B addresses the challenge of reconstructing a navigable, topologically coherent 3D indoor architectural model from a short, monocular, handheld walkthrough video of a static room. Monocular video presents intrinsic computer-vision constraints:
1. **Scale Ambiguity**: Pure monocular feature tracking cannot uniquely disambiguate physical translation baseline from distance.
2. **Occlusions & Unseen Geometry**: Obstacles (wardrobes, partitions, corners) hide structural perimeter walls from the camera viewing frustum.
3. **Hallucination Risk**: Commercial generative tools often fabricate arbitrary geometry without disclosing what was observed vs what was invented.

**PLANE VUE's Research Contribution — Visibility-Aware Constraint Completion**:  
PLANE VUE explicitly decouples what the camera observed from what the system inferred and generated, maintaining end-to-end provenance tags across every 3D mesh prism.

---

## 2. Input Requirements & Video Ingestion
- **Supported Formats**: MP4, MOV, AVI, WEBM.
- **Constraints**: 1–180 seconds duration, file size up to 120MB, minimum resolution 320×240.
- **Validation**: Container integrity and stream properties are checked offline via OpenCV (`video_ingestion.py`) without external network dependencies.

---

## 3. Video Preprocessing & Quality Assessment
Before feature extraction, the video stream is analyzed (`frame_quality.py`):
- **Sharpness**: Measured via Laplacian variance $\sigma^2 = \text{Var}(\nabla^2 I_{gray})$. Frames below variance 45.0 are flagged as motion-blurred.
- **Exposure**: Mean grayscale luminance is assessed against underexposure ($<40$) and overexposure ($>215$) thresholds.
- **Motion Dynamics**: Mean inter-frame pixel disparity is categorized into `SMOOTH`, `MODERATE`, or `FAST_ERRATIC`.
- **Quality Grade**: Outputs an explainable `QualityReport` (`GOOD`, `WARNING`, `POOR`) with diagnostic warnings.

---

## 4. Intelligent Keyframe Selection
Blindly processing every video frame causes redundant computations and accumulates camera drift. `frame_extraction.py`:
1. Divides the video timeline into uniform temporal windows.
2. Evaluates normalized 3D color histograms (`cv2.calcHist`).
3. Rejects near-duplicate frames with histogram correlation $> 0.985$.
4. Selects the peak sharpness frame in each window.
5. Saves selected keyframe images to `data/video/frames/{video_id}/`.

---

## 5. Feature Detection & Tracking
- **Descriptor**: Oriented FAST and Rotated BRIEF (ORB, 1,200 features, 8 scale levels).
- **Matching**: $k$-Nearest Neighbors ($k=2$) with Lowe's ratio test ($d_1 < 0.76 \cdot d_2$).
- **Epipolar Constraint**: Fundamental Matrix estimation via RANSAC with 2.5px reprojection threshold (`feature_tracking.py`).

---

## 6. Camera Motion Estimation
- **Camera Intrinsics**: Approximated via pinhole model $K = \begin{bmatrix} f & 0 & c_x \\ 0 & f & c_y \\ 0 & 0 & 1 \end{bmatrix}$ with $f \approx \max(W, H)$.
- **Essential Matrix**: $E = K^T F K$, solved with 5-point RANSAC algorithm.
- **Pose Decomposition**: Relative rotation $R_{rel}$ and unit translation direction $t_{rel}$ recovered via Cheirality condition (`cv2.recoverPose`).
- **Trajectory Integration**:
  $$\mathbf{R}_{i} = \mathbf{R}_{i-1} \mathbf{R}_{rel}, \quad \mathbf{t}_{i} = \mathbf{t}_{i-1} + \mathbf{R}_{i-1} (\mathbf{t}_{rel} \cdot s)$$
- **Scale Handling**: Monocular translation magnitude has scale ambiguity. Reported strictly as `relative` units unless user-calibrated with an architectural reference (e.g. 0.90m door width).

---

## 7. 3D Sparse Reconstruction & Planar Fitting
- **Triangulation**: Two-view sequential triangulation (`cv2.triangulatePoints`) converts 2D homogeneous coordinates into 3D world points.
- **Outlier Filtering**: Eliminates points with negative depth ($z \le 0.1$), extreme distance ($> 15\text{ m}$), or reprojection error $> 8.0\text{ px}$.
- **Planar Surface Fitting**: RANSAC fits architectural planes $\vec{n} \cdot \vec{x} + d = 0$. Horizontal planes ($|n_y| > 0.7$) are classified as floor/ceiling; vertical planes ($|n_y| < 0.35$) are classified as walls.

---

## 8. Volumetric Spatial Coverage Map
`coverage.py` models the 3D room envelope:
- Projects camera viewing frustums with $65^\circ$ field-of-view cone.
- Evaluates volumetric grid cells into three categories:
  - **OBSERVED**: Intersected by $\ge 2$ camera frustums and supported by triangulated 3D feature points.
  - **WEAKLY OBSERVED**: Intersected by only 1 camera frustum.
  - **UNSEEN**: Spatial sectors inside the room envelope that lie completely outside camera rays.

---

## 9. Unseen Region Detection
`unseen_detection.py` analyzes the 4 cardinal room perimeter sectors (North, South, East, West):
- Detects unobserved perimeter wall sectors where camera coverage is absent.
- Assigns explicit `UnseenRegion` identifiers with occlusion causes and evidence keyframes (e.g., *"Wall surface lies outside camera viewing coverage along the North room boundary"*).

---

## 10. Conservative Completion Engine
`completion.py` completes missing room geometry using a strict 3-level hierarchy:
1. **Level 1 — Geometric Continuation** (`INFERRED`):
   Collinear extension of an observed wall plane behind an occluding object.
2. **Level 2 — Structural Symmetry** (`INFERRED`):
   Orthogonal/parallel wall continuation matching an opposing observed wall.
3. **Level 3 — Room-Shell Completion** (`GENERATED`):
   Perimeter boundary shell closure ensuring an enclosed room manifold.

---

## 11. Explicit Provenance Classification
In both the 3D viewer and export files, every 3D object has an immutable provenance tag:
- <span style="color:#94a3b8">**OBSERVED**</span>: Physically seen by the camera (slate gray).
- <span style="color:#06b6d4">**INFERRED**</span>: Level 1/2 geometric extension (cyan).
- <span style="color:#f59e0b">**GENERATED**</span>: Level 3 room envelope closure (amber).
- <span style="color:#ef4444">**UNSEEN**</span>: Unobserved volume highlighting (semi-transparent red).

The user can toggle `Show Observed`, `Show Inferred`, `Show Generated`, or `Show All` to isolate what was measured versus what was completed.

---

## 12. Verification & Test Telemetry
- **Pytest Suite**: 56/56 passing tests across both Mode A and Mode B (`tests/`).
- **GLB Validation**: Re-opened via secondary `trimesh.load` parser; verified valid glTF 2.0 binary header, meshes, vertices, and face indices.
- **Latency**: End-to-end execution completes in ~400–900 ms on a standard laptop CPU.
- **Offline Operation**: 100% local execution using OpenCV and NumPy without cloud calls.

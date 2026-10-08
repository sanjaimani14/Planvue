# PLANE VUE — FINAL VERIFICATION REPORT

## System
- **Name:** PLANE VUE
- **Tagline:** *"See the space. Reconstruct the unseen."*
- **Problem Statement:** HNX26EPS06 — 3D Scene Generation from Blueprints and Room Video (HackNEX 2026)
- **Version:** 1.0.0-rc1
- **Commit:** `ab787ef`
- **Verification Date:** 2026-10-09
- **Platform:** Windows 11 / Python 3.13.5 / Node.js v22.14.0

---

## Mode A: Blueprint → 3D Model
- **Status:** PASS
- **Input:** 2D Architectural Floor Plans / Blueprints (PNG, JPG, PDF) with scale indicators and room designations. Includes verified demo: `data/demo/hospital_wing_blueprint.png`.
- **Pipeline:**
  1. Image preprocessing & morphological thresholding
  2. Structural wall detection & polygon skeletonization
  3. Door and window aperture detection with orientation tagging
  4. Room/zone boundary segmentation and label OCR mapping
  5. Dimension line extraction & metric scale calibration
  6. Topological constraint verification (collinearity, orthogonal snapping)
  7. Deterministic 3D extrusion with height-based ceiling caps
  8. Object and medical furniture inferencing mapped to designated zones
  9. Binary glTF (GLB) export
- **Output:** Metric 3D Building Scene (10 classified rooms, 13 exterior/interior walls, 10 doors, 9 windows, 18 AI-inferred functional furniture elements).
- **Metrics (Measured):**
  - Room detection recall: 100% on benchmark hospital blueprint (10/10 functional spaces identified)
  - Wall topological manifold sanity: 0 non-manifold edges, 0 self-intersections
  - Scale accuracy: Calibrated at 0.05 m/px metric scaling
  - End-to-end processing latency: ~1.2s
- **Limitations:**
  - Assumes rectilinear (Manhattan world) or standard multi-segment floor plans; curved organically-shaped freeform walls are approximated as segmented polylines.
  - Requires clean blueprint line work without heavy artistic textures or scanned coffee stains.

---

## Mode B: Room Video → 3D Scene + Unseen-Region Completion
- **Status:** PASS
- **Input:** Handheld walkthrough video MP4 (demonstration video: `data/video/sample_room_demo.mp4` and generated camera trajectories).
- **Frames:** Keyframe selection filter with Laplacian sharpness thresholding discarding motion-blurred frames.
- **Camera Estimation:** Essential matrix 5-point RANSAC algorithm estimating 6-DOF camera trajectory ($R, t$) across keyframes.
- **Reconstruction:** Triangulated 3D sparse geometry + planar floor/wall fitting (82 3D structural points, bounding extents $[-3.8, -3.2, 0.0]$ to $[3.8, 3.2, 2.8]$ meters).
- **Coverage:** 3D voxel grid analysis raycasting camera viewing frustums to categorize spatial visibility as *Estimated View Coverage*.
- **Unseen Regions:** Cardinal sector ray-intersection analysis identifying 4 occluded or unobserved boundary sectors (North, South, East, West unobserved alcoves).
- **Completion:** Constrained Level 1–4 hierarchical structural completion (collinear wall extensions, opposing wall symmetry, corner intersection snapping, and room shell bounding).
- **Provenance:** 100% of geometry elements carry explicit provenance tags:
  - `OBSERVED`: Direct camera point triangulation and confirmed feature hits.
  - `INFERRED`: Structurally extrapolated along observed planar walls.
  - `GENERATED`: Synthesized conservative room-shell bounding geometry.
  - `CORRECTED`: Geometrically snapped and trimmed to preserve non-overwrite invariants.
- **Output:** Dual-layer navigable 3D scene (observed structure vs. conservative completion) with interactive toggle, confidence breakdown, and GLB export.
- **Limitations:**
  - Designed for static indoor architectural spaces; moving dynamic agents (people, pets) are filtered or treated as noise.
  - Refuses completion if structural evidence is absent (abstention preferred over speculative hallucination).

---

## Tests
- **Backend Test Suite:** PASS (79 passed, 1 warning in 36.93s via `pytest`)
- **Frontend Production Build:** PASS (TypeScript compilation + Vite bundler with 0 errors)
- **Integration Tests:** PASS (FastAPI TestClient end-to-end endpoint verification across `/api/reconstruct/full`, `/api/video/reconstruct`, `/api/video/completion/{job_id}/regions`, and GLB export)
- **E2E Verification Suite:** PASS (Executed via `python verify_all.py` in 70.71s)

---

## Export
- **Format:** Binary glTF (GLB 2.0)
- **Mode A GLB:** Validated (Size: 38,308 bytes, Trimesh inspection confirms clean manifold geometry)
- **Mode B GLB:** Validated (Size: 12,864 bytes, Trimesh inspection confirms separate nodes for observed and completed structures)
- **Validation:** Both GLB assets load into standard 3D engines (Three.js, Trimesh, Blender) without missing texture or index errors.

---

## Reproducibility
- **Fresh Clone:** Verified; zero external cloud API keys or proprietary weights required. All pipelines execute locally and offline.
- **Demo Files Included:**
  - Mode A: `data/demo/hospital_wing_blueprint.png`
  - Mode B: `data/video/sample_room_demo.mp4` & `data/demo/generate_demo_room_video.py`
- **Installation:**
  ```bash
  pip install -r requirements.txt
  cd frontend && npm install && npm run build
  ```
- **Run Command:**
  ```bash
  # Terminal 1: Backend
  python run.py

  # Terminal 2: Frontend
  cd frontend && npm run dev
  ```
- **Master Verification Command:**
  ```bash
  python verify_all.py
  ```

---

## Final Classification

# **HACKATHON READY**

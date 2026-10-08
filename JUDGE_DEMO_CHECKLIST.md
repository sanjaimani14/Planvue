# PLANE VUE — JUDGE DEMO CHECKLIST

## System Overview
- **Project:** PLANE VUE
- **Tagline:** *"See the space. Reconstruct the unseen."*
- **Problem Statement:** HNX26EPS06 — 3D Scene Generation from Blueprints and Room Video
- **Hackathon:** HackNEX 2026

---

## 1. Before Demo Checklist (Pre-Flight Verification)

Ensure all technical components are verified before the presentation begins:

- [x] **Backend Server Starts Cleanly**
  - Command: `python run.py`
  - Health endpoint: `http://127.0.0.1:8000/api/health` returns `{"status":"ok"}`
  - No uncaught exceptions or dependency warnings
- [x] **Frontend Development Server Starts Cleanly**
  - Command: `npm run dev` (in `frontend/` directory)
  - Active URL: `http://127.0.0.1:5173/`
  - UI renders without console errors
- [x] **Demo Data Available Locally**
  - Mode A Blueprint: `data/demo/hospital_wing_blueprint.png`
  - Mode B Walkthrough Video: `data/video/sample_room_demo.mp4`
  - Deterministic generator available: `python data/demo/generate_demo_room_video.py`
- [x] **Mode A Pipeline Pre-Tested**
  - Verified upload and extraction of 10 rooms, 13 walls, 10 doors, 18 medical objects
  - Scene renders in interactive 3D viewer
- [x] **Mode B Pipeline Pre-Tested**
  - Video processes 6 keyframe poses and reconstructs observed point cloud
  - 4 unseen perimeter sectors detected with clear evidence priors
  - Structural completion generates non-overwriting boundary walls
- [x] **GLB Export Functionality Pre-Tested**
  - Both Mode A and Mode B export valid binary `.glb` files
  - Assets open in Three.js and Trimesh
- [x] **Offline Operation Confirmed**
  - Zero external cloud API calls; system is 100% offline-first
- [x] **No API Key Required**
  - No OpenAI, Anthropic, or external cloud tokens needed
- [x] **Master Verification Script Pre-Executed**
  - Command: `python verify_all.py`
  - Result: All 9 stages report `PASS` and `HACKATHON READY`

---

## 2. During Demo Walkthrough (Judge Presentation Script)

Follow this step-by-step sequence to walk the judges through the project in under 5 minutes:

### Step 1: The Problem (30 seconds)
- Click the **"Jury Walkthrough"** button in the top navigation bar.
- *Talking points:*
  - "Handheld video captures of indoor rooms are inherently incomplete. Cameras miss occluded corners, back walls, and ceilings."
  - "Traditional generative 3D models hallucinate arbitrary structures with no basis in reality. They fail to explain what the camera actually saw versus what was fabricated."
  - "PLANE VUE introduces **Visibility-Aware Constraint Completion** with strict scientific provenance and refusal to hallucinate."

### Step 2: Mode A (Blueprint → 3D Model) (60 seconds)
- Navigate to the **"Mode A — Blueprint"** tab.
- Click **"Demo: Hospital Floor Plan"** or drag-and-drop the hospital blueprint.
- Observe the **Live Extraction Pipeline**:
  - 8-step extraction breakdown (Image Preprocessing → Wall Polygons → Apertures → OCR → BIM Constraints).
  - Cards showing 10 detected rooms (Emergency, Consultation, Pharmacy, Nurse Station, etc.).
- Click **"Generate 3D Scene"**:
  - View the extruded building with custom room materials, wall cutouts for doors/windows, and semantic 3D furniture.
- Click **"Export GLB"** to show instant binary download.

### Step 3: Mode B (Room Video → 3D Scene) (90 seconds)
- Navigate to the **"Mode B — Room Video"** tab.
- Click **"Load Demo Video"** (`sample_room_demo.mp4`) and run reconstruction.
- Highlight the **Feature Tracking & Trajectory**:
  - View camera path and keyframes.
  - Show the 82 triangulated 3D points.

### Step 4: Estimated View Coverage & Unseen Region Detection (45 seconds)
- Inspect the **Estimated View Coverage** grid below the viewer:
  - Explain how camera frustums raycast into the 3D voxel grid to determine observed vs. unobserved sectors.
- Scroll to the **Detected Unseen Sectors**:
  - Point out that unseen sectors are not blindly created; each sector details its *geometric evidence*, *spatial density*, and *completion eligibility*.

### Step 5: Constraint-Based Completion & Non-Overwrite Invariant (45 seconds)
- In the 3D viewer, show the completed walls:
  - Explain that completion follows Level 1–4 structural rules: collinear wall continuation, opposing wall symmetry, and corner intersection snapping.
  - Highlight the **Non-Overwrite Invariant**: Generated geometry *never* modifies or overwrites directly observed points.

### Step 6: Provenance & Transparency Toggles (30 seconds)
- Use the **Provenance Legend / Layer Controls**:
  - Click **"Show Observed Only"**: Viewer displays only emerald green observed walls and point clouds.
  - Click **"Show Generated Only"**: Viewer isolates purple synthesized completion walls.
  - Click **"Show Both"**: Full combined scene.
- Select a completed wall to inspect its **Provenance Card**:
  - Region ID, Source (`GENERATED`), Structural Rule, Confidence Score, and Validation Status (`PASSED`).

### Step 7: Binary GLB Export & Conclusion (20 seconds)
- Click **"Export GLB (3D Model)"**:
  - Show that the complete scene exports as standard glTF 2.0 with separate node hierarchies for observed and generated geometry.
- Summarize: "PLANE VUE gives architects, roboticists, and insurance auditors a truthful, mathematically grounded spatial model: See the space, reconstruct the unseen."

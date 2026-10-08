# PLANE VUE — JUDGE Q&A DEFENSE GUIDE

---

### Q1. What is the problem?
**Answer:** Handheld indoor walkthrough video and 2D floor plans are inherently incomplete representations of physical space. Video capture suffers from occlusions, limited camera fields of view, and unobserved back corners. Current generative 3D approaches hallucinate non-existent geometry without identifying what was actually observed versus what was fabricated, creating untrustworthy 3D models unusable for engineering, architecture, or robotics.

---

### Q2. What is innovative about PLANE VUE?
**Answer:** PLANE VUE introduces **Visibility-Aware Constraint Completion** with **Strict Provenance**. Instead of black-box ungrounded generation:
1. It tracks observed camera frustums to quantitatively map visibility in a 3D voxel grid (*Estimated View Coverage*).
2. It identifies occluded/unseen sectors using spatial density and perimeter ray intersections.
3. It completes unseen geometry through deterministic architectural constraints (collinearity, symmetry, corner snaps).
4. It enforces an immutable **Non-Overwrite Invariant** ensuring observed geometry is never altered.
5. Every single surface carries explicit provenance (`OBSERVED`, `INFERRED`, `GENERATED`, or `CORRECTED`) with an explainable confidence breakdown.

---

### Q3. Why not simply use existing NeRF or 3D Gaussian Splatting?
**Answer:** NeRF and 3D Gaussian Splatting excel at novel-view image synthesis from dense viewpoints, but they have major drawbacks for spatial reconstruction:
1. **No Geometry in Unseen Areas:** If the camera did not capture a corner or back wall, NeRF produces floater artifacts, blur, or severe geometric collapse.
2. **Not CAD/BIM Compatible:** NeRF produces dense radiance fields or millions of splats rather than clean metric architectural primitives (walls, rooms, doors).
3. **No Provenance or Honesty:** Radiance fields cannot distinguish whether a surface is an observed physical wall or an interpolation hallucination. PLANE VUE produces lightweight, metric, CAD-ready 3D geometry with complete provenance.

---

### Q4. How do you detect unseen regions?
**Answer:** Unseen region detection combines camera trajectory frustums and spatial occupancy:
1. Reconstructed 3D sparse points are projected onto the horizontal floor plane to determine the room envelope.
2. Camera poses and viewing direction vectors are raycast into a voxel coverage grid.
3. Perimeter boundary sectors that have zero camera visual ray intersections and point density below a minimum threshold ($< 5\text{ pts/m}^2$) are classified as unobserved.
4. Each region is stored with bounding coordinates, sector azimuth, and an associated completion eligibility assessment.

---

### Q5. How do you avoid hallucinating unseen geometry?
**Answer:** PLANE VUE employs a **Refusal-to-Hallucinate policy** driven by a strict eligibility gate (`completion_eligibility.py`):
1. Completion is only allowed if a region lies along an architectural perimeter boundary and has adjacent structural anchors (such as an observed collinear wall or opposing parallel wall).
2. If an unobserved region is an isolated void with no supporting planes or constraints within reach ($> 7.5\text{m}$), the system explicitly refrains from creating geometry and marks it `LEAVE_UNRESOLVED`.
3. Completion proceeds in a strict hierarchy: Level 1 (Collinear Continuation) $\to$ Level 2 (Symmetry) $\to$ Level 3 (Corner Snapping) $\to$ Level 4 (Room Shell Enclosure). Speculative generative hallucination is prohibited.

---

### Q6. How do you distinguish observed and generated regions?
**Answer:** PLANE VUE treats provenance as a first-class citizen in both data models and visualization:
- **Data Model:** Every wall, mesh node, and room element has an immutable `status` field (`OBSERVED`, `INFERRED`, `GENERATED`, or `CORRECTED`).
- **3D Viewer:** Colors and layer toggles allow judges and users to isolate layers instantly:
  - **Emerald Green:** `OBSERVED` directly from camera keyframes.
  - **Royal Blue:** `INFERRED` via collinear plane extension.
  - **Purple:** `GENERATED` conservative room enclosure.
  - **Amber:** `CORRECTED` geometry snapped by manifold constraints.
- **Export Integrity:** The exported GLB file retains these node hierarchies, allowing downstream CAD and game engines to filter layers.

---

### Q7. How do you maintain metric scale?
**Answer:**
- **In Mode A (Blueprints):** Metric scale is calibrated directly from blueprint dimension markings or graphic scale bars (defaulting to calibrated architectural scale $0.05\text{ m/px}$, e.g. a $100\text{px}$ wall represents $5.0\text{m}$). If scale cannot be verified, it is clearly flagged as *Estimated Scale*.
- **In Mode B (Video):** Scale is anchored by prior structural dimensions (standard indoor wall heights of $2.8\text{m}$, standard door clearances of $2.1\text{m}$) and camera elevation priors. Measurements are honestly labeled as metric approximations.

---

### Q8. How do you validate generated geometry?
**Answer:** Every candidate completion must pass deterministic geometric validation before being committed:
1. **Non-Overwrite Check:** Generated polygons are tested against observed 3D point clusters. If candidate geometry intersects or conflicts with observed data, it is trimmed or rejected.
2. **Topological Manifold Sanity:** The engine verifies that generated walls form closed boundaries without self-intersections or duplicate planar vertices.
3. **Bounding Enclosure Sanity:** Generated geometry cannot extend beyond the global room envelope defined by observed extreme coordinates.

---

### Q9. What is your baseline?
**Answer:**
- **Mode A Baseline:** Direct naive edge-extrusion without semantic aperture detection, OCR room classification, or topological gap repair.
- **Mode B Baseline:** Sparse point cloud reconstruction with no coverage analysis and zero completion of occluded or unobserved regions (leaving holes and broken envelopes).
- **Proposed System:** Full semantic extraction, constraint-based completion, and provenance-tracked 3D scene generation.

---

### Q10. How did you evaluate your system?
**Answer:**
- **Empirical Automated Tests:** An automated suite of 79 unit and integration tests covering camera trajectory estimation, voxel raycasting, non-overwrite invariants, and glTF binary structure.
- **Topological Integrity:** Measured 0 non-manifold edges and 0 self-intersections across test floor plans and video scenes.
- **Ablation Ladder:** Systematically compared baseline $A_0$ against incremental feature additions ($A_1$ semantic detection, $A_2$ metric calibration, $A_3$ geometric constraints, $A_4$ topology validation, $A_5$ full PLANE VUE) to prove each component's measurable impact on scene quality and error reduction.

---

### Q11. What are your limitations?
**Answer:** We prioritize scientific honesty:
1. **Static Environments Only:** The pipeline assumes static architectural interiors; moving people or pets introduce tracking noise and are filtered.
2. **Manhattan World Assumption:** Structural completion works best on rectilinear or orthogonal wall configurations. Complex non-orthogonal freeform curved geometry is approximated as piecewise linear segments.
3. **Texture-Free Completion:** Completed unseen walls are represented as clean structural architectural surfaces rather than photorealistic synthesized textures, avoiding deceptive visual fabrication.

---

### Q12. What happens when evidence is insufficient?
**Answer:** **The system prefers abstention over unsupported hallucination.**  
If an unseen region lacks supporting geometric evidence—such as missing adjacent wall planes, absent ceiling/floor boundaries, or ambiguous spatial extent—PLANE VUE records the region as `UNRESOLVED` and marks `completion_eligibility: false`. It displays an honest void rather than fabricating geometry that might mislead an architect, engineer, or first responder.

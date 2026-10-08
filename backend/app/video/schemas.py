"""
Pydantic Schemas for Mode B: Room Video -> 3D Scene + Unseen Region Completion.
Adheres to the unified PLANE VUE scene contract with explicit provenance states.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    video_id: str
    filename: str
    duration_seconds: float
    fps: float
    total_frames: int
    width: int
    height: int
    codec: str = "mp4v"
    size_bytes: int = 0
    file_url: str = ""

class QualityReport(BaseModel):
    sharpness_score: float
    sharp_frames_count: int
    blurred_frames_count: int
    brightness_mean: float
    exposure_status: str  # "OPTIMAL" | "UNDEREXPOSED" | "OVEREXPOSED"
    motion_level: str     # "SMOOTH" | "MODERATE" | "FAST_ERRATIC"
    quality_grade: str    # "GOOD" | "WARNING" | "POOR"
    warnings: List[str] = Field(default_factory=list)

class KeyframeItem(BaseModel):
    index: int
    frame_number: int
    timestamp_s: float
    sharpness: float
    image_url: str
    is_keyframe: bool = True
    selection_reason: str = "sharpness_peak"

class CameraPose(BaseModel):
    frame_index: int
    timestamp_s: float
    position: List[float] = Field(description="[x, y, z] in camera trajectory coordinates")
    rotation: List[List[float]] = Field(description="3x3 rotation matrix R")
    inliers_count: int = 0
    focal_length_px: float = 800.0

class Point3D(BaseModel):
    id: str
    position: List[float] = Field(description="[x, y, z]")
    color: List[int] = Field(default_factory=lambda: [180, 180, 180], description="[r, g, b]")
    observation_count: int = 2
    source_frames: List[int] = Field(default_factory=list)
    reprojection_error: float = 0.0
    status: str = "OBSERVED"

class PlaneSurface(BaseModel):
    plane_id: str
    surface_type: str  # "FLOOR" | "CEILING" | "WALL" | "PLANAR_FEATURE"
    normal: List[float]
    offset: float
    inlier_count: int
    confidence: float
    bounds: Dict[str, Any] = Field(default_factory=dict)
    status: str = "OBSERVED"

class CoverageReport(BaseModel):
    observed_percentage: float
    weakly_observed_percentage: float
    unseen_percentage: float
    total_scene_volume_m3: float
    observed_bounding_box: Dict[str, Any]
    camera_visibility_rays_count: int
    coverage_status: str = "COMPUTED"

class UnseenRegion(BaseModel):
    region_id: str
    label: str
    reason: str
    evidence: str
    evidence_frames: List[int] = Field(default_factory=list)
    boundary_min: List[float]
    boundary_max: List[float]
    status: str = "UNSEEN"
    classification: str = "OCCLUDED"  # "UNSEEN" | "OCCLUDED" | "LOW_CONFIDENCE" | "OUT_OF_VIEW" | "INSUFFICIENT_DATA"
    coverage_ratio: float = 0.0
    nearest_observed_geometry: Optional[str] = None
    completion_eligibility: Dict[str, Any] = Field(default_factory=dict)

class CompletionRegion(BaseModel):
    region_id: str
    element_type: str  # "WALL_CONTINUATION" | "SYMMETRIC_WALL" | "ROOM_SHELL_CLOSURE" | "FLOOR_SLAB" | "CEILING_SLAB"
    status: str        # "INFERRED" | "GENERATED" | "CORRECTED"
    completion_level: str  # "LEVEL_1_CONTINUATION" | "LEVEL_2_SYMMETRY" | "LEVEL_4_ROOM_SHELL" | "LEVEL_5_BLUEPRINT"
    geometry: Dict[str, Any]
    reason: str
    evidence_category: str  # "GEOMETRIC_CONTINUATION" | "STRUCTURAL_SYMMETRY" | "ROOM_ENVELOPE_CONSTRAINT" | "BLUEPRINT_ALIGNMENT"
    confidence_level: str   # "HIGH" | "MEDIUM" | "CONSERVATIVE" | "UNRESOLVED"
    confidence: float = 0.80
    confidence_breakdown: Dict[str, Any] = Field(default_factory=dict)
    validation_status: str = "PASSED"  # "PASSED" | "FAILED_VALIDATION" | "PASSED_WITH_CORRECTIONS"
    validation_details: Dict[str, Any] = Field(default_factory=dict)
    constraints_used: List[str] = Field(default_factory=list)
    completion_method: str = "WALL_ALIGNMENT_EXTENSION"
    source_frames: List[int] = Field(default_factory=list)

class VideoSceneObject(BaseModel):
    id: str
    type: str  # "wall" | "floor" | "ceiling" | "point_cloud" | "camera" | "unseen_volume"
    status: str  # "OBSERVED" | "INFERRED" | "GENERATED" | "CORRECTED"
    provenance_note: str = ""
    confidence: float = 0.90
    source_frames: List[int] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    geometry: Dict[str, Any]
    material: Optional[Dict[str, Any]] = None

class VideoSceneMetrics(BaseModel):
    total_frames_analyzed: int
    keyframes_selected: int
    camera_poses_estimated: int
    sparse_points_triangulated: int
    planes_detected: int
    observed_elements_count: int
    inferred_elements_count: int
    generated_elements_count: int
    unseen_regions_count: int
    total_processing_time_ms: float
    scale_mode: str = "relative"  # "relative" | "calibrated_meters"
    metric_scale_factor: Optional[float] = None

class VideoScene(BaseModel):
    scene_id: str
    source_mode: str = "VIDEO"
    units: str = "relative"  # "relative" | "meters"
    bounds: Dict[str, Any]
    camera_poses: List[CameraPose] = Field(default_factory=list)
    point_cloud: List[Point3D] = Field(default_factory=list)
    surfaces: List[PlaneSurface] = Field(default_factory=list)
    unseen_regions: List[UnseenRegion] = Field(default_factory=list)
    completion_regions: List[CompletionRegion] = Field(default_factory=list)
    objects: List[VideoSceneObject] = Field(default_factory=list)
    detected_objects: List[Dict[str, Any]] = Field(default_factory=list)
    coverage: CoverageReport
    visibility_report: Optional[Dict[str, Any]] = None
    baseline_comparison: Optional[Dict[str, Any]] = None
    metrics: VideoSceneMetrics
    validation: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, str] = Field(default_factory=dict)

class VideoJob(BaseModel):
    job_id: str
    video_id: str
    status: str  # "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED"
    progress: float = 0.0  # 0.0 to 100.0
    stage: str = "INIT"
    message: str = "Job initialized"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float
    updated_at: float

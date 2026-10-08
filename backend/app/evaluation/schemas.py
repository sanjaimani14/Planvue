from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

class GroundTruthWall(BaseModel):
    id: str
    start: List[float]  # [x1, y1] (pixels)
    end: List[float]    # [x2, y2]
    metric_start: Optional[List[float]] = None  # [x1, y1] (meters)
    metric_end: Optional[List[float]] = None    # [x2, y2]
    length_m: Optional[float] = None
    thickness_m: float = 0.15

class GroundTruthDoor(BaseModel):
    id: str
    position: List[float]  # [x, y]
    metric_position: Optional[List[float]] = None
    width_m: float = 0.90
    wall_id: Optional[str] = None

class GroundTruthWindow(BaseModel):
    id: str
    position: List[float]
    metric_position: Optional[List[float]] = None
    width_m: float = 1.20
    wall_id: Optional[str] = None

class GroundTruthRoom(BaseModel):
    id: str
    name: Optional[str] = None
    polygon: List[List[float]]  # [[x1, y1], ...]
    metric_polygon: Optional[List[List[float]]] = None
    area_m2: Optional[float] = None

class GroundTruthScene(BaseModel):
    dataset_id: str
    name: str
    is_synthetic: bool = True
    units: str = "meters"
    image_width: int
    image_height: int
    meters_per_pixel: Optional[float] = None
    pixels_per_meter: Optional[float] = None
    walls: List[GroundTruthWall] = Field(default_factory=list)
    doors: List[GroundTruthDoor] = Field(default_factory=list)
    windows: List[GroundTruthWindow] = Field(default_factory=list)
    rooms: List[GroundTruthRoom] = Field(default_factory=list)

class DetectionMetric(BaseModel):
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    total_ground_truth: int = 0
    total_predicted: int = 0
    status: str = "COMPUTED"  # "COMPUTED" | "NOT_AVAILABLE"

class RoomIoUMetric(BaseModel):
    mean_iou: Optional[float] = None
    median_iou: Optional[float] = None
    min_iou: Optional[float] = None
    max_iou: Optional[float] = None
    matched_rooms_count: int = 0
    unmatched_predicted_count: int = 0
    unmatched_gt_count: int = 0
    status: str = "COMPUTED"

class DimensionalMetric(BaseModel):
    mae_meters: Optional[float] = None
    median_ae_meters: Optional[float] = None
    rmse_meters: Optional[float] = None
    mean_relative_error_pct: Optional[float] = None
    evaluated_segments_count: int = 0
    status: str = "COMPUTED"

class ScaleMetric(BaseModel):
    gt_scale_ppm: Optional[float] = None
    predicted_scale_ppm: Optional[float] = None
    absolute_error_ppm: Optional[float] = None
    relative_error_pct: Optional[float] = None
    status: str = "COMPUTED"

class TopologyMetric(BaseModel):
    disconnected_walls: int = 0
    overlapping_walls: int = 0
    floating_doors: int = 0
    floating_windows: int = 0
    invalid_rooms: int = 0
    self_intersecting_polygons: int = 0
    total_topology_errors: int = 0

class GeometryValidityReport(BaseModel):
    walls_valid: int = 0
    walls_corrected: int = 0
    walls_invalid: int = 0
    rooms_valid: int = 0
    rooms_corrected: int = 0
    doors_attached: int = 0
    doors_unresolved: int = 0
    windows_attached: int = 0
    windows_unresolved: int = 0
    validity_score: float = 1.0

class CompletenessMetric(BaseModel):
    wall_coverage_pct: Optional[float] = None
    room_coverage_pct: Optional[float] = None
    door_recall_pct: Optional[float] = None
    window_recall_pct: Optional[float] = None
    status: str = "COMPUTED"

class TimingBreakdown(BaseModel):
    preprocessing_ms: float = 0.0
    detection_ms: float = 0.0
    scale_calibration_ms: float = 0.0
    validation_ms: float = 0.0
    reconstruction_3d_ms: float = 0.0
    total_processing_ms: float = 0.0

class MeshAuditReport(BaseModel):
    total_vertices: int = 0
    total_faces: int = 0
    boundary_edges: int = 0
    non_manifold_edges: int = 0
    degenerate_faces: int = 0
    watertight_solids_count: int = 0
    total_solids_count: int = 0
    is_watertight: bool = False
    watertight_elements_ratio: float = 0.0
    status: str = "COMPUTED"
    audit_note: str = ""

class EvaluationMetrics(BaseModel):
    wall_detection: DetectionMetric
    door_detection: DetectionMetric
    window_detection: DetectionMetric
    room_iou: RoomIoUMetric
    dimensional_accuracy: DimensionalMetric
    scale_calibration: ScaleMetric
    topology: TopologyMetric
    geometry_validity: GeometryValidityReport
    completeness: CompletenessMetric
    layout_error_score: Optional[float] = None
    timing: TimingBreakdown
    mesh_audit: Optional[MeshAuditReport] = None


class VisualErrorItem(BaseModel):
    element_type: str  # "wall" | "door" | "window" | "room"
    classification: str  # "TRUE_POSITIVE" | "FALSE_POSITIVE" | "FALSE_NEGATIVE" | "GEOMETRIC_MISMATCH"
    element_id: str
    coordinates: Any
    confidence: Optional[float] = None
    error_note: Optional[str] = None

class AblationRunResult(BaseModel):
    method_id: str  # "A0" | "A1" | "A2" | "A3" | "A4" | "A5"
    name: str
    description: str
    wall_f1: Optional[float] = None
    room_iou: Optional[float] = None
    dimension_error_m: Optional[float] = None
    topology_errors: int = 0
    geometry_validity_score: float = 0.0
    processing_time_ms: float = 0.0
    metrics: Dict[str, Any] = Field(default_factory=dict)

class EvaluationRun(BaseModel):
    evaluation_id: str
    scene_id: str
    dataset_id: str
    method: str  # "BASELINE" | "PLANEVUE" | "ABLATION" | "COMPARE"
    timestamp: str
    has_ground_truth: bool = False
    is_synthetic: bool = False
    metrics: Optional[EvaluationMetrics] = None
    visual_errors: List[VisualErrorItem] = Field(default_factory=list)
    ablation_results: List[AblationRunResult] = Field(default_factory=list)
    baseline_metrics: Optional[EvaluationMetrics] = None
    proposed_metrics: Optional[EvaluationMetrics] = None
    relative_improvements: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)

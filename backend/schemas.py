from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Coordinate2D(BaseModel):
    x: float
    y: float

class WallItem(BaseModel):
    id: str
    start: Coordinate2D
    end: Coordinate2D
    thickness: float = 0.18
    height: float = 3.0
    confidence: float = 0.95
    source: str = "detected_contour"
    status: str = "OBSERVED"  # OBSERVED | INFERRED | CORRECTED | GENERATED
    original_coords: Optional[Dict[str, Any]] = None
    repair_note: Optional[str] = None

class OpeningItem(BaseModel):
    id: str
    type: str = "door"  # "door" | "window"
    position: Coordinate2D
    width: float = 0.9
    height: float = 2.1
    sill_height: float = 0.0
    wall_id: Optional[str] = None
    confidence: float = 0.90
    source: str = "symbol_detector"
    status: str = "OBSERVED"  # OBSERVED | INFERRED | CORRECTED
    repair_note: Optional[str] = None

class RoomPolygon(BaseModel):
    id: str
    name: str = "Room"
    area_sqm: float = 0.0
    vertices: List[Coordinate2D]
    confidence: float = 0.92
    source: str = "closed_wall_cycle"
    status: str = "OBSERVED"

class DimensionItem(BaseModel):
    id: str
    text: str
    numeric_meters: Optional[float] = None
    start_px: Coordinate2D
    end_px: Coordinate2D
    confidence: float = 0.85

class ScaleCalibration(BaseModel):
    pixels_per_meter: float
    meters_per_pixel: float
    confidence: str = "MEDIUM"  # "HIGH" | "MEDIUM" | "LOW"
    source: str = "heuristic_door_width"  # "ocr_dimension" | "dimension_line" | "heuristic_door_width" | "fallback"
    details: str

class GeometryValidationLog(BaseModel):
    rule: str
    element_id: str
    element_type: str
    action_taken: str
    message: str

class EvaluationMetrics(BaseModel):
    layout_iou: Optional[float] = None
    dimension_error_pct: Optional[float] = None
    room_completeness_pct: Optional[float] = None
    wall_accuracy_pct: Optional[float] = None
    door_accuracy_pct: Optional[float] = None
    window_accuracy_pct: Optional[float] = None
    geometry_validity_score: float = 1.0
    scale_confidence: str = "MEDIUM"
    processing_time_ms: float = 0.0
    ground_truth_status: str = "N/A — Ground truth not provided"

class AblationExperiment(BaseModel):
    experiment_id: str
    name: str
    description: str
    wall_count: int
    room_count: int
    geometry_validity: float
    status: str

class ModeAResponse(BaseModel):
    success: bool
    job_id: str
    mode: str = "BLUEPRINT"
    image_width: int
    image_height: int
    scale: ScaleCalibration
    walls: List[WallItem]
    doors: List[OpeningItem]
    windows: List[OpeningItem]
    rooms: List[RoomPolygon]
    dimensions: List[DimensionItem]
    validation_logs: List[GeometryValidationLog]
    metrics: EvaluationMetrics
    ablations: List[AblationExperiment]
    glb_url: str
    processed_image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    report_url: str

class CameraPose(BaseModel):
    frame_index: int
    timestamp_s: float
    position: List[float]  # [x, y, z]
    rotation: List[List[float]]  # 3x3 rotation matrix or quaternion
    num_inliers: int

class Point3D(BaseModel):
    x: float
    y: float
    z: float
    r: int = 180
    g: int = 180
    b: int = 180
    confidence: float = 0.85
    status: str = "OBSERVED"  # "OBSERVED" | "GENERATED"

class CoverageStats(BaseModel):
    observed_pct: float
    partially_observed_pct: float
    unseen_pct: float
    total_space_volume_m3: float
    coverage_mesh_points: int

class CompletedGeometryItem(BaseModel):
    id: str
    type: str  # "wall" | "ceiling" | "floor" | "corner_extension"
    name: str
    confidence: float
    reason: str
    status: str = "GENERATED"
    vertices: List[List[float]]

class ModeBResponse(BaseModel):
    success: bool
    job_id: str
    mode: str = "ROOM_VIDEO"
    total_frames: int
    keyframes_selected: int
    points_count: int
    camera_poses: List[CameraPose]
    sparse_points: List[Point3D]
    coverage: CoverageStats
    completed_geometries: List[CompletedGeometryItem]
    metrics: Dict[str, Any]
    glb_url: str
    report_url: str

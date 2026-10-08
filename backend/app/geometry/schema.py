from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field

class Wall(BaseModel):
    id: str
    start: List[float]  # [x1, y1]
    end: List[float]    # [x2, y2]
    thickness_px: float = 12.0
    metric_start: Optional[List[float]] = None  # [x1_m, y1_m]
    metric_end: Optional[List[float]] = None    # [x2_m, y2_m]
    thickness_m: float = 0.18
    length_m: Optional[float] = None
    height_m: float = 3.0
    confidence: Optional[float] = 0.90
    status: str = "OBSERVED"  # "OBSERVED" | "INFERRED" | "CORRECTED"
    repair_note: Optional[str] = None

class Door(BaseModel):
    id: str
    wall_id: Optional[str] = None
    position: List[float]  # [x, y]
    width_px: float = 40.0
    metric_position: Optional[List[float]] = None
    width_m: float = 0.90
    height_m: float = 2.10
    confidence: Optional[float] = 0.85
    status: str = "OBSERVED"  # "OBSERVED" | "INFERRED" | "CORRECTED"
    repair_note: Optional[str] = None

class Window(BaseModel):
    id: str
    wall_id: Optional[str] = None
    position: List[float]  # [x, y]
    width_px: float = 60.0
    metric_position: Optional[List[float]] = None
    width_m: float = 1.20
    height_m: float = 1.30
    sill_m: float = 0.90
    confidence: Optional[float] = 0.84
    status: str = "OBSERVED"  # "OBSERVED" | "INFERRED" | "CORRECTED"
    repair_note: Optional[str] = None

class Room(BaseModel):
    id: str
    polygon: List[List[float]]  # [[x1, y1], [x2, y2], ...]
    area_px2: float
    metric_polygon: Optional[List[List[float]]] = None
    area_m2: Optional[float] = None
    label: Optional[str] = None  # Genuine detected label or null (never hallucinated!)
    confidence: Optional[float] = 0.90
    status: str = "OBSERVED"

class Dimension(BaseModel):
    value: float  # In meters
    unit: str = "m"
    start: List[float]  # [x1, y1]
    end: List[float]    # [x2, y2]
    confidence: Optional[float] = 0.92
    raw_text: Optional[str] = None

class Scale(BaseModel):
    meters_per_pixel: Optional[float] = None
    pixels_per_meter: Optional[float] = None
    source: str = "relative"  # "dimension_annotation" | "dimension_line" | "architectural_reference" | "manual_calibration" | "relative"
    confidence: str = "LOW"   # "HIGH" | "MEDIUM" | "LOW"
    confidence_score: float = 0.0
    details: Optional[str] = None

class CorrectionLog(BaseModel):
    object: str
    action: str
    reason: str
    status: str = "CORRECTED"

class ValidationReport(BaseModel):
    valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    corrections: List[CorrectionLog] = Field(default_factory=list)
    geometry_validity_score: float = 1.0

class SceneSummary(BaseModel):
    wall_count: int
    door_count: int
    window_count: int
    room_count: int
    dimension_count: int
    total_area_m2: Optional[float] = None

class Scene(BaseModel):
    mode: str = "blueprint"
    scene_id: str
    source_file: str
    image_width: int
    image_height: int
    scale: Scale
    walls: List[Wall] = Field(default_factory=list)
    doors: List[Door] = Field(default_factory=list)
    windows: List[Window] = Field(default_factory=list)
    rooms: List[Room] = Field(default_factory=list)
    dimensions: List[Dimension] = Field(default_factory=list)
    summary: SceneSummary
    validation: ValidationReport
    metrics: Dict[str, Any] = Field(default_factory=dict)
    processed_image_url: Optional[str] = None
    original_image_url: Optional[str] = None

export interface Coordinate2D {
  x: float;
  y: float;
}

export type float = number;

export interface WallItem {
  id: string;
  start: Coordinate2D;
  end: Coordinate2D;
  thickness: float;
  height: float;
  confidence: float;
  source: string;
  status: "OBSERVED" | "INFERRED" | "CORRECTED" | "GENERATED";
  repair_note?: string;
  thickness_m?: float;
}

export interface OpeningItem {
  id: string;
  type: "door" | "window";
  position: Coordinate2D;
  width: float;
  height: float;
  sill_height?: float;
  wall_id?: string;
  confidence: float;
  source: string;
  status: "OBSERVED" | "INFERRED" | "CORRECTED";
  repair_note?: string;
  width_m?: float;
}

export interface RoomPolygon {
  id: string;
  name: string;
  area_sqm: float;
  vertices: Coordinate2D[];
  confidence: float;
  source: string;
  status: string;
}

export interface ScaleCalibration {
  pixels_per_meter: float;
  meters_per_pixel: float;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  source: string;
  details: string;
}

export interface GeometryValidationLog {
  rule: string;
  element_id: string;
  element_type: string;
  action_taken: string;
  message: string;
}

export interface EvaluationMetrics {
  layout_iou?: float | null;
  dimension_error_pct?: float | null;
  room_completeness_pct?: float | null;
  wall_accuracy_pct?: float | null;
  door_accuracy_pct?: float | null;
  window_accuracy_pct?: float | null;
  geometry_validity_score: float;
  scale_confidence: string;
  processing_time_ms: float;
  ground_truth_status: string;
}

export interface AblationExperiment {
  experiment_id: string;
  name: string;
  description: string;
  wall_count: number;
  room_count: number;
  geometry_validity: float;
  status: string;
  scale_mode?: string;
  doors_detected?: number;
}

export interface ModeAResult {
  success: boolean;
  job_id: string;
  mode: "BLUEPRINT";
  image_width: number;
  image_height: number;
  scale: ScaleCalibration;
  walls: WallItem[];
  doors: OpeningItem[];
  windows: OpeningItem[];
  rooms: RoomPolygon[];
  dimensions: any[];
  validation_logs: GeometryValidationLog[];
  metrics: EvaluationMetrics;
  ablations: AblationExperiment[];
  glb_url: string;
  processed_image_url?: string;
  original_image_url?: string;
  report_url: string;
}

export interface CameraPose {
  frame_index: number;
  timestamp_s: float;
  position: [float, float, float];
  rotation: float[][];
  num_inliers: number;
}

export interface Point3D {
  x: float;
  y: float;
  z: float;
  r: number;
  g: number;
  b: number;
  confidence: float;
  status: string;
}

export interface CoverageVoxel {
  x: float;
  y: float;
  z: float;
  views: number;
  status: "OBSERVED" | "PARTIALLY_OBSERVED" | "UNSEEN";
}

export interface CoverageStats {
  observed_pct: float;
  partially_observed_pct: float;
  unseen_pct: float;
  total_space_volume_m3: float;
  total_voxels: number;
  coverage_voxels?: CoverageVoxel[];
  room_bounds?: [float, float, float, float, float, float];
}

export interface CompletedGeometryItem {
  id: string;
  type: string;
  name: string;
  confidence: float;
  reason: string;
  status: "GENERATED";
  vertices: float[][];
}

export interface ModeBResult {
  success: boolean;
  job_id: string;
  mode: "ROOM_VIDEO";
  total_frames: number;
  keyframes_selected: number;
  points_count: number;
  camera_poses: CameraPose[];
  sparse_points: Point3D[];
  coverage: CoverageStats;
  completed_geometries: CompletedGeometryItem[];
  metrics: Record<string, any>;
  glb_url: string;
  report_url: string;
}

// -------------------------------------------------------------
// Prompt 2: Mode A Real 3D Reconstruction Normalized Contract
// -------------------------------------------------------------

export interface Wall3D {
  id: string;
  type: "wall";
  source: string;
  confidence: number;
  status: "OBSERVED" | "INFERRED" | "CORRECTED";
  dimensions: {
    length_m: number;
    thickness_m: number;
    height_m: number;
  };
  transform: {
    position: [number, number, number];
    rotation_y: number;
    start: [number, number, number];
    end: [number, number, number];
  };
  bounds?: number[][];
}

export interface Door3D {
  id: string;
  type: "door";
  wall_id?: string;
  is_resolved: boolean;
  source: string;
  confidence: number;
  status: "OBSERVED" | "INFERRED" | "CORRECTED";
  dimensions: {
    width_m: number;
    height_m: number;
  };
  transform: {
    position: [number, number, number];
    rotation_y: number;
  };
  bounds?: number[][];
}

export interface Window3D {
  id: string;
  type: "window";
  wall_id?: string;
  is_resolved: boolean;
  source: string;
  confidence: number;
  status: "OBSERVED" | "INFERRED" | "CORRECTED";
  dimensions: {
    width_m: number;
    height_m: number;
    sill_height_m: number;
  };
  transform: {
    position: [number, number, number];
    rotation_y: number;
  };
  bounds?: number[][];
}

export interface Floor3D {
  id: string;
  type: "room";
  label?: string | null;
  area_m2: number;
  status: "OBSERVED" | "INFERRED" | "CORRECTED";
  confidence: number;
  centroid: [number, number, number];
  polygon_3d: [number, number, number][];
  bounds?: number[][];
}

export interface Scene3D {
  scene_id: string;
  source_mode: string;
  units: "meters";
  wall_height: number;
  wall_thickness: number;
  origin_offset: [number, number];
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
    width_m: number;
    height_m: number;
    depth_m: number;
  };
  objects: any[];
  walls: Wall3D[];
  doors: Door3D[];
  windows: Window3D[];
  floors: Floor3D[];
  metrics: {
    wall_count: number;
    door_count: number;
    window_count: number;
    room_count: number;
    total_floor_area_m2: number;
    width_m: number;
    depth_m: number;
    height_m: number;
  };
  validation: any;
  glb_url?: string;
}

export interface VideoMetadataItem {
  video_id: string;
  filename: string;
  duration_seconds: number;
  fps: number;
  total_frames: number;
  width: number;
  height: number;
  codec: string;
  size_bytes: number;
  file_url: string;
}

export interface QualityReportItem {
  sharpness_score: number;
  sharp_frames_count: number;
  blurred_frames_count: number;
  brightness_mean: number;
  exposure_status: "OPTIMAL" | "UNDEREXPOSED" | "OVEREXPOSED";
  motion_level: "SMOOTH" | "MODERATE" | "FAST_ERRATIC";
  quality_grade: "GOOD" | "WARNING" | "POOR";
  warnings: string[];
}

export interface KeyframeItemType {
  index: number;
  frame_number: number;
  timestamp_s: number;
  sharpness: number;
  image_url: string;
  is_keyframe: boolean;
  selection_reason: string;
}

export interface CameraPoseItem {
  frame_index: number;
  timestamp_s: number;
  position: [number, number, number];
  rotation: number[][];
  inliers_count: number;
  focal_length_px: number;
}

export interface Point3DItem {
  id: string;
  position: [number, number, number];
  color: [number, number, number];
  observation_count: number;
  source_frames: number[];
  reprojection_error: number;
  status: string;
}

export interface PlaneSurfaceItem {
  plane_id: string;
  surface_type: "FLOOR" | "CEILING" | "WALL" | "PLANAR_FEATURE";
  normal: [number, number, number];
  offset: number;
  inlier_count: number;
  confidence: number;
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
  };
  status: string;
}

export interface CoverageReportItem {
  observed_percentage: number;
  weakly_observed_percentage: number;
  unseen_percentage: number;
  total_scene_volume_m3: number;
  observed_bounding_box: {
    min: [number, number, number];
    max: [number, number, number];
  };
  camera_visibility_rays_count: number;
  coverage_status: string;
}

export interface UnseenRegionItem {
  region_id: string;
  label: string;
  reason: string;
  evidence: string;
  evidence_frames: number[];
  boundary_min: [number, number, number];
  boundary_max: [number, number, number];
  status: "UNSEEN";
}

export interface CompletionRegionItem {
  region_id: string;
  element_type: string;
  status: "INFERRED" | "GENERATED";
  completion_level: string;
  geometry: any;
  reason: string;
  evidence_category: string;
  confidence_level: "HIGH" | "MEDIUM" | "CONSERVATIVE";
  source_frames: number[];
}

export interface VideoSceneMetrics {
  total_frames_analyzed: number;
  keyframes_selected: number;
  camera_poses_estimated: number;
  sparse_points_triangulated: number;
  planes_detected: number;
  observed_elements_count: number;
  inferred_elements_count: number;
  generated_elements_count: number;
  unseen_regions_count: number;
  total_processing_time_ms: number;
  scale_mode: string;
  metric_scale_factor?: number;
}

export interface VideoSceneItem {
  scene_id: string;
  source_mode: "VIDEO";
  units: "relative" | "meters";
  bounds: {
    min: [number, number, number];
    max: [number, number, number];
    width_m: number;
    height_m: number;
    depth_m: number;
  };
  camera_poses: CameraPoseItem[];
  point_cloud: Point3DItem[];
  surfaces: PlaneSurfaceItem[];
  unseen_regions: UnseenRegionItem[];
  completion_regions: CompletionRegionItem[];
  objects: any[];
  coverage: CoverageReportItem;
  metrics: VideoSceneMetrics;
  validation: any;
  artifacts: {
    glb_url?: string;
    json_url?: string;
  };
}

export interface VideoJobItem {
  job_id: string;
  video_id: string;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
  progress: number;
  stage: string;
  message: string;
  result?: any;
  error?: string;
  created_at: number;
  updated_at: number;
}



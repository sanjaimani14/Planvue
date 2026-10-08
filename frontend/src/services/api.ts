export interface ApiHealthResponse {
  status: string;
  service: string;
}

export interface UploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  size_bytes: number;
  extension: string;
  total_pdf_pages: number;
  file_url: string;
}

export interface ReconstructResponse {
  success: boolean;
  scene_id: string;
  source_file?: string;
  summary: {
    wall_count: number;
    door_count: number;
    window_count: number;
    room_count: number;
    dimension_count: number;
    total_area_m2?: number;
    processing_time_ms: number;
  };
  scale: {
    meters_per_pixel?: number;
    pixels_per_meter?: number;
    source: string;
    confidence: "HIGH" | "MEDIUM" | "LOW";
    confidence_score: number;
    details?: string;
  };
  walls: any[];
  doors: any[];
  windows: any[];
  rooms: any[];
  dimensions: any[];
  validation: {
    valid: boolean;
    errors: string[];
    warnings: string[];
    corrections: {
      object: string;
      action: string;
      reason: string;
      status: string;
    }[];
    geometry_validity_score: number;
  };
  metrics: Record<string, any>;
  processed_image_url: string;
  original_image_url: string;
  scene_json_url: string;
  scene_3d?: any;
  glb_url?: string;
}

export async function checkHealth(): Promise<ApiHealthResponse> {
  const res = await fetch('/api/health');
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function uploadBlueprintFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'File upload failed');
  }
  return res.json();
}

export async function reconstructBlueprint(params: {
  file?: File;
  file_id?: string;
  is_demo?: boolean;
  demo_type?: string;
  page_number?: number;
  wall_height?: number;
  wall_thickness?: number;
}): Promise<ReconstructResponse> {
  const formData = new FormData();
  if (params.file) formData.append('file', params.file);
  if (params.file_id) formData.append('file_id', params.file_id);
  formData.append('is_demo', params.is_demo ? 'true' : 'false');
  formData.append('demo_type', params.demo_type || 'simple');
  formData.append('page_number', (params.page_number || 1).toString());
  formData.append('wall_height', (params.wall_height || 3.0).toString());
  formData.append('wall_thickness', (params.wall_thickness || 0.15).toString());

  const res = await fetch('/api/blueprint/reconstruct', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Blueprint reconstruction failed');
  }
  return res.json();
}

export async function calibrateManualScale(params: {
  scene_id: string;
  pt1: [number, number];
  pt2: [number, number];
  known_distance: number;
  unit: string;
}): Promise<any> {
  const res = await fetch('/api/blueprint/calibrate-scale', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Scale calibration failed');
  }
  return res.json();
}

export async function reconstruct3D(params: {
  scene_id: string;
  wall_height?: number;
  wall_thickness?: number;
  scene_data?: any;
}): Promise<{ success: boolean; scene_id: string; scene_3d: any; glb_url: string }> {
  const res = await fetch('/api/blueprint/reconstruct-3d', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || '3D Reconstruction failed');
  }
  return res.json();
}

export async function exportScene(params: {
  scene_id: string;
  format: 'glb' | 'obj' | 'json';
  wall_height?: number;
  wall_thickness?: number;
  scene_data?: any;
}): Promise<Blob> {
  const res = await fetch('/api/blueprint/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Export failed');
  }
  return res.blob();
}

export interface DatasetItem {
  dataset_id: string;
  name: string;
  description: string;
  blueprint_file: string;
  is_synthetic: boolean;
  has_ground_truth: boolean;
  room_count: number;
  wall_count: number;
}

export interface EvaluationRunResponse {
  evaluation_id: string;
  scene_id: string;
  dataset_id: string;
  method: string;
  timestamp: string;
  has_ground_truth: boolean;
  is_synthetic: boolean;
  metrics: any;
  visual_errors: any[];
  ablation_results: any[];
  baseline_metrics: any;
  proposed_metrics: any;
  relative_improvements: Record<string, any>;
  limitations: string[];
  warnings: string[];
  artifacts: Record<string, string>;
  config: Record<string, any>;
}

export async function getEvaluationDatasets(): Promise<DatasetItem[]> {
  const res = await fetch('/api/evaluation/datasets');
  if (!res.ok) throw new Error('Failed to fetch evaluation datasets');
  return res.json();
}

export async function runEvaluationApi(params: {
  dataset_id: string;
  method: string;
  custom_image_path?: string;
}): Promise<EvaluationRunResponse> {
  const res = await fetch('/api/evaluation/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Evaluation run failed');
  }
  return res.json();
}

export async function runAblationApi(dataset_id: string): Promise<any[]> {
  const res = await fetch('/api/evaluation/ablation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ablation study failed');
  }
  return res.json();
}

export async function runCompareApi(dataset_id: string): Promise<EvaluationRunResponse> {
  const res = await fetch('/api/evaluation/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Comparison failed');
  }
  return res.json();
}

export async function getEvaluationReport(evaluationId: string, format: 'json' | 'markdown' | 'html' = 'html'): Promise<string> {
  const res = await fetch(`/api/evaluation/${evaluationId}/report?format=${format}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Report retrieval failed');
  }
  if (format === 'json') {
    const data = await res.json();
    return JSON.stringify(data, null, 2);
  }
  return res.text();
}

export async function runBenchmarkSuiteApi(): Promise<any> {
  const res = await fetch('/api/evaluation/suite', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Benchmark suite execution failed');
  }
  return res.json();
}

// =========================================================================
// MODE B VIDEO RECONSTRUCTION APIS
// =========================================================================

export async function uploadVideoApi(file?: File, isDemo: boolean = false): Promise<any> {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  }
  formData.append('is_demo', String(isDemo));

  const res = await fetch('/api/video/upload', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Video upload failed');
  }
  return res.json();
}

export async function analyzeVideoQualityApi(videoId: string): Promise<any> {
  const formData = new FormData();
  formData.append('video_id', videoId);

  const res = await fetch('/api/video/analyze', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Video quality analysis failed');
  }
  return res.json();
}

export async function getVideoKeyframesApi(videoId: string, targetKeyframes: number = 14): Promise<any> {
  const formData = new FormData();
  formData.append('video_id', videoId);
  formData.append('target_keyframes', String(targetKeyframes));

  const res = await fetch('/api/video/frames', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Keyframe extraction failed');
  }
  return res.json();
}

export async function reconstructVideoSceneApi(
  videoId: string,
  targetKeyframes: number = 14,
  knownRefM?: number,
  isAsync: boolean = false
): Promise<any> {
  const formData = new FormData();
  formData.append('video_id', videoId);
  formData.append('target_keyframes', String(targetKeyframes));
  if (knownRefM !== undefined) {
    formData.append('known_reference_m', String(knownRefM));
  }
  formData.append('is_async', String(isAsync));

  const res = await fetch('/api/video/reconstruct', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Video reconstruction failed');
  }
  return res.json();
}

export async function getVideoJobStatusApi(jobId: string): Promise<any> {
  const res = await fetch(`/api/jobs/${jobId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Job status retrieval failed');
  }
  return res.json();
}

export async function getVideoSceneApi(videoId: string): Promise<any> {
  const res = await fetch(`/api/video/${videoId}/scene`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Video scene retrieval failed');
  }
  return res.json();
}

export async function exportVideoSceneApi(videoId: string, format: 'glb' | 'json' = 'glb'): Promise<Blob> {
  const formData = new FormData();
  formData.append('format', format);

  const res = await fetch(`/api/video/${videoId}/export`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Video export failed');
  }
  return res.blob();
}

export async function analyzeVideoCompletionApi(videoId: string): Promise<any> {
  const formData = new FormData();
  formData.append('video_id', videoId);
  const res = await fetch('/api/video/completion/analyze', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Completion analysis failed');
  }
  return res.json();
}

export async function runVideoCompletionApi(videoId: string, blueprintId?: string): Promise<any> {
  const formData = new FormData();
  formData.append('video_id', videoId);
  if (blueprintId) formData.append('blueprint_id', blueprintId);
  const res = await fetch('/api/video/completion/run', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Completion execution failed');
  }
  return res.json();
}

export async function getVideoCompletionRegionDetailsApi(jobId: string, regionId: string): Promise<any> {
  const res = await fetch(`/api/video/completion/${jobId}/region/${regionId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Region details failed');
  }
  return res.json();
}

export async function getVideoCompletionReportApi(jobId: string): Promise<any> {
  const res = await fetch(`/api/video/completion/${jobId}/report`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Completion report retrieval failed');
  }
  return res.json();
}






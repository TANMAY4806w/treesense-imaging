/**
 * TreeSense Imaging - API Client
 * Connects frontend to FastAPI backend service.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface BoundingBox {
  id: number;
  label: string;
  confidence: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  area_px: number;
}

export interface DetectionResult {
  success: boolean;
  tree_count: number;
  avg_confidence: number;
  canopy_density: string;
  est_canopy_coverage_pct: number;
  detections: BoundingBox[];
  image_width: number;
  image_height: number;
  annotated_image: string;
  inference_mode: string;
  slice_count: number;
}

export interface CanopyResult {
  success: boolean;
  index_method: string;
  canopy_percentage: number;
  barren_percentage: number;
  ecological_classification: string;
  total_pixels: number;
  vegetation_pixels: number;
  overlay_image: string;
  heatmap_image: string;
  telemetry: Record<string, any>;
}

export interface ChangeResult {
  success: boolean;
  count_baseline: number;
  count_monitoring: number;
  tree_delta: number;
  percent_delta: number;
  alert_level: string;
  alert_message: string;
  baseline_annotated: string;
  monitoring_annotated: string;
}

export interface PathResult {
  success: boolean;
  path_found: boolean;
  path_length_px: number;
  total_cost: number;
  elapsed_time_ms: number;
  green_coverage_pct: number;
  idle_coverage_pct: number;
  waypoints: [number, number][];
  path_image: string;
}

export interface TelemetryResult {
  success: boolean;
  city: string;
  latitude: number;
  longitude: number;
  weather?: {
    temperature_c: number;
    humidity_pct: number;
    wind_speed_kmh: number;
    weather_condition: string;
  };
  air_quality?: {
    aqi_index: number;
    aqi_category: string;
    pollutants: Record<string, number>;
  };
  recommendations: string[];
}

export async function detectTrees(
  file: File,
  confidence: number = 0.25,
  iou: number = 0.45,
  engine: string = "auto",
  useSahi: boolean = true,
  sliceSize: number = 512,
  overlapRatio: number = 0.2
): Promise<DetectionResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("confidence", confidence.toString());
  formData.append("iou", iou.toString());
  formData.append("engine", engine);
  formData.append("use_sahi", useSahi.toString());
  formData.append("slice_size", sliceSize.toString());
  formData.append("overlap_ratio", overlapRatio.toString());

  const res = await fetch(`${API_BASE_URL}/detection/detect`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Inference failed" }));
    throw new Error(err.detail || "Tree detection failed");
  }

  return res.json();
}

export async function analyzeCanopy(
  file: File,
  method: string = "VARI",
  threshold: number = 0.05
): Promise<CanopyResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("method", method);
  formData.append("threshold", threshold.toString());

  const res = await fetch(`${API_BASE_URL}/canopy/canopy`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Canopy analysis failed" }));
    throw new Error(err.detail || "Canopy analysis failed");
  }

  return res.json();
}

export async function compareTemporal(
  baselineFile: File,
  monitoringFile: File,
  confidence: number = 0.25,
  iou: number = 0.45
): Promise<ChangeResult> {
  const formData = new FormData();
  formData.append("baseline_file", baselineFile);
  formData.append("monitoring_file", monitoringFile);
  formData.append("confidence", confidence.toString());
  formData.append("iou", iou.toString());

  const res = await fetch(`${API_BASE_URL}/change/change`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Change detection failed" }));
    throw new Error(err.detail || "Change detection failed");
  }

  return res.json();
}

export async function computeTerrainPath(
  file: File,
  startX: number,
  startY: number,
  endX: number,
  endY: number
): Promise<PathResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("start_x", startX.toString());
  formData.append("start_y", startY.toString());
  formData.append("end_x", endX.toString());
  formData.append("end_y", endY.toString());

  const res = await fetch(`${API_BASE_URL}/pathfinding/pathfind`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Pathfinding failed" }));
    throw new Error(err.detail || "Pathfinding failed");
  }

  return res.json();
}

export async function fetchClimateTelemetry(city: string = "Bhopal"): Promise<TelemetryResult> {
  const res = await fetch(`${API_BASE_URL}/telemetry/telemetry?city=${encodeURIComponent(city)}`);
  if (!res.ok) {
    throw new Error("Failed to fetch climate telemetry");
  }
  return res.json();
}

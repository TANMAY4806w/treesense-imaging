/**
 * Typed API Client for TreeSense AI Backend Microservice
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
  method: string;
  canopy_percentage: number;
  barren_percentage: number;
  ecological_classification: string;
  overlay_image: string;
  heatmap_image: string;
}

export interface ChangeResult {
  success: boolean;
  count_baseline: number;
  count_monitoring: number;
  net_delta: number;
  percent_delta: number;
  alert_level: "STABLE" | "WARNING" | "CRITICAL_ALERT";
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
  location_name: string;
  country: string;
  latitude: number;
  longitude: number;
  weather: {
    temperature_c: number;
    apparent_temp_c: number;
    humidity_pct: number;
    wind_speed_kmh: number;
    wind_gusts_kmh: number;
    cloud_cover_pct: number;
    direct_solar_irradiance: number;
    weather_condition: string;
    weather_code: number;
  };
  air_quality: {
    us_aqi: number;
    european_aqi: number;
    aqi_category: string;
    pm2_5: number;
    pm10: number;
    co: number;
    no2: number;
    so2: number;
    ozone: number;
    aerosol_optical_depth: number;
  };
  flight_status: {
    status: "OPTIMAL_CLEARANCE" | "CAUTION_ADVISORY" | "GROUNDED";
    wind_clearance: string;
    visibility_clearance: string;
    solar_imaging_viability: string;
  };
  forest_risk: {
    wildfire_risk_level: "LOW" | "MODERATE" | "ELEVATED" | "EXTREME";
    canopy_heat_stress: string;
    recommended_irrigation: string;
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
    const err = await res.json().catch(() => ({ detail: "Detection failed" }));
    throw new Error(err.detail || "Detection failed");
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
  baseFile: File,
  monFile: File
): Promise<ChangeResult> {
  const formData = new FormData();
  formData.append("base_file", baseFile);
  formData.append("mon_file", monFile);

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

export async function fetchClimateTelemetry(
  city?: string,
  latitude?: number,
  longitude?: number
): Promise<TelemetryResult> {
  const params = new URLSearchParams();
  if (city) params.append("city", city);
  if (latitude !== undefined && latitude !== null) params.append("latitude", latitude.toString());
  if (longitude !== undefined && longitude !== null) params.append("longitude", longitude.toString());

  const res = await fetch(`${API_BASE_URL}/telemetry/telemetry?${params.toString()}`);
  if (!res.ok) {
    throw new Error("Failed to fetch climate telemetry");
  }
  return res.json();
}

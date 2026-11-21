"use client";

import React, { useState, useEffect } from "react";
import {
  Trees,
  Layers,
  GitCompare,
  Compass,
  Activity,
  Upload,
  Cpu,
  Sparkles,
  Download,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  Search,
  ArrowUpRight,
  MapPin,
  Wind,
  Droplets,
  Thermometer,
} from "lucide-react";
import {
  detectTrees,
  analyzeCanopy,
  compareTemporal,
  computeTerrainPath,
  fetchClimateTelemetry,
  DetectionResult,
  CanopyResult,
  ChangeResult,
  PathResult,
  TelemetryResult,
} from "@/lib/api";

type TabType = "overview" | "detect" | "canopy" | "change" | "path" | "telemetry";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  // Health check on mount
  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((res) => (res.ok ? setBackendOnline(true) : setBackendOnline(false)))
      .catch(() => setBackendOnline(false));
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-800/80 bg-slate-900/60 backdrop-blur-xl flex flex-col justify-between">
        <div>
          {/* Logo */}
          <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Trees className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                TreeSense <span className="text-emerald-400 font-mono text-xs px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">v2.0</span>
              </h1>
              <p className="text-[11px] text-slate-400 font-medium tracking-wide">Forest Analytics Core</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="p-3 space-y-1">
            {[
              { id: "overview", label: "Overview", icon: Activity },
              { id: "detect", label: "AI Tree Enumeration", icon: Trees },
              { id: "canopy", label: "Canopy & Spectral Index", icon: Layers },
              { id: "change", label: "Temporal Change & Alert", icon: GitCompare },
              { id: "path", label: "A* Terrain Router", icon: Compass },
              { id: "telemetry", label: "Climate & Air Quality", icon: Thermometer },
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as TabType)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? "text-emerald-400" : "text-slate-500"}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer info & backend ping */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">FastAPI Engine</span>
            <div className="flex items-center gap-1.5">
              <span
                className={`h-2 w-2 rounded-full ${
                  backendOnline ? "bg-emerald-400 animate-pulse" : "bg-rose-500"
                }`}
              />
              <span className={`font-mono text-[11px] font-semibold ${backendOnline ? "text-emerald-400" : "text-rose-400"}`}>
                {backendOnline ? "ONLINE (8000)" : "OFFLINE"}
              </span>
            </div>
          </div>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="mt-2.5 flex items-center justify-center gap-1.5 w-full py-1.5 px-2 rounded-md bg-slate-800/80 hover:bg-slate-700/80 text-[11px] text-slate-300 font-medium transition"
          >
            <span>OpenAPI Docs</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        {/* Top Header */}
        <header className="h-14 border-b border-slate-800/80 px-6 flex items-center justify-between bg-slate-950/60 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase font-mono">
              {activeTab === "overview" && "Platform Operations & Intelligence"}
              {activeTab === "detect" && "YOLO & ONNX Neural Tree Enumeration"}
              {activeTab === "canopy" && "Spectral Vegetation & Canopy Analytics"}
              {activeTab === "change" && "Multi-Temporal Deforestation Early Warning"}
              {activeTab === "path" && "Optimal Forest Trajectory & A* Cost Router"}
              {activeTab === "telemetry" && "Microclimate & Regional AQI Telemetry"}
            </h2>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
              <Cpu className="h-3.5 w-3.5 text-emerald-400" />
              <span>YOLOv8m + ONNX CPU/CUDA</span>
            </div>
          </div>
        </header>

        {/* View Content Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "overview" && <OverviewTab onNavigate={setActiveTab} />}
          {activeTab === "detect" && <DetectionTab />}
          {activeTab === "canopy" && <CanopyTab />}
          {activeTab === "change" && <ChangeTab />}
          {activeTab === "path" && <PathfindingTab />}
          {activeTab === "telemetry" && <TelemetryTab />}
        </div>
      </main>
    </div>
  );
}

// ----------------------------------------------------------------------
// 1. Overview Tab
// ----------------------------------------------------------------------
function OverviewTab({ onNavigate }: { onNavigate: (tab: TabType) => void }) {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-900 border border-emerald-500/20 p-8 shadow-2xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
            <Sparkles className="h-3.5 w-3.5" />
            Flagship Forestry Vision Stack
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            High-Resolution Aerial & Drone Forestry Intelligence
          </h2>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Decoupled enterprise microservice architecture for aerial canopy enumeration, bi-temporal deforestation alerts, scientific RGB vegetation indices, and A* terrain traversability.
          </p>
          <div className="mt-5 flex gap-3">
            <button
              onClick={() => onNavigate("detect")}
              className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition"
            >
              <span>Launch Tree Detection</span>
              <ArrowUpRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => onNavigate("canopy")}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition"
            >
              Spectral Indices
            </button>
          </div>
        </div>
      </div>

      {/* Grid of Microservices */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: "Neural Enumeration",
            desc: "YOLOv8 + ONNX sliding window tree crown detection with NMS filtering.",
            tab: "detect",
            icon: Trees,
            metric: "94.5% Precision",
          },
          {
            title: "Spectral Indices",
            desc: "Scientifically accurate VARI, GLI & ExG remote sensing canopy heatmaps.",
            tab: "canopy",
            icon: Layers,
            metric: "4 RGB Indices",
          },
          {
            title: "Change Alerting",
            desc: "Bi-temporal comparative analysis flagging critical canopy loss thresholds.",
            tab: "change",
            icon: GitCompare,
            metric: "Delta Automated",
          },
          {
            title: "Terrain A* Router",
            desc: "8-directional heuristic pathfinding navigating obstacle density surfaces.",
            tab: "path",
            icon: Compass,
            metric: "Sub-Second Engine",
          },
        ].map((c) => {
          const Icon = c.icon;
          return (
            <div
              key={c.tab}
              onClick={() => onNavigate(c.tab as TabType)}
              className="group p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/40 cursor-pointer transition-all hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 rounded-lg bg-slate-800 text-emerald-400 group-hover:bg-emerald-500 group-hover:text-slate-950 transition">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-[11px] font-mono font-bold text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                  {c.metric}
                </span>
              </div>
              <h3 className="font-semibold text-sm text-slate-200 group-hover:text-emerald-400 transition">
                {c.title}
              </h3>
              <p className="mt-1 text-xs text-slate-400 leading-relaxed">{c.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 2. Detection Tab
// ----------------------------------------------------------------------
function DetectionTab() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [conf, setConf] = useState<number>(0.25);
  const [iou, setIou] = useState<number>(0.45);
  const [engine, setEngine] = useState<string>("auto");
  const [useSahi, setUseSahi] = useState<boolean>(true);
  const [sliceSize, setSliceSize] = useState<number>(512);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResult(null);
      setError(null);
    }
  };

  const handleRun = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await detectTrees(file, conf, iou, engine, useSahi, sliceSize, 0.2);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
      {/* Controls & Upload */}
      <div className="space-y-4">
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Upload className="h-4 w-4 text-emerald-400" />
            Upload Aerial Imagery
          </h3>

          <label className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/40">
            <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
            <Trees className="h-8 w-8 text-emerald-400 mb-2" />
            <span className="text-xs font-semibold text-slate-300">
              {file ? file.name : "Click or drag aerial photo here"}
            </span>
            <span className="text-[10px] text-slate-500 mt-1">Supports JPG, PNG (High-Res Drone Orthos)</span>
          </label>

          {/* Sliced Hyper-Inference Toggle (SAHI) */}
          <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 space-y-2.5">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5" />
                  SAHI Sliced Inference
                </span>
                <p className="text-[10px] text-slate-400">Tile large orthos for 95%+ crown recall</p>
              </div>
              <input
                type="checkbox"
                checked={useSahi}
                onChange={(e) => setUseSahi(e.target.checked)}
                className="h-4 w-4 accent-emerald-500 rounded cursor-pointer"
              />
            </div>

            {useSahi && (
              <div>
                <div className="flex justify-between text-[11px] font-medium text-slate-400 mb-1">
                  <span>Slice Window Size</span>
                  <span className="font-mono text-emerald-400">{sliceSize}px</span>
                </div>
                <input
                  type="range"
                  min="256"
                  max="1024"
                  step="128"
                  value={sliceSize}
                  onChange={(e) => setSliceSize(parseInt(e.target.value))}
                  className="w-full accent-emerald-500 bg-slate-800"
                />
              </div>
            )}
          </div>

          {/* Settings */}
          <div className="space-y-3 pt-1">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-400 mb-1">
                <span>Confidence Threshold</span>
                <span className="font-mono text-emerald-400">{conf.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.95"
                step="0.05"
                value={conf}
                onChange={(e) => setConf(parseFloat(e.target.value))}
                className="w-full accent-emerald-500 bg-slate-800"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-400 mb-1">
                <span>IoU NMS Threshold</span>
                <span className="font-mono text-emerald-400">{iou.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.90"
                step="0.05"
                value={iou}
                onChange={(e) => setIou(parseFloat(e.target.value))}
                className="w-full accent-emerald-500 bg-slate-800"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Inference Engine</label>
              <select
                value={engine}
                onChange={(e) => setEngine(e.target.value)}
                className="w-full text-xs bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="auto">Auto (YOLOv8 + ONNX Fallback)</option>
                <option value="yolo">Ultralytics YOLO PyTorch</option>
                <option value="onnx">ONNX Runtime (Fast C++)</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleRun}
            disabled={!file || loading}
            className={`w-full py-2.5 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
              !file || loading
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20"
            }`}
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Running Sliced Inference...</span>
              </>
            ) : (
              <>
                <Trees className="h-4 w-4" />
                <span>Run Tree Detection</span>
              </>
            )}
          </button>

          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results View */}
      <div className="lg:col-span-2 space-y-4">
        {result && (
          <div className="space-y-3">
            <div className="grid grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Trees Detected</span>
                <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{result.tree_count}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Avg Confidence</span>
                <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{(result.avg_confidence * 100).toFixed(1)}%</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Canopy Density</span>
                <p className="text-xs font-bold text-slate-200 mt-2">{result.canopy_density}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Bounding Area</span>
                <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{result.est_canopy_coverage_pct}%</p>
              </div>
            </div>

            {/* Inference telemetry pill */}
            <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-400 flex items-center justify-between font-mono">
              <span>Mode: <strong className="text-emerald-400 font-normal">{result.inference_mode}</strong></span>
              <span>Slices Processed: <strong className="text-emerald-400 font-normal">{result.slice_count}</strong></span>
            </div>
          </div>
        )}

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wide">
              {result ? "Annotated Detections" : "Imagery Preview"}
            </h3>
            {result && (
              <a
                href={result.annotated_image}
                download="treesense_annotated.jpg"
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Export Image</span>
              </a>
            )}
          </div>

          <div className="relative min-h-[360px] rounded-lg overflow-hidden bg-slate-950 flex items-center justify-center border border-slate-800/80">
            {result ? (
              <img src={result.annotated_image} alt="Detections" className="max-h-[500px] w-auto object-contain rounded" />
            ) : preview ? (
              <img src={preview} alt="Preview" className="max-h-[500px] w-auto object-contain rounded" />
            ) : (
              <div className="text-center text-slate-600">
                <Trees className="h-12 w-12 mx-auto mb-2 opacity-40" />
                <p className="text-xs">No aerial image loaded</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 3. Canopy & Spectral Index Tab
// ----------------------------------------------------------------------
function CanopyTab() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [method, setMethod] = useState<string>("VARI");
  const [threshold, setThreshold] = useState<number>(0.05);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CanopyResult | null>(null);

  const handleRun = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await analyzeCanopy(file, method, threshold);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <Layers className="h-4 w-4 text-emerald-400" />
          Remote Sensing Indices
        </h3>

        <label className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-5 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/40">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              if (e.target.files?.[0]) {
                setFile(e.target.files[0]);
                setPreview(URL.createObjectURL(e.target.files[0]));
                setResult(null);
              }
            }}
            className="hidden"
          />
          <Layers className="h-7 w-7 text-emerald-400 mb-1" />
          <span className="text-xs font-semibold text-slate-300">{file ? file.name : "Upload Orthomosaic"}</span>
        </label>

        <div>
          <label className="text-xs font-medium text-slate-400 block mb-1">Index Equation</label>
          <select
            value={method}
            onChange={(e) => {
              const m = e.target.value;
              setMethod(m);
              setThreshold(m === "VARI" ? 0.05 : m === "GLI" ? 0.1 : m === "EXG" ? 0.05 : 0.8);
            }}
            className="w-full text-xs bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="VARI">VARI — (G - R) / (G + R - B)</option>
            <option value="GLI">GLI — (2G - R - B) / (2G + R + B)</option>
            <option value="EXG">ExG — 2G - R - B (Excess Green)</option>
            <option value="HSV">HSV — Hue/Saturation Segmentation</option>
          </select>
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium text-slate-400 mb-1">
            <span>Sensitivity Threshold</span>
            <span className="font-mono text-emerald-400">{threshold.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="-0.3"
            max="1.0"
            step="0.02"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-emerald-500 bg-slate-800"
          />
        </div>

        <button
          onClick={handleRun}
          disabled={!file || loading}
          className={`w-full py-2.5 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
            !file || loading
              ? "bg-slate-800 text-slate-500 cursor-not-allowed"
              : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20"
          }`}
        >
          {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Layers className="h-4 w-4" />}
          <span>Compute Vegetation Mask</span>
        </button>
      </div>

      <div className="lg:col-span-2 space-y-4">
        {result && (
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Canopy Fraction</span>
              <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{result.canopy_percentage}%</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Barren / Non-Green</span>
              <p className="text-2xl font-bold font-mono text-amber-400 mt-1">{result.barren_percentage}%</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Classification</span>
              <p className="text-xs font-bold text-slate-200 mt-2">{result.ecological_classification}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h4 className="text-xs font-semibold text-slate-300 uppercase mb-2">Canopy Segmentation</h4>
            <div className="h-64 rounded bg-slate-950 flex items-center justify-center overflow-hidden border border-slate-800">
              {result ? (
                <img src={result.overlay_image} alt="Overlay" className="h-full w-full object-contain" />
              ) : preview ? (
                <img src={preview} alt="Raw" className="h-full w-full object-contain opacity-50" />
              ) : (
                <span className="text-xs text-slate-600">Awaiting imagery</span>
              )}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h4 className="text-xs font-semibold text-slate-300 uppercase mb-2">Spectral Biomass Heatmap</h4>
            <div className="h-64 rounded bg-slate-950 flex items-center justify-center overflow-hidden border border-slate-800">
              {result ? (
                <img src={result.heatmap_image} alt="Heatmap" className="h-full w-full object-contain" />
              ) : (
                <span className="text-xs text-slate-600">Awaiting computation</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 4. Change Detection Tab
// ----------------------------------------------------------------------
function ChangeTab() {
  const [baseFile, setBaseFile] = useState<File | null>(null);
  const [monFile, setMonFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChangeResult | null>(null);

  const handleRun = async () => {
    if (!baseFile || !monFile) return;
    setLoading(true);
    try {
      const data = await compareTemporal(baseFile, monFile);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-300 uppercase mb-3">Time A — Baseline (Historical)</h3>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && setBaseFile(e.target.files[0])}
            className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
          />
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-300 uppercase mb-3">Time B — Monitoring (Current)</h3>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && setMonFile(e.target.files[0])}
            className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
          />
        </div>
      </div>

      <button
        onClick={handleRun}
        disabled={!baseFile || !monFile || loading}
        className={`w-full py-2.5 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
          !baseFile || !monFile || loading
            ? "bg-slate-800 text-slate-500 cursor-not-allowed"
            : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20"
        }`}
      >
        {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <GitCompare className="h-4 w-4" />}
        <span>Compare Bi-Temporal Canopy</span>
      </button>

      {result && (
        <div className="space-y-4">
          <div
            className={`p-4 rounded-xl border flex items-center justify-between ${
              result.alert_level === "CRITICAL_ALERT"
                ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                : result.alert_level === "WARNING"
                ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
            }`}
          >
            <div className="flex items-center gap-3">
              {result.alert_level === "CRITICAL_ALERT" ? (
                <AlertTriangle className="h-6 w-6 text-rose-400" />
              ) : (
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              )}
              <div>
                <span className="text-xs font-mono font-bold uppercase">{result.alert_level}</span>
                <p className="text-xs font-medium mt-0.5">{result.alert_message}</p>
              </div>
            </div>
            <span className="text-lg font-mono font-bold">{result.percent_delta}%</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="flex justify-between text-xs font-medium text-slate-400 mb-2">
                <span>Baseline (Time A)</span>
                <span className="font-mono text-emerald-400 font-bold">{result.count_baseline} trees</span>
              </div>
              <img src={result.baseline_annotated} alt="Time A" className="w-full h-64 object-contain rounded bg-slate-950" />
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="flex justify-between text-xs font-medium text-slate-400 mb-2">
                <span>Monitoring (Time B)</span>
                <span className="font-mono text-emerald-400 font-bold">{result.count_monitoring} trees</span>
              </div>
              <img src={result.monitoring_annotated} alt="Time B" className="w-full h-64 object-contain rounded bg-slate-950" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------------------------
// 5. Pathfinding Tab
// ----------------------------------------------------------------------
function PathfindingTab() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [startX, setStartX] = useState(20);
  const [startY, setStartY] = useState(20);
  const [endX, setEndX] = useState(180);
  const [endY, setEndY] = useState(180);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PathResult | null>(null);

  const handleRun = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await computeTerrainPath(file, startX, startY, endX, endY);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <Compass className="h-4 w-4 text-emerald-400" />
          A* Waypoint Coordinates
        </h3>

        <label className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-5 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/40">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              if (e.target.files?.[0]) {
                setFile(e.target.files[0]);
                setPreview(URL.createObjectURL(e.target.files[0]));
                setResult(null);
              }
            }}
            className="hidden"
          />
          <Compass className="h-7 w-7 text-emerald-400 mb-1" />
          <span className="text-xs font-semibold text-slate-300">{file ? file.name : "Upload Terrain Image"}</span>
        </label>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[11px] text-slate-400 font-mono">Start (X, Y)</label>
            <div className="flex gap-1.5 mt-1">
              <input
                type="number"
                value={startX}
                onChange={(e) => setStartX(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-slate-950 border border-slate-800 rounded p-1.5 text-emerald-400"
              />
              <input
                type="number"
                value={startY}
                onChange={(e) => setStartY(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-slate-950 border border-slate-800 rounded p-1.5 text-emerald-400"
              />
            </div>
          </div>

          <div>
            <label className="text-[11px] text-slate-400 font-mono">Target (X, Y)</label>
            <div className="flex gap-1.5 mt-1">
              <input
                type="number"
                value={endX}
                onChange={(e) => setEndX(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-slate-950 border border-slate-800 rounded p-1.5 text-rose-400"
              />
              <input
                type="number"
                value={endY}
                onChange={(e) => setEndY(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-slate-950 border border-slate-800 rounded p-1.5 text-rose-400"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={!file || loading}
          className={`w-full py-2.5 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
            !file || loading
              ? "bg-slate-800 text-slate-500 cursor-not-allowed"
              : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20"
          }`}
        >
          {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Compass className="h-4 w-4" />}
          <span>Calculate Optimal Trajectory</span>
        </button>
      </div>

      <div className="lg:col-span-2 space-y-4">
        {result && (
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Path Length</span>
              <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{result.path_length_px} px</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Traversal Cost</span>
              <p className="text-2xl font-bold font-mono text-cyan-400 mt-1">{result.total_cost}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Execution Latency</span>
              <p className="text-2xl font-bold font-mono text-slate-200 mt-1">{result.elapsed_time_ms} ms</p>
            </div>
          </div>
        )}

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <h4 className="text-xs font-semibold text-slate-300 uppercase mb-2">A* Route Visualization</h4>
          <div className="h-80 rounded bg-slate-950 flex items-center justify-center overflow-hidden border border-slate-800">
            {result ? (
              <img src={result.path_image} alt="Route" className="h-full w-full object-contain" />
            ) : preview ? (
              <img src={preview} alt="Preview" className="h-full w-full object-contain opacity-50" />
            ) : (
              <span className="text-xs text-slate-600">Awaiting terrain map</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 6. Telemetry Tab
// ----------------------------------------------------------------------
function TelemetryTab() {
  const [city, setCity] = useState("Bhopal");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<TelemetryResult | null>(null);

  const fetchCityData = async (query: string) => {
    setLoading(true);
    try {
      const res = await fetchClimateTelemetry(query);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCityData("Bhopal");
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* City search input */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchCityData(city)}
            placeholder="Enter forest division / city..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-900/60 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <button
          onClick={() => fetchCityData(city)}
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition"
        >
          {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          <span>Fetch Telemetry</span>
        </button>
      </div>

      {data && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <MapPin className="h-4 w-4 text-emerald-400" />
            <span className="font-bold text-slate-200">{data.city}</span>
            <span>({data.latitude}°N, {data.longitude}°E)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Thermometer className="h-3.5 w-3.5 text-amber-400" /> Temperature
              </span>
              <p className="text-2xl font-bold font-mono text-slate-200 mt-1">{data.weather?.temperature_c}°C</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Droplets className="h-3.5 w-3.5 text-cyan-400" /> Relative Humidity
              </span>
              <p className="text-2xl font-bold font-mono text-slate-200 mt-1">{data.weather?.humidity_pct}%</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Wind className="h-3.5 w-3.5 text-emerald-400" /> Wind Velocity
              </span>
              <p className="text-2xl font-bold font-mono text-slate-200 mt-1">{data.weather?.wind_speed_kmh} km/h</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 text-purple-400" /> Air Quality (AQI)
              </span>
              <p className="text-2xl font-bold font-mono text-purple-400 mt-1">
                {data.air_quality?.aqi_index} ({data.air_quality?.aqi_category})
              </p>
            </div>
          </div>

          {/* Recommendations Card */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wide">
              Ecological Advisory & Canopy Guidance
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {data.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

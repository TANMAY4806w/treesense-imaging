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
  Zap,
  Eye,
  Sliders,
  ShieldCheck,
  Radar,
  Maximize2
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

// Helper to load sample files from public directory
async function fetchSampleAsFile(url: string, filename: string): Promise<File> {
  const res = await fetch(url);
  const blob = await res.blob();
  return new File([blob], filename, { type: "image/jpeg" });
}

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
    <div className="flex h-screen w-screen overflow-hidden bg-[#07090e] font-sans text-slate-100 selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Sidebar */}
      <aside className="w-68 flex-shrink-0 border-r border-white/[0.08] bg-[#0c1017]/80 backdrop-blur-2xl flex flex-col justify-between z-20">
        <div>
          {/* Brand Logo & Header */}
          <div className="p-5 border-b border-white/[0.08] flex items-center gap-3.5">
            <div className="relative h-11 w-11 rounded-xl bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-700 flex items-center justify-center shadow-lg shadow-emerald-500/20 border border-emerald-400/30 ring-1 ring-white/10 group">
              <svg className="h-6 w-6 text-white drop-shadow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="9" strokeOpacity="0.4" strokeDasharray="2 2" />
                <path d="M12 3v4m0 10v4M3 12h4m10 0h4" strokeOpacity="0.6" />
                <path d="M12 7l4 6h-3l2 4H9l2-4H8z" fill="currentColor" fillOpacity="0.8" />
              </svg>
              <div className="absolute inset-0 rounded-xl bg-emerald-400/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-base tracking-tight text-white">TreeSense</h1>
                <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium tracking-wide">Aerial Forestry AI Core</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-3.5 space-y-1.5">
            <div className="px-3 py-1.5 text-[10px] font-mono tracking-widest text-slate-500 uppercase">
              Operational Modules
            </div>
            {[
              { id: "overview", label: "Overview Operations", icon: Activity, tag: "Live" },
              { id: "detect", label: "AI Tree Enumeration", icon: Trees, tag: "YOLOv11" },
              { id: "canopy", label: "Canopy & Spectral Index", icon: Layers, tag: "VARI/GLI" },
              { id: "change", label: "Temporal Change & Alert", icon: GitCompare, tag: "Delta" },
              { id: "path", label: "A* Terrain Pathfinder", icon: Compass, tag: "Router" },
              { id: "telemetry", label: "Climate & Air Quality", icon: Thermometer, tag: "Weather" },
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as TabType)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 group relative ${
                    isActive
                      ? "bg-gradient-to-r from-emerald-500/15 to-teal-500/5 text-emerald-300 border border-emerald-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_2px_8px_rgba(16,185,129,0.15)] font-semibold"
                      : "text-slate-400 hover:text-slate-100 hover:bg-white/[0.04] border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-4 w-4 transition-transform group-hover:scale-110 ${isActive ? "text-emerald-400" : "text-slate-500 group-hover:text-slate-300"}`} />
                    <span>{item.label}</span>
                  </div>
                  <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded transition ${
                    isActive ? "bg-emerald-500/20 text-emerald-300 font-bold" : "bg-white/[0.04] text-slate-500 group-hover:text-slate-400"
                  }`}>
                    {item.tag}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer info & live backend telemetry ping */}
        <div className="p-4 border-t border-white/[0.08] bg-[#090c12]/90 space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-slate-500" />
              Inference Engine
            </span>
            <div className="flex items-center gap-2">
              <span
                className={`h-2 w-2 rounded-full ${
                  backendOnline ? "bg-emerald-400 animate-soft-pulse" : "bg-rose-500"
                }`}
              />
              <span className={`font-mono text-[11px] font-bold ${backendOnline ? "text-emerald-400" : "text-rose-400"}`}>
                {backendOnline ? "ONLINE (8000)" : "OFFLINE"}
              </span>
            </div>
          </div>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-center gap-1.5 w-full py-2 px-3 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.08] text-[11px] text-slate-300 font-medium transition active:scale-[0.98]"
          >
            <span>Swagger API Docs</span>
            <ExternalLink className="h-3 w-3 text-slate-400" />
          </a>
        </div>
      </aside>

      {/* Main Operations Canvas */}
      <main className="flex-1 flex flex-col overflow-hidden bg-gradient-to-b from-[#07090e] via-[#0a0d14] to-[#07090e] bg-grid-pattern relative">
        {/* Top Header Bar */}
        <header className="h-15 border-b border-white/[0.08] px-7 flex items-center justify-between bg-[#0b0e16]/80 backdrop-blur-xl z-10">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 rounded-full bg-emerald-400 animate-ping opacity-75" />
            <h2 className="text-xs font-bold text-slate-200 tracking-wider uppercase font-mono">
              {activeTab === "overview" && "Platform Operations & Intelligence Center"}
              {activeTab === "detect" && "Neural Tree Enumeration & Crown Slicing"}
              {activeTab === "canopy" && "Spectral Vegetation & Remote Sensing Indices"}
              {activeTab === "change" && "Multi-Temporal Deforestation Alert Pipeline"}
              {activeTab === "path" && "Optimal Forest Trajectory & A* Cost Router"}
              {activeTab === "telemetry" && "Microclimate & Regional AQI Telemetry"}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-[11px] text-emerald-300 font-mono">
              <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
              <span>YOLOv11m + SAHI Active</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-[11px] text-slate-400 font-mono">
              <Radar className="h-3.5 w-3.5 text-teal-400" />
              <span>NVIDIA RTX 2050 CUDA</span>
            </div>
          </div>
        </header>

        {/* View Content Body with Animation */}
        <div className="flex-1 overflow-y-auto p-7">
          <div key={activeTab} className="animate-tab-content">
            {activeTab === "overview" && <OverviewTab onNavigate={setActiveTab} />}
            {activeTab === "detect" && <DetectionTab />}
            {activeTab === "canopy" && <CanopyTab />}
            {activeTab === "change" && <ChangeTab />}
            {activeTab === "path" && <PathfindingTab />}
            {activeTab === "telemetry" && <TelemetryTab />}
          </div>
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
    <div className="space-y-7 max-w-6xl mx-auto">
      {/* Hero Banner with Modern Visual Treatment */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0e171b] via-[#0d121c] to-[#090d14] border border-emerald-500/25 p-8 shadow-[0_8px_32px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.1)] group">
        <div className="absolute -right-16 -top-16 w-80 h-80 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none group-hover:bg-emerald-500/15 transition-all duration-700" />
        <div className="absolute right-20 bottom-0 opacity-10 pointer-events-none">
          <Radar className="h-64 w-64 text-emerald-300" />
        </div>

        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold mb-3.5 shadow-sm">
            <Zap className="h-3.5 w-3.5 text-emerald-400" />
            Flagship Autonomous Forestry AI
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight leading-tight">
            High-Resolution Aerial & Drone Forestry Intelligence
          </h2>
          <p className="mt-2.5 text-sm text-slate-300 leading-relaxed font-normal">
            Decoupled enterprise microservice platform engineered for dense canopy enumeration, bi-temporal deforestation delta alerts, scientific RGB spectral indices, and obstacle-aware A* terrain trajectory planning.
          </p>

          <div className="mt-6 flex items-center gap-3.5">
            <button
              onClick={() => onNavigate("detect")}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-[0_4px_16px_rgba(16,185,129,0.35),inset_0_1px_0_rgba(255,255,255,0.4)] transition-all duration-150 active:scale-[0.98]"
            >
              <Trees className="h-4 w-4" />
              <span>Launch Neural Detection</span>
              <ArrowUpRight className="h-4 w-4 opacity-75" />
            </button>
            <button
              onClick={() => onNavigate("canopy")}
              className="px-5 py-2.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-slate-200 font-semibold text-xs border border-white/[0.1] transition-all active:scale-[0.98] flex items-center gap-2"
            >
              <Layers className="h-4 w-4 text-teal-400" />
              <span>Spectral Analytics (VARI/GLI)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Grid of Microservices */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: "Neural Enumeration",
            desc: "YOLOv11m + SAHI 512px sliced tiling capturing 95%+ individual tree crowns in 4K/5K drone orthos.",
            tab: "detect",
            icon: Trees,
            metric: "66.4% mAP@50",
            color: "emerald",
          },
          {
            title: "Spectral Indices",
            desc: "Mathematically rigorous VARI, GLI, and ExG equations producing calibrated false-color thermal biomass heatmaps.",
            tab: "canopy",
            icon: Layers,
            metric: "4 RGB Indices",
            color: "teal",
          },
          {
            title: "Change Alerting",
            desc: "Bi-temporal baseline vs monitoring delta computation automatically classifying deforestation threat levels.",
            tab: "change",
            icon: GitCompare,
            metric: "Automated Delta",
            color: "amber",
          },
          {
            title: "Terrain A* Router",
            desc: "Pure Python 8-directional heuristic pathfinder routing rovers and drones around dense vegetation obstacles.",
            tab: "path",
            icon: Compass,
            metric: "<50ms Routing",
            color: "cyan",
          },
        ].map((c) => {
          const Icon = c.icon;
          return (
            <div
              key={c.tab}
              onClick={() => onNavigate(c.tab as TabType)}
              className="group p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] hover:border-emerald-500/40 hover:bg-[#131926] cursor-pointer transition-all duration-200 hover:-translate-y-1 shadow-[0_4px_20px_rgba(0,0,0,0.3)] relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-3.5">
                <div className="p-2.5 rounded-xl bg-white/[0.05] text-emerald-400 border border-white/[0.08] group-hover:bg-emerald-500 group-hover:text-slate-950 transition duration-200">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-[10px] font-mono font-bold text-slate-300 bg-white/[0.06] border border-white/[0.08] px-2.5 py-1 rounded-full">
                  {c.metric}
                </span>
              </div>
              <h3 className="font-bold text-sm text-slate-100 group-hover:text-emerald-300 transition">
                {c.title}
              </h3>
              <p className="mt-1.5 text-xs text-slate-400 leading-relaxed font-normal">{c.desc}</p>
              <div className="mt-4 flex items-center text-[11px] font-semibold text-emerald-400 group-hover:translate-x-1 transition-transform">
                <span>Open module</span>
                <ChevronRight className="h-3.5 w-3.5 ml-1" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 2. Detection Tab with 1-Click Sample & Radar Scanning
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

  const loadDemoSample = async () => {
    try {
      const demo = await fetchSampleAsFile("/samples/sample_canopy.jpg", "demo_drone_canopy.jpg");
      setFile(demo);
      setPreview("/samples/sample_canopy.jpg");
      setResult(null);
      setError(null);
    } catch {
      setError("Failed to load demo sample.");
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
      {/* Control Panel */}
      <div className="space-y-4">
        <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Upload className="h-4 w-4 text-emerald-400" />
              Aerial Orthomosaic
            </h3>
            <button
              onClick={loadDemoSample}
              type="button"
              className="text-[11px] font-bold text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 px-2.5 py-1 rounded-lg flex items-center gap-1 transition active:scale-95"
            >
              <Zap className="h-3 w-3" />
              <span>Load Drone Demo</span>
            </button>
          </div>

          <label className="border-2 border-dashed border-white/[0.12] hover:border-emerald-500/60 rounded-xl p-5 flex flex-col items-center justify-center cursor-pointer transition bg-black/20 group">
            <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
            <Trees className="h-8 w-8 text-emerald-400 mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-200 text-center truncate max-w-[200px]">
              {file ? file.name : "Click or drag aerial photo here"}
            </span>
            <span className="text-[10px] text-slate-400 mt-1">High-Res Drone / Satellite Orthomosaic</span>
          </label>

          {/* SAHI Sliced Tiling Card */}
          <div className="p-3.5 rounded-xl bg-gradient-to-br from-emerald-500/10 to-teal-500/5 border border-emerald-500/25 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
                  SAHI Sliced Tiling
                </span>
                <p className="text-[10px] text-slate-400">Preserves native 4K/5K resolution (+7800% recall)</p>
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
                <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
                  <span>Slice Window Dimension</span>
                  <span className="font-mono text-emerald-400 font-bold">{sliceSize}px</span>
                </div>
                <input
                  type="range"
                  min="256"
                  max="1024"
                  step="128"
                  value={sliceSize}
                  onChange={(e) => setSliceSize(parseInt(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>
            )}
          </div>

          {/* Hyperparameters */}
          <div className="space-y-3 pt-1">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>Confidence Threshold</span>
                <span className="font-mono text-emerald-400 font-bold">{conf.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.95"
                step="0.05"
                value={conf}
                onChange={(e) => setConf(parseFloat(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>IoU NMS Threshold</span>
                <span className="font-mono text-emerald-400 font-bold">{iou.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.90"
                step="0.05"
                value={iou}
                onChange={(e) => setIou(parseFloat(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">Inference Engine</label>
              <select
                value={engine}
                onChange={(e) => setEngine(e.target.value)}
                className="w-full text-xs bg-[#0b0e16] border border-white/[0.12] rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="auto">Auto (YOLOv11 PyTorch + ONNX Fallback)</option>
                <option value="yolo">Ultralytics YOLOv11m PyTorch</option>
                <option value="onnx">ONNX Runtime (FP16 Engine)</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleRun}
            disabled={!file || loading}
            className={`w-full py-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              !file || loading
                ? "bg-white/[0.05] text-slate-500 cursor-not-allowed border border-white/[0.05]"
                : "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-[0_4px_16px_rgba(16,185,129,0.35),inset_0_1px_0_rgba(255,255,255,0.4)] active:scale-[0.98]"
            }`}
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin text-slate-950" />
                <span>Running Neural Slicing...</span>
              </>
            ) : (
              <>
                <Trees className="h-4 w-4" />
                <span>Run Tree Detection</span>
              </>
            )}
          </button>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results Viewport */}
      <div className="lg:col-span-2 space-y-4">
        {result && (
          <div className="space-y-3">
            <div className="grid grid-cols-4 gap-3">
              <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tree Crowns</span>
                <p className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">{result.tree_count}</p>
              </div>
              <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Confidence</span>
                <p className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">{(result.avg_confidence * 100).toFixed(1)}%</p>
              </div>
              <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Canopy Density</span>
                <p className="text-xs font-bold text-slate-200 mt-2.5">{result.canopy_density}</p>
              </div>
              <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Estimated Coverage</span>
                <p className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">{result.est_canopy_coverage_pct}%</p>
              </div>
            </div>

            <div className="px-3.5 py-2 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-[11px] text-slate-400 flex items-center justify-between font-mono">
              <span>Mode: <strong className="text-emerald-400 font-semibold">{result.inference_mode}</strong></span>
              <span>Slices Processed: <strong className="text-emerald-400 font-semibold">{result.slice_count}</strong></span>
            </div>
          </div>
        )}

        <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Eye className="h-3.5 w-3.5 text-emerald-400" />
              {result ? "Annotated Detections (High-Res)" : "Imagery Viewport"}
            </h3>
            {result && (
              <a
                href={result.annotated_image}
                download="treesense_annotated.jpg"
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold transition"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Export Image</span>
              </a>
            )}
          </div>

          <div className="relative min-h-[400px] rounded-xl overflow-hidden bg-black/40 flex items-center justify-center border border-white/[0.08]">
            {loading && (
              <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/70 backdrop-blur-sm">
                <div className="w-full absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-radar-sweep shadow-[0_0_15px_#10b981]" />
                <Radar className="h-10 w-10 text-emerald-400 animate-spin mb-3" />
                <p className="text-xs font-mono font-bold text-emerald-300 tracking-wider">
                  SCANNING ORTHOMOSAIC · YOLOv11 + SAHI TILES
                </p>
                <span className="text-[10px] text-slate-400 font-mono mt-1">Processing 512x512 native resolution patches...</span>
              </div>
            )}

            {result ? (
              <img src={result.annotated_image} alt="Detections" className="max-h-[520px] w-auto object-contain rounded-lg" />
            ) : preview ? (
              <img src={preview} alt="Preview" className="max-h-[520px] w-auto object-contain rounded-lg" />
            ) : (
              <div className="text-center text-slate-500 p-8">
                <Trees className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p className="text-xs font-medium text-slate-400">No aerial imagery loaded</p>
                <button
                  onClick={loadDemoSample}
                  type="button"
                  className="mt-3 text-xs text-emerald-400 hover:underline flex items-center gap-1 mx-auto"
                >
                  <Zap className="h-3 w-3" />
                  Load sample drone photo to test
                </button>
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

  const loadDemo = async () => {
    const demo = await fetchSampleAsFile("/samples/sample_canopy.jpg", "demo_canopy.jpg");
    setFile(demo);
    setPreview("/samples/sample_canopy.jpg");
    setResult(null);
  };

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
      <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Layers className="h-4 w-4 text-emerald-400" />
            Spectral Indices
          </h3>
          <button
            onClick={loadDemo}
            type="button"
            className="text-[11px] font-bold text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 px-2.5 py-1 rounded-lg flex items-center gap-1 transition active:scale-95"
          >
            <Zap className="h-3 w-3" />
            <span>Load Demo</span>
          </button>
        </div>

        <label className="border-2 border-dashed border-white/[0.12] hover:border-emerald-500/60 rounded-xl p-5 flex flex-col items-center justify-center cursor-pointer transition bg-black/20 group">
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
          <Layers className="h-7 w-7 text-emerald-400 mb-1 group-hover:scale-110 transition-transform" />
          <span className="text-xs font-semibold text-slate-200 truncate max-w-[200px]">
            {file ? file.name : "Upload Orthomosaic"}
          </span>
          <span className="text-[10px] text-slate-400 mt-1">RGB Aerial Survey Image</span>
        </label>

        <div>
          <label className="text-xs font-medium text-slate-300 block mb-1">Index Equation</label>
          <select
            value={method}
            onChange={(e) => {
              const m = e.target.value;
              setMethod(m);
              setThreshold(m === "VARI" ? 0.05 : m === "GLI" ? 0.1 : m === "EXG" ? 0.05 : 0.8);
            }}
            className="w-full text-xs bg-[#0b0e16] border border-white/[0.12] rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="VARI">VARI — (G - R) / (G + R - B)</option>
            <option value="GLI">GLI — (2G - R - B) / (2G + R + B)</option>
            <option value="EXG">ExG — 2G - R - B (Excess Green)</option>
            <option value="HSV">HSV — Hue/Saturation Segmentation</option>
          </select>
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
            <span>Sensitivity Threshold</span>
            <span className="font-mono text-emerald-400 font-bold">{threshold.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="-0.3"
            max="1.0"
            step="0.02"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-emerald-500"
          />
        </div>

        <button
          onClick={handleRun}
          disabled={!file || loading}
          className={`w-full py-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            !file || loading
              ? "bg-white/[0.05] text-slate-500 cursor-not-allowed border border-white/[0.05]"
              : "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-[0_4px_16px_rgba(16,185,129,0.35),inset_0_1px_0_rgba(255,255,255,0.4)] active:scale-[0.98]"
          }`}
        >
          {loading ? <RefreshCw className="h-4 w-4 animate-spin text-slate-950" /> : <Layers className="h-4 w-4" />}
          <span>Compute Vegetation Mask</span>
        </button>
      </div>

      <div className="lg:col-span-2 space-y-4">
        {result && (
          <div className="grid grid-cols-3 gap-3">
            <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Canopy Fraction</span>
              <p className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">{result.canopy_percentage}%</p>
            </div>
            <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Barren / Non-Green</span>
              <p className="text-2xl font-extrabold font-mono text-amber-400 mt-1">{result.barren_percentage}%</p>
            </div>
            <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Classification</span>
              <p className="text-xs font-bold text-slate-200 mt-2.5">{result.ecological_classification}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">Canopy Segmentation</h4>
            <div className="h-72 rounded-xl bg-black/40 flex items-center justify-center overflow-hidden border border-white/[0.08]">
              {result ? (
                <img src={result.overlay_image} alt="Overlay" className="h-full w-full object-contain" />
              ) : preview ? (
                <img src={preview} alt="Raw" className="h-full w-full object-contain opacity-50" />
              ) : (
                <span className="text-xs text-slate-500 font-medium">Awaiting imagery</span>
              )}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">Spectral Biomass Heatmap</h4>
            <div className="h-72 rounded-xl bg-black/40 flex items-center justify-center overflow-hidden border border-white/[0.08]">
              {result ? (
                <img src={result.heatmap_image} alt="Heatmap" className="h-full w-full object-contain" />
              ) : (
                <span className="text-xs text-slate-500 font-medium">Awaiting computation</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 4. Change Detection Tab with 1-Click Temporal Demos
// ----------------------------------------------------------------------
function ChangeTab() {
  const [baseFile, setBaseFile] = useState<File | null>(null);
  const [monFile, setMonFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChangeResult | null>(null);

  const loadDemoPair = async () => {
    const fA = await fetchSampleAsFile("/samples/sample_baseline.jpg", "baseline_time_a.jpg");
    const fB = await fetchSampleAsFile("/samples/sample_monitoring.jpg", "monitoring_time_b.jpg");
    setBaseFile(fA);
    setMonFile(fB);
    setResult(null);
  };

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
      <div className="flex items-center justify-between p-4 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08]">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <GitCompare className="h-4 w-4 text-emerald-400" />
            Bi-Temporal Comparative Analysis
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Upload historical baseline survey ($T_A$) and current monitoring survey ($T_B$)</p>
        </div>
        <button
          onClick={loadDemoPair}
          type="button"
          className="text-xs font-bold text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition active:scale-95"
        >
          <Zap className="h-3.5 w-3.5" />
          <span>Load Demo Survey Pair (T_A & T_B)</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08]">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Time A — Baseline (Historical)</h4>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && setBaseFile(e.target.files[0])}
            className="text-xs text-slate-300 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-white/[0.08] file:text-slate-200 hover:file:bg-white/[0.15] cursor-pointer"
          />
          {baseFile && <p className="text-xs font-mono text-emerald-400 mt-2 truncate">Loaded: {baseFile.name}</p>}
        </div>

        <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08]">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Time B — Monitoring (Current)</h4>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && setMonFile(e.target.files[0])}
            className="text-xs text-slate-300 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-white/[0.08] file:text-slate-200 hover:file:bg-white/[0.15] cursor-pointer"
          />
          {monFile && <p className="text-xs font-mono text-emerald-400 mt-2 truncate">Loaded: {monFile.name}</p>}
        </div>
      </div>

      <button
        onClick={handleRun}
        disabled={!baseFile || !monFile || loading}
        className={`w-full py-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
          !baseFile || !monFile || loading
            ? "bg-white/[0.05] text-slate-500 cursor-not-allowed border border-white/[0.05]"
            : "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-[0_4px_16px_rgba(16,185,129,0.35),inset_0_1px_0_rgba(255,255,255,0.4)] active:scale-[0.98]"
        }`}
      >
        {loading ? <RefreshCw className="h-4 w-4 animate-spin text-slate-950" /> : <GitCompare className="h-4 w-4" />}
        <span>Compare Bi-Temporal Canopy</span>
      </button>

      {result && (
        <div className="space-y-4">
          <div
            className={`p-4 rounded-xl border flex items-center justify-between ${
              result.alert_level === "CRITICAL_ALERT"
                ? "bg-rose-500/15 border-rose-500/30 text-rose-300"
                : result.alert_level === "WARNING"
                ? "bg-amber-500/15 border-amber-500/30 text-amber-300"
                : "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
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
            <span className="text-xl font-mono font-extrabold">{result.percent_delta}%</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08]">
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-2">
                <span>Baseline (Time A)</span>
                <span className="font-mono text-emerald-400 font-bold">{result.count_baseline} crowns</span>
              </div>
              <img src={result.baseline_annotated} alt="Time A" className="w-full h-72 object-contain rounded-xl bg-black/40" />
            </div>

            <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08]">
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-2">
                <span>Monitoring (Time B)</span>
                <span className="font-mono text-emerald-400 font-bold">{result.count_monitoring} crowns</span>
              </div>
              <img src={result.monitoring_annotated} alt="Time B" className="w-full h-72 object-contain rounded-xl bg-black/40" />
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

  const loadDemo = async () => {
    const demo = await fetchSampleAsFile("/samples/sample_canopy.jpg", "demo_terrain.jpg");
    setFile(demo);
    setPreview("/samples/sample_canopy.jpg");
    setResult(null);
  };

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
      <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Compass className="h-4 w-4 text-emerald-400" />
            A* Waypoint Coordinates
          </h3>
          <button
            onClick={loadDemo}
            type="button"
            className="text-[11px] font-bold text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 px-2.5 py-1 rounded-lg flex items-center gap-1 transition active:scale-95"
          >
            <Zap className="h-3 w-3" />
            <span>Load Demo</span>
          </button>
        </div>

        <label className="border-2 border-dashed border-white/[0.12] hover:border-emerald-500/60 rounded-xl p-5 flex flex-col items-center justify-center cursor-pointer transition bg-black/20 group">
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
          <Compass className="h-7 w-7 text-emerald-400 mb-1 group-hover:scale-110 transition-transform" />
          <span className="text-xs font-semibold text-slate-200 truncate max-w-[200px]">{file ? file.name : "Upload Terrain Image"}</span>
          <span className="text-[10px] text-slate-400 mt-1">Cost surface for 8-way traversal</span>
        </label>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[11px] text-slate-300 font-mono">Start (X, Y)</label>
            <div className="flex gap-1.5 mt-1">
              <input
                type="number"
                value={startX}
                onChange={(e) => setStartX(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-[#0b0e16] border border-white/[0.12] rounded-lg p-2 text-emerald-400 font-bold"
              />
              <input
                type="number"
                value={startY}
                onChange={(e) => setStartY(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-[#0b0e16] border border-white/[0.12] rounded-lg p-2 text-emerald-400 font-bold"
              />
            </div>
          </div>

          <div>
            <label className="text-[11px] text-slate-300 font-mono">Target (X, Y)</label>
            <div className="flex gap-1.5 mt-1">
              <input
                type="number"
                value={endX}
                onChange={(e) => setEndX(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-[#0b0e16] border border-white/[0.12] rounded-lg p-2 text-rose-400 font-bold"
              />
              <input
                type="number"
                value={endY}
                onChange={(e) => setEndY(parseInt(e.target.value) || 0)}
                className="w-full text-xs font-mono bg-[#0b0e16] border border-white/[0.12] rounded-lg p-2 text-rose-400 font-bold"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={!file || loading}
          className={`w-full py-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            !file || loading
              ? "bg-white/[0.05] text-slate-500 cursor-not-allowed border border-white/[0.05]"
              : "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-[0_4px_16px_rgba(16,185,129,0.35),inset_0_1px_0_rgba(255,255,255,0.4)] active:scale-[0.98]"
          }`}
        >
          {loading ? <RefreshCw className="h-4 w-4 animate-spin text-slate-950" /> : <Compass className="h-4 w-4" />}
          <span>Calculate Optimal Trajectory</span>
        </button>
      </div>

      <div className="lg:col-span-2 space-y-4">
        {result && (
          <div className="grid grid-cols-3 gap-3">
            <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Path Length</span>
              <p className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">{result.path_length_px} px</p>
            </div>
            <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Traversal Cost</span>
              <p className="text-2xl font-extrabold font-mono text-cyan-400 mt-1">{result.total_cost}</p>
            </div>
            <div className="p-4 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-md">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">A* Execution Latency</span>
              <p className="text-2xl font-extrabold font-mono text-slate-200 mt-1">{result.elapsed_time_ms} ms</p>
            </div>
          </div>
        )}

        <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">A* Route Visualization</h4>
          <div className="h-80 rounded-xl bg-black/40 flex items-center justify-center overflow-hidden border border-white/[0.08]">
            {result ? (
              <img src={result.path_image} alt="Route" className="h-full w-full object-contain" />
            ) : preview ? (
              <img src={preview} alt="Preview" className="h-full w-full object-contain opacity-50" />
            ) : (
              <span className="text-xs text-slate-500 font-medium">Awaiting terrain map</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// 6. Telemetry Tab (Enhanced with GPS, Forest Presets, Drone Flight Radar)
// ----------------------------------------------------------------------
function TelemetryTab() {
  const [city, setCity] = useState("Bhopal Forest Division");
  const [latInput, setLatInput] = useState<string>("23.2547");
  const [lonInput, setLonInput] = useState<string>("77.4029");
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [data, setData] = useState<TelemetryResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const forestPresets = [
    { name: "Jim Corbett Reserve", lat: 29.5300, lon: 78.7747, tag: "Tiger Reserve, India" },
    { name: "Amazon Basin", lat: -3.4653, lon: -62.2159, tag: "Rainforest, Brazil" },
    { name: "Black Forest", lat: 48.1800, lon: 8.1600, tag: "Schwarzwald, Germany" },
    { name: "Redwood National Park", lat: 41.2132, lon: -124.0046, tag: "California, USA" },
    { name: "Sundarbans Mangrove", lat: 21.9497, lon: 89.1833, tag: "Mangrove Biosphere" },
    { name: "Bandhavgarh Reserve", lat: 23.6800, lon: 81.0200, tag: "Central Zone, India" },
  ];

  const loadTelemetry = async (cityName?: string, latitude?: number, longitude?: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchClimateTelemetry(cityName, latitude, longitude);
      setData(res);
      setLatInput(res.latitude.toString());
      setLonInput(res.longitude.toString());
      if (res.location_name) setCity(res.location_name);
    } catch (err: any) {
      setError(err.message || "Failed to retrieve telemetry data");
    } finally {
      setLoading(false);
    }
  };

  const handleDetectGPS = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocating(false);
        const { latitude, longitude } = pos.coords;
        loadTelemetry(undefined, latitude, longitude);
      },
      (err) => {
        setLocating(false);
        setError(`GPS Access Denied: ${err.message}. Using manual coordinates.`);
      },
      { timeout: 8000 }
    );
  };

  const handleCoordinateSearch = () => {
    const lat = parseFloat(latInput);
    const lon = parseFloat(lonInput);
    if (!isNaN(lat) && !isNaN(lon)) {
      loadTelemetry(undefined, lat, lon);
    } else {
      loadTelemetry(city);
    }
  };

  useEffect(() => {
    loadTelemetry("Bhopal Forest Division", 23.2547, 77.4029);
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Search & Location Bar */}
      <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadTelemetry(city)}
              placeholder="Search forest division, city, or jurisdiction..."
              className="w-full pl-10 pr-4 py-2.5 text-xs bg-[#0b0e16] border border-white/[0.12] rounded-xl text-slate-200 focus:outline-none focus:border-emerald-500 font-medium"
            />
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 bg-[#0b0e16] border border-white/[0.12] rounded-xl px-2.5 py-1.5 text-xs font-mono">
              <span className="text-slate-500 font-bold">LAT</span>
              <input
                type="text"
                value={latInput}
                onChange={(e) => setLatInput(e.target.value)}
                className="w-16 bg-transparent text-emerald-400 font-bold focus:outline-none"
              />
              <span className="text-slate-500 font-bold ml-1">LON</span>
              <input
                type="text"
                value={lonInput}
                onChange={(e) => setLonInput(e.target.value)}
                className="w-16 bg-transparent text-emerald-400 font-bold focus:outline-none"
              />
            </div>

            <button
              onClick={handleCoordinateSearch}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md active:scale-95 transition"
            >
              {loading ? <RefreshCw className="h-3.5 w-3.5 animate-spin text-slate-950" /> : <Search className="h-3.5 w-3.5" />}
              <span>Query</span>
            </button>

            <button
              onClick={handleDetectGPS}
              type="button"
              className="px-3.5 py-2.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1.5 transition active:scale-95"
            >
              {locating ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <MapPin className="h-3.5 w-3.5 text-emerald-400" />}
              <span>My GPS</span>
            </button>
          </div>
        </div>

        {/* 1-Click Forest Reserve Presets */}
        <div>
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <Trees className="h-3 w-3 text-emerald-400" />
            Quick Presets (Major Forest Reserves)
          </div>
          <div className="flex flex-wrap gap-2">
            {forestPresets.map((p) => (
              <button
                key={p.name}
                onClick={() => {
                  setCity(p.name);
                  loadTelemetry(p.name, p.lat, p.lon);
                }}
                className="px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-emerald-500/15 border border-white/[0.08] hover:border-emerald-500/30 text-[11px] text-slate-300 hover:text-emerald-300 font-medium transition active:scale-95 flex items-center gap-1.5"
              >
                <span>{p.name}</span>
                <span className="text-[9px] font-mono text-slate-500 font-bold">({p.lat.toFixed(1)}°, {p.lon.toFixed(1)}°)</span>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {data && (
        <div className="space-y-6">
          {/* Active Jurisdiction Badge & Drone Flight Safety HUD */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] flex flex-col justify-between">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Field Jurisdiction</span>
                <h3 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-emerald-400" />
                  {data.location_name}
                </h3>
                <p className="text-xs text-slate-400 mt-1 font-mono">
                  Coordinates: <strong className="text-emerald-300 font-bold">{data.latitude}°N, {data.longitude}°E</strong>
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Atmosphere Source</span>
                <span className="text-emerald-400 font-bold">Open-Meteo Radar</span>
              </div>
            </div>

            {/* Drone Flight Clearance HUD */}
            <div className={`p-5 rounded-2xl border flex flex-col justify-between lg:col-span-2 ${
              data.flight_status.status === "OPTIMAL_CLEARANCE"
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                : data.flight_status.status === "CAUTION_ADVISORY"
                ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                : "bg-rose-500/10 border-rose-500/30 text-rose-300"
            }`}>
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider font-mono">UAV Flight Clearance Status</span>
                  <div className="flex items-center gap-2 mt-1">
                    <ShieldCheck className="h-5 w-5" />
                    <h4 className="text-lg font-extrabold tracking-wide font-mono">
                      {data.flight_status.status.replace("_", " ")}
                    </h4>
                  </div>
                </div>
                <div className="px-3 py-1 rounded-full bg-black/40 border border-current text-xs font-mono font-bold">
                  {data.weather.weather_condition}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4 pt-3 border-t border-current/20 text-xs">
                <div>
                  <span className="text-[10px] opacity-75 uppercase font-mono">Wind Parameter</span>
                  <p className="font-semibold mt-0.5">{data.flight_status.wind_clearance}</p>
                </div>
                <div>
                  <span className="text-[10px] opacity-75 uppercase font-mono">Atmospheric Optical Clarity</span>
                  <p className="font-semibold mt-0.5">{data.flight_status.visibility_clearance}</p>
                </div>
                <div>
                  <span className="text-[10px] opacity-75 uppercase font-mono">VARI / GLI Sunlight Viability</span>
                  <p className="font-semibold mt-0.5">{data.flight_status.solar_imaging_viability}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Microclimate Matrix */}
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Thermometer className="h-4 w-4 text-emerald-400" />
              Microclimate Atmospheric Telemetry
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center gap-1.5">
                  <Thermometer className="h-3.5 w-3.5 text-amber-400" /> Temperature
                </span>
                <p className="text-2xl font-extrabold font-mono text-slate-100 mt-1.5">{data.weather.temperature_c}°C</p>
                <span className="text-[10px] text-slate-500 font-mono">Feels like {data.weather.apparent_temp_c}°C</span>
              </div>

              <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center gap-1.5">
                  <Droplets className="h-3.5 w-3.5 text-cyan-400" /> Relative Humidity
                </span>
                <p className="text-2xl font-extrabold font-mono text-slate-100 mt-1.5">{data.weather.humidity_pct}%</p>
                <span className="text-[10px] text-slate-500 font-mono">Cloud Cover: {data.weather.cloud_cover_pct}%</span>
              </div>

              <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center gap-1.5">
                  <Wind className="h-3.5 w-3.5 text-emerald-400" /> Wind Velocity
                </span>
                <p className="text-2xl font-extrabold font-mono text-slate-100 mt-1.5">{data.weather.wind_speed_kmh} km/h</p>
                <span className="text-[10px] text-slate-500 font-mono">Peak Gusts: {data.weather.wind_gusts_kmh} km/h</span>
              </div>

              <div className="p-5 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-md">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center gap-1.5">
                  <Zap className="h-3.5 w-3.5 text-yellow-400" /> Solar Irradiance
                </span>
                <p className="text-2xl font-extrabold font-mono text-yellow-400 mt-1.5">{data.weather.direct_solar_irradiance} W/m²</p>
                <span className="text-[10px] text-slate-500 font-mono">Direct Nadir Radiation</span>
              </div>
            </div>
          </div>

          {/* Air Quality & Chemical Matrix */}
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-purple-400" />
                Atmospheric Chemistry & Air Quality Index
              </div>
              <span className="text-xs font-mono text-purple-300 font-bold bg-purple-500/10 border border-purple-500/20 px-2.5 py-0.5 rounded-full">
                US AQI: {data.air_quality.us_aqi} · {data.air_quality.aqi_category}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {[
                { label: "PM2.5", val: `${data.air_quality.pm2_5}`, unit: "µg/m³", desc: "Fine Particles" },
                { label: "PM10", val: `${data.air_quality.pm10}`, unit: "µg/m³", desc: "Coarse Dust" },
                { label: "NO₂", val: `${data.air_quality.no2}`, unit: "µg/m³", desc: "Nitrogen Dioxide" },
                { label: "SO₂", val: `${data.air_quality.so2}`, unit: "µg/m³", desc: "Sulphur Dioxide" },
                { label: "CO", val: `${data.air_quality.co}`, unit: "µg/m³", desc: "Carbon Monoxide" },
                { label: "Ozone", val: `${data.air_quality.ozone}`, unit: "µg/m³", desc: "Ground Ozone" },
                { label: "AOD", val: `${data.air_quality.aerosol_optical_depth}`, unit: "Index", desc: "Optical Depth" },
              ].map((pollutant) => (
                <div key={pollutant.label} className="p-3.5 rounded-xl bg-[#0f141e]/90 border border-white/[0.08] text-center shadow-sm">
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wide">{pollutant.label}</span>
                  <p className="text-lg font-extrabold font-mono text-slate-100 mt-1">{pollutant.val}</p>
                  <span className="text-[9px] text-slate-500 font-mono block">{pollutant.unit}</span>
                  <span className="text-[9px] text-slate-400 block mt-1">{pollutant.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Forestry & Wildfire Risk Assessment Card */}
          <div className="p-6 rounded-2xl bg-[#0f141e]/90 border border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="h-4 w-4" />
                Forestry Ecology & Wildfire Threat Assessment
              </h4>
              <span className={`text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full ${
                data.forest_risk.wildfire_risk_level === "EXTREME"
                  ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                  : data.forest_risk.wildfire_risk_level === "ELEVATED"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                  : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
              }`}>
                Wildfire Threat: {data.forest_risk.wildfire_risk_level}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 rounded-xl bg-black/20 border border-white/[0.06]">
                <span className="text-[10px] text-slate-400 uppercase font-mono">Canopy Heat Stress</span>
                <p className="text-slate-200 font-semibold mt-1">{data.forest_risk.canopy_heat_stress}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-black/20 border border-white/[0.06]">
                <span className="text-[10px] text-slate-400 uppercase font-mono">Irrigation Guidance</span>
                <p className="text-slate-200 font-semibold mt-1">{data.forest_risk.recommended_irrigation}</p>
              </div>
            </div>

            <div className="pt-2 border-t border-white/[0.08]">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wide mb-2">Automated Field Recommendations</div>
              <ul className="space-y-2 text-xs text-slate-300">
                {data.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2.5">
                    <span className="text-emerald-400 font-bold mt-0.5">•</span>
                    <span className="leading-relaxed">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useRef, useMemo } from "react";
import { Play, Pause, RotateCcw, Upload, Crosshair, FileUp } from "lucide-react";

const TelemetryVisualizer = () => {
  const [data, setData] = useState([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [fileName, setFileName] = useState("");
  
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const fileInputRef = useRef(null);

  // File Upload Logic
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.trim().split("\n");
      
      const parsed = lines
        .slice(1) // Skip header
        .map((line) => {
          const [ts, type, x, y, hit] = line.split(",");
          return {
            ts: parseInt(ts),
            type: type.trim(),
            y: parseFloat(x), // Cam_Rot_X (Vertical)
            x: parseFloat(y), // Player_Rot_Y (Horizontal)
            hit: parseInt(hit),
          };
        })
        .filter((d) => !isNaN(d.ts))
        .sort((a, b) => a.ts - b.ts);

      setData(parsed);
      setCurrentTime(0);
      setIsPlaying(false);
    };
    
    reader.readAsText(file);
  };

  const bounds = useMemo(() => {
    if (data.length === 0)
      return { minX: -1, maxX: 1, minY: -1, maxY: 1, maxTs: 0 };

    const xs = data.map((d) => d.x);
    const ys = data.map((d) => d.y);
    const padding = 0.05;

    return {
      minX: Math.min(...xs) - padding,
      maxX: Math.max(...xs) + padding,
      minY: Math.min(...ys) - padding,
      maxY: Math.max(...ys) + padding,
      maxTs: Math.max(...data.map((d) => d.ts)),
    };
  }, [data]);

  useEffect(() => {
    if (isPlaying && data.length > 0) {
      let lastFrameTime = performance.now();

      const animate = (now) => {
        const deltaTime = (now - lastFrameTime) * playbackSpeed;
        lastFrameTime = now;

        setCurrentTime((prev) => {
          const next = prev + deltaTime;
          if (next >= bounds.maxTs) {
            setIsPlaying(false);
            return bounds.maxTs;
          }
          return next;
        });
        animationRef.current = requestAnimationFrame(animate);
      };
      animationRef.current = requestAnimationFrame(animate);
    } else {
      cancelAnimationFrame(animationRef.current);
    }
    return () => cancelAnimationFrame(animationRef.current);
  }, [isPlaying, playbackSpeed, bounds.maxTs, data.length]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || data.length === 0) return;
    const ctx = canvas.getContext("2d");
    const { width: w, height: h } = canvas;

    const mapX = (val) => ((val - bounds.minX) / (bounds.maxX - bounds.minX)) * w;
    const mapY = (val) => ((val - bounds.minY) / (bounds.maxY - bounds.minY)) * h;

    ctx.fillStyle = "#020617";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1;
    for (let i = 1; i < 10; i++) {
      ctx.beginPath();
      ctx.moveTo((i * w) / 10, 0);
      ctx.lineTo((i * w) / 10, h);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, (i * h) / 10);
      ctx.lineTo(w, (i * h) / 10);
      ctx.stroke();
    }

    const visibleData = data.filter((d) => d.ts <= currentTime);

    ctx.beginPath();
    ctx.strokeStyle = "#00f2ff";
    ctx.lineWidth = 2;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.shadowBlur = 12;
    ctx.shadowColor = "#00f2ff";

    let pathStarted = false;
    visibleData.forEach((d) => {
      if (d.type === "MouseMove") {
        const px = mapX(d.x);
        const py = mapY(d.y);
        if (!pathStarted) {
          ctx.moveTo(px, py);
          pathStarted = true;
        } else {
          ctx.lineTo(px, py);
        }
      }
    });
    ctx.stroke();
    ctx.shadowBlur = 0;

    visibleData.forEach((d) => {
      if (d.type === "ShotFired") {
        const sx = mapX(d.x);
        const sy = mapY(d.y);

        ctx.beginPath();
        ctx.arc(sx, sy, 7, 0, Math.PI * 2);

        if (d.hit >= 0) {
          ctx.fillStyle = "#10b981";
          ctx.shadowBlur = 15;
          ctx.shadowColor = "#10b981";
        } else {
          ctx.fillStyle = "#f43f5e";
          ctx.shadowBlur = 15;
          ctx.shadowColor = "#f43f5e";
        }

        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.shadowBlur = 0;
      }
    });

    const lastPos = visibleData.findLast((d) => d.type === "MouseMove");
    if (lastPos) {
      const rx = mapX(lastPos.x);
      const ry = mapY(lastPos.y);
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(rx - 15, ry);
      ctx.lineTo(rx + 15, ry);
      ctx.moveTo(rx, ry - 15);
      ctx.lineTo(rx, ry + 15);
      ctx.stroke();
      
      ctx.beginPath();
      ctx.arc(rx, ry, 4, 0, Math.PI * 2);
      ctx.stroke();
    }
  }, [data, currentTime, bounds]);

  return (
    <div className="flex flex-col gap-4 p-6 bg-slate-950 text-slate-100 rounded-2xl border border-slate-800 shadow-2xl w-full max-w-5xl mx-auto font-sans">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <Crosshair className="text-cyan-400" size={24} />
          </div>
          <div>
            <h1 className="text-lg font-black uppercase tracking-tighter text-white">
              Trial Telemetry
            </h1>
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">
              3D Aim Trainer v1.0
            </p>
          </div>
        </div>
        <div className="text-right font-mono">
          <div className="text-xs text-slate-500 uppercase">Current Time</div>
          <div className="text-xl text-cyan-400 font-bold tracking-tighter">
            {Math.floor(currentTime).toLocaleString()}{" "}
            <span className="text-slate-600 text-sm">ms</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Upload Controls */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
              Data Source
            </label>
            
            <input 
              type="file" 
              accept=".csv" 
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden" 
            />
            
            <button
              onClick={() => fileInputRef.current.click()}
              className="flex flex-col items-center justify-center gap-2 bg-slate-900 border-2 border-dashed border-slate-700 hover:border-cyan-400 hover:bg-slate-800 transition-all p-8 rounded-xl text-slate-400 hover:text-cyan-400 h-80"
            >
              <FileUp size={32} />
              <span className="text-xs font-bold uppercase tracking-wider text-center">
                {fileName ? "Select Different File" : "Upload CSV File"}
              </span>
              {fileName && (
                <span className="text-[10px] text-slate-500 font-mono mt-4 break-all px-2 text-center">
                  Loaded: {fileName}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Visualizer Area */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-black aspect-video shadow-inner">
            <canvas
              ref={canvasRef}
              width={1200}
              height={675}
              className="w-full h-full cursor-crosshair"
            />
            {data.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-950/90 backdrop-blur-sm">
                <div className="text-center">
                  <Upload className="mx-auto text-slate-700 mb-2" size={48} />
                  <p className="text-slate-500 font-medium uppercase tracking-widest text-xs">Awaiting Data</p>
                </div>
              </div>
            )}
          </div>

          {/* Timeline & Playback */}
          <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <button
                disabled={data.length === 0}
                onClick={() => setIsPlaying(!isPlaying)}
                className={`p-3 rounded-full transition-all ${
                  isPlaying
                    ? "bg-red-500/10 text-red-400"
                    : "bg-cyan-500 text-slate-950 hover:bg-cyan-400 disabled:opacity-50 disabled:bg-slate-800 disabled:text-slate-600"
                }`}
              >
                {isPlaying ? <Pause size={24} /> : <Play size={24} fill="currentColor" />}
              </button>

              <button
                disabled={data.length === 0}
                onClick={() => {
                  setCurrentTime(0);
                  setIsPlaying(false);
                }}
                className="p-3 rounded-full bg-slate-800 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
              >
                <RotateCcw size={20} />
              </button>

              <div className="flex-1 px-2">
                <input
                  type="range"
                  min="0"
                  max={bounds.maxTs || 0}
                  value={currentTime}
                  onChange={(e) => {
                    setCurrentTime(parseInt(e.target.value));
                    setIsPlaying(false);
                  }}
                  disabled={data.length === 0}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 hover:accent-cyan-300 transition-all disabled:opacity-50"
                />
              </div>

              <div className="flex flex-col items-end min-w-[60px]">
                <span className="text-[9px] text-slate-500 uppercase font-bold">
                  Speed
                </span>
                <select
                  value={playbackSpeed}
                  onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                  disabled={data.length === 0}
                  className="bg-transparent text-sm font-bold text-cyan-400 focus:outline-none cursor-pointer disabled:opacity-50"
                >
                  <option value="0.5">0.5x</option>
                  <option value="1">1.0x</option>
                  <option value="2">2.0x</option>
                  <option value="5">5.0x</option>
                </select>
              </div>
            </div>

            <div className="flex justify-center gap-8 border-t border-slate-800 pt-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#22d3ee]"></div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Movement</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Target Hit</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_#f43f5e]"></div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Miss</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelemetryVisualizer;
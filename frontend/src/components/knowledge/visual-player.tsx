"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Sparkles,
  ExternalLink,
  Code2,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Activity,
  Layers,
  Database,
  ArrowRight,
} from "lucide-react";
import { api } from "@/lib/api";

interface VisualLessonStep {
  step: number;
  stage: string;
  stage_id: string;
  active_node: string;
  text_en: string;
  text_id: string;
  sql_state: string;
}

interface VisualLesson {
  slug: string;
  title: string;
  title_id: string;
  category: string;
  estimated_minutes: number;
  description_en: string;
  description_id: string;
  steps: VisualLessonStep[];
}

interface VisualPlayerProps {
  language?: "en" | "id";
  onOpenLab?: () => void;
}

export function VisualDatabaseAcademy({
  language = "id",
  onOpenLab,
}: VisualPlayerProps) {
  const isId = language === "id";
  const [lessons, setLessons] = useState<VisualLesson[]>([]);
  const [activeLesson, setActiveLesson] = useState<VisualLesson | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [bTreeSelectivity, setBTreeSelectivity] = useState<number>(1); // 1 to 50%
  const [tableRowCount, setTableRowCount] = useState<number>(100000);

  useEffect(() => {
    api
      .get("/knowledge/visual-lessons")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setLessons(res.data);
          setActiveLesson(res.data[0]);
        }
      })
      .catch((err) => console.error("Error fetching visual lessons:", err));
  }, []);

  // Playback timer loop
  useEffect(() => {
    if (!isPlaying || !activeLesson) return;

    const intervalTime = 3000 / playbackSpeed;
    const timer = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev >= activeLesson.steps.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, intervalTime);

    return () => clearInterval(timer);
  }, [isPlaying, activeLesson, playbackSpeed]);

  const handleLessonChange = (lesson: VisualLesson) => {
    setActiveLesson(lesson);
    setCurrentStepIndex(0);
    setIsPlaying(false);
  };

  const handleNextStep = () => {
    if (!activeLesson) return;
    if (currentStepIndex < activeLesson.steps.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
    }
  };

  const handlePrevStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  };

  const handleReset = () => {
    setCurrentStepIndex(0);
    setIsPlaying(false);
  };

  if (!activeLesson) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400 text-xs">
        Memuat Akademi Visual...
      </div>
    );
  }

  const currentStep = activeLesson.steps[currentStepIndex] || activeLesson.steps[0];
  const totalSteps = activeLesson.steps.length;
  const progressPct = ((currentStepIndex + 1) / totalSteps) * 100;

  return (
    <div className="flex flex-col xl:flex-row h-full w-full overflow-hidden bg-[#071A3A] text-slate-100">
      {/* SIDEBAR: Lesson Selector */}
      <div className="w-full xl:w-80 shrink-0 border-b xl:border-b-0 xl:border-r border-slate-800 bg-[#0A1B38]/90 p-3 sm:p-4 flex flex-col gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="h-4 w-4 text-[#F2B84B]" />
            <h2 className="text-sm font-bold text-white tracking-wide">
              {isId ? "Katalog Simulasi Visual" : "Visual Simulation Catalog"}
            </h2>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            {isId
              ? "Pelajari mekanisme internal database yang tidak kasat mata melalui simulasi visual langkah-demi-langkah."
              : "Explore invisible database internals through interactive step-by-step technical animations."}
          </p>
        </div>

        {/* Lesson Cards */}
        <div className="flex xl:flex-col gap-2 overflow-x-auto xl:overflow-y-auto no-scrollbar touch-scroll pb-2 xl:pb-0">
          {lessons.map((lesson) => {
            const isSelected = activeLesson.slug === lesson.slug;
            return (
              <button
                key={lesson.slug}
                onClick={() => handleLessonChange(lesson)}
                className={`flex flex-col text-left p-3 rounded-xl border transition-all shrink-0 w-64 xl:w-full min-h-[72px] active:scale-95 ${
                  isSelected
                    ? "bg-[#10264A] border-[#F2B84B] ring-1 ring-[#F2B84B]/40 shadow-sm"
                    : "bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300"
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[9px] font-mono text-[#F2B84B] border border-slate-700">
                    {lesson.category}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    ~{lesson.estimated_minutes} min
                  </span>
                </div>
                <h3 className="text-xs font-bold text-white leading-snug line-clamp-1">
                  {isId ? lesson.title_id : lesson.title}
                </h3>
                <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                  {isId ? lesson.description_id : lesson.description_en}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* MAIN VIEWPORT: Simulation Canvas & Control Dock */}
      <div className="flex flex-1 flex-col overflow-y-auto no-scrollbar p-3 sm:p-5 gap-4">
        {/* Title Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-[#F2B84B]/20 text-[#F2B84B] border border-[#F2B84B]/40 px-2 py-0.5 text-[10px] font-mono font-bold uppercase">
                {activeLesson.category}
              </span>
              <h1 className="text-base sm:text-lg font-bold text-white">
                {isId ? activeLesson.title_id : activeLesson.title}
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              {isId ? activeLesson.description_id : activeLesson.description_en}
            </p>
          </div>

          {onOpenLab && (
            <button
              onClick={onOpenLab}
              className="flex items-center gap-1.5 rounded-lg bg-[#10264A] hover:bg-[#F2B84B] hover:text-[#071A3A] border border-[#F2B84B]/40 px-3 py-1.5 text-xs font-bold text-[#F2B84B] transition-colors shrink-0 self-start sm:self-auto min-h-[38px] active:scale-95"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              <span>{isId ? "Eksperimen di Studio & Lab" : "Open in Studio Lab"}</span>
            </button>
          )}
        </div>

        {/* INTERACTIVE SIMULATION CANVAS */}
        <div className="relative w-full rounded-2xl border border-slate-700/80 bg-[#051329] p-4 sm:p-6 shadow-xl flex flex-col justify-between min-h-[280px] sm:min-h-[340px] overflow-hidden">
          {/* Top Stage Indicator */}
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#F2B84B] text-[#071A3A] text-xs font-bold font-mono">
                {currentStepIndex + 1}
              </span>
              <span className="text-xs font-bold text-white tracking-wide">
                {isId ? currentStep.stage_id : currentStep.stage}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
              <span>
                {isId ? "Langkah" : "Step"} {currentStepIndex + 1} / {totalSteps}
              </span>
            </div>
          </div>

          {/* SVG Visual Schematic Area */}
          <div className="my-6 flex items-center justify-center w-full">
            {activeLesson.slug === "sql-execution-lifecycle" && (
              <SqlLifecycleVisual activeNode={currentStep.active_node} />
            )}
            {activeLesson.slug === "btree-vs-tablescan" && (
              <BTreeScanVisual
                activeNode={currentStep.active_node}
                selectivity={bTreeSelectivity}
                rowCount={tableRowCount}
              />
            )}
            {activeLesson.slug === "concurrency-locks-deadlocks" && (
              <DeadlockVisual activeNode={currentStep.active_node} />
            )}
          </div>

          {/* Interactive Parameters (if B-Tree lesson) */}
          {activeLesson.slug === "btree-vs-tablescan" && (
            <div className="rounded-xl bg-slate-900/90 border border-slate-800 p-3 flex flex-wrap items-center justify-between gap-3 text-xs mb-2">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">{isId ? "Selektivitas Filter:" : "Selectivity:"}</span>
                <input
                  type="range"
                  min="1"
                  max="40"
                  value={bTreeSelectivity}
                  onChange={(e) => setBTreeSelectivity(Number(e.target.value))}
                  className="w-24 sm:w-32 accent-[#F2B84B]"
                />
                <span className="font-mono text-[#F2B84B] font-bold">{bTreeSelectivity}%</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <span>{isId ? "Total Baris Tabel:" : "Total Table Rows:"}</span>
                <span className="font-mono font-bold text-white">{tableRowCount.toLocaleString()}</span>
              </div>
            </div>
          )}

          {/* State / Code Trace Box */}
          <div className="rounded-lg bg-slate-950/80 border border-slate-800 p-2.5 font-mono text-[11px] text-emerald-400 flex items-center gap-2">
            <Code2 className="h-4 w-4 text-[#F2B84B] shrink-0" />
            <span className="text-slate-400 shrink-0 font-sans text-[10px]">
              {isId ? "Status Internal:" : "Internal State:"}
            </span>
            <span className="truncate">{currentStep.sql_state}</span>
          </div>
        </div>

        {/* STEP EXPLANATION CARD */}
        <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-[#10264A] p-2 text-[#F2B84B] border border-[#F2B84B]/30 shrink-0 mt-0.5">
              <Zap className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white mb-0.5">
                {isId ? currentStep.stage_id : currentStep.stage}
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                {isId ? currentStep.text_id : currentStep.text_en}
              </p>
            </div>
          </div>
        </div>

        {/* INTERACTIVE CONTROLS DOCK */}
        <div className="sticky bottom-0 z-20 rounded-2xl border border-slate-800 bg-[#0d2140]/95 backdrop-blur-md p-3 flex flex-wrap items-center justify-between gap-3 shadow-2xl">
          {/* Play/Pause & Steppers */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-1.5 rounded-lg bg-[#F2B84B] text-[#071A3A] px-3.5 py-2 text-xs font-bold hover:bg-[#F2B84B]/90 transition-all shadow-md min-h-[40px] active:scale-95"
            >
              {isPlaying ? <Pause className="h-4 w-4 fill-current" /> : <Play className="h-4 w-4 fill-current" />}
              <span>{isPlaying ? (isId ? "Jeda" : "Pause") : (isId ? "Putar" : "Play")}</span>
            </button>

            <button
              onClick={handlePrevStep}
              disabled={currentStepIndex === 0}
              className="flex items-center justify-center rounded-lg bg-slate-900 border border-slate-700 p-2 text-slate-300 hover:text-white disabled:opacity-40 min-h-[40px] min-w-[40px] active:scale-95"
              title={isId ? "Langkah Sebelumnya" : "Previous Step"}
            >
              <SkipBack className="h-4 w-4" />
            </button>

            <button
              onClick={handleNextStep}
              disabled={currentStepIndex >= totalSteps - 1}
              className="flex items-center justify-center rounded-lg bg-slate-900 border border-slate-700 p-2 text-slate-300 hover:text-white disabled:opacity-40 min-h-[40px] min-w-[40px] active:scale-95"
              title={isId ? "Langkah Berikutnya" : "Next Step"}
            >
              <SkipForward className="h-4 w-4" />
            </button>

            <button
              onClick={handleReset}
              className="flex items-center gap-1 rounded-lg bg-slate-900/60 border border-slate-800 px-2.5 py-2 text-xs text-slate-400 hover:text-white min-h-[40px] active:scale-95"
              title={isId ? "Kembalikan ke Langkah 1" : "Reset to Step 1"}
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">{isId ? "Reset" : "Reset"}</span>
            </button>
          </div>

          {/* Progress Bar & Speed Selector */}
          <div className="flex items-center gap-3 flex-1 max-w-xs sm:max-w-sm justify-end">
            <div className="hidden sm:flex flex-col flex-1 gap-1">
              <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-[#F2B84B] transition-all duration-300 rounded-full"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>

            {/* Speed Selector */}
            <div className="flex items-center rounded-lg bg-slate-900 p-0.5 border border-slate-800">
              {[0.5, 1, 1.5].map((speed) => (
                <button
                  key={speed}
                  onClick={() => setPlaybackSpeed(speed)}
                  className={`px-2 py-1 text-[10px] font-mono font-bold rounded-md transition-all ${
                    playbackSpeed === speed
                      ? "bg-[#F2B84B] text-[#071A3A]"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// SVG COMPONENT 1: SQL Execution Lifecycle
// ----------------------------------------------------------------------------
function SqlLifecycleVisual({ activeNode }: { activeNode: string }) {
  const nodes = [
    { id: "client", label: "Client Socket" },
    { id: "parser", label: "SQL Parser" },
    { id: "catalog", label: "Semantic / Catalog" },
    { id: "optimizer", label: "Cost Optimizer" },
    { id: "buffer", label: "Buffer Pool Cache" },
    { id: "result", label: "Output Stream" },
  ];

  return (
    <div className="w-full max-w-3xl overflow-x-auto no-scrollbar py-2">
      <div className="flex items-center justify-between min-w-[620px] gap-2">
        {nodes.map((n, i) => {
          const isActive = activeNode === n.id;
          return (
            <React.Fragment key={n.id}>
              <div
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all ${
                  isActive
                    ? "bg-[#10264A] border-[#F2B84B] text-[#F2B84B] shadow-lg scale-105 ring-2 ring-[#F2B84B]/40"
                    : "bg-slate-900/80 border-slate-800 text-slate-400"
                }`}
                style={{ width: 105, height: 75 }}
              >
                <div className="text-[10px] font-mono text-slate-500 mb-0.5">0{i + 1}</div>
                <span className="text-[11px] font-bold leading-tight">{n.label}</span>
              </div>
              {i < nodes.length - 1 && (
                <ArrowRight
                  className={`h-4 w-4 shrink-0 transition-colors ${
                    isActive ? "text-[#F2B84B] animate-pulse" : "text-slate-700"
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// SVG COMPONENT 2: B-Tree Index vs Table Scan
// ----------------------------------------------------------------------------
function BTreeScanVisual({
  activeNode,
  selectivity,
  rowCount,
}: {
  activeNode: string;
  selectivity: number;
  rowCount: number;
}) {
  const isSeq = activeNode === "seq_scan";
  const isRoot = activeNode === "btree_root";
  const isLeaf = activeNode === "btree_leaf";

  return (
    <div className="w-full max-w-2xl flex flex-col gap-4 items-center">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
        {/* Table Scan Box */}
        <div
          className={`rounded-xl border p-4 transition-all ${
            isSeq
              ? "bg-rose-950/40 border-rose-500 ring-2 ring-rose-500/40"
              : "bg-slate-900/60 border-slate-800 opacity-60"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-rose-300">Sequential Table Scan</span>
            <span className="text-[10px] font-mono text-rose-400">O(N) Complexity</span>
          </div>
          <p className="text-[11px] text-slate-400 mb-3">
            Membaca setiap halaman blok disk dari blok 1 sampai akhir tabel.
          </p>
          <div className="flex items-center justify-between text-xs font-mono bg-slate-950/60 p-2 rounded-lg">
            <span>Disk Pages I/O:</span>
            <span className="text-rose-400 font-bold">{Math.round(rowCount / 8).toLocaleString()} Pages</span>
          </div>
        </div>

        {/* B-Tree Box */}
        <div
          className={`rounded-xl border p-4 transition-all ${
            isRoot || isLeaf
              ? "bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-500/40"
              : "bg-slate-900/60 border-slate-800 opacity-60"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-emerald-300">B-Tree Index Lookup</span>
            <span className="text-[10px] font-mono text-emerald-400">O(log N) Complexity</span>
          </div>
          <p className="text-[11px] text-slate-400 mb-3">
            Melompati node pohon indeks B-Tree langsung ke halaman target.
          </p>
          <div className="flex items-center justify-between text-xs font-mono bg-slate-950/60 p-2 rounded-lg">
            <span>Disk Pages I/O:</span>
            <span className="text-emerald-400 font-bold">3 Pages (Root → Branch → Leaf)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// SVG COMPONENT 3: Concurrency Locks & Deadlock Detection
// ----------------------------------------------------------------------------
function DeadlockVisual({ activeNode }: { activeNode: string }) {
  const isS1LockA = activeNode === "s1_lock_a";
  const isS2LockB = activeNode === "s2_lock_b";
  const isS1WaitsB = activeNode === "s1_waits_b";
  const isDeadlock = activeNode === "deadlock_detected";
  const isVictim = activeNode === "victim_rollback";

  return (
    <div className="w-full max-w-xl flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-between w-full p-4 bg-slate-950/60 rounded-xl border border-slate-800">
        {/* Session 1 */}
        <div
          className={`flex flex-col items-center p-3 rounded-lg border text-center transition-all ${
            isVictim
              ? "bg-emerald-950/80 border-emerald-500 text-emerald-300 ring-2 ring-emerald-500/50"
              : isS1WaitsB || isDeadlock
              ? "bg-amber-950/80 border-amber-500 text-amber-300 animate-pulse"
              : "bg-slate-900 border-slate-700 text-slate-300"
          }`}
          style={{ width: 130 }}
        >
          <span className="text-xs font-bold">Session 1</span>
          <span className="text-[10px] font-mono mt-1">PID 1045</span>
          <span className="text-[9px] mt-1 text-emerald-400">Holds Lock A</span>
        </div>

        {/* Conflict / Deadlock Graph Center */}
        <div className="flex flex-col items-center px-4">
          {isDeadlock ? (
            <div className="flex flex-col items-center text-rose-400 animate-bounce">
              <AlertTriangle className="h-6 w-6" />
              <span className="text-[10px] font-bold uppercase tracking-wider mt-1">Deadlock Cycle!</span>
            </div>
          ) : isVictim ? (
            <div className="flex flex-col items-center text-emerald-400">
              <CheckCircle2 className="h-6 w-6" />
              <span className="text-[10px] font-bold uppercase tracking-wider mt-1">Victim Aborted</span>
            </div>
          ) : (
            <div className="text-slate-600 text-xs font-mono font-bold">↔ Lock Contention</div>
          )}
        </div>

        {/* Session 2 */}
        <div
          className={`flex flex-col items-center p-3 rounded-lg border text-center transition-all ${
            isVictim
              ? "bg-rose-950/80 border-rose-600 text-rose-300 line-through opacity-60"
              : isDeadlock
              ? "bg-rose-950/90 border-rose-500 text-rose-300 animate-pulse ring-2 ring-rose-500/50"
              : isS2LockB
              ? "bg-slate-900 border-slate-700 text-slate-300"
              : "bg-slate-900 border-slate-800 text-slate-400"
          }`}
          style={{ width: 130 }}
        >
          <span className="text-xs font-bold">Session 2</span>
          <span className="text-[10px] font-mono mt-1">PID 1088</span>
          <span className="text-[9px] mt-1 text-amber-400">Holds Lock B</span>
        </div>
      </div>
    </div>
  );
}

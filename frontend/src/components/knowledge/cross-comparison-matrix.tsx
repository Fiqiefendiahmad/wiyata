"use client";

import React, { useState, useEffect } from "react";
import {
  Layers,
  CheckCircle2,
  Cpu,
  Database,
  ArrowRightLeft,
  Shield,
  Clock,
  Sparkles,
} from "lucide-react";
import { api } from "@/lib/api";

interface EngineSpec {
  name: string;
  shared_pool: string;
  private_memory: string;
  diagnostics: string;
}

interface ComparisonTopic {
  topic: string;
  topic_id: string;
  dimension: string;
  summary: string;
  summary_id: string;
  engines: Record<string, EngineSpec>;
}

interface CrossComparisonMatrixProps {
  language?: "en" | "id";
}

export function CrossComparisonMatrix({
  language = "id",
}: CrossComparisonMatrixProps) {
  const isId = language === "id";
  const [comparisons, setComparisons] = useState<ComparisonTopic[]>([]);
  const [selectedTopicIndex, setSelectedTopicIndex] = useState<number>(0);

  useEffect(() => {
    api
      .get("/knowledge/comparisons")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setComparisons(res.data);
        }
      })
      .catch((err) => console.error("Error fetching comparisons:", err));
  }, []);

  if (comparisons.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400 text-xs">
        Memuat Matriks Komparasi...
      </div>
    );
  }

  const activeTopic = comparisons[selectedTopicIndex] || comparisons[0];
  const engineKeys = [
    { key: "postgres", label: "PostgreSQL 17" },
    { key: "mysql", label: "MariaDB 11.3 (MySQL)" },
    { key: "oracle", label: "Oracle 23ai" },
    { key: "mssql", label: "SQL Server 2022" },
    { key: "db2", label: "IBM Db2 11.5" },
    { key: "sqlite", label: "SQLite 3.45" },
  ];

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#071A3A] p-3 sm:p-5 gap-4">
      {/* Header */}
      <div className="border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ArrowRightLeft className="h-5 w-5 text-[#F2B84B]" />
          <h1 className="text-base sm:text-lg font-bold text-white">
            {isId ? "Matriks Komparasi Antar-Database" : "Cross-Database Architectural Matrix"}
          </h1>
        </div>
        <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
          {isId
            ? "Bandingkan bagaimana masing-masing vendor database enterprise mengimplementasikan memori, konkurensi/MVCC, logging, dan ketersediaan tinggi."
            : "Compare how different enterprise database engines implement memory, concurrency/MVCC, logging, and high availability."}
        </p>
      </div>

      {/* Topic Switcher Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto no-scrollbar touch-scroll pb-1">
        {comparisons.map((c, idx) => (
          <button
            key={c.dimension}
            onClick={() => setSelectedTopicIndex(idx)}
            className={`flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold transition-all border whitespace-nowrap min-h-[40px] active:scale-95 ${
              selectedTopicIndex === idx
                ? "bg-[#10264A] text-[#F2B84B] border-[#F2B84B] shadow-sm ring-1 ring-[#F2B84B]/40"
                : "bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            <Layers className="h-4 w-4" />
            <span>{isId ? c.topic_id : c.topic}</span>
          </button>
        ))}
      </div>

      {/* Summary Box */}
      <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-3.5 text-xs text-slate-300 leading-relaxed">
        <div className="flex items-center gap-1.5 font-bold text-[#F2B84B] mb-1 font-mono text-[11px]">
          <Sparkles className="h-3.5 w-3.5" />
          <span>{isId ? activeTopic.topic_id : activeTopic.topic}</span>
        </div>
        <p>{isId ? activeTopic.summary_id : activeTopic.summary}</p>
      </div>

      {/* 6-Engine Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 overflow-y-auto no-scrollbar pr-1 pb-6">
        {engineKeys.map(({ key, label }) => {
          const spec = activeTopic.engines[key];
          if (!spec) return null;

          return (
            <div
              key={key}
              className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4 flex flex-col justify-between hover:border-slate-700 transition-colors shadow-sm"
            >
              <div>
                {/* Engine Badge */}
                <div className="flex items-center justify-between mb-3 border-b border-slate-800/80 pb-2">
                  <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-[#F2B84B]" />
                    <h3 className="text-xs font-bold text-white">{spec.name}</h3>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 uppercase">
                    {key}
                  </span>
                </div>

                {/* Primary Mechanism */}
                <div className="space-y-2 mb-3">
                  <div>
                    <span className="text-[10px] font-mono font-bold text-slate-400 uppercase block mb-0.5">
                      {isId ? "Mekanisme Utama & Pool Bersama:" : "Primary Mechanism & Shared Pool:"}
                    </span>
                    <p className="text-xs text-slate-200 leading-relaxed">
                      {spec.shared_pool}
                    </p>
                  </div>

                  <div>
                    <span className="text-[10px] font-mono font-bold text-slate-400 uppercase block mb-0.5">
                      {isId ? "Memori Privat / Penanganan Sesi:" : "Private Working Memory / Session:"}
                    </span>
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      {spec.private_memory}
                    </p>
                  </div>
                </div>
              </div>

              {/* Native Diagnostics View */}
              <div className="rounded-lg bg-slate-950 p-2.5 border border-slate-800/80 mt-2">
                <span className="text-[10px] font-mono text-slate-400 block mb-0.5">
                  {isId ? "Sumber Telemetri Native:" : "Native Telemetry Source:"}
                </span>
                <code className="text-[11px] font-mono text-emerald-400 break-all">
                  {spec.diagnostics}
                </code>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

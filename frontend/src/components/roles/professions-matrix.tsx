"use client";

import React, { useState, useEffect } from "react";
import {
  Briefcase,
  Compass,
  CheckCircle2,
  Shield,
  Activity,
  Server,
  Layers,
  Wrench,
  GraduationCap,
  ChevronRight,
  TrendingUp,
  FileText,
  AlertTriangle,
  ArrowRight,
  Code2,
  Database,
  Cpu,
  Gauge,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";

interface Runbook {
  name: string;
  name_id: string;
  steps: string[];
}

interface ProfessionRole {
  id: string;
  title: string;
  title_id: string;
  category: string;
  category_id: string;
  summary: string;
  summary_id: string;
  engines: string[];
  recommended_tools: string[];
  core_responsibilities: string[];
  core_responsibilities_id: string[];
  skills_progression: {
    junior: string[];
    mid: string[];
    senior: string[];
  };
  key_metrics: string[];
  runbooks: Runbook[];
  recommended_challenges: string[];
}

interface ProfessionsMatrixProps {
  language: "en" | "id";
  onSelectChallenge: (challengeSlug: string) => void;
  onOpenTool: (toolSlug: string) => void;
}

const ROLE_ICONS: Record<string, any> = {
  "sql-developer": Code2,
  "dba-general": Server,
  "oracle-dba": Database,
  "postgres-dba": Database,
  "mysql-dba": Database,
  "sqlserver-dba": Server,
  "db2-dba": Server,
  "database-engineer": Cpu,
  dbre: Activity,
  "perf-engineer": Gauge,
  "data-engineer": Layers,
  "db-architect": Compass,
  dba: Server,
  "data-analyst": TrendingUp,
  "security-auditor": Shield,
};

export function ProfessionsMatrix({
  language,
  onSelectChallenge,
  onOpenTool,
}: ProfessionsMatrixProps) {
  const isId = language === "id";

  const [roles, setRoles] = useState<ProfessionRole[]>([]);
  const [selectedRole, setSelectedRole] = useState<ProfessionRole | null>(null);
  const [activeLevel, setActiveLevel] = useState<"junior" | "mid" | "senior">("mid");
  const [activeTab, setActiveTab] = useState<"overview" | "skills" | "runbooks" | "metrics">("overview");

  useEffect(() => {
    api
      .get("/learning/roles")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setRoles(res.data);
          setSelectedRole(res.data[0]);
        }
      })
      .catch((err) => console.error("Error loading professions:", err));
  }, []);

  if (!selectedRole && roles.length === 0) {
    return (
      <div className="flex h-[calc(100dvh-3.5rem)] items-center justify-center bg-[#071A3A] text-slate-400">
        <div className="flex items-center gap-2 text-xs">
          <Activity className="h-4 w-4 animate-spin text-[#F2B84B]" />
          <span>{isId ? "Memuat peta jalur profesi..." : "Loading career matrix..."}</span>
        </div>
      </div>
    );
  }

  const role = selectedRole || roles[0];
  const IconComponent = ROLE_ICONS[role?.id] || Briefcase;

  return (
    <div className="flex flex-col lg:flex-row h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* MOBILE ROLE SELECTOR (< lg) */}
      <div className="lg:hidden border-b border-slate-800 bg-[#10264A]/80 p-3">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
          {isId ? "Pilih Jalur Spesialisasi:" : "Select Specialization:"}
        </label>
        <select
          value={role?.id}
          onChange={(e) => {
            const found = roles.find((r) => r.id === e.target.value);
            if (found) setSelectedRole(found);
          }}
          className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white focus:outline-none focus:border-[#F2B84B] min-h-[44px]"
        >
          {roles.map((r) => (
            <option key={r.id} value={r.id}>
              {isId ? r.title_id : r.title}
            </option>
          ))}
        </select>
      </div>

      {/* DESKTOP SIDEBAR (>= lg) */}
      <aside className="hidden lg:flex w-84 xl:w-96 flex-col border-r border-slate-800 bg-[#071A3A]/95 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-[#10264A]/30">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-1">
            <Compass className="h-4 w-4" />
            <span>{isId ? "Peta Jalur Karier Database" : "Database Career Matrix"}</span>
          </div>
          <h2 className="text-base font-bold text-white">
            {isId ? "Spesialisasi Profesional" : "Professional Roles"}
          </h2>
          <p className="text-[11px] text-slate-400 mt-1">
            {isId
              ? "Standar kompetensi, metrik monitoring, dan SOP runbook teknis untuk tiap peran industri."
              : "Competency ladders, observability metrics, and production runbooks per role."}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {roles.map((r) => {
            const isSelected = role?.id === r.id;
            const ItemIcon = ROLE_ICONS[r.id] || Briefcase;

            return (
              <div
                key={r.id}
                onClick={() => setSelectedRole(r)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? "border-[#F2B84B] bg-[#10264A] shadow-md ring-1 ring-[#F2B84B]/20"
                    : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-800/40"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] mb-1.5">
                  <span className="rounded-full bg-slate-800 px-2 py-0.5 text-slate-400 font-medium">
                    {isId ? r.category_id : r.category}
                  </span>
                  <div className="flex items-center gap-1 font-mono text-[10px] text-[#F2B84B]">
                    <span>{r.engines.length} {isId ? "mesin" : "engines"}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2.5">
                  <div className={`p-2 rounded-lg ${isSelected ? "bg-[#F2B84B] text-[#071A3A]" : "bg-slate-800 text-slate-300"}`}>
                    <ItemIcon className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white leading-snug">
                      {isId ? r.title_id : r.title}
                    </h3>
                    <p className="mt-0.5 text-[11px] text-slate-400 line-clamp-1">
                      {isId ? r.summary_id : r.summary}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </aside>

      {/* MAIN CONTENT PANE */}
      <main className="flex-1 flex flex-col overflow-y-auto bg-[#071A3A] min-w-0">
        {role && (
          <div className="p-4 sm:p-6 max-w-5xl space-y-6">
            {/* Role Header Banner */}
            <div className="rounded-2xl border border-slate-800 bg-[#10264A]/40 p-4 sm:p-6 backdrop-blur-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-[#F2B84B] to-[#D99A32] text-[#071A3A] shadow-md">
                    <IconComponent className="h-6 w-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#F2B84B]">
                      {isId ? role.category_id : role.category}
                    </span>
                    <h1 className="text-lg sm:text-2xl font-bold text-white">
                      {isId ? role.title_id : role.title}
                    </h1>
                  </div>
                </div>

                {/* Engine Pills */}
                <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-mono">
                  {role.engines.map((eng) => (
                    <span
                      key={eng}
                      className="rounded-lg bg-slate-900 border border-slate-700/80 px-2.5 py-1 text-slate-300 font-semibold"
                    >
                      {eng}
                    </span>
                  ))}
                </div>
              </div>

              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-3xl">
                {isId ? role.summary_id : role.summary}
              </p>

              {/* Navigation Sub-Tabs */}
              <div className="mt-6 flex items-center gap-2 border-b border-slate-800/80 overflow-x-auto no-scrollbar pt-2">
                {[
                  { id: "overview", label: isId ? "Tanggung Jawab Utama" : "Core Responsibilities" },
                  { id: "skills", label: isId ? "Jenjang Keahlian (Skills)" : "Skills Progression" },
                  { id: "runbooks", label: isId ? "SOP & Runbook Darurat" : "Emergency Runbooks" },
                  { id: "metrics", label: isId ? "Metrik Monitoring & Tooling" : "Metrics & Observability" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`pb-2.5 px-3 text-xs font-semibold whitespace-nowrap transition-colors border-b-2 ${
                      activeTab === tab.id
                        ? "border-[#F2B84B] text-[#F2B84B]"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* TAB 1: OVERVIEW & RESPONSIBILITIES */}
            {activeTab === "overview" && (
              <div className="space-y-4">
                <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 sm:p-5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    <span>{isId ? "Tanggung Jawab Operasional Sehari-hari:" : "Daily Operational Responsibilities:"}</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {(isId ? role.core_responsibilities_id : role.core_responsibilities).map((resp, idx) => (
                      <div
                        key={idx}
                        className="rounded-lg border border-slate-800/80 bg-[#071329] p-3 text-xs text-slate-200 leading-relaxed flex items-start gap-2.5"
                      >
                        <span className="font-mono text-[#F2B84B] font-bold text-sm shrink-0">
                          {idx + 1}.
                        </span>
                        <span>{resp}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended SQL Challenges for this role */}
                {role.recommended_challenges.length > 0 && (
                  <div className="rounded-xl border border-amber-600/40 bg-amber-950/20 p-4 sm:p-5">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                        <GraduationCap className="h-4 w-4 text-amber-400" />
                        <span>{isId ? "Latihan Praktis Terkait Peran Ini:" : "Target Hands-on SQL Labs:"}</span>
                      </h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {role.recommended_challenges.map((slug) => (
                        <button
                          key={slug}
                          onClick={() => onSelectChallenge(slug)}
                          className="flex items-center gap-2 rounded-lg border border-amber-700/60 bg-amber-950/50 px-3.5 py-2 text-xs font-semibold text-amber-200 hover:bg-amber-900/60 transition-colors"
                        >
                          <span>{slug}</span>
                          <ArrowRight className="h-3 w-3 text-amber-400" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: SKILLS PROGRESSION LADDER */}
            {activeTab === "skills" && (
              <div className="space-y-4">
                <div className="flex items-center gap-2 bg-slate-900/70 p-1.5 rounded-xl border border-slate-800 w-fit">
                  {[
                    { id: "junior", label: isId ? "Pemula (Junior)" : "Junior Level" },
                    { id: "mid", label: isId ? "Menengah (Mid-Level)" : "Mid-Level" },
                    { id: "senior", label: isId ? "Senior / Principal" : "Senior / Lead" },
                  ].map((lvl) => (
                    <button
                      key={lvl.id}
                      onClick={() => setActiveLevel(lvl.id as any)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        activeLevel === lvl.id
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      {lvl.label}
                    </button>
                  ))}
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 sm:p-5">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-white mb-3">
                    {isId
                      ? `Keahlian yang Wajib Dikuasai pada Tingkat ${activeLevel.toUpperCase()}:`
                      : `Must-Have Competencies at ${activeLevel.toUpperCase()} Level:`}
                  </h4>
                  <div className="space-y-2">
                    {role.skills_progression[activeLevel]?.map((skill, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-3 rounded-lg border border-slate-800 bg-[#071329] p-3 text-xs text-slate-200"
                      >
                        <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                        <span className="leading-relaxed">{skill}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: EMERGENCY RUNBOOKS & SOPS */}
            {activeTab === "runbooks" && (
              <div className="space-y-4">
                {role.runbooks.map((rb, idx) => (
                  <div
                    key={idx}
                    className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 sm:p-5 space-y-3"
                  >
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#F2B84B]" />
                      <h3 className="text-sm font-bold text-white">
                        {isId ? rb.name_id : rb.name}
                      </h3>
                    </div>

                    <div className="space-y-2 pl-2">
                      {rb.steps.map((step, sIdx) => (
                        <div
                          key={sIdx}
                          className="flex items-start gap-3 text-xs text-slate-300 leading-relaxed font-mono"
                        >
                          <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-[#F2B84B] font-bold shrink-0">
                            LANGKAH {sIdx + 1}
                          </span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB 4: METRICS & OBSERVABILITY TOOLING */}
            {activeTab === "metrics" && (
              <div className="space-y-4">
                {/* Key Metrics */}
                <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 sm:p-5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                    <Activity className="h-4 w-4 text-[#F2B84B]" />
                    <span>{isId ? "Metrik Telemetri Kunci yang Harus Dipantau:" : "Key Telemetry Metrics to Watch:"}</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {role.key_metrics.map((metric, idx) => (
                      <div
                        key={idx}
                        className="rounded-lg border border-slate-800 bg-[#071329] p-3 text-xs font-mono text-slate-300 flex items-center gap-2"
                      >
                        <span className="h-2 w-2 rounded-full bg-emerald-400 shrink-0" />
                        <span>{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended Monitoring & Admin Tools */}
                <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 sm:p-5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                    <Wrench className="h-4 w-4 text-[#F2B84B]" />
                    <span>{isId ? "Toolchain & Monitoring Direkomendasikan:" : "Recommended Toolchain & Monitoring:"}</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {role.recommended_tools.map((t) => (
                      <button
                        key={t}
                        onClick={() => onOpenTool(t)}
                        className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 hover:border-[#F2B84B] hover:text-white transition-colors"
                      >
                        <span>{t.toUpperCase()}</span>
                        <ChevronRight className="h-3 w-3 text-slate-400" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

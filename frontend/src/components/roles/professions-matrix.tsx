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
  BookOpen,
  Tag,
  ShieldAlert,
  Play,
  Award,
  ExternalLink,
  Lock,
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

interface RoadmapResource {
  resource_type: string;
  resource_slug: string;
  resource_title_en: string;
  resource_title_id: string;
  importance: "required" | "recommended";
  expected_proficiency: string;
  completion_criteria_en: string;
  completion_criteria_id: string;
  prerequisites: string[];
}

interface RoadmapCompetency {
  competency_slug: string;
  title_en: string;
  title_id: string;
  description_en: string;
  description_id: string;
  expected_outcome_en: string;
  expected_outcome_id: string;
  resources: RoadmapResource[];
}

interface RoadmapStage {
  stage: number;
  stage_name_en: string;
  stage_name_id: string;
  competencies: RoadmapCompetency[];
}

interface RoleRoadmapData {
  role_slug: string;
  total_stages: number;
  total_resources: number;
  stages: RoadmapStage[];
}

interface UserProgressData {
  articles_read: string[];
  exercises_solved: string[];
  assessments_passed: string[];
  demonstrated_competencies: string[];
  portfolio_completed: string[];
}

interface ProfessionsMatrixProps {
  language: "en" | "id";
  onSelectChallenge: (challengeSlug: string) => void;
  onOpenTool: (toolSlug: string) => void;
  onOpenKnowledgeArticle?: (articleSlug: string) => void;
  initialRoleSlug?: string | null;
}

const ROLE_ICONS: Record<string, React.ElementType> = {
  "sql-developer": Code2,
  "dba-general": Database,
  "oracle-dba": Server,
  "postgres-dba": Database,
  "mysql-dba": Database,
  "sqlserver-dba": Server,
  "db2-dba": Server,
  "database-engineer": Cpu,
  "dbre": Gauge,
  "perf-engineer": Zap,
  "data-engineer": Layers,
  "db-architect": Compass,
  "security-auditor": Shield,
};

export function ProfessionsMatrix({
  language,
  onSelectChallenge,
  onOpenTool,
  onOpenKnowledgeArticle,
  initialRoleSlug,
}: ProfessionsMatrixProps) {
  const isId = language === "id";

  const [roles, setRoles] = useState<ProfessionRole[]>([]);
  const [selectedRole, setSelectedRole] = useState<ProfessionRole | null>(null);
  const [activeLevel, setActiveLevel] = useState<"junior" | "mid" | "senior">("mid");
  const [activeTab, setActiveTab] = useState<"roadmap" | "overview" | "skills" | "runbooks" | "metrics">("roadmap");
  const [roadmap, setRoadmap] = useState<RoleRoadmapData | null>(null);
  const [loadingRoadmap, setLoadingRoadmap] = useState(false);
  const [progress, setProgress] = useState<UserProgressData>({
    articles_read: [],
    exercises_solved: [],
    assessments_passed: [],
    demonstrated_competencies: [],
    portfolio_completed: [],
  });

  // 1. Fetch Roles
  useEffect(() => {
    api
      .get("/learning/roles")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setRoles(res.data);
          if (initialRoleSlug) {
            const target = res.data.find((r: ProfessionRole) => r.id === initialRoleSlug);
            setSelectedRole(target || res.data[0]);
          } else {
            setSelectedRole(res.data[0]);
          }
        }
      })
      .catch((err) => console.error("Error loading professions:", err));

    // 2. Fetch User Progress (Activity separated)
    api
      .get("/learning/progress")
      .then((res) => {
        if (res.data) {
          setProgress(res.data);
        }
      })
      .catch((err) => console.error("Error loading learning progress:", err));
  }, [initialRoleSlug]);

  // 3. Fetch Sequenced Roadmap when selectedRole changes
  useEffect(() => {
    if (!selectedRole) return;
    setLoadingRoadmap(true);
    api
      .get(`/learning/roles/${selectedRole.id}/roadmap`)
      .then((res) => {
        if (res.data) {
          setRoadmap(res.data);
        }
      })
      .catch((err) => console.error("Error loading roadmap for role:", err))
      .finally(() => setLoadingRoadmap(false));
  }, [selectedRole?.id]);

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

      {/* DESKTOP SIDEBAR (> lg) */}
      <aside className="hidden lg:flex w-80 xl:w-96 flex-col border-r border-slate-800 bg-[#071A3A]/95 overflow-hidden shrink-0">
        <div className="p-4 border-b border-slate-800 bg-[#10264A]/30">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-1">
            <Compass className="h-4 w-4" />
            <span>{isId ? "Akademi Karier & Jalur Profesi" : "Career Academy & Specializations"}</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            {isId
              ? "Standar kompetensi profesional, roadmap belajar terintegrasi, dan runbook produksi."
              : "Integrated professional competencies, sequenced roadmaps, and production runbooks."}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1.5 no-scrollbar">
          {roles.map((r) => {
            const isSelected = r.id === role.id;
            const ItemIcon = ROLE_ICONS[r.id] || Briefcase;

            return (
              <div
                key={r.id}
                onClick={() => setSelectedRole(r)}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? "border-[#F2B84B] bg-[#10264A] shadow-md ring-1 ring-[#F2B84B]/20"
                    : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-800/40 text-slate-300"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`p-2 rounded-lg shrink-0 mt-0.5 ${
                      isSelected ? "bg-[#F2B84B] text-[#071A3A]" : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    <ItemIcon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-[#F2B84B] font-bold block mb-0.5">
                      {isId ? r.category_id : r.category}
                    </span>
                    <h3 className="text-xs font-bold text-white leading-snug line-clamp-1">
                      {isId ? r.title_id : r.title}
                    </h3>
                    <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-relaxed">
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
            <div className="rounded-2xl border border-slate-800 bg-[#10264A]/40 p-4 sm:p-6 backdrop-blur-sm shadow-sm">
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
                  { id: "roadmap", label: isId ? "Jalur Belajar Terpadu" : "Learning Roadmap" },
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

            {/* TAB 0: INTEGRATED COMPETENCY LEARNING ROADMAP */}
            {activeTab === "roadmap" && (
              <div className="space-y-6">
                {/* Activity-Separated Progress Card */}
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 sm:p-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2">
                        <Award className="h-4 w-4 text-[#F2B84B]" />
                        <span>{isId ? "Status Kemajuan Belajar Berbasis Bukti" : "Evidence-Based Progress Status"}</span>
                      </h3>
                      <p className="text-[11px] text-slate-400 mt-1">
                        {isId
                          ? "Pelacakan terpisah antara pemahaman bacaan teori dan pembuktian kompetensi praktis."
                          : "Separate tracking distinguishing theoretical reading from verified practical demonstration."}
                      </p>
                    </div>

                    <span className="rounded-lg bg-[#10264A] border border-[#F2B84B]/40 px-3 py-1 text-xs font-mono font-bold text-[#F2B84B]">
                      {progress.demonstrated_competencies.length} {isId ? "Kompetensi Terbukti" : "Demonstrated"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div className="rounded-xl border border-slate-800 bg-[#071329] p-3">
                      <span className="text-[10px] text-slate-400 block mb-0.5">
                        {isId ? "Artikel Teori Terbaca" : "Theory Articles"}
                      </span>
                      <span className="text-base font-bold font-mono text-amber-300">
                        {progress.articles_read.length}
                      </span>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-[#071329] p-3">
                      <span className="text-[10px] text-slate-400 block mb-0.5">
                        {isId ? "Tantangan SQL Selesai" : "SQL Labs Solved"}
                      </span>
                      <span className="text-base font-bold font-mono text-emerald-400">
                        {progress.exercises_solved.length}
                      </span>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-[#071329] p-3">
                      <span className="text-[10px] text-slate-400 block mb-0.5">
                        {isId ? "Investigasi Insiden" : "Triaged Incidents"}
                      </span>
                      <span className="text-base font-bold font-mono text-rose-400">
                        {progress.assessments_passed.length + 1}
                      </span>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-[#071329] p-3">
                      <span className="text-[10px] text-slate-400 block mb-0.5">
                        {isId ? "Kompetensi Terbukti" : "Verified Skills"}
                      </span>
                      <span className="text-base font-bold font-mono text-purple-400">
                        {progress.demonstrated_competencies.length}
                      </span>
                    </div>
                  </div>

                  {/* Standard Principle Alert */}
                  <div className="mt-3.5 p-3 rounded-xl bg-amber-950/20 border border-amber-800/40 text-[11px] text-amber-200/90 leading-relaxed flex items-start gap-2">
                    <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 text-[#F2B84B]" />
                    <span>
                      {isId
                        ? "Prinsip WIYATA: Membaca materi pengetahuan membangun fondasi konseptual. Pengakuan kompetensi profesional mensyaratkan pembuktian langsung melalui eksekusi kueri praktis dan mitigasi insiden."
                        : "WIYATA Standard: Reading articles builds conceptual foundations. Professional competency requires direct demonstration through practical SQL execution and incident triage."}
                    </span>
                  </div>
                </div>

                {/* Sequenced Roadmap Stages */}
                {loadingRoadmap ? (
                  <div className="p-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                    <Activity className="h-4 w-4 animate-spin text-[#F2B84B]" />
                    <span>{isId ? "Menyusun peta jalur belajar..." : "Assembling roadmap sequence..."}</span>
                  </div>
                ) : roadmap && roadmap.stages.length > 0 ? (
                  <div className="space-y-6">
                    {roadmap.stages.map((st) => (
                      <div
                        key={st.stage}
                        className="rounded-2xl border border-slate-800 bg-[#0A1B38]/60 p-4 sm:p-5 space-y-4"
                      >
                        {/* Stage Header */}
                        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                          <div className="flex items-center gap-2.5">
                            <span className="rounded-lg bg-[#F2B84B] text-[#071A3A] px-2.5 py-0.5 text-xs font-bold font-mono">
                              TAHAP {st.stage}
                            </span>
                            <h2 className="text-sm sm:text-base font-bold text-white">
                              {isId ? st.stage_name_id : st.stage_name_en}
                            </h2>
                          </div>
                          <span className="text-[11px] text-slate-400 font-mono">
                            {st.competencies.length} {isId ? "Kelompok Kompetensi" : "Competencies"}
                          </span>
                        </div>

                        {/* Competencies in Stage */}
                        <div className="space-y-4">
                          {st.competencies.map((comp) => (
                            <div
                              key={comp.competency_slug}
                              className="rounded-xl border border-slate-800/80 bg-slate-900/70 p-3.5 sm:p-4 space-y-3"
                            >
                              <div>
                                <div className="flex items-center justify-between mb-1">
                                  <h3 className="text-xs sm:text-sm font-bold text-white flex items-center gap-2">
                                    <div className="h-1.5 w-1.5 rounded-full bg-[#F2B84B]" />
                                    <span>{isId ? comp.title_id : comp.title_en}</span>
                                  </h3>
                                  <span className="text-[10px] font-mono text-slate-400">
                                    {comp.competency_slug}
                                  </span>
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed">
                                  {isId ? comp.description_id : comp.description_en}
                                </p>
                                <div className="mt-1.5 p-2 rounded-lg bg-[#10264A]/30 border border-slate-800 text-[11px] text-emerald-300 flex items-start gap-1.5">
                                  <span className="font-bold text-[#F2B84B] shrink-0">
                                    {isId ? "Target Kemampuan:" : "Expected Outcome:"}
                                  </span>
                                  <span>{isId ? comp.expected_outcome_id : comp.expected_outcome_en}</span>
                                </div>
                              </div>

                              {/* Connected Resources */}
                              <div className="space-y-2 pt-1 border-t border-slate-800/60">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
                                  {isId ? "Materi & Praktik Terhubung (Knowledge Center):" : "Linked Knowledge Resources:"}
                                </span>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                  {comp.resources.map((res, rIdx) => {
                                    const isArticle = res.resource_type === "article";
                                    const isExercise = res.resource_type === "exercise";
                                    const isTool = res.resource_type === "tool";
                                    const isTrouble = res.resource_type === "troubleshooting";
                                    const isGlossary = res.resource_type === "glossary";
                                    const isSimulation = res.resource_type === "visual_lesson";

                                    return (
                                      <div
                                        key={rIdx}
                                        className="rounded-lg border border-slate-800 bg-[#071329] p-3 flex flex-col justify-between gap-2.5"
                                      >
                                        <div>
                                          <div className="flex items-center justify-between mb-1">
                                            <span
                                              className={`rounded px-1.5 py-0.2 text-[9px] font-mono font-bold flex items-center gap-1 ${
                                                isArticle
                                                  ? "bg-amber-950 text-amber-300 border border-amber-800"
                                                  : isExercise
                                                  ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                                                  : isTool
                                                  ? "bg-blue-950 text-blue-300 border border-blue-800"
                                                  : isTrouble
                                                  ? "bg-rose-950 text-rose-300 border border-rose-800"
                                                  : "bg-purple-950 text-purple-300 border border-purple-800"
                                              }`}
                                            >
                                              {isArticle && <BookOpen className="h-2.5 w-2.5" />}
                                              {isExercise && <Zap className="h-2.5 w-2.5" />}
                                              {isTool && <Wrench className="h-2.5 w-2.5" />}
                                              {isTrouble && <ShieldAlert className="h-2.5 w-2.5" />}
                                              {isGlossary && <Tag className="h-2.5 w-2.5" />}
                                              {isSimulation && <Play className="h-2.5 w-2.5" />}
                                              <span className="uppercase">{res.resource_type}</span>
                                            </span>

                                            <div className="flex items-center gap-1 text-[9px] font-mono">
                                              <span
                                                className={`rounded px-1.5 py-0.2 font-semibold ${
                                                  res.importance === "required"
                                                    ? "bg-rose-950/80 text-rose-300 border border-rose-800"
                                                    : "bg-slate-800 text-slate-400"
                                                }`}
                                              >
                                                {res.importance === "required"
                                                  ? isId
                                                    ? "Wajib"
                                                    : "Required"
                                                  : isId
                                                  ? "Disarankan"
                                                  : "Recommended"}
                                              </span>
                                              <span className="text-slate-400">{res.expected_proficiency}</span>
                                            </div>
                                          </div>

                                          <h4 className="text-xs font-bold text-white line-clamp-2 leading-snug">
                                            {isId ? res.resource_title_id : res.resource_title_en}
                                          </h4>
                                          <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                                            {isId ? res.completion_criteria_id : res.completion_criteria_en}
                                          </p>
                                        </div>

                                        {/* Action Button */}
                                        <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                                          {res.prerequisites.length > 0 && (
                                            <span className="text-[10px] text-amber-400/90 font-mono truncate max-w-[150px]">
                                              Prasyarat: {res.prerequisites[0]}
                                            </span>
                                          )}

                                          {isArticle && (
                                            <button
                                              onClick={() => onOpenKnowledgeArticle?.(res.resource_slug)}
                                              className="ml-auto flex items-center gap-1 text-xs text-[#F2B84B] font-semibold hover:text-white transition-colors"
                                            >
                                              <span>{isId ? "Baca Artikel" : "Read Guide"}</span>
                                              <ArrowRight className="h-3 w-3" />
                                            </button>
                                          )}

                                          {isExercise && (
                                            <button
                                              onClick={() => onSelectChallenge(res.resource_slug)}
                                              className="ml-auto flex items-center gap-1 text-xs text-emerald-400 font-semibold hover:text-white transition-colors"
                                            >
                                              <span>{isId ? "Mulai Latihan SQL" : "Open SQL Lab"}</span>
                                              <Zap className="h-3 w-3" />
                                            </button>
                                          )}

                                          {isTool && (
                                            <button
                                              onClick={() => onOpenTool(res.resource_slug)}
                                              className="ml-auto flex items-center gap-1 text-xs text-blue-400 font-semibold hover:text-white transition-colors"
                                            >
                                              <span>{isId ? "Katalog Alat" : "View Tool"}</span>
                                              <ExternalLink className="h-3 w-3" />
                                            </button>
                                          )}
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-xs text-slate-400">
                    {isId ? "Roadmap untuk jalur ini sedang disinkronkan." : "Roadmap syncing in progress."}
                  </div>
                )}
              </div>
            )}

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
                        <Wrench className="h-3 w-3 text-[#F2B84B]" />
                        <span>{t}</span>
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

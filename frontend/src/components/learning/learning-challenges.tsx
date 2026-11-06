"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  GraduationCap,
  Play,
  CheckCircle2,
  XCircle,
  Database,
  ChevronDown,
  ChevronRight,
  HelpCircle,
  RotateCcw,
  Search,
  Filter,
  Check,
  Table,
  Layers,
  Sparkles,
  ExternalLink,
  Code2,
  Wrench,
  BookOpen,
} from "lucide-react";
import { SqlEditor } from "@/components/editor/sql-editor";
import { api } from "@/lib/api";

interface Exercise {
  slug: string;
  title: string;
  title_id: string;
  level: "Beginner" | "Intermediate" | "Advanced" | "Professional";
  category: string;
  category_id: string;
  dataset: string;
  description: string;
  description_id: string;
  expected_columns: string[];
  starter_sql: string;
  hints: string[];
  hints_id: string[];
  supported_engines: string[];
  related_articles?: { slug: string; title_en: string; title_id: string }[];
  related_roles?: { slug: string; title_en: string; title_id: string }[];
  related_tools?: { slug: string; name: string }[];
}

interface DatasetTable {
  name: string;
  columns: {
    cid: number;
    name: string;
    type: string;
    notnull: boolean;
    pk: boolean;
  }[];
  row_count: number;
}

interface VerificationResult {
  passed: boolean;
  message: string;
  row_count: number;
  expected_row_count: number;
  user_columns: string[];
  expected_columns: string[];
  sample_user_rows: any[][];
  sample_expected_rows: any[][];
  elapsed_ms: number;
  feedback: string[];
  hints: string[];
}

interface LearningChallengesProps {
  language: "en" | "id";
  onOpenLabWithQuery: (query: string, template: string) => void;
  initialChallengeSlug?: string | null;
  onNavigateToKnowledge?: (slug: string) => void;
  onNavigateToRole?: (roleSlug: string) => void;
  onNavigateToTool?: (toolSlug: string) => void;
}

const LEVEL_LOCALES: Record<string, { en: string; id: string; badge: string }> = {
  Beginner: {
    en: "Beginner",
    id: "Pemula",
    badge: "border-emerald-600/60 bg-emerald-950/40 text-emerald-400",
  },
  Intermediate: {
    en: "Intermediate",
    id: "Menengah",
    badge: "border-amber-600/60 bg-amber-950/40 text-amber-400",
  },
  Advanced: {
    en: "Advanced",
    id: "Lanjutan",
    badge: "border-rose-600/60 bg-rose-950/40 text-rose-400",
  },
  Professional: {
    en: "Professional",
    id: "Profesional",
    badge: "border-purple-600/60 bg-purple-950/40 text-purple-400",
  },
};

export function LearningChallenges({
  language,
  onOpenLabWithQuery,
  initialChallengeSlug,
  onNavigateToKnowledge,
  onNavigateToRole,
  onNavigateToTool,
}: LearningChallengesProps) {
  const isId = language === "id";

  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [solutionSql, setSolutionSql] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [activeEngine, setActiveEngine] = useState<
    "postgres" | "mysql" | "oracle" | "mssql" | "db2" | "sqlite"
  >("postgres");

  // Filtering & Search
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedLevel, setSelectedLevel] = useState<string>("ALL");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");

  // Solved Tracker
  const [solvedSlugs, setSolvedSlugs] = useState<string[]>([]);

  // Hints Disclosure
  const [revealedHintIndex, setRevealedHintIndex] = useState<number>(-1);

  // Schema Drawer
  const [showSchemaDrawer, setShowSchemaDrawer] = useState<boolean>(false);
  const [datasetTables, setDatasetTables] = useState<DatasetTable[]>([]);
  const [loadingSchema, setLoadingSchema] = useState<boolean>(false);

  // Result View Tab
  const [activeResultTab, setActiveResultTab] = useState<"comparison" | "user" | "expected">("comparison");

  // Load exercises & saved solved progress
  useEffect(() => {
    try {
      const saved = localStorage.getItem("wiyata_solved_challenges");
      if (saved) setSolvedSlugs(JSON.parse(saved));
    } catch {}

    api
      .get("/learning/exercises")
      .then((res) => {
        setExercises(res.data);
        if (res.data.length > 0) {
          const target = initialChallengeSlug
            ? res.data.find((e: any) => e.slug === initialChallengeSlug) || res.data[0]
            : res.data[0];
          setSelectedExercise(target);
          setSolutionSql(target.starter_sql);
        }
      })
      .catch((err) => console.error("Error loading exercises:", err));
  }, [initialChallengeSlug]);

  // Dynamic challenge sync when initialChallengeSlug changes after initial load
  useEffect(() => {
    if (!initialChallengeSlug || exercises.length === 0) return;
    const target = exercises.find((e) => e.slug === initialChallengeSlug);
    if (target && target.slug !== selectedExercise?.slug) {
      handleSelectExercise(target);
    }
  }, [initialChallengeSlug, exercises]);

  // Fetch dataset schema when exercise changes or drawer opens
  useEffect(() => {
    if (!selectedExercise) return;
    setLoadingSchema(true);
    api
      .get(`/learning/datasets/${selectedExercise.dataset}/schema`)
      .then((res) => {
        setDatasetTables(res.data.tables || []);
      })
      .catch((err) => console.error("Error fetching schema:", err))
      .finally(() => setLoadingSchema(false));
  }, [selectedExercise?.dataset]);

  const handleSelectExercise = (ex: Exercise) => {
    setSelectedExercise(ex);
    setSolutionSql(ex.starter_sql);
    setResult(null);
    setRevealedHintIndex(-1);
    setShowSchemaDrawer(false);
  };

  const handleResetQuery = () => {
    if (!selectedExercise) return;
    setSolutionSql(selectedExercise.starter_sql);
    setResult(null);
  };

  const handleVerify = async () => {
    if (!selectedExercise || !solutionSql.trim()) return;
    setIsSubmitting(true);
    setResult(null);

    try {
      const res = await api.post(
        `/learning/exercises/${selectedExercise.slug}/submit`,
        {
          query: solutionSql,
          language: language,
          engine: activeEngine,
        }
      );
      setResult(res.data);

      if (res.data.passed) {
        setSolvedSlugs((prev) => {
          if (!prev.includes(selectedExercise.slug)) {
            const updated = [...prev, selectedExercise.slug];
            try {
              localStorage.setItem("wiyata_solved_challenges", JSON.stringify(updated));
            } catch {}
            return updated;
          }
          return prev;
        });
      }
    } catch (err: any) {
      setResult({
        passed: false,
        message: err.message || "Network error",
        row_count: 0,
        expected_row_count: 0,
        user_columns: [],
        expected_columns: selectedExercise.expected_columns,
        sample_user_rows: [],
        sample_expected_rows: [],
        elapsed_ms: 0,
        feedback: [
          isId
            ? "Gagal menghubungi server verifikasi pengujian."
            : "Failed to connect to verification testing server.",
        ],
        hints: selectedExercise.hints,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filtered exercises list
  const filteredExercises = useMemo(() => {
    return exercises.filter((ex) => {
      if (selectedLevel !== "ALL" && ex.level !== selectedLevel) return false;
      if (selectedCategory !== "ALL") {
        const cat = isId ? ex.category_id : ex.category;
        if (cat !== selectedCategory) return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const title = (isId ? ex.title_id : ex.title).toLowerCase();
        const desc = (isId ? ex.description_id : ex.description).toLowerCase();
        const dataset = ex.dataset.toLowerCase();
        return title.includes(q) || desc.includes(q) || dataset.includes(q);
      }
      return true;
    });
  }, [exercises, selectedLevel, selectedCategory, searchQuery, isId]);

  const uniqueCategories = useMemo(() => {
    const set = new Set<string>();
    exercises.forEach((ex) => {
      set.add(isId ? ex.category_id : ex.category);
    });
    return Array.from(set);
  }, [exercises, isId]);

  const solvedPercentage = exercises.length > 0
    ? Math.round((solvedSlugs.length / exercises.length) * 100)
    : 0;

  return (
    <div className="flex flex-col lg:flex-row h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* MOBILE CHALLENGE SELECTOR & QUICK BAR (< lg) */}
      <div className="lg:hidden border-b border-slate-800 bg-[#10264A]/80 p-3 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-bold text-white">
            <GraduationCap className="h-4 w-4 text-[#F2B84B]" />
            <span>{isId ? "Tantangan SQL Praktis" : "SQL Learning Lab"}</span>
          </div>
          <span className="text-[11px] font-mono text-[#F2B84B] font-semibold">
            {solvedSlugs.length}/{exercises.length} {isId ? "Selesai" : "Solved"}
          </span>
        </div>

        <div className="relative">
          <select
            value={selectedExercise?.slug || ""}
            onChange={(e) => {
              const ex = exercises.find((item) => item.slug === e.target.value);
              if (ex) handleSelectExercise(ex);
            }}
            className="w-full appearance-none rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white focus:outline-none focus:border-[#F2B84B] min-h-[44px]"
          >
            {exercises.map((ex) => {
              const isSolved = solvedSlugs.includes(ex.slug);
              return (
                <option key={ex.slug} value={ex.slug}>
                  {isSolved ? "✓ " : ""}
                  [{LEVEL_LOCALES[ex.level] ? (isId ? LEVEL_LOCALES[ex.level].id : LEVEL_LOCALES[ex.level].en) : ex.level}]
                  {" "}{isId ? ex.title_id : ex.title}
                </option>
              );
            })}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-3.5 h-4 w-4 text-slate-400" />
        </div>
      </div>

      {/* DESKTOP SIDEBAR (>= lg) */}
      <aside className="hidden lg:flex w-84 xl:w-96 flex-col border-r border-slate-800 bg-[#071A3A]/95 overflow-hidden">
        {/* Header & Progress */}
        <div className="p-4 border-b border-slate-800 bg-[#10264A]/30">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-1">
            <div className="flex items-center gap-2">
              <GraduationCap className="h-4 w-4" />
              <span>{isId ? "Tantangan SQL Praktis" : "Hands-on SQL Labs"}</span>
            </div>
            <span className="font-mono text-slate-300 font-bold">
              {solvedSlugs.length}/{exercises.length}
            </span>
          </div>

          <h2 className="text-base font-bold text-white">
            {isId ? "Jalur Pembelajaran DBA" : "DBA Learning Tracks"}
          </h2>

          {/* Progress Bar */}
          <div className="mt-2.5">
            <div className="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>{isId ? "Progres Penyelesaian" : "Challenge Progress"}</span>
              <span className="font-mono font-semibold text-white">{solvedPercentage}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#F2B84B] to-emerald-400 rounded-full transition-all duration-500"
                style={{ width: `${solvedPercentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Search & Filter Controls */}
        <div className="p-3 border-b border-slate-800/80 space-y-2 bg-[#071A3A]">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              placeholder={isId ? "Cari tantangan SQL..." : "Search SQL challenges..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg bg-slate-900 border border-slate-800 pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#F2B84B]"
            />
          </div>

          <div className="grid grid-cols-2 gap-1.5">
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="rounded-lg bg-slate-900 border border-slate-800 px-2 py-1.5 text-[11px] text-slate-300 focus:outline-none focus:border-[#F2B84B]"
            >
              <option value="ALL">{isId ? "Semua Tingkat" : "All Levels"}</option>
              <option value="Beginner">{isId ? "Pemula" : "Beginner"}</option>
              <option value="Intermediate">{isId ? "Menengah" : "Intermediate"}</option>
              <option value="Advanced">{isId ? "Lanjutan" : "Advanced"}</option>
              <option value="Professional">{isId ? "Profesional" : "Professional"}</option>
            </select>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="rounded-lg bg-slate-900 border border-slate-800 px-2 py-1.5 text-[11px] text-slate-300 focus:outline-none focus:border-[#F2B84B] truncate"
            >
              <option value="ALL">{isId ? "Semua Topik" : "All Topics"}</option>
              {uniqueCategories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Challenge Cards List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {filteredExercises.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500">
              {isId ? "Tidak ada tantangan yang cocok dengan filter." : "No challenges match filter."}
            </div>
          ) : (
            filteredExercises.map((ex) => {
              const isSelected = selectedExercise?.slug === ex.slug;
              const isSolved = solvedSlugs.includes(ex.slug);
              const levelCfg = LEVEL_LOCALES[ex.level] || LEVEL_LOCALES.Beginner;

              return (
                <div
                  key={ex.slug}
                  onClick={() => handleSelectExercise(ex)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? "border-[#F2B84B] bg-[#10264A] shadow-md ring-1 ring-[#F2B84B]/20"
                      : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-800/40"
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <span className={`px-2 py-0.5 rounded-full font-semibold border ${levelCfg.badge}`}>
                        {isId ? levelCfg.id : levelCfg.en}
                      </span>
                      <span className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-400 font-mono">
                        {ex.dataset}
                      </span>
                    </div>

                    {isSolved && (
                      <span className="flex items-center gap-1 text-emerald-400 font-semibold text-[11px]">
                        <Check className="h-3.5 w-3.5" />
                        <span>{isId ? "Lulus" : "Passed"}</span>
                      </span>
                    )}
                  </div>

                  <h3 className="text-xs font-bold text-white leading-snug">
                    {isId ? ex.title_id : ex.title}
                  </h3>

                  <p className="mt-1 text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {isId ? ex.description_id : ex.description}
                  </p>
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* MAIN SOLVER WORKSPACE */}
      <main className="flex-1 flex flex-col overflow-y-auto lg:overflow-hidden bg-[#071A3A] min-w-0">
        {selectedExercise ? (
          <>
            {/* Header: Title, Controls, Schema Inspector */}
            <div className="border-b border-slate-800 bg-[#10264A]/30 p-3 sm:p-4 shrink-0">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${
                      LEVEL_LOCALES[selectedExercise.level]?.badge || "border-slate-700 bg-slate-800"
                    }`}
                  >
                    {isId
                      ? LEVEL_LOCALES[selectedExercise.level]?.id
                      : LEVEL_LOCALES[selectedExercise.level]?.en}
                  </span>

                  <span className="rounded bg-slate-800/80 px-2 py-0.5 text-[11px] text-[#F2B84B] font-mono border border-slate-700">
                    {isId ? selectedExercise.category_id : selectedExercise.category}
                  </span>

                  {solvedSlugs.includes(selectedExercise.slug) && (
                    <span className="flex items-center gap-1 rounded bg-emerald-950/60 border border-emerald-700/60 px-2 py-0.5 text-[11px] font-semibold text-emerald-300">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span>{isId ? "Tantangan Diselesaikan" : "Challenge Completed"}</span>
                    </span>
                  )}
                </div>

                {/* Right toolbar buttons */}
                <div className="flex items-center gap-2 flex-wrap">
                  {/* Schema Inspector Button */}
                  <button
                    onClick={() => setShowSchemaDrawer(!showSchemaDrawer)}
                    className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/90 px-3 py-1.5 text-xs text-slate-300 hover:text-white hover:border-[#F2B84B] transition-colors min-h-[38px]"
                  >
                    <Layers className="h-3.5 w-3.5 text-[#F2B84B]" />
                    <span>{isId ? "Skema Dataset" : "Dataset Schema"}</span>
                  </button>

                  {/* Open in Query Studio */}
                  <button
                    onClick={() =>
                      onOpenLabWithQuery(solutionSql, selectedExercise.dataset)
                    }
                    className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/90 px-3 py-1.5 text-xs text-slate-300 hover:text-white hover:border-[#F2B84B] transition-colors min-h-[38px]"
                  >
                    <Database className="h-3.5 w-3.5 text-emerald-400" />
                    <span>{isId ? "Buka di Studio" : "Open in Studio"}</span>
                  </button>
                </div>
              </div>

              <h1 className="text-base sm:text-lg font-bold text-white mb-1.5">
                {isId ? selectedExercise.title_id : selectedExercise.title}
              </h1>

              <p className="text-xs text-slate-300 leading-relaxed max-w-4xl">
                {isId
                  ? selectedExercise.description_id
                  : selectedExercise.description}
              </p>

              {/* Expected Columns Badge Row */}
              <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[11px] font-mono">
                <span className="font-semibold text-slate-400">
                  {isId ? "Kolom Diharapkan:" : "Expected Columns:"}
                </span>
                {selectedExercise.expected_columns.map((c) => (
                  <span
                    key={c}
                    className="rounded bg-slate-900/90 px-2 py-0.5 text-[#F2B84B] border border-slate-700/80"
                  >
                    {c}
                  </span>
                ))}
              </div>

              {/* Ecosystem Relations (Knowledge, Career Roles, Practical Tools) */}
              {selectedExercise &&
                ((selectedExercise.related_articles && selectedExercise.related_articles.length > 0) ||
                  (selectedExercise.related_roles && selectedExercise.related_roles.length > 0) ||
                  (selectedExercise.related_tools && selectedExercise.related_tools.length > 0)) && (
                  <div className="mt-3.5 pt-3 border-t border-slate-800/80 flex flex-col gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      {isId ? "Ekosistem Terkait (Teori, Jalur Profesi & Alat):" : "Connected Ecosystem (Knowledge, Careers & Tools):"}
                    </span>
                    <div className="flex flex-wrap items-center gap-2">
                      {/* Articles */}
                      {selectedExercise.related_articles?.map((art) => (
                        <button
                          key={art.slug}
                          type="button"
                          onClick={() => onNavigateToKnowledge?.(art.slug)}
                          className="flex items-center gap-1.5 rounded-lg border border-amber-600/40 bg-amber-950/30 px-2.5 py-1 text-xs text-amber-300 hover:border-amber-400 hover:text-white transition-colors"
                        >
                          <BookOpen className="h-3 w-3 text-amber-400" />
                          <span>{isId ? art.title_id : art.title_en}</span>
                          <ExternalLink className="h-2.5 w-2.5 text-amber-400/70" />
                        </button>
                      ))}

                      {/* Career Roles */}
                      {selectedExercise.related_roles?.map((role) => (
                        <button
                          key={role.slug}
                          type="button"
                          onClick={() => onNavigateToRole?.(role.slug)}
                          className="flex items-center gap-1.5 rounded-lg border border-purple-600/40 bg-purple-950/30 px-2.5 py-1 text-xs text-purple-300 hover:border-purple-400 hover:text-white transition-colors"
                        >
                          <GraduationCap className="h-3 w-3 text-purple-400" />
                          <span>{isId ? role.title_id : role.title_en}</span>
                          <ExternalLink className="h-2.5 w-2.5 text-purple-400/70" />
                        </button>
                      ))}

                      {/* Tools */}
                      {selectedExercise.related_tools?.map((tool) => (
                        <button
                          key={tool.slug}
                          type="button"
                          onClick={() => onNavigateToTool?.(tool.slug)}
                          className="flex items-center gap-1.5 rounded-lg border border-blue-600/40 bg-blue-950/30 px-2.5 py-1 text-xs text-blue-300 hover:border-blue-400 hover:text-white transition-colors"
                        >
                          <Wrench className="h-3 w-3 text-blue-400" />
                          <span>{tool.name}</span>
                          <ExternalLink className="h-2.5 w-2.5 text-blue-400/70" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
            </div>

            {/* Collapsible Dataset Schema Drawer */}
            {showSchemaDrawer && (
              <div className="border-b border-slate-800 bg-[#071329] p-3 sm:p-4 max-h-64 overflow-y-auto w-full">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold text-[#F2B84B] flex items-center gap-1.5">
                    <Table className="h-3.5 w-3.5" />
                    <span>
                      {isId
                        ? `Tabel & Struktur Skema (${selectedExercise.dataset})`
                        : `Tables & Schema Structure (${selectedExercise.dataset})`}
                    </span>
                  </h4>
                  <button
                    onClick={() => setShowSchemaDrawer(false)}
                    className="text-xs text-slate-400 hover:text-white"
                  >
                    {isId ? "Tutup" : "Close"}
                  </button>
                </div>

                {loadingSchema ? (
                  <div className="text-xs text-slate-500 py-3">
                    {isId ? "Memuat struktur skema..." : "Loading schema structure..."}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                    {datasetTables.map((tbl) => (
                      <div
                        key={tbl.name}
                        className="rounded-lg border border-slate-800 bg-slate-900/70 p-2.5 text-xs"
                      >
                        <div className="flex items-center justify-between font-mono font-bold text-white mb-1.5 border-b border-slate-800 pb-1">
                          <span className="text-[#F2B84B]">{tbl.name}</span>
                          <span className="text-[10px] text-slate-400 font-normal">
                            {tbl.row_count} {isId ? "baris" : "rows"}
                          </span>
                        </div>
                        <div className="space-y-1">
                          {tbl.columns.map((col) => (
                            <div
                              key={col.name}
                              className="flex items-center justify-between text-[11px] font-mono text-slate-300"
                            >
                              <span className={col.pk ? "font-bold text-emerald-400" : ""}>
                                {col.name} {col.pk ? "(PK)" : ""}
                              </span>
                              <span className="text-slate-500 text-[10px] uppercase">
                                {col.type}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Editor & Execution Container */}
            <div className="flex-1 flex flex-col p-2 sm:p-4 overflow-hidden gap-3">
              {/* Engine Bar & Editor Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 bg-[#10264A]/40 p-2 rounded-xl border border-slate-800">
                {/* Engine Selector */}
                <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll max-w-full py-0.5">
                  <span className="text-[11px] font-semibold text-slate-400 pl-1 shrink-0">
                    {isId ? "Target Mesin:" : "Target Engine:"}
                  </span>
                  <div className="flex items-center rounded-lg bg-slate-900/90 p-0.5 border border-slate-700/80 shrink-0">
                    <button
                      onClick={() => setActiveEngine("postgres")}
                      className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                        activeEngine === "postgres"
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      Postgres 17
                    </button>
                    <button
                      onClick={() => setActiveEngine("mysql")}
                      className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                        activeEngine === "mysql"
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      MariaDB 11.3
                    </button>
                    <button
                      onClick={() => setActiveEngine("oracle")}
                      className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                        activeEngine === "oracle"
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      Oracle 23ai
                    </button>
                    <button
                      onClick={() => setActiveEngine("mssql")}
                      className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                        activeEngine === "mssql"
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      SQL Server
                    </button>
                    <button
                      onClick={() => setActiveEngine("db2")}
                      className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                        activeEngine === "db2"
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      IBM Db2
                    </button>
                    <button
                      onClick={() => setActiveEngine("sqlite")}
                      className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                        activeEngine === "sqlite"
                          ? "bg-[#F2B84B] text-[#071A3A] shadow-xs"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      SQLite 3.45
                    </button>
                  </div>
                </div>

                {/* Reset SQL */}
                <button
                  onClick={handleResetQuery}
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors px-2 py-1"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span>{isId ? "Kembalikan Soal Awal" : "Reset Starter SQL"}</span>
                </button>
              </div>

              {/* Monaco Editor Pane */}
              <div className="h-56 sm:h-64 lg:h-72 w-full shrink-0">
                <SqlEditor
                  value={solutionSql}
                  onChange={setSolutionSql}
                  onExecute={handleVerify}
                  language={language}
                  engine={activeEngine}
                />
              </div>

              {/* Action Toolbar & Progressive Hints Accordion */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 shrink-0">
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={handleVerify}
                    disabled={isSubmitting}
                    className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#F2B84B] to-[#D99A32] px-6 py-2.5 text-xs font-bold text-[#071A3A] hover:opacity-95 shadow-md transition-all disabled:opacity-50 min-h-[44px]"
                  >
                    <Play className="h-4 w-4 fill-current" />
                    <span>
                      {isSubmitting
                        ? isId
                          ? "Menguji Kueri..."
                          : "Verifying Query..."
                        : isId
                        ? "Verifikasi Jawaban"
                        : "Submit & Verify"}
                    </span>
                  </button>

                  {/* Progressive Hint Reveal Button */}
                  {(selectedExercise.hints?.length > 0 || selectedExercise.hints_id?.length > 0) && (
                    <button
                      onClick={() =>
                        setRevealedHintIndex((prev) =>
                          prev < (selectedExercise.hints?.length || 1) - 1 ? prev + 1 : prev
                        )
                      }
                      className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800/80 px-3.5 py-2.5 text-xs font-medium text-amber-300 hover:bg-slate-700/60 transition-colors min-h-[44px]"
                    >
                      <HelpCircle className="h-4 w-4 text-amber-400" />
                      <span>
                        {revealedHintIndex < 0
                          ? isId ? "Buka Petunjuk (Hint)" : "Reveal Hint"
                          : isId
                          ? `Petunjuk Berikutnya (${revealedHintIndex + 1}/${selectedExercise.hints?.length || 1})`
                          : `Next Hint (${revealedHintIndex + 1}/${selectedExercise.hints?.length || 1})`}
                      </span>
                    </button>
                  )}
                </div>

                <span className="text-[11px] text-slate-500 font-mono text-center sm:text-right">
                  {isId
                    ? `Dijalankan di sandbox ${activeEngine.toUpperCase()} terisolasi`
                    : `Verified against isolated ${activeEngine.toUpperCase()} sandbox`}
                </span>
              </div>

              {/* Revealed Hints Box */}
              {revealedHintIndex >= 0 && (
                <div className="rounded-xl border border-amber-600/50 bg-amber-950/20 p-3 text-xs text-amber-200 shrink-0">
                  <div className="flex items-center gap-1.5 font-bold mb-1.5 text-amber-300">
                    <Sparkles className="h-4 w-4" />
                    <span>{isId ? "Petunjuk Pembelajaran:" : "Learning Clues & Hints:"}</span>
                  </div>
                  <div className="space-y-1.5 pl-5 list-decimal">
                    {(isId ? selectedExercise.hints_id : selectedExercise.hints)
                      .slice(0, revealedHintIndex + 1)
                      .map((h, i) => (
                        <div key={i} className="flex items-start gap-2 text-[11px] leading-relaxed">
                          <span className="font-bold text-amber-400 shrink-0">{i + 1}.</span>
                          <span>{h}</span>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Test Result & Comparison View */}
              {result && (
                <div
                  className={`flex flex-col rounded-xl border p-3.5 sm:p-4 text-xs font-mono transition-all shrink-0 ${
                    result.passed
                      ? "border-emerald-600/60 bg-emerald-950/30 text-emerald-200"
                      : "border-rose-700/60 bg-rose-950/30 text-rose-200"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2 font-bold text-sm">
                      {result.passed ? (
                        <>
                          <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                          <span className="text-emerald-300">{result.message}</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-5 w-5 text-rose-400 shrink-0" />
                          <span className="text-rose-300">{result.message}</span>
                        </>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-slate-300">
                      <span>
                        {isId ? "Baris:" : "Rows:"}{" "}
                        <strong className="text-white">
                          {result.row_count} / {result.expected_row_count}
                        </strong>
                      </span>
                      <span>
                        {isId ? "Waktu:" : "Time:"}{" "}
                        <strong className="text-white">{result.elapsed_ms} ms</strong>
                      </span>
                    </div>
                  </div>

                  {/* Feedback bullets if any */}
                  {result.feedback.length > 0 && (
                    <div className="rounded-lg bg-black/30 p-2.5 my-2 border border-slate-800">
                      <ul className="list-disc pl-5 space-y-1 text-[11px] text-slate-300">
                        {result.feedback.map((f, idx) => (
                          <li key={idx}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Tab Selector for Output Comparison */}
                  <div className="flex items-center gap-1 border-b border-slate-800 pt-2 mb-2">
                    <button
                      onClick={() => setActiveResultTab("comparison")}
                      className={`px-3 py-1.5 text-xs font-semibold rounded-t-lg transition-colors ${
                        activeResultTab === "comparison"
                          ? "bg-slate-800 text-white border-b-2 border-[#F2B84B]"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {isId ? "Perbandingan Data" : "Side-by-Side Comparison"}
                    </button>
                    <button
                      onClick={() => setActiveResultTab("user")}
                      className={`px-3 py-1.5 text-xs font-semibold rounded-t-lg transition-colors ${
                        activeResultTab === "user"
                          ? "bg-slate-800 text-white border-b-2 border-[#F2B84B]"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {isId ? "Hasil Kueri Anda" : "Your Query Output"}
                    </button>
                    <button
                      onClick={() => setActiveResultTab("expected")}
                      className={`px-3 py-1.5 text-xs font-semibold rounded-t-lg transition-colors ${
                        activeResultTab === "expected"
                          ? "bg-slate-800 text-white border-b-2 border-[#F2B84B]"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {isId ? "Ekspektasi Referensi" : "Expected Output"}
                    </button>
                  </div>

                  {/* Comparison Tab View */}
                  {activeResultTab === "comparison" && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-1">
                      {/* Your Output */}
                      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5 overflow-x-auto">
                        <div className="font-bold text-xs text-slate-300 mb-1.5 flex items-center justify-between">
                          <span>{isId ? "Output Kueri Anda" : "Your Query Output"}</span>
                          <span className="text-[10px] text-slate-500">
                            {result.user_columns.join(", ") || (isId ? "Tidak ada kolom" : "No columns")}
                          </span>
                        </div>
                        {result.sample_user_rows && result.sample_user_rows.length > 0 ? (
                          <table className="w-full text-[11px] text-left">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-400">
                                {result.user_columns.map((c) => (
                                  <th key={c} className="py-1 px-2 font-semibold">
                                    {c}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {result.sample_user_rows.map((row, rIdx) => (
                                <tr key={rIdx} className="border-b border-slate-800/40 hover:bg-slate-800/20">
                                  {row.map((cell: any, cIdx: number) => (
                                    <td key={cIdx} className="py-1 px-2 text-slate-300">
                                      {String(cell)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        ) : (
                          <div className="text-[11px] text-slate-500 py-2">
                            {isId ? "Tidak ada baris data." : "No rows returned."}
                          </div>
                        )}
                      </div>

                      {/* Expected Reference Output */}
                      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5 overflow-x-auto">
                        <div className="font-bold text-xs text-amber-300 mb-1.5 flex items-center justify-between">
                          <span>{isId ? "Ekspektasi Referensi" : "Expected Reference"}</span>
                          <span className="text-[10px] text-slate-500">
                            {result.expected_columns.join(", ")}
                          </span>
                        </div>
                        {result.sample_expected_rows && result.sample_expected_rows.length > 0 ? (
                          <table className="w-full text-[11px] text-left">
                            <thead>
                              <tr className="border-b border-slate-800 text-amber-400/80">
                                {result.expected_columns.map((c) => (
                                  <th key={c} className="py-1 px-2 font-semibold">
                                    {c}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {result.sample_expected_rows.map((row, rIdx) => (
                                <tr key={rIdx} className="border-b border-slate-800/40 hover:bg-slate-800/20">
                                  {row.map((cell: any, cIdx: number) => (
                                    <td key={cIdx} className="py-1 px-2 text-slate-300">
                                      {String(cell)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        ) : (
                          <div className="text-[11px] text-slate-500 py-2">
                            {isId ? "Tidak ada baris referensi." : "No reference rows."}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Single Tab User View */}
                  {activeResultTab === "user" && (
                    <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
                      <table className="w-full text-[11px] text-left">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400">
                            {result.user_columns.map((c) => (
                              <th key={c} className="py-1 px-2 font-semibold">
                                {c}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {result.sample_user_rows?.map((row, rIdx) => (
                            <tr key={rIdx} className="border-b border-slate-800/40 hover:bg-slate-800/20">
                              {row.map((cell: any, cIdx: number) => (
                                <td key={cIdx} className="py-1 px-2 text-slate-300">
                                  {String(cell)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {/* Single Tab Expected View */}
                  {activeResultTab === "expected" && (
                    <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
                      <table className="w-full text-[11px] text-left">
                        <thead>
                          <tr className="border-b border-slate-800 text-amber-400/80">
                            {result.expected_columns.map((c) => (
                              <th key={c} className="py-1 px-2 font-semibold">
                                {c}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {result.sample_expected_rows?.map((row, rIdx) => (
                            <tr key={rIdx} className="border-b border-slate-800/40 hover:bg-slate-800/20">
                              {row.map((cell: any, cIdx: number) => (
                                <td key={cIdx} className="py-1 px-2 text-slate-300">
                                  {String(cell)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="p-8 text-center text-slate-400">
            {isId ? "Pilih tantangan dari daftar di sebelah kiri." : "Select a challenge from the list."}
          </div>
        )}
      </main>
    </div>
  );
}

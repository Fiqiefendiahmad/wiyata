"use client";

import React, { useState, useEffect } from "react";
import {
  GraduationCap,
  Play,
  CheckCircle2,
  XCircle,
  Database,
  ChevronDown,
} from "lucide-react";
import { SqlEditor } from "@/components/editor/sql-editor";
import { api } from "@/lib/api";

interface Exercise {
  slug: string;
  title: string;
  title_id: string;
  level: "Beginner" | "Intermediate" | "Advanced";
  dataset: string;
  description: string;
  description_id: string;
  expected_columns: string[];
  starter_sql: string;
}

interface VerificationResult {
  passed: boolean;
  message: string;
  row_count: number;
  expected_row_count: number;
  user_columns: string[];
  expected_columns: string[];
  elapsed_ms: number;
  feedback: string[];
}

interface LearningChallengesProps {
  language: "en" | "id";
  onOpenLabWithQuery: (query: string, template: string) => void;
}

const LEVEL_LOCALES: Record<string, { en: string; id: string }> = {
  Beginner: { en: "Beginner", id: "Pemula" },
  Intermediate: { en: "Intermediate", id: "Menengah" },
  Advanced: { en: "Advanced", id: "Lanjutan" },
};

export function LearningChallenges({
  language,
  onOpenLabWithQuery,
}: LearningChallengesProps) {
  const isId = language === "id";

  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(
    null
  );
  const [solutionSql, setSolutionSql] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [result, setResult] = useState<VerificationResult | null>(null);

  useEffect(() => {
    api
      .get("/learning/exercises")
      .then((res) => {
        setExercises(res.data);
        if (res.data.length > 0) {
          setSelectedExercise(res.data[0]);
          setSolutionSql(res.data[0].starter_sql);
        }
      })
      .catch((err) => console.error("Error loading exercises:", err));
  }, []);

  const handleSelectExercise = (ex: Exercise) => {
    setSelectedExercise(ex);
    setSolutionSql(ex.starter_sql);
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
        }
      );
      setResult(res.data);
    } catch (err: any) {
      setResult({
        passed: false,
        message: err.message,
        row_count: 0,
        expected_row_count: 0,
        user_columns: [],
        expected_columns: selectedExercise.expected_columns,
        elapsed_ms: 0,
        feedback: [
          isId
            ? "Terjadi kesalahan jaringan atau server saat mengeksekusi pengujian."
            : "Network or server error executing test.",
        ],
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* MOBILE CHALLENGE SELECTOR BAR (< lg) */}
      <div className="lg:hidden border-b border-slate-800 bg-[#10264A]/80 p-3">
        <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
          {isId ? "Pilih Tantangan SQL:" : "Select Challenge:"}
        </label>
        <div className="relative">
          <select
            value={selectedExercise?.slug || ""}
            onChange={(e) => {
              const ex = exercises.find((item) => item.slug === e.target.value);
              if (ex) handleSelectExercise(ex);
            }}
            className="w-full appearance-none rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white focus:outline-none focus:border-[#F2B84B] min-h-[44px]"
          >
            {exercises.map((ex) => (
              <option key={ex.slug} value={ex.slug}>
                [{LEVEL_LOCALES[ex.level] ? (isId ? LEVEL_LOCALES[ex.level].id : LEVEL_LOCALES[ex.level].en) : ex.level}]{" "}
                {isId ? ex.title_id : ex.title}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-3.5 h-4 w-4 text-slate-400" />
        </div>
      </div>

      {/* DESKTOP SIDEBAR (>= lg) */}
      <aside className="hidden lg:flex w-80 flex-col border-r border-slate-800 bg-[#071A3A]/95 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-1">
            <GraduationCap className="h-4 w-4" />
            <span>{isId ? "Tantangan SQL Praktis" : "Hands-on SQL Labs"}</span>
          </div>
          <h2 className="text-base font-bold text-white">
            {isId ? "Jalur Pembelajaran DBA" : "DBA Learning Tracks"}
          </h2>
          <p className="text-[11px] text-slate-400 mt-1">
            {isId
              ? "Uji kemampuan menulis SQL nyata dengan verifikasi otomatis."
              : "Solve realistic database scenarios with automated grading."}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
          {exercises.map((ex) => (
            <div
              key={ex.slug}
              onClick={() => handleSelectExercise(ex)}
              className={`p-3 rounded border cursor-pointer transition-all ${
                selectedExercise?.slug === ex.slug
                  ? "border-[#F2B84B] bg-[#10264A] shadow-sm"
                  : "border-slate-800/80 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-800/40"
              }`}
            >
              <div className="flex items-center justify-between text-[10px] mb-1">
                <span
                  className={`px-1.5 py-0.2 rounded font-semibold ${
                    ex.level === "Beginner"
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : "bg-amber-950 text-amber-400 border border-amber-800"
                  }`}
                >
                  {LEVEL_LOCALES[ex.level]
                    ? isId
                      ? LEVEL_LOCALES[ex.level].id
                      : LEVEL_LOCALES[ex.level].en
                    : ex.level}
                </span>
                <span className="font-mono text-slate-500">
                  {ex.dataset} {isId ? "skema" : "dataset"}
                </span>
              </div>
              <h3 className="text-xs font-bold text-slate-100">
                {isId ? ex.title_id : ex.title}
              </h3>
              <p className="mt-1 text-[11px] text-slate-400 line-clamp-2">
                {isId ? ex.description_id : ex.description}
              </p>
            </div>
          ))}
        </div>
      </aside>

      {/* Solver Pane */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#071A3A] min-w-0">
        {selectedExercise && (
          <>
            {/* Challenge Header */}
            <div className="border-b border-slate-800 bg-[#10264A]/40 p-3 sm:p-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-[#F2B84B]/20 px-2 py-0.5 text-[11px] font-bold text-[#F2B84B] border border-[#F2B84B]/30 shrink-0">
                    {LEVEL_LOCALES[selectedExercise.level]
                      ? isId
                        ? LEVEL_LOCALES[selectedExercise.level].id
                        : LEVEL_LOCALES[selectedExercise.level].en
                      : selectedExercise.level}
                  </span>
                  <h1 className="text-base sm:text-xl font-bold text-white truncate">
                    {isId ? selectedExercise.title_id : selectedExercise.title}
                  </h1>
                </div>

                <button
                  onClick={() =>
                    onOpenLabWithQuery(solutionSql, selectedExercise.dataset)
                  }
                  className="flex items-center justify-center gap-1.5 rounded border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs text-slate-300 hover:text-white hover:border-[#F2B84B] transition-colors min-h-[36px] shrink-0"
                >
                  <Database className="h-3.5 w-3.5 text-[#F2B84B]" />
                  <span>{isId ? "Buka di Studio" : "Open in Studio"}</span>
                </button>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mb-3">
                {isId
                  ? selectedExercise.description_id
                  : selectedExercise.description}
              </p>

              <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-mono text-slate-400">
                <span className="font-semibold text-slate-300">
                  {isId ? "Kolom Diharapkan:" : "Expected Columns:"}
                </span>
                {selectedExercise.expected_columns.map((c) => (
                  <span
                    key={c}
                    className="rounded bg-slate-900 px-1.5 py-0.5 text-[#F2B84B] border border-slate-800"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>

            {/* Editor & Verification Section */}
            <div className="flex-1 flex flex-col p-2 sm:p-4 overflow-hidden">
              <div className="h-64 sm:flex-1 min-h-[220px]">
                <SqlEditor
                  value={solutionSql}
                  onChange={setSolutionSql}
                  onExecute={handleVerify}
                  language={language}
                />
              </div>

              {/* Action Toolbar */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 py-3">
                <button
                  onClick={handleVerify}
                  disabled={isSubmitting}
                  className="flex items-center justify-center gap-2 rounded bg-gradient-to-r from-[#F2B84B] to-[#D99A32] px-5 py-2.5 text-xs font-bold text-[#071A3A] hover:opacity-90 shadow-md transition-all disabled:opacity-50 min-h-[44px]"
                >
                  <Play className="h-4 w-4 fill-current" />
                  <span>
                    {isSubmitting
                      ? isId
                        ? "Menguji Solusi..."
                        : "Verifying Query..."
                      : isId
                      ? "Verifikasi Jawaban"
                      : "Submit & Verify"}
                  </span>
                </button>

                <span className="text-[11px] text-slate-500 text-center sm:text-right">
                  {isId
                    ? "Query diuji langsung di sandbox SQLite terisolasi"
                    : "Verified in an isolated SQLite sandbox"}
                </span>
              </div>

              {/* Test Result Banner */}
              {result && (
                <div
                  className={`rounded-lg border p-3 sm:p-4 text-xs font-mono transition-all ${
                    result.passed
                      ? "border-emerald-600/60 bg-emerald-950/40 text-emerald-300"
                      : "border-rose-700/60 bg-rose-950/40 text-rose-300"
                  }`}
                >
                  <div className="flex items-center gap-2 font-bold text-sm mb-1">
                    {result.passed ? (
                      <>
                        <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                        <span>{result.message}</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-4 w-4 text-rose-400 shrink-0" />
                        <span>{result.message}</span>
                      </>
                    )}
                  </div>

                  <div className="mt-2 flex flex-wrap items-center gap-3 sm:gap-4 text-[11px] text-slate-300">
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

                  {result.feedback.length > 0 && (
                    <ul className="mt-2 list-disc pl-5 space-y-0.5 text-[11px] text-slate-300">
                      {result.feedback.map((f, idx) => (
                        <li key={idx}>{f}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  Code2,
  Table as TableIcon,
  Layers,
  ArrowRightLeft,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  ChevronRight,
  ChevronDown,
  Key,
  Database,
  Bookmark,
  HelpCircle,
  Lightbulb,
  SidebarClose,
  SidebarOpen,
} from "lucide-react";
import { SqlEditor } from "@/components/editor/sql-editor";
import { api } from "@/lib/api";

interface ColumnInfo {
  cid: number;
  name: string;
  type: string;
  notnull: boolean;
  default: any;
  pk: boolean;
}

interface TableSchema {
  name: string;
  type: string;
  columns: ColumnInfo[];
}

interface TemplateItem {
  slug: string;
  name: string;
  description: string;
}

interface SavedQueryItem {
  id: string;
  title: string;
  query_text: string;
  description: string | null;
}

interface QueryWorkbenchProps {
  sandboxId: string | null;
  onSandboxChange: (id: string) => void;
  language: "en" | "id";
  initialQuery?: string;
  initialTemplate?: string;
}

export function QueryWorkbench({
  sandboxId,
  onSandboxChange,
  language,
  initialQuery,
  initialTemplate,
}: QueryWorkbenchProps) {
  const isId = language === "id";

  // State
  const [query, setQuery] = useState<string>(
    initialQuery ||
      "SELECT c.first_name, c.last_name, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS total_spent\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.id\nORDER BY total_spent DESC\nLIMIT 5;"
  );
  const [transpileTarget, setTranspileTarget] = useState<string>("postgres");
  const [transpiledSql, setTranspiledSql] = useState<string>("");
  const [transpileWarnings, setTranspileWarnings] = useState<string[]>([]);
  const [activeOutputTab, setActiveOutputTab] = useState<
    "results" | "transpile" | "explain" | "ai_explain" | "optimize"
  >("results");
  const [allowDdl, setAllowDdl] = useState<boolean>(false);

  // Responsive sidebar toggle for mobile / tablet
  const [showMobileSidebar, setShowMobileSidebar] = useState<boolean>(false);

  // AI & Optimization State
  const [naturalPrompt, setNaturalPrompt] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [aiExplanation, setAiExplanation] = useState<string[]>([]);
  const [optimizations, setOptimizations] = useState<any[]>([]);

  // Saved Queries Library
  const [savedQueries, setSavedQueries] = useState<SavedQueryItem[]>([]);
  const [showSavedModal, setShowSavedModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>("");

  // Schema & Templates
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [activeTemplate, setActiveTemplate] = useState<string>(
    initialTemplate || "ecommerce"
  );
  const [schema, setSchema] = useState<TableSchema[]>([]);
  const [expandedTables, setExpandedTables] = useState<Record<string, boolean>>(
    { customers: true, orders: true }
  );

  // Execution State
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isFormatting, setIsFormatting] = useState<boolean>(false);
  const [isTranspiling, setIsTranspiling] = useState<boolean>(false);
  const [results, setResults] = useState<{
    columns: string[];
    rows: any[][];
    rowCount: number;
    elapsedMs: number;
    truncated: boolean;
    error?: string;
  } | null>(null);
  const [explainPlan, setExplainPlan] = useState<any[] | null>(null);

  // Fetch templates & saved queries on mount
  useEffect(() => {
    api
      .get("/sandboxes/templates")
      .then((res) => setTemplates(res.data))
      .catch((err) => console.error("Failed to load templates:", err));

    loadSavedQueries();
  }, []);

  const loadSavedQueries = () => {
    api
      .get("/library/queries")
      .then((res) => setSavedQueries(res.data))
      .catch((err) => console.error("Failed to load queries:", err));
  };

  // Initialize or fetch sandbox schema
  useEffect(() => {
    if (!sandboxId) {
      createSandbox(activeTemplate);
    } else {
      loadSchema(sandboxId);
    }
  }, [sandboxId]);

  const createSandbox = async (templateSlug: string) => {
    try {
      const res = await api.post("/sandboxes", {
        engine: "sqlite",
        template_slug: templateSlug,
      });
      onSandboxChange(res.data.id);
      setActiveTemplate(templateSlug);
      loadSchema(res.data.id);
    } catch (err: any) {
      console.error("Error creating sandbox:", err);
    }
  };

  const loadSchema = async (id: string) => {
    try {
      const res = await api.get(`/sandboxes/${id}/schema`);
      setSchema(res.data);
    } catch (err: any) {
      console.error("Error loading schema:", err);
    }
  };

  const handleTemplateChange = (slug: string) => {
    setActiveTemplate(slug);
    createSandbox(slug);
    if (slug === "ecommerce") {
      setQuery(
        "SELECT c.first_name, c.last_name, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS total_spent\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.id\nORDER BY total_spent DESC\nLIMIT 5;"
      );
    } else if (slug === "school") {
      setQuery(
        "SELECT s.name AS student, c.title AS course, e.grade\nFROM enrollments e\nJOIN students s ON e.student_id = s.id\nJOIN courses c ON e.course_id = c.id\nWHERE e.grade = 'A';"
      );
    } else if (slug === "blog") {
      setQuery(
        "SELECT p.title, a.username AS author, p.views\nFROM posts p\nJOIN authors a ON p.author_id = a.id\nORDER BY p.views DESC;"
      );
    } else {
      setQuery("CREATE TABLE demo (\n  id INTEGER PRIMARY KEY,\n  title TEXT\n);");
    }
    setShowMobileSidebar(false);
  };

  const toggleTableExpand = (tableName: string) => {
    setExpandedTables((prev) => ({ ...prev, [tableName]: !prev[tableName] }));
  };

  const insertQueryForTable = (tableName: string) => {
    setQuery(`SELECT * FROM ${tableName} LIMIT 20;`);
    setShowMobileSidebar(false);
  };

  // Run Query
  const handleRunQuery = async () => {
    if (!sandboxId || !query.trim()) return;
    setIsRunning(true);
    setActiveOutputTab("results");

    try {
      const res = await api.post(`/sandboxes/${sandboxId}/execute`, {
        query: query.trim(),
        confirmed: allowDdl,
        read_only: !allowDdl,
      });

      if (res.data.success) {
        setResults({
          columns: res.data.columns,
          rows: res.data.rows,
          rowCount: res.data.row_count,
          elapsedMs: res.data.elapsed_ms,
          truncated: res.data.truncated,
        });
        if (allowDdl) {
          loadSchema(sandboxId);
        }
      } else {
        setResults({
          columns: [],
          rows: [],
          rowCount: 0,
          elapsedMs: res.data.elapsed_ms || 0,
          truncated: false,
          error: res.data.error,
        });
      }
    } catch (err: any) {
      setResults({
        columns: [],
        rows: [],
        rowCount: 0,
        elapsedMs: 0,
        truncated: false,
        error: err.message,
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Format SQL
  const handleFormat = async () => {
    if (!query.trim()) return;
    setIsFormatting(true);
    try {
      const res = await api.post("/query/format", {
        query: query,
        dialect: "sqlite",
      });
      if (res.data.query) {
        setQuery(res.data.query);
      }
    } catch (err) {
      console.error("Format error:", err);
    } finally {
      setIsFormatting(false);
    }
  };

  // Transpile SQL Dialect
  const handleTranspile = async () => {
    if (!query.trim()) return;
    setIsTranspiling(true);
    setActiveOutputTab("transpile");

    try {
      const res = await api.post("/query/convert", {
        source_dialect: "sqlite",
        target_dialect: transpileTarget,
        query: query,
      });

      if (res.data.status === "success") {
        setTranspiledSql(res.data.query);
        setTranspileWarnings(res.data.warnings || []);
      } else {
        setTranspiledSql(`-- Error: ${res.data.error}`);
        setTranspileWarnings([]);
      }
    } catch (err: any) {
      setTranspiledSql(`-- Error: ${err.message}`);
    } finally {
      setIsTranspiling(false);
    }
  };

  // Explain Query Plan
  const handleExplain = async () => {
    if (!sandboxId || !query.trim()) return;
    setIsRunning(true);
    setActiveOutputTab("explain");

    try {
      const res = await api.post(`/sandboxes/${sandboxId}/execute`, {
        query: `EXPLAIN QUERY PLAN ${query.trim()}`,
        confirmed: false,
        read_only: true,
      });

      if (res.data.success) {
        setExplainPlan(res.data.rows);
      } else {
        setExplainPlan(null);
      }
    } catch (err: any) {
      console.error("Explain error:", err);
    } finally {
      setIsRunning(false);
    }
  };

  // AI: Generate SQL from Natural Language
  const handleGenerateSql = async () => {
    if (!naturalPrompt.trim()) return;
    setIsGenerating(true);

    try {
      const res = await api.post("/query/generate", {
        request: naturalPrompt.trim(),
        engine: "sqlite",
        language: language,
        schema_context: schema,
      });

      if (res.data.query) {
        setQuery(res.data.query);
        setNaturalPrompt("");
      }
    } catch (err: any) {
      console.error("Generate error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  // AI: Plain Language Explanation
  const handleExplainNatural = async () => {
    if (!query.trim()) return;
    setActiveOutputTab("ai_explain");

    try {
      const res = await api.post("/query/explain-natural", {
        query: query.trim(),
        language: language,
      });
      setAiExplanation(res.data.steps || []);
    } catch (err: any) {
      console.error("Explain error:", err);
    }
  };

  // Optimization & Lint Check
  const handleOptimizeCheck = async () => {
    if (!query.trim()) return;
    setActiveOutputTab("optimize");

    try {
      const res = await api.post("/query/optimize", {
        query: query.trim(),
        dialect: "sqlite",
      });
      setOptimizations(res.data.suggestions || []);
    } catch (err: any) {
      console.error("Optimize check error:", err);
    }
  };

  // Save Query to Library
  const handleSaveQuery = async () => {
    if (!newTitle.trim() || !query.trim()) return;
    try {
      await api.post("/library/queries", {
        title: newTitle.trim(),
        query_text: query.trim(),
        engine: "sqlite",
        dialect: "sqlite",
        description: "Saved from Query Studio",
      });
      setNewTitle("");
      setShowSavedModal(false);
      loadSavedQueries();
    } catch (err: any) {
      console.error("Save query error:", err);
    }
  };

  return (
    <div className="relative flex flex-col lg:flex-row h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A]">
      {/* MOBILE TOP CONTROLS BAR (< lg) */}
      <div className="lg:hidden flex items-center justify-between border-b border-slate-800 bg-[#10264A]/90 px-3 py-2 text-xs">
        <button
          onClick={() => setShowMobileSidebar(!showMobileSidebar)}
          className="flex items-center gap-1.5 rounded bg-slate-800 px-3 py-1.5 font-semibold text-[#F2B84B] border border-slate-700 min-h-[36px]"
        >
          {showMobileSidebar ? (
            <SidebarClose className="h-4 w-4" />
          ) : (
            <SidebarOpen className="h-4 w-4" />
          )}
          <span>
            {isId ? "Dataset & Tabel" : "Datasets & Schema"} ({schema.length})
          </span>
        </button>

        <span className="text-[11px] font-mono text-slate-400 capitalize">
          {activeTemplate} dataset
        </span>
      </div>

      {/* SIDEBAR: Desktop static, Mobile slide-down/drawer */}
      <aside
        className={`${
          showMobileSidebar ? "flex" : "hidden"
        } lg:flex w-full lg:w-72 flex-col border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#071A3A]/98 text-slate-200 z-30 max-h-[70vh] lg:max-h-none overflow-y-auto`}
      >
        {/* Template Selector */}
        <div className="border-b border-slate-800 p-3">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            {isId ? "Dataset Pembelajaran" : "Learning Dataset"}
          </label>
          <div className="mt-2 grid grid-cols-2 gap-1.5">
            {templates.map((tpl) => (
              <button
                key={tpl.slug}
                onClick={() => handleTemplateChange(tpl.slug)}
                className={`flex flex-col items-start rounded border p-2 text-left transition-all min-h-[44px] ${
                  activeTemplate === tpl.slug
                    ? "border-[#F2B84B] bg-[#10264A] text-white shadow-sm"
                    : "border-slate-800 bg-slate-900/40 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                }`}
              >
                <span className="text-xs font-semibold">{tpl.name}</span>
                <span className="mt-0.5 line-clamp-1 text-[10px] text-slate-500">
                  {tpl.description}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Schema Explorer */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span className="flex items-center gap-1.5">
              <TableIcon className="h-3.5 w-3.5 text-[#F2B84B]" />
              {isId ? "Struktur Tabel" : "Tables & Columns"} ({schema.length})
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {schema.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-500">
                {isId ? "Belum ada tabel" : "No tables found"}
              </div>
            ) : (
              schema.map((tbl) => (
                <div
                  key={tbl.name}
                  className="rounded border border-slate-800/80 bg-slate-900/30 overflow-hidden"
                >
                  <div
                    onClick={() => toggleTableExpand(tbl.name)}
                    className="flex cursor-pointer items-center justify-between px-2.5 py-2 text-xs hover:bg-slate-800/40 min-h-[36px]"
                  >
                    <div className="flex items-center gap-1.5 font-mono font-medium text-slate-200">
                      {expandedTables[tbl.name] ? (
                        <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                      ) : (
                        <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                      )}
                      <span>{tbl.name}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        insertQueryForTable(tbl.name);
                      }}
                      title="SELECT * FROM table"
                      className="rounded bg-[#10264A] px-2 py-1 text-[11px] font-mono text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors"
                    >
                      query
                    </button>
                  </div>

                  {expandedTables[tbl.name] && (
                    <div className="border-t border-slate-800/60 bg-black/20 px-2 py-1 space-y-1">
                      {tbl.columns.map((col) => (
                        <div
                          key={col.name}
                          className="flex items-center justify-between text-[11px] font-mono text-slate-400 py-0.5 pl-4 pr-1"
                        >
                          <div className="flex items-center gap-1">
                            {col.pk && (
                              <Key className="h-3 w-3 text-[#F2B84B]" />
                            )}
                            <span className={col.pk ? "text-[#F2B84B]" : ""}>
                              {col.name}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-600">
                            {col.type}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Saved Queries Shortcut */}
        <div className="border-t border-slate-800 p-2.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-1.5">
            <span className="flex items-center gap-1.5">
              <Bookmark className="h-3.5 w-3.5 text-[#F2B84B]" />
              {isId ? "Koleksi Query" : "Saved Queries"}
            </span>
            <button
              onClick={() => setShowSavedModal(true)}
              className="text-[#F2B84B] hover:underline text-[11px] p-1"
            >
              + {isId ? "Simpan" : "Save"}
            </button>
          </div>
          <div className="space-y-1 max-h-24 overflow-y-auto">
            {savedQueries.map((sq) => (
              <div
                key={sq.id}
                onClick={() => {
                  setQuery(sq.query_text);
                  setShowMobileSidebar(false);
                }}
                className="text-[11px] text-slate-300 hover:text-[#F2B84B] cursor-pointer truncate rounded px-2 py-1 hover:bg-slate-800/60 min-h-[32px] flex items-center"
                title={sq.title}
              >
                {sq.title}
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* MAIN QUERY WORKBENCH */}
      <main className="flex flex-1 flex-col overflow-hidden min-w-0">
        {/* AI Natural Language SQL Bar (Responsive layout) */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 border-b border-slate-800 bg-[#071A3A] p-2 sm:px-3 sm:py-1.5">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#F2B84B]">
            <Sparkles className="h-3.5 w-3.5 text-[#F2B84B]" />
            <span>AI SQL:</span>
          </div>
          <input
            type="text"
            placeholder={
              isId
                ? "Ketik: 'tampilkan 5 pelanggan belanja terbanyak'..."
                : "Type: 'show top 5 spending customers'..."
            }
            value={naturalPrompt}
            onChange={(e) => setNaturalPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerateSql()}
            className="flex-1 rounded bg-[#10264A]/80 border border-slate-700/60 px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#F2B84B] min-h-[38px] sm:min-h-0"
          />
          <button
            onClick={handleGenerateSql}
            disabled={isGenerating || !naturalPrompt.trim()}
            className="rounded bg-[#F2B84B] px-3.5 py-1.5 text-xs font-bold text-[#071A3A] hover:opacity-90 disabled:opacity-50 transition-opacity min-h-[38px] sm:min-h-0"
          >
            {isGenerating
              ? isId
                ? "Menghasilkan..."
                : "Generating..."
              : isId
              ? "Hasilkan SQL"
              : "Generate SQL"}
          </button>
        </div>

        {/* Editor Toolbar (Horizontally scrollable on small screens) */}
        <div className="flex h-auto sm:h-11 items-center justify-between border-b border-slate-800 bg-[#10264A]/50 p-2 sm:px-4 overflow-x-auto gap-2">
          <div className="flex items-center gap-1.5 sm:gap-2 flex-nowrap shrink-0">
            {/* Run Button */}
            <button
              onClick={handleRunQuery}
              disabled={isRunning}
              className="flex items-center gap-1.5 rounded bg-[#F2B84B] px-3 py-1.5 text-xs font-bold text-[#071A3A] hover:bg-[#F2B84B]/90 transition-colors shadow-sm disabled:opacity-50 min-h-[36px]"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>{isId ? "Jalankan" : "Run"}</span>
            </button>

            {/* Format Button */}
            <button
              onClick={handleFormat}
              disabled={isFormatting}
              className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/60 px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[36px]"
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>Format</span>
            </button>

            {/* Plain AI Explain */}
            <button
              onClick={handleExplainNatural}
              className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/60 px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[36px]"
            >
              <HelpCircle className="h-3.5 w-3.5 text-[#F2B84B]" />
              <span className="hidden sm:inline">
                {isId ? "Jelaskan" : "Explain"}
              </span>
            </button>

            {/* Lint & Optimize */}
            <button
              onClick={handleOptimizeCheck}
              className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/60 px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[36px]"
            >
              <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
              <span className="hidden sm:inline">Audit</span>
            </button>

            {/* Explain Plan */}
            <button
              onClick={handleExplain}
              className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/60 px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[36px]"
            >
              <Layers className="h-3.5 w-3.5" />
              <span>Plan</span>
            </button>

            {/* Dialect Transpiler */}
            <div className="flex items-center gap-1 pl-1 border-l border-slate-800">
              <select
                value={transpileTarget}
                onChange={(e) => setTranspileTarget(e.target.value)}
                className="rounded bg-slate-800 border border-slate-700 text-slate-200 text-xs px-2 py-1.5 focus:outline-none min-h-[36px]"
              >
                <option value="postgres">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="duckdb">DuckDB</option>
                <option value="oracle">Oracle</option>
              </select>
              <button
                onClick={handleTranspile}
                disabled={isTranspiling}
                className="flex items-center gap-1 rounded bg-[#10264A] border border-[#F2B84B]/40 px-2 py-1.5 text-xs text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors min-h-[36px]"
              >
                <ArrowRightLeft className="h-3 w-3" />
                <span>Konversi</span>
              </button>
            </div>
          </div>

          {/* Safety Mode Toggle */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setAllowDdl(!allowDdl)}
              className={`flex items-center gap-1.5 rounded px-2.5 py-1 text-[11px] font-mono transition-colors border min-h-[36px] ${
                allowDdl
                  ? "border-amber-500/50 bg-amber-500/10 text-amber-300"
                  : "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
              }`}
            >
              {allowDdl ? (
                <>
                  <ShieldAlert className="h-3.5 w-3.5" />
                  <span>DML/DDL</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>Hanya Baca</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Editor Area (Responsive height) */}
        <div className="h-56 sm:h-[40%] lg:h-[44%] w-full p-2">
          <SqlEditor
            value={query}
            onChange={setQuery}
            onExecute={handleRunQuery}
          />
        </div>

        {/* OUTPUT & RESULTS TABS */}
        <div className="flex flex-1 flex-col overflow-hidden border-t border-slate-800 bg-[#071A3A] min-h-[220px]">
          {/* Output Tab Header */}
          <div className="flex h-9 items-center justify-between border-b border-slate-800 bg-[#10264A]/30 px-2 sm:px-3 overflow-x-auto">
            <div className="flex items-center gap-1 sm:gap-2 shrink-0">
              <button
                onClick={() => setActiveOutputTab("results")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap ${
                  activeOutputTab === "results"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <TableIcon className="h-3.5 w-3.5" />
                <span>{isId ? "Hasil Query" : "Results"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("ai_explain")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap ${
                  activeOutputTab === "ai_explain"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Sparkles className="h-3.5 w-3.5 text-[#F2B84B]" />
                <span>{isId ? "Alur Logika" : "Logic"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("optimize")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap ${
                  activeOutputTab === "optimize"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
                <span>{isId ? "Audit" : "Audit"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("transpile")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap ${
                  activeOutputTab === "transpile"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <ArrowRightLeft className="h-3.5 w-3.5" />
                <span>{isId ? "Transpilasi" : "Transpile"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("explain")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap ${
                  activeOutputTab === "explain"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Layers className="h-3.5 w-3.5" />
                <span>Plan</span>
              </button>
            </div>

            {/* Execution Stats */}
            {results && !results.error && activeOutputTab === "results" && (
              <div className="flex items-center gap-2 sm:gap-3 text-xs font-mono text-slate-400 shrink-0">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                  {results.rowCount} {isId ? "baris" : "rows"}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3 text-slate-500" />
                  {results.elapsedMs} ms
                </span>
              </div>
            )}
          </div>

          {/* Tab Contents */}
          <div className="flex-1 overflow-auto p-2">
            {/* 1. Results View */}
            {activeOutputTab === "results" && (
              <>
                {results?.error ? (
                  <div className="m-2 rounded border border-rose-700/60 bg-rose-950/40 p-3 text-xs text-rose-300 font-mono">
                    <div className="flex items-center gap-2 font-bold mb-1">
                      <AlertTriangle className="h-4 w-4 text-rose-400" />
                      <span>
                        {isId ? "Kesalahan Eksekusi SQL" : "SQL Execution Error"}
                      </span>
                    </div>
                    <p className="whitespace-pre-wrap">{results.error}</p>
                  </div>
                ) : !results ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-500 py-6">
                    {isId
                      ? "Tekan 'Jalankan' atau Ctrl+Enter untuk mengeksekusi query"
                      : "Press 'Run' or Ctrl+Enter to execute query"}
                  </div>
                ) : results.columns.length === 0 ? (
                  <div className="p-4 text-center text-xs text-slate-400">
                    {isId
                      ? "Query selesai tanpa mengembalikan baris data."
                      : "Query executed with no returned rows."}
                  </div>
                ) : (
                  <div className="inline-block min-w-full overflow-x-auto rounded border border-slate-800">
                    <table className="min-w-full divide-y divide-slate-800 text-left font-mono text-xs">
                      <thead className="bg-[#10264A]/80 text-slate-300">
                        <tr>
                          {results.columns.map((col, idx) => (
                            <th
                              key={idx}
                              className="px-3 py-2 font-semibold tracking-wider text-[11px]"
                            >
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 bg-slate-900/30 text-slate-200">
                        {results.rows.map((row, rIdx) => (
                          <tr
                            key={rIdx}
                            className="hover:bg-slate-800/50 transition-colors"
                          >
                            {row.map((val, cIdx) => (
                              <td
                                key={cIdx}
                                className="whitespace-nowrap px-3 py-1.5 text-slate-300"
                              >
                                {val === null ? (
                                  <span className="italic text-slate-600">
                                    NULL
                                  </span>
                                ) : (
                                  String(val)
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}

            {/* 2. Logic Explanation Tab */}
            {activeOutputTab === "ai_explain" && (
              <div className="p-3">
                <h4 className="text-xs font-bold text-[#F2B84B] mb-2 flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4" />
                  <span>
                    {isId
                      ? "Alur Kerja Query Langkah-demi-Langkah:"
                      : "Step-by-Step Query Execution Logic:"}
                  </span>
                </h4>
                {aiExplanation.length === 0 ? (
                  <div className="text-xs text-slate-400">
                    {isId
                      ? "Klik 'Jelaskan' di toolbar untuk melihat urutan eksekusi query."
                      : "Click 'Explain' to inspect the query execution flow."}
                  </div>
                ) : (
                  <div className="space-y-1.5 font-sans text-xs text-slate-200 bg-[#10264A]/40 p-3 rounded border border-slate-800">
                    {aiExplanation.map((step, idx) => (
                      <div key={idx} className="flex items-start gap-2 py-0.5">
                        <span className="text-[#F2B84B] font-bold">•</span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* 3. Optimization Advice Tab */}
            {activeOutputTab === "optimize" && (
              <div className="p-3">
                <h4 className="text-xs font-bold text-amber-400 mb-2 flex items-center gap-1.5">
                  <Lightbulb className="h-4 w-4" />
                  <span>
                    {isId
                      ? "Hasil Audit Kinerja & Rekomendasi:"
                      : "Performance Audit & Recommendations:"}
                  </span>
                </h4>
                {optimizations.length === 0 ? (
                  <div className="text-xs text-slate-400">
                    {isId
                      ? "Query terlihat bersih atau klik 'Audit' untuk memeriksa anti-pattern."
                      : "No critical anti-patterns detected or click 'Audit'."}
                  </div>
                ) : (
                  <div className="space-y-2">
                    {optimizations.map((opt, idx) => (
                      <div
                        key={idx}
                        className="rounded border border-amber-800/60 bg-amber-950/30 p-2.5 text-xs text-amber-200"
                      >
                        <div className="flex items-center justify-between font-bold text-[11px] mb-1">
                          <span className="uppercase tracking-wider text-amber-400">
                            {opt.type}
                          </span>
                          <span className="font-mono text-slate-400">
                            {opt.rule}
                          </span>
                        </div>
                        <p className="text-slate-300 leading-relaxed">
                          {opt.message}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* 4. Transpile View */}
            {activeOutputTab === "transpile" && (
              <div className="h-full flex flex-col space-y-2">
                {transpileWarnings.length > 0 && (
                  <div className="rounded border border-amber-600/40 bg-amber-950/20 p-2 text-xs text-amber-300">
                    <p className="font-semibold flex items-center gap-1">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      {isId
                        ? "Peringatan Semantik Dialek:"
                        : "Dialect Semantics Warning:"}
                    </p>
                    <ul className="list-disc pl-5 mt-1 text-[11px]">
                      {transpileWarnings.map((w, idx) => (
                        <li key={idx}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="flex-1">
                  <SqlEditor
                    value={
                      transpiledSql ||
                      "-- Klik 'Konversi' untuk melihat SQL target"
                    }
                    onChange={() => {}}
                    readOnly={true}
                  />
                </div>
              </div>
            )}

            {/* 5. Explain Plan View */}
            {activeOutputTab === "explain" && (
              <div className="p-2">
                {!explainPlan ? (
                  <div className="text-center text-xs text-slate-500 py-6">
                    {isId
                      ? "Klik 'Plan' untuk melihat rencana optimasi query"
                      : "Click 'Plan' to inspect the execution plan"}
                  </div>
                ) : (
                  <div className="rounded border border-slate-800 bg-[#10264A]/40 p-3 font-mono text-xs overflow-x-auto">
                    <div className="font-bold text-[#F2B84B] mb-2">
                      SQLite Query Plan:
                    </div>
                    {explainPlan.map((step, idx) => (
                      <div key={idx} className="py-1 text-slate-300">
                        {step.detail || JSON.stringify(step)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Save Query Modal */}
      {showSavedModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-700 bg-[#071A3A] p-5 shadow-2xl">
            <h3 className="text-sm font-bold text-white mb-2">
              {isId ? "Simpan Query ke Koleksi" : "Save Query to Library"}
            </h3>
            <p className="text-xs text-slate-400 mb-3">
              {isId ? "Beri judul untuk kueri Anda:" : "Give this query a title:"}
            </p>
            <input
              type="text"
              placeholder="e.g. Analisis Pelanggan VIP"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white focus:outline-none focus:border-[#F2B84B] mb-4 min-h-[40px]"
            />
            <div className="flex justify-end gap-2 text-xs">
              <button
                onClick={() => setShowSavedModal(false)}
                className="px-4 py-2 rounded text-slate-400 hover:text-white min-h-[40px]"
              >
                {isId ? "Batal" : "Cancel"}
              </button>
              <button
                onClick={handleSaveQuery}
                disabled={!newTitle.trim()}
                className="px-5 py-2 rounded bg-[#F2B84B] font-bold text-[#071A3A] hover:opacity-90 disabled:opacity-50 min-h-[40px]"
              >
                {isId ? "Simpan" : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

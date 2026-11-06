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
  Download,
  RefreshCw,
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

const TEMPLATE_LOCALES: Record<
  string,
  { name: string; nameId: string; desc: string; descId: string }
> = {
  banking: {
    name: "Core Banking System",
    nameId: "Core Banking System",
    desc: "Customers, savings/checking accounts, transactions (QRIS/Transfer/ATM), and loans",
    descId: "Nasabah, rekening tabungan/giro, mutasi transaksi (QRIS/Transfer/ATM), dan pinjaman",
  },
  ecommerce: {
    name: "E-Commerce Store",
    nameId: "Toko E-Commerce",
    desc: "Customers, products, categories, and shopping order transactions",
    descId: "Pelanggan, produk, kategori, dan transaksi belanja online",
  },
  school: {
    name: "University Academy",
    nameId: "Akademi Kampus",
    desc: "Campus academics: students, professors, courses, and GPA grades",
    descId: "Akademik kampus: mahasiswa, dosen, mata kuliah, dan indeks prestasi",
  },
  blog: {
    name: "Tech Blog Platform",
    nameId: "Platform Blog Teknologi",
    desc: "Authors, tech articles, tags, and reader comments",
    descId: "Penulis, publikasi artikel teknik, tag, dan komentar pembaca",
  },
  blank: {
    name: "Blank Database",
    nameId: "Database Kosong",
    desc: "Empty SQLite database for schema experiments and custom DDL",
    descId: "Database SQLite kosong untuk eksperimen skema dan DDL bebas",
  },
};

const DEFAULT_BANKING_SQL = `-- Analisis Saldo Rekening Nasabah (Core Banking System)
SELECT
  c.cif_number,
  c.full_name,
  a.account_number,
  a.account_type,
  a.balance,
  b.branch_name
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
JOIN branches b ON a.branch_id = b.branch_id
ORDER BY a.balance DESC;`;

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
    initialQuery || DEFAULT_BANKING_SQL
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
    initialTemplate || "banking"
  );
  const [schema, setSchema] = useState<TableSchema[]>([]);
  const [schemaStatus, setSchemaStatus] = useState<
    "idle" | "loading" | "ready" | "empty" | "error"
  >("idle");
  const [schemaError, setSchemaError] = useState<string | null>(null);
  const [expandedTables, setExpandedTables] = useState<Record<string, boolean>>(
    { accounts: true, customers: true, transactions: true }
  );

  // Execution & Provenance State
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
  const [lastExecutedQuery, setLastExecutedQuery] = useState<string | null>(null);
  const [lastExecutedTimestamp, setLastExecutedTimestamp] = useState<Date | null>(null);
  const [lastExecutedEngine, setLastExecutedEngine] = useState<string>("sqlite");

  // Provenance flag: whether editor SQL was modified after the last run
  const isQueryStale = Boolean(
    results && lastExecutedQuery && query.trim() !== lastExecutedQuery
  );

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

  const [activeEngine, setActiveEngine] = useState<
    "sqlite" | "postgres" | "mysql" | "oracle" | "mssql" | "db2"
  >("sqlite");

  // Initialize or fetch sandbox schema
  useEffect(() => {
    if (!sandboxId) {
      createSandbox(activeTemplate, activeEngine);
    } else {
      loadSchema(sandboxId);
    }
  }, [sandboxId]);

  const createSandbox = async (
    templateSlug: string,
    engineChoice?: "sqlite" | "postgres" | "mysql" | "oracle" | "mssql" | "db2"
  ) => {
    const engineToUse = engineChoice || activeEngine;
    setSchemaStatus("loading");
    setSchemaError(null);
    try {
      const res = await api.post("/sandboxes", {
        engine: engineToUse,
        template_slug: templateSlug,
      });
      onSandboxChange(res.data.id);
      setActiveTemplate(templateSlug);
      setActiveEngine(engineToUse);
      loadSchema(res.data.id);
    } catch (err: any) {
      console.error("Error creating sandbox:", err);
      setSchemaStatus("error");
      setSchemaError(
        err?.response?.data?.detail || err.message || "Failed to provision database sandbox"
      );
    }
  };

  const handleEngineChange = (
    engine: "sqlite" | "postgres" | "mysql" | "oracle" | "mssql" | "db2"
  ) => {
    setActiveEngine(engine);
    createSandbox(activeTemplate, engine);
  };

  const loadSchema = async (id: string) => {
    setSchemaStatus("loading");
    setSchemaError(null);
    try {
      const res = await api.get(`/sandboxes/${id}/schema`);
      const tables = res.data || [];
      setSchema(tables);
      setSchemaStatus(tables.length === 0 ? "empty" : "ready");
    } catch (err: any) {
      console.error("Error loading schema:", err);
      setSchemaStatus("error");
      setSchemaError(
        err?.response?.data?.detail || err.message || "Failed to load table schema"
      );
    }
  };

  const handleTemplateChange = (slug: string) => {
    setActiveTemplate(slug);
    createSandbox(slug, activeEngine);
    if (slug === "banking") {
      setQuery(DEFAULT_BANKING_SQL);
      setExpandedTables({ accounts: true, customers: true, transactions: true });
    } else if (slug === "ecommerce") {
      setQuery(
        "SELECT c.first_name, c.last_name, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS total_spent\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.id\nORDER BY total_spent DESC\nLIMIT 5;"
      );
      setExpandedTables({ customers: true, orders: true });
    } else if (slug === "school") {
      setQuery(
        "SELECT s.name AS student, c.title AS course, e.grade\nFROM enrollments e\nJOIN students s ON e.student_id = s.id\nJOIN courses c ON e.course_id = c.id\nWHERE e.grade = 'A';"
      );
      setExpandedTables({ students: true, courses: true });
    } else if (slug === "blog") {
      setQuery(
        "SELECT p.title, a.username AS author, p.views\nFROM posts p\nJOIN authors a ON p.author_id = a.id\nORDER BY p.views DESC;"
      );
      setExpandedTables({ posts: true, authors: true });
    } else {
      setQuery("CREATE TABLE demo (\n  id INTEGER PRIMARY KEY,\n  title TEXT\n);");
      setExpandedTables({});
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
        setLastExecutedQuery(query.trim());
        setLastExecutedTimestamp(new Date());
        setLastExecutedEngine(activeEngine);
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
        setLastExecutedQuery(query.trim());
        setLastExecutedTimestamp(new Date());
        setLastExecutedEngine(activeEngine);
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
      setLastExecutedQuery(query.trim());
      setLastExecutedTimestamp(new Date());
      setLastExecutedEngine(activeEngine);
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

  // Export Sandbox SQL Dump
  const handleExportSql = () => {
    if (!sandboxId) return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
    window.open(`${apiUrl}/sandboxes/${sandboxId}/export?format=sql`, "_blank");
  };

  // Explain Query Plan
  const handleExplain = async () => {
    if (!sandboxId || !query.trim()) return;
    setIsRunning(true);
    setActiveOutputTab("explain");

    let explainSql = `EXPLAIN QUERY PLAN ${query.trim()}`;
    if (activeEngine === "postgres") {
      explainSql = `EXPLAIN (ANALYZE, BUFFERS, VERBOSE) ${query.trim()};`;
    } else if (activeEngine === "mysql") {
      explainSql = `EXPLAIN ${query.trim()};`;
    } else if (activeEngine === "oracle") {
      explainSql = `EXPLAIN PLAN FOR ${query.trim()};`;
    } else if (activeEngine === "mssql") {
      explainSql = `SET SHOWPLAN_TEXT ON; ${query.trim()};`;
    } else if (activeEngine === "db2") {
      explainSql = `EXPLAIN PLAN FOR ${query.trim()};`;
    }

    try {
      const res = await api.post(`/sandboxes/${sandboxId}/execute`, {
        query: explainSql,
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
        language: language,
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
      <div className="lg:hidden flex items-center justify-between border-b border-slate-800 bg-[#10264A]/90 px-3 py-2 text-xs gap-2">
        <button
          onClick={() => setShowMobileSidebar(!showMobileSidebar)}
          className="flex items-center gap-1.5 rounded-lg bg-slate-800 px-3 py-2 font-semibold text-[#F2B84B] border border-slate-700 min-h-[40px] shrink-0 active:bg-slate-700"
        >
          {showMobileSidebar ? (
            <SidebarClose className="h-4 w-4" />
          ) : (
            <SidebarOpen className="h-4 w-4" />
          )}
          <span>
            {isId ? "Skema & Tabel" : "Schema"} ({schema.length})
          </span>
        </button>

        {/* Active Engine & Template Indicator (Static, Truthful Badges) */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-300 shrink-0">
          <span
            title={
              activeEngine === "postgres"
                ? "PostgreSQL 17.0 (Dedicated Docker Container Sandbox)"
                : activeEngine === "mysql"
                ? "MariaDB 11.3 (MySQL Compatible Docker Container Sandbox)"
                : activeEngine === "oracle"
                ? "Oracle 23ai (SQLGlot AST Transpilation Sandbox)"
                : activeEngine === "mssql"
                ? "SQL Server 2022 (T-SQL AST Transpilation Sandbox)"
                : activeEngine === "db2"
                ? "IBM Db2 11.5 (ANSI / SQLGlot AST Transpilation Sandbox)"
                : "SQLite 3.45.0 (Isolated Native Sandbox)"
            }
            className="rounded-lg bg-slate-900 px-2.5 py-1 border border-slate-700/80 text-[#F2B84B] font-bold"
          >
            {activeEngine === "postgres"
              ? "PostgreSQL 17"
              : activeEngine === "mysql"
              ? "MariaDB 11.3 (MySQL)"
              : activeEngine === "oracle"
              ? "Oracle 23ai (Transpiled)"
              : activeEngine === "mssql"
              ? "SQL Server 2022 (Transpiled)"
              : activeEngine === "db2"
              ? "IBM Db2 11.5 (Transpiled)"
              : "SQLite 3.45"}
          </span>
          <span className="hidden sm:inline-block rounded-lg bg-slate-900/60 px-2 py-1 border border-slate-800 text-slate-400 capitalize">
            {activeTemplate}
          </span>
        </div>
      </div>

      {/* SIDEBAR: Desktop static, Mobile slide-down/drawer */}
      <aside
        className={`${
          showMobileSidebar ? "flex" : "hidden"
        } lg:flex w-full lg:w-72 flex-col border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#071A3A]/98 text-slate-200 z-30 max-h-[70vh] lg:max-h-none overflow-y-auto no-scrollbar touch-scroll`}
      >
        {/* Engine Switcher (Truthful Architecture & Versioning) */}
        <div className="border-b border-slate-800 p-3 bg-[#10264A]/30">
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              {isId ? "Mesin Database Sandbox" : "Sandbox Database Engine"}
            </label>
            <span className="text-[9px] text-[#F2B84B] font-mono">
              {activeEngine === "sqlite" || activeEngine === "postgres" || activeEngine === "mysql"
                ? (isId ? "Kontainer/Native" : "Native Container")
                : (isId ? "AST Emulasi" : "AST Transpiled")}
            </span>
          </div>
          <div className="grid grid-cols-2 xs:grid-cols-3 gap-1.5">
            {[
              {
                id: "sqlite" as const,
                name: "SQLite",
                badge: "3.45",
                type: isId ? "Sandbox Lokal Terisolasi" : "Isolated Native Sandbox",
              },
              {
                id: "postgres" as const,
                name: "Postgres",
                badge: "17",
                type: isId ? "Kontainer Docker PostgreSQL 17" : "Docker Container PostgreSQL 17",
              },
              {
                id: "mysql" as const,
                name: "MariaDB",
                badge: "11.3",
                type: isId ? "Kontainer Docker (Kompatibel MySQL)" : "Docker Container (MySQL Compatible)",
              },
              {
                id: "oracle" as const,
                name: "Oracle",
                badge: "23ai",
                type: isId ? "Emulasi AST Transpiled SQLGlot" : "SQLGlot AST Transpiled",
              },
              {
                id: "mssql" as const,
                name: "SQL Server",
                badge: "2022",
                type: isId ? "Emulasi AST Transpiled T-SQL" : "T-SQL AST Transpiled",
              },
              {
                id: "db2" as const,
                name: "IBM Db2",
                badge: "11.5",
                type: isId ? "Emulasi AST Transpiled ANSI/Db2" : "ANSI/Db2 AST Transpiled",
              },
            ].map((eng) => (
              <button
                key={eng.id}
                onClick={() => handleEngineChange(eng.id)}
                title={`${eng.name} ${eng.badge} - ${eng.type}`}
                className={`flex flex-col items-center justify-center py-2 px-1 rounded-lg text-xs font-semibold transition-all border min-h-[44px] active:scale-95 ${
                  activeEngine === eng.id
                    ? "bg-[#10264A] text-[#F2B84B] border-[#F2B84B] shadow-sm ring-1 ring-[#F2B84B]/40"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border-slate-800"
                }`}
              >
                <span className="text-[11px] font-bold">{eng.name}</span>
                <span className="text-[9px] opacity-75 font-mono">{eng.badge}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Template Selector */}
        <div className="border-b border-slate-800 p-3">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            {isId ? "Dataset Sandbox Aktif" : "Active Sandbox Dataset"}
          </label>
          <div className="mt-2 grid grid-cols-1 xs:grid-cols-2 gap-1.5">
            {templates.map((tpl) => (
              <button
                key={tpl.slug}
                onClick={() => handleTemplateChange(tpl.slug)}
                className={`flex flex-col items-start rounded-lg border p-2.5 text-left transition-all min-h-[48px] ${
                  activeTemplate === tpl.slug
                    ? "border-[#F2B84B] bg-[#10264A] text-white shadow-sm ring-1 ring-[#F2B84B]/40"
                    : "border-slate-800 bg-slate-900/40 text-slate-400 hover:border-slate-700 hover:text-slate-200 active:bg-slate-800"
                }`}
              >
                <span className="text-xs font-bold text-slate-100 flex items-center gap-1">
                  {tpl.slug === "banking" && "🏦 "}
                  {tpl.slug === "dba_ops" && "⚡ "}
                  {TEMPLATE_LOCALES[tpl.slug]
                    ? isId
                      ? TEMPLATE_LOCALES[tpl.slug].nameId
                      : TEMPLATE_LOCALES[tpl.slug].name
                    : tpl.name}
                </span>
                <span className="mt-0.5 line-clamp-1 text-[10px] text-slate-400">
                  {TEMPLATE_LOCALES[tpl.slug]
                    ? isId
                      ? TEMPLATE_LOCALES[tpl.slug].descId
                      : TEMPLATE_LOCALES[tpl.slug].desc
                    : tpl.description}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Schema Explorer with Robust State Machine */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span className="flex items-center gap-1.5">
              <TableIcon className="h-3.5 w-3.5 text-[#F2B84B]" />
              {isId ? "Struktur Tabel" : "Tables & Columns"} ({schema.length})
            </span>
            <button
              onClick={() => sandboxId && loadSchema(sandboxId)}
              disabled={schemaStatus === "loading"}
              title={isId ? "Muat ulang skema tabel" : "Reload table schema"}
              className="rounded p-1 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <RefreshCw
                className={`h-3 w-3 ${
                  schemaStatus === "loading" ? "animate-spin text-[#F2B84B]" : ""
                }`}
              />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {schemaStatus === "loading" ? (
              <div className="p-3 space-y-2 animate-pulse">
                <div className="text-[11px] text-slate-400 flex items-center gap-2 mb-2">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin text-[#F2B84B]" />
                  <span>
                    {isId ? "Mengambil skema tabel sandbox..." : "Loading sandbox table schema..."}
                  </span>
                </div>
                <div className="h-8 bg-slate-800/80 rounded-lg"></div>
                <div className="h-8 bg-slate-800/80 rounded-lg"></div>
                <div className="h-8 bg-slate-800/80 rounded-lg"></div>
              </div>
            ) : schemaStatus === "error" ? (
              <div className="p-3 m-1 rounded-xl border border-rose-800/60 bg-rose-950/30 text-xs text-rose-300">
                <div className="flex items-center gap-1.5 font-bold mb-1 text-rose-200">
                  <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
                  <span>{isId ? "Gagal memuat skema" : "Failed to load schema"}</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed mb-2.5">
                  {schemaError || (isId ? "Koneksi ke sandbox terputus." : "Connection to sandbox failed.")}
                </p>
                <button
                  onClick={() => sandboxId ? loadSchema(sandboxId) : createSandbox(activeTemplate, activeEngine)}
                  className="w-full flex items-center justify-center gap-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 border border-rose-700/80 py-1.5 text-xs font-semibold text-white transition-colors"
                >
                  <RefreshCw className="h-3 w-3" />
                  <span>{isId ? "Coba Muat Ulang" : "Retry Connection"}</span>
                </button>
              </div>
            ) : schema.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-400 space-y-1.5">
                <p className="font-semibold text-slate-300">
                  {isId ? "Database belum memiliki tabel." : "Database has no tables yet."}
                </p>
                <p className="text-[10px] text-slate-500 leading-relaxed">
                  {isId
                    ? "Pilih template dataset di atas atau ketik perintah DDL 'CREATE TABLE ...' lalu klik Jalankan."
                    : "Choose a dataset template above or write DDL 'CREATE TABLE ...' and click Run."}
                </p>
              </div>
            ) : (
              schema.map((tbl) => (
                <div
                  key={tbl.name}
                  className="rounded-lg border border-slate-800/80 bg-slate-900/30 overflow-hidden"
                >
                  <div
                    onClick={() => toggleTableExpand(tbl.name)}
                    className="flex cursor-pointer items-center justify-between px-2.5 py-2 text-xs hover:bg-slate-800/40 min-h-[40px]"
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
                      className="rounded bg-[#10264A] px-2.5 py-1 text-[11px] font-mono font-semibold text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors min-h-[30px]"
                    >
                      {isId ? "kueri" : "query"}
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
                            <span className={col.pk ? "text-[#F2B84B] font-semibold" : ""}>
                              {col.name}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500">
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
              className="text-[#F2B84B] hover:underline text-[11px] p-1 font-semibold"
            >
              + {isId ? "Simpan" : "Save"}
            </button>
          </div>
          <div className="space-y-1 max-h-24 overflow-y-auto no-scrollbar">
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
      <main className="flex flex-1 flex-col h-full min-h-0 overflow-hidden min-w-0">
        {/* AI Natural Language SQL Bar (Responsive layout) */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 border-b border-slate-800 bg-[#071A3A] p-2.5 sm:px-3 sm:py-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#F2B84B] shrink-0">
            <Sparkles className="h-4 w-4 text-[#F2B84B]" />
            <span>AI SQL:</span>
          </div>
          <input
            type="text"
            placeholder={
              isId
                ? activeTemplate === "banking"
                  ? "Contoh: cari 5 nasabah dengan saldo tabungan tertinggi..."
                  : "Ketik: tampilkan 5 pelanggan belanja terbanyak..."
                : "Type: find top 5 customers by account balance..."
            }
            value={naturalPrompt}
            onChange={(e) => setNaturalPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerateSql()}
            className="flex-1 rounded-lg bg-[#10264A]/80 border border-slate-700/60 px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#F2B84B] min-h-[42px]"
          />
          <button
            onClick={handleGenerateSql}
            disabled={isGenerating || !naturalPrompt.trim()}
            className="rounded-lg bg-[#F2B84B] px-4 py-2 text-xs font-bold text-[#071A3A] hover:opacity-90 disabled:opacity-50 transition-opacity min-h-[42px] shrink-0 active:scale-95"
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

        {/* Editor Toolbar (Harmonized actions with tooltips) */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-[#10264A]/50 px-2 py-1.5 sm:px-3 overflow-x-auto no-scrollbar touch-scroll gap-2">
          <div className="flex items-center gap-1.5 sm:gap-2 flex-nowrap shrink-0">
            {/* Run Button (Prominent 44px hit target) */}
            <button
              onClick={handleRunQuery}
              disabled={isRunning}
              title={
                isId
                  ? "Jalankan kueri ke sandbox aktif (Ctrl+Enter)"
                  : "Execute query against active sandbox (Ctrl+Enter)"
              }
              className="flex items-center gap-1.5 rounded-lg bg-[#F2B84B] px-3.5 py-2 text-xs font-bold text-[#071A3A] hover:bg-[#F2B84B]/90 transition-colors shadow-sm disabled:opacity-50 min-h-[42px] active:scale-95"
            >
              <Play className="h-4 w-4 fill-current" />
              <span>{isRunning ? "..." : isId ? "Jalankan" : "Run"}</span>
            </button>

            {/* Format Button */}
            <button
              onClick={handleFormat}
              disabled={isFormatting}
              title={isId ? "Rapikan format penulisan SQL" : "Format SQL syntax"}
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[42px]"
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>Format</span>
            </button>

            {/* Plain AI Explain */}
            <button
              onClick={handleExplainNatural}
              title={
                isId
                  ? "Jelaskan logika dan tujuan kueri SQL dalam bahasa manusia"
                  : "Explain SQL query logic and intent in plain English"
              }
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[42px]"
            >
              <HelpCircle className="h-3.5 w-3.5 text-[#F2B84B]" />
              <span>{isId ? "Jelaskan" : "Explain"}</span>
            </button>

            {/* Lint & Optimize */}
            <button
              onClick={handleOptimizeCheck}
              title={
                isId
                  ? "Audit risiko keamanan (injeksi/destruktif) dan anti-pattern kueri"
                  : "Audit security risks (injection/destructive) and query anti-patterns"
              }
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[42px]"
            >
              <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
              <span>Audit</span>
            </button>

            {/* Explain Plan */}
            <button
              onClick={handleExplain}
              title={
                isId
                  ? "Lihat rencana eksekusi kueri mesin database (EXPLAIN PLAN)"
                  : "View native database execution plan (EXPLAIN PLAN)"
              }
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700/60 transition-colors min-h-[42px]"
            >
              <Layers className="h-3.5 w-3.5" />
              <span>{isId ? "Rencana" : "Plan"}</span>
            </button>

            {/* Dialect Transpiler */}
            <div className="flex items-center gap-1 pl-1 border-l border-slate-800">
              <select
                value={transpileTarget}
                onChange={(e) => setTranspileTarget(e.target.value)}
                className="rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-xs px-2.5 py-2 focus:outline-none min-h-[42px]"
              >
                <option value="postgres">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="duckdb">DuckDB</option>
                <option value="oracle">Oracle</option>
                <option value="tsql">SQL Server (T-SQL)</option>
                <option value="db2">IBM Db2</option>
              </select>
              <button
                onClick={handleTranspile}
                disabled={isTranspiling}
                title={
                  isId
                    ? "Konversi sintaks SQL ke dialek mesin database lain via SQLGlot"
                    : "Transpile SQL syntax across database engines via SQLGlot"
                }
                className="flex items-center gap-1 rounded-lg bg-[#10264A] border border-[#F2B84B]/40 px-3 py-2 text-xs font-semibold text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors min-h-[42px]"
              >
                <ArrowRightLeft className="h-3.5 w-3.5" />
                <span>{isId ? "Konversi" : "Convert"}</span>
              </button>
            </div>

            {/* Export SQL */}
            <button
              onClick={handleExportSql}
              title={isId ? "Unduh DDL/DML SQL Database" : "Export SQL Database Dump"}
              className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-700/60 transition-colors min-h-[42px]"
            >
              <Download className="h-3.5 w-3.5 text-emerald-400" />
              <span>{isId ? "Ekspor" : "Export"}</span>
            </button>
          </div>

          {/* Safety Mode Toggle */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setAllowDdl(!allowDdl)}
              title={
                allowDdl
                  ? isId
                    ? "Mode Modifikasi (DML/DDL): Perubahan data diizinkan"
                    : "Modification Mode (DML/DDL): Data modifications permitted"
                  : isId
                  ? "Mode Keamanan: Hanya Baca"
                  : "Safety Mode: Read Only"
              }
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-[11px] font-mono transition-colors border min-h-[42px] ${
                allowDdl
                  ? "border-amber-500/50 bg-amber-500/10 text-amber-300"
                  : "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
              }`}
            >
              {allowDdl ? (
                <>
                  <ShieldAlert className="h-4 w-4" />
                  <span>DML/DDL</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="h-4 w-4" />
                  <span>{isId ? "Hanya Baca" : "Read Only"}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Editor Area (Explicit responsive height with shrink-0) */}
        <div className="h-64 sm:h-72 lg:h-[340px] xl:h-[380px] w-full p-2 shrink-0">
          <SqlEditor
            value={query}
            onChange={setQuery}
            onExecute={handleRunQuery}
            language={language}
            engine={activeEngine}
          />
        </div>

        {/* OUTPUT & RESULTS TABS */}
        <div className="flex flex-1 flex-col overflow-hidden border-t border-slate-800 bg-[#071A3A] min-h-[240px]">
          {/* Output Tab Header (Touch scrollable) */}
          <div className="flex h-10 items-center justify-between border-b border-slate-800 bg-[#10264A]/30 px-2 sm:px-3 overflow-x-auto no-scrollbar touch-scroll gap-2">
            <div className="flex items-center gap-1 sm:gap-2 shrink-0">
              <button
                onClick={() => setActiveOutputTab("results")}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap min-h-[38px] ${
                  activeOutputTab === "results"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <TableIcon className="h-3.5 w-3.5" />
                <span>{isId ? "Hasil Data" : "Data Results"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("ai_explain")}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap min-h-[38px] ${
                  activeOutputTab === "ai_explain"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Sparkles className="h-3.5 w-3.5 text-[#F2B84B]" />
                <span>{isId ? "Alur Logika" : "Logic Flow"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("optimize")}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap min-h-[38px] ${
                  activeOutputTab === "optimize"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
                <span>{isId ? "Audit Risiko" : "Risk Audit"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("transpile")}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap min-h-[38px] ${
                  activeOutputTab === "transpile"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <ArrowRightLeft className="h-3.5 w-3.5" />
                <span>{isId ? "Transpilasi Dialek" : "Dialect Transpile"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("explain")}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold transition-colors border-b-2 whitespace-nowrap min-h-[38px] ${
                  activeOutputTab === "explain"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Layers className="h-3.5 w-3.5" />
                <span>{isId ? "Rencana Eksekusi" : "Execution Plan"}</span>
              </button>
            </div>

            {/* Execution Stats & Provenance Badge */}
            {results && !results.error && activeOutputTab === "results" && (
              <div className="flex items-center gap-2 sm:gap-3 text-xs font-mono shrink-0 pr-1">
                {isQueryStale ? (
                  <span
                    title={
                      isId
                        ? "Kueri pada editor telah dimodifikasi sejak eksekusi ini dijalankan."
                        : "Query text in editor was edited after this run."
                    }
                    className="flex items-center gap-1 rounded bg-amber-950/80 border border-amber-600/70 px-2 py-0.5 text-[10px] text-amber-300 font-semibold"
                  >
                    <AlertTriangle className="h-3 w-3 text-amber-400" />
                    <span>{isId ? "Hasil Kueri Sebelumnya" : "Previous Run Result"}</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-1 rounded bg-emerald-950/80 border border-emerald-600/70 px-2 py-0.5 text-[10px] text-emerald-300 font-semibold">
                    <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                    <span>
                      {isId ? "Eksekusi Langsung" : "Live Execution"} ({lastExecutedEngine.toUpperCase()})
                    </span>
                  </span>
                )}
                <span className="text-slate-300 font-bold">
                  {results.rowCount} {isId ? "baris" : "rows"}
                </span>
                <span className="hidden sm:flex items-center gap-1 text-slate-500">
                  <Clock className="h-3 w-3" />
                  {results.elapsedMs} ms
                </span>
              </div>
            )}
          </div>

          {/* Tab Contents */}
          <div className="flex-1 overflow-auto p-2 no-scrollbar touch-scroll">
            {/* 1. Results View */}
            {activeOutputTab === "results" && (
              <>
                {results?.error ? (
                  <div className="m-2 rounded-lg border border-rose-700/60 bg-rose-950/40 p-3 text-xs text-rose-300 font-mono">
                    <div className="flex items-center gap-2 font-bold mb-1">
                      <AlertTriangle className="h-4 w-4 text-rose-400" />
                      <span>
                        {isId ? "Kesalahan Eksekusi SQL" : "SQL Execution Error"}
                      </span>
                    </div>
                    <p className="whitespace-pre-wrap">{results.error}</p>
                  </div>
                ) : !results ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center text-slate-500 space-y-2">
                    <div className="rounded-full bg-slate-900 border border-slate-800 p-3">
                      <Play className="h-6 w-6 text-slate-500 ml-0.5" />
                    </div>
                    <p className="text-xs font-semibold text-slate-300">
                      {isId ? "Belum Ada Eksekusi Kueri" : "No Execution Yet"}
                    </p>
                    <p className="text-[11px] text-slate-500 max-w-sm leading-relaxed">
                      {isId
                        ? "Klik tombol 'Jalankan' di atas atau tekan Ctrl+Enter untuk mengeksekusi kueri pada sandbox aktif."
                        : "Click 'Run' above or press Ctrl+Enter to execute query against the active database sandbox."}
                    </p>
                  </div>
                ) : results.columns.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-400">
                    <p className="font-semibold text-slate-300">
                      {isId ? "Query berhasil dieksekusi." : "Query executed successfully."}
                    </p>
                    <p className="text-[11px] text-slate-500 mt-1">
                      {isId
                        ? "Pernyataan selesai tanpa mengembalikan baris data (DDL / DML)."
                        : "Statement completed without returning data rows (DDL / DML)."}
                    </p>
                  </div>
                ) : (
                  <div className="w-full max-w-full overflow-x-auto no-scrollbar touch-scroll rounded-lg border border-slate-800 bg-slate-900/30">
                    <table className="w-full min-w-[500px] divide-y divide-slate-800 text-left font-mono text-xs">
                      <thead className="bg-[#10264A]/90 text-slate-300 sticky top-0">
                        <tr>
                          {results.columns.map((col, idx) => (
                            <th
                              key={idx}
                              className="px-3 py-2 font-bold tracking-wider text-[11px] text-slate-200"
                            >
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-200">
                        {results.rows.map((row, rIdx) => (
                          <tr
                            key={rIdx}
                            className="hover:bg-slate-800/50 transition-colors"
                          >
                            {row.map((val, cIdx) => (
                              <td
                                key={cIdx}
                                className="whitespace-nowrap px-3 py-2 text-slate-300"
                              >
                                {val === null ? (
                                  <span className="italic text-slate-600">
                                    NULL
                                  </span>
                                ) : typeof val === "number" ? (
                                  <span className="text-emerald-400">
                                    {val.toLocaleString("id-ID")}
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
                  <div className="space-y-1.5 font-sans text-xs text-slate-200 bg-[#10264A]/40 p-3 rounded-lg border border-slate-800">
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
                        className="rounded-lg border border-amber-800/60 bg-amber-950/30 p-2.5 text-xs text-amber-200"
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
                  <div className="rounded-lg border border-amber-600/40 bg-amber-950/20 p-2 text-xs text-amber-300">
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
                <div className="flex-1 min-h-[140px]">
                  <SqlEditor
                    value={
                      transpiledSql ||
                      (isId
                        ? "-- Klik 'Konversi' untuk melihat SQL target"
                        : "-- Click 'Convert' to see target dialect SQL")
                    }
                    onChange={() => {}}
                    readOnly={true}
                    language={language}
                    engine={
                      transpileTarget === "postgres"
                        ? "postgres"
                        : transpileTarget === "mysql"
                        ? "mysql"
                        : "sqlite"
                    }
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
                      ? "Klik 'Rencana' untuk melihat rencana optimasi query"
                      : "Click 'Plan' to inspect the execution plan"}
                  </div>
                ) : (
                  <div className="rounded-lg border border-slate-800 bg-[#10264A]/40 p-3 font-mono text-xs overflow-x-auto no-scrollbar touch-scroll">
                    <div className="font-bold text-[#F2B84B] mb-2">
                      {isId
                        ? "Rencana Eksekusi Query SQLite:"
                        : "SQLite Query Execution Plan:"}
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
              placeholder={
                isId
                  ? "Contoh: Analisis Saldo Nasabah Prioritas"
                  : "e.g. Priority Customers Balance Analysis"
              }
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white focus:outline-none focus:border-[#F2B84B] mb-4 min-h-[44px]"
            />
            <div className="flex justify-end gap-2 text-xs">
              <button
                onClick={() => setShowSavedModal(false)}
                className="px-4 py-2 rounded text-slate-400 hover:text-white min-h-[44px]"
              >
                {isId ? "Batal" : "Cancel"}
              </button>
              <button
                onClick={handleSaveQuery}
                disabled={!newTitle.trim()}
                className="px-5 py-2 rounded bg-[#F2B84B] font-bold text-[#071A3A] hover:opacity-90 disabled:opacity-50 min-h-[44px]"
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

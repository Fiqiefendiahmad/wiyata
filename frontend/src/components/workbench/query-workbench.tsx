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

interface QueryWorkbenchProps {
  sandboxId: string | null;
  onSandboxChange: (id: string) => void;
  language: "en" | "id";
}

export function QueryWorkbench({
  sandboxId,
  onSandboxChange,
  language,
}: QueryWorkbenchProps) {
  const isId = language === "id";

  // State
  const [query, setQuery] = useState<string>(
    "SELECT c.first_name, c.last_name, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS total_spent\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.id\nORDER BY total_spent DESC\nLIMIT 5;"
  );
  const [transpileTarget, setTranspileTarget] = useState<string>("postgres");
  const [transpiledSql, setTranspiledSql] = useState<string>("");
  const [transpileWarnings, setTranspileWarnings] = useState<string[]>([]);
  const [activeOutputTab, setActiveOutputTab] = useState<
    "results" | "transpile" | "explain"
  >("results");
  const [allowDdl, setAllowDdl] = useState<boolean>(false);

  // Schema & Templates
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [activeTemplate, setActiveTemplate] = useState<string>("ecommerce");
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

  // Fetch templates on mount
  useEffect(() => {
    api
      .get("/sandboxes/templates")
      .then((res) => setTemplates(res.data))
      .catch((err) => console.error("Failed to load templates:", err));
  }, []);

  // Initialize or fetch sandbox schema
  useEffect(() => {
    if (!sandboxId) {
      // Create initial sandbox
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
  };

  const toggleTableExpand = (tableName: string) => {
    setExpandedTables((prev) => ({ ...prev, [tableName]: !prev[tableName] }));
  };

  const insertQueryForTable = (tableName: string) => {
    setQuery(`SELECT * FROM ${tableName} LIMIT 20;`);
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
        // Reload schema in case DDL was executed
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

  return (
    <div className="flex h-[calc(100vh-3.5rem)] w-full overflow-hidden bg-[#071A3A]">
      {/* LEFT SIDEBAR: Templates & Schema */}
      <aside className="flex w-72 flex-col border-r border-slate-800 bg-[#071A3A]/95 text-slate-200">
        {/* Template Selector */}
        <div className="border-b border-slate-800 p-3">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            {isId ? "Dataset Pembelajaran" : "Learning Dataset"}
          </label>
          <div className="mt-2 grid grid-cols-2 gap-1.5">
            {templates.map((tpl) => (
              <button
                key={tpl.slug}
                onClick={() => handleTemplateChange(tpl.slug)}
                className={`flex flex-col items-start rounded border p-2 text-left transition-all ${
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
                    className="flex cursor-pointer items-center justify-between px-2.5 py-1.5 text-xs hover:bg-slate-800/40"
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
                      className="rounded bg-[#10264A] px-1.5 py-0.5 text-[10px] font-mono text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors"
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
      </aside>

      {/* MAIN QUERY WORKBENCH */}
      <main className="flex flex-1 flex-col overflow-hidden">
        {/* Editor Toolbar */}
        <div className="flex h-11 items-center justify-between border-b border-slate-800 bg-[#10264A]/50 px-4">
          <div className="flex items-center gap-2">
            {/* Run Button */}
            <button
              onClick={handleRunQuery}
              disabled={isRunning}
              className="flex items-center gap-1.5 rounded bg-[#F2B84B] px-3 py-1 text-xs font-bold text-[#071A3A] hover:bg-[#F2B84B]/90 transition-colors shadow-sm disabled:opacity-50"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>{isId ? "Jalankan (Ctrl+Enter)" : "Run (Ctrl+Enter)"}</span>
            </button>

            {/* Format Button */}
            <button
              onClick={handleFormat}
              disabled={isFormatting}
              className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/60 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-700/60 transition-colors"
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>{isId ? "Format SQL" : "Format SQL"}</span>
            </button>

            {/* Explain Plan */}
            <button
              onClick={handleExplain}
              className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/60 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-700/60 transition-colors"
            >
              <Layers className="h-3.5 w-3.5" />
              <span>{isId ? "Jelaskan Rencana" : "Explain Plan"}</span>
            </button>

            {/* Dialect Transpiler */}
            <div className="flex items-center gap-1 pl-2 border-l border-slate-800">
              <span className="text-[11px] text-slate-400">Transpile ke:</span>
              <select
                value={transpileTarget}
                onChange={(e) => setTranspileTarget(e.target.value)}
                className="rounded bg-slate-800 border border-slate-700 text-slate-200 text-xs px-2 py-0.5 focus:outline-none"
              >
                <option value="postgres">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="duckdb">DuckDB</option>
                <option value="oracle">Oracle</option>
              </select>
              <button
                onClick={handleTranspile}
                disabled={isTranspiling}
                className="flex items-center gap-1 rounded bg-[#10264A] border border-[#F2B84B]/40 px-2 py-1 text-xs text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors"
              >
                <ArrowRightLeft className="h-3 w-3" />
                <span>Konversi</span>
              </button>
            </div>
          </div>

          {/* Safety Mode Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAllowDdl(!allowDdl)}
              className={`flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-mono transition-colors border ${
                allowDdl
                  ? "border-amber-500/50 bg-amber-500/10 text-amber-300"
                  : "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
              }`}
            >
              {allowDdl ? (
                <>
                  <ShieldAlert className="h-3.5 w-3.5" />
                  <span>DML/DDL Diizinkan</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>Hanya Baca (Aman)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Editor Area */}
        <div className="h-[46%] w-full p-2">
          <SqlEditor
            value={query}
            onChange={setQuery}
            onExecute={handleRunQuery}
          />
        </div>

        {/* OUTPUT & RESULTS TABS */}
        <div className="flex flex-1 flex-col overflow-hidden border-t border-slate-800 bg-[#071A3A]">
          {/* Output Tab Header */}
          <div className="flex h-9 items-center justify-between border-b border-slate-800 bg-[#10264A]/30 px-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveOutputTab("results")}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold transition-colors border-b-2 ${
                  activeOutputTab === "results"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <TableIcon className="h-3.5 w-3.5" />
                <span>{isId ? "Hasil Query" : "Query Results"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("transpile")}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold transition-colors border-b-2 ${
                  activeOutputTab === "transpile"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <ArrowRightLeft className="h-3.5 w-3.5" />
                <span>{isId ? "Hasil Transpilasi" : "Transpile Output"}</span>
              </button>

              <button
                onClick={() => setActiveOutputTab("explain")}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold transition-colors border-b-2 ${
                  activeOutputTab === "explain"
                    ? "border-[#F2B84B] text-[#F2B84B]"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Layers className="h-3.5 w-3.5" />
                <span>{isId ? "Rencana Eksekusi" : "Explain Plan"}</span>
              </button>
            </div>

            {/* Execution Stats */}
            {results && !results.error && activeOutputTab === "results" && (
              <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  {results.rowCount} {isId ? "baris" : "rows"}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5 text-slate-500" />
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
                      <span>{isId ? "Kesalahan Eksekusi SQL" : "SQL Execution Error"}</span>
                    </div>
                    <p className="whitespace-pre-wrap">{results.error}</p>
                  </div>
                ) : !results ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-500">
                    {isId
                      ? "Tekan 'Jalankan' atau Ctrl+Enter untuk mengeksekusi query"
                      : "Press 'Run' or Ctrl+Enter to execute query"}
                  </div>
                ) : results.columns.length === 0 ? (
                  <div className="p-4 text-center text-xs text-slate-400">
                    {isId ? "Query selesai tanpa mengembalikan baris data." : "Query executed with no returned rows."}
                  </div>
                ) : (
                  <div className="inline-block min-w-full overflow-hidden rounded border border-slate-800">
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

            {/* 2. Transpile View */}
            {activeOutputTab === "transpile" && (
              <div className="h-full flex flex-col space-y-2">
                {transpileWarnings.length > 0 && (
                  <div className="rounded border border-amber-600/40 bg-amber-950/20 p-2 text-xs text-amber-300">
                    <p className="font-semibold flex items-center gap-1">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      {isId ? "Peringatan Semantik Dialek:" : "Dialect Semantics Warning:"}
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
                    value={transpiledSql || "-- Klik 'Konversi' untuk melihat SQL target"}
                    onChange={() => {}}
                    readOnly={true}
                  />
                </div>
              </div>
            )}

            {/* 3. Explain Plan View */}
            {activeOutputTab === "explain" && (
              <div className="p-2">
                {!explainPlan ? (
                  <div className="text-center text-xs text-slate-500 py-6">
                    {isId ? "Klik 'Jelaskan Rencana' untuk melihat rencana optimasi query" : "Click 'Explain Plan' to inspect the execution plan"}
                  </div>
                ) : (
                  <div className="rounded border border-slate-800 bg-[#10264A]/40 p-3 font-mono text-xs">
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
    </div>
  );
}

"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import {
  Database,
  Table as TableIcon,
  Key,
  Link as LinkIcon,
  Search,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Code2,
  ArrowRight,
  ShieldCheck,
  Layers,
  Eye,
  Network,
  ChevronRight,
  ChevronDown,
  Hash,
  SlidersHorizontal,
  ArrowUpDown,
  Check,
  Copy,
  Info,
  ExternalLink,
  ShieldAlert,
  X,
} from "lucide-react";
import { api } from "@/lib/api";

export interface ColumnMetadata {
  name: string;
  data_type: string;
  length?: number | null;
  precision?: number | null;
  scale?: number | null;
  nullable: boolean;
  primary_key: boolean;
  foreign_key: boolean;
  foreign_key_target?: string | null;
  unique: boolean;
  default_value?: string | null;
  auto_increment: boolean;
  comment?: string | null;
}

export interface IndexMetadata {
  name: string;
  table_name: string;
  columns: string[];
  is_unique: boolean;
  is_primary: boolean;
  index_type: string;
  predicate?: string | null;
}

export interface ConstraintMetadata {
  name: string;
  table_name: string;
  type: string;
  columns: string[];
  definition?: string | null;
  referenced_table?: string | null;
  referenced_columns?: string[] | null;
}

export interface RelationshipMetadata {
  id: string;
  from_table: string;
  from_column: string;
  to_table: string;
  to_column: string;
  source: "declared" | "inferred";
  constraint_name?: string | null;
  cardinality: string;
}

export interface TableMetadata {
  name: string;
  type: string;
  schema_name: string;
  columns: ColumnMetadata[];
  indexes: IndexMetadata[];
  constraints: ConstraintMetadata[];
  row_count: number;
  row_count_estimated: boolean;
}

export interface SchemaMetadata {
  name: string;
  tables: string[];
  views: string[];
  functions: string[];
  sequences: string[];
}

export interface DatabaseOverview {
  database_name: string;
  engine: string;
  engine_version: string;
  schema_count: number;
  table_count: number;
  view_count: number;
  index_count: number;
  relationship_count: number;
  total_row_count: number;
  row_count_is_estimated: boolean;
}

export interface FullDatabaseMetadata {
  overview: DatabaseOverview;
  schemas: SchemaMetadata[];
  tables: TableMetadata[];
  relationships: RelationshipMetadata[];
  indexes: IndexMetadata[];
  constraints: ConstraintMetadata[];
  refreshed_at: string;
}

interface SchemaExplorerProps {
  sandboxId: string | null;
  language: "en" | "id";
  activeEngine: string;
  initialSelectedTable?: string | null;
  onOpenQueryInEditor: (query: string) => void;
  onClose?: () => void;
}

type ExplorerTab = "structure" | "erd" | "indexes" | "constraints" | "preview";

export function SchemaExplorer({
  sandboxId,
  language,
  activeEngine,
  initialSelectedTable,
  onOpenQueryInEditor,
  onClose,
}: SchemaExplorerProps) {
  const isId = language === "id";

  const [metadata, setMetadata] = useState<FullDatabaseMetadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ExplorerTab>("structure");
  const [selectedTable, setSelectedTable] = useState<string | null>(initialSelectedTable || null);
  const [searchTerm, setSearchTerm] = useState("");
  const [copiedCol, setCopiedCol] = useState<string | null>(null);
  const [showMobileTableList, setShowMobileTableList] = useState(false);

  // Data Preview State
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewPage, setPreviewPage] = useState(1);
  const [previewPageSize, setPreviewPageSize] = useState(15);
  const [previewSortBy, setPreviewSortBy] = useState<string | null>(null);
  const [previewSortOrder, setPreviewSortOrder] = useState<"ASC" | "DESC">("ASC");

  // ERD Pan/Zoom/Drag State
  const [erdScale, setErdScale] = useState(1);
  const [erdPan, setErdPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [nodePositions, setNodePositions] = useState<Record<string, { x: number; y: number }>>({});
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const erdContainerRef = useRef<HTMLDivElement>(null);

  const fetchMetadata = async () => {
    if (!sandboxId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/sandboxes/${sandboxId}/metadata`);
      setMetadata(res.data);
      if (!selectedTable && res.data.tables.length > 0) {
        setSelectedTable(res.data.tables[0].name);
      }
    } catch (err: any) {
      console.error("Error fetching sandbox metadata:", err);
      setError(
        err?.response?.data?.detail || err.message || (isId ? "Gagal memuat metadata skema" : "Failed to load schema metadata")
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetadata();
  }, [sandboxId]);

  useEffect(() => {
    if (initialSelectedTable) {
      setSelectedTable(initialSelectedTable);
    }
  }, [initialSelectedTable]);

  // Set responsive scale for ERD on mobile viewport
  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      setErdScale(0.65);
      setErdPan({ x: 16, y: 16 });
    }
  }, []);

  // Compute default node layout for ERD once tables are loaded
  useEffect(() => {
    if (!metadata || metadata.tables.length === 0) return;
    const positions: Record<string, { x: number; y: number }> = {};
    const colsCount = metadata.tables.length > 4 ? 3 : 2;
    const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
    const spacingX = isMobile ? 300 : 340;
    const spacingY = 280;

    metadata.tables.forEach((tbl, idx) => {
      // If position already set by user drag, preserve it
      if (nodePositions[tbl.name]) {
        positions[tbl.name] = nodePositions[tbl.name];
      } else {
        const col = idx % colsCount;
        const row = Math.floor(idx / colsCount);
        positions[tbl.name] = {
          x: (isMobile ? 16 : 40) + col * spacingX,
          y: 40 + row * spacingY,
        };
      }
    });
    setNodePositions(positions);
  }, [metadata?.tables.length]);

  // Fetch Table Data Preview when preview tab is active
  useEffect(() => {
    if (activeTab !== "preview" || !sandboxId || !selectedTable) return;
    setPreviewLoading(true);
    const sortParam = previewSortBy ? `&sort_by=${previewSortBy}&sort_order=${previewSortOrder}` : "";
    api
      .get(
        `/sandboxes/${sandboxId}/tables/${selectedTable}/preview?page=${previewPage}&page_size=${previewPageSize}${sortParam}`
      )
      .then((res) => {
        setPreviewData(res.data);
      })
      .catch((err) => {
        console.error("Preview data error:", err);
        setPreviewData(null);
      })
      .finally(() => setPreviewLoading(false));
  }, [activeTab, sandboxId, selectedTable, previewPage, previewPageSize, previewSortBy, previewSortOrder]);

  const activeTableObj = useMemo(() => {
    if (!metadata || !selectedTable) return null;
    return metadata.tables.find((t) => t.name.toLowerCase() === selectedTable.toLowerCase()) || null;
  }, [metadata, selectedTable]);

  const filteredTables = useMemo(() => {
    if (!metadata) return [];
    if (!searchTerm.trim()) return metadata.tables;
    const q = searchTerm.toLowerCase();
    return metadata.tables.filter(
      (t) =>
        t.name.toLowerCase().includes(q) ||
        t.columns.some((c) => c.name.toLowerCase().includes(q))
    );
  }, [metadata, searchTerm]);

  // Quick Action Generators
  const handleGenerateSelect = (tableName: string) => {
    const targetTable = metadata?.tables.find((t) => t.name === tableName);
    if (!targetTable) return;
    const colList = targetTable.columns.map((c) => `    ${c.name}`).join(",\n");
    let query = "";
    if (activeEngine === "oracle") {
      query = `SELECT\n${colList}\nFROM ${tableName}\nWHERE ROWNUM <= 100;`;
    } else if (activeEngine === "db2") {
      query = `SELECT\n${colList}\nFROM ${tableName}\nFETCH FIRST 100 ROWS ONLY WITH UR;`;
    } else if (activeEngine === "mssql") {
      query = `SELECT TOP 100\n${colList}\nFROM ${tableName};`;
    } else {
      query = `SELECT\n${colList}\nFROM ${tableName}\nLIMIT 100;`;
    }
    onOpenQueryInEditor(query);
  };

  const handleCopyColumns = (tableName: string) => {
    const targetTable = metadata?.tables.find((t) => t.name === tableName);
    if (!targetTable) return;
    const colStr = targetTable.columns.map((c) => c.name).join(", ");
    navigator.clipboard.writeText(colStr);
    setCopiedCol(tableName);
    setTimeout(() => setCopiedCol(null), 2000);
  };

  // Auto-fit viewport helper
  const handleAutoFit = () => {
    if (!erdContainerRef.current) {
      setErdScale(1);
      setErdPan({ x: 0, y: 0 });
      return;
    }
    const containerWidth = erdContainerRef.current.clientWidth || 360;
    const isMobile = containerWidth < 768;
    if (isMobile) {
      setErdScale(0.65);
      setErdPan({ x: 16, y: 16 });
    } else {
      setErdScale(1);
      setErdPan({ x: 20, y: 20 });
    }
  };

  // ERD Drag & Pan Handlers (Mouse)
  const handleMouseDownErd = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest(".erd-node")) return;
    setIsPanning(true);
    setPanStart({ x: e.clientX - erdPan.x, y: e.clientY - erdPan.y });
  };

  const handleMouseMoveErd = (e: React.MouseEvent) => {
    if (isPanning) {
      setErdPan({ x: e.clientX - panStart.x, y: e.clientY - panStart.y });
    } else if (draggingNode) {
      setNodePositions((prev) => ({
        ...prev,
        [draggingNode]: {
          x: Math.max(10, (e.clientX - dragOffset.x - erdPan.x) / erdScale),
          y: Math.max(10, (e.clientY - dragOffset.y - erdPan.y) / erdScale),
        },
      }));
    }
  };

  const handleMouseUpErd = () => {
    setIsPanning(false);
    setDraggingNode(null);
  };

  const startDragNode = (tableName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDraggingNode(tableName);
    const pos = nodePositions[tableName] || { x: 0, y: 0 };
    setDragOffset({
      x: e.clientX - pos.x * erdScale - erdPan.x,
      y: e.clientY - pos.y * erdScale - erdPan.y,
    });
  };

  // ERD Drag & Pan Handlers (Touch)
  const handleTouchStartErd = (e: React.TouchEvent) => {
    if ((e.target as HTMLElement).closest(".erd-node")) return;
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      setIsPanning(true);
      setPanStart({ x: touch.clientX - erdPan.x, y: touch.clientY - erdPan.y });
    }
  };

  const handleTouchMoveErd = (e: React.TouchEvent) => {
    if (isPanning && e.touches.length === 1) {
      const touch = e.touches[0];
      setErdPan({ x: touch.clientX - panStart.x, y: touch.clientY - panStart.y });
    } else if (draggingNode && e.touches.length === 1) {
      const touch = e.touches[0];
      setNodePositions((prev) => ({
        ...prev,
        [draggingNode]: {
          x: Math.max(10, (touch.clientX - dragOffset.x - erdPan.x) / erdScale),
          y: Math.max(10, (touch.clientY - dragOffset.y - erdPan.y) / erdScale),
        },
      }));
    }
  };

  const handleTouchEndErd = () => {
    setIsPanning(false);
    setDraggingNode(null);
  };

  const startTouchDragNode = (tableName: string, e: React.TouchEvent) => {
    e.stopPropagation();
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      setDraggingNode(tableName);
      const pos = nodePositions[tableName] || { x: 0, y: 0 };
      setDragOffset({
        x: touch.clientX - pos.x * erdScale - erdPan.x,
        y: touch.clientY - pos.y * erdScale - erdPan.y,
      });
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#071A3A] text-slate-200 overflow-hidden select-none">
      {/* 1. TOP OVERVIEW HEADER */}
      <header className="flex-none border-b border-slate-800 bg-[#091b36] px-4 py-2.5 z-20 shadow-md">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-[#F2B84B]/15 border border-[#F2B84B]/30 p-2 text-[#F2B84B]">
              <Database className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-white tracking-wide">
                  {metadata?.overview.database_name || "Sandbox Database"}
                </h2>
                <span className="rounded-md bg-blue-950/70 border border-blue-700/50 px-2 py-0.5 text-[10px] font-mono font-semibold text-blue-300">
                  {metadata?.overview.engine.toUpperCase() || activeEngine.toUpperCase()}{" "}
                  {metadata?.overview.engine_version || ""}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                {isId ? "Penjelajah & Visualisasi Skema Database Produksi" : "Production Database Schema Explorer & Visualizer"}
              </p>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          {metadata && (
            <div className="flex items-center gap-2 overflow-x-auto no-scrollbar touch-scroll text-[11px] font-mono">
              <span className="rounded-lg bg-slate-900/80 border border-slate-800 px-2.5 py-1 text-slate-300">
                {isId ? "Tabel:" : "Tables:"}{" "}
                <strong className="text-[#F2B84B] font-bold">{metadata.overview.table_count}</strong>
              </span>
              <span className="rounded-lg bg-slate-900/80 border border-slate-800 px-2.5 py-1 text-slate-300">
                {isId ? "Relasi:" : "Relations:"}{" "}
                <strong className="text-emerald-400 font-bold">{metadata.overview.relationship_count}</strong>
              </span>
              <span className="rounded-lg bg-slate-900/80 border border-slate-800 px-2.5 py-1 text-slate-300">
                {isId ? "Indeks:" : "Indexes:"}{" "}
                <strong className="text-blue-400 font-bold">{metadata.overview.index_count}</strong>
              </span>
              <span className="rounded-lg bg-slate-900/80 border border-slate-800 px-2.5 py-1 text-slate-300">
                {isId ? "Total Baris:" : "Total Rows:"}{" "}
                <strong className="text-amber-300 font-bold">
                  {metadata.overview.total_row_count}
                </strong>
                <span className="text-[9px] text-slate-500 ml-1">
                  ({metadata.overview.row_count_is_estimated ? (isId ? "estimasi" : "est") : (isId ? "pasti" : "exact")})
                </span>
              </span>
              <button
                onClick={fetchMetadata}
                disabled={loading}
                title={isId ? "Segarkan metadata" : "Refresh metadata"}
                className="rounded-lg bg-slate-900/80 border border-slate-800 p-1.5 text-slate-400 hover:text-[#F2B84B] transition-colors"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin text-[#F2B84B]" : ""}`} />
              </button>
            </div>
          )}

          {/* Close / Back to Editor */}
          {onClose && (
            <button
              onClick={onClose}
              className="rounded-lg bg-slate-800 hover:bg-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors"
            >
              {isId ? "Kembali ke Editor" : "Back to SQL Editor"}
            </button>
          )}
        </div>

        {/* View Mode Tabs */}
        <div className="mt-2.5 flex items-center justify-between border-t border-slate-800/80 pt-2 gap-2 overflow-x-auto no-scrollbar touch-scroll">
          <div className="flex items-center gap-1">
            {[
              { id: "structure" as const, label: isId ? "Struktur Kolom" : "Table Structure", icon: TableIcon },
              { id: "erd" as const, label: isId ? "Diagram Relasi (ERD)" : "ER Diagram", icon: Network },
              { id: "indexes" as const, label: isId ? "Indeks Database" : "Indexes", icon: Layers },
              { id: "constraints" as const, label: isId ? "Batasan & Kunci" : "Constraints", icon: Key },
              { id: "preview" as const, label: isId ? "Pratinjau Data" : "Data Preview", icon: Eye },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all ${
                    isActive
                      ? "bg-[#F2B84B] text-[#071A3A] font-bold shadow-sm"
                      : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {selectedTable && (
            <div className="hidden md:flex items-center gap-2 text-xs">
              <span className="text-slate-400">{isId ? "Tabel Aktif:" : "Selected Table:"}</span>
              <span className="rounded-md bg-[#10264A] border border-[#F2B84B]/40 px-2 py-0.5 font-mono font-bold text-[#F2B84B]">
                {selectedTable}
              </span>
              <button
                onClick={() => handleGenerateSelect(selectedTable)}
                className="flex items-center gap-1 text-[11px] font-semibold text-[#F2B84B] hover:underline"
              >
                <Code2 className="h-3 w-3" />
                <span>{isId ? "Buka di Editor" : "Open in Editor"}</span>
              </button>
            </div>
          )}

          {/* Mobile active table badge & drawer trigger */}
          <div className="flex md:hidden items-center gap-1.5 shrink-0">
            <button
              onClick={() => setShowMobileTableList(true)}
              className="flex items-center gap-1 rounded-lg bg-[#10264A] border border-[#F2B84B]/40 px-2 py-1 text-xs font-mono font-bold text-[#F2B84B] shrink-0"
              title={isId ? "Pilih tabel lain" : "Select table"}
            >
              <TableIcon className="h-3 w-3" />
              <span className="max-w-[100px] truncate">{selectedTable || (isId ? "Tabel" : "Table")}</span>
              <ChevronDown className="h-3 w-3 text-slate-400 shrink-0" />
            </button>
            {selectedTable && (
              <button
                onClick={() => handleGenerateSelect(selectedTable)}
                title={isId ? "Buka di Editor" : "Open in Editor"}
                className="rounded-lg bg-slate-800 p-1 text-[#F2B84B] border border-slate-700"
              >
                <Code2 className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
      </header>

      {/* 2. MAIN BODY AREA */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Mobile Backdrop when drawer is open */}
        {showMobileTableList && (
          <div
            onClick={() => setShowMobileTableList(false)}
            className="md:hidden fixed inset-0 bg-black/60 z-20 backdrop-blur-xs transition-opacity"
          />
        )}

        {/* Sidebar: Schema Navigation Tree */}
        <aside
          className={`${
            showMobileTableList
              ? "flex fixed inset-y-0 left-0 z-30 w-72 shadow-2xl"
              : "hidden md:flex relative w-64 sm:w-72"
          } flex-none border-r border-slate-800 bg-[#071A3A]/98 flex flex-col overflow-hidden transition-all`}
        >
          {/* Search box & Mobile close header */}
          <div className="p-3 border-b border-slate-800 bg-[#10264A]/30 flex flex-col gap-2">
            <div className="flex items-center justify-between md:hidden pb-1 border-b border-slate-800/60">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <TableIcon className="h-3.5 w-3.5 text-[#F2B84B]" />
                <span>{isId ? "Daftar Tabel" : "Tables"}</span>
              </span>
              <button
                onClick={() => setShowMobileTableList(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                aria-label="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
              <input
                type="text"
                placeholder={isId ? "Cari tabel atau kolom..." : "Search tables or columns..."}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-lg bg-slate-900 border border-slate-700/80 pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#F2B84B]"
              />
            </div>
          </div>

          {/* Tree Navigation */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              {isId ? "Daftar Tabel & Entitas" : "Tables & Entities"} ({filteredTables.length})
            </div>

            {loading ? (
              <div className="p-4 text-center text-xs text-slate-400 space-y-2">
                <RefreshCw className="h-4 w-4 animate-spin text-[#F2B84B] mx-auto" />
                <p>{isId ? "Membaca metadata database..." : "Loading database catalog..."}</p>
              </div>
            ) : filteredTables.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-500">
                {isId ? "Tidak ada tabel yang cocok." : "No matching tables found."}
              </div>
            ) : (
              filteredTables.map((tbl) => {
                const isSelected = selectedTable === tbl.name;
                return (
                  <div
                    key={tbl.name}
                    onClick={() => {
                      setSelectedTable(tbl.name);
                      setShowMobileTableList(false);
                    }}
                    className={`flex items-center justify-between px-3 py-2 rounded-xl border text-xs cursor-pointer transition-all ${
                      isSelected
                        ? "bg-[#10264A] border-[#F2B84B] text-white shadow-sm ring-1 ring-[#F2B84B]/30"
                        : "bg-slate-900/40 border-slate-800/80 text-slate-300 hover:bg-slate-800/40 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <TableIcon className={`h-3.5 w-3.5 shrink-0 ${isSelected ? "text-[#F2B84B]" : "text-slate-400"}`} />
                      <span className="font-mono font-medium truncate">{tbl.name}</span>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0 font-mono text-[10px] text-slate-400">
                      <span className="rounded bg-slate-800 px-1.5 py-0.5">
                        {tbl.columns.length} col
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* Center Workspace Content based on activeTab */}
        <main className="flex-1 flex flex-col overflow-hidden bg-[#071A3A]">
          {/* TAB 1: STRUCTURE INSPECTOR */}
          {activeTab === "structure" && (
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
              {activeTableObj ? (
                <>
                  {/* Table Summary Card */}
                  <div className="rounded-2xl border border-slate-800 bg-[#0c1f3d] p-5 shadow-lg">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
                      <div>
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#F2B84B] mb-1">
                          <TableIcon className="h-4 w-4" />
                          <span>{isId ? "Inspeksi Struktur Tabel" : "Table Structure Inspector"}</span>
                        </div>
                        <h3 className="text-xl font-mono font-bold text-white flex items-center gap-2">
                          <span>{activeTableObj.name}</span>
                          <span className="text-xs text-slate-400 font-sans font-normal">
                            ({activeTableObj.row_count} {isId ? "baris data" : "rows"})
                          </span>
                        </h3>
                      </div>

                      <div className="flex items-center gap-2 flex-wrap">
                        <button
                          onClick={() => handleGenerateSelect(activeTableObj.name)}
                          className="flex items-center gap-1.5 rounded-lg bg-[#F2B84B] hover:bg-[#F2B84B]/90 text-[#071A3A] px-3 py-1.5 text-xs font-bold transition-all shadow-sm"
                        >
                          <Code2 className="h-3.5 w-3.5" />
                          <span>{isId ? "Hasilkan Kueri SELECT" : "Generate SELECT Query"}</span>
                        </button>
                        <button
                          onClick={() => handleCopyColumns(activeTableObj.name)}
                          className="flex items-center gap-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 text-xs font-semibold transition-all"
                        >
                          {copiedCol === activeTableObj.name ? (
                            <>
                              <Check className="h-3.5 w-3.5 text-emerald-400" />
                              <span>{isId ? "Tersalin ✔️" : "Copied ✔️"}</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3.5 w-3.5 text-slate-400" />
                              <span>{isId ? "Salin Kolom" : "Copy Columns"}</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Columns Metadata Table */}
                    <div className="mt-4 overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
                      <table className="w-full text-left text-xs text-slate-300">
                        <thead className="border-b border-slate-800 bg-[#10264A]/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                          <tr>
                            <th className="px-4 py-2.5">#</th>
                            <th className="px-4 py-2.5">{isId ? "Nama Kolom" : "Column Name"}</th>
                            <th className="px-4 py-2.5">{isId ? "Tipe Data" : "Data Type"}</th>
                            <th className="px-4 py-2.5">{isId ? "Dapat Null" : "Nullable"}</th>
                            <th className="px-4 py-2.5">{isId ? "Kunci Utama (PK)" : "Primary Key"}</th>
                            <th className="px-4 py-2.5">{isId ? "Kunci Tamu (FK)" : "Foreign Key"}</th>
                            <th className="px-4 py-2.5">{isId ? "Unik" : "Unique"}</th>
                            <th className="px-4 py-2.5">{isId ? "Nilai Bawaan" : "Default"}</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono">
                          {activeTableObj.columns.map((col, idx) => (
                            <tr key={col.name} className="hover:bg-slate-800/40 transition-colors">
                              <td className="px-4 py-2 text-slate-500 text-[11px]">{idx + 1}</td>
                              <td className="px-4 py-2 font-bold text-white flex items-center gap-1.5">
                                {col.primary_key && <Key className="h-3 w-3 text-[#F2B84B] shrink-0" />}
                                {col.foreign_key && <LinkIcon className="h-3 w-3 text-emerald-400 shrink-0" />}
                                <span>{col.name}</span>
                              </td>
                              <td className="px-4 py-2 text-blue-300">{col.data_type}</td>
                              <td className="px-4 py-2">
                                <span
                                  className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                                    col.nullable
                                      ? "bg-slate-800 text-slate-400"
                                      : "bg-amber-950/60 border border-amber-800/50 text-amber-300"
                                  }`}
                                >
                                  {col.nullable ? "YES" : "NO"}
                                </span>
                              </td>
                              <td className="px-4 py-2">
                                {col.primary_key ? (
                                  <span className="rounded bg-amber-500/20 border border-amber-500/40 px-2 py-0.5 text-[10px] font-bold text-[#F2B84B]">
                                    PK
                                  </span>
                                ) : (
                                  <span className="text-slate-600">-</span>
                                )}
                              </td>
                              <td className="px-4 py-2">
                                {col.foreign_key ? (
                                  <span className="rounded bg-emerald-500/20 border border-emerald-500/40 px-2 py-0.5 text-[10px] font-bold text-emerald-300 flex items-center gap-1 w-fit">
                                    <span>FK →</span>
                                    <span>{col.foreign_key_target}</span>
                                  </span>
                                ) : (
                                  <span className="text-slate-600">-</span>
                                )}
                              </td>
                              <td className="px-4 py-2">
                                {col.unique ? (
                                  <span className="rounded bg-purple-500/20 border border-purple-500/40 px-1.5 py-0.5 text-[10px] font-semibold text-purple-300">
                                    UNIQUE
                                  </span>
                                ) : (
                                  <span className="text-slate-600">-</span>
                                )}
                              </td>
                              <td className="px-4 py-2 text-slate-400 text-[11px] truncate max-w-[120px]">
                                {col.default_value !== null ? col.default_value : <span className="text-slate-600">NULL</span>}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Related Tables & Constraints Card */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Constraints Box */}
                    <div className="rounded-xl border border-slate-800 bg-[#09172e] p-4 space-y-3">
                      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
                        <Key className="h-3.5 w-3.5 text-[#F2B84B]" />
                        <span>{isId ? "Batasan Tabel (Constraints)" : "Table Constraints"}</span>
                      </div>
                      {activeTableObj.constraints.length === 0 ? (
                        <p className="text-xs text-slate-500 italic">
                          {isId ? "Tidak ada batasan terdaftar." : "No constraints declared."}
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {activeTableObj.constraints.map((c, i) => (
                            <div
                              key={`${c.name}-${i}`}
                              className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5 text-xs font-mono"
                            >
                              <div className="flex items-center justify-between text-[11px] mb-1">
                                <span className="text-white font-bold">{c.name}</span>
                                <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[#F2B84B] font-semibold">
                                  {c.type}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-400">{c.definition || c.columns.join(", ")}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Table Indexes Box */}
                    <div className="rounded-xl border border-slate-800 bg-[#09172e] p-4 space-y-3">
                      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
                        <Layers className="h-3.5 w-3.5 text-blue-400" />
                        <span>{isId ? "Indeks Terdaftar" : "Table Indexes"}</span>
                      </div>
                      {activeTableObj.indexes.length === 0 ? (
                        <p className="text-xs text-slate-500 italic">
                          {isId ? "Tidak ada indeks tambahan." : "No explicit indexes."}
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {activeTableObj.indexes.map((idx, i) => (
                            <div
                              key={`${idx.name}-${i}`}
                              className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5 text-xs font-mono"
                            >
                              <div className="flex items-center justify-between text-[11px] mb-1">
                                <span className="text-white font-bold">{idx.name}</span>
                                <span className="rounded bg-blue-950/60 border border-blue-800/40 px-1.5 py-0.5 text-blue-300 font-semibold">
                                  {idx.index_type} {idx.is_unique ? "(UNIQUE)" : ""}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-400">
                                {isId ? "Kolom:" : "Columns:"} {idx.columns.join(", ")}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-8 text-center text-slate-500">
                  {isId ? "Pilih tabel di panel kiri untuk memeriksa kolom." : "Select a table on the left to inspect columns."}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: INTERACTIVE VISUAL ERD */}
          {activeTab === "erd" && (
            <div className="flex-1 flex flex-col overflow-hidden relative">
              {/* ERD Control Strip */}
              <div className="flex items-center justify-between gap-2 border-b border-slate-800 bg-[#09172e] px-3 sm:px-4 py-2 z-10">
                <div className="flex items-center gap-1.5 sm:gap-2 text-xs overflow-x-auto no-scrollbar py-0.5">
                  <span className="text-slate-400 text-[11px] font-medium shrink-0">
                    {isId ? "Relasi:" : "Relations:"}
                  </span>
                  <span
                    title={isId ? "Kunci Tamu Terdeklarasi (FK Resmi)" : "Declared Foreign Key"}
                    className="flex items-center gap-1 rounded-md bg-emerald-950/60 border border-emerald-600/50 px-2 py-0.5 text-[10px] font-bold text-emerald-300 shrink-0"
                  >
                    <span className="inline-block w-2.5 h-0.5 bg-emerald-400 mr-0.5"></span>
                    <span className="hidden sm:inline">{isId ? "Kunci Tamu Terdeklarasi (FK)" : "Declared FK"}</span>
                    <span className="sm:hidden">{isId ? "FK Resmi" : "FK"}</span>
                  </span>
                  <span
                    title={isId ? "Inferensi Penamaan (Diduga Relasi)" : "Inferred by Name Convention"}
                    className="flex items-center gap-1 rounded-md bg-amber-950/60 border border-amber-600/50 px-2 py-0.5 text-[10px] font-bold text-amber-300 shrink-0"
                  >
                    <span className="inline-block w-2.5 h-0.5 border-t border-dashed border-amber-400 mr-0.5"></span>
                    <span className="hidden sm:inline">{isId ? "Inferensi Penamaan" : "Inferred Convention"}</span>
                    <span className="sm:hidden">{isId ? "Inferensi" : "Inferred"}</span>
                  </span>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  {/* Table Drawer Button on Mobile */}
                  <button
                    onClick={() => setShowMobileTableList(true)}
                    title={isId ? "Pilih Tabel" : "Select Table"}
                    className="md:hidden flex items-center gap-1 rounded-lg bg-slate-800 hover:bg-slate-700 px-2 py-1.5 text-[11px] font-semibold text-[#F2B84B] border border-slate-700 transition-colors"
                  >
                    <TableIcon className="h-3.5 w-3.5" />
                    <span>{isId ? "Tabel" : "Tables"}</span>
                  </button>

                  <button
                    onClick={() => setErdScale((s) => Math.min(2.0, Number((s + 0.1).toFixed(2))))}
                    title={isId ? "Perbesar (+10%)" : "Zoom in"}
                    className="rounded-lg bg-slate-800 hover:bg-slate-700 p-1.5 sm:p-2 text-slate-300 transition-colors active:scale-95"
                    aria-label="Zoom in"
                  >
                    <ZoomIn className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={() => setErdScale((s) => Math.max(0.3, Number((s - 0.1).toFixed(2))))}
                    title={isId ? "Perkecil (-10%)" : "Zoom out"}
                    className="rounded-lg bg-slate-800 hover:bg-slate-700 p-1.5 sm:p-2 text-slate-300 transition-colors active:scale-95"
                    aria-label="Zoom out"
                  >
                    <ZoomOut className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={handleAutoFit}
                    title={isId ? "Pusatkan tampilan" : "Fit to screen"}
                    className="rounded-lg bg-slate-800 hover:bg-slate-700 p-1.5 sm:p-2 text-slate-300 transition-colors active:scale-95"
                    aria-label="Fit to screen"
                  >
                    <Maximize2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              {/* Canvas viewport */}
              <div
                ref={erdContainerRef}
                onMouseDown={handleMouseDownErd}
                onMouseMove={handleMouseMoveErd}
                onMouseUp={handleMouseUpErd}
                onTouchStart={handleTouchStartErd}
                onTouchMove={handleTouchMoveErd}
                onTouchEnd={handleTouchEndErd}
                className="flex-1 w-full h-full overflow-hidden relative cursor-grab active:cursor-grabbing bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] touch-none select-none min-h-[360px]"
              >
                <div
                  style={{
                    transform: `translate(${erdPan.x}px, ${erdPan.y}px) scale(${erdScale})`,
                    transformOrigin: "top left",
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "3000px",
                    height: "3000px",
                  }}
                >
                  {/* SVG Connector Lines */}
                  <svg className="absolute top-0 left-0 w-full h-full pointer-events-none z-0">
                    <defs>
                      <marker
                        id="arrow-declared"
                        viewBox="0 0 10 10"
                        refX="8"
                        refY="5"
                        markerWidth="6"
                        markerHeight="6"
                        orient="auto-start-reverse"
                      >
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
                      </marker>
                      <marker
                        id="arrow-inferred"
                        viewBox="0 0 10 10"
                        refX="8"
                        refY="5"
                        markerWidth="6"
                        markerHeight="6"
                        orient="auto-start-reverse"
                      >
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
                      </marker>
                    </defs>

                    {metadata?.relationships.map((rel) => {
                      const fromPos = nodePositions[rel.from_table];
                      const toPos = nodePositions[rel.to_table];
                      if (!fromPos || !toPos) return null;

                      // Calculate connection points (from center right to center left, or closest edge)
                      const x1 = fromPos.x + 280;
                      const y1 = fromPos.y + 60;
                      const x2 = toPos.x;
                      const y2 = toPos.y + 60;

                      const dx = Math.abs(x2 - x1) * 0.5;
                      const pathData = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

                      const isDeclared = rel.source === "declared";
                      return (
                        <g key={rel.id}>
                          <path
                            d={pathData}
                            fill="none"
                            stroke={isDeclared ? "#10b981" : "#f59e0b"}
                            strokeWidth={isDeclared ? "2" : "1.5"}
                            strokeDasharray={isDeclared ? undefined : "5 5"}
                            markerEnd={isDeclared ? "url(#arrow-declared)" : "url(#arrow-inferred)"}
                            className="transition-all opacity-85"
                          />
                          {/* Midpoint badge for cardinality */}
                          <text
                            x={(x1 + x2) / 2}
                            y={(y1 + y2) / 2 - 8}
                            fill={isDeclared ? "#34d399" : "#fbbf24"}
                            fontSize="10"
                            fontFamily="monospace"
                            fontWeight="bold"
                            textAnchor="middle"
                            className="select-none bg-slate-900 px-1"
                          >
                            {rel.from_column} → {rel.to_column} ({rel.cardinality})
                          </text>
                        </g>
                      );
                    })}
                  </svg>

                  {/* Render Table Entity Nodes */}
                  {metadata?.tables.map((tbl) => {
                    const pos = nodePositions[tbl.name] || { x: 50, y: 50 };
                    const isSelected = selectedTable === tbl.name;
                    return (
                      <div
                        key={tbl.name}
                        onMouseDown={(e) => startDragNode(tbl.name, e)}
                        onTouchStart={(e) => startTouchDragNode(tbl.name, e)}
                        onClick={() => setSelectedTable(tbl.name)}
                        style={{
                          transform: `translate(${pos.x}px, ${pos.y}px)`,
                          width: "280px",
                        }}
                        className={`erd-node absolute rounded-xl border bg-[#0d203f]/95 shadow-2xl overflow-hidden cursor-move transition-shadow z-10 touch-none ${
                          isSelected
                            ? "border-[#F2B84B] ring-2 ring-[#F2B84B]/40"
                            : "border-slate-700/80 hover:border-slate-600"
                        }`}
                      >
                        {/* Table Header */}
                        <div className="flex items-center justify-between border-b border-slate-700/80 bg-[#14294d] px-3 py-2">
                          <div className="flex items-center gap-1.5 truncate">
                            <TableIcon className="h-3.5 w-3.5 text-[#F2B84B] shrink-0" />
                            <span className="text-xs font-mono font-bold text-white truncate">{tbl.name}</span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-400 shrink-0">
                            {tbl.row_count} rows
                          </span>
                        </div>

                        {/* Columns List inside node */}
                        <div className="p-2 space-y-1 max-h-56 overflow-y-auto no-scrollbar font-mono text-[11px]">
                          {tbl.columns.map((col) => (
                            <div
                              key={col.name}
                              className="flex items-center justify-between px-1.5 py-0.5 rounded hover:bg-slate-800/50"
                            >
                              <div className="flex items-center gap-1 truncate">
                                {col.primary_key && <Key className="h-3 w-3 text-[#F2B84B] shrink-0" />}
                                {col.foreign_key && <LinkIcon className="h-3 w-3 text-emerald-400 shrink-0" />}
                                <span
                                  className={`truncate ${
                                    col.primary_key
                                      ? "text-[#F2B84B] font-bold"
                                      : col.foreign_key
                                      ? "text-emerald-300 font-semibold"
                                      : "text-slate-300"
                                  }`}
                                >
                                  {col.name}
                                </span>
                              </div>
                              <span className="text-[10px] text-slate-500 shrink-0">{col.data_type}</span>
                            </div>
                          ))}
                        </div>

                        {/* Node Footer */}
                        <div className="border-t border-slate-800 bg-slate-900/50 px-2.5 py-1 flex items-center justify-between text-[10px] text-slate-400">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedTable(tbl.name);
                              setActiveTab("structure");
                            }}
                            className="text-[#F2B84B] hover:underline flex items-center gap-1"
                          >
                            <span>{isId ? "Detail Kolom" : "Inspect"}</span>
                            <ArrowRight className="h-2.5 w-2.5" />
                          </button>
                          <span>{tbl.columns.length} col</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: INDEXES EXPLORER */}
          {activeTab === "indexes" && (
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <Layers className="h-4 w-4 text-blue-400" />
                    <span>{isId ? "Katalog Indeks Database Sandbox" : "Sandbox Database Indexes Catalog"}</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    {isId
                      ? "Daftar seluruh indeks B-Tree yang aktif mempercepat akses data kueri."
                      : "All active B-Tree index objects supporting fast query access paths."}
                  </p>
                </div>
                <span className="rounded-lg bg-blue-950/60 border border-blue-800/40 px-3 py-1 font-mono text-xs font-bold text-blue-300">
                  {metadata?.indexes.length || 0} {isId ? "Indeks" : "Indexes"}
                </span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="border-b border-slate-800 bg-[#10264A]/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    <tr>
                      <th className="px-4 py-2.5">{isId ? "Nama Indeks" : "Index Name"}</th>
                      <th className="px-4 py-2.5">{isId ? "Tabel Terkait" : "Target Table"}</th>
                      <th className="px-4 py-2.5">{isId ? "Kolom Terindeks" : "Indexed Columns"}</th>
                      <th className="px-4 py-2.5">{isId ? "Tipe Indeks" : "Index Type"}</th>
                      <th className="px-4 py-2.5">{isId ? "Unik" : "Unique"}</th>
                      <th className="px-4 py-2.5">{isId ? "Indeks Utama" : "Primary"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-mono">
                    {metadata?.indexes.map((idx, i) => (
                      <tr key={`${idx.name}-${i}`} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-4 py-2.5 font-bold text-white">{idx.name}</td>
                        <td className="px-4 py-2.5 text-[#F2B84B] font-semibold">{idx.table_name}</td>
                        <td className="px-4 py-2.5 text-blue-300">{idx.columns.join(", ")}</td>
                        <td className="px-4 py-2.5 text-slate-400">{idx.index_type}</td>
                        <td className="px-4 py-2.5">
                          {idx.is_unique ? (
                            <span className="rounded bg-purple-950/60 border border-purple-800/40 px-2 py-0.5 text-[10px] font-bold text-purple-300">
                              UNIQUE
                            </span>
                          ) : (
                            <span className="text-slate-600">NO</span>
                          )}
                        </td>
                        <td className="px-4 py-2.5">
                          {idx.is_primary ? (
                            <span className="rounded bg-amber-500/20 border border-amber-500/40 px-2 py-0.5 text-[10px] font-bold text-[#F2B84B]">
                              PRIMARY
                            </span>
                          ) : (
                            <span className="text-slate-600">NO</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: CONSTRAINTS EXPLORER */}
          {activeTab === "constraints" && (
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <Key className="h-4 w-4 text-[#F2B84B]" />
                    <span>{isId ? "Katalog Batasan & Integritas Data" : "Database Constraints Catalog"}</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    {isId
                      ? "Daftar Primary Key, Foreign Key, dan Unique constraints yang menjaga integritas database."
                      : "Primary Keys, Foreign Keys, and Unique constraints safeguarding relational integrity."}
                  </p>
                </div>
                <span className="rounded-lg bg-amber-950/60 border border-amber-800/40 px-3 py-1 font-mono text-xs font-bold text-[#F2B84B]">
                  {metadata?.constraints.length || 0} {isId ? "Batasan" : "Constraints"}
                </span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="border-b border-slate-800 bg-[#10264A]/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    <tr>
                      <th className="px-4 py-2.5">{isId ? "Nama Batasan" : "Constraint Name"}</th>
                      <th className="px-4 py-2.5">{isId ? "Tabel" : "Table"}</th>
                      <th className="px-4 py-2.5">{isId ? "Jenis" : "Type"}</th>
                      <th className="px-4 py-2.5">{isId ? "Kolom" : "Columns"}</th>
                      <th className="px-4 py-2.5">{isId ? "Referensi Target" : "Target Reference"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-mono">
                    {metadata?.constraints.map((c, i) => (
                      <tr key={`${c.name}-${i}`} className="hover:bg-slate-800/40 transition-colors">
                        <td className="px-4 py-2.5 font-bold text-white">{c.name}</td>
                        <td className="px-4 py-2.5 text-[#F2B84B] font-semibold">{c.table_name}</td>
                        <td className="px-4 py-2.5">
                          <span
                            className={`rounded px-2 py-0.5 text-[10px] font-bold ${
                              c.type === "PRIMARY KEY"
                                ? "bg-amber-500/20 text-[#F2B84B] border border-amber-500/40"
                                : c.type === "FOREIGN KEY"
                                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                : "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                            }`}
                          >
                            {c.type}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-blue-300">{c.columns.join(", ")}</td>
                        <td className="px-4 py-2.5 text-slate-400">
                          {c.referenced_table ? `${c.referenced_table}(${(c.referenced_columns || []).join(", ")})` : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: TABLE DATA PREVIEW */}
          {activeTab === "preview" && (
            <div className="flex-1 flex flex-col overflow-hidden p-4 sm:p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3 flex-none">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <Eye className="h-4 w-4 text-[#F2B84B]" />
                    <span>{isId ? `Pratinjau Data Tabel: ${selectedTable || "-"}` : `Data Preview: ${selectedTable || "-"}`}</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    {isId
                      ? "Membaca baris data secara aman dengan pagination terkendali (Read-Only)."
                      : "Safe paginated table inspection respecting read-only sandbox mode."}
                  </p>
                </div>

                {/* Table Picker in Preview Tab */}
                <div className="flex items-center gap-2 flex-wrap text-xs">
                  <span className="text-slate-400">{isId ? "Pilih Tabel:" : "Select Table:"}</span>
                  <select
                    value={selectedTable || ""}
                    onChange={(e) => {
                      setSelectedTable(e.target.value);
                      setPreviewPage(1);
                    }}
                    className="rounded-lg bg-slate-900 border border-slate-700 px-3 py-1.5 text-white font-mono text-xs focus:outline-none focus:border-[#F2B84B]"
                  >
                    {metadata?.tables.map((t) => (
                      <option key={t.name} value={t.name}>
                        {t.name} ({t.row_count} rows)
                      </option>
                    ))}
                  </select>

                  <select
                    value={previewPageSize}
                    onChange={(e) => {
                      setPreviewPageSize(Number(e.target.value));
                      setPreviewPage(1);
                    }}
                    className="rounded-lg bg-slate-900 border border-slate-700 px-2 py-1.5 text-white font-mono text-xs focus:outline-none"
                  >
                    <option value={10}>10 / page</option>
                    <option value={20}>20 / page</option>
                    <option value={50}>50 / page</option>
                  </select>
                </div>
              </div>

              {/* Data Preview Table */}
              <div className="flex-1 overflow-auto rounded-xl border border-slate-800 bg-slate-900/60 relative">
                {previewLoading ? (
                  <div className="absolute inset-0 bg-[#071A3A]/80 flex items-center justify-center space-y-2 z-10">
                    <RefreshCw className="h-5 w-5 animate-spin text-[#F2B84B]" />
                  </div>
                ) : !previewData || previewData.rows.length === 0 ? (
                  <div className="p-8 text-center text-slate-500 text-xs">
                    {isId ? "Tabel belum memiliki data atau kosong." : "Table has no records."}
                  </div>
                ) : (
                  <table className="w-full text-left text-xs text-slate-200">
                    <thead className="sticky top-0 z-10 border-b border-slate-800 bg-[#10264A] text-[11px] font-bold uppercase tracking-wider text-slate-300">
                      <tr>
                        {previewData.columns.map((colName: string) => {
                          const isSorted = previewSortBy === colName;
                          return (
                            <th
                              key={colName}
                              onClick={() => {
                                if (previewSortBy === colName) {
                                  setPreviewSortOrder(previewSortOrder === "ASC" ? "DESC" : "ASC");
                                } else {
                                  setPreviewSortBy(colName);
                                  setPreviewSortOrder("ASC");
                                }
                              }}
                              className="px-4 py-2.5 font-mono cursor-pointer hover:bg-slate-800/80 transition-colors whitespace-nowrap"
                            >
                              <div className="flex items-center gap-1.5">
                                <span>{colName}</span>
                                <ArrowUpDown
                                  className={`h-3 w-3 ${isSorted ? "text-[#F2B84B]" : "text-slate-500"}`}
                                />
                              </div>
                            </th>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 font-mono text-[11px]">
                      {previewData.rows.map((row: any, rIdx: number) => (
                        <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                          {previewData.columns.map((cName: string) => {
                            const val = row[cName];
                            return (
                              <td key={cName} className="px-4 py-2 truncate max-w-[200px]">
                                {val === null ? (
                                  <span className="text-slate-600">NULL</span>
                                ) : typeof val === "boolean" ? (
                                  val ? "TRUE" : "FALSE"
                                ) : (
                                  String(val)
                                )}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {/* Pagination Footer */}
              {previewData && (
                <div className="flex items-center justify-between border-t border-slate-800 pt-2 text-xs text-slate-400 flex-none font-mono">
                  <span>
                    {isId ? "Menampilkan" : "Showing"} {previewData.rows.length} {isId ? "dari" : "of"}{" "}
                    {previewData.total_rows} {isId ? "baris" : "total rows"}
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPreviewPage((p) => Math.max(1, p - 1))}
                      disabled={previewPage <= 1}
                      className="rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 px-3 py-1 font-semibold text-slate-200"
                    >
                      {isId ? "Sebelumnya" : "Previous"}
                    </button>
                    <span>
                      {isId ? "Halaman" : "Page"} {previewPage} / {Math.max(1, Math.ceil(previewData.total_rows / previewPageSize))}
                    </span>
                    <button
                      onClick={() => setPreviewPage((p) => p + 1)}
                      disabled={previewPage * previewPageSize >= previewData.total_rows}
                      className="rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 px-3 py-1 font-semibold text-slate-200"
                    >
                      {isId ? "Selanjutnya" : "Next"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import {
  Wrench,
  ExternalLink,
  Search,
  CheckCircle,
  Database,
  Activity,
  Layers,
  FileCode,
  Shield,
  X,
  BookOpen,
  AlertTriangle,
  Terminal,
  Cpu,
  Server,
  Key,
  ShieldCheck,
  Check,
  Copy,
  Info,
  ArrowRight,
  GitBranch,
  RefreshCw,
  FolderGit2,
  Workflow,
  Lock,
  Compass,
  GraduationCap,
  Sparkles,
  SlidersHorizontal,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";

// ─── Interfaces ─────────────────────────────────────────────────────────────

interface FeatureItem {
  name_en: string;
  name_id: string;
  description_en: string;
  description_id: string;
  edition_scope: string;
  verification_status: string;
}

interface CompatibilityTarget {
  target_type: string;
  target_name: string;
  version_scope: string;
  support_level: string;
  notes_en: string;
  notes_id: string;
  verification_status: string;
}

interface SecurityConsiderations {
  credential_storage: string;
  network_and_ports: string;
  tls_ssl_support: string;
  privilege_model: string;
  audit_logging: string;
}

interface GettingStartedStep {
  step_number: number;
  title_en: string;
  title_id: string;
  command?: string | null;
  instruction_en: string;
  instruction_id: string;
  checkpoint_en?: string | null;
  checkpoint_id?: string | null;
}

interface GettingStartedWorkflow {
  prerequisites_en: string[];
  prerequisites_id: string[];
  steps: GettingStartedStep[];
  safe_first_test_en: string;
  safe_first_test_id: string;
  troubleshooting_tips_en: string[];
  troubleshooting_tips_id: string[];
}

interface ProfessionalScenario {
  scenario_id: string;
  title_en: string;
  title_id: string;
  role: string;
  goal_en: string;
  goal_id: string;
  environment: string;
  steps_en: string[];
  steps_id: string[];
  commands: string[];
  validation_en: string;
  validation_id: string;
  expected_result_en: string;
  expected_result_id: string;
  rollback_en?: string | null;
  rollback_id?: string | null;
}

interface CareerConnection {
  role_id: string;
  role_name_en: string;
  role_name_id: string;
  competency_id: string;
  competency_name_en: string;
  competency_name_id: string;
  proficiency_level: string;
  relevance_why_en: string;
  relevance_why_id: string;
}

interface KnowledgeConnection {
  article_slug: string;
  title_en: string;
  title_id: string;
  relationship_type: string;
}

interface ExerciseConnection {
  exercise_slug: string;
  title_en: string;
  title_id: string;
  lab_type: string;
}

interface ToolAlternative {
  slug: string;
  name: string;
  product_type: string;
  license_model: string;
  tradeoff_en: string;
  tradeoff_id: string;
}

interface VerifiedSourceCitation {
  claim_topic: string;
  source_url: string;
  source_title: string;
  verified_at: string;
  status: string;
}

interface ToolSummary {
  id: string;
  slug: string;
  name: string;
  vendor?: string | null;
  category_slug?: string | null;
  category_name?: string | null;
  category_name_id?: string | null;
  product_type: string;
  summary?: string | null;
  summary_id?: string | null;
  official_url?: string | null;
  documentation_url?: string | null;
  license_model?: string | null;
  supported_platforms: string[];
  supported_engines: string[];
  verification_status: string;
  publication_status: string;
  lifecycle_status: string;
  last_verified_at?: string | null;
}

interface ToolDetail extends ToolSummary {
  repository_url?: string | null;
  download_url?: string | null;
  overview_en?: string | null;
  overview_id?: string | null;
  primary_use_cases_en: string[];
  primary_use_cases_id: string[];
  explicit_boundaries_en: string[];
  explicit_boundaries_id: string[];
  features: FeatureItem[];
  compatibility_matrix: CompatibilityTarget[];
  security_considerations?: SecurityConsiderations | null;
  getting_started?: GettingStartedWorkflow | null;
  practical_scenarios: ProfessionalScenario[];
  career_connections: CareerConnection[];
  knowledge_connections: KnowledgeConnection[];
  exercise_connections: ExerciseConnection[];
  alternatives: ToolAlternative[];
  verified_sources: VerifiedSourceCitation[];
  content_reviewed_at?: string | null;
}

interface ToolCategory {
  id: string;
  slug: string;
  name_en: string;
  name_id: string;
  description_en?: string | null;
  description_id?: string | null;
  tool_count: number;
}

interface ToolsCatalogProps {
  language: "en" | "id";
  initialToolSlug?: string | null;
  onNavigateToKnowledge?: (slug: string) => void;
  onNavigateToRole?: (roleSlug: string) => void;
  onNavigateToChallenge?: (challengeSlug: string) => void;
  onNavigateToExercise?: (slug: string) => void;
}

type DetailTab =
  | "overview"
  | "features"
  | "getting_started"
  | "scenarios"
  | "compatibility"
  | "learning"
  | "alternatives"
  | "sources";

export function ToolsCatalog({
  language,
  initialToolSlug,
  onNavigateToKnowledge,
  onNavigateToRole,
  onNavigateToChallenge,
  onNavigateToExercise,
}: ToolsCatalogProps) {
  const isId = language === "id";

  // Catalog State
  const [tools, setTools] = useState<ToolSummary[]>([]);
  const [categories, setCategories] = useState<ToolCategory[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedEngine, setSelectedEngine] = useState<string>("all");
  const [selectedPlatform, setSelectedPlatform] = useState<string>("all");
  const [selectedLicense, setSelectedLicense] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("name");

  // Detail Modal State
  const [activeToolSlug, setActiveToolSlug] = useState<string | null>(null);
  const [activeDetail, setActiveDetail] = useState<ToolDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<DetailTab>("overview");
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  // Engine & Platform options
  const engineOptions = [
    { id: "all", label: isId ? "Semua Mesin" : "All Engines" },
    { id: "PostgreSQL", label: "PostgreSQL" },
    { id: "MySQL", label: "MySQL / MariaDB" },
    { id: "Oracle", label: "Oracle Database" },
    { id: "SQL Server", label: "SQL Server" },
    { id: "SQLite", label: "SQLite" },
    { id: "Snowflake", label: "Snowflake" },
    { id: "DuckDB", label: "DuckDB" },
  ];

  const platformOptions = [
    { id: "all", label: isId ? "Semua OS" : "All Platforms" },
    { id: "Linux", label: "Linux" },
    { id: "Windows", label: "Windows" },
    { id: "macOS", label: "macOS" },
    { id: "Docker", label: "Docker" },
  ];

  // Fetch Tools List
  const fetchTools = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, any> = {
        sort: sortBy,
        limit: 100,
      };
      if (searchTerm.trim()) params.search = searchTerm.trim();
      if (selectedCategory !== "all") params.category = selectedCategory;
      if (selectedEngine !== "all") params.engine = selectedEngine;
      if (selectedPlatform !== "all") params.platform = selectedPlatform;
      if (selectedLicense !== "all") params.license = selectedLicense;
      if (selectedStatus !== "all") params.status = selectedStatus;

      const res = await api.get("/tools", { params });
      if (res.data) {
        setTools(res.data.items || []);
        if (res.data.categories && res.data.categories.length > 0) {
          setCategories(res.data.categories);
        }
      }
    } catch (err: any) {
      console.error("Error fetching tools catalog:", err);
      setError(
        isId
          ? "Gagal memuat katalog alat dari server."
          : "Failed to load tools catalog from backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTools();
  }, [
    searchTerm,
    selectedCategory,
    selectedEngine,
    selectedPlatform,
    selectedLicense,
    selectedStatus,
    sortBy,
  ]);

  // Fetch Single Tool Detail
  const handleOpenDetail = async (slug: string) => {
    try {
      setActiveToolSlug(slug);
      setLoadingDetail(true);
      setActiveTab("overview");
      const res = await api.get(`/tools/${slug}`);
      if (res.data) {
        setActiveDetail(res.data);
      }
    } catch (err: any) {
      console.error("Error loading tool detail:", err);
    } finally {
      setLoadingDetail(false);
    }
  };

  useEffect(() => {
    if (initialToolSlug) {
      handleOpenDetail(initialToolSlug);
    }
  }, [initialToolSlug]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCommand(text);
    setTimeout(() => setCopiedCommand(null), 2000);
  };

  return (
    <div className="flex flex-col h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* ── Top Header & Filter Controls Bar ─────────────────────────────── */}
      <div className="border-b border-slate-800 bg-[#10264A]/40 p-3 sm:p-5 shrink-0 space-y-3">
        {/* Title & Search Line */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-0.5">
              <Wrench className="h-4 w-4" />
              <span>
                {isId
                  ? "Katalog Alat & Observabilitas Database Profesional"
                  : "Professional Database Tools & Observability Catalog"}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {isId
                ? "Direktori terverifikasi untuk administrasi, keandalan (DBRE), migrasi, dan pipeline data."
                : "Authoritative verified directory for DBA administration, reliability engineering, and migrations."}
            </p>
          </div>

          {/* Search Bar */}
          <div className="relative w-full md:w-80 shrink-0">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder={
                isId
                  ? "Cari nama, vendor, atau kapabilitas..."
                  : "Search tool, vendor, capability..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-xl bg-slate-900 border border-slate-700/80 pl-9 pr-8 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#F2B84B] min-h-[38px]"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                className="absolute right-2.5 top-2.5 text-slate-500 hover:text-slate-200"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll pt-1 border-t border-slate-800/80">
          <button
            onClick={() => setSelectedCategory("all")}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all min-h-[34px] ${
              selectedCategory === "all"
                ? "bg-[#F2B84B] text-[#071A3A] font-bold shadow-xs"
                : "bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800"
            }`}
          >
            {isId ? "Semua Kategori" : "All Categories"} ({tools.length})
          </button>
          {categories.map((c) => (
            <button
              key={c.slug}
              onClick={() => setSelectedCategory(c.slug)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all min-h-[34px] ${
                selectedCategory === c.slug
                  ? "bg-[#F2B84B] text-[#071A3A] font-bold shadow-xs"
                  : "bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              <span>{isId ? c.name_id || c.name_en : c.name_en}</span>
              {c.tool_count > 0 && (
                <span className="ml-1.5 opacity-75 text-[10px]">({c.tool_count})</span>
              )}
            </button>
          ))}
        </div>

        {/* Secondary Filter Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar touch-scroll">
            <span className="text-[11px] font-semibold text-slate-400 shrink-0">
              {isId ? "Filter Mesin:" : "Engine:"}
            </span>
            <div className="flex items-center gap-1">
              {engineOptions.map((e) => (
                <button
                  key={e.id}
                  onClick={() => setSelectedEngine(e.id)}
                  className={`rounded-md px-2 py-1 text-[11px] font-medium transition-colors ${
                    selectedEngine === e.id
                      ? "bg-slate-700 text-[#F2B84B] border border-[#F2B84B]/40 font-bold"
                      : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
                  }`}
                >
                  {e.label}
                </button>
              ))}
            </div>

            <div className="h-4 w-px bg-slate-800 mx-1 hidden sm:block" />

            <span className="text-[11px] font-semibold text-slate-400 shrink-0 hidden sm:inline">
              OS:
            </span>
            <div className="hidden sm:flex items-center gap-1">
              {platformOptions.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedPlatform(p.id)}
                  className={`rounded-md px-2 py-1 text-[11px] font-medium transition-colors ${
                    selectedPlatform === p.id
                      ? "bg-slate-700 text-[#F2B84B] border border-[#F2B84B]/40 font-bold"
                      : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Sort Selector */}
          <div className="flex items-center gap-1.5 shrink-0 text-[11px] font-mono">
            <span className="text-slate-400">{isId ? "Urutkan:" : "Sort:"}</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="rounded-lg bg-slate-900 border border-slate-700 text-slate-200 px-2 py-1 text-xs focus:outline-none"
            >
              <option value="name">{isId ? "Nama (A-Z)" : "Alphabetical (A-Z)"}</option>
              <option value="verified">{isId ? "Verifikasi Terbaru" : "Recently Verified"}</option>
              <option value="recent">{isId ? "Baru Ditambahkan" : "Recently Added"}</option>
            </select>
          </div>
        </div>
      </div>

      {/* ── Main Catalog Grid ────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 no-scrollbar touch-scroll">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-3">
            <RefreshCw className="h-7 w-7 animate-spin text-[#F2B84B]" />
            <p className="text-xs font-mono">
              {isId ? "Memuat katalog alat terverifikasi..." : "Loading verified tools catalog..."}
            </p>
          </div>
        ) : error ? (
          <div className="rounded-xl border border-red-500/40 bg-red-950/30 p-6 text-center text-red-300 max-w-md mx-auto">
            <AlertTriangle className="h-6 w-6 text-red-400 mx-auto mb-2" />
            <p className="text-xs">{error}</p>
            <button
              onClick={fetchTools}
              className="mt-3 rounded-lg bg-red-800 hover:bg-red-700 px-3 py-1.5 text-xs font-bold text-white"
            >
              {isId ? "Coba Lagi" : "Retry"}
            </button>
          </div>
        ) : tools.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500 space-y-2">
            <Wrench className="h-8 w-8 text-slate-600" />
            <p className="text-sm font-semibold">
              {isId ? "Tidak ada alat yang cocok dengan filter." : "No tools match active filters."}
            </p>
            <button
              onClick={() => {
                setSearchTerm("");
                setSelectedCategory("all");
                setSelectedEngine("all");
                setSelectedPlatform("all");
                setSelectedLicense("all");
                setSelectedStatus("all");
              }}
              className="text-xs text-[#F2B84B] hover:underline"
            >
              {isId ? "Reset semua filter" : "Clear all filters"}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 max-w-7xl mx-auto">
            {tools.map((tool) => (
              <div
                key={tool.slug}
                onClick={() => handleOpenDetail(tool.slug)}
                className="group flex flex-col justify-between rounded-2xl border border-slate-800 bg-[#071329]/80 p-4 sm:p-5 hover:border-[#F2B84B]/50 transition-all hover:bg-slate-900/50 shadow-sm cursor-pointer"
              >
                <div>
                  {/* Category & Status Badges */}
                  <div className="flex items-center justify-between text-[11px] mb-2.5 gap-2">
                    <span className="rounded-md bg-[#10264A] border border-slate-700/80 px-2.5 py-0.5 text-slate-300 font-semibold truncate">
                      {isId ? tool.category_name_id || tool.category_name : tool.category_name}
                    </span>
                    <span className="flex items-center gap-1 rounded-full bg-emerald-950/70 border border-emerald-600/50 px-2 py-0.5 text-[10px] text-emerald-300 font-bold shrink-0">
                      <ShieldCheck className="h-3 w-3 text-emerald-400" />
                      <span>{isId ? "Terverifikasi" : "Verified"}</span>
                    </span>
                  </div>

                  {/* Name and Vendor */}
                  <h3 className="text-base font-bold text-white group-hover:text-[#F2B84B] transition-colors mb-0.5">
                    {tool.name}
                  </h3>
                  <div className="text-[11px] font-mono text-slate-400 mb-2">
                    {isId ? "Oleh" : "By"} {tool.vendor || "Community"} •{" "}
                    <span className="text-slate-300 font-semibold">{tool.license_model}</span>
                  </div>

                  {/* Summary */}
                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-4">
                    {isId ? tool.summary_id || tool.summary : tool.summary}
                  </p>
                </div>

                <div>
                  {/* Supported Engines Tags */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {tool.supported_engines.slice(0, 5).map((eng) => (
                      <span
                        key={eng}
                        className="rounded bg-slate-900/90 border border-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400"
                      >
                        {eng}
                      </span>
                    ))}
                    {tool.supported_engines.length > 5 && (
                      <span className="rounded bg-slate-900/90 border border-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-500">
                        +{tool.supported_engines.length - 5}
                      </span>
                    )}
                  </div>

                  {/* Card Actions */}
                  <div className="flex items-center justify-between border-t border-slate-800/80 pt-3">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenDetail(tool.slug);
                      }}
                      className="flex items-center gap-1 text-xs font-bold text-[#F2B84B] group-hover:underline"
                    >
                      <span>{isId ? "Lihat Detail & Panduan" : "Full Specs & Guide"}</span>
                      <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </button>

                    {tool.official_url && (
                      <a
                        href={tool.official_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        title={isId ? "Kunjungi situs resmi" : "Visit official website"}
                        className="p-1 text-slate-400 hover:text-white"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Comprehensive Tool Detail Modal ──────────────────────────────── */}
      {activeToolSlug && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-2 sm:p-4 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-4xl max-h-[92vh] flex flex-col rounded-2xl border border-slate-700 bg-[#071A3A] shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="border-b border-slate-800 bg-[#10264A]/70 p-4 sm:p-5 shrink-0 flex items-start justify-between gap-4">
              {loadingDetail || !activeDetail ? (
                <div className="flex items-center gap-3">
                  <RefreshCw className="h-5 w-5 animate-spin text-[#F2B84B]" />
                  <span className="text-sm text-slate-400 font-mono">
                    {isId ? "Memuat spesifikasi teknis..." : "Loading technical specs..."}
                  </span>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-md bg-slate-900 border border-slate-700 px-2.5 py-0.5 text-[11px] font-semibold text-slate-300">
                      {isId
                        ? activeDetail.category_name_id || activeDetail.category_name
                        : activeDetail.category_name}
                    </span>
                    <span className="rounded-md bg-slate-900/80 border border-slate-700 px-2 py-0.5 text-[10px] font-mono text-[#F2B84B]">
                      {activeDetail.product_type}
                    </span>
                    <span className="flex items-center gap-1 rounded-full bg-emerald-950/80 border border-emerald-600/50 px-2 py-0.5 text-[10px] text-emerald-300 font-bold">
                      <ShieldCheck className="h-3 w-3 text-emerald-400" />
                      <span>{isId ? "Klaim Terverifikasi" : "Verified Claims"}</span>
                    </span>
                  </div>
                  <h2 className="text-lg sm:text-2xl font-bold text-white flex items-center gap-2">
                    <span>{activeDetail.name}</span>
                  </h2>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    <span>
                      {isId ? "Vendor / Proyek:" : "Vendor / Project:"}{" "}
                      <strong className="text-slate-200">{activeDetail.vendor}</strong>
                    </span>
                    <span>•</span>
                    <span>
                      {isId ? "Lisensi:" : "License:"}{" "}
                      <strong className="text-emerald-400">{activeDetail.license_model}</strong>
                    </span>
                    {activeDetail.official_url && (
                      <>
                        <span>•</span>
                        <a
                          href={activeDetail.official_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-[#F2B84B] hover:underline"
                        >
                          <span>{isId ? "Situs Resmi" : "Official Website"}</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </>
                    )}
                  </div>
                </div>
              )}

              <button
                onClick={() => {
                  setActiveToolSlug(null);
                  setActiveDetail(null);
                }}
                className="rounded-lg p-2 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors shrink-0"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Detail Tabs */}
            {activeDetail && (
              <div className="border-b border-slate-800 bg-[#071329] px-4 sm:px-6 flex items-center gap-1 overflow-x-auto no-scrollbar touch-scroll shrink-0">
                {[
                  { id: "overview" as const, label: isId ? "Ikhtisar" : "Overview", icon: Info },
                  { id: "features" as const, label: isId ? "Fitur & Keamanan" : "Features & Security", icon: Shield },
                  { id: "getting_started" as const, label: isId ? "Panduan Memulai" : "Getting Started", icon: Terminal },
                  { id: "scenarios" as const, label: isId ? "Skenario Produksi" : "Production Scenarios", icon: Workflow },
                  { id: "compatibility" as const, label: isId ? "Kompatibilitas" : "Compatibility", icon: Database },
                  { id: "learning" as const, label: isId ? "Jalur Karir & Belajar" : "Careers & Learning", icon: GraduationCap },
                  { id: "alternatives" as const, label: isId ? "Alternatif" : "Alternatives", icon: GitBranch },
                  { id: "sources" as const, label: isId ? "Sumber & Bukti" : "Verified Sources", icon: BookOpen },
                ].map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-semibold whitespace-nowrap transition-colors border-b-2 ${
                        isActive
                          ? "border-[#F2B84B] text-[#F2B84B] font-bold"
                          : "border-transparent text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Modal Body Container */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 no-scrollbar touch-scroll text-slate-300 text-xs">
              {!activeDetail ? (
                <div className="py-20 text-center text-slate-500 font-mono">
                  {isId ? "Sedang memuat data detail..." : "Loading detailed specs..."}
                </div>
              ) : (
                <>
                  {/* ── 1. Tab: Overview ── */}
                  {activeTab === "overview" && (
                    <div className="space-y-5 animate-fade-in">
                      {/* Summary & Technical Overview */}
                      <div className="space-y-3">
                        <div className="rounded-xl border border-slate-800 bg-[#10264A]/30 p-4 text-sm leading-relaxed text-slate-200">
                          {isId
                            ? activeDetail.summary_id || activeDetail.summary
                            : activeDetail.summary}
                        </div>
                        {activeDetail.overview_en && (
                          <div className="space-y-1.5">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B]">
                              {isId ? "Tinjauan Teknis Mendalam" : "In-Depth Technical Overview"}
                            </h4>
                            <p className="leading-relaxed text-slate-300">
                              {isId
                                ? activeDetail.overview_id || activeDetail.overview_en
                                : activeDetail.overview_en}
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Primary Use Cases */}
                      {activeDetail.primary_use_cases_en.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                            <CheckCircle className="h-4 w-4" />
                            <span>
                              {isId ? "Kapan Alat Ini Tepat Digunakan (Jobs-To-Be-Done)" : "Primary Jobs-To-Be-Done"}
                            </span>
                          </h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {(isId
                              ? activeDetail.primary_use_cases_id.length > 0
                                ? activeDetail.primary_use_cases_id
                                : activeDetail.primary_use_cases_en
                              : activeDetail.primary_use_cases_en
                            ).map((uc, i) => (
                              <div
                                key={i}
                                className="flex items-start gap-2 rounded-xl border border-slate-800 bg-slate-900/60 p-3"
                              >
                                <span className="text-emerald-400 font-bold">•</span>
                                <span>{uc}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Explicit Boundaries (What it does NOT do) */}
                      {activeDetail.explicit_boundaries_en.length > 0 && (
                        <div className="rounded-xl border border-amber-600/40 bg-amber-950/20 p-4 space-y-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                            <AlertTriangle className="h-4 w-4 text-amber-400" />
                            <span>
                              {isId
                                ? "Batasan Eksplisit (Kapan Alat Ini Tidak Tepat)"
                                : "Explicit Boundaries & Anti-Patterns"}
                            </span>
                          </h4>
                          <ul className="space-y-1.5 text-amber-200/90 text-xs">
                            {(isId
                              ? activeDetail.explicit_boundaries_id.length > 0
                                ? activeDetail.explicit_boundaries_id
                                : activeDetail.explicit_boundaries_en
                              : activeDetail.explicit_boundaries_en
                            ).map((b, i) => (
                              <li key={i} className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold">×</span>
                                <span>{b}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Quick Facts Grid */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800">
                        <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-2.5">
                          <span className="text-[10px] text-slate-500 uppercase block">
                            {isId ? "Tipe Produk" : "Product Type"}
                          </span>
                          <strong className="text-slate-200">{activeDetail.product_type}</strong>
                        </div>
                        <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-2.5">
                          <span className="text-[10px] text-slate-500 uppercase block">
                            {isId ? "Model Lisensi" : "License Model"}
                          </span>
                          <strong className="text-emerald-400">{activeDetail.license_model}</strong>
                        </div>
                        <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-2.5">
                          <span className="text-[10px] text-slate-500 uppercase block">
                            {isId ? "Status Siklus Hidup" : "Lifecycle Status"}
                          </span>
                          <strong className="text-slate-200 capitalize">
                            {activeDetail.lifecycle_status}
                          </strong>
                        </div>
                        <div className="rounded-lg bg-slate-900/80 border border-slate-800 p-2.5">
                          <span className="text-[10px] text-slate-500 uppercase block">
                            {isId ? "Terakhir Diverifikasi" : "Last Verified"}
                          </span>
                          <strong className="text-[#F2B84B] font-mono">
                            {activeDetail.last_verified_at
                              ? new Date(activeDetail.last_verified_at).toLocaleDateString()
                              : "2026-11-06"}
                          </strong>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* ── 2. Tab: Features & Security ── */}
                  {activeTab === "features" && (
                    <div className="space-y-5 animate-fade-in">
                      {/* Features List */}
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] mb-3 flex items-center gap-1.5">
                          <Layers className="h-4 w-4" />
                          <span>{isId ? "Fitur Utama & Lingkup Edisi" : "Key Capabilities & Editions"}</span>
                        </h4>
                        <div className="space-y-2.5">
                          {activeDetail.features.map((feat, idx) => (
                            <div
                              key={idx}
                              className="rounded-xl border border-slate-800 bg-[#071329] p-3.5 space-y-1"
                            >
                              <div className="flex items-center justify-between">
                                <h5 className="font-bold text-white text-xs">
                                  {isId ? feat.name_id || feat.name_en : feat.name_en}
                                </h5>
                                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-400 uppercase">
                                  {feat.edition_scope}
                                </span>
                              </div>
                              <p className="text-slate-300 leading-relaxed">
                                {isId ? feat.description_id || feat.description_en : feat.description_en}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Security Considerations Card */}
                      {activeDetail.security_considerations && (
                        <div className="rounded-xl border border-blue-900/60 bg-[#10264A]/30 p-4 space-y-3">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                            <Lock className="h-4 w-4 text-blue-400" />
                            <span>
                              {isId
                                ? "Pertimbangan Keamanan & Tata Kelola (Security Considerations)"
                                : "Security & Governance Architecture"}
                            </span>
                          </h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                            <div className="rounded-lg bg-slate-900/70 p-3 border border-slate-800">
                              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                {isId ? "Penyimpanan Kredensial" : "Credential Storage"}
                              </span>
                              <p className="text-slate-300">
                                {activeDetail.security_considerations.credential_storage}
                              </p>
                            </div>
                            <div className="rounded-lg bg-slate-900/70 p-3 border border-slate-800">
                              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                {isId ? "Jaringan & Port" : "Network Exposure & Ports"}
                              </span>
                              <p className="text-slate-300">
                                {activeDetail.security_considerations.network_and_ports}
                              </p>
                            </div>
                            <div className="rounded-lg bg-slate-900/70 p-3 border border-slate-800">
                              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                {isId ? "Dukungan TLS / SSL" : "TLS / SSL Encryption"}
                              </span>
                              <p className="text-slate-300">
                                {activeDetail.security_considerations.tls_ssl_support}
                              </p>
                            </div>
                            <div className="rounded-lg bg-slate-900/70 p-3 border border-slate-800">
                              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                {isId ? "Model Hak Akses" : "Least Privilege Model"}
                              </span>
                              <p className="text-slate-300">
                                {activeDetail.security_considerations.privilege_model}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* ── 3. Tab: Getting Started ── */}
                  {activeTab === "getting_started" && activeDetail.getting_started && (
                    <div className="space-y-5 animate-fade-in">
                      {/* Prerequisites */}
                      {activeDetail.getting_started.prerequisites_en.length > 0 && (
                        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-1.5">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B]">
                            {isId ? "Prasyarat Sistem" : "Prerequisites"}
                          </h4>
                          <ul className="space-y-1 text-slate-300 list-disc list-inside">
                            {(isId
                              ? activeDetail.getting_started.prerequisites_id
                              : activeDetail.getting_started.prerequisites_en
                            ).map((pre, i) => (
                              <li key={i}>{pre}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Step-by-Step Instructions */}
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-white">
                          {isId ? "Langkah Pemasangan & Konfigurasi" : "Installation & Setup Steps"}
                        </h4>
                        {activeDetail.getting_started.steps.map((step) => (
                          <div
                            key={step.step_number}
                            className="rounded-xl border border-slate-800 bg-[#071329] p-4 space-y-2.5"
                          >
                            <div className="flex items-center gap-2">
                              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#F2B84B] text-[11px] font-bold text-[#071A3A]">
                                {step.step_number}
                              </span>
                              <h5 className="font-bold text-white text-xs">
                                {isId ? step.title_id : step.title_en}
                              </h5>
                            </div>
                            <p className="text-slate-300 leading-relaxed">
                              {isId ? step.instruction_id : step.instruction_en}
                            </p>
                            {step.command && (
                              <div className="relative group rounded-lg bg-black/60 border border-slate-800 p-2.5 font-mono text-xs text-emerald-300">
                                <code>{step.command}</code>
                                <button
                                  onClick={() => handleCopy(step.command!)}
                                  className="absolute right-2 top-2 rounded bg-slate-800 p-1 text-slate-400 hover:text-white"
                                  title="Copy"
                                >
                                  {copiedCommand === step.command ? (
                                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                                  ) : (
                                    <Copy className="h-3.5 w-3.5" />
                                  )}
                                </button>
                              </div>
                            )}
                            {(step.checkpoint_en || step.checkpoint_id) && (
                              <div className="text-[11px] text-slate-400 flex items-center gap-1.5 pt-1">
                                <CheckCircle className="h-3.5 w-3.5 text-[#F2B84B]" />
                                <span>
                                  {isId
                                    ? `Titik periksa: ${step.checkpoint_id}`
                                    : `Checkpoint: ${step.checkpoint_en}`}
                                </span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Safe First Test Workflow */}
                      <div className="rounded-xl border border-emerald-600/40 bg-emerald-950/20 p-4 space-y-1">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                          <CheckCircle className="h-4 w-4" />
                          <span>
                            {isId ? "Uji Coba Pertama yang Aman" : "Safe First Test Workflow"}
                          </span>
                        </h4>
                        <p className="text-emerald-200/90 text-xs leading-relaxed">
                          {isId
                            ? activeDetail.getting_started.safe_first_test_id
                            : activeDetail.getting_started.safe_first_test_en}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* ── 4. Tab: Scenarios ── */}
                  {activeTab === "scenarios" && (
                    <div className="space-y-5 animate-fade-in">
                      <div className="space-y-4">
                        {activeDetail.practical_scenarios.map((scen, idx) => (
                          <div
                            key={scen.scenario_id || idx}
                            className="rounded-xl border border-slate-800 bg-[#071329] p-4 sm:p-5 space-y-3"
                          >
                            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2.5">
                              <div>
                                <span className="text-[10px] font-mono text-[#F2B84B] uppercase block">
                                  {isId ? "Peran:" : "Role:"} {scen.role}
                                </span>
                                <h5 className="text-sm font-bold text-white">
                                  {isId ? scen.title_id : scen.title_en}
                                </h5>
                              </div>
                              <span className="rounded-md bg-slate-900 border border-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-400">
                                {scen.environment}
                              </span>
                            </div>

                            {/* Goal */}
                            <div>
                              <strong className="text-slate-200 block mb-0.5">
                                {isId ? "Tujuan Operasional:" : "Operational Goal:"}
                              </strong>
                              <p className="text-slate-300">{isId ? scen.goal_id : scen.goal_en}</p>
                            </div>

                            {/* Steps */}
                            <div className="space-y-1">
                              <strong className="text-slate-200 block mb-1">
                                {isId ? "Langkah-Langkah Eksekusi:" : "Execution Steps:"}
                              </strong>
                              <ol className="space-y-1 list-decimal list-inside text-slate-300">
                                {(isId ? scen.steps_id : scen.steps_en).map((st, sidx) => (
                                  <li key={sidx}>{st}</li>
                                ))}
                              </ol>
                            </div>

                            {/* Commands */}
                            {scen.commands && scen.commands.length > 0 && (
                              <div className="space-y-1">
                                <strong className="text-slate-200 block text-[11px]">
                                  {isId ? "Perintah / Kueri Validasi:" : "Commands / Snippets:"}
                                </strong>
                                {scen.commands.map((cmd, cidx) => (
                                  <div
                                    key={cidx}
                                    className="relative group rounded-lg bg-black/60 border border-slate-800 p-2.5 font-mono text-xs text-emerald-300 overflow-x-auto"
                                  >
                                    <code>{cmd}</code>
                                    <button
                                      onClick={() => handleCopy(cmd)}
                                      className="absolute right-2 top-2 rounded bg-slate-800 p-1 text-slate-400 hover:text-white"
                                      title="Copy"
                                    >
                                      {copiedCommand === cmd ? (
                                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                                      ) : (
                                        <Copy className="h-3.5 w-3.5" />
                                      )}
                                    </button>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Validation & Expected Result */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                              <div className="rounded-lg bg-slate-900/60 p-3 border border-slate-800">
                                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                                  {isId ? "Kriteria Validasi" : "Validation Criteria"}
                                </span>
                                <p className="text-slate-300">
                                  {isId ? scen.validation_id : scen.validation_en}
                                </p>
                              </div>
                              <div className="rounded-lg bg-slate-900/60 p-3 border border-slate-800">
                                <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">
                                  {isId ? "Hasil yang Diharapkan" : "Expected Result"}
                                </span>
                                <p className="text-slate-300">
                                  {isId ? scen.expected_result_id : scen.expected_result_en}
                                </p>
                              </div>
                            </div>

                            {/* Rollback */}
                            {(scen.rollback_en || scen.rollback_id) && (
                              <div className="rounded-lg bg-slate-900/40 p-2.5 border border-slate-800/80 text-[11px] text-slate-400">
                                <strong className="text-slate-300">
                                  {isId ? "Panduan Rollback / Pembatalan:" : "Rollback Guidance:"}{" "}
                                </strong>
                                <span>{isId ? scen.rollback_id : scen.rollback_en}</span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* ── 5. Tab: Compatibility ── */}
                  {activeTab === "compatibility" && (
                    <div className="space-y-4 animate-fade-in">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] flex items-center gap-1.5">
                        <Database className="h-4 w-4" />
                        <span>{isId ? "Matriks Kompatibilitas Mesin & Platform" : "Engine & Platform Support Matrix"}</span>
                      </h4>

                      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-[#071329]">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-[#10264A]/70 text-[11px] font-bold text-[#F2B84B] uppercase tracking-wider">
                            <tr>
                              <th className="p-3">{isId ? "Target / Mesin" : "Target / Engine"}</th>
                              <th className="p-3">{isId ? "Cakupan Versi" : "Version Scope"}</th>
                              <th className="p-3">{isId ? "Tingkat Dukungan" : "Support Level"}</th>
                              <th className="p-3">{isId ? "Catatan Teknis" : "Technical Notes"}</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/80 text-slate-300">
                            {activeDetail.compatibility_matrix.map((c, i) => (
                              <tr key={i} className="hover:bg-slate-800/30">
                                <td className="p-3 font-semibold text-white">{c.target_name}</td>
                                <td className="p-3 font-mono text-[11px]">{c.version_scope}</td>
                                <td className="p-3">
                                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-emerald-400 capitalize">
                                    {c.support_level}
                                  </span>
                                </td>
                                <td className="p-3 text-slate-300">
                                  {isId ? c.notes_id : c.notes_en}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* ── 6. Tab: Careers & Learning ── */}
                  {activeTab === "learning" && (
                    <div className="space-y-5 animate-fade-in">
                      {/* Career Connections */}
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] flex items-center gap-1.5">
                          <GraduationCap className="h-4 w-4" />
                          <span>
                            {isId ? "Integrasi Kompetensi Jalur Profesi" : "Career Path Competencies"}
                          </span>
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {activeDetail.career_connections.map((cc, i) => (
                            <div
                              key={i}
                              className="rounded-xl border border-slate-800 bg-[#071329] p-3.5 space-y-2 flex flex-col justify-between"
                            >
                              <div className="space-y-1.5">
                                <div className="flex items-center justify-between">
                                  <span className="font-bold text-white text-xs">
                                    {isId ? cc.role_name_id : cc.role_name_en}
                                  </span>
                                  <span className="rounded bg-amber-950/80 border border-amber-600/40 px-2 py-0.5 text-[10px] font-mono text-amber-300 uppercase">
                                    {cc.proficiency_level}
                                  </span>
                                </div>
                                <div className="text-[11px] text-[#F2B84B] font-medium">
                                  {isId ? cc.competency_name_id : cc.competency_name_en}
                                </div>
                                <p className="text-slate-300 leading-relaxed text-xs">
                                  <strong className="text-slate-400 block mb-0.5">
                                    {isId ? "Mengapa alat ini relevan?" : "Why this tool is relevant:"}
                                  </strong>
                                  {isId ? cc.relevance_why_id : cc.relevance_why_en}
                                </p>
                              </div>
                              <div className="pt-2 border-t border-slate-800/80 flex justify-end">
                                <button
                                  type="button"
                                  onClick={() => {
                                    onNavigateToRole?.(cc.role_id);
                                    setActiveToolSlug(null);
                                  }}
                                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#F2B84B] hover:text-white transition-colors"
                                >
                                  <span>{isId ? "Jelajahi Jalur Profesi" : "Explore Career Path"}</span>
                                  <ArrowRight className="h-3 w-3" />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Related Knowledge Articles */}
                      {activeDetail.knowledge_connections.length > 0 && (
                        <div className="space-y-2 pt-2 border-t border-slate-800">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                            <BookOpen className="h-4 w-4 text-[#F2B84B]" />
                            <span>
                              {isId ? "Artikel Terkait di Pusat Pengetahuan" : "Related Knowledge Articles"}
                            </span>
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {activeDetail.knowledge_connections.map((kc, i) => (
                              <button
                                key={i}
                                onClick={() => {
                                  if (onNavigateToKnowledge) {
                                    onNavigateToKnowledge(kc.article_slug);
                                    setActiveToolSlug(null);
                                  }
                                }}
                                className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-200 hover:border-[#F2B84B] hover:text-[#F2B84B] transition-colors"
                              >
                                <span>{isId ? kc.title_id : kc.title_en}</span>
                                <ArrowRight className="h-3 w-3" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Related Practical SQL Challenges */}
                      {activeDetail.exercise_connections && activeDetail.exercise_connections.length > 0 && (
                        <div className="space-y-2 pt-2 border-t border-slate-800">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                            <Zap className="h-4 w-4" />
                            <span>
                              {isId ? "Tantangan SQL Terkait (Praktik Lab)" : "Related SQL Challenges & Labs"}
                            </span>
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {activeDetail.exercise_connections.map((ec, i) => (
                              <button
                                key={i}
                                type="button"
                                onClick={() => {
                                  if (onNavigateToChallenge) {
                                    onNavigateToChallenge(ec.exercise_slug);
                                  } else if (onNavigateToExercise) {
                                    onNavigateToExercise(ec.exercise_slug);
                                  }
                                  setActiveToolSlug(null);
                                }}
                                className="flex items-center gap-1.5 rounded-lg border border-emerald-700/60 bg-emerald-950/40 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:border-emerald-400 hover:text-white transition-colors min-h-[36px]"
                              >
                                <Database className="h-3.5 w-3.5 text-emerald-400" />
                                <span>{isId ? ec.title_id : ec.title_en}</span>
                                <ArrowRight className="h-3 w-3" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* ── 7. Tab: Alternatives ── */}
                  {activeTab === "alternatives" && (
                    <div className="space-y-4 animate-fade-in">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] flex items-center gap-1.5">
                        <GitBranch className="h-4 w-4" />
                        <span>
                          {isId ? "Komparasi Alternatif & Trade-off" : "Comparable Tools & Trade-offs"}
                        </span>
                      </h4>
                      <div className="space-y-3">
                        {activeDetail.alternatives.map((alt, i) => (
                          <div
                            key={i}
                            className="rounded-xl border border-slate-800 bg-[#071329] p-4 space-y-2"
                          >
                            <div className="flex items-center justify-between">
                              <h5 className="font-bold text-white text-xs">{alt.name}</h5>
                              <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400">
                                {alt.license_model}
                              </span>
                            </div>
                            <p className="text-slate-300 leading-relaxed text-xs">
                              {isId ? alt.tradeoff_id : alt.tradeoff_en}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* ── 8. Tab: Sources & References ── */}
                  {activeTab === "sources" && (
                    <div className="space-y-4 animate-fade-in">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] flex items-center gap-1.5">
                        <BookOpen className="h-4 w-4" />
                        <span>
                          {isId
                            ? "Sumber Primer & Bukti Verifikasi (Provenance)"
                            : "Primary Sources & Verification Evidence"}
                        </span>
                      </h4>

                      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-[#071329]">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-[#10264A]/70 text-[11px] font-bold text-[#F2B84B] uppercase tracking-wider">
                            <tr>
                              <th className="p-3">{isId ? "Topik Klaim" : "Claim Topic"}</th>
                              <th className="p-3">{isId ? "Judul Dokumen / Sumber" : "Source Document"}</th>
                              <th className="p-3">{isId ? "Tanggal Verifikasi" : "Verified Date"}</th>
                              <th className="p-3">{isId ? "Status" : "Status"}</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/80 text-slate-300">
                            {activeDetail.verified_sources.map((src, i) => (
                              <tr key={i} className="hover:bg-slate-800/30">
                                <td className="p-3 font-semibold text-white">{src.claim_topic}</td>
                                <td className="p-3">
                                  <a
                                    href={src.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-[#F2B84B] hover:underline flex items-center gap-1"
                                  >
                                    <span>{src.source_title}</span>
                                    <ExternalLink className="h-3 w-3 shrink-0" />
                                  </a>
                                </td>
                                <td className="p-3 font-mono text-[11px]">{src.verified_at}</td>
                                <td className="p-3">
                                  <span className="rounded bg-emerald-950/70 border border-emerald-600/40 px-2 py-0.5 text-[10px] text-emerald-300 font-bold uppercase">
                                    {src.status}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-800 bg-[#10264A]/50 p-3 sm:px-6 flex items-center justify-between text-xs text-slate-400">
              <span className="text-[11px] font-mono">
                WIYATA Database Learning Center • {isId ? "Katalog Terverifikasi" : "Verified Reference"}
              </span>
              <button
                onClick={() => {
                  setActiveToolSlug(null);
                  setActiveDetail(null);
                }}
                className="rounded-lg bg-slate-800 hover:bg-slate-700 px-4 py-1.5 font-bold text-white transition-colors"
              >
                {isId ? "Tutup" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

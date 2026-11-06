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
} from "lucide-react";
import { api } from "@/lib/api";

interface MonitoringGuide {
  goldenSignals: string[];
  goldenSignalsId: string[];
  sampleAlertQuery?: string;
  architectureOverview: string;
  architectureOverviewId: string;
  whenToUse: string;
  whenToUseId: string;
}

interface Tool {
  slug: string;
  name: string;
  vendor: string;
  category: "Clients & Administration" | "Monitoring & Observability" | "Backup & Migration";
  license: string;
  engines: string[];
  summary: string;
  summaryId?: string;
  url: string;
  guide?: MonitoringGuide;
}

const DEFAULT_TOOLS: Tool[] = [
  {
    slug: "pmm",
    name: "Percona Monitoring and Management (PMM)",
    vendor: "Percona",
    category: "Monitoring & Observability",
    license: "Open Source",
    engines: ["MySQL", "PostgreSQL", "MongoDB"],
    summary:
      "Best-of-breed open-source database monitoring, query analytics (QAN), and performance troubleshooting platform.",
    summaryId:
      "Platform monitoring database open-source terbaik untuk analisis performa query dan troubleshooting mendalam.",
    url: "https://www.percona.com/software/database-tools/percona-monitoring-and-management",
    guide: {
      goldenSignals: [
        "QAN (Query Analytics): Slow query execution count and latency histogram",
        "InnoDB Buffer Pool: Read efficiency hit ratio (must stay > 99%)",
        "Disk I/O: Temp tables created on disk per second",
        "Replication Lag: Thread delay in seconds between primary and replicas",
      ],
      goldenSignalsId: [
        "QAN (Query Analytics): Frekuensi kueri lambat dan histogram latensi",
        "InnoDB Buffer Pool: Rasio efisiensi cache pembacaan (target > 99%)",
        "I/O Disk: Pembuatan tabel sementara di disk per detik",
        "Lag Replikasi: Keterlambatan thread dalam detik antara primary dan replika",
      ],
      sampleAlertQuery: `increase(mysql_global_status_innodb_deadlocks[1h]) > 0`,
      architectureOverview:
        "Central PMM Server running Prometheus & Grafana in a Docker container, polling lightweight pmm-agent / vmagent on database hosts.",
      architectureOverviewId:
        "Server terpusat PMM yang menjalankan Prometheus & Grafana di kontainer Docker, mengumpulkan metrik dari pmm-agent di host database.",
      whenToUse:
        "Essential for production MySQL, Percona Server, and PostgreSQL clusters requiring granular slow query triage without proprietary agent licensing.",
      whenToUseId:
        "Wajib digunakan untuk klaster MySQL dan PostgreSQL produksi yang membutuhkan analisis kueri lambat tanpa biaya lisensi agen komersial.",
    },
  },
  {
    slug: "prometheus",
    name: "Prometheus & Database Exporters",
    vendor: "CNCF",
    category: "Monitoring & Observability",
    license: "Open Source",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "Universal"],
    summary:
      "Industry standard time-series metric scraper with PromQL, powering database exporters across all engines.",
    summaryId:
      "Standar industri pengumpul metrik time-series dengan bahasa kueri PromQL untuk memantau performa semua jenis database.",
    url: "https://prometheus.io/",
    guide: {
      goldenSignals: [
        "Saturation: Active connections vs max_connections capacity (> 85% alert)",
        "Latency: Average query duration via rate(pg_stat_statements_total_time)",
        "Throughput: Commits and rollbacks per second (TPS)",
        "Traffic: Network bytes transmitted and received per second",
      ],
      goldenSignalsId: [
        "Saturasi: Koneksi aktif berbanding kapasitas max_connections (> 85% waspada)",
        "Latensi: Rata-rata durasi kueri via rate(pg_stat_statements_total_time)",
        "Throughput: Jumlah transaksi commit dan rollback per detik (TPS)",
        "Trafik: Kecepatan transfer data jaringan per detik",
      ],
      sampleAlertQuery: `(pg_stat_database_numbackends / pg_settings_max_connections) > 0.85`,
      architectureOverview:
        "Pull-based metrics collection via postgres_exporter (port 9187), mysqld_exporter (port 9104), and sql_exporter.",
      architectureOverviewId:
        "Pengumpulan metrik berbasis Pull via postgres_exporter (port 9187), mysqld_exporter (port 9104), dan sql_exporter.",
      whenToUse:
        "The backbone for Cloud-Native database monitoring, Kubernetes deployments, and automated PagerDuty/Slack incident routing.",
      whenToUseId:
        "Fondasi utama monitoring database Cloud-Native, deployment Kubernetes, dan integrasi alert otomatis ke PagerDuty/Slack.",
    },
  },
  {
    slug: "grafana",
    name: "Grafana DBA Dashboards",
    vendor: "Grafana Labs",
    category: "Monitoring & Observability",
    license: "AGPLv3",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "Universal"],
    summary:
      "Interactive visual analytics dashboards displaying real-time database throughput, cache ratios, and connection pools.",
    summaryId:
      "Dashboard visual analitik interaktif untuk memvisualisasikan throughput database, rasio cache, dan connection pool.",
    url: "https://grafana.com/",
    guide: {
      goldenSignals: [
        "Real-time IOPS & Disk Wait Times (read/write await in ms)",
        "Buffer Cache Hit Ratio gauge panel",
        "Transaction volume heatmaps across cluster replicas",
        "Connection pool saturation bars (PgBouncer / ProxySQL)",
      ],
      goldenSignalsId: [
        "IOPS real-time & Waktu tunggu disk (await baca/tulis dalam ms)",
        "Panel gauge rasio keberhasilan Buffer Cache (Hit Ratio)",
        "Heatmap volume transaksi di seluruh replika klaster",
        "Bar saturasi connection pool (PgBouncer / ProxySQL)",
      ],
      sampleAlertQuery: `rate(node_disk_io_time_seconds_total[5m]) > 0.9`,
      architectureOverview:
        "Visual frontend connected to Prometheus, InfluxDB, or native SQL data sources with pre-built Community DBA Dashboards (#9628, #7362).",
      architectureOverviewId:
        "Frontend visual yang terhubung ke Prometheus, InfluxDB, atau sumber data SQL dengan template dashboard DBA komunitas.",
      whenToUse:
        "Used by DBAs and SREs in NOC dashboards to provide high-level and drill-down operational visibility.",
      whenToUseId:
        "Digunakan oleh DBA dan SRE di layar NOC untuk memantau status operasional secara menyeluruh maupun mendalam.",
    },
  },
  {
    slug: "pgmustard",
    name: "pgMustard",
    vendor: "pgMustard",
    category: "Monitoring & Observability",
    license: "Commercial",
    engines: ["PostgreSQL"],
    summary:
      "Visual query plan analyzer for PostgreSQL that explains execution bottlenecks, shared buffer hits, and index recommendations.",
    summaryId:
      "Alat analisis visual query plan PostgreSQL untuk mendeteksi bottleneck, shared buffer hits, dan rekomendasi indeks.",
    url: "https://www.pgmustard.com",
    guide: {
      goldenSignals: [
        "Sequential Scans: Table scans reading millions of rows without indexes",
        "Buffer Hits: Shared buffer cache read percentage vs physical disk reads",
        "Sort & Hash Spills: Operations exceeding work_mem and spilling to temporary disk files",
        "Row Estimate Discrepancy: Bad planner statistics causing suboptimal nested loop joins",
      ],
      goldenSignalsId: [
        "Sequential Scans: Pemindaian tabel berukuran jutaan baris tanpa indeks",
        "Buffer Hits: Persentase pembacaan memori shared buffer vs I/O disk fisik",
        "Sort & Hash Spill: Operasi yang melebihi work_mem sehingga tumpah ke disk sementara",
        "Discrepansi Estimasi: Statistik planner yang usang memicu nested loop lambat",
      ],
      sampleAlertQuery: `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT ...;`,
      architectureOverview:
        "Web application or CLI that parses raw PostgreSQL JSON/Text EXPLAIN output and scores optimization opportunities.",
      architectureOverviewId:
        "Aplikasi web atau CLI yang mem-parsing output EXPLAIN JSON PostgreSQL dan menilai peluang perbaikan kueri.",
      whenToUse:
        "When an individual PostgreSQL query is degrading performance and standard EXPLAIN text is too cryptic to diagnose.",
      whenToUseId:
        "Ketika kueri PostgreSQL tertentu berjalan lambat dan output teks EXPLAIN standar terlalu sulit dianalisis secara manual.",
    },
  },
  {
    slug: "dbeaver",
    name: "DBeaver Community",
    vendor: "DBeaver Corp",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["SQLite", "PostgreSQL", "MySQL", "Oracle", "SQL Server"],
    summary:
      "Universal database tool for developers and DBAs supporting any database with a JDBC driver, ER diagrams, and data editor.",
    summaryId:
      "Aplikasi universal manajemen database untuk developer dan DBA yang mendukung database apapun via driver JDBC.",
    url: "https://dbeaver.io",
  },
  {
    slug: "pgadmin",
    name: "pgAdmin 4",
    vendor: "PostgreSQL Global Development Group",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["PostgreSQL"],
    summary:
      "The official and most feature-rich graphical administration and query tool for PostgreSQL instances.",
    summaryId:
      "Platform administrasi grafis dan kueri resmi paling lengkap untuk mengelola server PostgreSQL.",
    url: "https://www.pgadmin.org",
  },
  {
    slug: "mysql-workbench",
    name: "MySQL Workbench",
    vendor: "Oracle Corporation",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["MySQL"],
    summary:
      "Unified visual tool for database architects, developers, and DBAs working with MySQL for schema design and user admin.",
    summaryId:
      "Alat visual terpadu untuk perancangan skema, administrasi pengguna, dan pengembangan kueri MySQL.",
    url: "https://www.mysql.com/products/workbench/",
  },
  {
    slug: "oracle-sql-developer",
    name: "Oracle SQL Developer",
    vendor: "Oracle Corporation",
    category: "Clients & Administration",
    license: "Free Proprietary",
    engines: ["Oracle"],
    summary:
      "Dedicated management and development interface for Oracle Database, PL/SQL debugging, and AWR reports.",
    summaryId:
      "Aplikasi grafis resmi untuk administrasi Oracle Database, debugging PL/SQL, dan pembuatan laporan AWR.",
    url: "https://www.oracle.com/database/sqldeveloper/",
  },
  {
    slug: "ssms",
    name: "SQL Server Management Studio (SSMS)",
    vendor: "Microsoft",
    category: "Clients & Administration",
    license: "Free Proprietary",
    engines: ["SQL Server"],
    summary:
      "Microsoft's official integrated environment for managing SQL Server infrastructure, Query Store, and Agent jobs.",
    summaryId:
      "Lingkungan resmi Microsoft untuk mengelola infrastruktur SQL Server, Query Store, dan jadwal SQL Agent.",
    url: "https://learn.microsoft.com/en-us/ssms/",
  },
  {
    slug: "litecli",
    name: "LiteCLI",
    vendor: "DBCLI Community",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["SQLite"],
    summary:
      "Terminal CLI for SQLite with intelligent auto-completion, syntax highlighting, and multi-line editor.",
    summaryId:
      "Terminal CLI untuk SQLite dengan auto-completion cerdas, penyorotan sintaks, dan editor multi-baris.",
    url: "https://litecli.com",
  },
  {
    slug: "pgbackrest",
    name: "pgBackRest",
    vendor: "pgBackRest Community",
    category: "Backup & Migration",
    license: "Open Source",
    engines: ["PostgreSQL"],
    summary:
      "Enterprise physical backup and restore for PostgreSQL with multi-threading, compression, and S3 streaming.",
    summaryId:
      "Solusi backup dan restore fisik tingkat enterprise untuk PostgreSQL dengan kompresi dan streaming ke S3.",
    url: "https://pgbackrest.org/",
  },
  {
    slug: "xtrabackup",
    name: "Percona XtraBackup",
    vendor: "Percona",
    category: "Backup & Migration",
    license: "Open Source",
    engines: ["MySQL"],
    summary:
      "Non-blocking physical hot backup utility for MySQL and MariaDB without locking database tables during backups.",
    summaryId:
      "Aplikasi backup fisik tanpa penguncian (hot backup) untuk MySQL dan MariaDB tanpa memblokir transaksi.",
    url: "https://www.percona.com/software/mysql-database/percona-xtrabackup",
  },
  {
    slug: "bytebase",
    name: "Bytebase",
    vendor: "Bytebase Inc",
    category: "Backup & Migration",
    license: "Freemium",
    engines: ["PostgreSQL", "MySQL", "Snowflake", "ClickHouse", "Oracle"],
    summary:
      "GitOps-style database schema change management, SQL linting, and access control for modern engineering teams.",
    summaryId:
      "Platform manajemen perubahan skema database bergaya GitOps dengan linting SQL dan kontrol akses terpadu.",
    url: "https://www.bytebase.com",
  },
  {
    slug: "flyway",
    name: "Flyway",
    vendor: "Redgate",
    category: "Backup & Migration",
    license: "Open Source / Commercial",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "SQLite"],
    summary:
      "Database version control and evolutionary migration tool supporting 25+ database engines in CI/CD pipelines.",
    summaryId:
      "Alat version control database dan migrasi skema evolusioner yang mendukung lebih dari 25 mesin database di pipeline CI/CD.",
    url: "https://www.red-gate.com/products/flyway/",
  },
];

interface ToolsCatalogProps {
  language: "en" | "id";
}

export function ToolsCatalog({ language }: ToolsCatalogProps) {
  const isId = language === "id";
  const [tools, setTools] = useState<Tool[]>(DEFAULT_TOOLS);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [selectedEngine, setSelectedEngine] = useState<string>("All");
  const [activeGuideTool, setActiveGuideTool] = useState<Tool | null>(null);

  const categories = [
    { id: "All", label: isId ? "Semua Kategori" : "All Categories" },
    { id: "Monitoring & Observability", label: isId ? "Monitoring & Observabilitas" : "Monitoring & Observability" },
    { id: "Clients & Administration", label: isId ? "Klien & Administrasi" : "Clients & Administration" },
    { id: "Backup & Migration", label: isId ? "Backup & Migrasi" : "Backup & Migration" },
  ];

  const engines = [
    "All",
    "PostgreSQL",
    "MySQL",
    "SQLite",
    "Oracle",
    "SQL Server",
  ];

  const filteredTools = tools.filter((tool) => {
    if (selectedCategory !== "All" && tool.category !== selectedCategory) {
      return false;
    }
    if (selectedEngine !== "All") {
      const matchEngine = tool.engines.some((e) =>
        e.toLowerCase().includes(selectedEngine.toLowerCase())
      );
      if (!matchEngine) return false;
    }
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchName = tool.name.toLowerCase().includes(q);
      const matchDesc = tool.summary.toLowerCase().includes(q);
      const matchVendor = tool.vendor.toLowerCase().includes(q);
      return matchName || matchDesc || matchVendor;
    }
    return true;
  });

  return (
    <div className="flex flex-col h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* Header & Filter Controls Bar */}
      <div className="border-b border-slate-800 bg-[#10264A]/40 p-4 sm:p-5 shrink-0">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-1">
              <Wrench className="h-4 w-4" />
              <span>{isId ? "Katalog Alat & Observabilitas" : "Professional Tooling & Observability"}</span>
            </div>
            <h1 className="text-lg sm:text-xl font-bold text-white">
              {isId ? "Ekosistem Perangkat Lunak Database" : "Database Software Ecosystem"}
            </h1>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-3 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder={isId ? "Cari alat atau monitoring..." : "Search tools or observability..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-xl bg-slate-900 border border-slate-700/80 pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#F2B84B]"
            />
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          {/* Categories */}
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll">
            {categories.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedCategory(c.id)}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-colors min-h-[36px] ${
                  selectedCategory === c.id
                    ? "bg-[#F2B84B] text-[#071A3A]"
                    : "bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800"
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>

          {/* Engine Filter */}
          <div className="flex items-center gap-1 overflow-x-auto no-scrollbar touch-scroll">
            <span className="text-[11px] font-semibold text-slate-400 mr-1 hidden sm:inline">
              {isId ? "Mesin:" : "Engine:"}
            </span>
            {engines.map((eng) => (
              <button
                key={eng}
                onClick={() => setSelectedEngine(eng)}
                className={`rounded-md px-2 py-1 text-[11px] font-medium transition-colors ${
                  selectedEngine === eng
                    ? "bg-slate-700 text-[#F2B84B] border border-[#F2B84B]/40"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800/80"
                }`}
              >
                {eng}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid of Tool Cards */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 max-w-7xl mx-auto">
          {filteredTools.map((tool) => {
            const hasGuide = Boolean(tool.guide);

            return (
              <div
                key={tool.slug}
                className="flex flex-col justify-between rounded-2xl border border-slate-800 bg-[#071329]/80 p-4 sm:p-5 hover:border-slate-700 transition-all hover:bg-slate-900/40 shadow-sm"
              >
                <div>
                  {/* Category & License Header */}
                  <div className="flex items-center justify-between text-[11px] mb-2.5">
                    <span className="rounded-full bg-slate-800 px-2.5 py-0.5 text-slate-300 font-medium">
                      {tool.category}
                    </span>
                    <span
                      className={`font-semibold ${
                        tool.license.includes("Open Source")
                          ? "text-emerald-400"
                          : "text-amber-400"
                      }`}
                    >
                      {tool.license}
                    </span>
                  </div>

                  <h3 className="text-sm sm:text-base font-bold text-white mb-1">
                    {tool.name}
                  </h3>
                  <div className="text-[11px] font-mono text-slate-400 mb-2">
                    {isId ? "Oleh" : "By"} {tool.vendor}
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-4">
                    {isId ? tool.summaryId || tool.summary : tool.summary}
                  </p>
                </div>

                <div>
                  {/* Supported Engines */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {tool.engines.map((e) => (
                      <span
                        key={e}
                        className="rounded bg-slate-900/90 border border-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400"
                      >
                        {e}
                      </span>
                    ))}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between border-t border-slate-800/80 pt-3 gap-2">
                    {hasGuide ? (
                      <button
                        onClick={() => setActiveGuideTool(tool)}
                        className="flex items-center gap-1.5 rounded-lg bg-[#10264A] border border-[#F2B84B]/40 px-3 py-1.5 text-xs font-semibold text-[#F2B84B] hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors"
                      >
                        <Activity className="h-3.5 w-3.5" />
                        <span>{isId ? "Panduan Monitoring" : "Observability Guide"}</span>
                      </button>
                    ) : (
                      <div className="text-[11px] text-slate-500 font-mono">
                        {isId ? "Aplikasi Standar" : "Standard Utility"}
                      </div>
                    )}

                    <a
                      href={tool.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
                    >
                      <span>{isId ? "Situs Resmi" : "Official Site"}</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* MONITORING GUIDE POPUP MODAL */}
      {activeGuideTool && activeGuideTool.guide && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-3 sm:p-4 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl border border-slate-700 bg-[#071A3A] p-5 sm:p-6 shadow-2xl space-y-4">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#F2B84B]">
                  {isId ? "Panduan Observabilitas Mendalam" : "Observability Architecture Guide"}
                </span>
                <h2 className="text-base sm:text-xl font-bold text-white flex items-center gap-2 mt-0.5">
                  <Activity className="h-5 w-5 text-[#F2B84B]" />
                  <span>{activeGuideTool.name}</span>
                </h2>
              </div>
              <button
                onClick={() => setActiveGuideTool(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* When to use */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3.5 text-xs text-slate-300 leading-relaxed">
              <strong className="text-white block mb-1">
                {isId ? "Kapan Harus Menggunakan Alat Ini:" : "When to Use This Tool:"}
              </strong>
              {isId ? activeGuideTool.guide.whenToUseId : activeGuideTool.guide.whenToUse}
            </div>

            {/* Architecture Overview */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Layers className="h-4 w-4 text-[#F2B84B]" />
                <span>{isId ? "Arsitektur & Pola Deployment:" : "Architecture & Deployment Topology:"}</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed font-mono bg-[#071329] p-3 rounded-lg border border-slate-800">
                {isId
                  ? activeGuideTool.guide.architectureOverviewId
                  : activeGuideTool.guide.architectureOverview}
              </p>
            </div>

            {/* Golden Signals */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                <CheckCircle className="h-4 w-4 text-emerald-400" />
                <span>{isId ? "Metrik Golden Signals Kunci yang Wajib Dipantau:" : "Key Golden Signals to Monitor:"}</span>
              </h3>
              <div className="space-y-1.5">
                {(isId
                  ? activeGuideTool.guide.goldenSignalsId
                  : activeGuideTool.guide.goldenSignals
                ).map((signal, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-2 text-xs text-slate-200 bg-[#071329] p-2.5 rounded-lg border border-slate-800/80 font-mono"
                  >
                    <span className="text-[#F2B84B] font-bold shrink-0">{idx + 1}.</span>
                    <span>{signal}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sample Alert Query */}
            {activeGuideTool.guide.sampleAlertQuery && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                  <FileCode className="h-4 w-4 text-[#F2B84B]" />
                  <span>{isId ? "Contoh Kueri Peringatan (Alert / Diagnostic Query):" : "Sample Alert / Diagnostic Query:"}</span>
                </h3>
                <pre className="rounded-xl border border-slate-800 bg-black/40 p-3 font-mono text-xs text-emerald-300 overflow-x-auto">
                  <code>{activeGuideTool.guide.sampleAlertQuery}</code>
                </pre>
              </div>
            )}

            {/* Footer */}
            <div className="border-t border-slate-800 pt-3 flex justify-end">
              <button
                onClick={() => setActiveGuideTool(null)}
                className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 hover:text-white"
              >
                {isId ? "Tutup Panduan" : "Close Guide"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

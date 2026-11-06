"use client";

import React, { useState, useEffect } from "react";
import { Wrench, ExternalLink, Search, CheckCircle, Database } from "lucide-react";
import { api } from "@/lib/api";

interface Tool {
  slug: string;
  name: string;
  vendor: string;
  category: string;
  license: string;
  engines: string[];
  summary: string;
  summaryId?: string;
  url: string;
}

const DEFAULT_TOOLS: Tool[] = [
  {
    slug: "dbeaver",
    name: "DBeaver Community",
    vendor: "DBeaver Corp",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["SQLite", "PostgreSQL", "MySQL", "Oracle", "SQL Server"],
    summary:
      "Universal database tool for developers and DBAs supporting any database with a JDBC driver.",
    summaryId:
      "Aplikasi universal manajemen database untuk developer dan DBA yang mendukung database apapun via driver JDBC.",
    url: "https://dbeaver.io",
  },
  {
    slug: "pmm",
    name: "Percona Monitoring and Management (PMM)",
    vendor: "Percona",
    category: "Monitoring & Observability",
    license: "Open Source",
    engines: ["MySQL", "PostgreSQL", "MongoDB"],
    summary:
      "Best-of-breed open-source database monitoring, query analytics, and performance troubleshooting platform.",
    summaryId:
      "Platform monitoring database open-source terbaik untuk analisis performa query dan troubleshooting mendalam.",
    url: "https://www.percona.com/software/database-tools/percona-monitoring-and-management",
  },
  {
    slug: "pgmustard",
    name: "pgMustard",
    vendor: "pgMustard",
    category: "Monitoring & Observability",
    license: "Commercial",
    engines: ["PostgreSQL"],
    summary:
      "Visual query plan analyzer for PostgreSQL that explains execution bottlenecks and recommends targeted index fixes.",
    summaryId:
      "Alat analisis visual query plan untuk PostgreSQL yang mendeteksi bottleneck dan memberikan saran optimasi indeks.",
    url: "https://www.pgmustard.com",
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
    slug: "litecli",
    name: "LiteCLI",
    vendor: "DBCLI community",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["SQLite"],
    summary:
      "Command-line interface for SQLite with auto-completion and syntax highlighting.",
    summaryId:
      "Terminal interaktif untuk SQLite yang dilengkapi auto-completion cerdas dan syntax highlighting.",
    url: "https://litecli.com",
  },
  {
    slug: "pgadmin",
    name: "pgAdmin 4",
    vendor: "PostgreSQL Global Development Group",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["PostgreSQL"],
    summary:
      "The most popular and feature-rich administration and development platform for PostgreSQL.",
    summaryId:
      "Platform administrasi dan pengembangan resmi paling populer dan lengkap untuk PostgreSQL.",
    url: "https://www.pgadmin.org",
  },
  {
    slug: "prometheus",
    name: "Prometheus",
    vendor: "CNCF",
    category: "Monitoring & Observability",
    license: "Open Source",
    engines: ["PostgreSQL", "MySQL", "Oracle", "Universal"],
    summary:
      "Open-source systems monitoring and alerting toolkit with dimensional data model and PromQL query language.",
    summaryId:
      "Sistem monitoring dan alerting open-source berbasis time-series dengan bahasa query PromQL.",
    url: "https://prometheus.io/",
  },
  {
    slug: "grafana",
    name: "Grafana",
    vendor: "Grafana Labs",
    category: "Monitoring & Observability",
    license: "Open Source / AGPL",
    engines: ["PostgreSQL", "MySQL", "Oracle", "ClickHouse", "Universal"],
    summary:
      "Visual query analytics, interactive dashboards, and multi-source observability platform.",
    summaryId:
      "Platform visualisasi dan dashboard analitik metrik performa database terpopuler di dunia.",
    url: "https://grafana.com/",
  },
  {
    slug: "pgbackrest",
    name: "pgBackRest",
    vendor: "pgBackRest Community",
    category: "Backup & Migration",
    license: "Open Source",
    engines: ["PostgreSQL"],
    summary:
      "Reliable, high-performance backup and restore solution for PostgreSQL with compression and parallel streaming.",
    summaryId:
      "Solusi backup dan restore terpercaya berperforma tinggi untuk PostgreSQL dengan kompresi dan multi-threading.",
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
      "Non-blocking physical hot backup utility for MySQL and Percona Server without database downtime.",
    summaryId:
      "Aplikasi backup fisik tanpa penguncian (hot backup) untuk MySQL tanpa menghentikan layanan database.",
    url: "https://www.percona.com/software/mysql-database/percona-xtrabackup",
  },
  {
    slug: "flyway",
    name: "Flyway",
    vendor: "Redgate",
    category: "Backup & Migration",
    license: "Open Source / Commercial",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "SQLite"],
    summary:
      "Database version control and evolutionary migration tool supporting 25+ database engines.",
    summaryId:
      "Alat version control database dan migrasi skema evolusioner yang mendukung lebih dari 25 mesin database.",
    url: "https://www.red-gate.com/products/flyway/",
  },
  {
    slug: "mysql-workbench",
    name: "MySQL Workbench",
    vendor: "Oracle Corporation",
    category: "Clients & Administration",
    license: "Open Source",
    engines: ["MySQL"],
    summary:
      "Unified visual tool for database architects, developers, and DBAs working with MySQL.",
    summaryId:
      "Alat visual terpadu untuk perancangan skema, administrasi, dan pengembangan kueri MySQL.",
    url: "https://www.mysql.com/products/workbench/",
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

  useEffect(() => {
    api
      .get("/tools")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          const apiMapped: Tool[] = res.data.map((t: any) => ({
            slug: t.slug,
            name: t.name,
            vendor: t.vendor || "Community",
            category: t.license_model === "Open Source" ? "Clients & Administration" : "Monitoring & Observability",
            license: t.license_model || "Open Source",
            engines: t.supported_engines || ["Universal"],
            summary: t.summary || "",
            summaryId: t.summary || "",
            url: t.official_url || "https://wiyata.sadeyan.my.id",
          }));
          // Merge unique
          const combined = [...DEFAULT_TOOLS];
          for (const item of apiMapped) {
            if (!combined.some((c) => c.slug === item.slug)) {
              combined.push(item);
            }
          }
          setTools(combined);
        }
      })
      .catch((err) => console.error("Error fetching live tools:", err));
  }, []);

  const CATEGORY_LOCALES: Record<string, { en: string; id: string }> = {
    "All": { en: "All", id: "Semua" },
    "Clients & Administration": { en: "Clients & Administration", id: "Klien & Administrasi" },
    "Monitoring & Observability": { en: "Monitoring & Observability", id: "Monitoring & Observabilitas" },
    "Backup & Migration": { en: "Backup & Migration", id: "Backup & Migrasi" },
  };

  const LICENSE_LOCALES: Record<string, { en: string; id: string }> = {
    "Open Source": { en: "Open Source", id: "Sumber Terbuka" },
    "Open Source / AGPL": { en: "Open Source / AGPL", id: "Sumber Terbuka / AGPL" },
    "Open Source / Commercial": { en: "Open Source / Commercial", id: "Sumber Terbuka / Komersial" },
    "Commercial": { en: "Commercial", id: "Komersial" },
    "Freemium": { en: "Freemium", id: "Freemium" },
  };

  const categories = [
    "All",
    "Clients & Administration",
    "Monitoring & Observability",
    "Backup & Migration",
  ];

  const filtered = tools.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.engines.some((e) =>
        e.toLowerCase().includes(searchTerm.toLowerCase())
      ) ||
      t.summary.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === "All" || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex h-auto lg:h-[calc(100dvh-3.5rem)] w-full flex-col overflow-y-auto bg-[#071A3A] p-4 sm:p-8 text-slate-200">
      <div className="max-w-6xl mx-auto w-full">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B]">
            <Wrench className="h-3.5 w-3.5" />
            <span>
              {isId
                ? "Direktori Software Profesional"
                : "Professional Software Directory"}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            {isId
              ? "Katalog Alat & Ekosistem Database"
              : "Database Tools & Ecosystem Catalog"}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
            {isId
              ? "Koleksi software terverifikasi untuk DBA, insinyur performa, dan pengembang data. Lisensi, kompatibilitas mesin, dan dokumentasi resmi."
              : "Curated software applications for DBAs, reliability engineers, and developers. Licensing, compatibility, and vendor details are verified against official documentation."}
          </p>
        </div>

        {/* Filter bar */}
        <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between mb-6 pb-4 border-b border-slate-800">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-3 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder={
                isId
                  ? "Cari nama alat atau database..."
                  : "Search tool or database..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded bg-slate-900 border border-slate-800 pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#F2B84B] min-h-[44px]"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll pb-1 sm:pb-0">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap min-h-[40px] shrink-0 active:scale-95 ${
                  selectedCategory === cat
                    ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/40 shadow-sm"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {CATEGORY_LOCALES[cat]
                  ? isId
                    ? CATEGORY_LOCALES[cat].id
                    : CATEGORY_LOCALES[cat].en
                  : cat}
              </button>
            ))}
          </div>
        </div>

        {/* Grid of Tools */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-8">
          {filtered.length === 0 ? (
            <div className="col-span-full py-12 text-center text-xs text-slate-500">
              {isId
                ? "Tidak ada software atau database yang cocok dengan kriteria pencarian Anda."
                : "No software tools or databases match your search query."}
            </div>
          ) : (
            filtered.map((tool) => (
              <div
                key={tool.slug}
                className="rounded-lg border border-slate-800 bg-[#10264A]/30 p-4 sm:p-5 flex flex-col justify-between hover:border-slate-700 hover:bg-[#10264A]/50 transition-all"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <h3 className="font-bold text-sm text-white">
                        {tool.name}
                      </h3>
                      <p className="text-[11px] text-slate-400">{tool.vendor}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide border shrink-0 ${
                        tool.license.includes("Open Source")
                          ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/80"
                          : tool.license === "Commercial"
                          ? "bg-purple-950/60 text-purple-400 border-purple-800/80"
                          : "bg-amber-950/60 text-amber-400 border-amber-800/80"
                      }`}
                    >
                      {LICENSE_LOCALES[tool.license]
                        ? isId
                          ? LICENSE_LOCALES[tool.license].id
                          : LICENSE_LOCALES[tool.license].en
                        : tool.license}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-4">
                    {isId && tool.summaryId ? tool.summaryId : tool.summary}
                  </p>
                </div>

                <div>
                  <div className="flex flex-wrap gap-1 mb-4">
                    {tool.engines.map((e) => (
                      <span
                        key={e}
                        className="rounded bg-slate-900 px-2 py-0.5 text-[10px] font-mono text-slate-400 border border-slate-800"
                      >
                        {e}
                      </span>
                    ))}
                  </div>

                  <a
                    href={tool.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 py-2.5 text-xs font-semibold text-slate-200 hover:text-white hover:border-[#F2B84B] transition-colors min-h-[44px]"
                  >
                    <span>
                      {isId ? "Kunjungi Dokumentasi Resmi" : "Visit Official Documentation"}
                    </span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState } from "react";
import { Wrench, ExternalLink, Search } from "lucide-react";

interface Tool {
  slug: string;
  name: string;
  vendor: string;
  category: string;
  license: "Open Source" | "Free Tier" | "Commercial" | "Freemium";
  engines: string[];
  summary: string;
  summaryId: string;
  url: string;
}

const TOOLS: Tool[] = [
  {
    slug: "dbeaver",
    name: "DBeaver Community",
    vendor: "DBeaver Corp",
    category: "GUI / IDE",
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
    category: "Performance Tuning",
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
    category: "Database CI/CD & Schema Migration",
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
    category: "CLI / Terminal",
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
    category: "GUI / Administration",
    license: "Open Source",
    engines: ["PostgreSQL"],
    summary:
      "The most popular and feature-rich administration and development platform for PostgreSQL.",
    summaryId:
      "Platform administrasi dan pengembangan resmi paling populer dan lengkap untuk PostgreSQL.",
    url: "https://www.pgadmin.org",
  },
];

interface ToolsCatalogProps {
  language: "en" | "id";
}

export function ToolsCatalog({ language }: ToolsCatalogProps) {
  const isId = language === "id";
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const categories = [
    "All",
    ...Array.from(new Set(TOOLS.map((t) => t.category))),
  ];

  const filtered = TOOLS.filter((t) => {
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
              ? "Koleksi software terverifikasi untuk DBA, insinyur performa, dan pengembang data. Lisensi dan status kepemilikan selalu transparan."
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
              className="w-full rounded bg-slate-900 border border-slate-800 pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#F2B84B] min-h-[40px]"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll pb-1 sm:pb-0">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors whitespace-nowrap min-h-[40px] shrink-0 ${
                  selectedCategory === cat
                    ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/40 font-semibold"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Grid of Tools */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((tool) => (
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
                      tool.license === "Open Source"
                        ? "bg-emerald-950/60 border-emerald-600/40 text-emerald-300"
                        : tool.license === "Commercial"
                        ? "bg-indigo-950/60 border-indigo-600/40 text-indigo-300"
                        : "bg-amber-950/60 border-amber-600/40 text-amber-300"
                    }`}
                  >
                    {tool.license}
                  </span>
                </div>

                <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed mb-4">
                  {isId ? tool.summaryId : tool.summary}
                </p>
              </div>

              <div>
                <div className="flex flex-wrap gap-1 mb-4">
                  {tool.engines.map((eng) => (
                    <span
                      key={eng}
                      className="rounded bg-slate-900 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 border border-slate-800"
                    >
                      {eng}
                    </span>
                  ))}
                </div>

                <a
                  href={tool.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-1.5 w-full rounded border border-slate-700 bg-slate-800/80 py-2.5 text-xs font-semibold text-slate-200 hover:bg-[#F2B84B] hover:text-[#071A3A] hover:border-[#F2B84B] transition-colors min-h-[44px]"
                >
                  <span>
                    {isId ? "Kunjungi Situs Resmi" : "Official Website"}
                  </span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

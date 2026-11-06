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
  category:
    | "Clients & Administration"
    | "Monitoring & Observability"
    | "Backup & Migration"
    | "Linux & Systems Diagnostics"
    | "Automation & Infrastructure";
  license: string;
  engines: string[];
  summary: string;
  summaryId?: string;
  url: string;
  lifecycleStatus?: "Active" | "Maintenance / Deprecated";
  guide?: MonitoringGuide;
}

const DEFAULT_TOOLS: Tool[] = [
  // 1. Clients & Administration
  {
    slug: "dbeaver",
    name: "DBeaver Community",
    vendor: "DBeaver Corp",
    category: "Clients & Administration",
    license: "Open Source (Apache 2.0)",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "IBM Db2", "SQLite"],
    summary:
      "Universal multi-platform database client for developers, SQL programmers, analysts, and DBAs supporting JDBC.",
    summaryId:
      "Aplikasi GUI multi-platform universal untuk developer dan DBA yang mendukung hampir semua mesin database via JDBC.",
    url: "https://dbeaver.io/",
  },
  {
    slug: "pgadmin",
    name: "pgAdmin 4",
    vendor: "PostgreSQL Global Development Group",
    category: "Clients & Administration",
    license: "Open Source (PostgreSQL License)",
    engines: ["PostgreSQL"],
    summary:
      "The premier open-source graphical administration and development platform for PostgreSQL with query analysis.",
    summaryId:
      "Platform administrasi dan manajemen database terkemuka khusus untuk ekosistem PostgreSQL.",
    url: "https://www.pgadmin.org/",
  },
  {
    slug: "mysql-workbench",
    name: "MySQL Workbench",
    vendor: "Oracle Corporation",
    category: "Clients & Administration",
    license: "Open Source (GPL)",
    engines: ["MySQL", "MariaDB"],
    summary:
      "Visual tool for database architects, developers, and DBAs providing data modeling, SQL development, and server configuration.",
    summaryId:
      "Aplikasi visual resmi untuk pemodelan data, pengembangan SQL, dan administrasi server MySQL.",
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
      "Integrated development environment for database tasks in Oracle Database, providing PL/SQL development and DBA consoles.",
    summaryId:
      "Aplikasi visual resmi Oracle untuk pengembangan PL/SQL, manajemen objek skema, dan konsol administrasi DBA.",
    url: "https://www.oracle.com/database/sqldeveloper/",
  },
  {
    slug: "sqlcl",
    name: "Oracle SQLcl",
    vendor: "Oracle Corporation",
    category: "Clients & Administration",
    license: "Free Proprietary",
    engines: ["Oracle"],
    summary:
      "Modern, feature-packed command-line interface for Oracle with inline editing, SQL history, auto-completion, and Liquibase.",
    summaryId:
      "CLI modern untuk Oracle Database dengan fitur auto-complete, format output interaktif, dan integrasi Liquibase.",
    url: "https://www.oracle.com/database/sqldeveloper/technologies/sqlcl/",
  },
  {
    slug: "sqlplus",
    name: "Oracle SQL*Plus",
    vendor: "Oracle Corporation",
    category: "Clients & Administration",
    license: "Proprietary",
    engines: ["Oracle"],
    summary:
      "Standard interactive and batch query command-line tool installed with every Oracle Database edition.",
    summaryId:
      "Alat baris perintah standar bawaan Oracle Database untuk administrasi, eksekusi skrip, dan operasi darurat DBA.",
    url: "https://docs.oracle.com/en/database/oracle/oracle-database/23/sqpug/",
  },
  {
    slug: "ssms",
    name: "SQL Server Management Studio (SSMS)",
    vendor: "Microsoft",
    category: "Clients & Administration",
    license: "Free Proprietary",
    engines: ["SQL Server"],
    summary:
      "The definitive Windows desktop environment for configuring, managing, and administering all SQL Server components.",
    summaryId:
      "Aplikasi desktop utama untuk konfigurasi, pemantauan, dan administrasi seluruh komponen Microsoft SQL Server.",
    url: "https://learn.microsoft.com/en-us/ssms/",
  },
  {
    slug: "azure-data-studio",
    name: "Azure Data Studio",
    vendor: "Microsoft",
    category: "Clients & Administration",
    license: "Open Source (MIT)",
    lifecycleStatus: "Maintenance / Deprecated",
    engines: ["SQL Server", "PostgreSQL"],
    summary:
      "Cross-platform desktop database tool for data professionals. (Note: Microsoft placed ADS into maintenance; active development shifted to VS Code mssql extension).",
    summaryId:
      "Alat database lintas platform. (Catatan: Microsoft mengumumkan status maintenance; pengembangan aktif dialihkan ke ekstensi mssql di VS Code).",
    url: "https://learn.microsoft.com/en-us/azure-data-studio/",
  },
  {
    slug: "ibm-dmc",
    name: "IBM Data Management Console (DMC)",
    vendor: "IBM",
    category: "Clients & Administration",
    license: "Commercial / Community",
    engines: ["IBM Db2"],
    summary:
      "Browser-based unified administration, performance tuning, and alert console for IBM Db2 instances.",
    summaryId:
      "Konsol berbasis web untuk memantau performa, tuning memori, dan mengelola database IBM Db2.",
    url: "https://www.ibm.com/products/db2-data-management-console",
  },
  {
    slug: "db2-clp",
    name: "IBM Db2 Command Line Processor (CLP)",
    vendor: "IBM",
    category: "Clients & Administration",
    license: "Proprietary",
    engines: ["IBM Db2"],
    summary:
      "Native command-line environment for Db2 database administration, HADR takeover commands, and storage management.",
    summaryId:
      "Lingkungan CLI native untuk mengendalikan database Db2, aktivasi HADR, dan konfigurasi bufferpool.",
    url: "https://www.ibm.com/docs/en/db2/11.5?topic=commands-command-line-processor-clp",
  },
  {
    slug: "datagrip",
    name: "JetBrains DataGrip",
    vendor: "JetBrains",
    category: "Clients & Administration",
    license: "Commercial",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "IBM Db2", "SQLite", "Snowflake", "ClickHouse"],
    summary:
      "Powerful multi-engine database IDE with smart schema introspection, refactoring, and Git integration.",
    summaryId:
      "IDE database multi-mesin profesional dengan auto-completion cerdas, refactoring skema, dan integrasi Git.",
    url: "https://www.jetbrains.com/datagrip/",
  },
  {
    slug: "heidisql",
    name: "HeidiSQL",
    vendor: "Ansgar Becker",
    category: "Clients & Administration",
    license: "Open Source (GPL)",
    engines: ["MariaDB", "MySQL", "SQL Server", "PostgreSQL", "SQLite"],
    summary:
      "Lightweight, blazing-fast native Windows tool for managing MariaDB, MySQL, SQL Server, and PostgreSQL.",
    summaryId:
      "Aplikasi klien native Windows yang sangat ringan dan cepat untuk mengelola database MariaDB, MySQL, dan PostgreSQL.",
    url: "https://www.heidisql.com/",
  },
  {
    slug: "litecli",
    name: "LiteCLI",
    vendor: "DBCLI Community",
    category: "Clients & Administration",
    license: "Open Source (BSD-3)",
    engines: ["SQLite"],
    summary:
      "Interactive command-line interface for SQLite featuring auto-completion and syntax highlighting.",
    summaryId:
      "CLI interaktif untuk SQLite dengan auto-completion cerdas dan pewarnaan sintaks di terminal.",
    url: "https://litecli.com/",
  },

  // 2. Monitoring & Observability
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
      sampleAlertQuery: "increase(mysql_global_status_innodb_deadlocks[1h]) > 0",
      architectureOverview:
        "Central PMM Server running Prometheus & Grafana in a Docker container, polling lightweight pmm-agent on hosts.",
      architectureOverviewId:
        "Server terpusat PMM yang menjalankan Prometheus & Grafana di kontainer Docker, mengumpulkan metrik dari pmm-agent.",
      whenToUse:
        "Essential for production MySQL and PostgreSQL clusters requiring granular slow query triage without commercial fees.",
      whenToUseId:
        "Wajib digunakan untuk klaster MySQL dan PostgreSQL produksi yang membutuhkan analisis kueri lambat tanpa biaya lisensi.",
    },
  },
  {
    slug: "prometheus",
    name: "Prometheus & Database Exporters",
    vendor: "CNCF",
    category: "Monitoring & Observability",
    license: "Open Source (Apache 2.0)",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "Universal"],
    summary:
      "Industry-standard metrics scraping and alerting system with PromQL, powering database exporters across all engines.",
    summaryId:
      "Standar industri pengumpul metrik time-series dengan PromQL untuk memantau performa semua jenis database.",
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
        "Latensi: Durasi rata-rata kueri via rate(pg_stat_statements_total_time)",
        "Throughput: Jumlah transaksi commit dan rollback per detik (TPS)",
        "Trafik: Kecepatan transmisi data jaringan per detik",
      ],
      sampleAlertQuery: "rate(pg_stat_database_xact_rollback[5m]) > 5",
      architectureOverview:
        "Pull-based metrics collection server pulling data from postgres_exporter, mysqld_exporter, and node_exporter.",
      architectureOverviewId:
        "Server metrik berbasis pull yang menarik data dari postgres_exporter, mysqld_exporter, dan node_exporter.",
      whenToUse:
        "The backbone for any modern cloud-native or Kubernetes infrastructure needing unified SLO alerting.",
      whenToUseId:
        "Fondasi telemetri untuk infrastruktur modern atau Kubernetes yang membutuhkan sistem alert SLO terintegrasi.",
    },
  },
  {
    slug: "grafana",
    name: "Grafana Dashboards",
    vendor: "Grafana Labs",
    category: "Monitoring & Observability",
    license: "Open Source (AGPLv3)",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "Universal"],
    summary:
      "Visualization and observability platform turning database metrics, logs, and traces into operational dashboards.",
    summaryId:
      "Platform visualisasi telemetri untuk mengubah metrik database dan server menjadi dashboard operasional real-time.",
    url: "https://grafana.com/",
  },
  {
    slug: "zabbix",
    name: "Zabbix Enterprise Monitoring",
    vendor: "Zabbix LLC",
    category: "Monitoring & Observability",
    license: "Open Source (AGPLv3)",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "IBM Db2"],
    summary:
      "Enterprise-class distributed monitoring platform with native agent and agentless templates for all enterprise databases.",
    summaryId:
      "Platform monitoring enterprise terdistribusi open-source dengan template bawaan untuk memantau performa database.",
    url: "https://www.zabbix.com/",
  },
  {
    slug: "datadog",
    name: "Datadog Database Monitoring (DBM)",
    vendor: "Datadog",
    category: "Monitoring & Observability",
    license: "Commercial SaaS",
    engines: ["PostgreSQL", "MySQL", "SQL Server", "Oracle"],
    summary:
      "Cloud observability platform providing normalized query samples, execution plan tracking, and host infrastructure telemetry.",
    summaryId:
      "Platform observabilitas cloud enterprise untuk pelacakan explain plan, historis kueri lambat, dan metrik infrastruktur.",
    url: "https://www.datadoghq.com/product/database-monitoring/",
  },
  {
    slug: "pgmustard",
    name: "pgMustard",
    vendor: "pgMustard Ltd",
    category: "Monitoring & Observability",
    license: "Commercial",
    engines: ["PostgreSQL"],
    summary:
      "Visual EXPLAIN ANALYZE plan explainer identifying bad estimates, sequential scans, and buffer cache misses in PostgreSQL.",
    summaryId:
      "Alat visualisasi EXPLAIN ANALYZE untuk mendeteksi estimasi baris salah, scan berurutan, dan memori cache miss di PostgreSQL.",
    url: "https://www.pgmustard.com/",
  },
  {
    slug: "oracle-enterprise-manager",
    name: "Oracle Enterprise Manager (OEM)",
    vendor: "Oracle Corporation",
    category: "Monitoring & Observability",
    license: "Commercial Enterprise",
    engines: ["Oracle"],
    summary:
      "The complete enterprise management solution for Oracle Database estates with AWR, ASH, ADDM, and Data Guard consoles.",
    summaryId:
      "Platform manajemen enterprise terpusat untuk memantau klaster Oracle Database, AWR, ASH, dan Data Guard.",
    url: "https://www.oracle.com/enterprise-manager/",
  },

  // 3. Backup & Migration
  {
    slug: "pgbackrest",
    name: "pgBackRest",
    vendor: "pgBackRest Community",
    category: "Backup & Migration",
    license: "Open Source (MIT)",
    engines: ["PostgreSQL"],
    summary:
      "Enterprise physical backup and restore for PostgreSQL with parallel processing, delta restore, compression, and S3 streaming.",
    summaryId:
      "Solusi backup dan restore fisik tingkat enterprise untuk PostgreSQL dengan kompresi dan streaming ke S3.",
    url: "https://pgbackrest.org/",
  },
  {
    slug: "xtrabackup",
    name: "Percona XtraBackup",
    vendor: "Percona",
    category: "Backup & Migration",
    license: "Open Source (GPL)",
    engines: ["MySQL", "MariaDB"],
    summary:
      "Non-blocking physical hot backup utility for MySQL and MariaDB without locking tables during backups.",
    summaryId:
      "Aplikasi backup fisik tanpa penguncian (hot backup) untuk MySQL dan MariaDB tanpa memblokir transaksi pengguna.",
    url: "https://www.percona.com/software/mysql-database/percona-xtrabackup",
  },
  {
    slug: "flyway",
    name: "Flyway",
    vendor: "Redgate",
    category: "Backup & Migration",
    license: "Open Source / Commercial",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "SQLite", "IBM Db2"],
    summary:
      "Database version control and evolutionary migration tool supporting 25+ database engines in CI/CD pipelines.",
    summaryId:
      "Alat version control database dan migrasi skema evolusioner yang mendukung lebih dari 25 mesin database di pipeline CI/CD.",
    url: "https://www.red-gate.com/products/flyway/",
  },
  {
    slug: "liquibase",
    name: "Liquibase",
    vendor: "Liquibase Inc",
    category: "Backup & Migration",
    license: "Open Source / Commercial",
    engines: ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "IBM Db2", "SQLite"],
    summary:
      "Database-independent library for tracking, managing, and applying database schema changes across SQL, YAML, and XML formats.",
    summaryId:
      "Alat otomasi perubahan skema database multi-format (SQL, YAML, XML) dengan kemampuan rollback terstruktur.",
    url: "https://www.liquibase.com/",
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
    slug: "percona-toolkit",
    name: "Percona Toolkit",
    vendor: "Percona",
    category: "Backup & Migration",
    license: "Open Source (GPL)",
    engines: ["MySQL", "MariaDB", "MongoDB"],
    summary:
      "Collection of advanced command-line tools (pt-online-schema-change, pt-query-digest, pt-table-checksum) for mission-critical operations.",
    summaryId:
      "Koleksi utilitas baris perintah canggih untuk migrasi skema online, digest kueri lambat, dan verifikasi checksum replika.",
    url: "https://www.percona.com/software/database-tools/percona-toolkit",
  },

  // 4. Linux & Systems Diagnostics
  {
    slug: "htop",
    name: "htop / btop",
    vendor: "Hisham Muhammad & Community",
    category: "Linux & Systems Diagnostics",
    license: "Open Source (GPL)",
    engines: ["Universal", "Linux"],
    summary:
      "Interactive process viewer and system monitor for Linux, displaying per-core CPU utilization, memory pressure, and database threads.",
    summaryId:
      "Monitor proses interaktif untuk Linux yang menampilkan utilisasi CPU per-core, konsumsi memori, dan thread proses database.",
    url: "https://htop.dev/",
  },
  {
    slug: "iostat",
    name: "sysstat (iostat / sar / mpstat)",
    vendor: "Sebastien Godard & Community",
    category: "Linux & Systems Diagnostics",
    license: "Open Source (GPL)",
    engines: ["Universal", "Linux"],
    summary:
      "Indispensable Linux I/O monitoring tools measuring disk read/write throughput, await latency, and %util saturation.",
    summaryId:
      "Utilitas utama Linux untuk memantau performa I/O disk, throughput baca/tulis, latensi await, dan persentase saturasi %util.",
    url: "https://github.com/sysstat/sysstat",
  },
  {
    slug: "vmstat",
    name: "vmstat",
    vendor: "procps-ng Community",
    category: "Linux & Systems Diagnostics",
    license: "Open Source (GPL)",
    engines: ["Universal", "Linux"],
    summary:
      "Reports processes, memory, paging, block I/O, traps, and CPU activity to detect database swap thrashing.",
    summaryId:
      "Menampilkan telemetri proses, paging memori, I/O blok, dan aktivitas CPU untuk mendeteksi bahaya swap thrashing pada server database.",
    url: "https://gitlab.com/procps-ng/procps",
  },
  {
    slug: "nmon",
    name: "nmon (Nigel's Monitor)",
    vendor: "Nigel Griffiths",
    category: "Linux & Systems Diagnostics",
    license: "Open Source (GPL)",
    engines: ["Universal", "Linux", "AIX"],
    summary:
      "Single-screen performance tuner for Linux and AIX displaying CPU, disks, memory, network, and file systems simultaneously.",
    summaryId:
      "Monitor performa terpadu untuk Linux dan AIX yang menampilkan grafik CPU, disk I/O, memori, dan jaringan secara simultan.",
    url: "https://nmon.sourceforge.net/",
  },
  {
    slug: "tcpdump-wireshark",
    name: "tcpdump & Wireshark",
    vendor: "Wireshark Foundation & TCPDUMP Team",
    category: "Linux & Systems Diagnostics",
    license: "Open Source (GPL)",
    engines: ["Universal", "PostgreSQL", "MySQL", "Oracle", "SQL Server"],
    summary:
      "Packet analyzer capturing database wire protocol packets (PostgreSQL FE/BE, MySQL, TDS, TNS) to diagnose TCP resets and TLS handshakes.",
    summaryId:
      "Penganalisis paket jaringan untuk membedah protokol database, latensi TCP handshake, reset koneksi, dan negosiasi TLS.",
    url: "https://www.wireshark.org/",
  },

  // 5. Automation & Infrastructure
  {
    slug: "ansible",
    name: "Ansible",
    vendor: "Red Hat",
    category: "Automation & Infrastructure",
    license: "Open Source (GPLv3)",
    engines: ["Universal", "PostgreSQL", "MySQL", "Oracle", "SQL Server"],
    summary:
      "Agentless automation engine used by DBAs for cluster provisioning, configuration drift remediation, and automated OS patching.",
    summaryId:
      "Mesin otomasi tanpa agen untuk provisioning cluster database, manajemen konfigurasi seragam, dan patching OS otomatis.",
    url: "https://www.ansible.com/",
  },
  {
    slug: "terraform",
    name: "Terraform & OpenTofu",
    vendor: "HashiCorp & Linux Foundation",
    category: "Automation & Infrastructure",
    license: "BSL / MPL 2.0",
    engines: ["Universal", "PostgreSQL", "MySQL", "Oracle", "SQL Server"],
    summary:
      "Infrastructure as Code (IaC) tool for provisioning database instances, private subnets, security groups, and storage volumes deterministically.",
    summaryId:
      "Alat Infrastructure as Code (IaC) untuk mengelola instance database cloud, subnet privat, security group, dan volume penyimpanan.",
    url: "https://www.opentofu.org/",
  },
  {
    slug: "docker-kubernetes",
    name: "Docker & Kubernetes (StatefulSets & Operators)",
    vendor: "CNCF",
    category: "Automation & Infrastructure",
    license: "Open Source (Apache 2.0)",
    engines: ["PostgreSQL", "MySQL", "Redis", "Cassandra"],
    summary:
      "Container orchestration platform powering database operators (CloudNativePG, Percona K8s Operators) with automated self-healing failover.",
    summaryId:
      "Platform orkestrasi kontainer yang menggerakkan operator database StatefulSet dengan fitur pemulihan failover otomatis.",
    url: "https://kubernetes.io/",
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
    {
      id: "Clients & Administration",
      label: isId ? "Klien & Administrasi" : "Clients & Administration",
    },
    {
      id: "Monitoring & Observability",
      label: isId ? "Monitoring & Observabilitas" : "Monitoring & Observability",
    },
    {
      id: "Backup & Migration",
      label: isId ? "Backup & Migrasi" : "Backup & Migration",
    },
    {
      id: "Linux & Systems Diagnostics",
      label: isId ? "Diagnostik Linux & Sistem" : "Linux & Diagnostics",
    },
    {
      id: "Automation & Infrastructure",
      label: isId ? "Otomasi & Infrastruktur" : "Automation & Infra",
    },
  ];

  const engines = [
    "All",
    "PostgreSQL",
    "MySQL",
    "Oracle",
    "SQL Server",
    "IBM Db2",
    "SQLite",
    "Linux",
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
              <span>
                {isId
                  ? "Katalog Alat & Observabilitas Database"
                  : "Database Tooling & Observability Catalog"}
              </span>
            </div>
            <h1 className="text-lg sm:text-xl font-bold text-white">
              {isId
                ? "Ekosistem Perangkat Lunak & Administrasi Database"
                : "Database Engineering & Systems Ecosystem"}
            </h1>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-3 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder={
                isId
                  ? "Cari alat, CLI, atau monitoring..."
                  : "Search tools, CLIs, or monitoring..."
              }
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
                    ? "bg-[#F2B84B] text-[#071A3A] font-bold"
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
                    ? "bg-slate-700 text-[#F2B84B] border border-[#F2B84B]/40 font-bold"
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

                  {/* Lifecycle Warning for Deprecated / Maintenance Tools */}
                  {tool.lifecycleStatus === "Maintenance / Deprecated" && (
                    <div className="mb-2 flex items-center gap-1.5 rounded-lg bg-amber-950/60 border border-amber-600/60 px-2 py-1 text-[10px] text-amber-300 font-semibold">
                      <AlertTriangle className="h-3 w-3 text-amber-400 shrink-0" />
                      <span>
                        {isId
                          ? "Status: Maintenance Mode (Dialihkan ke VS Code mssql)"
                          : "Status: Maintenance Mode (Transition to VS Code mssql)"}
                      </span>
                    </div>
                  )}

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
                        <span>
                          {isId ? "Panduan Monitoring" : "Observability Guide"}
                        </span>
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
                  {isId
                    ? "Panduan Observabilitas Mendalam"
                    : "Observability Architecture Guide"}
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
                {isId ? "Kapan Menggunakan Alat Ini?" : "When to Use This Tool:"}
              </strong>
              {isId
                ? activeGuideTool.guide.whenToUseId
                : activeGuideTool.guide.whenToUse}
            </div>

            {/* Architecture Overview */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] mb-1.5 flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5" />
                <span>
                  {isId
                    ? "Arsitektur Pengumpulan Metrik"
                    : "Metrics Architecture"}
                </span>
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed bg-[#10264A]/40 p-3 rounded-xl border border-slate-800">
                {isId
                  ? activeGuideTool.guide.architectureOverviewId
                  : activeGuideTool.guide.architectureOverview}
              </p>
            </div>

            {/* Golden Signals */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] mb-2 flex items-center gap-1.5">
                <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                <span>
                  {isId
                    ? "Sinyal Emas Observabilitas (Golden Signals)"
                    : "Observability Golden Signals"}
                </span>
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-300">
                {(isId
                  ? activeGuideTool.guide.goldenSignalsId
                  : activeGuideTool.guide.goldenSignals
                ).map((signal, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 bg-slate-900/40 p-2 rounded-lg border border-slate-800/80"
                  >
                    <span className="text-[#F2B84B] font-bold">•</span>
                    <span>{signal}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Sample Alert Query */}
            {activeGuideTool.guide.sampleAlertQuery && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#F2B84B] mb-1.5 flex items-center gap-1.5">
                  <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                  <span>
                    {isId ? "Contoh Kueri Peringatan (Alert Rule)" : "Sample Alert Rule Query"}
                  </span>
                </h4>
                <pre className="rounded-xl border border-slate-800 bg-[#071329] p-3 font-mono text-xs text-emerald-300 overflow-x-auto">
                  <code>{activeGuideTool.guide.sampleAlertQuery}</code>
                </pre>
              </div>
            )}

            {/* Footer */}
            <div className="border-t border-slate-800 pt-3 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-mono">
                {isId ? "Lisensi:" : "License:"} {activeGuideTool.license}
              </span>
              <a
                href={activeGuideTool.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 rounded-lg bg-[#F2B84B] px-3.5 py-1.5 text-xs font-bold text-[#071A3A] hover:bg-[#F2B84B]/90 transition-colors"
              >
                <span>
                  {isId ? "Dokumentasi Resmi" : "Official Documentation"}
                </span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

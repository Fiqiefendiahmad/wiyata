"use client";

import React, { useState } from "react";
import {
  BookOpen,
  Search,
  ArrowRight,
  Tag,
  Database,
  ArrowLeft,
} from "lucide-react";

interface Article {
  slug: string;
  title: string;
  titleId: string;
  category: string;
  engine: string;
  summary: string;
  summaryId: string;
  readTime: string;
  body: string;
  bodyId: string;
}

const ARTICLES: Article[] = [
  {
    slug: "understanding-acid-properties",
    title: "Understanding ACID Properties in Modern Relational Databases",
    titleId: "Memahami Prinsip ACID pada Database Relasional Modern",
    category: "Architecture",
    engine: "Universal",
    readTime: "5 min read",
    summary:
      "A deep dive into Atomicity, Consistency, Isolation, and Durability and why they matter in production workloads.",
    summaryId:
      "Penjelasan mendalam mengenai Atomicity, Consistency, Isolation, dan Durability dalam beban kerja produksi.",
    body: `### What is ACID?
ACID represents the four key guarantees of reliable database transactions:
- **Atomicity**: An operation succeeds entirely or is rolled back completely. Never partial.
- **Consistency**: Data transitions strictly from one valid state to another according to constraints and triggers.
- **Isolation**: Concurrent transactions do not interfere or observe partial, uncommitted states.
- **Durability**: Once committed, changes survive unexpected crashes or power failures.

### SQLite Implementation
SQLite guarantees ACID through its Write-Ahead Log (WAL) or Rollback Journal mechanisms.`,
    bodyId: `### Apa itu ACID?
ACID adalah empat pilar jaminan keandalan transaksi database relasional:
- **Atomicity (Keutuhan)**: Transaksi sukses seluruhnya atau dibatalkan total. Tidak ada status setengah jalan.
- **Consistency (Konsistensi)**: Data hanya berpindah dari satu status valid ke status valid lainnya sesuai aturan/integritas.
- **Isolation (Isolasi)**: Transaksi bersamaan tidak saling mengganggu atau melihat data yang belum di-commit.
- **Durability (Ketahanan)**: Sekali transaksi di-commit, data dijamin bertahan walau sistem crash.`,
  },
  {
    slug: "b-tree-indexes-deep-dive",
    title: "B-Tree Indexes: How They Work and When to Use Them",
    titleId: "B-Tree Index: Cara Kerja dan Kapan Harus Digunakan",
    category: "Performance",
    engine: "PostgreSQL & SQLite",
    readTime: "7 min read",
    summary:
      "Demystifying balanced trees, range queries, composite indexes, and index selectivity.",
    summaryId:
      "Memahami struktur balanced tree, pencarian rentang (range query), composite index, dan selektivitas index.",
    body: `### The B-Tree Data Structure
B-Trees keep data sorted and allow searches, sequential access, insertions, and deletions in logarithmic time: **O(log N)**.

### Best Practices for Indexes:
1. Index columns frequently used in \`WHERE\`, \`JOIN\`, and \`ORDER BY\` clauses.
2. Put the most selective column first in composite indexes.
3. Avoid over-indexing tables with high write volume.`,
    bodyId: `### Struktur Data B-Tree
B-Tree menjaga data tetap terurut dan memungkinkan pencarian, akses berurutan, penambahan, serta penghapusan data dalam kompleksitas waktu logaritmik: **O(log N)**.

### Praktik Terbaik Indeks:
1. Berikan indeks pada kolom yang sering muncul di klausa \`WHERE\`, \`JOIN\`, dan \`ORDER BY\`.
2. Letakkan kolom dengan selektivitas tertinggi di urutan pertama pada composite index.
3. Hindari pembuatan indeks berlebih pada tabel yang intensif operasi penulisan (write-heavy).`,
  },
  {
    slug: "sqlite-wal-mode-explained",
    title: "SQLite Write-Ahead Logging (WAL) Mode Explained",
    titleId: "Penjelasan Mode Write-Ahead Logging (WAL) pada SQLite",
    category: "Internals",
    engine: "SQLite",
    readTime: "4 min read",
    summary:
      "How WAL mode unlocks concurrent readers alongside a writer in SQLite environments.",
    summaryId:
      "Bagaimana mode WAL membuka kemampuan pembacaan bersamaan (concurrent readers) tanpa terblokir penulis pada SQLite.",
    body: `### The Default Journal vs. WAL
In classic rollback journal mode, writing locks the whole database from readers.
In **WAL mode** (\`PRAGMA journal_mode=WAL;\`):
- Readers never block writers.
- Writers never block readers.
- Commits are appended to a \`-wal\` file and periodically checkpointed back to the main database file.`,
    bodyId: `### Perbedaan Rollback Journal vs. Mode WAL
Pada mode rollback journal standar, operasi penulisan akan mengunci seluruh database dari proses pembacaan.
Pada **mode WAL** (\`PRAGMA journal_mode=WAL;\`):
- Pembaca (readers) tidak pernah memblokir penulis (writers).
- Penulis (writers) tidak pernah memblokir pembaca (readers).
- Operasi commit ditulis ke file \`-wal\` tambahan dan secara berkala dikonsolidasikan (checkpointing) ke file database utama.`,
  },
];

interface KnowledgeCenterProps {
  language: "en" | "id";
  onOpenLab: () => void;
}

export function KnowledgeCenter({ language, onOpenLab }: KnowledgeCenterProps) {
  const isId = language === "id";
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(
    ARTICLES[0]
  );
  const [mobileViewingArticle, setMobileViewingArticle] = useState(false);

  const filtered = ARTICLES.filter(
    (a) =>
      a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.titleId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelect = (art: Article) => {
    setSelectedArticle(art);
    setMobileViewingArticle(true);
  };

  return (
    <div className="flex flex-col lg:flex-row h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* Sidebar Article List */}
      <aside
        className={`${
          mobileViewingArticle ? "hidden" : "flex"
        } lg:flex w-full lg:w-80 flex-col border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#071A3A]/95 overflow-hidden`}
      >
        <div className="p-3 border-b border-slate-800">
          <div className="relative">
            <Search className="absolute left-2.5 top-3 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder={
                isId ? "Cari artikel database..." : "Search database guides..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded bg-slate-900 border border-slate-800 pl-8 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#F2B84B] min-h-[40px]"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
          {filtered.map((art) => (
            <div
              key={art.slug}
              onClick={() => handleSelect(art)}
              className={`p-3 rounded border cursor-pointer transition-all ${
                selectedArticle?.slug === art.slug
                  ? "border-[#F2B84B] bg-[#10264A] shadow-sm"
                  : "border-slate-800/80 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-800/40"
              }`}
            >
              <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                <span className="font-semibold text-[#F2B84B] uppercase tracking-wider">
                  {art.category}
                </span>
                <span>{art.readTime}</span>
              </div>
              <h3 className="text-xs font-bold text-slate-100 leading-snug">
                {isId ? art.titleId : art.title}
              </h3>
              <p className="mt-1 text-[11px] text-slate-400 line-clamp-2">
                {isId ? art.summaryId : art.summary}
              </p>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Reading Pane */}
      <main
        className={`${
          mobileViewingArticle ? "flex" : "hidden"
        } lg:flex flex-1 flex-col overflow-y-auto p-4 sm:p-8 max-w-4xl`}
      >
        {/* Mobile Back Button */}
        <div className="lg:hidden mb-4">
          <button
            onClick={() => setMobileViewingArticle(false)}
            className="flex items-center gap-1.5 text-xs text-[#F2B84B] font-semibold py-1.5 px-2 rounded bg-slate-900 border border-slate-800 min-h-[36px]"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>
              {isId ? "Kembali ke Daftar Artikel" : "Back to Article List"}
            </span>
          </button>
        </div>

        {selectedArticle ? (
          <div>
            <div className="flex items-center gap-2 text-xs text-[#F2B84B] font-semibold uppercase tracking-wider mb-2">
              <Tag className="h-3.5 w-3.5" />
              <span>{selectedArticle.category}</span>
              <span>•</span>
              <Database className="h-3.5 w-3.5" />
              <span>{selectedArticle.engine}</span>
            </div>

            <h1 className="text-xl sm:text-3xl font-extrabold text-white tracking-tight mb-4">
              {isId ? selectedArticle.titleId : selectedArticle.title}
            </h1>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed italic mb-6 border-l-2 border-[#F2B84B] pl-3 py-0.5">
              {isId ? selectedArticle.summaryId : selectedArticle.summary}
            </p>

            <div className="prose prose-invert prose-sm max-w-none text-slate-300 whitespace-pre-wrap leading-relaxed font-sans text-xs sm:text-sm">
              {isId ? selectedArticle.bodyId : selectedArticle.body}
            </div>

            <div className="mt-8 rounded-lg border border-[#F2B84B]/30 bg-[#10264A]/60 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h4 className="text-xs font-bold text-[#F2B84B]">
                  {isId
                    ? "Praktikkan Teori Ini Langsung"
                    : "Practice This Live in Sandbox"}
                </h4>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {isId
                    ? "Buka Query Studio untuk menguji query dan memverifikasi rencana eksekusi."
                    : "Launch Query Studio to experiment with SQL queries and inspect live execution plans."}
                </p>
              </div>
              <button
                onClick={onOpenLab}
                className="flex items-center justify-center gap-1.5 rounded bg-[#F2B84B] px-4 py-2 text-xs font-bold text-[#071A3A] hover:bg-[#F2B84B]/90 transition-colors min-h-[40px] shrink-0"
              >
                <span>{isId ? "Buka Studio" : "Open Studio"}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-slate-500 py-10">
            {isId
              ? "Pilih artikel dari daftar"
              : "Select an article from the list"}
          </div>
        )}
      </main>
    </div>
  );
}

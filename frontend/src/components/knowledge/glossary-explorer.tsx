"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Search,
  BookOpen,
  Tag,
  Copy,
  Check,
  Zap,
  Filter,
  ShieldCheck,
  ChevronRight,
} from "lucide-react";
import { api } from "@/lib/api";

interface GlossaryTerm {
  slug: string;
  term: string;
  acronym: string;
  aliases: string[];
  category: string;
  category_id: string;
  engines: string[];
  level: string;
  definition_en: string;
  definition_id: string;
  explanation_en: string;
  explanation_id: string;
  field_slang: string;
  diagnostic_query: string;
  related_slugs: string[];
}

interface GlossaryExplorerProps {
  language?: "en" | "id";
  onSelectTerm?: (slug: string) => void;
}

export function GlossaryExplorer({ language = "id" }: GlossaryExplorerProps) {
  const isId = language === "id";
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [search, setSearch] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedEngine, setSelectedEngine] = useState<string>("ALL");
  const [copiedQuerySlug, setCopiedQuerySlug] = useState<string | null>(null);

  useEffect(() => {
    api
      .get("/knowledge/glossary")
      .then((res) => {
        if (Array.isArray(res.data)) {
          setTerms(res.data);
        }
      })
      .catch((err) => console.error("Error loading glossary:", err));
  }, []);

  const categories = useMemo(() => {
    const set = new Set<string>();
    terms.forEach((t) => set.add(t.category));
    return ["ALL", ...Array.from(set)];
  }, [terms]);

  const filteredTerms = useMemo(() => {
    return terms.filter((t) => {
      if (selectedCategory !== "ALL" && t.category !== selectedCategory) {
        return false;
      }
      if (selectedEngine !== "ALL") {
        if (!t.engines.map((e) => e.toLowerCase()).includes(selectedEngine.toLowerCase())) {
          return false;
        }
      }
      if (search.trim()) {
        const q = search.trim().toLowerCase();
        return (
          t.term.toLowerCase().includes(q) ||
          t.acronym.toLowerCase().includes(q) ||
          t.aliases.some((a) => a.toLowerCase().includes(q)) ||
          t.field_slang.toLowerCase().includes(q) ||
          t.definition_en.toLowerCase().includes(q) ||
          t.definition_id.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [terms, selectedCategory, selectedEngine, search]);

  const handleCopyQuery = (slug: string, sql: string) => {
    navigator.clipboard.writeText(sql);
    setCopiedQuerySlug(slug);
    setTimeout(() => setCopiedQuerySlug(null), 2000);
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#071A3A] p-3 sm:p-5 gap-4">
      {/* Search & Filter Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-[#F2B84B]" />
            <h1 className="text-base sm:text-lg font-bold text-white">
              {isId ? "Glosarium & Istilah Lapangan DBA" : "DBA Glossary & Field Terminology"}
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {isId
              ? "Kamus bilingual akronim teknis, konsep inti database, dan istilah operasional lapangan."
              : "Searchable bilingual dictionary of database acronyms, core concepts, and production field terms."}
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72 shrink-0">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={
              isId ? "Cari istilah, akronim, atau slang..." : "Search terms, acronyms, slang..."
            }
            className="w-full rounded-xl bg-slate-900 border border-slate-700/80 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#F2B84B] transition-colors"
          />
        </div>
      </div>

      {/* Categories & Filter Chips */}
      <div className="flex flex-wrap items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll pb-1">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`rounded-lg px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-all border ${
              selectedCategory === cat
                ? "bg-[#F2B84B] text-[#071A3A] border-[#F2B84B] shadow-sm font-bold"
                : "bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            {cat === "ALL" ? (isId ? "Semua Kategori" : "All Categories") : cat}
          </button>
        ))}
      </div>

      {/* Term Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 overflow-y-auto no-scrollbar pr-1 pb-6">
        {filteredTerms.map((term) => (
          <div
            key={term.slug}
            className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4 flex flex-col justify-between hover:border-slate-700 transition-colors shadow-sm"
          >
            <div>
              {/* Top Meta Line */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5">
                  <span className="rounded-md bg-[#F2B84B]/20 text-[#F2B84B] border border-[#F2B84B]/40 px-2 py-0.5 text-[10px] font-mono font-bold">
                    {term.acronym}
                  </span>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[9px] font-mono text-slate-400 border border-slate-700">
                    {isId ? term.category_id : term.category}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 font-mono uppercase">
                  {term.level}
                </span>
              </div>

              {/* Title & Field Slang */}
              <h2 className="text-sm font-bold text-white mb-0.5">{term.term}</h2>
              {term.field_slang && (
                <div className="flex items-center gap-1 text-[11px] text-amber-300 font-mono mb-2">
                  <Tag className="h-3 w-3 text-amber-400" />
                  <span>
                    {isId ? "Istilah Lapangan:" : "Field Phrase:"} &quot;{term.field_slang}&quot;
                  </span>
                </div>
              )}

              {/* Definitions */}
              <p className="text-xs text-slate-300 leading-relaxed mb-2">
                {isId ? term.definition_id : term.definition_en}
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                {isId ? term.explanation_id : term.explanation_en}
              </p>
            </div>

            {/* Diagnostic Query Snippet */}
            {term.diagnostic_query && (
              <div className="mt-2 rounded-lg bg-slate-950 border border-slate-800/80 p-2.5 flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>{isId ? "Kueri Diagnostik Native:" : "Native Diagnostic Query:"}</span>
                  <button
                    onClick={() => handleCopyQuery(term.slug, term.diagnostic_query)}
                    className="flex items-center gap-1 text-[#F2B84B] hover:text-white transition-colors"
                    title={isId ? "Salin Kueri" : "Copy SQL"}
                  >
                    {copiedQuerySlug === term.slug ? (
                      <>
                        <Check className="h-3 w-3 text-emerald-400" />
                        <span className="text-emerald-400">{isId ? "Tersalin" : "Copied"}</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        <span>{isId ? "Salin" : "Copy"}</span>
                      </>
                    )}
                  </button>
                </div>
                <code className="text-[11px] font-mono text-emerald-400 line-clamp-2 break-all">
                  {term.diagnostic_query}
                </code>
              </div>
            )}
          </div>
        ))}

        {filteredTerms.length === 0 && (
          <div className="col-span-full py-16 text-center text-slate-500 text-xs">
            {isId
              ? "Tidak ada istilah yang cocok dengan kriteria pencarian."
              : "No terms match the selected criteria."}
          </div>
        )}
      </div>
    </div>
  );
}

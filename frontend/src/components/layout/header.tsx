"use client";

import React from "react";
import {
  Database,
  RefreshCw,
  BookOpen,
  Wrench,
  GraduationCap,
  Sparkles,
} from "lucide-react";

interface HeaderProps {
  activeTab: "workbench" | "challenges" | "knowledge" | "tools";
  setActiveTab: (tab: "workbench" | "challenges" | "knowledge" | "tools") => void;
  language: "en" | "id";
  setLanguage: (lang: "en" | "id") => void;
  sandboxStatus: string;
  onResetSandbox: () => void;
  isResetting: boolean;
}

export function Header({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
  sandboxStatus,
  onResetSandbox,
  isResetting,
}: HeaderProps) {
  const isId = language === "id";

  return (
    <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-slate-800 bg-[#071A3A]/90 px-4 backdrop-blur-md">
      {/* Brand */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[#F2B84B] to-[#D99A32] shadow-sm">
            <Database className="h-4 w-4 text-[#071A3A]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-wider text-white">WIYATA</span>
              <span className="rounded bg-[#F2B84B]/20 px-1.5 py-0.2 text-[10px] font-semibold text-[#F2B84B] border border-[#F2B84B]/30">
                PLATFORM
              </span>
            </div>
            <p className="text-[10px] text-slate-400">
              {isId ? "Pusat Pembelajaran Database" : "Database Learning Center"}
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 border-l border-slate-800 pl-6">
          <button
            onClick={() => setActiveTab("workbench")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              activeTab === "workbench"
                ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/30"
                : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
            }`}
          >
            <Database className="h-3.5 w-3.5" />
            <span>Query Studio & Lab</span>
          </button>

          <button
            onClick={() => setActiveTab("challenges")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              activeTab === "challenges"
                ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/30"
                : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
            }`}
          >
            <GraduationCap className="h-3.5 w-3.5" />
            <span>{isId ? "Tantangan SQL" : "SQL Challenges"}</span>
          </button>

          <button
            onClick={() => setActiveTab("knowledge")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              activeTab === "knowledge"
                ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/30"
                : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" />
            <span>{isId ? "Pusat Pengetahuan" : "Knowledge Center"}</span>
          </button>

          <button
            onClick={() => setActiveTab("tools")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              activeTab === "tools"
                ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/30"
                : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
            }`}
          >
            <Wrench className="h-3.5 w-3.5" />
            <span>{isId ? "Katalog Alat" : "Professional Tools"}</span>
          </button>
        </nav>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Sandbox Status Badge */}
        <div className="flex items-center gap-2 rounded-md bg-[#10264A]/80 border border-slate-700/60 px-2.5 py-1 text-xs">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-300 font-mono text-[11px]">
            SQLite 3.45 ({sandboxStatus})
          </span>
          <button
            onClick={onResetSandbox}
            disabled={isResetting}
            title={isId ? "Reset database sandbox ke kondisi awal" : "Reset sandbox database to initial state"}
            className="ml-1 text-slate-400 hover:text-[#F2B84B] transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-3 w-3 ${isResetting ? "animate-spin text-[#F2B84B]" : ""}`} />
          </button>
        </div>

        {/* Language Switch */}
        <div className="flex items-center rounded-md bg-[#10264A]/60 border border-slate-800 p-0.5 text-xs">
          <button
            onClick={() => setLanguage("en")}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              language === "en" ? "bg-[#F2B84B] text-[#071A3A] font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLanguage("id")}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              language === "id" ? "bg-[#F2B84B] text-[#071A3A] font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            ID
          </button>
        </div>
      </div>
    </header>
  );
}

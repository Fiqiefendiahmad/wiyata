"use client";

import React, { useState } from "react";
import {
  Database,
  RefreshCw,
  BookOpen,
  Wrench,
  GraduationCap,
  Menu,
  X,
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    {
      id: "workbench" as const,
      label: "Query Studio & Lab",
      icon: Database,
    },
    {
      id: "challenges" as const,
      label: isId ? "Tantangan SQL" : "SQL Challenges",
      icon: GraduationCap,
    },
    {
      id: "knowledge" as const,
      label: isId ? "Pusat Pengetahuan" : "Knowledge Center",
      icon: BookOpen,
    },
    {
      id: "tools" as const,
      label: isId ? "Katalog Alat" : "Professional Tools",
      icon: Wrench,
    },
  ];

  const handleTabClick = (tab: "workbench" | "challenges" | "knowledge" | "tools") => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-slate-800 bg-[#071A3A]/95 px-3 sm:px-4 backdrop-blur-md">
        {/* Brand */}
        <div className="flex items-center gap-2 sm:gap-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[#F2B84B] to-[#D99A32] shadow-sm">
              <Database className="h-4 w-4 text-[#071A3A]" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold tracking-wider text-white text-sm sm:text-base">
                  WIYATA
                </span>
                <span className="rounded bg-[#F2B84B]/20 px-1.5 py-0.2 text-[9px] sm:text-[10px] font-semibold text-[#F2B84B] border border-[#F2B84B]/30">
                  PLATFORM
                </span>
              </div>
              <p className="hidden xs:block text-[9px] sm:text-[10px] text-slate-400">
                {isId ? "Pusat Pembelajaran Database" : "Database Learning Center"}
              </p>
            </div>
          </div>

          {/* Desktop Navigation Tabs */}
          <nav className="hidden lg:flex items-center gap-1 border-l border-slate-800 pl-4 xl:pl-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleTabClick(item.id)}
                  className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/30"
                      : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Sandbox Status Badge */}
          <div className="flex items-center gap-1.5 sm:gap-2 rounded-md bg-[#10264A]/80 border border-slate-700/60 px-2 sm:px-2.5 py-1 text-xs">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300 font-mono text-[10px] sm:text-[11px] max-w-[100px] sm:max-w-none truncate">
              SQLite ({sandboxStatus})
            </span>
            <button
              onClick={onResetSandbox}
              disabled={isResetting}
              title={
                isId
                  ? "Reset database sandbox ke kondisi awal"
                  : "Reset sandbox database to initial state"
              }
              className="p-1 text-slate-400 hover:text-[#F2B84B] transition-colors disabled:opacity-50"
            >
              <RefreshCw
                className={`h-3 w-3 ${
                  isResetting ? "animate-spin text-[#F2B84B]" : ""
                }`}
              />
            </button>
          </div>

          {/* Language Switch */}
          <div className="flex items-center rounded-md bg-[#10264A]/60 border border-slate-800 p-0.5 text-xs">
            <button
              onClick={() => setLanguage("en")}
              className={`px-1.5 sm:px-2 py-0.5 rounded text-[10px] sm:text-[11px] font-medium transition-colors ${
                language === "en"
                  ? "bg-[#F2B84B] text-[#071A3A] font-bold"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage("id")}
              className={`px-1.5 sm:px-2 py-0.5 rounded text-[10px] sm:text-[11px] font-medium transition-colors ${
                language === "id"
                  ? "bg-[#F2B84B] text-[#071A3A] font-bold"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              ID
            </button>
          </div>

          {/* Mobile Hamburger Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden flex h-9 w-9 items-center justify-center rounded-md border border-slate-700 bg-[#10264A] text-slate-200"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? (
              <X className="h-4 w-4" />
            ) : (
              <Menu className="h-4 w-4" />
            )}
          </button>
        </div>
      </header>

      {/* Mobile Drawer Navigation Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-x-0 top-14 z-50 border-b border-slate-800 bg-[#071A3A]/98 p-3 shadow-2xl backdrop-blur-lg">
          <nav className="flex flex-col gap-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleTabClick(item.id)}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-semibold text-left transition-colors min-h-[44px] ${
                    isActive
                      ? "bg-[#10264A] text-[#F2B84B] border border-[#F2B84B]/30"
                      : "text-slate-300 hover:bg-slate-800/80"
                  }`}
                >
                  <Icon className="h-4 w-4 text-[#F2B84B]" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      )}
    </>
  );
}

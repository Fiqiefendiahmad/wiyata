"use client";

import React, { useState } from "react";
import Image from "next/image";
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
      label: isId ? "Studio & Lab" : "Query Studio & Lab",
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

  const handleTabClick = (
    tab: "workbench" | "challenges" | "knowledge" | "tools"
  ) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-slate-800 bg-[#071A3A]/95 px-3 sm:px-4 backdrop-blur-md">
        {/* Brand with Official App Icon */}
        <div className="flex items-center gap-2 sm:gap-6 min-w-0">
          <div
            onClick={() => setActiveTab("workbench")}
            className="flex cursor-pointer items-center gap-2.5 shrink-0"
          >
            <div className="relative h-8 w-8 overflow-hidden rounded-lg shadow-sm shrink-0 border border-[#F2B84B]/40 bg-[#10264A]">
              <Image
                src="/wiyata-app-icon.png"
                alt="WIYATA Platform Icon"
                width={32}
                height={32}
                className="h-full w-full object-cover"
                priority
              />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold tracking-wider text-white text-sm sm:text-base">
                  WIYATA
                </span>
                <span className="rounded bg-[#F2B84B]/20 px-1 py-0.2 text-[9px] font-bold text-[#F2B84B] border border-[#F2B84B]/30 hidden xs:inline-block">
                  SQL LAB
                </span>
              </div>
              <p className="text-[9px] sm:text-[10px] text-slate-400 leading-tight truncate max-w-[145px] xs:max-w-none">
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
        <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
          {/* Actionable Refresh Sandbox Data Button (Replaces passive status indicator) */}
          <button
            onClick={onResetSandbox}
            disabled={isResetting}
            title={
              isId
                ? "Muat Ulang / Reset Data Sandbox ke Kondisi Awal"
                : "Refresh & Reset Sandboxed Data to Initial State"
            }
            aria-label={isId ? "Segarkan data sandbox" : "Refresh and reset sandboxed data"}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-[#10264A] px-2.5 sm:px-3 py-1.5 text-xs font-semibold text-slate-200 hover:text-white hover:border-[#F2B84B] transition-colors disabled:opacity-50 min-h-[38px] active:scale-95"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 text-[#F2B84B] ${
                isResetting ? "animate-spin" : ""
              }`}
            />
            <span className="hidden xs:inline text-[11px] font-semibold">
              {isResetting
                ? isId
                  ? "Menyegarkan..."
                  : "Refreshing..."
                : isId
                ? "Segarkan Data"
                : "Refresh Data"}
            </span>
          </button>

          {/* Language Switch */}
          <div className="flex items-center rounded-md bg-[#10264A]/60 border border-slate-800 p-0.5 text-xs">
            <button
              onClick={() => setLanguage("en")}
              aria-label="Switch to English"
              className={`min-w-[30px] sm:min-w-[34px] py-1 rounded text-[10px] sm:text-[11px] font-semibold text-center transition-colors ${
                language === "en"
                  ? "bg-[#F2B84B] text-[#071A3A] font-bold"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage("id")}
              aria-label="Pilih Bahasa Indonesia"
              className={`min-w-[30px] sm:min-w-[34px] py-1 rounded text-[10px] sm:text-[11px] font-semibold text-center transition-colors ${
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
            className="lg:hidden flex h-10 w-10 items-center justify-center rounded-md border border-slate-700 bg-[#10264A] text-slate-200 active:bg-slate-800"
            aria-label="Menu Navigasi"
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>
      </header>

      {/* Mobile Drawer Navigation Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-x-0 top-14 z-50 border-b border-slate-800 bg-[#071A3A]/98 p-3 shadow-2xl backdrop-blur-lg">
          <div className="flex items-center gap-2.5 mb-3 pb-2.5 border-b border-slate-800/80 px-1">
            <div className="relative h-7 w-7 overflow-hidden rounded shadow shrink-0 border border-[#F2B84B]/40 bg-[#10264A]">
              <Image
                src="/wiyata-app-icon.png"
                alt="WIYATA"
                width={28}
                height={28}
                className="h-full w-full object-cover"
              />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-extrabold text-white tracking-wider">WIYATA</span>
                <span className="rounded bg-[#F2B84B]/20 px-1 py-0.2 text-[8px] font-bold text-[#F2B84B] border border-[#F2B84B]/30">
                  SQL LAB
                </span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                {isId ? "Pusat Pembelajaran Database" : "Database Learning Center"}
              </p>
            </div>
          </div>

          <nav className="flex flex-col gap-1.5 mb-3">
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
                      : "text-slate-300 hover:bg-slate-800/80 active:bg-slate-800"
                  }`}
                >
                  <Icon className="h-4 w-4 text-[#F2B84B] shrink-0" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Mobile Refresh Data Button */}
          <div className="border-t border-slate-800/80 pt-3">
            <button
              onClick={() => {
                onResetSandbox();
                setMobileMenuOpen(false);
              }}
              disabled={isResetting}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-[#10264A] border border-[#F2B84B]/40 py-2.5 text-xs font-bold text-white hover:bg-[#F2B84B] hover:text-[#071A3A] transition-colors min-h-[44px] active:scale-95"
            >
              <RefreshCw
                className={`h-4 w-4 text-[#F2B84B] ${
                  isResetting ? "animate-spin" : ""
                }`}
              />
              <span>
                {isResetting
                  ? isId
                    ? "Memulihkan Data..."
                    : "Refreshing Data..."
                  : isId
                  ? "Refresh & Pulihkan Data Sandbox"
                  : "Refresh & Reset Sandbox Data"}
              </span>
            </button>
          </div>
        </div>
      )}
    </>
  );
}

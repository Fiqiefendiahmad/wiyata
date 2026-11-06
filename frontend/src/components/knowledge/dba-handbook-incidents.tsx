"use client";

import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Check,
  RotateCcw,
  Activity,
  Terminal,
  Bug,
  BookOpen,
} from "lucide-react";
import { api } from "@/lib/api";

interface DiagnosticCommand {
  engine: string;
  risk: "read_only" | "privileged" | "disruptive" | "destructive";
  label: string;
  sql: string;
}

interface IncidentRunbook {
  slug: string;
  title: string;
  title_id: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM";
  category: string;
  symptoms: string[];
  first_checks: string[];
  diagnostic_commands: DiagnosticCommand[];
  remediation_steps: string[];
  rollback_plan: string;
}

interface TroubleshootingCase {
  slug: string;
  title: string;
  title_id: string;
  error_code: string;
  engines: string[];
  severity: "CRITICAL" | "HIGH" | "MEDIUM";
  symptoms: string[];
  root_cause: string;
  investigation_sql: string;
  remediation: string[];
  rollback: string;
}

interface DbaHandbookProps {
  language?: "en" | "id";
}

export function DbaHandbookIncidents({ language = "id" }: DbaHandbookProps) {
  const isId = language === "id";
  const [activeTab, setActiveTab] = useState<"runbooks" | "errors">("runbooks");
  const [incidents, setIncidents] = useState<IncidentRunbook[]>([]);
  const [troubleshooting, setTroubleshooting] = useState<TroubleshootingCase[]>([]);
  const [selectedIncidentSlug, setSelectedIncidentSlug] = useState<string>("");
  const [selectedErrorSlug, setSelectedErrorSlug] = useState<string>("");
  const [copiedIndex, setCopiedIndex] = useState<number | string | null>(null);

  useEffect(() => {
    // 1. Fetch Runbooks
    api
      .get("/knowledge/incidents")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setIncidents(res.data);
          setSelectedIncidentSlug(res.data[0].slug);
        }
      })
      .catch((err) => console.error("Error loading incident runbooks:", err));

    // 2. Fetch Troubleshooting Error Code KB
    api
      .get("/knowledge/troubleshooting")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setTroubleshooting(res.data);
          setSelectedErrorSlug(res.data[0].slug);
        }
      })
      .catch((err) => console.error("Error loading troubleshooting KB:", err));
  }, []);

  const activeIncident =
    incidents.find((i) => i.slug === selectedIncidentSlug) || incidents[0];
  const activeError =
    troubleshooting.find((t) => t.slug === selectedErrorSlug) || troubleshooting[0];

  const handleCopySql = (sql: string, id: number | string) => {
    navigator.clipboard.writeText(sql);
    setCopiedIndex(id);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="flex flex-col lg:flex-row h-full w-full overflow-hidden bg-[#071A3A] text-slate-100">
      {/* SIDEBAR: Scenario & Error Code Selector */}
      <div className="w-full lg:w-84 xl:w-96 shrink-0 border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#0A1B38]/95 p-3 sm:p-4 flex flex-col gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Terminal className="h-4 w-4 text-[#F2B84B]" />
            <h2 className="text-sm font-bold text-white tracking-wide">
              {isId ? "Buku Saku Insiden & Diagnostik" : "DBA Incident Handbook & KB"}
            </h2>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            {isId
              ? "Prosedur investigasi runbook darurat dan basis data kode galat produksi (ORA, PostgreSQL, MySQL, SQL Server, Db2)."
              : "Structured emergency diagnostic workflows and enterprise error code root-cause investigations."}
          </p>
        </div>

        {/* Tab Switcher: Runbooks vs Error Codes */}
        <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-800">
          <button
            onClick={() => setActiveTab("runbooks")}
            className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "runbooks"
                ? "bg-gradient-to-r from-[#F2B84B] to-[#E5A838] text-[#071A3A] font-bold shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" />
            <span>{isId ? "Runbook Insiden" : "Runbooks"}</span>
          </button>
          <button
            onClick={() => setActiveTab("errors")}
            className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "errors"
                ? "bg-gradient-to-r from-[#F2B84B] to-[#E5A838] text-[#071A3A] font-bold shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Bug className="h-3.5 w-3.5" />
            <span>{isId ? "Kode Galat KB" : "Error Codes"}</span>
          </button>
        </div>

        {/* List of Items */}
        <div className="flex lg:flex-col gap-2 overflow-x-auto lg:overflow-y-auto no-scrollbar touch-scroll pb-2 lg:pb-0 flex-1">
          {activeTab === "runbooks" ? (
            incidents.map((inc) => {
              const isSelected = inc.slug === activeIncident?.slug;
              return (
                <button
                  key={inc.slug}
                  onClick={() => setSelectedIncidentSlug(inc.slug)}
                  className={`flex flex-col text-left p-3 rounded-xl border transition-all shrink-0 w-64 lg:w-full min-h-[72px] active:scale-95 ${
                    isSelected
                      ? "bg-[#10264A] border-[#F2B84B] ring-1 ring-[#F2B84B]/40 shadow-sm"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span
                      className={`rounded px-1.5 py-0.2 text-[9px] font-mono font-bold ${
                        inc.severity === "CRITICAL"
                          ? "bg-rose-950 text-rose-400 border border-rose-800"
                          : "bg-amber-950 text-amber-400 border border-amber-800"
                      }`}
                    >
                      {inc.severity}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {inc.category}
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-white leading-snug line-clamp-1">
                    {isId ? inc.title_id : inc.title}
                  </h3>
                </button>
              );
            })
          ) : (
            troubleshooting.map((tc) => {
              const isSelected = tc.slug === activeError?.slug;
              return (
                <button
                  key={tc.slug}
                  onClick={() => setSelectedErrorSlug(tc.slug)}
                  className={`flex flex-col text-left p-3 rounded-xl border transition-all shrink-0 w-64 lg:w-full min-h-[72px] active:scale-95 ${
                    isSelected
                      ? "bg-[#10264A] border-[#F2B84B] ring-1 ring-[#F2B84B]/40 shadow-sm"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span className="rounded bg-rose-950/90 text-rose-300 border border-rose-700/80 px-1.5 py-0.2 text-[9px] font-mono font-bold">
                      {tc.error_code}
                    </span>
                    <span className="text-[10px] text-amber-400/90 font-mono">
                      {tc.engines.join(", ")}
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-white leading-snug line-clamp-1">
                    {isId ? tc.title_id : tc.title}
                  </h3>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* DETAIL VIEWPORT */}
      <div className="flex flex-1 flex-col overflow-y-auto no-scrollbar p-3 sm:p-5 gap-4">
        {activeTab === "runbooks" && activeIncident ? (
          <>
            {/* Runbook Header */}
            <div className="border-b border-slate-800/80 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-2 py-0.5 text-[10px] font-mono font-bold ${
                      activeIncident.severity === "CRITICAL"
                        ? "bg-rose-950 text-rose-400 border border-rose-800"
                        : "bg-amber-950 text-amber-400 border border-amber-800"
                    }`}
                  >
                    {activeIncident.severity}
                  </span>
                  <h1 className="text-base sm:text-lg font-bold text-white">
                    {isId ? activeIncident.title_id : activeIncident.title}
                  </h1>
                </div>
                <p className="text-xs text-slate-400 mt-1">{activeIncident.category}</p>
              </div>
            </div>

            {/* 1. Symptoms & First Checks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  <span>{isId ? "Gejala & Sinyal Peringatan" : "Observed Symptoms"}</span>
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {activeIncident.symptoms.map((s, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span>{isId ? "Langkah Awal Investigasi (Triage)" : "Immediate First Checks"}</span>
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {activeIncident.first_checks.map((fc, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">✓</span>
                      <span>{fc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* 2. Diagnostic Commands */}
            <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-[#F2B84B]" />
                  <span>{isId ? "Kueri & Perintah Diagnostik Native" : "Native Diagnostic Commands"}</span>
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">
                  {isId ? "Prioritaskan kueri Hanya Baca" : "Prioritize Read-Only execution"}
                </span>
              </div>

              <div className="space-y-2.5">
                {activeIncident.diagnostic_commands.map((cmd, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg bg-slate-950 p-3 border border-slate-800/80 flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="rounded bg-slate-800 px-2 py-0.5 text-[9px] font-mono text-[#F2B84B] font-bold uppercase">
                          {cmd.engine}
                        </span>
                        <span className="text-xs font-semibold text-slate-200">
                          {cmd.label}
                        </span>
                        <span className="rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800 px-1.5 py-0.2 text-[9px] font-mono font-bold flex items-center gap-1">
                          <ShieldCheck className="h-3 w-3" />
                          <span>{isId ? "Hanya Baca (Aman)" : "Read Only (Safe)"}</span>
                        </span>
                      </div>

                      <button
                        onClick={() => handleCopySql(cmd.sql, idx)}
                        className="flex items-center gap-1 text-[11px] font-mono text-[#F2B84B] hover:text-white transition-colors"
                      >
                        {copiedIndex === idx ? (
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

                    <code className="text-xs font-mono text-emerald-400 break-all leading-relaxed">
                      {cmd.sql}
                    </code>
                  </div>
                ))}
              </div>
            </div>

            {/* 3. Remediation & Rollback Plan */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-6">
              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <ShieldAlert className="h-4 w-4 text-[#F2B84B]" />
                  <span>{isId ? "Opsi Remediasi & Mitigasi" : "Remediation & Mitigation Options"}</span>
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {activeIncident.remediation_steps.map((r, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-[#F2B84B] font-bold">{idx + 1}.</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <RotateCcw className="h-4 w-4 text-rose-400" />
                  <span>{isId ? "Rencana Rollback & Risiko" : "Rollback Plan & Safeguards"}</span>
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {activeIncident.rollback_plan}
                </p>
              </div>
            </div>
          </>
        ) : activeTab === "errors" && activeError ? (
          <>
            {/* Error Code Header */}
            <div className="border-b border-slate-800/80 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="rounded px-2 py-0.5 text-xs font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                    {activeError.error_code}
                  </span>
                  <h1 className="text-base sm:text-lg font-bold text-white">
                    {isId ? activeError.title_id : activeError.title}
                  </h1>
                </div>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-xs text-slate-400">
                    {isId ? "Mesin Terdampak:" : "Impacted Engines:"}
                  </span>
                  {activeError.engines.map((eng) => (
                    <span
                      key={eng}
                      className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-[#F2B84B] font-semibold"
                    >
                      {eng}
                    </span>
                  ))}
                  <span
                    className={`ml-2 rounded px-1.5 py-0.2 text-[9px] font-mono font-bold ${
                      activeError.severity === "CRITICAL"
                        ? "bg-rose-950 text-rose-400 border border-rose-800"
                        : "bg-amber-950 text-amber-400 border border-amber-800"
                    }`}
                  >
                    {activeError.severity}
                  </span>
                </div>
              </div>
            </div>

            {/* Symptoms & Root Cause */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  <span>{isId ? "Gejala & Pola Kemunculan" : "Observed Symptoms"}</span>
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {activeError.symptoms.map((s, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <Bug className="h-4 w-4 text-rose-400" />
                  <span>{isId ? "Akar Permasalahan (Root Cause)" : "Technical Root Cause"}</span>
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {activeError.root_cause}
                </p>
              </div>
            </div>

            {/* Diagnostic Query */}
            <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4 flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-[#F2B84B]" />
                  <span>{isId ? "Kueri Investigasi & Telemetri" : "Investigation Query"}</span>
                </h3>
                <button
                  onClick={() => handleCopySql(activeError.investigation_sql, "err_sql")}
                  className="flex items-center gap-1 text-[11px] font-mono text-[#F2B84B] hover:text-white transition-colors"
                >
                  {copiedIndex === "err_sql" ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-400" />
                      <span className="text-emerald-400">{isId ? "Tersalin" : "Copied"}</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>{isId ? "Salin Kueri" : "Copy SQL"}</span>
                    </>
                  )}
                </button>
              </div>
              <div className="rounded-lg bg-slate-950 p-3 border border-slate-800/80">
                <code className="text-xs font-mono text-emerald-400 break-all leading-relaxed">
                  {activeError.investigation_sql}
                </code>
              </div>
            </div>

            {/* Remediation & Rollback */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-6">
              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-[#F2B84B]" />
                  <span>{isId ? "Langkah Mitigasi & Solusi Permanen" : "Remediation & Permanent Fix"}</span>
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {activeError.remediation.map((r, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-[#F2B84B] font-bold">{idx + 1}.</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-slate-800 bg-[#0A1B38] p-4">
                <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-1.5">
                  <RotateCcw className="h-4 w-4 text-amber-400" />
                  <span>{isId ? "Rencana Rollback & Mitigasi Risiko" : "Rollback & Risk Controls"}</span>
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {activeError.rollback}
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="flex h-64 items-center justify-center text-slate-400 text-xs">
            {isId ? "Memuat data diagnostik..." : "Loading diagnostic data..."}
          </div>
        )}
      </div>
    </div>
  );
}

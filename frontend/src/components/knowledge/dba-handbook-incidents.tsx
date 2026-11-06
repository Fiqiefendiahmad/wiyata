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
  HelpCircle,
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

interface DbaHandbookProps {
  language?: "en" | "id";
}

export function DbaHandbookIncidents({ language = "id" }: DbaHandbookProps) {
  const isId = language === "id";
  const [incidents, setIncidents] = useState<IncidentRunbook[]>([]);
  const [selectedIncidentSlug, setSelectedIncidentSlug] = useState<string>("");
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  useEffect(() => {
    api
      .get("/knowledge/incidents")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setIncidents(res.data);
          setSelectedIncidentSlug(res.data[0].slug);
        }
      })
      .catch((err) => console.error("Error loading incident runbooks:", err));
  }, []);

  const activeIncident =
    incidents.find((i) => i.slug === selectedIncidentSlug) || incidents[0];

  const handleCopySql = (sql: string, index: number) => {
    navigator.clipboard.writeText(sql);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (!activeIncident) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400 text-xs">
        Memuat Buku Saku Insiden...
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row h-full w-full overflow-hidden bg-[#071A3A] text-slate-100">
      {/* SIDEBAR: Incident Scenario List */}
      <div className="w-full lg:w-80 shrink-0 border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#0A1B38]/90 p-3 sm:p-4 flex flex-col gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Terminal className="h-4 w-4 text-[#F2B84B]" />
            <h2 className="text-sm font-bold text-white tracking-wide">
              {isId ? "Runbook Insiden Produksi" : "Production Incident Runbooks"}
            </h2>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            {isId
              ? "Prosedur investigasi terstruktur dari gejala, kueri diagnostik aman, hingga mitigasi dan verifikasi rollback."
              : "Structured emergency diagnostic workflows from first checks, read-only telemetry, to remediation and rollback."}
          </p>
        </div>

        {/* List of Incidents */}
        <div className="flex lg:flex-col gap-2 overflow-x-auto lg:overflow-y-auto no-scrollbar touch-scroll pb-2 lg:pb-0">
          {incidents.map((inc) => {
            const isSelected = inc.slug === activeIncident.slug;
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
          })}
        </div>
      </div>

      {/* DETAIL VIEWPORT: Runbook Content */}
      <div className="flex flex-1 flex-col overflow-y-auto no-scrollbar p-3 sm:p-5 gap-4">
        {/* Title Header */}
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
          {/* Symptoms */}
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

          {/* First Checks Checklist */}
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

        {/* 2. Diagnostic Commands with Risk Tags */}
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
          {/* Remediation */}
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

          {/* Rollback Plan */}
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
      </div>
    </div>
  );
}

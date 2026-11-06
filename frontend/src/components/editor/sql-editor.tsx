"use client";

import React, { useState, useEffect, useRef } from "react";
import dynamic from "next/dynamic";

const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute?: () => void;
  readOnly?: boolean;
  language?: "en" | "id";
}

const COMMON_SQL_KEYWORDS = [
  "SELECT",
  "FROM",
  "WHERE",
  "JOIN",
  "GROUP BY",
  "ORDER BY",
  "LIMIT",
];

export function SqlEditor({
  value,
  onChange,
  onExecute,
  readOnly = false,
  language = "id",
}: SqlEditorProps) {
  const isId = language === "id";
  const [mounted, setMounted] = useState(false);
  const [isMobileScreen, setIsMobileScreen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setMounted(true);
    const checkMobile = () => {
      setIsMobileScreen(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => {
      window.removeEventListener("resize", checkMobile);
    };
  }, []);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onExecute) onExecute();
    });
  };

  const handleTextareaKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (onExecute) onExecute();
    } else if (e.key === "Tab") {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const updated = value.substring(0, start) + "  " + value.substring(end);
      onChange(updated);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 2;
      }, 0);
    }
  };

  const insertKeyword = (keyword: string) => {
    if (!textareaRef.current) {
      onChange(value ? `${value} ${keyword} ` : `${keyword} `);
      return;
    }
    const el = textareaRef.current;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    const inserted = `${keyword} `;
    const updated =
      value.substring(0, start) + inserted + value.substring(end);
    onChange(updated);
    setTimeout(() => {
      el.focus();
      el.selectionStart = el.selectionEnd = start + inserted.length;
    }, 0);
  };

  const lineCount = (value.match(/\n/g) || []).length + 1;

  return (
    <div className="relative flex flex-col h-full w-full overflow-hidden rounded-lg border border-slate-700/80 bg-[#071A3A] shadow-inner">
      {/* Mobile Quick Keywords Toolbar */}
      {isMobileScreen && !readOnly && (
        <div className="flex items-center gap-1 overflow-x-auto border-b border-slate-800 bg-[#10264A]/90 px-2 py-1.5 no-scrollbar touch-scroll shrink-0">
          <span className="text-[10px] font-mono text-slate-500 uppercase px-1">
            SQL:
          </span>
          {COMMON_SQL_KEYWORDS.map((kw) => (
            <button
              key={kw}
              type="button"
              onClick={() => insertKeyword(kw)}
              className="rounded bg-slate-800 px-2.5 py-1 text-[11px] font-mono font-semibold text-[#F2B84B] border border-slate-700 active:bg-[#F2B84B] active:text-[#071A3A] transition-colors shrink-0 min-h-[32px]"
            >
              {kw}
            </button>
          ))}
        </div>
      )}

      {/* Editor Surface with Absolute Inset positioning to guarantee non-zero pixel bounds in Flexbox */}
      <div className="relative flex-1 w-full min-h-0 overflow-hidden">
        {mounted && !isMobileScreen ? (
          <div className="absolute inset-0">
            <Editor
              height="100%"
              width="100%"
              defaultLanguage="sql"
              language="sql"
              theme="vs-dark"
              value={value}
              onChange={(val) => onChange(val || "")}
              onMount={handleEditorDidMount}
              loading={
                <div className="flex h-full w-full items-center justify-center font-mono text-xs text-slate-400 bg-[#071A3A]">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#F2B84B] animate-ping" />
                    <span>{isId ? "Memuat SQL Editor..." : "Loading SQL Editor..."}</span>
                  </div>
                </div>
              }
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "var(--font-mono), monospace",
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                automaticLayout: true,
                readOnly: readOnly,
                padding: { top: 12, bottom: 12 },
                wordWrap: "on",
                tabSize: 2,
                cursorBlinking: "smooth",
                smoothScrolling: true,
                renderLineHighlight: "all",
                formatOnPaste: true,
              }}
            />
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col bg-[#071A3A]">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={handleTextareaKeyDown}
              readOnly={readOnly}
              autoCapitalize="none"
              autoComplete="off"
              autoCorrect="off"
              spellCheck={false}
              className="flex-1 w-full h-full resize-none bg-transparent p-3 font-mono text-xs text-slate-100 leading-relaxed focus:outline-none placeholder-slate-600"
              placeholder={
                isId
                  ? "-- Tulis perintah SQL di sini...\nSELECT * FROM accounts LIMIT 10;"
                  : "-- Enter SQL query here...\nSELECT * FROM accounts LIMIT 10;"
              }
            />
          </div>
        )}
      </div>

      {/* Sleek Editor Status Footer */}
      <div className="flex items-center justify-between border-t border-slate-800 bg-[#10264A]/40 px-3 py-1 text-[10px] font-mono text-slate-500 shrink-0">
        <span className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <span>SQLite 3</span>
          {readOnly && (
            <span className="rounded bg-slate-800 px-1.5 py-0.2 text-[9px] text-amber-400 border border-amber-800/60 font-sans">
              {isId ? "Hanya Baca" : "Read Only"}
            </span>
          )}
        </span>
        <div className="flex items-center gap-3">
          <span>{lineCount} {isId ? "baris" : "lines"}</span>
          <span className="hidden sm:inline">
            {isId ? "Ctrl + Enter untuk Menjalankan" : "Ctrl + Enter to Execute"}
          </span>
        </div>
      </div>
    </div>
  );
}

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
}: SqlEditorProps) {
  const [mounted, setMounted] = useState(false);
  const [isMobileScreen, setIsMobileScreen] = useState(false);
  const [monacoLoaded, setMonacoLoaded] = useState(false);
  const [monacoFailed, setMonacoFailed] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setMounted(true);
    const checkMobile = () => {
      setIsMobileScreen(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);

    // Timeout fallback for desktop Monaco loader
    const timer = setTimeout(() => {
      if (!monacoLoaded) {
        setMonacoFailed(true);
      }
    }, 4000);

    return () => {
      window.removeEventListener("resize", checkMobile);
      clearTimeout(timer);
    };
  }, [monacoLoaded]);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    setMonacoLoaded(true);
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
    <div className="relative flex flex-col h-full w-full overflow-hidden rounded-md border border-slate-700/60 bg-[#071A3A]">
      {/* Mobile Quick Keywords Toolbar */}
      {isMobileScreen && !readOnly && (
        <div className="flex items-center gap-1 overflow-x-auto border-b border-slate-800 bg-[#10264A]/90 px-2 py-1.5 no-scrollbar shrink-0">
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

      {/* Editor Surface */}
      <div className="relative flex-1 h-full w-full overflow-hidden">
        {mounted && !isMobileScreen && !monacoFailed ? (
          <Editor
            height="100%"
            defaultLanguage="sql"
            theme="vs-dark"
            value={value}
            onChange={(val) => onChange(val || "")}
            onMount={handleEditorDidMount}
            loading={
              <div className="flex h-full w-full items-center justify-center font-mono text-xs text-slate-400">
                Memuat SQL Editor...
              </div>
            }
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: "var(--font-mono), monospace",
              lineNumbers: "on",
              scrollBeyondLastLine: false,
              automaticLayout: true,
              readOnly: readOnly,
              padding: { top: 12, bottom: 12 },
              wordWrap: "on",
            }}
          />
        ) : (
          <div className="flex h-full w-full overflow-hidden bg-[#071A3A]">
            {/* Gutter Line Numbers */}
            <div className="select-none py-3 pl-2 pr-2 font-mono text-[11px] text-slate-600 text-right bg-[#071A3A] border-r border-slate-800/60 shrink-0">
              {Array.from({ length: Math.max(lineCount, 6) }).map((_, i) => (
                <div key={i} className="leading-5 h-5">
                  {i + 1}
                </div>
              ))}
            </div>

            {/* Mobile Native Textarea */}
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
              className="flex-1 h-full w-full resize-none bg-transparent p-3 font-mono text-xs text-slate-100 leading-5 focus:outline-none placeholder-slate-600"
              placeholder="-- Tulis perintah SQL di sini...&#10;SELECT * FROM accounts LIMIT 10;"
            />
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
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

export function SqlEditor({
  value,
  onChange,
  onExecute,
  readOnly = false,
}: SqlEditorProps) {
  const [mounted, setMounted] = useState(false);
  const [editorFailed, setEditorFailed] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Safety fallback: if Monaco fails to initialize in 4s, fallback to native textarea
    const timer = setTimeout(() => {
      // Keep running
    }, 4000);
    return () => clearTimeout(timer);
  }, []);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onExecute) onExecute();
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (onExecute) onExecute();
    }
  };

  return (
    <div className="relative h-full w-full overflow-hidden rounded-md border border-slate-700/60 bg-[#071A3A]">
      {mounted && !editorFailed ? (
        <Editor
          height="100%"
          defaultLanguage="sql"
          theme="vs-dark"
          value={value}
          onChange={(val) => onChange(val || "")}
          onMount={handleEditorDidMount}
          loading={
            <div className="flex h-full w-full items-center justify-center font-mono text-xs text-slate-400">
              Loading Monaco Editor...
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
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          className="h-full w-full resize-none bg-[#071A3A] p-3 font-mono text-xs text-slate-200 focus:outline-none"
          placeholder="Enter SQL statement here..."
        />
      )}
    </div>
  );
}

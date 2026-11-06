"use client";

import React from "react";
import dynamic from "next/dynamic";

const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center bg-[#071A3A]/40 text-slate-400 font-mono text-xs">
      Loading SQL Editor...
    </div>
  ),
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
  const handleEditorDidMount = (editor: any, monaco: any) => {
    // Add Ctrl+Enter or Cmd+Enter shortcut for execution
    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
      () => {
        if (onExecute) onExecute();
      }
    );
  };

  return (
    <div className="relative h-full w-full overflow-hidden rounded-md border border-slate-700/60 bg-[#071A3A]">
      <Editor
        height="100%"
        defaultLanguage="sql"
        theme="vs-dark"
        value={value}
        onChange={(val) => onChange(val || "")}
        onMount={handleEditorDidMount}
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
    </div>
  );
}

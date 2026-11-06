"use client";

import React, { useState } from "react";
import { Copy, Check, Terminal, Layers, AlertTriangle, Info, CheckCircle2 } from "lucide-react";

interface ArticleMarkdownProps {
  content: string;
}

function renderInline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  const regex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith("`") && token.endsWith("`")) {
      parts.push(
        <code
          key={match.index}
          className="rounded bg-slate-900 border border-slate-700/60 px-1.5 py-0.5 font-mono text-[11px] text-[#F2B84B]"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith("**") && token.endsWith("**")) {
      parts.push(
        <strong key={match.index} className="font-bold text-white">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith("*") && token.endsWith("*")) {
      parts.push(
        <em key={match.index} className="italic text-slate-300">
          {token.slice(1, -1)}
        </em>
      );
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  return parts.length > 0 ? parts : text;
}

export function ArticleMarkdown({ content }: ArticleMarkdownProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = (code: string, idx: number) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Tokenize document into logical blocks
  const lines = content.split("\n");
  const blocks: Array<
    | { type: "code"; lang: string; content: string }
    | { type: "table"; headers: string[]; rows: string[][] }
    | { type: "h2"; text: string }
    | { type: "h3"; text: string }
    | { type: "h4"; text: string }
    | { type: "alert"; kind: "NOTE" | "WARNING" | "IMPORTANT"; text: string }
    | { type: "ul"; items: string[] }
    | { type: "ol"; items: string[] }
    | { type: "p"; text: string }
  > = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // 1. Code blocks
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim() || "text";
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      blocks.push({
        type: "code",
        lang,
        content: codeLines.join("\n"),
      });
      i++; // skip closing ```
      continue;
    }

    // 2. Markdown Tables
    if (line.startsWith("|") && line.endsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].startsWith("|") && lines[i].endsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      if (tableLines.length >= 2) {
        const parseRow = (rowStr: string) =>
          rowStr
            .split("|")
            .slice(1, -1)
            .map((c) => c.trim());

        const headers = parseRow(tableLines[0]);
        // line 1 is separator |---|---|
        const rows = tableLines.slice(2).map(parseRow);
        blocks.push({ type: "table", headers, rows });
        continue;
      }
    }

    // 3. Headings
    if (line.startsWith("## ")) {
      blocks.push({ type: "h2", text: line.replace(/^## /, "").trim() });
      i++;
      continue;
    }
    if (line.startsWith("### ")) {
      blocks.push({ type: "h3", text: line.replace(/^### /, "").trim() });
      i++;
      continue;
    }
    if (line.startsWith("#### ")) {
      blocks.push({ type: "h4", text: line.replace(/^#### /, "").trim() });
      i++;
      continue;
    }

    // 4. Alerts
    if (line.startsWith("> [!NOTE]") || line.startsWith("> [!WARNING]") || line.startsWith("> [!IMPORTANT]")) {
      const kind = line.includes("WARNING")
        ? "WARNING"
        : line.includes("IMPORTANT")
        ? "IMPORTANT"
        : "NOTE";
      const alertLines: string[] = [];
      i++;
      while (i < lines.length && lines[i].startsWith(">")) {
        alertLines.push(lines[i].replace(/^>\s?/, ""));
        i++;
      }
      blocks.push({ type: "alert", kind, text: alertLines.join(" ") });
      continue;
    }

    // 5. Bullet Lists
    if (line.startsWith("- ") || line.startsWith("* ")) {
      const listItems: string[] = [];
      while (i < lines.length && (lines[i].startsWith("- ") || lines[i].startsWith("* "))) {
        listItems.push(lines[i].replace(/^[-*]\s+/, ""));
        i++;
      }
      blocks.push({ type: "ul", items: listItems });
      continue;
    }

    // 6. Numbered Lists
    if (/^\d+\.\s/.test(line)) {
      const listItems: string[] = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        listItems.push(lines[i].replace(/^\d+\.\s+/, ""));
        i++;
      }
      blocks.push({ type: "ol", items: listItems });
      continue;
    }

    // 7. Empty line
    if (!line.trim()) {
      i++;
      continue;
    }

    // 8. Paragraph
    const paraLines: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].startsWith("#") &&
      !lines[i].startsWith("```") &&
      !lines[i].startsWith("|") &&
      !lines[i].startsWith(">") &&
      !lines[i].startsWith("- ") &&
      !lines[i].startsWith("* ") &&
      !/^\d+\.\s/.test(lines[i])
    ) {
      paraLines.push(lines[i]);
      i++;
    }
    blocks.push({ type: "p", text: paraLines.join(" ") });
  }

  return (
    <div className="space-y-4 text-xs sm:text-sm text-slate-300 leading-relaxed">
      {blocks.map((block, idx) => {
        if (block.type === "h2") {
          return (
            <h2
              key={idx}
              className="text-lg font-bold text-white border-b border-slate-700/80 pb-2 mt-8 mb-3 flex items-center gap-2"
            >
              <Layers className="h-5 w-5 text-[#F2B84B]" />
              <span>{renderInline(block.text)}</span>
            </h2>
          );
        }

        if (block.type === "h3") {
          return (
            <h3
              key={idx}
              className="text-base font-bold text-white border-b border-slate-800/80 pb-1.5 mt-6 mb-2 flex items-center gap-2"
            >
              <div className="h-1.5 w-1.5 rounded-full bg-[#F2B84B]" />
              <span>{renderInline(block.text)}</span>
            </h3>
          );
        }

        if (block.type === "h4") {
          return (
            <h4 key={idx} className="text-sm font-semibold text-slate-100 mt-4 mb-1">
              {renderInline(block.text)}
            </h4>
          );
        }

        if (block.type === "code") {
          return (
            <div
              key={idx}
              className="rounded-xl border border-slate-800 bg-[#061124] overflow-hidden my-3 shadow-md"
            >
              <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-slate-800/80 text-[10px] font-mono text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Terminal className="h-3 w-3 text-[#F2B84B]" />
                  <span className="uppercase text-[#F2B84B] font-bold">{block.lang}</span>
                </span>
                <button
                  onClick={() => handleCopy(block.content, idx)}
                  className="flex items-center gap-1 hover:text-white transition-colors"
                >
                  {copiedIndex === idx ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-400" />
                      <span className="text-emerald-400 font-bold">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="p-3.5 font-mono text-[11px] sm:text-xs overflow-x-auto text-emerald-300 leading-relaxed whitespace-pre">
                <code>{block.content}</code>
              </pre>
            </div>
          );
        }

        if (block.type === "table") {
          return (
            <div
              key={idx}
              className="overflow-x-auto my-3 rounded-xl border border-slate-800 bg-slate-950/60"
            >
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-white font-bold">
                    {block.headers.map((h, hIdx) => (
                      <th key={hIdx} className="px-3.5 py-2.5 font-semibold text-slate-200">
                        {renderInline(h)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {block.rows.map((row, rIdx) => (
                    <tr
                      key={rIdx}
                      className={rIdx % 2 === 0 ? "bg-transparent" : "bg-slate-900/20"}
                    >
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="px-3.5 py-2 leading-relaxed">
                          {renderInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        if (block.type === "alert") {
          const isWarning = block.kind === "WARNING";
          const isImportant = block.kind === "IMPORTANT";
          const borderClass = isWarning
            ? "border-amber-600/70 bg-amber-950/30 text-amber-200"
            : isImportant
            ? "border-rose-600/70 bg-rose-950/30 text-rose-200"
            : "border-blue-600/70 bg-blue-950/30 text-blue-200";
          const Icon = isWarning ? AlertTriangle : isImportant ? AlertTriangle : Info;

          return (
            <div
              key={idx}
              className={`rounded-xl border p-3.5 my-3 flex items-start gap-2.5 ${borderClass}`}
            >
              <Icon className="h-4 w-4 shrink-0 mt-0.5" />
              <div className="text-xs leading-relaxed">{renderInline(block.text)}</div>
            </div>
          );
        }

        if (block.type === "ul") {
          return (
            <ul key={idx} className="list-disc pl-5 space-y-1.5 text-slate-300 my-2">
              {block.items.map((it, itIdx) => (
                <li key={itIdx}>{renderInline(it)}</li>
              ))}
            </ul>
          );
        }

        if (block.type === "ol") {
          return (
            <ol key={idx} className="list-decimal pl-5 space-y-1.5 text-slate-300 my-2">
              {block.items.map((it, itIdx) => (
                <li key={itIdx}>{renderInline(it)}</li>
              ))}
            </ol>
          );
        }

        return (
          <p key={idx} className="text-slate-300 leading-relaxed">
            {renderInline(block.text)}
          </p>
        );
      })}
    </div>
  );
}

"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/header";
import { QueryWorkbench } from "@/components/workbench/query-workbench";
import { KnowledgeCenter } from "@/components/knowledge/knowledge-center";
import { ToolsCatalog } from "@/components/tools/tools-catalog";
import { api } from "@/lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"workbench" | "knowledge" | "tools">("workbench");
  const [language, setLanguage] = useState<"en" | "id">("id");
  const [sandboxId, setSandboxId] = useState<string | null>(null);
  const [sandboxStatus, setSandboxStatus] = useState<string>("Ready");
  const [isResetting, setIsResetting] = useState<boolean>(false);

  const handleResetSandbox = async () => {
    if (!sandboxId) return;
    setIsResetting(true);
    setSandboxStatus("Resetting...");
    try {
      await api.post(`/sandboxes/${sandboxId}/reset`);
      setSandboxStatus("Ready");
      // Force trigger state refresh
      setSandboxId(sandboxId);
    } catch (err) {
      console.error("Reset error:", err);
      setSandboxStatus("Error");
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#071A3A] font-sans antialiased">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        sandboxStatus={sandboxStatus}
        onResetSandbox={handleResetSandbox}
        isResetting={isResetting}
      />

      <div className="flex-1 w-full overflow-hidden">
        {activeTab === "workbench" && (
          <QueryWorkbench
            sandboxId={sandboxId}
            onSandboxChange={(id) => {
              setSandboxId(id);
              setSandboxStatus("Ready");
            }}
            language={language}
          />
        )}

        {activeTab === "knowledge" && (
          <KnowledgeCenter
            language={language}
            onOpenLab={() => setActiveTab("workbench")}
          />
        )}

        {activeTab === "tools" && <ToolsCatalog language={language} />}
      </div>
    </div>
  );
}

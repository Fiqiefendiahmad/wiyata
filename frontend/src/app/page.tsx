"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/header";
import { QueryWorkbench } from "@/components/workbench/query-workbench";
import { LearningChallenges } from "@/components/learning/learning-challenges";
import { KnowledgeCenter } from "@/components/knowledge/knowledge-center";
import { ToolsCatalog } from "@/components/tools/tools-catalog";
import { api } from "@/lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<
    "workbench" | "challenges" | "knowledge" | "tools"
  >("workbench");
  const [language, setLanguage] = useState<"en" | "id">("id");
  const [sandboxId, setSandboxId] = useState<string | null>(null);
  const [sandboxStatus, setSandboxStatus] = useState<string>("Ready");
  const [isResetting, setIsResetting] = useState<boolean>(false);

  // Cross-component state injection
  const [labInitialQuery, setLabInitialQuery] = useState<string | undefined>(
    undefined
  );
  const [labInitialTemplate, setLabInitialTemplate] = useState<string | undefined>(
    undefined
  );

  const handleResetSandbox = async () => {
    if (!sandboxId) return;
    setIsResetting(true);
    setSandboxStatus("Resetting...");
    try {
      await api.post(`/sandboxes/${sandboxId}/reset`);
      setSandboxStatus("Ready");
      setSandboxId(sandboxId);
    } catch (err) {
      console.error("Reset error:", err);
      setSandboxStatus("Error");
    } finally {
      setIsResetting(false);
    }
  };

  const handleOpenLabWithQuery = (query: string, template: string) => {
    setLabInitialQuery(query);
    setLabInitialTemplate(template);
    setActiveTab("workbench");
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
            initialQuery={labInitialQuery}
            initialTemplate={labInitialTemplate}
          />
        )}

        {activeTab === "challenges" && (
          <LearningChallenges
            language={language}
            onOpenLabWithQuery={handleOpenLabWithQuery}
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

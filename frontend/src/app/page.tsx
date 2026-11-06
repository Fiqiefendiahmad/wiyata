"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/layout/header";
import { QueryWorkbench } from "@/components/workbench/query-workbench";
import { LearningChallenges } from "@/components/learning/learning-challenges";
import { ProfessionsMatrix } from "@/components/roles/professions-matrix";
import { KnowledgeCenter } from "@/components/knowledge/knowledge-center";
import { ToolsCatalog } from "@/components/tools/tools-catalog";
import { api } from "@/lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<
    "workbench" | "challenges" | "roles" | "knowledge" | "tools"
  >("workbench");
  const [language, setLanguage] = useState<"en" | "id">("id");
  const [sandboxId, setSandboxId] = useState<string | null>(null);
  const [sandboxStatus, setSandboxStatus] = useState<string>("Ready");
  const [isResetting, setIsResetting] = useState<boolean>(false);

  // Sync language with localStorage or follow browser language on initial launch
  useEffect(() => {
    try {
      const saved = localStorage.getItem("wiyata_lang");
      if (saved === "en" || saved === "id") {
        setLanguage(saved);
        return;
      }

      // Initial launch: detect browser language
      const browserLang =
        (typeof navigator !== "undefined" &&
          (navigator.language || (navigator.languages && navigator.languages[0]))) ||
        "";

      if (browserLang.toLowerCase().startsWith("id")) {
        setLanguage("id");
      } else {
        setLanguage("en");
      }
    } catch {
      // Fallback: keep default
    }
  }, []);

  const handleLanguageChange = (lang: "en" | "id") => {
    setLanguage(lang);
    try {
      localStorage.setItem("wiyata_lang", lang);
    } catch {}
  };

  // Cross-component state injection
  const [labInitialQuery, setLabInitialQuery] = useState<string | undefined>(
    undefined
  );
  const [labInitialTemplate, setLabInitialTemplate] = useState<string | undefined>(
    undefined
  );
  const [selectedChallengeSlug, setSelectedChallengeSlug] = useState<string | undefined>(
    undefined
  );
  const [selectedRoleSlug, setSelectedRoleSlug] = useState<string | null>(null);
  const [selectedKnowledgeSlug, setSelectedKnowledgeSlug] = useState<string | null>(null);
  const [selectedToolSlug, setSelectedToolSlug] = useState<string | null>(null);

  type TabType = "workbench" | "challenges" | "roles" | "knowledge" | "tools";

  // Sync tab and deep-link slug with HTML5 History API
  const pushNavState = (
    tab: TabType,
    slug?: string | null,
    action: "push" | "replace" = "push"
  ) => {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    url.searchParams.set("tab", tab);
    if (slug) {
      url.searchParams.set("slug", slug);
    } else {
      url.searchParams.delete("slug");
    }

    const newUrlString = url.pathname + url.search;
    const currentUrlString = window.location.pathname + window.location.search;

    if (newUrlString === currentUrlString) return;

    if (action === "replace") {
      window.history.replaceState({ tab, slug }, "", newUrlString);
    } else {
      window.history.pushState({ tab, slug }, "", newUrlString);
    }
  };

  // Initialize state from URL on first mount & anchor root history state
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get("tab") as TabType | null;
    const slugParam = params.get("slug");

    const validTabs: TabType[] = [
      "workbench",
      "challenges",
      "roles",
      "knowledge",
      "tools",
    ];
    const initialTab: TabType =
      tabParam && validTabs.includes(tabParam) ? tabParam : "workbench";

    if (initialTab !== "workbench") {
      setActiveTab(initialTab);
    }
    if (initialTab === "challenges" && slugParam) {
      setSelectedChallengeSlug(slugParam);
    } else if (initialTab === "roles" && slugParam) {
      setSelectedRoleSlug(slugParam);
    } else if (initialTab === "knowledge" && slugParam) {
      setSelectedKnowledgeSlug(slugParam);
    } else if (initialTab === "tools" && slugParam) {
      setSelectedToolSlug(slugParam);
    }

    pushNavState(initialTab, slugParam, "replace");
  }, []);

  // Handle browser Back / Forward buttons (popstate event)
  useEffect(() => {
    const handlePopState = () => {
      if (typeof window === "undefined") return;
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get("tab") as TabType | null;
      const slugParam = params.get("slug");

      const validTabs: TabType[] = [
        "workbench",
        "challenges",
        "roles",
        "knowledge",
        "tools",
      ];
      const nextTab: TabType =
        tabParam && validTabs.includes(tabParam) ? tabParam : "workbench";

      setActiveTab(nextTab);
      if (nextTab === "challenges") {
        setSelectedChallengeSlug(slugParam || undefined);
      } else if (nextTab === "roles") {
        setSelectedRoleSlug(slugParam || null);
      } else if (nextTab === "knowledge") {
        setSelectedKnowledgeSlug(slugParam || null);
      } else if (nextTab === "tools") {
        setSelectedToolSlug(slugParam || null);
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const handleTabChange = (newTab: TabType) => {
    setActiveTab(newTab);
    let activeSlug: string | null = null;
    if (newTab === "challenges") activeSlug = selectedChallengeSlug || null;
    else if (newTab === "roles") activeSlug = selectedRoleSlug;
    else if (newTab === "knowledge") activeSlug = selectedKnowledgeSlug;
    else if (newTab === "tools") activeSlug = selectedToolSlug;

    pushNavState(newTab, activeSlug, "push");
  };

  const navigateToKnowledge = (slug: string) => {
    setSelectedKnowledgeSlug(slug);
    setActiveTab("knowledge");
    pushNavState("knowledge", slug, "push");
  };

  const navigateToRole = (roleSlug: string) => {
    setSelectedRoleSlug(roleSlug);
    setActiveTab("roles");
    pushNavState("roles", roleSlug, "push");
  };

  const navigateToChallenge = (challengeSlug: string) => {
    setSelectedChallengeSlug(challengeSlug);
    setActiveTab("challenges");
    pushNavState("challenges", challengeSlug, "push");
  };

  const navigateToTool = (toolSlug: string) => {
    setSelectedToolSlug(toolSlug);
    setActiveTab("tools");
    pushNavState("tools", toolSlug, "push");
  };

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
    pushNavState("workbench", null, "push");
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#071A3A] font-sans antialiased">
      <Header
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        language={language}
        setLanguage={handleLanguageChange}
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
            initialChallengeSlug={selectedChallengeSlug}
            onSelectChallenge={(slug) => {
              setSelectedChallengeSlug(slug);
              pushNavState("challenges", slug, "push");
            }}
            onNavigateToKnowledge={navigateToKnowledge}
            onNavigateToRole={navigateToRole}
            onNavigateToTool={navigateToTool}
          />
        )}

        {activeTab === "roles" && (
          <ProfessionsMatrix
            language={language}
            initialRoleSlug={selectedRoleSlug}
            onSelectRole={(slug) => {
              setSelectedRoleSlug(slug);
              pushNavState("roles", slug, "push");
            }}
            onSelectChallenge={navigateToChallenge}
            onOpenTool={navigateToTool}
            onOpenKnowledgeArticle={navigateToKnowledge}
          />
        )}

        {activeTab === "knowledge" && (
          <KnowledgeCenter
            language={language}
            onOpenLab={() => handleTabChange("workbench")}
            initialArticleSlug={selectedKnowledgeSlug}
            onSelectArticle={(slug) => {
              setSelectedKnowledgeSlug(slug);
              pushNavState("knowledge", slug, slug ? "push" : "replace");
            }}
            onNavigateToRole={navigateToRole}
            onNavigateToChallenge={navigateToChallenge}
            onNavigateToTool={navigateToTool}
          />
        )}

        {activeTab === "tools" && (
          <ToolsCatalog
            language={language}
            initialToolSlug={selectedToolSlug}
            onSelectTool={(slug) => {
              setSelectedToolSlug(slug);
              pushNavState("tools", slug, slug ? "push" : "replace");
            }}
            onNavigateToKnowledge={navigateToKnowledge}
            onNavigateToRole={navigateToRole}
            onNavigateToChallenge={navigateToChallenge}
          />
        )}
      </div>
    </div>
  );
}

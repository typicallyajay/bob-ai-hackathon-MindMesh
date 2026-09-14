"use client"
import { useState, useEffect, useCallback } from "react";

export type TutorialStep = {
  id: string;
  title: string;
  description: string;
  target: string; // CSS selector or named anchor
  page: string;
  position: "top" | "bottom" | "left" | "right";
};

export const TUTORIAL_STEPS: TutorialStep[] = [
  {
    id: "welcome",
    title: "Welcome to THREATMESH",
    description: "This is your AI-powered Security Operations Center. THREATMESH correlates multi-source alerts into explainable attack narratives so your team can respond fast and with confidence.",
    target: "[data-tour='command-center-title']",
    page: "/",
    position: "bottom",
  },
  {
    id: "stat-cards",
    title: "Live Threat Metrics",
    description: "These cards show real-time counts of alerts and incidents by severity. Critical incidents are prioritised at the top — click any number to filter the incident list below.",
    target: "[data-tour='stat-cards']",
    page: "/",
    position: "bottom",
  },
  {
    id: "incident-list",
    title: "Correlated Incidents",
    description: "Raw alerts are automatically clustered into high-fidelity incidents. Each row shows the threat score, confidence, severity and the number of underlying alerts. Click any row to deep-dive.",
    target: "[data-tour='incident-list']",
    page: "/",
    position: "top",
  },
  {
    id: "severity-chart",
    title: "Severity Distribution",
    description: "A live breakdown of your incident landscape by severity level. Helps you understand the overall risk profile at a glance.",
    target: "[data-tour='severity-chart']",
    page: "/",
    position: "left",
  },
  {
    id: "alerts-page",
    title: "Raw Alert Feed",
    description: "Every individual alert ingested from all sources — SIEM, EDR, network, auth — is visible here. Use pagination to scroll through history.",
    target: "[data-tour='alerts-title']",
    page: "/alerts",
    position: "bottom",
  },
  {
    id: "incident-header",
    title: "Incident Overview",
    description: "The incident header shows you the overall threat score, confidence score, severity badge, affected hosts and users, and the automated summary. This is your command brief.",
    target: "[data-tour='incident-header']",
    page: "/incidents/1",
    position: "bottom",
  },
  {
    id: "attack-graph",
    title: "Interactive Attack Graph",
    description: "THREATMESH builds an entity relationship graph — hosts, users, IPs, processes — connected by the attack progression. Drag nodes, zoom, and inspect to understand lateral movement.",
    target: "[data-tour='incident-tabs']",
    page: "/incidents/1",
    position: "bottom",
  },
  {
    id: "counterfactual",
    title: "What-If / Counterfactual Analysis",
    description: "Select any alert in the attack chain and ask: \"What if this alert is a false positive?\" THREATMESH re-scores the incident and tells you if the chain still holds — giving auditable confidence for decisions.",
    target: "[data-tour='incident-tabs']",
    page: "/incidents/1",
    position: "bottom",
  },
  {
    id: "bob-chat",
    title: "Bob — Your AI Investigation Partner",
    description: "Bob is backed by real backend tools. Ask in plain English: \"Why is this malicious?\", \"Show attack path\", or \"What if alert ALT-0003 is false?\" — Bob calls the actual engines and explains results.",
    target: "[data-tour='bob-chat']",
    page: "/investigate",
    position: "top",
  },
];

const STORAGE_KEY = "threatmesh_tutorial_complete";
const DEMO_MODE_KEY = "threatmesh_demo_mode";

export function useDemo() {
  const [tutorialActive, setTutorialActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem(STORAGE_KEY);
    const demo = localStorage.getItem(DEMO_MODE_KEY);
    if (!completed) setTutorialActive(true);
    if (demo === "1") setDemoMode(true);
  }, []);

  const startTutorial = useCallback(() => {
    setCurrentStep(0);
    setTutorialActive(true);
  }, []);

  const nextStep = useCallback(() => {
    if (currentStep < TUTORIAL_STEPS.length - 1) {
      setCurrentStep(s => s + 1);
    } else {
      setTutorialActive(false);
      localStorage.setItem(STORAGE_KEY, "1");
    }
  }, [currentStep]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) setCurrentStep(s => s - 1);
  }, [currentStep]);

  const closeTutorial = useCallback(() => {
    setTutorialActive(false);
    localStorage.setItem(STORAGE_KEY, "1");
  }, []);

  const toggleDemoMode = useCallback(() => {
    setDemoMode(d => {
      const next = !d;
      if (next) localStorage.setItem(DEMO_MODE_KEY, "1");
      else localStorage.removeItem(DEMO_MODE_KEY);
      return next;
    });
  }, []);

  return {
    tutorialActive,
    currentStep,
    totalSteps: TUTORIAL_STEPS.length,
    step: TUTORIAL_STEPS[currentStep],
    startTutorial,
    nextStep,
    prevStep,
    closeTutorial,
    demoMode,
    toggleDemoMode,
  };
}

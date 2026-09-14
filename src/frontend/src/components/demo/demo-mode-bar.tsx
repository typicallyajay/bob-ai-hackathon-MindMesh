"use client"
import { BookOpen, X, Zap } from "lucide-react";

interface DemoModeBarProps {
  demoMode: boolean;
  onToggle: () => void;
  onStartTutorial: () => void;
}

const MARQUEE_TEXT = "DEMO MODE  ·  Synthetic telemetry active  ·  All data is representative  ·  IBM Bob AI connected  ·  Counterfactual engine live  ·  MITRE ATT&CK mapping enabled  ·  ";

export function DemoModeBar({ demoMode, onToggle, onStartTutorial }: DemoModeBarProps) {
  if (!demoMode) return null;

  return (
    <div
      className="fixed top-0 left-0 right-0 z-[9990] overflow-hidden"
      style={{
        background: "linear-gradient(90deg, #1e1b4b, #312e81, #4c1d95, #312e81, #1e1b4b)",
        backgroundSize: "400% 100%",
        animation: "shimmer 4s ease infinite",
        borderBottom: "1px solid rgba(139,92,246,0.4)",
      }}
    >
      <div className="flex items-center h-7">
        {/* Fixed left label */}
        <div
          className="shrink-0 flex items-center gap-1.5 px-3 text-[11px] font-bold text-violet-300 z-10"
          style={{ borderRight: "1px solid rgba(139,92,246,0.3)" }}
        >
          <Zap className="h-3 w-3 text-yellow-400" />
          DEMO
        </div>

        {/* Scrolling ticker */}
        <div className="flex-1 overflow-hidden relative">
          <div className="flex whitespace-nowrap animate-marquee text-[11px] text-violet-300/70 font-medium">
            <span>{MARQUEE_TEXT}</span>
            <span>{MARQUEE_TEXT}</span>
          </div>
        </div>

        {/* Fixed right controls */}
        <div
          className="shrink-0 flex items-center gap-1 px-2"
          style={{ borderLeft: "1px solid rgba(139,92,246,0.3)" }}
        >
          <button
            onClick={onStartTutorial}
            className="flex items-center gap-1 text-[10px] text-violet-300 hover:text-white transition-colors px-1.5 py-0.5 rounded hover:bg-white/10"
          >
            <BookOpen className="h-2.5 w-2.5" />
            Tutorial
          </button>
          <button
            onClick={onToggle}
            className="text-violet-400 hover:text-white transition-colors p-0.5 rounded hover:bg-white/10"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  );
}

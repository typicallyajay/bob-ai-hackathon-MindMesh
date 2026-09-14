"use client"
import { BobChat } from "@/components/bob/chat";
import { Lightbulb, Zap, FlaskConical, FileText } from "lucide-react";

const HINTS = [
  {
    icon: Lightbulb,
    color: "#f59e0b",
    fill: "#f59e0b",
    title: "Natural Language",
    desc: "Ask plain English questions — Bob calls real backend engines, not canned responses.",
  },
  {
    icon: Zap,
    color: "#60a5fa",
    fill: "#3b82f6",
    title: "Tool Calls Visible",
    desc: "Every engine Bob invokes shows below its reply — full transparency on what ran.",
  },
  {
    icon: FlaskConical,
    color: "#a78bfa",
    fill: "#8b5cf6",
    title: "What-If Scenarios",
    desc: "\"What if alert ALT-0003 is false?\" — Bob runs live counterfactual analysis.",
  },
  {
    icon: FileText,
    color: "#34d399",
    fill: "#10b981",
    title: "BLUF Summaries",
    desc: "Ask \"Generate BLUF\" for a commander-ready brief on any active incident.",
  },
];

export default function InvestigatePage() {
  return (
    <div className="max-w-5xl mx-auto h-full flex flex-col gap-5">
      <div className="animate-slide-up">
        <h1 className="text-2xl font-black tracking-tight text-slate-100 mb-1">
          Investigate with{" "}
          <span className="shimmer-text">Bob</span>
        </h1>
        <p className="text-sm text-slate-400">
          Your AI investigation partner — backed by real threat correlation engines.
        </p>
      </div>

      {/* Hint cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 animate-fade-in">
        {HINTS.map(({ icon: Icon, color, fill, title, desc }, idx) => (
          <div
            key={title}
            className="rounded-2xl p-4 flex flex-col gap-3 relative overflow-hidden cursor-default transition-all duration-300 hover:-translate-y-1"
            style={{
              background: `linear-gradient(135deg, ${fill}15 0%, rgba(17,23,38,0.92) 100%)`,
              border: `1px solid ${fill}30`,
              animationDelay: `${idx * 60}ms`,
              boxShadow: `0 0 0 ${fill}00`,
              transition: "transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease",
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLElement).style.boxShadow = `0 8px 24px ${fill}30`;
              (e.currentTarget as HTMLElement).style.borderColor = `${fill}50`;
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLElement).style.boxShadow = `0 0 0 ${fill}00`;
              (e.currentTarget as HTMLElement).style.borderColor = `${fill}30`;
            }}
          >
            {/* Background orb */}
            <div
              className="absolute -top-2 -right-2 w-12 h-12 rounded-full blur-xl pointer-events-none animate-float-medium"
              style={{ background: `${fill}25` }}
            />
            {/* Icon */}
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center relative z-10"
              style={{ background: `${fill}20`, border: `1px solid ${fill}35` }}
            >
              <Icon className="h-4 w-4" style={{ color }} />
            </div>
            <div className="relative z-10">
              <p className="text-xs font-bold text-slate-100 mb-1">{title}</p>
              <p className="text-[11px] leading-relaxed text-slate-400">{desc}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="flex-1 animate-fade-in" style={{ animationDelay: "200ms" }}>
        <BobChat />
      </div>
    </div>
  );
}

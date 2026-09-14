"use client"
import { useState, useEffect, useRef } from "react";
import { useDashboardStats } from "@/hooks/use-api";
import { Activity, RefreshCw, Wifi, Cpu, TrendingUp, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricPoint { value: number; ts: number; }

/* ── Area sparkline with gradient fill ── */
function AreaSparkline({ points, color, fillColor }: {
  points: MetricPoint[];
  color: string;
  fillColor: string;
}) {
  if (points.length < 2) return <div className="w-20 h-7" />;
  const W = 80, H = 28;
  const vals = points.map(p => p.value);
  const min = Math.min(...vals);
  const max = Math.max(...vals) || min + 1;
  const sy = (v: number) => H - 2 - ((v - min) / (max - min + 0.001)) * (H - 6);
  const sx = (i: number) => (i / (vals.length - 1)) * W;
  const pts = vals.map((v, i) => `${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join(" ");
  const areaPath = `M${sx(0).toFixed(1)},${H} ` +
    vals.map((v, i) => `L${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join(" ") +
    ` L${sx(vals.length - 1).toFixed(1)},${H} Z`;
  const uid = color.replace(/[^a-z0-9]/gi, "");

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} className="overflow-visible">
      <defs>
        <linearGradient id={`grad-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={fillColor} stopOpacity="0.45" />
          <stop offset="100%" stopColor={fillColor} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {/* Area fill */}
      <path d={areaPath} fill={`url(#grad-${uid})`} />
      {/* Line */}
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5"
        strokeLinejoin="round" strokeLinecap="round" />
      {/* Last dot */}
      <circle cx={sx(vals.length - 1)} cy={sy(vals[vals.length - 1])} r="2.5" fill={color} />
      {/* Glow dot */}
      <circle cx={sx(vals.length - 1)} cy={sy(vals[vals.length - 1])} r="5" fill={color} opacity="0.2">
        <animate attributeName="r" values="3;7;3" dur="2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.2;0;0.2" dur="2s" repeatCount="indefinite" />
      </circle>
    </svg>
  );
}

/* ── Metric tile ── */
function MetricTile({ label, value, unit, color, fillColor, sparkPoints, icon: Icon }: {
  label: string;
  value: number | string;
  unit?: string;
  color: string;
  fillColor: string;
  sparkPoints?: MetricPoint[];
  icon: React.ElementType;
}) {
  return (
    <div
      className="flex-1 min-w-[130px] rounded-2xl p-4 flex flex-col gap-2 relative overflow-hidden"
      style={{
        background: `linear-gradient(135deg, ${fillColor}12 0%, rgba(8,12,24,0.9) 100%)`,
        border: `1px solid ${fillColor}25`,
      }}
    >
      {/* Background orb */}
      <div
        className="absolute -top-3 -right-3 w-14 h-14 rounded-full blur-xl animate-float-slow pointer-events-none"
        style={{ background: `${fillColor}20` }}
      />
      <div className="flex items-center gap-1.5 relative">
        <Icon className="h-3 w-3" style={{ color }} />
        <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: `${color}99` }}>
          {label}
        </span>
      </div>
      <div className="flex items-end justify-between gap-1 relative">
        <span className="text-2xl font-black tabular-nums leading-none" style={{ color }}>
          {value}
          {unit && <span className="text-xs font-normal ml-0.5" style={{ color: `${color}70` }}>{unit}</span>}
        </span>
        {sparkPoints && <AreaSparkline points={sparkPoints} color={color} fillColor={fillColor} />}
      </div>
    </div>
  );
}

/* ── Event type config ── */
const EVENT_CONFIG = {
  alert:       { color: "#f97316", bg: "#f9731618", dot: "bg-orange-400",   label: "ALERT" },
  incident:    { color: "#ef4444", bg: "#ef444418", dot: "bg-red-400",      label: "INC"   },
  correlation: { color: "#60a5fa", bg: "#60a5fa18", dot: "bg-blue-400",     label: "CORR"  },
  ai:          { color: "#a78bfa", bg: "#a78bfa18", dot: "bg-violet-400",   label: "AI"    },
} as const;

type EventType = keyof typeof EVENT_CONFIG;

interface LiveEvent { id: number; time: string; text: string; type: EventType; }

const EVENT_POOL: Omit<LiveEvent, "id" | "time">[] = [
  { text: "Brute-force pattern detected on WS-04 via SIEM", type: "alert" },
  { text: "Correlation engine updated INC-001 score → 94/100", type: "incident" },
  { text: "Bob generated BLUF summary for INC-003", type: "ai" },
  { text: "EDR: suspicious powershell.exe spawned on DC-01", type: "alert" },
  { text: "Lateral movement confirmed: WS-04 → DC-01", type: "correlation" },
  { text: "Network: C2 beacon to 185.220.101.x detected", type: "alert" },
  { text: "Counterfactual — chain intact without ALT-0003", type: "ai" },
  { text: "Auth: privilege escalation by user jsmith", type: "alert" },
  { text: "INC-002 promoted to CRITICAL severity", type: "incident" },
  { text: "MITRE: T1059 + T1078 confirmed for INC-001", type: "correlation" },
  { text: "Bob answered \"Show me the attack path\"", type: "ai" },
  { text: "Alert batch: 12 events from Splunk SIEM", type: "alert" },
  { text: "INC-003 confidence updated → 87%", type: "incident" },
  { text: "Graph engine added 3 entity nodes for INC-001", type: "correlation" },
];

export function LiveDemoPanel() {
  const { data } = useDashboardStats();
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [alertsProcessed, setAlertsProcessed] = useState(247);
  const [latency, setLatency] = useState(12);
  const [corrRate, setCorrRate] = useState(94);
  const [uptime] = useState(99.9);

  const alertHist = useRef<MetricPoint[]>([]);
  const latHist   = useRef<MetricPoint[]>([]);
  const corrHist  = useRef<MetricPoint[]>([]);
  const eventId   = useRef(0);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const now = Date.now();
    alertHist.current = Array.from({ length: 14 }, (_, i) => ({ value: 20 + Math.random() * 15, ts: now - (13 - i) * 4000 }));
    latHist.current   = Array.from({ length: 14 }, (_, i) => ({ value: 8  + Math.random() * 10, ts: now - (13 - i) * 4000 }));
    corrHist.current  = Array.from({ length: 14 }, (_, i) => ({ value: 88 + Math.random() * 10, ts: now - (13 - i) * 4000 }));

    const seeds: LiveEvent[] = Array.from({ length: 6 }, (_, i) => ({
      ...EVENT_POOL[i % EVENT_POOL.length],
      id: i,
      time: new Date(Date.now() - (6 - i) * 7000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    }));
    setEvents(seeds);
    eventId.current = 6;
    if (data?.total_alerts) setAlertsProcessed(data.total_alerts);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      const ev = EVENT_POOL[Math.floor(Math.random() * EVENT_POOL.length)];
      const newEvent: LiveEvent = {
        ...ev, id: eventId.current++,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      };
      setEvents(prev => [newEvent, ...prev].slice(0, 10));

      const aV = 18 + Math.random() * 20;
      const lV = 7  + Math.random() * 14;
      const cV = 87 + Math.random() * 11;
      alertHist.current = [...alertHist.current, { value: aV, ts: now }].slice(-14);
      latHist.current   = [...latHist.current,   { value: lV, ts: now }].slice(-14);
      corrHist.current  = [...corrHist.current,   { value: cV, ts: now }].slice(-14);

      setAlertsProcessed(p => p + Math.floor(Math.random() * 4));
      setLatency(Math.round(lV * 10) / 10);
      setCorrRate(Math.round(cV));
      setTick(t => t + 1);
    }, 3800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="rounded-2xl overflow-hidden relative"
      style={{
        background: "linear-gradient(135deg, #0a0f1e 0%, #080c18 100%)",
        border: "1px solid rgba(99,102,241,0.18)",
        boxShadow: "0 0 60px rgba(99,102,241,0.08)",
      }}
      data-tour="live-demo-panel"
    >
      {/* Subtle scan line */}
      <div
        className="absolute left-0 right-0 h-px animate-scan pointer-events-none z-0"
        style={{ background: "linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent)" }}
      />

      {/* Header */}
      <div
        className="flex items-center justify-between px-5 py-3 relative z-10"
        style={{ borderBottom: "1px solid rgba(99,102,241,0.12)" }}
      >
        <div className="flex items-center gap-2.5">
          {/* Live indicator orb */}
          <div className="relative w-3 h-3">
            <div className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-60" />
            <div
              className="relative w-3 h-3 rounded-full bg-emerald-400"
              style={{ boxShadow: "0 0 8px rgba(52,211,153,0.9)" }}
            />
          </div>
          <span className="text-xs font-bold tracking-wider text-slate-300">LIVE SYSTEM MONITOR</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px] text-slate-600">
          <RefreshCw className="h-2.5 w-2.5 animate-spin [animation-duration:3s]" />
          auto-refresh
        </div>
      </div>

      {/* Metrics row */}
      <div className="flex flex-wrap gap-3 p-4 relative z-10" style={{ borderBottom: "1px solid rgba(99,102,241,0.08)" }}>
        <MetricTile
          label="Alerts Processed"
          value={alertsProcessed}
          color="#f97316"
          fillColor="#f97316"
          sparkPoints={alertHist.current}
          icon={Activity}
        />
        <MetricTile
          label="Correlation Rate"
          value={corrRate}
          unit="%"
          color="#60a5fa"
          fillColor="#3b82f6"
          sparkPoints={corrHist.current}
          icon={TrendingUp}
        />
        <MetricTile
          label="API Latency"
          value={latency}
          unit="ms"
          color="#34d399"
          fillColor="#10b981"
          sparkPoints={latHist.current}
          icon={Wifi}
        />
        <MetricTile
          label="Uptime"
          value={uptime}
          unit="%"
          color="#a78bfa"
          fillColor="#8b5cf6"
          icon={Cpu}
        />
      </div>

      {/* Event feed */}
      <div className="p-4 relative z-10">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="h-3 w-3 text-slate-500" />
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600">Live Event Stream</span>
          <div
            className="ml-auto px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest"
            style={{ background: "rgba(99,102,241,0.15)", color: "#818cf8" }}
          >
            {events.length} recent
          </div>
        </div>
        <div className="space-y-1 max-h-[180px] overflow-hidden">
          {events.map((ev, i) => {
            const cfg = EVENT_CONFIG[ev.type];
            return (
              <div
                key={ev.id}
                className={cn(
                  "flex items-start gap-2.5 rounded-lg px-2.5 py-1.5 transition-all duration-700",
                  i === 0 && "flash-new"
                )}
                style={{
                  opacity: i === 0 ? 1 : i < 3 ? 0.85 : i < 6 ? 0.55 : 0.25,
                  background: i === 0 ? cfg.bg : "transparent",
                }}
              >
                {/* Type badge */}
                <span
                  className="shrink-0 mt-0.5 text-[9px] font-black px-1 py-0.5 rounded leading-none"
                  style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.color}30` }}
                >
                  {cfg.label}
                </span>
                <span className="text-[10px] text-slate-500 font-mono whitespace-nowrap shrink-0">
                  {ev.time}
                </span>
                <span className="text-xs flex-1 leading-relaxed" style={{ color: i === 0 ? cfg.color : "#94a3b8" }}>
                  {ev.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

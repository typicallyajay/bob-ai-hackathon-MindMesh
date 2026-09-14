import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function severityColor(severity: string): string {
  switch (severity.toUpperCase()) {
    case 'CRITICAL': return 'text-rose-400';
    case 'HIGH': return 'text-amber-400';
    case 'MEDIUM': return 'text-yellow-300';
    case 'LOW': return 'text-emerald-400';
    default: return 'text-slate-400';
  }
}

export function severityBg(severity: string): string {
  switch (severity.toUpperCase()) {
    case 'CRITICAL': return 'bg-rose-500/15 border-rose-500/30';
    case 'HIGH': return 'bg-amber-500/15 border-amber-500/30';
    case 'MEDIUM': return 'bg-yellow-400/15 border-yellow-400/30';
    case 'LOW': return 'bg-emerald-500/15 border-emerald-500/30';
    default: return 'bg-slate-500/15 border-slate-500/30';
  }
}

export function formatTimestamp(ts: string | null | undefined): string {
  if (!ts) return 'N/A';
  return new Date(ts).toLocaleString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}

export function formatDate(ts: string | null | undefined): string {
  if (!ts) return 'N/A';
  return new Date(ts).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

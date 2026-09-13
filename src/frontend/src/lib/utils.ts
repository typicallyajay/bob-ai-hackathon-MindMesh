import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function severityColor(severity: string): string {
  switch (severity.toUpperCase()) {
    case 'CRITICAL': return 'text-red-500';
    case 'HIGH': return 'text-orange-500';
    case 'MEDIUM': return 'text-yellow-500';
    case 'LOW': return 'text-green-500';
    default: return 'text-slate-400';
  }
}

export function severityBg(severity: string): string {
  switch (severity.toUpperCase()) {
    case 'CRITICAL': return 'bg-red-500/10 border-red-500/30';
    case 'HIGH': return 'bg-orange-500/10 border-orange-500/30';
    case 'MEDIUM': return 'bg-yellow-500/10 border-yellow-500/30';
    case 'LOW': return 'bg-green-500/10 border-green-500/30';
    default: return 'bg-slate-500/10 border-slate-500/30';
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

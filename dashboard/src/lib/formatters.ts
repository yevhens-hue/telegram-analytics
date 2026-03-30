import { THRESHOLDS } from './config';

export function computeTrend(current: number, previous: number): string {
  if (previous === 0) return current > 0 ? "+New" : "+0%";
  const pct = ((current - previous) / previous) * 100;
  const sign = pct >= 0 ? "+" : "";
  return `${sign}${pct.toFixed(1)}%`;
}

export function getTrafficLabel(organicIndex: number): { label: string; className: string } {
  if (organicIndex > THRESHOLDS.viral) {
    return {
      label: "Viral",
      className: "px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[9px] font-bold rounded-lg border border-emerald-500/10 uppercase tracking-widest",
    };
  }
  if (organicIndex > THRESHOLDS.organic) {
    return {
      label: "Organic",
      className: "px-2 py-1 bg-indigo-500/10 text-indigo-400 text-[9px] font-bold rounded-lg border border-indigo-500/10 uppercase tracking-widest",
    };
  }
  return {
    label: "Paid Growth",
    className: "px-2 py-1 bg-amber-500/10 text-amber-400 text-[9px] font-bold rounded-lg border border-amber-500/10 uppercase tracking-widest",
  };
}

export function getSentimentColor(sentiment: number): string {
  if (sentiment > 70) return 'bg-emerald-500';
  if (sentiment > 40) return 'bg-amber-500';
  return 'bg-red-500';
}

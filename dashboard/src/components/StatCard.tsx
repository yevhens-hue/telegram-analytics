"use client";

import { motion } from "framer-motion";
import { Coins, Users, Trophy, Activity, LucideIcon } from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  coins: Coins,
  users: Users,
  trophy: Trophy,
  activity: Activity,
};

const colorMap: Record<string, { bg: string; icon: string; blur: string; blurHover: string }> = {
  indigo: {
    bg: "bg-indigo-500/10",
    icon: "text-indigo-400",
    blur: "bg-indigo-500/10",
    blurHover: "group-hover:bg-indigo-500/20",
  },
  blue: {
    bg: "bg-blue-500/10",
    icon: "text-blue-400",
    blur: "bg-blue-500/10",
    blurHover: "group-hover:bg-blue-500/20",
  },
  purple: {
    bg: "bg-purple-500/10",
    icon: "text-purple-400",
    blur: "bg-purple-500/10",
    blurHover: "group-hover:bg-purple-500/20",
  },
  emerald: {
    bg: "bg-emerald-500/10",
    icon: "text-emerald-400",
    blur: "bg-emerald-500/10",
    blurHover: "group-hover:bg-emerald-500/20",
  },
};

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: string;
  iconName: string;
  color: string;
  delay?: number;
}

function getTrendStyle(trend: string): string {
  if (trend.startsWith('+')) {
    return "flex items-center text-[10px] font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full uppercase tracking-wider";
  }
  if (trend.startsWith('-')) {
    return "flex items-center text-[10px] font-bold text-red-400 bg-red-400/10 px-2 py-1 rounded-full uppercase tracking-wider";
  }
  return "flex items-center text-[10px] font-bold text-slate-400 bg-slate-400/10 px-2 py-1 rounded-full uppercase tracking-wider";
}

export default function StatCard({ label, value, trend, iconName, color, delay = 0 }: StatCardProps) {
  const Icon = iconMap[iconName] || Activity;
  const colors = colorMap[color] || colorMap.indigo;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass-card p-6 rounded-3xl relative overflow-hidden group hover:border-white/10 transition-all"
    >
      <div className={`absolute top-0 right-0 w-32 h-32 ${colors.blur} blur-3xl -mr-16 -mt-16 ${colors.blurHover} transition-all`} />
      
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 ${colors.bg} rounded-2xl`}>
          <Icon className={`w-6 h-6 ${colors.icon}`} />
        </div>
        {trend && (
          <span className={getTrendStyle(trend)}>
            {trend}
          </span>
        )}
      </div>
      
      <h3 className="text-slate-500 text-xs font-bold uppercase tracking-widest mb-1">{label}</h3>
      <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
    </motion.div>
  );
}

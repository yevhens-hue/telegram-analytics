"use client";

import { LayoutDashboard, TrendingUp, BarChart3, Settings, Shield, Zap, Info } from "lucide-react";
import { motion } from "framer-motion";

const menuItems = [
  { icon: LayoutDashboard, label: "Overview", active: true },
  { icon: TrendingUp, label: "Top Charts" },
  { icon: BarChart3, label: "Market Depth" },
  { icon: Shield, label: "TON Indexer" },
];

const secondaryItems = [
  { icon: Settings, label: "Settings" },
  { icon: Info, label: "Documentation" },
];

export default function Sidebar() {
  return (
    <div className="w-64 border-r border-slate-800/50 bg-[#02040a] flex flex-col h-full sticky top-0">
      <div className="p-8 pb-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-[0_0_15px_rgba(99,102,241,0.5)]">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <span className="text-xl font-bold font-heading tracking-tight text-white">TMA Analytics</span>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-1">
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-4 mb-3">Main Menu</div>
        {menuItems.map((item, idx) => (
          <motion.button
            key={idx}
            whileHover={{ x: 4 }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all ${
              item.active 
                ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.05)]" 
                : "text-slate-400 hover:text-white hover:bg-slate-800/40"
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="text-sm font-medium">{item.label}</span>
          </motion.button>
        ))}

        <div className="pt-8 mb-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest px-4">System</div>
        {secondaryItems.map((item, idx) => (
          <motion.button
            key={idx}
            whileHover={{ x: 4 }}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/40 transition-all"
          >
            <item.icon className="w-5 h-5" />
            <span className="text-sm font-medium">{item.label}</span>
          </motion.button>
        ))}
      </nav>

      <div className="p-4">
        <div className="bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20 rounded-2xl p-4">
          <p className="text-xs font-semibold text-white mb-1">PRO Access</p>
          <p className="text-[10px] text-slate-400 mb-3 leading-relaxed">Unlock advanced whale tracking and deep market insights.</p>
          <button className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-bold rounded-lg shadow-lg shadow-indigo-600/20 transition-all">
            Upgrade Now
          </button>
        </div>
      </div>
    </div>
  );
}

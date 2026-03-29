"use client";

import { motion } from "framer-motion";
import { Zap, Clock } from "lucide-react";

interface ComingSoonProps {
  title: string;
  description: string;
}

export default function ComingSoon({ title, description }: ComingSoonProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="glass-card p-12 rounded-[3rem] border border-white/5 relative overflow-hidden max-w-2xl bg-gradient-to-br from-indigo-500/5 to-purple-500/5"
      >
        {/* Background Gradients */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-indigo-500/10 rounded-full blur-[80px]" />
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-purple-500/10 rounded-full blur-[80px]" />

        <div className="relative z-10 space-y-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-slate-900 border border-white/5 mb-4 shadow-xl">
            <Clock className="w-10 h-10 text-indigo-400" />
          </div>
          
          <div className="space-y-4">
            <h1 className="text-5xl font-black font-heading text-white tracking-tighter">
              {title}
            </h1>
            <div className="h-1.5 w-24 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full mx-auto" />
            <p className="text-slate-400 text-lg font-medium leading-relaxed max-w-md mx-auto">
              {description}
            </p>
          </div>

          <div className="flex items-center justify-center gap-4 text-xs font-bold text-slate-500 uppercase tracking-widest pt-4">
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5">In Development</span>
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5">Q2 2026</span>
          </div>
        </div>
      </motion.div>

      {/* Quick Stats Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 w-full max-w-4xl">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass p-6 rounded-2xl border border-white/5 flex items-center gap-4 group hover:border-indigo-500/20 transition-all opacity-40">
            <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
              <Zap className="w-5 h-5 text-slate-600" />
            </div>
            <div className="flex-1">
              <div className="h-2 w-20 bg-slate-800 rounded-full mb-2" />
              <div className="h-4 w-24 bg-slate-800 rounded-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

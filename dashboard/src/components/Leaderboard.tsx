'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Activity, ChevronDown } from 'lucide-react';
import { getTrafficLabel } from '@/lib/formatters';

interface AppData {
  app_name: string;
  category: string;
  position: number;
  daily_revenue_ton: number;
  daily_active_wallets: number;
  growth: number;
  organic_index: number;
  trend_score: number;
  market_sentiment: number;
  prediction_7d: number;
}

interface LeaderboardProps {
  apps: AppData[];
}

const ITEMS_PER_PAGE = 20;

const Leaderboard: React.FC<LeaderboardProps> = ({ apps }) => {
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE);

  const visibleApps = apps.slice(0, displayCount);
  const hasMore = displayCount < apps.length;

  const loadMore = () => {
    setDisplayCount(prev => Math.min(prev + ITEMS_PER_PAGE, apps.length));
  };

  return (
    <section className="pt-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold font-heading text-white mb-1">Global Leaderboard</h2>
          <p className="text-xs text-slate-500 font-medium uppercase tracking-widest">
            Ranked by Market Position & Trending Score ({apps.length} apps)
          </p>
        </div>
      </div>

      <div className="overflow-x-auto rounded-[2rem] border border-white/5 glass-card mb-8">
        <table className="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr className="bg-white/5 text-slate-500 text-[10px] font-bold uppercase tracking-widest">
              <th className="px-8 py-6 w-16 text-center">Rank</th>
              <th className="px-8 py-6">Application</th>
              <th className="px-8 py-6 text-center">Velocity</th>
              <th className="px-8 py-6 text-center">AI Sentiment</th>
              <th className="px-8 py-6 text-center">7D Forecast</th>
              <th className="px-8 py-6 text-center">Traffic Type</th>
              <th className="px-8 py-6 text-right">Viral Index</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            <AnimatePresence initial={false}>
              {visibleApps.map((app, i) => {
                const traffic = getTrafficLabel(app.organic_index);
                return (
                  <motion.tr
                    key={`${app.app_name}-${i}`}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                    className="hover:bg-indigo-500/5 transition-all group cursor-pointer"
                    onClick={() => window.location.href = `/app/${encodeURIComponent(app.app_name)}`}
                  >
                    <td className="px-8 py-6">
                      <div className={`flex items-center justify-center w-8 h-8 rounded-lg text-sm font-bold ${app.position <= 1 ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.4)]' : app.position <= 3 ? 'bg-slate-400 text-slate-900' : 'bg-slate-800/80 text-slate-500'}`}>
                        {app.position}
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center font-bold text-indigo-300 border border-white/5">
                          {app.app_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <Link href={`/app/${encodeURIComponent(app.app_name)}`} className="font-bold text-white group-hover:text-indigo-400 transition-colors hover:underline">{app.app_name}</Link>
                          <div className="text-[10px] text-slate-500 mt-1 uppercase tracking-widest font-bold">{app.category}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center">
                      {app.growth > 0 ? (
                        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
                          <TrendingUp className="w-3 h-3" /> +{app.growth}
                        </div>
                      ) : app.growth < 0 ? (
                        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/10 text-red-400 text-xs font-bold border border-red-500/20">
                          <Activity className="w-3 h-3 rotate-180" /> {app.growth}
                        </div>
                      ) : (
                        <span className="text-slate-600 font-bold">—</span>
                      )}
                    </td>
                    <td className="px-8 py-6 text-center">
                      <div className="flex flex-col items-center gap-1.5">
                        <div className="w-20 h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-1000 ${app.market_sentiment > 70 ? 'bg-emerald-500' : app.market_sentiment > 40 ? 'bg-amber-500' : 'bg-red-500'}`} 
                            style={{ width: `${app.market_sentiment}%` }} 
                          />
                        </div>
                        <span className="text-[10px] font-bold text-slate-500">{app.market_sentiment}%</span>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center">
                      <span className={`text-sm font-bold ${app.prediction_7d > app.daily_revenue_ton ? 'text-emerald-400' : 'text-slate-400'}`}>
                        {Math.round(app.prediction_7d).toLocaleString()} <span className="text-[10px] text-slate-600 ml-0.5">TON</span>
                      </span>
                    </td>
                    <td className="px-8 py-6 text-center">
                      <span className={traffic.className}>{traffic.label}</span>
                    </td>
                    <td className="px-8 py-6 text-right">
                       <div className="flex items-center justify-end gap-2">
                        <span className="text-sm font-bold text-white">{app.organic_index.toFixed(1)}</span>
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                      </div>
                    </td>
                  </motion.tr>
                );
              })}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {hasMore && (
        <div className="flex justify-center pb-12">
          <button 
            onClick={loadMore}
            className="flex items-center gap-2 px-8 py-4 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 font-bold rounded-2xl border border-indigo-500/20 transition-all group"
          >
            Load More <ChevronDown className="w-4 h-4 group-hover:translate-y-1 transition-transform" />
          </button>
        </div>
      )}
    </section>
  );
};

export default Leaderboard;

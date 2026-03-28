import { getTopApps, getRevenueTrend } from '@/lib/db';
import TrendChart from '@/components/TrendChart';
import Sidebar from '@/components/Sidebar';
import StatCard from '@/components/StatCard';
import { TrendingUp, Activity, Flame, Brain, Target, Coins, Users, Trophy } from 'lucide-react';
import * as motion from "framer-motion/client";

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

interface TrendData {
  date: string;
  total_ton: number;
  total_dau: number;
}

function computeTrend(current: number, previous: number): string {
  if (previous === 0) return "+0%";
  const pct = ((current - previous) / previous) * 100;
  const sign = pct >= 0 ? "+" : "";
  return `${sign}${pct.toFixed(1)}%`;
}

export default async function Dashboard() {
  const apps = (await getTopApps()) as unknown as AppData[];
  const trend = (await getRevenueTrend()) as unknown as TrendData[];

  const latestStats = trend[trend.length - 1] || { total_ton: 0, total_dau: 0 };
  const prevStats = trend.length >= 2 ? trend[trend.length - 2] : { total_ton: 0, total_dau: 0 };
  const topApp = apps[0];

  const revenueTrend = computeTrend(latestStats.total_ton, prevStats.total_ton);
  const dauTrend = computeTrend(latestStats.total_dau, prevStats.total_dau);

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />

      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-12 max-w-[1400px] mx-auto">
        
        {/* Top Header */}
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold font-heading text-white tracking-tight mb-2">Market Overview</h1>
            <p className="text-slate-500 font-medium italic">Latest insights from Telegram Mini Apps ecosystem</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.6)]" />
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest leading-none">Live Data Tracking</p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-4 gap-6">
          <StatCard 
            label="Total Daily Revenue" 
            value={`${Math.round(latestStats.total_ton).toLocaleString()} TON`}
            trend={revenueTrend} 
            iconName="coins" 
            color="indigo" 
            delay={0.1}
          />
          <StatCard 
            label="Active Wallets (DAU)" 
            value={latestStats.total_dau.toLocaleString()} 
            trend={dauTrend}
            iconName="users" 
            color="blue" 
            delay={0.2}
          />
          <StatCard 
            label="Market Leader" 
            value={topApp?.app_name || "N/A"} 
            trend={topApp ? `#${topApp.position}` : undefined}
            iconName="trophy" 
            color="purple" 
            delay={0.3}
          />
           <StatCard 
            label="Apps Monitored" 
            value={apps.length} 
            iconName="activity" 
            color="emerald" 
            delay={0.4}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          
          {/* Trend Chart Area */}
          <div className="lg:col-span-2 space-y-4">
             <div className="glass-card p-8 rounded-[2rem]">
               <div className="flex items-center justify-between mb-2">
                 <h2 className="text-xl font-bold font-heading text-white">Consolidated Growth</h2>
                 <div className="bg-slate-800/50 p-1 rounded-lg flex gap-1">
                   <button className="px-3 py-1 text-[10px] font-bold text-white bg-indigo-600 rounded-md">Revenue</button>
                   <button className="px-3 py-1 text-[10px] font-bold text-slate-500 hover:text-white transition-colors">Users</button>
                 </div>
               </div>
               <p className="text-xs text-slate-500 font-medium mb-8">Aggregate network activity across tracked smart contracts</p>
               <TrendChart data={trend} />
             </div>

             {/* Featured Horizontal Scroller */}
             <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide pt-4">
               {apps.slice(0, 5).map((app, idx) => (
                 <div key={idx} className="min-w-[220px] glass p-5 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-all cursor-pointer group">
                   <div className="flex items-center justify-between mb-4">
                     <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-slate-400 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                        {app.app_name[0]}
                     </div>
                     <Flame className="w-4 h-4 text-orange-500" style={{ filter: 'drop-shadow(0 0 4px rgba(249,115,22,0.3))' }} />
                   </div>
                   <h3 className="text-sm font-bold text-white truncate mb-1">{app.app_name}</h3>
                   <p className="text-[10px] text-slate-500 font-medium mb-3">{app.category}</p>
                   <div className="flex items-center justify-between">
                     <span className="text-xs font-bold text-indigo-400">{Math.round(app.daily_revenue_ton).toLocaleString()} TON</span>
                     <span className="text-[10px] font-bold text-emerald-500">+{app.growth}</span>
                   </div>
                 </div>
               ))}
             </div>
          </div>

          {/* Right Section: Trending Category */}
          <div className="glass-card p-8 rounded-[2rem] space-y-6">
             <h2 className="text-xl font-bold font-heading text-white">Rising Stars</h2>
             <div className="space-y-4">
                {apps.filter(a => a.growth > 0).slice(0, 6).map((app, i) => (
                  <div key={i} className="flex items-center gap-4 group cursor-pointer hover:bg-white/5 p-2 -mx-2 rounded-xl transition-all">
                    <div className="w-2 h-10 bg-indigo-500/20 rounded-full overflow-hidden">
                       <div className="w-full bg-indigo-500 transition-all" style={{ height: `${app.organic_index}%` }} />
                    </div>
                    <div className="flex-1 min-w-0">
                       <p className="text-sm font-bold text-white truncate">{app.app_name}</p>
                       <p className="text-[10px] text-slate-500">{app.category}</p>
                    </div>
                    <div className="text-right">
                       <p className="text-xs font-bold text-emerald-400">↑ {app.growth}</p>
                       <p className="text-[9px] text-slate-600 font-bold uppercase tracking-widest">{app.daily_active_wallets.toLocaleString()} WALLETS</p>
                    </div>
                  </div>
                ))}
             </div>
             <button className="w-full py-4 bg-slate-800/50 hover:bg-slate-800 text-slate-400 hover:text-white text-xs font-bold rounded-2xl transition-all border border-white/5 uppercase tracking-widest">
               Explore Velocity
             </button>
          </div>

        </div>

        {/* Global Leaderboard Table */}
        <section className="pt-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold font-heading text-white mb-1">Global Leaderboard</h2>
              <p className="text-xs text-slate-500 font-medium uppercase tracking-widest">Ranked by Market Position & Trending Score</p>
            </div>
          </div>
          
          <div className="overflow-hidden rounded-[2rem] border border-white/5 glass-card">
            <table className="w-full text-left border-collapse">
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
                {apps.map((app, i) => (
                  <motion.tr 
                    key={`${app.app_name}-${i}`} 
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 + i * 0.03, duration: 0.3 }}
                    className="hover:bg-indigo-500/5 transition-all group"
                  >
                    <td className="px-8 py-6">
                      <div className={`flex items-center justify-center w-8 h-8 rounded-lg text-sm font-bold ${app.position <= 1 ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.4)]' : app.position <= 3 ? 'bg-slate-400 text-slate-900' : 'bg-slate-800/80 text-slate-500'}`}>
                        {app.position}
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center font-bold text-indigo-300 border border-white/5">
                          {app.app_name.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-bold text-white group-hover:text-indigo-400 transition-colors">{app.app_name}</div>
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
                      <div className="flex items-center justify-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${app.market_sentiment > 70 ? 'bg-emerald-500' : app.market_sentiment > 40 ? 'bg-amber-500' : 'bg-red-500'}`} />
                        <span className="font-bold text-slate-300 tabular-nums">{Math.round(app.market_sentiment)}</span>
                        <Brain className="w-3 h-3 text-slate-600 opacity-40" />
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center">
                      <div className="flex flex-col items-center">
                        <div className="flex items-center gap-1">
                          <Target className="w-3 h-3 text-indigo-500/50" />
                          <span className={`text-sm font-black tracking-tight tabular-nums ${app.prediction_7d < app.position ? 'text-emerald-400' : 'text-slate-400'}`}>
                            #{Math.max(1, Math.floor(app.prediction_7d || app.position))}
                          </span>
                        </div>
                        <span className="text-[8px] text-slate-600 font-bold uppercase tracking-widest mt-0.5">7D AI Focus</span>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center">
                      <div className="flex justify-center">
                        {app.organic_index > 75 ? (
                          <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[9px] font-bold rounded-lg border border-emerald-500/10 uppercase tracking-widest">Viral</span>
                        ) : app.organic_index > 45 ? (
                          <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-[9px] font-bold rounded-lg border border-indigo-500/10 uppercase tracking-widest">Organic</span>
                        ) : (
                          <span className="px-2 py-1 bg-amber-500/10 text-amber-400 text-[9px] font-bold rounded-lg border border-amber-500/10 uppercase tracking-widest">Paid Growth</span>
                        )}
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center justify-end gap-3 min-w-[120px]">
                         <span className="text-[10px] font-black text-slate-500 italic">{Math.round(app.organic_index)}%</span>
                         <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden border border-white/5">
                           <div 
                             className="h-full bg-gradient-to-r from-indigo-500 to-purple-500" 
                             style={{ width: `${Math.min(100, Math.max(10, app.organic_index))}%` }}
                           />
                         </div>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>
  );
}

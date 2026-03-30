'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, TrendingUp, Users, Activity, ShieldCheck, DollarSign } from 'lucide-react';
import Link from 'next/link';

interface AnalyticsData {
  category?: string;
  description?: string;
  position: number;
  growth: number;
  revenue_ton: number;
  dau: number;
  market_sentiment: number;
  organic_index: number;
  trend_score: number;
  prediction_7d: number;
}

interface TonData {
  daily_revenue_ton?: number;
  daily_active_wallets?: number;
}

interface ChannelData {
  subscribers?: number;
}

interface AppDetailData {
  analytics: AnalyticsData;
  ton?: TonData;
  channel?: ChannelData;
  positionHistory: Array<{ date: string; position: number }>;
  analyticsHistory: Array<Record<string, unknown>>;
}

interface AppDetailClientProps {
  appName: string;
  appData: AppDetailData;
}

export default function AppDetailClient({ appName, appData }: AppDetailClientProps) {
  const analytics = appData.analytics;
  const ton = appData.ton || {};
  const channel = appData.channel || {};

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  };

  return (
    <div className="space-y-8">
      {/* Header section */}
      <motion.div {...fadeIn} className="flex flex-col gap-6 md:flex-row md:items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-colors border border-white/5 group">
            <ArrowLeft className="w-5 h-5 text-slate-400 group-hover:text-white transition-colors" />
          </Link>
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center font-bold text-3xl text-indigo-300 border border-indigo-500/20 shadow-[0_0_30px_rgba(99,102,241,0.1)]">
              {appName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                {appName}
              </h1>
              <div className="flex items-center gap-3 mt-2">
                <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-bold uppercase tracking-widest text-slate-300">
                  {analytics.category || 'App'}
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-bold text-emerald-400">
                  <ShieldCheck className="w-3 h-3" /> Verified Market App
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Description */}
      {analytics.description && (
        <motion.p {...fadeIn} transition={{ delay: 0.1 }} className="text-slate-400 text-lg leading-relaxed max-w-3xl">
          {analytics.description}
        </motion.p>
      )}

      {/* Primary KPIs */}
      <motion.div {...fadeIn} transition={{ delay: 0.2 }} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-colors" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-xl border border-indigo-500/20">
              <Activity className="w-5 h-5" />
            </div>
            {analytics.position <= 3 && (
              <span className="px-2 py-1 rounded-lg bg-amber-500/20 text-amber-400 text-xs font-bold border border-amber-500/20">
                Top {analytics.position} Trend
              </span>
            )}
          </div>
          <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-1">Market Rank</p>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold">#{analytics.position}</span>
            {analytics.growth > 0 ? (
              <span className="text-emerald-400 text-sm font-bold">+{analytics.growth}</span>
            ) : analytics.growth < 0 ? (
              <span className="text-red-400 text-sm font-bold">{analytics.growth}</span>
            ) : null}
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-colors" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl border border-emerald-500/20">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-1">Daily Revenue</p>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold">{ton.daily_revenue_ton?.toLocaleString() || analytics.revenue_ton?.toLocaleString()}</span>
            <span className="text-slate-500 text-sm font-bold">TON</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl group-hover:bg-purple-500/20 transition-colors" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-purple-500/20 text-purple-400 rounded-xl border border-purple-500/20">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-1">Active Wallets</p>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold">{ton.daily_active_wallets?.toLocaleString() || analytics.dau?.toLocaleString()}</span>
            <span className="text-slate-500 text-sm font-bold">24H</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl group-hover:bg-cyan-500/20 transition-colors" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-1">AI Sentiment</p>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold">{analytics.market_sentiment}</span>
            <span className="text-slate-500 text-sm font-bold">%</span>
          </div>
          <div className="w-full h-1.5 bg-white/10 rounded-full mt-4 overflow-hidden">
            <div className="h-full bg-cyan-400 transition-all duration-1000" style={{ width: `${analytics.market_sentiment}%` }} />
          </div>
        </div>
      </motion.div>

      {/* Further Analytics */}
      <motion.div {...fadeIn} transition={{ delay: 0.3 }} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-[#0A0A0A] border border-white/5 rounded-3xl p-8 backdrop-blur-xl">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <TrendingUp className="text-indigo-400" /> Advanced Insights
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-2 gap-8">
            <div>
              <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">Organic Viral Index</p>
              <div className="text-3xl font-bold text-white">{analytics.organic_index.toFixed(2)}x</div>
              <p className="text-slate-400 text-sm mt-2">Current viral coefficient calculated by engine algorithms.</p>
            </div>
            <div>
              <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">Trend Score</p>
              <div className="text-3xl font-bold text-white">{analytics.trend_score.toFixed(1)}</div>
              <p className="text-slate-400 text-sm mt-2">Overall compound algorithm scoring comparing similar apps.</p>
            </div>
            <div>
              <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">Social Reach</p>
              <div className="text-3xl font-bold text-white">{channel.subscribers?.toLocaleString() || 'N/A'}</div>
              <p className="text-slate-400 text-sm mt-2">Connected Telegram Channel or group members.</p>
            </div>
            <div>
              <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">7D Prediction</p>
              <div className="text-3xl font-bold text-emerald-400">+{(analytics.prediction_7d / (analytics.revenue_ton || 1) * 100).toFixed(1)}%</div>
              <p className="text-slate-400 text-sm mt-2">Est. revenue growth over 7D timeframe via ML backtest.</p>
            </div>
          </div>
        </div>
        
        <div className="bg-[#111116] border border-indigo-500/20 rounded-3xl p-8 shadow-[0_0_30px_rgba(99,102,241,0.05)] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl" />
          <h3 className="text-lg font-bold text-white mb-6">Historical Log (Latest)</h3>
          <div className="space-y-4">
            {appData.positionHistory.slice(0, 5).map((log, i: number) => (
              <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-slate-400 text-sm font-medium">{log.date}</span>
                <span className="text-white font-bold bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-md text-sm border border-indigo-500/20">
                  Rank #{log.position}
                </span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

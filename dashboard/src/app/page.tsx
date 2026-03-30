import Link from 'next/link';
import { getTopApps, getRevenueTrend, getLatestTonMetrics, getNewsSentiment, getLatestAlerts } from '@/lib/db';

import TrendChart from '@/components/TrendChart';
import Sidebar from '@/components/Sidebar';
import StatCard from '@/components/StatCard';
import NewsSentiment from '@/components/NewsSentiment';
import SystemAlerts from '@/components/SystemAlerts';
import Leaderboard from '@/components/Leaderboard';
import { Flame } from 'lucide-react';
import type { AppData, TrendData, TonMetrics, NewsItem, Alert } from '@/lib/types';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

import { computeTrend } from '@/lib/formatters';

async function fetchDashboardData() {
  try {
    const [apps, trend, tonMetrics, news, alerts] = await Promise.all([
      getTopApps(),
      getRevenueTrend(),
      getLatestTonMetrics(),
      getNewsSentiment(),
      getLatestAlerts()
    ]);
    return { 
      apps: apps as unknown as AppData[], 
      trend: trend as unknown as TrendData[], 
      tonMetrics: tonMetrics as unknown as TonMetrics,
      news: news as unknown as NewsItem[],
      alerts: alerts as unknown as Alert[],
      error: null 
    };
  } catch (e) {
    console.error('Dashboard data fetch failed:', e);
    return { 
      apps: [] as AppData[], 
      trend: [] as TrendData[], 
      tonMetrics: { price_usd: 1.23, asset_id: 'TON', date: '' } as TonMetrics,
      news: [] as NewsItem[],
      alerts: [] as Alert[],
      error: (e as Error).message 
    };
  }
}

export default async function Dashboard() {
  const { apps, trend, tonMetrics, news, alerts, error } = await fetchDashboardData();

  const latestStats = trend[trend.length - 1] || { total_ton: 0, total_dau: 0 };
  const prevStats = trend.length >= 2 ? trend[trend.length - 2] : { total_ton: 0, total_dau: 0 };
  const topApp = apps[0];

  const revenueTrend = computeTrend(latestStats.total_ton, prevStats.total_ton);
  const dauTrend = computeTrend(latestStats.total_dau, prevStats.total_dau);

  if (error) {
    return (
      <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
        <Sidebar />
        <main className="flex-1 overflow-y-auto px-10 py-12 max-w-[1400px] mx-auto">
          <div className="glass-card p-8 rounded-[2rem] border border-red-500/20">
            <h2 className="text-2xl font-bold font-heading text-red-400 mb-4">Dashboard Error</h2>
            <p className="text-slate-400">Failed to load analytics data: {error}</p>
          </div>
        </main>
      </div>
    );
  }

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
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <StatCard
            label="TON Market Price"
            value={`$${tonMetrics.price_usd.toFixed(2)}`}
            trend="+2.4%" 
            iconName="coins"
            color="emerald"
            delay={0.1}
          />
          <StatCard
            label="Total Daily Revenue"
            value={`${Math.round(latestStats.total_ton).toLocaleString()} TON`}
            trend={revenueTrend}
            iconName="activity"
            color="indigo"
            delay={0.2}
          />
          <StatCard
            label="Active Wallets (DAU)"
            value={latestStats.total_dau.toLocaleString()}
            trend={dauTrend}
            iconName="users"
            color="blue"
            delay={0.3}
          />
          <StatCard
            label="Market Leader"
            value={topApp?.app_name || "N/A"}
            trend={topApp ? `#${topApp.position}` : undefined}
            iconName="trophy"
            color="purple"
            delay={0.4}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

          <div className="lg:col-span-2 space-y-4">
            <div className="glass-card p-8 rounded-[2rem]">
              <TrendChart data={trend} />
            </div>

            <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide pt-4">
              {apps.slice(0, 5).map((app, idx) => (
                <Link href={`/app/${encodeURIComponent(app.app_name)}`} key={idx} className="min-w-[220px] glass p-5 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-all cursor-pointer group block">
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
                </Link>
              ))}
            </div>
          </div>

          <div className="space-y-8">
            <NewsSentiment news={news} />
            <SystemAlerts alerts={alerts} />
          </div>

        </div>

        {/* Global Leaderboard Client Component */}
        <Leaderboard apps={apps} />

      </main>
    </div>
  );
}
